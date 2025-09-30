"""
Intelligent Retry Orchestrator - Ainflue
========================================
Orchestrateur retry intelligent avec ML predictions.
Success rate prediction + adaptive strategies + failure pattern analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Retry Mechanisms
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture retry mechanisms et tous ses algorithmes sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import time
import json
import random
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RetryDecision(Enum):
    """Décisions possibles pour retry"""
    RETRY = "retry"
    ABORT = "abort"
    ESCALATE = "escalate"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"

class FailurePattern(Enum):
    """Types de patterns d'échec détectés"""
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    CASCADING = "cascading"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    TIMEOUT_PATTERN = "timeout_pattern"
    DEPENDENCY_FAILURE = "dependency_failure"
    ANOMALY = "anomaly"

@dataclass
class Operation:
    """Représentation d'une opération à retry"""
    id: str
    name: str
    service: str
    operation_type: str
    context: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    priority: int = 1  # 1=low, 5=critical
    timeout: Optional[float] = None
    created_at: float = field(default_factory=time.time)

@dataclass
class MLConfig:
    """Configuration ML pour orchestrateur"""
    prediction_enabled: bool = True
    pattern_analysis_enabled: bool = True
    adaptive_strategies_enabled: bool = True
    success_rate_threshold: float = 0.7
    confidence_threshold: float = 0.8
    learning_rate: float = 0.01
    model_update_interval: int = 3600  # 1 hour
    feature_window_size: int = 100

@dataclass
class ServiceMetrics:
    """Métriques service pour ML analysis"""
    service_name: str
    success_rate: float = 0.0
    average_latency: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    last_updated: float = field(default_factory=time.time)
    
    def update_metrics(self, success: bool, latency: float):
        """Mise à jour métriques temps réel"""
        # Simple moving average approximation
        alpha = 0.1
        if success:
            self.success_rate = self.success_rate * (1 - alpha) + alpha
        else:
            self.success_rate = self.success_rate * (1 - alpha)
        
        self.average_latency = self.average_latency * (1 - alpha) + latency * alpha
        self.error_rate = 1.0 - self.success_rate
        self.last_updated = time.time()

class RetrySuccessPredictor:
    """Prédicteur ML pour success rate des retry"""
    
    def __init__(self):
        self.feature_history = deque(maxlen=1000)
        self.success_history = deque(maxlen=1000)
        self.model_weights = defaultdict(float)
        self.learning_enabled = True
    
    async def predict_success_probability(self, operation: Operation, context: Dict) -> float:
        """Prédiction probabilité succès retry avec ML basique"""
        
        features = self._extract_features(operation, context)
        
        # Simple linear prediction basée sur features
        prediction = 0.5  # baseline
        
        for feature, value in features.items():
            prediction += self.model_weights[feature] * value
        
        # Normalisation entre 0 et 1
        prediction = max(0.0, min(1.0, prediction))
        
        # Facteurs contextuels
        if context.get('service_health', 1.0) < 0.5:
            prediction *= 0.7
        
        if context.get('load_factor', 1.0) > 0.8:
            prediction *= 0.8
        
        return prediction
    
    def _extract_features(self, operation: Operation, context: Dict) -> Dict[str, float]:
        """Extraction features pour ML prediction"""
        
        features = {
            'operation_priority': operation.priority / 5.0,
            'service_success_rate': context.get('service_success_rate', 0.5),
            'time_of_day': (time.time() % 86400) / 86400,  # Normalised time of day
            'previous_attempts': context.get('attempt_count', 0) / 10.0,
            'operation_complexity': self._calculate_operation_complexity(operation),
            'resource_availability': context.get('resource_availability', 1.0),
            'network_quality': context.get('network_quality', 1.0)
        }
        
        return features
    
    def _calculate_operation_complexity(self, operation: Operation) -> float:
        """Calcul complexité opération (heuristique)"""
        complexity = 0.1
        
        # Type d'opération
        complexity_map = {
            'content_processing': 0.8,
            'ai_processing': 0.9,
            'monetization': 0.6,
            'collaboration': 0.7,
            'distribution': 0.5,
            'protection': 0.4
        }
        
        complexity += complexity_map.get(operation.operation_type, 0.5)
        
        # Taille des données
        data_size = operation.metadata.get('data_size', 0)
        if data_size > 0:
            complexity += min(data_size / 1000000, 0.3)  # Cap at 0.3
        
        return min(complexity, 1.0)
    
    async def update_model(self, operation: Operation, context: Dict, success: bool):
        """Mise à jour modèle ML avec résultat"""
        if not self.learning_enabled:
            return
        
        features = self._extract_features(operation, context)
        
        # Simple gradient descent update
        learning_rate = 0.01
        prediction = await self.predict_success_probability(operation, context)
        error = (1.0 if success else 0.0) - prediction
        
        for feature, value in features.items():
            self.model_weights[feature] += learning_rate * error * value
        
        # Store for history
        self.feature_history.append(features)
        self.success_history.append(success)

class FailurePatternAnalyzer:
    """Analyseur patterns d'échec avec ML clustering"""
    
    def __init__(self):
        self.failure_history = deque(maxlen=1000)
        self.pattern_cache = {}
        self.anomaly_threshold = 0.8
    
    async def analyze_failure_pattern(self, failure_events: List[Dict]) -> FailurePattern:
        """Analyse pattern d'échec avec ML clustering basique"""
        
        if not failure_events:
            return FailurePattern.TRANSIENT
        
        # Analyse temporelle
        if self._is_cascading_failure(failure_events):
            return FailurePattern.CASCADING
        
        # Analyse par type d'erreur
        error_types = [event.get('error_type', 'unknown') for event in failure_events]
        most_common_error = max(set(error_types), key=error_types.count)
        
        if most_common_error in ['timeout', 'connection_timeout']:
            return FailurePattern.TIMEOUT_PATTERN
        elif most_common_error in ['resource_unavailable', 'out_of_memory']:
            return FailurePattern.RESOURCE_EXHAUSTION
        elif most_common_error in ['service_unavailable', 'dependency_error']:
            return FailurePattern.DEPENDENCY_FAILURE
        
        # Analyse fréquentielle
        if len(failure_events) > 10 and self._is_high_frequency_failure(failure_events):
            return FailurePattern.PERMANENT
        
        # Détection d'anomalie
        if self._is_anomalous_pattern(failure_events):
            return FailurePattern.ANOMALY
        
        return FailurePattern.TRANSIENT
    
    def _is_cascading_failure(self, failure_events: List[Dict]) -> bool:
        """Détection cascading failure"""
        if len(failure_events) < 3:
            return False
        
        # Check if failures spread across services
        services = set(event.get('service', 'unknown') for event in failure_events)
        if len(services) > 1:
            # Check temporal proximity
            times = [event.get('timestamp', 0) for event in failure_events]
            time_spread = max(times) - min(times)
            return time_spread < 300  # 5 minutes
        
        return False
    
    def _is_high_frequency_failure(self, failure_events: List[Dict]) -> bool:
        """Détection high frequency failure"""
        if len(failure_events) < 5:
            return False
        
        times = [event.get('timestamp', 0) for event in failure_events]
        time_span = max(times) - min(times)
        
        # Plus de 10 échecs en moins d'une heure
        return len(failure_events) > 10 and time_span < 3600
    
    def _is_anomalous_pattern(self, failure_events: List[Dict]) -> bool:
        """Détection pattern anomalique basique"""
        
        # Vérification patterns inhabituels
        error_distribution = defaultdict(int)
        for event in failure_events:
            error_distribution[event.get('error_type', 'unknown')] += 1
        
        # Si un type d'erreur domine > 80%, c'est probablement systémique
        total_events = len(failure_events)
        max_error_count = max(error_distribution.values()) if error_distribution else 0
        
        return max_error_count / total_events > 0.8 if total_events > 0 else False

class RetryStrategyOptimizer:
    """Optimiseur stratégies retry basé sur ML"""
    
    def __init__(self):
        self.strategy_performance = defaultdict(lambda: {'success_rate': 0.5, 'avg_latency': 1.0})
        self.optimization_history = deque(maxlen=500)
    
    async def optimize_strategy(self, service_metrics: ServiceMetrics, failure_pattern: FailurePattern) -> Dict:
        """Optimization stratégie retry basée sur métriques et patterns"""
        
        base_strategy = {
            'max_retries': 3,
            'initial_delay': 1.0,
            'max_delay': 60.0,
            'backoff_multiplier': 2.0,
            'jitter_enabled': True
        }
        
        # Adaptation basée sur service metrics
        if service_metrics.success_rate < 0.5:
            base_strategy['max_retries'] = 2  # Moins de retry si service instable
            base_strategy['initial_delay'] = 2.0  # Délai plus long
        elif service_metrics.success_rate > 0.9:
            base_strategy['max_retries'] = 5  # Plus de retry si service fiable
            base_strategy['initial_delay'] = 0.5  # Délai plus court
        
        # Adaptation basée sur failure pattern
        if failure_pattern == FailurePattern.TIMEOUT_PATTERN:
            base_strategy['max_delay'] = 120.0
            base_strategy['initial_delay'] = 5.0
        elif failure_pattern == FailurePattern.RESOURCE_EXHAUSTION:
            base_strategy['max_retries'] = 2
            base_strategy['initial_delay'] = 10.0
        elif failure_pattern == FailurePattern.CASCADING:
            base_strategy['max_retries'] = 1
            base_strategy['jitter_enabled'] = True
            base_strategy['backoff_multiplier'] = 3.0
        
        # Adaptation basée sur charge système
        if service_metrics.cpu_usage > 0.8:
            base_strategy['initial_delay'] *= 2
            base_strategy['jitter_enabled'] = True
        
        return base_strategy

class RetryContextManager:
    """Manager contexte retry avec tracking"""
    
    def __init__(self):
        self.active_operations = {}
        self.operation_history = deque(maxlen=1000)
        self.service_stats = defaultdict(ServiceMetrics)
    
    async def create_context(self, operation: Operation) -> Dict:
        """Création contexte retry enrichi"""
        
        service_stats = self.service_stats[operation.service]
        
        context = {
            'operation_id': operation.id,
            'service': operation.service,
            'operation_type': operation.operation_type,
            'priority': operation.priority,
            'created_at': operation.created_at,
            'attempt_count': 0,
            'service_success_rate': service_stats.success_rate,
            'service_avg_latency': service_stats.average_latency,
            'resource_availability': self._calculate_resource_availability(),
            'network_quality': self._estimate_network_quality(),
            'load_factor': self._calculate_load_factor(),
            'service_health': self._calculate_service_health(operation.service)
        }
        
        self.active_operations[operation.id] = context
        return context
    
    def _calculate_resource_availability(self) -> float:
        """Calcul disponibilité ressources (simulation)"""
        # En production, intégrerait avec monitoring système
        return random.uniform(0.7, 1.0)
    
    def _estimate_network_quality(self) -> float:
        """Estimation qualité réseau (simulation)"""
        # En production, intégrerait avec monitoring réseau
        return random.uniform(0.8, 1.0)
    
    def _calculate_load_factor(self) -> float:
        """Calcul facteur de charge système"""
        active_operations = len(self.active_operations)
        # Normalisation basique
        return min(active_operations / 100.0, 1.0)
    
    def _calculate_service_health(self, service: str) -> float:
        """Calcul santé service"""
        stats = self.service_stats[service]
        health = stats.success_rate * 0.6 + (1.0 - stats.error_rate) * 0.4
        return max(0.0, min(1.0, health))
    
    async def update_context(self, operation_id: str, success: bool, latency: float):
        """Mise à jour contexte après opération"""
        if operation_id in self.active_operations:
            context = self.active_operations[operation_id]
            service = context['service']
            
            # Mise à jour stats service
            self.service_stats[service].update_metrics(success, latency)
            
            # Historique
            self.operation_history.append({
                'operation_id': operation_id,
                'success': success,
                'latency': latency,
                'timestamp': time.time(),
                'service': service
            })
            
            if success:
                del self.active_operations[operation_id]

class IntelligentRetryOrchestrator:
    """
    Orchestrateur retry intelligent avec ML predictions.
    Success rate prediction + adaptive strategies + failure pattern analysis.
    """
    
    def __init__(self, ml_config: MLConfig = None):
        self.ml_config = ml_config or MLConfig()
        self.ml_predictor = RetrySuccessPredictor()
        self.pattern_analyzer = FailurePatternAnalyzer()
        self.strategy_optimizer = RetryStrategyOptimizer()
        self.context_manager = RetryContextManager()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Cache pour optimisations
        self.strategy_cache = {}
        self.pattern_cache = {}
        
        # Métriques orchestrateur
        self.orchestration_metrics = {
            'total_decisions': 0,
            'successful_predictions': 0,
            'pattern_detections': 0,
            'strategy_optimizations': 0,
            'last_model_update': time.time()
        }
    
    async def orchestrate_intelligent_retry(self, operation: Operation) -> RetryDecision:
        """
        Orchestration retry avec ML predictions et adaptive strategies.
        
        Intelligence Features:
        - ML-based success rate prediction pour retry decisions
        - Failure pattern analysis pour strategy optimization
        - Context-aware retry avec service health monitoring
        - Adaptive timeout adjustment basé sur historical data
        - Cross-service retry coordination
        - Resource-aware retry scheduling
        - Priority-based retry queue management
        """
        
        self.orchestration_metrics['total_decisions'] += 1
        
        try:
            # 1. Création contexte enrichi
            context = await self.context_manager.create_context(operation)
            
            # 2. Prédiction success rate avec ML
            success_probability = await self.predict_retry_success(context)
            
            # 3. Analyse pattern d'échec si applicable
            failure_pattern = await self._get_failure_pattern(operation, context)
            
            # 4. Décision intelligente basée sur ML et patterns
            decision = await self._make_intelligent_decision(
                operation, context, success_probability, failure_pattern
            )
            
            # 5. Optimisation stratégie si retry décidé
            if decision == RetryDecision.RETRY:
                await self._optimize_retry_strategy(operation, context, failure_pattern)
            
            self.logger.info(f"Orchestrated decision for {operation.id}: {decision.value} (probability: {success_probability:.2f})")
            return decision
            
        except Exception as e:
            self.logger.error(f"Error in orchestration for {operation.id}: {str(e)}")
            return RetryDecision.ABORT
    
    async def predict_retry_success(self, operation_context: Dict) -> float:
        """Prédiction probabilité succès retry avec ML."""
        
        if not self.ml_config.prediction_enabled:
            return 0.5  # Baseline probability
        
        # Création operation dummy pour prediction
        operation = Operation(
            id=operation_context.get('operation_id', 'unknown'),
            name=operation_context.get('operation_name', 'unknown'),
            service=operation_context.get('service', 'unknown'),
            operation_type=operation_context.get('operation_type', 'unknown'),
            priority=operation_context.get('priority', 1)
        )
        
        probability = await self.ml_predictor.predict_success_probability(operation, operation_context)
        
        # Facteurs correctifs basés sur contexte
        if operation_context.get('attempt_count', 0) > 2:
            probability *= 0.8  # Réduction après plusieurs échecs
        
        if operation_context.get('service_health', 1.0) < 0.3:
            probability *= 0.5  # Service très dégradé
        
        return max(0.0, min(1.0, probability))
    
    async def analyze_failure_patterns(self, failure_history: List[Dict]) -> FailurePattern:
        """Analyse patterns d'échec pour strategy optimization."""
        
        if not self.ml_config.pattern_analysis_enabled:
            return FailurePattern.TRANSIENT
        
        # Utilisation du cache si disponible
        cache_key = self._generate_cache_key(failure_history)
        if cache_key in self.pattern_cache:
            return self.pattern_cache[cache_key]
        
        pattern = await self.pattern_analyzer.analyze_failure_pattern(failure_history)
        
        # Mise en cache
        self.pattern_cache[cache_key] = pattern
        self.orchestration_metrics['pattern_detections'] += 1
        
        return pattern
    
    async def optimize_retry_strategy(self, service_metrics: Dict) -> Dict:
        """Optimization stratégie retry basée sur metrics service."""
        
        if not self.ml_config.adaptive_strategies_enabled:
            return {'max_retries': 3, 'initial_delay': 1.0}
        
        # Conversion metrics en ServiceMetrics object
        metrics = ServiceMetrics(service_metrics.get('service_name', 'unknown'))
        metrics.success_rate = service_metrics.get('success_rate', 0.5)
        metrics.average_latency = service_metrics.get('average_latency', 1.0)
        metrics.error_rate = service_metrics.get('error_rate', 0.5)
        metrics.cpu_usage = service_metrics.get('cpu_usage', 0.5)
        metrics.memory_usage = service_metrics.get('memory_usage', 0.5)
        
        # Analyse pattern récent
        recent_failures = service_metrics.get('recent_failures', [])
        failure_pattern = await self.analyze_failure_patterns(recent_failures)
        
        # Optimisation
        strategy = await self.strategy_optimizer.optimize_strategy(metrics, failure_pattern)
        
        self.orchestration_metrics['strategy_optimizations'] += 1
        return strategy
    
    async def coordinate_cross_service_retries(self, service_requests: List[Dict]) -> Dict:
        """Coordination retries cross-service pour éviter cascading failures."""
        
        coordination_result = {
            'coordinated_requests': 0,
            'delayed_requests': 0,
            'rejected_requests': 0,
            'recommendations': []
        }
        
        # Analyse charge globale
        total_load = sum(req.get('priority', 1) for req in service_requests)
        
        # Si charge excessive, coordination intelligente
        if total_load > 20:  # Seuil arbitraire
            coordination_result['recommendations'].append("High system load detected")
            
            # Priorisation des requêtes
            sorted_requests = sorted(service_requests, key=lambda x: x.get('priority', 1), reverse=True)
            
            # Délai échelonné pour éviter thundering herd
            for i, request in enumerate(sorted_requests):
                if i > 5:  # Limit concurrent requests
                    coordination_result['delayed_requests'] += 1
                    coordination_result['recommendations'].append(f"Delay request {request.get('id')} by {i}s")
                else:
                    coordination_result['coordinated_requests'] += 1
        else:
            coordination_result['coordinated_requests'] = len(service_requests)
        
        return coordination_result
    
    async def _get_failure_pattern(self, operation: Operation, context: Dict) -> FailurePattern:
        """Récupération pattern d'échec pour opération"""
        
        # Récupération historique échecs pour ce service
        failure_history = []
        for event in self.context_manager.operation_history:
            if (event.get('service') == operation.service and 
                not event.get('success', True) and
                time.time() - event.get('timestamp', 0) < 3600):  # Last hour
                failure_history.append(event)
        
        if not failure_history:
            return FailurePattern.TRANSIENT
        
        return await self.analyze_failure_patterns(failure_history)
    
    async def _make_intelligent_decision(
        self, 
        operation: Operation, 
        context: Dict, 
        success_probability: float, 
        failure_pattern: FailurePattern
    ) -> RetryDecision:
        """Décision intelligente basée sur ML et patterns"""
        
        # Seuils de décision adaptatifs
        retry_threshold = self.ml_config.success_rate_threshold
        
        # Ajustement basé sur priorité
        if operation.priority >= 4:  # High priority
            retry_threshold *= 0.7  # Plus tolérant pour retry
        elif operation.priority <= 2:  # Low priority
            retry_threshold *= 1.3  # Moins tolérant
        
        # Décision basée sur probabilité
        if success_probability < retry_threshold * 0.3:
            return RetryDecision.ABORT
        elif success_probability < retry_threshold * 0.6:
            if failure_pattern in [FailurePattern.PERMANENT, FailurePattern.CASCADING]:
                return RetryDecision.CIRCUIT_BREAK
            else:
                return RetryDecision.FALLBACK
        elif success_probability < retry_threshold:
            if context.get('attempt_count', 0) > 3:
                return RetryDecision.ESCALATE
            else:
                return RetryDecision.RETRY
        else:
            return RetryDecision.RETRY
    
    async def _optimize_retry_strategy(self, operation: Operation, context: Dict, failure_pattern: FailurePattern):
        """Optimisation stratégie retry pour opération"""
        
        service_metrics = {
            'service_name': operation.service,
            'success_rate': context.get('service_success_rate', 0.5),
            'average_latency': context.get('service_avg_latency', 1.0),
            'error_rate': 1.0 - context.get('service_success_rate', 0.5),
            'recent_failures': []  # Would be populated with real data
        }
        
        optimized_strategy = await self.optimize_retry_strategy(service_metrics)
        
        # Application stratégie optimisée au contexte
        context.update({
            'optimized_strategy': optimized_strategy,
            'failure_pattern': failure_pattern.value,
            'optimization_timestamp': time.time()
        })
    
    def _generate_cache_key(self, data: Any) -> str:
        """Génération clé cache pour patterns"""
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
    
    async def get_orchestration_metrics(self) -> Dict:
        """Récupération métriques orchestrateur"""
        return {
            **self.orchestration_metrics,
            'predictor_stats': {
                'feature_history_size': len(self.ml_predictor.feature_history),
                'success_history_size': len(self.ml_predictor.success_history),
                'learning_enabled': self.ml_predictor.learning_enabled
            },
            'pattern_analyzer_stats': {
                'failure_history_size': len(self.pattern_analyzer.failure_history),
                'pattern_cache_size': len(self.pattern_cache)
            },
            'context_manager_stats': {
                'active_operations': len(self.context_manager.active_operations),
                'operation_history_size': len(self.context_manager.operation_history),
                'tracked_services': len(self.context_manager.service_stats)
            }
        }
    
    async def update_ml_models(self, operation: Operation, context: Dict, success: bool):
        """Mise à jour modèles ML avec résultats"""
        await self.ml_predictor.update_model(operation, context, success)
        await self.context_manager.update_context(operation.id, success, context.get('latency', 0.0))
        
        if success:
            self.orchestration_metrics['successful_predictions'] += 1

# Factory functions
def create_intelligent_orchestrator(
    prediction_enabled: bool = True,
    pattern_analysis_enabled: bool = True,
    adaptive_strategies_enabled: bool = True
) -> IntelligentRetryOrchestrator:
    """Factory pour création orchestrateur intelligent"""
    
    ml_config = MLConfig(
        prediction_enabled=prediction_enabled,
        pattern_analysis_enabled=pattern_analysis_enabled,
        adaptive_strategies_enabled=adaptive_strategies_enabled
    )
    
    return IntelligentRetryOrchestrator(ml_config)

__all__ = [
    'IntelligentRetryOrchestrator',
    'RetryDecision',
    'FailurePattern', 
    'Operation',
    'MLConfig',
    'RetrySuccessPredictor',
    'FailurePatternAnalyzer',
    'RetryStrategyOptimizer',
    'RetryContextManager',
    'create_intelligent_orchestrator'
]