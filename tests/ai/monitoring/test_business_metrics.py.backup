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

"""Advanced Business Metrics Tests - Industrial Grade

Comprehensive, enterprise-level test suite for business intelligence and KPI tracking system.
Tests revenue tracking, user engagement analytics, and platform growth metrics with real scenarios.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use of this code without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted to the full
extent of the law.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
import statistics
import json
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch

from ai.monitoring.business_metrics import (
    BusinessMetricsCollector,
    RevenueSource,
    UserTier,
    EngagementType,
    RevenueMetrics,
    UserEngagementMetrics,
    ContentMetrics,
    CollaborationMetrics,
    PlatformGrowthMetrics,
    RevenueAnalyzer,
    EngagementAnalyzer,
    GrowthPredictor,
    ROICalculator,
    ChurnPredictor,
    LifetimeValueCalculator
)
from ai.core.metrics import MetricType, MetricPriority
from ai.core.exceptions import BusinessMetricsError
from .fixtures import (
    business_scenarios,
    revenue_test_data,
    engagement_patterns,
    growth_metrics_data,
    user_journey_data
)


class TestBusinessMetricsCollectorCore:
    """Core functionality tests for business metrics collection."""
    
    @pytest.fixture
    async def metrics_collector(self):
        """Create and initialize business metrics collector."""
        collector = BusinessMetricsCollector(
            config={
                "revenue_tracking": True,
                "engagement_analysis": True,
                "growth_monitoring": True,
                "real_time_processing": True,
                "data_retention_days": 365,
                "aggregation_intervals": ["minute", "hour", "day", "week", "month"],
                "currency_conversion": True,
                "fraud_detection": True
            }
        )
        await collector.initialize()
        yield collector
        await collector.shutdown()
    
    @pytest.fixture
    def revenue_scenarios(self, revenue_test_data):
        """Generate realistic revenue scenarios."""
        return revenue_test_data["production_scenarios"]
    
    async def test_collector_initialization_comprehensive(self, metrics_collector):
        """Test comprehensive initialization of business metrics collector."""
        # Verify core components
        assert metrics_collector is not None
        assert metrics_collector.is_initialized
        assert metrics_collector.revenue_analyzer is not None
        assert metrics_collector.engagement_analyzer is not None
        assert metrics_collector.growth_predictor is not None
        assert metrics_collector.roi_calculator is not None
        assert metrics_collector.churn_predictor is not None
        
        # Verify configuration
        config = metrics_collector.config
        assert config["revenue_tracking"] is True
        assert config["engagement_analysis"] is True
        assert config["real_time_processing"] is True
        
        # Verify supported revenue sources
        supported_sources = metrics_collector.get_supported_revenue_sources()
        expected_sources = [
            RevenueSource.CONTENT_PROTECTION,
            RevenueSource.COLLABORATION_MATCHING,
            RevenueSource.PREMIUM_FEATURES,
            RevenueSource.DISTRIBUTION_FEES,
            RevenueSource.ADVERTISING,
            RevenueSource.SUBSCRIPTION,
            RevenueSource.TRANSACTION_FEES
        ]
        assert all(source in supported_sources for source in expected_sources)
        
        # Verify aggregation setup
        aggregators = metrics_collector.get_active_aggregators()
        assert "revenue_aggregator" in aggregators
        assert "engagement_aggregator" in aggregators
        assert "growth_aggregator" in aggregators
    
    async def test_revenue_tracking_comprehensive(self, metrics_collector, revenue_scenarios):
        """Test comprehensive revenue tracking across all sources."""
        total_revenue = Decimal('0.00')
        revenue_by_source = {}
        
        for scenario in revenue_scenarios:
            # Record revenue transaction
            revenue_metrics = RevenueMetrics(
                user_id=scenario["user_id"],
                revenue_source=RevenueSource(scenario["source"]),
                amount=Decimal(str(scenario["amount"])),
                currency=scenario["currency"],
                content_id=scenario.get("content_id"),
                collaboration_id=scenario.get("collaboration_id"),
                commission_rate=scenario.get("commission_rate", 0.0),
                platform_fee=Decimal(str(scenario.get("platform_fee", 0.0)))
            )
            
            # Calculate net revenue
            revenue_metrics.net_revenue = revenue_metrics.amount - revenue_metrics.platform_fee
            
            # Record in system
            recording_result = await metrics_collector.record_revenue(revenue_metrics)
            
            assert recording_result is True
            
            # Track totals
            total_revenue += revenue_metrics.net_revenue
            source_key = scenario["source"]
            if source_key not in revenue_by_source:
                revenue_by_source[source_key] = Decimal('0.00')
            revenue_by_source[source_key] += revenue_metrics.net_revenue
        
        # Verify revenue aggregation
        revenue_summary = await metrics_collector.get_revenue_summary(
            start_date=datetime.utcnow() - timedelta(hours=1),
            end_date=datetime.utcnow()
        )
        
        assert revenue_summary["total_revenue"] > 0
        assert revenue_summary["transaction_count"] == len(revenue_scenarios)
        assert len(revenue_summary["by_source"]) > 0
        
        # Verify revenue source breakdown
        for source, expected_amount in revenue_by_source.items():
            assert source in revenue_summary["by_source"]
            recorded_amount = Decimal(str(revenue_summary["by_source"][source]))
            assert abs(recorded_amount - expected_amount) < Decimal('0.01')
        
        # Test revenue filtering and analysis
        content_protection_revenue = await metrics_collector.get_revenue_by_source(
            RevenueSource.CONTENT_PROTECTION,
            start_date=datetime.utcnow() - timedelta(hours=1)
        )
        
        assert content_protection_revenue["total"] >= 0
        assert "average_transaction" in content_protection_revenue
        assert "transaction_count" in content_protection_revenue
    
    async def test_user_engagement_tracking(self, metrics_collector, engagement_patterns):
        """Test comprehensive user engagement tracking and analysis."""
        engagement_sessions = []
        
        for pattern in engagement_patterns:
            user_id = pattern["user_id"]
            session_id = pattern["session_id"]
            
            # Record engagement events for this session
            for event in pattern["events"]:
                engagement_metrics = UserEngagementMetrics(
                    user_id=user_id,
                    engagement_type=EngagementType(event["type"]),
                    session_id=session_id,
                    engagement_value=event["value"],
                    duration=event.get("duration"),
                    feature_used=event.get("feature"),
                    success=event.get("success", True),
                    metadata=event.get("metadata", {})
                )
                
                result = await metrics_collector.record_engagement(engagement_metrics)
                assert result is True
            
            engagement_sessions.append({
                "user_id": user_id,
                "session_id": session_id,
                "event_count": len(pattern["events"]),
                "expected_score": pattern["expected_engagement_score"]
            })
        
        # Analyze engagement patterns
        for session in engagement_sessions:
            engagement_analysis = await metrics_collector.analyze_user_engagement(
                user_id=session["user_id"],
                analysis_period=timedelta(hours=1)
            )
            
            assert "engagement_score" in engagement_analysis
            assert "session_count" in engagement_analysis
            assert "feature_usage" in engagement_analysis
            assert "engagement_trends" in engagement_analysis
            
            # Verify engagement score calculation
            calculated_score = engagement_analysis["engagement_score"]
            expected_score = session["expected_score"]
            assert abs(calculated_score - expected_score) < 0.1
        
        # Test cohort analysis
        cohort_analysis = await metrics_collector.analyze_engagement_cohorts(
            cohort_period="daily",
            analysis_period=timedelta(days=7)
        )
        
        assert "cohort_data" in cohort_analysis
        assert "retention_rates" in cohort_analysis
        assert "engagement_progression" in cohort_analysis
    
    async def test_content_metrics_tracking(self, metrics_collector):
        """Test content performance and monetization metrics."""
        content_scenarios = [
            {
                "content_id": "content_001",
                "user_id": "creator_001",
                "content_type": "video",
                "upload_size_mb": 150,
                "processing_time": 45.2,
                "protection_applied": True,
                "seo_score": 8.5,
                "collaboration_requests": 3,
                "views": 1250,
                "revenue_generated": Decimal("125.50")
            },
            {
                "content_id": "content_002", 
                "user_id": "creator_002",
                "content_type": "audio",
                "upload_size_mb": 25,
                "processing_time": 12.8,
                "protection_applied": True,
                "seo_score": 7.8,
                "collaboration_requests": 1,
                "views": 850,
                "revenue_generated": Decimal("65.75")
            }
        ]
        
        for scenario in content_scenarios:
            content_metrics = ContentMetrics(
                content_id=scenario["content_id"],
                creator_id=scenario["user_id"],
                content_type=scenario["content_type"],
                upload_size_mb=scenario["upload_size_mb"],
                processing_time_seconds=scenario["processing_time"],
                protection_applied=scenario["protection_applied"],
                seo_optimization_score=scenario["seo_score"],
                collaboration_requests=scenario["collaboration_requests"],
                view_count=scenario["views"],
                revenue_generated=scenario["revenue_generated"]
            )
            
            result = await metrics_collector.record_content_metrics(content_metrics)
            assert result is True
        
        # Analyze content performance
        content_analysis = await metrics_collector.analyze_content_performance(
            time_period=timedelta(hours=1)
        )
        
        assert "total_content" in content_analysis
        assert "average_processing_time" in content_analysis
        assert "protection_rate" in content_analysis
        assert "average_seo_score" in content_analysis
        assert "revenue_per_content" in content_analysis
        
        # Verify metrics
        assert content_analysis["total_content"] == 2
        assert content_analysis["protection_rate"] == 1.0  # 100% protection rate
        
        expected_avg_processing = (45.2 + 12.8) / 2
        assert abs(content_analysis["average_processing_time"] - expected_avg_processing) < 0.1
        
        # Test content creator analytics
        creator_analytics = await metrics_collector.analyze_creator_performance(
            creator_id="creator_001",
            analysis_period=timedelta(days=30)
        )
        
        assert "content_count" in creator_analytics
        assert "total_revenue" in creator_analytics
        assert "average_views" in creator_analytics
        assert "collaboration_rate" in creator_analytics
    
    async def test_collaboration_metrics_tracking(self, metrics_collector):
        """Test collaboration matching and success metrics."""
        collaboration_scenarios = [
            {
                "collaboration_id": "collab_001",
                "creator_id": "creator_001",
                "collaborator_id": "creator_002",
                "match_score": 0.92,
                "negotiation_duration_hours": 24,
                "agreement_reached": True,
                "project_duration_days": 14,
                "combined_revenue": Decimal("450.00"),
                "satisfaction_scores": {"creator": 4.8, "collaborator": 4.6}
            },
            {
                "collaboration_id": "collab_002",
                "creator_id": "creator_003",
                "collaborator_id": "creator_004", 
                "match_score": 0.78,
                "negotiation_duration_hours": 72,
                "agreement_reached": False,
                "project_duration_days": 0,
                "combined_revenue": Decimal("0.00"),
                "satisfaction_scores": {"creator": 2.1, "collaborator": 2.3}
            }
        ]
        
        successful_collaborations = 0
        
        for scenario in collaboration_scenarios:
            collaboration_metrics = CollaborationMetrics(
                collaboration_id=scenario["collaboration_id"],
                creator_id=scenario["creator_id"],
                collaborator_id=scenario["collaborator_id"],
                match_algorithm_score=scenario["match_score"],
                negotiation_duration_hours=scenario["negotiation_duration_hours"],
                agreement_reached=scenario["agreement_reached"],
                project_completion_time_days=scenario["project_duration_days"],
                combined_revenue=scenario["combined_revenue"],
                creator_satisfaction=scenario["satisfaction_scores"]["creator"],
                collaborator_satisfaction=scenario["satisfaction_scores"]["collaborator"]
            )
            
            result = await metrics_collector.record_collaboration_metrics(collaboration_metrics)
            assert result is True
            
            if scenario["agreement_reached"]:
                successful_collaborations += 1
        
        # Analyze collaboration effectiveness
        collaboration_analysis = await metrics_collector.analyze_collaboration_effectiveness(
            analysis_period=timedelta(hours=1)
        )
        
        assert "total_attempts" in collaboration_analysis
        assert "success_rate" in collaboration_analysis
        assert "average_match_score" in collaboration_analysis
        assert "average_negotiation_time" in collaboration_analysis
        assert "average_satisfaction" in collaboration_analysis
        
        # Verify calculations
        assert collaboration_analysis["total_attempts"] == 2
        assert collaboration_analysis["success_rate"] == successful_collaborations / 2
        
        expected_avg_match = (0.92 + 0.78) / 2
        assert abs(collaboration_analysis["average_match_score"] - expected_avg_match) < 0.01
        
        # Test collaboration matching optimization
        matching_insights = await metrics_collector.analyze_matching_algorithm(
            time_period=timedelta(days=7)
        )
        
        assert "match_score_distribution" in matching_insights
        assert "success_by_score_range" in matching_insights
        assert "optimization_recommendations" in matching_insights


class TestBusinessMetricsAnalysis:
    """Tests for business metrics analysis and insights."""
    
    @pytest.fixture
    async def analytics_system(self):
        """Create analytics-focused metrics system."""
        system = BusinessMetricsCollector(
            config={
                "analytics_enabled": True,
                "predictive_modeling": True,
                "trend_analysis": True,
                "segmentation_analysis": True,
                "comparative_analysis": True
            }
        )
        await system.initialize()
        yield system
        await system.shutdown()
    
    async def test_revenue_trend_analysis(self, analytics_system):
        """Test revenue trend analysis and forecasting."""
        # Generate historical revenue data
        base_date = datetime.utcnow() - timedelta(days=30)
        revenue_history = []
        
        for day in range(30):
            date = base_date + timedelta(days=day)
            
            # Simulate growing revenue with seasonal patterns
            base_revenue = 1000 + (day * 50)  # Growth trend
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * day / 7)  # Weekly seasonality
            daily_revenue = base_revenue * seasonal_factor + np.random.normal(0, 100)
            
            revenue_metrics = RevenueMetrics(
                user_id=f"user_{day % 10}",
                revenue_source=RevenueSource.CONTENT_PROTECTION,
                amount=Decimal(str(max(daily_revenue, 100))),
                currency="USD",
                timestamp=date
            )
            
            await analytics_system.record_revenue(revenue_metrics)
            revenue_history.append(daily_revenue)
        
        # Analyze revenue trends
        trend_analysis = await analytics_system.analyze_revenue_trends(
            analysis_period=timedelta(days=30),
            trend_detection=True,
            seasonality_detection=True,
            forecast_days=7
        )
        
        assert "trend_direction" in trend_analysis
        assert "trend_strength" in trend_analysis
        assert "seasonality_detected" in trend_analysis
        assert "forecast" in trend_analysis
        
        # Verify trend detection
        assert trend_analysis["trend_direction"] == "increasing"
        assert trend_analysis["trend_strength"] > 0.5
        
        # Verify forecast
        forecast = trend_analysis["forecast"]
        assert len(forecast) == 7
        assert all(prediction > 0 for prediction in forecast)
        
        # Test growth rate calculation
        growth_rates = await analytics_system.calculate_growth_rates(
            metrics=["daily_revenue", "weekly_revenue", "monthly_revenue"],
            period=timedelta(days=30)
        )
        
        assert "daily_growth_rate" in growth_rates
        assert "weekly_growth_rate" in growth_rates
        assert "monthly_growth_rate" in growth_rates
        assert all(rate > 0 for rate in growth_rates.values())
    
    async def test_user_segmentation_analysis(self, analytics_system, user_journey_data):
        """Test user segmentation and behavior analysis."""
        # Record user journey data
        for journey in user_journey_data:
            user_id = journey["user_id"]
            
            # Record registration
            await analytics_system.record_user_event(
                user_id=user_id,
                event_type="registration",
                timestamp=journey["registration_date"],
                metadata={"source": journey["acquisition_source"]}
            )
            
            # Record tier upgrades
            for upgrade in journey["tier_history"]:
                await analytics_system.record_user_event(
                    user_id=user_id,
                    event_type="tier_upgrade",
                    timestamp=upgrade["date"],
                    metadata={
                        "from_tier": upgrade["from_tier"],
                        "to_tier": upgrade["to_tier"],
                        "revenue": upgrade["revenue"]
                    }
                )
            
            # Record content activities
            for activity in journey["content_activities"]:
                await analytics_system.record_user_event(
                    user_id=user_id,
                    event_type=activity["type"],
                    timestamp=activity["date"],
                    metadata=activity.get("metadata", {})
                )
        
        # Perform user segmentation
        segmentation_analysis = await analytics_system.perform_user_segmentation(
            segmentation_criteria=[
                "tier_level",
                "content_creation_frequency",
                "revenue_contribution",
                "collaboration_activity"
            ]
        )
        
        assert "segments" in segmentation_analysis
        assert "segment_characteristics" in segmentation_analysis
        assert "segment_performance" in segmentation_analysis
        
        segments = segmentation_analysis["segments"]
        assert len(segments) > 0
        
        # Verify segment characteristics
        for segment_name, segment_data in segments.items():
            assert "user_count" in segment_data
            assert "avg_revenue" in segment_data
            assert "engagement_score" in segment_data
            assert "retention_rate" in segment_data
        
        # Test cohort retention analysis
        cohort_analysis = await analytics_system.analyze_user_cohorts(
            cohort_period="weekly",
            retention_periods=[1, 4, 8, 12, 24]  # weeks
        )
        
        assert "cohort_table" in cohort_analysis
        assert "retention_curves" in cohort_analysis
        assert "average_retention" in cohort_analysis
    
    async def test_lifetime_value_calculation(self, analytics_system):
        """Test customer lifetime value calculation and prediction."""
        # Create user scenarios with different value profiles
        user_scenarios = [
            {
                "user_id": "high_value_user",
                "registration_date": datetime.utcnow() - timedelta(days=365),
                "tier": UserTier.PREMIUM,
                "monthly_revenue": 150.0,
                "engagement_score": 0.9,
                "churn_probability": 0.1
            },
            {
                "user_id": "medium_value_user",
                "registration_date": datetime.utcnow() - timedelta(days=180),
                "tier": UserTier.BASIC,
                "monthly_revenue": 45.0,
                "engagement_score": 0.6,
                "churn_probability": 0.3
            },
            {
                "user_id": "low_value_user",
                "registration_date": datetime.utcnow() - timedelta(days=90),
                "tier": UserTier.FREE,
                "monthly_revenue": 5.0,
                "engagement_score": 0.3,
                "churn_probability": 0.7
            }
        ]
        
        ltv_results = []
        
        for scenario in user_scenarios:
            # Record historical revenue for user
            days_active = (datetime.utcnow() - scenario["registration_date"]).days
            monthly_revenue = scenario["monthly_revenue"]
            
            for month in range(days_active // 30):
                # Simulate monthly revenue with some variation
                revenue = monthly_revenue * (1 + np.random.normal(0, 0.1))
                
                revenue_metrics = RevenueMetrics(
                    user_id=scenario["user_id"],
                    revenue_source=RevenueSource.SUBSCRIPTION,
                    amount=Decimal(str(max(revenue, 0))),
                    currency="USD",
                    timestamp=scenario["registration_date"] + timedelta(days=month * 30)
                )
                
                await analytics_system.record_revenue(revenue_metrics)
            
            # Calculate LTV
            ltv_calculation = await analytics_system.calculate_lifetime_value(
                user_id=scenario["user_id"],
                prediction_horizon_months=12,
                include_churn_prediction=True
            )
            
            ltv_results.append({
                "user_id": scenario["user_id"],
                "ltv": ltv_calculation,
                "expected_tier": scenario["tier"]
            })
            
            # Verify LTV calculation
            assert "historical_value" in ltv_calculation
            assert "predicted_value" in ltv_calculation
            assert "total_ltv" in ltv_calculation
            assert "confidence_score" in ltv_calculation
            assert "churn_probability" in ltv_calculation
            
            # Verify LTV ordering (premium > basic > free)
            historical_value = ltv_calculation["historical_value"]
            assert historical_value > 0
        
        # Verify LTV hierarchy
        ltv_by_tier = {result["expected_tier"]: result["ltv"]["total_ltv"] for result in ltv_results}
        assert ltv_by_tier[UserTier.PREMIUM] > ltv_by_tier[UserTier.BASIC]
        assert ltv_by_tier[UserTier.BASIC] > ltv_by_tier[UserTier.FREE]
        
        # Test LTV-based user ranking
        user_ranking = await analytics_system.rank_users_by_ltv(
            top_n=100,
            include_predictions=True
        )
        
        assert len(user_ranking) <= 100
        assert all("ltv_score" in user for user in user_ranking)
        assert all("predicted_churn" in user for user in user_ranking)
    
    async def test_roi_analysis(self, analytics_system):
        """Test return on investment analysis for different business activities."""
        # Define investment scenarios
        investment_scenarios = [
            {
                "campaign_id": "content_protection_campaign",
                "investment_amount": Decimal("10000.00"),
                "campaign_type": "content_protection",
                "start_date": datetime.utcnow() - timedelta(days=30),
                "target_metrics": ["user_acquisition", "revenue_increase"]
            },
            {
                "campaign_id": "collaboration_feature_dev",
                "investment_amount": Decimal("25000.00"),
                "campaign_type": "feature_development", 
                "start_date": datetime.utcnow() - timedelta(days=60),
                "target_metrics": ["collaboration_rate", "user_engagement"]
            }
        ]
        
        roi_results = []
        
        for scenario in investment_scenarios:
            # Record investment
            await analytics_system.record_investment(
                campaign_id=scenario["campaign_id"],
                amount=scenario["investment_amount"],
                campaign_type=scenario["campaign_type"],
                start_date=scenario["start_date"]
            )
            
            # Simulate campaign results
            campaign_duration = (datetime.utcnow() - scenario["start_date"]).days
            
            if scenario["campaign_type"] == "content_protection":
                # Simulate increased user acquisition and revenue
                for day in range(campaign_duration):
                    # New users acquired
                    new_users = np.random.poisson(5)  # Average 5 new users per day
                    for user in range(new_users):
                        await analytics_system.record_user_acquisition(
                            user_id=f"campaign_user_{scenario['campaign_id']}_{day}_{user}",
                            acquisition_source=scenario["campaign_id"],
                            acquisition_cost=scenario["investment_amount"] / (campaign_duration * 5)
                        )
                    
                    # Additional revenue from protection features
                    additional_revenue = np.random.uniform(100, 300)
                    revenue_metrics = RevenueMetrics(
                        user_id=f"campaign_revenue_{day}",
                        revenue_source=RevenueSource.CONTENT_PROTECTION,
                        amount=Decimal(str(additional_revenue)),
                        currency="USD",
                        metadata={"campaign_id": scenario["campaign_id"]}
                    )
                    await analytics_system.record_revenue(revenue_metrics)
            
            # Calculate ROI
            roi_analysis = await analytics_system.calculate_roi(
                campaign_id=scenario["campaign_id"],
                analysis_period=timedelta(days=campaign_duration)
            )
            
            roi_results.append({
                "campaign_id": scenario["campaign_id"],
                "roi": roi_analysis,
                "investment": scenario["investment_amount"]
            })
            
            # Verify ROI calculation
            assert "total_investment" in roi_analysis
            assert "total_return" in roi_analysis
            assert "roi_percentage" in roi_analysis
            assert "payback_period_days" in roi_analysis
            assert "break_even_date" in roi_analysis
            
            # Verify investment tracking
            assert roi_analysis["total_investment"] == scenario["investment_amount"]
        
        # Compare ROI across campaigns
        roi_comparison = await analytics_system.compare_campaign_roi(
            campaign_ids=[scenario["campaign_id"] for scenario in investment_scenarios]
        )
        
        assert "campaign_rankings" in roi_comparison
        assert "roi_summary" in roi_comparison
        assert "recommendations" in roi_comparison


class TestBusinessMetricsReporting:
    """Tests for business metrics reporting and dashboards."""
    
    @pytest.fixture
    async def reporting_system(self):
        """Create reporting-focused metrics system."""
        system = BusinessMetricsCollector(
            config={
                "reporting_enabled": True,
                "dashboard_generation": True,
                "automated_insights": True,
                "executive_summaries": True,
                "drill_down_analysis": True
            }
        )
        await system.initialize()
        yield system
        await system.shutdown()
    
    async def test_executive_dashboard_generation(self, reporting_system, business_scenarios):
        """Test generation of executive-level business dashboards."""
        # Populate system with business data
        for scenario in business_scenarios["executive_scenarios"]:
            # Record various business events
            for event in scenario["events"]:
                if event["type"] == "revenue":
                    revenue_metrics = RevenueMetrics(
                        user_id=event["user_id"],
                        revenue_source=RevenueSource(event["source"]),
                        amount=Decimal(str(event["amount"])),
                        currency=event["currency"]
                    )
                    await reporting_system.record_revenue(revenue_metrics)
                
                elif event["type"] == "engagement":
                    engagement_metrics = UserEngagementMetrics(
                        user_id=event["user_id"],
                        engagement_type=EngagementType(event["engagement_type"]),
                        session_id=event["session_id"],
                        engagement_value=event["value"]
                    )
                    await reporting_system.record_engagement(engagement_metrics)
        
        # Generate executive dashboard
        executive_dashboard = await reporting_system.generate_executive_dashboard(
            time_period=timedelta(days=30),
            include_forecasts=True,
            include_comparisons=True
        )
        
        # Verify dashboard structure
        assert "executive_summary" in executive_dashboard
        assert "key_metrics" in executive_dashboard
        assert "revenue_analytics" in executive_dashboard
        assert "user_analytics" in executive_dashboard
        assert "growth_analytics" in executive_dashboard
        assert "performance_indicators" in executive_dashboard
        
        # Verify executive summary
        summary = executive_dashboard["executive_summary"]
        assert "total_revenue" in summary
        assert "revenue_growth" in summary
        assert "active_users" in summary
        assert "user_growth" in summary
        assert "key_achievements" in summary
        assert "areas_for_improvement" in summary
        
        # Verify key metrics
        key_metrics = executive_dashboard["key_metrics"]
        assert "mrr" in key_metrics  # Monthly Recurring Revenue
        assert "arr" in key_metrics  # Annual Recurring Revenue
        assert "cac" in key_metrics  # Customer Acquisition Cost
        assert "ltv" in key_metrics  # Lifetime Value
        assert "churn_rate" in key_metrics
        assert "nps_score" in key_metrics  # Net Promoter Score
        
        # Verify analytics sections
        revenue_analytics = executive_dashboard["revenue_analytics"]
        assert "revenue_breakdown" in revenue_analytics
        assert "revenue_trends" in revenue_analytics
        assert "revenue_forecast" in revenue_analytics
    
    async def test_operational_reporting(self, reporting_system):
        """Test operational-level reporting and KPI tracking."""
        # Generate operational data
        operational_data = {
            "content_processing": [
                {"date": datetime.utcnow() - timedelta(days=i), "count": 100 + i * 5}
                for i in range(30)
            ],
            "collaboration_requests": [
                {"date": datetime.utcnow() - timedelta(days=i), "count": 20 + i * 2}
                for i in range(30)
            ],
            "user_support_tickets": [
                {"date": datetime.utcnow() - timedelta(days=i), "count": 15 - (i % 5)}
                for i in range(30)
            ]
        }
        
        # Record operational metrics
        for category, data_points in operational_data.items():
            for point in data_points:
                await reporting_system.record_operational_metric(
                    metric_name=category,
                    value=point["count"],
                    timestamp=point["date"]
                )
        
        # Generate operational report
        operational_report = await reporting_system.generate_operational_report(
            report_period=timedelta(days=30),
            include_trends=True,
            include_alerts=True
        )
        
        assert "operational_metrics" in operational_report
        assert "performance_trends" in operational_report
        assert "efficiency_indicators" in operational_report
        assert "bottleneck_analysis" in operational_report
        assert "recommendations" in operational_report
        
        # Verify metrics tracking
        metrics = operational_report["operational_metrics"]
        assert "content_processing" in metrics
        assert "collaboration_requests" in metrics
        assert "user_support_tickets" in metrics
        
        # Verify trend analysis
        trends = operational_report["performance_trends"]
        for metric_name in operational_data.keys():
            assert metric_name in trends
            trend_data = trends[metric_name]
            assert "trend_direction" in trend_data
            assert "trend_strength" in trend_data
            assert "forecast" in trend_data
    
    async def test_automated_insights_generation(self, reporting_system):
        """Test automated insights and anomaly detection in business metrics."""
        # Create data with known patterns and anomalies
        baseline_revenue = 5000
        anomaly_dates = []
        
        for day in range(60):
            date = datetime.utcnow() - timedelta(days=60-day)
            
            # Normal revenue pattern with growth
            daily_revenue = baseline_revenue + (day * 50)
            
            # Inject anomalies
            if day in [20, 45]:  # Revenue spikes
                daily_revenue *= 2.5
                anomaly_dates.append(date)
            elif day in [35]:  # Revenue drop
                daily_revenue *= 0.3
                anomaly_dates.append(date)
            
            # Add normal variation
            daily_revenue += np.random.normal(0, 200)
            
            # Record revenue
            revenue_metrics = RevenueMetrics(
                user_id=f"daily_user_{day}",
                revenue_source=RevenueSource.CONTENT_PROTECTION,
                amount=Decimal(str(max(daily_revenue, 100))),
                currency="USD",
                timestamp=date
            )
            await reporting_system.record_revenue(revenue_metrics)
        
        # Generate automated insights
        insights = await reporting_system.generate_automated_insights(
            analysis_period=timedelta(days=60),
            insight_types=[
                "anomaly_detection",
                "trend_analysis", 
                "pattern_recognition",
                "performance_alerts",
                "optimization_opportunities"
            ]
        )
        
        assert "anomalies_detected" in insights
        assert "trends_identified" in insights
        assert "patterns_recognized" in insights
        assert "alerts_generated" in insights
        assert "optimization_recommendations" in insights
        
        # Verify anomaly detection
        detected_anomalies = insights["anomalies_detected"]
        assert len(detected_anomalies) > 0
        
        # Check if major anomalies were detected
        detected_dates = [anomaly["date"] for anomaly in detected_anomalies]
        overlap = len(set(detected_dates) & set(anomaly_dates))
        assert overlap > 0  # At least some anomalies detected
        
        # Verify trend identification
        trends = insights["trends_identified"]
        assert "revenue_trend" in trends
        assert trends["revenue_trend"]["direction"] == "increasing"
        
        # Verify optimization recommendations
        recommendations = insights["optimization_recommendations"]
        assert len(recommendations) > 0
        assert all("recommendation" in rec for rec in recommendations)
        assert all("impact_estimate" in rec for rec in recommendations)


@pytest.mark.performance
class TestBusinessMetricsPerformance:
    """Performance tests for business metrics system."""
    
    @pytest.fixture
    async def performance_system(self):
        """Create high-performance metrics system."""
        system = BusinessMetricsCollector(
            config={
                "high_performance_mode": True,
                "batch_processing": True,
                "async_aggregation": True,
                "memory_optimization": True,
                "caching_enabled": True
            }
        )
        await system.initialize()
        yield system
        await system.shutdown()
    
    async def test_high_volume_revenue_processing(self, performance_system):
        """Test processing high volume of revenue transactions."""
        # Generate large number of revenue transactions
        transaction_count = 50000
        
        async def generate_revenue_batch(batch_id, batch_size):
            batch_results = []
            
            for i in range(batch_size):
                revenue_metrics = RevenueMetrics(
                    user_id=f"batch_{batch_id}_user_{i}",
                    revenue_source=RevenueSource.CONTENT_PROTECTION,
                    amount=Decimal(str(np.random.uniform(10, 500))),
                    currency="USD"
                )
                
                result = await performance_system.record_revenue(revenue_metrics)
                batch_results.append(result)
            
            return batch_results
        
        # Process transactions in batches
        batch_size = 1000
        num_batches = transaction_count // batch_size
        
        start_time = time.time()
        
        batch_tasks = [
            generate_revenue_batch(batch_id, batch_size)
            for batch_id in range(num_batches)
        ]
        
        batch_results = await asyncio.gather(*batch_tasks)
        
        processing_time = time.time() - start_time
        
        # Verify performance requirements
        assert processing_time < 30.0  # Process 50k transactions in under 30 seconds
        
        # Verify all transactions processed successfully
        total_successful = sum(sum(batch) for batch in batch_results)
        assert total_successful == transaction_count
        
        # Verify system performance metrics
        performance_metrics = await performance_system.get_performance_metrics()
        assert performance_metrics["transactions_per_second"] > 1000
        assert performance_metrics["memory_usage_mb"] < 2000
        assert performance_metrics["error_rate"] < 0.01
    
    async def test_concurrent_analytics_processing(self, performance_system):
        """Test concurrent processing of multiple analytics requests."""
        # Setup test data
        await self._setup_analytics_test_data(performance_system)
        
        # Define concurrent analytics tasks
        analytics_tasks = [
            performance_system.analyze_revenue_trends(timedelta(days=30)),
            performance_system.analyze_user_engagement(timedelta(days=30)),
            performance_system.calculate_growth_rates(["daily_revenue", "weekly_revenue"]),
            performance_system.perform_user_segmentation(["tier_level", "revenue"]),
            performance_system.calculate_lifetime_values(top_users=1000),
            performance_system.analyze_collaboration_effectiveness(timedelta(days=30)),
            performance_system.generate_executive_dashboard(timedelta(days=30)),
            performance_system.generate_operational_report(timedelta(days=30))
        ]
        
        # Execute tasks concurrently
        start_time = time.time()
        
        results = await asyncio.gather(*analytics_tasks, return_exceptions=True)
        
        concurrent_time = time.time() - start_time
        
        # Verify concurrent performance
        assert concurrent_time < 15.0  # Complete all analytics in under 15 seconds
        
        # Verify all tasks completed successfully
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == len(analytics_tasks)
        
        # Verify result quality
        for result in successful_results:
            assert result is not None
            assert isinstance(result, dict)
    
    async def _setup_analytics_test_data(self, system):
        """Setup test data for analytics performance testing."""
        # Generate 30 days of revenue data
        for day in range(30):
            date = datetime.utcnow() - timedelta(days=30-day)
            
            # Generate multiple transactions per day
            for transaction in range(100):
                revenue_metrics = RevenueMetrics(
                    user_id=f"perf_user_{transaction % 50}",
                    revenue_source=RevenueSource.CONTENT_PROTECTION,
                    amount=Decimal(str(np.random.uniform(50, 200))),
                    currency="USD",
                    timestamp=date + timedelta(minutes=transaction * 5)
                )
                await system.record_revenue(revenue_metrics)
        
        # Generate engagement data
        for day in range(30):
            date = datetime.utcnow() - timedelta(days=30-day)
            
            for user in range(50):
                engagement_metrics = UserEngagementMetrics(
                    user_id=f"perf_user_{user}",
                    engagement_type=EngagementType.CONTENT_UPLOAD,
                    session_id=f"session_{day}_{user}",
                    engagement_value=np.random.uniform(0.5, 1.0),
                    timestamp=date
                )
                await system.record_engagement(engagement_metrics)


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        "test_business_metrics.py",
        "-v",
        "--cov=backend.ai.monitoring.business_metrics",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=100"
    ])

import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
import numpy as np

from ai.monitoring.business_metrics import (
    BusinessMetricsCollector,
    RevenueSource,
    UserTier,
    CreatorTier,
    EngagementMetrics,
    RevenueMetrics,
    UserMetrics,
    CreatorMetrics,
    BusinessKPI
)
from .utils import TestDataGenerator, PerformanceValidator

class TestBusinessMetricsCollector:
    """Test suite for Business Metrics Collector."""
    
    @pytest.fixture
    async def metrics_collector(self):
        """Create Business Metrics Collector instance."""
        collector = BusinessMetricsCollector()
        await collector.initialize()
        yield collector
        await collector.shutdown()
    
    @pytest.fixture
    def business_test_data(self):
        """Generate comprehensive business test data."""
        return TestDataGenerator.generate_business_metrics_data(days=30)
    
    async def test_collector_initialization(self, metrics_collector):
        """Test proper initialization of business metrics collector."""
        assert metrics_collector is not None
        assert metrics_collector.is_initialized
        assert metrics_collector.revenue_tracker is not None
        assert metrics_collector.user_analytics is not None
        assert metrics_collector.creator_analytics is not None
        assert metrics_collector.engagement_tracker is not None
    
    async def test_revenue_tracking(self, metrics_collector):
        """Test comprehensive revenue tracking and calculation."""
        # Test various revenue sources
        revenue_data = [
            {
                "source": RevenueSource.SUBSCRIPTION,
                "amount": Decimal("99.99"),
                "user_id": "user_001",
                "transaction_id": "txn_001",
                "timestamp": datetime.utcnow()
            },
            {
                "source": RevenueSource.ADVERTISING,
                "amount": Decimal("25.50"),
                "user_id": "user_002",
                "campaign_id": "ad_campaign_001",
                "timestamp": datetime.utcnow()
            },
            {
                "source": RevenueSource.PREMIUM_FEATURES,
                "amount": Decimal("19.99"),
                "user_id": "user_003",
                "feature_id": "premium_audio_processing",
                "timestamp": datetime.utcnow()
            },
            {
                "source": RevenueSource.COLLABORATION_MATCHING,
                "amount": Decimal("15.00"),
                "creator_id": "creator_001",
                "collaboration_id": "collab_001",
                "timestamp": datetime.utcnow()
            }
        ]
        
        # Record revenue events
        total_expected = Decimal("0")
        for revenue_event in revenue_data:
            await metrics_collector.record_revenue(
                source=revenue_event["source"],
                amount=revenue_event["amount"],
                metadata=revenue_event
            )
            total_expected += revenue_event["amount"]
        
        # Verify revenue tracking
        daily_revenue = await metrics_collector.get_daily_revenue()
        assert daily_revenue is not None
        assert daily_revenue.total_amount >= total_expected
        
        # Test revenue by source
        revenue_by_source = await metrics_collector.get_revenue_by_source(
            time_range=timedelta(hours=1)
        )
        
        assert RevenueSource.SUBSCRIPTION in revenue_by_source
        assert RevenueSource.ADVERTISING in revenue_by_source
        assert RevenueSource.PREMIUM_FEATURES in revenue_by_source
        assert RevenueSource.COLLABORATION_MATCHING in revenue_by_source
        
        # Verify amounts
        assert revenue_by_source[RevenueSource.SUBSCRIPTION] >= Decimal("99.99")
        assert revenue_by_source[RevenueSource.ADVERTISING] >= Decimal("25.50")
    
    async def test_user_engagement_metrics(self, metrics_collector):
        """Test user engagement tracking and analysis."""
        # Simulate user sessions
        user_sessions = [
            {
                "user_id": "user_001",
                "session_start": datetime.utcnow() - timedelta(minutes=30),
                "session_end": datetime.utcnow() - timedelta(minutes=5),
                "pages_viewed": 15,
                "actions_performed": 8,
                "content_consumed": 3,
                "user_tier": UserTier.PREMIUM
            },
            {
                "user_id": "user_002",
                "session_start": datetime.utcnow() - timedelta(minutes=45),
                "session_end": datetime.utcnow() - timedelta(minutes=10),
                "pages_viewed": 25,
                "actions_performed": 12,
                "content_consumed": 5,
                "user_tier": UserTier.PRO
            },
            {
                "user_id": "user_003",
                "session_start": datetime.utcnow() - timedelta(minutes=15),
                "session_end": datetime.utcnow(),
                "pages_viewed": 8,
                "actions_performed": 3,
                "content_consumed": 1,
                "user_tier": UserTier.FREE
            }
        ]
        
        # Record user sessions
        for session in user_sessions:
            session_duration = (session["session_end"] - session["session_start"]).total_seconds()
            
            await metrics_collector.record_user_session(
                user_id=session["user_id"],
                session_duration=session_duration,
                pages_viewed=session["pages_viewed"],
                actions_performed=session["actions_performed"],
                content_consumed=session["content_consumed"],
                user_tier=session["user_tier"],
                timestamp=session["session_start"]
            )
        
        # Verify engagement metrics
        engagement_metrics = await metrics_collector.get_engagement_metrics(
            time_range=timedelta(hours=1)
        )
        
        assert engagement_metrics is not None
        assert engagement_metrics.total_sessions == 3
        assert engagement_metrics.total_page_views == 48
        assert engagement_metrics.total_actions == 23
        assert engagement_metrics.avg_session_duration > 0
        
        # Test engagement by user tier
        tier_engagement = await metrics_collector.get_engagement_by_tier()
        
        assert UserTier.PREMIUM in tier_engagement
        assert UserTier.PRO in tier_engagement
        assert UserTier.FREE in tier_engagement
        
        # Premium users should have higher engagement
        premium_engagement = tier_engagement[UserTier.PREMIUM]
        free_engagement = tier_engagement[UserTier.FREE]
        
        assert premium_engagement["avg_session_duration"] >= free_engagement["avg_session_duration"]
    
    async def test_creator_success_metrics(self, metrics_collector):
        """Test creator success tracking and analytics."""
        # Simulate creator activities
        creator_activities = [
            {
                "creator_id": "creator_001",
                "content_uploads": 5,
                "total_views": 15000,
                "total_likes": 1200,
                "total_shares": 300,
                "collaborations_initiated": 3,
                "collaborations_completed": 2,
                "revenue_generated": Decimal("450.00"),
                "creator_tier": CreatorTier.PROFESSIONAL,
                "timestamp": datetime.utcnow()
            },
            {
                "creator_id": "creator_002",
                "content_uploads": 8,
                "total_views": 8000,
                "total_likes": 600,
                "total_shares": 120,
                "collaborations_initiated": 1,
                "collaborations_completed": 1,
                "revenue_generated": Decimal("180.00"),
                "creator_tier": CreatorTier.EMERGING,
                "timestamp": datetime.utcnow()
            },
            {
                "creator_id": "creator_003",
                "content_uploads": 2,
                "total_views": 2500,
                "total_likes": 180,
                "total_shares": 25,
                "collaborations_initiated": 0,
                "collaborations_completed": 0,
                "revenue_generated": Decimal("35.00"),
                "creator_tier": CreatorTier.BEGINNER,
                "timestamp": datetime.utcnow()
            }
        ]
        
        # Record creator metrics
        for activity in creator_activities:
            await metrics_collector.record_creator_activity(
                creator_id=activity["creator_id"],
                content_uploads=activity["content_uploads"],
                views=activity["total_views"],
                likes=activity["total_likes"],
                shares=activity["total_shares"],
                collaborations=activity["collaborations_completed"],
                revenue=activity["revenue_generated"],
                creator_tier=activity["creator_tier"],
                timestamp=activity["timestamp"]
            )
        
        # Verify creator metrics
        creator_metrics = await metrics_collector.get_creator_metrics(
            time_range=timedelta(hours=1)
        )
        
        assert creator_metrics is not None
        assert creator_metrics.total_creators == 3
        assert creator_metrics.total_content_uploads == 15
        assert creator_metrics.total_views == 25500
        assert creator_metrics.total_revenue >= Decimal("665.00")
        
        # Test creator performance ranking
        top_creators = await metrics_collector.get_top_creators(
            metric="revenue",
            limit=10,
            time_range=timedelta(days=1)
        )
        
        assert len(top_creators) == 3
        assert top_creators[0]["creator_id"] == "creator_001"  # Highest revenue
        assert top_creators[0]["revenue"] >= Decimal("450.00")
        
        # Test creator tier analysis
        tier_performance = await metrics_collector.get_creator_performance_by_tier()
        
        assert CreatorTier.PROFESSIONAL in tier_performance
        assert CreatorTier.EMERGING in tier_performance
        assert CreatorTier.BEGINNER in tier_performance
        
        # Professional creators should have better metrics
        pro_performance = tier_performance[CreatorTier.PROFESSIONAL]
        beginner_performance = tier_performance[CreatorTier.BEGINNER]
        
        assert pro_performance["avg_revenue_per_creator"] > beginner_performance["avg_revenue_per_creator"]
    
    async def test_kpi_calculations(self, metrics_collector):
        """Test business KPI calculations and tracking."""
        # Generate historical data for KPI calculations
        historical_data = TestDataGenerator.generate_business_metrics_data(days=30)
        
        # Record historical revenue data
        for revenue_day in historical_data["revenue"]:
            await metrics_collector.record_revenue(
                source=RevenueSource.SUBSCRIPTION,
                amount=Decimal(str(revenue_day["subscription_revenue"])),
                timestamp=revenue_day["date"]
            )
            await metrics_collector.record_revenue(
                source=RevenueSource.ADVERTISING,
                amount=Decimal(str(revenue_day["advertising_revenue"])),
                timestamp=revenue_day["date"]
            )
        
        # Record user data
        for user_day in historical_data["users"]:
            await metrics_collector.record_daily_users(
                date=user_day["date"],
                total_users=user_day["total_users"],
                active_users=user_day["active_users"],
                new_users=user_day["new_users"]
            )
        
        # Calculate KPIs
        kpis = await metrics_collector.calculate_kpis(
            time_range=timedelta(days=30)
        )
        
        assert kpis is not None
        
        # Verify essential KPIs
        assert "monthly_recurring_revenue" in kpis
        assert "customer_acquisition_cost" in kpis
        assert "lifetime_value" in kpis
        assert "churn_rate" in kpis
        assert "user_growth_rate" in kpis
        assert "revenue_per_user" in kpis
        
        # Validate KPI values
        assert kpis["monthly_recurring_revenue"] > 0
        assert 0 <= kpis["churn_rate"] <= 1
        assert kpis["revenue_per_user"] > 0
        
        # Test KPI trends
        kpi_trends = await metrics_collector.calculate_kpi_trends(
            kpis=["monthly_recurring_revenue", "user_growth_rate"],
            periods=4,  # Weekly trends for last month
            period_type="week"
        )
        
        assert "monthly_recurring_revenue" in kpi_trends
        assert "user_growth_rate" in kpi_trends
        
        for kpi_name, trend_data in kpi_trends.items():
            assert len(trend_data) == 4  # 4 weeks
            assert all("value" in period for period in trend_data)
            assert all("growth_rate" in period for period in trend_data)
    
    async def test_conversion_funnel_analysis(self, metrics_collector):
        """Test conversion funnel tracking and analysis."""
        # Define conversion funnel stages
        funnel_stages = [
            "landing_page_visit",
            "signup_page_view",
            "account_creation",
            "content_upload",
            "first_collaboration",
            "premium_subscription"
        ]
        
        # Simulate user journey data
        user_journeys = []
        base_users = 10000
        
        # Simulate conversion rates at each stage
        conversion_rates = [1.0, 0.3, 0.6, 0.8, 0.4, 0.15]
        
        for i, stage in enumerate(funnel_stages):
            stage_users = int(base_users * np.prod(conversion_rates[:i+1]))
            user_journeys.append({
                "stage": stage,
                "user_count": stage_users,
                "timestamp": datetime.utcnow()
            })
        
        # Record funnel data
        for journey_stage in user_journeys:
            await metrics_collector.record_funnel_stage(
                stage=journey_stage["stage"],
                user_count=journey_stage["user_count"],
                timestamp=journey_stage["timestamp"]
            )
        
        # Analyze conversion funnel
        funnel_analysis = await metrics_collector.analyze_conversion_funnel(
            time_range=timedelta(hours=1)
        )
        
        assert funnel_analysis is not None
        assert "stages" in funnel_analysis
        assert "conversion_rates" in funnel_analysis
        assert "bottlenecks" in funnel_analysis
        
        # Verify funnel stages
        stages = funnel_analysis["stages"]
        assert len(stages) == len(funnel_stages)
        
        # Verify conversion rate calculations
        conversion_rates_calc = funnel_analysis["conversion_rates"]
        
        # First stage should have 100% "conversion" (base)
        assert abs(conversion_rates_calc[0] - 1.0) < 0.01
        
        # Subsequent stages should show progressive conversion
        for i in range(1, len(conversion_rates_calc)):
            assert 0 <= conversion_rates_calc[i] <= 1.0
            assert conversion_rates_calc[i] <= conversion_rates_calc[i-1]
        
        # Identify bottlenecks
        bottlenecks = funnel_analysis["bottlenecks"]
        assert len(bottlenecks) >= 1
        
        # Biggest bottleneck should be identified
        biggest_bottleneck = min(bottlenecks, key=lambda x: x["conversion_rate"])
        assert biggest_bottleneck["stage"] in funnel_stages
    
    async def test_cohort_analysis(self, metrics_collector):
        """Test user cohort analysis and retention tracking."""
        # Generate cohort data
        cohorts = {}
        base_date = datetime.utcnow() - timedelta(days=90)
        
        # Create weekly cohorts for 12 weeks
        for week in range(12):
            cohort_date = base_date + timedelta(weeks=week)
            cohort_size = 1000 + np.random.randint(-100, 200)
            
            cohorts[cohort_date] = {
                "cohort_date": cohort_date,
                "initial_users": cohort_size,
                "retention_by_week": {}
            }
            
            # Simulate retention rates for each week after cohort creation
            for retention_week in range(min(12 - week, 12)):
                base_retention = 0.8  # Start with 80% retention
                retention_decay = 0.05 * retention_week  # 5% decay per week
                retention_rate = max(0.1, base_retention - retention_decay + np.random.uniform(-0.05, 0.05))
                
                retained_users = int(cohort_size * retention_rate)
                cohorts[cohort_date]["retention_by_week"][retention_week] = retained_users
        
        # Record cohort data
        for cohort_date, cohort_data in cohorts.items():
            await metrics_collector.record_user_cohort(
                cohort_date=cohort_date,
                initial_users=cohort_data["initial_users"],
                retention_data=cohort_data["retention_by_week"]
            )
        
        # Analyze cohort retention
        cohort_analysis = await metrics_collector.analyze_cohort_retention(
            time_range=timedelta(days=90)
        )
        
        assert cohort_analysis is not None
        assert "cohorts" in cohort_analysis
        assert "average_retention" in cohort_analysis
        assert "retention_trends" in cohort_analysis
        
        # Verify cohort data
        analyzed_cohorts = cohort_analysis["cohorts"]
        assert len(analyzed_cohorts) == 12
        
        # Verify retention calculations
        avg_retention = cohort_analysis["average_retention"]
        for week, retention in avg_retention.items():
            assert 0 <= retention <= 1
            if week > 0:
                assert retention <= avg_retention.get(week - 1, 1.0)  # Retention should decrease over time
        
        # Test cohort comparison
        cohort_comparison = await metrics_collector.compare_cohorts(
            cohort_dates=[
                base_date,
                base_date + timedelta(weeks=6),
                base_date + timedelta(weeks=11)
            ]
        )
        
        assert cohort_comparison is not None
        assert len(cohort_comparison) == 3
    
    async def test_revenue_forecasting(self, metrics_collector):
        """Test revenue forecasting capabilities."""
        # Generate historical revenue data with trends
        historical_revenue = []
        base_date = datetime.utcnow() - timedelta(days=180)
        base_revenue = 10000
        
        for day in range(180):
            date = base_date + timedelta(days=day)
            
            # Add growth trend
            growth_factor = 1 + (day * 0.001)  # 0.1% daily growth
            
            # Add seasonal patterns (weekly and monthly)
            weekly_pattern = 1 + 0.1 * np.sin(2 * np.pi * day / 7)
            monthly_pattern = 1 + 0.05 * np.sin(2 * np.pi * day / 30)
            
            # Add noise
            noise_factor = 1 + np.random.uniform(-0.1, 0.1)
            
            daily_revenue = base_revenue * growth_factor * weekly_pattern * monthly_pattern * noise_factor
            
            historical_revenue.append({
                "date": date,
                "revenue": Decimal(str(round(daily_revenue, 2)))
            })
        
        # Record historical revenue
        for revenue_day in historical_revenue:
            await metrics_collector.record_revenue(
                source=RevenueSource.SUBSCRIPTION,
                amount=revenue_day["revenue"],
                timestamp=revenue_day["date"]
            )
        
        # Generate revenue forecast
        forecast = await metrics_collector.forecast_revenue(
            forecast_days=30,
            confidence_interval=0.95,
            model_type="arima"
        )
        
        assert forecast is not None
        assert "predictions" in forecast
        assert "confidence_bounds" in forecast
        assert "model_metrics" in forecast
        
        # Verify forecast output
        predictions = forecast["predictions"]
        confidence_bounds = forecast["confidence_bounds"]
        
        assert len(predictions) == 30
        assert len(confidence_bounds["lower"]) == 30
        assert len(confidence_bounds["upper"]) == 30
        
        # Confidence bounds should be reasonable
        for i in range(30):
            assert confidence_bounds["lower"][i] <= predictions[i] <= confidence_bounds["upper"][i]
        
        # Test forecast accuracy metrics
        model_metrics = forecast["model_metrics"]
        assert "mape" in model_metrics  # Mean Absolute Percentage Error
        assert "rmse" in model_metrics  # Root Mean Square Error
        assert "r_squared" in model_metrics
        
        # MAPE should be reasonable for business forecasting
        assert model_metrics["mape"] < 20.0  # Less than 20% error
    
    async def test_business_intelligence_dashboard(self, metrics_collector):
        """Test business intelligence dashboard data generation."""
        # Generate comprehensive business data
        business_data = TestDataGenerator.generate_business_metrics_data(days=30)
        
        # Record all business data
        for day_data in zip(
            business_data["revenue"],
            business_data["users"],
            business_data["creators"],
            business_data["engagement"]
        ):
            revenue_data, user_data, creator_data, engagement_data = day_data
            
            # Record revenue
            await metrics_collector.record_revenue(
                source=RevenueSource.SUBSCRIPTION,
                amount=Decimal(str(revenue_data["subscription_revenue"])),
                timestamp=revenue_data["date"]
            )
            
            # Record user metrics
            await metrics_collector.record_daily_users(
                date=user_data["date"],
                total_users=user_data["total_users"],
                active_users=user_data["active_users"],
                new_users=user_data["new_users"]
            )
            
            # Record creator metrics
            await metrics_collector.record_creator_activity(
                creator_id="aggregate",
                content_uploads=creator_data["content_uploads"],
                views=100000,  # Aggregate views
                likes=8000,    # Aggregate likes
                shares=1500,   # Aggregate shares
                collaborations=creator_data["collaborations"],
                revenue=Decimal("1000.00"),  # Aggregate creator revenue
                timestamp=creator_data["date"]
            )
        
        # Generate dashboard data
        dashboard_data = await metrics_collector.generate_dashboard_data(
            time_range=timedelta(days=30)
        )
        
        assert dashboard_data is not None
        
        # Verify dashboard components
        assert "kpis" in dashboard_data
        assert "charts" in dashboard_data
        assert "trends" in dashboard_data
        assert "alerts" in dashboard_data
        
        # Verify KPI cards
        kpis = dashboard_data["kpis"]
        essential_kpis = [
            "total_revenue",
            "active_users",
            "conversion_rate",
            "churn_rate",
            "customer_lifetime_value"
        ]
        
        for kpi in essential_kpis:
            assert kpi in kpis
            assert "value" in kpis[kpi]
            assert "change" in kpis[kpi]
            assert "trend" in kpis[kpi]
        
        # Verify chart data
        charts = dashboard_data["charts"]
        expected_charts = [
            "revenue_trend",
            "user_growth",
            "creator_activity",
            "conversion_funnel",
            "retention_cohorts"
        ]
        
        for chart in expected_charts:
            assert chart in charts
            assert "data" in charts[chart]
            assert "config" in charts[chart]
    
    async def test_real_time_metrics_streaming(self, metrics_collector):
        """Test real-time business metrics streaming."""
        # Set up real-time metrics streaming
        streaming_metrics = []
        
        async def metrics_callback(metric_data):
            streaming_metrics.append(metric_data)
        
        await metrics_collector.start_real_time_streaming(
            callback=metrics_callback,
            interval_seconds=0.1,
            metrics=["revenue", "active_users", "conversions"]
        )
        
        # Generate real-time events
        events = [
            {"type": "revenue", "amount": Decimal("99.99"), "source": "subscription"},
            {"type": "user_action", "user_id": "user_001", "action": "content_upload"},
            {"type": "conversion", "user_id": "user_002", "from_stage": "trial", "to_stage": "premium"},
            {"type": "revenue", "amount": Decimal("19.99"), "source": "premium_features"},
            {"type": "user_action", "user_id": "user_003", "action": "collaboration_request"}
        ]
        
        # Send events
        for event in events:
            if event["type"] == "revenue":
                await metrics_collector.record_revenue(
                    source=RevenueSource(event["source"]),
                    amount=event["amount"]
                )
            elif event["type"] == "conversion":
                await metrics_collector.record_conversion(
                    user_id=event["user_id"],
                    from_stage=event["from_stage"],
                    to_stage=event["to_stage"]
                )
            
            await asyncio.sleep(0.1)
        
        # Stop streaming
        await metrics_collector.stop_real_time_streaming()
        
        # Verify streaming data
        assert len(streaming_metrics) >= len([e for e in events if e["type"] in ["revenue", "conversion"]])
        
        # Verify metric data structure
        for metric in streaming_metrics:
            assert "timestamp" in metric
            assert "metric_type" in metric
            assert "value" in metric
            assert "metadata" in metric
    
    async def test_performance_optimization(self, metrics_collector):
        """Test business metrics collection performance and optimization."""
        # Performance test with high-volume data
        start_time = datetime.utcnow()
        
        # Generate high volume of metrics
        revenue_events = 1000
        user_events = 5000
        
        # Test revenue recording performance
        revenue_start = datetime.utcnow()
        
        revenue_tasks = []
        for i in range(revenue_events):
            task = metrics_collector.record_revenue(
                source=RevenueSource.SUBSCRIPTION,
                amount=Decimal("9.99"),
                metadata={"batch_id": f"batch_{i // 100}"}
            )
            revenue_tasks.append(task)
        
        await asyncio.gather(*revenue_tasks)
        revenue_duration = (datetime.utcnow() - revenue_start).total_seconds()
        
        # Test user metrics recording performance
        user_start = datetime.utcnow()
        
        user_tasks = []
        for i in range(user_events):
            task = metrics_collector.record_user_session(
                user_id=f"user_{i:06d}",
                session_duration=1800,
                pages_viewed=10,
                actions_performed=5,
                content_consumed=2,
                user_tier=UserTier.FREE
            )
            user_tasks.append(task)
        
        await asyncio.gather(*user_tasks)
        user_duration = (datetime.utcnow() - user_start).total_seconds()
        
        total_duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Verify performance requirements
        revenue_rate = revenue_events / revenue_duration
        user_rate = user_events / user_duration
        total_rate = (revenue_events + user_events) / total_duration
        
        # Should handle at least 100 events per second
        assert revenue_rate >= 100
        assert user_rate >= 100
        assert total_rate >= 100
        
        # Test query performance
        query_start = datetime.utcnow()
        
        # Complex aggregation query
        metrics_summary = await metrics_collector.get_comprehensive_metrics(
            time_range=timedelta(hours=1),
            include_trends=True,
            include_comparisons=True
        )
        
        query_duration = (datetime.utcnow() - query_start).total_seconds()
        
        # Complex queries should complete within reasonable time
        assert query_duration < 2.0  # Less than 2 seconds
        assert metrics_summary is not None
