"""Tests for Analytics Agents Registry

Test the unified 6-agent analytics system.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch

from ai_agents.analytics_agents_registry import (
    AnalyticsAgentsRegistry,
    AnalyticsRequest,
    AnalyticsResult,
    analytics_registry,
    run_full_analytics,
    get_analytics_dashboard,
    get_analytics_agents_status
)


class TestAnalyticsAgentsRegistry:
    """
Test the analytics agents registry."""
    
    @pytest.fixture
    def registry(self):
        """
Create test registry instance."""
        return AnalyticsAgentsRegistry()
    
    @pytest.fixture
    def sample_request(self):
        """
Create sample analytics request."""
        return AnalyticsRequest(
            request_id="test_request_123",
            agents_to_run=['user_behavior', 'performance_metrics', 'sentiment_analysis'],
            time_period="7_days",
            include_predictions=True,
            include_real_time=True
        )
    
    def test_registry_initialization(self, registry):
        """Test registry initializes correctly."""
        assert registry is not None
        assert hasattr(registry, 'agents')
        assert len(registry.agents) == 6
        
        # Check all expected agents are present
        expected_agents = [
            'predictive_analytics', 'user_behavior', 'performance_metrics',
            'market_research', 'sentiment_analysis', 'business_intelligence'
        ]
        for agent_name in expected_agents:
            assert agent_name in registry.agents
    
    def test_get_available_agents(self, registry):
        """
Test getting available agents."""
        available = registry.get_available_agents()
        assert isinstance(available, list)
        assert 'user_behavior' in available
        assert 'performance_metrics' in available
        assert 'sentiment_analysis' in available
        assert 'business_intelligence' in available
    
    def test_get_agent_status(self, registry):
        """
Test getting agent status."""
        status = registry.get_agent_status()
        assert isinstance(status, dict)
        assert len(status) == 6
        
        # Should have status for all agents
        for agent_name in ['user_behavior', 'performance_metrics', 'sentiment_analysis', 'business_intelligence']:
            assert agent_name in status
            assert status[agent_name] in ['available', 'unavailable']
    
    @pytest.mark.asyncio
    async def test_run_comprehensive_analytics(self, registry, sample_request):
        """
Test running comprehensive analytics."""
        result = await registry.run_comprehensive_analytics(sample_request)
        
        assert isinstance(result, AnalyticsResult)
        assert result.request_id == sample_request.request_id
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.overall_score, float)
        assert 0.0 <= result.overall_score <= 10.0
        assert isinstance(result.summary, dict)
        assert isinstance(result.agent_results, dict)
        assert isinstance(result.insights, list)
        assert isinstance(result.recommendations, list)
        assert isinstance(result.alerts, list)
    
    @pytest.mark.asyncio
    async def test_user_behavior_agent_analysis(self, registry, sample_request):
        """
Test user behavior agent analysis."""
        result = await registry._run_agent_analysis('user_behavior', sample_request)
        
        assert isinstance(result, dict)
        assert result.get('status') == 'success'
        assert 'data' in result
        assert result.get('agent_name') == 'User Behavior Agent'
        assert result.get('agent_type') == 'user_behavior'
    
    @pytest.mark.asyncio
    async def test_performance_metrics_agent_analysis(self, registry, sample_request):
        """
Test performance metrics agent analysis."""
        result = await registry._run_agent_analysis('performance_metrics', sample_request)
        
        assert isinstance(result, dict)
        assert result.get('status') == 'success'
        assert 'data' in result
        assert result.get('agent_name') == 'Performance Metrics Agent'
        assert result.get('agent_type') == 'performance_metrics'
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_agent_analysis(self, registry, sample_request):
        """
Test sentiment analysis agent analysis."""
        result = await registry._run_agent_analysis('sentiment_analysis', sample_request)
        
        assert isinstance(result, dict)
        assert result.get('status') == 'success'
        assert 'data' in result
        assert result.get('agent_name') == 'Sentiment Analysis Agent'
        assert result.get('agent_type') == 'sentiment_analysis'
    
    @pytest.mark.asyncio
    async def test_business_intelligence_agent_analysis(self, registry, sample_request):
        """
Test business intelligence agent analysis."""
        result = await registry._run_agent_analysis('business_intelligence', sample_request)
        
        assert isinstance(result, dict)
        assert result.get('status') == 'success'
        assert 'data' in result
        assert result.get('agent_name') == 'Business Intelligence Agent'
        assert result.get('agent_type') == 'business_intelligence'
    
    @pytest.mark.asyncio
    async def test_get_real_time_dashboard(self, registry):
        """
Test getting real-time dashboard."""
        dashboard = await registry.get_real_time_dashboard()
        
        assert isinstance(dashboard, dict)
        assert 'timestamp' in dashboard
        assert 'overall_health' in dashboard
        assert 'system_status' in dashboard
        assert 'agents_status' in dashboard
        assert isinstance(dashboard['agents_status'], dict)
    
    @pytest.mark.asyncio
    async def test_cross_agent_insights_generation(self, registry):
        """
Test cross-agent insights generation."""
        # Mock agent results
        mock_results = {
            'user_behavior': {'status': 'success', 'data': Mock()},
            'business_intelligence': {'status': 'success', 'data': Mock()},
            'sentiment_analysis': {'status': 'success', 'data': Mock()},
            'performance_metrics': {'status': 'success', 'data': Mock()}
        }
        
        insights = await registry._generate_cross_agent_insights(mock_results)
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        
        for insight in insights:
            assert 'type' in insight
            assert 'title' in insight
            assert 'description' in insight
            assert 'confidence' in insight
            assert 'supporting_agents' in insight
    
    @pytest.mark.asyncio
    async def test_unified_recommendations_generation(self, registry):
        """
Test unified recommendations generation."""
        mock_results = {'user_behavior': {'status': 'success'}}
        mock_insights = [{'type': 'correlation', 'confidence': 0.85}]
        
        recommendations = await registry._generate_unified_recommendations(mock_results, mock_insights)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert 'priority' in rec
            assert 'category' in rec
            assert 'title' in rec
            assert 'description' in rec
            assert 'expected_impact' in rec
            assert 'timeline' in rec


class TestAnalyticsAgentsConvenienceFunctions:
    """
Test convenience functions for analytics agents."""
    
    @pytest.mark.asyncio
    async def test_run_full_analytics(self):
        """
Test run_full_analytics convenience function."""
        result = await run_full_analytics(
            request_id="test_conv_123",
            time_period="7_days"
        )
        
        assert isinstance(result, AnalyticsResult)
        assert result.request_id == "test_conv_123"
    
    @pytest.mark.asyncio
    async def test_get_analytics_dashboard(self):
        """Test get_analytics_dashboard convenience function."""
        dashboard = await get_analytics_dashboard()
        
        assert isinstance(dashboard, dict)
        assert 'timestamp' in dashboard
        assert 'agents_status' in dashboard
    
    def test_get_analytics_agents_status(self):
        """
Test get_analytics_agents_status convenience function."""
        status = get_analytics_agents_status()
        
        assert isinstance(status, dict)
        assert len(status) == 6


class TestAnalyticsRequest:
    """
Test AnalyticsRequest data model."""
    
    def test_analytics_request_creation(self):
        """
Test creating analytics request."""
        request = AnalyticsRequest(
            request_id="test_123",
            agents_to_run=['user_behavior', 'sentiment_analysis'],
            time_period="30_days",
            include_predictions=True,
            include_real_time=False
        )
        
        assert request.request_id == "test_123"
        assert len(request.agents_to_run) == 2
        assert request.time_period == "30_days"
        assert request.include_predictions is True
        assert request.include_real_time is False
    
    def test_analytics_request_defaults(self):
        """Test analytics request with defaults."""
        request = AnalyticsRequest(request_id="test_456")
        
        assert len(request.agents_to_run) == 6  # All agents by default
        assert request.time_period == "30_days"
        assert request.include_predictions is True
        assert request.include_real_time is True
        assert request.priority == "medium"


class TestAnalyticsResult:
    """Test AnalyticsResult data model."""
    
    def test_analytics_result_creation(self):
        """
Test creating analytics result."""
        result = AnalyticsResult(
            request_id="test_789",
            timestamp=datetime.now(),
            overall_score=8.5,
            summary={'status': 'healthy'},
            agent_results={'user_behavior': {'status': 'success'}},
            insights=[{'type': 'correlation'}],
            recommendations=[{'priority': 'high'}],
            alerts=[{'severity': 'medium'}]
        )
        
        assert result.request_id == "test_789"
        assert isinstance(result.timestamp, datetime)
        assert result.overall_score == 8.5
        assert len(result.agent_results) == 1
        assert len(result.insights) == 1
        assert len(result.recommendations) == 1
        assert len(result.alerts) == 1


# Performance and integration tests
class TestAnalyticsPerformance:
    """Test analytics system performance."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_analytics_requests(self):
        """
Test handling multiple concurrent analytics requests."""
        registry = AnalyticsAgentsRegistry()
        
        # Create multiple requests
        requests = [
            AnalyticsRequest(
                request_id=f"concurrent_test_{i}",
                agents_to_run=['user_behavior', 'performance_metrics'],
                time_period="7_days"
            )
            for i in range(3)
        ]
        
        # Run concurrently
        tasks = [
            registry.run_comprehensive_analytics(req)
            for req in requests
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert isinstance(result, AnalyticsResult)
            assert result.request_id == f"concurrent_test_{i}"
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_analytics_response_time(self):
        """Test analytics response time is reasonable."""
        registry = AnalyticsAgentsRegistry()
        request = AnalyticsRequest(
            request_id="perf_test",
            agents_to_run=['user_behavior', 'sentiment_analysis']
        )
        
        start_time = datetime.now()
        result = await registry.run_comprehensive_analytics(request)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert processing_time < 30.0  # 30 seconds max
        assert result.metadata['processing_time_ms'] > 0
    
    @pytest.mark.asyncio
    async def test_error_handling_in_agent_failure(self):
        """Test graceful handling when an agent fails."""
        registry = AnalyticsAgentsRegistry()
        
        # Mock an agent to fail
        with patch.object(registry.agents['user_behavior'], 'analyze_user_behavior', side_effect=Exception("Test error")):
            request = AnalyticsRequest(
                request_id="error_test",
                agents_to_run=['user_behavior', 'performance_metrics']
            )
            
            result = await registry.run_comprehensive_analytics(request)
            
            # Should still return result despite one agent failure
            assert isinstance(result, AnalyticsResult)
            assert 'user_behavior' in result.agent_results
            assert 'error' in result.agent_results['user_behavior']
            assert 'performance_metrics' in result.agent_results
            assert result.agent_results['performance_metrics'].get('status') == 'success'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])