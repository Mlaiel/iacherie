"""Project Orchestrator - AI-Powered Project Workflow Orchestration
=================================================================

Intelligent project orchestration system providing:
- Automated workflow creation and management
- Dynamic workflow adaptation
- Cross-team coordination
- Resource optimization
- Real-time workflow monitoring
- Intelligent task dependencies

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """Types of workflow tasks"""
    CREATIVE = "creative"
    REVIEW = "review"
    APPROVAL = "approval"
    COMMUNICATION = "communication"
    DELIVERY = "delivery"
    RESEARCH = "research"
    PLANNING = "planning"
    EXECUTION = "execution"


class OrchestrationStrategy(Enum):
    """Orchestration strategies"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"
    OPTIMIZED = "optimized"


@dataclass
class ExecutionContext:
    """Context for workflow execution"""
    project_id: str
    collaborators: List[Dict[str, Any]] = field(default_factory=list)
    resources: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    def get_collaborator(self, collaborator_id: str) -> Optional[Dict[str, Any]]:
        """Get collaborator by ID"""
        for collaborator in self.collaborators:
            if collaborator.get('creator_id') == collaborator_id:
                return collaborator
        return None
    
    def has_resource(self, resource_type: str) -> bool:
        """Check if resource is available"""
        return resource_type in self.resources and self.resources[resource_type] > 0


@dataclass
class WorkflowTask:
    """Individual workflow task"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    task_type: TaskType = TaskType.EXECUTION
    assigned_to: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: int = 1  # days
    priority: int = 1  # 1-5 scale
    status: str = "pending"
    
    # Resource requirements
    required_skills: List[str] = field(default_factory=list)
    required_resources: Dict[str, int] = field(default_factory=dict)
    
    # Timing
    earliest_start: Optional[datetime] = None
    latest_start: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    # Execution tracking
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    progress_percentage: float = 0.0
    
    # Quality metrics
    quality_requirements: Dict[str, float] = field(default_factory=dict)
    deliverables: List[str] = field(default_factory=list)
    
    def is_ready_to_start(self, completed_tasks: List[str]) -> bool:
        """Check if task is ready to start"""
        return all(dep in completed_tasks for dep in self.dependencies)
    
    def calculate_slack(self) -> int:
        """Calculate slack time in days"""
        if not self.latest_start or not self.earliest_start:
            return 0
        return (self.latest_start - self.earliest_start).days


@dataclass
class WorkflowTemplate:
    """Reusable workflow template"""
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: str = ""
    tasks: List[WorkflowTask] = field(default_factory=list)
    default_timeline: int = 30  # days
    required_roles: List[str] = field(default_factory=list)
    success_criteria: Dict[str, float] = field(default_factory=dict)
    
    def instantiate(self, project_context: Dict[str, Any]) -> 'WorkflowExecution':
        """Create workflow execution from template"""
        return WorkflowExecution(
            template_id=self.template_id,
            name=f"{self.name} - {project_context.get('project_name', 'Project')}",
            tasks=self.tasks.copy(),
            estimated_timeline=self.default_timeline
        )


@dataclass
class WorkflowExecution:
    """Active workflow execution instance"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    template_id: Optional[str] = None
    name: str = ""
    description: str = ""
    status: WorkflowStatus = WorkflowStatus.DRAFT
    strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE
    
    # Tasks and structure
    tasks: List[WorkflowTask] = field(default_factory=list)
    critical_path: List[str] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_timeline: int = 30  # days
    actual_timeline: Optional[int] = None
    
    # Execution context
    context: Optional[ExecutionContext] = None
    
    # Metrics
    completion_percentage: float = 0.0
    quality_score: float = 0.0
    efficiency_score: float = 0.0
    
    # Adaptive features
    optimization_suggestions: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    
    def get_task(self, task_id: str) -> Optional[WorkflowTask]:
        """Get task by ID"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def get_completed_tasks(self) -> List[str]:
        """Get list of completed task IDs"""
        return [task.task_id for task in self.tasks if task.status == "completed"]
    
    def get_active_tasks(self) -> List[WorkflowTask]:
        """Get currently active tasks"""
        return [task for task in self.tasks if task.status == "active"]
    
    def calculate_completion_percentage(self) -> float:
        """Calculate overall completion percentage"""
        if not self.tasks:
            return 0.0
        
        total_weight = sum(task.estimated_duration for task in self.tasks)
        completed_weight = sum(
            task.estimated_duration * task.progress_percentage / 100
            for task in self.tasks
        )
        
        return (completed_weight / total_weight * 100) if total_weight > 0 else 0.0


class OrchestrationEngine:
    """
    Core engine for workflow orchestration
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize orchestration engine"""
        self.config = config or {}
        self.optimization_algorithms = {}
        self.scheduling_rules = {}
        
        # Initialize default optimization strategies
        self._initialize_optimization_algorithms()
        self._initialize_scheduling_rules()
        
        logger.info("⚙️ Orchestration Engine initialized")
    
    def _initialize_optimization_algorithms(self):
        """Initialize workflow optimization algorithms"""
        self.optimization_algorithms = {
            'critical_path': self._critical_path_optimization,
            'resource_leveling': self._resource_leveling_optimization,
            'time_compression': self._time_compression_optimization,
            'cost_optimization': self._cost_optimization,
            'quality_optimization': self._quality_optimization
        }
    
    def _initialize_scheduling_rules(self):
        """Initialize task scheduling rules"""
        self.scheduling_rules = {
            'priority_first': self._schedule_by_priority,
            'shortest_first': self._schedule_shortest_first,
            'longest_first': self._schedule_longest_first,
            'dependency_first': self._schedule_by_dependencies,
            'resource_balanced': self._schedule_resource_balanced
        }
    
    async def optimize_workflow(
        self,
        workflow: WorkflowExecution,
        optimization_goals: List[str] = None
    ) -> WorkflowExecution:
        """Optimize workflow structure and scheduling"""
        try:
            optimization_goals = optimization_goals or ['time_compression', 'resource_leveling']
            
            optimized_workflow = workflow
            
            for goal in optimization_goals:
                if goal in self.optimization_algorithms:
                    optimizer = self.optimization_algorithms[goal]
                    optimized_workflow = await optimizer(optimized_workflow)
            
            # Recalculate critical path
            optimized_workflow.critical_path = await self._calculate_critical_path(optimized_workflow)
            
            logger.info(f"✅ Workflow {workflow.workflow_id} optimized with goals: {optimization_goals}")
            
            return optimized_workflow
            
        except Exception as e:
            logger.error(f"❌ Error optimizing workflow: {e}")
            return workflow
    
    async def _critical_path_optimization(self, workflow: WorkflowExecution) -> WorkflowExecution:
        """Optimize using critical path method"""
        try:
            # Calculate earliest and latest start times
            await self._calculate_earliest_start_times(workflow)
            await self._calculate_latest_start_times(workflow)
            
            # Identify critical path
            critical_tasks = []
            for task in workflow.tasks:
                slack = task.calculate_slack()
                if slack == 0:
                    critical_tasks.append(task.task_id)
            
            workflow.critical_path = critical_tasks
            
            # Optimize critical path tasks
            for task_id in critical_tasks:
                task = workflow.get_task(task_id)
                if task:
                    # Increase priority for critical path tasks
                    task.priority = min(task.priority + 1, 5)
            
            return workflow
            
        except Exception as e:
            logger.error(f"❌ Error in critical path optimization: {e}")
            return workflow
    
    async def _resource_leveling_optimization(self, workflow: WorkflowExecution) -> WorkflowExecution:
        """Optimize resource allocation across timeline"""
        try:
            if not workflow.context:
                return workflow
            
            # Group tasks by time periods
            time_periods = {}
            
            for task in workflow.tasks:
                if task.earliest_start:
                    period = task.earliest_start.date()
                    if period not in time_periods:
                        time_periods[period] = []
                    time_periods[period].append(task)
            
            # Level resources within each period
            for period, tasks in time_periods.items():
                await self._level_resources_for_period(tasks, workflow.context)
            
            return workflow
            
        except Exception as e:
            logger.error(f"❌ Error in resource leveling: {e}")
            return workflow
    
    async def _time_compression_optimization(self, workflow: WorkflowExecution) -> WorkflowExecution:
        """Compress timeline by parallelizing tasks"""
        try:
            # Identify tasks that can be parallelized
            parallelizable_groups = await self._identify_parallelizable_tasks(workflow)
            
            # Adjust task scheduling for parallel execution
            for group in parallelizable_groups:
                # Find the earliest possible start time for the group
                earliest_start = None
                for task_id in group:
                    task = workflow.get_task(task_id)
                    if task and task.earliest_start:
                        if earliest_start is None or task.earliest_start < earliest_start:
                            earliest_start = task.earliest_start
                
                # Set all tasks in group to start at the same time
                if earliest_start:
                    for task_id in group:
                        task = workflow.get_task(task_id)
                        if task:
                            task.earliest_start = earliest_start
            
            return workflow
            
        except Exception as e:
            logger.error(f"❌ Error in time compression: {e}")
            return workflow
    
    async def _cost_optimization(self, workflow: WorkflowExecution) -> WorkflowExecution:
        """Optimize for cost efficiency"""
        try:
            # Prioritize tasks by cost-effectiveness
            for task in workflow.tasks:
                # Calculate cost-effectiveness score
                duration = task.estimated_duration
                value_score = task.priority / 5.0  # Normalize priority
                
                if duration > 0:
                    cost_effectiveness = value_score / duration
                    # Adjust priority based on cost-effectiveness
                    task.priority = max(1, min(5, int(cost_effectiveness * 5)))
            
            return workflow
            
        except Exception as e:
            logger.error(f"❌ Error in cost optimization: {e}")
            return workflow
    
    async def _quality_optimization(self, workflow: WorkflowExecution) -> WorkflowExecution:
        """Optimize for quality outcomes"""
        try:
            # Add quality gates and review tasks
            quality_tasks = []
            
            for task in workflow.tasks:
                if task.task_type in [TaskType.CREATIVE, TaskType.EXECUTION]:
                    # Add review task after creative/execution tasks
                    review_task = WorkflowTask(
                        name=f"Review: {task.name}",
                        description=f"Quality review for {task.name}",
                        task_type=TaskType.REVIEW,
                        dependencies=[task.task_id],
                        estimated_duration=1,
                        priority=task.priority
                    )
                    quality_tasks.append(review_task)
            
            # Add quality tasks to workflow
            workflow.tasks.extend(quality_tasks)
            
            return workflow
            
        except Exception as e:
            logger.error(f"❌ Error in quality optimization: {e}")
            return workflow
    
    async def _calculate_earliest_start_times(self, workflow: WorkflowExecution):
        """Calculate earliest start times for all tasks"""
        # Create dependency graph
        task_map = {task.task_id: task for task in workflow.tasks}
        
        # Topological sort for dependency resolution
        visited = set()
        sorted_tasks = []
        
        def visit(task_id):
            if task_id in visited:
                return
            visited.add(task_id)
            
            task = task_map.get(task_id)
            if task:
                for dep_id in task.dependencies:
                    visit(dep_id)
                sorted_tasks.append(task_id)
        
        # Visit all tasks
        for task in workflow.tasks:
            visit(task.task_id)
        
        # Calculate earliest start times
        project_start = workflow.started_at or datetime.now()
        
        for task_id in sorted_tasks:
            task = task_map[task_id]
            
            if not task.dependencies:
                # No dependencies, can start immediately
                task.earliest_start = project_start
            else:
                # Start after all dependencies complete
                latest_dependency_end = project_start
                
                for dep_id in task.dependencies:
                    dep_task = task_map.get(dep_id)
                    if dep_task and dep_task.earliest_start:
                        dep_end = dep_task.earliest_start + timedelta(days=dep_task.estimated_duration)
                        if dep_end > latest_dependency_end:
                            latest_dependency_end = dep_end
                
                task.earliest_start = latest_dependency_end
    
    async def _calculate_latest_start_times(self, workflow: WorkflowExecution):
        """Calculate latest start times for all tasks"""
        # Work backwards from project deadline
        project_deadline = workflow.started_at + timedelta(days=workflow.estimated_timeline) if workflow.started_at else datetime.now() + timedelta(days=workflow.estimated_timeline)
        
        task_map = {task.task_id: task for task in workflow.tasks}
        
        # Find tasks with no successors (end tasks)
        all_dependencies = set()
        for task in workflow.tasks:
            all_dependencies.update(task.dependencies)
        
        end_tasks = [task for task in workflow.tasks if task.task_id not in all_dependencies]
        
        # Set latest start for end tasks
        for task in end_tasks:
            task.latest_start = project_deadline - timedelta(days=task.estimated_duration)
        
        # Work backwards through dependencies
        def calculate_latest_start(task_id, visited=None):
            if visited is None:
                visited = set()
            
            if task_id in visited:
                return
            
            visited.add(task_id)
            task = task_map[task_id]
            
            # Find all tasks that depend on this task
            successor_tasks = [t for t in workflow.tasks if task_id in t.dependencies]
            
            if successor_tasks:
                # Latest start is the earliest of successor latest starts
                earliest_successor_start = min(
                    succ.latest_start for succ in successor_tasks if succ.latest_start
                )
                task.latest_start = earliest_successor_start - timedelta(days=task.estimated_duration)
            
            # Recursively calculate for dependencies
            for dep_id in task.dependencies:
                calculate_latest_start(dep_id, visited)
        
        # Calculate for all tasks
        for task in workflow.tasks:
            if task.latest_start is None:
                calculate_latest_start(task.task_id)
    
    async def _calculate_critical_path(self, workflow: WorkflowExecution) -> List[str]:
        """Calculate critical path through workflow"""
        critical_path = []
        
        for task in workflow.tasks:
            slack = task.calculate_slack()
            if slack == 0:
                critical_path.append(task.task_id)
        
        return critical_path
    
    async def _identify_parallelizable_tasks(self, workflow: WorkflowExecution) -> List[List[str]]:
        """Identify groups of tasks that can run in parallel"""
        parallelizable_groups = []
        task_map = {task.task_id: task for task in workflow.tasks}
        
        # Group tasks by dependency level
        dependency_levels = {}
        
        def get_dependency_level(task_id, visited=None):
            if visited is None:
                visited = set()
            
            if task_id in visited:
                return 0  # Circular dependency, return 0
            
            if task_id in dependency_levels:
                return dependency_levels[task_id]
            
            visited.add(task_id)
            task = task_map[task_id]
            
            if not task.dependencies:
                level = 0
            else:
                max_dep_level = max(
                    get_dependency_level(dep_id, visited) for dep_id in task.dependencies
                )
                level = max_dep_level + 1
            
            dependency_levels[task_id] = level
            visited.remove(task_id)
            return level
        
        # Calculate levels for all tasks
        for task in workflow.tasks:
            get_dependency_level(task.task_id)
        
        # Group tasks by level
        level_groups = {}
        for task_id, level in dependency_levels.items():
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(task_id)
        
        # Return groups with more than one task (parallelizable)
        for level, task_ids in level_groups.items():
            if len(task_ids) > 1:
                parallelizable_groups.append(task_ids)
        
        return parallelizable_groups
    
    async def _level_resources_for_period(
        self,
        tasks: List[WorkflowTask],
        context: ExecutionContext
    ):
        """Level resource usage for a specific time period"""
        try:
            # Calculate total resource requirements
            total_resource_demand = {}
            
            for task in tasks:
                for resource_type, amount in task.required_resources.items():
                    total_resource_demand[resource_type] = total_resource_demand.get(resource_type, 0) + amount
            
            # Check resource constraints
            for resource_type, demand in total_resource_demand.items():
                available = context.resources.get(resource_type, 0)
                
                if demand > available:
                    # Resource constraint - need to adjust scheduling
                    await self._resolve_resource_conflict(tasks, resource_type, available)
        
        except Exception as e:
            logger.error(f"❌ Error leveling resources: {e}")
    
    async def _resolve_resource_conflict(
        self,
        tasks: List[WorkflowTask],
        resource_type: str,
        available_amount: int
    ):
        """Resolve resource conflicts by adjusting task scheduling"""
        try:
            # Sort tasks by priority
            tasks.sort(key=lambda t: t.priority, reverse=True)
            
            # Allocate resources to highest priority tasks first
            allocated = 0
            
            for task in tasks:
                required = task.required_resources.get(resource_type, 0)
                
                if allocated + required <= available_amount:
                    # Can allocate to this task
                    allocated += required
                else:
                    # Need to delay this task
                    if task.earliest_start:
                        task.earliest_start += timedelta(days=1)
        
        except Exception as e:
            logger.error(f"❌ Error resolving resource conflict: {e}")
    
    # Scheduling rule implementations
    async def _schedule_by_priority(self, tasks: List[WorkflowTask]) -> List[WorkflowTask]:
        """Schedule tasks by priority"""
        return sorted(tasks, key=lambda t: t.priority, reverse=True)
    
    async def _schedule_shortest_first(self, tasks: List[WorkflowTask]) -> List[WorkflowTask]:
        """Schedule shortest tasks first"""
        return sorted(tasks, key=lambda t: t.estimated_duration)
    
    async def _schedule_longest_first(self, tasks: List[WorkflowTask]) -> List[WorkflowTask]:
        """Schedule longest tasks first"""
        return sorted(tasks, key=lambda t: t.estimated_duration, reverse=True)
    
    async def _schedule_by_dependencies(self, tasks: List[WorkflowTask]) -> List[WorkflowTask]:
        """Schedule by dependency order"""
        # Topological sort
        task_map = {task.task_id: task for task in tasks}
        visited = set()
        sorted_tasks = []
        
        def visit(task):
            if task.task_id in visited:
                return
            visited.add(task.task_id)
            
            for dep_id in task.dependencies:
                dep_task = task_map.get(dep_id)
                if dep_task:
                    visit(dep_task)
            
            sorted_tasks.append(task)
        
        for task in tasks:
            visit(task)
        
        return sorted_tasks
    
    async def _schedule_resource_balanced(self, tasks: List[WorkflowTask]) -> List[WorkflowTask]:
        """Schedule to balance resource usage"""
        # Group tasks by resource requirements
        resource_groups = {}
        
        for task in tasks:
            resource_signature = tuple(sorted(task.required_resources.items()))
            if resource_signature not in resource_groups:
                resource_groups[resource_signature] = []
            resource_groups[resource_signature].append(task)
        
        # Interleave tasks from different resource groups
        scheduled = []
        group_iterators = [iter(group) for group in resource_groups.values()]
        
        while group_iterators:
            for i, iterator in enumerate(group_iterators):
                try:
                    task = next(iterator)
                    scheduled.append(task)
                except StopIteration:
                    group_iterators.pop(i)
                    break
        
        return scheduled


class ProjectOrchestrator:
    """
    AI-powered project orchestration system
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize project orchestrator"""
        self.config = config or {}
        self.active_workflows: Dict[str, WorkflowExecution] = {}
        self.workflow_templates: Dict[str, WorkflowTemplate] = {}
        self.orchestration_engine = OrchestrationEngine(config)
        
        # Configuration
        self.max_concurrent_workflows = self.config.get('max_concurrent_workflows', 100)
        self.auto_optimization_enabled = self.config.get('auto_optimization', True)
        self.monitoring_interval = self.config.get('monitoring_interval', 3600)  # seconds
        
        # Initialize default templates
        asyncio.create_task(self._initialize_default_templates())
        
        logger.info("🎯 Project Orchestrator initialized")
    
    async def _initialize_default_templates(self):
        """Initialize default workflow templates"""
        try:
            # Content creation template
            content_template = WorkflowTemplate(
                name="Content Creation Collaboration",
                description="Standard workflow for content creation collaborations",
                category="content",
                default_timeline=21,
                required_roles=["creator", "collaborator"]
            )
            
            content_template.tasks = [
                WorkflowTask(
                    name="Project Planning",
                    description="Define project scope, timeline, and deliverables",
                    task_type=TaskType.PLANNING,
                    estimated_duration=2,
                    priority=5,
                    required_skills=["project_management"]
                ),
                WorkflowTask(
                    name="Content Research",
                    description="Research topic, audience, and market trends",
                    task_type=TaskType.RESEARCH,
                    estimated_duration=3,
                    priority=4,
                    dependencies=[content_template.tasks[0].task_id if content_template.tasks else "planning"],
                    required_skills=["research", "analysis"]
                ),
                WorkflowTask(
                    name="Content Creation",
                    description="Create primary content deliverables",
                    task_type=TaskType.CREATIVE,
                    estimated_duration=10,
                    priority=5,
                    dependencies=[content_template.tasks[1].task_id if len(content_template.tasks) > 1 else "research"],
                    required_skills=["content_creation"]
                ),
                WorkflowTask(
                    name="Content Review",
                    description="Review and provide feedback on content",
                    task_type=TaskType.REVIEW,
                    estimated_duration=2,
                    priority=4,
                    dependencies=[content_template.tasks[2].task_id if len(content_template.tasks) > 2 else "creation"],
                    required_skills=["review", "quality_assurance"]
                ),
                WorkflowTask(
                    name="Content Approval",
                    description="Final approval of content deliverables",
                    task_type=TaskType.APPROVAL,
                    estimated_duration=1,
                    priority=5,
                    dependencies=[content_template.tasks[3].task_id if len(content_template.tasks) > 3 else "review"],
                    required_skills=["approval"]
                ),
                WorkflowTask(
                    name="Content Delivery",
                    description="Deliver final content to stakeholders",
                    task_type=TaskType.DELIVERY,
                    estimated_duration=1,
                    priority=5,
                    dependencies=[content_template.tasks[4].task_id if len(content_template.tasks) > 4 else "approval"],
                    required_skills=["delivery"]
                )
            ]
            
            self.workflow_templates[content_template.template_id] = content_template
            
            logger.info("✅ Default workflow templates initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing templates: {e}")
    
    async def create_workflow(
        self,
        project_definition: Dict[str, Any],
        collaborators: List[Dict[str, Any]],
        template_id: Optional[str] = None
    ) -> WorkflowExecution:
        """Create new workflow execution"""
        try:
            if template_id and template_id in self.workflow_templates:
                # Create from template
                template = self.workflow_templates[template_id]
                workflow = template.instantiate(project_definition)
            else:
                # Create custom workflow
                workflow = WorkflowExecution(
                    name=project_definition.get('name', 'Custom Project'),
                    description=project_definition.get('description', ''),
                    estimated_timeline=project_definition.get('timeline', 30)
                )
                
                # Add custom tasks
                custom_tasks = project_definition.get('tasks', [])
                for task_data in custom_tasks:
                    task = WorkflowTask(
                        name=task_data.get('name', 'Untitled Task'),
                        description=task_data.get('description', ''),
                        task_type=TaskType(task_data.get('type', 'execution')),
                        estimated_duration=task_data.get('duration', 1),
                        priority=task_data.get('priority', 3),
                        dependencies=task_data.get('dependencies', []),
                        required_skills=task_data.get('skills', [])
                    )
                    workflow.tasks.append(task)
            
            # Set up execution context
            workflow.context = ExecutionContext(
                project_id=project_definition.get('project_id', workflow.workflow_id),
                collaborators=collaborators,
                resources=project_definition.get('resources', {}),
                constraints=project_definition.get('constraints', {}),
                environment=project_definition.get('environment', {}),
                configuration=project_definition.get('configuration', {})
            )
            
            # Assign tasks to collaborators
            await self._assign_tasks(workflow)
            
            # Optimize workflow if enabled
            if self.auto_optimization_enabled:
                workflow = await self.orchestration_engine.optimize_workflow(workflow)
            
            # Store active workflow
            self.active_workflows[workflow.workflow_id] = workflow
            
            logger.info(f"✅ Workflow {workflow.workflow_id} created successfully")
            
            return workflow
            
        except Exception as e:
            logger.error(f"❌ Error creating workflow: {e}")
            raise
    
    async def _assign_tasks(self, workflow: WorkflowExecution):
        """Automatically assign tasks to collaborators"""
        try:
            if not workflow.context or not workflow.context.collaborators:
                return
            
            # Create skill mapping
            collaborator_skills = {}
            for collaborator in workflow.context.collaborators:
                creator_id = collaborator['creator_id']
                skills = collaborator.get('skills', [])
                collaborator_skills[creator_id] = set(skills)
            
            # Assign tasks based on skill matching
            for task in workflow.tasks:
                if task.assigned_to:
                    continue  # Already assigned
                
                required_skills = set(task.required_skills)
                
                # Find best match
                best_match = None
                best_score = 0
                
                for creator_id, skills in collaborator_skills.items():
                    # Calculate skill match score
                    matching_skills = required_skills & skills
                    match_score = len(matching_skills) / len(required_skills) if required_skills else 1
                    
                    if match_score > best_score:
                        best_score = match_score
                        best_match = creator_id
                
                # Assign to best match if good enough
                if best_match and best_score >= 0.5:  # At least 50% skill match
                    task.assigned_to = best_match
                elif workflow.context.collaborators:
                    # Assign to first available collaborator
                    task.assigned_to = workflow.context.collaborators[0]['creator_id']
            
        except Exception as e:
            logger.error(f"❌ Error assigning tasks: {e}")
    
    async def start_workflow(self, workflow_id: str) -> bool:
        """Start workflow execution"""
        try:
            if workflow_id not in self.active_workflows:
                return False
            
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.ACTIVE
            workflow.started_at = datetime.now()
            
            # Start initial tasks (those with no dependencies)
            for task in workflow.tasks:
                if not task.dependencies:
                    task.status = "active"
                    task.actual_start = datetime.now()
            
            logger.info(f"🚀 Workflow {workflow_id} started")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting workflow: {e}")
            return False
    
    async def update_task_progress(
        self,
        workflow_id: str,
        task_id: str,
        progress_percentage: float,
        status: Optional[str] = None
    ) -> bool:
        """Update task progress and status"""
        try:
            if workflow_id not in self.active_workflows:
                return False
            
            workflow = self.active_workflows[workflow_id]
            task = workflow.get_task(task_id)
            
            if not task:
                return False
            
            # Update progress
            task.progress_percentage = max(0, min(100, progress_percentage))
            
            # Update status if provided
            if status:
                old_status = task.status
                task.status = status
                
                # Handle status changes
                if status == "completed" and old_status != "completed":
                    task.actual_end = datetime.now()
                    await self._on_task_completed(workflow, task)
                elif status == "active" and old_status != "active":
                    task.actual_start = datetime.now()
            
            # Update workflow completion percentage
            workflow.completion_percentage = workflow.calculate_completion_percentage()
            
            # Check if workflow is complete
            if workflow.completion_percentage >= 100:
                await self._complete_workflow(workflow)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating task progress: {e}")
            return False
    
    async def _on_task_completed(self, workflow: WorkflowExecution, completed_task: WorkflowTask):
        """Handle task completion"""
        try:
            # Check if any tasks can now start
            completed_tasks = workflow.get_completed_tasks()
            
            for task in workflow.tasks:
                if (task.status == "pending" and 
                    task.is_ready_to_start(completed_tasks)):
                    task.status = "active"
                    task.actual_start = datetime.now()
                    
                    logger.info(f"📋 Task {task.task_id} is now ready to start")
            
        except Exception as e:
            logger.error(f"❌ Error handling task completion: {e}")
    
    async def _complete_workflow(self, workflow: WorkflowExecution):
        """Mark workflow as completed"""
        try:
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            
            if workflow.started_at:
                workflow.actual_timeline = (workflow.completed_at - workflow.started_at).days
            
            # Calculate final metrics
            await self._calculate_final_metrics(workflow)
            
            logger.info(f"🎉 Workflow {workflow.workflow_id} completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error completing workflow: {e}")
    
    async def _calculate_final_metrics(self, workflow: WorkflowExecution):
        """Calculate final workflow metrics"""
        try:
            # Quality score based on task completion quality
            quality_scores = []
            for task in workflow.tasks:
                if task.status == "completed":
                    # Simple quality calculation based on on-time completion
                    if task.actual_end and task.deadline:
                        if task.actual_end <= task.deadline:
                            quality_scores.append(1.0)
                        else:
                            # Penalty for late completion
                            delay_ratio = (task.actual_end - task.deadline).days / task.estimated_duration
                            quality_scores.append(max(0.5, 1.0 - delay_ratio))
                    else:
                        quality_scores.append(0.8)  # Default for completed tasks
            
            workflow.quality_score = np.mean(quality_scores) if quality_scores else 0.0
            
            # Efficiency score based on timeline adherence
            if workflow.actual_timeline and workflow.estimated_timeline:
                efficiency_ratio = workflow.estimated_timeline / workflow.actual_timeline
                workflow.efficiency_score = min(1.0, efficiency_ratio)
            else:
                workflow.efficiency_score = 0.5
            
        except Exception as e:
            logger.error(f"❌ Error calculating final metrics: {e}")
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive workflow status"""
        try:
            if workflow_id not in self.active_workflows:
                return None
            
            workflow = self.active_workflows[workflow_id]
            
            status = {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "completion_percentage": workflow.completion_percentage,
                "quality_score": workflow.quality_score,
                "efficiency_score": workflow.efficiency_score,
                "estimated_timeline": workflow.estimated_timeline,
                "actual_timeline": workflow.actual_timeline,
                "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
                "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                "critical_path": workflow.critical_path,
                "task_summary": {
                    "total_tasks": len(workflow.tasks),
                    "completed_tasks": len([t for t in workflow.tasks if t.status == "completed"]),
                    "active_tasks": len([t for t in workflow.tasks if t.status == "active"]),
                    "pending_tasks": len([t for t in workflow.tasks if t.status == "pending"])
                },
                "optimization_suggestions": workflow.optimization_suggestions,
                "risk_factors": workflow.risk_factors
            }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error getting workflow status: {e}")
            return None
    
    async def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Get status of all active workflows"""
        workflows = []
        
        for workflow_id in self.active_workflows:
            status = await self.get_workflow_status(workflow_id)
            if status:
                workflows.append(status)
        
        return workflows
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause workflow execution"""
        try:
            if workflow_id not in self.active_workflows:
                return False
            
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.PAUSED
            
            # Pause all active tasks
            for task in workflow.tasks:
                if task.status == "active":
                    task.status = "paused"
            
            logger.info(f"⏸️ Workflow {workflow_id} paused")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error pausing workflow: {e}")
            return False
    
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume paused workflow"""
        try:
            if workflow_id not in self.active_workflows:
                return False
            
            workflow = self.active_workflows[workflow_id]
            
            if workflow.status != WorkflowStatus.PAUSED:
                return False
            
            workflow.status = WorkflowStatus.ACTIVE
            
            # Resume paused tasks
            for task in workflow.tasks:
                if task.status == "paused":
                    task.status = "active"
            
            logger.info(f"▶️ Workflow {workflow_id} resumed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resuming workflow: {e}")
            return False
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel workflow execution"""
        try:
            if workflow_id not in self.active_workflows:
                return False
            
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.now()
            
            # Cancel all active tasks
            for task in workflow.tasks:
                if task.status in ["active", "pending"]:
                    task.status = "cancelled"
            
            logger.info(f"❌ Workflow {workflow_id} cancelled")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cancelling workflow: {e}")
            return False