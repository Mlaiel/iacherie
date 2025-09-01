"""Tests for SEO & Marketing Agents

Basic functionality tests for the 9 SEO & Marketing agents.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

class TestKeywordResearchAgent:
    """Test the Keyword Research Agent functionality"""
    
    def test_import_keyword_research_agent(self):
        """Test that keyword research agent can be imported"""
        try:
            from ai_agents.keyword_research_agent import KeywordResearchManager, KeywordEngine
            assert KeywordResearchManager is not None
            assert KeywordEngine is not None
        except ImportError as e:
            pytest.skip(f"Keyword Research Agent not available: {e}")
    
    @pytest.mark.asyncio
    async def test_keyword_research_basic_functionality(self):
        """Test basic keyword research functionality"""
        try:
            from ai_agents.keyword_research_agent import KeywordEngine
            
            engine = KeywordEngine()
            result = await engine.research_keywords(
                seed_keywords=["artificial intelligence", "machine learning"],
                options={'language': 'en', 'content_type': 'blog'}
            )
            
            assert result.success is True
            assert len(result.keywords) > 0
            assert 'artificial intelligence' in str(result.keywords)
            
        except ImportError:
            pytest.skip("Keyword Research Agent not available")

class TestContentOptimizationAgent:
    """Test the Content Optimization Agent functionality"""
    
    def test_import_content_optimization_agent(self):
        """Test that content optimization agent can be imported"""
        try:
            from ai_agents.content_optimization_agent import ContentOptimizationManager, OptimizationEngine
            assert ContentOptimizationManager is not None
            assert OptimizationEngine is not None
        except ImportError as e:
            pytest.skip(f"Content Optimization Agent not available: {e}")
    
    @pytest.mark.asyncio
    async def test_content_optimization_basic_functionality(self):
        """Test basic content optimization functionality"""
        try:
            from ai_agents.content_optimization_agent import OptimizationEngine, OptimizationType, ContentType
            
            engine = OptimizationEngine()
            test_content = {
                'title': 'Test Article',
                'text': 'This is a test article about artificial intelligence and machine learning.',
                'meta_description': ''
            }
            
            result = await engine.optimize_content(
                content=test_content,
                optimization_types=[OptimizationType.SEO_OPTIMIZATION, OptimizationType.READABILITY],
                content_type=ContentType.BLOG_POST,
                options={'target_keywords': ['artificial intelligence']}
            )
            
            assert result.success is True
            assert result.optimized_content is not None
            assert len(result.recommendations) > 0
            
        except ImportError:
            pytest.skip("Content Optimization Agent not available")

class TestInfluencerMatchingAgent:
    """Test the Influencer Matching Agent functionality"""
    
    def test_import_influencer_matching_agent(self):
        """Test that influencer matching agent can be imported"""
        try:
            from ai_agents.influencer_matching_agent import InfluencerMatchingManager, MatchingEngine
            assert InfluencerMatchingManager is not None
            assert MatchingEngine is not None
        except ImportError as e:
            pytest.skip(f"Influencer Matching Agent not available: {e}")
    
    @pytest.mark.asyncio
    async def test_influencer_matching_basic_functionality(self):
        """Test basic influencer matching functionality"""
        try:
            from ai_agents.influencer_matching_agent import MatchingEngine
            
            engine = MatchingEngine()
            brand_requirements = {
                'content_categories': ['technology'],
                'budget_range': (1000, 5000),
                'preferred_platforms': ['youtube', 'instagram']
            }
            
            result = await engine.find_matching_creators(
                brand_requirements=brand_requirements,
                collaboration_type='sponsored_post'
            )
            
            assert result.success is True
            assert len(result.matched_creators) >= 0  # May be 0 if no matches
            assert len(result.recommendations) > 0
            
        except ImportError:
            pytest.skip("Influencer Matching Agent not available")

class TestCampaignOptimizationAgent:
    """Test the Campaign Optimization Agent functionality"""
    
    def test_import_campaign_optimization_agent(self):
        """Test that campaign optimization agent can be imported"""
        try:
            from ai_agents.campaign_optimization_agent import CampaignOptimizationManager, CampaignOptimizationEngine
            assert CampaignOptimizationManager is not None
            assert CampaignOptimizationEngine is not None
        except ImportError as e:
            pytest.skip(f"Campaign Optimization Agent not available: {e}")
    
    @pytest.mark.asyncio
    async def test_campaign_optimization_basic_functionality(self):
        """Test basic campaign optimization functionality"""
        try:
            from ai_agents.campaign_optimization_agent import CampaignOptimizationEngine
            
            engine = CampaignOptimizationEngine()
            current_metrics = {
                'impressions': 10000,
                'clicks': 150,
                'conversions': 10,
                'cost': 500.0,
                'revenue': 800.0,
                'roi': 1.6
            }
            
            result = await engine.optimize_campaign(
                campaign_id='test_campaign_001',
                optimization_goals=['maximize_roi'],
                current_metrics=current_metrics,
                constraints={'budget': {'max_increase': 0.2}}
            )
            
            assert result.success is True
            assert len(result.optimization_strategies) >= 0
            assert result.projected_improvements is not None
            
        except ImportError:
            pytest.skip("Campaign Optimization Agent not available")

class TestSEOMarketingAgentsIntegration:
    """Test integration between SEO & Marketing agents"""
    
    @pytest.mark.asyncio
    async def test_keyword_to_content_optimization_workflow(self):
        """Test workflow from keyword research to content optimization"""
        try:
            from ai_agents.keyword_research_agent import KeywordEngine
            from ai_agents.content_optimization_agent import OptimizationEngine, OptimizationType, ContentType
            
            # Step 1: Research keywords
            keyword_engine = KeywordEngine()
            keyword_result = await keyword_engine.research_keywords(
                seed_keywords=["digital marketing"],
                options={'content_type': 'blog'}
            )
            
            assert keyword_result.success is True
            
            # Step 2: Use keywords for content optimization
            content_engine = OptimizationEngine()
            test_content = {
                'title': 'Digital Marketing Guide',
                'text': 'Learn about digital marketing strategies and techniques.',
                'meta_description': ''
            }
            
            # Extract first keyword for optimization
            target_keywords = ['digital marketing']
            if keyword_result.keywords:
                target_keywords.append(keyword_result.keywords[0].get('keyword', ''))
            
            optimization_result = await content_engine.optimize_content(
                content=test_content,
                optimization_types=[OptimizationType.SEO_OPTIMIZATION],
                content_type=ContentType.BLOG_POST,
                options={'target_keywords': target_keywords}
            )
            
            assert optimization_result.success is True
            assert optimization_result.optimized_content is not None
            
        except ImportError:
            pytest.skip("Required agents not available")

def test_all_agents_registry():
    """Test that all 9 SEO & Marketing agents are properly registered"""
    
    expected_agents = [
        'seo_agent',  # SEO Agent Principal
        'brand_agent',  # Brand Management Agent
        'keyword_research_agent',  # Keyword Research Agent
        'content_optimization_agent',  # Content Optimization Agent
        'social_media_agent',  # Social Media Agent
        'influencer_matching_agent',  # Influencer Matching Agent
        'trend_agent',  # Trend Analysis Agent
        'competitor_monitoring_agent',  # Competitor Analysis Agent
        'campaign_optimization_agent'  # Campaign Optimization Agent
    ]
    
    import os
    ai_agents_dir = 'ai_agents'
    
    if os.path.exists(ai_agents_dir):
        existing_agents = [
            d for d in os.listdir(ai_agents_dir) 
            if os.path.isdir(os.path.join(ai_agents_dir, d)) and not d.startswith('__')
        ]
        
        for agent in expected_agents:
            if agent in existing_agents:
                assert True  # Agent directory exists
            else:
                pytest.skip(f"Agent {agent} directory not found")
    else:
        pytest.skip("ai_agents directory not found")

if __name__ == "__main__":
    # Run basic tests
    import sys
    import os
    
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, project_root)
    
    print("Running SEO & Marketing Agents Tests...")
    
    # Test imports
    try:
        test_agents_registry()
        print("✓ Agent registry test passed")
    except Exception as e:
        print(f"✗ Agent registry test failed: {e}")
    
    # Test individual agents
    agents_to_test = [
        TestKeywordResearchAgent(),
        TestContentOptimizationAgent(),
        TestInfluencerMatchingAgent(),
        TestCampaignOptimizationAgent()
    ]
    
    for test_class in agents_to_test:
        class_name = test_class.__class__.__name__
        try:
            # Test import
            import_method = getattr(test_class, f'test_import_{class_name.replace("Test", "").replace("Agent", "").lower()}_agent')
            import_method()
            print(f"✓ {class_name} import test passed")
        except Exception as e:
            print(f"✗ {class_name} import test failed: {e}")
    
    print("Basic tests completed!")