"""State Manager - Advanced Conversation State Management

Enterprise-grade state management system for complex conversation flows,
handling state persistence, transitions, rollbacks, and business workflow states
for multi-party creator collaborations and content monetization workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import deque, defaultdict

import aioredis
from transitions import Machine
from backend.core.database.session import DatabaseManager
from backend.services.ai.nlp_service import NLPService
from backend.services.notification.real_time_service import RealTimeNotificationService

logger = logging.getLogger(__name__)

class StateType(Enum):
    """
Types of conversation states"""

    CONVERSATIONAL = "conversational"  # Basic dialogue states
    BUSINESS_WORKFLOW = "business_workflow"  # Business process states
    COLLABORATION = "collaboration"  # Collaboration states
    CONTENT_PROCESSING = "content_processing"  # Content workflow states
    MONETIZATION = "monetization"  # Revenue workflow states
    PROTECTION = "protection"  # Content protection states
    NEGOTIATION = "negotiation"  # Business negotiation states
    SYSTEM = "system"  # System states

class StateCategory(Enum):
    """Categories for state organization"""

    ENTRY = "entry"
    ACTIVE = "active"
    TRANSITION = "transition"
    COMPLETION = "completion"
    ERROR = "error"
    ESCALATION = "escalation"

class StatePersistence(Enum):
    """State persistence levels"""

    TEMPORARY = "temporary"  # Session only
    SHORT_TERM = "short_term"  # Hours
    MEDIUM_TERM = "medium_term"  # Days
    LONG_TERM = "long_term"  # Weeks/Months
    PERMANENT = "permanent"  # Indefinite

@dataclass
class StateDefinition:
    """Definition of a conversation state"""
    state_id: str
    state_name: str
    state_type: StateType
    category: StateCategory
    persistence: StatePersistence
    
    # State properties
    description: str = ""
    is_terminal: bool = False
    requires_user_action: bool = False
    timeout_seconds: Optional[int] = None
    
    # Business context
    business_purpose: str = ""
    expected_outcomes: List[str] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    failure_conditions: List[str] = field(default_factory=list)
    
    # Workflow integration
    triggers_workflows: List[str] = field(default_factory=list)
    blocks_workflows: List[str] = field(default_factory=list)
    workflow_data: Dict[str, Any] = field(default_factory=dict)
    
    # Entry/Exit actions
    on_entry_actions: List[str] = field(default_factory=list)
    on_exit_actions: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)

@dataclass
class StateTransition:
    """Definition of state transition"""
    transition_id: str
    from_state: str
    to_state: str
    trigger: str
    
    # Transition conditions
    conditions: List[str] = field(default_factory=list)
    guard_functions: List[str] = field(default_factory=list)
    
    # Business rules
    business_rules: Dict[str, Any] = field(default_factory=dict)
    approval_required: bool = False
    cost_threshold: Optional[float] = None
    
    # Actions
    pre_actions: List[str] = field(default_factory=list)
    post_actions: List[str] = field(default_factory=list)
    
    # Metadata
    priority: int = 0
    is_automatic: bool = False
    rollback_supported: bool = True

@dataclass
class ConversationState:
    """
Current state of a conversation"""
    conversation_id: str
    current_state: str
    state_history: List[str] = field(default_factory=list)
    
    # State data
    state_data: Dict[str, Any] = field(default_factory=dict)
    workflow_states: Dict[str, str] = field(default_factory=dict)  # workflow_id -> state
    
    # Timing
    state_entered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_transition_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    state_duration: timedelta = field(default_factory=timedelta)
    
    # Business context
    business_context: Dict[str, Any] = field(default_factory=dict)
    pending_approvals: List[str] = field(default_factory=list)
    blocked_transitions: List[str] = field(default_factory=list)
    
    # Error handling
    error_count: int = 0
    last_error: Optional[str] = None
    rollback_points: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class StateSnapshot:
    """
Snapshot of conversation state for rollback"""
    snapshot_id: str
    conversation_id: str
    state_data: Dict[str, Any]
    timestamp: datetime
    trigger: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class StateMachine:
    """
State machine for individual conversation workflow"""
    
    def __init__(self, conversation_id: str, initial_state: str):
        self.conversation_id = conversation_id
        self.machine = Machine(
            model=self,
            states=[],
            initial=initial_state,
            auto_transitions=False,
            send_event=True
        )
        self.state_definitions: Dict[str, StateDefinition] = {}
        self.transition_definitions: Dict[str, StateTransition] = {}

class StateManager:
    """
    Enterprise state management system for IA Influencer conversations.
    
    Manages complex conversation states across multiple workflows including:
    - Multi-party collaboration states
    - Content processing workflows
    - Business negotiation states
    - Revenue optimization flows
    - Content protection states
    - Platform integration states
    
    Key features:
    - Hierarchical state management
    - State persistence with TTL
    - Rollback capabilities
    - Business rule enforcement
    - Workflow integration
    - Performance optimization
    """
    
    def __init__(
        self,
        redis_client: aioredis.Redis,
        database_manager: DatabaseManager,
        nlp_service: NLPService,
        notification_service: RealTimeNotificationService
    ):
        self.redis_client = redis_client
        self.database_manager = database_manager
        self.nlp_service = nlp_service
        self.notification_service = notification_service
        
        # State management
        self.state_definitions: Dict[str, StateDefinition] = {}
        self.transition_definitions: Dict[str, StateTransition] = {}
        self.active_states: Dict[str, ConversationState] = {}
        self.state_machines: Dict[str, StateMachine] = {}
        
        # Snapshots for rollback
        self.state_snapshots: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        
        # Performance tracking
        self.metrics = {
            'states_managed': 0,
            'transitions_executed': 0,
            'rollbacks_performed': 0,
            'average_state_duration': 0.0,
            'error_rate': 0.0
        }
        
        # Initialize state definitions
        self._initialize_state_definitions()
        self._initialize_transition_definitions()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_expired_states())
        asyncio.create_task(self._monitor_state_timeouts())
        
        logger.info("StateManager initialized for enterprise conversation management")

    def _initialize_state_definitions(self):
        """Initialize core state definitions for IA Influencer platform"""
        
        # Conversational states
        conversational_states = [
            StateDefinition(
                state_id="idle",
                state_name="Idle",
                state_type=StateType.CONVERSATIONAL,
                category=StateCategory.ENTRY,
                persistence=StatePersistence.TEMPORARY,
                description="Initial state waiting for user interaction",
                business_purpose="Entry point for all creator interactions",
                expected_outcomes=["user_engagement", "intent_identification"]
            ),
            StateDefinition(
                state_id="greeting",
                state_name="Greeting",
                state_type=StateType.CONVERSATIONAL,
                category=StateCategory.ACTIVE,
                persistence=StatePersistence.SHORT_TERM,
                description="Personalized greeting and initial assessment",
                business_purpose="Identify creator type and primary needs",
                requires_user_action=True,
                timeout_seconds=300,
                expected_outcomes=["creator_profile_identified", "workflow_direction_set"]
            ),
            StateDefinition(
                state_id="intent_analysis",
                state_name="Intent Analysis",
                state_type=StateType.CONVERSATIONAL,
                category=StateCategory.TRANSITION,
                persistence=StatePersistence.SHORT_TERM,
                description="Analyzing user intent and routing to appropriate workflow",
                business_purpose="Route creators to most valuable workflow",
                triggers_workflows=["business_intent_classification"],
                expected_outcomes=["workflow_routing", "business_context_establishment"]
            )
        ]
        
        # Business workflow states
        business_states = [
            StateDefinition(
                state_id="content_upload_init",
                state_name="Content Upload Initialization",
                state_type=StateType.BUSINESS_WORKFLOW,
                category=StateCategory.ACTIVE,
                persistence=StatePersistence.MEDIUM_TERM,
                description="Initiating secure content upload process",
                business_purpose="Begin content protection workflow",
                requires_user_action=True,
                timeout_seconds=600,
                triggers_workflows=["content_validation", "format_analysis"],
                expected_outcomes=["content_received", "metadata_extracted"]
            ),
            StateDefinition(
                state_id="collaboration_matching",
                state_name="Collaboration Matching",
                state_type=StateType.COLLABORATION,
                category=StateCategory.ACTIVE,
                persistence=StatePersistence.MEDIUM_TERM,
                description="Finding and matching potential collaborators",
                business_purpose="Connect creators for mutual benefit",
                triggers_workflows=["profile_analysis", "compatibility_scoring"],
                expected_outcomes=["matches_found", "collaboration_opportunities"]
            ),
            StateDefinition(
                state_id="revenue_optimization",
                state_name="Revenue Optimization",
                state_type=StateType.MONETIZATION,
                category=StateCategory.ACTIVE,
                persistence=StatePersistence.LONG_TERM,
                description="Analyzing and optimizing revenue streams",
                business_purpose="Maximize creator earnings",
                triggers_workflows=["revenue_analysis", "pricing_optimization"],
                expected_outcomes=["revenue_strategy", "monetization_setup"]
            )
        ]
        
        # Content processing states
        content_states = [
            StateDefinition(
                state_id="content_analysis",
                state_name="Content Analysis",
                state_type=StateType.CONTENT_PROCESSING,
                category=StateCategory.ACTIVE,
                persistence=StatePersistence.MEDIUM_TERM,
                description="AI-powered content analysis and fingerprinting",
                business_purpose="Prepare content for protection and distribution",
                triggers_workflows=["fingerprinting", "quality_analysis", "seo_optimization"],
                expected_outcomes=["content_fingerprinted", "quality_scored", "seo_optimized"]
            ),
            StateDefinition(
                state_id="protection_setup",
                state_name="Protection Setup",
                state_type=StateType.PROTECTION,
                category=StateCategory.ACTIVE,
                persistence=StatePersistence.LONG_TERM,
                description="Configuring content protection and monitoring",
                business_purpose="Secure creator intellectual property",
                triggers_workflows=["monitoring_setup", "alert_configuration"],
                expected_outcomes=["protection_active", "monitoring_enabled"]
            )
        ]
        
        # Negotiation and agreement states
        negotiation_states = [
            StateDefinition(
                state_id="revenue_negotiation",
                state_name="Revenue Negotiation",
                state_type=StateType.NEGOTIATION,
                category=StateCategory.ACTIVE,
                persistence=StatePersistence.MEDIUM_TERM,
                description="Negotiating revenue sharing terms",
                business_purpose="Establish fair revenue distribution",
                requires_user_action=True,
                timeout_seconds=1800,  # 30 minutes
                approval_required=True,
                expected_outcomes=["terms_agreed", "contract_generated"]
            ),
            StateDefinition(
                state_id="agreement_finalization",
                state_name="Agreement Finalization",
                state_type=StateType.NEGOTIATION,
                category=StateCategory.COMPLETION,
                persistence=StatePersistence.PERMANENT,
                description="Finalizing and executing agreements",
                business_purpose="Formalize collaboration agreements",
                triggers_workflows=["contract_creation", "payment_setup"],
                expected_outcomes=["agreement_signed", "collaboration_active"]
            )
        ]
        
        # System and error states
        system_states = [
            StateDefinition(
                state_id="processing_error",
                state_name="Processing Error",
                state_type=StateType.SYSTEM,
                category=StateCategory.ERROR,
                persistence=StatePersistence.SHORT_TERM,
                description="Handling processing errors",
                business_purpose="Recover from system errors gracefully",
                rollback_supported=True,
                on_entry_actions=["log_error", "notify_admin"],
                expected_outcomes=["error_resolved", "workflow_resumed"]
            ),
            StateDefinition(
                state_id="human_escalation",
                state_name="Human Escalation",
                state_type=StateType.SYSTEM,
                category=StateCategory.ESCALATION,
                persistence=StatePersistence.LONG_TERM,
                description="Escalated to human support",
                business_purpose="Ensure complex issues are resolved",
                requires_user_action=False,
                triggers_workflows=["support_ticket_creation"],
                expected_outcomes=["human_assistance", "issue_resolution"]
            )
        ]
        
        # Register all state definitions
        all_states = (conversational_states + business_states + 
                     content_states + negotiation_states + system_states)
        
        for state_def in all_states:
            self.state_definitions[state_def.state_id] = state_def
        
        logger.info(f"Initialized {len(all_states)} state definitions")

    def _initialize_transition_definitions(self):
        """Initialize state transition definitions"""
        
        transitions = [
            # Entry flow transitions
            StateTransition(
                transition_id="idle_to_greeting",
                from_state="idle",
                to_state="greeting",
                trigger="user_interaction",
                is_automatic=True,
                business_rules={"always_personalize": True}
            ),
            StateTransition(
                transition_id="greeting_to_intent_analysis",
                from_state="greeting",
                to_state="intent_analysis",
                trigger="greeting_complete",
                conditions=["has_user_response"],
                post_actions=["analyze_creator_profile"]
            ),
            
            # Business workflow transitions
            StateTransition(
                transition_id="intent_to_content_upload",
                from_state="intent_analysis",
                to_state="content_upload_init",
                trigger="content_upload_intent",
                conditions=["intent_confidence_high", "content_format_supported"],
                business_rules={"content_protection_required": True}
            ),
            StateTransition(
                transition_id="intent_to_collaboration",
                from_state="intent_analysis",
                to_state="collaboration_matching",
                trigger="collaboration_intent",
                conditions=["profile_complete", "collaboration_eligible"],
                business_rules={"minimum_content_threshold": True}
            ),
            StateTransition(
                transition_id="intent_to_monetization",
                from_state="intent_analysis",
                to_state="revenue_optimization",
                trigger="monetization_intent",
                conditions=["revenue_potential_exists"],
                business_rules={"minimum_audience_size": 1000}
            ),
            
            # Content processing flow
            StateTransition(
                transition_id="upload_to_analysis",
                from_state="content_upload_init",
                to_state="content_analysis",
                trigger="content_uploaded",
                conditions=["content_valid", "metadata_extracted"],
                post_actions=["start_fingerprinting"]
            ),
            StateTransition(
                transition_id="analysis_to_protection",
                from_state="content_analysis",
                to_state="protection_setup",
                trigger="analysis_complete",
                conditions=["fingerprint_created", "quality_acceptable"],
                business_rules={"auto_protection_enabled": True}
            ),
            
            # Collaboration flow
            StateTransition(
                transition_id="matching_to_negotiation",
                from_state="collaboration_matching",
                to_state="revenue_negotiation",
                trigger="match_found",
                conditions=["mutual_interest", "revenue_potential"],
                approval_required=True,
                business_rules={"minimum_match_score": 0.8}
            ),
            StateTransition(
                transition_id="negotiation_to_agreement",
                from_state="revenue_negotiation",
                to_state="agreement_finalization",
                trigger="terms_agreed",
                conditions=["all_parties_consent", "terms_valid"],
                approval_required=True,
                cost_threshold=10000.0  # Agreements over $10k need approval
            ),
            
            # Error handling transitions
            StateTransition(
                transition_id="any_to_error",
                from_state="*",  # From any state
                to_state="processing_error",
                trigger="system_error",
                is_automatic=True,
                rollback_supported=True,
                pre_actions=["create_rollback_point"]
            ),
            StateTransition(
                transition_id="error_to_escalation",
                from_state="processing_error",
                to_state="human_escalation",
                trigger="escalation_required",
                conditions=["retry_limit_reached", "high_priority_user"],
                post_actions=["create_support_ticket", "notify_support_team"]
            )
        ]
        
        # Register transition definitions
        for transition in transitions:
            self.transition_definitions[transition.transition_id] = transition
        
        logger.info(f"Initialized {len(transitions)} transition definitions")

    async def initialize_conversation_state(
        self,
        conversation_id: str,
        initial_state: str = "idle",
        business_context: Dict[str, Any] = None
    ) -> bool:
        """
        Initialize state management for new conversation
        
        Args:
            conversation_id: Conversation to initialize
            initial_state: Starting state
            business_context: Business context data
            
        Returns:
            Success status
        """
        
        # Validate initial state
        if initial_state not in self.state_definitions:
            logger.error(f"Invalid initial state: {initial_state}")
            return False
        
        # Create conversation state
        conv_state = ConversationState(
            conversation_id=conversation_id,
            current_state=initial_state,
            business_context=business_context or {}
        )
        
        # Create state machine
        state_machine = StateMachine(conversation_id, initial_state)
        
        # Add states to machine
        for state_id, state_def in self.state_definitions.items():
            state_machine.machine.add_state(
                state_id,
                on_enter=self._create_entry_callback(state_def),
                on_exit=self._create_exit_callback(state_def)
            )
        
        # Add transitions to machine
        for transition_id, transition_def in self.transition_definitions.items():
            if transition_def.from_state == "*":
                # Add transition from all states
                for state_id in self.state_definitions.keys():
                    if state_id != transition_def.to_state:
                        state_machine.machine.add_transition(
                            trigger=transition_def.trigger,
                            source=state_id,
                            dest=transition_def.to_state,
                            conditions=self._create_transition_conditions(transition_def),
                            before=self._create_pre_actions(transition_def),
                            after=self._create_post_actions(transition_def)
                        )
            else:
                state_machine.machine.add_transition(
                    trigger=transition_def.trigger,
                    source=transition_def.from_state,
                    dest=transition_def.to_state,
                    conditions=self._create_transition_conditions(transition_def),
                    before=self._create_pre_actions(transition_def),
                    after=self._create_post_actions(transition_def)
                )
        
        # Store state and machine
        self.active_states[conversation_id] = conv_state
        self.state_machines[conversation_id] = state_machine
        
        # Create initial snapshot
        await self._create_state_snapshot(conversation_id, "initialization")
        
        # Persist state
        await self._persist_conversation_state(conv_state)
        
        # Execute entry actions for initial state
        await self._execute_state_entry_actions(conversation_id, initial_state)
        
        # Update metrics
        self.metrics['states_managed'] += 1
        
        logger.info(f"Initialized state management for conversation {conversation_id} in state {initial_state}")
        return True

    async def transition_state(
        self,
        conversation_id: str,
        trigger: str,
        transition_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute state transition
        
        Args:
            conversation_id: Conversation to transition
            trigger: Transition trigger
            transition_data: Data for transition
            
        Returns:
            Transition result
        """
        
        conv_state = self.active_states.get(conversation_id)
        state_machine = self.state_machines.get(conversation_id)
        
        if not conv_state or not state_machine:
            return {"error": "Conversation state not found", "success": False}
        
        current_state = conv_state.current_state
        
        try:
            # Create snapshot before transition
            await self._create_state_snapshot(conversation_id, f"before_{trigger}")
            
            # Find applicable transition
            applicable_transition = self._find_applicable_transition(current_state, trigger)
            if not applicable_transition:
                return {"error": f"No valid transition from {current_state} with trigger {trigger}", "success": False}
            
            # Validate transition conditions
            validation_result = await self._validate_transition(
                conversation_id, applicable_transition, transition_data
            )
            if not validation_result["valid"]:
                return {"error": validation_result["reason"], "success": False}
            
            # Check if approval required
            if applicable_transition.approval_required:
                approval_result = await self._request_transition_approval(
                    conversation_id, applicable_transition, transition_data
                )
                if not approval_result["approved"]:
                    conv_state.pending_approvals.append(applicable_transition.transition_id)
                    await self._persist_conversation_state(conv_state)
                    return {
                        "success": True,
                        "status": "pending_approval",
                        "approval_id": approval_result["approval_id"]
                    }
            
            # Execute transition
            old_state = conv_state.current_state
            
            # Trigger state machine transition
            transition_success = getattr(state_machine, trigger)(transition_data or {})
            
            if transition_success:
                # Update conversation state
                new_state = state_machine.state
                conv_state.current_state = new_state
                conv_state.state_history.append(old_state)
                conv_state.last_transition_at = datetime.now(timezone.utc)
                conv_state.state_duration = conv_state.last_transition_at - conv_state.state_entered_at
                conv_state.state_entered_at = datetime.now(timezone.utc)
                
                # Update business context
                if transition_data and "business_context" in transition_data:
                    conv_state.business_context.update(transition_data["business_context"])
                
                # Execute workflow triggers
                await self._execute_workflow_triggers(conversation_id, new_state, transition_data)
                
                # Persist updated state
                await self._persist_conversation_state(conv_state)
                
                # Update metrics
                self.metrics['transitions_executed'] += 1
                
                # Send notifications
                await self._notify_state_transition(conversation_id, old_state, new_state, trigger)
                
                logger.info(f"Conversation {conversation_id} transitioned from {old_state} to {new_state} via {trigger}")
                
                return {
                    "success": True,
                    "old_state": old_state,
                    "new_state": new_state,
                    "trigger": trigger,
                    "transition_time": conv_state.last_transition_at.isoformat()
                }
            else:
                return {"error": "State machine transition failed", "success": False}
                
        except Exception as e:
            # Handle transition error
            conv_state.error_count += 1
            conv_state.last_error = str(e)
            await self._persist_conversation_state(conv_state)
            
            logger.error(f"Error executing transition {trigger} for conversation {conversation_id}: {str(e)}")
            
            # Attempt rollback if supported
            if applicable_transition and applicable_transition.rollback_supported:
                rollback_result = await self.rollback_state(conversation_id, f"error_recovery_{trigger}")
                return {
                    "error": str(e),
                    "success": False,
                    "rollback_performed": rollback_result["success"]
                }
            
            return {"error": str(e), "success": False}

    async def rollback_state(
        self,
        conversation_id: str,
        reason: str = "manual_rollback"
    ) -> Dict[str, Any]:
        """
        Rollback conversation state to previous snapshot
        
        Args:
            conversation_id: Conversation to rollback
            reason: Reason for rollback
            
        Returns:
            Rollback result
        """
        
        conv_state = self.active_states.get(conversation_id)
        if not conv_state:
            return {"error": "Conversation state not found", "success": False}
        
        # Get latest snapshot
        snapshots = self.state_snapshots.get(conversation_id)
        if not snapshots:
            return {"error": "No snapshots available for rollback", "success": False}
        
        try:
            # Get most recent snapshot
            latest_snapshot = snapshots[-1]
            
            # Restore state from snapshot
            conv_state.current_state = latest_snapshot.state_data["current_state"]
            conv_state.state_data = latest_snapshot.state_data.get("state_data", {})
            conv_state.business_context = latest_snapshot.state_data.get("business_context", {})
            conv_state.workflow_states = latest_snapshot.state_data.get("workflow_states", {})
            
            # Add rollback to history
            conv_state.state_history.append(f"ROLLBACK:{reason}")
            conv_state.last_transition_at = datetime.now(timezone.utc)
            conv_state.state_entered_at = datetime.now(timezone.utc)
            
            # Reset error state
            conv_state.error_count = 0
            conv_state.last_error = None
            
            # Update state machine
            state_machine = self.state_machines.get(conversation_id)
            if state_machine:
                state_machine.state = conv_state.current_state
            
            # Persist restored state
            await self._persist_conversation_state(conv_state)
            
            # Update metrics
            self.metrics['rollbacks_performed'] += 1
            
            # Notify rollback
            await self.notification_service.send_notification(
                user_id="system",
                notification_type="state_rollback",
                data={
                    "conversation_id": conversation_id,
                    "reason": reason,
                    "restored_state": conv_state.current_state,
                    "timestamp": latest_snapshot.timestamp.isoformat()
                }
            )
            
            logger.info(f"Rolled back conversation {conversation_id} to state {conv_state.current_state} (reason: {reason})")
            
            return {
                "success": True,
                "restored_state": conv_state.current_state,
                "rollback_reason": reason,
                "snapshot_timestamp": latest_snapshot.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error rolling back conversation {conversation_id}: {str(e)}")
            return {"error": str(e), "success": False}

    def _find_applicable_transition(self, current_state: str, trigger: str) -> Optional[StateTransition]:
        """Find applicable transition for current state and trigger"""
        
        for transition in self.transition_definitions.values():
            if (transition.from_state == current_state or transition.from_state == "*") and \
               transition.trigger == trigger:
                return transition
        
        return None

    async def _validate_transition(
        self,
        conversation_id: str,
        transition: StateTransition,
        transition_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Validate transition conditions and business rules"""
        
        conv_state = self.active_states[conversation_id]
        validation_errors = []
        
        # Check basic conditions
        for condition in transition.conditions:
            if not await self._evaluate_condition(conversation_id, condition, transition_data):
                validation_errors.append(f"Condition failed: {condition}")
        
        # Check business rules
        for rule_name, rule_value in transition.business_rules.items():
            if not await self._evaluate_business_rule(conversation_id, rule_name, rule_value, transition_data):
                validation_errors.append(f"Business rule failed: {rule_name}")
        
        # Check cost threshold
        if transition.cost_threshold:
            estimated_cost = transition_data.get("estimated_cost", 0) if transition_data else 0
            if estimated_cost > transition.cost_threshold:
                validation_errors.append(f"Cost threshold exceeded: {estimated_cost} > {transition.cost_threshold}")
        
        # Check blocked transitions
        if transition.transition_id in conv_state.blocked_transitions:
            validation_errors.append(f"Transition blocked: {transition.transition_id}")
        
        return {
            "valid": len(validation_errors) == 0,
            "reason": "; ".join(validation_errors) if validation_errors else None
        }

    async def _evaluate_condition(
        self,
        conversation_id: str,
        condition: str,
        transition_data: Dict[str, Any] = None
    ) -> bool:
        """Evaluate transition condition"""
        
        conv_state = self.active_states[conversation_id]
        
        # Standard conditions
        if condition == "has_user_response":
            return bool(transition_data and transition_data.get("user_message"))
        
        elif condition == "intent_confidence_high":
            confidence = transition_data.get("intent_confidence", 0) if transition_data else 0
            return confidence > 0.8
        
        elif condition == "content_format_supported":
            content_format = transition_data.get("content_format") if transition_data else None
            supported_formats = ["mp3", "wav", "mp4", "mov", "jpg", "png", "pdf", "txt"]
            return content_format in supported_formats
        
        elif condition == "profile_complete":
            return len(conv_state.business_context.get("creator_profile", {})) >= 3
        
        elif condition == "collaboration_eligible":
            return conv_state.business_context.get("content_count", 0) >= 1
        
        elif condition == "revenue_potential_exists":
            return conv_state.business_context.get("audience_size", 0) > 100
        
        elif condition == "content_valid":
            return transition_data.get("content_validation_passed", False) if transition_data else False
        
        elif condition == "metadata_extracted":
            return transition_data.get("metadata_extracted", False) if transition_data else False
        
        elif condition == "fingerprint_created":
            return transition_data.get("fingerprint_id") is not None if transition_data else False
        
        elif condition == "quality_acceptable":
            quality_score = transition_data.get("quality_score", 0) if transition_data else 0
            return quality_score >= 0.7
        
        elif condition == "mutual_interest":
            return transition_data.get("match_mutual", False) if transition_data else False
        
        elif condition == "all_parties_consent":
            return transition_data.get("all_consented", False) if transition_data else False
        
        elif condition == "terms_valid":
            return transition_data.get("terms_validated", False) if transition_data else False
        
        elif condition == "retry_limit_reached":
            return conv_state.error_count >= 3
        
        elif condition == "high_priority_user":
            return conv_state.business_context.get("user_tier") in ["premium", "enterprise"]
        
        # Default: unknown condition fails
        return False

    async def _evaluate_business_rule(
        self,
        conversation_id: str,
        rule_name: str,
        rule_value: Any,
        transition_data: Dict[str, Any] = None
    ) -> bool:
        """Evaluate business rule"""
        
        conv_state = self.active_states[conversation_id]
        
        if rule_name == "always_personalize":
            return True  # Always allow personalization
        
        elif rule_name == "content_protection_required":
            return rule_value  # Follow rule value
        
        elif rule_name == "minimum_content_threshold":
            content_count = conv_state.business_context.get("content_count", 0)
            return content_count >= 1
        
        elif rule_name == "minimum_audience_size":
            audience_size = conv_state.business_context.get("audience_size", 0)
            return audience_size >= rule_value
        
        elif rule_name == "auto_protection_enabled":
            return conv_state.business_context.get("auto_protection", True)
        
        elif rule_name == "minimum_match_score":
            match_score = transition_data.get("match_score", 0) if transition_data else 0
            return match_score >= rule_value
        
        # Default: unknown rule passes
        return True

    async def _request_transition_approval(
        self,
        conversation_id: str,
        transition: StateTransition,
        transition_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Request approval for transition requiring approval"""
        
        approval_id = str(uuid.uuid4())
        
        # Create approval request
        approval_request = {
            "approval_id": approval_id,
            "conversation_id": conversation_id,
            "transition_id": transition.transition_id,
            "from_state": transition.from_state,
            "to_state": transition.to_state,
            "trigger": transition.trigger,
            "transition_data": transition_data,
            "cost_estimate": transition_data.get("estimated_cost") if transition_data else None,
            "business_justification": transition_data.get("business_justification") if transition_data else None,
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending"
        }
        
        # Store approval request
        await self.redis_client.setex(
            f"approval_request:{approval_id}",
            timedelta(hours=24),  # 24 hour expiry
            json.dumps(approval_request, default=str)
        )
        
        # Notify approval team
        await self.notification_service.send_notification(
            user_id="approval_team",
            notification_type="transition_approval_required",
            data=approval_request
        )
        
        return {"approved": False, "approval_id": approval_id}

    def _create_entry_callback(self, state_def: StateDefinition):
        """Create callback for state entry"""
        
        async def on_entry_callback(event_data):
            conversation_id = event_data.model.conversation_id
            await self._execute_state_entry_actions(conversation_id, state_def.state_id)
        
        return on_entry_callback

    def _create_exit_callback(self, state_def: StateDefinition):
        """
Create callback for state exit"""
        
        async def on_exit_callback(event_data):
            conversation_id = event_data.model.conversation_id
            await self._execute_state_exit_actions(conversation_id, state_def.state_id)
        
        return on_exit_callback

    def _create_transition_conditions(self, transition_def: StateTransition):
        """
Create condition functions for transition"""
        
        async def check_conditions(event_data):
            conversation_id = event_data.model.conversation_id
            transition_data = event_data.kwargs
            
            validation_result = await self._validate_transition(
                conversation_id, transition_def, transition_data
            )
            return validation_result["valid"]
        
        return [check_conditions] if transition_def.conditions else []

    def _create_pre_actions(self, transition_def: StateTransition):
        """Create pre-action functions for transition"""
        
        async def execute_pre_actions(event_data):
            conversation_id = event_data.model.conversation_id
            for action in transition_def.pre_actions:
                await self._execute_transition_action(conversation_id, action, event_data.kwargs)
        
        return [execute_pre_actions] if transition_def.pre_actions else []

    def _create_post_actions(self, transition_def: StateTransition):
        """
Create post-action functions for transition"""
        
        async def execute_post_actions(event_data):
            conversation_id = event_data.model.conversation_id
            for action in transition_def.post_actions:
                await self._execute_transition_action(conversation_id, action, event_data.kwargs)
        
        return [execute_post_actions] if transition_def.post_actions else []

    async def _execute_state_entry_actions(self, conversation_id: str, state_id: str):
        """
Execute actions when entering state"""
        
        state_def = self.state_definitions.get(state_id)
        if not state_def:
            return
        
        for action in state_def.on_entry_actions:
            await self._execute_state_action(conversation_id, action, state_id)

    async def _execute_state_exit_actions(self, conversation_id: str, state_id: str):
        """
Execute actions when exiting state"""
        
        state_def = self.state_definitions.get(state_id)
        if not state_def:
            return
        
        for action in state_def.on_exit_actions:
            await self._execute_state_action(conversation_id, action, state_id)

    async def _execute_state_action(self, conversation_id: str, action: str, state_id: str):
        """
Execute individual state action"""
        
        try:
            if action == "log_error":
                logger.error(f"Conversation {conversation_id} entered error state {state_id}")
            
            elif action == "notify_admin":
                await self.notification_service.send_notification(
                    user_id="admin",
                    notification_type="state_action",
                    data={
                        "conversation_id": conversation_id,
                        "action": action,
                        "state": state_id
                    }
                )
            
            elif action == "create_rollback_point":
                await self._create_state_snapshot(conversation_id, f"rollback_point_{state_id}")
            
            elif action == "analyze_creator_profile":
                # Trigger creator profile analysis
                pass
            
            elif action == "start_fingerprinting":
                # Trigger content fingerprinting
                pass
            
        except Exception as e:
            logger.error(f"Error executing state action {action}: {str(e)}")

    async def _execute_transition_action(self, conversation_id: str, action: str, transition_data: Dict[str, Any]):
        """Execute individual transition action"""
        
        try:
            if action == "create_support_ticket":
                # Create support ticket for escalation
                pass
            
            elif action == "notify_support_team":
                await self.notification_service.send_notification(
                    user_id="support_team",
                    notification_type="transition_action",
                    data={
                        "conversation_id": conversation_id,
                        "action": action,
                        "transition_data": transition_data
                    }
                )
            
        except Exception as e:
            logger.error(f"Error executing transition action {action}: {str(e)}")

    async def _execute_workflow_triggers(self, conversation_id: str, new_state: str, transition_data: Dict[str, Any]):
        """Execute workflow triggers for new state"""
        
        state_def = self.state_definitions.get(new_state)
        if not state_def:
            return
        
        conv_state = self.active_states[conversation_id]
        
        for workflow in state_def.triggers_workflows:
            try:
                # Update workflow state
                conv_state.workflow_states[workflow] = "triggered"
                
                # Notify workflow service
                await self.notification_service.send_notification(
                    user_id="workflow_service",
                    notification_type="workflow_trigger",
                    data={
                        "conversation_id": conversation_id,
                        "workflow": workflow,
                        "trigger_state": new_state,
                        "transition_data": transition_data
                    }
                )
                
            except Exception as e:
                logger.error(f"Error triggering workflow {workflow}: {str(e)}")

    async def _notify_state_transition(self, conversation_id: str, old_state: str, new_state: str, trigger: str):
        """Send notification about state transition"""
        
        await self.notification_service.send_notification(
            user_id="system",
            notification_type="state_transition",
            data={
                "conversation_id": conversation_id,
                "old_state": old_state,
                "new_state": new_state,
                "trigger": trigger,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    async def _create_state_snapshot(self, conversation_id: str, trigger: str) -> str:
        """Create state snapshot for rollback"""
        
        conv_state = self.active_states.get(conversation_id)
        if not conv_state:
            return ""
        
        snapshot_id = str(uuid.uuid4())
        
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            conversation_id=conversation_id,
            state_data={
                "current_state": conv_state.current_state,
                "state_data": conv_state.state_data.copy(),
                "workflow_states": conv_state.workflow_states.copy(),
                "business_context": conv_state.business_context.copy()
            },
            timestamp=datetime.now(timezone.utc),
            trigger=trigger
        )
        
        # Add to snapshots deque
        self.state_snapshots[conversation_id].append(snapshot)
        
        # Persist snapshot
        await self.redis_client.setex(
            f"state_snapshot:{snapshot_id}",
            timedelta(days=7),  # 7 day expiry
            json.dumps({
                "snapshot_id": snapshot_id,
                "conversation_id": conversation_id,
                "state_data": snapshot.state_data,
                "timestamp": snapshot.timestamp.isoformat(),
                "trigger": trigger
            }, default=str)
        )
        
        return snapshot_id

    async def _persist_conversation_state(self, conv_state: ConversationState):
        """Persist conversation state to Redis"""
        
        try:
            state_data = {
                "conversation_id": conv_state.conversation_id,
                "current_state": conv_state.current_state,
                "state_history": conv_state.state_history[-50:],  # Keep last 50 states
                "state_data": conv_state.state_data,
                "workflow_states": conv_state.workflow_states,
                "state_entered_at": conv_state.state_entered_at.isoformat(),
                "last_transition_at": conv_state.last_transition_at.isoformat(),
                "business_context": conv_state.business_context,
                "pending_approvals": conv_state.pending_approvals,
                "blocked_transitions": conv_state.blocked_transitions,
                "error_count": conv_state.error_count,
                "last_error": conv_state.last_error
            }
            
            # Determine TTL based on state persistence level
            current_state_def = self.state_definitions.get(conv_state.current_state)
            if current_state_def:
                persistence_ttl = {
                    StatePersistence.TEMPORARY: timedelta(hours=1),
                    StatePersistence.SHORT_TERM: timedelta(hours=24),
                    StatePersistence.MEDIUM_TERM: timedelta(days=7),
                    StatePersistence.LONG_TERM: timedelta(days=30),
                    StatePersistence.PERMANENT: timedelta(days=365)
                }
                ttl = persistence_ttl.get(current_state_def.persistence, timedelta(days=1))
            else:
                ttl = timedelta(days=1)
            
            await self.redis_client.setex(
                f"conversation_state:{conv_state.conversation_id}",
                ttl,
                json.dumps(state_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Error persisting conversation state: {str(e)}")

    async def _cleanup_expired_states(self):
        """Background task to cleanup expired states"""
        
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                expired_conversations = []
                
                # Check for expired states
                for conversation_id, conv_state in list(self.active_states.items()):
                    state_def = self.state_definitions.get(conv_state.current_state)
                    if state_def and state_def.timeout_seconds:
                        state_age = (current_time - conv_state.state_entered_at).total_seconds()
                        if state_age > state_def.timeout_seconds:
                            expired_conversations.append(conversation_id)
                
                # Handle expired conversations
                for conversation_id in expired_conversations:
                    await self._handle_state_timeout(conversation_id)
                
                # Wait before next cleanup cycle
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in state cleanup: {str(e)}")
                await asyncio.sleep(600)  # Wait 10 minutes on error

    async def _monitor_state_timeouts(self):
        """Background task to monitor state timeouts"""
        
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                
                for conversation_id, conv_state in list(self.active_states.items()):
                    state_def = self.state_definitions.get(conv_state.current_state)
                    
                    if state_def and state_def.timeout_seconds:
                        state_age = (current_time - conv_state.state_entered_at).total_seconds()
                        
                        # Warning at 80% of timeout
                        warning_threshold = state_def.timeout_seconds * 0.8
                        if state_age >= warning_threshold and state_age < state_def.timeout_seconds:
                            await self._send_timeout_warning(conversation_id, state_def)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error monitoring timeouts: {str(e)}")
                await asyncio.sleep(300)

    async def _handle_state_timeout(self, conversation_id: str):
        """Handle state timeout"""
        
        conv_state = self.active_states.get(conversation_id)
        if not conv_state:
            return
        
        # Transition to appropriate timeout state
        timeout_transition = "timeout_occurred"
        
        try:
            await self.transition_state(
                conversation_id=conversation_id,
                trigger=timeout_transition,
                transition_data={"timeout_reason": "state_timeout"}
            )
        except Exception as e:
            logger.error(f"Error handling timeout for conversation {conversation_id}: {str(e)}")

    async def _send_timeout_warning(self, conversation_id: str, state_def: StateDefinition):
        """Send warning about approaching timeout"""
        
        await self.notification_service.send_notification(
            user_id="system",
            notification_type="state_timeout_warning",
            data={
                "conversation_id": conversation_id,
                "current_state": state_def.state_id,
                "timeout_seconds": state_def.timeout_seconds,
                "warning_message": f"State {state_def.state_name} approaching timeout"
            }
        )

    # Public API methods
    async def get_conversation_state(self, conversation_id: str) -> Dict[str, Any]:
        """Get current state of conversation"""
        
        conv_state = self.active_states.get(conversation_id)
        if not conv_state:
            return {"error": "Conversation state not found"}
        
        state_def = self.state_definitions.get(conv_state.current_state)
        
        return {
            "conversation_id": conversation_id,
            "current_state": conv_state.current_state,
            "state_name": state_def.state_name if state_def else "Unknown",
            "state_type": state_def.state_type.value if state_def else "unknown",
            "state_category": state_def.category.value if state_def else "unknown",
            "state_entered_at": conv_state.state_entered_at.isoformat(),
            "state_duration": (datetime.now(timezone.utc) - conv_state.state_entered_at).total_seconds(),
            "state_history": conv_state.state_history[-10:],  # Last 10 states
            "workflow_states": conv_state.workflow_states,
            "business_context": conv_state.business_context,
            "pending_approvals": conv_state.pending_approvals,
            "error_count": conv_state.error_count,
            "last_error": conv_state.last_error
        }

    async def get_available_transitions(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get available transitions from current state"""
        
        conv_state = self.active_states.get(conversation_id)
        if not conv_state:
            return []
        
        current_state = conv_state.current_state
        available_transitions = []
        
        for transition_id, transition_def in self.transition_definitions.items():
            if transition_def.from_state == current_state or transition_def.from_state == "*":
                # Check if transition is blocked
                if transition_id not in conv_state.blocked_transitions:
                    available_transitions.append({
                        "transition_id": transition_id,
                        "trigger": transition_def.trigger,
                        "to_state": transition_def.to_state,
                        "is_automatic": transition_def.is_automatic,
                        "approval_required": transition_def.approval_required,
                        "conditions": transition_def.conditions,
                        "business_rules": transition_def.business_rules
                    })
        
        return available_transitions

    async def block_transition(self, conversation_id: str, transition_id: str, reason: str) -> bool:
        """Block specific transition"""
        
        conv_state = self.active_states.get(conversation_id)
        if not conv_state:
            return False
        
        conv_state.blocked_transitions.append(transition_id)
        await self._persist_conversation_state(conv_state)
        
        logger.info(f"Blocked transition {transition_id} for conversation {conversation_id}: {reason}")
        return True

    async def unblock_transition(self, conversation_id: str, transition_id: str) -> bool:
        """Unblock specific transition"""
        
        conv_state = self.active_states.get(conversation_id)
        if not conv_state:
            return False
        
        if transition_id in conv_state.blocked_transitions:
            conv_state.blocked_transitions.remove(transition_id)
            await self._persist_conversation_state(conv_state)
            
            logger.info(f"Unblocked transition {transition_id} for conversation {conversation_id}")
            return True
        
        return False

    def get_state_metrics(self) -> Dict[str, Any]:
        """Get state management metrics"""
        
        return {
            "global_metrics": self.metrics,
            "active_conversations": len(self.active_states),
            "state_definitions": len(self.state_definitions),
            "transition_definitions": len(self.transition_definitions),
            "state_distribution": {
                state: len([conv for conv in self.active_states.values() if conv.current_state == state])
                for state in self.state_definitions.keys()
            },
            "workflow_distribution": {
                workflow: len([
                    conv for conv in self.active_states.values()
                    if workflow in conv.workflow_states
                ])
                for workflow in set().union(*[
                    conv.workflow_states.keys() for conv in self.active_states.values()
                ])
            }
        }
