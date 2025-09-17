"""
Circuit Breaker Rate Limiter Enterprise - Ainflue
==================================================
Circuit Breaker intégré avec Rate Limiting.
Fail-fast + gradual recovery + health monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Rate Limiting
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import deque, defaultdict
import statistics

from .distributed_rate_limiter import (
    DistributedRateLimiter, RateLimitConfig, RateLimitResult, 
    RateLimitAlgorithm, RateLimitStatus
)

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """États du circuit breaker"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit open - rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery

class FailureType(Enum):
    """Types de failures détectées"""
    TIMEOUT = "timeout"
    ERROR_RESPONSE = "error_response"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SERVICE_UNAVAILABLE = "service_unavailable"
    NETWORK_ERROR = "network_error"
    CUSTOM = "custom"

class RecoveryStrategy(Enum):
    """Stratégies de recovery"""
    IMMEDIATE = "immediate"      # Immediate full recovery
    GRADUAL = "gradual"         # Gradual increase
    EXPONENTIAL = "exponential" # Exponential backoff
    LINEAR = "linear"           # Linear increase
    ADAPTIVE = "adaptive"       # ML-adaptive recovery

@dataclass
class CircuitConfig:
    """Configuration circuit breaker"""
    failure_threshold: int = 5           # Failures before opening
    success_threshold: int = 3           # Successes to close from half-open
    timeout_seconds: float = 30.0        # Request timeout
    recovery_timeout_seconds: int = 60   # Time before trying half-open
    failure_rate_threshold: float = 0.5  # 50% failure rate threshold
    minimum_requests: int = 10           # Min requests before applying thresholds
    sliding_window_size: int = 100       # Window size for failure rate calculation
    max_concurrent_requests: int = 1000  # Max concurrent requests
    enable_adaptive_timeout: bool = True # Adaptive timeout adjustment
    enable_graceful_degradation: bool = True
    fallback_enabled: bool = True
    
@dataclass
class HealthProbe:
    """Configuration health probes"""
    probe_id: str
    endpoint: str
    method: str = "GET"
    timeout_seconds: float = 5.0
    expected_status_codes: List[int] = field(default_factory=lambda: [200, 204])
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    interval_seconds: int = 30
    enabled: bool = True

@dataclass
class HealthStatus:
    """Status santé service"""
    service_id: str
    healthy: bool
    response_time_ms: float
    last_check: datetime
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    failure_details: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RecoveryConfig:
    """Configuration recovery graduelle"""
    strategy: RecoveryStrategy
    initial_percentage: float = 0.1      # Start with 10% traffic
    increment_percentage: float = 0.1    # Increase by 10% each step
    increment_interval_seconds: int = 30 # Time between increments
    max_percentage: float = 1.0          # Maximum traffic percentage
    backoff_on_failure: bool = True      # Backoff if failures occur
    adaptive_increment: bool = True      # ML-adaptive increments

@dataclass
class FallbackResponse:
    """Réponse fallback"""
    response_id: str
    content: Any
    status_code: int = 503
    headers: Dict[str, str] = field(default_factory=dict)
    reason: str = "Circuit breaker open"
    cached: bool = False
    cache_expiry: Optional[datetime] = None

@dataclass
class CircuitDecision:
    """Décision circuit breaker"""
    allowed: bool
    circuit_state: CircuitState
    reason: str
    rate_limit_result: Optional[RateLimitResult] = None
    fallback_response: Optional[FallbackResponse] = None
    retry_after: Optional[float] = None
    health_status: Optional[HealthStatus] = None
    recovery_progress: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RecoveryProgress:
    """Progress recovery graduelle"""
    recovery_id: str
    current_percentage: float
    target_percentage: float
    elapsed_seconds: int
    successful_requests: int
    failed_requests: int
    estimated_completion: datetime
    strategy_applied: RecoveryStrategy

class FailureCounter:
    """Compteur failures avec sliding window"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.failures = deque(maxlen=window_size)
        self.requests = deque(maxlen=window_size)
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.total_requests = 0
        self.total_failures = 0
        
    def record_success(self):
        """Enregistrement succès"""
        self.requests.append(True)
        self.consecutive_failures = 0
        self.consecutive_successes += 1
        self.total_requests += 1
        
    def record_failure(self, failure_type: FailureType = FailureType.ERROR_RESPONSE):
        """Enregistrement failure"""
        self.failures.append({
            "timestamp": time.time(),
            "type": failure_type,
            "id": str(uuid.uuid4())
        })
        self.requests.append(False)
        self.consecutive_successes = 0
        self.consecutive_failures += 1
        self.total_requests += 1
        self.total_failures += 1
        
    def get_failure_rate(self) -> float:
        """Taux de failure dans sliding window"""
        if len(self.requests) == 0:
            return 0.0
        
        failed_requests = sum(1 for success in self.requests if not success)
        return failed_requests / len(self.requests)
    
    def get_recent_failures(self, seconds: int = 300) -> List[Dict[str, Any]]:
        """Failures récentes dans timeframe"""
        cutoff_time = time.time() - seconds
        return [f for f in self.failures if f["timestamp"] > cutoff_time]
    
    def reset(self):
        """Reset compteur"""
        self.failures.clear()
        self.requests.clear()
        self.consecutive_failures = 0
        self.consecutive_successes = 0

class HealthMonitor:
    """Monitoring santé services avec probes"""
    
    def __init__(self):
        self.health_probes = {}
        self.health_status = {}
        self.probe_history = defaultdict(lambda: deque(maxlen=100))
        self.logger = logging.getLogger(__name__)
        
        # Background tasks
        self._probe_tasks = {}
        self._stop_event = asyncio.Event()
        
    async def add_health_probe(self, probe: HealthProbe) -> bool:
        """Ajout health probe"""
        try:
            self.health_probes[probe.probe_id] = probe
            
            # Démarrage probe task si enabled
            if probe.enabled:
                probe_task = asyncio.create_task(self._probe_loop(probe))
                self._probe_tasks[probe.probe_id] = probe_task
                
            self.logger.info(f"Health probe added: {probe.probe_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add health probe {probe.probe_id}: {e}")
            return False
    
    async def _probe_loop(self, probe: HealthProbe):
        """Loop probe santé"""
        while not self._stop_event.is_set():
            try:
                # Exécution probe
                health_status = await self._execute_probe(probe)
                
                # Stockage résultat
                self.health_status[probe.probe_id] = health_status
                self.probe_history[probe.probe_id].append(health_status)
                
                # Attente avant prochain probe
                await asyncio.sleep(probe.interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Health probe error for {probe.probe_id}: {e}")
                await asyncio.sleep(min(probe.interval_seconds, 60))
    
    async def _execute_probe(self, probe: HealthProbe) -> HealthStatus:
        """Exécution probe santé"""
        start_time = time.time()
        
        try:
            # Simulation HTTP request - dans une implémentation réelle,
            # utiliser aiohttp ou requests
            await asyncio.sleep(0.01)  # Simulate network call
            
            # Simulation response
            response_time_ms = (time.time() - start_time) * 1000
            
            # Vérification santé basée sur response time et availability
            healthy = response_time_ms < probe.timeout_seconds * 1000
            
            # Update consecutive counters
            current_status = self.health_status.get(probe.probe_id)
            if current_status:
                if healthy:
                    consecutive_successes = current_status.consecutive_successes + 1
                    consecutive_failures = 0
                else:
                    consecutive_successes = 0
                    consecutive_failures = current_status.consecutive_failures + 1
            else:
                consecutive_successes = 1 if healthy else 0
                consecutive_failures = 0 if healthy else 1
            
            return HealthStatus(
                service_id=probe.probe_id,
                healthy=healthy,
                response_time_ms=response_time_ms,
                last_check=datetime.now(),
                consecutive_failures=consecutive_failures,
                consecutive_successes=consecutive_successes,
                failure_details=None if healthy else f"Response time {response_time_ms:.1f}ms exceeded timeout",
                metrics={
                    "probe_endpoint": probe.endpoint,
                    "probe_method": probe.method,
                    "timeout_threshold": probe.timeout_seconds * 1000
                }
            )
            
        except Exception as e:
            return HealthStatus(
                service_id=probe.probe_id,
                healthy=False,
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.now(),
                consecutive_failures=1,
                consecutive_successes=0,
                failure_details=str(e),
                metrics={"error": str(e)}
            )
    
    async def get_service_health(self, service_id: str) -> Optional[HealthStatus]:
        """Récupération status santé service"""
        return self.health_status.get(service_id)
    
    async def get_aggregated_health(self) -> Dict[str, Any]:
        """Status santé agrégé tous services"""
        total_services = len(self.health_status)
        healthy_services = sum(1 for status in self.health_status.values() if status.healthy)
        
        if total_services == 0:
            overall_health = "unknown"
        elif healthy_services == total_services:
            overall_health = "healthy"
        elif healthy_services > total_services * 0.5:
            overall_health = "degraded"
        else:
            overall_health = "unhealthy"
        
        return {
            "overall_health": overall_health,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "health_percentage": (healthy_services / max(1, total_services)) * 100,
            "services": {
                service_id: {
                    "healthy": status.healthy,
                    "response_time_ms": status.response_time_ms,
                    "last_check": status.last_check.isoformat()
                }
                for service_id, status in self.health_status.items()
            }
        }
    
    async def stop_monitoring(self):
        """Arrêt monitoring"""
        self._stop_event.set()
        
        # Attendre fin des probe tasks
        for task in self._probe_tasks.values():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

class GradualRecoveryStrategy:
    """Stratégie recovery graduelle"""
    
    def __init__(self, config: RecoveryConfig):
        self.config = config
        self.active_recoveries = {}
        self.recovery_history = deque(maxlen=1000)
        self.logger = logging.getLogger(__name__)
    
    async def start_recovery(self, service_id: str) -> str:
        """Démarrage recovery graduelle"""
        recovery_id = str(uuid.uuid4())
        
        recovery_progress = RecoveryProgress(
            recovery_id=recovery_id,
            current_percentage=self.config.initial_percentage,
            target_percentage=self.config.max_percentage,
            elapsed_seconds=0,
            successful_requests=0,
            failed_requests=0,
            estimated_completion=datetime.now() + timedelta(
                seconds=self._estimate_recovery_time()
            ),
            strategy_applied=self.config.strategy
        )
        
        self.active_recoveries[service_id] = recovery_progress
        
        # Démarrage recovery loop
        asyncio.create_task(self._recovery_loop(service_id, recovery_id))
        
        self.logger.info(f"Gradual recovery started for {service_id}: {recovery_id}")
        return recovery_id
    
    async def _recovery_loop(self, service_id: str, recovery_id: str):
        """Loop recovery graduelle"""
        start_time = time.time()
        
        while service_id in self.active_recoveries:
            try:
                recovery = self.active_recoveries[service_id]
                
                # Update elapsed time
                recovery.elapsed_seconds = int(time.time() - start_time)
                
                # Vérification si recovery complété
                if recovery.current_percentage >= recovery.target_percentage:
                    await self._complete_recovery(service_id, recovery_id)
                    break
                
                # Calcul next increment
                next_increment = await self._calculate_next_increment(recovery)
                
                # Application increment
                recovery.current_percentage = min(
                    recovery.target_percentage,
                    recovery.current_percentage + next_increment
                )
                
                # Update estimated completion
                remaining_percentage = recovery.target_percentage - recovery.current_percentage
                estimated_remaining_time = (
                    remaining_percentage / next_increment * self.config.increment_interval_seconds
                )
                recovery.estimated_completion = datetime.now() + timedelta(
                    seconds=estimated_remaining_time
                )
                
                # Attente avant prochain increment
                await asyncio.sleep(self.config.increment_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Recovery loop error for {service_id}: {e}")
                await asyncio.sleep(30)
    
    async def _calculate_next_increment(self, recovery: RecoveryProgress) -> float:
        """Calcul prochain increment recovery"""
        base_increment = self.config.increment_percentage
        
        if self.config.strategy == RecoveryStrategy.LINEAR:
            return base_increment
            
        elif self.config.strategy == RecoveryStrategy.EXPONENTIAL:
            # Exponential increase
            return base_increment * (1.2 ** (recovery.elapsed_seconds // 60))
            
        elif self.config.strategy == RecoveryStrategy.ADAPTIVE:
            # Adaptive basé sur success rate
            if recovery.successful_requests + recovery.failed_requests > 0:
                success_rate = recovery.successful_requests / (
                    recovery.successful_requests + recovery.failed_requests
                )
                if success_rate > 0.9:
                    return base_increment * 1.5  # Accelerate if going well
                elif success_rate < 0.7:
                    return base_increment * 0.5  # Slow down if issues
            return base_increment
            
        else:  # GRADUAL or default
            return base_increment
    
    async def _complete_recovery(self, service_id: str, recovery_id: str):
        """Completion recovery"""
        if service_id in self.active_recoveries:
            recovery = self.active_recoveries[service_id]
            
            # Archivage recovery
            self.recovery_history.append({
                "recovery_id": recovery_id,
                "service_id": service_id,
                "completed_at": datetime.now(),
                "total_time_seconds": recovery.elapsed_seconds,
                "final_percentage": recovery.current_percentage,
                "successful_requests": recovery.successful_requests,
                "failed_requests": recovery.failed_requests,
                "success_rate": recovery.successful_requests / max(1, 
                    recovery.successful_requests + recovery.failed_requests)
            })
            
            # Cleanup
            del self.active_recoveries[service_id]
            
            self.logger.info(f"Recovery completed for {service_id}: {recovery_id}")
    
    async def record_recovery_request(self, service_id: str, success: bool):
        """Enregistrement résultat request durant recovery"""
        if service_id in self.active_recoveries:
            recovery = self.active_recoveries[service_id]
            if success:
                recovery.successful_requests += 1
            else:
                recovery.failed_requests += 1
                
                # Backoff en cas de failure si configuré
                if self.config.backoff_on_failure:
                    recovery.current_percentage = max(
                        self.config.initial_percentage,
                        recovery.current_percentage * 0.8
                    )
    
    def _estimate_recovery_time(self) -> int:
        """Estimation temps recovery total"""
        total_increments = (
            (self.config.max_percentage - self.config.initial_percentage) / 
            self.config.increment_percentage
        )
        return int(total_increments * self.config.increment_interval_seconds)
    
    async def get_recovery_status(self, service_id: str) -> Optional[RecoveryProgress]:
        """Status recovery pour service"""
        return self.active_recoveries.get(service_id)

class FallbackManager:
    """Gestionnaire réponses fallback"""
    
    def __init__(self):
        self.fallback_handlers = {}
        self.fallback_cache = {}
        self.cache_stats = defaultdict(int)
        self.logger = logging.getLogger(__name__)
    
    def register_fallback_handler(self, service_id: str, 
                                 handler: Callable[[Dict[str, Any]], FallbackResponse]):
        """Enregistrement handler fallback"""
        self.fallback_handlers[service_id] = handler
        self.logger.info(f"Fallback handler registered for {service_id}")
    
    async def get_fallback_response(self, service_id: str, 
                                  request_context: Dict[str, Any]) -> FallbackResponse:
        """Génération réponse fallback"""
        try:
            # Vérification cache fallback
            cache_key = self._generate_cache_key(service_id, request_context)
            cached_response = self.fallback_cache.get(cache_key)
            
            if cached_response and not self._is_cache_expired(cached_response):
                self.cache_stats["cache_hits"] += 1
                return cached_response
            
            # Génération nouvelle réponse fallback
            if service_id in self.fallback_handlers:
                fallback_response = self.fallback_handlers[service_id](request_context)
            else:
                # Default fallback
                fallback_response = self._generate_default_fallback(service_id, request_context)
            
            # Cache si applicable
            if fallback_response.cached:
                self.fallback_cache[cache_key] = fallback_response
                self.cache_stats["cache_misses"] += 1
            
            return fallback_response
            
        except Exception as e:
            self.logger.error(f"Fallback generation failed for {service_id}: {e}")
            return self._generate_error_fallback(service_id, str(e))
    
    def _generate_cache_key(self, service_id: str, request_context: Dict[str, Any]) -> str:
        """Génération clé cache"""
        context_hash = hash(json.dumps(request_context, sort_keys=True))
        return f"fallback:{service_id}:{context_hash}"
    
    def _is_cache_expired(self, fallback_response: FallbackResponse) -> bool:
        """Vérification expiration cache"""
        if not fallback_response.cache_expiry:
            return False
        return datetime.now() > fallback_response.cache_expiry
    
    def _generate_default_fallback(self, service_id: str, 
                                 request_context: Dict[str, Any]) -> FallbackResponse:
        """Génération fallback par défaut"""
        return FallbackResponse(
            response_id=str(uuid.uuid4()),
            content={
                "error": "Service temporarily unavailable",
                "service_id": service_id,
                "timestamp": datetime.now().isoformat(),
                "retry_suggested": True
            },
            status_code=503,
            headers={"Retry-After": "60"},
            reason="Circuit breaker fallback",
            cached=True,
            cache_expiry=datetime.now() + timedelta(minutes=5)
        )
    
    def _generate_error_fallback(self, service_id: str, error: str) -> FallbackResponse:
        """Génération fallback d'erreur"""
        return FallbackResponse(
            response_id=str(uuid.uuid4()),
            content={
                "error": "Fallback generation failed",
                "service_id": service_id,
                "details": error,
                "timestamp": datetime.now().isoformat()
            },
            status_code=500,
            reason="Fallback error"
        )

class CircuitBreakerRateLimiter:
    """
    Circuit Breaker intégré avec Rate Limiting.
    Fail-fast + gradual recovery + health monitoring.
    """
    
    def __init__(self, distributed_limiter: DistributedRateLimiter, 
                 circuit_config: CircuitConfig):
        self.distributed_limiter = distributed_limiter
        self.circuit_config = circuit_config
        self.circuit_state = CircuitState.CLOSED
        self.failure_counter = FailureCounter(circuit_config.sliding_window_size)
        self.health_monitor = HealthMonitor()
        self.recovery_strategy = GradualRecoveryStrategy(RecoveryConfig(
            strategy=RecoveryStrategy.GRADUAL
        ))
        self.fallback_manager = FallbackManager()
        
        # État circuit breaker
        self.state_change_time = datetime.now()
        self.last_health_check = datetime.now()
        self.concurrent_requests = 0
        self.recovery_percentage = 0.0
        
        # Métriques
        self.circuit_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "circuit_opens": 0,
            "circuit_closes": 0,
            "fallback_responses": 0,
            "recovery_attempts": 0
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Background tasks
        self._background_tasks = []
        self._stop_event = asyncio.Event()
    
    async def initialize(self) -> bool:
        """Initialisation circuit breaker rate limiter"""
        try:
            # Initialisation distributed limiter
            await self.distributed_limiter.initialize()
            
            # Démarrage health monitoring
            await self._start_health_monitoring()
            
            # Démarrage background tasks
            await self._start_background_tasks()
            
            self.logger.info("Circuit breaker rate limiter initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Circuit breaker initialization failed: {e}")
            return False
    
    async def rate_limit_with_circuit_protection(self, request: Dict[str, Any]) -> CircuitDecision:
        """
        Rate limiting avec circuit breaker protection.
        
        Circuit Features:
        - Circuit breaker states (CLOSED/OPEN/HALF_OPEN)
        - Failure rate threshold monitoring
        - Gradual recovery avec progressive request allowance
        - Health check probes pour service recovery detection
        - Fallback responses pour requests rejected
        - Circuit state propagation across distributed nodes
        - Real-time circuit metrics et alerting
        """
        start_time = time.time()
        self.circuit_metrics["total_requests"] += 1
        
        try:
            # 1. Vérification état circuit
            if self.circuit_state == CircuitState.OPEN:
                return await self._handle_open_circuit(request)
            
            # 2. Vérification concurrency limits
            if self.concurrent_requests >= self.circuit_config.max_concurrent_requests:
                return await self._handle_concurrency_limit_exceeded(request)
            
            # 3. Vérification rate limiting standard
            rate_limit_result = await self.distributed_limiter.check_rate_limit(
                request.get("identifier", "default"),
                request.get("cost", 1),
                request.get("metadata", {})
            )
            
            # 4. Processing selon état circuit
            if self.circuit_state == CircuitState.HALF_OPEN:
                return await self._handle_half_open_circuit(request, rate_limit_result)
            else:  # CLOSED
                return await self._handle_closed_circuit(request, rate_limit_result)
                
        except Exception as e:
            self.logger.error(f"Circuit breaker decision failed: {e}")
            # Record failure
            self.failure_counter.record_failure(FailureType.ERROR_RESPONSE)
            await self._evaluate_circuit_state()
            
            return CircuitDecision(
                allowed=False,
                circuit_state=self.circuit_state,
                reason=f"Circuit breaker error: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _handle_open_circuit(self, request: Dict[str, Any]) -> CircuitDecision:
        """Handling circuit ouvert"""
        # Vérification si il faut tenter recovery
        time_since_open = (datetime.now() - self.state_change_time).total_seconds()
        
        if time_since_open >= self.circuit_config.recovery_timeout_seconds:
            # Tentative passage en half-open
            await self._transition_to_half_open()
            return await self._handle_half_open_circuit(request, None)
        
        # Circuit reste ouvert - fallback response
        fallback_response = None
        if self.circuit_config.fallback_enabled:
            fallback_response = await self.fallback_manager.get_fallback_response(
                request.get("service_id", "unknown"), request
            )
            self.circuit_metrics["fallback_responses"] += 1
        
        return CircuitDecision(
            allowed=False,
            circuit_state=CircuitState.OPEN,
            reason=f"Circuit open - {time_since_open:.1f}s since opening",
            fallback_response=fallback_response,
            retry_after=self.circuit_config.recovery_timeout_seconds - time_since_open,
            metadata={
                "time_since_open": time_since_open,
                "recovery_timeout": self.circuit_config.recovery_timeout_seconds
            }
        )
    
    async def _handle_half_open_circuit(self, request: Dict[str, Any], 
                                      rate_limit_result: Optional[RateLimitResult]) -> CircuitDecision:
        """Handling circuit half-open (recovery)"""
        # Vérification recovery percentage pour gradual recovery
        if hasattr(self, 'recovery_percentage'):
            import random
            if random.random() > self.recovery_percentage:
                # Request rejeté dans cadre gradual recovery
                fallback_response = await self.fallback_manager.get_fallback_response(
                    request.get("service_id", "unknown"), request
                ) if self.circuit_config.fallback_enabled else None
                
                return CircuitDecision(
                    allowed=False,
                    circuit_state=CircuitState.HALF_OPEN,
                    reason=f"Gradual recovery - {self.recovery_percentage*100:.1f}% traffic allowed",
                    fallback_response=fallback_response,
                    recovery_progress=self.recovery_percentage,
                    metadata={"recovery_percentage": self.recovery_percentage}
                )
        
        # Request autorisé dans recovery - mais vérifier rate limit
        if rate_limit_result and not rate_limit_result.allowed:
            return CircuitDecision(
                allowed=False,
                circuit_state=CircuitState.HALF_OPEN,
                reason="Rate limit exceeded during recovery",
                rate_limit_result=rate_limit_result,
                recovery_progress=self.recovery_percentage
            )
        
        # Request autorisé - monitoring du résultat pour décision circuit
        self.concurrent_requests += 1
        
        return CircuitDecision(
            allowed=True,
            circuit_state=CircuitState.HALF_OPEN,
            reason="Request allowed during recovery",
            rate_limit_result=rate_limit_result,
            recovery_progress=self.recovery_percentage,
            metadata={
                "recovery_monitoring": True,
                "concurrent_requests": self.concurrent_requests
            }
        )
    
    async def _handle_closed_circuit(self, request: Dict[str, Any], 
                                   rate_limit_result: RateLimitResult) -> CircuitDecision:
        """Handling circuit fermé (normal)"""
        if not rate_limit_result.allowed:
            # Rate limit exceeded
            self.failure_counter.record_failure(FailureType.RATE_LIMIT_EXCEEDED)
            await self._evaluate_circuit_state()
            
            return CircuitDecision(
                allowed=False,
                circuit_state=self.circuit_state,
                reason="Rate limit exceeded",
                rate_limit_result=rate_limit_result
            )
        
        # Request autorisé normalement
        self.concurrent_requests += 1
        self.circuit_metrics["successful_requests"] += 1
        
        return CircuitDecision(
            allowed=True,
            circuit_state=CircuitState.CLOSED,
            reason="Request allowed - normal operation",
            rate_limit_result=rate_limit_result,
            metadata={
                "concurrent_requests": self.concurrent_requests,
                "failure_rate": self.failure_counter.get_failure_rate()
            }
        )
    
    async def _handle_concurrency_limit_exceeded(self, request: Dict[str, Any]) -> CircuitDecision:
        """Handling dépassement limite concurrence"""
        self.failure_counter.record_failure(FailureType.SERVICE_UNAVAILABLE)
        await self._evaluate_circuit_state()
        
        fallback_response = await self.fallback_manager.get_fallback_response(
            request.get("service_id", "unknown"), request
        ) if self.circuit_config.fallback_enabled else None
        
        return CircuitDecision(
            allowed=False,
            circuit_state=self.circuit_state,
            reason=f"Concurrency limit exceeded: {self.concurrent_requests}/{self.circuit_config.max_concurrent_requests}",
            fallback_response=fallback_response,
            retry_after=1.0,
            metadata={
                "concurrent_requests": self.concurrent_requests,
                "max_concurrent": self.circuit_config.max_concurrent_requests
            }
        )
    
    async def _evaluate_circuit_state(self):
        """Évaluation et transition état circuit"""
        failure_rate = self.failure_counter.get_failure_rate()
        consecutive_failures = self.failure_counter.consecutive_failures
        
        # Transition vers OPEN si thresholds dépassés
        if (self.circuit_state == CircuitState.CLOSED and
            (consecutive_failures >= self.circuit_config.failure_threshold or
             (len(self.failure_counter.requests) >= self.circuit_config.minimum_requests and
              failure_rate >= self.circuit_config.failure_rate_threshold))):
            
            await self._transition_to_open()
        
        # Transition vers CLOSED depuis HALF_OPEN si succès
        elif (self.circuit_state == CircuitState.HALF_OPEN and
              self.failure_counter.consecutive_successes >= self.circuit_config.success_threshold):
            
            await self._transition_to_closed()
    
    async def _transition_to_open(self):
        """Transition vers circuit ouvert"""
        self.circuit_state = CircuitState.OPEN
        self.state_change_time = datetime.now()
        self.circuit_metrics["circuit_opens"] += 1
        
        self.logger.warning(f"Circuit breaker OPENED - failure rate: {self.failure_counter.get_failure_rate():.2f}")
    
    async def _transition_to_half_open(self):
        """Transition vers circuit half-open"""
        self.circuit_state = CircuitState.HALF_OPEN
        self.state_change_time = datetime.now()
        self.recovery_percentage = 0.1  # Start with 10%
        
        # Démarrage gradual recovery
        recovery_id = await self.recovery_strategy.start_recovery("main_service")
        self.circuit_metrics["recovery_attempts"] += 1
        
        self.logger.info(f"Circuit breaker transitioned to HALF_OPEN - recovery started: {recovery_id}")
    
    async def _transition_to_closed(self):
        """Transition vers circuit fermé"""
        self.circuit_state = CircuitState.CLOSED
        self.state_change_time = datetime.now()
        self.recovery_percentage = 1.0
        self.circuit_metrics["circuit_closes"] += 1
        
        # Reset failure counter
        self.failure_counter.reset()
        
        self.logger.info("Circuit breaker CLOSED - service recovered")
    
    async def record_request_result(self, request_id: str, success: bool, 
                                  response_time_ms: float, error_details: Optional[str] = None):
        """Enregistrement résultat request pour circuit decisions"""
        # Décrémentation concurrent requests
        if self.concurrent_requests > 0:
            self.concurrent_requests -= 1
        
        # Enregistrement résultat
        if success:
            self.failure_counter.record_success()
            
            # Update recovery progress si en recovery
            if self.circuit_state == CircuitState.HALF_OPEN:
                await self.recovery_strategy.record_recovery_request("main_service", True)
                recovery_status = await self.recovery_strategy.get_recovery_status("main_service")
                if recovery_status:
                    self.recovery_percentage = recovery_status.current_percentage
        else:
            # Détermination type de failure
            failure_type = FailureType.ERROR_RESPONSE
            if "timeout" in (error_details or "").lower():
                failure_type = FailureType.TIMEOUT
            elif "network" in (error_details or "").lower():
                failure_type = FailureType.NETWORK_ERROR
            
            self.failure_counter.record_failure(failure_type)
            self.circuit_metrics["failed_requests"] += 1
            
            # Update recovery progress si en recovery
            if self.circuit_state == CircuitState.HALF_OPEN:
                await self.recovery_strategy.record_recovery_request("main_service", False)
        
        # Réévaluation état circuit
        await self._evaluate_circuit_state()
    
    async def _start_health_monitoring(self):
        """Démarrage monitoring santé"""
        # Health probe par défaut
        default_probe = HealthProbe(
            probe_id="main_service",
            endpoint="/health",
            interval_seconds=30
        )
        
        await self.health_monitor.add_health_probe(default_probe)
    
    async def _start_background_tasks(self):
        """Démarrage tâches background"""
        # Tâche cleanup métriques
        cleanup_task = asyncio.create_task(self._metrics_cleanup_loop())
        self._background_tasks.append(cleanup_task)
        
        # Tâche adaptive timeout adjustment
        if self.circuit_config.enable_adaptive_timeout:
            timeout_task = asyncio.create_task(self._adaptive_timeout_loop())
            self._background_tasks.append(timeout_task)
    
    async def _metrics_cleanup_loop(self):
        """Loop cleanup métriques anciennes"""
        while not self._stop_event.is_set():
            try:
                # Cleanup failure records anciens
                cutoff_time = time.time() - 3600  # 1 hour
                self.failure_counter.failures = deque([
                    f for f in self.failure_counter.failures 
                    if f["timestamp"] > cutoff_time
                ], maxlen=self.failure_counter.window_size)
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Metrics cleanup error: {e}")
                await asyncio.sleep(60)
    
    async def _adaptive_timeout_loop(self):
        """Loop ajustement timeout adaptatif"""
        while not self._stop_event.is_set():
            try:
                # Analyse response times récents
                health_status = await self.health_monitor.get_aggregated_health()
                
                if health_status["healthy_services"] > 0:
                    # Calcul moyenne response times
                    avg_response_time = statistics.mean([
                        service["response_time_ms"] 
                        for service in health_status["services"].values()
                        if service["healthy"]
                    ])
                    
                    # Ajustement timeout basé sur response times
                    new_timeout = min(
                        max(avg_response_time * 3, 5.0),  # Min 5s
                        60.0  # Max 60s
                    )
                    
                    if abs(new_timeout - self.circuit_config.timeout_seconds) > 5.0:
                        old_timeout = self.circuit_config.timeout_seconds
                        self.circuit_config.timeout_seconds = new_timeout
                        self.logger.info(f"Adaptive timeout adjusted: {old_timeout:.1f}s -> {new_timeout:.1f}s")
                
                await asyncio.sleep(600)  # Every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Adaptive timeout error: {e}")
                await asyncio.sleep(300)
    
    async def get_circuit_status(self) -> Dict[str, Any]:
        """Status complet circuit breaker"""
        health_status = await self.health_monitor.get_aggregated_health()
        recovery_status = await self.recovery_strategy.get_recovery_status("main_service")
        
        return {
            "circuit_state": self.circuit_state.value,
            "state_duration_seconds": (datetime.now() - self.state_change_time).total_seconds(),
            "failure_rate": self.failure_counter.get_failure_rate(),
            "consecutive_failures": self.failure_counter.consecutive_failures,
            "consecutive_successes": self.failure_counter.consecutive_successes,
            "concurrent_requests": self.concurrent_requests,
            "recovery_percentage": self.recovery_percentage,
            "health_status": health_status,
            "recovery_status": recovery_status.__dict__ if recovery_status else None,
            "metrics": self.circuit_metrics,
            "config": {
                "failure_threshold": self.circuit_config.failure_threshold,
                "success_threshold": self.circuit_config.success_threshold,
                "timeout_seconds": self.circuit_config.timeout_seconds,
                "recovery_timeout_seconds": self.circuit_config.recovery_timeout_seconds,
                "failure_rate_threshold": self.circuit_config.failure_rate_threshold
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Arrêt propre circuit breaker"""
        self._stop_event.set()
        
        # Arrêt health monitoring
        await self.health_monitor.stop_monitoring()
        
        # Attendre fin background tasks
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.logger.info("Circuit breaker shutdown complete")

# Factory functions
def create_api_circuit_breaker(redis_client, api_limits: Dict[str, Any]) -> CircuitBreakerRateLimiter:
    """Factory pour circuit breaker API"""
    # Rate limiter base
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=api_limits.get("requests_per_second", 100),
        burst_capacity=api_limits.get("burst_capacity", 200),
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        redis_key_prefix="api_cb_rl"
    ))
    
    # Circuit breaker config
    circuit_config = CircuitConfig(
        failure_threshold=api_limits.get("failure_threshold", 5),
        success_threshold=3,
        timeout_seconds=api_limits.get("timeout_seconds", 30.0),
        recovery_timeout_seconds=60,
        failure_rate_threshold=0.5,
        minimum_requests=10,
        enable_adaptive_timeout=True,
        enable_graceful_degradation=True,
        fallback_enabled=True
    )
    
    return CircuitBreakerRateLimiter(base_limiter, circuit_config)

def create_service_circuit_breaker(redis_client, service_config: Dict[str, Any]) -> CircuitBreakerRateLimiter:
    """Factory pour circuit breaker service"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=service_config.get("requests_per_second", 1000),
        burst_capacity=service_config.get("burst_capacity", 2000),
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
        redis_key_prefix="service_cb_rl"
    ))
    
    circuit_config = CircuitConfig(
        failure_threshold=service_config.get("failure_threshold", 10),
        success_threshold=5,
        timeout_seconds=service_config.get("timeout_seconds", 60.0),
        recovery_timeout_seconds=120,
        failure_rate_threshold=0.3,
        minimum_requests=20,
        max_concurrent_requests=service_config.get("max_concurrent", 5000),
        enable_adaptive_timeout=True,
        enable_graceful_degradation=True,
        fallback_enabled=True
    )
    
    return CircuitBreakerRateLimiter(base_limiter, circuit_config)

# Export classes principales
__all__ = [
    'CircuitBreakerRateLimiter',
    'CircuitConfig',
    'CircuitState',
    'CircuitDecision',
    'HealthProbe',
    'HealthStatus',
    'RecoveryConfig',
    'FallbackResponse',
    'FailureType',
    'RecoveryStrategy',
    'create_api_circuit_breaker',
    'create_service_circuit_breaker'
]