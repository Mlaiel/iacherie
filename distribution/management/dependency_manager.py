"""
Publication Dependency Manager
============================

Advanced dependency management system for Ainflue Distribution Platform.
Handles complex publication workflows with dependencies, prerequisites, and conditional logic.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Union, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
import json
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class DependencyType(Enum):
    """Types of publication dependencies"""
    SEQUENTIAL = "sequential"  # Must execute in order
    PREREQUISITE = "prerequisite"  # Must complete before dependent can start
    CONDITIONAL = "conditional"  # Execute only if condition is met
    PARALLEL = "parallel"  # Can execute simultaneously
    DELAYED = "delayed"  # Execute after time delay
    SUCCESS_DEPENDENT = "success_dependent"  # Execute only if dependency succeeds
    FAILURE_DEPENDENT = "failure_dependent"  # Execute only if dependency fails

class ExecutionStatus(Enum):
    """Execution status for publications"""
    PENDING = "pending"
    WAITING_DEPENDENCIES = "waiting_dependencies"
    READY = "ready"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"

class ConditionType(Enum):
    """Types of conditional logic"""
    ENGAGEMENT_THRESHOLD = "engagement_threshold"
    TIME_BASED = "time_based"
    PLATFORM_STATUS = "platform_status"
    CONTENT_PERFORMANCE = "content_performance"
    CUSTOM_FUNCTION = "custom_function"
    API_RESPONSE = "api_response"

@dataclass
class Condition:
    """Conditional logic for dependencies"""
    condition_type: ConditionType
    parameters: Dict[str, Any] = field(default_factory=dict)
    expected_result: Any = True
    timeout_seconds: int = 300
    
    def __post_init__(self):
        if not self.parameters:
            self.parameters = {}

@dataclass
class Dependency:
    """Publication dependency definition"""
    dependency_id: str
    dependency_type: DependencyType
    source_publication_id: str
    target_publication_id: str
    delay_seconds: int = 0
    condition: Optional[Condition] = None
    priority: int = 1
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class Publication:
    """Publication item with dependencies"""
    publication_id: str
    content_id: str
    platform: str
    scheduled_time: datetime
    status: ExecutionStatus = ExecutionStatus.PENDING
    dependencies: List[str] = field(default_factory=list)  # List of dependency IDs
    dependents: List[str] = field(default_factory=list)  # Publications depending on this
    execution_data: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowExecution:
    """Workflow execution tracking"""
    workflow_id: str
    publications: List[str]
    dependencies: List[str]
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    total_count: int = 0
    execution_log: List[Dict[str, Any]] = field(default_factory=list)

class DependencyManager:
    """
    Advanced publication dependency management system
    
    Features:
    - Complex dependency graphs
    - Conditional execution logic
    - Parallel and sequential workflows
    - Retry mechanisms with backoff
    - Timeout handling
    - Real-time monitoring
    - Workflow orchestration
    """
    
    def __init__(self):
        self.publications: Dict[str, Publication] = {}
        self.dependencies: Dict[str, Dependency] = {}
        self.workflows: Dict[str, WorkflowExecution] = {}
        self.condition_evaluators: Dict[ConditionType, Callable] = {}
        self.execution_queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        
        # Register default condition evaluators
        self._register_default_evaluators()
        
    def _register_default_evaluators(self):
        """Register default condition evaluators"""
        self.condition_evaluators[ConditionType.ENGAGEMENT_THRESHOLD] = self._evaluate_engagement_threshold
        self.condition_evaluators[ConditionType.TIME_BASED] = self._evaluate_time_based
        self.condition_evaluators[ConditionType.PLATFORM_STATUS] = self._evaluate_platform_status
        self.condition_evaluators[ConditionType.CONTENT_PERFORMANCE] = self._evaluate_content_performance
        
    async def add_publication(self, publication: Publication):
        """Add a publication to the dependency graph"""
        async with self._lock:
            self.publications[publication.publication_id] = publication
            logger.info(f"Added publication {publication.publication_id} for platform {publication.platform}")
            
    async def add_dependency(self, dependency: Dependency):
        """Add a dependency relationship"""
        async with self._lock:
            # Validate that both publications exist
            if dependency.source_publication_id not in self.publications:
                raise ValueError(f"Source publication {dependency.source_publication_id} not found")
            if dependency.target_publication_id not in self.publications:
                raise ValueError(f"Target publication {dependency.target_publication_id} not found")
                
            self.dependencies[dependency.dependency_id] = dependency
            
            # Update publication dependency lists
            source_pub = self.publications[dependency.source_publication_id]
            target_pub = self.publications[dependency.target_publication_id]
            
            if dependency.dependency_id not in target_pub.dependencies:
                target_pub.dependencies.append(dependency.dependency_id)
            if dependency.dependency_id not in source_pub.dependents:
                source_pub.dependents.append(dependency.dependency_id)
                
            logger.info(f"Added dependency {dependency.dependency_id}: {dependency.source_publication_id} -> {dependency.target_publication_id}")
            
    async def create_workflow(self, workflow_id: str, publication_ids: List[str]) -> WorkflowExecution:
        """Create a workflow from a list of publications"""
        async with self._lock:
            # Validate all publications exist
            for pub_id in publication_ids:
                if pub_id not in self.publications:
                    raise ValueError(f"Publication {pub_id} not found")
                    
            # Find relevant dependencies
            relevant_deps = []
            for dep_id, dependency in self.dependencies.items():
                if (dependency.source_publication_id in publication_ids and 
                    dependency.target_publication_id in publication_ids):
                    relevant_deps.append(dep_id)
                    
            workflow = WorkflowExecution(
                workflow_id=workflow_id,
                publications=publication_ids.copy(),
                dependencies=relevant_deps,
                total_count=len(publication_ids)
            )
            
            self.workflows[workflow_id] = workflow
            logger.info(f"Created workflow {workflow_id} with {len(publication_ids)} publications")
            
            return workflow
            
    async def execute_workflow(self, workflow_id: str) -> bool:
        """Execute a complete workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
            
        workflow = self.workflows[workflow_id]
        workflow.status = ExecutionStatus.EXECUTING
        workflow.started_at = datetime.now(timezone.utc)
        
        logger.info(f"Starting execution of workflow {workflow_id}")
        
        try:
            # Build execution graph
            execution_graph = await self._build_execution_graph(workflow.publications)
            
            # Execute in dependency order
            success = await self._execute_dependency_graph(execution_graph, workflow)
            
            workflow.status = ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
            workflow.completed_at = datetime.now(timezone.utc)
            
            logger.info(f"Workflow {workflow_id} completed with status {workflow.status.value}")
            return success
            
        except Exception as e:
            workflow.status = ExecutionStatus.FAILED
            workflow.completed_at = datetime.now(timezone.utc)
            logger.error(f"Workflow {workflow_id} failed: {e}")
            return False
            
    async def _build_execution_graph(self, publication_ids: List[str]) -> Dict[str, Set[str]]:
        """Build execution dependency graph"""
        graph = defaultdict(set)
        
        for pub_id in publication_ids:
            publication = self.publications[pub_id]
            
            # Find all dependencies for this publication
            for dep_id in publication.dependencies:
                if dep_id in self.dependencies:
                    dependency = self.dependencies[dep_id]
                    if dependency.source_publication_id in publication_ids:
                        graph[pub_id].add(dependency.source_publication_id)
                        
        return dict(graph)
        
    async def _execute_dependency_graph(
        self, 
        graph: Dict[str, Set[str]], 
        workflow: WorkflowExecution
    ) -> bool:
        """Execute publications in dependency order"""
        # Topological sort to determine execution order
        execution_order = await self._topological_sort(graph)
        
        if not execution_order:
            logger.error("Circular dependency detected in workflow")
            return False
            
        # Execute publications in batches (parallel where possible)
        executed = set()
        
        for batch in execution_order:
            logger.info(f"Executing batch: {batch}")
            
            # Execute all publications in this batch in parallel
            tasks = []
            for pub_id in batch:
                if await self._can_execute_publication(pub_id, executed):
                    task = asyncio.create_task(self._execute_publication(pub_id, workflow))
                    tasks.append((pub_id, task))
                    
            # Wait for all tasks in batch to complete
            batch_success = True
            for pub_id, task in tasks:
                try:
                    success = await task
                    if success:
                        executed.add(pub_id)
                        workflow.success_count += 1
                    else:
                        workflow.failure_count += 1
                        batch_success = False
                        
                except Exception as e:
                    logger.error(f"Publication {pub_id} failed: {e}")
                    workflow.failure_count += 1
                    batch_success = False
                    
            # If any publication in batch failed and is critical, stop workflow
            if not batch_success:
                # Check if any failed publications have critical dependencies
                for pub_id in batch:
                    if pub_id not in executed:
                        if await self._is_critical_failure(pub_id):
                            logger.error(f"Critical publication {pub_id} failed, stopping workflow")
                            return False
                            
        return workflow.failure_count == 0
        
    async def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Perform topological sort to determine execution order"""
        # Calculate in-degrees
        in_degree = defaultdict(int)
        all_nodes = set(graph.keys())
        
        for node in graph:
            all_nodes.update(graph[node])
            
        for node in all_nodes:
            in_degree[node] = 0
            
        for node in graph:
            for neighbor in graph[node]:
                in_degree[node] += 1
                
        # Kahn's algorithm with batching
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        result = []
        
        while queue:
            # Process all nodes with no dependencies in parallel
            batch = []
            batch_size = len(queue)
            
            for _ in range(batch_size):
                node = queue.popleft()
                batch.append(node)
                
                # Reduce in-degree for neighbors
                for neighbor in all_nodes:
                    if node in graph.get(neighbor, set()):
                        in_degree[neighbor] -= 1
                        if in_degree[neighbor] == 0:
                            queue.append(neighbor)
                            
            if batch:
                result.append(batch)
                
        # Check for cycles
        total_processed = sum(len(batch) for batch in result)
        if total_processed != len(all_nodes):
            return []  # Circular dependency detected
            
        return result
        
    async def _can_execute_publication(self, pub_id: str, executed: Set[str]) -> bool:
        """Check if publication can be executed based on dependencies"""
        publication = self.publications[pub_id]
        
        # Check all dependencies
        for dep_id in publication.dependencies:
            if dep_id not in self.dependencies:
                continue
                
            dependency = self.dependencies[dep_id]
            source_pub_id = dependency.source_publication_id
            
            # Check dependency type requirements
            if dependency.dependency_type == DependencyType.PREREQUISITE:
                if source_pub_id not in executed:
                    return False
                source_pub = self.publications[source_pub_id]
                if source_pub.status != ExecutionStatus.SUCCESS:
                    return False
                    
            elif dependency.dependency_type == DependencyType.SUCCESS_DEPENDENT:
                if source_pub_id not in executed:
                    return False
                source_pub = self.publications[source_pub_id]
                if source_pub.status != ExecutionStatus.SUCCESS:
                    return False
                    
            elif dependency.dependency_type == DependencyType.FAILURE_DEPENDENT:
                if source_pub_id not in executed:
                    return False
                source_pub = self.publications[source_pub_id]
                if source_pub.status == ExecutionStatus.SUCCESS:
                    return False
                    
            # Check conditional dependencies
            if dependency.condition:
                try:
                    condition_met = await self._evaluate_condition(dependency.condition, dependency)
                    if not condition_met:
                        return False
                except Exception as e:
                    logger.error(f"Error evaluating condition for dependency {dep_id}: {e}")
                    return False
                    
        return True
        
    async def _execute_publication(self, pub_id: str, workflow: WorkflowExecution) -> bool:
        """Execute a single publication"""
        publication = self.publications[pub_id]
        publication.status = ExecutionStatus.EXECUTING
        publication.started_at = datetime.now(timezone.utc)
        
        workflow.execution_log.append({
            "publication_id": pub_id,
            "action": "started",
            "timestamp": publication.started_at.isoformat(),
            "platform": publication.platform
        })
        
        try:
            # Apply delays from dependencies
            await self._apply_dependency_delays(pub_id)
            
            # Simulate publication execution (replace with actual platform API calls)
            await self._simulate_publication_execution(publication)
            
            publication.status = ExecutionStatus.SUCCESS
            publication.completed_at = datetime.now(timezone.utc)
            
            workflow.execution_log.append({
                "publication_id": pub_id,
                "action": "completed",
                "timestamp": publication.completed_at.isoformat(),
                "status": "success"
            })
            
            logger.info(f"Publication {pub_id} executed successfully")
            return True
            
        except Exception as e:
            publication.status = ExecutionStatus.FAILED
            publication.completed_at = datetime.now(timezone.utc)
            publication.error_message = str(e)
            
            workflow.execution_log.append({
                "publication_id": pub_id,
                "action": "failed",
                "timestamp": publication.completed_at.isoformat(),
                "error": str(e)
            })
            
            logger.error(f"Publication {pub_id} failed: {e}")
            
            # Attempt retry if configured
            if publication.retry_count < publication.max_retries:
                publication.retry_count += 1
                publication.status = ExecutionStatus.PENDING
                logger.info(f"Retrying publication {pub_id} (attempt {publication.retry_count})")
                
                # Exponential backoff
                await asyncio.sleep(2 ** publication.retry_count)
                return await self._execute_publication(pub_id, workflow)
                
            return False
            
    async def _apply_dependency_delays(self, pub_id: str):
        """Apply delays specified in dependencies"""
        publication = self.publications[pub_id]
        
        for dep_id in publication.dependencies:
            if dep_id in self.dependencies:
                dependency = self.dependencies[dep_id]
                if dependency.delay_seconds > 0:
                    logger.info(f"Applying {dependency.delay_seconds}s delay for dependency {dep_id}")
                    await asyncio.sleep(dependency.delay_seconds)
                    
    async def _simulate_publication_execution(self, publication: Publication):
        """Simulate publication execution (replace with actual implementation)"""
        # Simulate variable execution time
        execution_time = min(max(0.5, publication.metadata.get("complexity", 1) * 0.5), 5.0)
        await asyncio.sleep(execution_time)
        
        # Simulate occasional failures
        failure_rate = publication.metadata.get("failure_rate", 0.05)
        if failure_rate > 0 and asyncio.get_event_loop().time() % 100 < failure_rate * 100:
            raise Exception(f"Simulated failure for {publication.platform}")
            
        # Set result
        publication.result = {
            "platform": publication.platform,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "post_id": f"post_{uuid.uuid4().hex[:8]}",
            "url": f"https://{publication.platform}.com/post/{uuid.uuid4().hex[:8]}"
        }
        
    async def _evaluate_condition(self, condition: Condition, dependency: Dependency) -> bool:
        """Evaluate a dependency condition"""
        if condition.condition_type not in self.condition_evaluators:
            logger.warning(f"No evaluator for condition type {condition.condition_type}")
            return True
            
        evaluator = self.condition_evaluators[condition.condition_type]
        
        try:
            result = await evaluator(condition, dependency)
            return result == condition.expected_result
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
            
    async def _evaluate_engagement_threshold(self, condition: Condition, dependency: Dependency) -> bool:
        """Evaluate engagement threshold condition"""
        threshold = condition.parameters.get("threshold", 0.05)
        metric = condition.parameters.get("metric", "engagement_rate")
        
        # Get source publication result
        source_pub = self.publications[dependency.source_publication_id]
        if not source_pub.result:
            return False
            
        # Simulate getting engagement metrics (replace with actual API calls)
        engagement_data = source_pub.result.get("engagement", {})
        current_value = engagement_data.get(metric, 0.0)
        
        return current_value >= threshold
        
    async def _evaluate_time_based(self, condition: Condition, dependency: Dependency) -> bool:
        """Evaluate time-based condition"""
        time_type = condition.parameters.get("type", "after")
        target_time = condition.parameters.get("time")
        
        if not target_time:
            return True
            
        current_time = datetime.now(timezone.utc)
        
        if isinstance(target_time, str):
            target_time = datetime.fromisoformat(target_time.replace('Z', '+00:00'))
            
        if time_type == "after":
            return current_time >= target_time
        elif time_type == "before":
            return current_time <= target_time
            
        return True
        
    async def _evaluate_platform_status(self, condition: Condition, dependency: Dependency) -> bool:
        """Evaluate platform status condition"""
        platform = condition.parameters.get("platform")
        expected_status = condition.parameters.get("status", "online")
        
        # Simulate platform status check (replace with actual implementation)
        # For now, assume all platforms are online
        return True
        
    async def _evaluate_content_performance(self, condition: Condition, dependency: Dependency) -> bool:
        """Evaluate content performance condition"""
        metric = condition.parameters.get("metric", "views")
        threshold = condition.parameters.get("threshold", 1000)
        
        # Get source publication performance
        source_pub = self.publications[dependency.source_publication_id]
        if not source_pub.result:
            return False
            
        # Simulate getting performance metrics
        performance = source_pub.result.get("performance", {})
        current_value = performance.get(metric, 0)
        
        return current_value >= threshold
        
    async def _is_critical_failure(self, pub_id: str) -> bool:
        """Check if publication failure is critical to workflow"""
        publication = self.publications[pub_id]
        
        # Check if this publication has dependents
        has_dependents = len(publication.dependents) > 0
        
        # Check if marked as critical in metadata
        is_critical = publication.metadata.get("critical", False)
        
        return has_dependents or is_critical
        
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get detailed workflow status"""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}
            
        workflow = self.workflows[workflow_id]
        
        publication_statuses = {}
        for pub_id in workflow.publications:
            pub = self.publications[pub_id]
            publication_statuses[pub_id] = {
                "status": pub.status.value,
                "platform": pub.platform,
                "started_at": pub.started_at.isoformat() if pub.started_at else None,
                "completed_at": pub.completed_at.isoformat() if pub.completed_at else None,
                "retry_count": pub.retry_count,
                "error_message": pub.error_message
            }
            
        return {
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "success_count": workflow.success_count,
            "failure_count": workflow.failure_count,
            "total_count": workflow.total_count,
            "publications": publication_statuses,
            "execution_log": workflow.execution_log
        }
        
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        if workflow_id not in self.workflows:
            return False
            
        workflow = self.workflows[workflow_id]
        workflow.status = ExecutionStatus.CANCELLED
        workflow.completed_at = datetime.now(timezone.utc)
        
        # Cancel all pending publications
        for pub_id in workflow.publications:
            pub = self.publications[pub_id]
            if pub.status in [ExecutionStatus.PENDING, ExecutionStatus.WAITING_DEPENDENCIES, ExecutionStatus.READY]:
                pub.status = ExecutionStatus.CANCELLED
                
        logger.info(f"Cancelled workflow {workflow_id}")
        return True

# Usage example
async def example_usage():
    """Example usage of DependencyManager"""
    manager = DependencyManager()
    
    # Create publications
    pub1 = Publication(
        publication_id="pub_1",
        content_id="content_123",
        platform="instagram",
        scheduled_time=datetime.now(timezone.utc) + timedelta(minutes=5)
    )
    
    pub2 = Publication(
        publication_id="pub_2", 
        content_id="content_123",
        platform="twitter",
        scheduled_time=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    
    pub3 = Publication(
        publication_id="pub_3",
        content_id="content_123", 
        platform="facebook",
        scheduled_time=datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    
    # Add publications
    await manager.add_publication(pub1)
    await manager.add_publication(pub2)
    await manager.add_publication(pub3)
    
    # Create dependencies
    # pub2 depends on pub1 success
    dep1 = Dependency(
        dependency_id="dep_1",
        dependency_type=DependencyType.SUCCESS_DEPENDENT,
        source_publication_id="pub_1",
        target_publication_id="pub_2",
        delay_seconds=30
    )
    
    # pub3 depends on pub2 with engagement condition
    dep2 = Dependency(
        dependency_id="dep_2",
        dependency_type=DependencyType.CONDITIONAL,
        source_publication_id="pub_2",
        target_publication_id="pub_3",
        condition=Condition(
            condition_type=ConditionType.ENGAGEMENT_THRESHOLD,
            parameters={"threshold": 0.05, "metric": "engagement_rate"},
            expected_result=True
        )
    )
    
    # Add dependencies
    await manager.add_dependency(dep1)
    await manager.add_dependency(dep2)
    
    # Create and execute workflow
    workflow = await manager.create_workflow("workflow_1", ["pub_1", "pub_2", "pub_3"])
    success = await manager.execute_workflow("workflow_1")
    
    print(f"Workflow completed successfully: {success}")
    
    # Get status
    status = await manager.get_workflow_status("workflow_1")
    print(f"Workflow status: {json.dumps(status, indent=2)}")

if __name__ == "__main__":
    asyncio.run(example_usage())