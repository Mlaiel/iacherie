#!/usr/bin/env python3
"""
🚀 Circuit Breaker - Enterprise MLOps Platform
Microservices Expertise: Circuit breaker avancé pour prévenir les cascading failures ML

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import threading
from functools import wraps
import statistics
import random

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """États du circuit breaker"""
    CLOSED = "closed"        # Circuit fermé - appels normaux
    OPEN = "open"           # Circuit ouvert - appels bloqués
    HALF_OPEN = "half_open" # Circuit semi-ouvert - test de récupération

class FailureType(Enum):
    """Types d'échecs détectés"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    HTTP_ERROR = "http_error"
    SLOW_RESPONSE = "slow_response"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CUSTOM = "custom"

@dataclass
class CircuitBreakerConfig:
    """Configuration du circuit breaker"""
    failure_threshold: int = 5          # Nombre d'échecs avant ouverture
    recovery_timeout: float = 60.0      # Timeout avant tentative de récupération (secondes)
    success_threshold: int = 3          # Succès requis pour fermeture en half-open
    timeout: float = 10.0               # Timeout par défaut pour les appels
    window_size: int = 10               # Taille de la fenêtre glissante
    slow_call_threshold: float = 5.0    # Seuil pour les appels lents (secondes)
    error_rate_threshold: float = 50.0  # Seuil de taux d'erreur (%)
    min_calls_threshold: int = 5        # Minimum d'appels avant évaluation
    exponential_backoff: bool = True    # Backoff exponentiel
    max_backoff: float = 300.0          # Backoff maximum (secondes)

@dataclass
class CallResult:
    """Résultat d'un appel"""
    timestamp: datetime
    duration: float
    success: bool
    failure_type: Optional[FailureType] = None
    error_message: Optional[str] = None
    response_data: Optional[Any] = None

@dataclass
class CircuitMetrics:
    """Métriques du circuit breaker"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    timeouts: int = 0
    slow_calls: int = 0
    current_failure_rate: float = 0.0
    average_response_time: float = 0.0
    state_transitions: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None

class CircuitBreakerException(Exception):
    """Exception levée quand le circuit est ouvert"""
    
    def __init__(self, circuit_name: str, state: CircuitState, message: str = None):
        self.circuit_name = circuit_name
        self.state = state
        self.message = message or f"Circuit breaker '{circuit_name}' is {state.value}"
        super().__init__(self.message)

class MLServiceCircuitBreaker:
    """Circuit breaker spécialisé pour services ML"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.metrics = CircuitMetrics()
        self.call_history: List[CallResult] = []
        self.last_failure_time = None
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.state_change_time = datetime.now()
        self.lock = threading.RLock()
        self.listeners: List[Callable] = []
        
        # Backoff exponentiel
        self.backoff_multiplier = 1.0
        self.current_timeout = config.recovery_timeout
        
        logger.info(f"Circuit breaker '{name}' initialisé en état {self.state.value}")
    
    def add_listener(self, listener: Callable[[str, CircuitState, CircuitState], None]):
        """Ajoute un listener pour les changements d'état"""
        self.listeners.append(listener)
    
    def _notify_listeners(self, old_state: CircuitState, new_state: CircuitState):
        """Notifie les listeners du changement d'état"""
        for listener in self.listeners:
            try:
                listener(self.name, old_state, new_state)
            except Exception as e:
                logger.error(f"Erreur listener circuit breaker: {e}")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Exécute un appel à travers le circuit breaker
        
        Args:
            func: Fonction à appeler
            *args: Arguments positionnels
            **kwargs: Arguments nommés
            
        Returns:
            Résultat de l'appel
            
        Raises:
            CircuitBreakerException: Si le circuit est ouvert
        """
        with self.lock:
            # Vérification de l'état du circuit
            if self.state == CircuitState.OPEN:
                if not self._should_attempt_reset():
                    self._record_blocked_call()
                    raise CircuitBreakerException(
                        self.name, 
                        self.state, 
                        f"Circuit ouvert, prochaine tentative dans {self._time_until_retry():.1f}s"
                    )
                else:
                    # Transition vers half-open
                    self._transition_to_half_open()
            
            elif self.state == CircuitState.HALF_OPEN:
                # En half-open, on limite le nombre d'appels simultanés
                if self.consecutive_successes >= self.config.success_threshold:
                    self._transition_to_closed()
        
        # Exécution de l'appel avec mesure des performances
        start_time = time.time()
        call_result = None
        
        try:
            # Exécution avec timeout
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs), 
                    timeout=self.config.timeout
                )
            else:
                # Pour les fonctions synchrones
                result = func(*args, **kwargs)
            
            duration = time.time() - start_time
            
            # Enregistrement du succès
            call_result = CallResult(
                timestamp=datetime.now(),
                duration=duration,
                success=True,
                response_data=result
            )
            
            self._record_success(call_result)
            return result
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            call_result = CallResult(
                timestamp=datetime.now(),
                duration=duration,
                success=False,
                failure_type=FailureType.TIMEOUT,
                error_message="Timeout dépassé"
            )
            self._record_failure(call_result)
            raise
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Classification de l'erreur
            failure_type = self._classify_error(e)
            
            call_result = CallResult(
                timestamp=datetime.now(),
                duration=duration,
                success=False,
                failure_type=failure_type,
                error_message=str(e)
            )
            
            self._record_failure(call_result)
            raise
    
    def _classify_error(self, error: Exception) -> FailureType:
        """Classifie le type d'erreur"""
        
        error_str = str(error).lower()
        
        if "timeout" in error_str or "timed out" in error_str:
            return FailureType.TIMEOUT
        elif "memory" in error_str or "out of memory" in error_str:
            return FailureType.RESOURCE_EXHAUSTION
        elif "connection" in error_str or "network" in error_str:
            return FailureType.HTTP_ERROR
        else:
            return FailureType.EXCEPTION
    
    def _record_success(self, call_result: CallResult):
        """Enregistre un appel réussi"""
        with self.lock:
            self.call_history.append(call_result)
            self._cleanup_old_calls()
            
            self.metrics.total_calls += 1
            self.metrics.successful_calls += 1
            self.metrics.last_success_time = call_result.timestamp
            
            # Vérification des appels lents
            if call_result.duration > self.config.slow_call_threshold:
                self.metrics.slow_calls += 1
            
            self.consecutive_failures = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.consecutive_successes += 1
                if self.consecutive_successes >= self.config.success_threshold:
                    self._transition_to_closed()
            
            self._update_metrics()
    
    def _record_failure(self, call_result: CallResult):
        """Enregistre un appel échoué"""
        with self.lock:
            self.call_history.append(call_result)
            self._cleanup_old_calls()
            
            self.metrics.total_calls += 1
            self.metrics.failed_calls += 1
            self.metrics.last_failure_time = call_result.timestamp
            
            if call_result.failure_type == FailureType.TIMEOUT:
                self.metrics.timeouts += 1
            
            self.consecutive_failures += 1
            self.consecutive_successes = 0
            self.last_failure_time = call_result.timestamp
            
            # Vérification des conditions d'ouverture
            if self.state == CircuitState.CLOSED:
                if self._should_open_circuit():
                    self._transition_to_open()
            elif self.state == CircuitState.HALF_OPEN:
                # Retour immédiat à l'état ouvert en cas d'échec en half-open
                self._transition_to_open()
            
            self._update_metrics()
    
    def _record_blocked_call(self):
        """Enregistre un appel bloqué par le circuit ouvert"""
        with self.lock:
            self.metrics.total_calls += 1
            self.metrics.failed_calls += 1
    
    def _should_open_circuit(self) -> bool:
        """Détermine si le circuit doit s'ouvrir"""
        
        # Vérification du nombre minimum d'appels
        if len(self.call_history) < self.config.min_calls_threshold:
            return False
        
        # Vérification du seuil d'échecs consécutifs
        if self.consecutive_failures >= self.config.failure_threshold:
            return True
        
        # Vérification du taux d'erreur dans la fenêtre
        recent_calls = self.call_history[-self.config.window_size:]
        if len(recent_calls) >= self.config.min_calls_threshold:
            failure_rate = (
                sum(1 for call in recent_calls if not call.success) / 
                len(recent_calls) * 100
            )
            
            if failure_rate >= self.config.error_rate_threshold:
                return True
        
        return False
    
    def _should_attempt_reset(self) -> bool:
        """Détermine si on peut tenter une réinitialisation"""
        if self.last_failure_time is None:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.current_timeout
    
    def _time_until_retry(self) -> float:
        """Calcule le temps restant avant la prochaine tentative"""
        if self.last_failure_time is None:
            return 0.0
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return max(0, self.current_timeout - elapsed)
    
    def _transition_to_open(self):
        """Transition vers l'état ouvert"""
        old_state = self.state
        self.state = CircuitState.OPEN
        self.state_change_time = datetime.now()
        self.metrics.state_transitions += 1
        
        # Backoff exponentiel
        if self.config.exponential_backoff:
            self.backoff_multiplier = min(
                self.backoff_multiplier * 2, 
                self.config.max_backoff / self.config.recovery_timeout
            )
            self.current_timeout = min(
                self.config.recovery_timeout * self.backoff_multiplier,
                self.config.max_backoff
            )
        
        logger.warning(f"Circuit breaker '{self.name}' OUVERT (timeout: {self.current_timeout:.1f}s)")
        self._notify_listeners(old_state, self.state)
    
    def _transition_to_half_open(self):
        """Transition vers l'état semi-ouvert"""
        old_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.state_change_time = datetime.now()
        self.consecutive_successes = 0
        self.metrics.state_transitions += 1
        
        logger.info(f"Circuit breaker '{self.name}' SEMI-OUVERT")
        self._notify_listeners(old_state, self.state)
    
    def _transition_to_closed(self):
        """Transition vers l'état fermé"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.state_change_time = datetime.now()
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.metrics.state_transitions += 1
        
        # Réinitialisation du backoff
        self.backoff_multiplier = 1.0
        self.current_timeout = self.config.recovery_timeout
        
        logger.info(f"Circuit breaker '{self.name}' FERMÉ")
        self._notify_listeners(old_state, self.state)
    
    def _cleanup_old_calls(self):
        """Nettoie les anciens appels pour maintenir la fenêtre glissante"""
        if len(self.call_history) > self.config.window_size * 2:
            self.call_history = self.call_history[-self.config.window_size:]
    
    def _update_metrics(self):
        """Met à jour les métriques calculées"""
        if not self.call_history:
            return
        
        recent_calls = self.call_history[-self.config.window_size:]
        
        # Taux d'erreur
        if recent_calls:
            failed_calls = sum(1 for call in recent_calls if not call.success)
            self.metrics.current_failure_rate = (failed_calls / len(recent_calls)) * 100
        
        # Temps de réponse moyen
        successful_calls = [call for call in recent_calls if call.success]
        if successful_calls:
            self.metrics.average_response_time = statistics.mean(
                call.duration for call in successful_calls
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques du circuit breaker"""
        with self.lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'total_calls': self.metrics.total_calls,
                'successful_calls': self.metrics.successful_calls,
                'failed_calls': self.metrics.failed_calls,
                'success_rate': (
                    (self.metrics.successful_calls / self.metrics.total_calls * 100) 
                    if self.metrics.total_calls > 0 else 0
                ),
                'current_failure_rate': self.metrics.current_failure_rate,
                'average_response_time': self.metrics.average_response_time,
                'timeouts': self.metrics.timeouts,
                'slow_calls': self.metrics.slow_calls,
                'consecutive_failures': self.consecutive_failures,
                'consecutive_successes': self.consecutive_successes,
                'state_transitions': self.metrics.state_transitions,
                'time_in_current_state': (datetime.now() - self.state_change_time).total_seconds(),
                'time_until_retry': self._time_until_retry() if self.state == CircuitState.OPEN else 0,
                'last_failure_time': self.metrics.last_failure_time.isoformat() if self.metrics.last_failure_time else None,
                'last_success_time': self.metrics.last_success_time.isoformat() if self.metrics.last_success_time else None,
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'recovery_timeout': self.config.recovery_timeout,
                    'success_threshold': self.config.success_threshold,
                    'timeout': self.config.timeout,
                    'window_size': self.config.window_size,
                    'error_rate_threshold': self.config.error_rate_threshold
                }
            }
    
    def force_open(self):
        """Force l'ouverture du circuit (pour maintenance)"""
        with self.lock:
            if self.state != CircuitState.OPEN:
                self._transition_to_open()
    
    def force_closed(self):
        """Force la fermeture du circuit (pour réinitialisation manuelle)"""
        with self.lock:
            if self.state != CircuitState.CLOSED:
                self._transition_to_closed()
    
    def reset(self):
        """Réinitialise le circuit breaker"""
        with self.lock:
            old_state = self.state
            self.state = CircuitState.CLOSED
            self.metrics = CircuitMetrics()
            self.call_history.clear()
            self.consecutive_failures = 0
            self.consecutive_successes = 0
            self.last_failure_time = None
            self.backoff_multiplier = 1.0
            self.current_timeout = self.config.recovery_timeout
            self.state_change_time = datetime.now()
            
            logger.info(f"Circuit breaker '{self.name}' réinitialisé")
            if old_state != CircuitState.CLOSED:
                self._notify_listeners(old_state, self.state)

class CircuitBreakerRegistry:
    """Registry pour gérer plusieurs circuit breakers"""
    
    def __init__(self):
        self._breakers: Dict[str, MLServiceCircuitBreaker] = {}
        self._global_metrics = {
            'total_breakers': 0,
            'open_breakers': 0,
            'half_open_breakers': 0,
            'closed_breakers': 0,
            'total_calls': 0,
            'total_failures': 0
        }
        self.lock = threading.RLock()
    
    def create_breaker(
        self, 
        name: str, 
        config: Optional[CircuitBreakerConfig] = None
    ) -> MLServiceCircuitBreaker:
        """Crée et enregistre un nouveau circuit breaker"""
        
        with self.lock:
            if name in self._breakers:
                raise ValueError(f"Circuit breaker '{name}' existe déjà")
            
            config = config or CircuitBreakerConfig()
            breaker = MLServiceCircuitBreaker(name, config)
            
            # Ajout d'un listener pour les métriques globales
            breaker.add_listener(self._on_state_change)
            
            self._breakers[name] = breaker
            self._global_metrics['total_breakers'] += 1
            self._global_metrics['closed_breakers'] += 1
            
            logger.info(f"Circuit breaker '{name}' créé et enregistré")
            return breaker
    
    def get_breaker(self, name: str) -> Optional[MLServiceCircuitBreaker]:
        """Récupère un circuit breaker par nom"""
        return self._breakers.get(name)
    
    def remove_breaker(self, name: str) -> bool:
        """Supprime un circuit breaker"""
        with self.lock:
            if name in self._breakers:
                del self._breakers[name]
                self._global_metrics['total_breakers'] -= 1
                logger.info(f"Circuit breaker '{name}' supprimé")
                return True
            return False
    
    def _on_state_change(self, name: str, old_state: CircuitState, new_state: CircuitState):
        """Gestionnaire de changement d'état pour les métriques globales"""
        with self.lock:
            # Décrémenter l'ancien état
            if old_state == CircuitState.OPEN:
                self._global_metrics['open_breakers'] -= 1
            elif old_state == CircuitState.HALF_OPEN:
                self._global_metrics['half_open_breakers'] -= 1
            elif old_state == CircuitState.CLOSED:
                self._global_metrics['closed_breakers'] -= 1
            
            # Incrémenter le nouvel état
            if new_state == CircuitState.OPEN:
                self._global_metrics['open_breakers'] += 1
            elif new_state == CircuitState.HALF_OPEN:
                self._global_metrics['half_open_breakers'] += 1
            elif new_state == CircuitState.CLOSED:
                self._global_metrics['closed_breakers'] += 1
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de tous les circuit breakers"""
        with self.lock:
            breaker_metrics = {}
            total_calls = 0
            total_failures = 0
            
            for name, breaker in self._breakers.items():
                metrics = breaker.get_metrics()
                breaker_metrics[name] = metrics
                total_calls += metrics['total_calls']
                total_failures += metrics['failed_calls']
            
            self._global_metrics['total_calls'] = total_calls
            self._global_metrics['total_failures'] = total_failures
            
            return {
                'global_metrics': self._global_metrics.copy(),
                'breakers': breaker_metrics,
                'summary': {
                    'total_breakers': len(self._breakers),
                    'healthy_breakers': self._global_metrics['closed_breakers'],
                    'at_risk_breakers': self._global_metrics['half_open_breakers'],
                    'failed_breakers': self._global_metrics['open_breakers'],
                    'overall_success_rate': (
                        ((total_calls - total_failures) / total_calls * 100) 
                        if total_calls > 0 else 100
                    )
                }
            }
    
    def reset_all(self):
        """Réinitialise tous les circuit breakers"""
        with self.lock:
            for breaker in self._breakers.values():
                breaker.reset()
            
            # Réinitialisation des métriques globales
            self._global_metrics.update({
                'open_breakers': 0,
                'half_open_breakers': 0,
                'closed_breakers': len(self._breakers),
                'total_calls': 0,
                'total_failures': 0
            })
            
            logger.info("Tous les circuit breakers ont été réinitialisés")
    
    def get_unhealthy_breakers(self) -> List[str]:
        """Récupère la liste des circuit breakers non sains"""
        with self.lock:
            unhealthy = []
            for name, breaker in self._breakers.items():
                if breaker.state in [CircuitState.OPEN, CircuitState.HALF_OPEN]:
                    unhealthy.append(name)
            return unhealthy

# Registry global
_global_registry = CircuitBreakerRegistry()

def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    timeout: float = 10.0,
    config: Optional[CircuitBreakerConfig] = None
):
    """
    Décorateur pour ajouter un circuit breaker à une fonction
    
    Args:
        name: Nom du circuit breaker
        failure_threshold: Seuil d'échecs avant ouverture
        recovery_timeout: Timeout avant tentative de récupération
        timeout: Timeout des appels
        config: Configuration personnalisée complète
    """
    
    def decorator(func):
        # Création ou récupération du circuit breaker
        breaker = _global_registry.get_breaker(name)
        if breaker is None:
            breaker_config = config or CircuitBreakerConfig(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                timeout=timeout
            )
            breaker = _global_registry.create_breaker(name, breaker_config)
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await breaker.call(func, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return asyncio.run(breaker.call(func, *args, **kwargs))
            return sync_wrapper
    
    return decorator

def get_circuit_breaker(name: str) -> Optional[MLServiceCircuitBreaker]:
    """Récupère un circuit breaker par nom"""
    return _global_registry.get_breaker(name)

def get_all_circuit_breakers() -> Dict[str, Any]:
    """Récupère tous les circuit breakers et leurs métriques"""
    return _global_registry.get_all_metrics()

def reset_all_circuit_breakers():
    """Réinitialise tous les circuit breakers"""
    _global_registry.reset_all()

# Exemples d'utilisation avec services ML spécifiques
class MLServiceClient:
    """Client pour service ML avec circuit breaker intégré"""
    
    def __init__(self, service_name: str, base_url: str):
        self.service_name = service_name
        self.base_url = base_url
        
        # Configuration spécialisée pour services ML
        ml_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            success_threshold=2,
            timeout=15.0,
            window_size=20,
            slow_call_threshold=10.0,
            error_rate_threshold=30.0,
            min_calls_threshold=5,
            exponential_backoff=True,
            max_backoff=300.0
        )
        
        self.circuit_breaker = _global_registry.create_breaker(
            f"ml_service_{service_name}",
            ml_config
        )
    
    async def predict(self, input_data: Any) -> Any:
        """Appel de prédiction avec circuit breaker"""
        return await self.circuit_breaker.call(self._do_predict, input_data)
    
    async def _do_predict(self, input_data: Any) -> Any:
        """Implémentation réelle de la prédiction"""
        # Simulation d'un appel HTTP à un service ML
        await asyncio.sleep(random.uniform(0.1, 2.0))
        
        # Simulation d'échecs occasionnels
        if random.random() < 0.1:  # 10% d'échecs
            raise Exception("Erreur de prédiction ML")
        
        return {"prediction": f"result_for_{input_data}"}
    
    async def health_check(self) -> bool:
        """Vérification de santé avec circuit breaker"""
        try:
            await self.circuit_breaker.call(self._do_health_check)
            return True
        except Exception:
            return False
    
    async def _do_health_check(self):
        """Implémentation réelle du health check"""
        await asyncio.sleep(0.1)
        if random.random() < 0.05:  # 5% d'échecs
            raise Exception("Service indisponible")

# Exemple d'utilisation
async def main():
    """Exemple d'utilisation du circuit breaker pour services ML"""
    
    # Création d'un client ML avec circuit breaker
    ml_client = MLServiceClient("recommendation_engine", "http://ml-service:8080")
    
    # Utilisation du décorateur
    @circuit_breaker(
        name="data_preprocessing",
        failure_threshold=3,
        recovery_timeout=30.0,
        timeout=5.0
    )
    async def preprocess_data(data):
        """Service de préprocessing avec circuit breaker"""
        await asyncio.sleep(random.uniform(0.1, 1.0))
        if random.random() < 0.15:  # 15% d'échecs
            raise Exception("Erreur de préprocessing")
        return f"processed_{data}"
    
    try:
        # Tests de fonctionnement normal
        print("=== Tests de fonctionnement normal ===")
        
        for i in range(5):
            try:
                result = await ml_client.predict(f"data_{i}")
                print(f"Prédiction {i}: {result}")
                
                processed = await preprocess_data(f"raw_data_{i}")
                print(f"Preprocessing {i}: {processed}")
                
            except CircuitBreakerException as e:
                print(f"Circuit breaker ouvert: {e}")
            except Exception as e:
                print(f"Erreur: {e}")
            
            await asyncio.sleep(0.5)
        
        # Affichage des métriques
        print("\n=== Métriques des circuit breakers ===")
        all_metrics = get_all_circuit_breakers()
        print(json.dumps(all_metrics, indent=2, default=str))
        
        # Simulation de surcharge pour déclencher l'ouverture
        print("\n=== Test de surcharge ===")
        
        for i in range(10):
            try:
                # Appels rapides pour déclencher des échecs
                result = await ml_client.predict(f"stress_data_{i}")
            except Exception as e:
                print(f"Échec {i}: {type(e).__name__}")
            
            await asyncio.sleep(0.1)
        
        # Métriques après stress test
        print("\n=== Métriques après stress test ===")
        final_metrics = get_all_circuit_breakers()
        print(json.dumps(final_metrics['summary'], indent=2))
        
        # Test de récupération
        print("\n=== Test de récupération ===")
        print("Attente de la récupération...")
        await asyncio.sleep(35)  # Attendre le recovery timeout
        
        try:
            result = await ml_client.predict("recovery_test")
            print(f"Récupération réussie: {result}")
        except Exception as e:
            print(f"Récupération échouée: {e}")
        
    except KeyboardInterrupt:
        print("\nArrêt du test")

if __name__ == "__main__":
    asyncio.run(main())