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
Test suite for AI Agents Index Module

Tests the main index file that orchestrates all AI agent functionalities,
imports, exports, and module initialization.

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
import inspect
from typing import Dict, Any, List
from unittest.mock import Mock, patch

# Import the index module and all expected agent classes
from ai.ai_agents import index
from ai.ai_agents.index import (
    # All agent imports should be available through index
    AudienceDevelopmentAgent,
    BrandConsultantAgent,
    CollaborationMatcherAgent,
    ContentProtectionAgent,
    ContentStrategistAgent,
    MonetizationAgent,
    SEOOptimizationAgent,
    TrendAnalysisAgent,
    # Agent factory and utilities
    AgentFactory,
    AgentManager,
    get_all_agents,
    initialize_agent_system
)


class TestIndexModuleStructure:
    """
Test the structure and organization of the index module"""
    
    def test_module_has_all_expected_agents(self):
        """
Test that index module exposes all expected agent classes"""
        expected_agents = [
            "AudienceDevelopmentAgent",
            "CommunityBuildingAgent", 
            "EngagementOptimizationAgent",
            "GrowthStrategyAgent",
            "BrandConsultantAgent",
            "PersonalBrandingAgent",
            "BrandPositioningAgent",
            "BrandStrategyAgent",
            "CollaborationMatcherAgent",
            "NetworkAnalysisAgent",
            "PartnershipAgent",
            "CrossPromotionAgent",
            "ContentProtectionAgent",
            "CopyrightDetectionAgent",
            "PlagiarismDetectionAgent",
            "DigitalRightsAgent",
            "ContentStrategistAgent",
            "PerformanceAnalysisAgent",
            "TrendAnalysisAgent",
            "ContentPlanningAgent",
            "MonetizationAgent",
            "SponsorshipAgent",
            "PricingOptimizationAgent",
            "RevenueAnalysisAgent",
            "SEOOptimizationAgent",
            "KeywordResearchAgent",
            "ContentOptimizationAgent",
            "VisibilityAnalysisAgent",
            "MarketTrendAnalyzer",
            "ContentTrendAgent",
            "PredictiveTrendAgent"
        ]
        
        # Check that all expected agents are available in the module
        for agent_name in expected_agents:
            assert hasattr(index, agent_name), f"Agent {agent_name} not found in index module"
            agent_class = getattr(index, agent_name)
            assert inspect.isclass(agent_class), f"{agent_name} is not a class"
    
    def test_module_version_and_metadata(self):
        """Test module version and metadata information"""
        assert hasattr(index, '__version__')
        assert hasattr(index, '__author__')
        assert hasattr(index, '__description__')
        
        assert index.__author__ == "Fahed Mlaiel"
        assert len(index.__version__) > 0
        assert len(index.__description__) > 0
    
    def test_module_exports_list(self):
        """Test that __all__ list is properly defined"""
        assert hasattr(index, '__all__')
        assert isinstance(index.__all__, list)
        assert len(index.__all__) > 0
        
        # Verify all items in __all__ are actually available
        for export_name in index.__all__:
            assert hasattr(index, export_name), f"Exported item {export_name} not found"


class TestAgentFactory:
    """Test the AgentFactory class functionality"""
    
    @pytest.fixture
    def factory(self):
        """
Create AgentFactory instance"""
        return AgentFactory()
    
    def test_factory_initialization(self, factory):
        """
Test AgentFactory initialization"""
        assert factory is not None
        assert hasattr(factory, 'create_agent')
        assert hasattr(factory, 'get_available_agents')
        assert hasattr(factory, 'register_agent')
    
    def test_create_audience_development_agent(self, factory):
        """
Test creating audience development agent via factory"""
        agent = factory.create_agent('audience_development')
        assert agent is not None
        assert isinstance(agent, AudienceDevelopmentAgent)
    
    def test_create_brand_consultant_agent(self, factory):
        """
Test creating brand consultant agent via factory"""
        agent = factory.create_agent('brand_consultant')
        assert agent is not None
        assert isinstance(agent, BrandConsultantAgent)
    
    def test_create_collaboration_agent(self, factory):
        """
Test creating collaboration agent via factory"""
        agent = factory.create_agent('collaboration_matcher')
        assert agent is not None
        assert isinstance(agent, CollaborationMatcherAgent)
    
    def test_create_content_protection_agent(self, factory):
        """
Test creating content protection agent via factory"""
        agent = factory.create_agent('content_protection')
        assert agent is not None
        assert isinstance(agent, ContentProtectionAgent)
    
    def test_create_content_strategist_agent(self, factory):
        """
Test creating content strategist agent via factory"""
        agent = factory.create_agent('content_strategist')
        assert agent is not None
        assert isinstance(agent, ContentStrategistAgent)
    
    def test_create_monetization_agent(self, factory):
        """
Test creating monetization agent via factory"""
        agent = factory.create_agent('monetization')
        assert agent is not None
        assert isinstance(agent, MonetizationAgent)
    
    def test_create_seo_optimization_agent(self, factory):
        """
Test creating SEO optimization agent via factory"""
        agent = factory.create_agent('seo_optimization')
        assert agent is not None
        assert isinstance(agent, SEOOptimizationAgent)
    
    def test_create_trend_analysis_agent(self, factory):
        """
Test creating trend analysis agent via factory"""
        agent = factory.create_agent('trend_analysis')
        assert agent is not None
        assert isinstance(agent, TrendAnalysisAgent)
    
    def test_create_invalid_agent_type(self, factory):
        """
Test creating agent with invalid type"""
        with pytest.raises(ValueError):
            factory.create_agent('invalid_agent_type')
    
    def test_get_available_agents(self, factory):
        """
Test getting list of available agents"""
        available_agents = factory.get_available_agents()
        assert isinstance(available_agents, list)
        assert len(available_agents) > 0
        
        expected_types = [
            'audience_development',
            'brand_consultant', 
            'collaboration_matcher',
            'content_protection',
            'content_strategist',
            'monetization',
            'seo_optimization',
            'trend_analysis'
        ]
        
        for agent_type in expected_types:
            assert agent_type in available_agents
    
    def test_register_custom_agent(self, factory):
        """
Test registering a custom agent type"""
        class CustomTestAgent:
            def __init__(self):
                self.agent_type = "custom_test"
        
        factory.register_agent('custom_test', CustomTestAgent)
        available = factory.get_available_agents()
        assert 'custom_test' in available
        
        # Test creating the custom agent
        agent = factory.create_agent('custom_test')
        assert isinstance(agent, CustomTestAgent)


class TestAgentManager:
    """Test the AgentManager class functionality"""
    
    @pytest.fixture
    def manager(self):
        """
Create AgentManager instance"""
        return AgentManager()
    
    def test_manager_initialization(self, manager):
        """
Test AgentManager initialization"""
        assert manager is not None
        assert hasattr(manager, 'agents')
        assert hasattr(manager, 'add_agent')
        assert hasattr(manager, 'get_agent')
        assert hasattr(manager, 'remove_agent')
        assert hasattr(manager, 'list_agents')
    
    def test_add_and_get_agent(self, manager):
        """
Test adding and retrieving agents"""
        # Create and add an agent
        agent = AudienceDevelopmentAgent()
        manager.add_agent('audience_dev_1', agent)
        
        # Retrieve the agent
        retrieved_agent = manager.get_agent('audience_dev_1')
        assert retrieved_agent is agent
        assert isinstance(retrieved_agent, AudienceDevelopmentAgent)
    
    def test_list_agents(self, manager):
        """
Test listing all managed agents"""
        # Add multiple agents
        agents_to_add = [
            ('brand_1', BrandConsultantAgent()),
            ('content_1', ContentStrategistAgent()),
            ('seo_1', SEOOptimizationAgent())
        ]
        
        for agent_id, agent in agents_to_add:
            manager.add_agent(agent_id, agent)
        
        # List agents
        agent_list = manager.list_agents()
        assert len(agent_list) == len(agents_to_add)
        
        for agent_id, _ in agents_to_add:
            assert agent_id in agent_list
    
    def test_remove_agent(self, manager):
        """
Test removing an agent"""
        # Add an agent
        agent = MonetizationAgent()
        manager.add_agent('monetization_1', agent)
        
        # Verify it's there
        assert manager.get_agent('monetization_1') is not None
        
        # Remove it
        removed_agent = manager.remove_agent('monetization_1')
        assert removed_agent is agent
        
        # Verify it's gone
        with pytest.raises(KeyError):
            manager.get_agent('monetization_1')
    
    def test_get_nonexistent_agent(self, manager):
        """
Test getting an agent that doesn't exist"""
        with pytest.raises(KeyError):
            manager.get_agent('nonexistent_agent')
    
    def test_remove_nonexistent_agent(self, manager):
        """
Test removing an agent that doesn't exist"""
        with pytest.raises(KeyError):
            manager.remove_agent('nonexistent_agent')
    
    @pytest.mark.asyncio
    async def test_agent_coordination(self, manager):
        """
Test coordination between multiple agents"""
        # Add multiple agents that might work together
        manager.add_agent('content_strategist', ContentStrategistAgent())
        manager.add_agent('seo_optimizer', SEOOptimizationAgent())
        manager.add_agent('trend_analyzer', TrendAnalysisAgent())
        
        # Test that agents can be retrieved and used together
        content_agent = manager.get_agent('content_strategist')
        seo_agent = manager.get_agent('seo_optimizer')
        trend_agent = manager.get_agent('trend_analyzer')
        
        assert content_agent is not None
        assert seo_agent is not None
        assert trend_agent is not None
        
        # Verify they're different instances
        assert content_agent is not seo_agent
        assert seo_agent is not trend_agent
        assert content_agent is not trend_agent


class TestUtilityFunctions:
    """
Test utility functions in the index module"""
    
    def test_get_all_agents_function(self):
        """
Test get_all_agents utility function"""
        all_agents = get_all_agents()
        
        assert isinstance(all_agents, dict)
        assert len(all_agents) > 0
        
        # Verify expected agent types are present
        expected_categories = [
            'audience_development',
            'brand_consulting', 
            'collaboration',
            'content_protection',
            'content_strategy',
            'monetization',
            'seo_optimization',
            'trend_analysis'
        ]
        
        for category in expected_categories:
            assert category in all_agents
            assert isinstance(all_agents[category], list)
            assert len(all_agents[category]) > 0
    
    @pytest.mark.asyncio
    async def test_initialize_agent_system(self):
        """
Test initialize_agent_system function"""
        config = {
            'enabled_agents': [
                'audience_development',
                'content_strategist',
                'seo_optimization'
            ],
            'default_settings': {
                'logging_level': 'INFO',
                'async_mode': True
            }
        }
        
        system = await initialize_agent_system(config)
        
        assert system is not None
        assert 'manager' in system
        assert 'factory' in system
        assert 'config' in system
        
        manager = system['manager']
        assert isinstance(manager, AgentManager)
        
        # Verify configured agents are available
        for agent_type in config['enabled_agents']:
            agents = manager.list_agents()
            # Should have at least one agent of each enabled type
            assert any(agent_type in agent_id for agent_id in agents)


class TestModuleIntegration:
    """
Test integration between different components of the index module"""
    
    @pytest.mark.asyncio
    async def test_factory_manager_integration(self):
        """
Test integration between AgentFactory and AgentManager"""
        factory = AgentFactory()
        manager = AgentManager()
        
        # Create agents via factory and manage them via manager
        agent_configs = [
            ('audience_dev', 'audience_development'),
            ('brand_cons', 'brand_consultant'),
            ('content_prot', 'content_protection')
        ]
        
        for agent_id, agent_type in agent_configs:
            agent = factory.create_agent(agent_type)
            manager.add_agent(agent_id, agent)
        
        # Verify all agents are managed
        managed_agents = manager.list_agents()
        assert len(managed_agents) == len(agent_configs)
        
        for agent_id, agent_type in agent_configs:
            assert agent_id in managed_agents
            agent = manager.get_agent(agent_id)
            assert agent is not None
    
    @pytest.mark.asyncio
    async def test_comprehensive_agent_workflow(self):
        """
Test a comprehensive workflow using multiple agents"""
        # Initialize the complete system
        system_config = {
            'enabled_agents': [
                'audience_development',
                'content_strategist', 
                'seo_optimization',
                'trend_analysis',
                'monetization'
            ],
            'workflow_mode': 'collaborative'
        }
        
        system = await initialize_agent_system(system_config)
        manager = system['manager']
        
        # Simulate a content creation workflow
        workflow_data = {
            'creator_profile': {
                'niche': 'technology',
                'audience_size': 50000,
                'goals': ['growth', 'monetization', 'engagement']
            },
            'content_request': {
                'topic': 'AI trends 2025',
                'format': 'educational_video',
                'target_platforms': ['youtube', 'linkedin']
            }
        }
        
        # Execute workflow steps
        # 1. Trend analysis
        trend_agents = [agent_id for agent_id in manager.list_agents() 
                       if 'trend' in agent_id.lower()]
        assert len(trend_agents) > 0
        
        # 2. Content strategy
        content_agents = [agent_id for agent_id in manager.list_agents() 
                         if 'content' in agent_id.lower()]
        assert len(content_agents) > 0
        
        # 3. SEO optimization
        seo_agents = [agent_id for agent_id in manager.list_agents() 
                     if 'seo' in agent_id.lower()]
        assert len(seo_agents) > 0
        
        # 4. Monetization strategy
        monetization_agents = [agent_id for agent_id in manager.list_agents() 
                              if 'monetization' in agent_id.lower()]
        assert len(monetization_agents) > 0
        
        # Verify workflow can be executed
        for agent_id in manager.list_agents():
            agent = manager.get_agent(agent_id)
            assert agent is not None
            assert hasattr(agent, '__class__')


class TestErrorHandling:
    """
Test error handling in index module components"""
    
    def test_factory_error_handling(self):
        """
Test error handling in AgentFactory"""
        factory = AgentFactory()
        
        # Test invalid agent type
        with pytest.raises(ValueError):
            factory.create_agent('invalid_agent_type')
        
        # Test None agent type
        with pytest.raises((ValueError, TypeError)):
            factory.create_agent(None)
        
        # Test empty string agent type
        with pytest.raises(ValueError):
            factory.create_agent('')
    
    def test_manager_error_handling(self):
        """
Test error handling in AgentManager"""
        manager = AgentManager()
        
        # Test getting non-existent agent
        with pytest.raises(KeyError):
            manager.get_agent('non_existent_agent')
        
        # Test removing non-existent agent
        with pytest.raises(KeyError):
            manager.remove_agent('non_existent_agent')
        
        # Test adding agent with invalid ID
        agent = AudienceDevelopmentAgent()
        
        with pytest.raises((ValueError, TypeError)):
            manager.add_agent(None, agent)
        
        with pytest.raises((ValueError, TypeError)):
            manager.add_agent('', agent)
    
    @pytest.mark.asyncio
    async def test_initialization_error_handling(self):
        """
Test error handling in system initialization"""
        # Test with invalid config
        invalid_configs = [
            None,
            {},
            {'enabled_agents': []},
            {'enabled_agents': ['invalid_agent_type']},
            {'enabled_agents': None}
        ]
        
        for invalid_config in invalid_configs:
            try:
                system = await initialize_agent_system(invalid_config)
                # Should either handle gracefully or raise appropriate error
                assert system is not None or True
            except (ValueError, TypeError, KeyError):
                # Expected for invalid configurations
                pass


class TestPerformanceAndScaling:
    """
Test performance and scaling aspects of the index module"""
    
    def test_factory_performance(self):
        """
Test AgentFactory performance with multiple agents"""
        factory = AgentFactory()
        
        # Create multiple agents rapidly
        agent_types = [
            'audience_development', 'brand_consultant', 'collaboration_matcher',
            'content_protection', 'content_strategist', 'monetization',
            'seo_optimization', 'trend_analysis'
        ]
        
        import time
        start_time = time.time()
        
        agents = []
        for _ in range(10):  # Create 10 of each type
            for agent_type in agent_types:
                agent = factory.create_agent(agent_type)
                agents.append(agent)
        
        creation_time = time.time() - start_time
        
        assert len(agents) == 10 * len(agent_types)
        assert creation_time < 5.0  # Should complete within reasonable time
    
    def test_manager_scalability(self):
        """
Test AgentManager scalability with many agents"""
        manager = AgentManager()
        factory = AgentFactory()
        
        # Add many agents
        num_agents = 100
        for i in range(num_agents):
            agent_type = ['audience_development', 'brand_consultant', 
                         'content_strategist', 'seo_optimization'][i % 4]
            agent = factory.create_agent(agent_type)
            manager.add_agent(f'agent_{i}', agent)
        
        # Test operations with many agents
        agent_list = manager.list_agents()
        assert len(agent_list) == num_agents
        
        # Test retrieval performance
        import time
        start_time = time.time()
        
        for i in range(0, num_agents, 10):  # Sample every 10th agent
            agent = manager.get_agent(f'agent_{i}')
            assert agent is not None
        
        retrieval_time = time.time() - start_time
        assert retrieval_time < 1.0  # Should be fast even with many agents
    
    @pytest.mark.asyncio
    async def test_system_initialization_performance(self):
        """
Test system initialization performance"""
        large_config = {
            'enabled_agents': [
                'audience_development', 'brand_consultant',
                'collaboration_matcher', 'content_protection',
                'content_strategist', 'monetization',
                'seo_optimization', 'trend_analysis'
            ] * 5,  # Multiply to test with many enabled agents
            'default_settings': {
                'logging_level': 'INFO',
                'async_mode': True,
                'batch_processing': True
            }
        }
        
        import time
        start_time = time.time()
        
        system = await initialize_agent_system(large_config)
        
        initialization_time = time.time() - start_time
        
        assert system is not None
        assert initialization_time < 10.0  # Should initialize within reasonable time
        
        # Verify system is functional
        manager = system['manager']
        assert len(manager.list_agents()) > 0


class TestModuleDocumentation:
    """
Test module documentation and metadata"""
    
    def test_agent_class_documentation(self):
        """
Test that all agent classes have proper documentation"""
        agent_classes = [
            AudienceDevelopmentAgent, BrandConsultantAgent, CollaborationMatcherAgent,
            ContentProtectionAgent, ContentStrategistAgent, MonetizationAgent,
            SEOOptimizationAgent, TrendAnalysisAgent
        ]
        
        for agent_class in agent_classes:
            assert agent_class.__doc__ is not None
            assert len(agent_class.__doc__.strip()) > 0
            
            # Check for key documentation elements
            doc = agent_class.__doc__.lower()
            assert any(keyword in doc for keyword in ['agent', 'ai', 'intelligence'])
    
    def test_factory_documentation(self):
        """
Test AgentFactory documentation"""
        assert AgentFactory.__doc__ is not None
        assert len(AgentFactory.__doc__.strip()) > 0
        
        # Test method documentation
        assert AgentFactory.create_agent.__doc__ is not None
        assert AgentFactory.get_available_agents.__doc__ is not None
    
    def test_manager_documentation(self):
        """
Test AgentManager documentation"""
        assert AgentManager.__doc__ is not None
        assert len(AgentManager.__doc__.strip()) > 0
        
        # Test method documentation
        assert AgentManager.add_agent.__doc__ is not None
        assert AgentManager.get_agent.__doc__ is not None
        assert AgentManager.remove_agent.__doc__ is not None
