"""Invitation System Database Module

Professional invitation and onboarding system for team collaboration.
Handles invitations, approvals, and team member onboarding workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices
"""from typing import List, Dict, Any, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import logging
import hashlib
import secrets
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, 
    ForeignKey, DECIMAL, ARRAY, JSON, Index, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
import asyncio
import aioredis
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

Base = declarative_base()

class InvitationStatus(Enum):
    """Invitation status enumeration"""    PENDING = "pending"
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REVOKED = "revoked"

class InvitationType(Enum):
    """Invitation type enumeration"""    PROJECT_COLLABORATION = "project_collaboration"
    TEAM_MEMBERSHIP = "team_membership"
    CONTENT_REVIEW = "content_review"
    GUEST_ACCESS = "guest_access"
    EXTERNAL_COLLABORATION = "external_collaboration"
    CONSULTATION = "consultation"

class OnboardingStage(Enum):
    """Onboarding stage enumeration"""    INVITATION_SENT = "invitation_sent"
    PROFILE_SETUP = "profile_setup"
    SKILL_ASSESSMENT = "skill_assessment"
    TEAM_INTRODUCTION = "team_introduction"
    PROJECT_BRIEFING = "project_briefing"
    TOOL_TRAINING = "tool_training"
    FIRST_TASK_ASSIGNMENT = "first_task_assignment"
    ONBOARDING_COMPLETE = "onboarding_complete"

class ProjectInvitation(Base):
    """    Comprehensive project invitation system.
    Manages invitations with advanced tracking and workflow features.
    """    __tablename__ = 'project_invitations'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invitation_id = Column(String(100), unique=True, nullable=False, index=True)
    invitation_token = Column(String(255), unique=True, nullable=False)
    
    # Invitation context
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=False)
    invitation_type = Column(ENUM(InvitationType), nullable=False)
    invited_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Invitee information
    invited_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))  # If user exists
    invited_email = Column(String(255), nullable=False)
    invited_name = Column(String(255))
    external_user = Column(Boolean, default=False)
    
    # Role and permissions
    proposed_role = Column(String(50), nullable=False)
    access_level = Column(String(20), default='member')
    permissions = Column(JSONB)
    responsibility_areas = Column(ARRAY(String))
    
    # Invitation details
    subject = Column(String(255))
    message = Column(Text)
    custom_message = Column(Text)
    invitation_requirements = Column(JSONB)
    
    # Timeline and expiration
    expires_at = Column(DateTime, nullable=False)
    max_uses = Column(Integer, default=1)
    current_uses = Column(Integer, default=0)
    auto_approve = Column(Boolean, default=False)
    
    # Status and tracking
    status = Column(ENUM(InvitationStatus), default=InvitationStatus.PENDING)
    sent_at = Column(DateTime)
    viewed_at = Column(DateTime)
    responded_at = Column(DateTime)
    
    # Response and feedback
    response_message = Column(Text)
    decline_reason = Column(String(100))
    acceptance_conditions = Column(JSONB)
    
    # Delivery tracking
    delivery_method = Column(String(20), default='email')  # email, link, direct
    delivery_status = Column(String(20), default='pending')
    delivery_attempts = Column(Integer, default=0)
    delivery_log = Column(JSONB)
    
    # Security and validation
    ip_restrictions = Column(ARRAY(String))
    domain_restrictions = Column(ARRAY(String))
    verification_required = Column(Boolean, default=False)
    verification_completed = Column(Boolean, default=False)
    
    # Follow-up and reminders
    reminder_sent = Column(Boolean, default=False)
    reminder_count = Column(Integer, default=0)
    follow_up_schedule = Column(JSONB)
    
    # Analytics and insights
    view_count = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)
    conversion_tracking = Column(JSONB)
    
    # Metadata
    tags = Column(ARRAY(String))
    custom_fields = Column(JSONB)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_invitation_project_status', 'project_id', 'status'),
        Index('idx_invitation_email_status', 'invited_email', 'status'),
        Index('idx_invitation_token', 'invitation_token'),
        Index('idx_invitation_expires', 'expires_at'),
    )

class OnboardingWorkflow(Base):
    """    Team member onboarding workflow management.
    Tracks onboarding progress and ensures complete integration.
    """    __tablename__ = 'onboarding_workflows'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(String(100), unique=True, nullable=False)
    
    # Workflow context
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    invitation_id = Column(UUID(as_uuid=True), ForeignKey('project_invitations.id'))
    assigned_buddy = Column(UUID(as_uuid=True), ForeignKey('users.id'))  # Onboarding buddy
    
    # Workflow progress
    current_stage = Column(ENUM(OnboardingStage), default=OnboardingStage.INVITATION_SENT)
    completed_stages = Column(ARRAY(String))
    stage_progress = Column(JSONB)  # Progress per stage
    overall_progress = Column(Float, default=0.0)
    
    # Timeline tracking
    started_at = Column(DateTime, default=datetime.utcnow)
    target_completion_date = Column(DateTime)
    actual_completion_date = Column(DateTime)
    stage_deadlines = Column(JSONB)
    
    # Stage-specific data
    profile_setup_data = Column(JSONB)
    skill_assessment_results = Column(JSONB)
    training_completions = Column(JSONB)
    first_task_feedback = Column(JSONB)
    
    # Quality and feedback
    onboarding_feedback = Column(JSONB)
    buddy_feedback = Column(JSONB)
    satisfaction_score = Column(Float)
    improvement_suggestions = Column(Text)
    
    # Customization
    custom_checklist = Column(JSONB)
    role_specific_requirements = Column(JSONB)
    project_specific_training = Column(JSONB)
    
    # Automation and notifications
    automated_reminders = Column(Boolean, default=True)
    notification_schedule = Column(JSONB)
    escalation_rules = Column(JSONB)
    
    # Status and completion
    is_completed = Column(Boolean, default=False)
    completion_certificate = Column(String(500))  # URL to certificate
    integration_status = Column(String(20), default='in_progress')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_onboarding_project_user', 'project_id', 'user_id'),
        Index('idx_onboarding_stage_progress', 'current_stage', 'overall_progress'),
        Index('idx_onboarding_completion', 'is_completed'),
    )

class InvitationTemplate(Base):
    """    Reusable invitation templates for different scenarios.
    Enables consistent and professional invitation management.
    """    __tablename__ = 'invitation_templates'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(String(100), unique=True, nullable=False)
    template_name = Column(String(255), nullable=False)
    
    # Template categorization
    invitation_type = Column(ENUM(InvitationType), nullable=False)
    category = Column(String(50))  # formal, casual, urgent, etc.
    industry = Column(String(50))  # music, video, design, etc.
    
    # Template content
    subject_template = Column(String(255), nullable=False)
    message_template = Column(Text, nullable=False)
    html_template = Column(Text)
    
    # Customization
    variable_fields = Column(JSONB)  # Available template variables
    required_fields = Column(ARRAY(String))
    optional_fields = Column(ARRAY(String))
    
    # Default settings
    default_permissions = Column(JSONB)
    default_expiry_days = Column(Integer, default=7)
    default_auto_approve = Column(Boolean, default=False)
    
    # Branding and styling
    branding_elements = Column(JSONB)
    color_scheme = Column(JSONB)
    logo_url = Column(String(500))
    
    # Usage and analytics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    average_response_time = Column(Float)  # Hours
    
    # Template metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    tags = Column(ARRAY(String))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_template_type_category', 'invitation_type', 'category'),
        Index('idx_template_active', 'is_active'),
        Index('idx_template_usage', 'usage_count'),
    )

@dataclass
class InvitationRequest:
    """Data class for invitation creation requests"""    project_id: str
    invited_email: str
    invitation_type: InvitationType
    proposed_role: str
    invited_by: str
    invited_name: str = None
    message: str = None
    permissions: Dict[str, Any] = None
    expires_in_days: int = 7
    template_id: str = None
    auto_approve: bool = False

@dataclass
class OnboardingConfig:
    """Data class for onboarding configuration"""    project_id: str
    user_id: str
    invitation_id: str = None
    assigned_buddy: str = None
    custom_stages: List[str] = None
    target_completion_days: int = 14
    automated_reminders: bool = True

class InvitationSystemManager:
    """    Enterprise invitation system manager with comprehensive features.
    Handles invitations, onboarding, and team integration workflows.
    """    
    def __init__(self, db_session, redis_client: aioredis.Redis = None, email_service = None):
        self.db_session = db_session
        self.redis_client = redis_client
        self.email_service = email_service
        self.cache_ttl = 3600  # 1 hour cache
        
        # Security settings
        self.token_length = 64
        self.max_invitation_age_days = 30
        self.max_reminder_count = 3
    
    async def create_invitation(self, request: InvitationRequest) -> Optional[ProjectInvitation]:
        """        Create a professional project invitation.
        
        Args:
            request: Invitation creation request
            
        Returns:
            Created invitation instance
        """        try:
            # Generate secure invitation token
            invitation_token = self._generate_secure_token()
            invitation_id = self._generate_invitation_id(request.project_id)
            
            # Calculate expiration date
            expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
            
            # Get template if specified
            template = None
            if request.template_id:
                template = await self._get_invitation_template(request.template_id)
            
            # Create invitation
            invitation = ProjectInvitation(
                invitation_id=invitation_id,
                invitation_token=invitation_token,
                project_id=uuid.UUID(request.project_id),
                invitation_type=request.invitation_type,
                invited_by=uuid.UUID(request.invited_by),
                invited_email=request.invited_email.lower(),
                invited_name=request.invited_name,
                proposed_role=request.proposed_role,
                permissions=request.permissions or self._default_permissions(request.proposed_role),
                expires_at=expires_at,
                auto_approve=request.auto_approve,
                subject=self._generate_subject(template, request),
                message=self._generate_message(template, request),
                invitation_requirements=self._generate_requirements(request),
                follow_up_schedule=self._generate_follow_up_schedule(request.expires_in_days),
                custom_fields={}
            )
            
            # Check for existing user
            existing_user = await self._find_user_by_email(request.invited_email)
            if existing_user:
                invitation.invited_user_id = existing_user.id
                invitation.external_user = False
            else:
                invitation.external_user = True
            
            # Save invitation
            self.db_session.add(invitation)
            await self.db_session.commit()
            await self.db_session.refresh(invitation)
            
            # Send invitation email
            await self._send_invitation_email(invitation)
            
            # Update template usage if used
            if template:
                await self._update_template_usage(template.id)
            
            # Cache invitation
            if self.redis_client:
                await self._cache_invitation(invitation)
            
            logger.info(f"Invitation created: {invitation_id}")
            
            return invitation
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create invitation: {str(e)}")
            raise
    
    async def accept_invitation(
        self, 
        invitation_token: str, 
        user_id: str = None,
        response_message: str = None
    ) -> Optional[ProjectInvitation]:
        """        Accept a project invitation and initiate onboarding.
        
        Args:
            invitation_token: Unique invitation token
            user_id: User accepting the invitation
            response_message: Optional acceptance message
            
        Returns:
            Updated invitation instance
        """        try:
            # Get invitation by token
            invitation = await self._get_invitation_by_token(invitation_token)
            if not invitation:
                logger.warning(f"Invitation not found for token: {invitation_token}")
                return None
            
            # Validate invitation
            if not await self._validate_invitation(invitation):
                return None
            
            # Update invitation status
            invitation.status = InvitationStatus.ACCEPTED
            invitation.responded_at = datetime.utcnow()
            invitation.response_message = response_message
            invitation.current_uses += 1
            
            # Link user if provided
            if user_id:
                invitation.invited_user_id = uuid.UUID(user_id)
            
            # Save changes
            await self.db_session.commit()
            
            # Create team member record
            team_member = await self._create_team_member_from_invitation(invitation)
            
            # Initialize onboarding workflow
            onboarding = await self._initialize_onboarding_workflow(invitation, team_member)
            
            # Send welcome notification
            await self._send_welcome_notification(invitation, team_member)
            
            # Update invitation analytics
            await self._update_invitation_analytics(invitation, 'accepted')
            
            logger.info(f"Invitation accepted: {invitation.invitation_id}")
            
            return invitation
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to accept invitation: {str(e)}")
            raise
    
    async def decline_invitation(
        self, 
        invitation_token: str, 
        decline_reason: str = None,
        response_message: str = None
    ) -> Optional[ProjectInvitation]:
        """        Decline a project invitation.
        
        Args:
            invitation_token: Unique invitation token
            decline_reason: Reason for declining
            response_message: Optional decline message
            
        Returns:
            Updated invitation instance
        """        try:
            # Get invitation by token
            invitation = await self._get_invitation_by_token(invitation_token)
            if not invitation:
                return None
            
            # Update invitation status
            invitation.status = InvitationStatus.DECLINED
            invitation.responded_at = datetime.utcnow()
            invitation.decline_reason = decline_reason
            invitation.response_message = response_message
            
            # Save changes
            await self.db_session.commit()
            
            # Notify invitation sender
            await self._notify_invitation_declined(invitation)
            
            # Update invitation analytics
            await self._update_invitation_analytics(invitation, 'declined')
            
            logger.info(f"Invitation declined: {invitation.invitation_id}")
            
            return invitation
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to decline invitation: {str(e)}")
            raise
    
    async def start_onboarding(self, config: OnboardingConfig) -> Optional[OnboardingWorkflow]:
        """        Start onboarding workflow for new team member.
        
        Args:
            config: Onboarding configuration
            
        Returns:
            Created onboarding workflow instance
        """        try:
            # Generate workflow ID
            workflow_id = self._generate_workflow_id(config.project_id)
            
            # Calculate target completion date
            target_completion = datetime.utcnow() + timedelta(days=config.target_completion_days)
            
            # Create onboarding workflow
            workflow = OnboardingWorkflow(
                workflow_id=workflow_id,
                project_id=uuid.UUID(config.project_id),
                user_id=uuid.UUID(config.user_id),
                invitation_id=uuid.UUID(config.invitation_id) if config.invitation_id else None,
                assigned_buddy=uuid.UUID(config.assigned_buddy) if config.assigned_buddy else None,
                target_completion_date=target_completion,
                completed_stages=[],
                stage_progress=self._initialize_stage_progress(config.custom_stages),
                automated_reminders=config.automated_reminders,
                notification_schedule=self._generate_notification_schedule(config.target_completion_days),
                custom_checklist=self._generate_custom_checklist(config.project_id),
                role_specific_requirements=await self._get_role_requirements(config.project_id, config.user_id)
            )
            
            # Save workflow
            self.db_session.add(workflow)
            await self.db_session.commit()
            await self.db_session.refresh(workflow)
            
            # Send onboarding welcome message
            await self._send_onboarding_welcome(workflow)
            
            # Schedule first onboarding task
            await self._schedule_first_onboarding_task(workflow)
            
            logger.info(f"Onboarding started: {workflow_id}")
            
            return workflow
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to start onboarding: {str(e)}")
            raise
    
    async def update_onboarding_progress(
        self,
        workflow_id: str,
        stage: OnboardingStage,
        progress_data: Dict[str, Any] = None
    ) -> Optional[OnboardingWorkflow]:
        """        Update onboarding workflow progress.
        
        Args:
            workflow_id: Workflow identifier
            stage: Completed stage
            progress_data: Stage-specific progress data
            
        Returns:
            Updated workflow instance
        """        try:
            # Get workflow
            workflow = await self._get_onboarding_workflow(workflow_id)
            if not workflow:
                return None
            
            # Update stage progress
            if stage.value not in workflow.completed_stages:
                workflow.completed_stages.append(stage.value)
            
            # Update current stage
            next_stage = self._get_next_onboarding_stage(stage)
            if next_stage:
                workflow.current_stage = next_stage
            
            # Update stage-specific data
            if progress_data:
                if stage == OnboardingStage.PROFILE_SETUP:
                    workflow.profile_setup_data = progress_data
                elif stage == OnboardingStage.SKILL_ASSESSMENT:
                    workflow.skill_assessment_results = progress_data
                elif stage == OnboardingStage.TOOL_TRAINING:
                    training_completions = workflow.training_completions or {}
                    training_completions.update(progress_data)
                    workflow.training_completions = training_completions
            
            # Calculate overall progress
            total_stages = len(OnboardingStage)
            completed_count = len(workflow.completed_stages)
            workflow.overall_progress = (completed_count / total_stages) * 100
            
            # Check if onboarding is complete
            if workflow.overall_progress >= 100:
                workflow.is_completed = True
                workflow.actual_completion_date = datetime.utcnow()
                workflow.integration_status = 'completed'
            
            # Save changes
            await self.db_session.commit()
            
            # Send progress notification
            await self._send_progress_notification(workflow, stage)
            
            # Generate completion certificate if done
            if workflow.is_completed:
                await self._generate_completion_certificate(workflow)
            
            logger.info(f"Onboarding progress updated: {workflow_id} - {stage.value}")
            
            return workflow
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to update onboarding progress: {str(e)}")
            raise
    
    async def get_invitation_analytics(self, project_id: str) -> Dict[str, Any]:
        """        Get comprehensive invitation analytics for project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Invitation analytics data
        """        try:
            # Get all invitations for project
            invitations = await self.db_session.query(ProjectInvitation)\
                .filter(ProjectInvitation.project_id == uuid.UUID(project_id))\
                .all()
            
            # Calculate metrics
            total_invitations = len(invitations)
            accepted_count = len([inv for inv in invitations if inv.status == InvitationStatus.ACCEPTED])
            declined_count = len([inv for inv in invitations if inv.status == InvitationStatus.DECLINED])
            pending_count = len([inv for inv in invitations if inv.status == InvitationStatus.PENDING])
            expired_count = len([inv for inv in invitations if inv.status == InvitationStatus.EXPIRED])
            
            # Calculate response rates
            acceptance_rate = (accepted_count / total_invitations * 100) if total_invitations > 0 else 0
            decline_rate = (declined_count / total_invitations * 100) if total_invitations > 0 else 0
            response_rate = ((accepted_count + declined_count) / total_invitations * 100) if total_invitations > 0 else 0
            
            # Calculate average response time
            responded_invitations = [inv for inv in invitations if inv.responded_at]
            avg_response_time = None
            if responded_invitations:
                response_times = [
                    (inv.responded_at - inv.sent_at).total_seconds() / 3600 
                    for inv in responded_invitations if inv.sent_at
                ]
                avg_response_time = sum(response_times) / len(response_times) if response_times else None
            
            # Group by invitation type
            type_breakdown = {}
            for inv_type in InvitationType:
                type_invitations = [inv for inv in invitations if inv.invitation_type == inv_type]
                type_breakdown[inv_type.value] = {
                    'total': len(type_invitations),
                    'accepted': len([inv for inv in type_invitations if inv.status == InvitationStatus.ACCEPTED]),
                    'acceptance_rate': len([inv for inv in type_invitations if inv.status == InvitationStatus.ACCEPTED]) / len(type_invitations) * 100 if type_invitations else 0
                }
            
            analytics = {
                'project_id': project_id,
                'generated_at': datetime.utcnow().isoformat(),
                'summary': {
                    'total_invitations': total_invitations,
                    'accepted_count': accepted_count,
                    'declined_count': declined_count,
                    'pending_count': pending_count,
                    'expired_count': expired_count
                },
                'rates': {
                    'acceptance_rate': round(acceptance_rate, 2),
                    'decline_rate': round(decline_rate, 2),
                    'response_rate': round(response_rate, 2)
                },
                'timing': {
                    'average_response_time_hours': round(avg_response_time, 2) if avg_response_time else None
                },
                'type_breakdown': type_breakdown,
                'recent_activity': await self._get_recent_invitation_activity(project_id)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get invitation analytics for {project_id}: {str(e)}")
            return {}
    
    # Private helper methods
    
    def _generate_secure_token(self) -> str:
        """Generate cryptographically secure invitation token"""        return secrets.token_urlsafe(self.token_length)
    
    def _generate_invitation_id(self, project_id: str) -> str:
        """Generate unique invitation identifier"""        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"INV-{timestamp}-{random_suffix}"
    
    def _generate_workflow_id(self, project_id: str) -> str:
        """Generate unique workflow identifier"""        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"ONBOARD-{timestamp}-{random_suffix}"
    
    def _default_permissions(self, role: str) -> Dict[str, Any]:
        """Get default permissions for role"""        permissions = {
            'project_lead': {
                'can_manage_team': True,
                'can_manage_tasks': True,
                'can_approve_content': True,
                'can_manage_budget': True
            },
            'content_creator': {
                'can_manage_team': False,
                'can_manage_tasks': False,
                'can_approve_content': False,
                'can_manage_budget': False
            },
            'reviewer': {
                'can_manage_team': False,
                'can_manage_tasks': False,
                'can_approve_content': True,
                'can_manage_budget': False
            }
        }
        
        return permissions.get(role.lower(), permissions['content_creator'])
    
    def _generate_subject(self, template: Optional[InvitationTemplate], request: InvitationRequest) -> str:
        """Generate invitation subject line"""        if template and template.subject_template:
            return template.subject_template.format(
                project_name="[Project Name]",  # Would be filled from actual project
                role=request.proposed_role,
                invited_name=request.invited_name or request.invited_email
            )
        
        return f"Invitation to collaborate on project as {request.proposed_role}"
    
    def _generate_message(self, template: Optional[InvitationTemplate], request: InvitationRequest) -> str:
        """Generate invitation message"""        if template and template.message_template:
            return template.message_template.format(
                project_name="[Project Name]",
                role=request.proposed_role,
                invited_name=request.invited_name or request.invited_email,
                custom_message=request.message or ""
            )
        
        base_message = f"""        You have been invited to join our project as a {request.proposed_role}.
        
        We believe your skills and expertise would be a valuable addition to our team.
        
        Please click the link below to accept this invitation and get started.
        """        
        if request.message:
            base_message += f"\n\nPersonal message:\n{request.message}"
        
        return base_message.strip()
    
    def _generate_requirements(self, request: InvitationRequest) -> Dict[str, Any]:
        """Generate invitation requirements"""        return {
            'profile_completion_required': True,
            'skill_verification_required': False,
            'background_check_required': False,
            'nda_signature_required': True,
            'portfolio_submission_required': request.invitation_type == InvitationType.PROJECT_COLLABORATION
        }
    
    def _generate_follow_up_schedule(self, expires_in_days: int) -> Dict[str, Any]:
        """Generate follow-up reminder schedule"""        schedule = {
            'enabled': True,
            'reminders': []
        }
        
        # Send reminder at 50% of expiry time
        reminder_1_days = max(1, expires_in_days // 2)
        schedule['reminders'].append({
            'type': 'gentle_reminder',
            'days_before_expiry': reminder_1_days,
            'sent': False
        })
        
        # Send urgent reminder 1 day before expiry
        if expires_in_days > 1:
            schedule['reminders'].append({
                'type': 'urgent_reminder',
                'days_before_expiry': 1,
                'sent': False
            })
        
        return schedule
    
    def _initialize_stage_progress(self, custom_stages: List[str] = None) -> Dict[str, Any]:
        """Initialize onboarding stage progress tracking"""        progress = {}
        
        # Standard stages
        for stage in OnboardingStage:
            progress[stage.value] = {
                'completed': False,
                'started_at': None,
                'completed_at': None,
                'progress_percentage': 0.0,
                'notes': []
            }
        
        # Add custom stages if provided
        if custom_stages:
            for stage in custom_stages:
                progress[f"custom_{stage}"] = {
                    'completed': False,
                    'started_at': None,
                    'completed_at': None,
                    'progress_percentage': 0.0,
                    'notes': []
                }
        
        return progress
    
    def _generate_notification_schedule(self, target_days: int) -> Dict[str, Any]:
        """Generate onboarding notification schedule"""        return {
            'welcome_notification': {'day': 0, 'sent': False},
            'progress_check_1': {'day': target_days // 4, 'sent': False},
            'progress_check_2': {'day': target_days // 2, 'sent': False},
            'final_reminder': {'day': target_days - 1, 'sent': False},
            'completion_celebration': {'day': target_days, 'sent': False}
        }
    
    def _get_next_onboarding_stage(self, current_stage: OnboardingStage) -> Optional[OnboardingStage]:
        """Get next onboarding stage in sequence"""        stages = list(OnboardingStage)
        try:
            current_index = stages.index(current_stage)
            if current_index < len(stages) - 1:
                return stages[current_index + 1]
        except ValueError:
            pass
        
        return None

# Export main classes
__all__ = [
    'ProjectInvitation',
    'OnboardingWorkflow',
    'InvitationTemplate',
    'InvitationStatus',
    'InvitationType',
    'OnboardingStage',
    'InvitationRequest',
    'OnboardingConfig',
    'InvitationSystemManager'
]
