"""Data Lineage Tracker - Comprehensive Data Lineage Management
==============================================================

Enterprise data lineage tracking with automated discovery, impact analysis,
and visual lineage mapping for complete data traceability.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

try:
    import sqlalchemy as sa
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import declarative_base, sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

import redis.asyncio as redis


class LineageType(Enum):
    """Data lineage relationship types."""
    READS_FROM = "reads_from"
    WRITES_TO = "writes_to"
    TRANSFORMS = "transforms"
    DERIVES_FROM = "derives_from"
    AGGREGATES = "aggregates"
    JOINS_WITH = "joins_with"


@dataclass
class LineageNode:
    """Data lineage node representing a data asset."""
    id: str
    name: str
    node_type: str  # table, view, file, api, process
    system: str
    location: str
    schema_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LineageEdge:
    """Data lineage relationship between nodes."""
    id: str
    source_node_id: str
    target_node_id: str
    relationship_type: LineageType
    process_id: Optional[str] = None
    transformation_logic: Optional[str] = None
    confidence_score: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataLineageTracker:
    """Enterprise data lineage tracking and management system."""
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        redis_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Database setup
        self.database_url = database_url
        self.engine = None
        self.async_session = None
        
        if database_url and SQLALCHEMY_AVAILABLE:
            self.engine = create_async_engine(database_url)
            self.async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
        
        # Redis setup
        self.redis_url = redis_url
        self.redis_client = None
        
        # Lineage graph
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: List[LineageEdge] = []
        self.lineage_cache: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.lineage_metrics = {
            'total_nodes': 0,
            'total_edges': 0,
            'lineage_queries': 0,
            'impact_analyses': 0
        }
    
    async def initialize(self):
        """Initialize the lineage tracker."""
        if self.redis_url:
            self.redis_client = redis.from_url(self.redis_url)
        
        if self.engine and SQLALCHEMY_AVAILABLE:
            # Create tables if needed
            pass
        
        self.logger.info("Data lineage tracker initialized")
    
    async def add_node(self, node: LineageNode):
        """Add a data lineage node."""
        self.nodes[node.id] = node
        self.lineage_metrics['total_nodes'] += 1
        
        # Store in Redis for fast access
        if self.redis_client:
            await self.redis_client.setex(
                f"lineage_node:{node.id}",
                86400,  # 24 hours
                json.dumps({
                    'id': node.id,
                    'name': node.name,
                    'node_type': node.node_type,
                    'system': node.system,
                    'location': node.location,
                    'metadata': node.metadata
                })
            )
        
        self.logger.info(f"Added lineage node: {node.name}")
    
    async def add_edge(self, edge: LineageEdge):
        """Add a lineage relationship."""
        self.edges.append(edge)
        self.lineage_metrics['total_edges'] += 1
        
        # Clear cache for affected nodes
        self._clear_cache_for_node(edge.source_node_id)
        self._clear_cache_for_node(edge.target_node_id)
        
        self.logger.info(f"Added lineage edge: {edge.source_node_id} -> {edge.target_node_id}")
    
    async def track_transformation(
        self,
        source_nodes: List[str],
        target_node: str,
        process_id: str,
        transformation_logic: str
    ):
        """Track a data transformation process."""
        for source_id in source_nodes:
            edge = LineageEdge(
                id=str(uuid.uuid4()),
                source_node_id=source_id,
                target_node_id=target_node,
                relationship_type=LineageType.TRANSFORMS,
                process_id=process_id,
                transformation_logic=transformation_logic
            )
            await self.add_edge(edge)
    
    async def get_lineage(self, node_id: str, direction: str = "both", depth: int = 3) -> Dict[str, Any]:
        """Get data lineage for a node."""
        self.lineage_metrics['lineage_queries'] += 1
        
        cache_key = f"{node_id}_{direction}_{depth}"
        if cache_key in self.lineage_cache:
            return self.lineage_cache[cache_key]
        
        lineage = {
            'node_id': node_id,
            'upstream': [],
            'downstream': [],
            'metadata': {}
        }
        
        if node_id not in self.nodes:
            return lineage
        
        # Get upstream lineage
        if direction in ["upstream", "both"]:
            upstream = await self._get_upstream_lineage(node_id, depth)
            lineage['upstream'] = upstream
        
        # Get downstream lineage
        if direction in ["downstream", "both"]:
            downstream = await self._get_downstream_lineage(node_id, depth)
            lineage['downstream'] = downstream
        
        # Cache result
        self.lineage_cache[cache_key] = lineage
        
        return lineage
    
    async def _get_upstream_lineage(self, node_id: str, depth: int, visited: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
        """Get upstream lineage recursively."""
        if visited is None:
            visited = set()
        
        if depth <= 0 or node_id in visited:
            return []
        
        visited.add(node_id)
        upstream = []
        
        # Find edges where this node is the target
        for edge in self.edges:
            if edge.target_node_id == node_id:
                source_node = self.nodes.get(edge.source_node_id)
                if source_node:
                    node_data = {
                        'node': {
                            'id': source_node.id,
                            'name': source_node.name,
                            'type': source_node.node_type,
                            'system': source_node.system
                        },
                        'relationship': edge.relationship_type.value,
                        'transformation': edge.transformation_logic,
                        'upstream': await self._get_upstream_lineage(source_node.id, depth - 1, visited)
                    }
                    upstream.append(node_data)
        
        return upstream
    
    async def _get_downstream_lineage(self, node_id: str, depth: int, visited: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
        """Get downstream lineage recursively."""
        if visited is None:
            visited = set()
        
        if depth <= 0 or node_id in visited:
            return []
        
        visited.add(node_id)
        downstream = []
        
        # Find edges where this node is the source
        for edge in self.edges:
            if edge.source_node_id == node_id:
                target_node = self.nodes.get(edge.target_node_id)
                if target_node:
                    node_data = {
                        'node': {
                            'id': target_node.id,
                            'name': target_node.name,
                            'type': target_node.node_type,
                            'system': target_node.system
                        },
                        'relationship': edge.relationship_type.value,
                        'transformation': edge.transformation_logic,
                        'downstream': await self._get_downstream_lineage(target_node.id, depth - 1, visited)
                    }
                    downstream.append(node_data)
        
        return downstream
    
    async def analyze_impact(self, node_id: str) -> Dict[str, Any]:
        """Analyze impact of changes to a data asset."""
        self.lineage_metrics['impact_analyses'] += 1
        
        if node_id not in self.nodes:
            return {'error': 'Node not found'}
        
        # Get all downstream dependencies
        downstream_lineage = await self.get_lineage(node_id, "downstream", depth=10)
        
        # Count impacted assets by type
        impact_summary = {
            'total_impacted': 0,
            'by_type': {},
            'by_system': {},
            'critical_paths': []
        }
        
        def count_nodes(lineage_data):
            for item in lineage_data:
                node = item['node']
                impact_summary['total_impacted'] += 1
                
                # Count by type
                node_type = node['type']
                impact_summary['by_type'][node_type] = impact_summary['by_type'].get(node_type, 0) + 1
                
                # Count by system
                system = node['system']
                impact_summary['by_system'][system] = impact_summary['by_system'].get(system, 0) + 1
                
                # Recurse
                count_nodes(item.get('downstream', []))
        
        count_nodes(downstream_lineage['downstream'])
        
        return {
            'source_node': node_id,
            'impact_summary': impact_summary,
            'detailed_lineage': downstream_lineage
        }
    
    def _clear_cache_for_node(self, node_id: str):
        """Clear lineage cache for a node."""
        keys_to_remove = [key for key in self.lineage_cache.keys() if key.startswith(node_id)]
        for key in keys_to_remove:
            del self.lineage_cache[key]
    
    def get_lineage_metrics(self) -> Dict[str, Any]:
        """Get lineage tracking metrics."""
        return {
            **self.lineage_metrics,
            'cached_lineages': len(self.lineage_cache)
        }


# Example usage
if __name__ == "__main__":
    async def main():
        tracker = DataLineageTracker(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            redis_url="redis://localhost:6379"
        )
        
        await tracker.initialize()
        
        # Add nodes
        source_table = LineageNode(
            id="source_table_1",
            name="User Events Table",
            node_type="table",
            system="postgres",
            location="postgres://db/events.user_events"
        )
        
        target_view = LineageNode(
            id="target_view_1",
            name="User Activity View",
            node_type="view",
            system="postgres",
            location="postgres://db/analytics.user_activity"
        )
        
        await tracker.add_node(source_table)
        await tracker.add_node(target_view)
        
        # Add relationship
        await tracker.track_transformation(
            source_nodes=["source_table_1"],
            target_node="target_view_1",
            process_id="etl_job_1",
            transformation_logic="SELECT user_id, COUNT(*) as activity_count FROM user_events GROUP BY user_id"
        )
        
        # Get lineage
        lineage = await tracker.get_lineage("source_table_1")
        print(f"Lineage: {json.dumps(lineage, indent=2)}")
        
        # Analyze impact
        impact = await tracker.analyze_impact("source_table_1")
        print(f"Impact analysis: {json.dumps(impact, indent=2)}")
    
    asyncio.run(main())