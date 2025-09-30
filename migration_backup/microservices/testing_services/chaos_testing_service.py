"""
Chaos Testing Service - Enterprise Chaos Engineering
Ainflue Platform - Microservices Architecture

© FAHED MLAIEL 2024-2025 - CONFIDENTIAL ENTERPRISE MODULE
"""

import asyncio
import aiohttp
import random
import time
import psutil
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta
import subprocess
import signal
import os

class ChaosExperimentType(Enum):
    """Types of chaos experiments"""
    SERVICE_FAILURE = "service_failure"
    NETWORK_LATENCY = "network_latency"
    NETWORK_PARTITION = "network_partition"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_STRESS = "disk_stress"
    PROCESS_KILLER = "process_killer"
    DEPENDENCY_FAILURE = "dependency_failure"

class ChaosStatus(Enum):
    """Chaos experiment status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

@dataclass
class ChaosExperiment:
    """Chaos experiment definition"""
    experiment_id: str
    name: str
    experiment_type: ChaosExperimentType
    target_service: str
    duration_seconds: int
    intensity: float  # 0.0 to 1.0
    parameters: Dict[str, Any]
    hypothesis: str
    success_criteria: Dict[str, Any]
    rollback_strategy: str

@dataclass
class ChaosExperimentResult:
    """Chaos experiment execution result"""
    experiment_id: str
    experiment: ChaosExperiment
    status: ChaosStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration: float
    hypothesis_validated: bool
    system_impact: Dict[str, Any]
    recovery_time: float
    observations: List[str]
    metrics_before: Dict[str, float]
    metrics_during: Dict[str, float]
    metrics_after: Dict[str, float]
    success: bool

class ChaosTestingService:
    """
    Enterprise Chaos Testing Service
    
    Provides chaos engineering capabilities for testing microservices
    resilience, fault tolerance, and system recovery under failure conditions.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_experiments = {}
        self.experiment_results = {}
        self.system_baseline = {}
        self.monitoring_tasks = {}
        
    async def initialize(self) -> bool:
        """Initialize chaos testing service"""
        try:
            self.logger.info("Initializing Chaos Testing Service...")
            
            # Setup system monitoring
            await self._setup_system_monitoring()
            
            # Initialize chaos experiments catalog
            self._init_experiment_catalog()
            
            # Setup safety mechanisms
            await self._setup_safety_mechanisms()
            
            self.logger.info("Chaos Testing Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Chaos Testing Service: {e}")
            return False
    
    async def _setup_system_monitoring(self):
        """Setup system monitoring for chaos experiments"""
        self.system_metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_connections": 0,
            "active_processes": 0
        }
        
        # Start baseline monitoring
        self.monitoring_task = asyncio.create_task(self._monitor_system_baseline())
    
    def _init_experiment_catalog(self):
        """Initialize chaos experiment catalog"""
        self.experiment_catalog = {
            "service_failure": {
                "name": "Service Failure",
                "description": "Simulate service crashes and failures",
                "duration_range": (30, 300),  # 30 seconds to 5 minutes
                "default_intensity": 0.5
            },
            "network_latency": {
                "name": "Network Latency",
                "description": "Inject network latency and delays",
                "duration_range": (60, 600),  # 1 to 10 minutes
                "default_intensity": 0.3
            },
            "cpu_stress": {
                "name": "CPU Stress",
                "description": "Stress CPU resources",
                "duration_range": (120, 600),  # 2 to 10 minutes
                "default_intensity": 0.7
            },
            "memory_stress": {
                "name": "Memory Stress",
                "description": "Consume memory resources",
                "duration_range": (60, 300),  # 1 to 5 minutes
                "default_intensity": 0.6
            }
        }
    
    async def _setup_safety_mechanisms(self):
        """Setup safety mechanisms for chaos experiments"""
        self.safety_limits = {
            "max_concurrent_experiments": 3,
            "max_experiment_duration": 1800,  # 30 minutes
            "min_recovery_time": 60,  # 1 minute between experiments
            "system_health_threshold": 0.8  # Stop if system health < 80%
        }
        
        self.emergency_stop = False
        self.last_experiment_end = None
    
    async def _monitor_system_baseline(self):
        """Monitor system baseline metrics"""
        try:
            while True:
                # Update system metrics
                self.system_metrics["cpu_usage"] = psutil.cpu_percent(interval=1)
                self.system_metrics["memory_usage"] = psutil.virtual_memory().percent
                self.system_metrics["disk_usage"] = psutil.disk_usage('/').percent
                self.system_metrics["network_connections"] = len(psutil.net_connections())
                self.system_metrics["active_processes"] = len(psutil.pids())
                
                # Store baseline if no experiments running
                if not self.active_experiments:
                    self.system_baseline = self.system_metrics.copy()
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"System monitoring error: {e}")
    
    async def run_chaos_experiment(self, experiment: ChaosExperiment) -> ChaosExperimentResult:
        """
        Execute chaos experiment
        
        Args:
            experiment: Chaos experiment configuration
            
        Returns:
            ChaosExperimentResult: Experiment execution result
        """
        try:
            # Safety checks
            if not await self._safety_checks(experiment):
                raise ValueError("Safety checks failed - experiment not allowed")
            
            self.logger.info(f"Starting chaos experiment: {experiment.experiment_id}")
            
            # Record metrics before experiment
            metrics_before = self.system_metrics.copy()
            start_time = datetime.now()
            
            # Mark experiment as active
            self.active_experiments[experiment.experiment_id] = experiment
            
            # Start experiment monitoring
            monitoring_task = asyncio.create_task(
                self._monitor_experiment(experiment.experiment_id)
            )
            self.monitoring_tasks[experiment.experiment_id] = monitoring_task
            
            # Execute experiment based on type
            experiment_task = None
            if experiment.experiment_type == ChaosExperimentType.SERVICE_FAILURE:
                experiment_task = await self._execute_service_failure(experiment)
            elif experiment.experiment_type == ChaosExperimentType.NETWORK_LATENCY:
                experiment_task = await self._execute_network_latency(experiment)
            elif experiment.experiment_type == ChaosExperimentType.CPU_STRESS:
                experiment_task = await self._execute_cpu_stress(experiment)
            elif experiment.experiment_type == ChaosExperimentType.MEMORY_STRESS:
                experiment_task = await self._execute_memory_stress(experiment)
            
            # Wait for experiment duration
            await asyncio.sleep(experiment.duration_seconds)
            
            # Stop experiment
            if experiment_task:
                experiment_task.cancel()
            
            # Record metrics during experiment (just before cleanup)
            metrics_during = self.system_metrics.copy()
            
            # Cleanup experiment
            await self._cleanup_experiment(experiment)
            
            # Wait for system recovery and record metrics after
            await asyncio.sleep(30)  # Recovery period
            metrics_after = self.system_metrics.copy()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Calculate recovery time
            recovery_time = await self._calculate_recovery_time(experiment, metrics_before)
            
            # Validate hypothesis
            hypothesis_validated = await self._validate_hypothesis(experiment, metrics_before, metrics_after)
            
            # Generate observations
            observations = await self._generate_observations(experiment, metrics_before, metrics_during, metrics_after)
            
            # Determine success
            success = (
                hypothesis_validated and 
                recovery_time < experiment.success_criteria.get("max_recovery_time", 300) and
                not self.emergency_stop
            )
            
            result = ChaosExperimentResult(
                experiment_id=experiment.experiment_id,
                experiment=experiment,
                status=ChaosStatus.COMPLETED,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                hypothesis_validated=hypothesis_validated,
                system_impact=await self._calculate_system_impact(metrics_before, metrics_during, metrics_after),
                recovery_time=recovery_time,
                observations=observations,
                metrics_before=metrics_before,
                metrics_during=metrics_during,
                metrics_after=metrics_after,
                success=success
            )
            
            # Cleanup
            monitoring_task.cancel()
            del self.active_experiments[experiment.experiment_id]
            del self.monitoring_tasks[experiment.experiment_id]
            
            self.experiment_results[experiment.experiment_id] = result
            self.last_experiment_end = end_time
            
            self.logger.info(f"Chaos experiment completed: {experiment.experiment_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Chaos experiment failed: {e}")
            
            # Cleanup on failure
            if experiment.experiment_id in self.active_experiments:
                await self._cleanup_experiment(experiment)
                del self.active_experiments[experiment.experiment_id]
            
            raise
    
    async def _safety_checks(self, experiment: ChaosExperiment) -> bool:
        """Perform safety checks before experiment"""
        # Check concurrent experiments limit
        if len(self.active_experiments) >= self.safety_limits["max_concurrent_experiments"]:
            self.logger.warning("Too many concurrent experiments")
            return False
        
        # Check experiment duration
        if experiment.duration_seconds > self.safety_limits["max_experiment_duration"]:
            self.logger.warning("Experiment duration exceeds safety limit")
            return False
        
        # Check recovery time since last experiment
        if self.last_experiment_end:
            time_since_last = (datetime.now() - self.last_experiment_end).total_seconds()
            if time_since_last < self.safety_limits["min_recovery_time"]:
                self.logger.warning("Insufficient recovery time since last experiment")
                return False
        
        # Check system health
        if self.system_metrics["cpu_usage"] > 90 or self.system_metrics["memory_usage"] > 90:
            self.logger.warning("System health below threshold")
            return False
        
        return True
    
    async def _monitor_experiment(self, experiment_id: str):
        """Monitor experiment execution"""
        try:
            while experiment_id in self.active_experiments:
                # Check system health
                if (self.system_metrics["cpu_usage"] > 95 or 
                    self.system_metrics["memory_usage"] > 95):
                    self.logger.warning(f"Emergency stop triggered for {experiment_id}")
                    self.emergency_stop = True
                    await self._emergency_stop_experiment(experiment_id)
                    break
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except asyncio.CancelledError:
            pass
    
    async def _execute_service_failure(self, experiment: ChaosExperiment) -> Optional[asyncio.Task]:
        """Execute service failure experiment"""
        try:
            service_url = experiment.parameters.get("service_url", "http://localhost:8000")
            failure_rate = experiment.intensity
            
            async def service_chaos():
                while True:
                    if random.random() < failure_rate:
                        # Simulate service failure by sending malformed requests
                        try:
                            async with aiohttp.ClientSession() as session:
                                # Send requests that might cause service stress
                                await session.post(f"{service_url}/chaos-test", 
                                                 json={"chaos": "failure_injection"})
                        except:
                            pass  # Expected failures
                    await asyncio.sleep(1)
            
            return asyncio.create_task(service_chaos())
            
        except Exception as e:
            self.logger.error(f"Service failure experiment error: {e}")
            return None
    
    async def _execute_network_latency(self, experiment: ChaosExperiment) -> Optional[asyncio.Task]:
        """Execute network latency experiment"""
        try:
            latency_ms = int(experiment.intensity * 1000)  # Convert to milliseconds
            
            async def network_chaos():
                # This would typically use network tools like tc (traffic control)
                # For simulation, we'll just add delays to our requests
                while True:
                    await asyncio.sleep(latency_ms / 1000)  # Simulate network delay
                    await asyncio.sleep(1)
            
            return asyncio.create_task(network_chaos())
            
        except Exception as e:
            self.logger.error(f"Network latency experiment error: {e}")
            return None
    
    async def _execute_cpu_stress(self, experiment: ChaosExperiment) -> Optional[asyncio.Task]:
        """Execute CPU stress experiment"""
        try:
            cpu_cores = int(psutil.cpu_count() * experiment.intensity)
            
            async def cpu_stress():
                # Start CPU stress processes
                processes = []
                for _ in range(cpu_cores):
                    # Simple CPU intensive task
                    process = subprocess.Popen([
                        "python3", "-c", 
                        "while True: pass"
                    ])
                    processes.append(process)
                
                try:
                    # Keep processes running
                    while True:
                        await asyncio.sleep(1)
                finally:
                    # Cleanup processes
                    for process in processes:
                        try:
                            process.terminate()
                            process.wait(timeout=5)
                        except:
                            try:
                                process.kill()
                            except:
                                pass
            
            return asyncio.create_task(cpu_stress())
            
        except Exception as e:
            self.logger.error(f"CPU stress experiment error: {e}")
            return None
    
    async def _execute_memory_stress(self, experiment: ChaosExperiment) -> Optional[asyncio.Task]:
        """Execute memory stress experiment"""
        try:
            memory_mb = int(psutil.virtual_memory().total * experiment.intensity / (1024**2))
            
            async def memory_stress():
                # Allocate memory
                memory_blocks = []
                block_size = 10 * 1024 * 1024  # 10MB blocks
                target_blocks = memory_mb // 10
                
                try:
                    for _ in range(target_blocks):
                        memory_blocks.append(bytearray(block_size))
                        await asyncio.sleep(0.1)  # Gradual allocation
                    
                    # Keep memory allocated
                    while True:
                        await asyncio.sleep(1)
                        
                finally:
                    # Cleanup memory
                    memory_blocks.clear()
            
            return asyncio.create_task(memory_stress())
            
        except Exception as e:
            self.logger.error(f"Memory stress experiment error: {e}")
            return None
    
    async def _cleanup_experiment(self, experiment: ChaosExperiment):
        """Cleanup experiment resources"""
        try:
            # Kill any stress processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('while True: pass' in ' '.join(cmdline) for cmd in [cmdline]):
                        proc.terminate()
                except:
                    pass
            
            self.logger.info(f"Cleaned up experiment: {experiment.experiment_id}")
            
        except Exception as e:
            self.logger.error(f"Experiment cleanup error: {e}")
    
    async def _emergency_stop_experiment(self, experiment_id: str):
        """Emergency stop for experiment"""
        if experiment_id in self.active_experiments:
            experiment = self.active_experiments[experiment_id]
            await self._cleanup_experiment(experiment)
            del self.active_experiments[experiment_id]
            
            self.logger.warning(f"Emergency stopped experiment: {experiment_id}")
    
    async def _calculate_recovery_time(self, experiment: ChaosExperiment, baseline_metrics: Dict) -> float:
        """Calculate system recovery time"""
        recovery_start = time.time()
        
        while time.time() - recovery_start < 300:  # Max 5 minutes wait
            current_metrics = self.system_metrics.copy()
            
            # Check if system recovered to within 10% of baseline
            cpu_recovered = abs(current_metrics["cpu_usage"] - baseline_metrics["cpu_usage"]) < 10
            memory_recovered = abs(current_metrics["memory_usage"] - baseline_metrics["memory_usage"]) < 10
            
            if cpu_recovered and memory_recovered:
                return time.time() - recovery_start
            
            await asyncio.sleep(5)
        
        return 300  # Max recovery time
    
    async def _validate_hypothesis(self, experiment: ChaosExperiment, 
                                 before_metrics: Dict, after_metrics: Dict) -> bool:
        """Validate experiment hypothesis"""
        # Simple validation: system should recover
        recovery_threshold = 20  # 20% difference allowed
        
        cpu_recovered = abs(after_metrics["cpu_usage"] - before_metrics["cpu_usage"]) < recovery_threshold
        memory_recovered = abs(after_metrics["memory_usage"] - before_metrics["memory_usage"]) < recovery_threshold
        
        return cpu_recovered and memory_recovered
    
    async def _generate_observations(self, experiment: ChaosExperiment,
                                   before: Dict, during: Dict, after: Dict) -> List[str]:
        """Generate experiment observations"""
        observations = []
        
        # CPU observations
        cpu_increase = during["cpu_usage"] - before["cpu_usage"]
        if cpu_increase > 20:
            observations.append(f"CPU usage increased by {cpu_increase:.1f}% during experiment")
        
        # Memory observations
        memory_increase = during["memory_usage"] - before["memory_usage"]
        if memory_increase > 20:
            observations.append(f"Memory usage increased by {memory_increase:.1f}% during experiment")
        
        # Recovery observations
        if after["cpu_usage"] <= before["cpu_usage"] + 5:
            observations.append("CPU usage recovered to normal levels")
        else:
            observations.append("CPU usage did not fully recover")
        
        if after["memory_usage"] <= before["memory_usage"] + 5:
            observations.append("Memory usage recovered to normal levels")
        else:
            observations.append("Memory usage did not fully recover")
        
        return observations
    
    async def _calculate_system_impact(self, before: Dict, during: Dict, after: Dict) -> Dict[str, Any]:
        """Calculate system impact metrics"""
        return {
            "cpu_impact": {
                "max_increase": during["cpu_usage"] - before["cpu_usage"],
                "recovery_difference": after["cpu_usage"] - before["cpu_usage"]
            },
            "memory_impact": {
                "max_increase": during["memory_usage"] - before["memory_usage"],
                "recovery_difference": after["memory_usage"] - before["memory_usage"]
            },
            "overall_impact": "low" if max(
                during["cpu_usage"] - before["cpu_usage"],
                during["memory_usage"] - before["memory_usage"]
            ) < 30 else "high"
        }
    
    async def run_chaos_suite(self, target_service: str) -> List[ChaosExperimentResult]:
        """Run comprehensive chaos testing suite"""
        results = []
        
        # Define experiment suite
        experiments = [
            ChaosExperiment(
                experiment_id=f"chaos_cpu_{int(time.time())}",
                name="CPU Stress Test",
                experiment_type=ChaosExperimentType.CPU_STRESS,
                target_service=target_service,
                duration_seconds=120,
                intensity=0.5,
                parameters={},
                hypothesis="System should handle CPU stress gracefully",
                success_criteria={"max_recovery_time": 120},
                rollback_strategy="Terminate stress processes"
            ),
            ChaosExperiment(
                experiment_id=f"chaos_memory_{int(time.time())}",
                name="Memory Stress Test",
                experiment_type=ChaosExperimentType.MEMORY_STRESS,
                target_service=target_service,
                duration_seconds=90,
                intensity=0.4,
                parameters={},
                hypothesis="System should handle memory pressure gracefully",
                success_criteria={"max_recovery_time": 90},
                rollback_strategy="Release allocated memory"
            ),
            ChaosExperiment(
                experiment_id=f"chaos_service_{int(time.time())}",
                name="Service Failure Test",
                experiment_type=ChaosExperimentType.SERVICE_FAILURE,
                target_service=target_service,
                duration_seconds=60,
                intensity=0.3,
                parameters={"service_url": f"http://localhost:8000"},
                hypothesis="Service should be resilient to failures",
                success_criteria={"max_recovery_time": 60},
                rollback_strategy="Stop failure injection"
            )
        ]
        
        for experiment in experiments:
            try:
                result = await self.run_chaos_experiment(experiment)
                results.append(result)
                
                # Wait between experiments
                await asyncio.sleep(self.safety_limits["min_recovery_time"])
                
            except Exception as e:
                self.logger.error(f"Chaos suite experiment failed: {e}")
        
        return results
    
    def get_experiment_results(self, experiment_id: Optional[str] = None) -> Dict[str, ChaosExperimentResult]:
        """Get chaos experiment results"""
        if experiment_id:
            return {experiment_id: self.experiment_results.get(experiment_id)}
        return self.experiment_results
    
    def get_active_experiments(self) -> Dict[str, ChaosExperiment]:
        """Get currently running experiments"""
        return self.active_experiments
    
    async def stop_experiment(self, experiment_id: str) -> bool:
        """Stop running experiment"""
        if experiment_id in self.active_experiments:
            await self._emergency_stop_experiment(experiment_id)
            return True
        return False
    
    async def generate_chaos_report(self) -> Dict[str, Any]:
        """Generate chaos testing report"""
        total_experiments = len(self.experiment_results)
        successful_experiments = sum(1 for r in self.experiment_results.values() if r.success)
        
        avg_recovery_time = sum(r.recovery_time for r in self.experiment_results.values()) / total_experiments if total_experiments > 0 else 0
        
        return {
            "summary": {
                "total_experiments": total_experiments,
                "successful_experiments": successful_experiments,
                "success_rate": f"{(successful_experiments/total_experiments*100):.1f}%" if total_experiments > 0 else "0%",
                "avg_recovery_time": f"{avg_recovery_time:.1f} seconds"
            },
            "resilience_score": self._calculate_resilience_score(),
            "recommendations": self._generate_chaos_recommendations(),
            "system_weaknesses": self._identify_system_weaknesses()
        }
    
    def _calculate_resilience_score(self) -> int:
        """Calculate system resilience score (0-100)"""
        if not self.experiment_results:
            return 0
        
        success_rate = sum(1 for r in self.experiment_results.values() if r.success) / len(self.experiment_results)
        avg_recovery = sum(r.recovery_time for r in self.experiment_results.values()) / len(self.experiment_results)
        
        # Score based on success rate and recovery time
        score = (success_rate * 70) + max(0, (300 - avg_recovery) / 300 * 30)
        return int(score)
    
    def _generate_chaos_recommendations(self) -> List[str]:
        """Generate chaos testing recommendations"""
        recommendations = []
        
        failed_experiments = [r for r in self.experiment_results.values() if not r.success]
        
        if failed_experiments:
            recommendations.append("Improve system resilience for failed experiments")
        
        high_recovery_experiments = [r for r in self.experiment_results.values() if r.recovery_time > 180]
        if high_recovery_experiments:
            recommendations.append("Optimize recovery time for better resilience")
        
        if len(self.experiment_results) < 5:
            recommendations.append("Run more chaos experiments for better coverage")
        
        return recommendations or ["System showing good resilience"]
    
    def _identify_system_weaknesses(self) -> List[str]:
        """Identify system weaknesses from experiments"""
        weaknesses = []
        
        for result in self.experiment_results.values():
            if result.experiment.experiment_type == ChaosExperimentType.CPU_STRESS and not result.success:
                weaknesses.append("CPU resource management")
            
            if result.experiment.experiment_type == ChaosExperimentType.MEMORY_STRESS and not result.success:
                weaknesses.append("Memory resource management")
            
            if result.recovery_time > 240:
                weaknesses.append("Slow recovery mechanisms")
        
        return list(set(weaknesses)) or ["No significant weaknesses identified"]

# Service instance
chaos_testing_service = ChaosTestingService()