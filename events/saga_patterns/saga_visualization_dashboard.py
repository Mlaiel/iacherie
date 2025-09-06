#!/usr/bin/env python3
"""Saga Visualization Dashboard - Interactive Monitoring Interface
================================================================

Advanced visualization dashboard for saga pattern monitoring.
Provides real-time visual insights, flow diagrams, and
interactive analytics for saga execution patterns.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class VisualizationType(Enum):
    """Types of visualizations available"""
    FLOW_DIAGRAM = "flow_diagram"
    TIMELINE = "timeline"
    PERFORMANCE_CHART = "performance_chart"
    HEATMAP = "heatmap"
    NETWORK_GRAPH = "network_graph"
    METRICS_DASHBOARD = "metrics_dashboard"


@dataclass
class VisualizationNode:
    """Node in visualization graph"""
    node_id: str
    node_type: str
    label: str
    status: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, float] = field(default_factory=dict)
    style: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VisualizationEdge:
    """Edge in visualization graph"""
    edge_id: str
    source_node: str
    target_node: str
    edge_type: str
    label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    style: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VisualizationData:
    """Complete visualization data structure"""
    visualization_id: str
    visualization_type: VisualizationType
    title: str
    nodes: List[VisualizationNode] = field(default_factory=list)
    edges: List[VisualizationEdge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "visualization_id": self.visualization_id,
            "visualization_type": self.visualization_type.value,
            "title": self.title,
            "nodes": [asdict(node) for node in self.nodes],
            "edges": [asdict(edge) for edge in self.edges],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class SagaVisualizationDashboard:
    """Main dashboard for saga visualization"""
    
    def __init__(self):
        self.active_visualizations: Dict[str, VisualizationData] = {}
        self.visualization_cache: Dict[str, Any] = {}
        self.dashboard_config: Dict[str, Any] = self._default_dashboard_config()
    
    def _default_dashboard_config(self) -> Dict[str, Any]:
        """Default dashboard configuration"""
        return {
            "theme": "dark",
            "auto_refresh_seconds": 30,
            "max_nodes_per_view": 100,
            "layout_algorithm": "hierarchical",
            "color_schemes": {
                "status": {
                    "running": "#3498db",
                    "completed": "#2ecc71",
                    "failed": "#e74c3c",
                    "pending": "#f39c12",
                    "compensating": "#9b59b6"
                },
                "node_types": {
                    "saga": "#1abc9c",
                    "step": "#34495e",
                    "service": "#16a085",
                    "event": "#f1c40f"
                }
            }
        }
    
    async def create_saga_flow_diagram(
        self,
        saga_id: str,
        saga_data: Dict[str, Any]
    ) -> str:
        """Create flow diagram visualization for saga"""
        
        visualization_id = f"flow_{saga_id}_{uuid.uuid4().hex[:8]}"
        
        # Create visualization data
        viz_data = VisualizationData(
            visualization_id=visualization_id,
            visualization_type=VisualizationType.FLOW_DIAGRAM,
            title=f"Saga Flow: {saga_id}"
        )
        
        # Add saga root node
        saga_node = VisualizationNode(
            node_id=saga_id,
            node_type="saga",
            label=f"Saga: {saga_data.get('saga_type', 'Unknown')}",
            status=saga_data.get("status", "unknown"),
            metadata={
                "saga_type": saga_data.get("saga_type"),
                "started_at": saga_data.get("started_at"),
                "creator_id": saga_data.get("creator_id")
            },
            position={"x": 0, "y": 0},
            style=self._get_node_style("saga", saga_data.get("status", "unknown"))
        )
        viz_data.nodes.append(saga_node)
        
        # Add step nodes
        steps = saga_data.get("steps", [])
        for i, step in enumerate(steps):
            step_node = VisualizationNode(
                node_id=f"{saga_id}_step_{i}",
                node_type="step",
                label=step.get("step_name", f"Step {i+1}"),
                status=step.get("status", "pending"),
                metadata=step.get("metadata", {}),
                position={"x": (i + 1) * 200, "y": 0},
                style=self._get_node_style("step", step.get("status", "pending"))
            )
            viz_data.nodes.append(step_node)
            
            # Add edge from previous node
            source_id = saga_id if i == 0 else f"{saga_id}_step_{i-1}"
            edge = VisualizationEdge(
                edge_id=f"edge_{source_id}_to_{step_node.node_id}",
                source_node=source_id,
                target_node=step_node.node_id,
                edge_type="sequence",
                style=self._get_edge_style("sequence")
            )
            viz_data.edges.append(edge)
        
        # Add parallel branches if any
        parallel_branches = saga_data.get("parallel_branches", [])
        for branch in parallel_branches:
            branch_node = VisualizationNode(
                node_id=f"{saga_id}_branch_{branch['branch_id']}",
                node_type="branch",
                label=f"Branch: {branch['branch_name']}",
                status=branch.get("status", "running"),
                position={"x": 100, "y": (len(viz_data.nodes) * 100)},
                style=self._get_node_style("branch", branch.get("status", "running"))
            )
            viz_data.nodes.append(branch_node)
        
        # Store visualization
        self.active_visualizations[visualization_id] = viz_data
        
        logger.info(f"Created saga flow diagram: {visualization_id}")
        return visualization_id
    
    async def create_performance_timeline(
        self,
        saga_ids: List[str],
        time_range_hours: int = 24
    ) -> str:
        """Create performance timeline visualization"""
        
        visualization_id = f"timeline_{uuid.uuid4().hex[:8]}"
        
        viz_data = VisualizationData(
            visualization_id=visualization_id,
            visualization_type=VisualizationType.TIMELINE,
            title=f"Performance Timeline ({time_range_hours}h)"
        )
        
        # Create timeline nodes for each saga
        for i, saga_id in enumerate(saga_ids):
            # Mock timeline data
            timeline_events = [
                {"time": 0, "event": "started", "status": "running"},
                {"time": 30, "event": "step_1_completed", "status": "running"},
                {"time": 60, "event": "step_2_completed", "status": "running"},
                {"time": 90, "event": "completed", "status": "completed"}
            ]
            
            for j, event in enumerate(timeline_events):
                node = VisualizationNode(
                    node_id=f"{saga_id}_event_{j}",
                    node_type="timeline_event",
                    label=f"{saga_id}: {event['event']}",
                    status=event["status"],
                    position={"x": event["time"], "y": i * 50},
                    metadata={"saga_id": saga_id, "event_type": event["event"]},
                    style=self._get_node_style("timeline_event", event["status"])
                )
                viz_data.nodes.append(node)
        
        self.active_visualizations[visualization_id] = viz_data
        
        logger.info(f"Created performance timeline: {visualization_id}")
        return visualization_id
    
    async def create_metrics_dashboard(
        self,
        metrics_data: Dict[str, Any]
    ) -> str:
        """Create metrics dashboard visualization"""
        
        visualization_id = f"metrics_{uuid.uuid4().hex[:8]}"
        
        viz_data = VisualizationData(
            visualization_id=visualization_id,
            visualization_type=VisualizationType.METRICS_DASHBOARD,
            title="Saga Metrics Dashboard",
            metadata={
                "metrics": metrics_data,
                "dashboard_config": self.dashboard_config
            }
        )
        
        # Create metric nodes
        metric_categories = ["throughput", "success_rate", "error_rate", "avg_duration"]
        
        for i, category in enumerate(metric_categories):
            value = metrics_data.get(category, 0)
            
            node = VisualizationNode(
                node_id=f"metric_{category}",
                node_type="metric",
                label=f"{category.replace('_', ' ').title()}: {value}",
                status="normal",
                position={"x": (i % 2) * 300, "y": (i // 2) * 200},
                metadata={"metric_type": category, "value": value},
                style=self._get_metric_style(category, value)
            )
            viz_data.nodes.append(node)
        
        self.active_visualizations[visualization_id] = viz_data
        
        logger.info(f"Created metrics dashboard: {visualization_id}")
        return visualization_id
    
    async def create_system_heatmap(
        self,
        service_metrics: Dict[str, Dict[str, float]]
    ) -> str:
        """Create system performance heatmap"""
        
        visualization_id = f"heatmap_{uuid.uuid4().hex[:8]}"
        
        viz_data = VisualizationData(
            visualization_id=visualization_id,
            visualization_type=VisualizationType.HEATMAP,
            title="System Performance Heatmap"
        )
        
        # Create heatmap cells
        services = list(service_metrics.keys())
        metrics = ["cpu_usage", "memory_usage", "error_rate", "response_time"]
        
        for i, service in enumerate(services):
            for j, metric in enumerate(metrics):
                value = service_metrics.get(service, {}).get(metric, 0)
                
                node = VisualizationNode(
                    node_id=f"heatmap_{service}_{metric}",
                    node_type="heatmap_cell",
                    label=f"{service}\n{metric}: {value}",
                    status=self._get_heatmap_status(metric, value),
                    position={"x": j * 150, "y": i * 100},
                    metadata={"service": service, "metric": metric, "value": value},
                    style=self._get_heatmap_style(metric, value)
                )
                viz_data.nodes.append(node)
        
        self.active_visualizations[visualization_id] = viz_data
        
        logger.info(f"Created system heatmap: {visualization_id}")
        return visualization_id
    
    async def create_network_graph(
        self,
        service_topology: Dict[str, List[str]]
    ) -> str:
        """Create service network graph"""
        
        visualization_id = f"network_{uuid.uuid4().hex[:8]}"
        
        viz_data = VisualizationData(
            visualization_id=visualization_id,
            visualization_type=VisualizationType.NETWORK_GRAPH,
            title="Service Network Topology"
        )
        
        # Create service nodes
        all_services = set()
        for service, dependencies in service_topology.items():
            all_services.add(service)
            all_services.update(dependencies)
        
        for i, service in enumerate(sorted(all_services)):
            node = VisualizationNode(
                node_id=service,
                node_type="service",
                label=service,
                status="active",
                position=self._calculate_network_position(i, len(all_services)),
                style=self._get_node_style("service", "active")
            )
            viz_data.nodes.append(node)
        
        # Create dependency edges
        for service, dependencies in service_topology.items():
            for dependency in dependencies:
                edge = VisualizationEdge(
                    edge_id=f"dep_{service}_{dependency}",
                    source_node=service,
                    target_node=dependency,
                    edge_type="dependency",
                    label="depends on",
                    style=self._get_edge_style("dependency")
                )
                viz_data.edges.append(edge)
        
        self.active_visualizations[visualization_id] = viz_data
        
        logger.info(f"Created network graph: {visualization_id}")
        return visualization_id
    
    def _get_node_style(self, node_type: str, status: str) -> Dict[str, Any]:
        """Get style configuration for node"""
        base_style = {
            "shape": "box",
            "font": {"size": 12},
            "border": {"width": 2}
        }
        
        # Apply color based on status
        status_colors = self.dashboard_config["color_schemes"]["status"]
        if status in status_colors:
            base_style["color"] = {"background": status_colors[status]}
        
        # Apply node type specific styles
        if node_type == "saga":
            base_style["shape"] = "ellipse"
            base_style["font"]["size"] = 16
        elif node_type == "step":
            base_style["shape"] = "box"
        elif node_type == "service":
            base_style["shape"] = "diamond"
        
        return base_style
    
    def _get_edge_style(self, edge_type: str) -> Dict[str, Any]:
        """Get style configuration for edge"""
        base_style = {
            "width": 2,
            "arrows": {"to": {"enabled": True}}
        }
        
        if edge_type == "sequence":
            base_style["color"] = {"color": "#3498db"}
        elif edge_type == "dependency":
            base_style["color"] = {"color": "#e74c3c"}
            base_style["dashes"] = True
        
        return base_style
    
    def _get_metric_style(self, metric_type: str, value: float) -> Dict[str, Any]:
        """Get style for metric visualization"""
        base_style = {
            "shape": "box",
            "font": {"size": 14},
            "border": {"width": 3}
        }
        
        # Color based on metric value and type
        if metric_type in ["success_rate", "throughput"]:
            # Higher is better
            if value >= 0.9:
                base_style["color"] = {"background": "#2ecc71"}  # Green
            elif value >= 0.7:
                base_style["color"] = {"background": "#f39c12"}  # Orange
            else:
                base_style["color"] = {"background": "#e74c3c"}  # Red
        elif metric_type in ["error_rate"]:
            # Lower is better
            if value <= 0.1:
                base_style["color"] = {"background": "#2ecc71"}  # Green
            elif value <= 0.3:
                base_style["color"] = {"background": "#f39c12"}  # Orange
            else:
                base_style["color"] = {"background": "#e74c3c"}  # Red
        
        return base_style
    
    def _get_heatmap_style(self, metric: str, value: float) -> Dict[str, Any]:
        """Get style for heatmap cell"""
        # Normalize value to 0-1 range for color intensity
        normalized = min(max(value / 100.0, 0), 1) if metric in ["cpu_usage", "memory_usage"] else value
        
        # Calculate color intensity
        if metric == "error_rate":
            # Red for high error rate
            color = f"rgba(231, 76, 60, {normalized})"
        elif metric in ["cpu_usage", "memory_usage"]:
            # Orange for resource usage
            color = f"rgba(243, 156, 18, {normalized})"
        else:
            # Blue for response time
            color = f"rgba(52, 152, 219, {normalized})"
        
        return {
            "shape": "box",
            "color": {"background": color},
            "font": {"size": 10}
        }
    
    def _get_heatmap_status(self, metric: str, value: float) -> str:
        """Determine status for heatmap cell"""
        if metric == "error_rate":
            return "critical" if value > 0.1 else "normal"
        elif metric in ["cpu_usage", "memory_usage"]:
            return "warning" if value > 80 else "normal"
        elif metric == "response_time":
            return "warning" if value > 1000 else "normal"
        
        return "normal"
    
    def _calculate_network_position(self, index: int, total: int) -> Dict[str, float]:
        """Calculate position for network graph node"""
        import math
        
        # Arrange in circle
        angle = (2 * math.pi * index) / total
        radius = 300
        
        return {
            "x": radius * math.cos(angle),
            "y": radius * math.sin(angle)
        }
    
    async def get_visualization(self, visualization_id: str) -> Optional[Dict[str, Any]]:
        """Get visualization data"""
        if visualization_id in self.active_visualizations:
            return self.active_visualizations[visualization_id].to_dict()
        return None
    
    async def update_visualization(
        self,
        visualization_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update existing visualization"""
        if visualization_id not in self.active_visualizations:
            return False
        
        viz_data = self.active_visualizations[visualization_id]
        
        # Update nodes
        if "nodes" in updates:
            for node_update in updates["nodes"]:
                node_id = node_update.get("node_id")
                for node in viz_data.nodes:
                    if node.node_id == node_id:
                        if "status" in node_update:
                            node.status = node_update["status"]
                            node.style = self._get_node_style(node.node_type, node.status)
                        if "metadata" in node_update:
                            node.metadata.update(node_update["metadata"])
                        break
        
        # Update metadata
        if "metadata" in updates:
            viz_data.metadata.update(updates["metadata"])
        
        logger.debug(f"Updated visualization: {visualization_id}")
        return True
    
    async def delete_visualization(self, visualization_id: str) -> bool:
        """Delete visualization"""
        if visualization_id in self.active_visualizations:
            del self.active_visualizations[visualization_id]
            logger.info(f"Deleted visualization: {visualization_id}")
            return True
        return False
    
    async def list_visualizations(self) -> List[Dict[str, Any]]:
        """List all active visualizations"""
        return [
            {
                "visualization_id": viz_id,
                "type": viz_data.visualization_type.value,
                "title": viz_data.title,
                "created_at": viz_data.created_at.isoformat(),
                "node_count": len(viz_data.nodes),
                "edge_count": len(viz_data.edges)
            }
            for viz_id, viz_data in self.active_visualizations.items()
        ]
    
    async def export_visualization(
        self,
        visualization_id: str,
        format: str = "json"
    ) -> Optional[Dict[str, Any]]:
        """Export visualization in specified format"""
        if visualization_id not in self.active_visualizations:
            return None
        
        viz_data = self.active_visualizations[visualization_id]
        
        if format == "json":
            return viz_data.to_dict()
        elif format == "graphml":
            # Convert to GraphML format (simplified)
            return {
                "format": "graphml",
                "data": {
                    "nodes": [{"id": n.node_id, "label": n.label, "type": n.node_type} for n in viz_data.nodes],
                    "edges": [{"source": e.source_node, "target": e.target_node, "type": e.edge_type} for e in viz_data.edges]
                }
            }
        
        return None
    
    async def get_dashboard_config(self) -> Dict[str, Any]:
        """Get dashboard configuration"""
        return self.dashboard_config.copy()
    
    async def update_dashboard_config(self, config_updates: Dict[str, Any]):
        """Update dashboard configuration"""
        self.dashboard_config.update(config_updates)
        logger.info("Dashboard configuration updated")


# Global dashboard instance
_visualization_dashboard: Optional[SagaVisualizationDashboard] = None


def get_saga_visualization_dashboard() -> SagaVisualizationDashboard:
    """Get global saga visualization dashboard"""
    global _visualization_dashboard
    if _visualization_dashboard is None:
        _visualization_dashboard = SagaVisualizationDashboard()
    
    return _visualization_dashboard


# Convenience functions
async def create_saga_flow_viz(saga_id: str, saga_data: Dict[str, Any]) -> str:
    """Convenience function to create saga flow visualization"""
    dashboard = get_saga_visualization_dashboard()
    return await dashboard.create_saga_flow_diagram(saga_id, saga_data)


async def create_metrics_viz(metrics_data: Dict[str, Any]) -> str:
    """Convenience function to create metrics visualization"""
    dashboard = get_saga_visualization_dashboard()
    return await dashboard.create_metrics_dashboard(metrics_data)


__all__ = [
    "SagaVisualizationDashboard",
    "VisualizationData",
    "VisualizationNode",
    "VisualizationEdge",
    "VisualizationType",
    "get_saga_visualization_dashboard",
    "create_saga_flow_viz",
    "create_metrics_viz"
]