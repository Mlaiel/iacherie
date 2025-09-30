"""
Chaos Engineering Integration - Enterprise Circuit Breakers
Advanced fault injection and resilience testing integration

This module provides controlled chaos engineering capabilities integrated with
circuit breakers, enabling comprehensive resilience testing and validation.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
            Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - PROTECTION FORTE
Cette implémentation est la propriété exclusive de Fahed Mlaiel.
Toute reproduction ou utilisation non autorisée est strictement interdite.
"""

import asyncio
import logging
import time
import uuid
import random
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from datetime import datetime, timedelta
import aiohttp
import statistics
from collections import defaultdict, deque
import psutil


logger = logging.getLogger(__name__)


class ChaosExperimentType(Enum):
    """Types of chaos experiments"""
    LATENCY_INJECTION = "latency_injection"
    ERROR_INJECTION = "error_injection"
    NETWORK_PARTITION = "network_partition"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SERVICE_KILL = "service_kill"
    DEPENDENCY_FAILURE = "dependency_failure"
    DATABASE_CHAOS = "database_chaos"
    MEMORY_PRESSURE = "memory_pressure"
    CPU_SPIKE = "cpu_spike"
    DISK_IO_STRESS = "disk_io_stress"


class ChaosScope(Enum):
    """Scope of chaos experiments"""
    SERVICE = "service"
    CLUSTER = "cluster"
    REGION = "region"
    DEPENDENCY = "dependency"
    INFRASTRUCTURE = "infrastructure"


class ExperimentStatus(Enum):
    """Chaos experiment execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLBACK = "rollback"


class ValidationResult(Enum):
    """Circuit breaker validation results"""
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    INCONCLUSIVE = "inconclusive"


@dataclass
class ChaosConfig:
    """Chaos experiment configuration"""
    experiment_name: str
    experiment_type: ChaosExperimentType
    scope: ChaosScope = ChaosScope.SERVICE
    target_services: List[str] = field(default_factory=list)
    duration_seconds: int = 300
    intensity: float = 0.5  # 0.0 to 1.0
    ramp_up_seconds: int = 30
    ramp_down_seconds: int = 30
    circuit_breaker_validation: bool = True
    auto_rollback: bool = True
    safety_checks: bool = True
    blast_radius_limit: int = 1  # Maximum number of services to affect
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentResult:
    """Chaos experiment execution result"""
    experiment_id: str
    experiment_name: str
    status: ExperimentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    circuit_validation_result: Optional[ValidationResult] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    observations: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    recovery_time_seconds: Optional[float] = None
    blast_radius: int = 0


@dataclass
class CircuitBehaviorObservation:
    """Circuit breaker behavior observation during chaos"""
    timestamp: datetime
    service_name: str
    circuit_state: str
    failure_count: int
    success_count: int
    response_time: float
    error_rate: float
    recovery_indicator: bool


class LatencyInjector:
    """Network latency injection for chaos testing"""
    
    def __init__(self):
        self.active_injections: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def inject_latency(self, target_service: str, latency_ms: int, 
                           percentage: float = 100.0) -> str:
        """Inject network latency for target service"""
        injection_id = str(uuid.uuid4())
        
        injection_config = {
            'target_service': target_service,
            'latency_ms': latency_ms,
            'percentage': percentage,
            'start_time': datetime.now(),
            'active': True
        }
        
        self.active_injections[injection_id] = injection_config
        
        # Start latency injection task
        task = asyncio.create_task(self._latency_injection_loop(injection_id))
        injection_config['task'] = task
        
        self.logger.info(f"💉 Latency injection started: {latency_ms}ms for {target_service} ({percentage}%)")
        return injection_id
    
    async def _latency_injection_loop(self, injection_id: str):
        """Latency injection execution loop"""
        injection = self.active_injections.get(injection_id)
        if not injection:
            return
        
        try:
            while injection.get('active', False):
                # Simulate latency injection
                if random.random() * 100 <= injection['percentage']:
                    delay = injection['latency_ms'] / 1000.0
                    await asyncio.sleep(delay)
                
                await asyncio.sleep(0.1)  # Check every 100ms
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"❌ Latency injection error: {e}")
    
    async def stop_injection(self, injection_id: str) -> bool:
        """Stop latency injection"""
        if injection_id in self.active_injections:
            injection = self.active_injections[injection_id]
            injection['active'] = False
            
            if 'task' in injection:
                injection['task'].cancel()
                try:
                    await injection['task']
                except asyncio.CancelledError:
                    pass
            
            del self.active_injections[injection_id]
            self.logger.info(f"⏹️ Latency injection stopped: {injection_id}")
            return True
        
        return False


class ErrorInjector:
    """Error injection for chaos testing"""
    
    def __init__(self):
        self.active_injections: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def inject_errors(self, target_service: str, error_rate: float, 
                          error_types: List[str] = None) -> str:
        """Inject errors for target service"""
        if error_types is None:
            error_types = ['500', '503', '504', 'timeout', 'connection_refused']
        
        injection_id = str(uuid.uuid4())
        
        injection_config = {
            'target_service': target_service,
            'error_rate': error_rate,
            'error_types': error_types,
            'start_time': datetime.now(),
            'active': True,
            'injected_errors': 0
        }
        
        self.active_injections[injection_id] = injection_config
        
        # Start error injection task
        task = asyncio.create_task(self._error_injection_loop(injection_id))
        injection_config['task'] = task
        
        self.logger.info(f"💀 Error injection started: {error_rate*100}% for {target_service}")
        return injection_id
    
    async def _error_injection_loop(self, injection_id: str):
        """Error injection execution loop"""
        injection = self.active_injections.get(injection_id)
        if not injection:
            return
        
        try:
            while injection.get('active', False):
                # Simulate error injection
                if random.random() <= injection['error_rate']:
                    error_type = random.choice(injection['error_types'])
                    injection['injected_errors'] += 1
                    
                    self.logger.debug(f"💥 Injected error: {error_type} for {injection['target_service']}")
                
                await asyncio.sleep(1.0)  # Check every second
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"❌ Error injection error: {e}")
    
    async def stop_injection(self, injection_id: str) -> bool:
        """Stop error injection"""
        if injection_id in self.active_injections:
            injection = self.active_injections[injection_id]
            injection['active'] = False
            
            if 'task' in injection:
                injection['task'].cancel()
                try:
                    await injection['task']
                except asyncio.CancelledError:
                    pass
            
            total_errors = injection.get('injected_errors', 0)
            del self.active_injections[injection_id]
            
            self.logger.info(f"⏹️ Error injection stopped: {injection_id} (total errors: {total_errors})")
            return True
        
        return False


class NetworkPartitioner:
    """Network partition simulation for chaos testing"""
    
    def __init__(self):
        self.active_partitions: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def create_partition(self, services_a: List[str], services_b: List[str], 
                             partition_type: str = "full") -> str:
        """Create network partition between service groups"""
        partition_id = str(uuid.uuid4())
        
        partition_config = {
            'services_a': services_a,
            'services_b': services_b,
            'partition_type': partition_type,  # full, partial, asymmetric
            'start_time': datetime.now(),
            'active': True
        }
        
        self.active_partitions[partition_id] = partition_config
        
        # Start partition simulation task
        task = asyncio.create_task(self._partition_simulation_loop(partition_id))
        partition_config['task'] = task
        
        self.logger.info(f"🔌 Network partition created: {services_a} ↔ {services_b} ({partition_type})")
        return partition_id
    
    async def _partition_simulation_loop(self, partition_id: str):
        """Network partition simulation loop"""
        partition = self.active_partitions.get(partition_id)
        if not partition:
            return
        
        try:
            while partition.get('active', False):
                # Simulate network partition effects
                # In a real implementation, this would use network tools like iptables, tc, etc.
                
                partition_type = partition['partition_type']
                
                if partition_type == 'full':
                    # Complete network isolation
                    packet_loss = 100.0
                elif partition_type == 'partial':
                    # Partial connectivity with high packet loss
                    packet_loss = random.uniform(70.0, 95.0)
                elif partition_type == 'asymmetric':
                    # One-way communication failure
                    packet_loss = random.choice([0.0, 100.0])
                else:
                    packet_loss = 50.0
                
                # Log partition effects
                self.logger.debug(f"🌐 Partition {partition_id}: {packet_loss}% packet loss")
                
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"❌ Network partition error: {e}")
    
    async def heal_partition(self, partition_id: str) -> bool:
        """Heal network partition"""
        if partition_id in self.active_partitions:
            partition = self.active_partitions[partition_id]
            partition['active'] = False
            
            if 'task' in partition:
                partition['task'].cancel()
                try:
                    await partition['task']
                except asyncio.CancelledError:
                    pass
            
            del self.active_partitions[partition_id]
            self.logger.info(f"🔗 Network partition healed: {partition_id}")
            return True
        
        return False


class ResourceExhauster:
    """Resource exhaustion simulation for chaos testing"""
    
    def __init__(self):
        self.active_exhaustions: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def exhaust_memory(self, target_service: str, memory_mb: int) -> str:
        """Exhaust memory resources"""
        exhaustion_id = str(uuid.uuid4())
        
        exhaustion_config = {
            'target_service': target_service,
            'resource_type': 'memory',
            'memory_mb': memory_mb,
            'start_time': datetime.now(),
            'active': True,
            'memory_blocks': []
        }
        
        self.active_exhaustions[exhaustion_id] = exhaustion_config
        
        # Start memory exhaustion task
        task = asyncio.create_task(self._memory_exhaustion_loop(exhaustion_id))
        exhaustion_config['task'] = task
        
        self.logger.info(f"💾 Memory exhaustion started: {memory_mb}MB for {target_service}")
        return exhaustion_id
    
    async def _memory_exhaustion_loop(self, exhaustion_id: str):
        """Memory exhaustion execution loop"""
        exhaustion = self.active_exhaustions.get(exhaustion_id)
        if not exhaustion:
            return
        
        try:
            target_mb = exhaustion['memory_mb']
            allocated_mb = 0
            
            while exhaustion.get('active', False) and allocated_mb < target_mb:
                # Allocate memory in chunks
                chunk_size = min(10, target_mb - allocated_mb)  # 10MB chunks
                memory_block = bytearray(chunk_size * 1024 * 1024)
                exhaustion['memory_blocks'].append(memory_block)
                allocated_mb += chunk_size
                
                self.logger.debug(f"💾 Allocated {allocated_mb}MB / {target_mb}MB")
                await asyncio.sleep(1.0)
            
            # Keep memory allocated while active
            while exhaustion.get('active', False):
                await asyncio.sleep(5.0)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"❌ Memory exhaustion error: {e}")
        finally:
            # Clean up memory blocks
            if exhaustion_id in self.active_exhaustions:
                self.active_exhaustions[exhaustion_id]['memory_blocks'].clear()
    
    async def exhaust_cpu(self, target_service: str, cpu_percentage: int) -> str:
        """Exhaust CPU resources"""
        exhaustion_id = str(uuid.uuid4())
        
        exhaustion_config = {
            'target_service': target_service,
            'resource_type': 'cpu',
            'cpu_percentage': cpu_percentage,
            'start_time': datetime.now(),
            'active': True
        }
        
        self.active_exhaustions[exhaustion_id] = exhaustion_config
        
        # Start CPU exhaustion task
        task = asyncio.create_task(self._cpu_exhaustion_loop(exhaustion_id))
        exhaustion_config['task'] = task
        
        self.logger.info(f"🔥 CPU exhaustion started: {cpu_percentage}% for {target_service}")
        return exhaustion_id
    
    async def _cpu_exhaustion_loop(self, exhaustion_id: str):
        """CPU exhaustion execution loop"""
        exhaustion = self.active_exhaustions.get(exhaustion_id)
        if not exhaustion:
            return
        
        try:
            cpu_percentage = exhaustion['cpu_percentage'] / 100.0
            
            while exhaustion.get('active', False):
                # CPU intensive work
                work_time = cpu_percentage
                sleep_time = 1.0 - work_time
                
                # Simulate CPU load
                start_time = time.time()
                while time.time() - start_time < work_time:
                    _ = sum(i * i for i in range(1000))  # CPU intensive calculation
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"❌ CPU exhaustion error: {e}")
    
    async def stop_exhaustion(self, exhaustion_id: str) -> bool:
        """Stop resource exhaustion"""
        if exhaustion_id in self.active_exhaustions:
            exhaustion = self.active_exhaustions[exhaustion_id]
            exhaustion['active'] = False
            
            if 'task' in exhaustion:
                exhaustion['task'].cancel()
                try:
                    await exhaustion['task']
                except asyncio.CancelledError:
                    pass
            
            resource_type = exhaustion.get('resource_type', 'unknown')
            del self.active_exhaustions[exhaustion_id]
            
            self.logger.info(f"⏹️ {resource_type.title()} exhaustion stopped: {exhaustion_id}")
            return True
        
        return False


class CircuitBehaviorValidator:
    """Circuit breaker behavior validation during chaos experiments"""
    
    def __init__(self):
        self.observations: deque = deque(maxlen=1000)
        self.validation_rules: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def add_validation_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """Add circuit breaker validation rule"""
        self.validation_rules[rule_name] = rule_config
        self.logger.info(f"📋 Added validation rule: {rule_name}")
    
    async def observe_circuit_behavior(self, service_name: str, circuit_state: str, 
                                     metrics: Dict[str, Any]):
        """Record circuit breaker behavior observation"""
        observation = CircuitBehaviorObservation(
            timestamp=datetime.now(),
            service_name=service_name,
            circuit_state=circuit_state,
            failure_count=metrics.get('failure_count', 0),
            success_count=metrics.get('success_count', 0),
            response_time=metrics.get('response_time', 0.0),
            error_rate=metrics.get('error_rate', 0.0),
            recovery_indicator=metrics.get('recovery_indicator', False)
        )
        
        self.observations.append(observation)
        self.logger.debug(f"📊 Circuit observation: {service_name} {circuit_state}")
    
    async def validate_circuit_behavior(self, validation_scenarios: Dict[str, Any]) -> Dict[str, Any]:
        """Validate circuit breaker behavior against scenarios"""
        results = {}
        
        for scenario_name, scenario_config in validation_scenarios.items():
            try:
                result = await self._validate_scenario(scenario_name, scenario_config)
                results[scenario_name] = result
            except Exception as e:
                results[scenario_name] = {
                    'result': ValidationResult.FAILED,
                    'error': str(e)
                }
        
        # Calculate overall validation result
        overall_result = ValidationResult.PASSED
        if any(r.get('result') == ValidationResult.FAILED for r in results.values()):
            overall_result = ValidationResult.FAILED
        elif any(r.get('result') == ValidationResult.PARTIAL for r in results.values()):
            overall_result = ValidationResult.PARTIAL
        
        return {
            'overall_result': overall_result,
            'scenario_results': results,
            'total_observations': len(self.observations),
            'validation_timestamp': datetime.now().isoformat()
        }
    
    async def _validate_scenario(self, scenario_name: str, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate specific scenario"""
        service_name = scenario_config.get('service_name')
        expected_behavior = scenario_config.get('expected_behavior', {})
        
        # Filter observations for this service
        service_observations = [obs for obs in self.observations 
                              if obs.service_name == service_name]
        
        if not service_observations:
            return {
                'result': ValidationResult.INCONCLUSIVE,
                'reason': 'No observations available'
            }
        
        # Validate circuit state transitions
        state_validation = await self._validate_state_transitions(
            service_observations, expected_behavior.get('state_transitions', [])
        )
        
        # Validate recovery behavior
        recovery_validation = await self._validate_recovery_behavior(
            service_observations, expected_behavior.get('recovery', {})
        )
        
        # Validate response time behavior
        response_time_validation = await self._validate_response_times(
            service_observations, expected_behavior.get('response_times', {})
        )
        
        # Determine overall scenario result
        validations = [state_validation, recovery_validation, response_time_validation]
        passed_validations = sum(1 for v in validations if v['passed'])
        
        if passed_validations == len(validations):
            result = ValidationResult.PASSED
        elif passed_validations > 0:
            result = ValidationResult.PARTIAL
        else:
            result = ValidationResult.FAILED
        
        return {
            'result': result,
            'passed_validations': passed_validations,
            'total_validations': len(validations),
            'state_validation': state_validation,
            'recovery_validation': recovery_validation,
            'response_time_validation': response_time_validation
        }
    
    async def _validate_state_transitions(self, observations: List[CircuitBehaviorObservation], 
                                        expected_transitions: List[str]) -> Dict[str, Any]:
        """Validate circuit state transitions"""
        if not expected_transitions:
            return {'passed': True, 'reason': 'No state transitions to validate'}
        
        # Extract state sequence from observations
        state_sequence = [obs.circuit_state for obs in observations]
        
        # Check if expected transitions occurred
        transitions_found = []
        for i in range(len(state_sequence) - 1):
            transition = f"{state_sequence[i]} -> {state_sequence[i+1]}"
            if transition in expected_transitions:
                transitions_found.append(transition)
        
        missing_transitions = set(expected_transitions) - set(transitions_found)
        
        return {
            'passed': len(missing_transitions) == 0,
            'found_transitions': transitions_found,
            'missing_transitions': list(missing_transitions),
            'state_sequence': state_sequence
        }
    
    async def _validate_recovery_behavior(self, observations: List[CircuitBehaviorObservation], 
                                        recovery_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate circuit recovery behavior"""
        if not recovery_config:
            return {'passed': True, 'reason': 'No recovery behavior to validate'}
        
        max_recovery_time = recovery_config.get('max_recovery_time_seconds', 300)
        min_success_rate = recovery_config.get('min_success_rate', 0.8)
        
        # Find recovery periods (transitions from OPEN to CLOSED)
        recovery_periods = []
        for i in range(len(observations) - 1):
            if (observations[i].circuit_state == 'OPEN' and 
                observations[i+1].circuit_state in ['HALF_OPEN', 'CLOSED']):
                
                # Find when it fully closes
                recovery_start = observations[i].timestamp
                recovery_end = None
                
                for j in range(i+1, len(observations)):
                    if observations[j].circuit_state == 'CLOSED':
                        recovery_end = observations[j].timestamp
                        break
                
                if recovery_end:
                    recovery_time = (recovery_end - recovery_start).total_seconds()
                    recovery_periods.append(recovery_time)
        
        # Validate recovery times
        slow_recoveries = [t for t in recovery_periods if t > max_recovery_time]
        avg_recovery_time = statistics.mean(recovery_periods) if recovery_periods else 0
        
        # Validate success rate after recovery
        success_rates_after_recovery = []
        for obs in observations:
            if obs.circuit_state == 'CLOSED' and obs.recovery_indicator:
                total_requests = obs.success_count + obs.failure_count
                if total_requests > 0:
                    success_rate = obs.success_count / total_requests
                    success_rates_after_recovery.append(success_rate)
        
        avg_success_rate = statistics.mean(success_rates_after_recovery) if success_rates_after_recovery else 1.0
        
        passed = (len(slow_recoveries) == 0 and avg_success_rate >= min_success_rate)
        
        return {
            'passed': passed,
            'recovery_periods': recovery_periods,
            'avg_recovery_time': avg_recovery_time,
            'slow_recoveries': slow_recoveries,
            'avg_success_rate_after_recovery': avg_success_rate,
            'min_required_success_rate': min_success_rate
        }
    
    async def _validate_response_times(self, observations: List[CircuitBehaviorObservation], 
                                     response_time_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response time behavior"""
        if not response_time_config:
            return {'passed': True, 'reason': 'No response time behavior to validate'}
        
        max_response_time = response_time_config.get('max_response_time_seconds', 5.0)
        max_degradation_factor = response_time_config.get('max_degradation_factor', 3.0)
        
        response_times = [obs.response_time for obs in observations if obs.response_time > 0]
        
        if not response_times:
            return {'passed': True, 'reason': 'No response time data available'}
        
        # Calculate metrics
        avg_response_time = statistics.mean(response_times)
        max_observed_response_time = max(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
        
        # Validate against thresholds
        slow_responses = [t for t in response_times if t > max_response_time]
        degradation_violations = [t for t in response_times if t > avg_response_time * max_degradation_factor]
        
        passed = (len(slow_responses) / len(response_times) < 0.1 and  # Less than 10% slow responses
                 len(degradation_violations) == 0)
        
        return {
            'passed': passed,
            'avg_response_time': avg_response_time,
            'max_response_time': max_observed_response_time,
            'p95_response_time': p95_response_time,
            'slow_responses_count': len(slow_responses),
            'degradation_violations_count': len(degradation_violations),
            'total_responses': len(response_times)
        }


class ChaosEngineeringIntegration:
    """
    Enterprise chaos engineering integration for circuit breakers.
    Provides controlled fault injection and resilience testing.
    """
    
    def __init__(self):
        """Initialize chaos engineering integration"""
        self.latency_injector = LatencyInjector()
        self.error_injector = ErrorInjector()
        self.network_partitioner = NetworkPartitioner()
        self.resource_exhauster = ResourceExhauster()
        self.circuit_validator = CircuitBehaviorValidator()
        
        self.active_experiments: Dict[str, Dict[str, Any]] = {}
        self.experiment_history: List[ExperimentResult] = []
        self.safety_checks_enabled = True
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize default validation rules
        self._initialize_default_validation_rules()
        
        self.logger.info("🔬 Chaos Engineering Integration initialized - Resilience testing ready")
    
    def _initialize_default_validation_rules(self):
        """Initialize default circuit breaker validation rules"""
        self.circuit_validator.add_validation_rule("fast_circuit_opening", {
            'max_failures_before_open': 5,
            'max_time_to_open_seconds': 30
        })
        
        self.circuit_validator.add_validation_rule("proper_recovery", {
            'max_recovery_time_seconds': 300,
            'min_success_rate_after_recovery': 0.9
        })
        
        self.circuit_validator.add_validation_rule("graceful_degradation", {
            'max_response_time_degradation_factor': 2.0,
            'max_error_rate_during_recovery': 0.1
        })
    
    async def inject_controlled_failures(self, chaos_config: Dict[str, Any]) -> Dict[str, Any]:
        """Inject controlled failures for circuit breaker testing"""
        try:
            experiment_id = str(uuid.uuid4())
            config = ChaosConfig(**chaos_config)
            
            # Safety checks
            if self.safety_checks_enabled:
                safety_check = await self._perform_safety_checks(config)
                if not safety_check['safe']:
                    return {
                        'experiment_id': experiment_id,
                        'status': 'cancelled',
                        'reason': 'Safety checks failed',
                        'safety_check': safety_check
                    }
            
            # Create experiment record
            experiment = {
                'experiment_id': experiment_id,
                'config': config,
                'start_time': datetime.now(),
                'status': ExperimentStatus.RUNNING,
                'injections': [],
                'observations': []
            }
            
            self.active_experiments[experiment_id] = experiment
            
            # Start experiment execution
            execution_task = asyncio.create_task(self._execute_chaos_experiment(experiment_id))
            experiment['execution_task'] = execution_task
            
            self.logger.info(f"🚀 Chaos experiment started: {config.experiment_name} ({experiment_id})")
            
            return {
                'experiment_id': experiment_id,
                'experiment_name': config.experiment_name,
                'status': 'started',
                'estimated_duration_seconds': config.duration_seconds + config.ramp_up_seconds + config.ramp_down_seconds,
                'target_services': config.target_services
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to inject controlled failures: {e}")
            raise
    
    async def _perform_safety_checks(self, config: ChaosConfig) -> Dict[str, Any]:
        """Perform safety checks before running experiment"""
        checks = []
        
        # Check blast radius
        if len(config.target_services) > config.blast_radius_limit:
            checks.append({
                'check': 'blast_radius',
                'passed': False,
                'reason': f'Too many target services ({len(config.target_services)} > {config.blast_radius_limit})'
            })
        else:
            checks.append({
                'check': 'blast_radius',
                'passed': True
            })
        
        # Check system resources
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        
        if cpu_usage > 80:
            checks.append({
                'check': 'system_cpu',
                'passed': False,
                'reason': f'High CPU usage: {cpu_usage}%'
            })
        else:
            checks.append({'check': 'system_cpu', 'passed': True})
        
        if memory_usage > 85:
            checks.append({
                'check': 'system_memory',
                'passed': False,
                'reason': f'High memory usage: {memory_usage}%'
            })
        else:
            checks.append({'check': 'system_memory', 'passed': True})
        
        # Check for conflicting experiments
        conflicting_experiments = []
        for exp_id, exp in self.active_experiments.items():
            if exp['status'] == ExperimentStatus.RUNNING:
                exp_targets = set(exp['config'].target_services)
                config_targets = set(config.target_services)
                if exp_targets.intersection(config_targets):
                    conflicting_experiments.append(exp_id)
        
        if conflicting_experiments:
            checks.append({
                'check': 'experiment_conflicts',
                'passed': False,
                'reason': f'Conflicting experiments: {conflicting_experiments}'
            })
        else:
            checks.append({'check': 'experiment_conflicts', 'passed': True})
        
        all_passed = all(check['passed'] for check in checks)
        
        return {
            'safe': all_passed,
            'checks': checks,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _execute_chaos_experiment(self, experiment_id: str):
        """Execute chaos experiment"""
        experiment = self.active_experiments.get(experiment_id)
        if not experiment:
            return
        
        config = experiment['config']
        
        try:
            # Ramp up phase
            self.logger.info(f"📈 Ramping up experiment {experiment_id}")
            await self._ramp_up_experiment(experiment_id)
            
            # Main experiment phase
            self.logger.info(f"🧪 Running main experiment phase {experiment_id}")
            await self._run_main_experiment(experiment_id)
            
            # Ramp down phase
            self.logger.info(f"📉 Ramping down experiment {experiment_id}")
            await self._ramp_down_experiment(experiment_id)
            
            # Validation phase
            if config.circuit_breaker_validation:
                self.logger.info(f"✅ Validating circuit breaker behavior {experiment_id}")
                validation_result = await self._validate_experiment(experiment_id)
                experiment['validation_result'] = validation_result
            
            # Complete experiment
            experiment['status'] = ExperimentStatus.COMPLETED
            experiment['end_time'] = datetime.now()
            experiment['duration_seconds'] = (experiment['end_time'] - experiment['start_time']).total_seconds()
            
            # Create experiment result
            result = await self._create_experiment_result(experiment_id)
            self.experiment_history.append(result)
            
            self.logger.info(f"✅ Chaos experiment completed: {experiment_id}")
            
        except Exception as e:
            experiment['status'] = ExperimentStatus.FAILED
            experiment['error'] = str(e)
            self.logger.error(f"❌ Chaos experiment failed: {experiment_id} - {e}")
        
        finally:
            # Cleanup
            await self._cleanup_experiment(experiment_id)
    
    async def _ramp_up_experiment(self, experiment_id: str):
        """Ramp up chaos experiment gradually"""
        experiment = self.active_experiments[experiment_id]
        config = experiment['config']
        
        if config.ramp_up_seconds <= 0:
            return await self._apply_full_chaos(experiment_id)
        
        steps = min(10, config.ramp_up_seconds)  # Max 10 ramp-up steps
        step_duration = config.ramp_up_seconds / steps
        
        for step in range(steps):
            intensity = (step + 1) / steps * config.intensity
            await self._apply_chaos_with_intensity(experiment_id, intensity)
            await asyncio.sleep(step_duration)
    
    async def _run_main_experiment(self, experiment_id: str):
        """Run main experiment phase"""
        experiment = self.active_experiments[experiment_id]
        config = experiment['config']
        
        # Apply full chaos intensity
        await self._apply_full_chaos(experiment_id)
        
        # Monitor for the duration
        monitoring_interval = 10  # seconds
        total_time = 0
        
        while total_time < config.duration_seconds and experiment['status'] == ExperimentStatus.RUNNING:
            await asyncio.sleep(monitoring_interval)
            total_time += monitoring_interval
            
            # Collect circuit breaker observations
            await self._collect_circuit_observations(experiment_id)
    
    async def _ramp_down_experiment(self, experiment_id: str):
        """Ramp down chaos experiment gradually"""
        experiment = self.active_experiments[experiment_id]
        config = experiment['config']
        
        if config.ramp_down_seconds <= 0:
            return await self._stop_all_chaos(experiment_id)
        
        steps = min(10, config.ramp_down_seconds)  # Max 10 ramp-down steps
        step_duration = config.ramp_down_seconds / steps
        
        for step in range(steps):
            intensity = (steps - step) / steps * config.intensity
            await self._apply_chaos_with_intensity(experiment_id, intensity)
            await asyncio.sleep(step_duration)
        
        # Ensure all chaos is stopped
        await self._stop_all_chaos(experiment_id)
    
    async def _apply_full_chaos(self, experiment_id: str):
        """Apply full chaos intensity"""
        experiment = self.active_experiments[experiment_id]
        config = experiment['config']
        
        await self._apply_chaos_with_intensity(experiment_id, config.intensity)
    
    async def _apply_chaos_with_intensity(self, experiment_id: str, intensity: float):
        """Apply chaos with specific intensity"""
        experiment = self.active_experiments[experiment_id]
        config = experiment['config']
        
        # Stop existing injections first
        await self._stop_current_injections(experiment_id)
        
        for service in config.target_services:
            if config.experiment_type == ChaosExperimentType.LATENCY_INJECTION:
                latency_ms = int(config.metadata.get('latency_ms', 1000) * intensity)
                percentage = config.metadata.get('percentage', 100) * intensity
                
                injection_id = await self.latency_injector.inject_latency(
                    service, latency_ms, percentage
                )
                experiment['injections'].append({
                    'type': 'latency',
                    'service': service,
                    'injection_id': injection_id,
                    'intensity': intensity
                })
            
            elif config.experiment_type == ChaosExperimentType.ERROR_INJECTION:
                error_rate = config.metadata.get('error_rate', 0.5) * intensity
                error_types = config.metadata.get('error_types', ['500', '503'])
                
                injection_id = await self.error_injector.inject_errors(
                    service, error_rate, error_types
                )
                experiment['injections'].append({
                    'type': 'error',
                    'service': service,
                    'injection_id': injection_id,
                    'intensity': intensity
                })
            
            elif config.experiment_type == ChaosExperimentType.RESOURCE_EXHAUSTION:
                resource_type = config.metadata.get('resource_type', 'memory')
                
                if resource_type == 'memory':
                    memory_mb = int(config.metadata.get('memory_mb', 500) * intensity)
                    injection_id = await self.resource_exhauster.exhaust_memory(service, memory_mb)
                elif resource_type == 'cpu':
                    cpu_percentage = int(config.metadata.get('cpu_percentage', 80) * intensity)
                    injection_id = await self.resource_exhauster.exhaust_cpu(service, cpu_percentage)
                else:
                    continue
                
                experiment['injections'].append({
                    'type': 'resource_exhaustion',
                    'service': service,
                    'injection_id': injection_id,
                    'intensity': intensity,
                    'resource_type': resource_type
                })
    
    async def _stop_current_injections(self, experiment_id: str):
        """Stop current chaos injections"""
        experiment = self.active_experiments[experiment_id]
        
        for injection in experiment.get('injections', []):
            try:
                injection_type = injection['type']
                injection_id = injection['injection_id']
                
                if injection_type == 'latency':
                    await self.latency_injector.stop_injection(injection_id)
                elif injection_type == 'error':
                    await self.error_injector.stop_injection(injection_id)
                elif injection_type == 'resource_exhaustion':
                    await self.resource_exhauster.stop_exhaustion(injection_id)
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to stop injection {injection.get('injection_id')}: {e}")
        
        experiment['injections'] = []
    
    async def _stop_all_chaos(self, experiment_id: str):
        """Stop all chaos injections"""
        await self._stop_current_injections(experiment_id)
    
    async def _collect_circuit_observations(self, experiment_id: str):
        """Collect circuit breaker observations during experiment"""
        experiment = self.active_experiments[experiment_id]
        config = experiment['config']
        
        for service in config.target_services:
            # In a real implementation, this would query actual circuit breaker state
            # For demo purposes, we'll simulate observations
            
            circuit_state = random.choice(['CLOSED', 'OPEN', 'HALF_OPEN'])
            metrics = {
                'failure_count': random.randint(0, 10),
                'success_count': random.randint(5, 50),
                'response_time': random.uniform(0.1, 2.0),
                'error_rate': random.uniform(0.0, 0.3),
                'recovery_indicator': circuit_state == 'CLOSED'
            }
            
            await self.circuit_validator.observe_circuit_behavior(service, circuit_state, metrics)
            
            experiment['observations'].append({
                'timestamp': datetime.now().isoformat(),
                'service': service,
                'circuit_state': circuit_state,
                'metrics': metrics
            })
    
    async def _validate_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Validate experiment results"""
        experiment = self.active_experiments[experiment_id]
        config = experiment['config']
        
        validation_scenarios = {}
        
        for service in config.target_services:
            validation_scenarios[f"{service}_behavior"] = {
                'service_name': service,
                'expected_behavior': {
                    'state_transitions': ['CLOSED -> OPEN', 'OPEN -> HALF_OPEN', 'HALF_OPEN -> CLOSED'],
                    'recovery': {
                        'max_recovery_time_seconds': 300,
                        'min_success_rate': 0.8
                    },
                    'response_times': {
                        'max_response_time_seconds': 5.0,
                        'max_degradation_factor': 3.0
                    }
                }
            }
        
        return await self.circuit_validator.validate_circuit_behavior(validation_scenarios)
    
    async def _create_experiment_result(self, experiment_id: str) -> ExperimentResult:
        """Create experiment result record"""
        experiment = self.active_experiments[experiment_id]
        config = experiment['config']
        
        result = ExperimentResult(
            experiment_id=experiment_id,
            experiment_name=config.experiment_name,
            status=experiment['status'],
            start_time=experiment['start_time'],
            end_time=experiment.get('end_time'),
            duration_seconds=experiment.get('duration_seconds'),
            circuit_validation_result=experiment.get('validation_result', {}).get('overall_result'),
            metrics={
                'total_injections': len(experiment.get('injections', [])),
                'total_observations': len(experiment.get('observations', [])),
                'target_services': len(config.target_services),
                'experiment_type': config.experiment_type.value,
                'intensity': config.intensity
            },
            blast_radius=len(config.target_services)
        )
        
        return result
    
    async def _cleanup_experiment(self, experiment_id: str):
        """Cleanup experiment resources"""
        if experiment_id in self.active_experiments:
            experiment = self.active_experiments[experiment_id]
            
            # Stop all injections
            await self._stop_all_chaos(experiment_id)
            
            # Cancel execution task if still running
            execution_task = experiment.get('execution_task')
            if execution_task and not execution_task.done():
                execution_task.cancel()
                try:
                    await execution_task
                except asyncio.CancelledError:
                    pass
            
            # Remove from active experiments
            del self.active_experiments[experiment_id]
    
    async def simulate_network_partitions(self, partition_scenarios: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate network partitions for resilience testing"""
        try:
            results = {}
            
            for scenario_name, scenario_config in partition_scenarios.items():
                services_a = scenario_config.get('services_a', [])
                services_b = scenario_config.get('services_b', [])
                partition_type = scenario_config.get('partition_type', 'full')
                duration_seconds = scenario_config.get('duration_seconds', 60)
                
                # Create network partition
                partition_id = await self.network_partitioner.create_partition(
                    services_a, services_b, partition_type
                )
                
                # Let partition run for specified duration
                await asyncio.sleep(duration_seconds)
                
                # Heal partition
                await self.network_partitioner.heal_partition(partition_id)
                
                results[scenario_name] = {
                    'partition_id': partition_id,
                    'services_a': services_a,
                    'services_b': services_b,
                    'partition_type': partition_type,
                    'duration_seconds': duration_seconds,
                    'status': 'completed'
                }
                
                self.logger.info(f"🌐 Network partition scenario completed: {scenario_name}")
            
            return {
                'total_scenarios': len(partition_scenarios),
                'completed_scenarios': len(results),
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to simulate network partitions: {e}")
            raise
    
    async def validate_circuit_behavior(self, validation_scenarios: Dict[str, Any]) -> Dict[str, Any]:
        """Validate circuit breaker behavior under chaos conditions"""
        try:
            return await self.circuit_validator.validate_circuit_behavior(validation_scenarios)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to validate circuit behavior: {e}")
            raise
    
    async def get_experiment_status(self, experiment_id: Optional[str] = None) -> Dict[str, Any]:
        """Get chaos experiment status"""
        try:
            if experiment_id:
                # Single experiment status
                if experiment_id not in self.active_experiments:
                    # Check experiment history
                    for result in self.experiment_history:
                        if result.experiment_id == experiment_id:
                            return {
                                'experiment_id': experiment_id,
                                'status': result.status.value,
                                'result': result,
                                'source': 'history'
                            }
                    
                    return {'error': f'Experiment {experiment_id} not found'}
                
                experiment = self.active_experiments[experiment_id]
                return {
                    'experiment_id': experiment_id,
                    'status': experiment['status'].value,
                    'config': experiment['config'].__dict__,
                    'start_time': experiment['start_time'].isoformat(),
                    'current_injections': len(experiment.get('injections', [])),
                    'observations_count': len(experiment.get('observations', [])),
                    'source': 'active'
                }
            else:
                # System-wide status
                return {
                    'active_experiments': len(self.active_experiments),
                    'completed_experiments': len(self.experiment_history),
                    'active_latency_injections': len(self.latency_injector.active_injections),
                    'active_error_injections': len(self.error_injector.active_injections),
                    'active_network_partitions': len(self.network_partitioner.active_partitions),
                    'active_resource_exhaustions': len(self.resource_exhauster.active_exhaustions),
                    'total_circuit_observations': len(self.circuit_validator.observations),
                    'safety_checks_enabled': self.safety_checks_enabled,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get experiment status: {e}")
            raise
    
    async def emergency_stop_all_experiments(self) -> Dict[str, Any]:
        """Emergency stop all running chaos experiments"""
        try:
            stopped_experiments = []
            
            for experiment_id in list(self.active_experiments.keys()):
                try:
                    await self._cleanup_experiment(experiment_id)
                    stopped_experiments.append(experiment_id)
                    self.logger.warning(f"🛑 Emergency stopped experiment: {experiment_id}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to stop experiment {experiment_id}: {e}")
            
            return {
                'stopped_experiments': stopped_experiments,
                'total_stopped': len(stopped_experiments),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to perform emergency stop: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup chaos engineering integration"""
        try:
            # Stop all active experiments
            await self.emergency_stop_all_experiments()
            
            # Clear history
            self.experiment_history.clear()
            
            self.logger.info("🧹 Chaos Engineering Integration cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")


# Global chaos engineering integration instance
chaos_engineering = ChaosEngineeringIntegration()


# Export main classes and functions
__all__ = [
    'ChaosEngineeringIntegration',
    'ChaosConfig',
    'ChaosExperimentType',
    'ChaosScope',
    'ExperimentStatus',
    'ValidationResult',
    'ExperimentResult',
    'CircuitBehaviorObservation',
    'LatencyInjector',
    'ErrorInjector',
    'NetworkPartitioner',
    'ResourceExhauster',
    'CircuitBehaviorValidator',
    'chaos_engineering'
]


if __name__ == "__main__":
    async def demo():
        """Demo chaos engineering integration functionality"""
        integration = ChaosEngineeringIntegration()
        
        # Configure chaos experiment
        chaos_config = {
            'experiment_name': 'user_service_resilience_test',
            'experiment_type': 'LATENCY_INJECTION',
            'target_services': ['user-service'],
            'duration_seconds': 60,
            'intensity': 0.7,
            'ramp_up_seconds': 10,
            'ramp_down_seconds': 10,
            'circuit_breaker_validation': True,
            'metadata': {
                'latency_ms': 2000,
                'percentage': 80
            }
        }
        
        # Start chaos experiment
        result = await integration.inject_controlled_failures(chaos_config)
        print(f"Chaos experiment: {json.dumps(result, indent=2)}")
        
        # Wait for experiment to run
        experiment_id = result['experiment_id']
        await asyncio.sleep(5)
        
        # Check status
        status = await integration.get_experiment_status(experiment_id)
        print(f"Experiment status: {json.dumps(status, indent=2, default=str)}")
        
        # Wait for completion (in real scenario)
        # await asyncio.sleep(90)
        
        # Emergency stop for demo
        await integration.emergency_stop_all_experiments()
        
        # Cleanup
        await integration.cleanup()
    
    # Run demo
    asyncio.run(demo())