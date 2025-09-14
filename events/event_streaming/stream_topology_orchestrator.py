"""IA Influencer Agent - Stream Topology Orchestrator
Advanced Stream Processing Topology Management for Ainflue Platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. This is proprietary technology.
"""

from typing import Dict, Any, List, Optional, Callable, Set, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
from uuid import uuid4
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class TopologyState(Enum):
    """Topology states"""
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class NodeType(Enum):
    """Stream processing node types"""
    SOURCE = "source"
    PROCESSOR = "processor"
    SINK = "sink"
    FORK = "fork"
    JOIN = "join"
    FILTER = "filter"
    TRANSFORM = "transform"
    AGGREGATE = "aggregate"


class ExecutionMode(Enum):
    """Execution modes for topology"""
    BATCH = "batch"
    STREAMING = "streaming"
    HYBRID = "hybrid"


@dataclass
class StreamNode:
    """Node in stream processing topology"""
    
    node_id: str
    node_type: NodeType
    name: str
    description: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    processor_class: Optional[str] = None
    parallelism: int = 1
    input_streams: List[str] = field(default_factory=list)
    output_streams: List[str] = field(default_factory=list)
    state: TopologyState = TopologyState.CREATED
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        if not self.node_id:
            self.node_id = str(uuid4())


@dataclass 
class StreamEdge:
    """Edge connecting stream nodes"""
    
    edge_id: str
    from_node: str
    to_node: str
    stream_name: str
    partitioner: Optional[str] = None
    serializer: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        if not self.edge_id:
            self.edge_id = str(uuid4())


@dataclass
class StreamTopology:
    """Complete stream processing topology"""
    
    topology_id: str
    name: str
    description: Optional[str] = None
    nodes: Dict[str, StreamNode] = field(default_factory=dict)
    edges: Dict[str, StreamEdge] = field(default_factory=dict)
    state: TopologyState = TopologyState.CREATED
    execution_mode: ExecutionMode = ExecutionMode.STREAMING
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"
    version: int = 1
    
    def __post_init__(self) -> None:
        if not self.topology_id:
            self.topology_id = str(uuid4())
    
    def add_node(self, node -> None: StreamNode) -> None:
        """Add node to topology"""
        self.nodes[node.node_id] = node
        logger.debug(f"Added node {node.node_id} to topology {self.topology_id}")
    
    def add_edge(self, edge -> None: StreamEdge) -> None:
        """Add edge to topology"""
        self.edges[edge.edge_id] = edge
        logger.debug(f"Added edge {edge.edge_id} to topology {self.topology_id}")
    
    def get_source_nodes(self) -> List[StreamNode]:
        """Get all source nodes"""
        return [node for node in self.nodes.values() if node.node_type == NodeType.SOURCE]
    
    def get_sink_nodes(self) -> List[StreamNode]:
        """Get all sink nodes"""
        return [node for node in self.nodes.values() if node.node_type == NodeType.SINK]
    
    def get_dependencies(self, node_id: str) -> List[str]:
        """Get dependencies for a node"""
        dependencies = []
        for edge in self.edges.values():
            if edge.to_node == node_id:
                dependencies.append(edge.from_node)
        return dependencies
    
    def get_dependents(self, node_id: str) -> List[str]:
        """Get dependents of a node"""
        dependents = []
        for edge in self.edges.values():
            if edge.from_node == node_id:
                dependents.append(edge.to_node)
        return dependents
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate topology structure"""
        errors = []
        
        # Check for cycles
        if self._has_cycles():
            errors.append("Topology contains cycles")
        
        # Check for orphaned nodes
        connected_nodes = set()
        for edge in self.edges.values():
            connected_nodes.add(edge.from_node)
            connected_nodes.add(edge.to_node)
        
        orphaned_nodes = set(self.nodes.keys()) - connected_nodes
        if orphaned_nodes and len(self.nodes) > 1:
            errors.append(f"Orphaned nodes found: {orphaned_nodes}")
        
        # Check source/sink constraints
        sources = self.get_source_nodes()
        sinks = self.get_sink_nodes()
        
        if not sources:
            errors.append("Topology must have at least one source node")
        
        if not sinks:
            errors.append("Topology must have at least one sink node")
        
        # Check edge connectivity
        for edge in self.edges.values():
            if edge.from_node not in self.nodes:
                errors.append(f"Edge {edge.edge_id} references unknown from_node: {edge.from_node}")
            
            if edge.to_node not in self.nodes:
                errors.append(f"Edge {edge.edge_id} references unknown to_node: {edge.to_node}")
        
        return len(errors) == 0, errors
    
    def _has_cycles(self) -> bool:
        """Check if topology has cycles using DFS"""
        visited = set()
        rec_stack = set()
        
        def has_cycle_util(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for dependent in self.get_dependents(node_id):
                if dependent not in visited:
                    if has_cycle_util(dependent):
                        return True
                elif dependent in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self.nodes.keys():
            if node_id not in visited:
                if has_cycle_util(node_id):
                    return True
        
        return False


class AinflueBusinesTopologies:
    """Predefined topology templates for Ainflue business workflows"""
    
    @staticmethod
    def create_content_processing_topology() -> StreamTopology:
        """Create content processing topology for Ainflue"""
        topology = StreamTopology(
            topology_id="ainflue-content-processing",
            name="Content Processing Pipeline",
            description="Complete content upload and processing workflow"
        )
        
        # Source: Content uploads
        upload_source = StreamNode(
            node_id="content-upload-source",
            node_type=NodeType.SOURCE,
            name="Content Upload Source",
            config={
                "topic": "ainflue-content-uploads",
                "parallelism": 3
            },
            output_streams=["raw-uploads"]
        )
        topology.add_node(upload_source)
        
        # Processor: Content validation
        validation_processor = StreamNode(
            node_id="content-validator",
            node_type=NodeType.PROCESSOR,
            name="Content Validator",
            config={
                "validation_rules": ["file_size", "format", "content_safety"]
            },
            input_streams=["raw-uploads"],
            output_streams=["validated-content", "invalid-content"]
        )
        topology.add_node(validation_processor)
        
        # Processor: AI analysis
        ai_processor = StreamNode(
            node_id="ai-analysis-processor",
            node_type=NodeType.PROCESSOR,
            name="AI Content Analysis",
            config={
                "analysis_types": ["sentiment", "topics", "quality_score"],
                "model_version": "v2.1"
            },
            input_streams=["validated-content"],
            output_streams=["analyzed-content"]
        )
        topology.add_node(ai_processor)
        
        # Processor: Content protection
        protection_processor = StreamNode(
            node_id="content-protection",
            node_type=NodeType.PROCESSOR,
            name="Content Protection",
            config={
                "protection_methods": ["watermark", "drm", "fingerprint"]
            },
            input_streams=["analyzed-content"],
            output_streams=["protected-content"]
        )
        topology.add_node(protection_processor)
        
        # Sink: Processed content storage
        content_sink = StreamNode(
            node_id="content-storage-sink",
            node_type=NodeType.SINK,
            name="Content Storage",
            config={
                "storage_type": "distributed",
                "replication_factor": 3
            },
            input_streams=["protected-content"]
        )
        topology.add_node(content_sink)
        
        # Sink: Invalid content handling
        invalid_sink = StreamNode(
            node_id="invalid-content-sink",
            node_type=NodeType.SINK,
            name="Invalid Content Handler",
            config={
                "action": "quarantine",
                "notification": True
            },
            input_streams=["invalid-content"]
        )
        topology.add_node(invalid_sink)
        
        # Add edges
        edges = [
            StreamEdge("edge-1", "content-upload-source", "content-validator", "raw-uploads"),
            StreamEdge("edge-2", "content-validator", "ai-analysis-processor", "validated-content"),
            StreamEdge("edge-3", "content-validator", "invalid-content-sink", "invalid-content"),
            StreamEdge("edge-4", "ai-analysis-processor", "content-protection", "analyzed-content"),
            StreamEdge("edge-5", "content-protection", "content-storage-sink", "protected-content")
        ]
        
        for edge in edges:
            topology.add_edge(edge)
        
        return topology
    
    @staticmethod
    def create_revenue_analytics_topology() -> StreamTopology:
        """Create revenue analytics topology"""
        topology = StreamTopology(
            topology_id="ainflue-revenue-analytics",
            name="Revenue Analytics Pipeline",
            description="Real-time revenue analytics and reporting"
        )
        
        # Source: Revenue events
        revenue_source = StreamNode(
            node_id="revenue-events-source",
            node_type=NodeType.SOURCE,
            name="Revenue Events Source",
            config={
                "topics": ["revenue-events", "payment-events"],
                "parallelism": 2
            },
            output_streams=["raw-revenue-events"]
        )
        topology.add_node(revenue_source)
        
        # Processor: Revenue aggregation
        aggregation_processor = StreamNode(
            node_id="revenue-aggregator",
            node_type=NodeType.AGGREGATE,
            name="Revenue Aggregator",
            config={
                "window_size": "1h",
                "aggregations": ["sum", "count", "avg"]
            },
            input_streams=["raw-revenue-events"],
            output_streams=["aggregated-revenue"]
        )
        topology.add_node(aggregation_processor)
        
        # Fork: Split for different analytics
        analytics_fork = StreamNode(
            node_id="analytics-fork",
            node_type=NodeType.FORK,
            name="Analytics Fork",
            input_streams=["aggregated-revenue"],
            output_streams=["creator-analytics", "platform-analytics", "trending-analytics"]
        )
        topology.add_node(analytics_fork)
        
        # Processor: Creator analytics
        creator_processor = StreamNode(
            node_id="creator-analytics-processor",
            node_type=NodeType.PROCESSOR,
            name="Creator Analytics",
            input_streams=["creator-analytics"],
            output_streams=["creator-insights"]
        )
        topology.add_node(creator_processor)
        
        # Processor: Platform analytics
        platform_processor = StreamNode(
            node_id="platform-analytics-processor",
            node_type=NodeType.PROCESSOR,
            name="Platform Analytics",
            input_streams=["platform-analytics"],
            output_streams=["platform-insights"]
        )
        topology.add_node(platform_processor)
        
        # Sink: Analytics dashboard
        dashboard_sink = StreamNode(
            node_id="analytics-dashboard-sink",
            node_type=NodeType.SINK,
            name="Analytics Dashboard",
            input_streams=["creator-insights", "platform-insights"]
        )
        topology.add_node(dashboard_sink)
        
        # Add edges
        edges = [
            StreamEdge("edge-1", "revenue-events-source", "revenue-aggregator", "raw-revenue-events"),
            StreamEdge("edge-2", "revenue-aggregator", "analytics-fork", "aggregated-revenue"),
            StreamEdge("edge-3", "analytics-fork", "creator-analytics-processor", "creator-analytics"),
            StreamEdge("edge-4", "analytics-fork", "platform-analytics-processor", "platform-analytics"),
            StreamEdge("edge-5", "creator-analytics-processor", "analytics-dashboard-sink", "creator-insights"),
            StreamEdge("edge-6", "platform-analytics-processor", "analytics-dashboard-sink", "platform-insights")
        ]
        
        for edge in edges:
            topology.add_edge(edge)
        
        return topology


class TopologyExecutor:
    """Executes stream processing topology"""
    
    def __init__(self, topology -> None: StreamTopology, metrics_collector=None) -> None:
        self.topology = topology
        self.metrics_collector = metrics_collector
        self.node_executors: Dict[str, asyncio.Task] = {}
        self.stream_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._shutdown_event = asyncio.Event()
        
    async def start(self) -> None:
        """Start topology execution"""
        try:
            logger.info(f"Starting topology execution: {self.topology.name}")
            
            # Validate topology
            is_valid, errors = self.topology.validate()
            if not is_valid:
                raise ValueError(f"Invalid topology: {errors}")
            
            self.topology.state = TopologyState.STARTING
            
            # Start nodes in topological order
            execution_order = self._get_execution_order()
            
            for node_id in execution_order:
                await self._start_node(node_id)
            
            self.topology.state = TopologyState.RUNNING
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("topology_started")
            
            logger.info(f"Topology {self.topology.topology_id} started successfully")
            
        except Exception as e:
            self.topology.state = TopologyState.ERROR
            logger.error(f"Failed to start topology: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop topology execution"""
        try:
            logger.info(f"Stopping topology: {self.topology.name}")
            
            self.topology.state = TopologyState.STOPPING
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Stop all node executors
            for node_id, executor_task in self.node_executors.items():
                executor_task.cancel()
                try:
                    await executor_task
                except asyncio.CancelledError:
                    pass
                
                node = self.topology.nodes[node_id]
                node.state = TopologyState.STOPPED
            
            self.topology.state = TopologyState.STOPPED
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("topology_stopped")
            
            logger.info(f"Topology {self.topology.topology_id} stopped successfully")
            
        except Exception as e:
            self.topology.state = TopologyState.ERROR
            logger.error(f"Error stopping topology: {e}")
            raise
    
    def _get_execution_order(self) -> List[str]:
        """Get topological order for node execution"""
        # Simple topological sort using DFS
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(node_id -> None: str) -> None:
            if node_id in temp_visited:
                raise ValueError("Cycle detected in topology")
            
            if node_id not in visited:
                temp_visited.add(node_id)
                
                # Visit dependencies first
                for dependency in self.topology.get_dependencies(node_id):
                    visit(dependency)
                
                temp_visited.remove(node_id)
                visited.add(node_id)
                order.append(node_id)
        
        for node_id in self.topology.nodes.keys():
            if node_id not in visited:
                visit(node_id)
        
        return order
    
    async def _start_node(self, node_id -> None: str) -> None:
        """Start execution for a specific node"""
        try:
            node = self.topology.nodes[node_id]
            node.state = TopologyState.STARTING
            
            # Create executor task for the node
            self.node_executors[node_id] = asyncio.create_task(
                self._execute_node(node_id)
            )
            
            node.state = TopologyState.RUNNING
            logger.debug(f"Started node {node_id}")
            
        except Exception as e:
            node = self.topology.nodes[node_id]
            node.state = TopologyState.ERROR
            logger.error(f"Error starting node {node_id}: {e}")
            raise
    
    async def _execute_node(self, node_id -> None: str) -> None:
        """Execute a specific node"""
        try:
            node = self.topology.nodes[node_id]
            
            while not self._shutdown_event.is_set():
                try:
                    if node.node_type == NodeType.SOURCE:
                        await self._execute_source_node(node)
                    elif node.node_type == NodeType.PROCESSOR:
                        await self._execute_processor_node(node)
                    elif node.node_type == NodeType.SINK:
                        await self._execute_sink_node(node)
                    elif node.node_type == NodeType.FORK:
                        await self._execute_fork_node(node)
                    elif node.node_type == NodeType.JOIN:
                        await self._execute_join_node(node)
                    
                    # Update node metrics
                    node.metrics["last_execution"] = datetime.now(timezone.utc).isoformat()
                    
                except Exception as e:
                    logger.error(f"Error executing node {node_id}: {e}")
                    node.state = TopologyState.ERROR
                    
                    if self.metrics_collector:
                        self.metrics_collector.increment_counter(f"node_execution_errors")
                    
                    # Brief pause before retrying
                    await asyncio.sleep(1)
                
                # Brief pause between executions
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            logger.debug(f"Node {node_id} execution cancelled")
        except Exception as e:
            logger.error(f"Fatal error in node {node_id}: {e}")
            node.state = TopologyState.ERROR
    
    async def _execute_source_node(self, node -> None: StreamNode) -> None:
        """Execute source node (generate/read data)"""
        try:
            # Simulate data generation for demo
            # In real implementation, would read from actual sources
            
            for output_stream in node.output_streams:
                # Generate sample event
                event = {
                    "event_id": str(uuid4()),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "node_id": node.node_id,
                    "data": f"sample_data_{datetime.now().timestamp()}"
                }
                
                # Add to output stream buffer
                self.stream_buffers[output_stream].append(event)
                
                # Update metrics
                node.metrics["events_produced"] = node.metrics.get("events_produced", 0) + 1
                
                if self.metrics_collector:
                    self.metrics_collector.increment_counter("source_events_produced")
            
        except Exception as e:
            logger.error(f"Error in source node {node.node_id}: {e}")
            raise
    
    async def _execute_processor_node(self, node -> None: StreamNode) -> None:
        """Execute processor node (transform data)"""
        try:
            # Process events from input streams
            for input_stream in node.input_streams:
                buffer = self.stream_buffers[input_stream]
                
                # Process available events
                while buffer:
                    event = buffer.popleft()
                    
                    # Apply processing logic (simulated)
                    processed_event = {
                        **event,
                        "processed_by": node.node_id,
                        "processed_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Send to output streams
                    for output_stream in node.output_streams:
                        self.stream_buffers[output_stream].append(processed_event)
                    
                    # Update metrics
                    node.metrics["events_processed"] = node.metrics.get("events_processed", 0) + 1
                    
                    if self.metrics_collector:
                        self.metrics_collector.increment_counter("processor_events_processed")
            
        except Exception as e:
            logger.error(f"Error in processor node {node.node_id}: {e}")
            raise
    
    async def _execute_sink_node(self, node -> None: StreamNode) -> None:
        """Execute sink node (write/store data)"""
        try:
            # Process events from input streams
            for input_stream in node.input_streams:
                buffer = self.stream_buffers[input_stream]
                
                # Process available events
                while buffer:
                    event = buffer.popleft()
                    
                    # Simulate writing to sink (database, file, etc.)
                    logger.debug(f"Sink {node.node_id} processed event: {event['event_id']}")
                    
                    # Update metrics
                    node.metrics["events_written"] = node.metrics.get("events_written", 0) + 1
                    
                    if self.metrics_collector:
                        self.metrics_collector.increment_counter("sink_events_written")
            
        except Exception as e:
            logger.error(f"Error in sink node {node.node_id}: {e}")
            raise
    
    async def _execute_fork_node(self, node -> None: StreamNode) -> None:
        """Execute fork node (split stream)"""
        try:
            # Process events from input streams
            for input_stream in node.input_streams:
                buffer = self.stream_buffers[input_stream]
                
                # Process available events
                while buffer:
                    event = buffer.popleft()
                    
                    # Send to all output streams
                    for output_stream in node.output_streams:
                        forked_event = {
                            **event,
                            "forked_by": node.node_id,
                            "forked_to": output_stream
                        }
                        self.stream_buffers[output_stream].append(forked_event)
                    
                    # Update metrics
                    node.metrics["events_forked"] = node.metrics.get("events_forked", 0) + 1
            
        except Exception as e:
            logger.error(f"Error in fork node {node.node_id}: {e}")
            raise
    
    async def _execute_join_node(self, node -> None: StreamNode) -> None:
        """Execute join node (combine streams)"""
        try:
            # Simple join implementation - wait for events from all input streams
            if len(node.input_streams) < 2:
                return
            
            # Check if we have events from all input streams
            events_by_stream = {}
            for input_stream in node.input_streams:
                buffer = self.stream_buffers[input_stream]
                if buffer:
                    events_by_stream[input_stream] = buffer.popleft()
            
            # If we have events from all streams, join them
            if len(events_by_stream) == len(node.input_streams):
                joined_event = {
                    "event_id": str(uuid4()),
                    "joined_by": node.node_id,
                    "joined_at": datetime.now(timezone.utc).isoformat(),
                    "joined_events": events_by_stream
                }
                
                # Send to output streams
                for output_stream in node.output_streams:
                    self.stream_buffers[output_stream].append(joined_event)
                
                # Update metrics
                node.metrics["events_joined"] = node.metrics.get("events_joined", 0) + 1
            
        except Exception as e:
            logger.error(f"Error in join node {node.node_id}: {e}")
            raise
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """Get execution metrics for the topology"""
        try:
            metrics = {
                "topology_id": self.topology.topology_id,
                "topology_state": self.topology.state.value,
                "total_nodes": len(self.topology.nodes),
                "running_nodes": sum(1 for node in self.topology.nodes.values() if node.state == TopologyState.RUNNING),
                "error_nodes": sum(1 for node in self.topology.nodes.values() if node.state == TopologyState.ERROR),
                "stream_buffer_sizes": {stream: len(buffer) for stream, buffer in self.stream_buffers.items()},
                "node_metrics": {}
            }
            
            # Collect metrics from each node
            for node_id, node in self.topology.nodes.items():
                metrics["node_metrics"][node_id] = {
                    "state": node.state.value,
                    "type": node.node_type.value,
                    "metrics": node.metrics
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting execution metrics: {e}")
            return {"error": str(e)}


class StreamTopologyOrchestrator:
    """Main orchestrator for managing stream processing topologies"""
    
    def __init__(self, metrics_collector=None) -> None:
        self.metrics_collector = metrics_collector
        self.topologies: Dict[str, StreamTopology] = {}
        self.executors: Dict[str, TopologyExecutor] = {}
        self._orchestrator_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start(self) -> None:
        """Start the topology orchestrator"""
        try:
            logger.info("Starting Stream Topology Orchestrator")
            
            # Load default Ainflue topologies
            await self._load_default_topologies()
            
            # Start monitoring task
            self._orchestrator_task = asyncio.create_task(self._orchestrator_loop())
            
            logger.info("Stream Topology Orchestrator started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start topology orchestrator: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the orchestrator"""
        try:
            logger.info("Stopping Stream Topology Orchestrator")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Stop all running topologies
            for topology_id in list(self.executors.keys()):
                await self.stop_topology(topology_id)
            
            # Wait for orchestrator task
            if self._orchestrator_task:
                await self._orchestrator_task
            
            logger.info("Stream Topology Orchestrator stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping topology orchestrator: {e}")
            raise
    
    async def _load_default_topologies(self) -> None:
        """Load default Ainflue topologies"""
        try:
            # Load content processing topology
            content_topology = AinflueBusinesTopologies.create_content_processing_topology()
            self.topologies[content_topology.topology_id] = content_topology
            
            # Load revenue analytics topology
            revenue_topology = AinflueBusinesTopologies.create_revenue_analytics_topology()
            self.topologies[revenue_topology.topology_id] = revenue_topology
            
            logger.info("Loaded default Ainflue topologies")
            
        except Exception as e:
            logger.error(f"Error loading default topologies: {e}")
            raise
    
    async def deploy_topology(self, topology: StreamTopology) -> bool:
        """Deploy a topology"""
        try:
            # Validate topology
            is_valid, errors = topology.validate()
            if not is_valid:
                logger.error(f"Invalid topology {topology.topology_id}: {errors}")
                return False
            
            # Store topology
            self.topologies[topology.topology_id] = topology
            
            # Create executor
            executor = TopologyExecutor(topology, self.metrics_collector)
            self.executors[topology.topology_id] = executor
            
            logger.info(f"Deployed topology {topology.topology_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deploying topology {topology.topology_id}: {e}")
            return False
    
    async def start_topology(self, topology_id: str) -> bool:
        """Start a topology"""
        try:
            if topology_id not in self.executors:
                logger.error(f"Topology {topology_id} not found")
                return False
            
            executor = self.executors[topology_id]
            await executor.start()
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("topologies_started")
            
            logger.info(f"Started topology {topology_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting topology {topology_id}: {e}")
            return False
    
    async def stop_topology(self, topology_id: str) -> bool:
        """Stop a topology"""
        try:
            if topology_id not in self.executors:
                logger.error(f"Topology {topology_id} not found")
                return False
            
            executor = self.executors[topology_id]
            await executor.stop()
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("topologies_stopped")
            
            logger.info(f"Stopped topology {topology_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping topology {topology_id}: {e}")
            return False
    
    async def _orchestrator_loop(self) -> None:
        """Main orchestrator monitoring loop"""
        try:
            while not self._shutdown_event.is_set():
                # Monitor topology health
                await self._monitor_topology_health()
                
                # Perform maintenance
                await self._perform_maintenance()
                
                # Sleep before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            logger.error(f"Error in orchestrator loop: {e}")
    
    async def _monitor_topology_health(self) -> None:
        """Monitor health of all topologies"""
        try:
            for topology_id, executor in self.executors.items():
                topology = self.topologies[topology_id]
                
                if topology.state == TopologyState.ERROR:
                    logger.warning(f"Topology {topology_id} is in error state")
                    
                    # Attempt restart
                    try:
                        await executor.stop()
                        await executor.start()
                        logger.info(f"Successfully restarted topology {topology_id}")
                    except Exception as e:
                        logger.error(f"Failed to restart topology {topology_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error monitoring topology health: {e}")
    
    async def _perform_maintenance(self) -> None:
        """Perform routine maintenance tasks"""
        try:
            # Log system status
            running_topologies = sum(1 for t in self.topologies.values() if t.state == TopologyState.RUNNING)
            logger.debug(f"Topology orchestrator health check: {running_topologies}/{len(self.topologies)} topologies running")
            
        except Exception as e:
            logger.error(f"Error performing maintenance: {e}")
    
    def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator metrics"""
        try:
            topology_states = defaultdict(int)
            for topology in self.topologies.values():
                topology_states[topology.state.value] += 1
            
            metrics = {
                "total_topologies": len(self.topologies),
                "running_executors": len(self.executors),
                "topology_states": dict(topology_states),
                "topologies": {}
            }
            
            # Get metrics from each executor
            for topology_id, executor in self.executors.items():
                metrics["topologies"][topology_id] = executor.get_execution_metrics()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting orchestrator metrics: {e}")
            return {"error": str(e)}


# Export public API
__all__ = [
    "StreamTopologyOrchestrator", "StreamTopology", "StreamNode", "StreamEdge",
    "TopologyExecutor", "AinflueBusinesTopologies", "TopologyState", "NodeType",
    "ExecutionMode"
]