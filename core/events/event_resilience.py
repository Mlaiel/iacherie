"""IA-Influencer-Agent - Event Circuit Breaker and Resilience System
Module: backend/core/events/event_resilience.py
Architecture: Advanced Resilience and Fault Tolerance for Event Processing
Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
INTERDIT : Copie, reproduction, modification, ou usage sans autorisation écrite explicite.
Toute violation sera poursuivie selon la loi allemande et française.
Contact autorisations : mlaiel@live.de

Description:
    Système avancé de résilience pour les événements incluant circuit breakers,
    bulkheads, timeout gestion, retry avec backoff, et recovery automatique.
    Garantit la stabilité de la plateforme IA-Influencer-Agent.
"""

from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import logging
import time
import statistics
from collections import deque, defaultdict
import uuid

from .event_bus import Event, EventBus, EventPriority, EventStatus

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """États du circuit breaker"""

    CLOSED = "closed"      # Circuit fermé, tout fonctionne
    OPEN = "open"          # Circuit ouvert, bloque les appels
    HALF_OPEN = "half_open"  # Test de récupération


class BulkheadState(Enum):
    """États des bulkheads"""

    AVAILABLE = "available"
    SATURATED = "saturated"
    OVERLOADED = "overloaded"


class RetryPolicy(Enum):
    """Politiques de retry"""

    NONE = "none"
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    CUSTOM = "custom"


class FailureType(Enum):
    """Types d'échecs"""

    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"
    CUSTOM = "custom"


@dataclass
class CircuitBreakerConfig:
    """Configuration du circuit breaker"""
    failure_threshold: int = 5  # Nombre d'échecs avant ouverture
    success_threshold: int = 3  # Nombre de succès pour fermer en half-open
    timeout: timedelta = timedelta(seconds=60)  # Délai avant half-open
    window_size: int = 100  # Taille de la fenêtre glissante
    minimum_calls: int = 10  # Minimum d'appels avant évaluation
    failure_rate_threshold: float = 50.0  # Seuil de taux d'échec (%)
    slow_call_threshold: timedelta = timedelta(seconds=5)  # Seuil d'appel lent
    slow_call_rate_threshold: float = 50.0  # Seuil de taux d'appels lents (%)


@dataclass
class BulkheadConfig:
    """
Configuration du bulkhead"""
    max_concurrent_calls: int = 100
    max_wait_duration: timedelta = timedelta(seconds=30)
    queue_capacity: int = 1000
    isolation_groups: List[str] = field(default_factory=list)


@dataclass
class RetryConfig:
    """
Configuration des retries"""
    policy: RetryPolicy = RetryPolicy.EXPONENTIAL
    max_attempts: int = 3
    base_delay: timedelta = timedelta(seconds=1)
    max_delay: timedelta = timedelta(seconds=60)
    backoff_multiplier: float = 2.0
    jitter: bool = True
    retryable_exceptions: List[str] = field(default_factory=list)
    retryable_failure_types: List[FailureType] = field(default_factory=list)


@dataclass
class TimeoutConfig:
    """
Configuration des timeouts"""
    call_timeout: timedelta = timedelta(seconds=30)
    total_timeout: timedelta = timedelta(minutes=5)
    connect_timeout: timedelta = timedelta(seconds=10)
    read_timeout: timedelta = timedelta(seconds=30)


@dataclass
class MetricsSnapshot:
    """
Snapshot des métriques"""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    slow_calls: int = 0
    average_response_time: float = 0.0
    failure_rate: float = 0.0
    slow_call_rate: float = 0.0


class CircuitBreaker:
    """
Circuit breaker pour protection contre les cascades d'échecs"""
    
    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig,
        fallback: Optional[Callable] = None
    ):
        self.name = name
        self.config = config
        self.fallback = fallback
        
        self.state = CircuitState.CLOSED
        self.last_failure_time: Optional[datetime] = None
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        
        # Fenêtre glissante pour les métriques
        self.call_results = deque(maxlen=config.window_size)
        self.response_times = deque(maxlen=config.window_size)
        
        # Statistiques
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.slow_calls = 0
        
        # Lock pour thread safety
        self._lock = asyncio.Lock()
        
        logger.info("CircuitBreaker '%s' initialized", name)
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Exécute une fonction protégée par le circuit breaker"""
        async with self._lock:
            # Vérification de l'état du circuit
            await self._update_state()
            
            if self.state == CircuitState.OPEN:
                if self.fallback:
                    logger.warning("Circuit '%s' is OPEN, using fallback", self.name)
                    return await self._execute_fallback(*args, **kwargs)
                else:
                    raise CircuitBreakerOpenError(f"Circuit {self.name} is OPEN")
            
            # Exécution de l'appel
            start_time = time.time()
            self.total_calls += 1
            
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Succès
                end_time = time.time()
                response_time = end_time - start_time
                
                await self._record_success(response_time)
                return result
                
            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                
                await self._record_failure(e, response_time)
                raise
    
    async def _update_state(self):
        """Met à jour l'état du circuit"""
        now = datetime.now(timezone.utc)
        
        if self.state == CircuitState.OPEN:
            # Vérification si on peut passer en half-open
            if (self.last_failure_time and 
                now - self.last_failure_time >= self.config.timeout):
                self.state = CircuitState.HALF_OPEN
                self.consecutive_successes = 0
                logger.info("Circuit '%s' state changed to HALF_OPEN", self.name)
        
        elif self.state == CircuitState.HALF_OPEN:
            # En half-open, on teste la récupération
            if self.consecutive_successes >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.consecutive_failures = 0
                logger.info("Circuit '%s' state changed to CLOSED", self.name)
        
        elif self.state == CircuitState.CLOSED:
            # Vérification des conditions d'ouverture
            if len(self.call_results) >= self.config.minimum_calls:
                failure_rate = self._calculate_failure_rate()
                slow_call_rate = self._calculate_slow_call_rate()
                
                should_open = (
                    self.consecutive_failures >= self.config.failure_threshold or
                    failure_rate >= self.config.failure_rate_threshold or
                    slow_call_rate >= self.config.slow_call_rate_threshold
                )
                
                if should_open:
                    self.state = CircuitState.OPEN
                    self.last_failure_time = now
                    logger.warning("Circuit '%s' state changed to OPEN", self.name)
    
    async def _record_success(self, response_time: float):
        """Enregistre un succès"""
        self.successful_calls += 1
        self.consecutive_failures = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.consecutive_successes += 1
        
        # Vérification d'appel lent
        is_slow = response_time >= self.config.slow_call_threshold.total_seconds()
        if is_slow:
            self.slow_calls += 1
        
        self.call_results.append(True)
        self.response_times.append(response_time)
    
    async def _record_failure(self, exception: Exception, response_time: float):
        """
Enregistre un échec"""
        self.failed_calls += 1
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        
        self.call_results.append(False)
        self.response_times.append(response_time)
    
    async def _execute_fallback(self, *args, **kwargs) -> Any:
        """
Exécute la fonction de fallback"""
        if asyncio.iscoroutinefunction(self.fallback):
            return await self.fallback(*args, **kwargs)
        else:
            return self.fallback(*args, **kwargs)
    
    def _calculate_failure_rate(self) -> float:
        """
Calcule le taux d'échec"""
        if not self.call_results:
            return 0.0
        
        failures = sum(1 for result in self.call_results if not result)
        return (failures / len(self.call_results)) * 100.0
    
    def _calculate_slow_call_rate(self) -> float:
        """
Calcule le taux d'appels lents"""
        if not self.response_times:
            return 0.0
        
        threshold = self.config.slow_call_threshold.total_seconds()
        slow_calls = sum(1 for time in self.response_times if time >= threshold)
        return (slow_calls / len(self.response_times)) * 100.0
    
    def get_metrics(self) -> MetricsSnapshot:
        """
Retourne les métriques actuelles"""
        return MetricsSnapshot(
            total_calls=self.total_calls,
            successful_calls=self.successful_calls,
            failed_calls=self.failed_calls,
            slow_calls=self.slow_calls,
            average_response_time=statistics.mean(self.response_times) if self.response_times else 0.0,
            failure_rate=self._calculate_failure_rate(),
            slow_call_rate=self._calculate_slow_call_rate()
        )
    
    def reset(self):
        """
Remet le circuit à zéro"""
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.last_failure_time = None
        self.call_results.clear()
        self.response_times.clear()
        logger.info("Circuit '%s' has been reset", self.name)


class Bulkhead:
    """Bulkhead pour isolation des ressources"""
    
    def __init__(self, name: str, config: BulkheadConfig):
        self.name = name
        self.config = config
        
        self.semaphore = asyncio.Semaphore(config.max_concurrent_calls)
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=config.queue_capacity)
        self.active_calls = 0
        self.total_calls = 0
        self.rejected_calls = 0
        self.queued_calls = 0
        
        self._lock = asyncio.Lock()
        
        logger.info("Bulkhead '%s' initialized with %d max concurrent calls", 
                   name, config.max_concurrent_calls)
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Exécute une fonction dans le bulkhead"""
        self.total_calls += 1
        
        try:
            # Tentative d'acquisition du semaphore avec timeout
            acquired = await asyncio.wait_for(
                self.semaphore.acquire(),
                timeout=self.config.max_wait_duration.total_seconds()
            )
            
            if not acquired:
                self.rejected_calls += 1
                raise BulkheadCapacityError(f"Bulkhead {self.name} capacity exceeded")
            
            try:
                async with self._lock:
                    self.active_calls += 1
                
                # Exécution de la fonction
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                return result
                
            finally:
                async with self._lock:
                    self.active_calls -= 1
                self.semaphore.release()
                
        except asyncio.TimeoutError:
            self.rejected_calls += 1
            raise BulkheadTimeoutError(f"Bulkhead {self.name} timeout waiting for capacity")
    
    def get_state(self) -> BulkheadState:
        """Retourne l'état du bulkhead"""
        utilization = self.active_calls / self.config.max_concurrent_calls
        
        if utilization >= 0.9:
            return BulkheadState.OVERLOADED
        elif utilization >= 0.7:
            return BulkheadState.SATURATED
        else:
            return BulkheadState.AVAILABLE
    
    def get_metrics(self) -> Dict[str, Any]:
        """
Retourne les métriques du bulkhead"""
        return {
            "name": self.name,
            "state": self.get_state().value,
            "active_calls": self.active_calls,
            "max_concurrent_calls": self.config.max_concurrent_calls,
            "utilization": self.active_calls / self.config.max_concurrent_calls,
            "total_calls": self.total_calls,
            "rejected_calls": self.rejected_calls,
            "queued_calls": self.queued_calls,
            "available_permits": self.semaphore._value
        }


class RetryManager:
    """Gestionnaire de retry avec différentes politiques"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
Exécute une fonction avec retry"""
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Vérification si l'exception est retryable
                if not self._is_retryable_exception(e):
                    raise e
                
                # Dernier essai, on propage l'exception
                if attempt == self.config.max_attempts - 1:
                    break
                
                # Calcul du délai
                delay = self._calculate_delay(attempt)
                logger.warning("Retry attempt %d/%d after %s seconds for function %s: %s",
                             attempt + 1, self.config.max_attempts, delay, 
                             func.__name__, str(e))
                
                await asyncio.sleep(delay)
        
        # Toutes les tentatives ont échoué
        raise last_exception
    
    def _is_retryable_exception(self, exception: Exception) -> bool:
        """Vérifie si une exception est retryable"""
        if not self.config.retryable_exceptions:
            return True  # Par défaut, toutes les exceptions sont retryables
        
        exception_name = type(exception).__name__
        return exception_name in self.config.retryable_exceptions
    
    def _calculate_delay(self, attempt: int) -> float:
        """
Calcule le délai pour le retry"""
        base_delay = self.config.base_delay.total_seconds()
        
        if self.config.policy == RetryPolicy.FIXED:
            delay = base_delay
        elif self.config.policy == RetryPolicy.LINEAR:
            delay = base_delay * (attempt + 1)
        elif self.config.policy == RetryPolicy.EXPONENTIAL:
            delay = base_delay * (self.config.backoff_multiplier ** attempt)
        else:
            delay = base_delay
        
        # Application du maximum
        delay = min(delay, self.config.max_delay.total_seconds())
        
        # Application du jitter
        if self.config.jitter:
            import random
            jitter = random.uniform(0.1, 0.2) * delay
            delay += jitter
        
        return delay


class TimeoutManager:
    """
Gestionnaire de timeouts"""
    
    def __init__(self, config: TimeoutConfig):
        self.config = config
    
    async def execute_with_timeout(
        self,
        func: Callable,
        timeout: Optional[timedelta] = None,
        *args,
        **kwargs
    ) -> Any:
        """
Exécute une fonction avec timeout"""
        timeout_seconds = (timeout or self.config.call_timeout).total_seconds()
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
            else:
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, func, *args, **kwargs),
                    timeout=timeout_seconds
                )
            
            return result
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Function {func.__name__} timed out after {timeout_seconds} seconds")


class ResilienceDecorator:
    """Décorateur combinant toutes les stratégies de résilience"""
    
    def __init__(
        self,
        circuit_breaker: Optional[CircuitBreaker] = None,
        bulkhead: Optional[Bulkhead] = None,
        retry_manager: Optional[RetryManager] = None,
        timeout_manager: Optional[TimeoutManager] = None,
        fallback: Optional[Callable] = None
    ):
        self.circuit_breaker = circuit_breaker
        self.bulkhead = bulkhead
        self.retry_manager = retry_manager
        self.timeout_manager = timeout_manager
        self.fallback = fallback
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
Exécute une fonction avec toutes les protections"""
        
        # Fonction wrapper qui combine toutes les protections
        async def protected_execution():
            async def timeout_wrapper():
                if self.timeout_manager:
                    return await self.timeout_manager.execute_with_timeout(func, None, *args, **kwargs)
                else:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
            
            if self.bulkhead:
                return await self.bulkhead.execute(timeout_wrapper)
            else:
                return await timeout_wrapper()
        
        # Application du circuit breaker
        if self.circuit_breaker:
            try:
                if self.retry_manager:
                    return await self.retry_manager.execute_with_retry(
                        self.circuit_breaker.call, protected_execution
                    )
                else:
                    return await self.circuit_breaker.call(protected_execution)
            except Exception as e:
                if self.fallback:
                    logger.warning("All resilience strategies failed, using fallback: %s", str(e))
                    if asyncio.iscoroutinefunction(self.fallback):
                        return await self.fallback(*args, **kwargs)
                    else:
                        return self.fallback(*args, **kwargs)
                else:
                    raise
        else:
            # Pas de circuit breaker, application directe du retry
            if self.retry_manager:
                return await self.retry_manager.execute_with_retry(protected_execution)
            else:
                return await protected_execution()


class EventResilienceManager:
    """Gestionnaire de résilience pour les événements"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
        # Registres des composants de résilience
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.bulkheads: Dict[str, Bulkhead] = {}
        self.retry_managers: Dict[str, RetryManager] = {}
        self.timeout_managers: Dict[str, TimeoutManager] = {}
        
        # Métriques globales
        self.global_stats = {
            "total_events_processed": 0,
            "failed_events": 0,
            "circuit_breaker_trips": 0,
            "bulkhead_rejections": 0,
            "retry_attempts": 0,
            "timeout_errors": 0,
            "fallback_executions": 0
        }
        
        # Configuration par défaut
        self.default_configs = {
            "circuit_breaker": CircuitBreakerConfig(),
            "bulkhead": BulkheadConfig(),
            "retry": RetryConfig(),
            "timeout": TimeoutConfig()
        }
        
        logger.info("EventResilienceManager initialized")
    
    def create_circuit_breaker(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        fallback: Optional[Callable] = None
    ) -> CircuitBreaker:
        """Crée un circuit breaker"""
        config = config or self.default_configs["circuit_breaker"]
        circuit_breaker = CircuitBreaker(name, config, fallback)
        self.circuit_breakers[name] = circuit_breaker
        return circuit_breaker
    
    def create_bulkhead(
        self,
        name: str,
        config: Optional[BulkheadConfig] = None
    ) -> Bulkhead:
        """Crée un bulkhead"""
        config = config or self.default_configs["bulkhead"]
        bulkhead = Bulkhead(name, config)
        self.bulkheads[name] = bulkhead
        return bulkhead
    
    def create_retry_manager(
        self,
        name: str,
        config: Optional[RetryConfig] = None
    ) -> RetryManager:
        """Crée un retry manager"""
        config = config or self.default_configs["retry"]
        retry_manager = RetryManager(config)
        self.retry_managers[name] = retry_manager
        return retry_manager
    
    def create_timeout_manager(
        self,
        name: str,
        config: Optional[TimeoutConfig] = None
    ) -> TimeoutManager:
        """Crée un timeout manager"""
        config = config or self.default_configs["timeout"]
        timeout_manager = TimeoutManager(config)
        self.timeout_managers[name] = timeout_manager
        return timeout_manager
    
    def create_resilient_handler(
        self,
        handler_name: str,
        circuit_breaker_name: Optional[str] = None,
        bulkhead_name: Optional[str] = None,
        retry_manager_name: Optional[str] = None,
        timeout_manager_name: Optional[str] = None,
        fallback: Optional[Callable] = None
    ) -> ResilienceDecorator:
        """Crée un handler résilient"""
        return ResilienceDecorator(
            circuit_breaker=self.circuit_breakers.get(circuit_breaker_name) if circuit_breaker_name else None,
            bulkhead=self.bulkheads.get(bulkhead_name) if bulkhead_name else None,
            retry_manager=self.retry_managers.get(retry_manager_name) if retry_manager_name else None,
            timeout_manager=self.timeout_managers.get(timeout_manager_name) if timeout_manager_name else None,
            fallback=fallback
        )
    
    async def execute_resilient_event_handler(
        self,
        event: Event,
        handler: Callable,
        resilience_config: Optional[Dict[str, str]] = None
    ) -> Any:
        """
Exécute un handler d'événement avec résilience"""
        self.global_stats["total_events_processed"] += 1
        
        try:
            # Configuration de résilience par défaut ou personnalisée
            config = resilience_config or {}
            
            # Création du décorateur de résilience
            decorator = self.create_resilient_handler(
                handler_name=f"event_handler_{event.type}",
                circuit_breaker_name=config.get("circuit_breaker"),
                bulkhead_name=config.get("bulkhead"),
                retry_manager_name=config.get("retry_manager"),
                timeout_manager_name=config.get("timeout_manager"),
                fallback=config.get("fallback")
            )
            
            # Exécution avec protection
            result = await decorator.execute(handler, event)
            return result
            
        except CircuitBreakerOpenError:
            self.global_stats["circuit_breaker_trips"] += 1
            raise
        except BulkheadCapacityError:
            self.global_stats["bulkhead_rejections"] += 1
            raise
        except TimeoutError:
            self.global_stats["timeout_errors"] += 1
            raise
        except Exception as e:
            self.global_stats["failed_events"] += 1
            logger.error("Resilient event handler failed for event %s: %s", event.id, str(e))
            raise
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retourne le statut de santé global"""
        circuit_breaker_status = {}
        for name, cb in self.circuit_breakers.items():
            metrics = cb.get_metrics()
            circuit_breaker_status[name] = {
                "state": cb.state.value,
                "failure_rate": metrics.failure_rate,
                "slow_call_rate": metrics.slow_call_rate,
                "total_calls": metrics.total_calls
            }
        
        bulkhead_status = {}
        for name, bh in self.bulkheads.items():
            bulkhead_status[name] = bh.get_metrics()
        
        return {
            "global_stats": self.global_stats.copy(),
            "circuit_breakers": circuit_breaker_status,
            "bulkheads": bulkhead_status,
            "components": {
                "circuit_breakers_count": len(self.circuit_breakers),
                "bulkheads_count": len(self.bulkheads),
                "retry_managers_count": len(self.retry_managers),
                "timeout_managers_count": len(self.timeout_managers)
            }
        }
    
    def reset_all_circuit_breakers(self):
        """Remet tous les circuit breakers à zéro"""
        for cb in self.circuit_breakers.values():
            cb.reset()
        logger.info("All circuit breakers have been reset")


# Exceptions personnalisées
class ResilienceError(Exception):
    """Exception de base pour les erreurs de résilience"""
    pass


class CircuitBreakerOpenError(ResilienceError):
    """
Exception levée quand le circuit breaker est ouvert"""
    pass


class BulkheadCapacityError(ResilienceError):
    """
Exception levée quand la capacité du bulkhead est dépassée"""
    pass


class BulkheadTimeoutError(ResilienceError):
    """
Exception levée quand le timeout du bulkhead est atteint"""
    pass


# Instance globale
event_resilience_manager: Optional[EventResilienceManager] = None


def initialize_resilience_manager(event_bus: EventBus) -> EventResilienceManager:
    """
Initialise le gestionnaire de résilience"""
    global event_resilience_manager
    
    if event_resilience_manager is None:
        event_resilience_manager = EventResilienceManager(event_bus)
        
        # Configuration des composants par défaut pour IA-Influencer-Agent
        
        # Circuit breakers pour les services critiques
        event_resilience_manager.create_circuit_breaker(
            "content_processing",
            CircuitBreakerConfig(failure_threshold=3, timeout=timedelta(seconds=30))
        )
        
        event_resilience_manager.create_circuit_breaker(
            "protection_service",
            CircuitBreakerConfig(failure_threshold=5, timeout=timedelta(minutes=1))
        )
        
        event_resilience_manager.create_circuit_breaker(
            "monetization_service",
            CircuitBreakerConfig(failure_threshold=3, timeout=timedelta(seconds=45))
        )
        
        # Bulkheads pour isolation des ressources
        event_resilience_manager.create_bulkhead(
            "fingerprinting",
            BulkheadConfig(max_concurrent_calls=50, queue_capacity=500)
        )
        
        event_resilience_manager.create_bulkhead(
            "api_calls",
            BulkheadConfig(max_concurrent_calls=100, queue_capacity=1000)
        )
        
        # Retry managers
        event_resilience_manager.create_retry_manager(
            "default",
            RetryConfig(max_attempts=3, base_delay=timedelta(seconds=1))
        )
        
        event_resilience_manager.create_retry_manager(
            "external_api",
            RetryConfig(max_attempts=5, base_delay=timedelta(seconds=2))
        )
        
        # Timeout managers
        event_resilience_manager.create_timeout_manager(
            "fast",
            TimeoutConfig(call_timeout=timedelta(seconds=10))
        )
        
        event_resilience_manager.create_timeout_manager(
            "slow",
            TimeoutConfig(call_timeout=timedelta(minutes=2))
        )
        
        logger.info("EventResilienceManager initialized with default configurations")
    
    return event_resilience_manager
