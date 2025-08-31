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
Comprehensive Tests for Example Implementations

Industrial-grade testing for example implementations, usage patterns,
best practices, and integration examples for AI agents.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import json
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

from ai.ai_agents.examples import (
    ExampleRunner,
    UsageDemonstrator,
    BestPracticesValidator,
    IntegrationExamples,
    TutorialGenerator,
    CodeExampleValidator,
    ExampleMetadata,
    ExampleCategory,
    DifficultyLevel
)

logger = logging.getLogger(__name__)


class TestBasicExamples:
    """Test basic usage examples for AI agents"""
    
    @pytest.fixture
    async def example_runner(self) -> ExampleRunner:
        """Create example runner for testing"""
        runner = ExampleRunner()
        await runner.initialize()
        
        yield runner
        
        await runner.shutdown()
    
    async def test_content_creator_basic_example(self, example_runner):
        """Test basic content creator agent example"""
        # Define basic content creation example
        content_example = {
            "name": "basic_content_creation",
            "description": "Create simple text content using ContentCreatorAgent",
            "category": ExampleCategory.BASIC,
            "difficulty": DifficultyLevel.BEGINNER,
            "code": """
# Basic Content Creation Example
from ai.ai_agents.content_creator import ContentCreatorAgent

async def create_basic_content():
    # Initialize the content creator agent
    agent = ContentCreatorAgent(
        agent_id="content_creator_001",
        config={
            "quality_preset": "standard",
            "content_types": ["text", "blog_post"]
        }
    )
    
    # Create a simple blog post
    task = {
        "type": "create_blog_post",
        "topic": "Benefits of AI in Content Creation",
        "length": "medium",
        "style": "informative"
    }
    
    result = await agent.execute_task(task)
    
    assert result["status"] == "completed"
    assert "content" in result
    assert len(result["content"]) > 100  # Should have substantial content
    
    return result

# Run the example
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(create_basic_content())
    print("Generated content:", result["content"][:200] + "...")
""",
            "expected_output": {
                "status": "completed",
                "content_type": "blog_post",
                "word_count": ">=100"
            },
            "prerequisites": ["ContentCreatorAgent"],
            "tags": ["content", "basic", "blog"]
        }
        
        # Execute the example
        execution_result = await example_runner.execute_example(content_example)
        
        assert execution_result["success"] is True
        assert execution_result["output"]["status"] == "completed"
        assert "content" in execution_result["output"]
    
    async def test_social_media_manager_example(self, example_runner):
        """Test social media manager basic example"""
        social_example = {
            "name": "basic_social_posting",
            "description": "Schedule and post content using SocialMediaManagerAgent",
            "category": ExampleCategory.BASIC,
            "difficulty": DifficultyLevel.BEGINNER,
            "code": """
# Basic Social Media Management Example
from ai.ai_agents.social_media_manager import SocialMediaManagerAgent

async def schedule_social_post():
    # Initialize the social media manager
    agent = SocialMediaManagerAgent(
        agent_id="social_manager_001",
        config={
            "platforms": ["twitter", "linkedin"],
            "posting_schedule": "immediate"
        }
    )
    
    # Schedule a post
    task = {
        "type": "schedule_post",
        "content": "Excited to share our latest AI breakthrough!  #AI #Innovation",
        "platforms": ["twitter"],
        "schedule_time": "now"
    }
    
    result = await agent.execute_task(task)
    
    assert result["status"] == "completed"
    assert "post_id" in result
    
    return result

# Run the example
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(schedule_social_post())
    print("Post scheduled:", result["post_id"])
""",
            "expected_output": {
                "status": "completed",
                "platforms_posted": ["twitter"],
                "post_id": "string"
            },
            "prerequisites": ["SocialMediaManagerAgent"],
            "tags": ["social", "posting", "scheduling"]
        }
        
        execution_result = await example_runner.execute_example(social_example)
        
        assert execution_result["success"] is True
        assert execution_result["output"]["status"] == "completed"
    
    async def test_analytics_agent_example(self, example_runner):
        """Test analytics agent basic example"""
        analytics_example = {
            "name": "basic_analytics_report",
            "description": "Generate analytics report using AnalyticsAgent",
            "category": ExampleCategory.BASIC,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "code": """
# Basic Analytics Example
from ai.ai_agents.analytics_agent import AnalyticsAgent

async def generate_analytics_report():
    # Initialize the analytics agent
    agent = AnalyticsAgent(
        agent_id="analytics_001",
        config={
            "data_sources": ["social_media", "website"],
            "report_format": "summary"
        }
    )
    
    # Generate a weekly report
    task = {
        "type": "generate_report",
        "timeframe": "last_7_days",
        "metrics": ["engagement", "reach", "conversions"],
        "format": "json"
    }
    
    result = await agent.execute_task(task)
    
    assert result["status"] == "completed"
    assert "report" in result
    assert "metrics" in result["report"]
    
    return result

# Run the example
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(generate_analytics_report())
    print("Report generated:", result["report"]["summary"])
""",
            "expected_output": {
                "status": "completed",
                "report": {
                    "timeframe": "last_7_days",
                    "metrics": "dict",
                    "summary": "string"
                }
            },
            "prerequisites": ["AnalyticsAgent"],
            "tags": ["analytics", "reporting", "metrics"]
        }
        
        execution_result = await example_runner.execute_example(analytics_example)
        
        assert execution_result["success"] is True
        assert execution_result["output"]["status"] == "completed"
        assert "report" in execution_result["output"]


class TestIntermediateExamples:
    """Test intermediate complexity examples"""
    
    @pytest.fixture
    def usage_demonstrator(self):
        """Create usage demonstrator for testing"""



        return UsageDemonstrator()
    
    async def test_multi_agent_workflow_example(self, usage_demonstrator):
        """Test multi-agent workflow example"""
        workflow_example = {
            "name": "content_to_social_workflow",
            "description": "Complete workflow from content creation to social media posting",
            "category": ExampleCategory.INTERMEDIATE,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "agents_used": ["ContentCreatorAgent", "SocialMediaManagerAgent", "AnalyticsAgent"],
            "workflow_steps": [
                "Create content",
                "Optimize for social media",
                "Schedule posts",
                "Track performance"
            ],
            "code": """
# Multi-Agent Workflow Example
from ai.ai_agents.content_creator import ContentCreatorAgent
from ai.ai_agents.social_media_manager import SocialMediaManagerAgent
from ai.ai_agents.analytics_agent import AnalyticsAgent
from ai.ai_agents.workflow import WorkflowOrchestrator

async def content_to_social_workflow():
    # Initialize agents
    content_agent = ContentCreatorAgent("content_001")
    social_agent = SocialMediaManagerAgent("social_001")
    analytics_agent = AnalyticsAgent("analytics_001")
    
    # Create workflow orchestrator
    orchestrator = WorkflowOrchestrator([
        content_agent, social_agent, analytics_agent
    ])
    
    # Define workflow
    workflow = {
        "name": "content_to_social",
        "steps": [
            {
                "agent": "content_001",
                "task": {
                    "type": "create_social_content",
                    "topic": "AI in Digital Marketing",
                    "platform_optimization": ["twitter", "linkedin"]
                }
            },
            {
                "agent": "social_001",
                "task": {
                    "type": "schedule_posts",
                    "content": "{{previous_output.content}}",
                    "platforms": ["twitter", "linkedin"],
                    "optimal_timing": True
                }
            },
            {
                "agent": "analytics_001",
                "task": {
                    "type": "setup_tracking",
                    "post_ids": "{{previous_output.post_ids}}",
                    "metrics": ["engagement", "reach", "clicks"]
                }
            }
        ]
    }
    
    # Execute workflow
    result = await orchestrator.execute_workflow(workflow)
    
    assert result["status"] == "completed"
    assert len(result["step_results"]) == 3
    
    return result

# Run the example
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(content_to_social_workflow())
    print("Workflow completed:", result["summary"])
""",
            "expected_output": {
                "status": "completed",
                "step_results": "list[3]",
                "workflow_duration": "float",
                "summary": "string"
            }
        }
        
        demonstration_result = await usage_demonstrator.demonstrate_workflow(workflow_example)
        
        assert demonstration_result["success"] is True
        assert demonstration_result["workflow_executed"] is True
        assert len(demonstration_result["step_results"]) == 3
    
    async def test_error_handling_example(self, usage_demonstrator):
        """Test error handling and recovery example"""
        error_handling_example = {
            "name": "robust_error_handling",
            "description": "Demonstrate proper error handling and recovery in agent workflows",
            "category": ExampleCategory.INTERMEDIATE,
            "difficulty": DifficultyLevel.ADVANCED,
            "code": """
# Error Handling and Recovery Example
from ai.ai_agents.base_agent import BaseAgent
from ai.ai_agents.exceptions import AgentException, TaskException

async def robust_agent_execution():
    agent = ContentCreatorAgent("robust_agent")
    
    # Task with potential for failure
    risky_task = {
        "type": "create_content",
        "topic": "Complex Technical Subject",
        "requirements": {
            "length": "very_long",
            "technical_depth": "expert",
            "deadline": "urgent"
        }
    }
    
    try:
        # Attempt primary execution
        result = await agent.execute_task(risky_task)
        
    except TaskException as e:
        logger.warning(f"Task failed: {e}, attempting recovery")
        
        # Implement fallback strategy
        fallback_task = {
            **risky_task,
            "requirements": {
                **risky_task["requirements"],
                "length": "medium",  # Reduce complexity
                "technical_depth": "intermediate"
            }
        }
        
        try:
            result = await agent.execute_task(fallback_task)
            result["recovery_used"] = True
            
        except TaskException as fallback_error:
            # Final fallback - minimal viable content
            minimal_task = {
                "type": "create_content",
                "topic": risky_task["topic"],
                "requirements": {"length": "short", "style": "summary"}
            }
            
            result = await agent.execute_task(minimal_task)
            result["minimal_fallback"] = True
    
    except AgentException as e:
        # Agent-level error - try different agent
        logger.error(f"Agent error: {e}, switching to backup")
        
        backup_agent = ContentCreatorAgent("backup_agent")
        result = await backup_agent.execute_task(risky_task)
        result["backup_agent_used"] = True
    
    return result

# Run the example
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(robust_agent_execution())
    print("Task completed with fallbacks:", result.get("recovery_used", False))
""",
            "demonstrates": [
                "Exception handling",
                "Fallback strategies", 
                "Recovery mechanisms",
                "Graceful degradation"
            ]
        }
        
        demonstration_result = await usage_demonstrator.demonstrate_error_handling(error_handling_example)
        
        assert demonstration_result["success"] is True
        assert demonstration_result["error_scenarios_tested"] > 0
    
    async def test_performance_optimization_example(self, usage_demonstrator):
        """Test performance optimization example"""
        performance_example = {
            "name": "performance_optimization",
            "description": "Optimize agent performance through caching, batching, and parallelization",
            "category": ExampleCategory.ADVANCED,
            "difficulty": DifficultyLevel.ADVANCED,
            "code": """
# Performance Optimization Example
import asyncio
from ai.ai_agents.content_creator import ContentCreatorAgent
from ai.ai_agents.optimization import PerformanceOptimizer

async def optimized_bulk_content_creation():
    # Initialize optimized agent
    agent = ContentCreatorAgent(
        "optimized_agent",
        config={
            "caching_enabled": True,
            "batch_processing": True,
            "max_concurrent_tasks": 5
        }
    )
    
    # Enable performance optimization
    optimizer = PerformanceOptimizer(agent)
    await optimizer.enable_caching()
    await optimizer.enable_batching(batch_size=10)
    
    # Create multiple content tasks
    tasks = []
    topics = [
        "AI in Healthcare",
        "Future of Remote Work", 
        "Sustainable Technology",
        "Digital Transformation",
        "Cybersecurity Trends"
    ] * 4  # 20 tasks total
    
    for i, topic in enumerate(topics):
        tasks.append({
            "type": "create_article",
            "topic": topic,
            "style": "professional",
            "length": "medium",
            "task_id": f"task_{i}"
        })
    
    # Execute with different strategies
    
    # 1. Sequential execution (baseline)
    start_time = asyncio.get_event_loop().time()
    sequential_results = []
    for task in tasks[:5]:  # Test with 5 tasks
        result = await agent.execute_task(task)
        sequential_results.append(result)
    sequential_time = asyncio.get_event_loop().time() - start_time
    
    # 2. Parallel execution
    start_time = asyncio.get_event_loop().time()
    parallel_tasks = [agent.execute_task(task) for task in tasks[5:10]]
    parallel_results = await asyncio.gather(*parallel_tasks)
    parallel_time = asyncio.get_event_loop().time() - start_time
    
    # 3. Batched execution
    start_time = asyncio.get_event_loop().time()
    batched_results = await optimizer.execute_batch(tasks[10:15])
    batched_time = asyncio.get_event_loop().time() - start_time
    
    # 4. Cached execution (repeat some tasks)
    start_time = asyncio.get_event_loop().time()
    cached_tasks = tasks[:3]  # Repeat first 3 tasks
    cached_results = []
    for task in cached_tasks:
        result = await agent.execute_task(task)
        cached_results.append(result)
    cached_time = asyncio.get_event_loop().time() - start_time
    
    performance_metrics = {
        "sequential_time": sequential_time,
        "parallel_time": parallel_time,
        "batched_time": batched_time,
        "cached_time": cached_time,
        "parallel_speedup": sequential_time / parallel_time if parallel_time > 0 else 0,
        "cache_efficiency": sequential_time / cached_time if cached_time > 0 else 0
    }
    
    assert performance_metrics["parallel_speedup"] > 1.5  # Should be significantly faster
    assert performance_metrics["cache_efficiency"] > 2.0  # Cache should be much faster
    
    return performance_metrics

# Run the example
if __name__ == "__main__":
    import asyncio
    metrics = asyncio.run(optimized_bulk_content_creation())
    print("Performance metrics:", metrics)
""",
            "performance_targets": {
                "parallel_speedup": ">1.5x",
                "cache_efficiency": ">2.0x",
                "memory_usage": "<500MB"
            }
        }
        
        demonstration_result = await usage_demonstrator.demonstrate_performance_optimization(performance_example)
        
        assert demonstration_result["success"] is True
        assert demonstration_result["performance_improved"] is True
        assert demonstration_result["speedup_achieved"] > 1.5


class TestAdvancedExamples:
    """Test advanced integration examples"""
    
    @pytest.fixture
    async def integration_examples(self) -> IntegrationExamples:
        """Create integration examples for testing"""
        examples = IntegrationExamples()
        await examples.initialize()
        
        yield examples
        
        await examples.shutdown()
    
    async def test_enterprise_integration_example(self, integration_examples):
        """Test enterprise-level integration example"""
        enterprise_example = {
            "name": "enterprise_ai_pipeline",
            "description": "Complete enterprise AI pipeline with multiple agents and external integrations",
            "category": ExampleCategory.ADVANCED,
            "difficulty": DifficultyLevel.EXPERT,
            "architecture": "microservices",
            "external_integrations": [
                "CRM_system",
                "marketing_automation", 
                "analytics_platform",
                "content_management_system"
            ],
            "code": """
# Enterprise AI Pipeline Example
from ai.ai_agents import *
from integrations.enterprise import *

class EnterpriseAIPipeline:
    def __init__(self):
        self.agents = {
            'content': ContentCreatorAgent('enterprise_content'),
            'social': SocialMediaManagerAgent('enterprise_social'),
            'analytics': AnalyticsAgent('enterprise_analytics'),
            'engagement': EngagementSpecialistAgent('enterprise_engagement')
        }
        
        self.integrations = {
            'crm': CRMIntegration(),
            'marketing': MarketingAutomationIntegration(),
            'cms': CMSIntegration(),
            'analytics_platform': AnalyticsPlatformIntegration()
        }
        
        self.orchestrator = EnterpriseOrchestrator(
            agents=self.agents,
            integrations=self.integrations
        )
    
    async def execute_campaign_pipeline(self, campaign_config):
        '''Execute complete marketing campaign pipeline'''
        
        # 1. Fetch customer data from CRM
        customer_data = await self.integrations['crm'].get_customer_segments(
            campaign_config['target_segments']
        )
        
        # 2. Generate personalized content
        content_tasks = []
        for segment in customer_data['segments']:
            task = {
                'type': 'create_personalized_content',
                'target_segment': segment,
                'campaign_theme': campaign_config['theme'],
                'content_types': ['email', 'social', 'blog']
            }
            content_tasks.append(task)
        
        content_results = await self.orchestrator.execute_parallel_tasks(
            agent_type='content',
            tasks=content_tasks
        )
        
        # 3. Optimize content for different channels
        optimization_tasks = []
        for content in content_results:
            for channel in ['email', 'social_media', 'website']:
                task = {
                    'type': 'optimize_for_channel',
                    'content': content['output'],
                    'channel': channel,
                    'audience': content['target_segment']
                }
                optimization_tasks.append(task)
        
        optimized_content = await self.orchestrator.execute_batch_tasks(
            optimization_tasks
        )
        
        # 4. Schedule and deploy across channels
        deployment_tasks = []
        for content in optimized_content:
            if content['channel'] == 'email':
                # Deploy to marketing automation
                deployment_tasks.append(
                    self.integrations['marketing'].schedule_email_campaign(content)
                )
            elif content['channel'] == 'social_media':
                # Deploy to social media
                deployment_tasks.append(
                    self.agents['social'].schedule_posts(content)
                )
            elif content['channel'] == 'website':
                # Deploy to CMS
                deployment_tasks.append(
                    self.integrations['cms'].publish_content(content)
                )
        
        deployment_results = await asyncio.gather(*deployment_tasks)
        
        # 5. Set up tracking and analytics
        tracking_setup = await self.agents['analytics'].setup_campaign_tracking({
            'campaign_id': campaign_config['id'],
            'channels': ['email', 'social_media', 'website'],
            'metrics': ['engagement', 'conversions', 'roi'],
            'attribution_model': 'multi_touch'
        })
        
        # 6. Monitor and optimize in real-time
        monitoring_task = await self.orchestrator.start_continuous_monitoring({
            'campaign_id': campaign_config['id'],
            'optimization_frequency': '1h',
            'auto_adjust_budgets': True,
            'performance_thresholds': campaign_config['kpis']
        })
        
        return {
            'status': 'campaign_launched',
            'campaign_id': campaign_config['id'],
            'content_pieces_created': len(content_results),
            'channels_activated': len(deployment_results),
            'tracking_enabled': tracking_setup['success'],
            'monitoring_active': monitoring_task['active']
        }

# Usage example
async def run_enterprise_campaign():
    pipeline = EnterpriseAIPipeline()
    
    campaign_config = {
        'id': 'Q1_2024_PRODUCT_LAUNCH',
        'theme': 'Next-Gen AI Solutions',
        'target_segments': ['enterprise_customers', 'tech_innovators'],
        'channels': ['email', 'social_media', 'website'],
        'duration': '30_days',
        'kpis': {
            'engagement_rate': 0.15,
            'conversion_rate': 0.05,
            'roi_target': 3.0
        }
    }
    
    result = await pipeline.execute_campaign_pipeline(campaign_config)
    return result

# Run the example
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(run_enterprise_campaign())
    print("Enterprise campaign launched:", result)
""",
            "expected_integrations": 4,
            "performance_requirements": {
                "campaign_launch_time": "<30_minutes",
                "concurrent_content_creation": ">10_pieces",
                "real_time_monitoring": True
            }
        }
        
        execution_result = await integration_examples.execute_enterprise_example(enterprise_example)
        
        assert execution_result["success"] is True
        assert execution_result["integrations_tested"] >= 4
        assert execution_result["performance_met"] is True
    
    async def test_ai_agent_ecosystem_example(self, integration_examples):
        """Test complete AI agent ecosystem example"""
        ecosystem_example = {
            "name": "ai_agent_ecosystem",
            "description": "Comprehensive ecosystem with agent communication, learning, and adaptation",
            "category": ExampleCategory.ADVANCED,
            "difficulty": DifficultyLevel.EXPERT,
            "features": [
                "inter_agent_communication",
                "collaborative_learning",
                "adaptive_behavior",
                "distributed_intelligence",
                "autonomous_optimization"
            ],
            "code": """
# AI Agent Ecosystem Example
from ai.ai_agents.ecosystem import AgentEcosystem
from ai.ai_agents.communication import AgentCommunicationHub
from ai.ai_agents.learning import CollaborativeLearningEngine
from ai.ai_agents.adaptation import AdaptiveBehaviorManager

class AIAgentEcosystem:
    def __init__(self):
        self.communication_hub = AgentCommunicationHub()
        self.learning_engine = CollaborativeLearningEngine()
        self.adaptation_manager = AdaptiveBehaviorManager()
        
        # Initialize diverse agent population
        self.agents = {
            'content_specialists': [
                ContentCreatorAgent(f'content_{i}') for i in range(3)
            ],
            'social_managers': [
                SocialMediaManagerAgent(f'social_{i}') for i in range(2)
            ],
            'analytics_experts': [
                AnalyticsAgent(f'analytics_{i}') for i in range(2)
            ],
            'engagement_specialists': [
                EngagementSpecialistAgent(f'engagement_{i}') for i in range(2)
            ]
        }
        
        # Connect all agents to communication hub
        for agent_group in self.agents.values():
            for agent in agent_group:
                self.communication_hub.register_agent(agent)
    
    async def demonstrate_collaborative_intelligence(self):
        '''Demonstrate agents working together and learning from each other'''
        
        # Scenario: Optimize content performance across multiple campaigns
        
        # 1. Agents share knowledge and experience
        knowledge_sharing_session = await self.communication_hub.initiate_knowledge_sharing({
            'topic': 'content_performance_optimization',
            'participants': 'all_agents',
            'sharing_mode': 'round_robin'
        })
        
        # Content agents share successful content patterns
        content_insights = []
        for agent in self.agents['content_specialists']:
            insights = await agent.share_performance_insights()
            content_insights.append(insights)
        
        # Social managers share engagement strategies
        social_insights = []
        for agent in self.agents['social_managers']:
            insights = await agent.share_engagement_strategies()
            social_insights.append(insights)
        
        # Analytics experts share performance patterns
        analytics_insights = []
        for agent in self.agents['analytics_experts']:
            insights = await agent.share_performance_patterns()
            analytics_insights.append(insights)
        
        # 2. Collaborative learning and model updates
        combined_insights = content_insights + social_insights + analytics_insights
        
        learning_results = await self.learning_engine.collaborative_learning_session({
            'insights': combined_insights,
            'learning_objectives': [
                'improve_content_quality',
                'increase_engagement_rates',
                'optimize_posting_schedules'
            ],
            'adaptation_targets': 'all_participating_agents'
        })
        
        # 3. Adaptive behavior based on collective learning
        adaptation_plans = await self.adaptation_manager.generate_adaptation_plans({
            'learning_results': learning_results,
            'agent_groups': self.agents.keys(),
            'adaptation_scope': 'ecosystem_wide'
        })
        
        # Apply adaptations to each agent group
        adaptation_results = {}
        for group_name, agents in self.agents.items():
            group_adaptations = adaptation_plans[group_name]
            group_results = []
            
            for agent in agents:
                adaptation_result = await agent.apply_adaptive_behaviors(
                    group_adaptations
                )
                group_results.append(adaptation_result)
            
            adaptation_results[group_name] = group_results
        
        # 4. Test improved performance through collaborative task
        collaborative_task = {
            'type': 'multi_channel_campaign',
            'objective': 'maximize_engagement_and_conversions',
            'duration': '7_days',
            'channels': ['blog', 'social_media', 'email', 'video'],
            'target_metrics': {
                'engagement_rate': 0.12,
                'conversion_rate': 0.08,
                'cross_channel_synergy': 0.25
            }
        }
        
        # Agents collaborate on the task
        collaboration_result = await self.execute_collaborative_task(
            collaborative_task
        )
        
        return {
            'knowledge_sharing_completed': True,
            'agents_learned': len([
                agent for group in self.agents.values() for agent in group
            ]),
            'adaptations_applied': sum(
                len(results) for results in adaptation_results.values()
            ),
            'collaborative_task_performance': collaboration_result,
            'ecosystem_intelligence_level': self.measure_collective_intelligence()
        }
    
    async def execute_collaborative_task(self, task):
        '''Execute task with full agent collaboration'''
        
        # Form optimal team based on task requirements
        optimal_team = await self.communication_hub.form_optimal_team(task)
        
        # Create collaborative execution plan
        execution_plan = await optimal_team.create_collaborative_plan(task)
        
        # Execute with real-time coordination
        execution_results = await optimal_team.execute_with_coordination(
            execution_plan
        )
        
        return execution_results
    
    def measure_collective_intelligence(self):
        '''Measure the collective intelligence level of the ecosystem'''
        
        intelligence_metrics = {
            'knowledge_diversity': self.calculate_knowledge_diversity(),
            'collaboration_efficiency': self.calculate_collaboration_efficiency(),
            'adaptive_capacity': self.calculate_adaptive_capacity(),
            'emergent_behaviors': self.detect_emergent_behaviors()
        }
        
        # Composite intelligence score
        composite_score = sum(intelligence_metrics.values()) / len(intelligence_metrics)
        
        return {
            'metrics': intelligence_metrics,
            'composite_score': composite_score,
            'intelligence_level': self.classify_intelligence_level(composite_score)
        }

# Usage example
async def run_ecosystem_demonstration():
    ecosystem = AIAgentEcosystem()
    
    # Initialize the ecosystem
    await ecosystem.initialize()
    
    # Demonstrate collaborative intelligence
    collaboration_results = await ecosystem.demonstrate_collaborative_intelligence()
    
    # Measure ecosystem evolution
    evolution_metrics = await ecosystem.measure_ecosystem_evolution()
    
    return {
        'collaboration_results': collaboration_results,
        'evolution_metrics': evolution_metrics,
        'ecosystem_maturity': ecosystem.assess_maturity_level()
    }

# Run the example
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(run_ecosystem_demonstration())
    print("AI Ecosystem demonstration completed:", result)
""",
            "ecosystem_features": [
                "knowledge_sharing",
                "collaborative_learning", 
                "adaptive_behavior",
                "emergent_intelligence"
            ]
        }
        
        execution_result = await integration_examples.execute_ecosystem_example(ecosystem_example)
        
        assert execution_result["success"] is True
        assert execution_result["agents_collaborated"] > 5
        assert execution_result["emergent_behaviors_detected"] > 0
        assert execution_result["collective_intelligence_improved"] is True


class TestBestPracticesValidation:
    """Test best practices validation for examples"""
    
    @pytest.fixture
    def best_practices_validator(self):
        """Create best practices validator for testing"""



        return BestPracticesValidator()
    
    def test_code_quality_validation(self, best_practices_validator):
        """Test code quality validation for examples"""
        # Good example code
        good_example = """
# Well-structured example with proper error handling
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def well_structured_example():
    '''
    Example demonstrating proper code structure and error handling.
    
    Returns:
        Dict[str, Any]: Results of the operation
    '''
    try:
        agent = ContentCreatorAgent(
            agent_id="example_agent",
            config={"quality": "high"}
        )
        
        await agent.initialize()
        
        task = {
            "type": "create_content",
            "topic": "AI Best Practices"
        }
        
        result = await agent.execute_task(task)
        
        # Validate result
        if not result or "content" not in result:
            raise ValueError("Invalid result from agent")
        
        return result
        
    except Exception as e:
        logger.error(f"Example execution failed: {e}")
        raise
    
    finally:
        if 'agent' in locals():
            await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(well_structured_example())
"""
        
        validation_result = best_practices_validator.validate_code_quality(good_example)
        
        assert validation_result["quality_score"] >= 0.8
        assert validation_result["has_error_handling"] is True
        assert validation_result["has_documentation"] is True
        assert validation_result["has_type_hints"] is True
        assert validation_result["follows_naming_conventions"] is True
        
        # Poor example code
        poor_example = """
# Poor example without error handling or documentation
def bad_example():
    agent = ContentCreatorAgent("agent")
    result = agent.execute_task({"type": "create"})
    return result
"""
        
        poor_validation = best_practices_validator.validate_code_quality(poor_example)
        
        assert poor_validation["quality_score"] < 0.5
        assert poor_validation["has_error_handling"] is False
        assert poor_validation["has_documentation"] is False
        assert poor_validation["issues"] is not None
    
    def test_security_practices_validation(self, best_practices_validator):
        """Test security practices validation"""
        # Secure example
        secure_example = """
import os
from cryptography.fernet import Fernet

async def secure_api_example():
    '''Example demonstrating secure API key handling'''
    
    # Secure: Get API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("API key not found in environment variables")
    
    # Secure: Use encryption for sensitive data
    encryption_key = os.getenv('ENCRYPTION_KEY', '').encode()
    cipher = Fernet(encryption_key)
    
    agent = ContentCreatorAgent(
        agent_id="secure_agent",
        config={
            "api_key": api_key,  # Passed securely
            "encryption_enabled": True
        }
    )
    
    # Secure: Validate input
    task = {
        "type": "create_content",
        "topic": "Security Best Practices"
    }
    
    # Validate task structure
    required_fields = ["type", "topic"]
    if not all(field in task for field in required_fields):
        raise ValueError("Invalid task structure")
    
    result = await agent.execute_task(task)
    
    # Secure: Don't log sensitive information
    logger.info("Content creation completed successfully")
    
    return result
"""
        
        security_validation = best_practices_validator.validate_security_practices(secure_example)
        
        assert security_validation["security_score"] >= 0.8
        assert security_validation["uses_environment_variables"] is True
        assert security_validation["has_input_validation"] is True
        assert security_validation["no_hardcoded_secrets"] is True
        
        # Insecure example
        insecure_example = """
# Insecure example with hardcoded secrets and no validation
def insecure_example():
    api_key = "sk-1234567890abcdef"  # Hardcoded secret
    
    agent = ContentCreatorAgent(
        config={"api_key": api_key}
    )
    
    # No input validation
    result = agent.execute_task(user_input)  # Direct use of user input
    
    print(f"API key: {api_key}")  # Logging sensitive data
    
    return result
"""
        
        insecure_validation = best_practices_validator.validate_security_practices(insecure_example)
        
        assert insecure_validation["security_score"] < 0.5
        assert insecure_validation["no_hardcoded_secrets"] is False
        assert insecure_validation["security_issues"] is not None
    
    def test_performance_practices_validation(self, best_practices_validator):
        """Test performance practices validation"""
        # Optimized example
        optimized_example = """
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def performance_optimized_example():
    '''Example demonstrating performance optimization techniques'''
    
    # Use connection pooling
    agent = ContentCreatorAgent(
        agent_id="optimized_agent",
        config={
            "connection_pool_size": 10,
            "cache_enabled": True,
            "batch_processing": True
        }
    )
    
    # Parallel processing for multiple tasks
    tasks = [
        {"type": "create_content", "topic": f"Topic {i}"}
        for i in range(10)
    ]
    
    # Use asyncio.gather for concurrent execution
    results = await asyncio.gather(*[
        agent.execute_task(task) for task in tasks
    ], return_exceptions=True)
    
    # Process results efficiently
    successful_results = [
        result for result in results
        if not isinstance(result, Exception)
    ]
    
    return successful_results

# Use thread pool for CPU-intensive operations
async def cpu_intensive_processing():
    with ThreadPoolExecutor(max_workers=4) as executor:
        loop = asyncio.get_event_loop()
        
        # Offload CPU-intensive work to thread pool
        result = await loop.run_in_executor(
            executor, 
            process_large_dataset, 
            dataset
        )
        
        return result
"""
        
        performance_validation = best_practices_validator.validate_performance_practices(optimized_example)
        
        assert performance_validation["performance_score"] >= 0.8
        assert performance_validation["uses_async_patterns"] is True
        assert performance_validation["has_connection_pooling"] is True
        assert performance_validation["uses_parallel_processing"] is True
        
        # Unoptimized example
        unoptimized_example = """
# Unoptimized example with blocking operations
def slow_example():
    agent = ContentCreatorAgent("slow_agent")
    
    results = []
    for i in range(100):  # Sequential processing
        task = {"type": "create_content", "topic": f"Topic {i}"}
        result = agent.execute_task_sync(task)  # Blocking call
        results.append(result)
        
        # Inefficient data processing
        processed = process_data_inefficiently(result)
        
    return results
"""
        
        poor_performance_validation = best_practices_validator.validate_performance_practices(unoptimized_example)
        
        assert poor_performance_validation["performance_score"] < 0.5
        assert poor_performance_validation["uses_async_patterns"] is False
        assert poor_performance_validation["performance_issues"] is not None


class TestTutorialGeneration:
    """Test tutorial generation functionality"""
    
    @pytest.fixture
    async def tutorial_generator(self) -> TutorialGenerator:
        """Create tutorial generator for testing"""
        generator = TutorialGenerator()
        await generator.initialize()
        
        yield generator
        
        await generator.shutdown()
    
    async def test_beginner_tutorial_generation(self, tutorial_generator):
        """Test generation of beginner-level tutorials"""
        tutorial_request = {
            "target_audience": "beginners",
            "topic": "getting_started_with_ai_agents",
            "duration": "30_minutes",
            "learning_objectives": [
                "Understand what AI agents are",
                "Create your first agent",
                "Execute a simple task",
                "Handle basic errors"
            ],
            "include_code_examples": True,
            "include_exercises": True
        }
        
        tutorial = await tutorial_generator.generate_tutorial(tutorial_request)
        
        assert tutorial["success"] is True
        assert tutorial["difficulty_level"] == "beginner"
        assert len(tutorial["sections"]) >= 4
        assert tutorial["estimated_duration"] <= 30
        assert tutorial["code_examples_count"] >= 3
        assert tutorial["exercises_count"] >= 2
        
        # Validate tutorial structure
        required_sections = ["introduction", "setup", "first_example", "conclusion"]
        tutorial_sections = [section["title"].lower() for section in tutorial["sections"]]
        
        assert all(req_section in " ".join(tutorial_sections) for req_section in required_sections)
    
    async def test_intermediate_tutorial_generation(self, tutorial_generator):
        """Test generation of intermediate-level tutorials"""
        tutorial_request = {
            "target_audience": "intermediate",
            "topic": "multi_agent_workflows",
            "duration": "60_minutes",
            "learning_objectives": [
                "Design multi-agent workflows",
                "Implement agent communication",
                "Handle workflow errors",
                "Optimize workflow performance"
            ],
            "prerequisites": ["basic_ai_agents", "python_async"],
            "include_code_examples": True,
            "include_exercises": True,
            "include_best_practices": True
        }
        
        tutorial = await tutorial_generator.generate_tutorial(tutorial_request)
        
        assert tutorial["success"] is True
        assert tutorial["difficulty_level"] == "intermediate"
        assert len(tutorial["sections"]) >= 6
        assert tutorial["estimated_duration"] <= 60
        assert tutorial["prerequisites_covered"] is True
        assert tutorial["best_practices_included"] is True
    
    async def test_advanced_tutorial_generation(self, tutorial_generator):
        """Test generation of advanced-level tutorials"""
        tutorial_request = {
            "target_audience": "advanced",
            "topic": "enterprise_ai_agent_architecture",
            "duration": "120_minutes",
            "learning_objectives": [
                "Design scalable agent architectures",
                "Implement enterprise security",
                "Build monitoring and observability",
                "Optimize for production deployment"
            ],
            "include_architecture_diagrams": True,
            "include_deployment_guides": True,
            "include_performance_benchmarks": True
        }
        
        tutorial = await tutorial_generator.generate_tutorial(tutorial_request)
        
        assert tutorial["success"] is True
        assert tutorial["difficulty_level"] == "advanced"
        assert len(tutorial["sections"]) >= 8
        assert tutorial["architecture_diagrams_count"] >= 2
        assert tutorial["deployment_guides_included"] is True
        assert tutorial["performance_benchmarks_included"] is True
    
    async def test_interactive_tutorial_features(self, tutorial_generator):
        """Test interactive tutorial features"""
        interactive_request = {
            "target_audience": "intermediate",
            "topic": "agent_debugging_and_testing",
            "format": "interactive",
            "include_live_code_examples": True,
            "include_debugging_exercises": True,
            "include_testing_scenarios": True,
            "enable_progress_tracking": True
        }
        
        tutorial = await tutorial_generator.generate_interactive_tutorial(interactive_request)
        
        assert tutorial["success"] is True
        assert tutorial["format"] == "interactive"
        assert tutorial["live_code_examples"] > 0
        assert tutorial["debugging_exercises"] > 0
        assert tutorial["testing_scenarios"] > 0
        assert tutorial["progress_tracking_enabled"] is True
        
        # Test interactive features
        assert "step_validation" in tutorial["features"]
        assert "live_code_execution" in tutorial["features"]
        assert "automated_feedback" in tutorial["features"]


@pytest.mark.integration
class TestExamplesIntegration:
    """Integration tests for complete examples system"""
    
    @pytest.fixture
    async def examples_system(self):
        """Create complete examples system for integration testing"""
        from ai.ai_agents.examples import ExamplesSystem
        
        system = ExamplesSystem()
        await system.initialize()
        
        yield system
        
        await system.shutdown()
    
    async def test_complete_examples_lifecycle(self, examples_system):
        """Test complete lifecycle of examples system"""
        # 1. Create new example
        new_example = {
            "name": "integration_test_example",
            "description": "Example for integration testing",
            "category": ExampleCategory.INTERMEDIATE,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "code": "# Integration test example code",
            "tags": ["integration", "testing"]
        }
        
        creation_result = await examples_system.create_example(new_example)
        assert creation_result["success"] is True
        example_id = creation_result["example_id"]
        
        # 2. Validate example
        validation_result = await examples_system.validate_example(example_id)
        assert validation_result["valid"] is True
        
        # 3. Execute example
        execution_result = await examples_system.execute_example(example_id)
        assert execution_result["success"] is True
        
        # 4. Update example
        updates = {
            "description": "Updated example for integration testing",
            "tags": ["integration", "testing", "updated"]
        }
        
        update_result = await examples_system.update_example(example_id, updates)
        assert update_result["success"] is True
        
        # 5. Search for example
        search_results = await examples_system.search_examples("integration")
        assert len(search_results) > 0
        assert example_id in [result["id"] for result in search_results]
        
        # 6. Generate tutorial from example
        tutorial_request = {
            "example_id": example_id,
            "target_audience": "intermediate",
            "include_explanations": True
        }
        
        tutorial_result = await examples_system.generate_tutorial_from_example(tutorial_request)
        assert tutorial_result["success"] is True
        
        # 7. Archive example
        archive_result = await examples_system.archive_example(example_id)
        assert archive_result["success"] is True
    
    async def test_examples_catalog_management(self, examples_system):
        """Test examples catalog management functionality"""
        # Get catalog overview
        catalog_overview = await examples_system.get_catalog_overview()
        
        assert "total_examples" in catalog_overview
        assert "categories" in catalog_overview
        assert "difficulty_distribution" in catalog_overview
        assert "popular_examples" in catalog_overview
        
        # Filter examples by category
        content_examples = await examples_system.filter_examples({
            "category": ExampleCategory.BASIC,
            "tags": ["content"]
        })
        
        assert isinstance(content_examples, list)
        
        # Get trending examples
        trending = await examples_system.get_trending_examples(limit=5)
        assert len(trending) <= 5
        
        # Generate example recommendations
        recommendations = await examples_system.get_recommendations({
            "user_level": "intermediate",
            "interests": ["content", "social_media"],
            "completed_examples": []
        })
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
    
    @pytest.mark.performance
    async def test_examples_system_performance(self, examples_system, assert_performance):
        """Test examples system performance"""
        # Measure example search performance
        start_time = datetime.now(timezone.utc)
        
        # Perform multiple searches
        search_queries = [
            "content creation",
            "social media",
            "analytics",
            "workflow",
            "integration"
        ]
        
        search_tasks = [
            examples_system.search_examples(query)
            for query in search_queries
        ]
        
        search_results = await asyncio.gather(*search_tasks)
        search_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        assert search_time < 10.0  # Should complete within 10 seconds
        assert_performance("examples_search", max_time=10.0)
        
        # Measure example execution performance
        start_time = datetime.now(timezone.utc)
        
        # Execute multiple examples in parallel
        example_ids = [result["id"] for result in search_results[0][:3]]
        execution_tasks = [
            examples_system.execute_example(example_id)
            for example_id in example_ids
        ]
        
        execution_results = await asyncio.gather(*execution_tasks, return_exceptions=True)
        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        assert execution_time < 60.0  # Should execute within 60 seconds
        assert_performance("examples_execution", max_time=60.0)
