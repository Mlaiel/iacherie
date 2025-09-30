"""
🔄 ADAPTIVE ALGORITHM SELECTOR - ENTERPRISE LOAD BALANCING
Sélecteur adaptatif d'algorithmes load balancing intelligent

Implements context-aware algorithm switching + performance monitoring
for optimal load balancing algorithm selection based on real-time conditions.

Key Features:
- Context-aware algorithm switching basé sur request patterns
- Performance monitoring algorithmes avec A/B testing
- Dynamic algorithm selection basée sur load conditions
- Historical performance tracking per algorithm
- Business priority routing rules
- Geographic routing optimization

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture adaptive algorithm selector est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution sans autorisation écrite est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
from collections import defaultdict, deque
import numpy as np

logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    """Algorithmes de load balancing disponibles"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    GEOGRAPHIC = "geographic"
    SESSION_AWARE = "session_aware"
    PRIORITY_QUEUE = "priority_queue"
    INTELLIGENT_ML = "intelligent_ml"

class AlgorithmPerformanceMetric(Enum):
    """Métriques performance algorithmes"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    CONNECTION_DISTRIBUTION = "connection_distribution"
    SUCCESS_RATE = "success_rate"

class ContextCategory(Enum):
    """Catégories de contexte pour sélection algorithme"""
    HIGH_TRAFFIC = "high_traffic"
    LOW_LATENCY_REQUIRED = "low_latency_required"
    SESSION_CRITICAL = "session_critical"
    GEOGRAPHIC_SENSITIVE = "geographic_sensitive"
    PRIORITY_SENSITIVE = "priority_sensitive"
    RESOURCE_CONSTRAINED = "resource_constrained"
    FAULT_TOLERANT = "fault_tolerant"

@dataclass
class AlgorithmPerformanceData:
    """Données performance algorithme"""
    algorithm: LoadBalancingAlgorithm
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    throughput_samples: deque = field(default_factory=lambda: deque(maxlen=1000))
    error_rates: deque = field(default_factory=lambda: deque(maxlen=1000))
    success_count: int = 0
    failure_count: int = 0
    total_requests: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def average_response_time(self) -> float:
        """Temps de réponse moyen"""
        return statistics.mean(self.response_times) if self.response_times else 0.0
    
    @property
    def average_throughput(self) -> float:
        """Throughput moyen"""
        return statistics.mean(self.throughput_samples) if self.throughput_samples else 0.0
    
    @property
    def average_error_rate(self) -> float:
        """Taux d'erreur moyen"""
        return statistics.mean(self.error_rates) if self.error_rates else 0.0
    
    @property
    def success_rate(self) -> float:
        """Taux de succès"""
        if self.total_requests == 0:
            return 0.0
        return self.success_count / self.total_requests

@dataclass
class RequestContext:
    """Contexte requête pour sélection algorithme"""
    request_id: str
    client_ip: str
    request_type: str
    payload_size: int
    priority_level: int
    session_id: Optional[str] = None
    geographic_origin: Optional[str] = None
    user_tier: str = "standard"
    latency_requirement: float = 1.0  # seconds
    resource_constraints: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ServerLoadState:
    """État charge serveurs pour sélection algorithme"""
    total_servers: int
    active_servers: int
    average_cpu_usage: float
    average_memory_usage: float
    total_connections: int
    requests_per_second: float
    error_rate: float
    geographic_distribution: Dict[str, int]
    health_status: Dict[str, str]

@dataclass
class SelectorConfig:
    """Configuration sélecteur adaptatif"""
    performance_window_size: int = 1000
    switching_threshold: float = 0.15  # 15% différence performance
    min_samples_for_switch: int = 50
    algorithm_cooldown_seconds: int = 300  # 5 minutes
    a_b_testing_enabled: bool = True
    a_b_testing_ratio: float = 0.1  # 10% trafic pour tests
    fallback_algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN
    context_weight_factors: Dict[str, float] = field(default_factory=lambda: {
        "response_time": 0.4,
        "throughput": 0.3,
        "error_rate": 0.2,
        "resource_usage": 0.1
    })

class RequestContextAnalyzer:
    """Analyseur contexte requêtes pour sélection optimale algorithme"""
    
    def __init__(self):
        self.context_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.context_algorithm_mapping: Dict[str, LoadBalancingAlgorithm] = {}
        
    def analyze_request_context(self, request_context: RequestContext, current_load: ServerLoadState) -> List[ContextCategory]:
        """Analyse contexte requête et retourne catégories applicables"""
        categories = []
        
        try:
            # Analyse trafic élevé
            if current_load.requests_per_second > 1000:
                categories.append(ContextCategory.HIGH_TRAFFIC)
            
            # Analyse exigences latence
            if request_context.latency_requirement < 0.1:  # < 100ms
                categories.append(ContextCategory.LOW_LATENCY_REQUIRED)
            
            # Analyse session critique
            if request_context.session_id and request_context.user_tier in ["premium", "enterprise"]:
                categories.append(ContextCategory.SESSION_CRITICAL)
            
            # Analyse sensibilité géographique
            if request_context.geographic_origin and len(current_load.geographic_distribution) > 1:
                categories.append(ContextCategory.GEOGRAPHIC_SENSITIVE)
            
            # Analyse sensibilité priorité
            if request_context.priority_level > 7:
                categories.append(ContextCategory.PRIORITY_SENSITIVE)
            
            # Analyse contraintes ressources
            if current_load.average_cpu_usage > 80 or current_load.average_memory_usage > 80:
                categories.append(ContextCategory.RESOURCE_CONSTRAINED)
            
            # Analyse tolérance aux pannes
            if current_load.error_rate > 0.05 or current_load.active_servers < current_load.total_servers * 0.8:
                categories.append(ContextCategory.FAULT_TOLERANT)
            
            # Stockage pattern pour apprentissage
            pattern_key = self._generate_pattern_key(categories)
            self.context_patterns[pattern_key].append({
                "request_context": request_context,
                "load_state": current_load,
                "categories": categories,
                "timestamp": datetime.now()
            })
            
            # Limite historique patterns
            if len(self.context_patterns[pattern_key]) > 100:
                self.context_patterns[pattern_key] = self.context_patterns[pattern_key][-80:]
            
            logger.debug(f"🔍 Contexte analysé: {len(categories)} catégories identifiées")
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse contexte requête: {e}")
            categories = [ContextCategory.HIGH_TRAFFIC]  # Fallback
            
        return categories
    
    def _generate_pattern_key(self, categories: List[ContextCategory]) -> str:
        """Génération clé pattern pour stockage"""
        category_names = sorted([cat.value for cat in categories])
        return "_".join(category_names) if category_names else "default"

class AlgorithmPerformanceTracker:
    """Tracker performance algorithmes load balancing"""
    
    def __init__(self, config: SelectorConfig):
        self.config = config
        self.performance_data: Dict[LoadBalancingAlgorithm, AlgorithmPerformanceData] = {}
        self.context_performance: Dict[str, Dict[LoadBalancingAlgorithm, AlgorithmPerformanceData]] = defaultdict(dict)
        
        # Initialisation données performance
        for algorithm in LoadBalancingAlgorithm:
            self.performance_data[algorithm] = AlgorithmPerformanceData(algorithm=algorithm)
    
    def record_algorithm_performance(
        self, 
        algorithm: LoadBalancingAlgorithm,
        response_time: float,
        throughput: float,
        error_occurred: bool,
        context_categories: Optional[List[ContextCategory]] = None
    ):
        """Enregistrement performance algorithme"""
        try:
            # Mise à jour données globales
            perf_data = self.performance_data[algorithm]
            perf_data.response_times.append(response_time)
            perf_data.throughput_samples.append(throughput)
            perf_data.error_rates.append(1.0 if error_occurred else 0.0)
            perf_data.total_requests += 1
            
            if error_occurred:
                perf_data.failure_count += 1
            else:
                perf_data.success_count += 1
            
            perf_data.last_updated = datetime.now()
            
            # Mise à jour données contextuelles
            if context_categories:
                context_key = "_".join(sorted([cat.value for cat in context_categories]))
                if algorithm not in self.context_performance[context_key]:
                    self.context_performance[context_key][algorithm] = AlgorithmPerformanceData(algorithm=algorithm)
                
                context_perf = self.context_performance[context_key][algorithm]
                context_perf.response_times.append(response_time)
                context_perf.throughput_samples.append(throughput)
                context_perf.error_rates.append(1.0 if error_occurred else 0.0)
                context_perf.total_requests += 1
                
                if error_occurred:
                    context_perf.failure_count += 1
                else:
                    context_perf.success_count += 1
                
                context_perf.last_updated = datetime.now()
            
            logger.debug(f"📊 Performance enregistrée pour {algorithm.value}")
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement performance: {e}")
    
    def get_algorithm_performance_score(
        self, 
        algorithm: LoadBalancingAlgorithm,
        context_categories: Optional[List[ContextCategory]] = None
    ) -> float:
        """Calcul score performance algorithme"""
        try:
            # Sélection données performance appropriées
            if context_categories:
                context_key = "_".join(sorted([cat.value for cat in context_categories]))
                if context_key in self.context_performance and algorithm in self.context_performance[context_key]:
                    perf_data = self.context_performance[context_key][algorithm]
                else:
                    perf_data = self.performance_data[algorithm]
            else:
                perf_data = self.performance_data[algorithm]
            
            # Vérification données suffisantes
            if perf_data.total_requests < 10:
                return 0.5  # Score neutre pour données insuffisantes
            
            # Calcul score composite
            response_time_score = max(0.0, 1.0 - (perf_data.average_response_time / 2.0))  # Normalisation à 2s max
            throughput_score = min(1.0, perf_data.average_throughput / 1000.0)  # Normalisation à 1000 RPS
            error_rate_score = max(0.0, 1.0 - (perf_data.average_error_rate * 10.0))  # Pénalisation erreurs
            success_rate_score = perf_data.success_rate
            
            # Score pondéré
            composite_score = (
                response_time_score * self.config.context_weight_factors.get("response_time", 0.4) +
                throughput_score * self.config.context_weight_factors.get("throughput", 0.3) +
                error_rate_score * self.config.context_weight_factors.get("error_rate", 0.2) +
                success_rate_score * 0.1
            )
            
            return max(0.0, min(1.0, composite_score))
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul score performance: {e}")
            return 0.5
    
    def get_best_performing_algorithms(
        self, 
        context_categories: Optional[List[ContextCategory]] = None,
        top_n: int = 3
    ) -> List[Tuple[LoadBalancingAlgorithm, float]]:
        """Obtention meilleurs algorithmes par performance"""
        algorithm_scores = []
        
        for algorithm in LoadBalancingAlgorithm:
            score = self.get_algorithm_performance_score(algorithm, context_categories)
            algorithm_scores.append((algorithm, score))
        
        # Tri par score décroissant
        algorithm_scores.sort(key=lambda x: x[1], reverse=True)
        
        return algorithm_scores[:top_n]

class AlgorithmSwitchingEngine:
    """Moteur switching algorithmes intelligents"""
    
    def __init__(self, config: SelectorConfig):
        self.config = config
        self.current_algorithm: LoadBalancingAlgorithm = config.fallback_algorithm
        self.last_switch_time: Dict[LoadBalancingAlgorithm, datetime] = {}
        self.switch_history: List[Dict[str, Any]] = []
        self.a_b_testing_active: bool = False
        self.a_b_test_algorithm: Optional[LoadBalancingAlgorithm] = None
        
    def should_switch_algorithm(
        self, 
        current_algorithm: LoadBalancingAlgorithm,
        candidate_algorithm: LoadBalancingAlgorithm,
        current_score: float,
        candidate_score: float
    ) -> bool:
        """Détermine si switch algorithme est recommandé"""
        try:
            # Vérification cooldown
            if candidate_algorithm in self.last_switch_time:
                cooldown_end = self.last_switch_time[candidate_algorithm] + timedelta(
                    seconds=self.config.algorithm_cooldown_seconds
                )
                if datetime.now() < cooldown_end:
                    logger.debug(f"⏰ Algorithme {candidate_algorithm.value} en cooldown")
                    return False
            
            # Vérification amélioration performance significative
            improvement = candidate_score - current_score
            if improvement < self.config.switching_threshold:
                logger.debug(f"📊 Amélioration insuffisante: {improvement:.3f} < {self.config.switching_threshold}")
                return False
            
            # Vérification stabilité candidat
            if candidate_score < 0.3:  # Score minimum pour switch
                logger.debug(f"📉 Score candidat trop faible: {candidate_score:.3f}")
                return False
            
            logger.info(f"✅ Switch algorithme recommandé: {current_algorithm.value} → {candidate_algorithm.value} "
                       f"(amélioration: {improvement:.3f})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur évaluation switch algorithme: {e}")
            return False
    
    def execute_algorithm_switch(
        self, 
        new_algorithm: LoadBalancingAlgorithm,
        reason: str,
        performance_improvement: Optional[float] = None
    ) -> bool:
        """Exécution switch algorithme"""
        try:
            old_algorithm = self.current_algorithm
            self.current_algorithm = new_algorithm
            self.last_switch_time[new_algorithm] = datetime.now()
            
            # Enregistrement historique
            switch_record = {
                "timestamp": datetime.now(),
                "old_algorithm": old_algorithm.value,
                "new_algorithm": new_algorithm.value,
                "reason": reason,
                "performance_improvement": performance_improvement
            }
            
            self.switch_history.append(switch_record)
            
            # Limitation historique
            if len(self.switch_history) > 100:
                self.switch_history = self.switch_history[-80:]
            
            logger.info(f"🔄 Switch algorithme exécuté: {old_algorithm.value} → {new_algorithm.value} "
                       f"(raison: {reason})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution switch algorithme: {e}")
            return False
    
    def start_a_b_testing(self, test_algorithm: LoadBalancingAlgorithm) -> bool:
        """Démarrage A/B testing algorithme"""
        if not self.config.a_b_testing_enabled:
            return False
        
        try:
            self.a_b_testing_active = True
            self.a_b_test_algorithm = test_algorithm
            
            logger.info(f"🧪 A/B testing démarré: {self.current_algorithm.value} vs {test_algorithm.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage A/B testing: {e}")
            return False
    
    def should_use_a_b_test_algorithm(self) -> bool:
        """Détermine si utiliser algorithme A/B test"""
        if not self.a_b_testing_active or not self.a_b_test_algorithm:
            return False
        
        # Utilisation ratio A/B testing
        import random
        return random.random() < self.config.a_b_testing_ratio

class AdaptiveAlgorithmSelector:
    """
    🔄 SÉLECTEUR ADAPTATIF ALGORITHMES LOAD BALANCING ENTERPRISE
    
    Sélecteur adaptatif d'algorithmes load balancing intelligent.
    Context-aware algorithm switching + performance monitoring.
    """
    
    def __init__(self, selector_config: Optional[SelectorConfig] = None):
        self.selector_config = selector_config or SelectorConfig()
        self.context_analyzer = RequestContextAnalyzer()
        self.performance_tracker = AlgorithmPerformanceTracker(self.selector_config)
        self.switching_engine = AlgorithmSwitchingEngine(self.selector_config)
        
        # Règles sélection contextuelles
        self.context_algorithm_rules = self._initialize_context_rules()
        
        # Métriques sélecteur
        self.total_selections = 0
        self.successful_selections = 0
        self.algorithm_switches = 0
        
        logger.info("🔄 Adaptive Algorithm Selector initialisé avec succès")
    
    def _initialize_context_rules(self) -> Dict[ContextCategory, List[LoadBalancingAlgorithm]]:
        """Initialisation règles sélection contextuelles"""
        return {
            ContextCategory.HIGH_TRAFFIC: [
                LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
                LoadBalancingAlgorithm.LEAST_CONNECTIONS,
                LoadBalancingAlgorithm.INTELLIGENT_ML
            ],
            ContextCategory.LOW_LATENCY_REQUIRED: [
                LoadBalancingAlgorithm.LEAST_RESPONSE_TIME,
                LoadBalancingAlgorithm.INTELLIGENT_ML,
                LoadBalancingAlgorithm.GEOGRAPHIC
            ],
            ContextCategory.SESSION_CRITICAL: [
                LoadBalancingAlgorithm.SESSION_AWARE,
                LoadBalancingAlgorithm.IP_HASH,
                LoadBalancingAlgorithm.INTELLIGENT_ML
            ],
            ContextCategory.GEOGRAPHIC_SENSITIVE: [
                LoadBalancingAlgorithm.GEOGRAPHIC,
                LoadBalancingAlgorithm.INTELLIGENT_ML,
                LoadBalancingAlgorithm.LEAST_RESPONSE_TIME
            ],
            ContextCategory.PRIORITY_SENSITIVE: [
                LoadBalancingAlgorithm.PRIORITY_QUEUE,
                LoadBalancingAlgorithm.INTELLIGENT_ML,
                LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN
            ],
            ContextCategory.RESOURCE_CONSTRAINED: [
                LoadBalancingAlgorithm.ROUND_ROBIN,
                LoadBalancingAlgorithm.RANDOM,
                LoadBalancingAlgorithm.LEAST_CONNECTIONS
            ],
            ContextCategory.FAULT_TOLERANT: [
                LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
                LoadBalancingAlgorithm.LEAST_CONNECTIONS,
                LoadBalancingAlgorithm.INTELLIGENT_ML
            ]
        }

    async def select_optimal_algorithm(
        self, 
        request_context: RequestContext, 
        current_load: ServerLoadState
    ) -> LoadBalancingAlgorithm:
        """
        🎯 SÉLECTION ALGORITHME OPTIMAL BASÉ SUR CONTEXT ET PERFORMANCE
        
        Sélection algorithme optimal basé sur context et performance historique.
        """
        start_time = time.time()
        
        try:
            logger.debug(f"🎯 Sélection algorithme pour requête {request_context.request_id}")
            
            # Analyse contexte requête
            context_categories = self.context_analyzer.analyze_request_context(request_context, current_load)
            
            # A/B testing check
            if self.switching_engine.should_use_a_b_test_algorithm():
                selected_algorithm = self.switching_engine.a_b_test_algorithm
                logger.debug(f"🧪 Utilisation algorithme A/B test: {selected_algorithm.value}")
            else:
                # Sélection basée sur contexte et performance
                selected_algorithm = await self._select_by_context_and_performance(
                    context_categories, current_load
                )
            
            # Mise à jour métriques
            self.total_selections += 1
            selection_time = time.time() - start_time
            
            logger.info(f"✅ Algorithme sélectionné: {selected_algorithm.value} "
                       f"(contexte: {len(context_categories)} catégories, "
                       f"temps: {selection_time*1000:.1f}ms)")
            
            return selected_algorithm
            
        except Exception as e:
            logger.error(f"❌ Erreur sélection algorithme optimal: {e}")
            return self.selector_config.fallback_algorithm

    async def monitor_algorithm_performance(self, algorithm: LoadBalancingAlgorithm, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        📊 MONITORING PERFORMANCE ALGORITHMES AVEC A/B TESTING
        
        Monitoring performance algorithmes avec A/B testing automatique.
        """
        logger.debug(f"📊 Monitoring performance algorithme: {algorithm.value}")
        
        monitoring_result = {
            "algorithm": algorithm.value,
            "performance_recorded": False,
            "switch_triggered": False,
            "a_b_test_started": False,
            "performance_score": 0.0
        }
        
        try:
            # Extraction métriques
            response_time = metrics.get("response_time", 0.0)
            throughput = metrics.get("throughput", 0.0)
            error_occurred = metrics.get("error_occurred", False)
            context_categories = metrics.get("context_categories", [])
            
            # Enregistrement performance
            self.performance_tracker.record_algorithm_performance(
                algorithm, response_time, throughput, error_occurred, context_categories
            )
            monitoring_result["performance_recorded"] = True
            
            # Calcul score performance actuel
            current_score = self.performance_tracker.get_algorithm_performance_score(
                algorithm, context_categories
            )
            monitoring_result["performance_score"] = current_score
            
            # Évaluation switch potentiel
            await self._evaluate_algorithm_switch(algorithm, context_categories, monitoring_result)
            
            # Démarrage A/B testing si performance dégradée
            if current_score < 0.6 and not self.switching_engine.a_b_testing_active:
                best_algorithms = self.performance_tracker.get_best_performing_algorithms(
                    context_categories, top_n=1
                )
                
                if best_algorithms and best_algorithms[0][0] != algorithm:
                    test_algorithm = best_algorithms[0][0]
                    if self.switching_engine.start_a_b_testing(test_algorithm):
                        monitoring_result["a_b_test_started"] = True
            
            logger.debug(f"📊 Performance monitoring terminé: score={current_score:.3f}")
            
        except Exception as e:
            logger.error(f"❌ Erreur monitoring performance algorithme: {e}")
            
        return monitoring_result

    async def trigger_algorithm_switch(self, performance_degradation: Dict[str, Any]) -> bool:
        """
        🔄 DÉCLENCHEMENT SWITCH ALGORITHME EN CAS DÉGRADATION
        
        Déclenchement switch algorithme en cas dégradation performance.
        """
        logger.info("🔄 Évaluation déclenchement switch algorithme")
        
        try:
            current_algorithm = self.switching_engine.current_algorithm
            degradation_score = performance_degradation.get("degradation_score", 0.0)
            context_categories = performance_degradation.get("context_categories", [])
            
            # Vérification seuil dégradation
            if degradation_score < 0.3:  # Dégradation significative
                logger.warning(f"⚠️ Dégradation performance détectée: {degradation_score:.3f}")
                
                # Recherche meilleur algorithme alternatif
                best_algorithms = self.performance_tracker.get_best_performing_algorithms(
                    context_categories, top_n=3
                )
                
                for candidate_algorithm, candidate_score in best_algorithms:
                    if candidate_algorithm != current_algorithm:
                        current_score = self.performance_tracker.get_algorithm_performance_score(
                            current_algorithm, context_categories
                        )
                        
                        if self.switching_engine.should_switch_algorithm(
                            current_algorithm, candidate_algorithm, current_score, candidate_score
                        ):
                            # Exécution switch
                            improvement = candidate_score - current_score
                            switch_success = self.switching_engine.execute_algorithm_switch(
                                candidate_algorithm,
                                f"Dégradation performance détectée (score: {degradation_score:.3f})",
                                improvement
                            )
                            
                            if switch_success:
                                self.algorithm_switches += 1
                                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur déclenchement switch algorithme: {e}")
            return False

    async def learn_context_patterns(self, context_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        📚 APPRENTISSAGE PATTERNS CONTEXT POUR SÉLECTION OPTIMALE
        
        Apprentissage patterns context pour améliorer sélection future.
        """
        logger.info("📚 Apprentissage patterns contexte")
        
        learning_result = {
            "patterns_learned": 0,
            "rules_updated": 0,
            "performance_improvements": [],
            "learning_summary": {}
        }
        
        try:
            # Analyse historique contextes
            context_samples = context_history.get("samples", [])
            if not context_samples:
                logger.warning("Aucun échantillon contexte fourni pour apprentissage")
                return learning_result
            
            # Analyse patterns performance par contexte
            context_performance_map = {}
            
            for sample in context_samples[-1000:]:  # Derniers 1000 échantillons
                context_key = sample.get("context_key", "default")
                algorithm_used = sample.get("algorithm", "unknown")
                performance_score = sample.get("performance_score", 0.0)
                
                if context_key not in context_performance_map:
                    context_performance_map[context_key] = {}
                
                if algorithm_used not in context_performance_map[context_key]:
                    context_performance_map[context_key][algorithm_used] = []
                
                context_performance_map[context_key][algorithm_used].append(performance_score)
            
            # Mise à jour règles contextuelles
            rules_updated = 0
            for context_key, algorithm_performances in context_performance_map.items():
                if len(algorithm_performances) > 1:
                    # Identification meilleur algorithme pour ce contexte
                    best_algorithm = None
                    best_avg_score = 0.0
                    
                    for algorithm, scores in algorithm_performances.items():
                        if len(scores) >= 5:  # Minimum échantillons
                            avg_score = statistics.mean(scores)
                            if avg_score > best_avg_score:
                                best_avg_score = avg_score
                                best_algorithm = algorithm
                    
                    if best_algorithm and best_avg_score > 0.7:
                        # Mise à jour contexte analyzer
                        self.context_analyzer.context_algorithm_mapping[context_key] = best_algorithm
                        rules_updated += 1
                        
                        learning_result["performance_improvements"].append({
                            "context": context_key,
                            "best_algorithm": best_algorithm,
                            "performance_score": best_avg_score
                        })
            
            learning_result["patterns_learned"] = len(context_performance_map)
            learning_result["rules_updated"] = rules_updated
            learning_result["learning_summary"] = {
                "total_contexts_analyzed": len(context_performance_map),
                "contexts_with_multiple_algorithms": sum(1 for v in context_performance_map.values() if len(v) > 1),
                "average_samples_per_context": statistics.mean([
                    sum(len(scores) for scores in alg_perf.values())
                    for alg_perf in context_performance_map.values()
                ]) if context_performance_map else 0
            }
            
            logger.info(f"✅ Apprentissage patterns terminé: "
                       f"{learning_result['patterns_learned']} patterns, "
                       f"{rules_updated} règles mises à jour")
            
        except Exception as e:
            logger.error(f"❌ Erreur apprentissage patterns contexte: {e}")
            
        return learning_result

    # Méthodes utilitaires privées
    
    async def _select_by_context_and_performance(
        self, 
        context_categories: List[ContextCategory], 
        current_load: ServerLoadState
    ) -> LoadBalancingAlgorithm:
        """Sélection algorithme basée sur contexte et performance"""
        try:
            # Collecte algorithmes candidats basés sur contexte
            candidate_algorithms = set()
            
            for category in context_categories:
                if category in self.context_algorithm_rules:
                    candidate_algorithms.update(self.context_algorithm_rules[category])
            
            # Fallback si pas de candidats contextuels
            if not candidate_algorithms:
                candidate_algorithms = {
                    LoadBalancingAlgorithm.ROUND_ROBIN,
                    LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
                    LoadBalancingAlgorithm.LEAST_CONNECTIONS
                }
            
            # Sélection basée sur performance historique
            best_algorithm = self.selector_config.fallback_algorithm
            best_score = 0.0
            
            for algorithm in candidate_algorithms:
                score = self.performance_tracker.get_algorithm_performance_score(
                    algorithm, context_categories
                )
                
                if score > best_score:
                    best_score = score
                    best_algorithm = algorithm
            
            return best_algorithm
            
        except Exception as e:
            logger.error(f"❌ Erreur sélection contexte/performance: {e}")
            return self.selector_config.fallback_algorithm
    
    async def _evaluate_algorithm_switch(
        self, 
        current_algorithm: LoadBalancingAlgorithm, 
        context_categories: List[ContextCategory],
        monitoring_result: Dict[str, Any]
    ):
        """Évaluation switch algorithme potentiel"""
        try:
            current_score = monitoring_result.get("performance_score", 0.0)
            
            # Recherche alternatives meilleures
            best_algorithms = self.performance_tracker.get_best_performing_algorithms(
                context_categories, top_n=3
            )
            
            for candidate_algorithm, candidate_score in best_algorithms:
                if candidate_algorithm != current_algorithm:
                    if self.switching_engine.should_switch_algorithm(
                        current_algorithm, candidate_algorithm, current_score, candidate_score
                    ):
                        improvement = candidate_score - current_score
                        switch_success = self.switching_engine.execute_algorithm_switch(
                            candidate_algorithm,
                            f"Amélioration performance détectée (+{improvement:.3f})",
                            improvement
                        )
                        
                        if switch_success:
                            monitoring_result["switch_triggered"] = True
                            self.algorithm_switches += 1
                            break
            
        except Exception as e:
            logger.error(f"❌ Erreur évaluation switch algorithme: {e}")

# Point d'entrée pour tests et démonstration
async def main():
    """Démonstration Adaptive Algorithm Selector"""
    logger.info("🚀 Démonstration Adaptive Algorithm Selector")
    
    # Configuration sélecteur
    config = SelectorConfig(
        switching_threshold=0.1,
        a_b_testing_enabled=True,
        a_b_testing_ratio=0.15
    )
    
    # Initialisation sélecteur
    selector = AdaptiveAlgorithmSelector(config)
    
    # Context requête test
    request_context = RequestContext(
        request_id="test_selector_001",
        client_ip="192.168.1.200",
        request_type="api_heavy",
        payload_size=2048,
        priority_level=8,
        session_id="session_123",
        geographic_origin="eu-west",
        user_tier="premium",
        latency_requirement=0.05  # 50ms
    )
    
    # État charge serveur test
    load_state = ServerLoadState(
        total_servers=5,
        active_servers=4,
        average_cpu_usage=75.0,
        average_memory_usage=60.0,
        total_connections=250,
        requests_per_second=850.0,
        error_rate=0.02,
        geographic_distribution={"us-east": 2, "eu-west": 2, "asia-pacific": 1},
        health_status={"server_1": "healthy", "server_2": "healthy", "server_3": "degraded", "server_4": "healthy", "server_5": "maintenance"}
    )
    
    # Test sélection algorithme
    selected_algorithm = await selector.select_optimal_algorithm(request_context, load_state)
    logger.info(f"🎯 Algorithme sélectionné: {selected_algorithm.value}")
    
    # Simulation monitoring performance
    metrics = {
        "response_time": 0.08,
        "throughput": 180.0,
        "error_occurred": False,
        "context_categories": [ContextCategory.HIGH_TRAFFIC, ContextCategory.LOW_LATENCY_REQUIRED]
    }
    
    monitoring_result = await selector.monitor_algorithm_performance(selected_algorithm, metrics)
    logger.info(f"📊 Monitoring result: score={monitoring_result['performance_score']:.3f}")
    
    logger.info("✅ Démonstration terminée avec succès")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())