"""
🎯 Creator Onboarding Microservice
Advanced multi-format creator registration and verification workflow service

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import uuid
from abc import ABC, abstractmethod
import hashlib
import logging

logger = logging.getLogger(__name__)


class CreatorType(str, Enum):
    """Types of creators supported by the platform"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    ARTIST = "artist"
    WRITER = "writer"
    DANCER = "dancer"
    EDUCATOR = "educator"


class OnboardingStatus(str, Enum):
    """Creator onboarding status"""
    INITIATED = "initiated"
    PROFILE_CREATED = "profile_created"
    VERIFICATION_PENDING = "verification_pending"
    VERIFICATION_SUBMITTED = "verification_submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    ACTIVE = "active"


class VerificationType(str, Enum):
    """Types of verification required"""
    EMAIL = "email"
    PHONE = "phone"
    IDENTITY = "identity"
    SOCIAL_MEDIA = "social_media"
    PORTFOLIO = "portfolio"
    TAX_INFO = "tax_info"
    BANKING = "banking"


class CreatorProfile(BaseModel):
    """Creator profile data model"""
    creator_id: str = Field(..., description="Unique creator identifier")
    email: EmailStr = Field(..., description="Creator email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    display_name: str = Field(..., min_length=1, max_length=100, description="Public display name")
    creator_types: List[CreatorType] = Field(..., min_length=1, description="Creator categories")
    bio: Optional[str] = Field(None, max_length=1000, description="Creator biography")
    website: Optional[str] = Field(None, description="Creator website URL")
    location: Optional[str] = Field(None, description="Creator location")
    birth_date: Optional[datetime] = Field(None, description="Creator birth date")
    phone: Optional[str] = Field(None, description="Phone number")
    profile_image_url: Optional[str] = Field(None, description="Profile image URL")
    banner_image_url: Optional[str] = Field(None, description="Banner image URL")
    social_links: Dict[str, str] = Field(default_factory=dict, description="Social media links")
    tags: List[str] = Field(default_factory=list, description="Creator tags/interests")
    languages: List[str] = Field(default_factory=list, description="Supported languages")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VerificationDocument(BaseModel):
    """Verification document data model"""
    document_id: str = Field(..., description="Unique document identifier")
    creator_id: str = Field(..., description="Associated creator ID")
    verification_type: VerificationType = Field(..., description="Type of verification")
    document_url: str = Field(..., description="Document storage URL")
    document_hash: str = Field(..., description="Document content hash")
    status: str = Field(default="pending", description="Verification status")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = Field(None, description="Review completion time")
    reviewer_notes: Optional[str] = Field(None, description="Reviewer comments")
    expiry_date: Optional[datetime] = Field(None, description="Document expiry date")


class OnboardingStep(BaseModel):
    """Individual onboarding step"""
    step_id: str = Field(..., description="Unique step identifier")
    step_name: str = Field(..., description="Step name")
    description: str = Field(..., description="Step description")
    required: bool = Field(default=True, description="Whether step is required")
    completed: bool = Field(default=False, description="Whether step is completed")
    completion_data: Dict[str, Any] = Field(default_factory=dict, description="Step completion data")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


class OnboardingWorkflow(BaseModel):
    """Complete onboarding workflow"""
    workflow_id: str = Field(..., description="Unique workflow identifier")
    creator_id: str = Field(..., description="Associated creator ID")
    creator_types: List[CreatorType] = Field(..., description="Creator types")
    status: OnboardingStatus = Field(default=OnboardingStatus.INITIATED)
    current_step: int = Field(default=0, description="Current step index")
    steps: List[OnboardingStep] = Field(..., description="Workflow steps")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Workflow completion time")
    estimated_completion_time: int = Field(..., description="Estimated time in minutes")
    progress_percentage: float = Field(default=0.0, description="Completion percentage")


class OnboardingRequest(BaseModel):
    """Creator onboarding request"""
    email: EmailStr = Field(..., description="Creator email")
    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    creator_types: List[CreatorType] = Field(..., min_length=1)
    referral_code: Optional[str] = Field(None, description="Referral code")
    source: Optional[str] = Field(None, description="Registration source")
    utm_params: Dict[str, str] = Field(default_factory=dict, description="UTM parameters")


class OnboardingResponse(BaseModel):
    """Onboarding response"""
    success: bool = Field(..., description="Operation success status")
    creator_id: Optional[str] = Field(None, description="Created creator ID")
    workflow_id: Optional[str] = Field(None, description="Workflow ID")
    status: OnboardingStatus = Field(..., description="Current status")
    next_steps: List[str] = Field(default_factory=list, description="Next required steps")
    verification_url: Optional[str] = Field(None, description="Verification URL")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    estimated_completion_minutes: Optional[int] = Field(None, description="Estimated completion time")


class CreatorOnboardingOrchestrator:
    """Main orchestrator for creator onboarding workflows"""
    
    def __init__(self):
        self.workflows: Dict[str, OnboardingWorkflow] = {}
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.verification_documents: Dict[str, List[VerificationDocument]] = {}
        
    async def initiate_onboarding(self, request: OnboardingRequest) -> OnboardingResponse:
        """Initiate creator onboarding process"""
        
        try:
            # Validate request
            if await self._is_email_taken(request.email):
                return OnboardingResponse(
                    success=False,
                    status=OnboardingStatus.INITIATED,
                    error_message="Email address already registered"
                )
            
            if await self._is_username_taken(request.username):
                return OnboardingResponse(
                    success=False,
                    status=OnboardingStatus.INITIATED,
                    error_message="Username already taken"
                )
            
            # Generate unique IDs
            creator_id = str(uuid.uuid4())
            workflow_id = str(uuid.uuid4())
            
            # Create initial profile
            profile = CreatorProfile(
                creator_id=creator_id,
                email=request.email,
                username=request.username,
                display_name=request.display_name,
                creator_types=request.creator_types
            )
            
            # Create workflow based on creator types
            workflow = await self._create_workflow(
                workflow_id, creator_id, request.creator_types
            )
            
            # Store data
            self.creator_profiles[creator_id] = profile
            self.workflows[workflow_id] = workflow
            self.verification_documents[creator_id] = []
            
            logger.info(f"Initiated onboarding for creator {creator_id}")
            
            return OnboardingResponse(
                success=True,
                creator_id=creator_id,
                workflow_id=workflow_id,
                status=OnboardingStatus.PROFILE_CREATED,
                next_steps=self._get_next_steps(workflow),
                verification_url=f"/verify/{creator_id}",
                estimated_completion_minutes=workflow.estimated_completion_time
            )
            
        except Exception as e:
            logger.error(f"Onboarding initiation failed: {str(e)}")
            return OnboardingResponse(
                success=False,
                status=OnboardingStatus.INITIATED,
                error_message=f"Onboarding failed: {str(e)}"
            )
    
    async def _create_workflow(
        self, 
        workflow_id: str, 
        creator_id: str, 
        creator_types: List[CreatorType]
    ) -> OnboardingWorkflow:
        """Create customized onboarding workflow based on creator types"""
        
        steps = []
        
        # Basic steps for all creators
        steps.extend([
            OnboardingStep(
                step_id="email_verification",
                step_name="Email Verification",
                description="Verify your email address",
                required=True
            ),
            OnboardingStep(
                step_id="profile_completion",
                step_name="Complete Profile",
                description="Fill out your creator profile",
                required=True
            ),
            OnboardingStep(
                step_id="social_links",
                step_name="Connect Social Media",
                description="Link your social media accounts",
                required=False
            )
        ])
        
        # Type-specific steps
        for creator_type in creator_types:
            if creator_type == CreatorType.MUSICIAN:
                steps.extend([
                    OnboardingStep(
                        step_id="music_portfolio",
                        step_name="Music Portfolio",
                        description="Upload sample music tracks",
                        required=True
                    ),
                    OnboardingStep(
                        step_id="performance_rights",
                        step_name="Performance Rights",
                        description="Verify performance rights ownership",
                        required=True
                    )
                ])
            elif creator_type == CreatorType.PHOTOGRAPHER:
                steps.extend([
                    OnboardingStep(
                        step_id="photo_portfolio",
                        step_name="Photo Portfolio",
                        description="Upload sample photography work",
                        required=True
                    ),
                    OnboardingStep(
                        step_id="copyright_verification",
                        step_name="Copyright Verification",
                        description="Verify image copyright ownership",
                        required=True
                    )
                ])
            elif creator_type == CreatorType.BLOGGER:
                steps.extend([
                    OnboardingStep(
                        step_id="writing_samples",
                        step_name="Writing Samples",
                        description="Provide writing samples",
                        required=True
                    ),
                    OnboardingStep(
                        step_id="niche_selection",
                        step_name="Content Niche",
                        description="Define your content niche",
                        required=True
                    )
                ])
        
        # Final steps for monetization
        steps.extend([
            OnboardingStep(
                step_id="tax_information",
                step_name="Tax Information",
                description="Provide tax information for monetization",
                required=True
            ),
            OnboardingStep(
                step_id="payment_setup",
                step_name="Payment Setup",
                description="Set up payment methods",
                required=True
            ),
            OnboardingStep(
                step_id="final_review",
                step_name="Final Review",
                description="Account review and activation",
                required=True
            )
        ])
        
        # Calculate estimated completion time
        estimated_time = len(steps) * 5  # 5 minutes per step average
        
        return OnboardingWorkflow(
            workflow_id=workflow_id,
            creator_id=creator_id,
            creator_types=creator_types,
            status=OnboardingStatus.PROFILE_CREATED,
            steps=steps,
            estimated_completion_time=estimated_time
        )
    
    async def complete_step(
        self, 
        workflow_id: str, 
        step_id: str, 
        completion_data: Dict[str, Any]
    ) -> OnboardingResponse:
        """Complete a specific onboarding step"""
        
        if workflow_id not in self.workflows:
            return OnboardingResponse(
                success=False,
                status=OnboardingStatus.INITIATED,
                error_message="Workflow not found"
            )
        
        workflow = self.workflows[workflow_id]
        
        # Find and complete the step
        step_completed = False
        for step in workflow.steps:
            if step.step_id == step_id:
                step.completed = True
                step.completion_data = completion_data
                step.completed_at = datetime.utcnow()
                step_completed = True
                break
        
        if not step_completed:
            return OnboardingResponse(
                success=False,
                status=workflow.status,
                error_message="Step not found"
            )
        
        # Update workflow progress
        completed_steps = sum(1 for step in workflow.steps if step.completed)
        total_steps = len(workflow.steps)
        workflow.progress_percentage = (completed_steps / total_steps) * 100
        
        # Update workflow status
        if workflow.progress_percentage == 100:
            workflow.status = OnboardingStatus.UNDER_REVIEW
            workflow.completed_at = datetime.utcnow()
        elif step_id == "email_verification":
            workflow.status = OnboardingStatus.VERIFICATION_PENDING
        
        # Update current step index
        for i, step in enumerate(workflow.steps):
            if not step.completed:
                workflow.current_step = i
                break
        else:
            workflow.current_step = total_steps
        
        return OnboardingResponse(
            success=True,
            creator_id=workflow.creator_id,
            workflow_id=workflow_id,
            status=workflow.status,
            next_steps=self._get_next_steps(workflow)
        )
    
    async def submit_verification_document(
        self, 
        creator_id: str, 
        verification_type: VerificationType,
        document_url: str,
        document_content: bytes
    ) -> bool:
        """Submit verification document"""
        
        if creator_id not in self.verification_documents:
            return False
        
        # Generate document hash
        document_hash = hashlib.sha256(document_content).hexdigest()
        
        # Create verification document
        document = VerificationDocument(
            document_id=str(uuid.uuid4()),
            creator_id=creator_id,
            verification_type=verification_type,
            document_url=document_url,
            document_hash=document_hash
        )
        
        self.verification_documents[creator_id].append(document)
        
        logger.info(f"Verification document submitted for creator {creator_id}")
        return True
    
    async def approve_creator(self, creator_id: str, reviewer_notes: str = "") -> bool:
        """Approve creator after review"""
        
        if creator_id not in self.creator_profiles:
            return False
        
        # Find workflow
        workflow = None
        for wf in self.workflows.values():
            if wf.creator_id == creator_id:
                workflow = wf
                break
        
        if not workflow:
            return False
        
        # Update status
        workflow.status = OnboardingStatus.APPROVED
        
        # Mark final review step as completed
        for step in workflow.steps:
            if step.step_id == "final_review":
                step.completed = True
                step.completion_data = {"reviewer_notes": reviewer_notes}
                step.completed_at = datetime.utcnow()
                break
        
        logger.info(f"Creator {creator_id} approved")
        return True
    
    async def reject_creator(self, creator_id: str, reason: str) -> bool:
        """Reject creator application"""
        
        if creator_id not in self.creator_profiles:
            return False
        
        # Find workflow
        workflow = None
        for wf in self.workflows.values():
            if wf.creator_id == creator_id:
                workflow = wf
                break
        
        if not workflow:
            return False
        
        # Update status
        workflow.status = OnboardingStatus.REJECTED
        
        logger.info(f"Creator {creator_id} rejected: {reason}")
        return True
    
    async def get_onboarding_status(self, workflow_id: str) -> Optional[OnboardingWorkflow]:
        """Get current onboarding status"""
        return self.workflows.get(workflow_id)
    
    async def get_creator_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """Get creator profile"""
        return self.creator_profiles.get(creator_id)
    
    def _get_next_steps(self, workflow: OnboardingWorkflow) -> List[str]:
        """Get list of next required steps"""
        next_steps = []
        for step in workflow.steps:
            if not step.completed and step.required:
                next_steps.append(f"{step.step_name}: {step.description}")
                if len(next_steps) >= 3:  # Limit to next 3 steps
                    break
        return next_steps
    
    async def _is_email_taken(self, email: str) -> bool:
        """Check if email is already registered"""
        for profile in self.creator_profiles.values():
            if profile.email.lower() == email.lower():
                return True
        return False
    
    async def _is_username_taken(self, username: str) -> bool:
        """Check if username is already taken"""
        for profile in self.creator_profiles.values():
            if profile.username.lower() == username.lower():
                return True
        return False
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health metrics"""
        total_workflows = len(self.workflows)
        completed_workflows = sum(
            1 for wf in self.workflows.values() 
            if wf.status in [OnboardingStatus.APPROVED, OnboardingStatus.ACTIVE]
        )
        
        return {
            "service_status": "healthy",
            "total_workflows": total_workflows,
            "completed_workflows": completed_workflows,
            "success_rate": completed_workflows / total_workflows if total_workflows > 0 else 0,
            "supported_creator_types": [ct.value for ct in CreatorType],
            "verification_types": [vt.value for vt in VerificationType],
            "active_profiles": len(self.creator_profiles)
        }


# Export classes for external use
__all__ = [
    'CreatorType',
    'OnboardingStatus', 
    'VerificationType',
    'CreatorProfile',
    'VerificationDocument',
    'OnboardingStep',
    'OnboardingWorkflow',
    'OnboardingRequest',
    'OnboardingResponse',
    'CreatorOnboardingOrchestrator'
]