"""Dependency Resolver - Advanced Dependency Management & Resolution System

Intelligent dependency resolution engine for managing complex interdependencies
between workflows, tasks, and resources with circular dependency detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import networkx as nx

from backend.core.utils.metrics_collector import MetricsCollector
from backend.core.utils.event_dispatcher import EventDispatcher


class DependencyType(Enum):
    """
Dependency relationship types."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    RESOURCE = "resource"
    DATA = "data"
    TEMPORAL = "temporal"


class DependencyStatus(Enum):
    """Dependency status enumeration."""

    PENDING = "pending"
    SATISFIED = "satisfied"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


class ResolutionStrategy(Enum):
    """Dependency resolution strategies."""

    STRICT = "strict"
    BEST_EFFORT = "best_effort"
    FALLBACK = "fallback"
    PARALLEL_WHEN_POSSIBLE = "parallel_when_possible"


@dataclass
class DependencyRule:
    """Dependency rule definition."""
    rule_id: str
    name: str
    dependency_type: DependencyType
    source_id: str
    target_id: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    required: bool = True
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyNode:
    """
Node in dependency graph."""
    node_id: str
    name: str
    node_type: str
    status: str = "pending"
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Execution tracking
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class DependencyGraph:
    """Complete dependency graph structure."""
    graph_id: str
    name: str
    nodes: Dict[str, DependencyNode] = field(default_factory=dict)
    rules: Dict[str, DependencyRule] = field(default_factory=dict)
    resolution_strategy: ResolutionStrategy = ResolutionStrategy.STRICT
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResolutionPlan:
    """
Dependency resolution execution plan."""
    plan_id: str
    graph_id: str
    execution_order: List[List[str]]  # List of parallel execution batches
    estimated_duration: float
    critical_path: List[str]
    parallel_opportunities: List[List[str]]
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    risks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResolutionResult:
    """
Dependency resolution result."""
    resolution_id: str
    graph_id: str
    plan_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    completed_nodes: List[str] = field(default_factory=list)
    failed_nodes: List[str] = field(default_factory=list)
    skipped_nodes: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class DependencyResolver:
    """
    Advanced dependency resolution engine with intelligent graph analysis.
    
    Provides comprehensive dependency management capabilities including:
    - Complex dependency graph construction and validation
    - Circular dependency detection and resolution
    - Optimal execution plan generation
    - Multi-strategy resolution with fallback mechanisms
    - Real-time dependency tracking and monitoring
    """
    
    def __init__(self, resolution_strategy: ResolutionStrategy = ResolutionStrategy.PARALLEL_WHEN_POSSIBLE):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = MetricsCollector()
        self.event_dispatcher = EventDispatcher()
        
        # Core configuration
        self.default_resolution_strategy = resolution_strategy
        self.dependency_graphs: Dict[str, DependencyGraph] = {}
        self.resolution_plans: Dict[str, ResolutionPlan] = {}
        self.active_resolutions: Dict[str, ResolutionResult] = {}
        self.resolution_history: List[ResolutionResult] = []
        
        # Graph analysis
        self.nx_graphs: Dict[str, nx.DiGraph] = {}
        
        # Performance tracking
        self.resolver_stats = {
            'total_graphs': 0,
            'total_resolutions': 0,
            'successful_resolutions': 0,
            'failed_resolutions': 0,
            'circular_dependencies_detected': 0,
            'average_resolution_time': 0.0,
            'optimization_ratio': 0.0,
            'parallel_efficiency': 0.0
        }
        
        self.logger.info(f"DependencyResolver initialized with strategy: {resolution_strategy.value}")
    
    async def create_dependency_graph(self, graph: DependencyGraph) -> bool:
        """
        Create a new dependency graph.
        
        Args:
            graph: Dependency graph definition
            
        Returns:
            bool: Success status
        """
        try:
            # Validate graph structure
            if not await self._validate_graph(graph):
                return False
            
            # Build NetworkX graph for analysis
            nx_graph = await self._build_networkx_graph(graph)
            
            # Check for circular dependencies
            if not nx.is_directed_acyclic_graph(nx_graph):
                cycles = list(nx.simple_cycles(nx_graph))
                self.resolver_stats['circular_dependencies_detected'] += 1
                
                await self.event_dispatcher.emit('circular_dependency_detected', {
                    'graph_id': graph.graph_id,
                    'cycles': cycles
                })
                
                raise ValueError(f"Circular dependencies detected: {cycles}")
            
            # Store graph
            self.dependency_graphs[graph.graph_id] = graph
            self.nx_graphs[graph.graph_id] = nx_graph
            
            await self.event_dispatcher.emit('dependency_graph_created', {
                'graph_id': graph.graph_id,
                'node_count': len(graph.nodes),
                'rule_count': len(graph.rules)
            })
            
            self.resolver_stats['total_graphs'] += 1
            await self.metrics_collector.increment('dependency_graphs.created')
            
            self.logger.info(f"Dependency graph created: {graph.graph_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create dependency graph: {e}")
            return False
    
    async def add_dependency_rule(self, graph_id: str, rule: DependencyRule) -> bool:
        """
        Add a dependency rule to existing graph.
        
        Args:
            graph_id: Graph identifier
            rule: Dependency rule to add
            
        Returns:
            bool: Success status
        """
        try:
            if graph_id not in self.dependency_graphs:
                raise ValueError(f"Graph not found: {graph_id}")
            
            graph = self.dependency_graphs[graph_id]
            
            # Validate rule
            if not await self._validate_dependency_rule(graph, rule):
                return False
            
            # Add rule to graph
            graph.rules[rule.rule_id] = rule
            
            # Update node relationships
            if rule.source_id in graph.nodes:
                graph.nodes[rule.source_id].dependents.add(rule.target_id)
            
            if rule.target_id in graph.nodes:
                graph.nodes[rule.target_id].dependencies.add(rule.source_id)
            
            # Rebuild NetworkX graph
            self.nx_graphs[graph_id] = await self._build_networkx_graph(graph)
            
            # Check for new circular dependencies
            if not nx.is_directed_acyclic_graph(self.nx_graphs[graph_id]):
                # Rollback
                del graph.rules[rule.rule_id]
                if rule.source_id in graph.nodes:
                    graph.nodes[rule.source_id].dependents.discard(rule.target_id)
                if rule.target_id in graph.nodes:
                    graph.nodes[rule.target_id].dependencies.discard(rule.source_id)
                
                raise ValueError("Adding rule would create circular dependency")
            
            await self.event_dispatcher.emit('dependency_rule_added', {
                'graph_id': graph_id,
                'rule_id': rule.rule_id,
                'dependency_type': rule.dependency_type.value
            })
            
            await self.metrics_collector.increment('dependency_rules.added')
            
            self.logger.debug(f"Dependency rule added: {rule.rule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add dependency rule: {e}")
            return False
    
    async def generate_resolution_plan(self, graph_id: str) -> Optional[str]:
        """
        Generate optimal resolution plan for dependency graph.
        
        Args:
            graph_id: Graph identifier
            
        Returns:
            Optional[str]: Plan ID if successful
        """
        try:
            if graph_id not in self.dependency_graphs:
                raise ValueError(f"Graph not found: {graph_id}")
            
            graph = self.dependency_graphs[graph_id]
            nx_graph = self.nx_graphs[graph_id]
            
            plan_id = str(uuid.uuid4())
            
            # Generate execution order
            execution_order = await self._generate_execution_order(graph, nx_graph)
            
            # Find critical path
            critical_path = await self._find_critical_path(graph, nx_graph)
            
            # Identify parallel opportunities
            parallel_opportunities = await self._identify_parallel_opportunities(graph, nx_graph)
            
            # Estimate duration
            estimated_duration = await self._estimate_execution_duration(graph, execution_order)
            
            # Analyze risks
            risks = await self._analyze_execution_risks(graph, nx_graph)
            
            # Calculate resource requirements
            resource_requirements = await self._calculate_resource_requirements(graph)
            
            plan = ResolutionPlan(
                plan_id=plan_id,
                graph_id=graph_id,
                execution_order=execution_order,
                estimated_duration=estimated_duration,
                critical_path=critical_path,
                parallel_opportunities=parallel_opportunities,
                resource_requirements=resource_requirements,
                risks=risks
            )
            
            self.resolution_plans[plan_id] = plan
            
            await self.event_dispatcher.emit('resolution_plan_generated', {
                'plan_id': plan_id,
                'graph_id': graph_id,
                'execution_batches': len(execution_order),
                'estimated_duration': estimated_duration,
                'parallel_opportunities': len(parallel_opportunities)
            })
            
            await self.metrics_collector.increment('resolution_plans.generated')
            
            self.logger.info(f"Resolution plan generated: {plan_id}")
            return plan_id
            
        except Exception as e:
            self.logger.error(f"Failed to generate resolution plan: {e}")
            return None
    
    async def execute_resolution_plan(self, plan_id: str) -> str:
        """
        Execute dependency resolution plan.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            str: Resolution execution ID
        """
        resolution_id = str(uuid.uuid4())
        
        try:
            if plan_id not in self.resolution_plans:
                raise ValueError(f"Plan not found: {plan_id}")
            
            plan = self.resolution_plans[plan_id]
            graph = self.dependency_graphs[plan.graph_id]
            
            # Create resolution result
            result = ResolutionResult(
                resolution_id=resolution_id,
                graph_id=plan.graph_id,
                plan_id=plan_id,
                status="running",
                start_time=datetime.now()
            )
            
            self.active_resolutions[resolution_id] = result
            
            # Execute resolution asynchronously
            asyncio.create_task(self._execute_resolution_async(resolution_id, plan, graph))
            
            await self.event_dispatcher.emit('resolution_started', {
                'resolution_id': resolution_id,
                'plan_id': plan_id,
                'graph_id': plan.graph_id,
                'node_count': len(graph.nodes)
            })
            
            self.resolver_stats['total_resolutions'] += 1
            await self.metrics_collector.increment('resolutions.started')
            
            return resolution_id
            
        except Exception as e:
            self.logger.error(f"Failed to execute resolution plan: {e}")
            raise
    
    async def _execute_resolution_async(
        self,
        resolution_id: str,
        plan: ResolutionPlan,
        graph: DependencyGraph
    ) -> None:
        """Internal asynchronous resolution execution."""
        result = self.active_resolutions[resolution_id]
        
        try:
            # Execute batches in order
            for batch in plan.execution_order:
                await self._execute_batch(batch, graph, result)
                
                # Check for failures
                if result.failed_nodes and graph.resolution_strategy == ResolutionStrategy.STRICT:
                    break
            
            # Finalize result
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()
            
            if not result.failed_nodes:
                result.status = "completed"
                self.resolver_stats['successful_resolutions'] += 1
            else:
                result.status = "failed"
                self.resolver_stats['failed_resolutions'] += 1
            
            # Update performance stats
            self._update_performance_stats(result)
            
            await self.event_dispatcher.emit('resolution_completed', {
                'resolution_id': resolution_id,
                'status': result.status,
                'duration': result.duration,
                'completed_nodes': len(result.completed_nodes),
                'failed_nodes': len(result.failed_nodes)
            })
            
            await self.metrics_collector.record('resolution.duration', result.duration)
            await self.metrics_collector.increment(f'resolutions.{result.status}')
            
        except Exception as e:
            result.status = "error"
            result.end_time = datetime.now()
            result.errors.append(str(e))
            
            self.logger.error(f"Resolution execution failed: {e}")
        
        finally:
            # Move to history
            self.resolution_history.append(result)
            if resolution_id in self.active_resolutions:
                del self.active_resolutions[resolution_id]
    
    async def _execute_batch(
        self,
        batch: List[str],
        graph: DependencyGraph,
        result: ResolutionResult
    ) -> None:
        """Execute a batch of nodes in parallel."""
        # Execute nodes in parallel
        tasks = []
        for node_id in batch:
            if node_id in graph.nodes:
                tasks.append(self._execute_node(node_id, graph, result))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_node(
        self,
        node_id: str,
        graph: DependencyGraph,
        result: ResolutionResult
    ) -> None:
        """
Execute individual node."""
        node = graph.nodes[node_id]
        
        try:
            # Check dependencies are satisfied
            if not await self._check_dependencies_satisfied(node_id, graph, result):
                result.skipped_nodes.append(node_id)
                return
            
            node.start_time = datetime.now()
            node.status = "running"
            
            # Simulate node execution (in reality, this would call actual handlers)
            await asyncio.sleep(0.1)  # Placeholder execution
            
            node.end_time = datetime.now()
            node.status = "completed"
            result.completed_nodes.append(node_id)
            
            await self.event_dispatcher.emit('node_completed', {
                'node_id': node_id,
                'resolution_id': result.resolution_id,
                'duration': (node.end_time - node.start_time).total_seconds()
            })
            
        except Exception as e:
            node.status = "failed"
            node.error = str(e)
            node.end_time = datetime.now()
            result.failed_nodes.append(node_id)
            result.errors.append(f"Node {node_id}: {str(e)}")
            
            await self.event_dispatcher.emit('node_failed', {
                'node_id': node_id,
                'resolution_id': result.resolution_id,
                'error': str(e)
            })
    
    async def _generate_execution_order(
        self,
        graph: DependencyGraph,
        nx_graph: nx.DiGraph
    ) -> List[List[str]]:
        """Generate optimal execution order."""
        execution_order = []
        
        if graph.resolution_strategy == ResolutionStrategy.PARALLEL_WHEN_POSSIBLE:
            # Use topological sorting with level-based grouping
            levels = {}
            
            # Calculate levels for each node
            for node in nx.topological_sort(nx_graph):
                if not list(nx_graph.predecessors(node)):
                    levels[node] = 0
                else:
                    levels[node] = max(levels[pred] for pred in nx_graph.predecessors(node)) + 1
            
            # Group by level
            level_groups = {}
            for node, level in levels.items():
                if level not in level_groups:
                    level_groups[level] = []
                level_groups[level].append(node)
            
            # Convert to execution order
            for level in sorted(level_groups.keys()):
                execution_order.append(level_groups[level])
        
        else:
            # Sequential execution
            for node in nx.topological_sort(nx_graph):
                execution_order.append([node])
        
        return execution_order
    
    async def _find_critical_path(
        self,
        graph: DependencyGraph,
        nx_graph: nx.DiGraph
    ) -> List[str]:
        """
Find critical path through dependency graph."""
        # Simplified critical path calculation
        # In practice, this would consider node weights/durations
        
        longest_path = []
        max_length = 0
        
        # Find all paths and select longest
        try:
            for source in [n for n in nx_graph.nodes() if nx_graph.in_degree(n) == 0]:
                for sink in [n for n in nx_graph.nodes() if nx_graph.out_degree(n) == 0]:
                    try:
                        path = nx.shortest_path(nx_graph, source, sink)
                        if len(path) > max_length:
                            max_length = len(path)
                            longest_path = path
                    except nx.NetworkXNoPath:
                        continue
        except Exception:
            # Fallback to topological sort
            longest_path = list(nx.topological_sort(nx_graph))
        
        return longest_path
    
    async def _identify_parallel_opportunities(
        self,
        graph: DependencyGraph,
        nx_graph: nx.DiGraph
    ) -> List[List[str]]:
        """
Identify nodes that can be executed in parallel."""
        parallel_groups = []
        
        # Find nodes at the same dependency level
        levels = {}
        for node in nx.topological_sort(nx_graph):
            if not list(nx_graph.predecessors(node)):
                levels[node] = 0
            else:
                levels[node] = max(levels[pred] for pred in nx_graph.predecessors(node)) + 1
        
        # Group by level
        level_groups = {}
        for node, level in levels.items():
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(node)
        
        # Add groups with more than one node
        for level, nodes in level_groups.items():
            if len(nodes) > 1:
                parallel_groups.append(nodes)
        
        return parallel_groups
    
    async def _estimate_execution_duration(
        self,
        graph: DependencyGraph,
        execution_order: List[List[str]]
    ) -> float:
        """
Estimate total execution duration."""
        total_duration = 0.0
        
        for batch in execution_order:
            # Assume parallel execution within batch
            max_batch_duration = 0.0
            
            for node_id in batch:
                node = graph.nodes.get(node_id)
                if node:
                    # Use node metadata for duration estimate
                    estimated_duration = node.metadata.get('estimated_duration', 1.0)
                    max_batch_duration = max(max_batch_duration, estimated_duration)
            
            total_duration += max_batch_duration
        
        return total_duration
    
    async def _analyze_execution_risks(
        self,
        graph: DependencyGraph,
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess__analyze_execution_risks_input(graph)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess__analyze_execution_risks_result(result)
            
                    logger.info(f"AI processing _analyze_execution_risks completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing _analyze_execution_risks failed: {e}")
                    raise
    async def _calculate_resource_requirements(self, graph: DependencyGraph) -> Dict[str, Any]:
        """Calculate total resource requirements."""
        requirements = {
            'cpu': 0.0,
            'memory': 0.0,
            'storage': 0.0,
            'network': 0.0
        }
        
        for node in graph.nodes.values():
            node_requirements = node.metadata.get('resource_requirements', {})
            for resource, amount in node_requirements.items():
                if resource in requirements:
                    requirements[resource] += amount
        
        return requirements
    
    async def _check_dependencies_satisfied(
        self,
        node_id: str,
        graph: DependencyGraph,
        result: ResolutionResult
    ) -> bool:
        """
Check if node dependencies are satisfied."""
        node = graph.nodes[node_id]
        
        for dep_id in node.dependencies:
            if dep_id not in result.completed_nodes:
                return False
        
        return True
    
    async def _build_networkx_graph(self, graph: DependencyGraph) -> nx.DiGraph:
        """
Build NetworkX graph from dependency graph."""
        nx_graph = nx.DiGraph()
        
        # Add nodes
        for node_id, node in graph.nodes.items():
            nx_graph.add_node(node_id, **node.metadata)
        
        # Add edges from rules
        for rule in graph.rules.values():
            if rule.source_id in graph.nodes and rule.target_id in graph.nodes:
                nx_graph.add_edge(
                    rule.source_id,
                    rule.target_id,
                    weight=rule.weight,
                    dependency_type=rule.dependency_type.value
                )
        
        return nx_graph
    
    async def _validate_graph(self, graph: DependencyGraph) -> bool:
        """
Validate dependency graph structure."""
        try:
            if not graph.graph_id or not graph.name:
                return False
            
            # Check all rule references exist
            for rule in graph.rules.values():
                if rule.source_id not in graph.nodes or rule.target_id not in graph.nodes:
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def _validate_dependency_rule(self, graph: DependencyGraph, rule: DependencyRule) -> bool:
        """
Validate dependency rule."""
        try:
            if not rule.rule_id or not rule.source_id or not rule.target_id:
                return False
            
            if rule.source_id not in graph.nodes or rule.target_id not in graph.nodes:
                return False
            
            if rule.source_id == rule.target_id:
                return False  # Self-dependency
            
            return True
            
        except Exception:
            return False
    
    def _update_performance_stats(self, result: ResolutionResult) -> None:
        """
Update performance statistics."""
        # Update average resolution time
        if result.duration:
            current_avg = self.resolver_stats['average_resolution_time']
            total_resolutions = self.resolver_stats['total_resolutions']
            
            self.resolver_stats['average_resolution_time'] = (
                (current_avg * (total_resolutions - 1) + result.duration) / total_resolutions
            )
        
        # Calculate optimization ratio
        total_nodes = len(result.completed_nodes) + len(result.failed_nodes) + len(result.skipped_nodes)
        if total_nodes > 0:
            success_ratio = len(result.completed_nodes) / total_nodes
            self.resolver_stats['optimization_ratio'] = success_ratio
    
    async def get_graph_info(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """
Get comprehensive graph information."""
        if graph_id not in self.dependency_graphs:
            return None
        
        graph = self.dependency_graphs[graph_id]
        nx_graph = self.nx_graphs[graph_id]
        
        return {
            'graph_id': graph_id,
            'name': graph.name,
            'node_count': len(graph.nodes),
            'rule_count': len(graph.rules),
            'is_acyclic': nx.is_directed_acyclic_graph(nx_graph),
            'complexity_score': len(graph.rules) / max(len(graph.nodes), 1),
            'created_at': graph.created_at.isoformat(),
            'resolution_strategy': graph.resolution_strategy.value
        }
    
    async def get_resolution_status(self, resolution_id: str) -> Optional[Dict[str, Any]]:
        """
Get resolution execution status."""
        if resolution_id in self.active_resolutions:
            result = self.active_resolutions[resolution_id]
        else:
            result = next((r for r in self.resolution_history if r.resolution_id == resolution_id), None)
        
        if not result:
            return None
        
        return {
            'resolution_id': resolution_id,
            'status': result.status,
            'start_time': result.start_time.isoformat(),
            'end_time': result.end_time.isoformat() if result.end_time else None,
            'duration': result.duration,
            'completed_nodes': len(result.completed_nodes),
            'failed_nodes': len(result.failed_nodes),
            'skipped_nodes': len(result.skipped_nodes),
            'errors': result.errors
        }
    
    async def get_resolver_stats(self) -> Dict[str, Any]:
        """
Get dependency resolver statistics."""
        return {
            **self.resolver_stats,
            'active_graphs': len(self.dependency_graphs),
            'active_resolutions': len(self.active_resolutions),
            'cached_plans': len(self.resolution_plans),
            'resolution_history_size': len(self.resolution_history)
        }
