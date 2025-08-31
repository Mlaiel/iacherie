"""
IA-Influencer Agent - Workflow Agent Index

Simplified access point for the Workflow Agent module with quick setup and common workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 - All Rights Reserved

 IMPORTANT LEGAL NOTICE 
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import all main components
from . import (
    WorkflowAgent,
    WorkflowOrchestrator,
    WorkflowEngine,
    WorkflowTemplateManager,
    WorkflowScheduler,
    WorkflowMonitor,
    ExecutionMode,
    OrchestrationStrategy,
    TemplateType,
    TemplateCategory,
    ScheduleType,
    Priority
)

# Setup module logger
logger = logging.getLogger(__name__)


class WorkflowAgentFactory:
    """Factory class for creating and configuring Workflow Agent instances."""
    
    @staticmethod
    async def create_agent(
        config: Optional[Dict[str, Any]] = None
    ) -> WorkflowAgent:
        """
        Create and initialize a fully configured Workflow Agent.
        
        Args:
            config: Optional configuration dictionary
            
        Returns:
            WorkflowAgent: Initialized agent instance
        """



        try:
            # Create agent with default or custom config
            agent = WorkflowAgent()
            
            # Apply custom configuration if provided
            if config:
                if 'max_workers' in config:
                    agent.engine.max_workers = config['max_workers']
                if 'max_concurrent_executions' in config:
                    agent.scheduler.max_concurrent_executions = config['max_concurrent_executions']
                if 'monitoring_retention_days' in config:
                    agent.monitor.retention_days = config['monitoring_retention_days']
            
            # Initialize the agent
            await agent.initialize()
            
            logger.info("Workflow Agent created and initialized successfully")
            return agent
            
        except Exception as e:
            logger.error(f"Error creating Workflow Agent: {str(e)}")
            raise

    @staticmethod
    async def create_quick_setup(
        agent_type: str = "content_creator"
    ) -> WorkflowAgent:
        """
        Create a pre-configured agent for common use cases.
        
        Args:
            agent_type: Type of agent setup ('content_creator', 'musician', 'influencer', 'photographer')
            
        Returns:
            WorkflowAgent: Configured agent instance
        """



        try:
            configs = {
                'content_creator': {
                    'max_workers': 50,
                    'max_concurrent_executions': 25,
                    'monitoring_retention_days': 30
                },
                'musician': {
                    'max_workers': 100,
                    'max_concurrent_executions': 50,
                    'monitoring_retention_days': 60  # Longer retention for music releases
                },
                'influencer': {
                    'max_workers': 200,  # Higher throughput for social media
                    'max_concurrent_executions': 100,
                    'monitoring_retention_days': 30
                },
                'photographer': {
                    'max_workers': 75,
                    'max_concurrent_executions': 35,
                    'monitoring_retention_days': 45
                }
            }
            
            config = configs.get(agent_type, configs['content_creator'])
            return await WorkflowAgentFactory.create_agent(config)
            
        except Exception as e:
            logger.error(f"Error creating quick setup agent: {str(e)}")
            raise


class WorkflowTemplateLibrary:
    """Library of pre-built workflow templates for common use cases."""
    
    @staticmethod
    def get_template_recommendations(user_profile: Dict[str, Any]) -> List[str]:
        """Get template recommendations based on user profile."""



        try:
            user_type = user_profile.get('type', 'content_creator')
            interests = user_profile.get('interests', [])
            
            recommendations = []
            
            if user_type == 'musician' or 'music' in interests:
                recommendations.extend([
                    'music_release_workflow',
                    'audio_processing_pipeline',
                    'spotify_integration_workflow'
                ])
            
            if user_type == 'influencer' or 'social_media' in interests:
                recommendations.extend([
                    'social_media_workflow',
                    'content_distribution_workflow',
                    'engagement_analytics_workflow'
                ])
            
            if user_type == 'photographer' or 'photography' in interests:
                recommendations.extend([
                    'image_processing_workflow',
                    'portfolio_management_workflow',
                    'photo_protection_workflow'
                ])
            
            if 'video' in interests or user_type == 'videographer':
                recommendations.extend([
                    'video_processing_workflow',
                    'youtube_publishing_workflow',
                    'video_protection_workflow'
                ])
            
            # Universal templates
            recommendations.extend([
                'seo_optimization_workflow',
                'content_protection_workflow',
                'analytics_reporting_workflow'
            ])
            
            return list(set(recommendations))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error getting template recommendations: {str(e)}")
            return []

    @staticmethod
    def get_template_by_category(category: str) -> List[str]:
        """Get templates by category."""
        templates = {
            'music': [
                'music_release_workflow',
                'audio_mastering_workflow',
                'spotify_playlist_workflow',
                'music_licensing_workflow'
            ],
            'social_media': [
                'instagram_posting_workflow',
                'tiktok_content_workflow',
                'youtube_shorts_workflow',
                'cross_platform_posting_workflow'
            ],
            'content_protection': [
                'dmca_protection_workflow',
                'copyright_monitoring_workflow',
                'plagiarism_detection_workflow',
                'content_fingerprinting_workflow'
            ],
            'seo': [
                'keyword_research_workflow',
                'content_optimization_workflow',
                'backlink_analysis_workflow',
                'site_audit_workflow'
            ],
            'analytics': [
                'performance_reporting_workflow',
                'audience_analysis_workflow',
                'roi_tracking_workflow',
                'competitor_analysis_workflow'
            ]
        }
        
        return templates.get(category, [])


class QuickWorkflowBuilder:
    """Builder for creating common workflows quickly."""
    
    @staticmethod
    async def create_content_publishing_workflow(
        agent: WorkflowAgent,
        platforms: List[str],
        content_type: str = "general"
    ) -> str:
        """Create a content publishing workflow for specified platforms."""



        try:
            workflow_definition = {
                'id': f'content_publishing_{content_type}',
                'name': f'Content Publishing - {content_type.title()}',
                'nodes': [
                    {
                        'id': 'content_preparation',
                        'name': 'Prepare Content',
                        'task_type': 'content_agent',
                        'executor': 'prepare_content',
                        'parameters': {'content_type': content_type}
                    },
                    {
                        'id': 'seo_optimization',
                        'name': 'SEO Optimization',
                        'task_type': 'seo_agent',
                        'executor': 'optimize_for_seo',
                        'dependencies': ['content_preparation']
                    }
                ],
                'edges': [
                    {'from': 'content_preparation', 'to': 'seo_optimization'}
                ]
            }
            
            # Add platform-specific publishing nodes
            for platform in platforms:
                node_id = f'publish_{platform}'
                workflow_definition['nodes'].append({
                    'id': node_id,
                    'name': f'Publish to {platform.title()}',
                    'task_type': 'distribution_agent',
                    'executor': f'publish_to_{platform}',
                    'dependencies': ['seo_optimization'],
                    'parameters': {'platform': platform}
                })
                
                workflow_definition['edges'].append({
                    'from': 'seo_optimization',
                    'to': node_id
                })
            
            # Create workflow
            workflow_id = await agent.create_workflow(
                name=f"Content Publishing to {', '.join(platforms)}",
                description=f"Automated content publishing workflow for {content_type} content",
                workflow_definition=workflow_definition,
                category='content_publishing'
            )
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"Error creating content publishing workflow: {str(e)}")
            raise

    @staticmethod
    async def create_music_release_workflow(
        agent: WorkflowAgent,
        release_platforms: List[str],
        protection_enabled: bool = True
    ) -> str:
        """Create a complete music release workflow."""



        try:
            nodes = [
                {
                    'id': 'audio_processing',
                    'name': 'Process Audio',
                    'task_type': 'audio_agent',
                    'executor': 'process_audio_for_release'
                },
                {
                    'id': 'metadata_extraction',
                    'name': 'Extract Metadata',
                    'task_type': 'music_agent',
                    'executor': 'extract_metadata',
                    'dependencies': ['audio_processing']
                }
            ]
            
            edges = [
                {'from': 'audio_processing', 'to': 'metadata_extraction'}
            ]
            
            # Add protection if enabled
            if protection_enabled:
                nodes.append({
                    'id': 'audio_fingerprinting',
                    'name': 'Generate Audio Fingerprint',
                    'task_type': 'fingerprinting_agent',
                    'executor': 'generate_audio_fingerprint',
                    'dependencies': ['audio_processing']
                })
                
                nodes.append({
                    'id': 'protection_registration',
                    'name': 'Register Protection',
                    'task_type': 'protection_agent',
                    'executor': 'register_music_protection',
                    'dependencies': ['audio_fingerprinting', 'metadata_extraction']
                })
                
                edges.extend([
                    {'from': 'audio_processing', 'to': 'audio_fingerprinting'},
                    {'from': 'audio_fingerprinting', 'to': 'protection_registration'},
                    {'from': 'metadata_extraction', 'to': 'protection_registration'}
                ])
            
            # Add platform publishing nodes
            last_dependency = 'protection_registration' if protection_enabled else 'metadata_extraction'
            
            for platform in release_platforms:
                node_id = f'release_{platform}'
                nodes.append({
                    'id': node_id,
                    'name': f'Release on {platform.title()}',
                    'task_type': 'distribution_agent',
                    'executor': f'release_on_{platform}',
                    'dependencies': [last_dependency],
                    'parameters': {'platform': platform}
                })
                
                edges.append({
                    'from': last_dependency,
                    'to': node_id
                })
            
            workflow_definition = {
                'id': 'music_release_complete',
                'name': 'Complete Music Release',
                'nodes': nodes,
                'edges': edges
            }
            
            workflow_id = await agent.create_workflow(
                name=f"Music Release - {', '.join(release_platforms)}",
                description="Complete music release workflow with processing, protection, and distribution",
                workflow_definition=workflow_definition,
                category='music_release'
            )
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"Error creating music release workflow: {str(e)}")
            raise


class WorkflowUtilities:
    """Utility functions for workflow management."""
    
    @staticmethod
    async def bulk_execute_workflows(
        agent: WorkflowAgent,
        workflow_configs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute multiple workflows in parallel."""



        try:
            tasks = []
            
            for config in workflow_configs:
                task = agent.execute_workflow(
                    workflow_id=config['workflow_id'],
                    execution_context=config.get('context', {}),
                    execution_mode=ExecutionMode(config.get('mode', 'asynchronous')),
                    orchestration_strategy=OrchestrationStrategy(config.get('strategy', 'adaptive'))
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return [
                result if not isinstance(result, Exception) else {'error': str(result)}
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error in bulk workflow execution: {str(e)}")
            return []

    @staticmethod
    async def monitor_workflow_health(
        agent: WorkflowAgent,
        workflow_ids: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Monitor health status for multiple workflows."""



        try:
            health_statuses = {}
            
            for workflow_id in workflow_ids:
                health_status = await agent.get_workflow_status(workflow_id)
                health_statuses[workflow_id] = health_status
            
            return health_statuses
            
        except Exception as e:
            logger.error(f"Error monitoring workflow health: {str(e)}")
            return {}

    @staticmethod
    def get_performance_summary(
        health_statuses: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate performance summary from health statuses."""



        try:
            total_workflows = len(health_statuses)
            if total_workflows == 0:
                return {'total_workflows': 0}
            
            healthy_count = sum(
                1 for status in health_statuses.values()
                if status.get('health', {}).get('overall_status') == 'healthy'
            )
            
            total_executions = sum(
                status.get('performance', {}).get('total_executions', 0)
                for status in health_statuses.values()
            )
            
            avg_success_rate = sum(
                status.get('performance', {}).get('success_rate', 0)
                for status in health_statuses.values()
            ) / total_workflows
            
            avg_duration = sum(
                status.get('performance', {}).get('average_duration', 0)
                for status in health_statuses.values()
            ) / total_workflows
            
            return {
                'total_workflows': total_workflows,
                'healthy_workflows': healthy_count,
                'health_percentage': (healthy_count / total_workflows) * 100,
                'total_executions': total_executions,
                'average_success_rate': avg_success_rate,
                'average_duration': avg_duration,
                'performance_score': (avg_success_rate * 0.7 + (healthy_count / total_workflows) * 0.3) * 100
            }
            
        except Exception as e:
            logger.error(f"Error generating performance summary: {str(e)}")
            return {'error': str(e)}


# Quick access functions for common operations
async def quick_setup(agent_type: str = "content_creator") -> WorkflowAgent:
    """Quick setup function for creating a pre-configured agent."""



    return await WorkflowAgentFactory.create_quick_setup(agent_type)


async def create_simple_workflow(
    agent: WorkflowAgent,
    name: str,
    tasks: List[Dict[str, Any]]
) -> str:
    """Create a simple sequential workflow from a list of tasks."""



    try:
        nodes = []
        edges = []
        
        for i, task in enumerate(tasks):
            node_id = f"task_{i}"
            node = {
                'id': node_id,
                'name': task.get('name', f'Task {i+1}'),
                'task_type': task.get('type', 'general'),
                'executor': task.get('executor', 'default_executor')
            }
            
            # Add dependencies (sequential by default)
            if i > 0:
                node['dependencies'] = [f"task_{i-1}"]
                edges.append({
                    'from': f"task_{i-1}",
                    'to': node_id
                })
            
            nodes.append(node)
        
        workflow_definition = {
            'id': f'simple_workflow_{name.lower().replace(" ", "_")}',
            'name': name,
            'nodes': nodes,
            'edges': edges
        }
        
        return await agent.create_workflow(
            name=name,
            description=f"Simple workflow: {name}",
            workflow_definition=workflow_definition,
            category='general'
        )
        
    except Exception as e:
        logger.error(f"Error creating simple workflow: {str(e)}")
        raise


# Export main classes and functions for easy access
__all__ = [
    'WorkflowAgentFactory',
    'WorkflowTemplateLibrary',
    'QuickWorkflowBuilder',
    'WorkflowUtilities',
    'quick_setup',
    'create_simple_workflow'
]
