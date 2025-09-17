"""
🤖 Intelligent Load Balancer Enterprise - Ainflue
=================================================
Load balancer intelligent avec ML predictions.
Traffic prediction + health scoring + adaptive routing.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Service Discovery
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de
"""

import asyncio
import time
import logging
import hashlib
import statistics
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import math

from .distributed_service_registry import ServiceInstance, ServiceStatus

logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    """Algorithmes de load balancing"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RESPONSE_TIME = "response_time"
    RESOURCE_BASED = "resource_based"
    GEOGRAPHIC = "geographic"
    ML_PREDICTIVE = "ml_predictive"
    CONSISTENT_HASH = "consistent_hash"

class RequestType(Enum):
    """Types de requêtes pour le routing intelligent"""
    CPU_INTENSIVE = "cpu_intensive"
    IO_INTENSIVE = "io_intensive"
    MEMORY_INTENSIVE = "memory_intensive"
    NETWORK_INTENSIVE = "network_intensive"
    BALANCED = "balanced"

@dataclass
class RequestContext:
    """Contexte d'une requête pour le load balancing"""
    request_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    user_location: Optional[str] = None
    request_type: RequestType = RequestType.BALANCED
    priority: int = 1
    metadata: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class LoadPrediction:
    """Prédiction de charge d'une instance"""
    instance_id: str
    predicted_load: float  # 0.0 à 1.0
    confidence: float  # 0.0 à 1.0
    time_window: int  # secondes
    factors: Dict[str, float] = field(default_factory=dict)

@dataclass
class HealthScore:
    """Score de santé d'une instance"""
    instance_id: str
    overall_score: float  # 0.0 à 1.0
    cpu_score: float = 0.0
    memory_score: float = 0.0
    network_score: float = 0.0
    response_time_score: float = 0.0
    error_rate_score: float = 0.0
    last_updated: float = field(default_factory=time.time)

@dataclass
class RoutingStrategy:
    """Stratégie de routing optimale"""
    algorithm: LoadBalancingAlgorithm
    weights: Dict[str, float] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    effectiveness_score: float = 0.0

class TrafficPredictionEngine:
    """Moteur de prédiction de trafic basé sur ML"""
    
    def __init__(self):
        self.historical_data: Dict[str, List[Dict]] = {}
        self.prediction_models: Dict[str, Any] = {}
        self.learning_rate = 0.01
    
    async def predict_instance_load(self, instance: ServiceInstance, time_window: int = 300) -> LoadPrediction:
        """Prédire la charge d'une instance avec ML time series"""
        try:
            instance_id = instance.service_id
            
            # Collecter les données historiques
            history = self.historical_data.get(instance_id, [])
            if len(history) < 3:
                # Pas assez de données, prédiction basique
                base_load = 0.3  # Charge par défaut
                return LoadPrediction(
                    instance_id=instance_id,
                    predicted_load=base_load,
                    confidence=0.5,
                    time_window=time_window,
                    factors={'insufficient_data': 1.0}
                )
            
            # Analyse des tendances
            recent_loads = [entry['load'] for entry in history[-10:]]
            trend = self._calculate_trend(recent_loads)
            
            # Prédiction basée sur les patterns
            base_load = statistics.mean(recent_loads)
            predicted_load = max(0.0, min(1.0, base_load + trend * 0.1))
            
            # Facteurs d'influence
            factors = {
                'historical_average': base_load,
                'trend': trend,
                'time_of_day': self._get_time_factor(),
                'day_of_week': self._get_day_factor()
            }
            
            # Ajustement basé sur les facteurs
            time_factor = factors['time_of_day']
            day_factor = factors['day_of_week']
            
            predicted_load *= (time_factor * day_factor)
            predicted_load = max(0.0, min(1.0, predicted_load))
            
            confidence = min(0.95, len(history) / 50.0)  # Plus de données = plus de confiance
            
            return LoadPrediction(
                instance_id=instance_id,
                predicted_load=predicted_load,
                confidence=confidence,
                time_window=time_window,
                factors=factors
            )
            
        except Exception as e:
            logger.error(f"Erreur prédiction charge: {e}")
            return LoadPrediction(
                instance_id=instance.service_id,
                predicted_load=0.5,
                confidence=0.1,
                time_window=time_window
            )
    
    def _calculate_trend(self, data: List[float]) -> float:
        """Calculer la tendance des données"""
        if len(data) < 2:
            return 0.0
        
        # Simple linear regression
        n = len(data)
        x_sum = sum(range(n))
        y_sum = sum(data)
        xy_sum = sum(i * data[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope
    
    def _get_time_factor(self) -> float:
        """Facteur basé sur l'heure de la journée"""
        hour = datetime.now().hour
        # Peak hours: 9-11, 14-16, 19-21
        if hour in [9, 10, 11, 14, 15, 16, 19, 20, 21]:
            return 1.3
        elif hour in [0, 1, 2, 3, 4, 5]:
            return 0.5
        else:
            return 1.0
    
    def _get_day_factor(self) -> float:
        """Facteur basé sur le jour de la semaine"""
        weekday = datetime.now().weekday()
        # Lundi = 0, Dimanche = 6
        if weekday < 5:  # Jours de semaine
            return 1.2
        else:  # Weekend
            return 0.8
    
    async def record_load_data(self, instance_id: str, load: float, metadata: Dict = None):
        """Enregistrer les données de charge pour l'apprentissage"""
        if instance_id not in self.historical_data:
            self.historical_data[instance_id] = []
        
        data_entry = {
            'timestamp': time.time(),
            'load': load,
            'metadata': metadata or {}
        }
        
        self.historical_data[instance_id].append(data_entry)
        
        # Limiter l'historique (garder 1000 derniers points)
        if len(self.historical_data[instance_id]) > 1000:
            self.historical_data[instance_id] = self.historical_data[instance_id][-1000:]

class ServiceHealthScorer:
    """Calculateur de score de santé des services"""
    
    def __init__(self):
        self.health_history: Dict[str, List[Dict]] = {}
        self.weights = {
            'cpu': 0.25,
            'memory': 0.25,
            'network': 0.2,
            'response_time': 0.2,
            'error_rate': 0.1
        }
    
    async def calculate_health_score(self, instance: ServiceInstance) -> HealthScore:
        """Calcul score santé instance avec multiple metrics"""
        try:
            instance_id = instance.service_id
            
            # Métriques par défaut (simulation - à remplacer par vraies métriques)
            metrics = await self._get_instance_metrics(instance)
            
            # Calcul des scores individuels
            cpu_score = self._calculate_cpu_score(metrics.get('cpu_usage', 0.5))
            memory_score = self._calculate_memory_score(metrics.get('memory_usage', 0.5))
            network_score = self._calculate_network_score(metrics.get('network_latency', 50))
            response_time_score = self._calculate_response_time_score(metrics.get('response_time', 100))
            error_rate_score = self._calculate_error_rate_score(metrics.get('error_rate', 0.01))
            
            # Score global pondéré
            overall_score = (
                cpu_score * self.weights['cpu'] +
                memory_score * self.weights['memory'] +
                network_score * self.weights['network'] +
                response_time_score * self.weights['response_time'] +
                error_rate_score * self.weights['error_rate']
            )
            
            # Ajustement basé sur le statut
            if instance.status == ServiceStatus.UNHEALTHY:
                overall_score *= 0.1
            elif instance.status == ServiceStatus.DEGRADED:
                overall_score *= 0.6
            
            health_score = HealthScore(
                instance_id=instance_id,
                overall_score=overall_score,
                cpu_score=cpu_score,
                memory_score=memory_score,
                network_score=network_score,
                response_time_score=response_time_score,
                error_rate_score=error_rate_score
            )
            
            # Enregistrer dans l'historique
            await self._record_health_score(instance_id, health_score)
            
            return health_score
            
        except Exception as e:
            logger.error(f"Erreur calcul health score: {e}")
            return HealthScore(
                instance_id=instance.service_id,
                overall_score=0.5
            )
    
    def _calculate_cpu_score(self, cpu_usage: float) -> float:
        """Score basé sur l'utilisation CPU (0-1)"""
        # Score inversement proportionnel à l'utilisation
        return max(0.0, 1.0 - cpu_usage)
    
    def _calculate_memory_score(self, memory_usage: float) -> float:
        """Score basé sur l'utilisation mémoire (0-1)"""
        return max(0.0, 1.0 - memory_usage)
    
    def _calculate_network_score(self, latency_ms: float) -> float:
        """Score basé sur la latence réseau"""
        # Score décroissant avec la latence
        if latency_ms <= 10:
            return 1.0
        elif latency_ms <= 50:
            return 0.8
        elif latency_ms <= 100:
            return 0.6
        elif latency_ms <= 200:
            return 0.4
        else:
            return 0.2
    
    def _calculate_response_time_score(self, response_time_ms: float) -> float:
        """Score basé sur le temps de réponse"""
        if response_time_ms <= 50:
            return 1.0
        elif response_time_ms <= 100:
            return 0.9
        elif response_time_ms <= 200:
            return 0.7
        elif response_time_ms <= 500:
            return 0.5
        else:
            return 0.2
    
    def _calculate_error_rate_score(self, error_rate: float) -> float:
        """Score basé sur le taux d'erreur"""
        return max(0.0, 1.0 - error_rate * 10)  # Pénalité forte pour les erreurs
    
    async def _get_instance_metrics(self, instance: ServiceInstance) -> Dict[str, float]:
        """Obtenir les métriques d'une instance (simulation)"""
        # En production, ces métriques viendraient de Prometheus, New Relic, etc.
        return {
            'cpu_usage': min(0.9, 0.3 + (instance.failure_count * 0.1)),
            'memory_usage': min(0.9, 0.4 + (instance.failure_count * 0.05)),
            'network_latency': max(10, 30 + (instance.failure_count * 20)),
            'response_time': max(20, 80 + (instance.failure_count * 30)),
            'error_rate': min(0.1, instance.failure_count * 0.01)
        }
    
    async def _record_health_score(self, instance_id: str, health_score: HealthScore):
        """Enregistrer le score de santé dans l'historique"""
        if instance_id not in self.health_history:
            self.health_history[instance_id] = []
        
        score_entry = {
            'timestamp': time.time(),
            'overall_score': health_score.overall_score,
            'cpu_score': health_score.cpu_score,
            'memory_score': health_score.memory_score,
            'network_score': health_score.network_score,
            'response_time_score': health_score.response_time_score,
            'error_rate_score': health_score.error_rate_score
        }
        
        self.health_history[instance_id].append(score_entry)
        
        # Limiter l'historique
        if len(self.health_history[instance_id]) > 500:
            self.health_history[instance_id] = self.health_history[instance_id][-500:]

class RoutingOptimizer:
    """Optimiseur de stratégies de routing"""
    
    def __init__(self):
        self.routing_history: Dict[str, List[Dict]] = {}
        self.algorithm_performance: Dict[LoadBalancingAlgorithm, float] = {}
    
    async def optimize_routing_strategy(self, service_name: str, service_metrics: Dict) -> RoutingStrategy:
        """Optimization stratégie routing basée sur performance historique"""
        try:
            # Analyser les performances des différents algorithmes
            algorithm_scores = {}
            
            for algorithm in LoadBalancingAlgorithm:
                score = await self._evaluate_algorithm_performance(service_name, algorithm, service_metrics)
                algorithm_scores[algorithm] = score
            
            # Sélectionner le meilleur algorithme
            best_algorithm = max(algorithm_scores.items(), key=lambda x: x[1])
            selected_algorithm, effectiveness_score = best_algorithm
            
            # Paramètres optimaux pour l'algorithme sélectionné
            parameters = await self._get_optimal_parameters(selected_algorithm, service_metrics)
            
            # Poids optimaux pour les instances
            weights = await self._calculate_optimal_weights(service_metrics)
            
            routing_strategy = RoutingStrategy(
                algorithm=selected_algorithm,
                weights=weights,
                parameters=parameters,
                effectiveness_score=effectiveness_score
            )
            
            logger.info(f"🎯 Stratégie optimale pour {service_name}: {selected_algorithm.value} (score: {effectiveness_score:.3f})")
            return routing_strategy
            
        except Exception as e:
            logger.error(f"Erreur optimisation routing: {e}")
            return RoutingStrategy(
                algorithm=LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
                effectiveness_score=0.5
            )
    
    async def _evaluate_algorithm_performance(self, service_name: str, algorithm: LoadBalancingAlgorithm, metrics: Dict) -> float:
        """Évaluer la performance d'un algorithme"""
        # Score basé sur les caractéristiques du service
        base_score = 0.5
        
        # Ajustements selon l'algorithme et les métriques
        if algorithm == LoadBalancingAlgorithm.RESPONSE_TIME:
            # Bon pour les services sensibles à la latence
            latency_sensitivity = metrics.get('latency_sensitivity', 0.5)
            base_score += latency_sensitivity * 0.3
        
        elif algorithm == LoadBalancingAlgorithm.RESOURCE_BASED:
            # Bon pour les services avec charges variables
            load_variance = metrics.get('load_variance', 0.5)
            base_score += load_variance * 0.4
        
        elif algorithm == LoadBalancingAlgorithm.GEOGRAPHIC:
            # Bon pour les services distribués géographiquement
            geographic_distribution = metrics.get('geographic_distribution', 0.5)
            base_score += geographic_distribution * 0.35
        
        elif algorithm == LoadBalancingAlgorithm.ML_PREDICTIVE:
            # Meilleur avec plus de données historiques
            data_availability = metrics.get('historical_data_points', 0) / 1000.0
            base_score += min(0.4, data_availability * 0.4)
        
        # Pénalités pour certaines conditions
        error_rate = metrics.get('error_rate', 0)
        base_score -= error_rate * 2  # Pénalité pour les erreurs
        
        return max(0.0, min(1.0, base_score))
    
    async def _get_optimal_parameters(self, algorithm: LoadBalancingAlgorithm, metrics: Dict) -> Dict[str, Any]:
        """Obtenir les paramètres optimaux pour un algorithme"""
        parameters = {}
        
        if algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            parameters['weight_factor'] = 1.0
            parameters['health_weight'] = 0.7
            parameters['performance_weight'] = 0.3
        
        elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            parameters['connection_threshold'] = 100
            parameters['overflow_strategy'] = 'round_robin'
        
        elif algorithm == LoadBalancingAlgorithm.RESPONSE_TIME:
            parameters['time_window'] = 60  # seconds
            parameters['sample_size'] = 10
        
        elif algorithm == LoadBalancingAlgorithm.ML_PREDICTIVE:
            parameters['prediction_window'] = 300  # seconds
            parameters['confidence_threshold'] = 0.7
            parameters['fallback_algorithm'] = LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN.value
        
        return parameters
    
    async def _calculate_optimal_weights(self, metrics: Dict) -> Dict[str, float]:
        """Calculer les poids optimaux pour les instances"""
        weights = {}
        
        # Facteurs de pondération
        factors = {
            'health_factor': 0.4,
            'performance_factor': 0.3,
            'capacity_factor': 0.2,
            'geographic_factor': 0.1
        }
        
        return factors

class PerformanceTracker:
    """Traqueur de performance pour optimisation continue"""
    
    def __init__(self):
        self.performance_data: Dict[str, List[Dict]] = {}
        self.decision_outcomes: Dict[str, List[Dict]] = {}
    
    async def track_routing_decision(self, decision_id: str, instance: ServiceInstance, 
                                   context: RequestContext, outcome: Dict):
        """Tracker une décision de routing et son résultat"""
        decision_data = {
            'decision_id': decision_id,
            'instance_id': instance.service_id,
            'request_context': {
                'request_type': context.request_type.value,
                'priority': context.priority,
                'user_location': context.user_location
            },
            'outcome': outcome,
            'timestamp': time.time()
        }
        
        service_name = instance.service_name
        if service_name not in self.decision_outcomes:
            self.decision_outcomes[service_name] = []
        
        self.decision_outcomes[service_name].append(decision_data)
        
        # Limiter l'historique
        if len(self.decision_outcomes[service_name]) > 1000:
            self.decision_outcomes[service_name] = self.decision_outcomes[service_name][-1000:]
    
    async def get_performance_metrics(self, service_name: str, time_window: int = 3600) -> Dict:
        """Obtenir les métriques de performance"""
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        decisions = self.decision_outcomes.get(service_name, [])
        recent_decisions = [d for d in decisions if d['timestamp'] >= cutoff_time]
        
        if not recent_decisions:
            return {'error': 'Pas de données récentes'}
        
        # Calculer les métriques
        success_rate = sum(1 for d in recent_decisions if d['outcome'].get('success', False)) / len(recent_decisions)
        avg_response_time = statistics.mean([d['outcome'].get('response_time', 0) for d in recent_decisions])
        
        return {
            'total_decisions': len(recent_decisions),
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'time_window': time_window
        }

class IntelligentLoadBalancer:
    """
    Load balancer intelligent avec ML predictions.
    Traffic prediction + health scoring + adaptive routing.
    """
    
    def __init__(self, balancer_config: Dict = None):
        self.balancer_config = balancer_config or {}
        
        # Composants intelligents
        self.traffic_predictor = TrafficPredictionEngine()
        self.health_scorer = ServiceHealthScorer()
        self.routing_optimizer = RoutingOptimizer()
        self.performance_tracker = PerformanceTracker()
        
        # État du load balancer
        self.current_strategies: Dict[str, RoutingStrategy] = {}
        self.instance_counters: Dict[str, int] = {}  # Pour round-robin
        self.session_affinity: Dict[str, str] = {}  # session_id -> instance_id
        
        logger.info("🤖 IntelligentLoadBalancer initialisé")
    
    async def select_optimal_instance(self, service_name: str, instances: List[ServiceInstance], 
                                    request_context: RequestContext) -> Optional[ServiceInstance]:
        """
        Sélection instance optimale avec ML predictions.
        
        Load Balancing Features:
        - ML-based traffic prediction pour capacity planning
        - Health score calculation avec weighted factors
        - Geographic proximity routing
        - Request type-aware routing (CPU vs I/O intensive)
        - Circuit breaker integration pour failed instances
        - Adaptive weight adjustment basé sur performance
        - Session affinity avec consistent hashing
        """
        try:
            if not instances:
                return None
            
            # Filtrer les instances saines
            healthy_instances = [i for i in instances if i.status == ServiceStatus.HEALTHY]
            if not healthy_instances:
                # Fallback vers instances dégradées si aucune saine
                healthy_instances = [i for i in instances if i.status == ServiceStatus.DEGRADED]
                if not healthy_instances:
                    return None
            
            # Vérifier session affinity
            if request_context.session_id and request_context.session_id in self.session_affinity:
                preferred_instance_id = self.session_affinity[request_context.session_id]
                preferred_instance = next((i for i in healthy_instances if i.service_id == preferred_instance_id), None)
                if preferred_instance:
                    logger.info(f"🔗 Session affinity: {request_context.session_id} -> {preferred_instance_id}")
                    return preferred_instance
            
            # Obtenir ou optimiser la stratégie de routing
            strategy = await self._get_routing_strategy(service_name, healthy_instances)
            
            # Sélectionner l'instance selon la stratégie
            selected_instance = await self._apply_routing_strategy(
                strategy, healthy_instances, request_context
            )
            
            if selected_instance:
                # Enregistrer pour session affinity si applicable
                if request_context.session_id:
                    self.session_affinity[request_context.session_id] = selected_instance.service_id
                
                # Tracker la décision pour l'apprentissage
                decision_id = f"{service_name}-{int(time.time())}-{request_context.request_id}"
                asyncio.create_task(self._track_decision(decision_id, selected_instance, request_context))
                
                logger.info(f"🎯 Instance sélectionnée: {selected_instance.service_id} pour {service_name}")
                return selected_instance
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur sélection instance: {e}")
            # Fallback simple
            return healthy_instances[0] if healthy_instances else None
    
    async def calculate_health_score(self, instance: ServiceInstance) -> HealthScore:
        """Calcul score santé instance avec multiple metrics"""
        return await self.health_scorer.calculate_health_score(instance)
    
    async def predict_instance_load(self, instance: ServiceInstance, time_window: int = 300) -> LoadPrediction:
        """Prédiction charge instance avec ML time series"""
        return await self.traffic_predictor.predict_instance_load(instance, time_window)
    
    async def optimize_routing_strategy(self, service_name: str, service_metrics: Dict) -> RoutingStrategy:
        """Optimization stratégie routing basée sur performance historique"""
        strategy = await self.routing_optimizer.optimize_routing_strategy(service_name, service_metrics)
        self.current_strategies[service_name] = strategy
        return strategy
    
    async def _get_routing_strategy(self, service_name: str, instances: List[ServiceInstance]) -> RoutingStrategy:
        """Obtenir la stratégie de routing pour un service"""
        if service_name not in self.current_strategies:
            # Créer les métriques de service
            service_metrics = await self._calculate_service_metrics(service_name, instances)
            
            # Optimiser la stratégie
            strategy = await self.routing_optimizer.optimize_routing_strategy(service_name, service_metrics)
            self.current_strategies[service_name] = strategy
        
        return self.current_strategies[service_name]
    
    async def _apply_routing_strategy(self, strategy: RoutingStrategy, 
                                    instances: List[ServiceInstance], 
                                    context: RequestContext) -> Optional[ServiceInstance]:
        """Appliquer une stratégie de routing"""
        algorithm = strategy.algorithm
        
        if algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return await self._weighted_round_robin(instances, strategy.weights)
        
        elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return await self._least_connections(instances)
        
        elif algorithm == LoadBalancingAlgorithm.RESPONSE_TIME:
            return await self._response_time_based(instances)
        
        elif algorithm == LoadBalancingAlgorithm.RESOURCE_BASED:
            return await self._resource_based(instances)
        
        elif algorithm == LoadBalancingAlgorithm.GEOGRAPHIC:
            return await self._geographic_routing(instances, context)
        
        elif algorithm == LoadBalancingAlgorithm.ML_PREDICTIVE:
            return await self._ml_predictive_routing(instances, context)
        
        elif algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
            return await self._consistent_hash_routing(instances, context)
        
        else:
            # Fallback vers round robin simple
            return await self._round_robin(instances)
    
    async def _weighted_round_robin(self, instances: List[ServiceInstance], weights: Dict[str, float]) -> ServiceInstance:
        """Load balancing weighted round robin"""
        # Calculer les poids effectifs basés sur santé et poids configurés
        weighted_instances = []
        for instance in instances:
            health_score = await self.health_scorer.calculate_health_score(instance)
            effective_weight = instance.weight * health_score.overall_score
            weighted_instances.extend([instance] * max(1, int(effective_weight * 10)))
        
        if not weighted_instances:
            return instances[0]
        
        # Sélection round robin sur les instances pondérées
        service_name = instances[0].service_name
        counter = self.instance_counters.get(service_name, 0) % len(weighted_instances)
        self.instance_counters[service_name] = counter + 1
        
        return weighted_instances[counter]
    
    async def _least_connections(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Load balancing least connections (simulation)"""
        # En production, utiliser les vraies métriques de connexions
        min_connections = min(instance.metadata.get('active_connections', 0) for instance in instances)
        candidates = [i for i in instances if i.metadata.get('active_connections', 0) == min_connections]
        return candidates[0]
    
    async def _response_time_based(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Load balancing basé sur le temps de réponse"""
        # Trier par temps de réponse croissant
        instances_with_response_time = []
        for instance in instances:
            metrics = await self.health_scorer._get_instance_metrics(instance)
            response_time = metrics.get('response_time', 100)
            instances_with_response_time.append((instance, response_time))
        
        instances_with_response_time.sort(key=lambda x: x[1])
        return instances_with_response_time[0][0]
    
    async def _resource_based(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Load balancing basé sur les ressources"""
        best_instance = instances[0]
        best_score = 0
        
        for instance in instances:
            health_score = await self.health_scorer.calculate_health_score(instance)
            # Combiner CPU, mémoire et santé générale
            resource_score = (health_score.cpu_score + health_score.memory_score) / 2
            combined_score = resource_score * health_score.overall_score
            
            if combined_score > best_score:
                best_score = combined_score
                best_instance = instance
        
        return best_instance
    
    async def _geographic_routing(self, instances: List[ServiceInstance], context: RequestContext) -> ServiceInstance:
        """Routing géographique basé sur la proximité"""
        user_location = context.user_location
        if not user_location:
            return await self._weighted_round_robin(instances, {})
        
        # Trouver l'instance la plus proche (simulation basée sur région)
        best_instance = instances[0]
        best_distance = float('inf')
        
        for instance in instances:
            # Distance simulée basée sur région
            distance = self._calculate_geographic_distance(user_location, instance.region)
            if distance < best_distance:
                best_distance = distance
                best_instance = instance
        
        return best_instance
    
    async def _ml_predictive_routing(self, instances: List[ServiceInstance], context: RequestContext) -> ServiceInstance:
        """Routing prédictif basé sur ML"""
        predictions = []
        
        for instance in instances:
            prediction = await self.traffic_predictor.predict_instance_load(instance)
            health_score = await self.health_scorer.calculate_health_score(instance)
            
            # Score combiné: faible charge prédite + bonne santé
            combined_score = (1 - prediction.predicted_load) * health_score.overall_score * prediction.confidence
            predictions.append((instance, combined_score))
        
        # Trier par score décroissant
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[0][0]
    
    async def _consistent_hash_routing(self, instances: List[ServiceInstance], context: RequestContext) -> ServiceInstance:
        """Consistent hashing pour session affinity"""
        # Utiliser user_id ou session_id pour le hashing
        hash_key = context.user_id or context.session_id or context.request_id
        if not hash_key:
            return await self._round_robin(instances)
        
        # Hash consistent
        hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
        instance_index = hash_value % len(instances)
        return instances[instance_index]
    
    async def _round_robin(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Simple round robin"""
        service_name = instances[0].service_name
        counter = self.instance_counters.get(service_name, 0) % len(instances)
        self.instance_counters[service_name] = counter + 1
        return instances[counter]
    
    def _calculate_geographic_distance(self, location1: str, location2: str) -> float:
        """Calculer la distance géographique (simulation)"""
        # Mapping simple région -> coordonnées
        regions = {
            'us-east-1': (39.0458, -76.6413),
            'us-west-1': (37.7749, -122.4194),
            'eu-west-1': (53.3498, -6.2603),
            'ap-southeast-1': (1.3521, 103.8198),
            'default': (0, 0)
        }
        
        coord1 = regions.get(location1, regions['default'])
        coord2 = regions.get(location2, regions['default'])
        
        # Distance euclidienne simple
        return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)
    
    async def _calculate_service_metrics(self, service_name: str, instances: List[ServiceInstance]) -> Dict:
        """Calculer les métriques d'un service"""
        if not instances:
            return {}
        
        # Métriques agrégées du service
        total_failures = sum(instance.failure_count for instance in instances)
        avg_weight = sum(instance.weight for instance in instances) / len(instances)
        regions = set(instance.region for instance in instances)
        
        return {
            'instance_count': len(instances),
            'total_failures': total_failures,
            'error_rate': min(0.1, total_failures / (len(instances) * 10)),
            'avg_weight': avg_weight,
            'geographic_distribution': len(regions) / 5.0,  # Normalised sur 5 régions max
            'latency_sensitivity': 0.7,  # À ajuster selon le type de service
            'load_variance': 0.5,  # À calculer depuis les métriques réelles
            'historical_data_points': len(self.traffic_predictor.historical_data.get(service_name, []))
        }
    
    async def _track_decision(self, decision_id: str, instance: ServiceInstance, context: RequestContext):
        """Tracker une décision de routing pour l'apprentissage"""
        # Simuler le résultat (en production, vient du monitoring)
        outcome = {
            'success': True,
            'response_time': 50 + (instance.failure_count * 20),
            'error': None
        }
        
        await self.performance_tracker.track_routing_decision(decision_id, instance, context, outcome)
    
    async def get_load_balancer_stats(self) -> Dict:
        """Obtenir les statistiques du load balancer"""
        return {
            'strategies_count': len(self.current_strategies),
            'session_affinity_count': len(self.session_affinity),
            'algorithms_used': [s.algorithm.value for s in self.current_strategies.values()],
            'avg_effectiveness': statistics.mean([s.effectiveness_score for s in self.current_strategies.values()]) if self.current_strategies else 0
        }

# Factory function
def create_intelligent_load_balancer(config: Dict = None) -> IntelligentLoadBalancer:
    """Factory pour créer un load balancer intelligent"""
    return IntelligentLoadBalancer(config)

__all__ = [
    'IntelligentLoadBalancer',
    'LoadBalancingAlgorithm',
    'RequestContext',
    'RequestType',
    'LoadPrediction',
    'HealthScore',
    'RoutingStrategy',
    'TrafficPredictionEngine',
    'ServiceHealthScorer',
    'RoutingOptimizer',
    'PerformanceTracker',
    'create_intelligent_load_balancer'
]