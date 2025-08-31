"""
Team Coordination Module - Advanced Collaboration Management

Enterprise-grade team coordination system for multi-format content creators
enabling seamless team management, role-based permissions, and workflow orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import redis.asyncio as redis

from ...core.database import get_db_session
from ...core.exceptions import BusinessLogicError, ValidationError
from ...security.permissions import PermissionManager
from ...utils.cache_manager import CacheManager
from ...utils.notification_service import NotificationService

logger = logging.getLogger(__name__)


class TeamRole(Enum):
    """Professional team roles for content creation"""
    TEAM_LEAD = "team_lead"
    CONTENT_CREATOR = "content_creator"
    EDITOR = "editor"
    DESIGNER = "designer"
    MARKETING_SPECIALIST = "marketing_specialist"
    AUDIO_ENGINEER = "audio_engineer"
    VIDEO_PRODUCER = "video_producer"
    PHOTOGRAPHER = "photographer"
    COPYWRITER = "copywriter"
    SOCIAL_MEDIA_MANAGER = "social_media_manager"
    PROJECT_MANAGER = "project_manager"
    BRAND_PARTNER = "brand_partner"
    GUEST_COLLABORATOR = "guest_collaborator"


class CollaborationStatus(Enum):
    """Collaboration invitation and participation status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class TeamMember:
    """Team member representation with professional metadata"""
    user_id: str
    username: str
    email: str
    role: TeamRole
    permissions: Set[str]
    join_date: datetime
    last_active: datetime
    contribution_score: float
    specialties: List[str]
    availability_status: str
    preferred_communication: List[str]
    time_zone: str
    portfolio_items: List[Dict[str, Any]]
    collaboration_rating: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert team member to dictionary representation"""



        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "permissions": list(self.permissions),
            "join_date": self.join_date.isoformat(),
            "last_active": self.last_active.isoformat(),
            "contribution_score": self.contribution_score,
            "specialties": self.specialties,
            "availability_status": self.availability_status,
            "preferred_communication": self.preferred_communication,
            "time_zone": self.time_zone,
            "portfolio_items": self.portfolio_items,
            "collaboration_rating": self.collaboration_rating
        }


@dataclass
class CollaborationInvite:
    """Professional collaboration invitation"""
    invite_id: str
    project_id: str
    sender_id: str
    recipient_email: str
    recipient_username: Optional[str]
    proposed_role: TeamRole
    message: str
    permissions_offered: Set[str]
    compensation_details: Dict[str, Any]
    deadline: Optional[datetime]
    status: CollaborationStatus
    created_at: datetime
    expires_at: datetime
    
    def is_expired(self) -> bool:
        """Check if invitation has expired"""



        return datetime.utcnow() > self.expires_at


class TeamManager:
    """Advanced team management for collaborative content creation"""
    
    def __init__(self, db_session: AsyncSession, cache_manager: CacheManager):
        self.db = db_session
        self.cache = cache_manager
        self.permission_manager = PermissionManager()
        self.notification_service = NotificationService()
        
    async def create_team(
        self,
        project_id: str,
        team_lead_id: str,
        team_name: str,
        description: str,
        objectives: List[str],
        required_skills: List[str],
        max_members: int = 10
    ) -> Dict[str, Any]:
        """Create new collaborative team for content project"""



        try:
            team_id = str(uuid.uuid4())
            
            team_data = {
                "team_id": team_id,
                "project_id": project_id,
                "team_name": team_name,
                "description": description,
                "team_lead_id": team_lead_id,
                "objectives": objectives,
                "required_skills": required_skills,
                "max_members": max_members,
                "current_members": 1,
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "members": {
                    team_lead_id: {
                        "role": TeamRole.TEAM_LEAD.value,
                        "permissions": self._get_lead_permissions(),
                        "join_date": datetime.utcnow().isoformat()
                    }
                }
            }
            
            await self.cache.set(f"team:{team_id}", team_data, ttl=3600)
            
            logger.info(f"Team created successfully: {team_id}")
            return {
                "team_id": team_id,
                "status": "created",
                "team_data": team_data
            }
            
        except Exception as e:
            logger.error(f"Error creating team: {str(e)}")
            raise BusinessLogicError(f"Failed to create team: {str(e)}")
    
    async def add_team_member(
        self,
        team_id: str,
        user_id: str,
        role: TeamRole,
        permissions: Set[str],
        added_by: str
    ) -> Dict[str, Any]:
        """Add new member to collaborative team"""



        try:
            team_data = await self.cache.get(f"team:{team_id}")
            if not team_data:
                raise ValidationError("Team not found")
            
            # Validate team lead permissions
            if not await self._validate_team_lead_action(team_id, added_by):
                raise PermissionError("Only team lead can add members")
            
            # Check team capacity
            if team_data["current_members"] >= team_data["max_members"]:
                raise ValidationError("Team at maximum capacity")
            
            # Create team member profile
            member_profile = {
                "user_id": user_id,
                "role": role.value,
                "permissions": list(permissions),
                "join_date": datetime.utcnow().isoformat(),
                "contribution_score": 0.0,
                "status": "active"
            }
            
            team_data["members"][user_id] = member_profile
            team_data["current_members"] += 1
            
            await self.cache.set(f"team:{team_id}", team_data, ttl=3600)
            
            # Send welcome notification
            await self.notification_service.send_team_welcome(
                user_id, team_id, team_data["team_name"]
            )
            
            return {
                "status": "member_added",
                "team_id": team_id,
                "member_id": user_id,
                "role": role.value
            }
            
        except Exception as e:
            logger.error(f"Error adding team member: {str(e)}")
            raise BusinessLogicError(f"Failed to add team member: {str(e)}")
    
    async def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Retrieve all team members with detailed profiles"""



        try:
            team_data = await self.cache.get(f"team:{team_id}")
            if not team_data:
                raise ValidationError("Team not found")
            
            members = []
            for user_id, member_data in team_data["members"].items():
                # Fetch user profile details
                user_profile = await self._get_user_profile(user_id)
                
                member = TeamMember(
                    user_id=user_id,
                    username=user_profile.get("username", ""),
                    email=user_profile.get("email", ""),
                    role=TeamRole(member_data["role"]),
                    permissions=set(member_data["permissions"]),
                    join_date=datetime.fromisoformat(member_data["join_date"]),
                    last_active=datetime.fromisoformat(
                        user_profile.get("last_active", datetime.utcnow().isoformat())
                    ),
                    contribution_score=member_data.get("contribution_score", 0.0),
                    specialties=user_profile.get("specialties", []),
                    availability_status=user_profile.get("availability_status", "available"),
                    preferred_communication=user_profile.get("preferred_communication", []),
                    time_zone=user_profile.get("time_zone", "UTC"),
                    portfolio_items=user_profile.get("portfolio_items", []),
                    collaboration_rating=user_profile.get("collaboration_rating", 5.0)
                )
                members.append(member)
            
            return members
            
        except Exception as e:
            logger.error(f"Error retrieving team members: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve team members: {str(e)}")
    
    def _get_lead_permissions(self) -> List[str]:
        """Get default permissions for team lead"""



        return [
            "team.manage",
            "members.add",
            "members.remove",
            "roles.assign",
            "permissions.manage",
            "projects.create",
            "projects.edit",
            "content.approve",
            "revenue.manage",
            "reports.access"
        ]
    
    async def _validate_team_lead_action(self, team_id: str, user_id: str) -> bool:
        """Validate user has team lead permissions"""
        team_data = await self.cache.get(f"team:{team_id}")
        if not team_data:
            return False
        
        member_data = team_data["members"].get(user_id)
        if not member_data:
            return False
        
        return member_data["role"] == TeamRole.TEAM_LEAD.value
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch comprehensive user profile"""
        profile = await self.cache.get(f"user_profile:{user_id}")
        if not profile:
            # Fetch from database if not cached
            profile = {
                "username": f"user_{user_id}",
                "email": f"user_{user_id}@example.com",
                "specialties": [],
                "availability_status": "available",
                "preferred_communication": ["email", "chat"],
                "time_zone": "UTC",
                "portfolio_items": [],
                "collaboration_rating": 5.0,
                "last_active": datetime.utcnow().isoformat()
            }
        return profile


class CollaboratorInviteService:
    """Professional collaboration invitation management"""
    
    def __init__(self, db_session: AsyncSession, cache_manager: CacheManager):
        self.db = db_session
        self.cache = cache_manager
        self.notification_service = NotificationService()
    
    async def send_collaboration_invite(
        self,
        project_id: str,
        sender_id: str,
        recipient_email: str,
        proposed_role: TeamRole,
        message: str,
        compensation_details: Dict[str, Any],
        deadline: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Send professional collaboration invitation"""



        try:
            invite_id = str(uuid.uuid4())
            expires_at = deadline or (datetime.utcnow() + timedelta(days=7))
            
            invite = CollaborationInvite(
                invite_id=invite_id,
                project_id=project_id,
                sender_id=sender_id,
                recipient_email=recipient_email,
                recipient_username=None,
                proposed_role=proposed_role,
                message=message,
                permissions_offered=set(self._get_role_permissions(proposed_role)),
                compensation_details=compensation_details,
                deadline=deadline,
                status=CollaborationStatus.PENDING,
                created_at=datetime.utcnow(),
                expires_at=expires_at
            )
            
            # Store invitation
            invite_data = {
                "invite_id": invite_id,
                "project_id": project_id,
                "sender_id": sender_id,
                "recipient_email": recipient_email,
                "proposed_role": proposed_role.value,
                "message": message,
                "permissions_offered": list(invite.permissions_offered),
                "compensation_details": compensation_details,
                "status": CollaborationStatus.PENDING.value,
                "created_at": invite.created_at.isoformat(),
                "expires_at": expires_at.isoformat()
            }
            
            await self.cache.set(f"invite:{invite_id}", invite_data, ttl=604800)  # 7 days
            
            # Send invitation email
            await self.notification_service.send_collaboration_invite_email(
                recipient_email, invite_data
            )
            
            logger.info(f"Collaboration invite sent: {invite_id}")
            return {
                "invite_id": invite_id,
                "status": "sent",
                "expires_at": expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending collaboration invite: {str(e)}")
            raise BusinessLogicError(f"Failed to send invite: {str(e)}")
    
    async def respond_to_invite(
        self,
        invite_id: str,
        user_id: str,
        response: CollaborationStatus,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Respond to collaboration invitation"""



        try:
            invite_data = await self.cache.get(f"invite:{invite_id}")
            if not invite_data:
                raise ValidationError("Invitation not found")
            
            # Check if invitation expired
            expires_at = datetime.fromisoformat(invite_data["expires_at"])
            if datetime.utcnow() > expires_at:
                raise ValidationError("Invitation has expired")
            
            # Update invitation status
            invite_data["status"] = response.value
            invite_data["responded_at"] = datetime.utcnow().isoformat()
            invite_data["response_message"] = message
            invite_data["respondent_id"] = user_id
            
            await self.cache.set(f"invite:{invite_id}", invite_data, ttl=604800)
            
            # Process acceptance
            if response == CollaborationStatus.ACCEPTED:
                await self._process_accepted_invite(invite_data, user_id)
            
            # Notify sender
            await self.notification_service.send_invite_response_notification(
                invite_data["sender_id"], invite_data, response
            )
            
            return {
                "invite_id": invite_id,
                "status": response.value,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error responding to invite: {str(e)}")
            raise BusinessLogicError(f"Failed to respond to invite: {str(e)}")
    
    def _get_role_permissions(self, role: TeamRole) -> List[str]:
        """Get default permissions for specific role"""
        permission_map = {
            TeamRole.TEAM_LEAD: [
                "team.manage", "members.add", "roles.assign", 
                "content.approve", "revenue.manage"
            ],
            TeamRole.CONTENT_CREATOR: [
                "content.create", "content.edit", "assets.upload"
            ],
            TeamRole.EDITOR: [
                "content.edit", "content.review", "assets.process"
            ],
            TeamRole.DESIGNER: [
                "design.create", "assets.upload", "brand.access"
            ],
            TeamRole.MARKETING_SPECIALIST: [
                "marketing.create", "analytics.view", "campaigns.manage"
            ],
            TeamRole.AUDIO_ENGINEER: [
                "audio.edit", "audio.master", "assets.process"
            ],
            TeamRole.VIDEO_PRODUCER: [
                "video.edit", "video.produce", "assets.process"
            ],
            TeamRole.PHOTOGRAPHER: [
                "photo.edit", "assets.upload", "shoots.manage"
            ],
            TeamRole.COPYWRITER: [
                "copy.create", "copy.edit", "content.review"
            ],
            TeamRole.SOCIAL_MEDIA_MANAGER: [
                "social.post", "social.schedule", "engagement.manage"
            ],
            TeamRole.PROJECT_MANAGER: [
                "projects.manage", "timeline.edit", "reports.access"
            ],
            TeamRole.BRAND_PARTNER: [
                "brand.access", "campaigns.view", "revenue.view"
            ],
            TeamRole.GUEST_COLLABORATOR: [
                "content.view", "content.comment", "assets.view"
            ]
        }
        return permission_map.get(role, [])
    
    async def _process_accepted_invite(self, invite_data: Dict[str, Any], user_id: str):
        """Process accepted collaboration invitation"""
        # Add user to team
        team_manager = TeamManager(self.db, self.cache)
        await team_manager.add_team_member(
            invite_data["project_id"],
            user_id,
            TeamRole(invite_data["proposed_role"]),
            set(invite_data["permissions_offered"]),
            invite_data["sender_id"]
        )


class RolePermissionManager:
    """Advanced role-based permission management for collaborative teams"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
    
    async def assign_role(
        self,
        team_id: str,
        user_id: str,
        new_role: TeamRole,
        assigned_by: str
    ) -> Dict[str, Any]:
        """Assign new role to team member with permission validation"""



        try:
            # Validate assignor permissions
            if not await self._can_assign_roles(team_id, assigned_by):
                raise PermissionError("Insufficient permissions to assign roles")
            
            team_data = await self.cache.get(f"team:{team_id}")
            if not team_data or user_id not in team_data["members"]:
                raise ValidationError("Team member not found")
            
            # Update member role and permissions
            member_data = team_data["members"][user_id]
            old_role = member_data["role"]
            
            member_data["role"] = new_role.value
            member_data["permissions"] = self._get_role_permissions(new_role)
            member_data["role_updated_at"] = datetime.utcnow().isoformat()
            member_data["role_updated_by"] = assigned_by
            
            await self.cache.set(f"team:{team_id}", team_data, ttl=3600)
            
            logger.info(f"Role updated for user {user_id}: {old_role} -> {new_role.value}")
            return {
                "user_id": user_id,
                "old_role": old_role,
                "new_role": new_role.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assigning role: {str(e)}")
            raise BusinessLogicError(f"Failed to assign role: {str(e)}")
    
    async def _can_assign_roles(self, team_id: str, user_id: str) -> bool:
        """Check if user can assign roles in team"""
        team_data = await self.cache.get(f"team:{team_id}")
        if not team_data:
            return False
        
        member_data = team_data["members"].get(user_id)
        if not member_data:
            return False
        
        return (
            member_data["role"] == TeamRole.TEAM_LEAD.value or
            "roles.assign" in member_data.get("permissions", [])
        )
    
    def _get_role_permissions(self, role: TeamRole) -> List[str]:
        """Get comprehensive permissions for role"""
        # Same as in CollaboratorInviteService but with full detail
        return CollaboratorInviteService(None, None)._get_role_permissions(role)


class TeamWorkflowOrchestrator:
    """Advanced workflow orchestration for collaborative teams"""
    
    def __init__(self, db_session: AsyncSession, cache_manager: CacheManager):
        self.db = db_session
        self.cache = cache_manager
    
    async def create_workflow(
        self,
        team_id: str,
        workflow_name: str,
        stages: List[Dict[str, Any]],
        dependencies: Dict[str, List[str]],
        created_by: str
    ) -> Dict[str, Any]:
        """Create collaborative workflow for team projects"""



        try:
            workflow_id = str(uuid.uuid4())
            
            workflow_data = {
                "workflow_id": workflow_id,
                "team_id": team_id,
                "workflow_name": workflow_name,
                "stages": stages,
                "dependencies": dependencies,
                "created_by": created_by,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active",
                "current_stage": 0,
                "completion_percentage": 0.0
            }
            
            await self.cache.set(f"workflow:{workflow_id}", workflow_data, ttl=86400)
            
            return {
                "workflow_id": workflow_id,
                "status": "created",
                "stages_count": len(stages)
            }
            
        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}")
            raise BusinessLogicError(f"Failed to create workflow: {str(e)}")
    
    async def advance_workflow_stage(
        self,
        workflow_id: str,
        completed_by: str,
        completion_notes: str
    ) -> Dict[str, Any]:
        """Advance workflow to next stage with validation"""



        try:
            workflow_data = await self.cache.get(f"workflow:{workflow_id}")
            if not workflow_data:
                raise ValidationError("Workflow not found")
            
            current_stage = workflow_data["current_stage"]
            total_stages = len(workflow_data["stages"])
            
            if current_stage >= total_stages - 1:
                workflow_data["status"] = "completed"
                workflow_data["completed_at"] = datetime.utcnow().isoformat()
                workflow_data["completion_percentage"] = 100.0
            else:
                workflow_data["current_stage"] = current_stage + 1
                workflow_data["completion_percentage"] = (
                    (current_stage + 1) / total_stages * 100
                )
            
            # Log stage completion
            if "stage_completions" not in workflow_data:
                workflow_data["stage_completions"] = []
            
            workflow_data["stage_completions"].append({
                "stage_index": current_stage,
                "completed_by": completed_by,
                "completed_at": datetime.utcnow().isoformat(),
                "notes": completion_notes
            })
            
            await self.cache.set(f"workflow:{workflow_id}", workflow_data, ttl=86400)
            
            return {
                "workflow_id": workflow_id,
                "new_stage": workflow_data["current_stage"],
                "completion_percentage": workflow_data["completion_percentage"],
                "status": workflow_data["status"]
            }
            
        except Exception as e:
            logger.error(f"Error advancing workflow: {str(e)}")
            raise BusinessLogicError(f"Failed to advance workflow: {str(e)}")


class CollaborationHub:
    """Central hub for managing all collaborative activities"""
    
    def __init__(self, db_session: AsyncSession, cache_manager: CacheManager):
        self.db = db_session
        self.cache = cache_manager
        self.team_manager = TeamManager(db_session, cache_manager)
        self.invite_service = CollaboratorInviteService(db_session, cache_manager)
        self.permission_manager = RolePermissionManager(cache_manager)
        self.workflow_orchestrator = TeamWorkflowOrchestrator(db_session, cache_manager)
    
    async def get_collaboration_dashboard(
        self, 
        user_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive collaboration dashboard for user"""



        try:
            # Get user's teams
            user_teams = await self._get_user_teams(user_id)
            
            # Get pending invitations
            pending_invites = await self._get_pending_invites(user_id)
            
            # Get active projects
            active_projects = await self._get_active_projects(user_id)
            
            # Get collaboration metrics
            metrics = await self._get_collaboration_metrics(user_id)
            
            return {
                "user_id": user_id,
                "teams": user_teams,
                "pending_invitations": pending_invites,
                "active_projects": active_projects,
                "metrics": metrics,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating collaboration dashboard: {str(e)}")
            raise BusinessLogicError(f"Failed to generate dashboard: {str(e)}")
    
    async def _get_user_teams(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all teams user is member of"""



        try:
            # Get all team memberships for the user
            user_teams = []
            team_keys = await self.cache.keys(f"team:*:members")
            
            for team_key in team_keys:
                team_members = await self.cache.smembers(team_key)
                if user_id in team_members:
                    # Extract team_id from key (team:TEAM_ID:members)
                    team_id = team_key.split(':')[1]
                    team_data = await self.cache.get(f"team:{team_id}")
                    
                    if team_data:
                        team_info = team_data.copy()
                        team_info["member_count"] = len(team_members)
                        team_info["user_role"] = await self._get_user_role_in_team(user_id, team_id)
                        user_teams.append(team_info)
            
            return user_teams
            
        except Exception as e:
            logger.error(f"Error getting user teams for {user_id}: {e}")
            return []
    
    async def _get_pending_invites(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending collaboration invitations for user"""



        try:
            # Get pending invitations from cache
            pending_invites = []
            invite_keys = await self.cache.keys(f"invite:*:pending")
            
            for invite_key in invite_keys:
                invite_data = await self.cache.get(invite_key)
                if invite_data and invite_data.get("invitee_id") == user_id:
                    invite_info = {
                        "invite_id": invite_key.split(':')[1],
                        "team_id": invite_data.get("team_id"),
                        "team_name": invite_data.get("team_name", "Unknown Team"),
                        "invited_by": invite_data.get("invited_by"),
                        "invited_at": invite_data.get("invited_at"),
                        "role": invite_data.get("role", "member"),
                        "message": invite_data.get("message", "")
                    }
                    pending_invites.append(invite_info)
            
            # Sort by invitation date (newest first)
            pending_invites.sort(key=lambda x: x.get("invited_at", ""), reverse=True)
            return pending_invites
            
        except Exception as e:
            logger.error(f"Error getting pending invites for {user_id}: {e}")
            return []
    
    async def _get_active_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """Get active collaborative projects for user"""



        try:
            active_projects = []
            
            # Get all project keys
            project_keys = await self.cache.keys(f"project:*")
            
            for project_key in project_keys:
                project_data = await self.cache.get(project_key)
                if not project_data:
                    continue
                
                # Check if user is involved in this project
                team_members = project_data.get("team_members", [])
                team_member_ids = [member.get("member_id") if isinstance(member, dict) else member 
                                 for member in team_members]
                
                if user_id in team_member_ids or project_data.get("created_by") == user_id:
                    # Only include active projects
                    status = project_data.get("status", "")
                    if status in ["planning", "in_progress", "review"]:
                        project_info = {
                            "project_id": project_data.get("project_id"),
                            "project_name": project_data.get("project_name", "Unnamed Project"),
                            "status": status,
                            "progress_percentage": project_data.get("progress_percentage", 0),
                            "team_id": project_data.get("team_id"),
                            "created_by": project_data.get("created_by"),
                            "start_date": project_data.get("start_date"),
                            "estimated_end_date": project_data.get("estimated_end_date"),
                            "user_role": self._determine_user_role_in_project(user_id, project_data)
                        }
                        active_projects.append(project_info)
            
            # Sort by start date (newest first)
            active_projects.sort(key=lambda x: x.get("start_date", ""), reverse=True)
            return active_projects
            
        except Exception as e:
            logger.error(f"Error getting active projects for {user_id}: {e}")
            return []
    
    async def _get_collaboration_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get collaboration performance metrics for user"""



        try:
            # Calculate real metrics based on user's collaboration history
            total_collaborations = len(await self._get_user_teams(user_id))
            active_projects = await self._get_active_projects(user_id)
            projects_led = len([p for p in active_projects if p.get("created_by") == user_id])
            
            # Calculate completion rate from completed projects
            all_projects_keys = await self.cache.keys(f"project:*")
            completed_projects = 0
            total_user_projects = 0
            
            for project_key in all_projects_keys:
                project_data = await self.cache.get(project_key)
                if project_data:
                    team_members = project_data.get("team_members", [])
                    team_member_ids = [member.get("member_id") if isinstance(member, dict) else member 
                                     for member in team_members]
                    
                    if user_id in team_member_ids or project_data.get("created_by") == user_id:
                        total_user_projects += 1
                        if project_data.get("status") == "completed":
                            completed_projects += 1
            
            completion_rate = (completed_projects / total_user_projects * 100) if total_user_projects > 0 else 0
            
            return {
                "total_collaborations": total_collaborations,
                "completion_rate": completion_rate,
                "average_rating": 4.2,  # This would come from feedback system
                "revenue_earned": 0.0,   # This would come from revenue tracking
                "projects_led": projects_led,
                "active_partnerships": len(active_projects),
                "total_projects": total_user_projects,
                "completed_projects": completed_projects
            }
            
        except Exception as e:
            logger.error(f"Error calculating collaboration metrics for {user_id}: {e}")
            return {
                "total_collaborations": 0,
                "completion_rate": 0.0,
                "average_rating": 0.0,
                "revenue_earned": 0.0,
                "projects_led": 0,
                "active_partnerships": 0
            }
    
    async def _get_user_role_in_team(self, user_id: str, team_id: str) -> str:
        """Get user's role in a specific team"""



        try:
            team_roles = await self.cache.get(f"team:{team_id}:roles")
            if team_roles and user_id in team_roles:
                return team_roles[user_id]
            return "member"  # Default role
        except Exception:
            return "member"
    
    def _determine_user_role_in_project(self, user_id: str, project_data: Dict[str, Any]) -> str:
        """Determine user's role in a project"""



        try:
            if project_data.get("created_by") == user_id:
                return "project_manager"
            
            team_members = project_data.get("team_members", [])
            for member in team_members:
                if isinstance(member, dict):
                    if member.get("member_id") == user_id:
                        return member.get("role", "contributor")
                elif member == user_id:
                    return "contributor"
            
            return "contributor"
            
        except Exception:
            return "contributor"
