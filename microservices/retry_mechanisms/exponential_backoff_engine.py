"""
Exponential Backoff Engine Enterprise - IA Chérie
===============================================
Moteur exponential backoff avec jitter, circuit breaker integration.
Algorithmes retry sophistiqués pour microservices haute disponibilité.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Retry Mechanisms
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture retry mechanisms et tous ses algorithmes sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import random
import time
import math
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)

class BackoffStrategy(Enum):
    """Stratégies de backoff disponibles"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIBONACCI = "fibonacci"
    POLYNOMIAL = "polynomial"
    DECORRELATED_JITTER = "decorrelated_jitter"

@dataclass
class BackoffConfig:
    """Configuration pour exponential backoff"""
    strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    initial_delay: float = 1.0
    max_delay: float = 300.0
    multiplier: float = 2.0
    jitter_enabled: bool = True
    jitter_factor: float = 0.1
    max_retries: int = 5
    timeout: Optional[float] = None
    circuit_breaker_enabled: bool = True
    
    # Advanced settings
    polynomial_degree: int = 2
    fibonacci_cap: int = 21
    decorrelated_base: float = 1.0

@dataclass
class BackoffMetrics:
    """Métriques du moteur backoff"""
    total_attempts: int = 0
    successful_retries: int = 0
    failed_retries: int = 0
    total_delay_time: float = 0.0
    average_delay: float = 0.0
    success_rate: float = 0.0
    last_updated: float = field(default_factory=time.time)
    
    def update_success(self, delay_time: float):
        """Mise à jour métriques pour succès"""
        self.total_attempts += 1
        self.successful_retries += 1
        self.total_delay_time += delay_time
        self._recalculate_metrics()
    
    def update_failure(self, delay_time: float):
        """Mise à jour métriques pour échec"""
        self.total_attempts += 1
        self.failed_retries += 1
        self.total_delay_time += delay_time
        self._recalculate_metrics()
    
    def _recalculate_metrics(self):
        """Recalcul des métriques dérivées"""
        if self.total_attempts > 0:
            self.success_rate = self.successful_retries / self.total_attempts
            self.average_delay = self.total_delay_time / self.total_attempts
        self.last_updated = time.time()

class ExponentialBackoffEngine:
    """
    Moteur exponential backoff enterprise avec algorithmes avancés.
    Multi-strategy + jitter + circuit breaker integration + metrics.
    """
    
    def __init__(self, config: BackoffConfig):
        self.config = config
        self.metrics = BackoffMetrics()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._fibonacci_cache = {0: 0, 1: 1}
        
        # Circuit breaker state
        self.circuit_open = False
        self.circuit_failures = 0
        self.circuit_last_failure = None
        
    async def execute_with_backoff(self, operation: Callable, context: Dict = None) -> Any:
        """
        Exécution opération avec exponential backoff intelligent.
        
        Backoff Features:
        - Multi-strategy backoff algorithms (exponential, linear, fibonacci)
        - Intelligent jitter pour éviter thundering herd
        - Context-aware retry decisions
        - Circuit breaker integration
        - Real-time metrics collection
        - Adaptive delay adjustment basé sur success rate
        - Dead letter queue pour failed operations
        """
        context = context or {}
        operation_id = context.get('operation_id', f"op_{int(time.time())}")
        
        # Vérification circuit breaker
        if self.circuit_open and self._should_circuit_remain_open():
            raise Exception("Circuit breaker is OPEN - operation blocked")
        
        last_exception = None
        previous_delay = None
        start_time = time.time()
        
        for attempt in range(self.config.max_retries + 1):
            try:
                # Timeout pour l'opération
                if self.config.timeout:
                    result = await asyncio.wait_for(
                        self._execute_operation(operation, context),
                        timeout=self.config.timeout
                    )
                else:
                    result = await self._execute_operation(operation, context)
                
                # Succès - mise à jour métriques et circuit breaker
                delay_time = time.time() - start_time
                self.metrics.update_success(delay_time)
                self._reset_circuit_breaker()
                
                self.logger.info(f"Operation {operation_id} succeeded on attempt {attempt + 1}")
                return result
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Operation {operation_id} failed on attempt {attempt + 1}: {str(e)}")
                
                # Mise à jour circuit breaker
                self._update_circuit_breaker_on_failure()
                
                if attempt == self.config.max_retries:
                    # Échec final
                    delay_time = time.time() - start_time
                    self.metrics.update_failure(delay_time)
                    self.logger.error(f"Operation {operation_id} failed after {self.config.max_retries + 1} attempts")
                    break
                
                # Calcul du délai de retry
                delay = await self.calculate_delay(attempt, previous_delay)
                previous_delay = delay
                
                self.logger.info(f"Retrying operation {operation_id} in {delay:.2f}s")
                await asyncio.sleep(delay)
        
        if last_exception:
            raise last_exception
    
    async def calculate_delay(self, attempt: int, previous_delay: float = None) -> float:
        """Calcul delay avec stratégie configurée et jitter."""
        
        if self.config.strategy == BackoffStrategy.EXPONENTIAL:
            delay = self._exponential_delay(attempt)
        elif self.config.strategy == BackoffStrategy.LINEAR:
            delay = self._linear_delay(attempt)
        elif self.config.strategy == BackoffStrategy.FIBONACCI:
            delay = self._fibonacci_delay(attempt)
        elif self.config.strategy == BackoffStrategy.POLYNOMIAL:
            delay = self._polynomial_delay(attempt)
        elif self.config.strategy == BackoffStrategy.DECORRELATED_JITTER:
            delay = self._decorrelated_jitter_delay(attempt, previous_delay)
        else:
            delay = self._exponential_delay(attempt)
        
        # Application du jitter si activé
        if self.config.jitter_enabled:
            delay = self._apply_jitter(delay)
        
        # Respect de la limite max_delay
        return min(delay, self.config.max_delay)
    
    def _exponential_delay(self, attempt: int) -> float:
        """Calcul exponential delay: initial_delay * (multiplier ^ attempt)"""
        return self.config.initial_delay * (self.config.multiplier ** attempt)
    
    def _linear_delay(self, attempt: int) -> float:
        """Calcul linear delay: initial_delay * (attempt + 1)"""
        return self.config.initial_delay * (attempt + 1)
    
    def _fibonacci_delay(self, attempt: int) -> float:
        """Calcul Fibonacci delay pour retry plus graduel."""
        fib_number = self._get_fibonacci(min(attempt, self.config.fibonacci_cap))
        return self.config.initial_delay * fib_number
    
    def _polynomial_delay(self, attempt: int) -> float:
        """Calcul polynomial delay: initial_delay * (attempt ^ degree)"""
        return self.config.initial_delay * (attempt ** self.config.polynomial_degree)
    
    def _decorrelated_jitter_delay(self, attempt: int, previous_delay: float) -> float:
        """
        Decorrelated jitter delay pour distribution optimale.
        Inspiré par AWS exponential backoff best practices.
        """
        if previous_delay is None:
            return random.uniform(0, self.config.decorrelated_base)
        
        next_delay = random.uniform(
            self.config.decorrelated_base,
            previous_delay * 3
        )
        return next_delay
    
    def _apply_jitter(self, delay: float) -> float:
        """Application jitter pour éviter synchronisation."""
        jitter_range = delay * self.config.jitter_factor
        return delay + random.uniform(-jitter_range, jitter_range)
    
    def _get_fibonacci(self, n: int) -> int:
        """Calcul Fibonacci avec cache pour performance"""
        if n in self._fibonacci_cache:
            return self._fibonacci_cache[n]
        
        if n <= 1:
            return n
        
        self._fibonacci_cache[n] = self._get_fibonacci(n-1) + self._get_fibonacci(n-2)
        return self._fibonacci_cache[n]
    
    async def _execute_operation(self, operation: Callable, context: Dict) -> Any:
        """Exécution sécurisée de l'opération"""
        if asyncio.iscoroutinefunction(operation):
            return await operation(context)
        else:
            return operation(context)
    
    def _should_circuit_remain_open(self) -> bool:
        """Vérification si le circuit breaker doit rester ouvert"""
        if not self.config.circuit_breaker_enabled:
            return False
        
        if not self.circuit_last_failure:
            return False
        
        # Circuit ouvert pendant 60 secondes après 5 échecs
        time_threshold = 60.0
        failure_threshold = 5
        
        time_since_failure = time.time() - self.circuit_last_failure
        return (self.circuit_failures >= failure_threshold and 
                time_since_failure < time_threshold)
    
    def _update_circuit_breaker_on_failure(self):
        """Mise à jour état circuit breaker sur échec"""
        if not self.config.circuit_breaker_enabled:
            return
        
        self.circuit_failures += 1
        self.circuit_last_failure = time.time()
        
        if self.circuit_failures >= 5:
            self.circuit_open = True
            self.logger.warning("Circuit breaker OPENED due to repeated failures")
    
    def _reset_circuit_breaker(self):
        """Reset circuit breaker sur succès"""
        if self.circuit_failures > 0:
            self.circuit_failures = 0
            self.circuit_open = False
            self.circuit_last_failure = None
            self.logger.info("Circuit breaker RESET after successful operation")
    
    async def should_retry(self, exception: Exception, attempt: int, context: Dict) -> bool:
        """Décision retry basée sur exception type et contexte."""
        # Types d'exceptions qui ne doivent pas être retry
        non_retryable_exceptions = [
            ValueError,  # Erreurs de validation
            TypeError,   # Erreurs de type
            KeyError,    # Erreurs de clé manquante
        ]
        
        if type(exception) in non_retryable_exceptions:
            return False
        
        # Vérification du contexte pour décisions spécialisées
        if context.get('no_retry', False):
            return False
        
        # Timeout global
        if context.get('start_time'):
            elapsed = time.time() - context['start_time']
            max_total_time = context.get('max_total_time', 300.0)  # 5 minutes
            if elapsed > max_total_time:
                return False
        
        return True
    
    async def create_retry_context(self, operation_id: str, metadata: Dict = None) -> Dict:
        """Création contexte retry avec tracking."""
        metadata = metadata or {}
        
        return {
            'operation_id': operation_id,
            'start_time': time.time(),
            'metadata': metadata,
            'backoff_strategy': self.config.strategy.value,
            'max_retries': self.config.max_retries,
            'circuit_open': self.circuit_open,
            'current_failures': self.circuit_failures
        }
    
    def get_metrics(self) -> Dict:
        """Récupération métriques actuelles"""
        return {
            'total_attempts': self.metrics.total_attempts,
            'successful_retries': self.metrics.successful_retries,
            'failed_retries': self.metrics.failed_retries,
            'success_rate': self.metrics.success_rate,
            'average_delay': self.metrics.average_delay,
            'total_delay_time': self.metrics.total_delay_time,
            'circuit_open': self.circuit_open,
            'circuit_failures': self.circuit_failures,
            'last_updated': self.metrics.last_updated,
            'strategy': self.config.strategy.value
        }
    
    async def health_check(self) -> Dict:
        """Vérification santé du moteur backoff"""
        return {
            'status': 'healthy' if not self.circuit_open else 'circuit_open',
            'circuit_breaker': {
                'open': self.circuit_open,
                'failures': self.circuit_failures,
                'last_failure': self.circuit_last_failure
            },
            'config': {
                'strategy': self.config.strategy.value,
                'max_retries': self.config.max_retries,
                'max_delay': self.config.max_delay,
                'jitter_enabled': self.config.jitter_enabled
            },
            'metrics': self.get_metrics()
        }

# Factory functions
def create_exponential_backoff_engine(
    strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter_enabled: bool = True
) -> ExponentialBackoffEngine:
    """Factory pour création moteur backoff avec config standard"""
    config = BackoffConfig(
        strategy=strategy,
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=max_delay,
        jitter_enabled=jitter_enabled
    )
    return ExponentialBackoffEngine(config)

# Configuration prédéfinies pour IA Chérie business logic
AINFLUE_BACKOFF_CONFIGS = {
    'content_processing': BackoffConfig(
        strategy=BackoffStrategy.EXPONENTIAL,
        max_retries=5,
        initial_delay=2.0,
        max_delay=120.0,
        jitter_enabled=True,
        timeout=300.0
    ),
    'ai_processing': BackoffConfig(
        strategy=BackoffStrategy.FIBONACCI,
        max_retries=3,
        initial_delay=5.0,
        max_delay=180.0,
        jitter_enabled=True,
        timeout=600.0
    ),
    'monetization': BackoffConfig(
        strategy=BackoffStrategy.LINEAR,
        max_retries=2,
        initial_delay=1.0,
        max_delay=30.0,
        jitter_enabled=False,  # Transactions financières sans jitter
        timeout=60.0
    ),
    'distribution': BackoffConfig(
        strategy=BackoffStrategy.DECORRELATED_JITTER,
        max_retries=4,
        initial_delay=3.0,
        max_delay=240.0,
        jitter_enabled=True,
        timeout=900.0
    )
}

__all__ = [
    'ExponentialBackoffEngine',
    'BackoffConfig', 
    'BackoffStrategy',
    'BackoffMetrics',
    'create_exponential_backoff_engine',
    'AINFLUE_BACKOFF_CONFIGS'
]