"""Creator Workflow Documentation Tracker
Advanced workflow tracking and documentation system for Creator Economy.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    """Types of creator workflows"""
    ONBOARDING = "onboarding"
    CONTENT_CREATION = "content_creation"
    MONETIZATION_SETUP = "monetization_setup"
    COLLABORATION = "collaboration"
    ANALYTICS_REVIEW = "analytics_review"
    PROTECTION_SETUP = "protection_setup"
    SEO_OPTIMIZATION = "seo_optimization"
    DISTRIBUTION_SETUP = "distribution_setup"
    PROFILE_OPTIMIZATION = "profile_optimization"
    COMMUNITY_ENGAGEMENT = "community_engagement"

class WorkflowStatus(Enum):
    """Workflow execution status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"
    SKIPPED = "skipped"
    REQUIRES_ATTENTION = "requires_attention"

class StepType(Enum):
    """Types of workflow steps"""
    INFORMATION = "information"
    ACTION = "action"
    VERIFICATION = "verification"
    DECISION = "decision"
    INTEGRATION = "integration"
    REVIEW = "review"

@dataclass
class WorkflowStep:
    """Individual workflow step"""
    step_id: str
    title: str
    description: str
    step_type: StepType
    order: int
    required: bool
    estimated_duration: int  # in minutes
    prerequisites: List[str]
    documentation_url: Optional[str] = None
    video_tutorial_url: Optional[str] = None
    help_text: Optional[str] = None
    validation_criteria: Optional[Dict[str, Any]] = None
    creator_specific: bool = False
    applicable_creator_types: Optional[List[str]] = None

@dataclass
class WorkflowStepProgress:
    """Progress tracking for workflow step"""
    step_id: str
    status: WorkflowStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    success_rate: Optional[float] = None
    notes: Optional[str] = None
    errors: Optional[List[str]] = None
    help_requests: int = 0
    retry_count: int = 0

@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    workflow_type: WorkflowType
    creator_types: List[str]
    steps: List[WorkflowStep]
    estimated_total_duration: int  # in minutes
    success_criteria: Dict[str, Any]
    documentation_version: str
    created_at: datetime
    updated_at: datetime

@dataclass
class WorkflowExecution:
    """Active workflow execution instance"""
    execution_id: str
    workflow_id: str
    creator_id: str
    creator_type: str
    status: WorkflowStatus
    current_step: Optional[str]
    step_progress: Dict[str, WorkflowStepProgress]
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_duration: Optional[int] = None
    success_rate: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class WorkflowAnalytics:
    """Workflow performance analytics"""
    workflow_id: str
    total_executions: int
    completed_executions: int
    success_rate: float
    average_duration: float
    step_completion_rates: Dict[str, float]
    common_failure_points: List[Dict[str, Any]]
    creator_type_performance: Dict[str, Dict[str, float]]
    improvement_suggestions: List[str]

class CreatorWorkflowDocumentationTracker:
    """
    Advanced workflow tracking and documentation system
    
    Tracks creator workflows, generates step-by-step documentation,
    and provides analytics for workflow optimization.
    """
    
    def __init__(self, project_root: str = "/home/runner/work/IA Chéries/IA Chéries"):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(f"{__name__}.CreatorWorkflowDocumentationTracker")
        
        # Workflow definitions storage
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        
        # Active workflow executions
        self.active_executions: Dict[str, WorkflowExecution] = {}
        
        # Completed executions for analytics
        self.completed_executions: List[WorkflowExecution] = []
        
        # Workflow analytics cache
        self.analytics_cache: Dict[str, WorkflowAnalytics] = {}
        
        # Statistics tracking
        self.stats = {
            'total_workflows_created': 0,
            'total_executions_started': 0,
            'total_executions_completed': 0,
            'average_completion_rate': 0.0,
            'most_popular_workflows': {},
            'creator_type_performance': {}
        }
        
        # Initialize default workflows
        asyncio.create_task(self._initialize_default_workflows())
        
        self.logger.info("Creator Workflow Documentation Tracker initialized")
    
    async def _initialize_default_workflows(self):
        """Initialize default workflow definitions"""
        try:
            # Creator onboarding workflow
            onboarding_workflow = await self._create_onboarding_workflow()
            self.workflow_definitions[onboarding_workflow.workflow_id] = onboarding_workflow
            
            # Content creation workflow
            content_workflow = await self._create_content_creation_workflow()
            self.workflow_definitions[content_workflow.workflow_id] = content_workflow
            
            # Monetization setup workflow
            monetization_workflow = await self._create_monetization_workflow()
            self.workflow_definitions[monetization_workflow.workflow_id] = monetization_workflow
            
            # Collaboration workflow
            collaboration_workflow = await self._create_collaboration_workflow()
            self.workflow_definitions[collaboration_workflow.workflow_id] = collaboration_workflow
            
            self.logger.info(f"Initialized {len(self.workflow_definitions)} default workflows")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize default workflows: {e}")
    
    async def _create_onboarding_workflow(self) -> WorkflowDefinition:
        """Create comprehensive creator onboarding workflow"""
        steps = [
            WorkflowStep(
                step_id="welcome_intro",
                title="Welcome to IA Chéries",
                description="Introduction to the Creator Economy platform and your journey ahead",
                step_type=StepType.INFORMATION,
                order=1,
                required=True,
                estimated_duration=5,
                prerequisites=[],
                help_text="This step introduces you to the platform and sets expectations for your creator journey."
            ),
            WorkflowStep(
                step_id="profile_setup",
                title="Complete Your Creator Profile",
                description="Set up your creator profile with essential information",
                step_type=StepType.ACTION,
                order=2,
                required=True,
                estimated_duration=15,
                prerequisites=["welcome_intro"],
                validation_criteria={"profile_completeness": 80},
                help_text="A complete profile helps other creators find you and builds trust with your audience."
            ),
            WorkflowStep(
                step_id="creator_type_selection",
                title="Define Your Creator Type",
                description="Select your primary creator type and specializations",
                step_type=StepType.DECISION,
                order=3,
                required=True,
                estimated_duration=10,
                prerequisites=["profile_setup"],
                creator_specific=True,
                help_text="Choose the creator type that best represents your content and goals."
            ),
            WorkflowStep(
                step_id="platform_tour",
                title="Platform Features Tour",
                description="Interactive tour of key platform features and tools",
                step_type=StepType.INFORMATION,
                order=4,
                required=False,
                estimated_duration=20,
                prerequisites=["creator_type_selection"],
                video_tutorial_url="/tutorials/platform-tour",
                help_text="Learn about the tools and features available to help you succeed."
            ),
            WorkflowStep(
                step_id="first_content_upload",
                title="Upload Your First Content",
                description="Upload and publish your first piece of content",
                step_type=StepType.ACTION,
                order=5,
                required=True,
                estimated_duration=25,
                prerequisites=["creator_type_selection"],
                validation_criteria={"content_uploaded": True, "content_published": True},
                help_text="Start building your presence by sharing your first piece of content."
            ),
            WorkflowStep(
                step_id="monetization_intro",
                title="Monetization Options Overview",
                description="Learn about available monetization strategies for your creator type",
                step_type=StepType.INFORMATION,
                order=6,
                required=False,
                estimated_duration=15,
                prerequisites=["first_content_upload"],
                creator_specific=True,
                help_text="Understand how you can start earning from your content."
            ),
            WorkflowStep(
                step_id="community_engagement",
                title="Join Creator Community",
                description="Connect with other creators and join relevant communities",
                step_type=StepType.ACTION,
                order=7,
                required=False,
                estimated_duration=10,
                prerequisites=["first_content_upload"],
                help_text="Build relationships with other creators in your niche."
            ),
            WorkflowStep(
                step_id="onboarding_completion",
                title="Onboarding Complete",
                description="Review your onboarding progress and next steps",
                step_type=StepType.REVIEW,
                order=8,
                required=True,
                estimated_duration=5,
                prerequisites=["first_content_upload"],
                help_text="Congratulations on completing your onboarding! Here's what to do next."
            )
        ]
        
        return WorkflowDefinition(
            workflow_id="creator_onboarding_v1",
            name="Creator Onboarding",
            description="Complete onboarding process for new creators on IA Chéries platform",
            workflow_type=WorkflowType.ONBOARDING,
            creator_types=["all"],
            steps=steps,
            estimated_total_duration=105,  # Total minutes
            success_criteria={
                "profile_completed": True,
                "content_uploaded": True,
                "minimum_completion_rate": 80.0
            },
            documentation_version="1.0",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    async def _create_content_creation_workflow(self) -> WorkflowDefinition:
        """Create content creation workflow"""
        steps = [
            WorkflowStep(
                step_id="content_planning",
                title="Content Planning & Strategy",
                description="Plan your content strategy and individual piece",
                step_type=StepType.ACTION,
                order=1,
                required=True,
                estimated_duration=20,
                prerequisites=[],
                help_text="Good planning leads to better content and audience engagement."
            ),
            WorkflowStep(
                step_id="content_creation",
                title="Create Your Content",
                description="Use platform tools to create or upload your content",
                step_type=StepType.ACTION,
                order=2,
                required=True,
                estimated_duration=60,
                prerequisites=["content_planning"],
                creator_specific=True,
                applicable_creator_types=["musician", "blogger", "photographer", "influencer", "comedian"],
                help_text="Take advantage of our AI-powered creation tools for enhanced content."
            ),
            WorkflowStep(
                step_id="ai_enhancement",
                title="AI Content Enhancement",
                description="Apply AI processing and enhancement to your content",
                step_type=StepType.ACTION,
                order=3,
                required=False,
                estimated_duration=10,
                prerequisites=["content_creation"],
                help_text="Our AI can improve quality, optimize for engagement, and suggest improvements."
            ),
            WorkflowStep(
                step_id="metadata_optimization",
                title="Optimize Metadata & SEO",
                description="Add titles, descriptions, tags, and SEO optimization",
                step_type=StepType.ACTION,
                order=4,
                required=True,
                estimated_duration=15,
                prerequisites=["content_creation"],
                validation_criteria={"title_added": True, "description_added": True, "tags_count": 3},
                help_text="Good metadata helps your content get discovered by the right audience."
            ),
            WorkflowStep(
                step_id="content_review",
                title="Review & Quality Check",
                description="Review your content for quality and compliance",
                step_type=StepType.VERIFICATION,
                order=5,
                required=True,
                estimated_duration=10,
                prerequisites=["metadata_optimization"],
                help_text="Ensure your content meets quality standards and platform guidelines."
            ),
            WorkflowStep(
                step_id="publishing_settings",
                title="Configure Publishing Settings",
                description="Set publishing schedule, visibility, and monetization options",
                step_type=StepType.ACTION,
                order=6,
                required=True,
                estimated_duration=10,
                prerequisites=["content_review"],
                help_text="Choose when and how your content will be published and monetized."
            ),
            WorkflowStep(
                step_id="content_publish",
                title="Publish Content",
                description="Publish your content to selected platforms",
                step_type=StepType.ACTION,
                order=7,
                required=True,
                estimated_duration=5,
                prerequisites=["publishing_settings"],
                validation_criteria={"content_published": True},
                help_text="Your content is now live and available to your audience!"
            )
        ]
        
        return WorkflowDefinition(
            workflow_id="content_creation_v1",
            name="Content Creation & Publishing",
            description="Complete workflow for creating and publishing content",
            workflow_type=WorkflowType.CONTENT_CREATION,
            creator_types=["all"],
            steps=steps,
            estimated_total_duration=130,
            success_criteria={
                "content_published": True,
                "metadata_complete": True,
                "quality_score": 75.0
            },
            documentation_version="1.0",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    async def _create_monetization_workflow(self) -> WorkflowDefinition:
        """Create monetization setup workflow"""
        steps = [
            WorkflowStep(
                step_id="monetization_assessment",
                title="Assess Monetization Readiness",
                description="Evaluate your content and audience for monetization opportunities",
                step_type=StepType.VERIFICATION,
                order=1,
                required=True,
                estimated_duration=15,
                prerequisites=[],
                help_text="Understand your monetization potential and readiness."
            ),
            WorkflowStep(
                step_id="payment_setup",
                title="Set Up Payment Methods",
                description="Configure payment methods and tax information",
                step_type=StepType.ACTION,
                order=2,
                required=True,
                estimated_duration=20,
                prerequisites=["monetization_assessment"],
                validation_criteria={"payment_method_added": True},
                help_text="Secure payment setup ensures you get paid for your content."
            ),
            WorkflowStep(
                step_id="pricing_strategy",
                title="Develop Pricing Strategy",
                description="Set prices for your content and services",
                step_type=StepType.DECISION,
                order=3,
                required=True,
                estimated_duration=25,
                prerequisites=["payment_setup"],
                creator_specific=True,
                help_text="Strategic pricing helps maximize revenue while maintaining audience engagement."
            ),
            WorkflowStep(
                step_id="monetization_features",
                title="Enable Monetization Features",
                description="Activate relevant monetization features for your content type",
                step_type=StepType.ACTION,
                order=4,
                required=True,
                estimated_duration=15,
                prerequisites=["pricing_strategy"],
                help_text="Enable the monetization methods that work best for your creator type."
            ),
            WorkflowStep(
                step_id="revenue_tracking",
                title="Set Up Revenue Tracking",
                description="Configure analytics and revenue tracking dashboard",
                step_type=StepType.ACTION,
                order=5,
                required=False,
                estimated_duration=10,
                prerequisites=["monetization_features"],
                help_text="Track your earnings and understand what content performs best financially."
            )
        ]
        
        return WorkflowDefinition(
            workflow_id="monetization_setup_v1",
            name="Monetization Setup",
            description="Complete setup for content monetization and revenue generation",
            workflow_type=WorkflowType.MONETIZATION_SETUP,
            creator_types=["all"],
            steps=steps,
            estimated_total_duration=85,
            success_criteria={
                "payment_configured": True,
                "monetization_enabled": True,
                "pricing_set": True
            },
            documentation_version="1.0",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    async def _create_collaboration_workflow(self) -> WorkflowDefinition:
        """Create creator collaboration workflow"""
        steps = [
            WorkflowStep(
                step_id="collaboration_goals",
                title="Define Collaboration Goals",
                description="Identify what you want to achieve through collaborations",
                step_type=StepType.DECISION,
                order=1,
                required=True,
                estimated_duration=15,
                prerequisites=[],
                help_text="Clear goals help you find the right collaboration partners."
            ),
            WorkflowStep(
                step_id="partner_discovery",
                title="Find Collaboration Partners",
                description="Search for and connect with potential collaboration partners",
                step_type=StepType.ACTION,
                order=2,
                required=True,
                estimated_duration=30,
                prerequisites=["collaboration_goals"],
                help_text="Use our matching system to find creators who complement your skills."
            ),
            WorkflowStep(
                step_id="collaboration_proposal",
                title="Create Collaboration Proposal",
                description="Draft and send collaboration proposals to potential partners",
                step_type=StepType.ACTION,
                order=3,
                required=True,
                estimated_duration=20,
                prerequisites=["partner_discovery"],
                help_text="A well-crafted proposal increases your chances of successful collaboration."
            ),
            WorkflowStep(
                step_id="collaboration_agreement",
                title="Finalize Collaboration Agreement",
                description="Agree on terms, responsibilities, and revenue sharing",
                step_type=StepType.ACTION,
                order=4,
                required=True,
                estimated_duration=25,
                prerequisites=["collaboration_proposal"],
                validation_criteria={"agreement_signed": True},
                help_text="Clear agreements prevent misunderstandings and ensure fair collaboration."
            ),
            WorkflowStep(
                step_id="collaborative_content",
                title="Create Collaborative Content",
                description="Work together to create and produce collaborative content",
                step_type=StepType.ACTION,
                order=5,
                required=True,
                estimated_duration=120,
                prerequisites=["collaboration_agreement"],
                help_text="Use our collaboration tools to work together effectively."
            ),
            WorkflowStep(
                step_id="collaboration_review",
                title="Review Collaboration Results",
                description="Analyze the success of your collaboration and plan future ones",
                step_type=StepType.REVIEW,
                order=6,
                required=False,
                estimated_duration=15,
                prerequisites=["collaborative_content"],
                help_text="Learning from each collaboration helps improve future partnerships."
            )
        ]
        
        return WorkflowDefinition(
            workflow_id="collaboration_v1",
            name="Creator Collaboration",
            description="Complete workflow for setting up and managing creator collaborations",
            workflow_type=WorkflowType.COLLABORATION,
            creator_types=["all"],
            steps=steps,
            estimated_total_duration=225,
            success_criteria={
                "collaboration_established": True,
                "content_created": True,
                "partners_satisfied": True
            },
            documentation_version="1.0",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    async def initialize_creator_workflow(
        self,
        creator_id: str,
        creator_type: str,
        workflow_type: str = "onboarding"
    ) -> Dict[str, Any]:
        """
        Initialize a new workflow execution for a creator
        
        Args:
            creator_id: Unique creator identifier
            creator_type: Type of creator
            workflow_type: Type of workflow to initialize
        
        Returns:
            Workflow execution details
        """
        try:
            # Find appropriate workflow definition
            workflow_def = None
            for wf_id, wf in self.workflow_definitions.items():
                if (wf.workflow_type.value == workflow_type and 
                    (creator_type in wf.creator_types or "all" in wf.creator_types)):
                    workflow_def = wf
                    break
            
            if not workflow_def:
                raise ValueError(f"No workflow found for type '{workflow_type}' and creator type '{creator_type}'")
            
            # Create new execution instance
            execution_id = str(uuid.uuid4())
            
            # Initialize step progress
            step_progress = {}
            for step in workflow_def.steps:
                step_progress[step.step_id] = WorkflowStepProgress(
                    step_id=step.step_id,
                    status=WorkflowStatus.NOT_STARTED
                )
            
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_def.workflow_id,
                creator_id=creator_id,
                creator_type=creator_type,
                status=WorkflowStatus.IN_PROGRESS,
                current_step=workflow_def.steps[0].step_id if workflow_def.steps else None,
                step_progress=step_progress,
                started_at=datetime.now(),
                metadata={
                    'workflow_name': workflow_def.name,
                    'estimated_duration': workflow_def.estimated_total_duration
                }
            )
            
            # Store active execution
            self.active_executions[execution_id] = execution
            
            # Update statistics
            self.stats['total_executions_started'] += 1
            
            self.logger.info(f"Initialized workflow '{workflow_type}' for creator {creator_id}")
            
            return {
                'execution_id': execution_id,
                'workflow_id': workflow_def.workflow_id,
                'workflow_name': workflow_def.name,
                'workflow_type': workflow_type,
                'creator_id': creator_id,
                'creator_type': creator_type,
                'status': execution.status.value,
                'current_step': execution.current_step,
                'total_steps': len(workflow_def.steps),
                'estimated_duration': workflow_def.estimated_total_duration,
                'started_at': execution.started_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize workflow: {e}")
            raise
    
    async def track_creator_workflow(
        self,
        creator_id: str,
        workflow_type: str,
        execution_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track progress of a creator's workflow
        
        Args:
            creator_id: Creator identifier
            workflow_type: Type of workflow
            execution_id: Specific execution ID (optional)
        
        Returns:
            Workflow progress information
        """
        try:
            # Find relevant execution
            execution = None
            if execution_id:
                execution = self.active_executions.get(execution_id)
            else:
                # Find most recent execution for this creator and workflow type
                for exec_id, exec_instance in self.active_executions.items():
                    if (exec_instance.creator_id == creator_id and 
                        exec_instance.workflow_id.startswith(workflow_type)):
                        execution = exec_instance
                        break
            
            if not execution:
                # Try to find in completed executions
                for completed_exec in self.completed_executions:
                    if (completed_exec.creator_id == creator_id and
                        completed_exec.workflow_id.startswith(workflow_type)):
                        execution = completed_exec
                        break
            
            if not execution:
                return {
                    'creator_id': creator_id,
                    'workflow_type': workflow_type,
                    'status': 'not_found',
                    'message': 'No workflow execution found for this creator'
                }
            
            # Get workflow definition
            workflow_def = self.workflow_definitions.get(execution.workflow_id)
            if not workflow_def:
                raise ValueError(f"Workflow definition not found: {execution.workflow_id}")
            
            # Calculate progress
            total_steps = len(workflow_def.steps)
            completed_steps = len([
                step for step in execution.step_progress.values()
                if step.status == WorkflowStatus.COMPLETED
            ])
            progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
            
            # Get current step information
            current_step_info = None
            if execution.current_step:
                for step in workflow_def.steps:
                    if step.step_id == execution.current_step:
                        current_step_info = {
                            'step_id': step.step_id,
                            'title': step.title,
                            'description': step.description,
                            'type': step.step_type.value,
                            'estimated_duration': step.estimated_duration,
                            'help_text': step.help_text,
                            'video_tutorial_url': step.video_tutorial_url,
                            'documentation_url': step.documentation_url
                        }
                        break
            
            # Get step progress details
            step_details = []
            for step in workflow_def.steps:
                progress = execution.step_progress.get(step.step_id)
                step_detail = {
                    'step_id': step.step_id,
                    'title': step.title,
                    'description': step.description,
                    'order': step.order,
                    'required': step.required,
                    'status': progress.status.value if progress else 'not_started',
                    'started_at': progress.started_at.isoformat() if progress and progress.started_at else None,
                    'completed_at': progress.completed_at.isoformat() if progress and progress.completed_at else None,
                    'duration_minutes': progress.duration_minutes if progress else None,
                    'help_requests': progress.help_requests if progress else 0,
                    'retry_count': progress.retry_count if progress else 0
                }
                step_details.append(step_detail)
            
            return {
                'execution_id': execution.execution_id,
                'workflow_id': execution.workflow_id,
                'workflow_name': workflow_def.name,
                'creator_id': creator_id,
                'creator_type': execution.creator_type,
                'status': execution.status.value,
                'progress_percentage': progress_percentage,
                'completed_steps': completed_steps,
                'total_steps': total_steps,
                'current_step': current_step_info,
                'step_details': step_details,
                'started_at': execution.started_at.isoformat(),
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'total_duration': execution.total_duration,
                'success_rate': execution.success_rate
            }
            
        except Exception as e:
            self.logger.error(f"Failed to track workflow: {e}")
            raise
    
    async def update_step_progress(
        self,
        execution_id: str,
        step_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update progress for a specific workflow step
        
        Args:
            execution_id: Workflow execution ID
            step_id: Step identifier
            status: New status for the step
            notes: Optional notes about the step
        
        Returns:
            Updated step progress
        """
        try:
            execution = self.active_executions.get(execution_id)
            if not execution:
                raise ValueError(f"Workflow execution not found: {execution_id}")
            
            step_progress = execution.step_progress.get(step_id)
            if not step_progress:
                raise ValueError(f"Step not found: {step_id}")
            
            # Update step progress
            old_status = step_progress.status
            step_progress.status = WorkflowStatus(status)
            step_progress.notes = notes
            
            # Handle status transitions
            if old_status == WorkflowStatus.NOT_STARTED and step_progress.status == WorkflowStatus.IN_PROGRESS:
                step_progress.started_at = datetime.now()
            
            elif step_progress.status == WorkflowStatus.COMPLETED:
                if not step_progress.completed_at:
                    step_progress.completed_at = datetime.now()
                
                if step_progress.started_at:
                    duration = step_progress.completed_at - step_progress.started_at
                    step_progress.duration_minutes = int(duration.total_seconds() / 60)
                
                # Move to next step
                await self._advance_to_next_step(execution, step_id)
            
            elif step_progress.status == WorkflowStatus.FAILED:
                step_progress.retry_count += 1
            
            # Update execution status if necessary
            await self._update_execution_status(execution)
            
            self.logger.info(f"Updated step {step_id} to status {status} for execution {execution_id}")
            
            return {
                'execution_id': execution_id,
                'step_id': step_id,
                'status': step_progress.status.value,
                'started_at': step_progress.started_at.isoformat() if step_progress.started_at else None,
                'completed_at': step_progress.completed_at.isoformat() if step_progress.completed_at else None,
                'duration_minutes': step_progress.duration_minutes,
                'notes': step_progress.notes,
                'retry_count': step_progress.retry_count
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update step progress: {e}")
            raise
    
    async def _advance_to_next_step(self, execution: WorkflowExecution, completed_step_id: str):
        """Advance workflow to the next step"""
        try:
            workflow_def = self.workflow_definitions.get(execution.workflow_id)
            if not workflow_def:
                return
            
            # Find current step index
            current_step_index = None
            for i, step in enumerate(workflow_def.steps):
                if step.step_id == completed_step_id:
                    current_step_index = i
                    break
            
            if current_step_index is None:
                return
            
            # Find next step that hasn't been completed
            next_step_id = None
            for i in range(current_step_index + 1, len(workflow_def.steps)):
                step = workflow_def.steps[i]
                step_progress = execution.step_progress.get(step.step_id)
                
                if step_progress and step_progress.status != WorkflowStatus.COMPLETED:
                    # Check prerequisites
                    prerequisites_met = True
                    for prereq in step.prerequisites:
                        prereq_progress = execution.step_progress.get(prereq)
                        if not prereq_progress or prereq_progress.status != WorkflowStatus.COMPLETED:
                            prerequisites_met = False
                            break
                    
                    if prerequisites_met:
                        next_step_id = step.step_id
                        break
            
            execution.current_step = next_step_id
            
        except Exception as e:
            self.logger.error(f"Failed to advance to next step: {e}")
    
    async def _update_execution_status(self, execution: WorkflowExecution):
        """Update overall execution status based on step progress"""
        try:
            workflow_def = self.workflow_definitions.get(execution.workflow_id)
            if not workflow_def:
                return
            
            total_steps = len(workflow_def.steps)
            completed_steps = len([
                step for step in execution.step_progress.values()
                if step.status == WorkflowStatus.COMPLETED
            ])
            failed_steps = len([
                step for step in execution.step_progress.values()
                if step.status == WorkflowStatus.FAILED
            ])
            
            # Calculate success rate
            execution.success_rate = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
            
            # Update status
            if completed_steps == total_steps:
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.now()
                execution.total_duration = int((execution.completed_at - execution.started_at).total_seconds() / 60)
                
                # Move to completed executions
                self.completed_executions.append(execution)
                if execution.execution_id in self.active_executions:
                    del self.active_executions[execution.execution_id]
                
                # Update statistics
                self.stats['total_executions_completed'] += 1
                self._update_completion_statistics()
                
            elif failed_steps > 0 and execution.current_step is None:
                execution.status = WorkflowStatus.FAILED
            
        except Exception as e:
            self.logger.error(f"Failed to update execution status: {e}")
    
    def _update_completion_statistics(self):
        """Update completion rate statistics"""
        if self.stats['total_executions_started'] > 0:
            self.stats['average_completion_rate'] = (
                self.stats['total_executions_completed'] / 
                self.stats['total_executions_started'] * 100
            )
    
    async def get_workflow_analytics(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive workflow analytics
        
        Args:
            workflow_id: Specific workflow ID (optional)
        
        Returns:
            Workflow analytics data
        """
        try:
            if workflow_id:
                return await self._get_single_workflow_analytics(workflow_id)
            else:
                return await self._get_all_workflows_analytics()
        
        except Exception as e:
            self.logger.error(f"Failed to get workflow analytics: {e}")
            raise
    
    async def _get_single_workflow_analytics(self, workflow_id: str) -> Dict[str, Any]:
        """Get analytics for a specific workflow"""
        workflow_def = self.workflow_definitions.get(workflow_id)
        if not workflow_def:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        # Collect executions for this workflow
        all_executions = []
        
        # Active executions
        for execution in self.active_executions.values():
            if execution.workflow_id == workflow_id:
                all_executions.append(execution)
        
        # Completed executions
        for execution in self.completed_executions:
            if execution.workflow_id == workflow_id:
                all_executions.append(execution)
        
        total_executions = len(all_executions)
        completed_executions = len([e for e in all_executions if e.status == WorkflowStatus.COMPLETED])
        success_rate = (completed_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Calculate average duration for completed executions
        completed_with_duration = [e for e in all_executions if e.total_duration is not None]
        average_duration = (
            sum(e.total_duration for e in completed_with_duration) / len(completed_with_duration)
            if completed_with_duration else 0
        )
        
        # Step completion rates
        step_completion_rates = {}
        for step in workflow_def.steps:
            completed_count = len([
                e for e in all_executions
                if e.step_progress.get(step.step_id) and 
                e.step_progress[step.step_id].status == WorkflowStatus.COMPLETED
            ])
            step_completion_rates[step.step_id] = (
                completed_count / total_executions * 100 if total_executions > 0 else 0
            )
        
        # Creator type performance
        creator_type_performance = {}
        for execution in all_executions:
            creator_type = execution.creator_type
            if creator_type not in creator_type_performance:
                creator_type_performance[creator_type] = {
                    'total': 0,
                    'completed': 0,
                    'success_rate': 0,
                    'average_duration': 0
                }
            
            creator_type_performance[creator_type]['total'] += 1
            if execution.status == WorkflowStatus.COMPLETED:
                creator_type_performance[creator_type]['completed'] += 1
                if execution.total_duration:
                    creator_type_performance[creator_type]['average_duration'] += execution.total_duration
        
        # Calculate final metrics for creator types
        for creator_type, metrics in creator_type_performance.items():
            if metrics['total'] > 0:
                metrics['success_rate'] = metrics['completed'] / metrics['total'] * 100
                if metrics['completed'] > 0:
                    metrics['average_duration'] /= metrics['completed']
        
        return {
            'workflow_id': workflow_id,
            'workflow_name': workflow_def.name,
            'total_executions': total_executions,
            'completed_executions': completed_executions,
            'success_rate': success_rate,
            'average_duration': average_duration,
            'step_completion_rates': step_completion_rates,
            'creator_type_performance': creator_type_performance,
            'total_steps': len(workflow_def.steps)
        }
    
    async def _get_all_workflows_analytics(self) -> Dict[str, Any]:
        """Get analytics for all workflows"""
        analytics = {
            'total_workflows': len(self.workflow_definitions),
            'workflows': {},
            'overall_stats': self.stats,
            'summary': {
                'total_executions': self.stats['total_executions_started'],
                'completed_executions': self.stats['total_executions_completed'],
                'overall_completion_rate': self.stats['average_completion_rate']
            }
        }
        
        # Get analytics for each workflow
        for workflow_id in self.workflow_definitions.keys():
            try:
                workflow_analytics = await self._get_single_workflow_analytics(workflow_id)
                analytics['workflows'][workflow_id] = workflow_analytics
            except Exception as e:
                self.logger.warning(f"Failed to get analytics for workflow {workflow_id}: {e}")
        
        return analytics
    
    async def generate_workflow_documentation(
        self,
        workflow_id: str,
        language: str = 'en',
        format_type: str = 'markdown'
    ) -> str:
        """
        Generate comprehensive documentation for a workflow
        
        Args:
            workflow_id: Workflow identifier
            language: Documentation language
            format_type: Output format (markdown, html, json)
        
        Returns:
            Generated documentation content
        """
        try:
            workflow_def = self.workflow_definitions.get(workflow_id)
            if not workflow_def:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            if format_type.lower() == 'markdown':
                return await self._generate_markdown_documentation(workflow_def, language)
            elif format_type.lower() == 'html':
                return await self._generate_html_documentation(workflow_def, language)
            elif format_type.lower() == 'json':
                return await self._generate_json_documentation(workflow_def, language)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
        
        except Exception as e:
            self.logger.error(f"Failed to generate workflow documentation: {e}")
            raise
    
    async def _generate_markdown_documentation(self, workflow_def: WorkflowDefinition, language: str) -> str:
        """Generate Markdown documentation for workflow"""
        content = f"""# {workflow_def.name}

{workflow_def.description}

**Workflow Type:** {workflow_def.workflow_type.value.replace('_', ' ').title()}  
**Creator Types:** {', '.join(workflow_def.creator_types)}  
**Estimated Duration:** {workflow_def.estimated_total_duration} minutes  
**Documentation Version:** {workflow_def.documentation_version}

## Workflow Steps

"""
        
        for step in workflow_def.steps:
            content += f"""### {step.order}. {step.title}

**Type:** {step.step_type.value.replace('_', ' ').title()}  
**Required:** {'Yes' if step.required else 'No'}  
**Estimated Time:** {step.estimated_duration} minutes

{step.description}

"""
            if step.help_text:
                content += f"**Help:** {step.help_text}\n\n"
            
            if step.prerequisites:
                content += f"**Prerequisites:** {', '.join(step.prerequisites)}\n\n"
            
            if step.video_tutorial_url:
                content += f"**Video Tutorial:** {step.video_tutorial_url}\n\n"
            
            if step.documentation_url:
                content += f"**Documentation:** {step.documentation_url}\n\n"
        
        content += f"""## Success Criteria

"""
        for criterion, value in workflow_def.success_criteria.items():
            content += f"- **{criterion.replace('_', ' ').title()}:** {value}\n"
        
        return content
    
    async def _generate_html_documentation(self, workflow_def: WorkflowDefinition, language: str) -> str:
        """Generate HTML documentation for workflow"""
        # Simplified HTML generation
        content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{workflow_def.name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .step {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .required {{ background-color: #fff3cd; }}
        .optional {{ background-color: #f8f9fa; }}
    </style>
</head>
<body>
    <h1>{workflow_def.name}</h1>
    <p>{workflow_def.description}</p>
    
    <h2>Workflow Steps</h2>
"""
        
        for step in workflow_def.steps:
            css_class = "required" if step.required else "optional"
            content += f"""
    <div class="step {css_class}">
        <h3>{step.order}. {step.title}</h3>
        <p><strong>Type:</strong> {step.step_type.value.replace('_', ' ').title()}</p>
        <p><strong>Duration:</strong> {step.estimated_duration} minutes</p>
        <p>{step.description}</p>
"""
            if step.help_text:
                content += f"        <p><strong>Help:</strong> {step.help_text}</p>"
            
            content += "    </div>"
        
        content += """
</body>
</html>"""
        
        return content
    
    async def _generate_json_documentation(self, workflow_def: WorkflowDefinition, language: str) -> str:
        """Generate JSON documentation for workflow"""
        # Convert workflow definition to JSON-serializable format
        workflow_dict = asdict(workflow_def)
        
        # Convert datetime objects to ISO strings
        for key, value in workflow_dict.items():
            if isinstance(value, datetime):
                workflow_dict[key] = value.isoformat()
        
        return json.dumps(workflow_dict, indent=2, ensure_ascii=False)

__all__ = [
    'CreatorWorkflowDocumentationTracker',
    'WorkflowType',
    'WorkflowStatus',
    'StepType',
    'WorkflowStep',
    'WorkflowStepProgress',
    'WorkflowDefinition',
    'WorkflowExecution',
    'WorkflowAnalytics'
]