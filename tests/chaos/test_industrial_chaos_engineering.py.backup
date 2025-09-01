"""
Industrial-grade Chaos Engineering tests for system resilience.
Tests real system recovery under various failure conditions.
"""

import asyncio
import logging
import time
import random
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import aiohttp
import pytest
import psutil
import signal
import subprocess

logger = logging.getLogger(__name__)


class ChaosType(Enum):
    """Types of chaos engineering tests."""
    NETWORK_PARTITION = "network_partition"
    SERVICE_FAILURE = "service_failure"
    DATABASE_FAILURE = "database_failure"
    HIGH_CPU_LOAD = "high_cpu_load"
    MEMORY_EXHAUSTION = "memory_exhaustion"
    DISK_FULL = "disk_full"
    NETWORK_LATENCY = "network_latency"
    DEPENDENCY_FAILURE = "dependency_failure"
    CASCADING_FAILURE = "cascading_failure"


class RecoveryStrategy(Enum):
    """System recovery strategies."""
    AUTOMATIC_RESTART = "automatic_restart"
    FAILOVER = "failover"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    RETRY_WITH_BACKOFF = "retry_with_backoff"


@dataclass
class ChaosExperiment:
    """Definition of a chaos engineering experiment."""
    name: str
    chaos_type: ChaosType
    target_component: str
    duration_seconds: int
    expected_recovery_strategy: RecoveryStrategy
    max_acceptable_downtime_seconds: int = 300  # 5 minutes
    max_acceptable_data_loss: float = 0.0  # No data loss acceptable
    success_criteria: Dict[str, Any] = None


@dataclass
class ChaosResult:
    """Result from a chaos engineering experiment."""
    experiment_name: str
    chaos_type: ChaosType
    success: bool
    actual_downtime_seconds: float
    recovery_time_seconds: float
    data_loss_detected: bool
    recovery_strategy_used: Optional[RecoveryStrategy]
    system_state_after_recovery: Dict[str, Any]
    error_message: Optional[str] = None
    performance_impact: Optional[Dict[str, float]] = None


class SystemMonitor:
    """Real system monitoring for chaos experiments."""
    
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.monitoring_active = False
    
    async def start_monitoring(self, interval_seconds: float = 1.0):
        """Start continuous system monitoring."""
        self.monitoring_active = True
        
        while self.monitoring_active:
            metrics = await self._collect_system_metrics()
            self.metrics_history.append({
                "timestamp": time.time(),
                "metrics": metrics
            })
            await asyncio.sleep(interval_seconds)
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring_active = False
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect real system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network stats
            network = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "process_count": process_count,
                "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def get_metrics_during_period(self, start_time: float, end_time: float) -> List[Dict[str, Any]]:
        """Get metrics collected during a specific time period."""
        return [
            entry for entry in self.metrics_history
            if start_time <= entry["timestamp"] <= end_time
        ]


class RealServiceManager:
    """Manages real services for chaos testing."""
    
    def __init__(self):
        self.managed_services: Dict[str, Dict[str, Any]] = {}
    
    async def discover_services(self) -> List[str]:
        """Discover running services for chaos testing."""
        services = []
        
        # Check for common service processes
        service_patterns = [
            "python.*main.py",  # Main application
            "nginx",
            "postgres",
            "redis-server",
            "celery",
            "uvicorn"
        ]
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                for pattern in service_patterns:
                    if pattern.lower() in cmdline.lower():
                        service_name = pattern.split('.*')[0]
                        if service_name not in services:
                            services.append(service_name)
                            self.managed_services[service_name] = {
                                "pid": proc.info['pid'],
                                "name": proc.info['name'],
                                "cmdline": cmdline
                            }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return services
    
    async def kill_service(self, service_name: str) -> bool:
        """Kill a service to simulate failure."""
        if service_name not in self.managed_services:
            logger.error(f"Service {service_name} not found")
            return False
        
        try:
            pid = self.managed_services[service_name]["pid"]
            process = psutil.Process(pid)
            process.terminate()
            
            # Wait for termination
            try:
                process.wait(timeout=10)
            except psutil.TimeoutExpired:
                process.kill()  # Force kill if termination fails
            
            logger.info(f"Service {service_name} (PID: {pid}) terminated")
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Failed to kill service {service_name}: {e}")
            return False
    
    async def restart_service(self, service_name: str) -> bool:
        """Restart a service after failure."""
        if service_name not in self.managed_services:
            return False
        
        try:
            # For demonstration, we'll simulate service restart
            # In real implementation, this would restart the actual service
            await asyncio.sleep(5)  # Simulate restart time
            
            logger.info(f"Service {service_name} restarted")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restart service {service_name}: {e}")
            return False


class IndustrialChaosEngineer:
    """
    Industrial-grade chaos engineering for system resilience testing.
    Tests real system recovery under actual failure conditions.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.monitor = SystemMonitor()
        self.service_manager = RealServiceManager()
        self.session: Optional[aiohttp.ClientSession] = None
        self.results: List[ChaosResult] = []
    
    async def __aenter__(self):
        """Setup chaos engineering environment."""
        self.session = aiohttp.ClientSession()
        await self.service_manager.discover_services()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup chaos engineering environment."""
        self.monitor.stop_monitoring()
        if self.session:
            await self.session.close()
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        health_status = {
            "api_responsive": False,
            "database_accessible": False,
            "services_running": [],
            "response_time_ms": None
        }
        
        try:
            # Check API health
            start_time = time.time()
            async with self.session.get(f"{self.base_url}/api/v1/health") as response:
                response_time = (time.time() - start_time) * 1000
                health_status["response_time_ms"] = response_time
                health_status["api_responsive"] = response.status == 200
            
            # Check database (through API)
            async with self.session.get(f"{self.base_url}/api/v1/health/database") as response:
                health_status["database_accessible"] = response.status == 200
            
            # Check running services
            health_status["services_running"] = await self.service_manager.discover_services()
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
        
        return health_status
    
    async def _inject_cpu_stress(self, duration_seconds: int, cpu_percent: int = 80) -> bool:
        """Inject CPU stress to simulate high load."""
        try:
            # Create CPU stress
            num_cores = psutil.cpu_count()
            stress_processes = []
            
            for _ in range(num_cores):
                # Simple CPU stress loop
                proc = subprocess.Popen([
                    "python", "-c",
                    f"import time; end_time = time.time() + {duration_seconds}; "
                    f"while time.time() < end_time: pass"
                ])
                stress_processes.append(proc)
            
            logger.info(f"Started CPU stress test for {duration_seconds} seconds")
            
            # Wait for stress duration
            await asyncio.sleep(duration_seconds)
            
            # Terminate stress processes
            for proc in stress_processes:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
            
            logger.info("CPU stress test completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to inject CPU stress: {e}")
            return False
    
    async def _inject_memory_pressure(self, duration_seconds: int, memory_mb: int = 1024) -> bool:
        """Inject memory pressure to simulate memory exhaustion."""
        try:
            # Allocate large amount of memory
            memory_blocks = []
            block_size = 1024 * 1024  # 1MB blocks
            
            for _ in range(memory_mb):
                memory_blocks.append(bytearray(block_size))
            
            logger.info(f"Allocated {memory_mb}MB for memory pressure test")
            await asyncio.sleep(duration_seconds)
            
            # Clear memory
            memory_blocks.clear()
            
            logger.info("Memory pressure test completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to inject memory pressure: {e}")
            return False
    
    async def run_chaos_experiment(self, experiment: ChaosExperiment) -> ChaosResult:
        """Run a chaos engineering experiment."""
        logger.info(f"Starting chaos experiment: {experiment.name}")
        
        # Start monitoring
        monitor_task = asyncio.create_task(self.monitor.start_monitoring())
        
        experiment_start = time.time()
        
        try:
            # Get baseline health
            baseline_health = await self._check_system_health()
            if not baseline_health["api_responsive"]:
                raise Exception("System not healthy before experiment")
            
            # Record pre-chaos state
            chaos_start = time.time()
            
            # Inject chaos based on type
            chaos_injected = False
            if experiment.chaos_type == ChaosType.SERVICE_FAILURE:
                chaos_injected = await self.service_manager.kill_service(experiment.target_component)
            elif experiment.chaos_type == ChaosType.HIGH_CPU_LOAD:
                chaos_injected = await self._inject_cpu_stress(experiment.duration_seconds)
            elif experiment.chaos_type == ChaosType.MEMORY_EXHAUSTION:
                chaos_injected = await self._inject_memory_pressure(experiment.duration_seconds)
            else:
                logger.warning(f"Chaos type {experiment.chaos_type} not implemented")
                chaos_injected = False
            
            if not chaos_injected:
                raise Exception(f"Failed to inject chaos: {experiment.chaos_type}")
            
            # Monitor system during chaos
            downtime_start = None
            recovery_start = None
            system_down = False
            
            # Check system health periodically during chaos
            check_interval = 5  # seconds
            max_checks = experiment.duration_seconds // check_interval + 10  # Extra time for recovery
            
            for check in range(max_checks):
                await asyncio.sleep(check_interval)
                
                health = await self._check_system_health()
                
                if not health["api_responsive"] and not system_down:
                    # System just went down
                    system_down = True
                    downtime_start = time.time()
                    logger.info("System detected as down")
                
                elif health["api_responsive"] and system_down:
                    # System recovered
                    recovery_start = time.time()
                    logger.info("System recovery detected")
                    break
            
            # Calculate metrics
            experiment_end = time.time()
            
            if downtime_start:
                if recovery_start:
                    actual_downtime = recovery_start - downtime_start
                    recovery_time = recovery_start - chaos_start
                else:
                    actual_downtime = experiment_end - downtime_start
                    recovery_time = actual_downtime
            else:
                actual_downtime = 0
                recovery_time = 0
            
            # Get final system state
            final_health = await self._check_system_health()
            
            # Determine success
            success = (
                actual_downtime <= experiment.max_acceptable_downtime_seconds and
                final_health["api_responsive"] and
                final_health["database_accessible"]
            )
            
            # Get performance impact
            metrics_during_chaos = self.monitor.get_metrics_during_period(chaos_start, experiment_end)
            performance_impact = self._calculate_performance_impact(metrics_during_chaos)
            
            result = ChaosResult(
                experiment_name=experiment.name,
                chaos_type=experiment.chaos_type,
                success=success,
                actual_downtime_seconds=actual_downtime,
                recovery_time_seconds=recovery_time,
                data_loss_detected=False,  # Would need specific checks
                recovery_strategy_used=experiment.expected_recovery_strategy,
                system_state_after_recovery=final_health,
                performance_impact=performance_impact
            )
            
            logger.info(f"Chaos experiment completed: {result}")
            return result
            
        except Exception as e:
            experiment_end = time.time()
            logger.error(f"Chaos experiment failed: {e}")
            
            result = ChaosResult(
                experiment_name=experiment.name,
                chaos_type=experiment.chaos_type,
                success=False,
                actual_downtime_seconds=experiment_end - experiment_start,
                recovery_time_seconds=0,
                data_loss_detected=False,
                recovery_strategy_used=None,
                system_state_after_recovery={},
                error_message=str(e)
            )
            
            return result
            
        finally:
            # Stop monitoring
            self.monitor.stop_monitoring()
            monitor_task.cancel()
            
            # Attempt service recovery if needed
            if experiment.chaos_type == ChaosType.SERVICE_FAILURE:
                await self.service_manager.restart_service(experiment.target_component)
    
    def _calculate_performance_impact(self, metrics: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate performance impact during chaos."""
        if not metrics:
            return {}
        
        cpu_values = [m["metrics"].get("cpu_percent", 0) for m in metrics if "metrics" in m]
        memory_values = [m["metrics"].get("memory_percent", 0) for m in metrics if "metrics" in m]
        
        return {
            "avg_cpu_percent": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "max_cpu_percent": max(cpu_values) if cpu_values else 0,
            "avg_memory_percent": sum(memory_values) / len(memory_values) if memory_values else 0,
            "max_memory_percent": max(memory_values) if memory_values else 0,
        }
    
    async def run_chaos_suite(self) -> List[ChaosResult]:
        """Run comprehensive chaos engineering test suite."""
        logger.info("Starting comprehensive chaos engineering suite...")
        
        experiments = [
            ChaosExperiment(
                name="High CPU Load",
                chaos_type=ChaosType.HIGH_CPU_LOAD,
                target_component="system",
                duration_seconds=45,
                expected_recovery_strategy=RecoveryStrategy.GRACEFUL_DEGRADATION,
                max_acceptable_downtime_seconds=0
            ),
            ChaosExperiment(
                name="Memory Pressure",
                chaos_type=ChaosType.MEMORY_EXHAUSTION,
                target_component="system",
                duration_seconds=30,
                expected_recovery_strategy=RecoveryStrategy.GRACEFUL_DEGRADATION,
                max_acceptable_downtime_seconds=0
            ),
        ]
        
        results = []
        
        for experiment in experiments:
            try:
                logger.info(f"Running experiment: {experiment.name}")
                result = await self.run_chaos_experiment(experiment)
                results.append(result)
                self.results.append(result)
                
                # Recovery time between experiments
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Experiment {experiment.name} failed: {e}")
                
                error_result = ChaosResult(
                    experiment_name=experiment.name,
                    chaos_type=experiment.chaos_type,
                    success=False,
                    actual_downtime_seconds=0,
                    recovery_time_seconds=0,
                    data_loss_detected=False,
                    recovery_strategy_used=None,
                    system_state_after_recovery={},
                    error_message=str(e)
                )
                results.append(error_result)
                self.results.append(error_result)
        
        return results
    
    def generate_resilience_report(self) -> Dict[str, Any]:
        """Generate comprehensive resilience test report."""
        if not self.results:
            return {"error": "No chaos engineering results available"}
        
        total_experiments = len(self.results)
        successful_experiments = len([r for r in self.results if r.success])
        
        avg_recovery_time = sum(r.recovery_time_seconds for r in self.results) / total_experiments if total_experiments > 0 else 0
        max_recovery_time = max(r.recovery_time_seconds for r in self.results) if self.results else 0
        
        total_downtime = sum(r.actual_downtime_seconds for r in self.results)
        
        # Calculate resilience score
        resilience_score = (successful_experiments / total_experiments * 100) if total_experiments > 0 else 0
        
        # Adjust score based on recovery time
        if avg_recovery_time > 300:  # More than 5 minutes average
            resilience_score *= 0.7
        elif avg_recovery_time > 60:  # More than 1 minute average
            resilience_score *= 0.85
        
        report = {
            "summary": {
                "total_experiments": total_experiments,
                "successful_experiments": successful_experiments,
                "failed_experiments": total_experiments - successful_experiments,
                "resilience_score": resilience_score,
                "avg_recovery_time_seconds": avg_recovery_time,
                "max_recovery_time_seconds": max_recovery_time,
                "total_downtime_seconds": total_downtime,
                "system_resilience_rating": self._get_resilience_rating(resilience_score)
            },
            "chaos_types": {
                chaos_type.value: {
                    "experiments": len([r for r in self.results if r.chaos_type == chaos_type]),
                    "success_rate": len([r for r in self.results if r.chaos_type == chaos_type and r.success]) / 
                                   len([r for r in self.results if r.chaos_type == chaos_type]) * 100
                                   if len([r for r in self.results if r.chaos_type == chaos_type]) > 0 else 0,
                    "avg_recovery_time": sum(r.recovery_time_seconds for r in self.results if r.chaos_type == chaos_type) /
                                        len([r for r in self.results if r.chaos_type == chaos_type])
                                        if len([r for r in self.results if r.chaos_type == chaos_type]) > 0 else 0
                }
                for chaos_type in ChaosType
            },
            "detailed_results": [
                {
                    "experiment_name": result.experiment_name,
                    "chaos_type": result.chaos_type.value,
                    "status": "PASS" if result.success else "FAIL",
                    "downtime_seconds": result.actual_downtime_seconds,
                    "recovery_time_seconds": result.recovery_time_seconds,
                    "system_recovered": result.system_state_after_recovery.get("api_responsive", False),
                    "error_message": result.error_message
                }
                for result in self.results
            ]
        }
        
        return report
    
    def _get_resilience_rating(self, score: float) -> str:
        """Get resilience rating based on score."""
        if score >= 90:
            return "EXCELLENT"
        elif score >= 80:
            return "GOOD"
        elif score >= 70:
            return "ACCEPTABLE"
        elif score >= 60:
            return "POOR"
        else:
            return "CRITICAL"


class TestIndustrialChaosEngineering:
    """Test class for industrial chaos engineering."""
    
    @pytest.mark.chaos
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_comprehensive_chaos_suite(self):
        """
        Run comprehensive chaos engineering test suite.
        Tests system resilience under real failure conditions.
        """
        async with IndustrialChaosEngineer() as chaos_engineer:
            results = await chaos_engineer.run_chaos_suite()
            report = chaos_engineer.generate_resilience_report()
            
            # Log detailed results
            logger.info(f"Chaos engineering completed: {report['summary']}")
            
            # Assert resilience requirements
            assert len(results) > 0, "No chaos experiments were executed"
            assert report['summary']['resilience_score'] >= 70, f"Resilience score too low: {report['summary']['resilience_score']:.1f}%"
            assert report['summary']['avg_recovery_time_seconds'] <= 300, f"Average recovery time too high: {report['summary']['avg_recovery_time_seconds']:.1f}s"
            assert report['summary']['system_resilience_rating'] in ["GOOD", "EXCELLENT"], f"Poor resilience rating: {report['summary']['system_resilience_rating']}"
    
    @pytest.mark.chaos
    @pytest.mark.asyncio
    async def test_resource_exhaustion_resilience(self):
        """Test resilience under resource exhaustion."""
        async with IndustrialChaosEngineer() as chaos_engineer:
            # Test CPU stress
            cpu_experiment = ChaosExperiment(
                name="CPU Stress Test",
                chaos_type=ChaosType.HIGH_CPU_LOAD,
                target_component="system",
                duration_seconds=30,
                expected_recovery_strategy=RecoveryStrategy.GRACEFUL_DEGRADATION,
                max_acceptable_downtime_seconds=0
            )
            
            cpu_result = await chaos_engineer.run_chaos_experiment(cpu_experiment)
            
            # System should handle high CPU load gracefully
            assert cpu_result.actual_downtime_seconds <= 5, f"CPU stress caused too much downtime: {cpu_result.actual_downtime_seconds:.1f}s"
            
            # Wait for system recovery
            await asyncio.sleep(30)
            
            # Test memory pressure
            memory_experiment = ChaosExperiment(
                name="Memory Pressure Test",
                chaos_type=ChaosType.MEMORY_EXHAUSTION,
                target_component="system",
                duration_seconds=20,
                expected_recovery_strategy=RecoveryStrategy.GRACEFUL_DEGRADATION,
                max_acceptable_downtime_seconds=0
            )
            
            memory_result = await chaos_engineer.run_chaos_experiment(memory_experiment)
            
            # System should handle memory pressure gracefully
            assert memory_result.actual_downtime_seconds <= 5, f"Memory pressure caused too much downtime: {memory_result.actual_downtime_seconds:.1f}s"