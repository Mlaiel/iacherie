"""Conversation State Manager - IA Influencer Agent

Enterprise conversation state management for multi-format content creators with
intelligent state transitions, persistence, and workflow optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict, deque

from ...core.exceptions import StateManagerError
from ...core.monitoring import MetricsCollector
from ...utils.cache import CacheManager


class ConversationPhase(Enum):
    """Conversation phases in creator workflow"""    ONBOARDING = "onboarding"
    CONTENT_DISCOVERY = "content_discovery"
    PROTECTION_SETUP = "protection_setup"
    COLLABORATION_EXPLORATION = "collaboration_exploration"
    MONETIZATION_PLANNING = "monetization_planning"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    ANALYTICS_REVIEW = "analytics_review"
    FEATURE_EXPLORATION = "feature_exploration"
    SUPPORT_REQUEST = "support_request"
    WORKFLOW_COMPLETION = "workflow_completion"


class StateTransitionReason(Enum):
    """Reasons for state transitions"""    USER_REQUEST = "user_request"
    WORKFLOW_COMPLETION = "workflow_completion"
    TIMEOUT = "timeout"
    ERROR_RECOVERY = "error_recovery"
    SYSTEM_RECOMMENDATION = "system_recommendation"
    COLLABORATION_TRIGGER = "collaboration_trigger"
    PROTECTION_ALERT = "protection_alert"


@dataclass
class StateTransition:
    """State transition record"""    transition_id: str
    from_state: str
    to_state: str
    reason: StateTransitionReason
    timestamp: datetime
    context_data: Dict[str, Any]
    success: bool = True
    duration: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "reason": self.reason.value,
            "timestamp": self.timestamp.isoformat(),
            "context_data": self.context_data,
            "success": self.success,
            "duration": self.duration
        }


@dataclass
class WorkflowStep:
    """Individual workflow step"""    step_id: str
    step_name: str
    phase: ConversationPhase
    required_inputs: List[str]
    expected_outputs: List[str]
    estimated_duration: int  # seconds
    completion_criteria: Dict[str, Any]
    is_completed: bool = False
    completion_timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "step_name": self.step_name,
            "phase": self.phase.value,
            "required_inputs": self.required_inputs,
            "expected_outputs": self.expected_outputs,
            "estimated_duration": self.estimated_duration,
            "completion_criteria": self.completion_criteria,
            "is_completed": self.is_completed,
            "completion_timestamp": self.completion_timestamp.isoformat() if self.completion_timestamp else None
        }


@dataclass
class ConversationWorkflow:
    """Complete conversation workflow"""    workflow_id: str
    workflow_name: str
    creator_type: str
    steps: List[WorkflowStep]
    current_step_index: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    
    def get_current_step(self) -> Optional[WorkflowStep]:
        """Get current workflow step"""        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def get_next_step(self) -> Optional[WorkflowStep]:
        """Get next workflow step"""        if self.current_step_index + 1 < len(self.steps):
            return self.steps[self.current_step_index + 1]
        return None
    
    def calculate_progress(self) -> float:
        """Calculate workflow completion progress"""        if not self.steps:
            return 0.0
        completed_steps = sum(1 for step in self.steps if step.is_completed)
        return completed_steps / len(self.steps)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "creator_type": self.creator_type,
            "steps": [step.to_dict() for step in self.steps],
            "current_step_index": self.current_step_index,
            "started_at": self.started_at.isoformat(),
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "actual_completion": self.actual_completion.isoformat() if self.actual_completion else None,
            "progress": self.calculate_progress()
        }


@dataclass
class ConversationState:
    """Comprehensive conversation state"""    conversation_id: str
    user_id: str
    session_id: str
    
    # Current state
    current_phase: ConversationPhase
    current_workflow: Optional[ConversationWorkflow] = None
    state_context: Dict[str, Any] = field(default_factory=dict)
    
    # State history
    state_history: List[StateTransition] = field(default_factory=list)
    phase_durations: Dict[str, float] = field(default_factory=dict)
    
    # Workflow tracking
    completed_workflows: List[str] = field(default_factory=list)
    pending_actions: List[str] = field(default_factory=list)
    blocked_actions: Dict[str, str] = field(default_factory=dict)  # action -> reason
    
    # Temporal tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_state_change: datetime = field(default_factory=datetime.utcnow)
    phase_start_time: datetime = field(default_factory=datetime.utcnow)
    
    # Engagement tracking
    user_engagement_level: float = 0.5
    conversation_momentum: float = 0.5
    completion_likelihood: float = 0.5
    
    def add_transition(self, transition: StateTransition):
        """Add state transition to history"""        self.state_history.append(transition)
        self.last_state_change = datetime.utcnow()
        
        # Update phase duration if phase changed
        if transition.to_state != transition.from_state:
            if transition.from_state in self.phase_durations:
                self.phase_durations[transition.from_state] += (
                    datetime.utcnow() - self.phase_start_time
                ).total_seconds()
            else:
                self.phase_durations[transition.from_state] = (
                    datetime.utcnow() - self.phase_start_time
                ).total_seconds()
            
            self.phase_start_time = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "current_phase": self.current_phase.value,
            "current_workflow": self.current_workflow.to_dict() if self.current_workflow else None,
            "state_context": self.state_context,
            "state_history_count": len(self.state_history),
            "phase_durations": self.phase_durations,
            "completed_workflows": self.completed_workflows,
            "pending_actions": self.pending_actions,
            "blocked_actions": self.blocked_actions,
            "created_at": self.created_at.isoformat(),
            "last_state_change": self.last_state_change.isoformat(),
            "phase_start_time": self.phase_start_time.isoformat(),
            "user_engagement_level": self.user_engagement_level,
            "conversation_momentum": self.conversation_momentum,
            "completion_likelihood": self.completion_likelihood
        }


class ConversationStateManager:
    """    Enterprise conversation state manager providing intelligent state tracking,
    workflow orchestration, and completion optimization for content creators.
    
    Features:
    - Multi-phase conversation management
    - Workflow-driven state transitions
    - Intelligent completion prediction
    - State persistence and recovery
    - Analytics and optimization
    """    
    def __init__(
        self,
        cache_manager: CacheManager,
        metrics_collector: MetricsCollector,
        state_timeout: int = 3600,  # 1 hour
        max_state_history: int = 100
    ):
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
        self.state_timeout = state_timeout
        self.max_state_history = max_state_history
        
        # State storage
        self.conversation_states: Dict[str, ConversationState] = {}
        
        # Workflow templates
        self.workflow_templates: Dict[str, ConversationWorkflow] = {}
        
        # State machine configuration
        self.valid_transitions: Dict[ConversationPhase, Set[ConversationPhase]] = {}
        
        # Background processing
        self.cleanup_task: Optional[asyncio.Task] = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("ConversationStateManager initialized")
    
    async def start(self):
        """Start the conversation state manager"""        try:
            # Load existing states
            await self._load_states()
            
            # Initialize workflow templates
            await self._initialize_workflow_templates()
            
            # Setup state machine
            await self._setup_state_machine()
            
            # Start background cleanup
            self.cleanup_task = asyncio.create_task(self._background_cleanup())
            
            self.logger.info("ConversationStateManager started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start ConversationStateManager: {e}")
            raise StateManagerError(f"Startup failed: {e}")
    
    async def stop(self):
        """Stop the conversation state manager"""        try:
            # Cancel background tasks
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Save states
            await self._save_states()
            
            self.logger.info("ConversationStateManager stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping ConversationStateManager: {e}")
    
    async def initialize_conversation_state(
        self,
        conversation_id: str,
        user_id: str,
        session_id: str,
        creator_type: str = "multi_format",
        initial_phase: ConversationPhase = ConversationPhase.ONBOARDING
    ) -> ConversationState:
        """        Initialize new conversation state
        
        Args:
            conversation_id: Conversation identifier
            user_id: User identifier
            session_id: Session identifier
            creator_type: Type of content creator
            initial_phase: Starting conversation phase
            
        Returns:
            ConversationState: Initialized state
        """        try:
            # Create conversation state
            state = ConversationState(
                conversation_id=conversation_id,
                user_id=user_id,
                session_id=session_id,
                current_phase=initial_phase
            )
            
            # Initialize workflow if applicable
            workflow = await self._create_workflow_for_phase(initial_phase, creator_type)
            if workflow:
                state.current_workflow = workflow
            
            # Store state
            self.conversation_states[conversation_id] = state
            
            # Cache state
            await self._cache_state(state)
            
            # Collect metrics
            await self.metrics_collector.increment(
                "conversation_states.initialized",
                tags={"phase": initial_phase.value, "creator_type": creator_type}
            )
            
            self.logger.info(f"Conversation state initialized: {conversation_id}")
            return state
            
        except Exception as e:
            self.logger.error(f"Error initializing conversation state: {e}")
            raise StateManagerError(f"Failed to initialize state: {e}")
    
    async def get_conversation_state(
        self,
        conversation_id: str
    ) -> Optional[ConversationState]:
        """        Get conversation state
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            ConversationState or None if not found
        """        try:
            # Check in-memory storage
            if conversation_id in self.conversation_states:
                return self.conversation_states[conversation_id]
            
            # Try to load from cache
            state = await self._load_state(conversation_id)
            if state:
                self.conversation_states[conversation_id] = state
                return state
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting conversation state {conversation_id}: {e}")
            return None
    
    async def transition_to_phase(
        self,
        conversation_id: str,
        target_phase: ConversationPhase,
        reason: StateTransitionReason = StateTransitionReason.USER_REQUEST,
        context_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """        Transition conversation to new phase
        
        Args:
            conversation_id: Conversation identifier
            target_phase: Target conversation phase
            reason: Reason for transition
            context_data: Additional context data
            
        Returns:
            bool: Success status
        """        try:
            state = await self.get_conversation_state(conversation_id)
            if not state:
                return False
            
            current_phase = state.current_phase
            
            # Validate transition
            if not await self._validate_transition(current_phase, target_phase):
                self.logger.warning(f"Invalid transition from {current_phase.value} to {target_phase.value}")
                return False
            
            # Create transition record
            transition = StateTransition(
                transition_id=str(uuid.uuid4()),
                from_state=current_phase.value,
                to_state=target_phase.value,
                reason=reason,
                timestamp=datetime.utcnow(),
                context_data=context_data or {}
            )
            
            # Update state
            state.current_phase = target_phase
            state.add_transition(transition)
            
            # Handle workflow changes
            await self._handle_phase_change(state, current_phase, target_phase)
            
            # Update engagement metrics
            await self._update_engagement_metrics(state, transition)
            
            # Cache updated state
            await self._cache_state(state)
            
            # Collect metrics
            await self.metrics_collector.increment(
                "conversation_states.transitions",
                tags={
                    "from_phase": current_phase.value,
                    "to_phase": target_phase.value,
                    "reason": reason.value
                }
            )
            
            self.logger.info(f"State transition: {conversation_id} from {current_phase.value} to {target_phase.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error transitioning state: {e}")
            return False
    
    async def update_workflow_progress(
        self,
        conversation_id: str,
        step_id: str,
        completion_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """        Update workflow step progress
        
        Args:
            conversation_id: Conversation identifier
            step_id: Workflow step identifier
            completion_data: Step completion data
            
        Returns:
            bool: Success status
        """        try:
            state = await self.get_conversation_state(conversation_id)
            if not state or not state.current_workflow:
                return False
            
            workflow = state.current_workflow
            
            # Find and update step
            for step in workflow.steps:
                if step.step_id == step_id:
                    step.is_completed = True
                    step.completion_timestamp = datetime.utcnow()
                    break
            else:
                return False  # Step not found
            
            # Update workflow progress
            progress = workflow.calculate_progress()
            
            # Check if workflow is complete
            if progress >= 1.0:
                workflow.actual_completion = datetime.utcnow()
                state.completed_workflows.append(workflow.workflow_id)
                
                # Suggest next phase
                next_phase = await self._suggest_next_phase(state)
                if next_phase and next_phase != state.current_phase:
                    await self.transition_to_phase(
                        conversation_id,
                        next_phase,
                        StateTransitionReason.WORKFLOW_COMPLETION
                    )
            else:
                # Move to next step
                current_step = workflow.get_current_step()
                if current_step and current_step.is_completed:
                    workflow.current_step_index += 1
            
            # Update completion likelihood
            state.completion_likelihood = min(
                state.completion_likelihood + 0.1,
                1.0
            )
            
            # Cache updated state
            await self._cache_state(state)
            
            # Collect metrics
            await self.metrics_collector.increment(
                "workflow.steps.completed",
                tags={"workflow_id": workflow.workflow_id}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating workflow progress: {e}")
            return False
    
    async def add_pending_action(
        self,
        conversation_id: str,
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """        Add pending action to conversation state
        
        Args:
            conversation_id: Conversation identifier
            action: Action to add
            context: Action context
            
        Returns:
            bool: Success status
        """        try:
            state = await self.get_conversation_state(conversation_id)
            if not state:
                return False
            
            if action not in state.pending_actions:
                state.pending_actions.append(action)
                
                # Update state context if provided
                if context:
                    state.state_context.update(context)
                
                # Cache updated state
                await self._cache_state(state)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding pending action: {e}")
            return False
    
    async def complete_pending_action(
        self,
        conversation_id: str,
        action: str
    ) -> bool:
        """        Mark pending action as completed
        
        Args:
            conversation_id: Conversation identifier
            action: Action to complete
            
        Returns:
            bool: Success status
        """        try:
            state = await self.get_conversation_state(conversation_id)
            if not state:
                return False
            
            if action in state.pending_actions:
                state.pending_actions.remove(action)
                
                # Update momentum
                state.conversation_momentum = min(
                    state.conversation_momentum + 0.05,
                    1.0
                )
                
                # Cache updated state
                await self._cache_state(state)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error completing pending action: {e}")
            return False
    
    async def get_state_analytics(
        self,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        phase: Optional[ConversationPhase] = None
    ) -> Dict[str, Any]:
        """        Get state analytics
        
        Args:
            conversation_id: Specific conversation to analyze
            user_id: Specific user to analyze
            phase: Specific phase to analyze
            
        Returns:
            Dict containing analytics data
        """        try:
            states_to_analyze = []
            
            if conversation_id:
                state = await self.get_conversation_state(conversation_id)
                if state:
                    states_to_analyze = [state]
            else:
                # Analyze all states with filters
                for state in self.conversation_states.values():
                    if user_id and state.user_id != user_id:
                        continue
                    if phase and state.current_phase != phase:
                        continue
                    states_to_analyze.append(state)
            
            if not states_to_analyze:
                return {"total_conversations": 0}
            
            # Calculate analytics
            total_conversations = len(states_to_analyze)
            
            # Phase distribution
            phase_dist = defaultdict(int)
            for state in states_to_analyze:
                phase_dist[state.current_phase.value] += 1
            
            # Completion statistics
            total_workflows = sum(len(state.completed_workflows) for state in states_to_analyze)
            avg_completion_likelihood = sum(state.completion_likelihood for state in states_to_analyze) / total_conversations
            
            # Engagement statistics
            avg_engagement = sum(state.user_engagement_level for state in states_to_analyze) / total_conversations
            avg_momentum = sum(state.conversation_momentum for state in states_to_analyze) / total_conversations
            
            # Duration statistics
            conversation_durations = []
            for state in states_to_analyze:
                duration = (datetime.utcnow() - state.created_at).total_seconds()
                conversation_durations.append(duration)
            
            avg_duration = sum(conversation_durations) / len(conversation_durations)
            
            # Phase duration analysis
            phase_durations = defaultdict(list)
            for state in states_to_analyze:
                for phase_name, duration in state.phase_durations.items():
                    phase_durations[phase_name].append(duration)
            
            avg_phase_durations = {}
            for phase_name, durations in phase_durations.items():
                avg_phase_durations[phase_name] = sum(durations) / len(durations)
            
            return {
                "total_conversations": total_conversations,
                "phase_distribution": dict(phase_dist),
                "completion_statistics": {
                    "total_workflows_completed": total_workflows,
                    "average_completion_likelihood": avg_completion_likelihood,
                    "high_completion_likelihood_count": sum(1 for state in states_to_analyze if state.completion_likelihood > 0.7)
                },
                "engagement_statistics": {
                    "average_engagement": avg_engagement,
                    "average_momentum": avg_momentum,
                    "high_engagement_count": sum(1 for state in states_to_analyze if state.user_engagement_level > 0.7)
                },
                "duration_statistics": {
                    "average_conversation_duration": avg_duration,
                    "average_phase_durations": avg_phase_durations
                },
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating state analytics: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _validate_transition(
        self,
        from_phase: ConversationPhase,
        to_phase: ConversationPhase
    ) -> bool:
        """Validate if state transition is allowed"""        valid_targets = self.valid_transitions.get(from_phase, set())
        return to_phase in valid_targets or from_phase == to_phase
    
    async def _handle_phase_change(
        self,
        state: ConversationState,
        from_phase: ConversationPhase,
        to_phase: ConversationPhase
    ):
        """Handle workflow changes when phase changes"""        if from_phase != to_phase:
            # Create new workflow for the target phase if needed
            if to_phase in [
                ConversationPhase.PROTECTION_SETUP,
                ConversationPhase.COLLABORATION_EXPLORATION,
                ConversationPhase.MONETIZATION_PLANNING
            ]:
                creator_type = state.state_context.get("creator_type", "multi_format")
                new_workflow = await self._create_workflow_for_phase(to_phase, creator_type)
                if new_workflow:
                    state.current_workflow = new_workflow
    
    async def _update_engagement_metrics(
        self,
        state: ConversationState,
        transition: StateTransition
    ):
        """Update engagement metrics based on transition"""        # Update engagement based on transition reason
        if transition.reason == StateTransitionReason.USER_REQUEST:
            state.user_engagement_level = min(state.user_engagement_level + 0.1, 1.0)
        elif transition.reason == StateTransitionReason.TIMEOUT:
            state.user_engagement_level = max(state.user_engagement_level - 0.2, 0.0)
        
        # Update momentum based on transition speed
        time_since_last = (datetime.utcnow() - state.last_state_change).total_seconds()
        if time_since_last < 300:  # Fast transition (< 5 minutes)
            state.conversation_momentum = min(state.conversation_momentum + 0.1, 1.0)
        elif time_since_last > 1800:  # Slow transition (> 30 minutes)
            state.conversation_momentum = max(state.conversation_momentum - 0.1, 0.0)
    
    async def _suggest_next_phase(
        self,
        state: ConversationState
    ) -> Optional[ConversationPhase]:
        """Suggest next conversation phase based on current state"""        current_phase = state.current_phase
        creator_type = state.state_context.get("creator_type", "multi_format")
        
        # Phase progression logic
        phase_progression = {
            ConversationPhase.ONBOARDING: ConversationPhase.CONTENT_DISCOVERY,
            ConversationPhase.CONTENT_DISCOVERY: ConversationPhase.PROTECTION_SETUP,
            ConversationPhase.PROTECTION_SETUP: ConversationPhase.COLLABORATION_EXPLORATION,
            ConversationPhase.COLLABORATION_EXPLORATION: ConversationPhase.MONETIZATION_PLANNING,
            ConversationPhase.MONETIZATION_PLANNING: ConversationPhase.PLATFORM_OPTIMIZATION,
            ConversationPhase.PLATFORM_OPTIMIZATION: ConversationPhase.ANALYTICS_REVIEW,
            ConversationPhase.ANALYTICS_REVIEW: ConversationPhase.WORKFLOW_COMPLETION
        }
        
        return phase_progression.get(current_phase)
    
    async def _create_workflow_for_phase(
        self,
        phase: ConversationPhase,
        creator_type: str
    ) -> Optional[ConversationWorkflow]:
        """Create workflow for specific phase and creator type"""        workflow_key = f"{phase.value}_{creator_type}"
        
        if workflow_key in self.workflow_templates:
            template = self.workflow_templates[workflow_key]
            # Create a copy with new ID
            workflow = ConversationWorkflow(
                workflow_id=str(uuid.uuid4()),
                workflow_name=template.workflow_name,
                creator_type=creator_type,
                steps=[
                    WorkflowStep(
                        step_id=str(uuid.uuid4()),
                        step_name=step.step_name,
                        phase=step.phase,
                        required_inputs=step.required_inputs.copy(),
                        expected_outputs=step.expected_outputs.copy(),
                        estimated_duration=step.estimated_duration,
                        completion_criteria=step.completion_criteria.copy()
                    )
                    for step in template.steps
                ]
            )
            return workflow
        
        return None
    
    async def _initialize_workflow_templates(self):
        """Initialize workflow templates for different phases and creator types"""        # Onboarding workflow for musicians
        musician_onboarding = ConversationWorkflow(
            workflow_id="template_onboarding_musician",
            workflow_name="Musician Onboarding",
            creator_type="musician",
            steps=[
                WorkflowStep(
                    step_id="profile_setup",
                    step_name="Profile Setup",
                    phase=ConversationPhase.ONBOARDING,
                    required_inputs=["name", "genre", "experience_level"],
                    expected_outputs=["user_profile"],
                    estimated_duration=300,
                    completion_criteria={"profile_completeness": 0.8}
                ),
                WorkflowStep(
                    step_id="platform_connection",
                    step_name="Connect Platforms",
                    phase=ConversationPhase.ONBOARDING,
                    required_inputs=["spotify_account", "social_media"],
                    expected_outputs=["platform_connections"],
                    estimated_duration=180,
                    completion_criteria={"connected_platforms": 2}
                ),
                WorkflowStep(
                    step_id="content_upload",
                    step_name="Upload First Content",
                    phase=ConversationPhase.ONBOARDING,
                    required_inputs=["audio_file"],
                    expected_outputs=["protected_content"],
                    estimated_duration=240,
                    completion_criteria={"uploaded_files": 1}
                )
            ]
        )
        
        self.workflow_templates["onboarding_musician"] = musician_onboarding
        
        # Protection setup workflow
        protection_setup = ConversationWorkflow(
            workflow_id="template_protection_setup",
            workflow_name="Content Protection Setup",
            creator_type="multi_format",
            steps=[
                WorkflowStep(
                    step_id="fingerprint_creation",
                    step_name="Create Content Fingerprints",
                    phase=ConversationPhase.PROTECTION_SETUP,
                    required_inputs=["content_files"],
                    expected_outputs=["fingerprints"],
                    estimated_duration=120,
                    completion_criteria={"fingerprints_created": True}
                ),
                WorkflowStep(
                    step_id="monitoring_setup",
                    step_name="Setup Monitoring",
                    phase=ConversationPhase.PROTECTION_SETUP,
                    required_inputs=["platforms_to_monitor"],
                    expected_outputs=["monitoring_config"],
                    estimated_duration=180,
                    completion_criteria={"monitoring_active": True}
                )
            ]
        )
        
        self.workflow_templates["protection_setup_multi_format"] = protection_setup
        
        # Add more workflow templates as needed
    
    async def _setup_state_machine(self):
        """Setup valid state transitions"""        self.valid_transitions = {
            ConversationPhase.ONBOARDING: {
                ConversationPhase.CONTENT_DISCOVERY,
                ConversationPhase.SUPPORT_REQUEST,
                ConversationPhase.ONBOARDING
            },
            ConversationPhase.CONTENT_DISCOVERY: {
                ConversationPhase.PROTECTION_SETUP,
                ConversationPhase.COLLABORATION_EXPLORATION,
                ConversationPhase.SUPPORT_REQUEST,
                ConversationPhase.CONTENT_DISCOVERY
            },
            ConversationPhase.PROTECTION_SETUP: {
                ConversationPhase.COLLABORATION_EXPLORATION,
                ConversationPhase.MONETIZATION_PLANNING,
                ConversationPhase.SUPPORT_REQUEST,
                ConversationPhase.PROTECTION_SETUP
            },
            ConversationPhase.COLLABORATION_EXPLORATION: {
                ConversationPhase.MONETIZATION_PLANNING,
                ConversationPhase.PLATFORM_OPTIMIZATION,
                ConversationPhase.SUPPORT_REQUEST,
                ConversationPhase.COLLABORATION_EXPLORATION
            },
            ConversationPhase.MONETIZATION_PLANNING: {
                ConversationPhase.PLATFORM_OPTIMIZATION,
                ConversationPhase.ANALYTICS_REVIEW,
                ConversationPhase.SUPPORT_REQUEST,
                ConversationPhase.MONETIZATION_PLANNING
            },
            ConversationPhase.PLATFORM_OPTIMIZATION: {
                ConversationPhase.ANALYTICS_REVIEW,
                ConversationPhase.FEATURE_EXPLORATION,
                ConversationPhase.SUPPORT_REQUEST,
                ConversationPhase.PLATFORM_OPTIMIZATION
            },
            ConversationPhase.ANALYTICS_REVIEW: {
                ConversationPhase.WORKFLOW_COMPLETION,
                ConversationPhase.FEATURE_EXPLORATION,
                ConversationPhase.SUPPORT_REQUEST,
                ConversationPhase.ANALYTICS_REVIEW
            },
            ConversationPhase.FEATURE_EXPLORATION: {
                ConversationPhase.WORKFLOW_COMPLETION,
                ConversationPhase.SUPPORT_REQUEST,
                ConversationPhase.FEATURE_EXPLORATION
            },
            ConversationPhase.SUPPORT_REQUEST: {
                phase for phase in ConversationPhase  # Can go to any phase from support
            },
            ConversationPhase.WORKFLOW_COMPLETION: {
                ConversationPhase.CONTENT_DISCOVERY,  # Start new cycle
                ConversationPhase.FEATURE_EXPLORATION,
                ConversationPhase.WORKFLOW_COMPLETION
            }
        }
    
    async def _cache_state(self, state: ConversationState):
        """Cache conversation state"""        try:
            await self.cache_manager.set(
                f"conversation_state:{state.conversation_id}",
                state.to_dict(),
                ttl=self.state_timeout
            )
        except Exception as e:
            self.logger.error(f"Error caching state: {e}")
    
    async def _load_state(self, conversation_id: str) -> Optional[ConversationState]:
        """Load conversation state from cache"""        try:
            state_data = await self.cache_manager.get(f"conversation_state:{conversation_id}")
            if state_data:
                return self._state_from_dict(state_data)
            return None
        except Exception as e:
            self.logger.error(f"Error loading state: {e}")
            return None
    
    async def _load_states(self):
        """Load all conversation states"""        try:
            # Implementation would load from persistent storage
            pass
        except Exception as e:
            self.logger.error(f"Error loading states: {e}")
    
    async def _save_states(self):
        """Save all conversation states"""        try:
            # Implementation would save to persistent storage
            states_data = {}
            for conversation_id, state in self.conversation_states.items():
                states_data[conversation_id] = state.to_dict()
            
            await self.cache_manager.set(
                "conversation_states_backup",
                states_data,
                ttl=86400  # 24 hours
            )
        except Exception as e:
            self.logger.error(f"Error saving states: {e}")
    
    async def _background_cleanup(self):
        """Background task for state cleanup"""        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Clean up expired states
                expired_states = []
                for conversation_id, state in self.conversation_states.items():
                    time_since_activity = (datetime.utcnow() - state.last_state_change).total_seconds()
                    if time_since_activity > self.state_timeout:
                        expired_states.append(conversation_id)
                
                for conversation_id in expired_states:
                    del self.conversation_states[conversation_id]
                
                # Limit state history
                for state in self.conversation_states.values():
                    if len(state.state_history) > self.max_state_history:
                        state.state_history = state.state_history[-self.max_state_history:]
                
                if expired_states:
                    await self.metrics_collector.increment(
                        "conversation_states.expired",
                        value=len(expired_states)
                    )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Background cleanup error: {e}")
                await asyncio.sleep(60)
    
    def _state_from_dict(self, data: Dict[str, Any]) -> ConversationState:
        """Reconstruct state from dictionary"""        # Reconstruct workflow if present
        current_workflow = None
        workflow_data = data.get("current_workflow")
        if workflow_data:
            steps = []
            for step_data in workflow_data["steps"]:
                step = WorkflowStep(
                    step_id=step_data["step_id"],
                    step_name=step_data["step_name"],
                    phase=ConversationPhase(step_data["phase"]),
                    required_inputs=step_data["required_inputs"],
                    expected_outputs=step_data["expected_outputs"],
                    estimated_duration=step_data["estimated_duration"],
                    completion_criteria=step_data["completion_criteria"],
                    is_completed=step_data["is_completed"],
                    completion_timestamp=datetime.fromisoformat(step_data["completion_timestamp"]) if step_data["completion_timestamp"] else None
                )
                steps.append(step)
            
            current_workflow = ConversationWorkflow(
                workflow_id=workflow_data["workflow_id"],
                workflow_name=workflow_data["workflow_name"],
                creator_type=workflow_data["creator_type"],
                steps=steps,
                current_step_index=workflow_data["current_step_index"],
                started_at=datetime.fromisoformat(workflow_data["started_at"]),
                estimated_completion=datetime.fromisoformat(workflow_data["estimated_completion"]) if workflow_data["estimated_completion"] else None,
                actual_completion=datetime.fromisoformat(workflow_data["actual_completion"]) if workflow_data["actual_completion"] else None
            )
        
        state = ConversationState(
            conversation_id=data["conversation_id"],
            user_id=data["user_id"],
            session_id=data["session_id"],
            current_phase=ConversationPhase(data["current_phase"]),
            current_workflow=current_workflow,
            state_context=data["state_context"],
            phase_durations=data["phase_durations"],
            completed_workflows=data["completed_workflows"],
            pending_actions=data["pending_actions"],
            blocked_actions=data["blocked_actions"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_state_change=datetime.fromisoformat(data["last_state_change"]),
            phase_start_time=datetime.fromisoformat(data["phase_start_time"]),
            user_engagement_level=data["user_engagement_level"],
            conversation_momentum=data["conversation_momentum"],
            completion_likelihood=data["completion_likelihood"]
        )
        
        # Note: state_history is not fully restored to save space
        
        return state
