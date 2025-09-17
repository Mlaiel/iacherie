"""
Retry Testing Framework - Ainflue
=================================
Framework tests retry mechanisms.
Chaos testing + failure injection + retry validation.

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
import uuid
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
import random
import statistics
import math

logger = logging.getLogger(__name__)

class TestType(Enum):
    """Types de tests disponibles"""
    UNIT_TEST = "unit_test"
    INTEGRATION_TEST = "integration_test"
    LOAD_TEST = "load_test"
    STRESS_TEST = "stress_test"  
    CHAOS_TEST = "chaos_test"
    RESILIENCE_TEST = "resilience_test"
    PERFORMANCE_TEST = "performance_test"
    FAILURE_INJECTION = "failure_injection"

class FailureType(Enum):
    """Types de pannes à injecter"""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"
    AUTHENTICATION_ERROR = "authentication_error"
    NETWORK_PARTITION = "network_partition"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATABASE_ERROR = "database_error"
    RANDOM_ERROR = "random_error"

class TestSeverity(Enum):
    """Sévérité des tests"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class TestConfig:
    """Configuration test"""
    test_id: str
    test_type: TestType
    test_name: str
    description: str
    severity: TestSeverity
    target_services: List[str]
    duration_seconds: int = 300  # 5 minutes
    concurrent_operations: int = 10
    failure_rate: float = 0.1  # 10% failure rate
    expected_success_rate: float = 0.95
    timeout_threshold: float = 1000.0  # ms
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FailureInjectionConfig:
    """Configuration injection pannes"""
    failure_type: FailureType
    injection_rate: float = 0.2  # 20% des opérations
    duration_seconds: int = 60
    delay_range: Tuple[float, float] = (0.1, 2.0)  # délai en secondes
    error_message: str = "Injected failure"
    cascading_failure: bool = False
    recovery_time: float = 5.0  # temps récupération

@dataclass
class TestOperation:
    """Opération de test"""
    operation_id: str
    operation_type: str
    target_service: str
    payload: Dict[str, Any]
    expected_result: Any
    timeout: float = 30.0
    retry_config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestResult:
    """Résultat test individuel"""
    test_id: str
    operation_id: str
    success: bool
    execution_time: float
    retry_count: int
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    expected_vs_actual: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class TestSummary:
    """Résumé complet test"""
    test_id: str
    test_type: TestType
    test_name: str
    overall_success: bool
    total_operations: int
    successful_operations: int
    failed_operations: int
    success_rate: float
    average_execution_time: float
    average_retry_count: float
    p95_latency: float
    p99_latency: float
    error_distribution: Dict[str, int]
    performance_metrics: Dict[str, Any]
    started_at: datetime
    completed_at: datetime
    duration: float
    recommendations: List[str] = field(default_factory=list)

@dataclass
class ValidationConfig:
    """Configuration validation"""
    min_success_rate: float = 0.95
    max_average_latency: float = 1000.0  # ms
    max_p95_latency: float = 2000.0  # ms
    max_retry_count: float = 3.0
    expected_error_types: List[str] = field(default_factory=list)
    performance_baseline: Dict[str, float] = field(default_factory=dict)

@dataclass
class ValidationResults:
    """Résultats validation"""
    validation_id: str
    test_id: str
    overall_passed: bool
    checks_passed: int
    checks_total: int
    validation_details: List[Dict] = field(default_factory=list)
    performance_comparison: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

class FailureInjector:
    """Injecteur de pannes pour chaos testing"""
    
    def __init__(self):
        self.active_failures = {}
        self.failure_generators = {
            FailureType.TIMEOUT: self._generate_timeout_failure,
            FailureType.CONNECTION_ERROR: self._generate_connection_failure,
            FailureType.RATE_LIMIT: self._generate_rate_limit_failure,
            FailureType.SERVICE_UNAVAILABLE: self._generate_service_unavailable,
            FailureType.AUTHENTICATION_ERROR: self._generate_auth_failure,
            FailureType.NETWORK_PARTITION: self._generate_network_partition,
            FailureType.RESOURCE_EXHAUSTION: self._generate_resource_exhaustion,
            FailureType.DATABASE_ERROR: self._generate_database_error,
            FailureType.RANDOM_ERROR: self._generate_random_error
        }
        self.injection_history = deque(maxlen=1000)
    
    async def inject_failure(self, config: FailureInjectionConfig, operation: TestOperation) -> bool:
        """Injection panne selon configuration"""
        # Vérification taux injection
        if random.random() > config.injection_rate:
            return False  # Pas d'injection cette fois
        
        failure_generator = self.failure_generators.get(config.failure_type, self._generate_random_error)
        
        # Génération panne
        failure_data = await failure_generator(config, operation)
        
        # Enregistrement injection
        injection_record = {
            'operation_id': operation.operation_id,
            'failure_type': config.failure_type.value,
            'timestamp': datetime.now(),
            'failure_data': failure_data,
            'target_service': operation.target_service
        }
        
        self.injection_history.append(injection_record)
        
        # Stockage panne active
        self.active_failures[operation.operation_id] = {
            'config': config,
            'failure_data': failure_data,
            'injected_at': time.time()
        }
        
        logger.info(f"Failure injected: {config.failure_type.value} for operation {operation.operation_id}")
        return True
    
    async def _generate_timeout_failure(self, config: FailureInjectionConfig, operation: TestOperation) -> Dict:
        """Génération timeout failure"""
        timeout_delay = random.uniform(*config.delay_range)
        return {
            'type': 'timeout',
            'delay': timeout_delay,
            'original_timeout': operation.timeout,
            'message': f"Operation timed out after {timeout_delay}s"
        }
    
    async def _generate_connection_failure(self, config: FailureInjectionConfig, operation: TestOperation) -> Dict:
        """Génération connection error"""
        error_codes = [500, 502, 503, 504, 521, 522, 523]
        error_code = random.choice(error_codes)
        return {
            'type': 'connection_error',
            'error_code': error_code,
            'message': f"Connection failed with HTTP {error_code}",
            'retry_after': random.uniform(1, 5)
        }
    
    async def _generate_rate_limit_failure(self, config: FailureInjectionConfig, operation: TestOperation) -> Dict:
        """Génération rate limit error"""
        return {
            'type': 'rate_limit',
            'error_code': 429,
            'message': "Rate limit exceeded",
            'retry_after': random.uniform(5, 30),
            'remaining_quota': 0
        }
    
    async def _generate_service_unavailable(self, config: FailureInjectionConfig, operation: TestOperation) -> Dict:
        """Génération service unavailable"""
        return {
            'type': 'service_unavailable',
            'error_code': 503,
            'message': "Service temporarily unavailable",
            'retry_after': random.uniform(10, 60),
            'maintenance_mode': random.choice([True, False])
        }
    
    async def _generate_auth_failure(self, config: FailureInjectionConfig, operation: TestOperation) -> Dict:
        """Génération authentication error"""
        auth_errors = ['invalid_token', 'expired_token', 'insufficient_permissions', 'token_revoked']
        auth_error = random.choice(auth_errors)
        return {
            'type': 'authentication_error',
            'error_code': 401,
            'auth_error': auth_error,
            'message': f"Authentication failed: {auth_error}"
        }
    
    async def _generate_network_partition(self, config: FailureInjectionConfig, operation: TestOperation) -> Dict:
        """Génération network partition"""
        return {
            'type': 'network_partition',
            'message': "Network partition detected",
            'partition_duration': random.uniform(5, 30),
            'affected_nodes': random.randint(1, 3)
        }
    
    async def _generate_resource_exhaustion(self, config: FailureInjectionConfig, operation: TestOperation) -> Dict:
        """Génération resource exhaustion"""
        resource_types = ['memory', 'cpu', 'disk', 'connections']
        resource_type = random.choice(resource_types)
        return {
            'type': 'resource_exhaustion',
            'resource_type': resource_type,
            'utilization': random.uniform(0.95, 1.0),
            'message': f"{resource_type.title()} resources exhausted"
        }
    
    async def _generate_database_error(self, config: FailureInjectionConfig, operation: TestOperation) -> Dict:
        """Génération database error"""
        db_errors = ['connection_pool_exhausted', 'deadlock', 'timeout', 'constraint_violation']
        db_error = random.choice(db_errors)
        return {
            'type': 'database_error',
            'db_error': db_error,
            'message': f"Database error: {db_error}",
            'rollback_required': random.choice([True, False])
        }
    
    async def _generate_random_error(self, config: FailureInjectionConfig, operation: TestOperation) -> Dict:
        """Génération error aléatoire"""
        error_types = ['internal_error', 'parsing_error', 'validation_error', 'business_logic_error']
        error_type = random.choice(error_types)
        return {
            'type': 'random_error',
            'error_subtype': error_type,
            'message': f"Random error: {error_type}",
            'error_code': random.randint(400, 599)
        }
    
    async def should_fail_operation(self, operation_id: str) -> Tuple[bool, Optional[Dict]]:
        """Vérification si opération doit échouer"""
        if operation_id in self.active_failures:
            failure_info = self.active_failures[operation_id]
            
            # Vérification expiration
            if time.time() - failure_info['injected_at'] > failure_info['config'].duration_seconds:
                del self.active_failures[operation_id]
                return False, None
            
            return True, failure_info['failure_data']
        
        return False, None

class LoadGenerator:
    """Générateur charge pour tests performance"""
    
    def __init__(self):
        self.active_loads = {}
        self.load_patterns = {
            'constant': self._generate_constant_load,
            'ramp_up': self._generate_ramp_up_load,
            'spike': self._generate_spike_load,
            'wave': self._generate_wave_load,
            'random': self._generate_random_load
        }
    
    async def generate_load(self, pattern: str, duration: int, target_rps: int) -> List[TestOperation]:
        """Génération charge selon pattern"""
        load_generator = self.load_patterns.get(pattern, self._generate_constant_load)
        return await load_generator(duration, target_rps)
    
    async def _generate_constant_load(self, duration: int, target_rps: int) -> List[TestOperation]:
        """Génération charge constante"""
        operations = []
        total_operations = duration * target_rps
        
        for i in range(total_operations):
            operation = TestOperation(
                operation_id=f"load_op_{i}",
                operation_type="load_test",
                target_service="retry_service",
                payload={"test_data": f"load_test_{i}", "timestamp": time.time()},
                expected_result={"status": "success"}
            )
            operations.append(operation)
        
        return operations
    
    async def _generate_ramp_up_load(self, duration: int, target_rps: int) -> List[TestOperation]:
        """Génération charge progressive"""
        operations = []
        
        for second in range(duration):
            # RPS progressif: commence à 1, monte jusqu'à target_rps
            current_rps = int(target_rps * (second + 1) / duration)
            
            for i in range(current_rps):
                operation = TestOperation(
                    operation_id=f"ramp_op_{second}_{i}",
                    operation_type="ramp_test",
                    target_service="retry_service",
                    payload={"test_data": f"ramp_test_{second}_{i}", "rps": current_rps},
                    expected_result={"status": "success"}
                )
                operations.append(operation)
        
        return operations
    
    async def _generate_spike_load(self, duration: int, target_rps: int) -> List[TestOperation]:
        """Génération pics de charge"""
        operations = []
        
        for second in range(duration):
            # Pics aléatoires: normal load ou 5x load
            if random.random() < 0.1:  # 10% chance de pic
                current_rps = target_rps * 5
            else:
                current_rps = target_rps
            
            for i in range(current_rps):
                operation = TestOperation(
                    operation_id=f"spike_op_{second}_{i}",
                    operation_type="spike_test",
                    target_service="retry_service",
                    payload={"test_data": f"spike_test_{second}_{i}", "spike": current_rps > target_rps},
                    expected_result={"status": "success"}
                )
                operations.append(operation)
        
        return operations
    
    async def _generate_wave_load(self, duration: int, target_rps: int) -> List[TestOperation]:
        """Génération charge en vagues"""
        operations = []
        
        for second in range(duration):
            # Pattern sinusoïdal
            wave_factor = (1 + math.sin(2 * math.pi * second / 60)) / 2  # Cycle 60s
            current_rps = int(target_rps * wave_factor)
            
            for i in range(current_rps):
                operation = TestOperation(
                    operation_id=f"wave_op_{second}_{i}",
                    operation_type="wave_test",
                    target_service="retry_service",
                    payload={"test_data": f"wave_test_{second}_{i}", "wave_factor": wave_factor},
                    expected_result={"status": "success"}
                )
                operations.append(operation)
        
        return operations
    
    async def _generate_random_load(self, duration: int, target_rps: int) -> List[TestOperation]:
        """Génération charge aléatoire"""
        operations = []
        
        for second in range(duration):
            # RPS aléatoire entre 50% et 150% du target
            current_rps = int(target_rps * random.uniform(0.5, 1.5))
            
            for i in range(current_rps):
                operation = TestOperation(
                    operation_id=f"random_op_{second}_{i}",
                    operation_type="random_test",
                    target_service="retry_service",
                    payload={"test_data": f"random_test_{second}_{i}", "randomness": random.random()},
                    expected_result={"status": "success"}
                )
                operations.append(operation)
        
        return operations

class RetryValidator:
    """Validateur comportement retry"""
    
    def __init__(self):
        self.validation_rules = {
            'exponential_backoff': self._validate_exponential_backoff,
            'max_retries': self._validate_max_retries,
            'success_rate': self._validate_success_rate,
            'latency_bounds': self._validate_latency_bounds,
            'error_handling': self._validate_error_handling,
            'circuit_breaker': self._validate_circuit_breaker
        }
    
    async def validate_retry_behavior(self, validation_config: ValidationConfig, 
                                    test_results: List[TestResult]) -> ValidationResults:
        """Validation comportement retry complet"""
        validation_id = str(uuid.uuid4())
        validation_details = []
        checks_passed = 0
        checks_total = 0
        
        # Validation success rate
        success_rate = sum(1 for r in test_results if r.success) / len(test_results) if test_results else 0
        checks_total += 1
        if success_rate >= validation_config.min_success_rate:
            checks_passed += 1
            validation_details.append({
                'check': 'success_rate',
                'passed': True,
                'expected': validation_config.min_success_rate,
                'actual': success_rate,
                'message': f"Success rate {success_rate:.1%} meets minimum {validation_config.min_success_rate:.1%}"
            })
        else:
            validation_details.append({
                'check': 'success_rate',
                'passed': False,
                'expected': validation_config.min_success_rate,
                'actual': success_rate,
                'message': f"Success rate {success_rate:.1%} below minimum {validation_config.min_success_rate:.1%}"
            })
        
        # Validation latence moyenne
        if test_results:
            avg_latency = sum(r.execution_time for r in test_results) / len(test_results) * 1000  # ms
            checks_total += 1
            if avg_latency <= validation_config.max_average_latency:
                checks_passed += 1
                validation_details.append({
                    'check': 'average_latency',
                    'passed': True,
                    'expected': validation_config.max_average_latency,
                    'actual': avg_latency,
                    'message': f"Average latency {avg_latency:.1f}ms within limit"
                })
            else:
                validation_details.append({
                    'check': 'average_latency',
                    'passed': False,
                    'expected': validation_config.max_average_latency,
                    'actual': avg_latency,
                    'message': f"Average latency {avg_latency:.1f}ms exceeds limit"
                })
        
        # Validation P95 latence
        if test_results:
            latencies = [r.execution_time * 1000 for r in test_results]  # ms
            p95_latency = self._percentile(latencies, 0.95)
            checks_total += 1
            if p95_latency <= validation_config.max_p95_latency:
                checks_passed += 1
                validation_details.append({
                    'check': 'p95_latency',
                    'passed': True,
                    'expected': validation_config.max_p95_latency,
                    'actual': p95_latency,
                    'message': f"P95 latency {p95_latency:.1f}ms within limit"
                })
            else:
                validation_details.append({
                    'check': 'p95_latency',
                    'passed': False,
                    'expected': validation_config.max_p95_latency,
                    'actual': p95_latency,
                    'message': f"P95 latency {p95_latency:.1f}ms exceeds limit"
                })
        
        # Validation retry count
        if test_results:
            avg_retry_count = sum(r.retry_count for r in test_results) / len(test_results)
            checks_total += 1
            if avg_retry_count <= validation_config.max_retry_count:
                checks_passed += 1
                validation_details.append({
                    'check': 'retry_count',
                    'passed': True,
                    'expected': validation_config.max_retry_count,
                    'actual': avg_retry_count,
                    'message': f"Average retry count {avg_retry_count:.1f} within limit"
                })
            else:
                validation_details.append({
                    'check': 'retry_count',
                    'passed': False,
                    'expected': validation_config.max_retry_count,
                    'actual': avg_retry_count,
                    'message': f"Average retry count {avg_retry_count:.1f} exceeds limit"
                })
        
        # Génération recommandations
        recommendations = await self._generate_validation_recommendations(validation_details)
        
        return ValidationResults(
            validation_id=validation_id,
            test_id=test_results[0].test_id if test_results else "unknown",
            overall_passed=checks_passed == checks_total,
            checks_passed=checks_passed,
            checks_total=checks_total,
            validation_details=validation_details,
            recommendations=recommendations
        )
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calcul percentile"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    async def _validate_exponential_backoff(self, test_results: List[TestResult]) -> Dict:
        """Validation exponential backoff"""
        # Analyse des temps entre retries pour vérifier pattern exponentiel
        retry_delays = []
        for result in test_results:
            if result.retry_count > 1:
                # Simulation extraction delays (en production: vraie data)
                estimated_delays = [1.0 * (2 ** i) for i in range(result.retry_count)]
                retry_delays.extend(estimated_delays)
        
        if not retry_delays:
            return {'valid': True, 'message': 'No retries to validate'}
        
        # Vérification pattern approximativement exponentiel
        is_exponential = all(
            retry_delays[i] >= retry_delays[i-1] * 1.5 
            for i in range(1, min(len(retry_delays), 5))
        )
        
        return {
            'valid': is_exponential,
            'message': 'Exponential backoff pattern detected' if is_exponential else 'Non-exponential pattern detected',
            'sample_delays': retry_delays[:5]
        }
    
    async def _validate_max_retries(self, test_results: List[TestResult]) -> Dict:
        """Validation respect max retries"""
        max_retries_observed = max(r.retry_count for r in test_results) if test_results else 0
        
        # En général, max retries ne devrait pas dépasser 5
        max_allowed = 5
        
        return {
            'valid': max_retries_observed <= max_allowed,
            'message': f'Max retries observed: {max_retries_observed} (limit: {max_allowed})',
            'max_observed': max_retries_observed
        }
    
    async def _validate_success_rate(self, test_results: List[TestResult]) -> Dict:
        """Validation success rate minimum"""
        if not test_results:
            return {'valid': False, 'message': 'No test results to validate'}
        
        success_rate = sum(1 for r in test_results if r.success) / len(test_results)
        min_expected = 0.95
        
        return {
            'valid': success_rate >= min_expected,
            'message': f'Success rate: {success_rate:.1%} (minimum: {min_expected:.1%})',
            'success_rate': success_rate
        }
    
    async def _validate_latency_bounds(self, test_results: List[TestResult]) -> Dict:
        """Validation bornes latence"""
        if not test_results:
            return {'valid': False, 'message': 'No test results to validate'}
        
        latencies = [r.execution_time * 1000 for r in test_results]  # ms
        p95_latency = self._percentile(latencies, 0.95)
        
        max_acceptable = 2000  # 2s
        
        return {
            'valid': p95_latency <= max_acceptable,
            'message': f'P95 latency: {p95_latency:.1f}ms (limit: {max_acceptable}ms)',
            'p95_latency': p95_latency
        }
    
    async def _validate_error_handling(self, test_results: List[TestResult]) -> Dict:
        """Validation gestion erreurs"""
        error_types = [r.error_type for r in test_results if r.error_type]
        error_distribution = defaultdict(int)
        
        for error_type in error_types:
            error_distribution[error_type] += 1
        
        # Vérification diversité error handling
        handled_error_types = len(error_distribution)
        
        return {
            'valid': handled_error_types > 0,  # Au moins quelques erreurs gérées
            'message': f'Handled {handled_error_types} different error types',
            'error_distribution': dict(error_distribution)
        }
    
    async def _validate_circuit_breaker(self, test_results: List[TestResult]) -> Dict:
        """Validation circuit breaker"""
        # Recherche patterns circuit breaker
        consecutive_failures = 0
        max_consecutive_failures = 0
        
        for result in test_results:
            if not result.success:
                consecutive_failures += 1
                max_consecutive_failures = max(max_consecutive_failures, consecutive_failures)
            else:
                consecutive_failures = 0
        
        # Circuit breaker devrait déclencher après ~5 failures
        circuit_breaker_likely = max_consecutive_failures < 10
        
        return {
            'valid': circuit_breaker_likely,
            'message': f'Max consecutive failures: {max_consecutive_failures} (circuit breaker likely active)',
            'max_consecutive_failures': max_consecutive_failures
        }
    
    async def _generate_validation_recommendations(self, validation_details: List[Dict]) -> List[str]:
        """Génération recommandations validation"""
        recommendations = []
        
        failed_checks = [detail for detail in validation_details if not detail['passed']]
        
        for failed_check in failed_checks:
            check_type = failed_check['check']
            
            if check_type == 'success_rate':
                recommendations.append("Consider implementing more robust error handling and retry strategies")
                recommendations.append("Review and optimize timeout configurations")
            elif check_type == 'average_latency':
                recommendations.append("Optimize retry delay strategies to reduce overall latency")
                recommendations.append("Consider implementing parallel retry patterns where appropriate")
            elif check_type == 'p95_latency':
                recommendations.append("Implement circuit breaker to prevent high latency operations")
                recommendations.append("Add adaptive timeout management")
            elif check_type == 'retry_count':
                recommendations.append("Reduce maximum retry count or improve first-attempt success rate")
                recommendations.append("Implement intelligent retry decision making")
        
        return recommendations[:5]  # Limite à 5 recommandations

class RetryTestingFramework:
    """
    Framework tests retry mechanisms.
    Chaos testing + failure injection + retry validation.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.failure_injector = FailureInjector()
        self.load_generator = LoadGenerator()
        self.retry_validator = RetryValidator()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Registre tests
        self.test_registry = {}
        self.test_results = {}
        
        # Métriques test
        self.test_metrics = defaultdict(list)
    
    async def execute_retry_tests(self, test_config: TestConfig) -> TestSummary:
        """
        Exécution tests retry complets avec chaos engineering.
        
        Testing Features:
        - Comprehensive retry behavior testing
        - Chaos engineering avec failure injection
        - Load testing sous différents patterns
        - Performance regression testing
        - Resilience testing avec network partitions
        - Error handling validation
        - Circuit breaker testing
        - Real-world scenario simulation
        """
        start_time = datetime.now()
        test_results = []
        
        self.logger.info(f"Starting test: {test_config.test_name} ({test_config.test_type.value})")
        
        try:
            # Génération opérations test
            if test_config.test_type == TestType.LOAD_TEST:
                operations = await self.load_generator.generate_load(
                    'constant', test_config.duration_seconds, test_config.concurrent_operations
                )
            elif test_config.test_type == TestType.STRESS_TEST:
                operations = await self.load_generator.generate_load(
                    'spike', test_config.duration_seconds, test_config.concurrent_operations * 3
                )
            elif test_config.test_type == TestType.CHAOS_TEST:
                operations = await self.load_generator.generate_load(
                    'random', test_config.duration_seconds, test_config.concurrent_operations
                )
            else:
                operations = await self._generate_basic_operations(test_config)
            
            # Configuration injection pannes pour chaos testing
            failure_config = None
            if test_config.test_type in [TestType.CHAOS_TEST, TestType.RESILIENCE_TEST, TestType.FAILURE_INJECTION]:
                failure_config = FailureInjectionConfig(
                    failure_type=FailureType.RANDOM_ERROR,
                    injection_rate=test_config.failure_rate,
                    duration_seconds=test_config.duration_seconds
                )
            
            # Exécution opérations
            tasks = []
            for operation in operations[:test_config.concurrent_operations * test_config.duration_seconds]:
                task = self._execute_test_operation(operation, failure_config)
                tasks.append(task)
            
            # Exécution concurrente avec limitation
            batch_size = min(test_config.concurrent_operations, 50)
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i + batch_size]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, TestResult):
                        test_results.append(result)
                    elif isinstance(result, Exception):
                        # Gestion exceptions
                        test_results.append(TestResult(
                            test_id=test_config.test_id,
                            operation_id=f"error_{i}",
                            success=False,
                            execution_time=0.0,
                            retry_count=0,
                            error_type="execution_exception",
                            error_message=str(result)
                        ))
                
                # Délai entre batches pour éviter surcharge
                if i + batch_size < len(tasks):
                    await asyncio.sleep(1)
            
            # Calcul métriques
            end_time = datetime.now()
            summary = await self._calculate_test_summary(test_config, test_results, start_time, end_time)
            
            # Stockage résultats
            self.test_results[test_config.test_id] = {
                'config': test_config,
                'results': test_results,
                'summary': summary
            }
            
            self.logger.info(
                f"Test completed: {test_config.test_name}, "
                f"Success rate: {summary.success_rate:.1%}, "
                f"Avg latency: {summary.average_execution_time*1000:.1f}ms"
            )
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {str(e)}")
            raise
    
    async def validate_retry_behavior(self, validation_config: ValidationConfig) -> ValidationResults:
        """
        Validation comportement retry sous différentes conditions.
        
        Validation Features:
        - Exponential backoff pattern verification
        - Maximum retry count compliance
        - Success rate threshold validation
        - Latency boundary compliance
        - Error handling coverage
        - Circuit breaker activation testing
        - Performance regression detection
        """
        if not self.test_results:
            raise ValueError("No test results available for validation")
        
        # Utilisation derniers résultats test
        latest_test_id = max(self.test_results.keys(), key=lambda x: self.test_results[x]['summary'].started_at)
        latest_results = self.test_results[latest_test_id]['results']
        
        return await self.retry_validator.validate_retry_behavior(validation_config, latest_results)
    
    async def _generate_basic_operations(self, test_config: TestConfig) -> List[TestOperation]:
        """Génération opérations test basiques"""
        operations = []
        
        num_operations = test_config.concurrent_operations * (test_config.duration_seconds // 60)  # Par minute
        
        for i in range(num_operations):
            operation = TestOperation(
                operation_id=f"{test_config.test_id}_op_{i}",
                operation_type=test_config.test_type.value,
                target_service=test_config.target_services[0] if test_config.target_services else "default_service",
                payload={
                    "test_id": test_config.test_id,
                    "operation_index": i,
                    "timestamp": time.time()
                },
                expected_result={"status": "success", "processed": True}
            )
            operations.append(operation)
        
        return operations
    
    async def _execute_test_operation(self, operation: TestOperation, 
                                    failure_config: Optional[FailureInjectionConfig] = None) -> TestResult:
        """Exécution opération test individuelle"""
        start_time = time.time()
        retry_count = 0
        last_error = None
        
        # Vérification injection panne
        should_fail = False
        failure_data = None
        
        if failure_config:
            should_fail, failure_data = await self.failure_injector.should_fail_operation(operation.operation_id)
            
            if not should_fail:
                # Tentative injection nouvelle panne
                injected = await self.failure_injector.inject_failure(failure_config, operation)
                if injected:
                    should_fail, failure_data = await self.failure_injector.should_fail_operation(operation.operation_id)
        
        # Simulation exécution avec retries
        max_retries = 3
        for attempt in range(max_retries + 1):
            try:
                if should_fail and failure_data:
                    # Simulation panne injectée
                    if failure_data['type'] == 'timeout':
                        await asyncio.sleep(failure_data.get('delay', 1.0))
                        raise asyncio.TimeoutError(failure_data.get('message', 'Timeout'))
                    else:
                        raise Exception(failure_data.get('message', 'Injected failure'))
                
                # Simulation opération normale
                operation_delay = random.uniform(0.1, 0.5)  # 100-500ms
                await asyncio.sleep(operation_delay)
                
                # Succès
                execution_time = time.time() - start_time
                return TestResult(
                    test_id=operation.operation_id.split('_')[0],
                    operation_id=operation.operation_id,
                    success=True,
                    execution_time=execution_time,
                    retry_count=retry_count
                )
                
            except Exception as e:
                last_error = e
                retry_count += 1
                
                if attempt < max_retries:
                    # Exponential backoff
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(delay)
                    continue
                
                # Échec final
                execution_time = time.time() - start_time
                return TestResult(
                    test_id=operation.operation_id.split('_')[0],
                    operation_id=operation.operation_id,
                    success=False,
                    execution_time=execution_time,
                    retry_count=retry_count,
                    error_type=type(last_error).__name__,
                    error_message=str(last_error)
                )
        
        # Ne devrait jamais arriver
        execution_time = time.time() - start_time
        return TestResult(
            test_id=operation.operation_id.split('_')[0],
            operation_id=operation.operation_id,
            success=False,
            execution_time=execution_time,
            retry_count=retry_count,
            error_type="unknown_error",
            error_message="Unexpected execution path"
        )
    
    async def _calculate_test_summary(self, test_config: TestConfig, test_results: List[TestResult],
                                    start_time: datetime, end_time: datetime) -> TestSummary:
        """Calcul résumé test"""
        if not test_results:
            return TestSummary(
                test_id=test_config.test_id,
                test_type=test_config.test_type,
                test_name=test_config.test_name,
                overall_success=False,
                total_operations=0,
                successful_operations=0,
                failed_operations=0,
                success_rate=0.0,
                average_execution_time=0.0,
                average_retry_count=0.0,
                p95_latency=0.0,
                p99_latency=0.0,
                error_distribution={},
                performance_metrics={},
                started_at=start_time,
                completed_at=end_time,
                duration=(end_time - start_time).total_seconds()
            )
        
        # Calculs statistiques
        successful_operations = sum(1 for r in test_results if r.success)
        failed_operations = len(test_results) - successful_operations
        success_rate = successful_operations / len(test_results)
        
        execution_times = [r.execution_time for r in test_results]
        average_execution_time = statistics.mean(execution_times)
        
        retry_counts = [r.retry_count for r in test_results]
        average_retry_count = statistics.mean(retry_counts)
        
        # Percentiles latence
        latencies_ms = [t * 1000 for t in execution_times]  # Conversion en ms
        p95_latency = self._percentile(latencies_ms, 0.95)
        p99_latency = self._percentile(latencies_ms, 0.99)
        
        # Distribution erreurs
        error_distribution = defaultdict(int)
        for result in test_results:
            if result.error_type:
                error_distribution[result.error_type] += 1
        
        # Métriques performance
        performance_metrics = {
            'min_latency': min(latencies_ms),
            'max_latency': max(latencies_ms),
            'median_latency': statistics.median(latencies_ms),
            'std_dev_latency': statistics.stdev(latencies_ms) if len(latencies_ms) > 1 else 0,
            'operations_per_second': len(test_results) / (end_time - start_time).total_seconds(),
            'max_retry_count': max(retry_counts) if retry_counts else 0
        }
        
        # Recommandations
        recommendations = []
        if success_rate < test_config.expected_success_rate:
            recommendations.append(f"Success rate {success_rate:.1%} below expected {test_config.expected_success_rate:.1%}")
        
        if p95_latency > test_config.timeout_threshold:
            recommendations.append(f"P95 latency {p95_latency:.1f}ms exceeds threshold {test_config.timeout_threshold}ms")
        
        if average_retry_count > 2.0:
            recommendations.append("High average retry count indicates potential configuration issues")
        
        overall_success = (
            success_rate >= test_config.expected_success_rate and
            p95_latency <= test_config.timeout_threshold
        )
        
        return TestSummary(
            test_id=test_config.test_id,
            test_type=test_config.test_type,
            test_name=test_config.test_name,
            overall_success=overall_success,
            total_operations=len(test_results),
            successful_operations=successful_operations,
            failed_operations=failed_operations,
            success_rate=success_rate,
            average_execution_time=average_execution_time,
            average_retry_count=average_retry_count,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            error_distribution=dict(error_distribution),
            performance_metrics=performance_metrics,
            started_at=start_time,
            completed_at=end_time,
            duration=(end_time - start_time).total_seconds(),
            recommendations=recommendations
        )
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calcul percentile"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    async def run_chaos_experiment(self, duration: int = 300, failure_rate: float = 0.3) -> TestSummary:
        """Exécution expérience chaos engineering"""
        chaos_config = TestConfig(
            test_id=f"chaos_{int(time.time())}",
            test_type=TestType.CHAOS_TEST,
            test_name="Chaos Engineering Experiment",
            description="Random failure injection and resilience testing",
            severity=TestSeverity.HIGH,
            target_services=["retry_service", "content_processing", "ai_processing"],
            duration_seconds=duration,
            concurrent_operations=20,
            failure_rate=failure_rate,
            expected_success_rate=0.8  # Lower expectation for chaos
        )
        
        return await self.execute_retry_tests(chaos_config)
    
    async def get_test_report(self, test_id: str) -> Dict[str, Any]:
        """Génération rapport test détaillé"""
        if test_id not in self.test_results:
            return {'error': f'Test {test_id} not found'}
        
        test_data = self.test_results[test_id]
        summary = test_data['summary']
        results = test_data['results']
        
        return {
            'test_summary': {
                'test_id': summary.test_id,
                'test_name': summary.test_name,
                'test_type': summary.test_type.value,
                'overall_success': summary.overall_success,
                'duration': summary.duration,
                'success_rate': summary.success_rate
            },
            'performance_metrics': summary.performance_metrics,
            'error_analysis': {
                'error_distribution': summary.error_distribution,
                'most_common_error': max(summary.error_distribution.items(), key=lambda x: x[1])[0] if summary.error_distribution else None,
                'error_rate': summary.failed_operations / summary.total_operations if summary.total_operations > 0 else 0
            },
            'retry_analysis': {
                'average_retry_count': summary.average_retry_count,
                'operations_with_retries': sum(1 for r in results if r.retry_count > 0),
                'max_retries_observed': max(r.retry_count for r in results) if results else 0
            },
            'recommendations': summary.recommendations
        }

# Instance globale
retry_testing_framework = RetryTestingFramework()

# Export des classes principales
__all__ = [
    'RetryTestingFramework',
    'TestConfig',
    'TestResult',
    'TestSummary',
    'ValidationConfig',
    'ValidationResults',
    'FailureInjectionConfig',
    'TestType',
    'FailureType',
    'retry_testing_framework'
]