"""Tests for Individual Analytics Agents

Test each of the 6 analytics agents individually.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from ai_agents.user_behavior_agent import (
    UserBehaviorAgent,
    BehaviorAnalysisRequest,
    BehaviorAnalysisResult,
    UserSegmentType,
    BehaviorPatternType
)
from ai_agents.performance_metrics_agent import (
    PerformanceMetricsAgent,
    PerformanceMetricsRequest,
    PerformanceMetricsResult,
    MetricType,
    AlertSeverity
)
from ai_agents.sentiment_analysis_agent import (
    SentimentAnalysisAgent,
    SentimentAnalysisRequest,
    SentimentAnalysisResult,
    SentimentType,
    ContentType
)
from ai_agents.business_intelligence_agent import (
    BusinessIntelligenceAgent,
    BusinessIntelligenceRequest,
    BusinessIntelligenceResult,
    BusinessMetricType,
    DashboardType
)


class TestUserBehaviorAgent:
    """
Test User Behavior Agent."""
    
    @pytest.fixture
    def agent(self):
        """
Create user behavior agent instance."""
        return UserBehaviorAgent()
    
    @pytest.fixture
    def behavior_request(self):
        """
Create behavior analysis request."""
        return BehaviorAnalysisRequest(
            user_ids=["user_123", "user_456"],
            pattern_types=[BehaviorPatternType.ENGAGEMENT, BehaviorPatternType.CONTENT_CONSUMPTION],
            include_predictions=True,
            include_segmentation=True,
            include_recommendations=True
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.agent_name == "User Behavior Agent"
        assert agent.agent_version == "1.0.0"
        assert hasattr(agent, 'behavior_collector')
        assert hasattr(agent, '_analysis_cache')
    
    @pytest.mark.asyncio
    async def test_analyze_user_behavior(self, agent, behavior_request):
        """Test user behavior analysis."""
        result = await agent.analyze_user_behavior(behavior_request)
        
        assert isinstance(result, BehaviorAnalysisResult)
        assert result.analysis_id is not None
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.user_segments, list)
        assert isinstance(result.predictions, list)
        assert isinstance(result.insights, dict)
        assert isinstance(result.recommendations, list)
        
        # Check user segments
        for segment in result.user_segments:
            assert hasattr(segment, 'segment')
            assert isinstance(segment.segment, UserSegmentType)
            assert segment.user_count > 0
            assert 0.0 <= segment.engagement_score <= 10.0
            assert 0.0 <= segment.retention_rate <= 1.0
    
    @pytest.mark.asyncio
    async def test_user_segments_analysis(self, agent):
        """
Test user segments analysis."""
        segments = await agent._analyze_user_segments([])
        
        assert isinstance(segments, list)
        assert len(segments) > 0
        
        for segment in segments:
            assert segment.segment in UserSegmentType
            assert segment.user_count >= 0
            assert segment.engagement_score >= 0.0
            assert 0.0 <= segment.retention_rate <= 1.0
            assert segment.lifetime_value >= 0.0
    
    @pytest.mark.asyncio 
    async def test_behavior_predictions(self, agent):
        """
Test behavior predictions generation."""
        user_ids = ["user_123", "user_456"]
        predictions = await agent._generate_behavior_predictions([], user_ids)
        
        assert isinstance(predictions, list)
        assert len(predictions) > 0
        
        for prediction in predictions:
            assert prediction.user_id in user_ids
            assert prediction.prediction_type in ['churn_probability', 'engagement_score']
            assert 0.0 <= prediction.confidence <= 1.0
            assert isinstance(prediction.factors, dict)
    
    @pytest.mark.asyncio
    async def test_real_time_behavior_metrics(self, agent):
        """Test real-time behavior metrics."""
        metrics = await agent.get_real_time_behavior_metrics()
        
        assert isinstance(metrics, dict)
        assert 'active_users_now' in metrics
        assert 'content_being_created' in metrics
        assert 'engagement_rate_last_hour' in metrics
        assert 'user_sessions_active' in metrics
        assert isinstance(metrics['active_users_now'], int)
        assert isinstance(metrics['engagement_rate_last_hour'], float)


class TestPerformanceMetricsAgent:
    """
Test Performance Metrics Agent."""
    
    @pytest.fixture
    def agent(self):
        """
Create performance metrics agent instance."""
        return PerformanceMetricsAgent()
    
    @pytest.fixture
    def metrics_request(self):
        """
Create performance metrics request."""
        return PerformanceMetricsRequest(
            metric_types=[MetricType.ENGAGEMENT, MetricType.REVENUE, MetricType.SYSTEM_PERFORMANCE],
            include_trends=True,
            include_alerts=True,
            include_forecasts=True,
            granularity="hour"
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.agent_name == "Performance Metrics Agent"
        assert agent.agent_version == "1.0.0"
        assert hasattr(agent, '_alert_configs')
        assert hasattr(agent, '_metrics_history')
        assert len(agent._alert_configs) > 0
    
    @pytest.mark.asyncio
    async def test_collect_performance_metrics(self, agent, metrics_request):
        """Test performance metrics collection."""
        result = await agent.collect_performance_metrics(metrics_request)
        
        assert isinstance(result, PerformanceMetricsResult)
        assert result.request_id is not None
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.metrics, list)
        assert isinstance(result.alerts, list)
        assert isinstance(result.summary, dict)
        assert isinstance(result.trends, dict)
        
        # Check metrics
        for metric in result.metrics:
            assert metric.name is not None
            assert isinstance(metric.value, (int, float))
            assert metric.unit is not None
            assert isinstance(metric.metric_type, MetricType)
            assert isinstance(metric.timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_metrics_by_type_collection(self, agent, metrics_request):
        """
Test collection of metrics by type."""
        for metric_type in MetricType:
            metrics = await agent._collect_metrics_by_type(metric_type, metrics_request)
            
            assert isinstance(metrics, list)
            for metric in metrics:
                assert metric.metric_type == metric_type
                assert isinstance(metric.value, (int, float))
    
    @pytest.mark.asyncio
    async def test_alert_checking(self, agent):
        """
Test alert checking functionality."""
        # Create mock metrics that should trigger alerts
        from ai_agents.performance_metrics_agent.models.performance_models import KPIMetric, TrendDirection
        
        mock_metrics = [
            KPIMetric(
                name="user_engagement_rate",
                value=0.03,  # Below threshold
                unit="percentage",
                timestamp=datetime.now(),
                metric_type=MetricType.ENGAGEMENT,
                trend=TrendDirection.DOWN
            ),
            KPIMetric(
                name="system_response_time",
                value=3000,  # Above threshold
                unit="milliseconds",
                timestamp=datetime.now(),
                metric_type=MetricType.SYSTEM_PERFORMANCE,
                trend=TrendDirection.UP
            )
        ]
        
        alerts = await agent._check_alerts(mock_metrics)
        
        assert isinstance(alerts, list)
        assert len(alerts) >= 1  # Should trigger at least one alert
        
        for alert in alerts:
            assert alert.alert_id is not None
            assert alert.metric_name in ["user_engagement_rate", "system_response_time"]
            assert isinstance(alert.severity, AlertSeverity)
    
    @pytest.mark.asyncio
    async def test_real_time_dashboard(self, agent):
        """Test real-time dashboard data."""
        dashboard = await agent.get_real_time_dashboard()
        
        assert isinstance(dashboard, dict)
        assert 'timestamp' in dashboard
        assert 'system_status' in dashboard
        assert 'current_users_online' in dashboard
        assert 'requests_per_second' in dashboard
        assert 'revenue_today' in dashboard
        assert 'key_metrics' in dashboard


class TestSentimentAnalysisAgent:
    """
Test Sentiment Analysis Agent."""
    
    @pytest.fixture
    def agent(self):
        """
Create sentiment analysis agent instance."""
        return SentimentAnalysisAgent()
    
    @pytest.fixture
    def sentiment_request(self):
        """
Create sentiment analysis request."""
        return SentimentAnalysisRequest(
            content_text="This is an amazing platform! I love creating content here.",
            content_type=ContentType.TEXT,
            include_emotions=True,
            include_trends=True,
            include_keywords=True
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.agent_name == "Sentiment Analysis Agent"
        assert agent.agent_version == "1.0.0"
        assert hasattr(agent, 'text_analyzer')
        assert hasattr(agent, '_sentiment_history')
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, agent, sentiment_request):
        """Test sentiment analysis."""
        result = await agent.analyze_sentiment(sentiment_request)
        
        assert isinstance(result, SentimentAnalysisResult)
        assert result.analysis_id is not None
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.sentiment, SentimentType)
        assert 0.0 <= result.confidence <= 1.0
        assert -1.0 <= result.polarity <= 1.0
        assert 0.0 <= result.subjectivity <= 1.0
        assert isinstance(result.keywords, list)
        assert isinstance(result.insights, dict)
    
    @pytest.mark.asyncio
    async def test_emotion_profile_generation(self, agent):
        """
Test emotion profile generation."""
        # Mock sentiment result
        mock_result = Mock()
        mock_result.emotions = {'joy': 0.8, 'trust': 0.6, 'anticipation': 0.4}
        mock_result.keywords = ['amazing', 'love', 'fantastic']
        
        emotion_profile = await agent._generate_emotion_profile(mock_result)
        
        assert emotion_profile is not None
        assert hasattr(emotion_profile, 'primary_emotion')
        assert hasattr(emotion_profile, 'emotion_scores')
        assert hasattr(emotion_profile, 'intensity')
        assert 0.0 <= emotion_profile.intensity <= 1.0
        assert 0.0 <= emotion_profile.confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_sentiment_trends_analysis(self, agent):
        """
Test sentiment trends analysis."""
        trends = await agent._analyze_sentiment_trends("content_123")
        
        assert trends is not None
        assert hasattr(trends, 'time_period')
        assert hasattr(trends, 'sentiment_scores')
        assert hasattr(trends, 'trend_direction')
        assert hasattr(trends, 'volatility')
        assert isinstance(trends.key_events, list)
    
    @pytest.mark.asyncio
    async def test_brand_sentiment_summary(self, agent):
        """Test brand sentiment summary."""
        summary = await agent.get_brand_sentiment_summary("Ainflue")
        
        assert isinstance(summary, dict)
        assert 'brand_name' in summary
        assert 'overall_sentiment' in summary
        assert 'sentiment_score' in summary
        assert 'confidence' in summary
        assert 'sentiment_distribution' in summary
        assert isinstance(summary['sentiment_distribution'], dict)
    
    @pytest.mark.asyncio
    async def test_real_time_sentiment_metrics(self, agent):
        """Test real-time sentiment metrics."""
        metrics = await agent.get_real_time_sentiment_metrics()
        
        assert isinstance(metrics, dict)
        assert 'current_sentiment_score' in metrics
        assert 'sentiment_trend_24h' in metrics
        assert 'content_analyzed_today' in metrics
        assert 'emotion_breakdown' in metrics
        assert 'top_positive_keywords' in metrics
        assert 'top_negative_keywords' in metrics


class TestBusinessIntelligenceAgent:
    """
Test Business Intelligence Agent."""
    
    @pytest.fixture
    def agent(self):
        """
Create business intelligence agent instance."""
        return BusinessIntelligenceAgent()
    
    @pytest.fixture
    def bi_request(self):
        """
Create business intelligence request."""
        return BusinessIntelligenceRequest(
            analysis_type="comprehensive",
            metric_types=[BusinessMetricType.REVENUE, BusinessMetricType.GROWTH, BusinessMetricType.CUSTOMER],
            dashboard_types=[DashboardType.EXECUTIVE, DashboardType.FINANCIAL],
            include_forecasts=True,
            include_insights=True,
            include_benchmarks=True
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.agent_name == "Business Intelligence Agent"
        assert agent.agent_version == "1.0.0"
        assert hasattr(agent, '_analysis_cache')
        assert hasattr(agent, '_kpi_configs')
        assert isinstance(agent._kpi_configs, dict)
    
    @pytest.mark.asyncio
    async def test_generate_business_intelligence(self, agent, bi_request):
        """Test business intelligence generation."""
        result = await agent.generate_business_intelligence(bi_request)
        
        assert isinstance(result, BusinessIntelligenceResult)
        assert result.analysis_id is not None
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.executive_summary, dict)
        assert isinstance(result.dashboards, list)
        assert isinstance(result.insights, list)
        assert isinstance(result.forecasts, dict)
        assert isinstance(result.benchmarks, dict)
        assert isinstance(result.recommendations, list)
    
    @pytest.mark.asyncio
    async def test_executive_summary_generation(self, agent, bi_request):
        """
Test executive summary generation."""
        summary = await agent._generate_executive_summary(bi_request)
        
        assert isinstance(summary, dict)
        assert 'business_health_score' in summary
        assert 'revenue_status' in summary
        assert 'user_growth_status' in summary
        assert 'key_highlights' in summary
        assert 'critical_metrics' in summary
        assert 'strategic_priorities' in summary
        assert isinstance(summary['key_highlights'], list)
    
    @pytest.mark.asyncio
    async def test_dashboards_generation(self, agent, bi_request):
        """
Test dashboards generation."""
        dashboards = await agent._generate_dashboards(bi_request)
        
        assert isinstance(dashboards, list)
        assert len(dashboards) > 0
        
        for dashboard in dashboards:
            assert dashboard.dashboard_id is not None
            assert isinstance(dashboard.dashboard_type, DashboardType)
            assert dashboard.title is not None
            assert isinstance(dashboard.metrics, list)
            assert isinstance(dashboard.charts, list)
    
    @pytest.mark.asyncio
    async def test_business_insights_generation(self, agent, bi_request):
        """
Test business insights generation."""
        insights = await agent._generate_business_insights(bi_request)
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        
        for insight in insights:
            assert insight.insight_id is not None
            assert hasattr(insight, 'insight_type')
            assert insight.title is not None
            assert insight.description is not None
            assert 0.0 <= insight.impact_score <= 10.0
            assert 0.0 <= insight.confidence <= 1.0
            assert isinstance(insight.recommendations, list)
    
    @pytest.mark.asyncio
    async def test_business_forecasts_generation(self, agent, bi_request):
        """
Test business forecasts generation."""
        forecasts = await agent._generate_business_forecasts(bi_request)
        
        assert isinstance(forecasts, dict)
        assert 'revenue_forecast' in forecasts
        assert 'user_growth_forecast' in forecasts
        assert 'market_opportunities' in forecasts
        
        # Check revenue forecast structure
        revenue_forecast = forecasts['revenue_forecast']
        assert 'next_quarter' in revenue_forecast
        assert 'next_year' in revenue_forecast
        assert 'predicted_revenue' in revenue_forecast['next_quarter']
        assert 'confidence_interval' in revenue_forecast['next_quarter']
    
    @pytest.mark.asyncio
    async def test_benchmarks_generation(self, agent, bi_request):
        """
Test benchmarks generation."""
        benchmarks = await agent._generate_benchmarks(bi_request)
        
        assert isinstance(benchmarks, dict)
        assert 'industry_averages' in benchmarks
        assert 'competitive_position' in benchmarks
        assert 'performance_vs_benchmarks' in benchmarks
    
    @pytest.mark.asyncio
    async def test_real_time_business_metrics(self, agent):
        """
Test real-time business metrics."""
        metrics = await agent.get_real_time_business_metrics()
        
        assert isinstance(metrics, dict)
        assert 'current_revenue_rate' in metrics
        assert 'active_users_now' in metrics
        assert 'revenue_today' in metrics
        assert 'new_users_today' in metrics
        assert 'top_revenue_sources' in metrics
        assert isinstance(metrics['top_revenue_sources'], list)


# Integration tests for agent interoperability
class TestAgentsIntegration:
    """
Test integration between different analytics agents."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_cross_agent_data_consistency(self):
        """
Test data consistency across agents."""
        # Initialize agents
        user_behavior_agent = UserBehaviorAgent()
        performance_agent = PerformanceMetricsAgent()
        bi_agent = BusinessIntelligenceAgent()
        
        # Get real-time data from each
        user_data = await user_behavior_agent.get_real_time_behavior_metrics()
        performance_data = await performance_agent.get_real_time_dashboard()
        bi_data = await bi_agent.get_real_time_business_metrics()
        
        # Check for reasonable consistency in user counts
        user_behavior_users = user_data.get('active_users_now', 0)
        performance_users = performance_data.get('current_users_online', 0)
        bi_users = bi_data.get('active_users_now', 0)
        
        # Allow for reasonable variance (within 20% difference)
        max_diff = max(user_behavior_users, performance_users, bi_users) * 0.2
        assert abs(user_behavior_users - performance_users) <= max_diff
        assert abs(performance_users - bi_users) <= max_diff
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_coordinated_agent_analysis(self):
        """
Test coordinated analysis across multiple agents."""
        # Run analysis on all agents with related data
        user_agent = UserBehaviorAgent()
        sentiment_agent = SentimentAnalysisAgent()
        bi_agent = BusinessIntelligenceAgent()
        
        # Create related requests
        user_request = BehaviorAnalysisRequest(include_predictions=True)
        sentiment_request = SentimentAnalysisRequest(
            content_text="Users love the new analytics features!",
            include_emotions=True
        )
        bi_request = BusinessIntelligenceRequest(include_forecasts=True)
        
        # Run analyses
        user_result = await user_agent.analyze_user_behavior(user_request)
        sentiment_result = await sentiment_agent.analyze_sentiment(sentiment_request)
        bi_result = await bi_agent.generate_business_intelligence(bi_request)
        
        # Verify all completed successfully
        assert isinstance(user_result, BehaviorAnalysisResult)
        assert isinstance(sentiment_result, SentimentAnalysisResult)
        assert isinstance(bi_result, BusinessIntelligenceResult)
        
        # Check for logical consistency
        assert sentiment_result.sentiment in [SentimentType.POSITIVE, SentimentType.NEUTRAL]
        assert user_result.overall_score >= 0.0
        assert bi_result.executive_summary['business_health_score'] >= 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])