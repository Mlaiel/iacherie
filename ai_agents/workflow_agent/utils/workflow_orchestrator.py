"""
IA-Influencer Agent - Advanced Workflow Orchestrator

Enterprise-grade workflow orchestration system for multi-format content creators.
Handles complex business process orchestration with AI-powered optimization.

Key Features:
- Dynamic workflow orchestration
- Multi-step process management
- Parallel execution optimization
- Error recovery and retry logic
- Workflow dependency management
- Resource allocation optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 - All Rights Reserved

 IMPORTANT LEGAL NOTICE 
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from collections import defaultdict, deque
import networkx as nx
import traceback
from contextlib import asynccontextmanager

from ..base import BaseAgent


class OrchestrationStrategy(Enum):
    """Workflow orchestration strategy enumeration."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    MIXED = "mixed"
    ADAPTIVE = "adaptive"
    PRIORITY_BASED = "priority_based"
    RESOURCE_OPTIMIZED = "resource_optimized"


class ResourceType(Enum):
    """Resource type enumeration."""
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    STORAGE = "storage"
    GPU = "gpu"
    DATABASE = "database"


@dataclass
class WorkflowNode:
    """Represents a workflow node with execution details."""
    id: str
    name: str
    task_type: str
    executor: Callable
    dependencies: Set[str] = field(default_factory=set)
    resources: Dict[ResourceType, float] = field(default_factory=dict)
    timeout: Optional[int] = None
    retry_count: int = 3
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post initialization setup."""
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class ExecutionContext:
    """Workflow execution context."""
    workflow_id: str
    user_id: str
    session_id: str
    environment: str
    variables: Dict[str, Any] = field(default_factory=dict)
    resources: Dict[ResourceType, float] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Workflow execution result."""
    node_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    resources_used: Dict[ResourceType, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowOrchestrator(BaseAgent):
    """
    Advanced workflow orchestrator for enterprise content creation workflows.
    
    This orchestrator provides sophisticated workflow management capabilities
    including dynamic scheduling, resource optimization, and intelligent
    execution strategies.
    """

    def __init__(self):
        """Initialize the workflow orchestrator."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.workflow_graph = nx.DiGraph()
        self.execution_contexts: Dict[str, ExecutionContext] = {}
        self.execution_results: Dict[str, Dict[str, ExecutionResult]] = defaultdict(dict)
        self.active_workflows: Set[str] = set()
        
        # Resource management
        self.available_resources = {
            ResourceType.CPU: 100.0,
            ResourceType.MEMORY: 16384.0,  # MB
            ResourceType.NETWORK: 1000.0,  # Mbps
            ResourceType.STORAGE: 100000.0,  # MB
            ResourceType.GPU: 8.0,  # GPU units
            ResourceType.DATABASE: 1000.0  # Connection pool
        }
        
        self.resource_locks = {resource: asyncio.Lock() for resource in ResourceType}
        
        # Execution engines
        self.thread_executor = ThreadPoolExecutor(max_workers=50)
        self.process_executor = ProcessPoolExecutor(max_workers=10)
        
        # Statistics and monitoring
        self.execution_stats = {
            'total_workflows': 0,
            'successful_workflows': 0,
            'failed_workflows': 0,
            'average_execution_time': 0.0,
            'resource_utilization': defaultdict(float)
        }

    async def orchestrate_workflow(
        self,
        workflow_definition: Dict[str, Any],
        context: ExecutionContext,
        strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE
    ) -> Dict[str, Any]:
        """
        Orchestrate a complete workflow execution.
        
        Args:
            workflow_definition: Complete workflow definition
            context: Execution context
            strategy: Orchestration strategy to use
            
        Returns:
            Dict containing workflow execution results
        """



        try:
            workflow_id = context.workflow_id
            self.logger.info(f"Starting workflow orchestration: {workflow_id}")
            
            # Build workflow graph
            await self._build_workflow_graph(workflow_definition, workflow_id)
            
            # Validate workflow
            validation_result = await self._validate_workflow(workflow_id)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f"Workflow validation failed: {validation_result['errors']}",
                    'workflow_id': workflow_id
                }
            
            # Register execution context
            self.execution_contexts[workflow_id] = context
            self.active_workflows.add(workflow_id)
            
            # Execute workflow based on strategy
            execution_result = await self._execute_workflow_strategy(
                workflow_id, strategy
            )
            
            # Update statistics
            self._update_execution_stats(workflow_id, execution_result)
            
            return {
                'success': execution_result['success'],
                'workflow_id': workflow_id,
                'results': execution_result['results'],
                'execution_time': execution_result['execution_time'],
                'nodes_executed': execution_result['nodes_executed'],
                'resource_usage': execution_result['resource_usage']
            }
            
        except Exception as e:
            self.logger.error(f"Workflow orchestration error: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'workflow_id': context.workflow_id
            }
        finally:
            # Cleanup
            if context.workflow_id in self.active_workflows:
                self.active_workflows.remove(context.workflow_id)

    async def _build_workflow_graph(
        self,
        workflow_definition: Dict[str, Any],
        workflow_id: str
    ):
        """Build workflow execution graph from definition."""



        try:
            nodes = workflow_definition.get('nodes', [])
            edges = workflow_definition.get('edges', [])
            
            # Create workflow subgraph
            subgraph_nodes = []
            
            for node_def in nodes:
                node = WorkflowNode(
                    id=node_def['id'],
                    name=node_def['name'],
                    task_type=node_def['task_type'],
                    executor=self._resolve_executor(node_def['executor']),
                    dependencies=set(node_def.get('dependencies', [])),
                    resources=self._parse_resources(node_def.get('resources', {})),
                    timeout=node_def.get('timeout'),
                    retry_count=node_def.get('retry_count', 3),
                    priority=node_def.get('priority', 0),
                    metadata=node_def.get('metadata', {})
                )
                
                # Add to graph with workflow prefix
                node_id = f"{workflow_id}:{node.id}"
                self.workflow_graph.add_node(node_id, node=node)
                subgraph_nodes.append(node_id)
            
            # Add edges
            for edge in edges:
                from_node = f"{workflow_id}:{edge['from']}"
                to_node = f"{workflow_id}:{edge['to']}"
                
                if from_node in subgraph_nodes and to_node in subgraph_nodes:
                    self.workflow_graph.add_edge(
                        from_node,
                        to_node,
                        weight=edge.get('weight', 1.0),
                        condition=edge.get('condition')
                    )
            
            self.logger.info(f"Built workflow graph with {len(subgraph_nodes)} nodes")
            
        except Exception as e:
            self.logger.error(f"Error building workflow graph: {str(e)}")
            raise

    async def _validate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Validate workflow graph for execution."""



        try:
            errors = []
            
            # Get workflow nodes
            workflow_nodes = [
                node for node in self.workflow_graph.nodes()
                if node.startswith(f"{workflow_id}:")
            ]
            
            if not workflow_nodes:
                errors.append("No nodes found for workflow")
                return {'valid': False, 'errors': errors}
            
            # Check for cycles
            try:
                cycles = list(nx.simple_cycles(self.workflow_graph))
                workflow_cycles = [
                    cycle for cycle in cycles
                    if any(node.startswith(f"{workflow_id}:") for node in cycle)
                ]
                if workflow_cycles:
                    errors.append(f"Cycles detected: {workflow_cycles}")
            except Exception as e:
                self.logger.warning(f"Cycle detection error: {str(e)}")
            
            # Validate resource requirements
            total_resources = defaultdict(float)
            for node_id in workflow_nodes:
                node_data = self.workflow_graph.nodes[node_id]
                node = node_data['node']
                
                for resource_type, amount in node.resources.items():
                    total_resources[resource_type] += amount
            
            # Check resource availability
            for resource_type, required in total_resources.items():
                available = self.available_resources.get(resource_type, 0.0)
                if required > available:
                    errors.append(
                        f"Insufficient {resource_type.value}: "
                        f"required {required}, available {available}"
                    )
            
            # Validate executors
            for node_id in workflow_nodes:
                node_data = self.workflow_graph.nodes[node_id]
                node = node_data['node']
                
                if not callable(node.executor):
                    errors.append(f"Invalid executor for node {node.id}")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'resource_requirements': dict(total_resources)
            }
            
        except Exception as e:
            self.logger.error(f"Workflow validation error: {str(e)}")
            return {'valid': False, 'errors': [str(e)]}

    async def _execute_workflow_strategy(
        self,
        workflow_id: str,
        strategy: OrchestrationStrategy
    ) -> Dict[str, Any]:
        """Execute workflow using specified strategy."""
        start_time = datetime.now()
        
        try:
            if strategy == OrchestrationStrategy.SEQUENTIAL:
                result = await self._execute_sequential(workflow_id)
            elif strategy == OrchestrationStrategy.PARALLEL:
                result = await self._execute_parallel(workflow_id)
            elif strategy == OrchestrationStrategy.MIXED:
                result = await self._execute_mixed(workflow_id)
            elif strategy == OrchestrationStrategy.ADAPTIVE:
                result = await self._execute_adaptive(workflow_id)
            elif strategy == OrchestrationStrategy.PRIORITY_BASED:
                result = await self._execute_priority_based(workflow_id)
            elif strategy == OrchestrationStrategy.RESOURCE_OPTIMIZED:
                result = await self._execute_resource_optimized(workflow_id)
            else:
                result = await self._execute_adaptive(workflow_id)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result['execution_time'] = execution_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"Strategy execution error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': (datetime.now() - start_time).total_seconds(),
                'results': {},
                'nodes_executed': 0,
                'resource_usage': {}
            }

    async def _execute_adaptive(self, workflow_id: str) -> Dict[str, Any]:
        """Execute workflow using adaptive strategy."""



        try:
            # Analyze workflow characteristics
            analysis = await self._analyze_workflow_characteristics(workflow_id)
            
            # Choose optimal strategy based on analysis
            if analysis['node_count'] <= 5:
                return await self._execute_sequential(workflow_id)
            elif analysis['parallelization_potential'] > 0.7:
                return await self._execute_parallel(workflow_id)
            elif analysis['resource_intensity'] > 0.8:
                return await self._execute_resource_optimized(workflow_id)
            else:
                return await self._execute_mixed(workflow_id)
                
        except Exception as e:
            self.logger.error(f"Adaptive execution error: {str(e)}")
            return await self._execute_sequential(workflow_id)

    async def _execute_sequential(self, workflow_id: str) -> Dict[str, Any]:
        """Execute workflow nodes sequentially."""



        try:
            workflow_nodes = [
                node for node in self.workflow_graph.nodes()
                if node.startswith(f"{workflow_id}:")
            ]
            
            # Topological sort for execution order
            subgraph = self.workflow_graph.subgraph(workflow_nodes)
            execution_order = list(nx.topological_sort(subgraph))
            
            results = {}
            resource_usage = defaultdict(float)
            nodes_executed = 0
            
            for node_id in execution_order:
                node_data = self.workflow_graph.nodes[node_id]
                node = node_data['node']
                
                # Execute node
                result = await self._execute_node(
                    node, workflow_id, results
                )
                
                if result.success:
                    results[node.id] = result.result
                    nodes_executed += 1
                    
                    # Update resource usage
                    for resource_type, amount in result.resources_used.items():
                        resource_usage[resource_type] += amount
                else:
                    # Handle failure based on strategy
                    if node.retry_count > 0:
                        # Retry logic
                        for retry in range(node.retry_count):
                            result = await self._execute_node(
                                node, workflow_id, results
                            )
                            if result.success:
                                results[node.id] = result.result
                                nodes_executed += 1
                                break
                    
                    if not result.success:
                        return {
                            'success': False,
                            'error': f"Node {node.id} failed: {result.error}",
                            'results': results,
                            'nodes_executed': nodes_executed,
                            'resource_usage': dict(resource_usage)
                        }
            
            return {
                'success': True,
                'results': results,
                'nodes_executed': nodes_executed,
                'resource_usage': dict(resource_usage)
            }
            
        except Exception as e:
            self.logger.error(f"Sequential execution error: {str(e)}")
            raise

    async def _execute_parallel(self, workflow_id: str) -> Dict[str, Any]:
        """Execute workflow nodes in parallel where possible."""



        try:
            workflow_nodes = [
                node for node in self.workflow_graph.nodes()
                if node.startswith(f"{workflow_id}:")
            ]
            
            # Group nodes by execution levels
            execution_levels = self._compute_execution_levels(workflow_id)
            
            results = {}
            resource_usage = defaultdict(float)
            nodes_executed = 0
            
            for level, node_ids in execution_levels.items():
                # Execute all nodes in current level in parallel
                tasks = []
                for node_id in node_ids:
                    node_data = self.workflow_graph.nodes[node_id]
                    node = node_data['node']
                    
                    task = asyncio.create_task(
                        self._execute_node(node, workflow_id, results)
                    )
                    tasks.append((node, task))
                
                # Wait for all tasks in current level
                level_results = await asyncio.gather(
                    *[task for _, task in tasks],
                    return_exceptions=True
                )
                
                # Process results
                for (node, _), result in zip(tasks, level_results):
                    if isinstance(result, Exception):
                        return {
                            'success': False,
                            'error': f"Node {node.id} failed: {str(result)}",
                            'results': results,
                            'nodes_executed': nodes_executed,
                            'resource_usage': dict(resource_usage)
                        }
                    
                    if result.success:
                        results[node.id] = result.result
                        nodes_executed += 1
                        
                        for resource_type, amount in result.resources_used.items():
                            resource_usage[resource_type] += amount
            
            return {
                'success': True,
                'results': results,
                'nodes_executed': nodes_executed,
                'resource_usage': dict(resource_usage)
            }
            
        except Exception as e:
            self.logger.error(f"Parallel execution error: {str(e)}")
            raise

    async def _execute_node(
        self,
        node: WorkflowNode,
        workflow_id: str,
        context_results: Dict[str, Any]
    ) -> ExecutionResult:
        """Execute a single workflow node."""
        start_time = datetime.now()
        
        try:
            # Check resource availability
            await self._acquire_resources(node.resources)
            
            # Prepare execution context
            execution_context = {
                'node': node,
                'workflow_id': workflow_id,
                'results': context_results,
                'user_context': self.execution_contexts.get(workflow_id)
            }
            
            # Execute with timeout
            if node.timeout:
                result = await asyncio.wait_for(
                    node.executor(execution_context),
                    timeout=node.timeout
                )
            else:
                result = await node.executor(execution_context)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ExecutionResult(
                node_id=node.id,
                success=True,
                result=result,
                execution_time=execution_time,
                resources_used=node.resources.copy(),
                metadata={'executed_at': start_time.isoformat()}
            )
            
        except asyncio.TimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ExecutionResult(
                node_id=node.id,
                success=False,
                error="Execution timeout",
                execution_time=execution_time,
                resources_used=node.resources.copy()
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Node execution error for {node.id}: {str(e)}")
            
            return ExecutionResult(
                node_id=node.id,
                success=False,
                error=str(e),
                execution_time=execution_time,
                resources_used=node.resources.copy()
            )
        finally:
            # Release resources
            await self._release_resources(node.resources)

    def _resolve_executor(self, executor_definition: Union[str, Callable]) -> Callable:
        """Resolve executor from definition."""
        if callable(executor_definition):
            return executor_definition
        
        # Handle string-based executor resolution
        if isinstance(executor_definition, str):
            # Import and resolve from string
            # This would typically use a registry pattern
            return self._get_executor_from_registry(executor_definition)
        
        raise ValueError(f"Invalid executor definition: {executor_definition}")

    def _parse_resources(self, resources_dict: Dict[str, Any]) -> Dict[ResourceType, float]:
        """Parse resource requirements from dictionary."""
        parsed_resources = {}
        
        for resource_name, amount in resources_dict.items():
            try:
                resource_type = ResourceType(resource_name.lower())
                parsed_resources[resource_type] = float(amount)
            except ValueError:
                self.logger.warning(f"Unknown resource type: {resource_name}")
        
        return parsed_resources

    async def _acquire_resources(self, resources: Dict[ResourceType, float]):
        """Acquire required resources for execution."""
        acquired_resources = []
        
        try:
            for resource_type, amount in resources.items():
                async with self.resource_locks[resource_type]:
                    available = self.available_resources.get(resource_type, 0.0)
                    if available >= amount:
                        self.available_resources[resource_type] -= amount
                        acquired_resources.append((resource_type, amount))
                    else:
                        # Release already acquired resources
                        for res_type, res_amount in acquired_resources:
                            self.available_resources[res_type] += res_amount
                        raise RuntimeError(
                            f"Insufficient resources: {resource_type.value}"
                        )
                        
        except Exception as e:
            self.logger.error(f"Resource acquisition error: {str(e)}")
            raise

    async def _release_resources(self, resources: Dict[ResourceType, float]):
        """Release resources after execution."""
        for resource_type, amount in resources.items():
            async with self.resource_locks[resource_type]:
                self.available_resources[resource_type] += amount

    def _compute_execution_levels(self, workflow_id: str) -> Dict[int, List[str]]:
        """Compute execution levels for parallel execution."""
        workflow_nodes = [
            node for node in self.workflow_graph.nodes()
            if node.startswith(f"{workflow_id}:")
        ]
        
        subgraph = self.workflow_graph.subgraph(workflow_nodes)
        levels = defaultdict(list)
        
        # Compute the longest path from each node to determine levels
        for node in workflow_nodes:
            try:
                # Find all paths from roots to this node
                in_degree = subgraph.in_degree(node)
                if in_degree == 0:
                    levels[0].append(node)
                else:
                    # Find maximum level of predecessors
                    max_pred_level = -1
                    for pred in subgraph.predecessors(node):
                        for level, nodes in levels.items():
                            if pred in nodes:
                                max_pred_level = max(max_pred_level, level)
                    
                    levels[max_pred_level + 1].append(node)
            except Exception as e:
                self.logger.warning(f"Level computation error for {node}: {str(e)}")
                levels[0].append(node)
        
        return dict(levels)

    async def _analyze_workflow_characteristics(self, workflow_id: str) -> Dict[str, float]:
        """Analyze workflow characteristics for strategy selection."""
        workflow_nodes = [
            node for node in self.workflow_graph.nodes()
            if node.startswith(f"{workflow_id}:")
        ]
        
        if not workflow_nodes:
            return {
                'node_count': 0,
                'parallelization_potential': 0.0,
                'resource_intensity': 0.0,
                'complexity_score': 0.0
            }
        
        subgraph = self.workflow_graph.subgraph(workflow_nodes)
        
        # Calculate metrics
        node_count = len(workflow_nodes)
        edge_count = subgraph.number_of_edges()
        
        # Parallelization potential (based on dependency structure)
        if node_count <= 1:
            parallelization_potential = 0.0
        else:
            # Ratio of independent nodes to total nodes
            independent_nodes = sum(1 for node in workflow_nodes 
                                  if subgraph.in_degree(node) == 0)
            parallelization_potential = independent_nodes / node_count
        
        # Resource intensity
        total_resources = 0.0
        max_single_resource = 0.0
        
        for node_id in workflow_nodes:
            node_data = self.workflow_graph.nodes[node_id]
            node = node_data['node']
            
            node_total = sum(node.resources.values())
            total_resources += node_total
            max_single_resource = max(max_single_resource, node_total)
        
        avg_resource_per_node = total_resources / node_count if node_count > 0 else 0.0
        resource_intensity = min(1.0, avg_resource_per_node / 100.0)  # Normalize
        
        # Complexity score
        complexity_score = min(1.0, (edge_count + node_count) / 50.0)  # Normalize
        
        return {
            'node_count': node_count,
            'parallelization_potential': parallelization_potential,
            'resource_intensity': resource_intensity,
            'complexity_score': complexity_score
        }

    def _update_execution_stats(self, workflow_id: str, result: Dict[str, Any]):
        """Update execution statistics."""
        self.execution_stats['total_workflows'] += 1
        
        if result['success']:
            self.execution_stats['successful_workflows'] += 1
        else:
            self.execution_stats['failed_workflows'] += 1
        
        # Update average execution time
        current_avg = self.execution_stats['average_execution_time']
        total_workflows = self.execution_stats['total_workflows']
        execution_time = result.get('execution_time', 0.0)
        
        self.execution_stats['average_execution_time'] = (
            (current_avg * (total_workflows - 1) + execution_time) / total_workflows
        )
        
        # Update resource utilization
        for resource_type, usage in result.get('resource_usage', {}).items():
            self.execution_stats['resource_utilization'][resource_type] += usage

    def _get_executor_from_registry(self, executor_name: str) -> Callable:
        """Get executor function from registry."""
        # This would typically be a more sophisticated registry
        # For now, return a placeholder
        async def placeholder_executor(context):
            return f"Executed {executor_name} with context"
        
        return placeholder_executor

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current workflow execution status."""



        try:
            if workflow_id not in self.execution_contexts:
                return {'status': 'not_found'}
            
            context = self.execution_contexts[workflow_id]
            results = self.execution_results.get(workflow_id, {})
            
            return {
                'status': 'running' if workflow_id in self.active_workflows else 'completed',
                'context': {
                    'user_id': context.user_id,
                    'started_at': context.started_at.isoformat(),
                    'environment': context.environment
                },
                'results': results,
                'progress': {
                    'total_nodes': len([n for n in self.workflow_graph.nodes() 
                                      if n.startswith(f"{workflow_id}:")]),
                    'completed_nodes': len(results)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting workflow status: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def cancel_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Cancel a running workflow."""



        try:
            if workflow_id in self.active_workflows:
                self.active_workflows.remove(workflow_id)
                
                return {
                    'success': True,
                    'message': f"Workflow {workflow_id} cancelled"
                }
            else:
                return {
                    'success': False,
                    'message': f"Workflow {workflow_id} not found or not running"
                }
                
        except Exception as e:
            self.logger.error(f"Error cancelling workflow: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def get_execution_stats(self) -> Dict[str, Any]:
        """Get workflow execution statistics."""



        return {
            'stats': self.execution_stats.copy(),
            'active_workflows': len(self.active_workflows),
            'available_resources': self.available_resources.copy(),
            'total_workflows_in_memory': len(self.execution_contexts)
        }
