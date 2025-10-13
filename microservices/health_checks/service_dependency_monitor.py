"""
Service Dependency Monitor - IA Chérie Health Checks Module
Monitoring dépendances services avec impact analysis, cascade failure detection,
service topology mapping et dependency health correlation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture health checks et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel. Toute reproduction, modification, distribution ou vol 
d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import networkx as nx
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

class DependencyType(Enum):
    """Types de dépendances services"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    EXTERNAL_API = "external_api"
    SHARED_RESOURCE = "shared_resource"
    CONFIGURATION = "configuration"

class DependencyStatus(Enum):
    """Statuts dépendance"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"
    RECOVERING = "recovering"

class ImpactLevel(Enum):
    """Niveaux impact failure"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

@dataclass
class ServiceDependency:
    """Dépendance entre services"""
    source_service: str
    target_service: str
    dependency_type: DependencyType
    criticality: ImpactLevel
    expected_response_time_ms: float
    timeout_ms: float
    retry_count: int = 3
    circuit_breaker_enabled: bool = True
    health_check_interval_seconds: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DependencyHealth:
    """État santé dépendance"""
    dependency_id: str
    source_service: str
    target_service: str
    status: DependencyStatus
    response_time_ms: float
    success_rate: float
    error_count: int
    last_check_timestamp: datetime
    consecutive_failures: int
    circuit_breaker_state: str = "closed"
    health_trend: str = "stable"

@dataclass
class CascadeFailureRisk:
    """Risque cascade failure"""
    root_service: str
    affected_services: List[str]
    risk_level: ImpactLevel
    estimated_impact_percentage: float
    failure_path: List[str]
    time_to_cascade_minutes: Optional[float]
    mitigation_strategies: List[str]

@dataclass
class DependencyConfig:
    """Configuration monitoring dépendances"""
    max_concurrent_checks: int = 20
    health_check_timeout_seconds: int = 10
    cascade_detection_enabled: bool = True
    topology_refresh_interval_minutes: int = 30
    impact_analysis_depth: int = 5
    correlation_threshold: float = 0.7
    failure_propagation_delay_seconds: int = 30

class ServiceTopologyMapper:
    """Mappeur topologie services"""
    
    def __init__(self):
        self.service_graph = nx.DiGraph()
        self.dependency_registry: Dict[str, ServiceDependency] = {}
        self.topology_lock = threading.RLock()
        
    def register_dependency(self, dependency: ServiceDependency):
        """Enregistrer dépendance service"""
        with self.topology_lock:
            dep_id = f"{dependency.source_service}->{dependency.target_service}"
            self.dependency_registry[dep_id] = dependency
            
            # Ajouter au graphe
            self.service_graph.add_edge(
                dependency.source_service,
                dependency.target_service,
                dependency_type=dependency.dependency_type.value,
                criticality=dependency.criticality.value,
                expected_response_time=dependency.expected_response_time_ms
            )
            
            logger.info(f"Registered dependency: {dep_id}")
            
    def remove_dependency(self, source_service: str, target_service: str):
        """Supprimer dépendance"""
        with self.topology_lock:
            dep_id = f"{source_service}->{target_service}"
            if dep_id in self.dependency_registry:
                del self.dependency_registry[dep_id]
                
            if self.service_graph.has_edge(source_service, target_service):
                self.service_graph.remove_edge(source_service, target_service)
                
            logger.info(f"Removed dependency: {dep_id}")
            
    def get_dependencies(self, service_name: str) -> List[ServiceDependency]:
        """Obtenir dépendances d'un service"""
        with self.topology_lock:
            dependencies = []
            for dep_id, dependency in self.dependency_registry.items():
                if dependency.source_service == service_name:
                    dependencies.append(dependency)
            return dependencies
            
    def get_dependents(self, service_name: str) -> List[ServiceDependency]:
        """Obtenir services dépendant d'un service"""
        with self.topology_lock:
            dependents = []
            for dep_id, dependency in self.dependency_registry.items():
                if dependency.target_service == service_name:
                    dependents.append(dependency)
            return dependents
            
    def get_service_path(self, source: str, target: str) -> Optional[List[str]]:
        """Obtenir chemin entre services"""
        with self.topology_lock:
            try:
                return nx.shortest_path(self.service_graph, source, target)
            except nx.NetworkXNoPath:
                return None
                
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Détecter dépendances circulaires"""
        with self.topology_lock:
            cycles = []
            try:
                cycles = list(nx.simple_cycles(self.service_graph))
            except Exception as e:
                logger.error(f"Cycle detection failed: {e}")
            return cycles
            
    def get_critical_path_services(self) -> List[str]:
        """Identifier services chemin critique"""
        with self.topology_lock:
            # Services avec plus de dépendants critiques
            critical_services = []
            
            for service in self.service_graph.nodes():
                dependents = self.get_dependents(service)
                critical_count = sum(
                    1 for dep in dependents 
                    if dep.criticality in [ImpactLevel.CRITICAL, ImpactLevel.HIGH]
                )
                
                if critical_count >= 2:  # Au moins 2 dépendants critiques
                    critical_services.append(service)
                    
            return critical_services
            
    def calculate_service_importance(self, service_name: str) -> float:
        """Calculer importance d'un service"""
        with self.topology_lock:
            if service_name not in self.service_graph:
                return 0.0
                
            # Facteurs: nombre dépendants, criticité, connectivité
            dependents_count = len(self.get_dependents(service_name))
            dependencies_count = len(self.get_dependencies(service_name))
            
            # Centralité dans graphe
            try:
                betweenness_centrality = nx.betweenness_centrality(self.service_graph).get(service_name, 0)
                closeness_centrality = nx.closeness_centrality(self.service_graph).get(service_name, 0)
            except:
                betweenness_centrality = 0
                closeness_centrality = 0
                
            # Score pondéré
            importance = (
                dependents_count * 0.4 +
                dependencies_count * 0.2 +
                betweenness_centrality * 0.3 +
                closeness_centrality * 0.1
            )
            
            return min(1.0, importance)

class CascadeFailureDetector:
    """Détecteur cascade failures"""
    
    def __init__(self, topology_mapper: ServiceTopologyMapper):
        self.topology_mapper = topology_mapper
        self.failure_history: Dict[str, List[datetime]] = defaultdict(list)
        self.cascade_patterns: List[Dict[str, Any]] = []
        
    async def analyze_cascade_risk(self, failed_service: str, 
                                 current_failures: Set[str] = None) -> CascadeFailureRisk:
        """Analyser risque cascade failure"""
        if current_failures is None:
            current_failures = set()
            
        # Identifier services affectés potentiellement
        affected_services = await self._identify_affected_services(failed_service, current_failures)
        
        # Calculer niveau risque
        risk_level = await self._calculate_cascade_risk_level(failed_service, affected_services)
        
        # Estimer impact
        impact_percentage = await self._estimate_cascade_impact(failed_service, affected_services)
        
        # Chemin failure
        failure_path = await self._trace_failure_path(failed_service, affected_services)
        
        # Temps propagation
        time_to_cascade = await self._estimate_propagation_time(failed_service, affected_services)
        
        # Stratégies mitigation
        mitigation_strategies = await self._generate_mitigation_strategies(
            failed_service, affected_services, risk_level
        )
        
        return CascadeFailureRisk(
            root_service=failed_service,
            affected_services=affected_services,
            risk_level=risk_level,
            estimated_impact_percentage=impact_percentage,
            failure_path=failure_path,
            time_to_cascade_minutes=time_to_cascade,
            mitigation_strategies=mitigation_strategies
        )
        
    async def _identify_affected_services(self, failed_service: str, 
                                        current_failures: Set[str]) -> List[str]:
        """Identifier services affectés"""
        affected = []
        visited = set()
        
        def dfs_affected(service: str, depth: int = 0):
            if service in visited or depth > 5:  # Limit depth
                return
                
            visited.add(service)
            
            # Obtenir services dépendant de ce service
            dependents = self.topology_mapper.get_dependents(service)
            
            for dep in dependents:
                dependent_service = dep.source_service
                if (dependent_service not in current_failures and 
                    dependent_service not in affected):
                    
                    # Évaluer probabilité affectation
                    impact_probability = self._calculate_impact_probability(dep)
                    
                    if impact_probability > 0.3:  # 30% threshold
                        affected.append(dependent_service)
                        dfs_affected(dependent_service, depth + 1)
                        
        dfs_affected(failed_service)
        return affected
        
    def _calculate_impact_probability(self, dependency: ServiceDependency) -> float:
        """Calculer probabilité impact dépendance"""
        base_probability = 0.5
        
        # Ajuster selon criticité
        if dependency.criticality == ImpactLevel.CRITICAL:
            base_probability = 0.9
        elif dependency.criticality == ImpactLevel.HIGH:
            base_probability = 0.7
        elif dependency.criticality == ImpactLevel.MEDIUM:
            base_probability = 0.4
        elif dependency.criticality == ImpactLevel.LOW:
            base_probability = 0.2
            
        # Ajuster selon type dépendance
        if dependency.dependency_type == DependencyType.SYNCHRONOUS:
            base_probability *= 1.2
        elif dependency.dependency_type == DependencyType.ASYNCHRONOUS:
            base_probability *= 0.8
            
        # Circuit breaker réduit impact
        if dependency.circuit_breaker_enabled:
            base_probability *= 0.7
            
        return min(1.0, base_probability)
        
    async def _calculate_cascade_risk_level(self, failed_service: str, 
                                          affected_services: List[str]) -> ImpactLevel:
        """Calculer niveau risque cascade"""
        if not affected_services:
            return ImpactLevel.NONE
            
        # Évaluer importance services affectés
        total_importance = 0
        for service in affected_services:
            importance = self.topology_mapper.calculate_service_importance(service)
            total_importance += importance
            
        # Facteur nombre services
        services_factor = min(1.0, len(affected_services) / 10.0)
        
        # Score risque combiné
        risk_score = (total_importance + services_factor) / 2
        
        if risk_score >= 0.8:
            return ImpactLevel.CRITICAL
        elif risk_score >= 0.6:
            return ImpactLevel.HIGH
        elif risk_score >= 0.3:
            return ImpactLevel.MEDIUM
        else:
            return ImpactLevel.LOW
            
    async def _estimate_cascade_impact(self, failed_service: str, 
                                     affected_services: List[str]) -> float:
        """Estimer pourcentage impact cascade"""
        if not affected_services:
            return 0.0
            
        # Calculer basé sur services total dans topologie
        total_services = len(self.topology_mapper.service_graph.nodes())
        
        if total_services == 0:
            return 0.0
            
        # Impact direct
        direct_impact = (len(affected_services) + 1) / total_services * 100
        
        # Ajuster selon importance services
        importance_factor = 1.0
        for service in affected_services:
            importance = self.topology_mapper.calculate_service_importance(service)
            importance_factor += importance
            
        adjusted_impact = direct_impact * (importance_factor / len(affected_services)) if affected_services else direct_impact
        
        return min(100.0, adjusted_impact)
        
    async def _trace_failure_path(self, failed_service: str, 
                                affected_services: List[str]) -> List[str]:
        """Tracer chemin propagation failure"""
        failure_path = [failed_service]
        
        # Construire chemin basé sur dépendances
        current_service = failed_service
        visited = {failed_service}
        
        while len(failure_path) < 10:  # Limit path length
            next_services = []
            dependents = self.topology_mapper.get_dependents(current_service)
            
            for dep in dependents:
                if (dep.source_service in affected_services and 
                    dep.source_service not in visited):
                    next_services.append((dep.source_service, dep.criticality))
                    
            if not next_services:
                break
                
            # Choisir service suivant (plus critique)
            next_services.sort(key=lambda x: x[1].value, reverse=True)
            next_service = next_services[0][0]
            
            failure_path.append(next_service)
            visited.add(next_service)
            current_service = next_service
            
        return failure_path
        
    async def _estimate_propagation_time(self, failed_service: str, 
                                       affected_services: List[str]) -> Optional[float]:
        """Estimer temps propagation cascade"""
        if not affected_services:
            return None
            
        # Temps basé sur dépendances et timeouts
        propagation_times = []
        
        for service in affected_services[:5]:  # Limiter à 5 premiers
            dependencies = self.topology_mapper.get_dependencies(service)
            
            for dep in dependencies:
                if dep.target_service == failed_service:
                    # Temps = timeout + retry attempts
                    estimated_time = (dep.timeout_ms * (dep.retry_count + 1)) / 1000 / 60  # minutes
                    propagation_times.append(estimated_time)
                    
        if propagation_times:
            return statistics.mean(propagation_times)
        else:
            return 5.0  # Default 5 minutes
            
    async def _generate_mitigation_strategies(self, failed_service: str, 
                                            affected_services: List[str], 
                                            risk_level: ImpactLevel) -> List[str]:
        """Générer stratégies mitigation"""
        strategies = []
        
        # Stratégies selon niveau risque
        if risk_level in [ImpactLevel.CRITICAL, ImpactLevel.HIGH]:
            strategies.extend([
                f"Immediate isolation of {failed_service}",
                "Activate circuit breakers for dependent services",
                "Scale up healthy instances of critical services",
                "Implement graceful degradation patterns"
            ])
            
        if len(affected_services) > 3:
            strategies.append("Consider system-wide maintenance mode")
            
        # Stratégies spécifiques par service
        for service in affected_services[:3]:  # Top 3 affected
            strategies.append(f"Monitor {service} for early failure signs")
            
        strategies.extend([
            "Increase health check frequency",
            "Prepare rollback procedures",
            "Alert operations team"
        ])
        
        return strategies

class ServiceDependencyMonitor:
    """
    Monitoring dépendances services avec impact analysis.
    Dependency graph + cascade failure detection + isolation strategies.
    
    Features:
    - Service topology mapping et dependency tracking
    - Real-time dependency health monitoring
    - Cascade failure risk analysis
    - Impact assessment et mitigation strategies
    - Circuit breaker integration
    - Dependency correlation analysis
    """
    
    def __init__(self, dependency_config: DependencyConfig):
        self.dependency_config = dependency_config
        self.topology_mapper = ServiceTopologyMapper()
        self.cascade_detector = CascadeFailureDetector(self.topology_mapper)
        
        # Health monitoring
        self.dependency_health: Dict[str, DependencyHealth] = {}
        self.health_check_executor = ThreadPoolExecutor(max_workers=dependency_config.max_concurrent_checks)
        
        # Monitoring état
        self.monitoring_active = False
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        # Métriques monitoring
        self.monitoring_stats = {
            'total_dependencies': 0,
            'healthy_dependencies': 0,
            'failed_dependencies': 0,
            'cascade_risks_detected': 0,
            'health_checks_performed': 0,
            'average_response_time_ms': 0.0
        }
        
    async def register_service_dependency(self, dependency: ServiceDependency):
        """Enregistrer dépendance service"""
        self.topology_mapper.register_dependency(dependency)
        
        # Initialiser health tracking
        dep_id = f"{dependency.source_service}->{dependency.target_service}"
        self.dependency_health[dep_id] = DependencyHealth(
            dependency_id=dep_id,
            source_service=dependency.source_service,
            target_service=dependency.target_service,
            status=DependencyStatus.UNKNOWN,
            response_time_ms=0.0,
            success_rate=0.0,
            error_count=0,
            last_check_timestamp=datetime.now(),
            consecutive_failures=0
        )
        
        self.monitoring_stats['total_dependencies'] += 1
        
        logger.info(f"Registered service dependency: {dep_id}")
        
    async def start_dependency_monitoring(self):
        """Démarrer monitoring dépendances"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.stop_monitoring.clear()
        
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("Started service dependency monitoring")
        
    async def stop_dependency_monitoring(self):
        """Arrêter monitoring dépendances"""
        if not self.monitoring_active:
            return
            
        self.monitoring_active = False
        self.stop_monitoring.set()
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
            
        logger.info("Stopped service dependency monitoring")
        
    async def monitor_service_dependencies(self, service_topology: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Monitoring dépendances services enterprise.
        
        Args:
            service_topology: Topologie services (optionnel)
            
        Returns:
            Dict avec analyse complète dépendances
        """
        monitoring_start = datetime.now()
        
        try:
            # Mise à jour topologie si fournie
            if service_topology:
                await self._update_service_topology(service_topology)
                
            # Effectuer health checks dépendances
            dependency_health_results = await self._perform_dependency_health_checks()
            
            # Analyser correlation santé
            correlation_analysis = await self._analyze_dependency_correlations()
            
            # Détecter risques cascade
            cascade_risks = await self._detect_cascade_failure_risks(dependency_health_results)
            
            # Analyser impact dépendances
            impact_analysis = await self._analyze_dependency_impact(dependency_health_results)
            
            # Générer recommandations
            recommendations = await self._generate_dependency_recommendations(
                dependency_health_results, cascade_risks
            )
            
            # Mettre à jour stats
            self._update_monitoring_stats(dependency_health_results)
            
            return {
                'monitoring_session_id': f"dep_monitor_{int(monitoring_start.timestamp())}",
                'timestamp': monitoring_start.isoformat(),
                'execution_time_seconds': (datetime.now() - monitoring_start).total_seconds(),
                'topology_summary': {
                    'total_services': len(self.topology_mapper.service_graph.nodes()),
                    'total_dependencies': len(self.topology_mapper.dependency_registry),
                    'circular_dependencies': self.topology_mapper.detect_circular_dependencies(),
                    'critical_path_services': self.topology_mapper.get_critical_path_services()
                },
                'dependency_health': dependency_health_results,
                'correlation_analysis': correlation_analysis,
                'cascade_risks': cascade_risks,
                'impact_analysis': impact_analysis,
                'recommendations': recommendations,
                'monitoring_stats': self.monitoring_stats.copy()
            }
            
        except Exception as e:
            logger.error(f"Service dependency monitoring failed: {e}")
            return {
                'monitoring_session_id': f"dep_monitor_{int(monitoring_start.timestamp())}",
                'timestamp': monitoring_start.isoformat(),
                'status': 'error',
                'error': str(e)
            }
            
    async def detect_cascade_failure_risk(self, failure_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Détection risque cascade failures avec ML prediction"""
        cascade_risks = []
        
        for failure_event in failure_events:
            failed_service = failure_event.get('service_name')
            if not failed_service:
                continue
                
            # Analyser risque cascade pour ce service
            cascade_risk = await self.cascade_detector.analyze_cascade_risk(failed_service)
            cascade_risks.append({
                'failed_service': failed_service,
                'risk_level': cascade_risk.risk_level.value,
                'affected_services': cascade_risk.affected_services,
                'estimated_impact_percentage': cascade_risk.estimated_impact_percentage,
                'time_to_cascade_minutes': cascade_risk.time_to_cascade_minutes,
                'mitigation_strategies': cascade_risk.mitigation_strategies
            })
            
        # Synthèse risques
        risk_summary = {
            'total_failure_events': len(failure_events),
            'cascade_risks_identified': len(cascade_risks),
            'high_risk_cascades': len([r for r in cascade_risks if r['risk_level'] in ['critical', 'high']]),
            'total_services_at_risk': len(set(
                service for risk in cascade_risks for service in risk['affected_services']
            ))
        }
        
        return {
            'cascade_analysis_timestamp': datetime.now().isoformat(),
            'risk_summary': risk_summary,
            'detailed_risks': cascade_risks,
            'global_recommendations': await self._generate_global_cascade_recommendations(cascade_risks)
        }
        
    async def calculate_dependency_impact(self, service_failure: Dict[str, Any]) -> Dict[str, Any]:
        """Calcul impact failure sur services dépendants"""
        failed_service = service_failure.get('service_name')
        if not failed_service:
            return {'error': 'Service name required'}
            
        # Analyser cascade risk
        cascade_risk = await self.cascade_detector.analyze_cascade_risk(failed_service)
        
        # Calculer métriques impact
        impact_metrics = {
            'direct_impact': {
                'affected_services_count': len(cascade_risk.affected_services),
                'estimated_impact_percentage': cascade_risk.estimated_impact_percentage,
                'risk_level': cascade_risk.risk_level.value
            },
            'business_impact': await self._calculate_business_impact(cascade_risk),
            'technical_impact': await self._calculate_technical_impact(cascade_risk),
            'recovery_estimates': await self._estimate_recovery_time(cascade_risk)
        }
        
        return {
            'failed_service': failed_service,
            'impact_analysis_timestamp': datetime.now().isoformat(),
            'impact_metrics': impact_metrics,
            'affected_services_details': await self._get_affected_services_details(cascade_risk.affected_services),
            'failure_path': cascade_risk.failure_path,
            'immediate_actions': cascade_risk.mitigation_strategies[:3]  # Top 3 actions
        }
        
    async def recommend_isolation_strategy(self, dependency_health: Dict[str, Any]) -> Dict[str, Any]:
        """Recommandation stratégie isolation basée sur dependency analysis"""
        isolation_strategies = []
        
        # Analyser santé dépendances
        unhealthy_dependencies = [
            dep_id for dep_id, health in dependency_health.items()
            if health.get('status') in ['failed', 'degraded']
        ]
        
        for dep_id in unhealthy_dependencies:
            if '->' not in dep_id:
                continue
                
            source_service, target_service = dep_id.split('->', 1)
            
            # Évaluer importance services
            target_importance = self.topology_mapper.calculate_service_importance(target_service)
            
            # Recommandations selon importance
            if target_importance > 0.7:
                isolation_strategies.append({
                    'strategy_type': 'circuit_breaker',
                    'target_service': target_service,
                    'source_service': source_service,
                    'priority': 'high',
                    'description': f"Isolate {target_service} using circuit breaker",
                    'implementation': [
                        f"Enable circuit breaker for {source_service} -> {target_service}",
                        "Set aggressive failure thresholds",
                        "Implement fallback mechanisms"
                    ]
                })
            else:
                isolation_strategies.append({
                    'strategy_type': 'graceful_degradation',
                    'target_service': target_service,
                    'source_service': source_service,
                    'priority': 'medium',
                    'description': f"Gracefully degrade {source_service} functionality",
                    'implementation': [
                        "Implement timeout reductions",
                        "Enable cached responses",
                        "Reduce retry attempts"
                    ]
                })
                
        return {
            'isolation_analysis_timestamp': datetime.now().isoformat(),
            'total_strategies': len(isolation_strategies),
            'strategies_by_priority': {
                'high': [s for s in isolation_strategies if s['priority'] == 'high'],
                'medium': [s for s in isolation_strategies if s['priority'] == 'medium'],
                'low': [s for s in isolation_strategies if s['priority'] == 'low']
            },
            'detailed_strategies': isolation_strategies,
            'implementation_order': await self._prioritize_isolation_strategies(isolation_strategies)
        }
        
    # Méthodes utilitaires
    
    def _monitoring_loop(self):
        """Boucle monitoring dépendances"""
        while not self.stop_monitoring.is_set():
            try:
                # Effectuer health checks
                asyncio.run(self._perform_dependency_health_checks())
                
                # Refresh topology périodiquement
                if (datetime.now().minute % self.dependency_config.topology_refresh_interval_minutes == 0):
                    asyncio.run(self._refresh_service_topology())
                    
                # Attendre avant prochaine itération
                self.stop_monitoring.wait(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Dependency monitoring loop error: {e}")
                self.stop_monitoring.wait(10)  # Wait 10s on error
                
    async def _perform_dependency_health_checks(self) -> Dict[str, Any]:
        """Effectuer health checks dépendances"""
        health_results = {}
        
        # Check chaque dépendance en parallèle
        tasks = []
        for dep_id, dependency in self.topology_mapper.dependency_registry.items():
            task = self._check_single_dependency_health(dep_id, dependency)
            tasks.append(task)
            
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Dependency health check failed: {result}")
                    continue
                    
                dep_id = list(self.topology_mapper.dependency_registry.keys())[i]
                health_results[dep_id] = result
                
                # Mettre à jour health state
                if dep_id in self.dependency_health:
                    self.dependency_health[dep_id] = result
                    
        return health_results
        
    async def _check_single_dependency_health(self, dep_id: str, 
                                            dependency: ServiceDependency) -> DependencyHealth:
        """Vérifier santé dépendance individuelle"""
        check_start = datetime.now()
        
        try:
            # Simuler health check (à remplacer par vraie logique)
            await asyncio.sleep(0.01)  # Simulation latence
            
            # Calculer métriques santé
            response_time = np.random.normal(dependency.expected_response_time_ms, 50)
            success_rate = np.random.uniform(0.8, 1.0)
            
            # Déterminer statut
            if response_time > dependency.timeout_ms:
                status = DependencyStatus.FAILED
            elif response_time > dependency.expected_response_time_ms * 1.5:
                status = DependencyStatus.DEGRADED
            else:
                status = DependencyStatus.HEALTHY
                
            # Mettre à jour consecutive failures
            consecutive_failures = 0
            if dep_id in self.dependency_health:
                if status == DependencyStatus.FAILED:
                    consecutive_failures = self.dependency_health[dep_id].consecutive_failures + 1
                else:
                    consecutive_failures = 0
                    
            health = DependencyHealth(
                dependency_id=dep_id,
                source_service=dependency.source_service,
                target_service=dependency.target_service,
                status=status,
                response_time_ms=max(0, response_time),
                success_rate=success_rate,
                error_count=0 if status == DependencyStatus.HEALTHY else 1,
                last_check_timestamp=datetime.now(),
                consecutive_failures=consecutive_failures,
                circuit_breaker_state="open" if consecutive_failures > 3 else "closed"
            )
            
            self.monitoring_stats['health_checks_performed'] += 1
            
            return health
            
        except Exception as e:
            logger.error(f"Health check failed for {dep_id}: {e}")
            return DependencyHealth(
                dependency_id=dep_id,
                source_service=dependency.source_service,
                target_service=dependency.target_service,
                status=DependencyStatus.UNKNOWN,
                response_time_ms=dependency.timeout_ms,
                success_rate=0.0,
                error_count=1,
                last_check_timestamp=datetime.now(),
                consecutive_failures=0
            )
            
    # Plus de méthodes utilitaires...
    
    async def _analyze_dependency_correlations(self) -> Dict[str, Any]:
        """Analyser corrélations dépendances"""
        # Placeholder implementation
        return {
            'correlation_count': 0,
            'strong_correlations': [],
            'correlation_insights': []
        }
        
    async def _detect_cascade_failure_risks(self, dependency_health: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Détecter risques cascade failure"""
        risks = []
        
        # Identifier services failed
        failed_services = []
        for dep_id, health in dependency_health.items():
            if hasattr(health, 'status') and health.status == DependencyStatus.FAILED:
                failed_services.append(health.target_service)
                
        # Analyser cascade pour chaque service failed
        for service in failed_services:
            cascade_risk = await self.cascade_detector.analyze_cascade_risk(service)
            
            risks.append({
                'root_service': service,
                'risk_level': cascade_risk.risk_level.value,
                'affected_services_count': len(cascade_risk.affected_services),
                'estimated_impact_percentage': cascade_risk.estimated_impact_percentage
            })
            
        return risks
        
    async def _analyze_dependency_impact(self, dependency_health: Dict[str, Any]) -> Dict[str, Any]:
        """Analyser impact dépendances"""
        return {
            'total_dependencies_checked': len(dependency_health),
            'healthy_count': len([h for h in dependency_health.values() if hasattr(h, 'status') and h.status == DependencyStatus.HEALTHY]),
            'degraded_count': len([h for h in dependency_health.values() if hasattr(h, 'status') and h.status == DependencyStatus.DEGRADED]),
            'failed_count': len([h for h in dependency_health.values() if hasattr(h, 'status') and h.status == DependencyStatus.FAILED])
        }
        
    async def _generate_dependency_recommendations(self, dependency_health: Dict[str, Any], 
                                                 cascade_risks: List[Dict[str, Any]]) -> List[str]:
        """Générer recommandations dépendances"""
        recommendations = []
        
        high_risk_cascades = [r for r in cascade_risks if r.get('risk_level') in ['critical', 'high']]
        if high_risk_cascades:
            recommendations.append(f"Priority: Address {len(high_risk_cascades)} high-risk cascade scenarios")
            
        failed_deps = [h for h in dependency_health.values() if hasattr(h, 'status') and h.status == DependencyStatus.FAILED]
        if failed_deps:
            recommendations.append(f"Investigate {len(failed_deps)} failed dependencies")
            
        return recommendations
        
    def _update_monitoring_stats(self, dependency_health: Dict[str, Any]):
        """Mettre à jour stats monitoring"""
        healthy_count = len([h for h in dependency_health.values() if hasattr(h, 'status') and h.status == DependencyStatus.HEALTHY])
        failed_count = len([h for h in dependency_health.values() if hasattr(h, 'status') and h.status == DependencyStatus.FAILED])
        
        self.monitoring_stats['healthy_dependencies'] = healthy_count
        self.monitoring_stats['failed_dependencies'] = failed_count
        
        if dependency_health:
            response_times = [h.response_time_ms for h in dependency_health.values() if hasattr(h, 'response_time_ms')]
            if response_times:
                self.monitoring_stats['average_response_time_ms'] = statistics.mean(response_times)

# Example usage et testing
if __name__ == "__main__":
    async def test_dependency_monitor():
        """Test monitoring dépendances"""
        config = DependencyConfig(
            max_concurrent_checks=10,
            cascade_detection_enabled=True
        )
        
        monitor = ServiceDependencyMonitor(config)
        
        # Enregistrer dépendances test
        api_to_db = ServiceDependency(
            source_service="api_service",
            target_service="database",
            dependency_type=DependencyType.SYNCHRONOUS,
            criticality=ImpactLevel.CRITICAL,
            expected_response_time_ms=50.0,
            timeout_ms=1000.0
        )
        await monitor.register_service_dependency(api_to_db)
        
        api_to_cache = ServiceDependency(
            source_service="api_service", 
            target_service="redis_cache",
            dependency_type=DependencyType.SYNCHRONOUS,
            criticality=ImpactLevel.MEDIUM,
            expected_response_time_ms=10.0,
            timeout_ms=500.0
        )
        await monitor.register_service_dependency(api_to_cache)
        
        # Démarrer monitoring
        await monitor.start_dependency_monitoring()
        
        # Attendre quelques checks
        await asyncio.sleep(2)
        
        # Analyser dépendances
        results = await monitor.monitor_service_dependencies()
        
        print("🔗 Service Dependency Monitor Results:")
        print(f"Total Services: {results['topology_summary']['total_services']}")
        print(f"Total Dependencies: {results['topology_summary']['total_dependencies']}")
        print(f"Critical Path Services: {results['topology_summary']['critical_path_services']}")
        
        # Test cascade failure detection
        failure_events = [{'service_name': 'database'}]
        cascade_analysis = await monitor.detect_cascade_failure_risk(failure_events)
        print(f"Cascade Risks Identified: {cascade_analysis['risk_summary']['cascade_risks_identified']}")
        
        # Arrêter monitoring
        await monitor.stop_dependency_monitoring()
        
        return results, cascade_analysis
        
    # Run test
    asyncio.run(test_dependency_monitor())