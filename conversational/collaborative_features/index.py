"""Collaborative Features Index - Central Access Point

This module provides centralized access to all collaborative features
and services for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from . import team_coordination, project_management, matching_engine
from . import communication_hub, workflow_synchronization, revenue_sharing
from . import collaboration_analytics, networking_engine
from . import content_co_creation, partnership_management

logger = logging.getLogger(__name__)


class CollaborativeFeaturesRegistry:
    """
    Central registry for all collaborative features and services
    
    This class provides a unified interface to access and manage
    all collaboration-related functionality in the platform.
    """
    
    def __init__(self):
        self._services = {}
        self._initialized = False
    
    async def initialize_services(self, config: Dict[str, Any]) -> None:
        """
Initialize all collaborative services"""
        try:
            if self._initialized:
                return
            
            # Initialize core services
            self._services.update({
                'team_manager': getattr(team_coordination, 'TeamManager', None),
                'project_coordinator': getattr(project_management, 'ProjectCoordinator', None),
                'collaboration_matcher': getattr(matching_engine, 'CollaborationMatcher', None),
                'communication_hub': getattr(communication_hub, 'CollaborativeCommunicationManager', None),
                'workflow_synchronizer': getattr(workflow_synchronization, 'WorkflowSynchronizer', None),
                'revenue_distributor': getattr(revenue_sharing, 'RevenueDistributionEngine', None),
                'analytics_collector': getattr(collaboration_analytics, 'CollaborationMetricsCollector', None),
                'networking_engine': getattr(networking_engine, 'ProfessionalNetworkingEngine', None),
                'cocreation_workspace': getattr(content_co_creation, 'CoCreationWorkspace', None),
                'partnership_broker': getattr(partnership_management, 'PartnershipBroker', None)
            })
            
            self._initialized = True
            logger.info("Collaborative features services initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing collaborative services: {e}")
            raise
    
    def get_service(self, service_name: str) -> Any:
        """Get a specific collaborative service"""
        if not self._initialized:
            raise RuntimeError("Services not initialized. Call initialize_services() first.")
        
        return self._services.get(service_name)
    
    def list_available_services(self) -> List[str]:
        """List all available collaborative services"""
        return list(self._services.keys())


class CollaborationWorkflowManager:
    """
    High-level workflow manager for collaboration processes
    
    This class orchestrates complex collaboration workflows by
    coordinating multiple services and ensuring proper execution order.
    """
    
    def __init__(self, registry: CollaborativeFeaturesRegistry):
        self.registry = registry
        self.active_workflows = {}
    
    async def start_collaboration_workflow(
        self,
        workflow_type: str,
        participants: List[str],
        project_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Start a comprehensive collaboration workflow"""
        try:
            workflow_id = f"workflow_{workflow_type}_{len(self.active_workflows)}"
            
            # Get required services
            team_manager_class = self.registry.get_service('team_manager')
            project_coordinator_class = self.registry.get_service('project_coordinator')
            communication_hub_class = self.registry.get_service('communication_hub')
            
            if not all([team_manager_class, project_coordinator_class, communication_hub_class]):
                raise RuntimeError("Required services not available")
            
            # Initialize service instances
            team_manager = team_manager_class() if team_manager_class else None
            project_coordinator = project_coordinator_class() if project_coordinator_class else None
            communication_hub = communication_hub_class() if communication_hub_class else None
            
            # Create team
            team_result = await team_manager.create_team(
                project_id=project_details.get('project_id'),
                team_lead_id=participants[0],
                team_name=project_details.get('name'),
                description=project_details.get('description'),
                objectives=project_details.get('objectives', []),
                required_skills=project_details.get('required_skills', [])
            )
            
            # Initialize project
            project_result = await project_coordinator.initialize_project(
                team_id=team_result['team_id'],
                project_details=project_details
            )
            
            # Set up communication
            comm_result = await communication_hub.setup_project_communication(
                project_id=project_details.get('project_id'),
                participants=participants
            )
            
            # Track workflow
            self.active_workflows[workflow_id] = {
                'type': workflow_type,
                'participants': participants,
                'team_id': team_result['team_id'],
                'project_id': project_details.get('project_id'),
                'communication_channels': comm_result.get('channels'),
                'status': 'active',
                'created_at': datetime.utcnow().isoformat()
            }
            
            return {
                'workflow_id': workflow_id,
                'status': 'started',
                'team_id': team_result['team_id'],
                'project_id': project_details.get('project_id'),
                'next_steps': [
                    'Add remaining team members',
                    'Define project milestones',
                    'Set up content creation workflow'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error starting collaboration workflow: {e}")
            raise


# Global registry instance
collaboration_registry = CollaborativeFeaturesRegistry()


async def get_collaboration_service(service_name: str) -> Any:
    """Get a collaboration service from the global registry"""
    return collaboration_registry.get_service(service_name)


async def initialize_collaboration_features(config: Dict[str, Any] = None) -> None:
    """
Initialize all collaboration features"""
    await collaboration_registry.initialize_services(config or {})


def get_feature_summary() -> Dict[str, Any]:
    """
Get summary of all collaborative features"""
    return {
        "module_name": "collaborative_features",
        "version": "1.0.0",
        "total_services": len(collaboration_registry.list_available_services()),
        "available_services": collaboration_registry.list_available_services(),
        "capabilities": [
            "AI-powered creator matching",
            "Real-time collaboration",
            "Project management",
            "Revenue sharing",
            "Analytics and insights",
            "Professional networking",
            "Content co-creation",
            "Partnership management"
        ],
        "supported_content_types": [
            "audio", "video", "image", "text", 
            "music", "podcast", "blog_post", 
            "social_media", "marketing_material"
        ],
        "platforms_supported": [
            "Spotify", "YouTube", "Instagram", "TikTok",
            "Twitter", "LinkedIn", "Facebook", "Twitch"
        ]
    }
