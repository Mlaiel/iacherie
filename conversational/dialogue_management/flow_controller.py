"""Flow Controller - Advanced Dialogue Flow Control System

Enterprise-grade flow control system that orchestrates complex dialogue patterns,
manages dynamic routing, handles interruptions, and coordinates multi-workflow
execution for content creator business processes.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set, Tuple, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import deque, defaultdict
import heapq

import aioredis
import networkx as nx
from backend.core.database.session import DatabaseManager
from backend.services.ai.nlp_service import NLPService
from backend.services.notification.real_time_service import RealTimeNotificationService

from .dialogue_flow_manager import DialogueFlowManager, DialogueState, DialogueIntent
from .state_manager import StateManager
from .turn_manager import TurnManager

logger = logging.getLogger(__name__)

class FlowType(Enum):
    """Types of dialogue flows"""    LINEAR = "linear"  # Sequential steps
    BRANCHING = "branching"  # Multiple paths based on conditions
    PARALLEL = "parallel"  # Multiple flows simultaneously
    ITERATIVE = "iterative"  # Repeating cycles
    INTERRUPT_DRIVEN = "interrupt_driven"  # Reactive to interruptions
    BUSINESS_WORKFLOW = "business_workflow"  # Business process flows
    NEGOTIATION = "negotiation"  # Back-and-forth negotiation
    COLLABORATIVE = "collaborative"  # Multi-party collaboration

class FlowPriority(Enum):
    """Priority levels for flow execution"""    BACKGROUND = 1
    LOW = 2
    NORMAL = 3
    HIGH = 4
    URGENT = 5
    CRITICAL = 6

class FlowStatus(Enum):
    """Status of dialogue flows"""    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    INTERRUPTED = "interrupted"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class InterruptionType(Enum):
    """Types of flow interruptions"""    USER_INTERRUPT = "user_interrupt"
    SYSTEM_INTERRUPT = "system_interrupt"
    PRIORITY_OVERRIDE = "priority_override"
    ERROR_INTERRUPT = "error_interrupt"
    TIMEOUT_INTERRUPT = "timeout_interrupt"
    BUSINESS_INTERRUPT = "business_interrupt"
    COLLABORATION_INTERRUPT = "collaboration_interrupt"

@dataclass
class FlowNode:
    """Node in dialogue flow"""    node_id: str
    node_type: str  # start, end, action, decision, wait, parallel, join
    name: str
    description: str = ""
    
    # Node properties
    is_entry_point: bool = False
    is_exit_point: bool = False
    requires_user_input: bool = False
    timeout_seconds: Optional[int] = None
    
    # Business properties
    business_value: float = 0.0
    cost_estimate: float = 0.0
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    
    # Execution properties
    max_retries: int = 3
    retry_delay: int = 30  # seconds
    rollback_supported: bool = True
    
    # Actions
    on_enter_actions: List[str] = field(default_factory=list)
    on_exit_actions: List[str] = field(default_factory=list)
    
    # Conditions for execution
    execution_conditions: List[str] = field(default_factory=list)
    skip_conditions: List[str] = field(default_factory=list)

@dataclass
class FlowEdge:
    """Edge connecting flow nodes"""    edge_id: str
    from_node: str
    to_node: str
    condition: str = ""
    
    # Edge properties
    weight: float = 1.0
    probability: float = 1.0
    is_default: bool = False
    
    # Business rules
    business_condition: str = ""
    approval_required: bool = False
    cost_threshold: Optional[float] = None
    
    # Execution rules
    guard_functions: List[str] = field(default_factory=list)
    transformation_actions: List[str] = field(default_factory=list)

@dataclass
class FlowDefinition:
    """Definition of a dialogue flow"""    flow_id: str
    flow_name: str
    flow_type: FlowType
    description: str
    
    # Flow properties
    is_interruptible: bool = True
    is_resumable: bool = True
    max_execution_time: Optional[int] = None  # seconds
    max_parallel_instances: int = 1
    
    # Business properties
    business_category: str = ""
    expected_roi: Optional[float] = None
    target_completion_time: Optional[int] = None
    
    # Flow structure
    nodes: Dict[str, FlowNode] = field(default_factory=dict)
    edges: List[FlowEdge] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    exit_points: List[str] = field(default_factory=list)
    
    # Metadata
    version: str = "1.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = field(default_factory=list)

@dataclass
class FlowExecution:
    """Runtime execution of a dialogue flow"""    execution_id: str
    flow_id: str
    conversation_id: str
    status: FlowStatus
    priority: FlowPriority = FlowPriority.NORMAL
    
    # Execution state
    current_node: Optional[str] = None
    visited_nodes: List[str] = field(default_factory=list)
    execution_path: List[str] = field(default_factory=list)
    
    # Timing
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    # Execution data
    flow_data: Dict[str, Any] = field(default_factory=dict)
    node_results: Dict[str, Any] = field(default_factory=dict)
    error_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # Interruption handling
    interruptions: List[Dict[str, Any]] = field(default_factory=list)
    can_be_interrupted: bool = True
    interrupt_recovery_point: Optional[str] = None
    
    # Performance metrics
    execution_time: Optional[float] = None
    node_execution_times: Dict[str, float] = field(default_factory=dict)
    retry_count: int = 0
    
    # Business metrics
    business_value_generated: float = 0.0
    cost_incurred: float = 0.0
    success_score: float = 0.0

@dataclass
class FlowInterruption:
    """Interruption in flow execution"""    interrupt_id: str
    execution_id: str
    interrupt_type: InterruptionType
    interrupt_reason: str
    
    # Interruption context
    interrupted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    interrupted_node: Optional[str] = None
    interrupt_data: Dict[str, Any] = field(default_factory=dict)
    
    # Recovery information
    recovery_strategy: str = "resume"  # resume, restart, skip, escalate
    recovery_node: Optional[str] = None
    recovery_data: Dict[str, Any] = field(default_factory=dict)
    
    # Resolution
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_action: Optional[str] = None

class FlowController:
    """    Enterprise flow control system for IA Influencer dialogue management.
    
    Orchestrates complex dialogue flows for content creator business workflows,
    handling dynamic routing, interruptions, parallel execution, and business
    process integration.
    
    Key capabilities:
    - Multi-flow parallel execution
    - Dynamic flow routing based on business logic
    - Intelligent interruption handling
    - Business workflow integration
    - Performance optimization
    - Error recovery and rollback
    - Real-time flow monitoring
    """    
    def __init__(
        self,
        dialogue_manager: DialogueFlowManager,
        state_manager: StateManager,
        turn_manager: TurnManager,
        redis_client: aioredis.Redis,
        database_manager: DatabaseManager,
        nlp_service: NLPService,
        notification_service: RealTimeNotificationService
    ):
        self.dialogue_manager = dialogue_manager
        self.state_manager = state_manager
        self.turn_manager = turn_manager
        self.redis_client = redis_client
        self.database_manager = database_manager
        self.nlp_service = nlp_service
        self.notification_service = notification_service
        
        # Flow management
        self.flow_definitions: Dict[str, FlowDefinition] = {}
        self.active_executions: Dict[str, FlowExecution] = {}
        self.execution_queue: List[Tuple[int, str]] = []  # Priority queue
        self.interrupted_executions: Dict[str, FlowInterruption] = {}
        
        # Flow execution control
        self.max_concurrent_executions = 50
        self.execution_semaphore = asyncio.Semaphore(self.max_concurrent_executions)
        self.flow_processors: Dict[str, Callable] = {}
        
        # Business flow routing
        self.business_flow_map = {
            DialogueIntent.CONTENT_PROTECTION: "content_protection_flow",
            DialogueIntent.COLLABORATION_SEEKING: "collaboration_matching_flow",
            DialogueIntent.CONTENT_MONETIZATION: "monetization_optimization_flow",
            DialogueIntent.SEO_ENHANCEMENT: "seo_optimization_flow",
            DialogueIntent.SPOTIFY_INTEGRATION: "platform_integration_flow",
            DialogueIntent.TECHNICAL_ISSUE: "technical_support_flow"
        }
        
        # Performance metrics
        self.metrics = {
            'flows_executed': 0,
            'flows_completed': 0,
            'flows_failed': 0,
            'interruptions_handled': 0,
            'average_execution_time': 0.0,
            'business_value_generated': 0.0,
            'user_satisfaction_score': 0.0
        }
        
        # Initialize flow definitions
        self._initialize_business_flows()
        self._initialize_flow_processors()
        
        # Start background tasks
        asyncio.create_task(self._process_execution_queue())
        asyncio.create_task(self._monitor_flow_timeouts())
        asyncio.create_task(self._handle_interrupted_flows())
        
        logger.info("FlowController initialized for enterprise dialogue management")

    def _initialize_business_flows(self):
        """Initialize business workflow flow definitions"""        
        # Content Protection Flow
        content_protection_flow = FlowDefinition(
            flow_id="content_protection_flow",
            flow_name="Content Protection Workflow",
            flow_type=FlowType.LINEAR,
            description="Complete content protection setup workflow",
            business_category="content_protection",
            expected_roi=500.0,  # Expected value in revenue protection
            target_completion_time=300,  # 5 minutes
            max_execution_time=600  # 10 minutes max
        )
        
        # Define nodes for content protection flow
        content_protection_nodes = {
            "start": FlowNode(
                node_id="start",
                node_type="start",
                name="Start Content Protection",
                is_entry_point=True,
                business_value=10.0,
                on_enter_actions=["log_workflow_start", "initialize_protection_context"]
            ),
            "content_analysis": FlowNode(
                node_id="content_analysis",
                node_type="action",
                name="Analyze Content",
                timeout_seconds=120,
                business_value=50.0,
                cost_estimate=2.0,
                success_criteria={"fingerprint_created": True, "metadata_extracted": True},
                on_enter_actions=["start_content_analysis"],
                execution_conditions=["content_uploaded", "format_supported"]
            ),
            "fingerprint_creation": FlowNode(
                node_id="fingerprint_creation",
                node_type="action",
                name="Create Digital Fingerprint",
                timeout_seconds=60,
                business_value=100.0,
                cost_estimate=5.0,
                success_criteria={"fingerprint_id": "not_null"},
                on_enter_actions=["create_fingerprint", "store_fingerprint"]
            ),
            "monitoring_setup": FlowNode(
                node_id="monitoring_setup",
                node_type="action",
                name="Setup Content Monitoring",
                business_value=150.0,
                cost_estimate=3.0,
                success_criteria={"monitoring_active": True},
                on_enter_actions=["configure_monitoring", "enable_alerts"]
            ),
            "protection_complete": FlowNode(
                node_id="protection_complete",
                node_type="end",
                name="Protection Setup Complete",
                is_exit_point=True,
                business_value=200.0,
                on_enter_actions=["notify_protection_active", "update_user_dashboard"]
            )
        }
        
        # Define edges for content protection flow
        content_protection_edges = [
            FlowEdge("start_to_analysis", "start", "content_analysis", "always"),
            FlowEdge("analysis_to_fingerprint", "content_analysis", "fingerprint_creation", "analysis_successful"),
            FlowEdge("fingerprint_to_monitoring", "fingerprint_creation", "monitoring_setup", "fingerprint_created"),
            FlowEdge("monitoring_to_complete", "monitoring_setup", "protection_complete", "monitoring_enabled")
        ]
        
        content_protection_flow.nodes = content_protection_nodes
        content_protection_flow.edges = content_protection_edges
        content_protection_flow.entry_points = ["start"]
        content_protection_flow.exit_points = ["protection_complete"]
        
        # Collaboration Matching Flow
        collaboration_flow = FlowDefinition(
            flow_id="collaboration_matching_flow",
            flow_name="Collaboration Matching Workflow",
            flow_type=FlowType.BRANCHING,
            description="Find and connect creators for collaboration",
            business_category="collaboration",
            expected_roi=1000.0,  # Expected collaboration value
            target_completion_time=600,  # 10 minutes
            is_interruptible=True,
            is_resumable=True
        )
        
        collaboration_nodes = {
            "start": FlowNode(
                node_id="start",
                node_type="start",
                name="Start Collaboration Matching",
                is_entry_point=True,
                on_enter_actions=["initialize_collaboration_context"]
            ),
            "profile_analysis": FlowNode(
                node_id="profile_analysis",
                node_type="action",
                name="Analyze Creator Profile",
                timeout_seconds=180,
                business_value=30.0,
                success_criteria={"profile_score": ">0.5"},
                on_enter_actions=["analyze_creator_profile", "extract_collaboration_preferences"]
            ),
            "match_search": FlowNode(
                node_id="match_search",
                node_type="action",
                name="Search for Matches",
                timeout_seconds=300,
                business_value=100.0,
                cost_estimate=10.0,
                success_criteria={"matches_found": ">0"},
                on_enter_actions=["search_compatible_creators", "score_matches"]
            ),
            "match_presentation": FlowNode(
                node_id="match_presentation",
                node_type="action",
                name="Present Matches",
                requires_user_input=True,
                timeout_seconds=600,
                business_value=50.0,
                on_enter_actions=["present_matches_to_user", "collect_preferences"]
            ),
            "connection_facilitation": FlowNode(
                node_id="connection_facilitation",
                node_type="action",
                name="Facilitate Connection",
                business_value=200.0,
                success_criteria={"connection_established": True},
                on_enter_actions=["create_collaboration_room", "send_connection_invites"]
            ),
            "no_matches_found": FlowNode(
                node_id="no_matches_found",
                node_type="end",
                name="No Suitable Matches",
                is_exit_point=True,
                on_enter_actions=["suggest_profile_improvements", "schedule_retry"]
            ),
            "collaboration_established": FlowNode(
                node_id="collaboration_established",
                node_type="end",
                name="Collaboration Established",
                is_exit_point=True,
                business_value=300.0,
                on_enter_actions=["track_collaboration_success", "setup_revenue_sharing"]
            )
        }
        
        collaboration_edges = [
            FlowEdge("start_to_profile", "start", "profile_analysis", "always"),
            FlowEdge("profile_to_search", "profile_analysis", "match_search", "profile_adequate"),
            FlowEdge("search_to_presentation", "match_search", "match_presentation", "matches_found"),
            FlowEdge("search_to_no_matches", "match_search", "no_matches_found", "no_matches"),
            FlowEdge("presentation_to_connection", "match_presentation", "connection_facilitation", "user_interested"),
            FlowEdge("connection_to_established", "connection_facilitation", "collaboration_established", "connection_successful")
        ]
        
        collaboration_flow.nodes = collaboration_nodes
        collaboration_flow.edges = collaboration_edges
        collaboration_flow.entry_points = ["start"]
        collaboration_flow.exit_points = ["no_matches_found", "collaboration_established"]
        
        # Monetization Optimization Flow
        monetization_flow = FlowDefinition(
            flow_id="monetization_optimization_flow",
            flow_name="Revenue Optimization Workflow",
            flow_type=FlowType.ITERATIVE,
            description="Optimize creator revenue streams",
            business_category="monetization",
            expected_roi=2000.0,  # Expected revenue increase
            target_completion_time=900,  # 15 minutes
            max_parallel_instances=3
        )
        
        monetization_nodes = {
            "start": FlowNode(
                node_id="start",
                node_type="start",
                name="Start Revenue Optimization",
                is_entry_point=True,
                on_enter_actions=["initialize_revenue_context"]
            ),
            "revenue_analysis": FlowNode(
                node_id="revenue_analysis",
                node_type="action",
                name="Analyze Current Revenue",
                timeout_seconds=240,
                business_value=50.0,
                cost_estimate=8.0,
                success_criteria={"baseline_established": True},
                on_enter_actions=["analyze_current_revenue", "identify_opportunities"]
            ),
            "strategy_generation": FlowNode(
                node_id="strategy_generation",
                node_type="action",
                name="Generate Optimization Strategy",
                timeout_seconds=180,
                business_value=100.0,
                success_criteria={"strategy_created": True, "roi_projected": True},
                on_enter_actions=["generate_optimization_strategies", "calculate_projections"]
            ),
            "implementation_planning": FlowNode(
                node_id="implementation_planning",
                node_type="action",
                name="Plan Implementation",
                requires_user_input=True,
                timeout_seconds=600,
                business_value=75.0,
                on_enter_actions=["present_strategies", "create_implementation_plan"]
            ),
            "optimization_implementation": FlowNode(
                node_id="optimization_implementation",
                node_type="action",
                name="Implement Optimizations",
                timeout_seconds=300,
                business_value=200.0,
                cost_estimate=20.0,
                success_criteria={"optimizations_active": True},
                on_enter_actions=["implement_optimizations", "configure_tracking"]
            ),
            "performance_monitoring": FlowNode(
                node_id="performance_monitoring",
                node_type="action",
                name="Monitor Performance",
                business_value=150.0,
                success_criteria={"tracking_active": True},
                on_enter_actions=["setup_performance_monitoring", "schedule_reviews"]
            ),
            "optimization_complete": FlowNode(
                node_id="optimization_complete",
                node_type="end",
                name="Optimization Complete",
                is_exit_point=True,
                business_value=250.0,
                on_enter_actions=["notify_optimization_complete", "schedule_follow_up"]
            )
        }
        
        monetization_edges = [
            FlowEdge("start_to_analysis", "start", "revenue_analysis", "always"),
            FlowEdge("analysis_to_strategy", "revenue_analysis", "strategy_generation", "analysis_complete"),
            FlowEdge("strategy_to_planning", "strategy_generation", "implementation_planning", "strategies_generated"),
            FlowEdge("planning_to_implementation", "implementation_planning", "optimization_implementation", "plan_approved"),
            FlowEdge("implementation_to_monitoring", "optimization_implementation", "performance_monitoring", "implementation_successful"),
            FlowEdge("monitoring_to_complete", "performance_monitoring", "optimization_complete", "monitoring_setup")
        ]
        
        monetization_flow.nodes = monetization_nodes
        monetization_flow.edges = monetization_edges
        monetization_flow.entry_points = ["start"]
        monetization_flow.exit_points = ["optimization_complete"]
        
        # Register all flows
        self.flow_definitions["content_protection_flow"] = content_protection_flow
        self.flow_definitions["collaboration_matching_flow"] = collaboration_flow
        self.flow_definitions["monetization_optimization_flow"] = monetization_flow
        
        # Create additional flows for other intents
        self._create_seo_optimization_flow()
        self._create_platform_integration_flow()
        self._create_technical_support_flow()
        
        logger.info(f"Initialized {len(self.flow_definitions)} business flow definitions")

    def _create_seo_optimization_flow(self):
        """Create SEO optimization flow"""        
        seo_flow = FlowDefinition(
            flow_id="seo_optimization_flow",
            flow_name="SEO Enhancement Workflow",
            flow_type=FlowType.LINEAR,
            description="Optimize content for search and discovery",
            business_category="seo",
            expected_roi=300.0,
            target_completion_time=420  # 7 minutes
        )
        
        # Add to flow definitions
        self.flow_definitions["seo_optimization_flow"] = seo_flow

    def _create_platform_integration_flow(self):
        """Create platform integration flow"""        
        platform_flow = FlowDefinition(
            flow_id="platform_integration_flow",
            flow_name="Platform Integration Workflow",
            flow_type=FlowType.PARALLEL,
            description="Integrate with multiple content platforms",
            business_category="platform_integration",
            expected_roi=800.0,
            target_completion_time=480  # 8 minutes
        )
        
        # Add to flow definitions
        self.flow_definitions["platform_integration_flow"] = platform_flow

    def _create_technical_support_flow(self):
        """Create technical support flow"""        
        support_flow = FlowDefinition(
            flow_id="technical_support_flow",
            flow_name="Technical Support Workflow",
            flow_type=FlowType.INTERRUPT_DRIVEN,
            description="Handle technical issues and support requests",
            business_category="support",
            expected_roi=0.0,  # Support flow, not revenue generating
            target_completion_time=600,  # 10 minutes
            is_interruptible=False  # Support flows should not be interrupted
        )
        
        # Add to flow definitions
        self.flow_definitions["technical_support_flow"] = support_flow

    def _initialize_flow_processors(self):
        """Initialize processors for different node types"""        
        self.flow_processors = {
            "start": self._process_start_node,
            "end": self._process_end_node,
            "action": self._process_action_node,
            "decision": self._process_decision_node,
            "wait": self._process_wait_node,
            "parallel": self._process_parallel_node,
            "join": self._process_join_node
        }

    async def start_flow(
        self,
        conversation_id: str,
        flow_id: str,
        initial_data: Dict[str, Any] = None,
        priority: FlowPriority = FlowPriority.NORMAL
    ) -> str:
        """        Start execution of a dialogue flow
        
        Args:
            conversation_id: Conversation to execute flow for
            flow_id: ID of flow to execute
            initial_data: Initial flow data
            priority: Execution priority
            
        Returns:
            Execution ID
        """        
        flow_def = self.flow_definitions.get(flow_id)
        if not flow_def:
            raise ValueError(f"Flow definition not found: {flow_id}")
        
        # Check max parallel instances
        active_instances = len([
            exec for exec in self.active_executions.values()
            if exec.flow_id == flow_id and exec.status == FlowStatus.ACTIVE
        ])
        
        if active_instances >= flow_def.max_parallel_instances:
            raise RuntimeError(f"Maximum parallel instances ({flow_def.max_parallel_instances}) reached for flow {flow_id}")
        
        # Create execution
        execution_id = str(uuid.uuid4())
        execution = FlowExecution(
            execution_id=execution_id,
            flow_id=flow_id,
            conversation_id=conversation_id,
            status=FlowStatus.INACTIVE,
            priority=priority,
            flow_data=initial_data or {}
        )
        
        # Set entry point
        if flow_def.entry_points:
            execution.current_node = flow_def.entry_points[0]
        
        # Store execution
        self.active_executions[execution_id] = execution
        
        # Add to execution queue
        heapq.heappush(self.execution_queue, (-priority.value, execution_id))
        
        # Persist execution
        await self._persist_flow_execution(execution)
        
        # Update metrics
        self.metrics['flows_executed'] += 1
        
        logger.info(f"Started flow {flow_id} for conversation {conversation_id} with execution {execution_id}")
        return execution_id

    async def start_flow_for_intent(
        self,
        conversation_id: str,
        intent: DialogueIntent,
        context_data: Dict[str, Any] = None,
        priority: FlowPriority = FlowPriority.NORMAL
    ) -> Optional[str]:
        """        Start appropriate flow for dialogue intent
        
        Args:
            conversation_id: Conversation to execute flow for
            intent: Dialogue intent to handle
            context_data: Context data from intent analysis
            priority: Execution priority
            
        Returns:
            Execution ID if flow started, None if no matching flow
        """        
        flow_id = self.business_flow_map.get(intent)
        if not flow_id:
            logger.warning(f"No flow mapped for intent: {intent}")
            return None
        
        try:
            execution_id = await self.start_flow(
                conversation_id=conversation_id,
                flow_id=flow_id,
                initial_data=context_data,
                priority=priority
            )
            
            logger.info(f"Started flow {flow_id} for intent {intent.value} in conversation {conversation_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Error starting flow for intent {intent.value}: {str(e)}")
            return None

    async def interrupt_flow(
        self,
        execution_id: str,
        interrupt_type: InterruptionType,
        interrupt_reason: str,
        interrupt_data: Dict[str, Any] = None
    ) -> bool:
        """        Interrupt flow execution
        
        Args:
            execution_id: Execution to interrupt
            interrupt_type: Type of interruption
            interrupt_reason: Reason for interruption
            interrupt_data: Additional interruption data
            
        Returns:
            Success status
        """        
        execution = self.active_executions.get(execution_id)
        if not execution:
            return False
        
        flow_def = self.flow_definitions.get(execution.flow_id)
        if not flow_def or not flow_def.is_interruptible:
            logger.warning(f"Flow {execution.flow_id} is not interruptible")
            return False
        
        if not execution.can_be_interrupted:
            logger.warning(f"Execution {execution_id} cannot be interrupted at current node")
            return False
        
        # Create interruption record
        interrupt_id = str(uuid.uuid4())
        interruption = FlowInterruption(
            interrupt_id=interrupt_id,
            execution_id=execution_id,
            interrupt_type=interrupt_type,
            interrupt_reason=interrupt_reason,
            interrupted_node=execution.current_node,
            interrupt_data=interrupt_data or {}
        )
        
        # Update execution status
        execution.status = FlowStatus.INTERRUPTED
        execution.interruptions.append({
            "interrupt_id": interrupt_id,
            "type": interrupt_type.value,
            "reason": interrupt_reason,
            "timestamp": interruption.interrupted_at.isoformat()
        })
        
        # Store interruption
        self.interrupted_executions[interrupt_id] = interruption
        
        # Persist changes
        await self._persist_flow_execution(execution)
        await self._persist_flow_interruption(interruption)
        
        # Update metrics
        self.metrics['interruptions_handled'] += 1
        
        # Notify about interruption
        await self.notification_service.send_notification(
            user_id="system",
            notification_type="flow_interrupted",
            data={
                "execution_id": execution_id,
                "flow_id": execution.flow_id,
                "conversation_id": execution.conversation_id,
                "interrupt_type": interrupt_type.value,
                "interrupt_reason": interrupt_reason
            }
        )
        
        logger.info(f"Interrupted flow execution {execution_id}: {interrupt_reason}")
        return True

    async def resume_flow(
        self,
        execution_id: str,
        resume_data: Dict[str, Any] = None
    ) -> bool:
        """        Resume interrupted flow execution
        
        Args:
            execution_id: Execution to resume
            resume_data: Data for resumption
            
        Returns:
            Success status
        """        
        execution = self.active_executions.get(execution_id)
        if not execution or execution.status != FlowStatus.INTERRUPTED:
            return False
        
        flow_def = self.flow_definitions.get(execution.flow_id)
        if not flow_def or not flow_def.is_resumable:
            logger.warning(f"Flow {execution.flow_id} is not resumable")
            return False
        
        # Find latest interruption
        latest_interruption = None
        for interruption in self.interrupted_executions.values():
            if (interruption.execution_id == execution_id and 
                not interruption.is_resolved and
                (latest_interruption is None or interruption.interrupted_at > latest_interruption.interrupted_at)):
                latest_interruption = interruption
        
        if not latest_interruption:
            logger.warning(f"No unresolved interruption found for execution {execution_id}")
            return False
        
        # Resume execution
        execution.status = FlowStatus.ACTIVE
        execution.last_activity = datetime.now(timezone.utc)
        
        # Apply resume data
        if resume_data:
            execution.flow_data.update(resume_data)
        
        # Resolve interruption
        latest_interruption.is_resolved = True
        latest_interruption.resolved_at = datetime.now(timezone.utc)
        latest_interruption.resolution_action = "resumed"
        
        # Add back to execution queue with higher priority
        heapq.heappush(self.execution_queue, (-execution.priority.value - 1, execution_id))
        
        # Persist changes
        await self._persist_flow_execution(execution)
        await self._persist_flow_interruption(latest_interruption)
        
        logger.info(f"Resumed flow execution {execution_id}")
        return True

    async def _process_execution_queue(self):
        """Background task to process flow execution queue"""        
        while True:
            try:
                if self.execution_queue:
                    # Get highest priority execution
                    _, execution_id = heapq.heappop(self.execution_queue)
                    
                    execution = self.active_executions.get(execution_id)
                    if execution and execution.status in [FlowStatus.INACTIVE, FlowStatus.ACTIVE]:
                        await self._execute_flow_step(execution)
                
                # Wait before processing next item
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in execution queue processing: {str(e)}")
                await asyncio.sleep(1)

    async def _execute_flow_step(self, execution: FlowExecution):
        """Execute single step of flow"""        
        async with self.execution_semaphore:
            try:
                flow_def = self.flow_definitions[execution.flow_id]
                current_node_id = execution.current_node
                
                if not current_node_id:
                    logger.error(f"No current node for execution {execution.execution_id}")
                    return
                
                current_node = flow_def.nodes.get(current_node_id)
                if not current_node:
                    logger.error(f"Node {current_node_id} not found in flow {execution.flow_id}")
                    return
                
                # Update execution status
                execution.status = FlowStatus.ACTIVE
                execution.last_activity = datetime.now(timezone.utc)
                
                # Check execution conditions
                if not await self._check_node_conditions(execution, current_node):
                    # Skip this node
                    next_node = await self._get_next_node(execution, current_node, "skip")
                    if next_node:
                        execution.current_node = next_node
                        heapq.heappush(self.execution_queue, (-execution.priority.value, execution.execution_id))
                    return
                
                # Execute node
                node_start_time = datetime.now(timezone.utc)
                
                # Process node based on type
                processor = self.flow_processors.get(current_node.node_type)
                if processor:
                    result = await processor(execution, current_node)
                else:
                    result = {"success": False, "error": f"No processor for node type {current_node.node_type}"}
                
                node_execution_time = (datetime.now(timezone.utc) - node_start_time).total_seconds()
                execution.node_execution_times[current_node_id] = node_execution_time
                
                # Store node result
                execution.node_results[current_node_id] = result
                execution.visited_nodes.append(current_node_id)
                execution.execution_path.append(current_node_id)
                
                # Update business metrics
                execution.business_value_generated += current_node.business_value
                execution.cost_incurred += current_node.cost_estimate
                
                # Determine next step
                if result.get("success", False):
                    if current_node.is_exit_point:
                        # Flow completed
                        await self._complete_flow_execution(execution)
                    else:
                        # Move to next node
                        next_node = await self._get_next_node(execution, current_node, "success")
                        if next_node:
                            execution.current_node = next_node
                            
                            # Schedule next step
                            if current_node.node_type != "wait":  # Don't immediately reschedule wait nodes
                                heapq.heappush(self.execution_queue, (-execution.priority.value, execution.execution_id))
                        else:
                            # No next node, complete flow
                            await self._complete_flow_execution(execution)
                else:
                    # Node execution failed
                    await self._handle_node_failure(execution, current_node, result)
                
                # Persist execution state
                await self._persist_flow_execution(execution)
                
            except Exception as e:
                logger.error(f"Error executing flow step for {execution.execution_id}: {str(e)}")
                await self._handle_execution_error(execution, str(e))

    async def _check_node_conditions(self, execution: FlowExecution, node: FlowNode) -> bool:
        """Check if node execution conditions are met"""        
        for condition in node.execution_conditions:
            if not await self._evaluate_flow_condition(execution, condition):
                return False
        
        # Check skip conditions
        for condition in node.skip_conditions:
            if await self._evaluate_flow_condition(execution, condition):
                return False
        
        return True

    async def _evaluate_flow_condition(self, execution: FlowExecution, condition: str) -> bool:
        """Evaluate flow condition"""        
        flow_data = execution.flow_data
        
        # Content-related conditions
        if condition == "content_uploaded":
            return flow_data.get("content_uploaded", False)
        
        elif condition == "format_supported":
            content_format = flow_data.get("content_format")
            supported_formats = ["mp3", "wav", "mp4", "mov", "jpg", "png", "pdf", "txt"]
            return content_format in supported_formats
        
        elif condition == "analysis_complete":
            return flow_data.get("analysis_status") == "complete"
        
        elif condition == "fingerprint_created":
            return flow_data.get("fingerprint_id") is not None
        
        elif condition == "monitoring_enabled":
            return flow_data.get("monitoring_active", False)
        
        # Collaboration conditions
        elif condition == "profile_adequate":
            profile_score = flow_data.get("profile_score", 0.0)
            return profile_score >= 0.5
        
        elif condition == "matches_found":
            matches = flow_data.get("potential_matches", [])
            return len(matches) > 0
        
        elif condition == "no_matches":
            matches = flow_data.get("potential_matches", [])
            return len(matches) == 0
        
        elif condition == "user_interested":
            return flow_data.get("user_interest_confirmed", False)
        
        elif condition == "connection_successful":
            return flow_data.get("connection_established", False)
        
        # Monetization conditions
        elif condition == "analysis_complete":
            return flow_data.get("revenue_analysis_complete", False)
        
        elif condition == "strategies_generated":
            strategies = flow_data.get("optimization_strategies", [])
            return len(strategies) > 0
        
        elif condition == "plan_approved":
            return flow_data.get("implementation_plan_approved", False)
        
        elif condition == "implementation_successful":
            return flow_data.get("optimizations_implemented", False)
        
        elif condition == "monitoring_setup":
            return flow_data.get("performance_monitoring_active", False)
        
        # Default conditions
        elif condition == "always":
            return True
        
        elif condition == "never":
            return False
        
        # Unknown condition defaults to False
        return False

    async def _get_next_node(self, execution: FlowExecution, current_node: FlowNode, result_type: str) -> Optional[str]:
        """Get next node in flow based on current node and result"""        
        flow_def = self.flow_definitions[execution.flow_id]
        
        # Find outgoing edges from current node
        for edge in flow_def.edges:
            if edge.from_node == current_node.node_id:
                # Check edge condition
                if await self._evaluate_flow_condition(execution, edge.condition):
                    return edge.to_node
                elif edge.is_default and result_type == "success":
                    return edge.to_node
        
        return None

    # Node processors
    async def _process_start_node(self, execution: FlowExecution, node: FlowNode) -> Dict[str, Any]:
        """Process start node"""        
        # Execute entry actions
        for action in node.on_enter_actions:
            await self._execute_node_action(execution, action, node)
        
        return {"success": True, "message": f"Started flow {execution.flow_id}"}

    async def _process_end_node(self, execution: FlowExecution, node: FlowNode) -> Dict[str, Any]:
        """Process end node"""        
        # Execute entry actions
        for action in node.on_enter_actions:
            await self._execute_node_action(execution, action, node)
        
        return {"success": True, "message": f"Completed flow {execution.flow_id}"}

    async def _process_action_node(self, execution: FlowExecution, node: FlowNode) -> Dict[str, Any]:
        """Process action node"""        
        try:
            # Execute entry actions
            for action in node.on_enter_actions:
                await self._execute_node_action(execution, action, node)
            
            # Simulate action execution (in real implementation, would call actual services)
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Check success criteria
            success = True
            for criterion, expected_value in node.success_criteria.items():
                actual_value = execution.flow_data.get(criterion)
                
                if expected_value == "not_null":
                    if actual_value is None:
                        success = False
                        break
                elif expected_value == "true" or expected_value is True:
                    if not actual_value:
                        success = False
                        break
                elif isinstance(expected_value, str) and expected_value.startswith(">"):
                    threshold = float(expected_value[1:])
                    if not actual_value or actual_value <= threshold:
                        success = False
                        break
            
            if success:
                return {"success": True, "message": f"Action {node.name} completed successfully"}
            else:
                return {"success": False, "error": "Success criteria not met"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _process_decision_node(self, execution: FlowExecution, node: FlowNode) -> Dict[str, Any]:
        """Process decision node"""        
        # Decision nodes evaluate conditions and route accordingly
        return {"success": True, "message": f"Decision {node.name} evaluated"}

    async def _process_wait_node(self, execution: FlowExecution, node: FlowNode) -> Dict[str, Any]:
        """Process wait node"""        
        if node.requires_user_input:
            # Schedule timeout if specified
            if node.timeout_seconds:
                asyncio.create_task(self._schedule_wait_timeout(execution, node))
            
            # Wait for user input (in real implementation, would wait for actual input)
            execution.status = FlowStatus.PAUSED
            return {"success": True, "message": f"Waiting for user input at {node.name}"}
        else:
            # Simple wait
            if node.timeout_seconds:
                await asyncio.sleep(min(node.timeout_seconds, 5))  # Max 5 second wait for demo
            
            return {"success": True, "message": f"Wait {node.name} completed"}

    async def _process_parallel_node(self, execution: FlowExecution, node: FlowNode) -> Dict[str, Any]:
        """Process parallel node (splits flow into parallel branches)"""        
        # In real implementation, would create parallel executions
        return {"success": True, "message": f"Parallel {node.name} initiated"}

    async def _process_join_node(self, execution: FlowExecution, node: FlowNode) -> Dict[str, Any]:
        """Process join node (waits for parallel branches to complete)"""        
        # In real implementation, would wait for parallel executions
        return {"success": True, "message": f"Join {node.name} completed"}

    async def _execute_node_action(self, execution: FlowExecution, action: str, node: FlowNode):
        """Execute individual node action"""        
        try:
            if action == "log_workflow_start":
                logger.info(f"Started workflow {execution.flow_id} for conversation {execution.conversation_id}")
            
            elif action == "initialize_protection_context":
                execution.flow_data["protection_context"] = {
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "content_type": execution.flow_data.get("content_type", "unknown")
                }
            
            elif action == "start_content_analysis":
                # Simulate content analysis
                execution.flow_data["analysis_status"] = "complete"
                execution.flow_data["fingerprint_created"] = True
                execution.flow_data["metadata_extracted"] = True
            
            elif action == "create_fingerprint":
                execution.flow_data["fingerprint_id"] = str(uuid.uuid4())
            
            elif action == "configure_monitoring":
                execution.flow_data["monitoring_active"] = True
            
            elif action == "notify_protection_active":
                await self.notification_service.send_notification(
                    user_id=execution.conversation_id,
                    notification_type="protection_active",
                    data={"execution_id": execution.execution_id}
                )
            
            # Add more action implementations as needed
            
        except Exception as e:
            logger.error(f"Error executing node action {action}: {str(e)}")

    async def _complete_flow_execution(self, execution: FlowExecution):
        """Complete flow execution"""        
        execution.status = FlowStatus.COMPLETED
        execution.completed_at = datetime.now(timezone.utc)
        execution.execution_time = (execution.completed_at - execution.started_at).total_seconds()
        
        # Calculate success score
        execution.success_score = self._calculate_success_score(execution)
        
        # Update metrics
        self.metrics['flows_completed'] += 1
        self.metrics['business_value_generated'] += execution.business_value_generated
        
        # Update average execution time
        total_executions = self.metrics['flows_completed']
        current_avg = self.metrics['average_execution_time']
        self.metrics['average_execution_time'] = (
            (current_avg * (total_executions - 1) + execution.execution_time) / total_executions
        )
        
        # Notify completion
        await self.notification_service.send_notification(
            user_id=execution.conversation_id,
            notification_type="flow_completed",
            data={
                "execution_id": execution.execution_id,
                "flow_id": execution.flow_id,
                "execution_time": execution.execution_time,
                "business_value": execution.business_value_generated,
                "success_score": execution.success_score
            }
        )
        
        logger.info(f"Completed flow execution {execution.execution_id} in {execution.execution_time:.2f}s")

    def _calculate_success_score(self, execution: FlowExecution) -> float:
        """Calculate success score for flow execution"""        
        score = 0.0
        
        # Completion score
        if execution.status == FlowStatus.COMPLETED:
            score += 0.4
        
        # Time efficiency score
        flow_def = self.flow_definitions[execution.flow_id]
        if flow_def.target_completion_time and execution.execution_time:
            time_ratio = execution.execution_time / flow_def.target_completion_time
            if time_ratio <= 1.0:
                score += 0.3 * (1.0 - time_ratio)
        
        # Business value score
        if execution.business_value_generated > 0:
            score += min(execution.business_value_generated / 1000.0, 0.2)
        
        # Error-free execution score
        if execution.retry_count == 0:
            score += 0.1
        
        return min(score, 1.0)

    async def _handle_node_failure(self, execution: FlowExecution, node: FlowNode, result: Dict[str, Any]):
        """Handle node execution failure"""        
        execution.retry_count += 1
        execution.error_log.append({
            "node_id": node.node_id,
            "error": result.get("error", "Unknown error"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "retry_count": execution.retry_count
        })
        
        if execution.retry_count < node.max_retries:
            # Retry after delay
            await asyncio.sleep(node.retry_delay)
            heapq.heappush(self.execution_queue, (-execution.priority.value, execution.execution_id))
        else:
            # Max retries reached, fail execution
            execution.status = FlowStatus.FAILED
            self.metrics['flows_failed'] += 1
            
            logger.error(f"Flow execution {execution.execution_id} failed at node {node.node_id}")

    async def _handle_execution_error(self, execution: FlowExecution, error: str):
        """Handle general execution error"""        
        execution.status = FlowStatus.FAILED
        execution.error_log.append({
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": "execution_error"
        })
        
        self.metrics['flows_failed'] += 1
        
        # Attempt to trigger error interrupt for recovery
        await self.interrupt_flow(
            execution.execution_id,
            InterruptionType.ERROR_INTERRUPT,
            f"Execution error: {error}"
        )

    async def _schedule_wait_timeout(self, execution: FlowExecution, node: FlowNode):
        """Schedule timeout for wait node"""        
        await asyncio.sleep(node.timeout_seconds)
        
        # Check if still waiting
        if (execution.execution_id in self.active_executions and
            execution.current_node == node.node_id and
            execution.status == FlowStatus.PAUSED):
            
            # Trigger timeout interrupt
            await self.interrupt_flow(
                execution.execution_id,
                InterruptionType.TIMEOUT_INTERRUPT,
                f"Wait timeout at node {node.name}"
            )

    async def _monitor_flow_timeouts(self):
        """Background task to monitor flow timeouts"""        
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                
                for execution in list(self.active_executions.values()):
                    if execution.status not in [FlowStatus.ACTIVE, FlowStatus.PAUSED]:
                        continue
                    
                    flow_def = self.flow_definitions.get(execution.flow_id)
                    if not flow_def or not flow_def.max_execution_time:
                        continue
                    
                    execution_duration = (current_time - execution.started_at).total_seconds()
                    
                    if execution_duration > flow_def.max_execution_time:
                        await self.interrupt_flow(
                            execution.execution_id,
                            InterruptionType.TIMEOUT_INTERRUPT,
                            f"Flow execution timeout ({execution_duration}s > {flow_def.max_execution_time}s)"
                        )
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring flow timeouts: {str(e)}")
                await asyncio.sleep(60)

    async def _handle_interrupted_flows(self):
        """Background task to handle interrupted flows"""        
        while True:
            try:
                for interruption in list(self.interrupted_executions.values()):
                    if interruption.is_resolved:
                        continue
                    
                    # Check if interruption is stale (older than 1 hour)
                    if (datetime.now(timezone.utc) - interruption.interrupted_at).total_seconds() > 3600:
                        # Auto-resolve stale interruptions
                        interruption.is_resolved = True
                        interruption.resolved_at = datetime.now(timezone.utc)
                        interruption.resolution_action = "auto_resolved_stale"
                        
                        # Mark execution as failed
                        execution = self.active_executions.get(interruption.execution_id)
                        if execution:
                            execution.status = FlowStatus.FAILED
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error handling interrupted flows: {str(e)}")
                await asyncio.sleep(600)

    async def _persist_flow_execution(self, execution: FlowExecution):
        """Persist flow execution to Redis"""        
        try:
            execution_data = {
                "execution_id": execution.execution_id,
                "flow_id": execution.flow_id,
                "conversation_id": execution.conversation_id,
                "status": execution.status.value,
                "priority": execution.priority.value,
                "current_node": execution.current_node,
                "visited_nodes": execution.visited_nodes,
                "execution_path": execution.execution_path,
                "started_at": execution.started_at.isoformat(),
                "last_activity": execution.last_activity.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "flow_data": execution.flow_data,
                "node_results": execution.node_results,
                "execution_time": execution.execution_time,
                "node_execution_times": execution.node_execution_times,
                "retry_count": execution.retry_count,
                "business_value_generated": execution.business_value_generated,
                "cost_incurred": execution.cost_incurred,
                "success_score": execution.success_score,
                "error_log": execution.error_log[-10:]  # Keep last 10 errors
            }
            
            await self.redis_client.setex(
                f"flow_execution:{execution.execution_id}",
                timedelta(days=30),  # 30 day expiry
                json.dumps(execution_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Error persisting flow execution: {str(e)}")

    async def _persist_flow_interruption(self, interruption: FlowInterruption):
        """Persist flow interruption to Redis"""        
        try:
            interruption_data = {
                "interrupt_id": interruption.interrupt_id,
                "execution_id": interruption.execution_id,
                "interrupt_type": interruption.interrupt_type.value,
                "interrupt_reason": interruption.interrupt_reason,
                "interrupted_at": interruption.interrupted_at.isoformat(),
                "interrupted_node": interruption.interrupted_node,
                "interrupt_data": interruption.interrupt_data,
                "recovery_strategy": interruption.recovery_strategy,
                "recovery_node": interruption.recovery_node,
                "recovery_data": interruption.recovery_data,
                "is_resolved": interruption.is_resolved,
                "resolved_at": interruption.resolved_at.isoformat() if interruption.resolved_at else None,
                "resolution_action": interruption.resolution_action
            }
            
            await self.redis_client.setex(
                f"flow_interruption:{interruption.interrupt_id}",
                timedelta(days=7),  # 7 day expiry
                json.dumps(interruption_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Error persisting flow interruption: {str(e)}")

    # Public API methods
    async def get_flow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get status of flow execution"""        
        execution = self.active_executions.get(execution_id)
        if not execution:
            return {"error": "Execution not found"}
        
        flow_def = self.flow_definitions.get(execution.flow_id)
        current_node = flow_def.nodes.get(execution.current_node) if flow_def else None
        
        return {
            "execution_id": execution_id,
            "flow_id": execution.flow_id,
            "flow_name": flow_def.flow_name if flow_def else "Unknown",
            "conversation_id": execution.conversation_id,
            "status": execution.status.value,
            "priority": execution.priority.value,
            "current_node": execution.current_node,
            "current_node_name": current_node.name if current_node else "Unknown",
            "progress": {
                "visited_nodes": len(execution.visited_nodes),
                "total_nodes": len(flow_def.nodes) if flow_def else 0,
                "completion_percentage": (len(execution.visited_nodes) / len(flow_def.nodes) * 100) if flow_def and flow_def.nodes else 0
            },
            "timing": {
                "started_at": execution.started_at.isoformat(),
                "last_activity": execution.last_activity.isoformat(),
                "execution_time": (datetime.now(timezone.utc) - execution.started_at).total_seconds(),
                "estimated_remaining": None  # Could calculate based on flow definition
            },
            "business_metrics": {
                "value_generated": execution.business_value_generated,
                "cost_incurred": execution.cost_incurred,
                "success_score": execution.success_score
            },
            "interruptions": len(execution.interruptions),
            "errors": len(execution.error_log)
        }

    async def get_conversation_flows(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all flows for conversation"""        
        conversation_flows = []
        
        for execution in self.active_executions.values():
            if execution.conversation_id == conversation_id:
                flow_status = await self.get_flow_status(execution.execution_id)
                conversation_flows.append(flow_status)
        
        return conversation_flows

    async def cancel_flow(self, execution_id: str, reason: str = "user_cancelled") -> bool:
        """Cancel flow execution"""        
        execution = self.active_executions.get(execution_id)
        if not execution:
            return False
        
        execution.status = FlowStatus.CANCELLED
        execution.completed_at = datetime.now(timezone.utc)
        execution.error_log.append({
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": "cancellation"
        })
        
        await self._persist_flow_execution(execution)
        
        logger.info(f"Cancelled flow execution {execution_id}: {reason}")
        return True

    def get_flow_metrics(self) -> Dict[str, Any]:
        """Get flow controller metrics"""        
        return {
            "global_metrics": self.metrics,
            "active_executions": len(self.active_executions),
            "queued_executions": len(self.execution_queue),
            "interrupted_executions": len([i for i in self.interrupted_executions.values() if not i.is_resolved]),
            "flow_definitions": len(self.flow_definitions),
            "execution_distribution": {
                status.value: len([e for e in self.active_executions.values() if e.status == status])
                for status in FlowStatus
            },
            "flow_usage": {
                flow_id: len([e for e in self.active_executions.values() if e.flow_id == flow_id])
                for flow_id in self.flow_definitions.keys()
            }
        }


# Additional Enterprise Classes Required by __init__.py

@dataclass
class FlowExecutionStatus:
    """Detailed flow execution status"""    execution_id: str
    status: FlowStatus
    current_node: Optional[str] = None
    progress_percentage: float = 0.0
    estimated_completion: Optional[datetime] = None
    error_count: int = 0
    warning_count: int = 0
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class FlowInterruption:
    """Flow interruption details"""    interruption_id: str
    execution_id: str
    interruption_type: InterruptionType
    source: str  # user, system, external
    reason: str
    
    # Interruption context
    interrupted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    current_node: Optional[str] = None
    user_context: Dict[str, Any] = field(default_factory=dict)
    system_context: Dict[str, Any] = field(default_factory=dict)
    
    # Recovery information
    recovery_strategy: Optional[str] = None
    resume_node: Optional[str] = None
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_action: Optional[str] = None

@dataclass
class FlowResumption:
    """Flow resumption configuration"""    resumption_id: str
    interruption_id: str
    execution_id: str
    
    # Resume strategy
    resume_strategy: str  # continue, restart, alternative_path
    resume_node: str
    context_restoration: Dict[str, Any] = field(default_factory=dict)
    
    # Validation
    prerequisites: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    
    # Timing
    scheduled_resume: Optional[datetime] = None
    resume_timeout: Optional[int] = None
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ConditionalFlow:
    """Conditional flow execution based on business rules"""    condition_id: str
    flow_id: str
    condition_expression: str
    condition_type: str  # business_rule, user_attribute, system_state, time_based
    
    # Condition evaluation
    evaluation_context: Dict[str, Any] = field(default_factory=dict)
    evaluation_frequency: str = "on_demand"  # on_demand, periodic, event_driven
    last_evaluation: Optional[datetime] = None
    evaluation_result: Optional[bool] = None
    
    # Flow execution
    execution_priority: FlowPriority = FlowPriority.NORMAL
    execution_parameters: Dict[str, Any] = field(default_factory=dict)
    alternative_flows: List[str] = field(default_factory=list)
    
    # Business context
    business_impact: float = 0.0
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ParallelFlow:
    """Parallel flow execution management"""    parallel_id: str
    main_flow_id: str
    parallel_flows: List[str] = field(default_factory=list)
    
    # Execution strategy
    execution_strategy: str = "concurrent"  # concurrent, sequential, conditional
    synchronization_points: List[str] = field(default_factory=list)
    merge_strategy: str = "wait_all"  # wait_all, wait_any, best_result
    
    # Resource management
    max_concurrent: int = 5
    resource_constraints: Dict[str, Any] = field(default_factory=dict)
    load_balancing: bool = True
    
    # Progress tracking
    flow_progress: Dict[str, float] = field(default_factory=dict)
    completion_status: Dict[str, str] = field(default_factory=dict)
    execution_results: Dict[str, Any] = field(default_factory=dict)
    
    # Performance
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class FlowValidation:
    """Flow validation and quality assurance"""    validation_id: str
    flow_id: str
    validation_type: str  # structural, business_logic, performance, security
    
    # Validation rules
    validation_rules: List[str] = field(default_factory=list)
    business_constraints: Dict[str, Any] = field(default_factory=dict)
    performance_requirements: Dict[str, float] = field(default_factory=dict)
    
    # Validation results
    is_valid: bool = False
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    validation_score: float = 0.0
    
    # Recommendations
    improvement_suggestions: List[str] = field(default_factory=list)
    optimization_opportunities: List[str] = field(default_factory=list)
    
    validation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class FlowOptimization:
    """Flow optimization analysis and recommendations"""    optimization_id: str
    flow_id: str
    optimization_type: str  # performance, cost, user_experience, business_value
    
    # Current metrics
    current_performance: Dict[str, float] = field(default_factory=dict)
    performance_baseline: Dict[str, float] = field(default_factory=dict)
    bottlenecks: List[str] = field(default_factory=list)
    
    # Optimization recommendations
    recommendations: List[str] = field(default_factory=list)
    expected_improvements: Dict[str, float] = field(default_factory=dict)
    implementation_effort: str = "low"  # low, medium, high
    business_impact: str = "medium"  # low, medium, high
    
    # A/B testing
    test_variants: List[str] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)
    winning_variant: Optional[str] = None
    
    optimization_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# Export all classes
__all__ = [
    "FlowController",
    "FlowType",
    "FlowPriority", 
    "FlowStatus",
    "InterruptionType",
    "FlowNode",
    "FlowEdge",
    "FlowExecution",
    "FlowDefinition",
    "FlowInterruption",
    "FlowResumption",
    "ConditionalFlow",
    "ParallelFlow",
    "FlowValidation",
    "FlowOptimization",
    "FlowExecutionStatus"
]
