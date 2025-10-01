"""
🔗 SERVICE DEPENDENCY ANALYZER - Module Analyseur Dépendances Services IA Chéries
============================================================================

**Expert Team**: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Copyright**: ©2025 IA Chéries Platform - Tous droits réservés

⚠️  PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
====================================================
Ce code constitue la propriété intellectuelle exclusive de Fahed Mlaiel.
- Email: mlaiel@live.de  
- Projet: IA Chéries Platform
- Licence: Propriétaire - Usage commercial interdit sans autorisation
- Protection: Code source confidentiel

🔗 SERVICE DEPENDENCY ANALYZER ENGINE
===================================
Analyseur dépendances services avec impact analysis:
- Dependency mapping & graph topology analysis
- Cascade failure prediction & impact assessment
- Critical path identification & bottleneck detection
- Resilience scoring & recovery planning
- Real-time dependency health monitoring
"""

import asyncio
import logging
import time
import json
import numpy as np
import networkx as nx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from collections import defaultdict, deque
from sklearn.cluster import SpectralClustering
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class DependencyType(Enum):
    """Types de dépendances."""
    SYNCHRONOUS = "synchronous"      # Appel synchrone direct
    ASYNCHRONOUS = "asynchronous"    # Communication async/queue
    DATA = "data"                    # Dépendance données/stockage
    CIRCUIT_BREAKER = "circuit_breaker"  # Protected par circuit breaker
    CACHED = "cached"                # Avec cache/fallback
    OPTIONAL = "optional"            # Dépendance optionnelle

class DependencyStrength(Enum):
    """Force de la dépendance."""
    WEAK = "weak"          # Peut fonctionner sans
    MODERATE = "moderate"   # Dégradation acceptable
    STRONG = "strong"      # Fonctionnalité limitée
    CRITICAL = "critical"  # Service inutilisable sans

class FailureImpact(Enum):
    """Impact d'une panne."""
    MINIMAL = "minimal"      # <5% fonctionnalités affectées
    LOW = "low"             # 5-20% fonctionnalités affectées
    MODERATE = "moderate"    # 20-50% fonctionnalités affectées
    HIGH = "high"           # 50-80% fonctionnalités affectées
    CRITICAL = "critical"   # >80% fonctionnalités affectées

@dataclass
class ServiceDependency:
    """Dépendance entre services."""
    source_service: str
    target_service: str
    dependency_type: DependencyType
    strength: DependencyStrength
    call_frequency: float  # appels/minute
    avg_latency: float     # ms
    error_rate: float      # 0.0 - 1.0
    timeout: int           # ms
    has_fallback: bool = False
    circuit_breaker_enabled: bool = False
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ServiceNode:
    """Nœud service dans graphe dépendances."""
    service_id: str
    service_name: str
    service_type: str
    criticality_score: float  # 0.0 - 1.0
    health_score: float       # 0.0 - 1.0
    avg_response_time: float  # ms
    error_rate: float        # 0.0 - 1.0
    dependencies_out: Set[str] = field(default_factory=set)
    dependencies_in: Set[str] = field(default_factory=set)

@dataclass
class DependencyAnalysis:
    """Résultat analyse dépendances."""
    analysis_timestamp: datetime
    total_services: int
    total_dependencies: int
    critical_path_services: List[str]
    bottleneck_services: List[str]
    single_points_of_failure: List[str]
    dependency_clusters: Dict[str, List[str]]
    resilience_score: float  # 0.0 - 1.0
    recommendations: List[str]

@dataclass
class FailurePrediction:
    """Prédiction d'impact panne."""
    failed_service: str
    cascade_services: List[str]
    impact_level: FailureImpact
    affected_users_estimate: int
    recovery_time_estimate: int  # minutes
    mitigation_strategies: List[str]
    confidence_score: float  # 0.0 - 1.0

@dataclass
class DependencyConfig:
    """Configuration analyseur dépendances."""
    analysis_interval: int = 300  # 5 minutes
    failure_simulation_enabled: bool = True
    impact_threshold: float = 0.1  # Seuil impact significatif
    max_cascade_depth: int = 5
    dependency_timeout: int = 5000  # 5s
    health_check_interval: int = 60  # 1 minute

class ServiceDependencyAnalyzer:
    """Analyseur dépendances services avec impact modeling."""
    
    def __init__(self, redis_client: aioredis.Redis, 
                 dependency_config: DependencyConfig):
        self.redis_client = redis_client
        self.config = dependency_config
        
        # Graphe dépendances
        self.dependency_graph = nx.DiGraph()
        self.service_nodes: Dict[str, ServiceNode] = {}
        self.dependencies: Dict[Tuple[str, str], ServiceDependency] = {}
        
        # ML Components
        self.clustering_model = SpectralClustering(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()
        
        # Cache et historique
        self.analysis_history: deque = deque(maxlen=1000)
        self.failure_simulations: Dict[str, Any] = {}
        self.critical_paths_cache: List[List[str]] = []
        
        # Métriques temps réel
        self.dependency_metrics: Dict[Tuple[str, str], deque] = defaultdict(lambda: deque(maxlen=100))
        self.service_health_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=500))
        
        # Tâches background
        self._running = False
        self._analysis_task: Optional[asyncio.Task] = None
        self._health_monitoring_task: Optional[asyncio.Task] = None
        self._simulation_task: Optional[asyncio.Task] = None
        
        logger.info("🔗 ServiceDependencyAnalyzer initialisé")
    
    async def start(self):
        """Démarre l'analyseur dépendances."""
        if self._running:
            return
        
        self._running = True
        
        # Charger données existantes
        await self._load_dependency_graph()
        
        # Démarrer tâches background
        self._analysis_task = asyncio.create_task(self._dependency_analysis_loop())
        self._health_monitoring_task = asyncio.create_task(self._health_monitoring_loop())
        
        if self.config.failure_simulation_enabled:
            self._simulation_task = asyncio.create_task(self._failure_simulation_loop())
        
        logger.info("✅ ServiceDependencyAnalyzer démarré")
    
    async def stop(self):
        """Arrête l'analyseur dépendances."""
        if not self._running:
            return
        
        self._running = False
        
        # Arrêter tâches
        tasks = [self._analysis_task, self._health_monitoring_task, self._simulation_task]
        
        for task in tasks:
            if task and not task.done():
                task.cancel()
        
        # Attendre fin des tâches
        running_tasks = [t for t in tasks if t and not t.done()]
        if running_tasks:
            await asyncio.gather(*running_tasks, return_exceptions=True)
        
        logger.info("🛑 ServiceDependencyAnalyzer arrêté")
    
    async def register_service_dependency(self, dependency: ServiceDependency):
        """Enregistre une dépendance service."""
        try:
            # Ajouter services au graphe s'ils n'existent pas
            for service_id in [dependency.source_service, dependency.target_service]:
                if service_id not in self.service_nodes:
                    await self._create_service_node(service_id)
            
            # Ajouter dépendance au graphe
            self.dependency_graph.add_edge(
                dependency.source_service,
                dependency.target_service,
                weight=self._calculate_dependency_weight(dependency),
                dependency_type=dependency.dependency_type.value,
                strength=dependency.strength.value
            )
            
            # Stocker dépendance détaillée
            dep_key = (dependency.source_service, dependency.target_service)
            self.dependencies[dep_key] = dependency
            
            # Mettre à jour nœuds services
            source_node = self.service_nodes[dependency.source_service]
            target_node = self.service_nodes[dependency.target_service]
            
            source_node.dependencies_out.add(dependency.target_service)
            target_node.dependencies_in.add(dependency.source_service)
            
            # Persister dépendance
            await self._persist_dependency(dependency)
            
            logger.info(f"✅ Dépendance enregistrée: {dependency.source_service} → {dependency.target_service}")
            
        except Exception as e:
            logger.error(f"Erreur enregistrement dépendance: {e}")
            raise
    
    async def analyze_service_dependencies(self) -> DependencyAnalysis:
        """Analyse complète des dépendances services."""
        try:
            start_time = time.time()
            
            # Mettre à jour métriques services
            await self._update_service_metrics()
            
            # Analyser topologie graphe
            topology_analysis = await self._analyze_graph_topology()
            
            # Identifier chemins critiques
            critical_paths = await self._identify_critical_paths()
            
            # Détecter goulots d'étranglement
            bottlenecks = await self._detect_bottlenecks()
            
            # Identifier points de défaillance unique
            spof = await self._identify_single_points_of_failure()
            
            # Clustering services
            clusters = await self._cluster_services()
            
            # Calculer score résilience
            resilience_score = await self._calculate_resilience_score()
            
            # Générer recommandations
            recommendations = await self._generate_dependency_recommendations(
                critical_paths, bottlenecks, spof, clusters
            )
            
            # Créer résultat analyse
            analysis = DependencyAnalysis(
                analysis_timestamp=datetime.now(),
                total_services=len(self.service_nodes),
                total_dependencies=len(self.dependencies),
                critical_path_services=critical_paths[0] if critical_paths else [],
                bottleneck_services=bottlenecks,
                single_points_of_failure=spof,
                dependency_clusters=clusters,
                resilience_score=resilience_score,
                recommendations=recommendations
            )
            
            # Enregistrer analyse
            self.analysis_history.append(analysis)
            await self._persist_analysis(analysis)
            
            processing_time = time.time() - start_time
            logger.info(f"🔗 Analyse dépendances complétée en {processing_time:.2f}s")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur analyse dépendances: {e}")
            raise
    
    async def predict_failure_impact(self, service_id: str, 
                                   failure_type: str = "complete") -> FailurePrediction:
        """Prédit impact panne d'un service."""
        try:
            if service_id not in self.service_nodes:
                raise ValueError(f"Service {service_id} non trouvé")
            
            # Simuler panne et propagation
            cascade_services = await self._simulate_cascade_failure(service_id, failure_type)
            
            # Évaluer impact
            impact_level = await self._assess_failure_impact(service_id, cascade_services)
            
            # Estimer utilisateurs affectés
            affected_users = await self._estimate_affected_users(cascade_services)
            
            # Estimer temps récupération
            recovery_time = await self._estimate_recovery_time(service_id, cascade_services)
            
            # Générer stratégies mitigation
            mitigation_strategies = await self._generate_mitigation_strategies(
                service_id, cascade_services, impact_level
            )
            
            # Calculer score confiance
            confidence_score = await self._calculate_prediction_confidence(
                service_id, cascade_services
            )
            
            prediction = FailurePrediction(
                failed_service=service_id,
                cascade_services=cascade_services,
                impact_level=impact_level,
                affected_users_estimate=affected_users,
                recovery_time_estimate=recovery_time,
                mitigation_strategies=mitigation_strategies,
                confidence_score=confidence_score
            )
            
            # Enregistrer prédiction
            await self._persist_failure_prediction(prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Erreur prédiction impact panne {service_id}: {e}")
            raise
    
    async def _create_service_node(self, service_id: str):
        """Crée nœud service."""
        try:
            # Récupérer infos service depuis registry
            service_info = await self._get_service_info(service_id)
            
            node = ServiceNode(
                service_id=service_id,
                service_name=service_info.get('service_name', service_id),
                service_type=service_info.get('service_type', 'unknown'),
                criticality_score=service_info.get('criticality_score', 0.5),
                health_score=1.0,
                avg_response_time=0.0,
                error_rate=0.0
            )
            
            self.service_nodes[service_id] = node
            self.dependency_graph.add_node(service_id, **{
                'service_name': node.service_name,
                'service_type': node.service_type,
                'criticality': node.criticality_score
            })
            
        except Exception as e:
            logger.error(f"Erreur création nœud service {service_id}: {e}")
    
    def _calculate_dependency_weight(self, dependency: ServiceDependency) -> float:
        """Calcule poids dépendance pour graphe."""
        # Poids basé sur force, fréquence et fiabilité
        strength_weights = {
            DependencyStrength.WEAK: 0.2,
            DependencyStrength.MODERATE: 0.4,
            DependencyStrength.STRONG: 0.7,
            DependencyStrength.CRITICAL: 1.0
        }
        
        base_weight = strength_weights[dependency.strength]
        
        # Ajuster selon fréquence (normaliser sur échelle log)
        frequency_factor = min(1.0, np.log10(max(1, dependency.call_frequency)) / 3)
        
        # Ajuster selon fiabilité (taux d'erreur inversé)
        reliability_factor = 1.0 - min(0.8, dependency.error_rate)
        
        return base_weight * (0.5 + 0.3 * frequency_factor + 0.2 * reliability_factor)
    
    async def _analyze_graph_topology(self) -> Dict[str, Any]:
        """Analyse topologie du graphe."""
        try:
            if not self.dependency_graph.nodes():
                return {}
            
            analysis = {}
            
            # Métriques de base
            analysis['node_count'] = len(self.dependency_graph.nodes())
            analysis['edge_count'] = len(self.dependency_graph.edges())
            analysis['density'] = nx.density(self.dependency_graph)
            
            # Métriques centralité
            if len(self.dependency_graph.nodes()) > 1:
                # PageRank pour identifier services importants
                pagerank = nx.pagerank(self.dependency_graph)
                analysis['most_central_services'] = sorted(
                    pagerank.items(), key=lambda x: x[1], reverse=True
                )[:5]
                
                # Centralité betweenness pour goulots
                betweenness = nx.betweenness_centrality(self.dependency_graph)
                analysis['potential_bottlenecks'] = sorted(
                    betweenness.items(), key=lambda x: x[1], reverse=True
                )[:5]
            
            # Composants connexes
            if self.dependency_graph.is_directed():
                weakly_connected = list(nx.weakly_connected_components(self.dependency_graph))
                strongly_connected = list(nx.strongly_connected_components(self.dependency_graph))
                
                analysis['weakly_connected_components'] = len(weakly_connected)
                analysis['strongly_connected_components'] = len(strongly_connected)
            
            # Cycles (dépendances circulaires)
            try:
                cycles = list(nx.simple_cycles(self.dependency_graph))
                analysis['circular_dependencies'] = len(cycles)
                analysis['circular_dependency_examples'] = cycles[:3]  # Top 3
            except nx.NetworkXError:
                analysis['circular_dependencies'] = 0
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur analyse topologie: {e}")
            return {}
    
    async def _identify_critical_paths(self) -> List[List[str]]:
        """Identifie chemins critiques dans le graphe."""
        try:
            critical_paths = []
            
            # Identifier services sources (peu de dépendances entrantes)
            sources = [node for node, in_degree in self.dependency_graph.in_degree() 
                      if in_degree <= 1]
            
            # Identifier services terminaux (peu de dépendances sortantes)
            sinks = [node for node, out_degree in self.dependency_graph.out_degree() 
                    if out_degree <= 1]
            
            # Calculer chemins entre sources et terminaux
            for source in sources[:5]:  # Limiter pour performance
                for sink in sinks[:5]:
                    if source != sink:
                        try:
                            # Chemin le plus court pondéré
                            if nx.has_path(self.dependency_graph, source, sink):
                                path = nx.shortest_path(
                                    self.dependency_graph, source, sink, weight='weight'
                                )
                                
                                # Calculer criticité du chemin
                                path_criticality = self._calculate_path_criticality(path)
                                
                                if path_criticality > 0.7:  # Seuil criticité
                                    critical_paths.append(path)
                                    
                        except nx.NetworkXNoPath:
                            continue
            
            # Trier par criticité décroissante
            critical_paths.sort(key=self._calculate_path_criticality, reverse=True)
            
            # Cache pour utilisation future
            self.critical_paths_cache = critical_paths[:10]  # Top 10
            
            return critical_paths
            
        except Exception as e:
            logger.error(f"Erreur identification chemins critiques: {e}")
            return []
    
    def _calculate_path_criticality(self, path: List[str]) -> float:
        """Calcule criticité d'un chemin."""
        if len(path) < 2:
            return 0.0
        
        criticality_scores = []
        
        for i in range(len(path) - 1):
            source, target = path[i], path[i + 1]
            
            # Score nœud source
            source_node = self.service_nodes.get(source)
            if source_node:
                criticality_scores.append(source_node.criticality_score)
            
            # Score dépendance
            dep = self.dependencies.get((source, target))
            if dep:
                dep_score = {
                    DependencyStrength.WEAK: 0.2,
                    DependencyStrength.MODERATE: 0.4,
                    DependencyStrength.STRONG: 0.7,
                    DependencyStrength.CRITICAL: 1.0
                }[dep.strength]
                criticality_scores.append(dep_score)
        
        return np.mean(criticality_scores) if criticality_scores else 0.0
    
    async def _detect_bottlenecks(self) -> List[str]:
        """Détecte goulots d'étranglement."""
        try:
            bottlenecks = []
            
            if len(self.dependency_graph.nodes()) <= 1:
                return bottlenecks
            
            # Centralité betweenness pour flux
            betweenness = nx.betweenness_centrality(self.dependency_graph, weight='weight')
            
            # Services avec haute centralité = potentiels goulots
            high_betweenness = [
                service for service, score in betweenness.items() 
                if score > 0.1  # Seuil arbitraire
            ]
            
            # Analyser métriques performance pour confirmer
            for service_id in high_betweenness:
                service_node = self.service_nodes.get(service_id)
                if service_node:
                    # Critères goulot: haute centralité + performance dégradée
                    if (service_node.avg_response_time > 1000 or  # >1s
                        service_node.error_rate > 0.05):  # >5% erreurs
                        bottlenecks.append(service_id)
            
            return bottlenecks
            
        except Exception as e:
            logger.error(f"Erreur détection goulots d'étranglement: {e}")
            return []
    
    async def _identify_single_points_of_failure(self) -> List[str]:
        """Identifie points de défaillance unique."""
        try:
            spof = []
            
            # Services critiques avec beaucoup de dépendants
            for service_id, node in self.service_nodes.items():
                # Critères SPOF:
                # 1. Beaucoup de services dépendent de lui
                # 2. Pas de redondance/fallback
                # 3. Criticité élevée
                
                dependents_count = len(node.dependencies_in)
                has_redundancy = await self._check_service_redundancy(service_id)
                
                if (dependents_count >= 3 and  # Au moins 3 dépendants
                    not has_redundancy and     # Pas de redondance
                    node.criticality_score > 0.7):  # Haute criticité
                    spof.append(service_id)
            
            # Vérifier avec analyse de connectivité
            for service_id in list(spof):
                # Simuler suppression du service
                temp_graph = self.dependency_graph.copy()
                temp_graph.remove_node(service_id)
                
                # Vérifier si graphe reste connecté
                if temp_graph.nodes():
                    if self.dependency_graph.is_directed():
                        remaining_components = list(nx.weakly_connected_components(temp_graph))
                    else:
                        remaining_components = list(nx.connected_components(temp_graph))
                    
                    # Si fragmentation significative = SPOF confirmé
                    if len(remaining_components) > 1:
                        if service_id not in spof:
                            spof.append(service_id)
            
            return spof
            
        except Exception as e:
            logger.error(f"Erreur identification SPOF: {e}")
            return []
    
    async def _cluster_services(self) -> Dict[str, List[str]]:
        """Groupe services en clusters selon dépendances."""
        try:
            if len(self.service_nodes) < 3:
                return {'cluster_0': list(self.service_nodes.keys())}
            
            # Créer matrice adjacence
            nodes = list(self.service_nodes.keys())
            adjacency_matrix = nx.adjacency_matrix(
                self.dependency_graph, nodelist=nodes, weight='weight'
            ).toarray()
            
            # Ajouter matrice transposée pour bidirectionnalité
            similarity_matrix = adjacency_matrix + adjacency_matrix.T
            
            # Clustering spectral
            n_clusters = min(5, len(nodes) // 2)  # Adapter selon taille
            if n_clusters < 2:
                return {'cluster_0': nodes}
            
            clustering = SpectralClustering(
                n_clusters=n_clusters, 
                affinity='precomputed',
                random_state=42
            )
            
            cluster_labels = clustering.fit_predict(similarity_matrix)
            
            # Organiser résultats
            clusters = defaultdict(list)
            for i, node in enumerate(nodes):
                cluster_id = f"cluster_{cluster_labels[i]}"
                clusters[cluster_id].append(node)
            
            return dict(clusters)
            
        except Exception as e:
            logger.error(f"Erreur clustering services: {e}")
            return {'cluster_0': list(self.service_nodes.keys())}
    
    async def _calculate_resilience_score(self) -> float:
        """Calcule score résilience global."""
        try:
            if not self.service_nodes:
                return 0.0
            
            scores = []
            
            # Score 1: Santé moyenne services
            health_scores = [node.health_score for node in self.service_nodes.values()]
            avg_health = np.mean(health_scores)
            scores.append(avg_health)
            
            # Score 2: Redondance (absence SPOF)
            spof = await self._identify_single_points_of_failure()
            spof_penalty = len(spof) / len(self.service_nodes)
            redundancy_score = max(0.0, 1.0 - spof_penalty)
            scores.append(redundancy_score)
            
            # Score 3: Diversité connexions (éviter goulots)
            if len(self.dependency_graph.edges()) > 0:
                # Entropie distribution degrés
                degrees = [d for n, d in self.dependency_graph.degree()]
                degree_entropy = -sum([p * np.log2(p) for p in np.histogram(degrees, bins=5)[0] / len(degrees) if p > 0])
                diversity_score = min(1.0, degree_entropy / 3.0)  # Normaliser
                scores.append(diversity_score)
            
            # Score 4: Présence fallbacks/circuit breakers
            protected_deps = sum(1 for dep in self.dependencies.values() 
                               if dep.has_fallback or dep.circuit_breaker_enabled)
            if self.dependencies:
                protection_score = protected_deps / len(self.dependencies)
                scores.append(protection_score)
            
            return np.mean(scores)
            
        except Exception as e:
            logger.error(f"Erreur calcul score résilience: {e}")
            return 0.0
    
    async def _simulate_cascade_failure(self, failed_service: str, 
                                      failure_type: str) -> List[str]:
        """Simule cascade de pannes."""
        try:
            cascade_services = []
            failed_services = {failed_service}
            
            # Propagation sur plusieurs niveaux
            for depth in range(self.config.max_cascade_depth):
                new_failures = set()
                
                for failed in failed_services:
                    # Services dépendant du service en panne
                    dependents = self.service_nodes[failed].dependencies_in
                    
                    for dependent in dependents:
                        if dependent not in failed_services:
                            # Probabilité panne selon force dépendance
                            dep = self.dependencies.get((dependent, failed))
                            if dep:
                                failure_prob = self._calculate_cascade_probability(
                                    dep, failure_type
                                )
                                
                                # Simulation probabiliste
                                if np.random.random() < failure_prob:
                                    new_failures.add(dependent)
                                    cascade_services.append(dependent)
                
                if not new_failures:
                    break  # Plus de propagation
                
                failed_services.update(new_failures)
            
            return cascade_services
            
        except Exception as e:
            logger.error(f"Erreur simulation cascade: {e}")
            return []
    
    def _calculate_cascade_probability(self, dependency: ServiceDependency, 
                                     failure_type: str) -> float:
        """Calcule probabilité cascade selon dépendance."""
        base_probabilities = {
            DependencyStrength.WEAK: 0.1,
            DependencyStrength.MODERATE: 0.3,
            DependencyStrength.STRONG: 0.6,
            DependencyStrength.CRITICAL: 0.9
        }
        
        base_prob = base_probabilities[dependency.strength]
        
        # Ajustements selon type panne
        if failure_type == "partial":
            base_prob *= 0.5
        elif failure_type == "degraded":
            base_prob *= 0.3
        
        # Réduction si protections
        if dependency.has_fallback:
            base_prob *= 0.4
        if dependency.circuit_breaker_enabled:
            base_prob *= 0.3
        
        return min(1.0, base_prob)
    
    async def _assess_failure_impact(self, failed_service: str, 
                                   cascade_services: List[str]) -> FailureImpact:
        """Évalue impact d'une panne."""
        try:
            total_services = len(self.service_nodes)
            affected_count = 1 + len(cascade_services)  # Service principal + cascade
            
            # Calculer impact pondéré par criticité
            impact_weight = 0
            for service_id in [failed_service] + cascade_services:
                node = self.service_nodes.get(service_id)
                if node:
                    impact_weight += node.criticality_score
            
            # Normaliser impact
            max_possible_impact = total_services * 1.0  # Si tous services criticité max
            impact_ratio = impact_weight / max_possible_impact if max_possible_impact > 0 else 0
            
            # Mapper à enum impact
            if impact_ratio < 0.05:
                return FailureImpact.MINIMAL
            elif impact_ratio < 0.2:
                return FailureImpact.LOW
            elif impact_ratio < 0.5:
                return FailureImpact.MODERATE
            elif impact_ratio < 0.8:
                return FailureImpact.HIGH
            else:
                return FailureImpact.CRITICAL
                
        except Exception as e:
            logger.error(f"Erreur évaluation impact: {e}")
            return FailureImpact.LOW
    
    # Helper methods (implémentations simplifiées)
    async def _get_service_info(self, service_id: str) -> Dict[str, Any]:
        """Récupère infos service depuis registry."""
        try:
            # Récupérer depuis Redis ou service registry
            service_data = await self.redis_client.get(f"service_info:{service_id}")
            if service_data:
                return json.loads(service_data)
            
            # Valeurs par défaut
            return {
                'service_name': service_id,
                'service_type': 'unknown',
                'criticality_score': 0.5
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération infos service {service_id}: {e}")
            return {'service_name': service_id, 'service_type': 'unknown', 'criticality_score': 0.5}
    
    async def _check_service_redundancy(self, service_id: str) -> bool:
        """Vérifie si service a redondance."""
        # Logique simplifiée - en production, vérifier load balancer, replicas, etc.
        return False
    
    async def _estimate_affected_users(self, cascade_services: List[str]) -> int:
        """Estime utilisateurs affectés."""
        # Logique simplifiée - en production, calculer depuis métriques usage
        return len(cascade_services) * 1000
    
    async def _estimate_recovery_time(self, failed_service: str, 
                                    cascade_services: List[str]) -> int:
        """Estime temps récupération en minutes."""
        # Temps base + cascade
        base_time = 15  # 15 min base
        cascade_time = len(cascade_services) * 5  # 5 min par service cascade
        return base_time + cascade_time
    
    async def _generate_mitigation_strategies(self, failed_service: str,
                                            cascade_services: List[str],
                                            impact_level: FailureImpact) -> List[str]:
        """Génère stratégies mitigation."""
        strategies = []
        
        if impact_level in [FailureImpact.HIGH, FailureImpact.CRITICAL]:
            strategies.append("Activation plan reprise activité d'urgence")
            strategies.append("Communication utilisateurs - maintenance planifiée")
        
        strategies.append(f"Redémarrage service principal: {failed_service}")
        
        for service in cascade_services:
            strategies.append(f"Vérification santé et redémarrage si nécessaire: {service}")
        
        strategies.append("Monitoring renforcé post-incident")
        strategies.append("Analyse post-mortem pour améliorer résilience")
        
        return strategies
    
    async def _calculate_prediction_confidence(self, failed_service: str,
                                             cascade_services: List[str]) -> float:
        """Calcule confiance prédiction."""
        # Score basé sur quantité données historiques et complexité graphe
        return 0.8  # Placeholder
    
    # Tâches background
    async def _dependency_analysis_loop(self):
        """Boucle analyse dépendances."""
        while self._running:
            try:
                await self.analyze_service_dependencies()
                await asyncio.sleep(self.config.analysis_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dependency analysis loop: {e}")
                await asyncio.sleep(60)
    
    async def _health_monitoring_loop(self):
        """Boucle monitoring santé dépendances."""
        while self._running:
            try:
                await self._update_service_metrics()
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur health monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _failure_simulation_loop(self):
        """Boucle simulation pannes."""
        while self._running:
            try:
                # Simulation périodique pour tester résilience
                if self.service_nodes:
                    # Simuler panne service aléatoire
                    random_service = np.random.choice(list(self.service_nodes.keys()))
                    prediction = await self.predict_failure_impact(random_service)
                    
                    # Stocker simulation pour analyse
                    self.failure_simulations[f"sim_{int(time.time())}"] = {
                        'service': random_service,
                        'prediction': prediction,
                        'timestamp': datetime.now().isoformat()
                    }
                
                await asyncio.sleep(3600)  # Simulation toutes les heures
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur failure simulation loop: {e}")
                await asyncio.sleep(1800)
    
    async def _update_service_metrics(self):
        """Met à jour métriques services."""
        try:
            # Mettre à jour métriques depuis sources externes
            for service_id, node in self.service_nodes.items():
                # Récupérer métriques récentes
                metrics = await self._get_service_metrics(service_id)
                
                if metrics:
                    node.health_score = metrics.get('health_score', node.health_score)
                    node.avg_response_time = metrics.get('avg_response_time', node.avg_response_time)
                    node.error_rate = metrics.get('error_rate', node.error_rate)
                    
                    # Historique pour tendances
                    self.service_health_history[service_id].append({
                        'timestamp': time.time(),
                        'health_score': node.health_score,
                        'response_time': node.avg_response_time,
                        'error_rate': node.error_rate
                    })
            
        except Exception as e:
            logger.error(f"Erreur mise à jour métriques services: {e}")
    
    async def _get_service_metrics(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Récupère métriques d'un service."""
        try:
            metrics_data = await self.redis_client.get(f"service_metrics:{service_id}")
            if metrics_data:
                return json.loads(metrics_data)
            return None
            
        except Exception as e:
            logger.error(f"Erreur récupération métriques {service_id}: {e}")
            return None
    
    # Persistance
    async def _persist_dependency(self, dependency: ServiceDependency):
        """Persiste dépendance."""
        try:
            key = f"dependency:{dependency.source_service}:{dependency.target_service}"
            data = {
                'source_service': dependency.source_service,
                'target_service': dependency.target_service,
                'dependency_type': dependency.dependency_type.value,
                'strength': dependency.strength.value,
                'call_frequency': dependency.call_frequency,
                'avg_latency': dependency.avg_latency,
                'error_rate': dependency.error_rate,
                'timeout': dependency.timeout,
                'has_fallback': dependency.has_fallback,
                'circuit_breaker_enabled': dependency.circuit_breaker_enabled,
                'last_updated': dependency.last_updated.isoformat()
            }
            
            await self.redis_client.setex(
                key,
                timedelta(days=30).total_seconds(),
                json.dumps(data)
            )
            
        except Exception as e:
            logger.error(f"Erreur persistance dépendance: {e}")
    
    async def _load_dependency_graph(self):
        """Charge graphe dépendances depuis Redis."""
        try:
            # Charger dépendances
            dependency_keys = await self.redis_client.keys("dependency:*")
            
            for key in dependency_keys:
                data = await self.redis_client.get(key)
                if data:
                    dep_data = json.loads(data)
                    
                    dependency = ServiceDependency(
                        source_service=dep_data['source_service'],
                        target_service=dep_data['target_service'],
                        dependency_type=DependencyType(dep_data['dependency_type']),
                        strength=DependencyStrength(dep_data['strength']),
                        call_frequency=dep_data['call_frequency'],
                        avg_latency=dep_data['avg_latency'],
                        error_rate=dep_data['error_rate'],
                        timeout=dep_data['timeout'],
                        has_fallback=dep_data['has_fallback'],
                        circuit_breaker_enabled=dep_data['circuit_breaker_enabled'],
                        last_updated=datetime.fromisoformat(dep_data['last_updated'])
                    )
                    
                    await self.register_service_dependency(dependency)
            
            logger.info(f"✅ {len(dependency_keys)} dépendances chargées")
            
        except Exception as e:
            logger.error(f"Erreur chargement graphe dépendances: {e}")
    
    async def _persist_analysis(self, analysis: DependencyAnalysis):
        """Persiste analyse dépendances."""
        try:
            key = f"dependency_analysis:{analysis.analysis_timestamp.strftime('%Y%m%d_%H%M%S')}"
            data = {
                'analysis_timestamp': analysis.analysis_timestamp.isoformat(),
                'total_services': analysis.total_services,
                'total_dependencies': analysis.total_dependencies,
                'critical_path_services': analysis.critical_path_services,
                'bottleneck_services': analysis.bottleneck_services,
                'single_points_of_failure': analysis.single_points_of_failure,
                'dependency_clusters': analysis.dependency_clusters,
                'resilience_score': analysis.resilience_score,
                'recommendations': analysis.recommendations
            }
            
            await self.redis_client.setex(
                key,
                timedelta(days=7).total_seconds(),
                json.dumps(data)
            )
            
        except Exception as e:
            logger.error(f"Erreur persistance analyse: {e}")
    
    async def _persist_failure_prediction(self, prediction: FailurePrediction):
        """Persiste prédiction panne."""
        try:
            key = f"failure_prediction:{prediction.failed_service}:{int(time.time())}"
            data = {
                'failed_service': prediction.failed_service,
                'cascade_services': prediction.cascade_services,
                'impact_level': prediction.impact_level.value,
                'affected_users_estimate': prediction.affected_users_estimate,
                'recovery_time_estimate': prediction.recovery_time_estimate,
                'mitigation_strategies': prediction.mitigation_strategies,
                'confidence_score': prediction.confidence_score
            }
            
            await self.redis_client.setex(
                key,
                timedelta(days=1).total_seconds(),
                json.dumps(data)
            )
            
        except Exception as e:
            logger.error(f"Erreur persistance prédiction: {e}")
    
    # Placeholder pour recommandations
    async def _generate_dependency_recommendations(self, critical_paths: List[List[str]],
                                                 bottlenecks: List[str],
                                                 spof: List[str],
                                                 clusters: Dict[str, List[str]]) -> List[str]:
        """Génère recommandations basées sur analyse."""
        recommendations = []
        
        if spof:
            recommendations.append(f"CRITIQUE: Éliminer points de défaillance unique: {', '.join(spof)}")
        
        if bottlenecks:
            recommendations.append(f"Optimiser goulots d'étranglement: {', '.join(bottlenecks)}")
        
        if critical_paths:
            recommendations.append(f"Surveiller chemin critique: {' → '.join(critical_paths[0])}")
        
        recommendations.append("Implémenter circuit breakers sur dépendances critiques")
        recommendations.append("Ajouter monitoring dépendances temps réel")
        
        return recommendations

# Factory pour création instance
async def create_service_dependency_analyzer(redis_client: aioredis.Redis,
                                           dependency_config: DependencyConfig = None) -> ServiceDependencyAnalyzer:
    """Crée instance ServiceDependencyAnalyzer."""
    if not dependency_config:
        dependency_config = DependencyConfig()
    
    analyzer = ServiceDependencyAnalyzer(redis_client, dependency_config)
    await analyzer.start()
    return analyzer

# Export classes principales
__all__ = [
    'ServiceDependencyAnalyzer',
    'ServiceDependency',
    'ServiceNode',
    'DependencyAnalysis',
    'FailurePrediction',
    'DependencyType',
    'DependencyStrength',
    'FailureImpact',
    'DependencyConfig',
    'create_service_dependency_analyzer'
]