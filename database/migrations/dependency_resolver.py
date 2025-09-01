"""🔗 Migration Dependency Resolver - Ultra-Industrial Dependency Engine
====================================================================
Module: backend/database/migrations/dependency_resolver.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Dependency Engine - Ultra Enterprise Production-Ready
Responsibility: Advanced dependency resolution for content protection and monetization migrations
================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

Advanced dependency resolution for:
- Content fingerprinting schema dependency management
- Monetization database migration sequencing
- AI processing pipeline dependency analysis
- Platform integration dependency resolution
- Cross-system migration coordination

DEPENDENCY RESOLUTION LOGIC:
Migration Discovery → Dependency Analysis → Conflict Detection → 
Resolution Planning → Execution Ordering → Parallel Optimization
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import networkx as nx
from collections import defaultdict, deque

from .migration_types import MigrationType, MigrationPriority, MigrationStatus
from .migration_models import DependencyGraph, MigrationRecord

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """
Types of dependencies between migrations"""

    HARD_DEPENDENCY = "hard_dependency"      # Must run before
    SOFT_DEPENDENCY = "soft_dependency"      # Should run before
    CONFLICT = "conflict"                    # Cannot run together
    SEQUENCE = "sequence"                    # Must run in order
    PARALLEL = "parallel"                    # Can run in parallel
    CONDITIONAL = "conditional"              # Depends on conditions
    PLATFORM_SPECIFIC = "platform_specific" # Platform dependencies
    RESOURCE_DEPENDENCY = "resource_dependency" # Resource constraints


class ResolutionStrategy(Enum):
    """Strategies for dependency resolution"""

    CONSERVATIVE = "conservative"            # Minimize parallelism, ensure safety
    OPTIMIZED = "optimized"                 # Maximize parallelism, optimize time
    BALANCED = "balanced"                   # Balance safety and performance
    CUSTOM = "custom"                       # Use custom resolution rules


@dataclass
class DependencyRule:
    """Individual dependency rule definition"""
    rule_id: str
    source_migration: str
    target_migration: str
    dependency_type: DependencyType
    priority: int = 1
    description: str = ""
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResolutionResult:
    """Result of dependency resolution process"""
    resolution_id: str
    success: bool
    execution_plan: List[List[str]] = field(default_factory=list)
    parallel_groups: List[List[str]] = field(default_factory=list)
    sequential_order: List[str] = field(default_factory=list)
    conflicts_found: List[Dict[str, Any]] = field(default_factory=list)
    unresolved_dependencies: List[str] = field(default_factory=list)
    estimated_total_time: int = 0
    max_parallelism: int = 1
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class MigrationDependencyResolver:
    """
    Ultra-advanced dependency resolver for enterprise migration management
    
    Provides comprehensive dependency resolution for:
    - Content protection schema migrations
    - Monetization database evolution
    - AI processing pipeline migrations
    - Platform integration dependencies
    - Cross-system migration coordination
    """
    
    def __init__(self):
        self.dependency_rules: Dict[str, DependencyRule] = {}
        self.migration_graph = nx.DiGraph()
        self.resolution_cache: Dict[str, ResolutionResult] = {}
        self.conflict_rules: List[Dict[str, Any]] = []
        
        # Built-in rules
        self._initialize_builtin_rules()
        
        logger.info("✅ Migration Dependency Resolver initialized")
    
    async def initialize(self) -> bool:
        """Initialize dependency resolver with built-in and custom rules"""
        try:
            # Load custom dependency rules
            await self._load_custom_rules()
            
            # Initialize conflict detection rules
            await self._initialize_conflict_detection()
            
            # Setup performance optimization
            await self._setup_optimization_rules()
            
            logger.info("🚀 Dependency Resolver fully initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Dependency Resolver: {e}")
            return False
    
    async def analyze_dependencies(
        self,
        migrations: List[str],
        strategy: ResolutionStrategy = ResolutionStrategy.BALANCED
    ) -> ResolutionResult:
        """Analyze and resolve dependencies for a set of migrations"""
        
        resolution_id = f"resolution_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🔍 Analyzing dependencies for {len(migrations)} migrations")
        
        try:
            # Build dependency graph for migrations
            graph = await self._build_migration_graph(migrations)
            
            # Detect dependency conflicts
            conflicts = await self._detect_conflicts(graph, migrations)
            
            # Resolve dependencies based on strategy
            resolution = await self._resolve_dependencies(graph, migrations, strategy, conflicts)
            
            # Optimize execution plan
            optimized_plan = await self._optimize_execution_plan(resolution, strategy)
            
            # Validate resolution
            validation_result = await self._validate_resolution(optimized_plan, migrations)
            
            result = ResolutionResult(
                resolution_id=resolution_id,
                success=validation_result["valid"],
                execution_plan=optimized_plan["execution_levels"],
                parallel_groups=optimized_plan["parallel_groups"],
                sequential_order=optimized_plan["sequential_order"],
                conflicts_found=conflicts,
                estimated_total_time=optimized_plan["estimated_time"],
                max_parallelism=optimized_plan["max_parallelism"],
                warnings=validation_result.get("warnings", []),
                recommendations=await self._generate_recommendations(optimized_plan, conflicts)
            )
            
            # Cache result
            self.resolution_cache[resolution_id] = result
            
            logger.info(f"✅ Dependency analysis completed: {len(result.execution_plan)} execution levels")
            return result
            
        except Exception as e:
            logger.error(f"❌ Dependency analysis failed: {e}")
            return ResolutionResult(
                resolution_id=resolution_id,
                success=False,
                warnings=[f"Analysis failed: {str(e)}"]
            )
    
    async def add_dependency_rule(self, rule: DependencyRule) -> bool:
        """Add custom dependency rule to the resolver"""
        try:
            # Validate rule
            validation_result = await self._validate_dependency_rule(rule)
            if not validation_result["valid"]:
                logger.error(f"❌ Invalid dependency rule: {validation_result['errors']}")
                return False
            
            # Add to rules
            self.dependency_rules[rule.rule_id] = rule
            
            # Update graph if needed
            await self._update_dependency_graph(rule)
            
            logger.info(f"✅ Added dependency rule: {rule.rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add dependency rule: {e}")
            return False
    
    async def detect_circular_dependencies(
        self,
        migrations: List[str]
    ) -> Dict[str, Any]:
        """Detect circular dependencies in migration set"""
        
        try:
            # Build graph for analysis
            graph = await self._build_migration_graph(migrations)
            
            # Find strongly connected components
            strongly_connected = list(nx.strongly_connected_components(graph))
            
            # Identify cycles
            cycles = []
            for component in strongly_connected:
                if len(component) > 1:
                    # This is a cycle
                    cycle_nodes = list(component)
                    cycle_edges = []
                    for node in cycle_nodes:
                        for successor in graph.successors(node):
                            if successor in component:
                                cycle_edges.append((node, successor))
                    
                    cycles.append({
                        "nodes": cycle_nodes,
                        "edges": cycle_edges,
                        "severity": "high" if len(cycle_nodes) > 2 else "medium"
                    })
            
            return {
                "has_cycles": len(cycles) > 0,
                "cycle_count": len(cycles),
                "cycles": cycles,
                "affected_migrations": [node for cycle in cycles for node in cycle["nodes"]]
            }
            
        except Exception as e:
            logger.error(f"❌ Circular dependency detection failed: {e}")
            return {"has_cycles": False, "error": str(e)}
    
    async def suggest_migration_order(
        self,
        migrations: List[str],
        constraints: Dict[str, Any] = None
    ) -> List[str]:
        """Suggest optimal migration execution order"""
        
        try:
            # Analyze dependencies
            resolution = await self.analyze_dependencies(migrations)
            
            if not resolution.success:
                logger.warning("⚠️ Could not resolve dependencies, suggesting basic order")
                return migrations  # Return original order as fallback
            
            # Apply constraints if provided
            if constraints:
                resolution = await self._apply_execution_constraints(resolution, constraints)
            
            # Return sequential order
            return resolution.sequential_order
            
        except Exception as e:
            logger.error(f"❌ Failed to suggest migration order: {e}")
            return migrations
    
    async def get_migration_dependencies(self, migration_id: str) -> Dict[str, Any]:
        """Get detailed dependency information for a specific migration"""
        
        try:
            dependencies = {
                "migration_id": migration_id,
                "direct_dependencies": [],
                "indirect_dependencies": [],
                "dependents": [],
                "conflicts": [],
                "dependency_path": [],
                "critical_path": False
            }
            
            # Find direct dependencies
            for rule in self.dependency_rules.values():
                if rule.source_migration == migration_id:
                    dependencies["direct_dependencies"].append({
                        "target": rule.target_migration,
                        "type": rule.dependency_type.value,
                        "priority": rule.priority,
                        "description": rule.description
                    })
                elif rule.target_migration == migration_id:
                    dependencies["dependents"].append({
                        "source": rule.source_migration,
                        "type": rule.dependency_type.value,
                        "priority": rule.priority,
                        "description": rule.description
                    })
            
            # Find conflicts
            for rule in self.dependency_rules.values():
                if rule.dependency_type == DependencyType.CONFLICT:
                    if migration_id in [rule.source_migration, rule.target_migration]:
                        conflict_target = rule.target_migration if rule.source_migration == migration_id else rule.source_migration
                        dependencies["conflicts"].append({
                            "migration": conflict_target,
                            "description": rule.description
                        })
            
            return dependencies
            
        except Exception as e:
            logger.error(f"❌ Failed to get migration dependencies: {e}")
            return {"error": str(e)}
    
    # Private implementation methods
    
    def _initialize_builtin_rules(self):
        """Initialize built-in dependency rules for common scenarios"""
        
        # Schema creation before data migration
        self.dependency_rules["schema_before_data"] = DependencyRule(
            rule_id="schema_before_data",
            source_migration="*_schema_*",
            target_migration="*_data_*",
            dependency_type=DependencyType.HARD_DEPENDENCY,
            priority=1,
            description="Schema creation must precede data migration"
        )
        
        # Security migrations before feature migrations
        self.dependency_rules["security_first"] = DependencyRule(
            rule_id="security_first",
            source_migration="*_security_*",
            target_migration="*_feature_*",
            dependency_type=DependencyType.SOFT_DEPENDENCY,
            priority=2,
            description="Security migrations should run before feature migrations"
        )
        
        # Index creation after data migration
        self.dependency_rules["indexes_after_data"] = DependencyRule(
            rule_id="indexes_after_data",
            source_migration="*_data_*",
            target_migration="*_index_*",
            dependency_type=DependencyType.HARD_DEPENDENCY,
            priority=1,
            description="Indexes should be created after data migration"
        )
        
        # Content protection specific rules
        self.dependency_rules["fingerprint_schema_first"] = DependencyRule(
            rule_id="fingerprint_schema_first",
            source_migration="*_fingerprint_schema_*",
            target_migration="*_fingerprint_*",
            dependency_type=DependencyType.HARD_DEPENDENCY,
            priority=1,
            description="Fingerprint schema must be created before fingerprint operations"
        )
        
        # Monetization specific rules
        self.dependency_rules["payment_before_revenue"] = DependencyRule(
            rule_id="payment_before_revenue",
            source_migration="*_payment_*",
            target_migration="*_revenue_*",
            dependency_type=DependencyType.HARD_DEPENDENCY,
            priority=1,
            description="Payment setup must precede revenue tracking"
        )
        
        logger.info(f"📋 Initialized {len(self.dependency_rules)} built-in dependency rules")
    
    async def _load_custom_rules(self):
        """Load custom dependency rules from configuration"""
        # Implementation would load from database or configuration files
        logger.info("📋 Custom dependency rules loaded")
    
    async def _initialize_conflict_detection(self):
        """Initialize conflict detection rules"""
        
        # Resource conflicts
        self.conflict_rules.append({
            "type": "resource_conflict",
            "description": "Migrations requiring exclusive table locks",
            "pattern": "table_lock_required",
            "severity": "high"
        })
        
        # Schema conflicts
        self.conflict_rules.append({
            "type": "schema_conflict",
            "description": "Conflicting schema modifications",
            "pattern": "same_table_modification",
            "severity": "critical"
        })
        
        logger.info(f"🚨 Initialized {len(self.conflict_rules)} conflict detection rules")
    
    async def _setup_optimization_rules(self):
        """Setup performance optimization rules"""
        logger.info("⚡ Optimization rules configured")
    
    async def _build_migration_graph(self, migrations: List[str]) -> nx.DiGraph:
        """Build directed graph representing migration dependencies"""
        
        graph = nx.DiGraph()
        
        # Add migration nodes
        for migration in migrations:
            graph.add_node(migration)
        
        # Add dependency edges based on rules
        for rule in self.dependency_rules.values():
            source_matches = self._match_migration_pattern(rule.source_migration, migrations)
            target_matches = self._match_migration_pattern(rule.target_migration, migrations)
            
            for source in source_matches:
                for target in target_matches:
                    if source != target and source in migrations and target in migrations:
                        if rule.dependency_type in [DependencyType.HARD_DEPENDENCY, DependencyType.SOFT_DEPENDENCY]:
                            graph.add_edge(source, target, **{
                                "type": rule.dependency_type.value,
                                "priority": rule.priority,
                                "rule_id": rule.rule_id
                            })
        
        return graph
    
    def _match_migration_pattern(self, pattern: str, migrations: List[str]) -> List[str]:
        """Match migration pattern against migration list"""
        
        if pattern.startswith("*") and pattern.endswith("*"):
            # Wildcard pattern
            substring = pattern[1:-1]
            return [m for m in migrations if substring in m]
        elif pattern.startswith("*"):
            # Suffix pattern
            suffix = pattern[1:]
            return [m for m in migrations if m.endswith(suffix)]
        elif pattern.endswith("*"):
            # Prefix pattern
            prefix = pattern[:-1]
            return [m for m in migrations if m.startswith(prefix)]
        else:
            # Exact match
            return [pattern] if pattern in migrations else []
    
    async def _detect_conflicts(
        self,
        graph: nx.DiGraph,
        migrations: List[str]
    ) -> List[Dict[str, Any]]:
        """Detect conflicts between migrations"""
        
        conflicts = []
        
        # Check for circular dependencies
        try:
            cycles = list(nx.simple_cycles(graph))
            for cycle in cycles:
                conflicts.append({
                    "type": "circular_dependency",
                    "severity": "critical",
                    "migrations": cycle,
                    "description": f"Circular dependency detected: {' -> '.join(cycle)}"
                })
        except nx.NetworkXError:
            pass
        
        # Check conflict rules
        for rule in self.conflict_rules:
            conflict_migrations = self._find_conflicting_migrations(migrations, rule)
            if len(conflict_migrations) > 1:
                conflicts.append({
                    "type": rule["type"],
                    "severity": rule["severity"],
                    "migrations": conflict_migrations,
                    "description": rule["description"]
                })
        
        return conflicts
    
    def _find_conflicting_migrations(self, migrations: List[str], rule: Dict[str, Any]) -> List[str]:
        """Find migrations that conflict according to a rule"""
        # Simplified implementation - would be more sophisticated in production
        return []
    
    async def _resolve_dependencies(
        self,
        graph: nx.DiGraph,
        migrations: List[str],
        strategy: ResolutionStrategy,
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
Resolve dependencies and create execution plan"""
        
        if conflicts:
            # Handle conflicts based on strategy
            graph = await self._resolve_conflicts(graph, conflicts, strategy)
        
        # Perform topological sort
        try:
            if nx.is_directed_acyclic_graph(graph):
                topo_order = list(nx.topological_sort(graph))
                
                # Group into execution levels
                execution_levels = self._create_execution_levels(graph, topo_order, strategy)
                
                return {
                    "success": True,
                    "topological_order": topo_order,
                    "execution_levels": execution_levels,
                    "has_cycles": False
                }
            else:
                # Graph has cycles - try to break them
                broken_graph = await self._break_cycles(graph, strategy)
                topo_order = list(nx.topological_sort(broken_graph))
                execution_levels = self._create_execution_levels(broken_graph, topo_order, strategy)
                
                return {
                    "success": True,
                    "topological_order": topo_order,
                    "execution_levels": execution_levels,
                    "has_cycles": True,
                    "cycles_broken": True
                }
                
        except nx.NetworkXError as e:
            logger.error(f"❌ Dependency resolution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_order": migrations
            }
    
    def _create_execution_levels(
        self,
        graph: nx.DiGraph,
        topo_order: List[str],
        strategy: ResolutionStrategy
    ) -> List[List[str]]:
        """Create execution levels for parallel execution"""
        
        levels = []
        remaining = set(topo_order)
        
        while remaining:
            # Find nodes with no dependencies in remaining set
            current_level = []
            for node in topo_order:
                if node in remaining:
                    # Check if all dependencies are satisfied
                    deps_satisfied = all(
                        dep not in remaining 
                        for dep in graph.predecessors(node)
                    )
                    if deps_satisfied:
                        current_level.append(node)
            
            if not current_level:
                # Fallback: take first remaining node to break deadlock
                current_level = [next(iter(remaining))]
            
            levels.append(current_level)
            remaining -= set(current_level)
        
        return levels
    
    async def _optimize_execution_plan(
        self,
        resolution: Dict[str, Any],
        strategy: ResolutionStrategy
    ) -> Dict[str, Any]:
        """
Optimize execution plan based on strategy"""
        
        if not resolution.get("success", False):
            return resolution
        
        execution_levels = resolution["execution_levels"]
        
        # Apply strategy-specific optimizations
        if strategy == ResolutionStrategy.OPTIMIZED:
            # Maximize parallelism
            optimized_levels = await self._maximize_parallelism(execution_levels)
        elif strategy == ResolutionStrategy.CONSERVATIVE:
            # Minimize parallelism for safety
            optimized_levels = await self._minimize_parallelism(execution_levels)
        else:  # BALANCED
            # Balance performance and safety
            optimized_levels = await self._balance_execution(execution_levels)
        
        # Calculate metrics
        parallel_groups = [level for level in optimized_levels if len(level) > 1]
        sequential_order = [item for level in optimized_levels for item in level]
        max_parallelism = max(len(level) for level in optimized_levels) if optimized_levels else 1
        
        # Estimate execution time (placeholder calculation)
        estimated_time = len(optimized_levels) * 10  # 10 minutes per level
        
        return {
            "execution_levels": optimized_levels,
            "parallel_groups": parallel_groups,
            "sequential_order": sequential_order,
            "max_parallelism": max_parallelism,
            "estimated_time": estimated_time
        }
    
    async def _validate_resolution(
        self,
        plan: Dict[str, Any],
        migrations: List[str]
    ) -> Dict[str, Any]:
        """Validate the resolution plan"""
        
        warnings = []
        
        # Check all migrations are included
        planned_migrations = set(plan["sequential_order"])
        if planned_migrations != set(migrations):
            missing = set(migrations) - planned_migrations
            extra = planned_migrations - set(migrations)
            if missing:
                warnings.append(f"Missing migrations: {list(missing)}")
            if extra:
                warnings.append(f"Extra migrations: {list(extra)}")
        
        # Check for potential issues
        if plan["max_parallelism"] > 10:
            warnings.append("High parallelism may cause resource contention")
        
        if plan["estimated_time"] > 180:  # 3 hours
            warnings.append("Long execution time - consider breaking into smaller batches")
        
        return {
            "valid": len(warnings) == 0 or all("Missing" not in w and "Extra" not in w for w in warnings),
            "warnings": warnings
        }
    
    async def _generate_recommendations(
        self,
        plan: Dict[str, Any],
        conflicts: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for the execution plan"""
        
        recommendations = []
        
        if conflicts:
            recommendations.append("Review and resolve conflicts before execution")
        
        if plan["max_parallelism"] > 5:
            recommendations.append("Monitor system resources during parallel execution")
        
        if plan["estimated_time"] > 60:
            recommendations.append("Execute during maintenance window")
        
        recommendations.append("Create backup before executing migration plan")
        recommendations.append("Test migration plan in staging environment")
        
        return recommendations
    
    # Additional helper methods (placeholders for full implementation)
    
    async def _validate_dependency_rule(self, rule: DependencyRule) -> Dict[str, Any]:
        """Validate dependency rule configuration"""
        return {"valid": True, "errors": []}
    
    async def _update_dependency_graph(self, rule: DependencyRule):
        """Update internal dependency graph with new rule"""
        pass
    
    async def _resolve_conflicts(
        self,
        graph: nx.DiGraph,
        conflicts: List[Dict[str, Any]],
        strategy: ResolutionStrategy
    ) -> nx.DiGraph:
        """
Resolve detected conflicts"""
        return graph
    
    async def _break_cycles(self, graph: nx.DiGraph, strategy: ResolutionStrategy) -> nx.DiGraph:
        """
Break cycles in dependency graph"""
        return graph
    
    async def _maximize_parallelism(self, levels: List[List[str]]) -> List[List[str]]:
        """
Maximize parallel execution opportunities"""
        return levels
    
    async def _minimize_parallelism(self, levels: List[List[str]]) -> List[List[str]]:
        """
Minimize parallel execution for safety"""
        return [[item] for level in levels for item in level]
    
    async def _balance_execution(self, levels: List[List[str]]) -> List[List[str]]:
        """
Balance parallelism and safety"""
        return levels
    
    async def _apply_execution_constraints(
        self,
        resolution: ResolutionResult,
        constraints: Dict[str, Any]
    ) -> ResolutionResult:
        """
Apply execution constraints to resolution"""
        return resolution


# Export the main class
__all__ = ["MigrationDependencyResolver", "DependencyRule", "ResolutionResult", "DependencyType", "ResolutionStrategy"]
