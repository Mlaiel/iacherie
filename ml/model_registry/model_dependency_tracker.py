"""🔍 Model Dependency Tracker - Enterprise ML Infrastructure
==========================================================
Module: ml/model_registry/model_dependency_tracker.py
Author: Fahed Mlaiel (mlaiel@live.de)
==========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODEL DEPENDENCY TRACKING SYSTEM
Enterprise model dependency tracking and impact analysis
- Model dependency graph construction
- Impact analysis for model updates
- Circular dependency detection
- Version compatibility validation
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
from pathlib import Path
from collections import defaultdict, deque

import networkx as nx
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of model dependencies"""
    DIRECT = "direct"
    TRANSITIVE = "transitive"
    CIRCULAR = "circular"
    OPTIONAL = "optional"
    RUNTIME = "runtime"
    BUILD_TIME = "build_time"


class DependencyStatus(Enum):
    """Dependency status"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    BROKEN = "broken"
    UPDATING = "updating"
    INCOMPATIBLE = "incompatible"


@dataclass
class ModelDependency:
    """Model dependency representation"""
    source_model_id: str
    target_model_id: str
    dependency_type: DependencyType
    version_constraint: str
    status: DependencyStatus = DependencyStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ImpactAnalysis:
    """Impact analysis result"""
    affected_models: List[str]
    impact_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    estimated_downtime: timedelta
    rollback_plan: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]


class ModelDependencyTracker:
    """Enterprise Model Dependency Tracking System"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.dependency_graph = nx.DiGraph()
        self.dependencies: Dict[str, ModelDependency] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        self.version_history: Dict[str, List[str]] = defaultdict(list)
        
        # Configuration
        self.max_dependency_depth = self.config.get('max_dependency_depth', 10)
        self.cache_ttl = self.config.get('cache_ttl', 3600)
        self.enable_circular_detection = self.config.get('enable_circular_detection', True)
        
        # Metrics
        self.metrics = {
            'dependency_checks': 0,
            'impact_analyses': 0,
            'circular_dependencies_detected': 0,
            'last_update': datetime.utcnow()
        }
        
        logger.info("🔍 Model Dependency Tracker initialized")
    
    async def register_dependency(
        self,
        source_model_id: str,
        target_model_id: str,
        dependency_type: DependencyType,
        version_constraint: str = "*",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a new model dependency"""
        try:
            dependency_id = f"{source_model_id}:{target_model_id}:{dependency_type.value}"
            
            dependency = ModelDependency(
                source_model_id=source_model_id,
                target_model_id=target_model_id,
                dependency_type=dependency_type,
                version_constraint=version_constraint,
                metadata=metadata or {}
            )
            
            self.dependencies[dependency_id] = dependency
            
            # Update dependency graph
            self.dependency_graph.add_edge(
                source_model_id,
                target_model_id,
                dependency_id=dependency_id,
                dependency_type=dependency_type.value,
                version_constraint=version_constraint
            )
            
            # Check for circular dependencies
            if self.enable_circular_detection:
                circular_deps = await self._detect_circular_dependencies()
                if circular_deps:
                    logger.warning(f"Circular dependencies detected: {circular_deps}")
                    self.metrics['circular_dependencies_detected'] += 1
            
            self.metrics['dependency_checks'] += 1
            
            logger.info(f"✅ Dependency registered: {source_model_id} -> {target_model_id}")
            return dependency_id
            
        except Exception as e:
            logger.error(f"❌ Error registering dependency: {e}")
            raise
    
    async def remove_dependency(self, dependency_id: str) -> bool:
        """Remove a model dependency"""
        try:
            if dependency_id not in self.dependencies:
                return False
            
            dependency = self.dependencies[dependency_id]
            
            # Remove from graph
            if self.dependency_graph.has_edge(
                dependency.source_model_id,
                dependency.target_model_id
            ):
                self.dependency_graph.remove_edge(
                    dependency.source_model_id,
                    dependency.target_model_id
                )
            
            # Remove from dependencies
            del self.dependencies[dependency_id]
            
            logger.info(f"✅ Dependency removed: {dependency_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error removing dependency: {e}")
            return False
    
    async def get_dependencies(
        self,
        model_id: str,
        dependency_type: Optional[DependencyType] = None,
        include_transitive: bool = False
    ) -> List[ModelDependency]:
        """Get model dependencies"""
        try:
            dependencies = []
            
            for dep_id, dependency in self.dependencies.items():
                if dependency.source_model_id == model_id:
                    if dependency_type is None or dependency.dependency_type == dependency_type:
                        dependencies.append(dependency)
            
            # Include transitive dependencies if requested
            if include_transitive:
                transitive_deps = await self._get_transitive_dependencies(model_id)
                dependencies.extend(transitive_deps)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"❌ Error getting dependencies: {e}")
            return []
    
    async def get_dependents(
        self,
        model_id: str,
        include_transitive: bool = False
    ) -> List[str]:
        """Get models that depend on this model"""
        try:
            dependents = []
            
            for dependency in self.dependencies.values():
                if dependency.target_model_id == model_id:
                    dependents.append(dependency.source_model_id)
            
            # Include transitive dependents if requested
            if include_transitive:
                transitive_dependents = await self._get_transitive_dependents(model_id)
                dependents.extend(transitive_dependents)
            
            return list(set(dependents))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"❌ Error getting dependents: {e}")
            return []
    
    async def analyze_impact(
        self,
        model_id: str,
        proposed_version: str,
        operation: str = "update"
    ) -> ImpactAnalysis:
        """Analyze impact of model changes"""
        try:
            self.metrics['impact_analyses'] += 1
            
            # Get all affected models
            affected_models = await self.get_dependents(model_id, include_transitive=True)
            
            # Assess impact level
            impact_level = await self._assess_impact_level(model_id, affected_models, operation)
            
            # Estimate downtime
            estimated_downtime = await self._estimate_downtime(affected_models, operation)
            
            # Generate rollback plan
            rollback_plan = await self._generate_rollback_plan(model_id, affected_models)
            
            # Risk assessment
            risk_assessment = await self._assess_risks(model_id, affected_models, operation)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                model_id, affected_models, impact_level
            )
            
            return ImpactAnalysis(
                affected_models=affected_models,
                impact_level=impact_level,
                estimated_downtime=estimated_downtime,
                rollback_plan=rollback_plan,
                risk_assessment=risk_assessment,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Error analyzing impact: {e}")
            raise
    
    async def validate_compatibility(
        self,
        model_id: str,
        version: str
    ) -> Dict[str, Any]:
        """Validate version compatibility with dependencies"""
        try:
            compatibility_results = {
                'compatible': True,
                'conflicts': [],
                'warnings': [],
                'recommendations': []
            }
            
            # Check direct dependencies
            dependencies = await self.get_dependencies(model_id)
            
            for dependency in dependencies:
                is_compatible = await self._check_version_compatibility(
                    dependency.target_model_id,
                    dependency.version_constraint
                )
                
                if not is_compatible:
                    compatibility_results['compatible'] = False
                    compatibility_results['conflicts'].append({
                        'target_model': dependency.target_model_id,
                        'constraint': dependency.version_constraint,
                        'current_version': version
                    })
            
            # Check dependents
            dependents = await self.get_dependents(model_id)
            
            for dependent_id in dependents:
                dependent_deps = await self.get_dependencies(dependent_id)
                for dep in dependent_deps:
                    if dep.target_model_id == model_id:
                        is_compatible = await self._check_version_compatibility(
                            version,
                            dep.version_constraint
                        )
                        
                        if not is_compatible:
                            compatibility_results['compatible'] = False
                            compatibility_results['conflicts'].append({
                                'dependent_model': dependent_id,
                                'constraint': dep.version_constraint,
                                'proposed_version': version
                            })
            
            return compatibility_results
            
        except Exception as e:
            logger.error(f"❌ Error validating compatibility: {e}")
            raise
    
    async def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the graph"""
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            return cycles
            
        except Exception as e:
            logger.error(f"❌ Error detecting circular dependencies: {e}")
            return []
    
    async def _get_transitive_dependencies(self, model_id: str) -> List[ModelDependency]:
        """Get transitive dependencies"""
        try:
            transitive_deps = []
            visited = set()
            queue = deque([model_id])
            
            while queue and len(visited) < self.max_dependency_depth:
                current_model = queue.popleft()
                if current_model in visited:
                    continue
                
                visited.add(current_model)
                
                # Get direct dependencies
                direct_deps = await self.get_dependencies(current_model)
                
                for dep in direct_deps:
                    if dep.target_model_id not in visited:
                        queue.append(dep.target_model_id)
                        # Mark as transitive
                        transitive_dep = ModelDependency(
                            source_model_id=model_id,
                            target_model_id=dep.target_model_id,
                            dependency_type=DependencyType.TRANSITIVE,
                            version_constraint=dep.version_constraint,
                            metadata={'original_source': current_model}
                        )
                        transitive_deps.append(transitive_dep)
            
            return transitive_deps
            
        except Exception as e:
            logger.error(f"❌ Error getting transitive dependencies: {e}")
            return []
    
    async def _get_transitive_dependents(self, model_id: str) -> List[str]:
        """Get transitive dependents"""
        try:
            transitive_dependents = []
            visited = set()
            queue = deque([model_id])
            
            while queue and len(visited) < self.max_dependency_depth:
                current_model = queue.popleft()
                if current_model in visited:
                    continue
                
                visited.add(current_model)
                
                # Get direct dependents
                direct_dependents = []
                for dependency in self.dependencies.values():
                    if dependency.target_model_id == current_model:
                        direct_dependents.append(dependency.source_model_id)
                
                for dependent in direct_dependents:
                    if dependent not in visited and dependent != model_id:
                        queue.append(dependent)
                        transitive_dependents.append(dependent)
            
            return transitive_dependents
            
        except Exception as e:
            logger.error(f"❌ Error getting transitive dependents: {e}")
            return []
    
    async def _assess_impact_level(
        self,
        model_id: str,
        affected_models: List[str],
        operation: str
    ) -> str:
        """Assess impact level of changes"""
        try:
            num_affected = len(affected_models)
            
            if num_affected == 0:
                return "LOW"
            elif num_affected <= 5:
                return "MEDIUM"
            elif num_affected <= 20:
                return "HIGH"
            else:
                return "CRITICAL"
                
        except Exception as e:
            logger.error(f"❌ Error assessing impact level: {e}")
            return "UNKNOWN"
    
    async def _estimate_downtime(
        self,
        affected_models: List[str],
        operation: str
    ) -> timedelta:
        """Estimate downtime for operation"""
        try:
            # Base downtime estimates per operation
            base_times = {
                'update': timedelta(minutes=10),
                'replace': timedelta(minutes=30),
                'remove': timedelta(minutes=5)
            }
            
            base_time = base_times.get(operation, timedelta(minutes=15))
            
            # Scale based on number of affected models
            scale_factor = max(1, len(affected_models) / 5)
            
            return base_time * scale_factor
            
        except Exception as e:
            logger.error(f"❌ Error estimating downtime: {e}")
            return timedelta(minutes=60)  # Default conservative estimate
    
    async def _generate_rollback_plan(
        self,
        model_id: str,
        affected_models: List[str]
    ) -> Dict[str, Any]:
        """Generate rollback plan"""
        try:
            return {
                'strategy': 'blue_green',
                'steps': [
                    f"1. Stop traffic to {model_id}",
                    f"2. Rollback {model_id} to previous version",
                    f"3. Validate {model_id} functionality",
                    f"4. Restart dependent models: {affected_models[:5]}",
                    "5. Verify system health"
                ],
                'estimated_time': '30 minutes',
                'risk_level': 'LOW',
                'automation_possible': True
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating rollback plan: {e}")
            return {}
    
    async def _assess_risks(
        self,
        model_id: str,
        affected_models: List[str],
        operation: str
    ) -> Dict[str, Any]:
        """Assess risks of operation"""
        try:
            risks = []
            
            if len(affected_models) > 10:
                risks.append("HIGH: Large number of affected models")
            
            if operation == "remove":
                risks.append("MEDIUM: Model removal may break dependent services")
            
            if await self._detect_circular_dependencies():
                risks.append("HIGH: Circular dependencies present")
            
            return {
                'risks': risks,
                'mitigation_strategies': [
                    "Use canary deployments",
                    "Implement circuit breakers",
                    "Prepare rollback procedures",
                    "Monitor health metrics closely"
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error assessing risks: {e}")
            return {}
    
    async def _generate_recommendations(
        self,
        model_id: str,
        affected_models: List[str],
        impact_level: str
    ) -> List[str]:
        """Generate recommendations for operation"""
        try:
            recommendations = []
            
            if impact_level in ["HIGH", "CRITICAL"]:
                recommendations.append("Schedule during maintenance window")
                recommendations.append("Notify all affected teams in advance")
                recommendations.append("Prepare detailed rollback plan")
            
            if len(affected_models) > 5:
                recommendations.append("Consider staged rollout")
                recommendations.append("Implement health checks for all affected models")
            
            recommendations.extend([
                "Backup current model versions",
                "Test in staging environment first",
                "Monitor system metrics during deployment"
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return []
    
    async def _check_version_compatibility(
        self,
        version: str,
        constraint: str
    ) -> bool:
        """Check if version satisfies constraint"""
        try:
            # Simplified version compatibility check
            # In practice, this would use semantic versioning
            if constraint == "*":
                return True
            
            if constraint.startswith(">="):
                required_version = constraint[2:]
                return version >= required_version
            
            if constraint.startswith("=="):
                required_version = constraint[2:]
                return version == required_version
            
            return True  # Default to compatible
            
        except Exception as e:
            logger.error(f"❌ Error checking version compatibility: {e}")
            return False
    
    async def get_dependency_graph(self) -> Dict[str, Any]:
        """Get dependency graph visualization data"""
        try:
            nodes = []
            edges = []
            
            # Add nodes
            for model_id in self.dependency_graph.nodes():
                nodes.append({
                    'id': model_id,
                    'label': model_id,
                    'type': 'model'
                })
            
            # Add edges
            for source, target, data in self.dependency_graph.edges(data=True):
                edges.append({
                    'source': source,
                    'target': target,
                    'type': data.get('dependency_type', 'direct'),
                    'constraint': data.get('version_constraint', '*')
                })
            
            return {
                'nodes': nodes,
                'edges': edges,
                'stats': {
                    'total_models': len(nodes),
                    'total_dependencies': len(edges),
                    'circular_dependencies': len(await self._detect_circular_dependencies())
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting dependency graph: {e}")
            return {'nodes': [], 'edges': [], 'stats': {}}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get tracker metrics"""
        return {
            **self.metrics,
            'total_dependencies': len(self.dependencies),
            'total_models': len(self.dependency_graph.nodes()),
            'graph_complexity': len(self.dependency_graph.edges())
        }


# Global instance
dependency_tracker = ModelDependencyTracker()


async def main() -> None:
    """Test the Model Dependency Tracker"""
    tracker = ModelDependencyTracker()
    
    print("🔍 Testing Model Dependency Tracker...")
    
    # Register dependencies
    await tracker.register_dependency(
        "model_a", "model_b", DependencyType.DIRECT, ">=1.0.0"
    )
    await tracker.register_dependency(
        "model_b", "model_c", DependencyType.DIRECT, ">=2.0.0"
    )
    await tracker.register_dependency(
        "model_c", "model_a", DependencyType.OPTIONAL, "*"
    )
    
    # Analyze impact
    impact = await tracker.analyze_impact("model_a", "2.0.0", "update")
    print(f"Impact analysis: {impact.impact_level}")
    print(f"Affected models: {impact.affected_models}")
    
    # Check compatibility
    compatibility = await tracker.validate_compatibility("model_a", "2.0.0")
    print(f"Compatibility: {compatibility['compatible']}")
    
    # Get metrics
    metrics = await tracker.get_metrics()
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())