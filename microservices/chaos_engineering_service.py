"""Chaos Engineering Service - Resilience testing and validation
Enterprise-grade chaos engineering implementation for the Ainflue AI platform.

This service implements chaos engineering practices to test system resilience,
identify weaknesses, and validate failure recovery mechanisms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import random
import json
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
import psutil
import os
import signal
from pathlib import Path


class ChaosType(Enum):
    """Types of chaos experiments."""
    LATENCY_INJECTION = "latency_injection"
    SERVICE_FAILURE = "service_failure"
    NETWORK_PARTITION = "network_partition"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATA_CORRUPTION = "data_corruption"
    DEPENDENCY_FAILURE = "dependency_failure"
    TRAFFIC_SPIKE = "traffic_spike"
    DISK_FAILURE = "disk_failure"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"


class ExperimentState(Enum):
    """Chaos experiment states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class SafetyLevel(Enum):
    """Safety levels for chaos experiments."""
    LOW = "low"          # Can run in production with approval
    MEDIUM = "medium"    # Staging environment only
    HIGH = "high"        # Development environment only
    CRITICAL = "critical"  # Local testing only


@dataclass
class ChaosExperiment:
    """Represents a chaos engineering experiment."""
    id: str
    name: str
    description: str
    chaos_type: ChaosType
    target_services: List[str]
    duration_seconds: int
    parameters: Dict[str, Any] = field(default_factory=dict)
    safety_level: SafetyLevel = SafetyLevel.MEDIUM
    state: ExperimentState = ExperimentState.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    results: Dict[str, Any] = field(default_factory=dict)
    metrics_before: Dict[str, Any] = field(default_factory=dict)
    metrics_after: Dict[str, Any] = field(default_factory=dict)
    recovery_time: Optional[float] = None
    errors: List[str] = field(default_factory=list)


@dataclass
class ChaosMetrics:
    """Metrics collected during chaos experiments."""
    timestamp: float = field(default_factory=time.time)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_connections: int = 0
    disk_io: Dict[str, float] = field(default_factory=dict)
    response_times: List[float] = field(default_factory=list)
    error_rates: Dict[str, float] = field(default_factory=dict)
    service_health: Dict[str, bool] = field(default_factory=dict)


class ChaosEngineeringService:
    """Enterprise chaos engineering service for resilience testing."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the chaos engineering service.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.experiments: Dict[str, ChaosExperiment] = {}
        self.active_experiments: Dict[str, asyncio.Task] = {}
        self.safety_checks_enabled = True
        self.monitoring_enabled = True
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="chaos-eng")
        
        # Metrics collection
        self.metrics_history: List[ChaosMetrics] = []
        self.max_metrics_history = 1000
        
        # Safety thresholds
        self.safety_thresholds = {
            'max_cpu_usage': 90.0,
            'max_memory_usage': 85.0,
            'max_error_rate': 0.5,
            'min_healthy_services': 0.7,
            'max_concurrent_experiments': 3
        }
        
        # Built-in experiment templates
        self.experiment_templates = self._create_experiment_templates()
        
        # Load configuration if provided
        if config_path:
            self._load_configuration(config_path)
        
        self.logger.info(f"ChaosEngineeringService initialized for {self.environment} environment")
    
    def _create_experiment_templates(self) -> Dict[str, Dict[str, Any]]:
        """Create built-in experiment templates."""
        return {
            'latency_spike': {
                'name': 'Latency Spike Test',
                'description': 'Inject artificial latency to test timeout handling',
                'chaos_type': ChaosType.LATENCY_INJECTION,
                'duration_seconds': 300,
                'parameters': {
                    'min_delay_ms': 500,
                    'max_delay_ms': 2000,
                    'affected_percentage': 0.1
                },
                'safety_level': SafetyLevel.LOW
            },
            'service_shutdown': {
                'name': 'Service Shutdown Test',
                'description': 'Gracefully shutdown service to test failover',
                'chaos_type': ChaosType.SERVICE_FAILURE,
                'duration_seconds': 180,
                'parameters': {
                    'shutdown_type': 'graceful',
                    'recovery_delay': 30
                },
                'safety_level': SafetyLevel.MEDIUM
            },
            'memory_pressure': {
                'name': 'Memory Pressure Test',
                'description': 'Create memory pressure to test resource handling',
                'chaos_type': ChaosType.MEMORY_STRESS,
                'duration_seconds': 240,
                'parameters': {
                    'memory_percentage': 70,
                    'ramp_up_time': 30
                },
                'safety_level': SafetyLevel.MEDIUM
            },
            'cpu_spike': {
                'name': 'CPU Spike Test',
                'description': 'Create CPU spike to test performance under load',
                'chaos_type': ChaosType.CPU_STRESS,
                'duration_seconds': 180,
                'parameters': {
                    'cpu_percentage': 80,
                    'burst_duration': 30
                },
                'safety_level': SafetyLevel.MEDIUM
            },
            'network_partition': {
                'name': 'Network Partition Test',
                'description': 'Simulate network partition between services',
                'chaos_type': ChaosType.NETWORK_PARTITION,
                'duration_seconds': 300,
                'parameters': {
                    'partition_percentage': 0.3,
                    'recovery_time': 60
                },
                'safety_level': SafetyLevel.HIGH
            },
            'traffic_flood': {
                'name': 'Traffic Flood Test',
                'description': 'Generate traffic spike to test auto-scaling',
                'chaos_type': ChaosType.TRAFFIC_SPIKE,
                'duration_seconds': 600,
                'parameters': {
                    'requests_per_second': 1000,
                    'ramp_up_time': 60
                },
                'safety_level': SafetyLevel.MEDIUM
            }
        }
    
    async def create_experiment(self, template_name: str, target_services: List[str],
                              custom_parameters: Optional[Dict[str, Any]] = None) -> str:
        """Create a new chaos experiment from a template.
        
        Args:
            template_name: Name of the experiment template
            target_services: List of target service names
            custom_parameters: Optional custom parameters to override defaults
            
        Returns:
            Experiment ID
        """
        try:
            if template_name not in self.experiment_templates:
                raise ValueError(f"Unknown experiment template: {template_name}")
            
            template = self.experiment_templates[template_name].copy()
            
            # Override parameters if provided
            if custom_parameters:
                template['parameters'].update(custom_parameters)
            
            # Generate unique experiment ID
            experiment_id = f"chaos-{int(time.time())}-{random.randint(1000, 9999)}"
            
            # Create experiment
            experiment = ChaosExperiment(
                id=experiment_id,
                name=template['name'],
                description=template['description'],
                chaos_type=template['chaos_type'],
                target_services=target_services,
                duration_seconds=template['duration_seconds'],
                parameters=template['parameters'],
                safety_level=template['safety_level']
            )
            
            # Validate experiment safety
            if not self._validate_experiment_safety(experiment):
                raise ValueError("Experiment failed safety validation")
            
            with self._lock:
                self.experiments[experiment_id] = experiment
            
            self.logger.info(f"Created chaos experiment: {experiment_id} - {template['name']}")
            return experiment_id
            
        except Exception as e:
            self.logger.error(f"Failed to create experiment: {e}")
            raise
    
    async def start_experiment(self, experiment_id: str) -> bool:
        """Start a chaos experiment.
        
        Args:
            experiment_id: ID of the experiment to start
            
        Returns:
            True if experiment started successfully
        """
        try:
            if experiment_id not in self.experiments:
                self.logger.error(f"Experiment {experiment_id} not found")
                return False
            
            experiment = self.experiments[experiment_id]
            
            # Check if already running
            if experiment.state == ExperimentState.RUNNING:
                self.logger.warning(f"Experiment {experiment_id} is already running")
                return False
            
            # Safety checks
            if not self._can_start_experiment(experiment):
                self.logger.error(f"Safety checks failed for experiment {experiment_id}")
                return False
            
            # Start experiment task
            task = asyncio.create_task(self._run_experiment(experiment))
            self.active_experiments[experiment_id] = task
            
            experiment.state = ExperimentState.RUNNING
            experiment.started_at = time.time()
            
            self.logger.info(f"Started chaos experiment: {experiment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start experiment {experiment_id}: {e}")
            return False
    
    async def stop_experiment(self, experiment_id: str, reason: str = "Manual stop") -> bool:
        """Stop a running chaos experiment.
        
        Args:
            experiment_id: ID of the experiment to stop
            reason: Reason for stopping
            
        Returns:
            True if experiment stopped successfully
        """
        try:
            if experiment_id not in self.experiments:
                self.logger.error(f"Experiment {experiment_id} not found")
                return False
            
            experiment = self.experiments[experiment_id]
            
            # Cancel the experiment task
            if experiment_id in self.active_experiments:
                task = self.active_experiments[experiment_id]
                task.cancel()
                
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                del self.active_experiments[experiment_id]
            
            # Update experiment state
            experiment.state = ExperimentState.CANCELLED
            experiment.completed_at = time.time()
            experiment.errors.append(f"Stopped: {reason}")
            
            # Ensure cleanup
            await self._cleanup_experiment(experiment)
            
            self.logger.info(f"Stopped chaos experiment: {experiment_id} - {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop experiment {experiment_id}: {e}")
            return False
    
    async def _run_experiment(self, experiment: ChaosExperiment) -> None:
        """Run a chaos experiment.
        
        Args:
            experiment: Experiment to run
        """
        try:
            self.logger.info(f"Running chaos experiment: {experiment.id} - {experiment.name}")
            
            # Collect baseline metrics
            experiment.metrics_before = await self._collect_metrics(experiment.target_services)
            
            # Execute the chaos action
            await self._execute_chaos_action(experiment)
            
            # Monitor during experiment
            await self._monitor_experiment(experiment)
            
            # Wait for experiment duration
            await asyncio.sleep(experiment.duration_seconds)
            
            # Cleanup and recovery
            await self._cleanup_experiment(experiment)
            
            # Collect post-experiment metrics
            experiment.metrics_after = await self._collect_metrics(experiment.target_services)
            
            # Calculate recovery time
            experiment.recovery_time = await self._measure_recovery_time(experiment)
            
            # Mark as completed
            experiment.state = ExperimentState.COMPLETED
            experiment.completed_at = time.time()
            
            # Generate results
            experiment.results = await self._generate_experiment_results(experiment)
            
            self.logger.info(f"Completed chaos experiment: {experiment.id}")
            
        except asyncio.CancelledError:
            self.logger.info(f"Chaos experiment cancelled: {experiment.id}")
            await self._cleanup_experiment(experiment)
            raise
        except Exception as e:
            self.logger.error(f"Error in chaos experiment {experiment.id}: {e}")
            experiment.state = ExperimentState.FAILED
            experiment.errors.append(str(e))
            await self._cleanup_experiment(experiment)
        finally:
            # Remove from active experiments
            if experiment.id in self.active_experiments:
                del self.active_experiments[experiment.id]
    
    async def _execute_chaos_action(self, experiment: ChaosExperiment) -> None:
        """Execute the specific chaos action for an experiment.
        
        Args:
            experiment: Experiment to execute
        """
        chaos_type = experiment.chaos_type
        parameters = experiment.parameters
        
        if chaos_type == ChaosType.LATENCY_INJECTION:
            await self._inject_latency(experiment)
        elif chaos_type == ChaosType.SERVICE_FAILURE:
            await self._simulate_service_failure(experiment)
        elif chaos_type == ChaosType.NETWORK_PARTITION:
            await self._simulate_network_partition(experiment)
        elif chaos_type == ChaosType.RESOURCE_EXHAUSTION:
            await self._exhaust_resources(experiment)
        elif chaos_type == ChaosType.CPU_STRESS:
            await self._stress_cpu(experiment)
        elif chaos_type == ChaosType.MEMORY_STRESS:
            await self._stress_memory(experiment)
        elif chaos_type == ChaosType.TRAFFIC_SPIKE:
            await self._generate_traffic_spike(experiment)
        else:
            self.logger.warning(f"Unsupported chaos type: {chaos_type}")
    
    async def _inject_latency(self, experiment: ChaosExperiment) -> None:
        """Inject artificial latency into target services.
        
        Args:
            experiment: Experiment configuration
        """
        parameters = experiment.parameters
        min_delay = parameters.get('min_delay_ms', 100) / 1000.0
        max_delay = parameters.get('max_delay_ms', 500) / 1000.0
        
        self.logger.info(f"Injecting latency: {min_delay*1000}ms - {max_delay*1000}ms")
        
        # This would integrate with service mesh or proxy to inject actual latency
        # For now, we simulate by adding delays to service calls
        experiment.results['latency_injected'] = True
        experiment.results['latency_range'] = f"{min_delay*1000}-{max_delay*1000}ms"
    
    async def _simulate_service_failure(self, experiment: ChaosExperiment) -> None:
        """Simulate service failure.
        
        Args:
            experiment: Experiment configuration
        """
        parameters = experiment.parameters
        shutdown_type = parameters.get('shutdown_type', 'graceful')
        
        self.logger.info(f"Simulating {shutdown_type} service failure")
        
        # This would integrate with orchestration platform to actually stop services
        # For now, we simulate the action
        experiment.results['service_failure_simulated'] = True
        experiment.results['shutdown_type'] = shutdown_type
    
    async def _simulate_network_partition(self, experiment: ChaosExperiment) -> None:
        """Simulate network partition between services.
        
        Args:
            experiment: Experiment configuration
        """
        parameters = experiment.parameters
        partition_percentage = parameters.get('partition_percentage', 0.3)
        
        self.logger.info(f"Simulating network partition affecting {partition_percentage*100}% of connections")
        
        # This would integrate with network tools to create actual partitions
        experiment.results['network_partition_simulated'] = True
        experiment.results['partition_percentage'] = partition_percentage
    
    async def _stress_cpu(self, experiment: ChaosExperiment) -> None:
        """Create CPU stress on target services.
        
        Args:
            experiment: Experiment configuration
        """
        parameters = experiment.parameters
        cpu_percentage = parameters.get('cpu_percentage', 70)
        burst_duration = parameters.get('burst_duration', 30)
        
        self.logger.info(f"Creating CPU stress: {cpu_percentage}% for {burst_duration}s bursts")
        
        # Start CPU stress in background
        stress_task = asyncio.create_task(self._cpu_stress_worker(cpu_percentage, burst_duration))
        experiment.results['cpu_stress_active'] = True
        experiment.results['cpu_target'] = cpu_percentage
        
        # Store task for cleanup
        experiment.parameters['_stress_task'] = stress_task
    
    async def _cpu_stress_worker(self, target_percentage: float, burst_duration: int) -> None:
        """Worker function to create CPU stress.
        
        Args:
            target_percentage: Target CPU percentage
            burst_duration: Duration of each burst in seconds
        """
        try:
            while True:
                # Create CPU load for burst duration
                end_time = time.time() + burst_duration
                while time.time() < end_time:
                    # Busy loop to consume CPU
                    for _ in range(100000):
                        pass
                
                # Brief pause between bursts
                await asyncio.sleep(5)
                
        except asyncio.CancelledError:
            pass
    
    async def _stress_memory(self, experiment: ChaosExperiment) -> None:
        """Create memory pressure on target services.
        
        Args:
            experiment: Experiment configuration
        """
        parameters = experiment.parameters
        memory_percentage = parameters.get('memory_percentage', 70)
        
        self.logger.info(f"Creating memory pressure: {memory_percentage}%")
        
        # Calculate target memory usage
        total_memory = psutil.virtual_memory().total
        target_bytes = int(total_memory * (memory_percentage / 100))
        
        # Allocate memory gradually
        memory_blocks = []
        block_size = 1024 * 1024  # 1MB blocks
        
        try:
            while len(memory_blocks) * block_size < target_bytes:
                memory_blocks.append(bytearray(block_size))
                await asyncio.sleep(0.1)  # Gradual allocation
            
            experiment.results['memory_pressure_created'] = True
            experiment.results['memory_allocated_mb'] = len(memory_blocks)
            
            # Store for cleanup
            experiment.parameters['_memory_blocks'] = memory_blocks
            
        except MemoryError:
            self.logger.warning("Memory allocation limit reached")
            experiment.results['memory_limit_reached'] = True
    
    async def _generate_traffic_spike(self, experiment: ChaosExperiment) -> None:
        """Generate artificial traffic spike.
        
        Args:
            experiment: Experiment configuration
        """
        parameters = experiment.parameters
        requests_per_second = parameters.get('requests_per_second', 100)
        ramp_up_time = parameters.get('ramp_up_time', 30)
        
        self.logger.info(f"Generating traffic spike: {requests_per_second} RPS")
        
        # This would integrate with load testing tools
        experiment.results['traffic_spike_generated'] = True
        experiment.results['target_rps'] = requests_per_second
    
    async def _monitor_experiment(self, experiment: ChaosExperiment) -> None:
        """Monitor experiment progress and safety.
        
        Args:
            experiment: Experiment to monitor
        """
        monitoring_task = asyncio.create_task(self._experiment_monitor_worker(experiment))
        experiment.parameters['_monitoring_task'] = monitoring_task
    
    async def _experiment_monitor_worker(self, experiment: ChaosExperiment) -> None:
        """Worker function for experiment monitoring.
        
        Args:
            experiment: Experiment to monitor
        """
        try:
            while experiment.state == ExperimentState.RUNNING:
                # Collect current metrics
                metrics = await self._collect_metrics(experiment.target_services)
                
                # Check safety thresholds
                if self._check_safety_violation(metrics):
                    self.logger.warning(f"Safety violation detected in experiment {experiment.id}")
                    await self.stop_experiment(experiment.id, "Safety violation")
                    break
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
        except asyncio.CancelledError:
            pass
    
    async def _cleanup_experiment(self, experiment: ChaosExperiment) -> None:
        """Clean up resources after experiment.
        
        Args:
            experiment: Experiment to clean up
        """
        try:
            # Cancel monitoring task
            if '_monitoring_task' in experiment.parameters:
                task = experiment.parameters['_monitoring_task']
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Cancel stress tasks
            if '_stress_task' in experiment.parameters:
                task = experiment.parameters['_stress_task']
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Free memory blocks
            if '_memory_blocks' in experiment.parameters:
                del experiment.parameters['_memory_blocks']
            
            self.logger.info(f"Cleaned up experiment: {experiment.id}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up experiment {experiment.id}: {e}")
    
    async def _collect_metrics(self, target_services: List[str]) -> ChaosMetrics:
        """Collect current system metrics.
        
        Args:
            target_services: List of target services
            
        Returns:
            Current metrics
        """
        try:
            metrics = ChaosMetrics()
            
            # System metrics
            metrics.cpu_usage = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            metrics.memory_usage = memory_info.percent
            metrics.network_connections = len(psutil.net_connections())
            
            # Disk I/O metrics
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics.disk_io = {
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes
                }
            
            # Service health (simulated)
            for service in target_services:
                metrics.service_health[service] = random.choice([True, True, True, False])  # 75% healthy
                metrics.error_rates[service] = random.uniform(0.0, 0.1)  # 0-10% error rate
            
            # Response times (simulated)
            metrics.response_times = [random.uniform(50, 500) for _ in range(10)]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return ChaosMetrics()
    
    async def _measure_recovery_time(self, experiment: ChaosExperiment) -> float:
        """Measure system recovery time after experiment.
        
        Args:
            experiment: Experiment configuration
            
        Returns:
            Recovery time in seconds
        """
        start_time = time.time()
        max_recovery_time = 300  # 5 minutes max
        
        while time.time() - start_time < max_recovery_time:
            metrics = await self._collect_metrics(experiment.target_services)
            
            # Check if system has recovered
            if self._is_system_healthy(metrics):
                recovery_time = time.time() - start_time
                self.logger.info(f"System recovered in {recovery_time:.2f} seconds")
                return recovery_time
            
            await asyncio.sleep(5)
        
        self.logger.warning("System did not recover within maximum time")
        return max_recovery_time
    
    def _is_system_healthy(self, metrics: ChaosMetrics) -> bool:
        """Check if system is in healthy state.
        
        Args:
            metrics: Current system metrics
            
        Returns:
            True if system is healthy
        """
        # Check CPU and memory
        if metrics.cpu_usage > 80 or metrics.memory_usage > 80:
            return False
        
        # Check service health
        healthy_services = sum(1 for health in metrics.service_health.values() if health)
        total_services = len(metrics.service_health)
        
        if total_services > 0 and healthy_services / total_services < 0.8:
            return False
        
        # Check error rates
        avg_error_rate = sum(metrics.error_rates.values()) / max(len(metrics.error_rates), 1)
        if avg_error_rate > 0.05:  # 5% error rate threshold
            return False
        
        return True
    
    async def _generate_experiment_results(self, experiment: ChaosExperiment) -> Dict[str, Any]:
        """Generate comprehensive experiment results.
        
        Args:
            experiment: Completed experiment
            
        Returns:
            Results dictionary
        """
        results = experiment.results.copy()
        
        # Calculate experiment duration
        if experiment.started_at and experiment.completed_at:
            results['actual_duration'] = experiment.completed_at - experiment.started_at
        
        # Analyze metrics changes
        if experiment.metrics_before and experiment.metrics_after:
            results['metrics_comparison'] = {
                'cpu_change': experiment.metrics_after.cpu_usage - experiment.metrics_before.cpu_usage,
                'memory_change': experiment.metrics_after.memory_usage - experiment.metrics_before.memory_usage,
                'network_change': experiment.metrics_after.network_connections - experiment.metrics_before.network_connections
            }
        
        # Include recovery time
        if experiment.recovery_time:
            results['recovery_time_seconds'] = experiment.recovery_time
        
        # Error analysis
        results['error_count'] = len(experiment.errors)
        results['errors'] = experiment.errors
        
        # Success criteria
        results['experiment_successful'] = (
            experiment.state == ExperimentState.COMPLETED and
            len(experiment.errors) == 0 and
            (experiment.recovery_time or 0) < 120  # 2 minutes recovery
        )
        
        return results
    
    def _validate_experiment_safety(self, experiment: ChaosExperiment) -> bool:
        """Validate if experiment is safe to run.
        
        Args:
            experiment: Experiment to validate
            
        Returns:
            True if experiment is safe
        """
        # Check environment restrictions
        if self.environment == 'production' and experiment.safety_level in [SafetyLevel.HIGH, SafetyLevel.CRITICAL]:
            self.logger.error("High/Critical safety level experiments not allowed in production")
            return False
        
        # Check concurrent experiments limit
        if len(self.active_experiments) >= self.safety_thresholds['max_concurrent_experiments']:
            self.logger.error("Too many concurrent experiments running")
            return False
        
        # Check service availability
        if not experiment.target_services:
            self.logger.error("No target services specified")
            return False
        
        return True
    
    def _can_start_experiment(self, experiment: ChaosExperiment) -> bool:
        """Check if experiment can be started now.
        
        Args:
            experiment: Experiment to check
            
        Returns:
            True if experiment can start
        """
        if not self.safety_checks_enabled:
            return True
        
        # Re-validate safety
        if not self._validate_experiment_safety(experiment):
            return False
        
        # Check current system health
        try:
            current_cpu = psutil.cpu_percent(interval=1)
            current_memory = psutil.virtual_memory().percent
            
            if current_cpu > self.safety_thresholds['max_cpu_usage']:
                self.logger.error(f"Current CPU usage too high: {current_cpu}%")
                return False
            
            if current_memory > self.safety_thresholds['max_memory_usage']:
                self.logger.error(f"Current memory usage too high: {current_memory}%")
                return False
            
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
            return False
        
        return True
    
    def _check_safety_violation(self, metrics: ChaosMetrics) -> bool:
        """Check if current metrics violate safety thresholds.
        
        Args:
            metrics: Current metrics
            
        Returns:
            True if safety violation detected
        """
        # Check CPU and memory thresholds
        if metrics.cpu_usage > self.safety_thresholds['max_cpu_usage']:
            return True
        
        if metrics.memory_usage > self.safety_thresholds['max_memory_usage']:
            return True
        
        # Check service health
        if metrics.service_health:
            healthy_services = sum(1 for health in metrics.service_health.values() if health)
            total_services = len(metrics.service_health)
            health_ratio = healthy_services / total_services
            
            if health_ratio < self.safety_thresholds['min_healthy_services']:
                return True
        
        # Check error rates
        if metrics.error_rates:
            avg_error_rate = sum(metrics.error_rates.values()) / len(metrics.error_rates)
            if avg_error_rate > self.safety_thresholds['max_error_rate']:
                return True
        
        return False
    
    def get_experiment_status(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get status information for an experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Experiment status dictionary or None if not found
        """
        if experiment_id not in self.experiments:
            return None
        
        experiment = self.experiments[experiment_id]
        
        status = {
            'id': experiment.id,
            'name': experiment.name,
            'description': experiment.description,
            'chaos_type': experiment.chaos_type.value,
            'target_services': experiment.target_services,
            'state': experiment.state.value,
            'safety_level': experiment.safety_level.value,
            'duration_seconds': experiment.duration_seconds,
            'created_at': experiment.created_at,
            'started_at': experiment.started_at,
            'completed_at': experiment.completed_at,
            'recovery_time': experiment.recovery_time,
            'error_count': len(experiment.errors),
            'results': experiment.results
        }
        
        # Add progress information for running experiments
        if experiment.state == ExperimentState.RUNNING and experiment.started_at:
            elapsed = time.time() - experiment.started_at
            status['elapsed_seconds'] = elapsed
            status['progress_percentage'] = min(100, (elapsed / experiment.duration_seconds) * 100)
        
        return status
    
    def list_experiments(self, state_filter: Optional[ExperimentState] = None) -> List[Dict[str, Any]]:
        """List all experiments, optionally filtered by state.
        
        Args:
            state_filter: Optional state to filter by
            
        Returns:
            List of experiment summaries
        """
        experiments = []
        
        for experiment in self.experiments.values():
            if state_filter is None or experiment.state == state_filter:
                experiments.append({
                    'id': experiment.id,
                    'name': experiment.name,
                    'chaos_type': experiment.chaos_type.value,
                    'state': experiment.state.value,
                    'target_services': experiment.target_services,
                    'created_at': experiment.created_at,
                    'started_at': experiment.started_at,
                    'completed_at': experiment.completed_at
                })
        
        return sorted(experiments, key=lambda x: x['created_at'], reverse=True)
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all available experiment templates.
        
        Returns:
            Dictionary of template names and their configurations
        """
        return self.experiment_templates.copy()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics and chaos engineering statistics.
        
        Returns:
            System metrics dictionary
        """
        try:
            # Current system state
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            
            # Chaos engineering statistics
            total_experiments = len(self.experiments)
            running_experiments = len(self.active_experiments)
            completed_experiments = len([e for e in self.experiments.values() if e.state == ExperimentState.COMPLETED])
            failed_experiments = len([e for e in self.experiments.values() if e.state == ExperimentState.FAILED])
            
            return {
                'system': {
                    'cpu_usage_percent': cpu_usage,
                    'memory_usage_percent': memory_info.percent,
                    'memory_available_gb': memory_info.available / (1024**3),
                    'disk_usage_percent': (disk_info.used / disk_info.total) * 100,
                    'network_connections': len(psutil.net_connections())
                },
                'chaos_engineering': {
                    'total_experiments': total_experiments,
                    'running_experiments': running_experiments,
                    'completed_experiments': completed_experiments,
                    'failed_experiments': failed_experiments,
                    'success_rate': completed_experiments / max(total_experiments, 1) * 100,
                    'available_templates': len(self.experiment_templates),
                    'safety_checks_enabled': self.safety_checks_enabled,
                    'environment': self.environment
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def _load_configuration(self, config_path: str) -> None:
        """Load configuration from file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Load safety thresholds
                if 'safety_thresholds' in config:
                    self.safety_thresholds.update(config['safety_thresholds'])
                
                # Load custom experiment templates
                if 'experiment_templates' in config:
                    self.experiment_templates.update(config['experiment_templates'])
                
                # Load other settings
                self.safety_checks_enabled = config.get('safety_checks_enabled', True)
                self.monitoring_enabled = config.get('monitoring_enabled', True)
                
                self.logger.info(f"Loaded configuration from {config_path}")
            else:
                self.logger.warning(f"Configuration file {config_path} not found")
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the chaos engineering service."""
        try:
            # Stop all running experiments
            experiment_ids = list(self.active_experiments.keys())
            for experiment_id in experiment_ids:
                await self.stop_experiment(experiment_id, "Service shutdown")
            
            # Shutdown executor
            self._executor.shutdown(wait=True)
            
            self.logger.info("ChaosEngineeringService shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Example usage and testing
async def main():
    """Example usage of the ChaosEngineeringService."""
    # Initialize service
    service = ChaosEngineeringService()
    
    try:
        # List available templates
        templates = service.get_available_templates()
        print(f"Available templates: {list(templates.keys())}")
        
        # Create an experiment
        experiment_id = await service.create_experiment(
            'latency_spike',
            ['ai_inference', 'content_processing'],
            {'min_delay_ms': 200, 'max_delay_ms': 800}
        )
        print(f"Created experiment: {experiment_id}")
        
        # Start the experiment
        started = await service.start_experiment(experiment_id)
        print(f"Experiment started: {started}")
        
        # Monitor for a few seconds
        await asyncio.sleep(10)
        
        # Get experiment status
        status = service.get_experiment_status(experiment_id)
        print(f"Experiment status: {status}")
        
        # Get system metrics
        metrics = service.get_system_metrics()
        print(f"System metrics: {metrics}")
        
        # Stop the experiment
        stopped = await service.stop_experiment(experiment_id, "Testing complete")
        print(f"Experiment stopped: {stopped}")
        
    finally:
        # Cleanup
        await service.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())