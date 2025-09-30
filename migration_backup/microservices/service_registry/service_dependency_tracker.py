#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 SERVICE REGISTRY ENTERPRISE - SERVICE DEPENDENCY TRACKER
===========================================================

**Author**: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer)
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Project**: Ainflue Service Registry Enterprise
**Version**: 1.0 Production
**Created**: 2025-01-07 | Updated: 2025-12-14

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture service registry et tous ses algorithmes sont la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

🔗 SERVICE DEPENDENCY TRACKER
Tracker dépendances services avec impact analysis.
Dependency mapping + impact assessment + change propagation analysis.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Set, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import networkx as nx
from collections import defaultdict, deque

# Core logger
logger = logging.getLogger(__name__)

class DependencyType(Enum):
    """Types de dépendances"""
    DIRECT = "direct"
    INDIRECT = "indirect"
    CIRCULAR = "circular"
    WEAK = "weak"
    STRONG = "strong"
    TEMPORAL = "temporal"
    DATA = "data"
    FUNCTIONAL = "functional"

class DependencyDirection(Enum):
    """Direction des dépendances"""
    UPSTREAM = "upstream"    # Services dont ce service dépend
    DOWNSTREAM = "downstream"  # Services qui dépendent de ce service
    BIDIRECTIONAL = "bidirectional"

class ImpactLevel(Enum):
    """Niveaux d'impact"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ChangeType(Enum):
    """Types de changements"""
    DEPLOYMENT = "deployment"
    CONFIGURATION = "configuration"
    SCALING = "scaling"
    SHUTDOWN = "shutdown"
    RESTART = "restart"
    MIGRATION = "migration"
    UPDATE = "update"

@dataclass
class ServiceDependency:
    """Dépendance entre services"""
    source_service_id: str
    target_service_id: str
    dependency_type: DependencyType
    dependency_strength: float  # 0.0 à 1.0
    created_at: float
    last_verified: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_critical: bool = False
    retry_policy: Optional[Dict[str, Any]] = None
    fallback_strategy: Optional[str] = None

@dataclass
class DependencyGraph:
    """Graphe de dépendances"""
    services: Set[str]
    dependencies: List[ServiceDependency]
    graph_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

@dataclass
class ImpactAssessment:
    """Évaluation d'impact"""
    affected_service_id: str
    impact_level: ImpactLevel
    impact_description: str
    estimated_downtime_minutes: int
    affected_functionality: List[str]
    mitigation_strategies: List[str]
    recovery_time_estimate_minutes: int
    business_impact: str
    confidence_score: float

@dataclass
class ChangeImpactAnalysis:
    """Analyse d'impact de changement"""
    change_type: ChangeType
    source_service_id: str
    impact_assessments: List[ImpactAssessment]
    propagation_path: List[str]
    total_affected_services: int
    estimated_total_downtime_minutes: int
    risk_level: str
    recommended_actions: List[str]
    rollback_plan: Optional[Dict[str, Any]] = None

@dataclass
class DependencyTrackingResult:
    """Résultat de tracking des dépendances"""
    tracking_timestamp: datetime
    dependency_graph: DependencyGraph
    circular_dependencies: List[List[str]]
    critical_paths: List[List[str]]
    isolated_services: List[str]
    dependency_health_score: float
    recommendations: List[str]
    warnings: List[str]

class ServiceDependencyTracker:
    """
    Tracker dépendances services avec impact analysis.
    Dependency mapping + impact assessment + change propagation analysis.
    """
    
    def __init__(self, tracking_config: Dict[str, Any] = None):
        """Initialisation du tracker de dépendances"""
        self.tracking_config = tracking_config or {}
        self.dependency_graph: nx.DiGraph = nx.DiGraph()
        self.service_dependencies: Dict[str, List[ServiceDependency]] = defaultdict(list)
        self.dependency_history: List[DependencyGraph] = []
        
        # Composants spécialisés
        self.graph_analyzer = DependencyGraphAnalyzer()
        self.impact_calculator = ImpactCalculator()
        self.change_propagator = ChangePropagator()
        self.health_assessor = DependencyHealthAssessor()
        
        logger.info("🔗 Service Dependency Tracker initialized")

    async def track_service_dependencies(
        self, 
        tracking_config: Dict[str, Any]
    ) -> DependencyTrackingResult:
        """
        Tracking dépendances service avec impact modeling.
        
        Features:
        - Dependency graph construction and analysis
        - Circular dependency detection
        - Critical path identification
        - Impact propagation modeling
        - Health scoring
        """
        try:
            tracking_start = datetime.now()
            
            # Construction du graphe de dépendances
            dependency_graph = await self._build_dependency_graph(tracking_config)
            
            # Détection des dépendances circulaires
            circular_dependencies = await self._detect_circular_dependencies()
            
            # Identification des chemins critiques
            critical_paths = await self._identify_critical_paths()
            
            # Identification des services isolés
            isolated_services = await self._find_isolated_services()
            
            # Calcul du score de santé des dépendances
            health_score = await self._calculate_dependency_health_score()
            
            # Génération des recommandations
            recommendations = await self._generate_dependency_recommendations(
                circular_dependencies, critical_paths, isolated_services
            )
            
            # Génération des avertissements
            warnings = await self._generate_dependency_warnings(
                circular_dependencies, critical_paths
            )
            
            # Sauvegarde de l'historique
            self.dependency_history.append(dependency_graph)
            self._cleanup_old_history()
            
            logger.info(
                f"🔗 Dependency tracking completed: {len(dependency_graph.services)} services, "
                f"{len(dependency_graph.dependencies)} dependencies, "
                f"{len(circular_dependencies)} circular dependencies detected"
            )
            
            return DependencyTrackingResult(
                tracking_timestamp=tracking_start,
                dependency_graph=dependency_graph,
                circular_dependencies=circular_dependencies,
                critical_paths=critical_paths,
                isolated_services=isolated_services,
                dependency_health_score=health_score,
                recommendations=recommendations,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"❌ Dependency tracking failed: {str(e)}")
            raise

    async def analyze_change_impact(
        self, 
        service_change: Dict[str, Any]
    ) -> ChangeImpactAnalysis:
        """
        Analyse impact changement service sur écosystème.
        
        Features:
        - Multi-level impact propagation
        - Business impact assessment
        - Recovery time estimation
        - Risk level calculation
        - Mitigation strategy recommendations
        """
        try:
            change_type = ChangeType(service_change.get('change_type', 'deployment'))
            source_service = service_change['service_id']
            
            # Analyse de propagation d'impact
            propagation_analysis = await self._analyze_impact_propagation(
                source_service, change_type
            )
            
            # Évaluation d'impact par service affecté
            impact_assessments = await self._assess_service_impacts(
                propagation_analysis, change_type
            )
            
            # Calcul des métriques globales
            total_affected = len(impact_assessments)
            total_downtime = sum(ia.estimated_downtime_minutes for ia in impact_assessments)
            
            # Détermination du niveau de risque
            risk_level = await self._calculate_risk_level(impact_assessments)
            
            # Génération des actions recommandées
            recommended_actions = await self._generate_mitigation_actions(
                impact_assessments, change_type
            )
            
            # Génération du plan de rollback
            rollback_plan = await self._generate_rollback_plan(
                source_service, change_type, impact_assessments
            )
            
            logger.info(
                f"🔗 Change impact analysis completed: {source_service} -> "
                f"{total_affected} services affected, risk level: {risk_level}"
            )
            
            return ChangeImpactAnalysis(
                change_type=change_type,
                source_service_id=source_service,
                impact_assessments=impact_assessments,
                propagation_path=propagation_analysis['path'],
                total_affected_services=total_affected,
                estimated_total_downtime_minutes=total_downtime,
                risk_level=risk_level,
                recommended_actions=recommended_actions,
                rollback_plan=rollback_plan
            )
            
        except Exception as e:
            logger.error(f"❌ Change impact analysis failed: {str(e)}")
            raise

    async def add_service_dependency(
        self, 
        dependency: ServiceDependency
    ) -> bool:
        """Ajout d'une dépendance de service"""
        try:
            # Validation de la dépendance
            if not await self._validate_dependency(dependency):
                return False
                
            # Ajout au graphe
            self.dependency_graph.add_edge(
                dependency.source_service_id,
                dependency.target_service_id,
                dependency_type=dependency.dependency_type.value,
                strength=dependency.dependency_strength,
                is_critical=dependency.is_critical,
                metadata=dependency.metadata
            )
            
            # Ajout à la liste des dépendances
            self.service_dependencies[dependency.source_service_id].append(dependency)
            
            # Vérification des dépendances circulaires
            if await self._would_create_circular_dependency(dependency):
                logger.warning(
                    f"⚠️ Dependency creates circular reference: "
                    f"{dependency.source_service_id} -> {dependency.target_service_id}"
                )
            
            logger.info(
                f"🔗 Added service dependency: {dependency.source_service_id} -> "
                f"{dependency.target_service_id} ({dependency.dependency_type.value})"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add service dependency: {str(e)}")
            return False

    async def remove_service_dependency(
        self, 
        source_service_id: str, 
        target_service_id: str
    ) -> bool:
        """Suppression d'une dépendance de service"""
        try:
            # Suppression du graphe
            if self.dependency_graph.has_edge(source_service_id, target_service_id):
                self.dependency_graph.remove_edge(source_service_id, target_service_id)
                
            # Suppression de la liste
            self.service_dependencies[source_service_id] = [
                dep for dep in self.service_dependencies[source_service_id]
                if dep.target_service_id != target_service_id
            ]
            
            logger.info(
                f"🔗 Removed service dependency: {source_service_id} -> {target_service_id}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove service dependency: {str(e)}")
            return False

    async def get_service_dependencies(
        self, 
        service_id: str, 
        direction: DependencyDirection = DependencyDirection.DOWNSTREAM
    ) -> List[str]:
        """Récupération des dépendances d'un service"""
        if direction == DependencyDirection.DOWNSTREAM:
            # Services qui dépendent de ce service
            return list(self.dependency_graph.successors(service_id))
        elif direction == DependencyDirection.UPSTREAM:
            # Services dont ce service dépend
            return list(self.dependency_graph.predecessors(service_id))
        else:
            # Bidirectionnel
            return list(set(
                list(self.dependency_graph.successors(service_id)) +
                list(self.dependency_graph.predecessors(service_id))
            ))

    async def _build_dependency_graph(
        self, 
        tracking_config: Dict[str, Any]
    ) -> DependencyGraph:
        """Construction du graphe de dépendances"""
        # Collecte de tous les services uniques
        all_services = set()
        all_dependencies = []
        
        for source_service_id, dependencies in self.service_dependencies.items():
            all_services.add(source_service_id)
            for dep in dependencies:
                all_services.add(dep.target_service_id)
                all_dependencies.append(dep)
        
        return DependencyGraph(
            services=all_services,
            dependencies=all_dependencies,
            graph_metadata={
                'total_edges': self.dependency_graph.number_of_edges(),
                'total_nodes': self.dependency_graph.number_of_nodes(),
                'is_dag': nx.is_directed_acyclic_graph(self.dependency_graph),
                'density': nx.density(self.dependency_graph)
            }
        )

    async def _detect_circular_dependencies(self) -> List[List[str]]:
        """Détection des dépendances circulaires"""
        circular_deps = []
        
        try:
            # Recherche de cycles dans le graphe dirigé
            cycles = list(nx.simple_cycles(self.dependency_graph))
            circular_deps = cycles
            
        except Exception as e:
            logger.error(f"❌ Error detecting circular dependencies: {str(e)}")
            
        return circular_deps

    async def _identify_critical_paths(self) -> List[List[str]]:
        """Identification des chemins critiques"""
        critical_paths = []
        
        # Identification des nœuds avec beaucoup de dépendances
        for node in self.dependency_graph.nodes():
            out_degree = self.dependency_graph.out_degree(node)
            in_degree = self.dependency_graph.in_degree(node)
            
            # Un nœud critique a soit beaucoup de dépendants soit beaucoup de dépendances
            if out_degree > 5 or in_degree > 5:
                # Trouver les chemins les plus longs depuis ce nœud
                try:
                    paths = self._find_longest_paths_from_node(node)
                    critical_paths.extend(paths[:3])  # Top 3 paths
                except:
                    pass
                    
        return critical_paths

    def _find_longest_paths_from_node(self, start_node: str, max_length: int = 10) -> List[List[str]]:
        """Recherche des chemins les plus longs depuis un nœud"""
        paths = []
        
        def dfs(current_node, path, visited):
            if len(path) > max_length:
                return
                
            if len(path) > 1:
                paths.append(path.copy())
                
            for neighbor in self.dependency_graph.successors(current_node):
                if neighbor not in visited:
                    path.append(neighbor)
                    visited.add(neighbor)
                    dfs(neighbor, path, visited)
                    path.pop()
                    visited.remove(neighbor)
        
        dfs(start_node, [start_node], {start_node})
        
        # Tri par longueur décroissante
        paths.sort(key=len, reverse=True)
        
        return paths[:5]  # Top 5 plus longs chemins

    async def _find_isolated_services(self) -> List[str]:
        """Recherche des services isolés"""
        isolated = []
        
        for node in self.dependency_graph.nodes():
            in_degree = self.dependency_graph.in_degree(node)
            out_degree = self.dependency_graph.out_degree(node)
            
            # Service isolé = pas de dépendances entrantes ni sortantes
            if in_degree == 0 and out_degree == 0:
                isolated.append(node)
                
        return isolated

    async def _calculate_dependency_health_score(self) -> float:
        """Calcul du score de santé des dépendances"""
        return await self.health_assessor.calculate_health_score(self.dependency_graph)

    async def _generate_dependency_recommendations(
        self, 
        circular_deps: List[List[str]],
        critical_paths: List[List[str]],
        isolated_services: List[str]
    ) -> List[str]:
        """Génération des recommandations de dépendances"""
        recommendations = []
        
        if circular_deps:
            recommendations.append(
                f"Break {len(circular_deps)} circular dependencies to improve system stability"
            )
            recommendations.append(
                "Consider introducing service interfaces or event-driven patterns"
            )
            
        if critical_paths:
            recommendations.append(
                "Optimize critical dependency paths to reduce cascading failures"
            )
            recommendations.append(
                "Implement circuit breakers for services in critical paths"
            )
            
        if isolated_services:
            recommendations.append(
                f"Review {len(isolated_services)} isolated services for potential removal"
            )
            
        # Recommandations générales
        recommendations.extend([
            "Implement health checks for all service dependencies",
            "Add retry logic and fallback mechanisms",
            "Consider async communication patterns to reduce tight coupling",
            "Regular dependency audits to maintain clean architecture"
        ])
        
        return recommendations

    async def _generate_dependency_warnings(
        self, 
        circular_deps: List[List[str]],
        critical_paths: List[List[str]]
    ) -> List[str]:
        """Génération des avertissements de dépendances"""
        warnings = []
        
        if circular_deps:
            for cycle in circular_deps:
                warnings.append(f"Circular dependency detected: {' -> '.join(cycle + [cycle[0]])}")
                
        if len(critical_paths) > 10:
            warnings.append(f"High number of critical paths ({len(critical_paths)}) may indicate tight coupling")
            
        # Détection de services avec trop de dépendances
        for node in self.dependency_graph.nodes():
            out_degree = self.dependency_graph.out_degree(node)
            if out_degree > 10:
                warnings.append(f"Service {node} has {out_degree} outgoing dependencies (consider refactoring)")
                
        return warnings

    async def _analyze_impact_propagation(
        self, 
        source_service: str, 
        change_type: ChangeType
    ) -> Dict[str, Any]:
        """Analyse de propagation d'impact"""
        return await self.change_propagator.analyze_propagation(
            self.dependency_graph, source_service, change_type
        )

    async def _assess_service_impacts(
        self, 
        propagation_analysis: Dict[str, Any],
        change_type: ChangeType
    ) -> List[ImpactAssessment]:
        """Évaluation des impacts par service"""
        return await self.impact_calculator.calculate_impacts(
            propagation_analysis, change_type
        )

    async def _calculate_risk_level(
        self, 
        impact_assessments: List[ImpactAssessment]
    ) -> str:
        """Calcul du niveau de risque"""
        if any(ia.impact_level == ImpactLevel.CRITICAL for ia in impact_assessments):
            return "critical"
        elif any(ia.impact_level == ImpactLevel.HIGH for ia in impact_assessments):
            return "high"
        elif any(ia.impact_level == ImpactLevel.MEDIUM for ia in impact_assessments):
            return "medium"
        else:
            return "low"

    async def _generate_mitigation_actions(
        self, 
        impact_assessments: List[ImpactAssessment],
        change_type: ChangeType
    ) -> List[str]:
        """Génération des actions de mitigation"""
        actions = []
        
        high_impact_services = [
            ia for ia in impact_assessments 
            if ia.impact_level in [ImpactLevel.HIGH, ImpactLevel.CRITICAL]
        ]
        
        if high_impact_services:
            actions.append("Schedule change during low-traffic hours")
            actions.append("Prepare rollback procedures before deployment")
            actions.append("Monitor affected services closely during change")
            
        if change_type == ChangeType.DEPLOYMENT:
            actions.extend([
                "Use blue-green or canary deployment strategies",
                "Perform thorough testing in staging environment",
                "Have support team on standby during deployment"
            ])
            
        return actions

    async def _generate_rollback_plan(
        self, 
        source_service: str,
        change_type: ChangeType,
        impact_assessments: List[ImpactAssessment]
    ) -> Dict[str, Any]:
        """Génération du plan de rollback"""
        return {
            'rollback_strategy': 'automated' if change_type == ChangeType.DEPLOYMENT else 'manual',
            'rollback_steps': [
                f"Stop new traffic to {source_service}",
                "Restore previous version",
                "Verify service functionality",
                "Resume normal traffic routing"
            ],
            'estimated_rollback_time_minutes': 15,
            'rollback_triggers': [
                'Error rate > 5%',
                'Response time > 2x baseline',
                'Any critical service failure'
            ],
            'verification_steps': [
                'Health check passes',
                'Key functionality tests pass',
                'Dependent services stable'
            ]
        }

    async def _validate_dependency(self, dependency: ServiceDependency) -> bool:
        """Validation d'une dépendance"""
        if dependency.source_service_id == dependency.target_service_id:
            logger.error("Self-dependency not allowed")
            return False
            
        if dependency.dependency_strength < 0.0 or dependency.dependency_strength > 1.0:
            logger.error("Dependency strength must be between 0.0 and 1.0")
            return False
            
        return True

    async def _would_create_circular_dependency(self, dependency: ServiceDependency) -> bool:
        """Vérification si une dépendance créerait un cycle"""
        # Ajouter temporairement l'arête et vérifier les cycles
        temp_graph = self.dependency_graph.copy()
        temp_graph.add_edge(dependency.source_service_id, dependency.target_service_id)
        
        try:
            list(nx.simple_cycles(temp_graph))
            return not nx.is_directed_acyclic_graph(temp_graph)
        except:
            return False

    def _cleanup_old_history(self):
        """Nettoyage de l'historique ancien"""
        # Garder seulement les 100 derniers snapshots
        if len(self.dependency_history) > 100:
            self.dependency_history = self.dependency_history[-100:]

class DependencyGraphAnalyzer:
    """Analyseur de graphe de dépendances"""
    
    async def analyze_graph_properties(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyse des propriétés du graphe"""
        return {
            'nodes': graph.number_of_nodes(),
            'edges': graph.number_of_edges(),
            'density': nx.density(graph),
            'is_dag': nx.is_directed_acyclic_graph(graph),
            'strongly_connected_components': len(list(nx.strongly_connected_components(graph))),
            'weakly_connected_components': len(list(nx.weakly_connected_components(graph)))
        }

class ImpactCalculator:
    """Calculateur d'impact"""
    
    async def calculate_impacts(
        self, 
        propagation_analysis: Dict[str, Any],
        change_type: ChangeType
    ) -> List[ImpactAssessment]:
        """Calcul des impacts"""
        impacts = []
        
        affected_services = propagation_analysis.get('affected_services', [])
        
        for service_id in affected_services:
            # Simulation d'évaluation d'impact
            impact_level = self._determine_impact_level(service_id, change_type)
            
            impact = ImpactAssessment(
                affected_service_id=service_id,
                impact_level=impact_level,
                impact_description=f"Service may experience {impact_level.value} impact",
                estimated_downtime_minutes=self._estimate_downtime(impact_level),
                affected_functionality=["core_functionality"],
                mitigation_strategies=["implement_circuit_breaker", "add_fallback"],
                recovery_time_estimate_minutes=self._estimate_recovery_time(impact_level),
                business_impact=f"{impact_level.value.title()} business impact expected",
                confidence_score=0.75
            )
            
            impacts.append(impact)
            
        return impacts
        
    def _determine_impact_level(self, service_id: str, change_type: ChangeType) -> ImpactLevel:
        """Détermination du niveau d'impact"""
        # Logique simplifiée - en réalité basée sur des modèles complexes
        if change_type == ChangeType.SHUTDOWN:
            return ImpactLevel.CRITICAL
        elif change_type == ChangeType.DEPLOYMENT:
            return ImpactLevel.MEDIUM
        else:
            return ImpactLevel.LOW
            
    def _estimate_downtime(self, impact_level: ImpactLevel) -> int:
        """Estimation du temps d'arrêt"""
        downtime_map = {
            ImpactLevel.NONE: 0,
            ImpactLevel.LOW: 2,
            ImpactLevel.MEDIUM: 10,
            ImpactLevel.HIGH: 30,
            ImpactLevel.CRITICAL: 60
        }
        return downtime_map.get(impact_level, 5)
        
    def _estimate_recovery_time(self, impact_level: ImpactLevel) -> int:
        """Estimation du temps de récupération"""
        recovery_map = {
            ImpactLevel.NONE: 0,
            ImpactLevel.LOW: 5,
            ImpactLevel.MEDIUM: 15,
            ImpactLevel.HIGH: 45,
            ImpactLevel.CRITICAL: 120
        }
        return recovery_map.get(impact_level, 10)

class ChangePropagator:
    """Propagateur de changements"""
    
    async def analyze_propagation(
        self, 
        graph: nx.DiGraph, 
        source_service: str, 
        change_type: ChangeType
    ) -> Dict[str, Any]:
        """Analyse de propagation de changement"""
        affected_services = []
        propagation_path = []
        
        # BFS pour trouver tous les services affectés
        queue = deque([source_service])
        visited = {source_service}
        level = 0
        
        while queue and level < 5:  # Limiter à 5 niveaux de propagation
            level_size = len(queue)
            current_level = []
            
            for _ in range(level_size):
                current_service = queue.popleft()
                current_level.append(current_service)
                
                # Ajouter tous les successeurs
                for successor in graph.successors(current_service):
                    if successor not in visited:
                        visited.add(successor)
                        queue.append(successor)
                        affected_services.append(successor)
            
            if current_level:
                propagation_path.append(current_level)
            level += 1
        
        return {
            'affected_services': affected_services,
            'path': propagation_path,
            'total_levels': len(propagation_path),
            'propagation_width': len(affected_services)
        }

class DependencyHealthAssessor:
    """Évaluateur de santé des dépendances"""
    
    async def calculate_health_score(self, graph: nx.DiGraph) -> float:
        """Calcul du score de santé"""
        score = 100.0
        
        # Pénalité pour dépendances circulaires
        try:
            cycles = list(nx.simple_cycles(graph))
            score -= len(cycles) * 15
        except:
            score -= 20  # Pénalité pour problème de détection
        
        # Pénalité pour forte densité (couplage serré)
        density = nx.density(graph)
        if density > 0.5:
            score -= (density - 0.5) * 40
        
        # Pénalité pour services avec trop de dépendances
        for node in graph.nodes():
            out_degree = graph.out_degree(node)
            if out_degree > 10:
                score -= (out_degree - 10) * 2
        
        return max(0.0, min(100.0, score))

# Factory function
def create_service_dependency_tracker(config: Dict[str, Any] = None) -> ServiceDependencyTracker:
    """Factory function pour créer un Service Dependency Tracker"""
    return ServiceDependencyTracker(config)

# Export des classes principales
__all__ = [
    'ServiceDependencyTracker',
    'ServiceDependency',
    'DependencyGraph',
    'ImpactAssessment',
    'ChangeImpactAnalysis',
    'DependencyTrackingResult',
    'DependencyType',
    'DependencyDirection',
    'ImpactLevel',
    'ChangeType',
    'create_service_dependency_tracker'
]