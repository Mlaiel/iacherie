"""Feature Version Manager - Advanced versioning and lineage tracking

Manages feature versions, lineage tracking, and backward compatibility
for the centralized feature store.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of feature changes"""
    SCHEMA_UPDATE = "schema_update"
    DATA_UPDATE = "data_update"
    VALIDATION_CHANGE = "validation_change"
    DEPRECATION = "deprecation"
    ROLLBACK = "rollback"


@dataclass
class FeatureChange:
    """Feature change record"""
    change_id: str
    feature_name: str
    change_type: ChangeType
    old_version: str
    new_version: str
    description: str
    changed_by: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LineageNode:
    """Feature lineage node"""
    feature_name: str
    version: str
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    source_type: str = "feature_store"
    transformation: str = ""
    created_at: datetime = field(default_factory=datetime.now)


class FeatureVersionManager:
    """Advanced feature versioning and lineage management"""
    
    def __init__(self):
        self.changes: List[FeatureChange] = []
        self.lineage_graph: Dict[str, LineageNode] = {}
        self.version_compatibility: Dict[str, List[str]] = {}
        
        logger.info("Feature version manager initialized")
    
    
    async def create_version_change(self, feature_name: str, change_type: ChangeType,
                                   old_version: str, new_version: str, 
                                   description: str, changed_by: str = "system",
                                   metadata: Dict[str, Any] = None) -> str:
        """Record a feature version change"""
        try:
            change_id = str(uuid.uuid4())
            
            change = FeatureChange(
                change_id=change_id,
                feature_name=feature_name,
                change_type=change_type,
                old_version=old_version,
                new_version=new_version,
                description=description,
                changed_by=changed_by,
                metadata=metadata or {}
            )
            
            self.changes.append(change)
            
            # Update compatibility matrix
            await self._update_compatibility(feature_name, old_version, new_version)
            
            logger.info(f"Version change recorded: {feature_name} {old_version} -> {new_version}")
            return change_id
            
        except Exception as e:
            logger.error(f"Version change recording failed: {e}")
            raise
    
    
    async def add_lineage_node(self, feature_name: str, version: str,
                               dependencies: List[str] = None,
                               source_type: str = "feature_store",
                               transformation: str = "") -> bool:
        """Add a node to the feature lineage graph"""
        try:
            lineage_key = f"{feature_name}:{version}"
            
            node = LineageNode(
                feature_name=feature_name,
                version=version,
                dependencies=dependencies or [],
                source_type=source_type,
                transformation=transformation
            )
            
            self.lineage_graph[lineage_key] = node
            
            # Update dependent relationships
            if dependencies:
                for dep in dependencies:
                    if dep in self.lineage_graph:
                        self.lineage_graph[dep].dependents.append(lineage_key)
            
            logger.debug(f"Lineage node added: {lineage_key}")
            return True
            
        except Exception as e:
            logger.error(f"Lineage node addition failed: {e}")
            return False
    
    
    async def get_feature_lineage(self, feature_name: str, version: str = None) -> Dict[str, Any]:
        """Get complete lineage for a feature"""
        try:
            if version:
                lineage_key = f"{feature_name}:{version}"
                if lineage_key in self.lineage_graph:
                    node = self.lineage_graph[lineage_key]
                    return {
                        "feature": lineage_key,
                        "dependencies": node.dependencies,
                        "dependents": node.dependents,
                        "source_type": node.source_type,
                        "transformation": node.transformation,
                        "created_at": node.created_at.isoformat()
                    }
            else:
                # Get lineage for all versions of the feature
                lineage = {}
                for key, node in self.lineage_graph.items():
                    if node.feature_name == feature_name:
                        lineage[key] = {
                            "dependencies": node.dependencies,
                            "dependents": node.dependents,
                            "source_type": node.source_type,
                            "transformation": node.transformation,
                            "created_at": node.created_at.isoformat()
                        }
                return lineage
            
            return {}
            
        except Exception as e:
            logger.error(f"Lineage retrieval failed: {e}")
            return {}
    
    
    async def get_version_history(self, feature_name: str) -> List[Dict[str, Any]]:
        """Get complete version history for a feature"""
        try:
            feature_changes = [
                asdict(change) for change in self.changes 
                if change.feature_name == feature_name
            ]
            
            # Sort by timestamp
            feature_changes.sort(key=lambda x: x['timestamp'])
            
            return feature_changes
            
        except Exception as e:
            logger.error(f"Version history retrieval failed: {e}")
            return []
    
    
    async def check_compatibility(self, feature_name: str, 
                                  old_version: str, new_version: str) -> bool:
        """Check if two versions are compatible"""
        try:
            compatible_versions = self.version_compatibility.get(
                f"{feature_name}:{old_version}", []
            )
            
            return f"{feature_name}:{new_version}" in compatible_versions
            
        except Exception as e:
            logger.error(f"Compatibility check failed: {e}")
            return False
    
    
    async def get_compatible_versions(self, feature_name: str, version: str) -> List[str]:
        """Get all compatible versions for a feature version"""
        try:
            compatibility_key = f"{feature_name}:{version}"
            return self.version_compatibility.get(compatibility_key, [])
            
        except Exception as e:
            logger.error(f"Compatible versions retrieval failed: {e}")
            return []
    
    
    async def rollback_version(self, feature_name: str, target_version: str,
                               rolled_back_by: str = "system") -> bool:
        """Rollback to a specific version"""
        try:
            # Find current version
            current_changes = [
                c for c in self.changes 
                if c.feature_name == feature_name
            ]
            
            if not current_changes:
                logger.error(f"No version history found for {feature_name}")
                return False
            
            current_version = current_changes[-1].new_version
            
            # Record rollback change
            await self.create_version_change(
                feature_name=feature_name,
                change_type=ChangeType.ROLLBACK,
                old_version=current_version,
                new_version=target_version,
                description=f"Rollback from {current_version} to {target_version}",
                changed_by=rolled_back_by,
                metadata={"rollback_reason": "manual_rollback"}
            )
            
            logger.info(f"Version rollback completed: {feature_name} -> {target_version}")
            return True
            
        except Exception as e:
            logger.error(f"Version rollback failed: {e}")
            return False
    
    
    async def analyze_impact(self, feature_name: str, version: str) -> Dict[str, Any]:
        """Analyze impact of changing a feature version"""
        try:
            lineage_key = f"{feature_name}:{version}"
            
            if lineage_key not in self.lineage_graph:
                return {"impact": "unknown", "affected_features": []}
            
            node = self.lineage_graph[lineage_key]
            
            # Find all downstream dependencies
            affected = []
            to_check = node.dependents.copy()
            checked = set()
            
            while to_check:
                dependent = to_check.pop(0)
                if dependent not in checked:
                    checked.add(dependent)
                    affected.append(dependent)
                    
                    # Add further dependents
                    if dependent in self.lineage_graph:
                        to_check.extend(self.lineage_graph[dependent].dependents)
            
            impact_level = "low"
            if len(affected) > 10:
                impact_level = "high"
            elif len(affected) > 3:
                impact_level = "medium"
            
            return {
                "impact": impact_level,
                "affected_features": affected,
                "direct_dependents": node.dependents,
                "total_affected": len(affected)
            }
            
        except Exception as e:
            logger.error(f"Impact analysis failed: {e}")
            return {"impact": "unknown", "affected_features": []}
    
    
    async def _update_compatibility(self, feature_name: str, 
                                    old_version: str, new_version: str):
        """Update version compatibility matrix"""
        try:
            old_key = f"{feature_name}:{old_version}"
            new_key = f"{feature_name}:{new_version}"
            
            # Initialize compatibility lists if not exist
            if old_key not in self.version_compatibility:
                self.version_compatibility[old_key] = []
            if new_key not in self.version_compatibility:
                self.version_compatibility[new_key] = []
            
            # Simple compatibility rule: adjacent versions are compatible
            # In production, this would use more sophisticated rules
            self.version_compatibility[old_key].append(new_key)
            self.version_compatibility[new_key].append(old_key)
            
        except Exception as e:
            logger.error(f"Compatibility update failed: {e}")
    
    
    async def export_lineage_graph(self) -> Dict[str, Any]:
        """Export the complete lineage graph"""
        try:
            return {
                "nodes": {
                    key: asdict(node) for key, node in self.lineage_graph.items()
                },
                "compatibility": self.version_compatibility,
                "exported_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Lineage graph export failed: {e}")
            return {}
    
    
    async def import_lineage_graph(self, graph_data: Dict[str, Any]) -> bool:
        """Import lineage graph from data"""
        try:
            if "nodes" in graph_data:
                for key, node_data in graph_data["nodes"].items():
                    # Convert datetime strings back to datetime objects
                    if "created_at" in node_data:
                        node_data["created_at"] = datetime.fromisoformat(node_data["created_at"])
                    
                    self.lineage_graph[key] = LineageNode(**node_data)
            
            if "compatibility" in graph_data:
                self.version_compatibility.update(graph_data["compatibility"])
            
            logger.info("Lineage graph imported successfully")
            return True
            
        except Exception as e:
            logger.error(f"Lineage graph import failed: {e}")
            return False