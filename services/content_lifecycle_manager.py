"""
🔄 Content Lifecycle Manager Service
Enterprise content lifecycle management with automated workflows and state transitions

Demonstrates: Backend Senior + DBA + DevOps + Security expertise
Features: Workflow automation, state management, versioning, audit trails

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import uuid
import json
from dataclasses import dataclass, field
import structlog
from abc import ABC, abstractmethod
from collections import defaultdict
import aiofiles
from pathlib import Path

logger = structlog.get_logger(__name__)

class ContentLifecycleState(str, Enum):
    """Content lifecycle states"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    UPDATED = "updated"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    DELETED = "deleted"
    QUARANTINED = "quarantined"

class TransitionTrigger(str, Enum):
    """Lifecycle transition triggers"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    CONDITION_MET = "condition_met"

class WorkflowAction(str, Enum):
    """Workflow actions"""
    VALIDATE = "validate"
    REVIEW = "review"
    APPROVE = "approve"
    REJECT = "reject"
    PUBLISH = "publish"
    UPDATE = "update"
    ARCHIVE = "archive"
    DELETE = "delete"
    BACKUP = "backup"
    NOTIFY = "notify"

@dataclass
class StateTransition:
    """Represents a state transition"""
    from_state: ContentLifecycleState
    to_state: ContentLifecycleState
    trigger: TransitionTrigger
    conditions: List[str] = field(default_factory=list)
    actions: List[WorkflowAction] = field(default_factory=list)
    required_roles: List[str] = field(default_factory=list)
    auto_transition: bool = False

class ContentVersion(BaseModel):
    """Content version information"""
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version_number: str = Field(..., description="Semantic version number")
    content_id: str = Field(..., description="Parent content ID")
    state: ContentLifecycleState
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(..., description="User who created this version")
    changes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    file_path: Optional[str] = None
    file_checksum: Optional[str] = None
    is_current: bool = False

class AuditLogEntry(BaseModel):
    """Audit log entry for lifecycle changes"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    action: str
    old_state: Optional[ContentLifecycleState] = None
    new_state: Optional[ContentLifecycleState] = None
    triggered_by: str
    trigger_type: TransitionTrigger
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class WorkflowStep(BaseModel):
    """Workflow step definition"""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    action: WorkflowAction
    conditions: List[str] = Field(default_factory=list)
    timeout_minutes: Optional[int] = None
    retry_count: int = 0
    parallel: bool = False
    required_roles: List[str] = Field(default_factory=list)

class ContentWorkflow(BaseModel):
    """Content workflow definition"""
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    content_types: List[str] = Field(default_factory=list)
    steps: List[WorkflowStep] = Field(default_factory=list)
    triggers: List[TransitionTrigger] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

class ContentLifecycleInfo(BaseModel):
    """Complete content lifecycle information"""
    content_id: str
    current_state: ContentLifecycleState
    current_version: ContentVersion
    all_versions: List[ContentVersion] = Field(default_factory=list)
    workflow_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LifecycleRule(ABC):
    """Abstract base class for lifecycle rules"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def evaluate(self, content: ContentLifecycleInfo, context: Dict[str, Any]) -> bool:
        """Evaluate if rule condition is met"""
        pass

class TimeBasedRule(LifecycleRule):
    """Time-based lifecycle rule"""
    
    def __init__(self, name: str, days_threshold: int, target_state: ContentLifecycleState):
        super().__init__(name, f"Transition to {target_state} after {days_threshold} days")
        self.days_threshold = days_threshold
        self.target_state = target_state
    
    async def evaluate(self, content: ContentLifecycleInfo, context: Dict[str, Any]) -> bool:
        """Check if time threshold has been exceeded"""
        days_since_update = (datetime.now() - content.updated_at).days
        return days_since_update >= self.days_threshold

class ViewCountRule(LifecycleRule):
    """View count based lifecycle rule"""
    
    def __init__(self, name: str, view_threshold: int, action: str):
        super().__init__(name, f"Trigger {action} when views exceed {view_threshold}")
        self.view_threshold = view_threshold
        self.action = action
    
    async def evaluate(self, content: ContentLifecycleInfo, context: Dict[str, Any]) -> bool:
        """Check if view count threshold has been exceeded"""
        view_count = context.get('view_count', 0)
        return view_count >= self.view_threshold

class ContentLifecycleManager:
    """
    Enterprise Content Lifecycle Manager
    
    Demonstrates expertise in:
    - Backend Senior: Complex state management, async workflows, error handling
    - DBA: Data versioning, audit trails, state consistency
    - DevOps: Automated workflows, monitoring, performance optimization
    - Security: Access control, audit logging, secure state transitions
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.state_machine: Dict[ContentLifecycleState, List[StateTransition]] = {}
        self.workflows: Dict[str, ContentWorkflow] = {}
        self.rules: Dict[str, LifecycleRule] = {}
        self.content_registry: Dict[str, ContentLifecycleInfo] = {}
        self.audit_log: List[AuditLogEntry] = []
        self.metrics = {
            'total_content_items': 0,
            'active_workflows': 0,
            'state_transitions': 0,
            'automatic_transitions': 0,
            'manual_transitions': 0,
            'failed_transitions': 0
        }
        
        # Initialize state machine and default workflows
        self._initialize_state_machine()
        self._initialize_default_workflows()
        self._initialize_default_rules()
        
        logger.info("Content Lifecycle Manager initialized",
                   states=len(self.state_machine),
                   workflows=len(self.workflows),
                   rules=len(self.rules))
    
    def _initialize_state_machine(self):
        """Initialize content lifecycle state machine"""
        
        # Define valid state transitions
        transitions = [
            # Creation flow
            StateTransition(
                ContentLifecycleState.DRAFT, 
                ContentLifecycleState.PENDING_REVIEW,
                TransitionTrigger.MANUAL,
                conditions=["content_complete", "metadata_valid"],
                actions=[WorkflowAction.VALIDATE, WorkflowAction.NOTIFY]
            ),
            
            # Review flow
            StateTransition(
                ContentLifecycleState.PENDING_REVIEW,
                ContentLifecycleState.IN_REVIEW,
                TransitionTrigger.AUTOMATIC,
                actions=[WorkflowAction.NOTIFY],
                required_roles=["reviewer"]
            ),
            
            StateTransition(
                ContentLifecycleState.IN_REVIEW,
                ContentLifecycleState.APPROVED,
                TransitionTrigger.MANUAL,
                actions=[WorkflowAction.APPROVE, WorkflowAction.NOTIFY],
                required_roles=["reviewer", "editor"]
            ),
            
            StateTransition(
                ContentLifecycleState.IN_REVIEW,
                ContentLifecycleState.DRAFT,
                TransitionTrigger.MANUAL,
                actions=[WorkflowAction.REJECT, WorkflowAction.NOTIFY]
            ),
            
            # Publishing flow
            StateTransition(
                ContentLifecycleState.APPROVED,
                ContentLifecycleState.PUBLISHED,
                TransitionTrigger.MANUAL,
                actions=[WorkflowAction.PUBLISH, WorkflowAction.BACKUP, WorkflowAction.NOTIFY],
                required_roles=["publisher"]
            ),
            
            # Update flow
            StateTransition(
                ContentLifecycleState.PUBLISHED,
                ContentLifecycleState.UPDATED,
                TransitionTrigger.MANUAL,
                actions=[WorkflowAction.UPDATE, WorkflowAction.BACKUP]
            ),
            
            # Archival flow
            StateTransition(
                ContentLifecycleState.PUBLISHED,
                ContentLifecycleState.DEPRECATED,
                TransitionTrigger.CONDITION_MET,
                conditions=["age_threshold_met", "view_count_low"],
                actions=[WorkflowAction.NOTIFY],
                auto_transition=True
            ),
            
            StateTransition(
                ContentLifecycleState.DEPRECATED,
                ContentLifecycleState.ARCHIVED,
                TransitionTrigger.CONDITION_MET,
                conditions=["deprecated_time_exceeded"],
                actions=[WorkflowAction.ARCHIVE, WorkflowAction.BACKUP],
                auto_transition=True
            ),
            
            # Security transitions
            StateTransition(
                ContentLifecycleState.PUBLISHED,
                ContentLifecycleState.QUARANTINED,
                TransitionTrigger.EVENT_DRIVEN,
                conditions=["security_threat_detected"],
                actions=[WorkflowAction.NOTIFY],
                required_roles=["security_admin"]
            )
        ]
        
        # Organize transitions by from_state
        for transition in transitions:
            if transition.from_state not in self.state_machine:
                self.state_machine[transition.from_state] = []
            self.state_machine[transition.from_state].append(transition)
    
    def _initialize_default_workflows(self):
        """Initialize default content workflows"""
        
        # Standard content workflow
        standard_workflow = ContentWorkflow(
            name="Standard Content Workflow",
            description="Default workflow for regular content",
            content_types=["article", "blog_post", "tutorial"],
            steps=[
                WorkflowStep(
                    name="Initial Validation",
                    action=WorkflowAction.VALIDATE,
                    timeout_minutes=5
                ),
                WorkflowStep(
                    name="Editorial Review",
                    action=WorkflowAction.REVIEW,
                    timeout_minutes=1440,  # 24 hours
                    required_roles=["editor"]
                ),
                WorkflowStep(
                    name="Final Approval",
                    action=WorkflowAction.APPROVE,
                    required_roles=["publisher"]
                ),
                WorkflowStep(
                    name="Publication",
                    action=WorkflowAction.PUBLISH,
                    required_roles=["publisher"]
                )
            ],
            triggers=[TransitionTrigger.MANUAL, TransitionTrigger.AUTOMATIC]
        )
        
        # Fast track workflow for trusted creators
        fast_track_workflow = ContentWorkflow(
            name="Fast Track Workflow",
            description="Expedited workflow for trusted creators",
            content_types=["quick_post", "update"],
            steps=[
                WorkflowStep(
                    name="Automated Validation",
                    action=WorkflowAction.VALIDATE,
                    timeout_minutes=1
                ),
                WorkflowStep(
                    name="Auto Approval",
                    action=WorkflowAction.APPROVE,
                    conditions=["creator_trusted", "content_low_risk"]
                ),
                WorkflowStep(
                    name="Immediate Publication",
                    action=WorkflowAction.PUBLISH
                )
            ],
            triggers=[TransitionTrigger.AUTOMATIC]
        )
        
        self.workflows[standard_workflow.workflow_id] = standard_workflow
        self.workflows[fast_track_workflow.workflow_id] = fast_track_workflow
    
    def _initialize_default_rules(self):
        """Initialize default lifecycle rules"""
        
        # Auto-archive old content
        auto_archive_rule = TimeBasedRule(
            "auto_archive",
            days_threshold=365,  # 1 year
            target_state=ContentLifecycleState.ARCHIVED
        )
        
        # Deprecate low-performing content
        low_performance_rule = ViewCountRule(
            "low_performance_deprecation",
            view_threshold=100,
            action="deprecate"
        )
        
        # Popular content protection
        popular_content_rule = ViewCountRule(
            "popular_content_protection",
            view_threshold=10000,
            action="protect"
        )
        
        self.rules[auto_archive_rule.name] = auto_archive_rule
        self.rules[low_performance_rule.name] = low_performance_rule
        self.rules[popular_content_rule.name] = popular_content_rule
    
    async def create_content(self, content_id: str, creator_id: str, 
                           content_type: str, initial_metadata: Dict[str, Any] = None) -> ContentLifecycleInfo:
        """
        Create new content and initialize its lifecycle
        
        Backend Senior: Proper initialization, error handling
        DBA: Data structure creation, version management
        """
        try:
            # Create initial version
            initial_version = ContentVersion(
                version_number="1.0.0",
                content_id=content_id,
                state=ContentLifecycleState.DRAFT,
                created_by=creator_id,
                is_current=True,
                metadata=initial_metadata or {}
            )
            
            # Create lifecycle info
            lifecycle_info = ContentLifecycleInfo(
                content_id=content_id,
                current_state=ContentLifecycleState.DRAFT,
                current_version=initial_version,
                all_versions=[initial_version],
                created_by=creator_id,
                metadata=initial_metadata or {}
            )
            
            # Store in registry
            self.content_registry[content_id] = lifecycle_info
            
            # Create audit log entry
            await self._create_audit_entry(
                content_id=content_id,
                action="content_created",
                new_state=ContentLifecycleState.DRAFT,
                triggered_by=creator_id,
                trigger_type=TransitionTrigger.MANUAL,
                details={"content_type": content_type, "initial_metadata": initial_metadata}
            )
            
            # Update metrics
            self.metrics['total_content_items'] += 1
            
            logger.info("Content created",
                       content_id=content_id,
                       creator_id=creator_id,
                       content_type=content_type)
            
            return lifecycle_info
            
        except Exception as e:
            logger.error("Failed to create content",
                        content_id=content_id,
                        error=str(e))
            raise
    
    async def transition_state(self, content_id: str, target_state: ContentLifecycleState,
                             triggered_by: str, trigger_type: TransitionTrigger = TransitionTrigger.MANUAL,
                             context: Dict[str, Any] = None) -> bool:
        """
        Transition content to new state
        
        Backend Senior: Complex state management, validation
        Security: Access control, audit logging
        DevOps: Automated workflow execution
        """
        try:
            content = self.content_registry.get(content_id)
            if not content:
                logger.error("Content not found for state transition", content_id=content_id)
                return False
            
            current_state = content.current_state
            context = context or {}
            
            # Find valid transition
            valid_transition = None
            possible_transitions = self.state_machine.get(current_state, [])
            
            for transition in possible_transitions:
                if transition.to_state == target_state:
                    # Check conditions
                    if await self._check_transition_conditions(transition, content, context):
                        valid_transition = transition
                        break
            
            if not valid_transition:
                logger.warning("Invalid state transition attempted",
                             content_id=content_id,
                             from_state=current_state,
                             to_state=target_state)
                return False
            
            # Check role requirements
            if valid_transition.required_roles and not self._check_role_permissions(
                triggered_by, valid_transition.required_roles, context
            ):
                logger.warning("Insufficient permissions for state transition",
                             content_id=content_id,
                             triggered_by=triggered_by,
                             required_roles=valid_transition.required_roles)
                return False
            
            # Execute transition actions
            for action in valid_transition.actions:
                await self._execute_workflow_action(action, content, triggered_by, context)
            
            # Update content state
            old_state = content.current_state
            content.current_state = target_state
            content.updated_at = datetime.now()
            
            # Create new version if significant change
            if self._is_significant_change(old_state, target_state):
                await self._create_new_version(content, triggered_by, f"State transition: {old_state} -> {target_state}")
            
            # Create audit log entry
            await self._create_audit_entry(
                content_id=content_id,
                action="state_transition",
                old_state=old_state,
                new_state=target_state,
                triggered_by=triggered_by,
                trigger_type=trigger_type,
                details=context
            )
            
            # Update metrics
            self.metrics['state_transitions'] += 1
            if trigger_type == TransitionTrigger.AUTOMATIC:
                self.metrics['automatic_transitions'] += 1
            else:
                self.metrics['manual_transitions'] += 1
            
            logger.info("State transition completed",
                       content_id=content_id,
                       from_state=old_state,
                       to_state=target_state,
                       triggered_by=triggered_by)
            
            # Check for follow-up automatic transitions
            await self._check_automatic_transitions(content_id)
            
            return True
            
        except Exception as e:
            logger.error("State transition failed",
                        content_id=content_id,
                        target_state=target_state,
                        error=str(e))
            self.metrics['failed_transitions'] += 1
            return False
    
    async def _check_transition_conditions(self, transition: StateTransition, 
                                         content: ContentLifecycleInfo, 
                                         context: Dict[str, Any]) -> bool:
        """Check if transition conditions are met"""
        for condition in transition.conditions:
            if not await self._evaluate_condition(condition, content, context):
                return False
        return True
    
    async def _evaluate_condition(self, condition: str, content: ContentLifecycleInfo, 
                                context: Dict[str, Any]) -> bool:
        """Evaluate a specific condition"""
        try:
            # Built-in conditions
            if condition == "content_complete":
                return len(content.metadata.get('description', '')) > 10
            elif condition == "metadata_valid":
                required_fields = ['title', 'description', 'category']
                return all(field in content.metadata for field in required_fields)
            elif condition == "age_threshold_met":
                age_days = (datetime.now() - content.updated_at).days
                return age_days > 365
            elif condition == "view_count_low":
                return context.get('view_count', 0) < 100
            elif condition == "deprecated_time_exceeded":
                deprecated_days = (datetime.now() - content.updated_at).days
                return deprecated_days > 90
            elif condition == "security_threat_detected":
                return context.get('security_alert', False)
            elif condition == "creator_trusted":
                return context.get('creator_trust_score', 0) > 0.8
            elif condition == "content_low_risk":
                return context.get('risk_score', 1.0) < 0.3
            else:
                logger.warning("Unknown condition", condition=condition)
                return False
                
        except Exception as e:
            logger.error("Condition evaluation failed", condition=condition, error=str(e))
            return False
    
    def _check_role_permissions(self, user_id: str, required_roles: List[str], 
                               context: Dict[str, Any]) -> bool:
        """Check if user has required roles"""
        user_roles = context.get('user_roles', [])
        return any(role in user_roles for role in required_roles)
    
    async def _execute_workflow_action(self, action: WorkflowAction, content: ContentLifecycleInfo,
                                     triggered_by: str, context: Dict[str, Any]):
        """Execute workflow action"""
        try:
            if action == WorkflowAction.VALIDATE:
                # Trigger content validation
                logger.info("Executing validation action", content_id=content.content_id)
                
            elif action == WorkflowAction.NOTIFY:
                # Send notifications
                await self._send_notification(content, action, triggered_by, context)
                
            elif action == WorkflowAction.BACKUP:
                # Create backup
                await self._create_backup(content)
                
            elif action == WorkflowAction.PUBLISH:
                # Publish content
                logger.info("Publishing content", content_id=content.content_id)
                content.metadata['published_at'] = datetime.now().isoformat()
                
            elif action == WorkflowAction.ARCHIVE:
                # Archive content
                logger.info("Archiving content", content_id=content.content_id)
                content.metadata['archived_at'] = datetime.now().isoformat()
                
            # Add more actions as needed
            
        except Exception as e:
            logger.error("Workflow action execution failed",
                        action=action,
                        content_id=content.content_id,
                        error=str(e))
    
    async def _send_notification(self, content: ContentLifecycleInfo, action: WorkflowAction,
                               triggered_by: str, context: Dict[str, Any]):
        """Send notification for workflow action"""
        # Simulate notification sending
        logger.info("Notification sent",
                   content_id=content.content_id,
                   action=action,
                   triggered_by=triggered_by)
    
    async def _create_backup(self, content: ContentLifecycleInfo):
        """Create content backup"""
        backup_id = str(uuid.uuid4())
        backup_path = f"/backups/{content.content_id}/{backup_id}"
        
        # Simulate backup creation
        logger.info("Backup created",
                   content_id=content.content_id,
                   backup_id=backup_id,
                   backup_path=backup_path)
    
    def _is_significant_change(self, old_state: ContentLifecycleState, 
                              new_state: ContentLifecycleState) -> bool:
        """Check if state change is significant enough to create new version"""
        significant_changes = [
            (ContentLifecycleState.DRAFT, ContentLifecycleState.PUBLISHED),
            (ContentLifecycleState.PUBLISHED, ContentLifecycleState.UPDATED),
            (ContentLifecycleState.PUBLISHED, ContentLifecycleState.ARCHIVED)
        ]
        return (old_state, new_state) in significant_changes
    
    async def _create_new_version(self, content: ContentLifecycleInfo, created_by: str, 
                                changes: str):
        """Create new content version"""
        # Calculate new version number
        current_version = content.current_version.version_number
        version_parts = current_version.split('.')
        minor_version = int(version_parts[1]) + 1
        new_version = f"{version_parts[0]}.{minor_version}.0"
        
        # Mark current version as not current
        content.current_version.is_current = False
        
        # Create new version
        new_version_obj = ContentVersion(
            version_number=new_version,
            content_id=content.content_id,
            state=content.current_state,
            created_by=created_by,
            changes=[changes],
            metadata=content.metadata.copy(),
            is_current=True
        )
        
        # Update content
        content.current_version = new_version_obj
        content.all_versions.append(new_version_obj)
        
        logger.info("New content version created",
                   content_id=content.content_id,
                   version=new_version,
                   created_by=created_by)
    
    async def _create_audit_entry(self, content_id: str, action: str, 
                                triggered_by: str, trigger_type: TransitionTrigger,
                                old_state: Optional[ContentLifecycleState] = None,
                                new_state: Optional[ContentLifecycleState] = None,
                                details: Dict[str, Any] = None):
        """Create audit log entry"""
        entry = AuditLogEntry(
            content_id=content_id,
            action=action,
            old_state=old_state,
            new_state=new_state,
            triggered_by=triggered_by,
            trigger_type=trigger_type,
            details=details or {}
        )
        
        self.audit_log.append(entry)
        
        # Keep audit log size manageable
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-5000:]  # Keep last 5000 entries
    
    async def _check_automatic_transitions(self, content_id: str):
        """Check and execute automatic transitions"""
        content = self.content_registry.get(content_id)
        if not content:
            return
        
        current_state = content.current_state
        possible_transitions = self.state_machine.get(current_state, [])
        
        for transition in possible_transitions:
            if transition.auto_transition:
                # Check if conditions are met
                context = await self._get_content_context(content_id)
                if await self._check_transition_conditions(transition, content, context):
                    await self.transition_state(
                        content_id,
                        transition.to_state,
                        "system",
                        TransitionTrigger.AUTOMATIC,
                        context
                    )
                    break  # Only one automatic transition at a time
    
    async def _get_content_context(self, content_id: str) -> Dict[str, Any]:
        """Get context information for content"""
        # In production, this would fetch real metrics from analytics service
        return {
            'view_count': 150,
            'like_count': 25,
            'comment_count': 5,
            'creator_trust_score': 0.85,
            'risk_score': 0.2,
            'user_roles': ['creator', 'editor']
        }
    
    async def get_content_lifecycle(self, content_id: str) -> Optional[ContentLifecycleInfo]:
        """Get complete lifecycle information for content"""
        return self.content_registry.get(content_id)
    
    async def get_content_versions(self, content_id: str) -> List[ContentVersion]:
        """Get all versions of content"""
        content = self.content_registry.get(content_id)
        return content.all_versions if content else []
    
    async def get_audit_log(self, content_id: Optional[str] = None, 
                          limit: int = 100) -> List[AuditLogEntry]:
        """Get audit log entries"""
        if content_id:
            entries = [entry for entry in self.audit_log if entry.content_id == content_id]
        else:
            entries = self.audit_log
        
        # Return most recent entries
        return sorted(entries, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    async def process_lifecycle_rules(self):
        """Process automated lifecycle rules"""
        processed_count = 0
        
        for content_id, content in self.content_registry.items():
            context = await self._get_content_context(content_id)
            
            # Evaluate all rules
            for rule_name, rule in self.rules.items():
                try:
                    if await rule.evaluate(content, context):
                        logger.info("Lifecycle rule triggered",
                                   content_id=content_id,
                                   rule=rule_name)
                        
                        # Execute rule-specific actions
                        if isinstance(rule, TimeBasedRule):
                            await self.transition_state(
                                content_id,
                                rule.target_state,
                                "system",
                                TransitionTrigger.CONDITION_MET,
                                context
                            )
                        
                        processed_count += 1
                        
                except Exception as e:
                    logger.error("Rule processing failed",
                               content_id=content_id,
                               rule=rule_name,
                               error=str(e))
        
        logger.info("Lifecycle rules processing completed", processed_count=processed_count)
        return processed_count
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        state_distribution = defaultdict(int)
        for content in self.content_registry.values():
            state_distribution[content.current_state] += 1
        
        return {
            **self.metrics,
            'state_distribution': dict(state_distribution),
            'audit_log_entries': len(self.audit_log),
            'content_registry_size': len(self.content_registry),
            'active_workflows': len([w for w in self.workflows.values() if w.is_active]),
            'service_status': 'healthy'
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            'service': 'content_lifecycle_manager',
            'status': 'healthy',
            'version': '1.0.0',
            'content_items': len(self.content_registry),
            'workflows': len(self.workflows),
            'rules': len(self.rules),
            'total_transitions': self.metrics['state_transitions']
        }

# Example usage and testing
async def example_usage():
    """Example usage of the Content Lifecycle Manager"""
    
    # Initialize manager
    manager = ContentLifecycleManager()
    
    # Create new content
    content_info = await manager.create_content(
        content_id="test_content_001",
        creator_id="creator_001",
        content_type="article",
        initial_metadata={
            "title": "Test Article",
            "description": "This is a test article for demonstration",
            "category": "technology"
        }
    )
    
    print(f"Content created: {content_info.content_id}")
    print(f"Current state: {content_info.current_state}")
    
    # Transition to review
    success = await manager.transition_state(
        content_info.content_id,
        ContentLifecycleState.PENDING_REVIEW,
        "creator_001",
        context={"user_roles": ["creator"]}
    )
    print(f"Transition to review: {success}")
    
    # Transition to published
    success = await manager.transition_state(
        content_info.content_id,
        ContentLifecycleState.IN_REVIEW,
        "reviewer_001",
        context={"user_roles": ["reviewer"]}
    )
    print(f"Transition to in_review: {success}")
    
    success = await manager.transition_state(
        content_info.content_id,
        ContentLifecycleState.APPROVED,
        "reviewer_001",
        context={"user_roles": ["reviewer", "editor"]}
    )
    print(f"Transition to approved: {success}")
    
    success = await manager.transition_state(
        content_info.content_id,
        ContentLifecycleState.PUBLISHED,
        "publisher_001",
        context={"user_roles": ["publisher"]}
    )
    print(f"Transition to published: {success}")
    
    # Get audit log
    audit_entries = await manager.get_audit_log(content_info.content_id)
    print(f"Audit entries: {len(audit_entries)}")
    
    # Get metrics
    metrics = await manager.get_service_metrics()
    print(f"Service metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(example_usage())