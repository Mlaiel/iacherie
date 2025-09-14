"""Collaboration System Integration Module

This module provides integration between the new 12-agent collaboration system
and the existing Ainflue agent ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from collaboration_orchestrator import (
    CollaborationOrchestrator,
    CollaborationType,
    CollaborationProject,
    CreatorProfile,
    create_collaboration_orchestrator
)

logger = logging.getLogger(__name__)

class CollaborationSystemManager:
    """
    Manages the integration of the 12-agent collaboration system
    with the broader Ainflue platform.
    """
    
    def __init__(self) -> None:
        self.orchestrator = create_collaboration_orchestrator()
        self.integration_status = "active"
        self.registered_workflows = {}
        
    async def start_collaboration_workflow(
        self,
        creator_id: str,
        collaboration_type: str,
        project_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Start a new collaboration workflow through the orchestrator
        
        Args:
            creator_id: ID of the creator initiating collaboration
            collaboration_type: Type of collaboration (content_creation, etc.)
            project_details: Details about the collaboration project
            
        Returns:
            Dictionary containing workflow information and status
        """
        try:
            # Prepare collaboration request
            collaboration_request = {
                "creator_name": project_details.get("creator_name", f"Creator_{creator_id}"),
                "title": project_details.get("title", "New Collaboration Project"),
                "description": project_details.get("description", ""),
                "type": collaboration_type,
                "skills": project_details.get("required_skills", []),
                "content_types": project_details.get("content_types", ["video"]),
                "requirements": project_details.get("requirements", {}),
                "budget": project_details.get("budget"),
                "complexity": project_details.get("complexity", "medium")
            }
            
            # Initiate workflow through orchestrator
            result = await self.orchestrator.initiate_collaboration_workflow(
                creator_id, collaboration_request
            )
            
            if result["success"]:
                # Register workflow for tracking
                workflow_id = result["workflow_id"]
                self.registered_workflows[workflow_id] = {
                    "creator_id": creator_id,
                    "started_at": datetime.now(timezone.utc),
                    "status": "active",
                    "project_id": result["project_id"]
                }
                
                logger.info(f"Collaboration workflow {workflow_id} started successfully")
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to start collaboration workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_collaboration_matches(
        self,
        creator_id: str,
        creator_profile: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get collaboration matches for a creator
        
        Args:
            creator_id: ID of the creator
            creator_profile: Profile information for the creator
            requirements: Requirements for collaboration
            
        Returns:
            List of potential collaboration matches
        """
        try:
            # Create creator profile
            profile = CreatorProfile(
                creator_id=creator_id,
                name=creator_profile.get("name", f"Creator_{creator_id}"),
                skills=creator_profile.get("skills", []),
                specialties=creator_profile.get("specialties", []),
                audience_size=creator_profile.get("audience_size", 0),
                engagement_rate=creator_profile.get("engagement_rate", 0.0),
                content_types=creator_profile.get("content_types", [])
            )
            
            # Use matching agent to find matches
            matching_agent = self.orchestrator.agents["collaboration_matching"]
            matches = await matching_agent.find_matches(profile, requirements)
            
            return matches
            
        except Exception as e:
            logger.error(f"Failed to get collaboration matches: {e}")
            return []
    
    async def create_marketplace_listing(
        self,
        creator_id: str,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a marketplace listing for collaboration
        
        Args:
            creator_id: ID of the creator
            project_data: Project information
            
        Returns:
            Dictionary containing listing information
        """
        try:
            # Create collaboration project
            project = CollaborationProject(
                title=project_data.get("title", "Collaboration Project"),
                description=project_data.get("description", ""),
                collaboration_type=CollaborationType(project_data.get("type", "content_creation")),
                creators=[creator_id],
                requirements=project_data.get("requirements", {}),
                budget=project_data.get("budget")
            )
            
            # Create listing through marketplace agent
            marketplace_agent = self.orchestrator.agents["marketplace"]
            result = await marketplace_agent.create_listing(project)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create marketplace listing: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_creator_skills(
        self,
        creator_id: str,
        portfolio_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze creator skills using the skill matching agent
        
        Args:
            creator_id: ID of the creator
            portfolio_data: Creator's portfolio data
            
        Returns:
            Dictionary containing skill analysis
        """
        try:
            skill_agent = self.orchestrator.agents["skill_matching"]
            analysis = await skill_agent.analyze_skills(creator_id, portfolio_data)
            
            return {
                "success": True,
                "creator_id": creator_id,
                "skills_analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze creator skills: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_revenue_agreement(
        self,
        project_id: str,
        participants: List[str],
        revenue_terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create revenue sharing agreement for collaboration
        
        Args:
            project_id: ID of the collaboration project
            participants: List of participant IDs
            revenue_terms: Revenue sharing terms
            
        Returns:
            Dictionary containing agreement information
        """
        try:
            revenue_agent = self.orchestrator.agents["revenue_sharing"]
            result = await revenue_agent.create_revenue_agreement(
                project_id, participants, revenue_terms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create revenue agreement: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_quality_check(
        self,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run quality assurance check on content
        
        Args:
            content_data: Content to be checked
            
        Returns:
            Dictionary containing quality assessment
        """
        try:
            qa_agent = self.orchestrator.agents["quality_assurance"]
            result = await qa_agent.run_quality_check(content_data)
            
            return {
                "success": True,
                "quality_check": result
            }
            
        except Exception as e:
            logger.error(f"Failed to run quality check: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a collaboration workflow"""
        try:
            # Get status from orchestrator
            orchestrator_status = await self.orchestrator.get_workflow_status(workflow_id)
            
            # Add local tracking information
            if workflow_id in self.registered_workflows:
                local_info = self.registered_workflows[workflow_id]
                orchestrator_status.update({
                    "local_tracking": local_info
                })
            
            return orchestrator_status
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall collaboration system health"""
        try:
            health = await self.orchestrator.get_system_health()
            
            # Add integration-specific information
            health.update({
                "integration_status": self.integration_status,
                "registered_workflows": len(self.registered_workflows),
                "system_manager": {
                    "status": "healthy",
                    "version": "1.0.0"
                }
            })
            
            return health
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "integration_status": "error",
                "error": str(e)
            }

# Global instance for easy access
_collaboration_manager = None

def get_collaboration_manager() -> CollaborationSystemManager:
    """Get or create the global collaboration system manager"""
    global _collaboration_manager
    if _collaboration_manager is None:
        _collaboration_manager = CollaborationSystemManager()
    return _collaboration_manager

# Convenience functions for direct access to collaboration features
async def start_collaboration(
    creator_id: str,
    collaboration_type: str,
    project_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
Convenience function to start a collaboration workflow"""
    manager = get_collaboration_manager()
    return await manager.start_collaboration_workflow(creator_id, collaboration_type, project_details)

async def find_collaborators(
    creator_id: str,
    creator_profile: Dict[str, Any],
    requirements: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
Convenience function to find collaboration matches"""
    manager = get_collaboration_manager()
    return await manager.get_collaboration_matches(creator_id, creator_profile, requirements)

async def create_project_listing(
    creator_id: str,
    project_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
Convenience function to create marketplace listing"""
    manager = get_collaboration_manager()
    return await manager.create_marketplace_listing(creator_id, project_data)

async def assess_content_quality(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """
Convenience function to run quality assessment"""
    manager = get_collaboration_manager()
    return await manager.run_quality_check(content_data)

# Export key classes and functions
__all__ = [
    'CollaborationSystemManager',
    'get_collaboration_manager',
    'start_collaboration',
    'find_collaborators', 
    'create_project_listing',
    'assess_content_quality'
]