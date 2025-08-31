"""
IA-Influencer Agent - Agent Coordinator

Advanced multi-agent coordination system for intelligent orchestration of
specialized AI agents in content creation and protection workflows.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: 2025 - All rights reserved

⚠️ IMPORTANT LEGAL NOTICE ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.

Expert Team Specializations:
- Lead AI Developer: Fahed Mlaiel
- Multi-Agent Systems Expert
- Distributed Computing Specialist
- Workflow Orchestration Engineer
- Performance Optimization Expert
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict, deque
import statistics
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...utils.metrics_collector import MetricsCollector
from ..base import BaseAgent


class AgentType(Enum):
    """Types of agents in the system."""
    AUDIO_AGENT = "audio_agent"
    VIDEO_AGENT = "video_agent"
    IMAGE_AGENT = "image_agent"
    TEXT_AGENT = "text_agent"
    MUSIC_AGENT = "music_agent"
    SOCIAL_MEDIA_AGENT = "social_media_agent"
    ANALYTICS_AGENT = "analytics_agent"
    PROTECTION_AGENT = "protection_agent"
    MONETIZATION_AGENT = "monetization_agent"
    COLLABORATION_AGENT = "collaboration_agent"
    SEO_AGENT = "seo_agent"
    TREND_AGENT = "trend_agent"
    NOTIFICATION_AGENT = "notification_agent"
    QUALITY_AGENT = "quality_agent"
    WORKFLOW_AGENT = "workflow_agent"


class AgentCapability(Enum):
    """Capabilities that agents can provide."""
    CONTENT_ANALYSIS = "content_analysis"
    CONTENT_GENERATION = "content_generation"
    CONTENT_OPTIMIZATION = "content_optimization"
    FINGERPRINTING = "fingerprinting"
    MONITORING = "monitoring"
    RECOMMENDATION = "recommendation"
    TRANSLATION = "translation"
    TREND_ANALYSIS = "trend_analysis"
    AUDIENCE_ANALYSIS = "audience_analysis"
    MONETIZATION = "monetization"
    COLLABORATION_MATCHING = "collaboration_matching"
    SEO_OPTIMIZATION = "seo_optimization"
    PERFORMANCE_TRACKING = "performance_tracking"
    ALERT_MANAGEMENT = "alert_management"
    WORKFLOW_AUTOMATION = "workflow_automation"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


@dataclass
class AgentInfo:
    """Information about a registered agent."""
    agent_id: str
    agent_type: AgentType
    capabilities: List[AgentCapability]
    status: str = "idle"
    current_load: float = 0.0
    max_concurrent_tasks: int = 5
    average_response_time: float = 0.0
    success_rate: float = 100.0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    last_heartbeat: Optional[datetime] = None
    health_score: float = 100.0
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    specialization_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class CoordinationTask:
    """Task to be coordinated among agents."""
    task_id: str
    task_type: str
    priority: TaskPriority
    capabilities_required: List[AgentCapability]
    input_data: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    assigned_agents: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowPlan:
    """Execution plan for a multi-agent workflow."""
    workflow_id: str
    tasks: List[CoordinationTask]
    execution_graph: nx.DiGraph
    estimated_duration: timedelta
    resource_requirements: Dict[str, Any]
    success_probability: float
    risk_assessment: Dict[str, Any]
    optimization_suggestions: List[str]


class AgentCoordinator:
    """
    Advanced multi-agent coordination system for content creators.
    
    Provides intelligent orchestration including:
    - Dynamic agent discovery and registration
    - Load balancing and resource optimization
    - Workflow planning and execution
    - Fault tolerance and recovery
    - Performance monitoring and optimization
    - Inter-agent communication management
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Agent Coordinator with advanced orchestration capabilities."""
        self.config = config or {}
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # Agent registry and management
        self.registered_agents: Dict[str, AgentInfo] = {}
        self.agent_capabilities: Dict[AgentCapability, List[str]] = defaultdict(list)
        self.agent_performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Task management
        self.active_tasks: Dict[str, CoordinationTask] = {}
        self.task_queue: Dict[TaskPriority, asyncio.Queue] = {
            priority: asyncio.Queue() for priority in TaskPriority
        }
        self.completed_tasks: Dict[str, CoordinationTask] = {}
        
        # Workflow management
        self.active_workflows: Dict[str, WorkflowPlan] = {}
        self.workflow_templates: Dict[str, Dict[str, Any]] = {}
        
        # Communication and coordination
        self.message_bus: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        self.coordination_events: asyncio.Event = asyncio.Event()
        
        # Performance optimization
        self.load_balancer = LoadBalancer()
        self.performance_optimizer = PerformanceOptimizer()
        self.metrics_collector = MetricsCollector()
        
        # Configuration
        self.max_concurrent_workflows = self.config.get('max_concurrent_workflows', 50)
        self.task_timeout_default = self.config.get('task_timeout_default', 300)
        self.health_check_interval = self.config.get('health_check_interval', 30)
        self.optimization_interval = self.config.get('optimization_interval', 300)
        
        # Execution management
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.coordination_tasks: Dict[str, asyncio.Task] = {}
        
        # Initialize coordination system
        self._initialize_workflow_templates()
        self._start_coordination_services()
        
        self.logger.info("Agent Coordinator initialized with advanced orchestration")
    
    def _initialize_workflow_templates(self):
        """Initialize common workflow templates for content creation."""
        self.workflow_templates = {
            'content_creation_full': {
                'name': 'Full Content Creation Pipeline',
                'steps': [
                    {
                        'task_type': 'content_analysis',
                        'capabilities': [AgentCapability.CONTENT_ANALYSIS, AgentCapability.TREND_ANALYSIS],
                        'parallel': False
                    },
                    {
                        'task_type': 'content_optimization',
                        'capabilities': [AgentCapability.CONTENT_OPTIMIZATION, AgentCapability.SEO_OPTIMIZATION],
                        'parallel': True
                    },
                    {
                        'task_type': 'protection_setup',
                        'capabilities': [AgentCapability.FINGERPRINTING, AgentCapability.MONITORING],
                        'parallel': True
                    },
                    {
                        'task_type': 'distribution',
                        'capabilities': [AgentCapability.WORKFLOW_AUTOMATION],
                        'parallel': False
                    }
                ]
            },
            'content_protection': {
                'name': 'Content Protection Workflow',
                'steps': [
                    {
                        'task_type': 'fingerprint_generation',
                        'capabilities': [AgentCapability.FINGERPRINTING],
                        'parallel': False
                    },
                    {
                        'task_type': 'monitoring_setup',
                        'capabilities': [AgentCapability.MONITORING],
                        'parallel': False
                    },
                    {
                        'task_type': 'alert_configuration',
                        'capabilities': [AgentCapability.ALERT_MANAGEMENT],
                        'parallel': False
                    }
                ]
            },
            'collaboration_matching': {
                'name': 'Collaboration Matching Workflow',
                'steps': [
                    {
                        'task_type': 'profile_analysis',
                        'capabilities': [AgentCapability.AUDIENCE_ANALYSIS, AgentCapability.CONTENT_ANALYSIS],
                        'parallel': True
                    },
                    {
                        'task_type': 'match_generation',
                        'capabilities': [AgentCapability.COLLABORATION_MATCHING],
                        'parallel': False
                    },
                    {
                        'task_type': 'recommendation_delivery',
                        'capabilities': [AgentCapability.RECOMMENDATION],
                        'parallel': False
                    }
                ]
            }
        }
    
    def _start_coordination_services(self):
        """Start background coordination services."""
        # Start task processing
        for priority in TaskPriority:
            task_name = f"task_processor_{priority.name.lower()}"
            self.coordination_tasks[task_name] = asyncio.create_task(
                self._process_task_queue(priority)
            )
        
        # Start health monitoring
        self.coordination_tasks['health_monitor'] = asyncio.create_task(
            self._monitor_agent_health()
        )
        
        # Start performance optimization
        self.coordination_tasks['performance_optimizer'] = asyncio.create_task(
            self._optimize_performance()
        )
        
        # Start workflow management
        self.coordination_tasks['workflow_manager'] = asyncio.create_task(
            self._manage_workflows()
        )
    
    async def register_agent(
        self,
        agent_id: str,
        agent_type: AgentType,
        capabilities: List[AgentCapability],
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a new agent with the coordination system.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of the agent
            capabilities: List of agent capabilities
            config: Optional agent configuration
            
        Returns:
            bool: Registration success status
        """
        try:
            if agent_id in self.registered_agents:
                self.logger.warning(f"Agent {agent_id} already registered, updating...")
            
            # Create agent info
            agent_info = AgentInfo(
                agent_id=agent_id,
                agent_type=agent_type,
                capabilities=capabilities,
                last_heartbeat=datetime.now(),
                max_concurrent_tasks=config.get('max_concurrent_tasks', 5) if config else 5
            )
            
            # Register agent
            self.registered_agents[agent_id] = agent_info
            
            # Update capability mapping
            for capability in capabilities:
                if agent_id not in self.agent_capabilities[capability]:
                    self.agent_capabilities[capability].append(agent_id)
            
            # Initialize performance tracking
            if agent_id not in self.agent_performance_history:
                self.agent_performance_history[agent_id] = deque(maxlen=1000)
            
            self.logger.info(
                f"Agent registered: {agent_id} ({agent_type.value}) "
                f"with {len(capabilities)} capabilities"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent_id}: {str(e)}")
            return False
    
    async def execute_workflow(
        self,
        workflow_template: str,
        input_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> str:
        """
        Execute a predefined workflow using optimal agent coordination.
        
        Args:
            workflow_template: Name of workflow template to execute
            input_data: Input data for the workflow
            priority: Workflow execution priority
            
        Returns:
            str: Workflow execution ID
        """
        try:
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            if workflow_template not in self.workflow_templates:
                raise ValueError(f"Unknown workflow template: {workflow_template}")
            
            template = self.workflow_templates[workflow_template]
            
            # Create workflow plan
            workflow_plan = await self._create_workflow_plan(
                workflow_id, template, input_data, priority
            )
            
            # Validate resource availability
            if not await self._validate_resource_availability(workflow_plan):
                raise RuntimeError("Insufficient resources for workflow execution")
            
            # Store workflow
            self.active_workflows[workflow_id] = workflow_plan
            
            # Start workflow execution
            execution_task = asyncio.create_task(
                self._execute_workflow_plan(workflow_plan)
            )
            self.coordination_tasks[f"workflow_{workflow_id}"] = execution_task
            
            self.logger.info(f"Workflow started: {workflow_id} ({workflow_template})")
            
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to execute workflow: {str(e)}")
            raise
    
    async def submit_task(
        self,
        task_type: str,
        capabilities_required: List[AgentCapability],
        input_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: List[str] = None
    ) -> str:
        """
        Submit a single task for agent coordination.
        
        Args:
            task_type: Type of task to execute
            capabilities_required: Required agent capabilities
            input_data: Task input data
            priority: Task priority level
            dependencies: List of task IDs that must complete first
            
        Returns:
            str: Task ID for tracking
        """
        try:
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create coordination task
            task = CoordinationTask(
                task_id=task_id,
                task_type=task_type,
                priority=priority,
                capabilities_required=capabilities_required,
                input_data=input_data,
                dependencies=dependencies or []
            )
            
            # Store task
            self.active_tasks[task_id] = task
            
            # Queue task for processing
            await self.task_queue[priority].put(task)
            
            self.logger.info(f"Task submitted: {task_id} ({task_type}, priority: {priority.name})")
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit task: {str(e)}")
            raise
    
    async def get_optimal_agents(
        self,
        capabilities_required: List[AgentCapability],
        exclude_agents: List[str] = None
    ) -> Dict[AgentCapability, str]:
        """
        Find optimal agents for required capabilities.
        
        Args:
            capabilities_required: List of required capabilities
            exclude_agents: Agents to exclude from selection
            
        Returns:
            Dict mapping capabilities to optimal agent IDs
        """
        optimal_assignments = {}
        exclude_agents = exclude_agents or []
        
        for capability in capabilities_required:
            # Get available agents for this capability
            available_agents = [
                agent_id for agent_id in self.agent_capabilities[capability]
                if agent_id not in exclude_agents
                and self.registered_agents[agent_id].status in ['idle', 'busy']
                and self.registered_agents[agent_id].current_load < 0.8
            ]
            
            if not available_agents:
                raise RuntimeError(f"No available agents for capability: {capability.value}")
            
            # Select best agent based on performance and load
            best_agent = await self._select_best_agent(available_agents, capability)
            optimal_assignments[capability] = best_agent
            
            # Update agent load prediction
            await self._update_agent_load_prediction(best_agent, 1)
        
        return optimal_assignments
    
    async def _create_workflow_plan(
        self,
        workflow_id: str,
        template: Dict[str, Any],
        input_data: Dict[str, Any],
        priority: TaskPriority
    ) -> WorkflowPlan:
        """Create detailed execution plan for a workflow."""
        tasks = []
        execution_graph = nx.DiGraph()
        
        # Create tasks from template steps
        for i, step in enumerate(template['steps']):
            task_id = f"{workflow_id}_step_{i}"
            
            task = CoordinationTask(
                task_id=task_id,
                task_type=step['task_type'],
                priority=priority,
                capabilities_required=step['capabilities'],
                input_data=input_data.copy()
            )
            
            tasks.append(task)
            execution_graph.add_node(task_id, task=task)
            
            # Add dependencies (sequential by default unless parallel)
            if i > 0 and not step.get('parallel', False):
                prev_task_id = f"{workflow_id}_step_{i-1}"
                execution_graph.add_edge(prev_task_id, task_id)
                task.dependencies.append(prev_task_id)
        
        # Estimate workflow duration and requirements
        estimated_duration = await self._estimate_workflow_duration(tasks)
        resource_requirements = await self._calculate_resource_requirements(tasks)
        success_probability = await self._calculate_success_probability(tasks)
        risk_assessment = await self._assess_workflow_risks(tasks)
        optimization_suggestions = await self._generate_optimization_suggestions(tasks)
        
        return WorkflowPlan(
            workflow_id=workflow_id,
            tasks=tasks,
            execution_graph=execution_graph,
            estimated_duration=estimated_duration,
            resource_requirements=resource_requirements,
            success_probability=success_probability,
            risk_assessment=risk_assessment,
            optimization_suggestions=optimization_suggestions
        )
    
    async def _execute_workflow_plan(self, workflow_plan: WorkflowPlan):
        """Execute a workflow plan with proper coordination."""
        try:
            workflow_id = workflow_plan.workflow_id
            self.logger.info(f"Executing workflow plan: {workflow_id}")
            
            # Execute tasks in dependency order
            completed_tasks = set()
            
            while len(completed_tasks) < len(workflow_plan.tasks):
                # Find ready tasks (all dependencies completed)
                ready_tasks = []
                for task in workflow_plan.tasks:
                    if (task.task_id not in completed_tasks and
                        all(dep in completed_tasks for dep in task.dependencies)):
                        ready_tasks.append(task)
                
                if not ready_tasks:
                    # Check if we're stuck due to failed dependencies
                    remaining_tasks = [t for t in workflow_plan.tasks if t.task_id not in completed_tasks]
                    if remaining_tasks:
                        self.logger.error(f"Workflow {workflow_id} stuck - dependency deadlock")
                        break
                    continue
                
                # Execute ready tasks
                task_futures = []
                for task in ready_tasks:
                    future = asyncio.create_task(self._execute_single_task(task))
                    task_futures.append((task, future))
                
                # Wait for task completion
                for task, future in task_futures:
                    try:
                        result = await future
                        task.result = result
                        task.status = TaskStatus.COMPLETED
                        task.completed_at = datetime.now()
                        completed_tasks.add(task.task_id)
                        
                    except Exception as e:
                        self.logger.error(f"Task {task.task_id} failed: {str(e)}")
                        task.status = TaskStatus.FAILED
                        task.error_message = str(e)
                        completed_tasks.add(task.task_id)  # Mark as processed
                
                # Brief pause between batches
                await asyncio.sleep(0.1)
            
            self.logger.info(f"Workflow completed: {workflow_id}")
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            raise
    
    async def _execute_single_task(self, task: CoordinationTask) -> Dict[str, Any]:
        """Execute a single coordination task."""
        try:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            
            # Find optimal agents for task capabilities
            agent_assignments = await self.get_optimal_agents(task.capabilities_required)
            task.assigned_agents = list(agent_assignments.values())
            
            # Execute task with assigned agents
            if len(task.capabilities_required) == 1:
                # Single capability task
                capability = task.capabilities_required[0]
                agent_id = agent_assignments[capability]
                result = await self._execute_agent_task(agent_id, task)
            else:
                # Multi-capability task - coordinate between agents
                result = await self._execute_multi_agent_task(agent_assignments, task)
            
            # Update agent performance metrics
            for agent_id in task.assigned_agents:
                await self._update_agent_performance(agent_id, task, True)
            
            return result
            
        except Exception as e:
            # Update agent performance metrics for failure
            for agent_id in task.assigned_agents:
                await self._update_agent_performance(agent_id, task, False)
            raise
    
    async def _execute_agent_task(self, agent_id: str, task: CoordinationTask) -> Dict[str, Any]:
        """Execute task with a single agent."""
        # Simulate agent execution (in real implementation, would call actual agent)
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            'agent_id': agent_id,
            'task_type': task.task_type,
            'execution_time': 0.1,
            'success': True,
            'result_data': f"Processed {task.task_type} with {agent_id}"
        }
    
    async def _execute_multi_agent_task(
        self,
        agent_assignments: Dict[AgentCapability, str],
        task: CoordinationTask
    ) -> Dict[str, Any]:
        """Execute task requiring coordination between multiple agents."""
        results = {}
        
        # Execute sub-tasks in parallel
        futures = []
        for capability, agent_id in agent_assignments.items():
            sub_task = CoordinationTask(
                task_id=f"{task.task_id}_{capability.value}",
                task_type=f"{task.task_type}_{capability.value}",
                priority=task.priority,
                capabilities_required=[capability],
                input_data=task.input_data
            )
            
            future = self._execute_agent_task(agent_id, sub_task)
            futures.append((capability, future))
        
        # Collect results
        for capability, future in futures:
            try:
                result = await future
                results[capability.value] = result
            except Exception as e:
                results[capability.value] = {'error': str(e)}
        
        return {
            'multi_agent_results': results,
            'coordination_success': all('error' not in r for r in results.values()),
            'agents_involved': list(agent_assignments.values())
        }
    
    async def _select_best_agent(
        self,
        available_agents: List[str],
        capability: AgentCapability
    ) -> str:
        """Select the best agent for a specific capability."""
        if not available_agents:
            raise RuntimeError(f"No agents available for capability: {capability.value}")
        
        # Score agents based on multiple criteria
        agent_scores = []
        
        for agent_id in available_agents:
            agent_info = self.registered_agents[agent_id]
            
            # Calculate score based on various factors
            load_score = 1.0 - agent_info.current_load  # Lower load is better
            performance_score = agent_info.success_rate / 100.0
            speed_score = max(0, 1.0 - (agent_info.average_response_time / 10.0))
            health_score = agent_info.health_score / 100.0
            specialization_score = agent_info.specialization_scores.get(capability.value, 0.5)
            
            # Weighted combined score
            total_score = (
                load_score * 0.3 +
                performance_score * 0.25 +
                speed_score * 0.2 +
                health_score * 0.15 +
                specialization_score * 0.1
            )
            
            agent_scores.append((total_score, agent_id))
        
        # Return agent with highest score
        agent_scores.sort(key=lambda x: x[0], reverse=True)
        best_agent = agent_scores[0][1]
        
        return best_agent
    
    async def _process_task_queue(self, priority: TaskPriority):
        """Process tasks from a specific priority queue."""
        queue = self.task_queue[priority]
        
        while True:
            try:
                # Get task from queue
                task = await queue.get()
                
                # Check if dependencies are met
                if not await self._check_task_dependencies(task):
                    # Re-queue task if dependencies not met
                    await asyncio.sleep(1)
                    await queue.put(task)
                    continue
                
                # Execute task
                try:
                    result = await self._execute_single_task(task)
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now()
                    
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error_message = str(e)
                    
                    # Retry if within limit
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.status = TaskStatus.RETRY
                        await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
                        await queue.put(task)
                        continue
                
                # Move to completed tasks
                self.completed_tasks[task.task_id] = task
                if task.task_id in self.active_tasks:
                    del self.active_tasks[task.task_id]
                
                # Mark queue task as done
                queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error processing {priority.name} queue: {str(e)}")
                await asyncio.sleep(1)
    
    async def _monitor_agent_health(self):
        """Monitor health of all registered agents."""
        while True:
            try:
                current_time = datetime.now()
                
                for agent_id, agent_info in self.registered_agents.items():
                    # Check heartbeat
                    if agent_info.last_heartbeat:
                        time_since_heartbeat = current_time - agent_info.last_heartbeat
                        if time_since_heartbeat > timedelta(seconds=120):  # 2 minutes timeout
                            agent_info.status = "offline"
                            agent_info.health_score = max(0, agent_info.health_score - 10)
                    
                    # Update performance metrics
                    performance_data = {
                        'timestamp': current_time,
                        'health_score': agent_info.health_score,
                        'current_load': agent_info.current_load,
                        'success_rate': agent_info.success_rate,
                        'response_time': agent_info.average_response_time
                    }
                    
                    self.agent_performance_history[agent_id].append(performance_data)
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {str(e)}")
                await asyncio.sleep(60)
    
    async def get_coordination_analytics(self) -> Dict[str, Any]:
        """Get comprehensive coordination system analytics."""
        total_agents = len(self.registered_agents)
        active_agents = sum(1 for a in self.registered_agents.values() if a.status == "idle" or a.status == "busy")
        total_tasks = len(self.active_tasks) + len(self.completed_tasks)
        active_workflows = len(self.active_workflows)
        
        # Calculate average metrics
        if self.registered_agents:
            avg_load = statistics.mean(a.current_load for a in self.registered_agents.values())
            avg_health = statistics.mean(a.health_score for a in self.registered_agents.values())
            avg_success_rate = statistics.mean(a.success_rate for a in self.registered_agents.values())
        else:
            avg_load = avg_health = avg_success_rate = 0.0
        
        # Task distribution by priority
        priority_distribution = {}
        for priority in TaskPriority:
            priority_distribution[priority.name] = sum(
                1 for task in self.active_tasks.values() if task.priority == priority
            )
        
        return {
            'agent_statistics': {
                'total_agents': total_agents,
                'active_agents': active_agents,
                'average_load': round(avg_load, 3),
                'average_health': round(avg_health, 2),
                'average_success_rate': round(avg_success_rate, 2)
            },
            'task_statistics': {
                'total_tasks_processed': total_tasks,
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'priority_distribution': priority_distribution
            },
            'workflow_statistics': {
                'active_workflows': active_workflows,
                'workflow_templates': len(self.workflow_templates)
            },
            'system_health': {
                'coordination_services_active': len(self.coordination_tasks),
                'message_queues_active': len(self.message_bus),
                'performance_optimization_enabled': True
            }
        }


class LoadBalancer:
    """Load balancing utilities for agent coordination."""
    
    def __init__(self):
        self.load_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
    
    def calculate_optimal_distribution(
        self,
        agents: List[str],
        tasks: List[CoordinationTask]
    ) -> Dict[str, List[str]]:
        """Calculate optimal task distribution among agents."""
        # Simple round-robin for now (can be enhanced with ML)
        distribution = {agent_id: [] for agent_id in agents}
        
        for i, task in enumerate(tasks):
            agent_id = agents[i % len(agents)]
            distribution[agent_id].append(task.task_id)
        
        return distribution


class PerformanceOptimizer:
    """Performance optimization utilities for agent coordination."""
    
    def __init__(self):
        self.optimization_history: List[Dict[str, Any]] = []
    
    def suggest_optimizations(
        self,
        agent_metrics: Dict[str, AgentInfo],
        task_metrics: Dict[str, Any]
    ) -> List[str]:
        """Suggest performance optimizations based on current metrics."""
        suggestions = []
        
        # Check for overloaded agents
        overloaded_agents = [
            agent_id for agent_id, info in agent_metrics.items()
            if info.current_load > 0.8
        ]
        
        if overloaded_agents:
            suggestions.append(f"Scale up or redistribute load for {len(overloaded_agents)} overloaded agents")
        
        # Check for underutilized agents
        underutilized_agents = [
            agent_id for agent_id, info in agent_metrics.items()
            if info.current_load < 0.2 and info.status == "idle"
        ]
        
        if underutilized_agents:
            suggestions.append(f"Consider consolidating or reassigning {len(underutilized_agents)} underutilized agents")
        
        return suggestions
