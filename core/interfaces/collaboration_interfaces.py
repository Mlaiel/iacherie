"""Collaboration interfaces for IA Influencer Agent.

Defines interfaces for collaboration matching, project management,
communication, contract management and teamwork functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
© 2025 - All rights reserved. Unauthorized use prohibited.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from enum import Enum


class CollaborationType(Enum):
    """Types of collaboration projects."""    MUSIC_COLLABORATION = "music_collaboration"
    VIDEO_PRODUCTION = "video_production"
    CONTENT_CREATION = "content_creation"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_VENTURE = "joint_venture"
    LICENSING_DEAL = "licensing_deal"


class ProjectStatus(Enum):
    """Project status levels."""    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CollaborationRole(Enum):
    """Roles in collaboration projects."""    PROJECT_LEAD = "project_lead"
    CONTRIBUTOR = "contributor"
    ADVISOR = "advisor"
    REVIEWER = "reviewer"
    INVESTOR = "investor"


class CollaborationMatchingInterface(ABC):
    """Interface for AI-powered collaboration matching."""    
    @abstractmethod
    async def find_collaboration_matches(
        self,
        user_id: str,
        collaboration_criteria: Dict[str, Any],
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """        Find potential collaboration partners using AI matching.
        
        Args:
            user_id: User seeking collaboration
            collaboration_criteria: Matching criteria and preferences
            max_results: Maximum number of matches to return
            
        Returns:
            List of potential collaboration matches with scores
        """        pass
    
    @abstractmethod
    async def calculate_collaboration_compatibility(
        self,
        user1_id: str,
        user2_id: str,
        collaboration_type: CollaborationType
    ) -> Dict[str, float]:
        """Calculate compatibility score between potential collaborators."""        pass
    
    @abstractmethod
    async def suggest_collaboration_opportunities(
        self,
        user_id: str,
        market_trends: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Suggest collaboration opportunities based on market trends."""        pass
    
    @abstractmethod
    async def analyze_collaboration_success_factors(
        self,
        user_id: str,
        historical_collaborations: List[str]
    ) -> Dict[str, Any]:
        """Analyze factors that lead to successful collaborations."""        pass
    
    @abstractmethod
    async def recommend_collaboration_terms(
        self,
        participants: List[str],
        collaboration_type: CollaborationType,
        project_scope: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recommend fair collaboration terms and conditions."""        pass


class ProjectManagerInterface(ABC):
    """Interface for collaboration project management."""    
    @abstractmethod
    async def create_collaboration_project(
        self,
        project_data: Dict[str, Any],
        participants: List[str],
        project_lead: str
    ) -> str:
        """        Create new collaboration project.
        
        Args:
            project_data: Project details and configuration
            participants: List of participant user IDs
            project_lead: Project leader user ID
            
        Returns:
            Created project ID
        """        pass
    
    @abstractmethod
    async def update_project_status(
        self,
        project_id: str,
        new_status: ProjectStatus,
        status_message: Optional[str] = None
    ) -> bool:
        """Update project status and notify participants."""        pass
    
    @abstractmethod
    async def assign_project_roles(
        self,
        project_id: str,
        role_assignments: Dict[str, CollaborationRole]
    ) -> bool:
        """Assign roles to project participants."""        pass
    
    @abstractmethod
    async def set_project_milestones(
        self,
        project_id: str,
        milestones: List[Dict[str, Any]]
    ) -> bool:
        """Set project milestones and deadlines."""        pass
    
    @abstractmethod
    async def track_project_progress(
        self,
        project_id: str
    ) -> Dict[str, Any]:
        """Track and analyze project progress."""        pass
    
    @abstractmethod
    async def manage_project_resources(
        self,
        project_id: str,
        resource_allocation: Dict[str, Any]
    ) -> bool:
        """Manage project resources and budget allocation."""        pass


class CommunicationInterface(ABC):
    """Interface for collaboration communication management."""    
    @abstractmethod
    async def create_project_communication_channel(
        self,
        project_id: str,
        channel_config: Dict[str, Any]
    ) -> str:
        """        Create communication channel for project.
        
        Args:
            project_id: Project identifier
            channel_config: Communication channel configuration
            
        Returns:
            Communication channel ID
        """        pass
    
    @abstractmethod
    async def send_project_message(
        self,
        channel_id: str,
        sender_id: str,
        message_content: Dict[str, Any]
    ) -> str:
        """Send message in project communication channel."""        pass
    
    @abstractmethod
    async def schedule_project_meeting(
        self,
        project_id: str,
        organizer_id: str,
        meeting_details: Dict[str, Any]
    ) -> str:
        """Schedule meeting for project participants."""        pass
    
    @abstractmethod
    async def share_project_files(
        self,
        project_id: str,
        uploader_id: str,
        file_metadata: Dict[str, Any]
    ) -> str:
        """Share files within project workspace."""        pass
    
    @abstractmethod
    async def create_project_announcement(
        self,
        project_id: str,
        sender_id: str,
        announcement: Dict[str, Any]
    ) -> str:
        """Create project-wide announcement."""        pass
    
    @abstractmethod
    async def manage_communication_permissions(
        self,
        channel_id: str,
        permissions: Dict[str, List[str]]
    ) -> bool:
        """Manage communication permissions for participants."""        pass


class ContractManagerInterface(ABC):
    """Interface for collaboration contract management."""    
    @abstractmethod
    async def generate_collaboration_contract(
        self,
        project_id: str,
        contract_terms: Dict[str, Any],
        template_type: str
    ) -> str:
        """        Generate collaboration contract from template.
        
        Args:
            project_id: Project identifier
            contract_terms: Contract terms and conditions
            template_type: Contract template to use
            
        Returns:
            Generated contract ID
        """        pass
    
    @abstractmethod
    async def review_contract_terms(
        self,
        contract_id: str,
        reviewer_id: str,
        review_comments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit contract review and comments."""        pass
    
    @abstractmethod
    async def negotiate_contract_terms(
        self,
        contract_id: str,
        proposer_id: str,
        proposed_changes: List[Dict[str, Any]]
    ) -> str:
        """Propose contract term negotiations."""        pass
    
    @abstractmethod
    async def execute_digital_signature(
        self,
        contract_id: str,
        signer_id: str,
        signature_data: Dict[str, Any]
    ) -> bool:
        """Execute digital signature on contract."""        pass
    
    @abstractmethod
    async def validate_contract_compliance(
        self,
        contract_id: str,
        compliance_check: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Validate contract compliance with regulations."""        pass
    
    @abstractmethod
    async def archive_completed_contract(
        self,
        contract_id: str,
        archival_metadata: Dict[str, Any]
    ) -> bool:
        """Archive completed contract for future reference."""        pass


class TeamworkInterface(ABC):
    """Interface for teamwork and coordination features."""    
    @abstractmethod
    async def create_team_workspace(
        self,
        project_id: str,
        workspace_config: Dict[str, Any]
    ) -> str:
        """        Create collaborative workspace for team.
        
        Args:
            project_id: Project identifier
            workspace_config: Workspace configuration settings
            
        Returns:
            Workspace ID
        """        pass
    
    @abstractmethod
    async def manage_team_permissions(
        self,
        workspace_id: str,
        permission_matrix: Dict[str, Dict[str, bool]]
    ) -> bool:
        """Manage team member permissions and access levels."""        pass
    
    @abstractmethod
    async def coordinate_workflow(
        self,
        project_id: str,
        workflow_definition: Dict[str, Any]
    ) -> str:
        """Coordinate team workflow and task dependencies."""        pass
    
    @abstractmethod
    async def track_team_contributions(
        self,
        project_id: str,
        tracking_period: str
    ) -> Dict[str, Any]:
        """Track individual team member contributions."""        pass
    
    @abstractmethod
    async def facilitate_decision_making(
        self,
        project_id: str,
        decision_request: Dict[str, Any]
    ) -> str:
        """Facilitate team decision-making processes."""        pass
    
    @abstractmethod
    async def generate_team_performance_report(
        self,
        project_id: str,
        report_period: str
    ) -> Dict[str, Any]:
        """Generate comprehensive team performance report."""        pass
