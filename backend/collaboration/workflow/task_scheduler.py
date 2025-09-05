"""Task Scheduler Module - Intelligent Task Scheduling and Priority Management
=============================================================================

Advanced task scheduling system providing intelligent task prioritization,
dependency management, resource optimization, and automated scheduling for
collaborative workflows.

This module implements:
- AI-powered task prioritization algorithms
- Dynamic dependency resolution
- Resource-aware scheduling optimization
- Adaptive timeline adjustments
- Intelligent workload balancing
- Automated conflict resolution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import heapq
from collections import defaultdict, deque
import networkx as nx

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEFERRED = "deferred"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class DependencyType(Enum):
    """Types of task dependencies"""
    FINISH_TO_START = "finish_to_start"  # Task B starts when A finishes
    START_TO_START = "start_to_start"    # Task B starts when A starts
    FINISH_TO_FINISH = "finish_to_finish" # Task B finishes when A finishes
    START_TO_FINISH = "start_to_finish"   # Task B finishes when A starts


class SchedulingStrategy(Enum):
    """Scheduling optimization strategies"""
    CRITICAL_PATH = "critical_path"
    RESOURCE_LEVELING = "resource_leveling"
    EARLIEST_START = "earliest_start"
    LATEST_START = "latest_start"
    PRIORITY_FIRST = "priority_first"
    BALANCED = "balanced"


class ResourceType(Enum):
    """Types of resources"""
    HUMAN = "human"
    COMPUTATIONAL = "computational"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    TOOL = "tool"
    LICENSE = "license"


@dataclass
class ResourceRequirement:
    """Resource requirement specification"""
    resource_type: ResourceType
    resource_id: str
    quantity: float
    duration: timedelta
    is_exclusive: bool = False  # True if resource cannot be shared
    alternatives: List[str] = field(default_factory=list)  # Alternative resources


@dataclass
class TaskDependency:
    """Task dependency definition"""
    dependency_id: str
    predecessor_task_id: str
    successor_task_id: str
    dependency_type: DependencyType
    lag_time: timedelta = field(default_factory=lambda: timedelta(0))  # Delay between tasks
    lead_time: timedelta = field(default_factory=lambda: timedelta(0))  # Overlap time
    is_mandatory: bool = True


@dataclass
class ScheduledTask:
    """Complete task definition with scheduling information"""
    task_id: str
    name: str
    description: str
    project_id: str
    assignee_id: Optional[str] = None
    
    # Scheduling properties
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    estimated_duration: timedelta = field(default_factory=lambda: timedelta(hours=4))
    actual_duration: Optional[timedelta] = None
    
    # Timeline
    earliest_start: Optional[datetime] = None
    latest_start: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    # Dependencies and constraints
    dependencies: List[TaskDependency] = field(default_factory=list)
    resource_requirements: List[ResourceRequirement] = field(default_factory=list)
    
    # Progress tracking
    progress_percentage: float = 0.0
    completion_score: float = 0.0
    quality_score: float = 0.0
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # AI scheduling insights
    complexity_score: float = 1.0  # 0.1 (simple) to 10.0 (very complex)
    risk_score: float = 0.5  # 0.0 (no risk) to 1.0 (high risk)
    automation_potential: float = 0.0  # 0.0 (manual) to 1.0 (fully automatable)


@dataclass
class ResourceAllocation:
    """Resource allocation result"""
    allocation_id: str
    task_id: str
    resource_id: str
    resource_type: ResourceType
    allocated_quantity: float
    allocation_start: datetime
    allocation_end: datetime
    utilization_rate: float
    cost: float = 0.0
    is_confirmed: bool = False


@dataclass
class SchedulingResult:
    """Result of scheduling operation"""
    schedule_id: str
    project_id: str
    tasks: List[ScheduledTask]
    resource_allocations: List[ResourceAllocation]
    critical_path: List[str]  # Task IDs in critical path
    total_duration: timedelta
    resource_utilization: Dict[str, float]
    optimization_score: float
    conflicts: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TaskScheduler:
    """Advanced AI-powered task scheduling system"""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.dependencies: Dict[str, List[TaskDependency]] = defaultdict(list)
        self.resource_pools: Dict[str, Dict[str, Any]] = {}
        self.scheduling_results: Dict[str, SchedulingResult] = {}
        self.task_graph = nx.DiGraph()
        
        # Configuration
        self.max_parallel_tasks = 10
        self.resource_buffer_percentage = 0.1  # 10% buffer for resources
        self.default_working_hours = 8
        self.default_working_days = [0, 1, 2, 3, 4]  # Monday to Friday
        
        logger.info("⏰ Task Scheduler initialized with AI-powered optimization")
    
    async def add_task(
        self,
        name: str,
        description: str,
        project_id: str,
        estimated_duration: timedelta,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assignee_id: Optional[str] = None,
        deadline: Optional[datetime] = None,
        resource_requirements: Optional[List[ResourceRequirement]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ScheduledTask:
        """Add new task to scheduler"""
        try:
            task_id = str(uuid.uuid4())
            
            # Calculate AI-based scores
            complexity_score = await self._calculate_complexity_score(
                name, description, estimated_duration, resource_requirements or []
            )
            risk_score = await self._calculate_risk_score(
                estimated_duration, deadline, priority, complexity_score
            )
            automation_potential = await self._assess_automation_potential(
                name, description, metadata or {}
            )
            
            task = ScheduledTask(
                task_id=task_id,
                name=name,
                description=description,
                project_id=project_id,
                assignee_id=assignee_id,
                priority=priority,
                estimated_duration=estimated_duration,
                deadline=deadline,
                resource_requirements=resource_requirements or [],
                metadata=metadata or {},
                complexity_score=complexity_score,
                risk_score=risk_score,
                automation_potential=automation_potential
            )
            
            self.tasks[task_id] = task
            self.task_graph.add_node(task_id, task=task)
            
            logger.info(f"📝 Task added: {task_id} - {name}")
            return task
            
        except Exception as e:
            logger.error(f"❌ Error adding task: {e}")
            raise
    
    async def add_dependency(
        self,
        predecessor_task_id: str,
        successor_task_id: str,
        dependency_type: DependencyType = DependencyType.FINISH_TO_START,
        lag_time: timedelta = timedelta(0),
        lead_time: timedelta = timedelta(0)
    ) -> TaskDependency:
        """Add dependency between tasks"""
        try:
            if predecessor_task_id not in self.tasks:
                raise ValueError(f"Predecessor task {predecessor_task_id} not found")
            if successor_task_id not in self.tasks:
                raise ValueError(f"Successor task {successor_task_id} not found")
            
            dependency_id = str(uuid.uuid4())
            dependency = TaskDependency(
                dependency_id=dependency_id,
                predecessor_task_id=predecessor_task_id,
                successor_task_id=successor_task_id,
                dependency_type=dependency_type,
                lag_time=lag_time,
                lead_time=lead_time
            )
            
            # Add to dependency tracking
            self.dependencies[successor_task_id].append(dependency)
            self.tasks[successor_task_id].dependencies.append(dependency)
            
            # Update task graph
            self.task_graph.add_edge(
                predecessor_task_id, 
                successor_task_id, 
                dependency=dependency
            )
            
            # Check for cycles
            if not nx.is_directed_acyclic_graph(self.task_graph):
                # Remove the edge that created the cycle
                self.task_graph.remove_edge(predecessor_task_id, successor_task_id)
                self.dependencies[successor_task_id].remove(dependency)
                self.tasks[successor_task_id].dependencies.remove(dependency)
                raise ValueError("Dependency would create a cycle in task graph")
            
            logger.info(f"🔗 Dependency added: {predecessor_task_id} → {successor_task_id}")
            return dependency
            
        except Exception as e:
            logger.error(f"❌ Error adding dependency: {e}")
            raise
    
    async def schedule_project(
        self,
        project_id: str,
        start_date: datetime,
        strategy: SchedulingStrategy = SchedulingStrategy.BALANCED,
        optimize_for: str = "time"  # "time", "resources", "cost", "quality"
    ) -> SchedulingResult:
        """Schedule all tasks in a project"""
        try:
            # Get project tasks
            project_tasks = [
                task for task in self.tasks.values()
                if task.project_id == project_id
            ]
            
            if not project_tasks:
                raise ValueError(f"No tasks found for project {project_id}")
            
            # Build project subgraph
            project_graph = self._build_project_graph(project_tasks)
            
            # Calculate critical path
            critical_path = await self._calculate_critical_path(project_graph, project_tasks)
            
            # Apply scheduling strategy
            if strategy == SchedulingStrategy.CRITICAL_PATH:
                scheduled_tasks = await self._schedule_critical_path_first(
                    project_tasks, critical_path, start_date
                )
            elif strategy == SchedulingStrategy.PRIORITY_FIRST:
                scheduled_tasks = await self._schedule_priority_first(
                    project_tasks, start_date
                )
            elif strategy == SchedulingStrategy.RESOURCE_LEVELING:
                scheduled_tasks = await self._schedule_resource_leveling(
                    project_tasks, start_date
                )
            else:  # BALANCED
                scheduled_tasks = await self._schedule_balanced(
                    project_tasks, critical_path, start_date
                )
            
            # Allocate resources
            resource_allocations = await self._allocate_resources(scheduled_tasks)
            
            # Optimize based on criteria
            if optimize_for == "time":
                scheduled_tasks, resource_allocations = await self._optimize_for_time(
                    scheduled_tasks, resource_allocations
                )
            elif optimize_for == "resources":
                scheduled_tasks, resource_allocations = await self._optimize_for_resources(
                    scheduled_tasks, resource_allocations
                )
            
            # Calculate metrics
            total_duration = await self._calculate_total_duration(scheduled_tasks)
            resource_utilization = await self._calculate_resource_utilization(resource_allocations)
            optimization_score = await self._calculate_optimization_score(
                scheduled_tasks, resource_allocations, strategy
            )
            
            # Detect conflicts
            conflicts = await self._detect_conflicts(scheduled_tasks, resource_allocations)
            warnings = await self._generate_warnings(scheduled_tasks, resource_allocations)
            
            # Create result
            schedule_id = str(uuid.uuid4())
            result = SchedulingResult(
                schedule_id=schedule_id,
                project_id=project_id,
                tasks=scheduled_tasks,
                resource_allocations=resource_allocations,
                critical_path=critical_path,
                total_duration=total_duration,
                resource_utilization=resource_utilization,
                optimization_score=optimization_score,
                conflicts=conflicts,
                warnings=warnings
            )
            
            self.scheduling_results[schedule_id] = result
            
            # Update task schedules
            for task in scheduled_tasks:
                self.tasks[task.task_id] = task
            
            logger.info(f"📅 Project scheduled: {project_id} - {len(scheduled_tasks)} tasks")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error scheduling project: {e}")
            raise
    
    async def reschedule_task(
        self,
        task_id: str,
        new_start: Optional[datetime] = None,
        new_duration: Optional[timedelta] = None,
        new_priority: Optional[TaskPriority] = None,
        cascade_changes: bool = True
    ) -> List[ScheduledTask]:
        """Reschedule a task and optionally cascade changes"""
        try:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")
            
            task = self.tasks[task_id]
            affected_tasks = [task]
            
            # Update task properties
            if new_start:
                task.scheduled_start = new_start
                task.scheduled_end = new_start + (new_duration or task.estimated_duration)
            
            if new_duration:
                task.estimated_duration = new_duration
                if task.scheduled_start:
                    task.scheduled_end = task.scheduled_start + new_duration
            
            if new_priority:
                task.priority = new_priority
            
            task.updated_at = datetime.now(timezone.utc)
            
            # Cascade changes to dependent tasks
            if cascade_changes:
                dependent_tasks = await self._find_dependent_tasks(task_id)
                for dep_task in dependent_tasks:
                    # Recalculate start times based on dependencies
                    new_dep_start = await self._calculate_earliest_start(dep_task.task_id)
                    if new_dep_start and new_dep_start != dep_task.scheduled_start:
                        dep_task.scheduled_start = new_dep_start
                        dep_task.scheduled_end = new_dep_start + dep_task.estimated_duration
                        dep_task.updated_at = datetime.now(timezone.utc)
                        affected_tasks.append(dep_task)
            
            logger.info(f"🔄 Task rescheduled: {task_id} - {len(affected_tasks)} tasks affected")
            return affected_tasks
            
        except Exception as e:
            logger.error(f"❌ Error rescheduling task: {e}")
            return []
    
    async def get_task_recommendations(
        self,
        task_id: str
    ) -> Dict[str, Any]:
        """Get AI-powered recommendations for task optimization"""
        try:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")
            
            task = self.tasks[task_id]
            recommendations = {
                "task_id": task_id,
                "optimization_opportunities": [],
                "risk_mitigation": [],
                "resource_suggestions": [],
                "timeline_improvements": [],
                "automation_suggestions": []
            }
            
            # Analyze optimization opportunities
            if task.complexity_score > 7.0:
                recommendations["optimization_opportunities"].append(
                    "Consider breaking down this complex task into smaller subtasks"
                )
            
            if task.risk_score > 0.7:
                recommendations["risk_mitigation"].extend([
                    "Add buffer time to account for potential delays",
                    "Assign backup resources or team members",
                    "Create contingency plans for critical dependencies"
                ])
            
            # Resource optimization
            if len(task.resource_requirements) > 5:
                recommendations["resource_suggestions"].append(
                    "Consider consolidating or optimizing resource requirements"
                )
            
            # Timeline suggestions
            if task.deadline and task.scheduled_end and task.scheduled_end > task.deadline:
                recommendations["timeline_improvements"].append(
                    "Task is scheduled to finish after deadline - consider priority increase or resource addition"
                )
            
            # Automation opportunities
            if task.automation_potential > 0.6:
                recommendations["automation_suggestions"].append(
                    f"Task has {task.automation_potential:.0%} automation potential - consider workflow automation"
                )
            
            logger.info(f"💡 Recommendations generated for task {task_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return {}
    
    async def analyze_schedule_performance(
        self,
        schedule_id: str
    ) -> Dict[str, Any]:
        """Analyze schedule performance and adherence"""
        try:
            if schedule_id not in self.scheduling_results:
                raise ValueError(f"Schedule {schedule_id} not found")
            
            result = self.scheduling_results[schedule_id]
            analysis = {
                "schedule_id": schedule_id,
                "overall_performance": {},
                "task_performance": {},
                "resource_performance": {},
                "timeline_analysis": {},
                "recommendations": []
            }
            
            # Overall performance metrics
            completed_tasks = [t for t in result.tasks if t.status == TaskStatus.COMPLETED]
            on_time_tasks = [
                t for t in completed_tasks
                if t.actual_end and t.scheduled_end and t.actual_end <= t.scheduled_end
            ]
            
            analysis["overall_performance"] = {
                "completion_rate": len(completed_tasks) / len(result.tasks) * 100,
                "on_time_rate": len(on_time_tasks) / max(len(completed_tasks), 1) * 100,
                "average_quality_score": sum(t.quality_score for t in completed_tasks) / max(len(completed_tasks), 1),
                "resource_utilization_avg": sum(result.resource_utilization.values()) / max(len(result.resource_utilization), 1)
            }
            
            # Task performance analysis
            for task in result.tasks:
                if task.actual_start and task.actual_end:
                    actual_duration = task.actual_end - task.actual_start
                    duration_variance = (actual_duration - task.estimated_duration).total_seconds() / 3600
                    
                    analysis["task_performance"][task.task_id] = {
                        "estimated_hours": task.estimated_duration.total_seconds() / 3600,
                        "actual_hours": actual_duration.total_seconds() / 3600,
                        "variance_hours": duration_variance,
                        "quality_score": task.quality_score,
                        "on_time": task.actual_end <= task.scheduled_end if task.scheduled_end else True
                    }
            
            # Generate recommendations
            if analysis["overall_performance"]["on_time_rate"] < 80:
                analysis["recommendations"].append("Consider adding more buffer time to task estimates")
            
            if analysis["overall_performance"]["resource_utilization_avg"] > 90:
                analysis["recommendations"].append("Resource utilization is high - consider capacity planning")
            
            logger.info(f"📊 Schedule performance analyzed: {schedule_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing schedule performance: {e}")
            return {}
    
    # Helper methods for scheduling algorithms
    
    def _build_project_graph(self, tasks: List[ScheduledTask]) -> nx.DiGraph:
        """Build project task graph"""
        graph = nx.DiGraph()
        
        for task in tasks:
            graph.add_node(task.task_id, task=task)
        
        for task in tasks:
            for dep in task.dependencies:
                if dep.predecessor_task_id in [t.task_id for t in tasks]:
                    graph.add_edge(dep.predecessor_task_id, task.task_id, dependency=dep)
        
        return graph
    
    async def _calculate_critical_path(
        self,
        graph: nx.DiGraph,
        tasks: List[ScheduledTask]
    ) -> List[str]:
        """Calculate critical path using longest path algorithm"""
        try:
            # Create duration mapping
            task_durations = {task.task_id: task.estimated_duration.total_seconds() for task in tasks}
            
            # Find all paths from start nodes to end nodes
            start_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
            end_nodes = [n for n in graph.nodes() if graph.out_degree(n) == 0]
            
            longest_path = []
            max_duration = 0
            
            for start in start_nodes:
                for end in end_nodes:
                    try:
                        paths = list(nx.all_simple_paths(graph, start, end))
                        for path in paths:
                            path_duration = sum(task_durations.get(node, 0) for node in path)
                            if path_duration > max_duration:
                                max_duration = path_duration
                                longest_path = path
                    except nx.NetworkXNoPath:
                        continue
            
            return longest_path
            
        except Exception as e:
            logger.error(f"❌ Error calculating critical path: {e}")
            return []
    
    async def _schedule_critical_path_first(
        self,
        tasks: List[ScheduledTask],
        critical_path: List[str],
        start_date: datetime
    ) -> List[ScheduledTask]:
        """Schedule critical path tasks first"""
        scheduled_tasks = tasks.copy()
        current_time = start_date
        
        # Schedule critical path tasks
        for task_id in critical_path:
            task = next((t for t in scheduled_tasks if t.task_id == task_id), None)
            if task:
                task.scheduled_start = current_time
                task.scheduled_end = current_time + task.estimated_duration
                current_time = task.scheduled_end
        
        # Schedule remaining tasks
        for task in scheduled_tasks:
            if task.task_id not in critical_path:
                earliest_start = await self._calculate_earliest_start_for_task(task, scheduled_tasks)
                task.scheduled_start = max(earliest_start, start_date)
                task.scheduled_end = task.scheduled_start + task.estimated_duration
        
        return scheduled_tasks
    
    async def _schedule_priority_first(
        self,
        tasks: List[ScheduledTask],
        start_date: datetime
    ) -> List[ScheduledTask]:
        """Schedule tasks by priority"""
        # Sort by priority
        priority_order = {
            TaskPriority.CRITICAL: 5,
            TaskPriority.HIGH: 4,
            TaskPriority.MEDIUM: 3,
            TaskPriority.LOW: 2,
            TaskPriority.DEFERRED: 1
        }
        
        sorted_tasks = sorted(tasks, key=lambda t: priority_order[t.priority], reverse=True)
        scheduled_tasks = []
        
        for task in sorted_tasks:
            # Calculate earliest possible start considering dependencies
            earliest_start = await self._calculate_earliest_start_for_task(task, scheduled_tasks)
            task.scheduled_start = max(earliest_start, start_date)
            task.scheduled_end = task.scheduled_start + task.estimated_duration
            scheduled_tasks.append(task)
        
        return scheduled_tasks
    
    async def _schedule_resource_leveling(
        self,
        tasks: List[ScheduledTask],
        start_date: datetime
    ) -> List[ScheduledTask]:
        """Schedule with resource leveling optimization"""
        scheduled_tasks = []
        resource_timeline = defaultdict(list)  # resource_id -> [(start, end, task_id)]
        
        # Sort tasks by earliest start time
        for task in tasks:
            earliest_start = await self._calculate_earliest_start_for_task(task, scheduled_tasks)
            task.earliest_start = max(earliest_start, start_date)
        
        sorted_tasks = sorted(tasks, key=lambda t: t.earliest_start or start_date)
        
        for task in sorted_tasks:
            # Find optimal start time considering resource availability
            optimal_start = await self._find_optimal_start_with_resources(
                task, resource_timeline, task.earliest_start or start_date
            )
            
            task.scheduled_start = optimal_start
            task.scheduled_end = optimal_start + task.estimated_duration
            
            # Update resource timeline
            for req in task.resource_requirements:
                resource_timeline[req.resource_id].append(
                    (task.scheduled_start, task.scheduled_end, task.task_id)
                )
            
            scheduled_tasks.append(task)
        
        return scheduled_tasks
    
    async def _schedule_balanced(
        self,
        tasks: List[ScheduledTask],
        critical_path: List[str],
        start_date: datetime
    ) -> List[ScheduledTask]:
        """Balanced scheduling considering multiple factors"""
        # Combine priority, critical path, and resource optimization
        scheduled_tasks = []
        
        # First pass: Schedule critical path with priority weighting
        critical_tasks = [t for t in tasks if t.task_id in critical_path]
        non_critical_tasks = [t for t in tasks if t.task_id not in critical_path]
        
        # Schedule critical tasks first
        for task in critical_tasks:
            earliest_start = await self._calculate_earliest_start_for_task(task, scheduled_tasks)
            task.scheduled_start = max(earliest_start, start_date)
            task.scheduled_end = task.scheduled_start + task.estimated_duration
            scheduled_tasks.append(task)
        
        # Schedule non-critical tasks with resource leveling
        priority_order = {TaskPriority.CRITICAL: 5, TaskPriority.HIGH: 4, TaskPriority.MEDIUM: 3, TaskPriority.LOW: 2, TaskPriority.DEFERRED: 1}
        non_critical_tasks.sort(key=lambda t: priority_order[t.priority], reverse=True)
        
        for task in non_critical_tasks:
            earliest_start = await self._calculate_earliest_start_for_task(task, scheduled_tasks)
            task.scheduled_start = max(earliest_start, start_date)
            task.scheduled_end = task.scheduled_start + task.estimated_duration
            scheduled_tasks.append(task)
        
        return scheduled_tasks
    
    async def _calculate_earliest_start_for_task(
        self,
        task: ScheduledTask,
        scheduled_tasks: List[ScheduledTask]
    ) -> datetime:
        """Calculate earliest possible start time for task"""
        if not task.dependencies:
            return datetime.now(timezone.utc)
        
        max_predecessor_end = datetime.now(timezone.utc)
        
        for dep in task.dependencies:
            pred_task = next(
                (t for t in scheduled_tasks if t.task_id == dep.predecessor_task_id),
                None
            )
            if pred_task and pred_task.scheduled_end:
                end_time = pred_task.scheduled_end + dep.lag_time
                max_predecessor_end = max(max_predecessor_end, end_time)
        
        return max_predecessor_end
    
    async def _find_optimal_start_with_resources(
        self,
        task: ScheduledTask,
        resource_timeline: Dict[str, List[Tuple[datetime, datetime, str]]],
        earliest_start: datetime
    ) -> datetime:
        """Find optimal start time considering resource availability"""
        if not task.resource_requirements:
            return earliest_start
        
        # Check resource availability starting from earliest start
        current_start = earliest_start
        max_attempts = 100  # Prevent infinite loops
        attempts = 0
        
        while attempts < max_attempts:
            current_end = current_start + task.estimated_duration
            
            # Check if all resources are available in this time window
            resources_available = True
            for req in task.resource_requirements:
                resource_schedule = resource_timeline.get(req.resource_id, [])
                
                for scheduled_start, scheduled_end, _ in resource_schedule:
                    if (current_start < scheduled_end and current_end > scheduled_start):
                        resources_available = False
                        # Move start time to after this conflict
                        current_start = scheduled_end
                        break
                
                if not resources_available:
                    break
            
            if resources_available:
                return current_start
            
            attempts += 1
        
        return current_start  # Return best attempt
    
    async def _calculate_earliest_start(self, task_id: str) -> Optional[datetime]:
        """Calculate earliest start time based on dependencies"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        if not task.dependencies:
            return datetime.now(timezone.utc)
        
        max_end_time = datetime.now(timezone.utc)
        
        for dep in task.dependencies:
            pred_task = self.tasks.get(dep.predecessor_task_id)
            if pred_task and pred_task.scheduled_end:
                end_time = pred_task.scheduled_end + dep.lag_time
                max_end_time = max(max_end_time, end_time)
        
        return max_end_time
    
    async def _find_dependent_tasks(self, task_id: str) -> List[ScheduledTask]:
        """Find all tasks that depend on the given task"""
        dependent_tasks = []
        
        for task in self.tasks.values():
            for dep in task.dependencies:
                if dep.predecessor_task_id == task_id:
                    dependent_tasks.append(task)
        
        return dependent_tasks
    
    # AI scoring methods
    
    async def _calculate_complexity_score(
        self,
        name: str,
        description: str,
        duration: timedelta,
        resources: List[ResourceRequirement]
    ) -> float:
        """Calculate AI-based complexity score"""
        score = 1.0
        
        # Duration factor
        if duration.total_seconds() > 40 * 3600:  # > 1 week
            score += 2.0
        elif duration.total_seconds() > 8 * 3600:  # > 1 day
            score += 1.0
        
        # Resource complexity
        score += len(resources) * 0.5
        
        # Description complexity (simplified NLP)
        complex_keywords = ["integrate", "complex", "advanced", "multiple", "coordinate", "synchronize"]
        for keyword in complex_keywords:
            if keyword in description.lower():
                score += 0.5
        
        return min(score, 10.0)
    
    async def _calculate_risk_score(
        self,
        duration: timedelta,
        deadline: Optional[datetime],
        priority: TaskPriority,
        complexity_score: float
    ) -> float:
        """Calculate AI-based risk score"""
        risk = 0.0
        
        # Complexity risk
        risk += complexity_score / 20.0  # Normalize to 0-0.5
        
        # Deadline pressure
        if deadline:
            time_to_deadline = deadline - datetime.now(timezone.utc)
            if time_to_deadline < duration * 1.2:  # Less than 20% buffer
                risk += 0.3
        
        # Priority risk
        if priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]:
            risk += 0.2
        
        return min(risk, 1.0)
    
    async def _assess_automation_potential(
        self,
        name: str,
        description: str,
        metadata: Dict[str, Any]
    ) -> float:
        """Assess automation potential using AI"""
        potential = 0.0
        
        # Check for automation keywords
        automation_keywords = ["automated", "script", "batch", "routine", "repetitive", "template"]
        for keyword in automation_keywords:
            if keyword in description.lower() or keyword in name.lower():
                potential += 0.2
        
        # Check metadata for automation hints
        if metadata.get("automation_ready", False):
            potential += 0.3
        
        if metadata.get("manual_only", False):
            potential = 0.0
        
        return min(potential, 1.0)
    
    # Resource allocation and optimization methods
    
    async def _allocate_resources(self, tasks: List[ScheduledTask]) -> List[ResourceAllocation]:
        """Allocate resources to scheduled tasks"""
        allocations = []
        
        for task in tasks:
            if not task.scheduled_start or not task.scheduled_end:
                continue
            
            for req in task.resource_requirements:
                allocation_id = str(uuid.uuid4())
                allocation = ResourceAllocation(
                    allocation_id=allocation_id,
                    task_id=task.task_id,
                    resource_id=req.resource_id,
                    resource_type=req.resource_type,
                    allocated_quantity=req.quantity,
                    allocation_start=task.scheduled_start,
                    allocation_end=task.scheduled_end,
                    utilization_rate=req.quantity,  # Simplified
                    is_confirmed=True
                )
                allocations.append(allocation)
        
        return allocations
    
    async def _optimize_for_time(
        self,
        tasks: List[ScheduledTask],
        allocations: List[ResourceAllocation]
    ) -> Tuple[List[ScheduledTask], List[ResourceAllocation]]:
        """Optimize schedule for minimum time"""
        # Find parallel execution opportunities
        optimized_tasks = tasks.copy()
        
        # Group tasks that can run in parallel
        parallel_groups = await self._find_parallel_groups(optimized_tasks)
        
        # Adjust start times for parallel execution
        for group in parallel_groups:
            earliest_start = min(task.scheduled_start for task in group if task.scheduled_start)
            for task in group:
                if task.scheduled_start and task.scheduled_start > earliest_start:
                    task.scheduled_start = earliest_start
                    task.scheduled_end = earliest_start + task.estimated_duration
        
        return optimized_tasks, allocations
    
    async def _optimize_for_resources(
        self,
        tasks: List[ScheduledTask],
        allocations: List[ResourceAllocation]
    ) -> Tuple[List[ScheduledTask], List[ResourceAllocation]]:
        """Optimize schedule for resource utilization"""
        # Implement resource leveling
        optimized_tasks = tasks.copy()
        
        # Sort by resource requirements
        optimized_tasks.sort(key=lambda t: len(t.resource_requirements), reverse=True)
        
        # Reschedule to balance resource usage
        for i, task in enumerate(optimized_tasks):
            if i > 0:
                # Check for resource conflicts with previous tasks
                conflicting_tasks = [
                    t for t in optimized_tasks[:i]
                    if self._has_resource_conflict(task, t)
                ]
                
                if conflicting_tasks:
                    # Delay task to avoid conflicts
                    latest_end = max(t.scheduled_end for t in conflicting_tasks if t.scheduled_end)
                    task.scheduled_start = latest_end
                    task.scheduled_end = latest_end + task.estimated_duration
        
        return optimized_tasks, allocations
    
    async def _find_parallel_groups(self, tasks: List[ScheduledTask]) -> List[List[ScheduledTask]]:
        """Find groups of tasks that can execute in parallel"""
        groups = []
        processed = set()
        
        for task in tasks:
            if task.task_id in processed:
                continue
            
            group = [task]
            processed.add(task.task_id)
            
            # Find tasks that can run in parallel with this task
            for other_task in tasks:
                if (other_task.task_id not in processed and
                    await self._can_run_in_parallel(task, other_task)):
                    group.append(other_task)
                    processed.add(other_task.task_id)
            
            if len(group) > 1:
                groups.append(group)
        
        return groups
    
    async def _can_run_in_parallel(self, task1: ScheduledTask, task2: ScheduledTask) -> bool:
        """Check if two tasks can run in parallel"""
        # Check for dependency conflicts
        if any(dep.predecessor_task_id == task2.task_id for dep in task1.dependencies):
            return False
        if any(dep.predecessor_task_id == task1.task_id for dep in task2.dependencies):
            return False
        
        # Check for resource conflicts
        if self._has_resource_conflict(task1, task2):
            return False
        
        # Check for assignee conflicts
        if (task1.assignee_id and task2.assignee_id and 
            task1.assignee_id == task2.assignee_id):
            return False
        
        return True
    
    def _has_resource_conflict(self, task1: ScheduledTask, task2: ScheduledTask) -> bool:
        """Check if two tasks have resource conflicts"""
        task1_resources = {req.resource_id for req in task1.resource_requirements if req.is_exclusive}
        task2_resources = {req.resource_id for req in task2.resource_requirements if req.is_exclusive}
        
        return bool(task1_resources.intersection(task2_resources))
    
    # Calculation and analysis methods
    
    async def _calculate_total_duration(self, tasks: List[ScheduledTask]) -> timedelta:
        """Calculate total project duration"""
        if not tasks:
            return timedelta(0)
        
        earliest_start = min(
            task.scheduled_start for task in tasks 
            if task.scheduled_start
        )
        latest_end = max(
            task.scheduled_end for task in tasks 
            if task.scheduled_end
        )
        
        return latest_end - earliest_start if earliest_start and latest_end else timedelta(0)
    
    async def _calculate_resource_utilization(
        self,
        allocations: List[ResourceAllocation]
    ) -> Dict[str, float]:
        """Calculate resource utilization rates"""
        utilization = {}
        
        # Group allocations by resource
        resource_allocations = defaultdict(list)
        for allocation in allocations:
            resource_allocations[allocation.resource_id].append(allocation)
        
        # Calculate utilization for each resource
        for resource_id, resource_allocs in resource_allocations.items():
            total_allocated_time = sum(
                (alloc.allocation_end - alloc.allocation_start).total_seconds()
                for alloc in resource_allocs
            )
            
            # Calculate available time (simplified - assume 8 hours/day)
            if resource_allocs:
                earliest = min(alloc.allocation_start for alloc in resource_allocs)
                latest = max(alloc.allocation_end for alloc in resource_allocs)
                total_available_time = (latest - earliest).total_seconds()
                
                utilization[resource_id] = (total_allocated_time / max(total_available_time, 1)) * 100
        
        return utilization
    
    async def _calculate_optimization_score(
        self,
        tasks: List[ScheduledTask],
        allocations: List[ResourceAllocation],
        strategy: SchedulingStrategy
    ) -> float:
        """Calculate optimization score based on multiple factors"""
        score = 0.0
        
        # Time efficiency (30%)
        total_duration = await self._calculate_total_duration(tasks)
        estimated_duration = sum(task.estimated_duration for task in tasks)
        if estimated_duration.total_seconds() > 0:
            time_efficiency = min(estimated_duration.total_seconds() / total_duration.total_seconds(), 1.0)
            score += time_efficiency * 30
        
        # Resource utilization (30%)
        resource_util = await self._calculate_resource_utilization(allocations)
        avg_utilization = sum(resource_util.values()) / max(len(resource_util), 1) / 100
        score += min(avg_utilization, 1.0) * 30
        
        # Priority adherence (20%)
        high_priority_tasks = [t for t in tasks if t.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]]
        early_scheduled = len([
            t for t in high_priority_tasks 
            if t.scheduled_start and t.scheduled_start <= datetime.now(timezone.utc) + timedelta(days=1)
        ])
        priority_score = early_scheduled / max(len(high_priority_tasks), 1)
        score += priority_score * 20
        
        # Dependency compliance (20%)
        dependency_score = 1.0  # Simplified - assume all dependencies are properly handled
        score += dependency_score * 20
        
        return min(score, 100.0)
    
    async def _detect_conflicts(
        self,
        tasks: List[ScheduledTask],
        allocations: List[ResourceAllocation]
    ) -> List[str]:
        """Detect scheduling conflicts"""
        conflicts = []
        
        # Resource conflicts
        resource_timeline = defaultdict(list)
        for allocation in allocations:
            resource_timeline[allocation.resource_id].append(
                (allocation.allocation_start, allocation.allocation_end, allocation.task_id)
            )
        
        for resource_id, timeline in resource_timeline.items():
            timeline.sort(key=lambda x: x[0])  # Sort by start time
            
            for i in range(len(timeline) - 1):
                current_end = timeline[i][1]
                next_start = timeline[i + 1][0]
                
                if current_end > next_start:
                    conflicts.append(
                        f"Resource conflict: {resource_id} double-booked between "
                        f"tasks {timeline[i][2]} and {timeline[i + 1][2]}"
                    )
        
        # Deadline conflicts
        for task in tasks:
            if (task.deadline and task.scheduled_end and 
                task.scheduled_end > task.deadline):
                conflicts.append(
                    f"Deadline conflict: Task {task.task_id} scheduled to finish "
                    f"after deadline ({task.scheduled_end} > {task.deadline})"
                )
        
        return conflicts
    
    async def _generate_warnings(
        self,
        tasks: List[ScheduledTask],
        allocations: List[ResourceAllocation]
    ) -> List[str]:
        """Generate scheduling warnings"""
        warnings = []
        
        # High-risk tasks
        high_risk_tasks = [t for t in tasks if t.risk_score > 0.7]
        if high_risk_tasks:
            warnings.append(
                f"{len(high_risk_tasks)} high-risk tasks identified - consider additional planning"
            )
        
        # Over-utilized resources
        resource_util = await self._calculate_resource_utilization(allocations)
        over_utilized = [r for r, util in resource_util.items() if util > 90]
        if over_utilized:
            warnings.append(
                f"Resources over-utilized (>90%): {', '.join(over_utilized)}"
            )
        
        # Critical path risks
        total_duration = await self._calculate_total_duration(tasks)
        if total_duration.days > 30:
            warnings.append("Project duration exceeds 30 days - consider risk mitigation")
        
        return warnings


# Example usage
async def main():
    """Example usage of task scheduler"""
    scheduler = TaskScheduler()
    
    project_id = "project_001"
    
    # Add tasks
    task1 = await scheduler.add_task(
        name="Design UI Mockups",
        description="Create initial UI designs and wireframes",
        project_id=project_id,
        estimated_duration=timedelta(hours=16),
        priority=TaskPriority.HIGH,
        resource_requirements=[
            ResourceRequirement(
                resource_type=ResourceType.HUMAN,
                resource_id="designer_001",
                quantity=1.0,
                duration=timedelta(hours=16)
            )
        ]
    )
    
    task2 = await scheduler.add_task(
        name="Implement Frontend",
        description="Develop frontend components based on designs",
        project_id=project_id,
        estimated_duration=timedelta(hours=32),
        priority=TaskPriority.MEDIUM,
        resource_requirements=[
            ResourceRequirement(
                resource_type=ResourceType.HUMAN,
                resource_id="developer_001",
                quantity=1.0,
                duration=timedelta(hours=32)
            )
        ]
    )
    
    task3 = await scheduler.add_task(
        name="Testing and QA",
        description="Comprehensive testing of implemented features",
        project_id=project_id,
        estimated_duration=timedelta(hours=12),
        priority=TaskPriority.HIGH,
        resource_requirements=[
            ResourceRequirement(
                resource_type=ResourceType.HUMAN,
                resource_id="tester_001",
                quantity=1.0,
                duration=timedelta(hours=12)
            )
        ]
    )
    
    # Add dependencies
    await scheduler.add_dependency(
        predecessor_task_id=task1.task_id,
        successor_task_id=task2.task_id,
        dependency_type=DependencyType.FINISH_TO_START
    )
    
    await scheduler.add_dependency(
        predecessor_task_id=task2.task_id,
        successor_task_id=task3.task_id,
        dependency_type=DependencyType.FINISH_TO_START
    )
    
    # Schedule project
    start_date = datetime.now(timezone.utc) + timedelta(days=1)
    result = await scheduler.schedule_project(
        project_id=project_id,
        start_date=start_date,
        strategy=SchedulingStrategy.BALANCED
    )
    
    print(f"Project scheduled:")
    print(f"  Total duration: {result.total_duration}")
    print(f"  Critical path: {len(result.critical_path)} tasks")
    print(f"  Optimization score: {result.optimization_score:.1f}")
    print(f"  Conflicts: {len(result.conflicts)}")
    
    # Get recommendations
    recommendations = await scheduler.get_task_recommendations(task1.task_id)
    print(f"Recommendations for task 1: {len(recommendations.get('optimization_opportunities', []))}")
    
    # Analyze performance
    analysis = await scheduler.analyze_schedule_performance(result.schedule_id)
    print(f"Performance analysis: {analysis.get('overall_performance', {})}")


if __name__ == "__main__":
    asyncio.run(main())