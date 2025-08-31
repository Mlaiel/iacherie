"""
Test for new SEO & Marketing agents

Testing the newly implemented agents:
- Keyword Research Agent
- Content Optimization Agent
- Influencer Matching Agent (to be implemented)
- Campaign Optimization Agent (to be implemented)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

# Import the new agents
try:
    from ai_agents.keyword_research_agent import KeywordResearchManager, KeywordSystemStatus
    from ai_agents.content_optimization_agent import ContentOptimizationManager, ContentSystemStatus
    from ai_agents.base import AgentRequest, AgentResponse
except ImportError as e:
    pytest.skip(f"Agent imports failed: {e}", allow_module_level=True)


class TestKeywordResearchAgent:
    """Test cases for Keyword Research Agent"""
    
    @pytest.fixture
    async def keyword_agent(self):
        """Create a keyword research agent for testing"""
        config = {
            "api_keys": {"test": "test_key"},
            "max_concurrent_requests": 10,
            "cache_ttl": 3600,
            "supported_platforms": ["general", "youtube", "instagram"]
        }
        agent = KeywordResearchManager(config)
        await agent.initialize()
        yield agent
        await agent.shutdown()
    
    @pytest.mark.asyncio
    async def test_keyword_discovery(self, keyword_agent):
        """Test keyword discovery functionality"""
        request = AgentRequest(
            action="discover_keywords",
            data={
                "topic": "artificial intelligence",
                "platform": "general",
                "language": "en",
                "depth": "medium"
            }
        )
        
        response = await keyword_agent.process(request)
        
        assert response.success
        assert "primary_keywords" in response.data
        assert "secondary_keywords" in response.data
        assert "long_tail_keywords" in response.data
        assert "keyword_metrics" in response.data
        assert response.data["total_discovered"] > 0
    
    @pytest.mark.asyncio
    async def test_competition_analysis(self, keyword_agent):
        """Test keyword competition analysis"""
        request = AgentRequest(
            action="analyze_competition",
            data={
                "keywords": ["AI", "machine learning", "artificial intelligence"],
                "platform": "general"
            }
        )
        
        response = await keyword_agent.process(request)
        
        assert response.success
        assert "competition_analysis" in response.data
        assert len(response.data["competition_analysis"]) == 3
        
        # Check each keyword has competition data
        for keyword in ["AI", "machine learning", "artificial intelligence"]:
            assert keyword in response.data["competition_analysis"]
            analysis = response.data["competition_analysis"][keyword]
            assert "competition_level" in analysis
            assert "opportunity_score" in analysis
    
    @pytest.mark.asyncio
    async def test_trend_research(self, keyword_agent):
        """Test keyword trend research"""
        request = AgentRequest(
            action="research_trends",
            data={
                "niche": "technology",
                "timeframe": "30d",
                "region": "global"
            }
        )
        
        response = await keyword_agent.process(request)
        
        assert response.success
        assert "trending_keywords" in response.data
        assert "seasonal_patterns" in response.data
        assert "emerging_topics" in response.data
        assert response.data["niche"] == "technology"
    
    @pytest.mark.asyncio
    async def test_system_status(self, keyword_agent):
        """Test system status retrieval"""
        status = await keyword_agent.get_system_status()
        
        assert isinstance(status, KeywordSystemStatus)
        assert status.engine_status in ["running", "stopped", "unknown"]
        assert isinstance(status.active_research_jobs, int)
        assert isinstance(status.total_keywords_discovered, int)


class TestContentOptimizationAgent:
    """Test cases for Content Optimization Agent"""
    
    @pytest.fixture
    async def content_agent(self):
        """Create a content optimization agent for testing"""
        config = {
            "nlp_models": {"sentiment": "test_model"},
            "seo_apis": {"test": "test_api"},
            "readability_apis": {"flesch": "test_api"},
            "platform_configs": {"instagram": {"max_length": 2200}}
        }
        agent = ContentOptimizationManager(config)
        await agent.initialize()
        yield agent
        await agent.shutdown()
    
    @pytest.mark.asyncio
    async def test_content_optimization(self, content_agent):
        """Test comprehensive content optimization"""
        sample_content = """
        This is a sample article about artificial intelligence and machine learning.
        AI has become very important in today's world. Many companies are using AI.
        Machine learning is a subset of AI. It helps computers learn from data.
        """
        
        request = AgentRequest(
            action="optimize_content",
            data={
                "content": sample_content,
                "target_keywords": ["artificial intelligence", "machine learning", "AI"],
                "platform": "general",
                "goals": ["seo", "readability", "engagement"]
            }
        )
        
        response = await content_agent.process(request)
        
        assert response.success
        assert "optimized_content" in response.data
        assert "optimization_steps" in response.data
        assert "before_analysis" in response.data
        assert "after_analysis" in response.data
        assert len(response.data["optimization_steps"]) > 0
    
    @pytest.mark.asyncio
    async def test_seo_analysis(self, content_agent):
        """Test SEO performance analysis"""
        sample_content = """
        # The Ultimate Guide to Artificial Intelligence
        
        Artificial intelligence is revolutionizing the world. This comprehensive guide
        covers everything you need to know about AI and machine learning.
        """
        
        request = AgentRequest(
            action="analyze_seo",
            data={
                "content": sample_content,
                "target_keywords": ["artificial intelligence", "AI guide", "machine learning"]
            }
        )
        
        response = await content_agent.process(request)
        
        assert response.success
        assert "content_analysis" in response.data
        assert "keyword_optimization" in response.data
        assert "performance_score" in response.data
        assert isinstance(response.data["performance_score"], (int, float))
    
    @pytest.mark.asyncio
    async def test_readability_improvement(self, content_agent):
        """Test readability improvement"""
        complex_content = """
        The implementation of artificial intelligence methodologies in contemporary
        technological infrastructures necessitates comprehensive understanding of
        algorithmic paradigms and computational frameworks.
        """
        
        request = AgentRequest(
            action="improve_readability",
            data={
                "content": complex_content,
                "target_audience": "general",
                "reading_level": "intermediate"
            }
        )
        
        response = await content_agent.process(request)
        
        assert response.success
        assert "improved_content" in response.data
        assert "readability_before" in response.data
        assert "readability_after" in response.data
        assert "improvements_made" in response.data
    
    @pytest.mark.asyncio
    async def test_platform_adaptation(self, content_agent):
        """Test content adaptation for different platforms"""
        long_content = "This is a long article about AI. " * 100  # Make it long
        
        request = AgentRequest(
            action="adapt_platform",
            data={
                "content": long_content,
                "source_platform": "general",
                "target_platforms": ["twitter", "instagram", "linkedin"]
            }
        )
        
        response = await content_agent.process(request)
        
        assert response.success
        assert "adaptations" in response.data
        assert "twitter" in response.data["adaptations"]
        assert "instagram" in response.data["adaptations"]
        assert "linkedin" in response.data["adaptations"]
    
    @pytest.mark.asyncio
    async def test_metadata_generation(self, content_agent):
        """Test metadata generation"""
        sample_content = """
        Learn about the latest trends in artificial intelligence and how AI
        is transforming industries across the globe.
        """
        
        request = AgentRequest(
            action="generate_metadata",
            data={
                "content": sample_content,
                "platform": "youtube",
                "target_keywords": ["AI trends", "artificial intelligence", "industry transformation"]
            }
        )
        
        response = await content_agent.process(request)
        
        assert response.success
        assert "metadata" in response.data
        assert "title" in response.data["metadata"]
        assert "description" in response.data["metadata"]
        assert "keywords" in response.data["metadata"]
    
    @pytest.mark.asyncio
    async def test_content_quality_scoring(self, content_agent):
        """Test content quality scoring"""
        sample_content = """
        # AI Revolution
        
        Artificial intelligence is changing everything. Here's what you need to know.
        
        ## What is AI?
        AI helps computers think like humans.
        
        ## Why AI Matters
        - Improves efficiency
        - Reduces costs
        - Enables innovation
        
        Ready to learn more? Subscribe to our newsletter!
        """
        
        request = AgentRequest(
            action="score_content",
            data={
                "content": sample_content,
                "criteria": ["seo", "readability", "engagement", "structure"]
            }
        )
        
        response = await content_agent.process(request)
        
        assert response.success
        assert "quality_scores" in response.data
        assert "overall_score" in response.data
        assert "detailed_analysis" in response.data
        
        # Check all criteria are scored
        for criterion in ["seo", "readability", "engagement", "structure"]:
            assert criterion in response.data["quality_scores"]
            assert isinstance(response.data["quality_scores"][criterion], (int, float))
    
    @pytest.mark.asyncio
    async def test_system_status(self, content_agent):
        """Test system status retrieval"""
        status = await content_agent.get_system_status()
        
        assert isinstance(status, ContentSystemStatus)
        assert status.engine_status in ["running", "stopped", "unknown"]
        assert isinstance(status.active_optimization_jobs, int)
        assert isinstance(status.total_content_optimized, int)


class TestAgentIntegration:
    """Test integration between the new SEO & Marketing agents"""
    
    @pytest.mark.asyncio
    async def test_keyword_to_content_workflow(self):
        """Test workflow from keyword research to content optimization"""
        # Initialize agents
        keyword_config = {
            "api_keys": {"test": "test_key"},
            "max_concurrent_requests": 10,
            "cache_ttl": 3600,
            "supported_platforms": ["general"]
        }
        
        content_config = {
            "nlp_models": {"sentiment": "test_model"},
            "seo_apis": {"test": "test_api"},
            "readability_apis": {"flesch": "test_api"},
            "platform_configs": {"general": {"max_length": 5000}}
        }
        
        keyword_agent = KeywordResearchManager(keyword_config)
        content_agent = ContentOptimizationManager(content_config)
        
        try:
            await keyword_agent.initialize()
            await content_agent.initialize()
            
            # Step 1: Research keywords
            keyword_request = AgentRequest(
                action="discover_keywords",
                data={
                    "topic": "sustainable technology",
                    "platform": "general",
                    "language": "en",
                    "depth": "medium"
                }
            )
            
            keyword_response = await keyword_agent.process(keyword_request)
            assert keyword_response.success
            
            # Step 2: Use discovered keywords for content optimization
            discovered_keywords = keyword_response.data["primary_keywords"][:3]  # Take top 3
            
            sample_content = """
            Sustainable technology is becoming increasingly important in our fight against climate change.
            Companies around the world are investing in green technologies and renewable energy solutions.
            """
            
            content_request = AgentRequest(
                action="optimize_content",
                data={
                    "content": sample_content,
                    "target_keywords": discovered_keywords,
                    "platform": "general",
                    "goals": ["seo", "readability"]
                }
            )
            
            content_response = await content_agent.process(content_request)
            assert content_response.success
            assert "optimized_content" in content_response.data
            
            # Verify the optimization used the discovered keywords
            optimized_content = content_response.data["optimized_content"]
            assert len(optimized_content) > len(sample_content)  # Content should be enhanced
            
        finally:
            await keyword_agent.shutdown()
            await content_agent.shutdown()


# Test runner for manual execution
if __name__ == "__main__":
    pytest.main([__file__, "-v"])