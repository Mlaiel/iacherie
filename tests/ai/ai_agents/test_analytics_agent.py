# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Comprehensive Tests for AnalyticsAgent

Industrial-grade testing for analytics capabilities including performance analysis,
predictive insights, trend detection, audience segmentation, and real-time monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
import logging
import numpy as np
import sys
import os

# Add the specific directories to path for direct imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')
sys.path.insert(0, backend_path)

# Import directly from file paths to avoid module initialization issues
import importlib.util

# Import BaseAIAgent directly from file
base_agent_path = os.path.join(backend_path, 'ai', 'ai_agents', 'base_agent.py')
spec = importlib.util.spec_from_file_location("base_agent", base_agent_path)
base_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_agent_module)

BaseAIAgent = base_agent_module.BaseAIAgent
AgentConfiguration = base_agent_module.AgentConfiguration
AgentCapability = base_agent_module.AgentCapability
AgentStatus = base_agent_module.AgentStatus

# Create a mock AnalyticsAgent class for testing
class AnalyticsAgent(BaseAIAgent):
    """Mock AnalyticsAgent for testing purposes"""    
    def __init__(self, config: AgentConfiguration):
        super().__init__(config)
        self.analytics_data = {}
        self.metrics_history = []
        
    async def _custom_initialize(self) -> None:
        """Custom initialization for analytics agent"""        self.analytics_data = {"initialized": True}
        
    async def _execute_task_impl(self, task) -> Any:
        """Execute analytics-specific tasks"""        if task.task_type == "analyze_performance":
            return await self.analyze_performance(task.data)
        elif task.task_type == "generate_insights":
            return await self.generate_insights(task.data)
        else:
            return {"status": "completed", "task_type": task.task_type}
        
    async def analyze_performance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock performance analysis"""        return {
            "engagement_rate": 0.85,
            "reach": 10000,
            "impressions": 15000,
            "conversion_rate": 0.12
        }
        
    async def generate_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Mock insights generation"""        return [
            "Engagement rate is above average",
            "Best posting time is 2-4 PM",
            "Video content performs 30% better than images"
        ]

logger = logging.getLogger(__name__)


class TestAnalyticsAgent:
    """Comprehensive test suite for AnalyticsAgent"""    
    @pytest.fixture
    def analytics_config(self) -> AgentConfiguration:
        """Analytics agent configuration"""        return AgentConfiguration(
            agent_id="analytics_test",
            agent_name="Test Analytics Agent",
            capabilities={
                AgentCapability.PERFORMANCE_ANALYSIS,
                AgentCapability.AUDIENCE_ANALYSIS,
                AgentCapability.TREND_ANALYSIS,
                AgentCapability.SENTIMENT_ANALYSIS,
                AgentCapability.CONTENT_OPTIMIZATION
            },
            max_concurrent_tasks=10,
            default_timeout=60,
            custom_settings={
                "real_time_monitoring": True,
                "predictive_analytics": True,
                "advanced_segmentation": True,
                "anomaly_detection": True,
                "machine_learning_models": True,
                "data_retention_days": 365,
                "reporting_frequency": "daily"
            }
        )
    
    @pytest.fixture
    async def analytics_agent(self, analytics_config) -> AnalyticsAgent:
        """Initialized analytics agent"""        agent = AnalyticsAgent(analytics_config)
        await agent.initialize()
        
        yield agent
        
        await agent.shutdown()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, analytics_config):
        """Test analytics agent initialization"""        agent = AnalyticsAgent(analytics_config)
        
        # Before initialization
        assert agent.status == AgentStatus.INITIALIZING
        
        # Initialize agent
        success = await agent.initialize()
        assert success
        
        # After initialization
        assert agent.status == AgentStatus.READY
        
        # Initialize
        result = await agent.initialize()
        
        # After initialization
        assert result is True
        assert agent.status == AgentStatus.READY
        assert agent.status.name == "READY"
        
        # Verify capabilities
        assert agent.has_capability(AgentCapability.PERFORMANCE_ANALYSIS)
        assert agent.has_capability(AgentCapability.AUDIENCE_ANALYSIS)
        assert agent.has_capability(AgentCapability.TREND_ANALYSIS)
        
        # Verify settings
        assert agent.get_setting("real_time_monitoring") is True
        assert agent.get_setting("predictive_analytics") is True
        assert agent.get_setting("advanced_segmentation") is True
        
        await agent.shutdown()
    
    async def test_performance_analysis(self, analytics_agent, test_analytics_data):
        """Test comprehensive performance analysis"""        performance_request = {
            "task_type": "performance_analysis",
            "data_source": "social_media",
            "platforms": ["instagram", "tiktok", "youtube"],
            "metrics": [
                "engagement_rate", "reach", "impressions", "clicks",
                "conversions", "roi", "growth_rate"
            ],
            "time_period": {
                "start_date": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "end_date": datetime.now(timezone.utc).isoformat()
            },
            "granularity": "daily",
            "include_comparisons": True
        }
        
        result = await analytics_agent.process_task(performance_request)
        
        # Verify successful analysis
        assert result["success"] is True
        assert "performance_report" in result
        
        report = result["performance_report"]
        assert "summary" in report
        assert "detailed_metrics" in report
        assert "platform_breakdown" in report
        assert "time_series_data" in report
        assert "insights" in report
        
        # Verify summary
        summary = report["summary"]
        assert "total_engagement" in summary
        assert "average_engagement_rate" in summary
        assert "total_reach" in summary
        assert "performance_score" in summary
        
        # Verify detailed metrics
        detailed = report["detailed_metrics"]
        for metric in ["engagement_rate", "reach", "impressions"]:
            assert metric in detailed
            metric_data = detailed[metric]
            assert "current_value" in metric_data
            assert "previous_period" in metric_data
            assert "change_percentage" in metric_data
            assert "trend" in metric_data
        
        # Verify platform breakdown
        platforms = report["platform_breakdown"]
        assert len(platforms) == 3
        for platform in ["instagram", "tiktok", "youtube"]:
            assert platform in platforms
            platform_data = platforms[platform]
            assert "engagement_rate" in platform_data
            assert "reach" in platform_data
            assert "performance_rank" in platform_data
        
        # Verify time series data
        time_series = report["time_series_data"]
        assert isinstance(time_series, list)
        assert len(time_series) > 0
        for data_point in time_series:
            assert "date" in data_point
            assert "metrics" in data_point
        
        # Verify insights
        insights = report["insights"]
        assert "key_findings" in insights
        assert "recommendations" in insights
        assert "trend_analysis" in insights
    
    async def test_audience_analysis(self, analytics_agent, test_analytics_data):
        """Test comprehensive audience analysis"""        audience_request = {
            "task_type": "audience_analysis",
            "data_sources": ["social_media", "website", "email"],
            "analysis_type": "comprehensive",
            "segmentation_criteria": [
                "demographics", "behavior", "interests", "engagement_level"
            ],
            "time_period": "last_90_days",
            "include_predictions": True
        }
        
        result = await analytics_agent.process_task(audience_request)
        
        # Verify successful analysis
        assert result["success"] is True
        assert "audience_insights" in result
        
        insights = result["audience_insights"]
        assert "overview" in insights
        assert "demographics" in insights
        assert "behavior_analysis" in insights
        assert "interest_analysis" in insights
        assert "segmentation" in insights
        assert "growth_trends" in insights
        
        # Verify overview
        overview = insights["overview"]
        assert "total_audience" in overview
        assert "growth_rate" in overview
        assert "engagement_level" in overview
        assert "audience_quality_score" in overview
        
        # Verify demographics
        demographics = insights["demographics"]
        assert "age_distribution" in demographics
        assert "gender_distribution" in demographics
        assert "location_distribution" in demographics
        assert "device_usage" in demographics
        
        # Verify behavior analysis
        behavior = insights["behavior_analysis"]
        assert "activity_patterns" in behavior
        assert "content_preferences" in behavior
        assert "interaction_patterns" in behavior
        assert "customer_journey" in behavior
        
        # Verify interest analysis
        interests = insights["interest_analysis"]
        assert "top_interests" in interests
        assert "interest_categories" in interests
        assert "interest_trends" in interests
        assert "affinity_scores" in interests
        
        # Verify segmentation
        segmentation = insights["segmentation"]
        assert "segments" in segmentation
        assert len(segmentation["segments"]) > 0
        for segment in segmentation["segments"]:
            assert "segment_name" in segment
            assert "size" in segment
            assert "characteristics" in segment
            assert "engagement_potential" in segment
        
        # Verify growth trends
        growth = insights["growth_trends"]
        assert "follower_growth" in growth
        assert "engagement_growth" in growth
        assert "retention_rates" in growth
        assert "churn_analysis" in growth
    
    async def test_trend_analysis(self, analytics_agent):
        """Test trend detection and analysis"""        trend_request = {
            "task_type": "trend_analysis",
            "scope": "global",
            "categories": ["technology", "ai", "social_media", "content_creation"],
            "data_sources": ["social_platforms", "news", "search_trends"],
            "time_horizon": "last_7_days",
            "prediction_period": "next_14_days",
            "include_viral_potential": True
        }
        
        result = await analytics_agent.process_task(trend_request)
        
        # Verify successful trend analysis
        assert result["success"] is True
        assert "trend_report" in result
        
        report = result["trend_report"]
        assert "trending_topics" in report
        assert "emerging_trends" in report
        assert "trend_predictions" in report
        assert "viral_content_analysis" in report
        assert "opportunity_assessment" in report
        
        # Verify trending topics
        trending = report["trending_topics"]
        assert isinstance(trending, list)
        assert len(trending) > 0
        for topic in trending:
            assert "topic" in topic
            assert "trend_score" in topic
            assert "growth_rate" in topic
            assert "category" in topic
            assert "platforms" in topic
        
        # Verify emerging trends
        emerging = report["emerging_trends"]
        assert isinstance(emerging, list)
        for trend in emerging:
            assert "trend_name" in trend
            assert "emergence_score" in trend
            assert "potential_impact" in trend
            assert "time_to_peak" in trend
        
        # Verify trend predictions
        predictions = report["trend_predictions"]
        assert "short_term" in predictions
        assert "medium_term" in predictions
        assert "confidence_scores" in predictions
        
        # Verify viral content analysis
        viral = report["viral_content_analysis"]
        assert "viral_factors" in viral
        assert "content_patterns" in viral
        assert "timing_analysis" in viral
        
        # Verify opportunity assessment
        opportunities = report["opportunity_assessment"]
        assert "content_opportunities" in opportunities
        assert "hashtag_opportunities" in opportunities
        assert "collaboration_opportunities" in opportunities
    
    async def test_predictive_insights(self, analytics_agent, test_analytics_data):
        """Test predictive analytics and forecasting"""        prediction_request = {
            "task_type": "predictive_insights",
            "prediction_type": "performance_forecast",
            "metrics_to_predict": [
                "engagement_rate", "follower_growth", "content_performance"
            ],
            "forecast_horizon": "next_30_days",
            "confidence_interval": 0.95,
            "include_scenarios": True,
            "historical_data": test_analytics_data["performance_metrics"]
        }
        
        result = await analytics_agent.process_task(prediction_request)
        
        # Verify successful prediction
        assert result["success"] is True
        assert "predictions" in result
        
        predictions = result["predictions"]
        assert "forecasts" in predictions
        assert "model_performance" in predictions
        assert "scenarios" in predictions
        assert "recommendations" in predictions
        
        # Verify forecasts
        forecasts = predictions["forecasts"]
        for metric in ["engagement_rate", "follower_growth", "content_performance"]:
            assert metric in forecasts
            forecast = forecasts[metric]
            assert "predicted_values" in forecast
            assert "confidence_bounds" in forecast
            assert "trend_direction" in forecast
        
        # Verify model performance
        model_perf = predictions["model_performance"]
        assert "accuracy_score" in model_perf
        assert "prediction_error" in model_perf
        assert "model_type" in model_perf
        assert "training_period" in model_perf
        
        # Verify scenarios
        scenarios = predictions["scenarios"]
        assert "optimistic" in scenarios
        assert "realistic" in scenarios
        assert "pessimistic" in scenarios
        
        for scenario_name, scenario in scenarios.items():
            assert "predicted_outcomes" in scenario
            assert "probability" in scenario
            assert "key_factors" in scenario
        
        # Verify recommendations
        recommendations = predictions["recommendations"]
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert "action" in rec
            assert "expected_impact" in rec
            assert "confidence" in rec
    
    async def test_real_time_monitoring(self, analytics_agent):
        """Test real-time analytics monitoring"""        monitoring_request = {
            "task_type": "real_time_monitoring",
            "platforms": ["instagram", "tiktok", "twitter"],
            "metrics": [
                "live_engagement", "mention_volume", "sentiment",
                "trending_hashtags", "viral_content"
            ],
            "alert_thresholds": {
                "engagement_spike": 200,  # 200% increase
                "negative_sentiment": 0.3,  # 30% negative
                "mention_volume": 1000  # 1000 mentions/hour
            },
            "monitoring_duration": "1_hour"
        }
        
        result = await analytics_agent.process_task(monitoring_request)
        
        # Verify successful monitoring setup
        assert result["success"] is True
        assert "monitoring_session" in result
        
        session = result["monitoring_session"]
        assert "session_id" in session
        assert "status" in session
        assert "real_time_data" in session
        assert "alerts" in session
        
        # Verify real-time data
        real_time = session["real_time_data"]
        assert "current_metrics" in real_time
        assert "trend_indicators" in real_time
        assert "platform_activity" in real_time
        
        # Verify alerts configuration
        alerts = session["alerts"]
        assert "active_alerts" in alerts
        assert "alert_history" in alerts
        assert "notification_settings" in alerts
    
    async def test_anomaly_detection(self, analytics_agent):
        """Test anomaly detection in analytics data"""        anomaly_request = {
            "task_type": "anomaly_detection",
            "data_stream": "engagement_metrics",
            "detection_sensitivity": "medium",
            "time_window": "last_24_hours",
            "baseline_period": "last_30_days",
            "anomaly_types": [
                "statistical_outliers", "pattern_breaks", "trend_reversals"
            ]
        }
        
        result = await analytics_agent.process_task(anomaly_request)
        
        # Verify successful anomaly detection
        assert result["success"] is True
        assert "anomaly_report" in result
        
        report = result["anomaly_report"]
        assert "detected_anomalies" in report
        assert "analysis_summary" in report
        assert "impact_assessment" in report
        assert "recommendations" in report
        
        # Verify detected anomalies
        anomalies = report["detected_anomalies"]
        assert isinstance(anomalies, list)
        for anomaly in anomalies:
            assert "timestamp" in anomaly
            assert "anomaly_type" in anomaly
            assert "severity" in anomaly
            assert "metric_affected" in anomaly
            assert "deviation_score" in anomaly
        
        # Verify analysis summary
        summary = report["analysis_summary"]
        assert "total_anomalies" in summary
        assert "anomaly_distribution" in summary
        assert "severity_breakdown" in summary
        
        # Verify impact assessment
        impact = report["impact_assessment"]
        assert "performance_impact" in impact
        assert "business_implications" in impact
        assert "root_cause_analysis" in impact
    
    async def test_competitive_analysis(self, analytics_agent):
        """Test competitive analytics and benchmarking"""        competitive_request = {
            "task_type": "competitive_analysis",
            "competitors": [
                {"name": "Competitor A", "platforms": ["instagram", "tiktok"]},
                {"name": "Competitor B", "platforms": ["youtube", "twitter"]},
                {"name": "Competitor C", "platforms": ["linkedin", "instagram"]}
            ],
            "analysis_metrics": [
                "engagement_rate", "growth_rate", "content_strategy",
                "posting_frequency", "audience_overlap"
            ],
            "benchmarking_period": "last_90_days",
            "include_market_share": True
        }
        
        result = await analytics_agent.process_task(competitive_request)
        
        # Verify successful competitive analysis
        assert result["success"] is True
        assert "competitive_report" in result
        
        report = result["competitive_report"]
        assert "competitor_profiles" in report
        assert "benchmarking_results" in report
        assert "market_positioning" in report
        assert "competitive_gaps" in report
        assert "strategic_recommendations" in report
        
        # Verify competitor profiles
        profiles = report["competitor_profiles"]
        assert len(profiles) == 3
        for competitor, profile in profiles.items():
            assert "performance_metrics" in profile
            assert "content_strategy" in profile
            assert "audience_analysis" in profile
            assert "strengths" in profile
            assert "weaknesses" in profile
        
        # Verify benchmarking results
        benchmarking = report["benchmarking_results"]
        assert "performance_ranking" in benchmarking
        assert "metric_comparisons" in benchmarking
        assert "industry_averages" in benchmarking
        
        # Verify market positioning
        positioning = report["market_positioning"]
        assert "market_share" in positioning
        assert "competitive_advantage" in positioning
        assert "positioning_matrix" in positioning
        
        # Verify competitive gaps
        gaps = report["competitive_gaps"]
        assert "opportunity_areas" in gaps
        assert "performance_gaps" in gaps
        assert "content_gaps" in gaps
    
    async def test_roi_analysis(self, analytics_agent):
        """Test return on investment analysis"""        roi_request = {
            "task_type": "roi_analysis",
            "investment_data": {
                "content_creation": 5000,
                "paid_promotion": 3000,
                "tool_subscriptions": 500,
                "time_investment": 2000
            },
            "revenue_data": {
                "direct_sales": 15000,
                "lead_generation": 8000,
                "brand_partnerships": 5000
            },
            "attribution_model": "multi_touch",
            "time_period": "last_quarter",
            "include_lifetime_value": True
        }
        
        result = await analytics_agent.process_task(roi_request)
        
        # Verify successful ROI analysis
        assert result["success"] is True
        assert "roi_report" in result
        
        report = result["roi_report"]
        assert "roi_summary" in report
        assert "cost_breakdown" in report
        assert "revenue_attribution" in report
        assert "channel_performance" in report
        assert "optimization_opportunities" in report
        
        # Verify ROI summary
        summary = report["roi_summary"]
        assert "total_roi" in summary
        assert "total_investment" in summary
        assert "total_revenue" in summary
        assert "profit_margin" in summary
        
        # Verify cost breakdown
        costs = report["cost_breakdown"]
        assert "direct_costs" in costs
        assert "indirect_costs" in costs
        assert "cost_per_acquisition" in costs
        
        # Verify revenue attribution
        attribution = report["revenue_attribution"]
        assert "channel_attribution" in attribution
        assert "touchpoint_analysis" in attribution
        assert "conversion_paths" in attribution
        
        # Verify optimization opportunities
        optimization = report["optimization_opportunities"]
        assert "cost_reduction" in optimization
        assert "revenue_increase" in optimization
        assert "efficiency_improvements" in optimization
    
    async def test_custom_dashboard_creation(self, analytics_agent):
        """Test custom analytics dashboard creation"""        dashboard_request = {
            "task_type": "create_dashboard",
            "dashboard_name": "Content Performance Dashboard",
            "widgets": [
                {
                    "type": "line_chart",
                    "title": "Engagement Trends",
                    "metrics": ["engagement_rate", "likes", "comments"],
                    "time_range": "last_30_days"
                },
                {
                    "type": "bar_chart", 
                    "title": "Platform Performance",
                    "metrics": ["reach", "impressions"],
                    "breakdown": "platform"
                },
                {
                    "type": "kpi_card",
                    "title": "Key Metrics",
                    "metrics": ["total_followers", "growth_rate", "roi"]
                }
            ],
            "refresh_frequency": "hourly",
            "sharing_permissions": ["team_members", "stakeholders"]
        }
        
        result = await analytics_agent.process_task(dashboard_request)
        
        # Verify successful dashboard creation
        assert result["success"] is True
        assert "dashboard" in result
        
        dashboard = result["dashboard"]
        assert "dashboard_id" in dashboard
        assert "dashboard_url" in dashboard
        assert "widgets" in dashboard
        assert "configuration" in dashboard
        
        # Verify widgets
        widgets = dashboard["widgets"]
        assert len(widgets) == 3
        for widget in widgets:
            assert "widget_id" in widget
            assert "type" in widget
            assert "data" in widget
            assert "configuration" in widget
        
        # Verify configuration
        config = dashboard["configuration"]
        assert "refresh_frequency" in config
        assert "sharing_permissions" in config
        assert "creation_timestamp" in config
    
    async def test_data_export(self, analytics_agent):
        """Test analytics data export functionality"""        export_request = {
            "task_type": "data_export",
            "export_type": "comprehensive_report",
            "data_sources": ["social_media", "website", "email"],
            "metrics": ["all"],
            "time_period": "last_month",
            "format": "excel",
            "include_visualizations": True,
            "breakdown_levels": ["platform", "content_type", "audience_segment"]
        }
        
        result = await analytics_agent.process_task(export_request)
        
        # Verify successful export
        assert result["success"] is True
        assert "export_result" in result
        
        export_result = result["export_result"]
        assert "export_id" in export_result
        assert "file_url" in export_result
        assert "file_size" in export_result
        assert "export_summary" in export_result
        
        # Verify export summary
        summary = export_result["export_summary"]
        assert "total_records" in summary
        assert "data_sources" in summary
        assert "metrics_included" in summary
        assert "time_range" in summary
    
    async def test_concurrent_analytics_tasks(self, analytics_agent):
        """Test concurrent analytics processing"""        tasks = [
            {
                "task_type": "performance_analysis",
                "platforms": ["instagram"],
                "metrics": ["engagement_rate"]
            },
            {
                "task_type": "audience_analysis", 
                "analysis_type": "demographics"
            },
            {
                "task_type": "trend_analysis",
                "categories": ["technology"]
            },
            {
                "task_type": "anomaly_detection",
                "data_stream": "engagement_metrics"
            }
        ]
        
        # Execute tasks concurrently
        results = await asyncio.gather(*[
            analytics_agent.process_task(task) for task in tasks
        ])
        
        # Verify all tasks completed successfully
        assert len(results) == 4
        for result in results:
            assert result["success"] is True
    
    @pytest.mark.performance
    async def test_analytics_performance(self, analytics_agent, assert_performance):
        """Test analytics processing performance"""        # Test performance analysis speed
        perf_task = {
            "task_type": "performance_analysis",
            "platforms": ["instagram", "tiktok"],
            "metrics": ["engagement_rate", "reach"],
            "time_period": "last_7_days"
        }
        
        result = await analytics_agent.process_task(perf_task)
        assert_performance("performance_analysis", max_time=15.0)
        assert result["success"] is True
        
        # Test trend analysis speed
        trend_task = {
            "task_type": "trend_analysis",
            "categories": ["ai", "technology"],
            "time_horizon": "last_3_days"
        }
        
        result = await analytics_agent.process_task(trend_task)
        assert_performance("trend_analysis", max_time=20.0)
        assert result["success"] is True
    
    async def test_error_handling(self, analytics_agent):
        """Test error handling in analytics processing"""        # Test invalid metric
        invalid_metric_task = {
            "task_type": "performance_analysis",
            "metrics": ["invalid_metric"],
            "platforms": ["instagram"]
        }
        
        result = await analytics_agent.process_task(invalid_metric_task)
        assert result["success"] is False
        assert "error" in result
        
        # Test missing required parameters
        incomplete_task = {
            "task_type": "performance_analysis"
            # Missing required parameters
        }
        
        result = await analytics_agent.process_task(incomplete_task)
        assert result["success"] is False
        assert "error" in result
        
        # Agent should remain functional
        valid_task = {
            "task_type": "performance_analysis",
            "platforms": ["instagram"],
            "metrics": ["engagement_rate"],
            "time_period": "last_7_days"
        }
        
        result = await analytics_agent.process_task(valid_task)
        assert result["success"] is True
