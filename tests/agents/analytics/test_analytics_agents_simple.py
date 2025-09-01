"""Simple Tests for Analytics Agents

Test the analytics agents without complex imports.
"""

import pytest
import sys
import os
from datetime import datetime

# Add the agents path for direct import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ai_agents'))

from user_behavior_agent.core.user_behavior_agent import UserBehaviorAgent
from user_behavior_agent.models.behavior_models import BehaviorAnalysisRequest
from performance_metrics_agent.core.performance_metrics_agent import PerformanceMetricsAgent
from performance_metrics_agent.models.performance_models import PerformanceMetricsRequest
from sentiment_analysis_agent.core.sentiment_analysis_agent import SentimentAnalysisAgent
from sentiment_analysis_agent.models.sentiment_models import SentimentAnalysisRequest
from business_intelligence_agent.core.business_intelligence_agent import BusinessIntelligenceAgent
from business_intelligence_agent.models.bi_models import BusinessIntelligenceRequest


class TestAnalyticsAgentsSimple:
    """
Simple test class for analytics agents."""
    
    def test_user_behavior_agent_init(self):
        """
Test user behavior agent initialization."""
        agent = UserBehaviorAgent()
        assert agent.agent_name == "User Behavior Agent"
        assert agent.agent_version == "1.0.0"
    
    def test_performance_metrics_agent_init(self):
        """Test performance metrics agent initialization."""
        agent = PerformanceMetricsAgent()
        assert agent.agent_name == "Performance Metrics Agent"
        assert agent.agent_version == "1.0.0"
    
    def test_sentiment_analysis_agent_init(self):
        """Test sentiment analysis agent initialization."""
        agent = SentimentAnalysisAgent()
        assert agent.agent_name == "Sentiment Analysis Agent"
        assert agent.agent_version == "1.0.0"
    
    def test_business_intelligence_agent_init(self):
        """Test business intelligence agent initialization."""
        agent = BusinessIntelligenceAgent()
        assert agent.agent_name == "Business Intelligence Agent"
        assert agent.agent_version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_user_behavior_analysis(self):
        """Test user behavior analysis."""
        agent = UserBehaviorAgent()
        request = BehaviorAnalysisRequest(
            user_ids=["test_user"],
            include_predictions=True,
            include_segmentation=True
        )
        result = await agent.analyze_user_behavior(request)
        
        assert result.analysis_id is not None
        assert isinstance(result.timestamp, datetime)
        assert len(result.user_segments) > 0
        assert len(result.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_performance_metrics_collection(self):
        """Test performance metrics collection."""
        agent = PerformanceMetricsAgent()
        request = PerformanceMetricsRequest(
            include_trends=True,
            include_alerts=True
        )
        result = await agent.collect_performance_metrics(request)
        
        assert result.request_id is not None
        assert isinstance(result.timestamp, datetime)
        assert len(result.metrics) > 0
        assert isinstance(result.summary, dict)
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis(self):
        """
Test sentiment analysis."""
        agent = SentimentAnalysisAgent()
        request = SentimentAnalysisRequest(
            content_text="This is amazing! I love this platform.",
            include_emotions=True,
            include_keywords=True
        )
        result = await agent.analyze_sentiment(request)
        
        assert result.analysis_id is not None
        assert isinstance(result.timestamp, datetime)
        assert result.sentiment is not None
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.keywords) > 0
    
    @pytest.mark.asyncio
    async def test_business_intelligence_generation(self):
        """Test business intelligence generation."""
        agent = BusinessIntelligenceAgent()
        request = BusinessIntelligenceRequest(
            include_forecasts=True,
            include_insights=True
        )
        result = await agent.generate_business_intelligence(request)
        
        assert result.analysis_id is not None
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.executive_summary, dict)
        assert len(result.insights) > 0
        assert len(result.recommendations) > 0
    
    def test_all_agents_have_correct_names(self):
        """
Test that all agents have the expected names."""
        expected_agents = {
            UserBehaviorAgent(): "User Behavior Agent",
            PerformanceMetricsAgent(): "Performance Metrics Agent", 
            SentimentAnalysisAgent(): "Sentiment Analysis Agent",
            BusinessIntelligenceAgent(): "Business Intelligence Agent"
        }
        
        for agent, expected_name in expected_agents.items():
            assert agent.agent_name == expected_name
            assert agent.agent_version == "1.0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])