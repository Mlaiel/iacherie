"""
Circuit Breaker Retry Integration - Ainflue
==========================================
Intégration circuit breaker avec retry mechanisms.
State-aware retry + gradual recovery + health probing.

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
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """États du circuit breaker"""
    CLOSED = "closed"      # Trafic normal
    OPEN = "open"          # Circuit ouvert, pas de trafic
    HALF_OPEN = "half_open"  # Test de récupération

class RecoveryPhase(Enum):
    """Phases de récupération graduelle"""
    PROBING = "probing"
    TESTING = "testing" 
    RECOVERING = "recovering"
    STABILIZING = "stabilizing"
    RECOVERED = "recovered"

@dataclass
class IntegrationConfig:
    """Configuration intégration circuit breaker"""
    # Circuit breaker settings
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_duration: float = 60.0
    half_open_max_calls: int = 10
    
    # Health probing settings
    probe_interval: float = 30.0
    probe_timeout: float = 5.0
    probe_max_failures: int = 3
    
    # Recovery settings
    recovery_stages: int = 4
    recovery_stage_duration: float = 30.0
    recovery_success_threshold: float = 0.8
    
    # Retry integration
    retry_budget_adjustment: float = 0.5
    circuit_aware_backoff: bool = True
    fallback_enabled: bool = True

@dataclass
class CircuitMetrics:
    """Métriques circuit breaker"""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    total_requests: int = 0
    last_failure_time: Optional[float] = None
    state_changed_at: float = field(default_factory=time.time)
    recovery_attempts: int = 0
    
    def record_success(self):
        """Enregistrement succès"""
        self.success_count += 1
        self.total_requests += 1
        
    def record_failure(self):
        """Enregistrement échec"""
        self.failure_count += 1
        self.total_requests += 1
        self.last_failure_time = time.time()
    
    def get_failure_rate(self) -> float:
        """Calcul taux d'échec"""
        if self.total_requests == 0:
            return 0.0
        return self.failure_count / self.total_requests
    
    def reset_counts(self):
        """Reset compteurs"""
        self.failure_count = 0
        self.success_count = 0
        # Keep total_requests for historical tracking

@dataclass
class HealthProbe:
    """Configuration probe de santé"""
    service_id: str
    endpoint: str
    method: str = "GET"
    timeout: float = 5.0
    expected_status: int = 200
    payload: Optional[Dict] = None
    headers: Optional[Dict] = None

@dataclass
class ProbeResult:
    """Résultat probe de santé"""
    service_id: str
    success: bool
    latency: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

class CircuitStateMonitor:
    """Moniteur état circuit breaker"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.circuit_metrics = defaultdict(CircuitMetrics)
        self.state_history = defaultdict(lambda: deque(maxlen=100))
        
    async def get_circuit_state(self, service_id: str) -> CircuitState:
        """Récupération état actuel du circuit"""
        metrics = self.circuit_metrics[service_id]
        return metrics.state
    
    async def update_circuit_state(self, service_id: str, success: bool) -> CircuitState:
        """Mise à jour état circuit basé sur résultat opération"""
        metrics = self.circuit_metrics[service_id]
        current_time = time.time()
        
        if success:
            metrics.record_success()
        else:
            metrics.record_failure()
        
        # Logique de transition d'état
        previous_state = metrics.state
        new_state = await self._calculate_new_state(service_id, metrics, current_time)
        
        if new_state != previous_state:
            metrics.state = new_state
            metrics.state_changed_at = current_time
            
            # Historique des changements d'état
            self.state_history[service_id].append({
                'from_state': previous_state.value,
                'to_state': new_state.value,
                'timestamp': current_time,
                'failure_count': metrics.failure_count,
                'success_count': metrics.success_count
            })
            
            logger.info(f"Circuit breaker state changed for {service_id}: {previous_state.value} -> {new_state.value}")
        
        return new_state
    
    async def _calculate_new_state(self, service_id: str, metrics: CircuitMetrics, current_time: float) -> CircuitState:
        """Calcul nouvel état circuit"""
        
        if metrics.state == CircuitState.CLOSED:
            # CLOSED -> OPEN si trop d'échecs
            if metrics.failure_count >= self.config.failure_threshold:
                logger.warning(f"Circuit breaker opening for {service_id} - failure threshold reached")
                return CircuitState.OPEN
                
        elif metrics.state == CircuitState.OPEN:
            # OPEN -> HALF_OPEN après timeout
            if (metrics.last_failure_time and 
                current_time - metrics.last_failure_time >= self.config.timeout_duration):
                logger.info(f"Circuit breaker transitioning to HALF_OPEN for {service_id}")
                metrics.reset_counts()
                return CircuitState.HALF_OPEN
                
        elif metrics.state == CircuitState.HALF_OPEN:
            # HALF_OPEN -> CLOSED si assez de succès
            if metrics.success_count >= self.config.success_threshold:
                logger.info(f"Circuit breaker closing for {service_id} - recovery successful")
                metrics.reset_counts()
                return CircuitState.CLOSED
            
            # HALF_OPEN -> OPEN si échec ou trop de requêtes
            if (metrics.failure_count > 0 or 
                metrics.total_requests >= self.config.half_open_max_calls):
                logger.warning(f"Circuit breaker reopening for {service_id}")
                return CircuitState.OPEN
        
        return metrics.state
    
    async def get_metrics(self, service_id: str) -> Dict:
        """Récupération métriques circuit"""
        metrics = self.circuit_metrics[service_id]
        return {
            'service_id': service_id,
            'state': metrics.state.value,
            'failure_count': metrics.failure_count,
            'success_count': metrics.success_count,
            'total_requests': metrics.total_requests,
            'failure_rate': metrics.get_failure_rate(),
            'last_failure_time': metrics.last_failure_time,
            'state_changed_at': metrics.state_changed_at,
            'time_in_current_state': time.time() - metrics.state_changed_at,
            'recovery_attempts': metrics.recovery_attempts
        }

class ServiceHealthProber:
    """Probeur santé services pour récupération circuit"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.probe_results = defaultdict(lambda: deque(maxlen=50))
        self.active_probes = {}
        
    async def execute_health_probe(self, probe: HealthProbe) -> ProbeResult:
        """Exécution probe de santé"""
        start_time = time.time()
        
        try:
            # Simulation probe HTTP (en production, vraie requête HTTP)
            await asyncio.sleep(0.1)  # Simulate network latency
            
            # Simulation réponse basée sur service_id
            success_probability = 0.8 if "stable" in probe.service_id else 0.6
            success = time.time() % 1 < success_probability
            
            latency = time.time() - start_time
            status_code = 200 if success else 500
            
            result = ProbeResult(
                service_id=probe.service_id,
                success=success,
                latency=latency,
                status_code=status_code
            )
            
        except Exception as e:
            result = ProbeResult(
                service_id=probe.service_id,
                success=False,
                latency=time.time() - start_time,
                error_message=str(e)
            )
        
        # Stockage résultat
        self.probe_results[probe.service_id].append(result)
        return result
    
    async def execute_continuous_probing(self, service_id: str, probe: HealthProbe) -> bool:
        """Probing continu pour service en récupération"""
        probe_count = 0
        success_count = 0
        
        while probe_count < self.config.probe_max_failures * 2:
            result = await self.execute_health_probe(probe)
            probe_count += 1
            
            if result.success:
                success_count += 1
            
            # Vérification si récupération détectée
            if success_count >= self.config.probe_max_failures:
                logger.info(f"Service {service_id} appears to be recovering - {success_count} successful probes")
                return True
            
            await asyncio.sleep(self.config.probe_interval)
        
        return False
    
    async def get_service_health_score(self, service_id: str) -> float:
        """Calcul score santé service basé sur probes récents"""
        results = list(self.probe_results[service_id])
        
        if not results:
            return 0.5  # Unknown health
        
        # Score basé sur succès récents avec pondération temporelle
        current_time = time.time()
        weighted_score = 0.0
        total_weight = 0.0
        
        for result in results[-10:]:  # Last 10 probes
            age = current_time - result.timestamp
            weight = max(0.1, 1.0 - (age / 300.0))  # Decay over 5 minutes
            
            score = 1.0 if result.success else 0.0
            weighted_score += score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0

class GradualRecoveryManager:
    """Manager récupération graduelle des circuits"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.recovery_states = defaultdict(lambda: RecoveryPhase.PROBING)
        self.recovery_metrics = defaultdict(lambda: {
            'stage': 0,
            'success_rate': 0.0,
            'requests_allowed': 1,
            'stage_start_time': time.time()
        })
    
    async def initiate_recovery(self, service_id: str) -> RecoveryPhase:
        """Initiation récupération graduelle"""
        self.recovery_states[service_id] = RecoveryPhase.PROBING
        self.recovery_metrics[service_id] = {
            'stage': 0,
            'success_rate': 0.0,
            'requests_allowed': 1,
            'stage_start_time': time.time()
        }
        
        logger.info(f"Initiated gradual recovery for service {service_id}")
        return RecoveryPhase.PROBING
    
    async def update_recovery_progress(self, service_id: str, success_rate: float) -> RecoveryPhase:
        """Mise à jour progrès récupération"""
        current_phase = self.recovery_states[service_id]
        metrics = self.recovery_metrics[service_id]
        current_time = time.time()
        
        # Mise à jour success rate
        metrics['success_rate'] = success_rate
        
        # Vérification si stage est complété
        stage_duration = current_time - metrics['stage_start_time']
        stage_completed = (stage_duration >= self.config.recovery_stage_duration and
                          success_rate >= self.config.recovery_success_threshold)
        
        if stage_completed:
            new_phase = await self._advance_recovery_stage(service_id, current_phase, metrics)
            
            if new_phase != current_phase:
                self.recovery_states[service_id] = new_phase
                metrics['stage'] += 1
                metrics['stage_start_time'] = current_time
                
                # Augmentation progressive des requêtes autorisées
                if new_phase != RecoveryPhase.RECOVERED:
                    metrics['requests_allowed'] = min(
                        metrics['requests_allowed'] * 2,
                        50  # Cap max requests
                    )
                
                logger.info(f"Advanced recovery stage for {service_id}: {current_phase.value} -> {new_phase.value}")
            
            return new_phase
        
        return current_phase
    
    async def _advance_recovery_stage(self, service_id: str, current_phase: RecoveryPhase, metrics: Dict) -> RecoveryPhase:
        """Avancement stage récupération"""
        
        phase_progression = {
            RecoveryPhase.PROBING: RecoveryPhase.TESTING,
            RecoveryPhase.TESTING: RecoveryPhase.RECOVERING,
            RecoveryPhase.RECOVERING: RecoveryPhase.STABILIZING,
            RecoveryPhase.STABILIZING: RecoveryPhase.RECOVERED
        }
        
        return phase_progression.get(current_phase, current_phase)
    
    async def get_recovery_status(self, service_id: str) -> Dict:
        """Status récupération service"""
        phase = self.recovery_states[service_id]
        metrics = self.recovery_metrics[service_id]
        current_time = time.time()
        
        return {
            'service_id': service_id,
            'recovery_phase': phase.value,
            'current_stage': metrics['stage'],
            'total_stages': self.config.recovery_stages,
            'success_rate': metrics['success_rate'],
            'requests_allowed': metrics['requests_allowed'],
            'stage_duration': current_time - metrics['stage_start_time'],
            'stage_remaining': max(0, self.config.recovery_stage_duration - (current_time - metrics['stage_start_time'])),
            'recovery_progress': min(1.0, metrics['stage'] / self.config.recovery_stages)
        }

class CircuitBreakerRetryIntegration:
    """
    Intégration circuit breaker avec retry mechanisms.
    State-aware retry + gradual recovery + health probing.
    """
    
    def __init__(self, integration_config: IntegrationConfig = None):
        self.integration_config = integration_config or IntegrationConfig()
        self.circuit_monitor = CircuitStateMonitor(self.integration_config)
        self.health_prober = ServiceHealthProber(self.integration_config)
        self.recovery_manager = GradualRecoveryManager(self.integration_config)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Fallback handlers
        self.fallback_handlers = {}
        
        # Métriques intégration
        self.integration_metrics = {
            'retry_attempts_blocked': 0,
            'retry_attempts_allowed': 0,
            'circuit_trips': 0,
            'successful_recoveries': 0,
            'fallback_executions': 0
        }
    
    async def retry_with_circuit_awareness(self, operation_func: Callable, service_id: str, **kwargs) -> Any:
        """
        Retry execution avec circuit breaker state awareness.
        
        Integration Features:
        - Circuit state-aware retry decisions (CLOSED/OPEN/HALF_OPEN)
        - Health probing durant circuit OPEN state
        - Gradual recovery avec progressive retry allowance
        - Failure threshold monitoring pour circuit trip
        - Success rate tracking pour circuit recovery
        - Retry budgets coordination avec circuit breaker
        - Fallback execution pour circuit OPEN state
        """
        
        try:
            # 1. Vérification état circuit
            circuit_state = await self.circuit_monitor.get_circuit_state(service_id)
            
            # 2. Décision retry basée sur état circuit
            if circuit_state == CircuitState.OPEN:
                return await self._handle_open_circuit(operation_func, service_id, **kwargs)
            elif circuit_state == CircuitState.HALF_OPEN:
                return await self._handle_half_open_circuit(operation_func, service_id, **kwargs)
            else:  # CLOSED
                return await self._handle_closed_circuit(operation_func, service_id, **kwargs)
                
        except Exception as e:
            # Mise à jour circuit sur échec
            await self.circuit_monitor.update_circuit_state(service_id, False)
            raise e
    
    async def _handle_closed_circuit(self, operation_func: Callable, service_id: str, **kwargs) -> Any:
        """Handling circuit CLOSED - retry normal"""
        
        try:
            result = await operation_func(**kwargs)
            await self.circuit_monitor.update_circuit_state(service_id, True)
            self.integration_metrics['retry_attempts_allowed'] += 1
            return result
        except Exception as e:
            await self.circuit_monitor.update_circuit_state(service_id, False)
            self.integration_metrics['retry_attempts_blocked'] += 1
            raise e
    
    async def _handle_half_open_circuit(self, operation_func: Callable, service_id: str, **kwargs) -> Any:
        """Handling circuit HALF_OPEN - retry avec limitations"""
        
        # Vérification si requête autorisée durant récupération
        recovery_status = await self.recovery_manager.get_recovery_status(service_id)
        requests_allowed = recovery_status.get('requests_allowed', 1)
        
        # Limitation basique (en production, implémentation plus sophistiquée)
        if requests_allowed <= 0:
            self.integration_metrics['retry_attempts_blocked'] += 1
            return await self.handle_circuit_fallback(operation_func, service_id)
        
        try:
            result = await operation_func(**kwargs)
            
            # Succès - mise à jour circuit et récupération
            await self.circuit_monitor.update_circuit_state(service_id, True)
            await self.recovery_manager.update_recovery_progress(service_id, 1.0)
            
            self.integration_metrics['retry_attempts_allowed'] += 1
            return result
            
        except Exception as e:
            # Échec - circuit peut revenir OPEN
            await self.circuit_monitor.update_circuit_state(service_id, False)
            await self.recovery_manager.update_recovery_progress(service_id, 0.0)
            
            self.integration_metrics['retry_attempts_blocked'] += 1
            raise e
    
    async def _handle_open_circuit(self, operation_func: Callable, service_id: str, **kwargs) -> Any:
        """Handling circuit OPEN - pas de retry, fallback ou exception"""
        
        # Initiation probing pour récupération
        probe = HealthProbe(service_id=service_id, endpoint=f"/health/{service_id}")
        probe_result = await self.health_prober.execute_health_probe(probe)
        
        if probe_result.success:
            # Service semble récupérer, initiation récupération graduelle
            await self.recovery_manager.initiate_recovery(service_id)
            await self.circuit_monitor.update_circuit_state(service_id, True)
            
            # Tentative avec circuit maintenant HALF_OPEN
            return await self._handle_half_open_circuit(operation_func, service_id, **kwargs)
        
        # Service toujours down, exécution fallback
        self.integration_metrics['retry_attempts_blocked'] += 1
        return await self.handle_circuit_fallback(operation_func, service_id)
    
    async def monitor_circuit_state(self, service_id: str) -> CircuitState:
        """Monitoring état circuit breaker pour retry decisions."""
        return await self.circuit_monitor.get_circuit_state(service_id)
    
    async def execute_health_probes(self, probe_config: Dict) -> Dict:
        """Exécution health probes durant circuit recovery."""
        
        service_id = probe_config.get('service_id')
        if not service_id:
            raise ValueError("service_id required in probe_config")
        
        probe = HealthProbe(
            service_id=service_id,
            endpoint=probe_config.get('endpoint', f'/health/{service_id}'),
            method=probe_config.get('method', 'GET'),
            timeout=probe_config.get('timeout', self.integration_config.probe_timeout)
        )
        
        result = await self.health_prober.execute_health_probe(probe)
        health_score = await self.health_prober.get_service_health_score(service_id)
        
        return {
            'probe_result': {
                'service_id': result.service_id,
                'success': result.success,
                'latency': result.latency,
                'status_code': result.status_code,
                'timestamp': result.timestamp
            },
            'health_score': health_score
        }
    
    async def manage_gradual_recovery(self, recovery_phase: RecoveryPhase, service_id: str) -> Dict:
        """Gestion recovery graduelle avec retry coordination."""
        
        if recovery_phase == RecoveryPhase.PROBING:
            await self.recovery_manager.initiate_recovery(service_id)
        
        # Simulation success rate basée sur phase
        success_rates = {
            RecoveryPhase.PROBING: 0.3,
            RecoveryPhase.TESTING: 0.6,
            RecoveryPhase.RECOVERING: 0.8,
            RecoveryPhase.STABILIZING: 0.9,
            RecoveryPhase.RECOVERED: 1.0
        }
        
        simulated_success_rate = success_rates.get(recovery_phase, 0.5)
        updated_phase = await self.recovery_manager.update_recovery_progress(service_id, simulated_success_rate)
        
        return await self.recovery_manager.get_recovery_status(service_id)
    
    async def handle_circuit_fallback(self, operation_func: Callable, service_id: str) -> Any:
        """Handling fallback execution quand circuit est OPEN."""
        
        self.integration_metrics['fallback_executions'] += 1
        
        # Vérification si fallback handler configuré
        if service_id in self.fallback_handlers:
            fallback_func = self.fallback_handlers[service_id]
            try:
                return await fallback_func()
            except Exception as e:
                self.logger.error(f"Fallback execution failed for {service_id}: {str(e)}")
        
        # Fallback par défaut - retour cached data ou exception
        if self.integration_config.fallback_enabled:
            return await self._default_fallback(service_id)
        else:
            raise Exception(f"Circuit breaker OPEN for service {service_id} - no fallback available")
    
    async def _default_fallback(self, service_id: str) -> Dict:
        """Fallback par défaut"""
        return {
            'fallback': True,
            'service_id': service_id,
            'message': 'Service temporarily unavailable - fallback response',
            'timestamp': time.time()
        }
    
    def register_fallback_handler(self, service_id: str, handler: Callable):
        """Enregistrement handler fallback pour service"""
        self.fallback_handlers[service_id] = handler
        self.logger.info(f"Registered fallback handler for service {service_id}")
    
    async def get_integration_metrics(self) -> Dict:
        """Métriques intégration circuit breaker"""
        return {
            **self.integration_metrics,
            'config': {
                'failure_threshold': self.integration_config.failure_threshold,
                'timeout_duration': self.integration_config.timeout_duration,
                'probe_interval': self.integration_config.probe_interval,
                'recovery_stages': self.integration_config.recovery_stages
            }
        }
    
    async def get_service_status(self, service_id: str) -> Dict:
        """Status complet service avec circuit et récupération"""
        
        circuit_metrics = await self.circuit_monitor.get_metrics(service_id)
        health_score = await self.health_prober.get_service_health_score(service_id)
        recovery_status = await self.recovery_manager.get_recovery_status(service_id)
        
        return {
            'service_id': service_id,
            'circuit_breaker': circuit_metrics,
            'health_score': health_score,
            'recovery': recovery_status,
            'integration_metrics': self.integration_metrics
        }

# Factory functions
def create_circuit_breaker_integration(
    failure_threshold: int = 5,
    timeout_duration: float = 60.0,
    probe_interval: float = 30.0,
    fallback_enabled: bool = True
) -> CircuitBreakerRetryIntegration:
    """Factory pour création intégration circuit breaker"""
    
    config = IntegrationConfig(
        failure_threshold=failure_threshold,
        timeout_duration=timeout_duration,
        probe_interval=probe_interval,
        fallback_enabled=fallback_enabled
    )
    
    return CircuitBreakerRetryIntegration(config)

# Configuration prédéfinies pour Ainflue
AINFLUE_CIRCUIT_CONFIGS = {
    'content_processing': IntegrationConfig(
        failure_threshold=3,
        timeout_duration=120.0,
        probe_interval=30.0,
        recovery_stages=3
    ),
    'ai_processing': IntegrationConfig(
        failure_threshold=2,
        timeout_duration=180.0,
        probe_interval=60.0,
        recovery_stages=4
    ),
    'monetization': IntegrationConfig(
        failure_threshold=2,
        timeout_duration=30.0,
        probe_interval=15.0,
        recovery_stages=2,
        fallback_enabled=False  # No fallback for financial operations
    ),
    'distribution': IntegrationConfig(
        failure_threshold=5,
        timeout_duration=300.0,
        probe_interval=60.0,
        recovery_stages=4
    )
}

__all__ = [
    'CircuitBreakerRetryIntegration',
    'CircuitState',
    'RecoveryPhase',
    'IntegrationConfig',
    'CircuitStateMonitor',
    'ServiceHealthProber', 
    'GradualRecoveryManager',
    'HealthProbe',
    'ProbeResult',
    'create_circuit_breaker_integration',
    'AINFLUE_CIRCUIT_CONFIGS'
]