"""Data Lineage Tracking System

Advanced data lineage tracking and auditing system for complete
data flow visibility and governance compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib
from abc import ABC, abstractmethod

from ...core.base import BaseManager
from ...core.exceptions import LineageError, ValidationError
from ...core.database import DatabaseManager
from ...core.cache import CacheManager


class LineageEventType(Enum):
    """Types of lineage events"""    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    COPY = "copy"
    MOVE = "move"
    TRANSFORM = "transform"
    MERGE = "merge"
    SPLIT = "split"
    DERIVE = "derive"
    ARCHIVE = "archive"
    RESTORE = "restore"


class LineageNodeType(Enum):
    """Types of lineage nodes"""    SOURCE = "source"
    PROCESS = "process"
    DATASET = "dataset"
    SYSTEM = "system"
    USER = "user"
    API = "api"
    SERVICE = "service"


@dataclass
class LineageNode:
    """Node in the data lineage graph"""    node_id: str
    node_type: LineageNodeType
    name: str
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LineageEdge:
    """Edge in the data lineage graph"""    edge_id: str
    source_node_id: str
    target_node_id: str
    event_type: LineageEventType
    timestamp: datetime
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LineageEvent:
    """Data lineage event record"""    event_id: str
    content_id: str
    event_type: LineageEventType
    source_system: str
    target_system: Optional[str]
    user_id: Optional[str]
    timestamp: datetime
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataLineage:
    """Complete data lineage for a content item"""    content_id: str
    origin_node: LineageNode
    current_node: LineageNode
    lineage_events: List[LineageEvent]
    impact_analysis: Dict[str, List[str]]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class LineageGraph:
    """    Graph structure for managing data lineage relationships
    
    Provides efficient storage and traversal of lineage information
    with support for complex dependency analysis.
    """    
    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: Dict[str, LineageEdge] = {}
        self.adjacency_list: Dict[str, Set[str]] = {}  # node_id -> set of connected node_ids
        self.reverse_adjacency_list: Dict[str, Set[str]] = {}  # for upstream traversal
    
    def add_node(self, node: LineageNode) -> None:
        """Add a node to the lineage graph"""        self.nodes[node.node_id] = node
        if node.node_id not in self.adjacency_list:
            self.adjacency_list[node.node_id] = set()
        if node.node_id not in self.reverse_adjacency_list:
            self.reverse_adjacency_list[node.node_id] = set()
    
    def add_edge(self, edge: LineageEdge) -> None:
        """Add an edge to the lineage graph"""        self.edges[edge.edge_id] = edge
        
        # Update adjacency lists
        if edge.source_node_id not in self.adjacency_list:
            self.adjacency_list[edge.source_node_id] = set()
        if edge.target_node_id not in self.reverse_adjacency_list:
            self.reverse_adjacency_list[edge.target_node_id] = set()
        
        self.adjacency_list[edge.source_node_id].add(edge.target_node_id)
        self.reverse_adjacency_list[edge.target_node_id].add(edge.source_node_id)
    
    def get_downstream_nodes(self, node_id: str, max_depth: Optional[int] = None) -> List[str]:
        """Get all downstream nodes from a given node"""        visited = set()
        result = []
        
        def dfs(current_id: str, depth: int = 0):
            if current_id in visited or (max_depth and depth > max_depth):
                return
            
            visited.add(current_id)
            if current_id != node_id:  # Don't include the starting node
                result.append(current_id)
            
            for neighbor_id in self.adjacency_list.get(current_id, set()):
                dfs(neighbor_id, depth + 1)
        
        dfs(node_id)
        return result
    
    def get_upstream_nodes(self, node_id: str, max_depth: Optional[int] = None) -> List[str]:
        """Get all upstream nodes for a given node"""        visited = set()
        result = []
        
        def dfs(current_id: str, depth: int = 0):
            if current_id in visited or (max_depth and depth > max_depth):
                return
            
            visited.add(current_id)
            if current_id != node_id:  # Don't include the starting node
                result.append(current_id)
            
            for neighbor_id in self.reverse_adjacency_list.get(current_id, set()):
                dfs(neighbor_id, depth + 1)
        
        dfs(node_id)
        return result
    
    def find_path(self, source_id: str, target_id: str) -> List[str]:
        """Find path between two nodes"""        if source_id not in self.nodes or target_id not in self.nodes:
            return []
        
        visited = set()
        path = []
        
        def dfs(current_id: str) -> bool:
            if current_id in visited:
                return False
            
            visited.add(current_id)
            path.append(current_id)
            
            if current_id == target_id:
                return True
            
            for neighbor_id in self.adjacency_list.get(current_id, set()):
                if dfs(neighbor_id):
                    return True
            
            path.pop()
            return False
        
        if dfs(source_id):
            return path
        return []
    
    def get_connected_components(self) -> List[List[str]]:
        """Get all connected components in the graph"""        visited = set()
        components = []
        
        def dfs(node_id: str, component: List[str]):
            if node_id in visited:
                return
            
            visited.add(node_id)
            component.append(node_id)
            
            # Check both directions
            for neighbor_id in self.adjacency_list.get(node_id, set()):
                dfs(neighbor_id, component)
            
            for neighbor_id in self.reverse_adjacency_list.get(node_id, set()):
                dfs(neighbor_id, component)
        
        for node_id in self.nodes:
            if node_id not in visited:
                component = []
                dfs(node_id, component)
                if component:
                    components.append(component)
        
        return components


class LineageTracker(BaseManager):
    """    Central data lineage tracking system
    
    Tracks and manages complete data lineage across all content types
    and processing operations in the platform.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the lineage tracker"""        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.db_manager = DatabaseManager(config)
        self.cache_manager = CacheManager(config)
        
        # Lineage storage
        self.lineage_graph = LineageGraph()
        self.lineage_events: List[LineageEvent] = []
        self.content_lineages: Dict[str, DataLineage] = {}
        
        # Performance metrics
        self.metrics = {
            "total_events": 0,
            "total_nodes": 0,
            "total_edges": 0,
            "lineage_depth_avg": 0.0
        }
    
    async def initialize(self) -> None:
        """Initialize the lineage tracker"""        try:
            await self._load_lineage_data()
            self.logger.info("Lineage tracker initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize lineage tracker: {e}")
            raise LineageError(f"Lineage tracker initialization failed: {e}")
    
    async def track_event(
        self,
        content_id: str,
        event_type: LineageEventType,
        source_system: str,
        target_system: Optional[str] = None,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """        Track a lineage event
        
        Args:
            content_id: ID of content involved in the event
            event_type: Type of lineage event
            source_system: Source system identifier
            target_system: Target system identifier (for transfers)
            user_id: User who triggered the event
            properties: Event-specific properties
            metadata: Additional metadata
            
        Returns:
            str: Event ID
        """        try:
            # Create lineage event
            event = LineageEvent(
                event_id=f"lineage_{content_id}_{event_type.value}_{datetime.utcnow().timestamp()}",
                content_id=content_id,
                event_type=event_type,
                source_system=source_system,
                target_system=target_system,
                user_id=user_id,
                timestamp=datetime.utcnow(),
                properties=properties or {},
                metadata=metadata or {}
            )
            
            # Store event
            self.lineage_events.append(event)
            
            # Update lineage graph
            await self._update_lineage_graph(event)
            
            # Update content lineage
            await self._update_content_lineage(event)
            
            # Update metrics
            self.metrics["total_events"] += 1
            
            self.logger.info(f"Tracked lineage event: {event.event_id}")
            return event.event_id
            
        except Exception as e:
            self.logger.error(f"Error tracking lineage event: {e}")
            raise LineageError(f"Lineage event tracking failed: {e}")
    
    async def get_content_lineage(self, content_id: str) -> Optional[DataLineage]:
        """        Get complete lineage for a content item
        
        Args:
            content_id: ID of content
            
        Returns:
            DataLineage: Complete lineage information
        """        return self.content_lineages.get(content_id)
    
    async def get_upstream_dependencies(
        self,
        content_id: str,
        max_depth: Optional[int] = None
    ) -> List[str]:
        """        Get upstream dependencies for content
        
        Args:
            content_id: ID of content
            max_depth: Maximum depth to traverse
            
        Returns:
            List[str]: List of upstream content IDs
        """        try:
            # Find content node in graph
            content_node_id = await self._get_content_node_id(content_id)
            if not content_node_id:
                return []
            
            # Get upstream nodes
            upstream_nodes = self.lineage_graph.get_upstream_nodes(content_node_id, max_depth)
            
            # Convert node IDs to content IDs
            upstream_content = []
            for node_id in upstream_nodes:
                node = self.lineage_graph.nodes.get(node_id)
                if node and node.node_type == LineageNodeType.DATASET:
                    upstream_content.append(node.properties.get("content_id", node_id))
            
            return upstream_content
            
        except Exception as e:
            self.logger.error(f"Error getting upstream dependencies for {content_id}: {e}")
            return []
    
    async def get_downstream_impact(
        self,
        content_id: str,
        max_depth: Optional[int] = None
    ) -> List[str]:
        """        Get downstream impact analysis for content
        
        Args:
            content_id: ID of content
            max_depth: Maximum depth to traverse
            
        Returns:
            List[str]: List of impacted content IDs
        """        try:
            # Find content node in graph
            content_node_id = await self._get_content_node_id(content_id)
            if not content_node_id:
                return []
            
            # Get downstream nodes
            downstream_nodes = self.lineage_graph.get_downstream_nodes(content_node_id, max_depth)
            
            # Convert node IDs to content IDs
            impacted_content = []
            for node_id in downstream_nodes:
                node = self.lineage_graph.nodes.get(node_id)
                if node and node.node_type == LineageNodeType.DATASET:
                    impacted_content.append(node.properties.get("content_id", node_id))
            
            return impacted_content
            
        except Exception as e:
            self.logger.error(f"Error getting downstream impact for {content_id}: {e}")
            return []
    
    async def trace_lineage_path(
        self,
        source_content_id: str,
        target_content_id: str
    ) -> List[Dict[str, Any]]:
        """        Trace lineage path between two content items
        
        Args:
            source_content_id: Source content ID
            target_content_id: Target content ID
            
        Returns:
            List[Dict]: Path with nodes and events
        """        try:
            source_node_id = await self._get_content_node_id(source_content_id)
            target_node_id = await self._get_content_node_id(target_content_id)
            
            if not source_node_id or not target_node_id:
                return []
            
            # Find path in graph
            path_nodes = self.lineage_graph.find_path(source_node_id, target_node_id)
            if not path_nodes:
                return []
            
            # Build detailed path information
            path_details = []
            for i, node_id in enumerate(path_nodes):
                node = self.lineage_graph.nodes.get(node_id)
                if not node:
                    continue
                
                path_item = {
                    "node_id": node_id,
                    "node_type": node.node_type.value,
                    "name": node.name,
                    "properties": node.properties
                }
                
                # Add edge information if not the last node
                if i < len(path_nodes) - 1:
                    next_node_id = path_nodes[i + 1]
                    edge = await self._find_edge(node_id, next_node_id)
                    if edge:
                        path_item["edge"] = {
                            "event_type": edge.event_type.value,
                            "timestamp": edge.timestamp.isoformat(),
                            "properties": edge.properties
                        }
                
                path_details.append(path_item)
            
            return path_details
            
        except Exception as e:
            self.logger.error(f"Error tracing lineage path: {e}")
            return []
    
    async def get_lineage_events(
        self,
        content_id: Optional[str] = None,
        event_type: Optional[LineageEventType] = None,
        system: Optional[str] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LineageEvent]:
        """        Get lineage events with optional filtering
        
        Args:
            content_id: Filter by content ID
            event_type: Filter by event type
            system: Filter by system
            user_id: Filter by user
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List[LineageEvent]: Filtered lineage events
        """        filtered_events = self.lineage_events.copy()
        
        if content_id:
            filtered_events = [e for e in filtered_events if e.content_id == content_id]
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if system:
            filtered_events = [
                e for e in filtered_events 
                if e.source_system == system or e.target_system == system
            ]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
        
        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
        
        return sorted(filtered_events, key=lambda e: e.timestamp, reverse=True)
    
    async def analyze_lineage_complexity(self, content_id: str) -> Dict[str, Any]:
        """        Analyze lineage complexity for content
        
        Args:
            content_id: ID of content to analyze
            
        Returns:
            Dict with complexity analysis
        """        try:
            lineage = await self.get_content_lineage(content_id)
            if not lineage:
                return {"complexity": "unknown", "details": {}}
            
            # Get dependencies
            upstream = await self.get_upstream_dependencies(content_id)
            downstream = await self.get_downstream_impact(content_id)
            
            # Calculate complexity metrics
            upstream_count = len(upstream)
            downstream_count = len(downstream)
            event_count = len(lineage.lineage_events)
            
            # Determine complexity level
            total_connections = upstream_count + downstream_count
            if total_connections <= 2:
                complexity = "simple"
            elif total_connections <= 10:
                complexity = "moderate"
            elif total_connections <= 50:
                complexity = "complex"
            else:
                complexity = "highly_complex"
            
            return {
                "complexity": complexity,
                "details": {
                    "upstream_dependencies": upstream_count,
                    "downstream_impact": downstream_count,
                    "total_events": event_count,
                    "lineage_depth": await self._calculate_lineage_depth(content_id),
                    "branching_factor": max(upstream_count, downstream_count)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing lineage complexity for {content_id}: {e}")
            return {"complexity": "error", "details": {"error": str(e)}}
    
    async def generate_lineage_report(
        self,
        content_id: str,
        include_visual: bool = False
    ) -> Dict[str, Any]:
        """        Generate comprehensive lineage report
        
        Args:
            content_id: ID of content
            include_visual: Whether to include visual representation
            
        Returns:
            Dict with complete lineage report
        """        try:
            lineage = await self.get_content_lineage(content_id)
            if not lineage:
                return {"error": "No lineage data found"}
            
            # Get dependencies and impact
            upstream = await self.get_upstream_dependencies(content_id)
            downstream = await self.get_downstream_impact(content_id)
            
            # Get complexity analysis
            complexity = await self.analyze_lineage_complexity(content_id)
            
            # Get recent events
            recent_events = await self.get_lineage_events(
                content_id=content_id,
                start_time=datetime.utcnow() - timedelta(days=30)
            )
            
            report = {
                "content_id": content_id,
                "generated_at": datetime.utcnow().isoformat(),
                "origin": {
                    "node_id": lineage.origin_node.node_id,
                    "name": lineage.origin_node.name,
                    "created_at": lineage.origin_node.created_at.isoformat()
                },
                "current_location": {
                    "node_id": lineage.current_node.node_id,
                    "name": lineage.current_node.name,
                    "updated_at": lineage.current_node.updated_at.isoformat()
                },
                "dependencies": {
                    "upstream_count": len(upstream),
                    "upstream_items": upstream[:10],  # Limit for readability
                    "downstream_count": len(downstream),
                    "downstream_items": downstream[:10]
                },
                "complexity": complexity,
                "activity": {
                    "total_events": len(lineage.lineage_events),
                    "recent_events_30d": len(recent_events),
                    "last_activity": max(
                        (e.timestamp for e in lineage.lineage_events),
                        default=lineage.created_at
                    ).isoformat()
                },
                "event_summary": self._summarize_events(lineage.lineage_events)
            }
            
            if include_visual:
                report["visual"] = await self._generate_visual_lineage(content_id)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating lineage report for {content_id}: {e}")
            return {"error": f"Report generation failed: {e}"}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get lineage tracking metrics"""        return {
            **self.metrics,
            "total_content_tracked": len(self.content_lineages),
            "graph_nodes": len(self.lineage_graph.nodes),
            "graph_edges": len(self.lineage_graph.edges),
            "event_types_breakdown": self._get_event_type_breakdown()
        }
    
    async def _update_lineage_graph(self, event: LineageEvent) -> None:
        """Update the lineage graph with new event"""        # Create or update source node
        source_node_id = f"{event.source_system}_{event.content_id}"
        if source_node_id not in self.lineage_graph.nodes:
            source_node = LineageNode(
                node_id=source_node_id,
                node_type=LineageNodeType.DATASET,
                name=f"Content {event.content_id} in {event.source_system}",
                description=f"Content dataset in {event.source_system}",
                properties={"content_id": event.content_id, "system": event.source_system}
            )
            self.lineage_graph.add_node(source_node)
        
        # Create target node if needed
        if event.target_system:
            target_node_id = f"{event.target_system}_{event.content_id}"
            if target_node_id not in self.lineage_graph.nodes:
                target_node = LineageNode(
                    node_id=target_node_id,
                    node_type=LineageNodeType.DATASET,
                    name=f"Content {event.content_id} in {event.target_system}",
                    description=f"Content dataset in {event.target_system}",
                    properties={"content_id": event.content_id, "system": event.target_system}
                )
                self.lineage_graph.add_node(target_node)
            
            # Create edge between source and target
            edge = LineageEdge(
                edge_id=event.event_id,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                event_type=event.event_type,
                timestamp=event.timestamp,
                properties=event.properties,
                metadata=event.metadata
            )
            self.lineage_graph.add_edge(edge)
    
    async def _update_content_lineage(self, event: LineageEvent) -> None:
        """Update content lineage with new event"""        if event.content_id not in self.content_lineages:
            # Create new lineage
            origin_node = LineageNode(
                node_id=f"{event.source_system}_{event.content_id}",
                node_type=LineageNodeType.DATASET,
                name=f"Content {event.content_id}",
                description=f"Origin of content {event.content_id}",
                properties={"content_id": event.content_id}
            )
            
            lineage = DataLineage(
                content_id=event.content_id,
                origin_node=origin_node,
                current_node=origin_node,
                lineage_events=[],
                impact_analysis={},
                created_at=event.timestamp,
                updated_at=event.timestamp
            )
            
            self.content_lineages[event.content_id] = lineage
        
        # Add event to lineage
        lineage = self.content_lineages[event.content_id]
        lineage.lineage_events.append(event)
        lineage.updated_at = event.timestamp
        
        # Update current node if this is a transfer
        if event.target_system:
            lineage.current_node = LineageNode(
                node_id=f"{event.target_system}_{event.content_id}",
                node_type=LineageNodeType.DATASET,
                name=f"Content {event.content_id} in {event.target_system}",
                description=f"Current location of content {event.content_id}",
                properties={"content_id": event.content_id, "system": event.target_system}
            )
    
    async def _get_content_node_id(self, content_id: str) -> Optional[str]:
        """Get current node ID for content"""        lineage = self.content_lineages.get(content_id)
        if lineage:
            return lineage.current_node.node_id
        return None
    
    async def _find_edge(self, source_node_id: str, target_node_id: str) -> Optional[LineageEdge]:
        """Find edge between two nodes"""        for edge in self.lineage_graph.edges.values():
            if edge.source_node_id == source_node_id and edge.target_node_id == target_node_id:
                return edge
        return None
    
    async def _calculate_lineage_depth(self, content_id: str) -> int:
        """Calculate lineage depth for content"""        upstream = await self.get_upstream_dependencies(content_id)
        return len(upstream)
    
    def _summarize_events(self, events: List[LineageEvent]) -> Dict[str, int]:
        """Summarize events by type"""        summary = {}
        for event in events:
            event_type = event.event_type.value
            summary[event_type] = summary.get(event_type, 0) + 1
        return summary
    
    def _get_event_type_breakdown(self) -> Dict[str, int]:
        """Get breakdown of events by type"""        breakdown = {}
        for event in self.lineage_events:
            event_type = event.event_type.value
            breakdown[event_type] = breakdown.get(event_type, 0) + 1
        return breakdown
    
    async def _generate_visual_lineage(self, content_id: str) -> Dict[str, Any]:
        """Generate visual representation of lineage"""        # This would generate graph visualization data
        # For now, return basic structure
        upstream = await self.get_upstream_dependencies(content_id)
        downstream = await self.get_downstream_impact(content_id)
        
        return {
            "nodes": [
                {"id": content_id, "type": "content", "level": 0},
                *[{"id": uid, "type": "upstream", "level": -1} for uid in upstream[:5]],
                *[{"id": did, "type": "downstream", "level": 1} for did in downstream[:5]]
            ],
            "edges": [
                *[{"from": uid, "to": content_id} for uid in upstream[:5]],
                *[{"from": content_id, "to": did} for did in downstream[:5]]
            ]
        }
    
    async def _load_lineage_data(self) -> None:
        """Load lineage data from database"""        try:
            logger.info("Loading lineage data from database")
            
            # Load lineage entries from database
            lineage_records = await self._fetch_lineage_records_from_database()
            
            for record in lineage_records:
                entry = LineageEntry(
                    entry_id=record["entry_id"],
                    content_id=record["content_id"],
                    parent_content_ids=record.get("parent_content_ids", []),
                    child_content_ids=record.get("child_content_ids", []),
                    transformation_type=TransformationType(record.get("transformation_type", "unknown")),
                    transformation_details=record.get("transformation_details", {}),
                    created_at=datetime.fromisoformat(record["created_at"]) if "created_at" in record else datetime.utcnow(),
                    metadata=record.get("metadata", {})
                )
                
                self.lineage_entries[entry.content_id] = entry
            
            # Build the lineage graph from loaded entries
            await self._build_lineage_graph()
            
            logger.info(f"Loaded {len(self.lineage_entries)} lineage entries from database")
            
        except Exception as e:
            logger.error(f"Error loading lineage data from database: {e}")
            # Initialize empty data structures if loading fails
            self.lineage_entries = {}
            self.lineage_graph = nx.DiGraph()

    async def _fetch_lineage_records_from_database(self) -> List[Dict[str, Any]]:
        """Fetch lineage records from database"""        # Mock implementation - would query actual database
        logger.debug("Fetching lineage records from database")
        return []
    
    async def _build_lineage_graph(self) -> None:
        """Build networkx graph from lineage entries"""        try:
            # Clear existing graph
            self.lineage_graph.clear()
            
            # Add nodes and edges from lineage entries
            for content_id, entry in self.lineage_entries.items():
                # Add the content node
                self.lineage_graph.add_node(content_id, **{
                    "transformation_type": entry.transformation_type.value,
                    "created_at": entry.created_at.isoformat(),
                    "metadata": entry.metadata
                })
                
                # Add edges to parent content
                for parent_id in entry.parent_content_ids:
                    self.lineage_graph.add_edge(parent_id, content_id, **{
                        "transformation_type": entry.transformation_type.value,
                        "transformation_details": entry.transformation_details
                    })
                
                # Add edges to child content
                for child_id in entry.child_content_ids:
                    self.lineage_graph.add_edge(content_id, child_id)
            
            logger.debug(f"Built lineage graph with {self.lineage_graph.number_of_nodes()} nodes and {self.lineage_graph.number_of_edges()} edges")
            
        except Exception as e:
            logger.error(f"Error building lineage graph: {e}")
            self.lineage_graph = nx.DiGraph()
