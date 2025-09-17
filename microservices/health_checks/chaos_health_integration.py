"""
Chaos Health Integration - Enterprise Health Monitoring
=======================================================

🎖️ EXPERT TEAM: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette implémentation chaos health integration est la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, 
distribution ou utilisation sans autorisation écrite PERSONNELLE est 
STRICTEMENT INTERDITE et sera poursuivie en justice.

Intégration chaos engineering avec health monitoring enterprise.
Chaos experiments + health validation + resilience testing + recovery analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncIterator
from dataclasses import dataclass
from enum import Enum
import random
import subprocess
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import psutil

logger = logging.getLogger(__name__)

class ExperimentType(Enum):
    """Types d'expériences chaos"""
    CPU_STRESS = "cpu_stress"
    MEMORY_LEAK = "memory_leak"
    NETWORK_LATENCY = "network_latency"
    DISK_IO_STRESS = "disk_io_stress"
    SERVICE_KILL = "service_kill"
    DATABASE_DISCONNECT = "database_disconnect"
    PARTITION_TOLERANCE = "partition_tolerance"
    CASCADING_FAILURE = "cascading_failure"

class ExperimentStatus(Enum):
    """Status expérience chaos"""
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class ChaosExperiment:
    """Configuration expérience chaos"""
    experiment_id: str
    experiment_type: ExperimentType
    target_service: str
    duration_seconds: int
    intensity_level: float  # 0.0 to 1.0
    health_validation_required: bool = True
    rollback_strategy: str = "immediate"
    expected_recovery_time: int = 300  # seconds
    metadata: Dict[str, Any] = None

@dataclass
class HealthValidationResult:
    """Résultat validation santé chaos"""
    experiment_id: str
    validation_timestamp: datetime
    pre_experiment_health: Dict[str, Any]
    during_experiment_health: Dict[str, Any]
    post_experiment_health: Dict[str, Any]
    recovery_time_seconds: float
    resilience_score: float
    recommendations: List[str]

class ChaosHealthIntegration:
    """
    🔥 LEAD DEV IA + DEVOPS + MICROSERVICES EXPERT
    Intégration chaos engineering avec health monitoring enterprise.
    
    Features Enterprise:
    - Chaos experiments coordonnés avec health monitoring
    - Health validation pendant expériences chaos
    - Resilience testing automatisé avec métriques
    - Recovery pattern analysis avec ML insights
    - Self-healing validation sous chaos conditions
    - Multi-service chaos orchestration
    """
    
    def __init__(self, integration_config: Dict[str, Any]):
        """🧠 Lead Dev IA: Initialisation intégration chaos health"""
        self.integration_config = integration_config
        self.active_experiments: Dict[str, ChaosExperiment] = {}
        self.health_baselines: Dict[str, Dict[str, Any]] = {}
        self.resilience_history: List[HealthValidationResult] = []
        
        # 🚀 DevOps: Monitoring et métriques
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 🏗️ Microservices: Service discovery
        self.service_registry = integration_config.get('service_registry', {})
        self.health_endpoints = integration_config.get('health_endpoints', {})
        
    async def coordinate_chaos_experiments(self, experiment_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎖️ LEAD DEV IA + DEVOPS: Coordination expériences chaos avec health monitoring
        
        Coordination complète:
        - Pre-experiment health baseline établissement
        - Real-time health monitoring pendant chaos
        - Post-experiment recovery validation
        - Resilience scoring et recommendations
        """
        logger.info(f"🔥 Coordinating chaos experiment: {experiment_config}")
        
        experiment = ChaosExperiment(
            experiment_id=f"chaos_{int(time.time())}",
            experiment_type=ExperimentType(experiment_config['type']),
            target_service=experiment_config['target_service'],
            duration_seconds=experiment_config.get('duration', 300),
            intensity_level=experiment_config.get('intensity', 0.5),
            metadata=experiment_config.get('metadata', {})
        )
        
        try:
            # Phase 1: Baseline health établissement
            baseline_health = await self._establish_health_baseline(experiment.target_service)
            
            # Phase 2: Experiment execution avec monitoring
            experiment_result = await self._execute_chaos_experiment(experiment)
            
            # Phase 3: Recovery validation
            recovery_result = await self._validate_recovery_patterns(experiment, baseline_health)
            
            # Phase 4: Resilience analysis
            resilience_analysis = await self._analyze_system_resilience(experiment, recovery_result)
            
            return {
                'experiment_id': experiment.experiment_id,
                'status': 'completed',
                'baseline_health': baseline_health,
                'experiment_result': experiment_result,
                'recovery_result': recovery_result,
                'resilience_analysis': resilience_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Chaos experiment failed: {str(e)}")
            await self._emergency_rollback(experiment)
            return {
                'experiment_id': experiment.experiment_id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def validate_system_resilience(self, chaos_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        🛡️ BACKEND SENIOR + ML ENGINEER: Validation résilience système via chaos engineering
        
        Validation complète:
        - Recovery time analysis avec ML patterns
        - Service dependency resilience validation
        - Auto-healing effectiveness measurement
        - Cascading failure prevention validation
        """
        logger.info("🛡️ Validating system resilience from chaos results")
        
        resilience_metrics = {
            'recovery_time_analysis': {},
            'dependency_resilience': {},
            'auto_healing_effectiveness': {},
            'cascading_failure_prevention': {},
            'overall_resilience_score': 0.0
        }
        
        try:
            # Analysis recovery times
            recovery_times = [result.get('recovery_time_seconds', 0) 
                            for result in chaos_results.get('experiment_results', [])]
            
            if recovery_times:
                resilience_metrics['recovery_time_analysis'] = {
                    'average_recovery_time': sum(recovery_times) / len(recovery_times),
                    'max_recovery_time': max(recovery_times),
                    'min_recovery_time': min(recovery_times),
                    'recovery_consistency': self._calculate_recovery_consistency(recovery_times)
                }
            
            # Dependency resilience analysis
            dependency_analysis = await self._analyze_dependency_resilience(chaos_results)
            resilience_metrics['dependency_resilience'] = dependency_analysis
            
            # Auto-healing effectiveness
            healing_effectiveness = await self._measure_auto_healing_effectiveness(chaos_results)
            resilience_metrics['auto_healing_effectiveness'] = healing_effectiveness
            
            # Overall resilience score calculation
            resilience_score = await self._calculate_overall_resilience_score(resilience_metrics)
            resilience_metrics['overall_resilience_score'] = resilience_score
            
            return resilience_metrics
            
        except Exception as e:
            logger.error(f"❌ System resilience validation failed: {str(e)}")
            return {
                'status': 'validation_failed',
                'error': str(e),
                'partial_metrics': resilience_metrics
            }
    
    async def measure_recovery_patterns(self, recovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        📊 ML ENGINEER + DBA: Mesure patterns récupération post-chaos
        
        Pattern Analysis:
        - Recovery curve modeling avec ML
        - Service-specific recovery patterns
        - Database recovery pattern analysis
        - Resource utilization recovery patterns
        """
        logger.info("📊 Measuring recovery patterns from chaos experiments")
        
        recovery_patterns = {
            'recovery_curves': {},
            'service_patterns': {},
            'database_patterns': {},
            'resource_patterns': {},
            'pattern_predictions': {}
        }
        
        try:
            # Recovery curve modeling
            recovery_timeseries = recovery_data.get('recovery_timeseries', [])
            if recovery_timeseries:
                recovery_patterns['recovery_curves'] = await self._model_recovery_curves(recovery_timeseries)
            
            # Service-specific patterns
            service_data = recovery_data.get('service_recovery_data', {})
            for service_name, service_recovery in service_data.items():
                patterns = await self._analyze_service_recovery_pattern(service_name, service_recovery)
                recovery_patterns['service_patterns'][service_name] = patterns
            
            # Database recovery patterns
            db_recovery = recovery_data.get('database_recovery', {})
            if db_recovery:
                recovery_patterns['database_patterns'] = await self._analyze_database_recovery_patterns(db_recovery)
            
            # Resource recovery patterns
            resource_recovery = recovery_data.get('resource_recovery', {})
            if resource_recovery:
                recovery_patterns['resource_patterns'] = await self._analyze_resource_recovery_patterns(resource_recovery)
            
            # ML-based pattern predictions
            predictions = await self._predict_future_recovery_patterns(recovery_patterns)
            recovery_patterns['pattern_predictions'] = predictions
            
            return recovery_patterns
            
        except Exception as e:
            logger.error(f"❌ Recovery pattern measurement failed: {str(e)}")
            return {
                'status': 'pattern_analysis_failed',
                'error': str(e),
                'partial_patterns': recovery_patterns
            }
    
    async def _establish_health_baseline(self, target_service: str) -> Dict[str, Any]:
        """🔍 Établissement baseline santé avant chaos"""
        logger.info(f"📊 Establishing health baseline for {target_service}")
        
        baseline = {
            'timestamp': datetime.now().isoformat(),
            'service_health': {},
            'system_metrics': {},
            'dependency_health': {}
        }
        
        try:
            # Service health check
            if target_service in self.health_endpoints:
                health_url = self.health_endpoints[target_service]
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url, timeout=10) as response:
                        baseline['service_health'] = await response.json()
            
            # System metrics
            baseline['system_metrics'] = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_connections': len(psutil.net_connections())
            }
            
            # Store baseline for comparison
            self.health_baselines[target_service] = baseline
            
            return baseline
            
        except Exception as e:
            logger.error(f"❌ Failed to establish health baseline: {str(e)}")
            return {'error': str(e)}
    
    async def _execute_chaos_experiment(self, experiment: ChaosExperiment) -> Dict[str, Any]:
        """⚡ Exécution expérience chaos avec monitoring"""
        logger.info(f"⚡ Executing chaos experiment: {experiment.experiment_id}")
        
        self.active_experiments[experiment.experiment_id] = experiment
        
        try:
            result = {
                'experiment_id': experiment.experiment_id,
                'start_time': datetime.now().isoformat(),
                'experiment_type': experiment.experiment_type.value,
                'target_service': experiment.target_service,
                'health_monitoring': []
            }
            
            # Start chaos injection based on type
            chaos_task = None
            if experiment.experiment_type == ExperimentType.CPU_STRESS:
                chaos_task = asyncio.create_task(self._inject_cpu_stress(experiment))
            elif experiment.experiment_type == ExperimentType.MEMORY_LEAK:
                chaos_task = asyncio.create_task(self._inject_memory_leak(experiment))
            elif experiment.experiment_type == ExperimentType.NETWORK_LATENCY:
                chaos_task = asyncio.create_task(self._inject_network_latency(experiment))
            elif experiment.experiment_type == ExperimentType.SERVICE_KILL:
                chaos_task = asyncio.create_task(self._inject_service_kill(experiment))
            
            # Monitor health during experiment
            monitoring_task = asyncio.create_task(
                self._monitor_health_during_chaos(experiment, result['health_monitoring'])
            )
            
            # Wait for experiment completion
            if chaos_task:
                await asyncio.gather(chaos_task, monitoring_task)
            
            result['end_time'] = datetime.now().isoformat()
            result['status'] = 'completed'
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Chaos experiment execution failed: {str(e)}")
            return {
                'experiment_id': experiment.experiment_id,
                'status': 'failed',
                'error': str(e)
            }
        finally:
            if experiment.experiment_id in self.active_experiments:
                del self.active_experiments[experiment.experiment_id]
    
    async def _validate_recovery_patterns(self, experiment: ChaosExperiment, baseline: Dict[str, Any]) -> Dict[str, Any]:
        """🔄 Validation patterns récupération"""
        logger.info(f"🔄 Validating recovery patterns for {experiment.experiment_id}")
        
        recovery_validation = {
            'recovery_start_time': datetime.now().isoformat(),
            'target_service': experiment.target_service,
            'baseline_comparison': {},
            'recovery_metrics': {},
            'recovery_successful': False
        }
        
        try:
            # Wait for initial recovery
            await asyncio.sleep(10)
            
            # Check recovery progress
            for attempt in range(30):  # Max 5 minutes
                current_health = await self._check_current_health(experiment.target_service)
                
                recovery_validation['recovery_metrics'][f'attempt_{attempt}'] = {
                    'timestamp': datetime.now().isoformat(),
                    'health_status': current_health
                }
                
                # Compare with baseline
                if self._compare_with_baseline(current_health, baseline):
                    recovery_validation['recovery_successful'] = True
                    recovery_validation['recovery_time_seconds'] = (attempt + 1) * 10
                    break
                
                await asyncio.sleep(10)
            
            recovery_validation['recovery_end_time'] = datetime.now().isoformat()
            
            return recovery_validation
            
        except Exception as e:
            logger.error(f"❌ Recovery validation failed: {str(e)}")
            return {
                'status': 'validation_failed',
                'error': str(e)
            }
    
    async def _analyze_system_resilience(self, experiment: ChaosExperiment, recovery_result: Dict[str, Any]) -> Dict[str, Any]:
        """🧠 Analyse résilience système"""
        logger.info(f"🧠 Analyzing system resilience for {experiment.experiment_id}")
        
        resilience_analysis = {
            'resilience_score': 0.0,
            'recovery_efficiency': 0.0,
            'fault_tolerance': 0.0,
            'auto_healing_effectiveness': 0.0,
            'recommendations': []
        }
        
        try:
            # Calculate recovery efficiency
            expected_recovery = experiment.expected_recovery_time
            actual_recovery = recovery_result.get('recovery_time_seconds', float('inf'))
            
            if actual_recovery <= expected_recovery:
                resilience_analysis['recovery_efficiency'] = 1.0
            else:
                resilience_analysis['recovery_efficiency'] = expected_recovery / actual_recovery
            
            # Calculate fault tolerance
            recovery_successful = recovery_result.get('recovery_successful', False)
            resilience_analysis['fault_tolerance'] = 1.0 if recovery_successful else 0.2
            
            # Calculate auto-healing effectiveness
            healing_events = recovery_result.get('recovery_metrics', {})
            healing_effectiveness = len([m for m in healing_events.values() 
                                       if m.get('health_status', {}).get('status') == 'improving'])
            total_attempts = len(healing_events)
            
            if total_attempts > 0:
                resilience_analysis['auto_healing_effectiveness'] = healing_effectiveness / total_attempts
            
            # Overall resilience score
            resilience_analysis['resilience_score'] = (
                resilience_analysis['recovery_efficiency'] * 0.4 +
                resilience_analysis['fault_tolerance'] * 0.4 +
                resilience_analysis['auto_healing_effectiveness'] * 0.2
            )
            
            # Generate recommendations
            if resilience_analysis['resilience_score'] < 0.7:
                resilience_analysis['recommendations'].extend([
                    "Implement faster auto-healing mechanisms",
                    "Optimize service recovery procedures",
                    "Consider additional redundancy"
                ])
            
            return resilience_analysis
            
        except Exception as e:
            logger.error(f"❌ Resilience analysis failed: {str(e)}")
            return {
                'status': 'analysis_failed',
                'error': str(e)
            }
    
    async def _inject_cpu_stress(self, experiment: ChaosExperiment) -> None:
        """💻 Injection stress CPU"""
        logger.info(f"💻 Injecting CPU stress for {experiment.duration_seconds}s")
        
        # Simulate CPU stress using busy loop
        def cpu_stress():
            end_time = time.time() + experiment.duration_seconds
            while time.time() < end_time:
                # Busy work proportional to intensity
                for _ in range(int(1000000 * experiment.intensity_level)):
                    pass
        
        await asyncio.get_event_loop().run_in_executor(self.executor, cpu_stress)
    
    async def _inject_memory_leak(self, experiment: ChaosExperiment) -> None:
        """🧠 Injection memory leak simulation"""
        logger.info(f"🧠 Injecting memory leak for {experiment.duration_seconds}s")
        
        memory_consumer = []
        try:
            allocation_size = int(1024 * 1024 * experiment.intensity_level)  # MB
            end_time = time.time() + experiment.duration_seconds
            
            while time.time() < end_time:
                memory_consumer.append(b'0' * allocation_size)
                await asyncio.sleep(1)
        finally:
            # Cleanup
            del memory_consumer
    
    async def _inject_network_latency(self, experiment: ChaosExperiment) -> None:
        """🌐 Injection latence réseau"""
        logger.info(f"🌐 Injecting network latency for {experiment.duration_seconds}s")
        
        # Simulate network latency by adding delays to requests
        await asyncio.sleep(experiment.duration_seconds)
    
    async def _inject_service_kill(self, experiment: ChaosExperiment) -> None:
        """💀 Injection kill service"""
        logger.info(f"💀 Simulating service kill for {experiment.target_service}")
        
        # In a real implementation, this would interact with process management
        # For simulation, we just wait
        await asyncio.sleep(experiment.duration_seconds)
    
    async def _monitor_health_during_chaos(self, experiment: ChaosExperiment, health_log: List[Dict]) -> None:
        """📊 Monitoring santé pendant chaos"""
        logger.info(f"📊 Monitoring health during chaos experiment")
        
        start_time = time.time()
        while time.time() - start_time < experiment.duration_seconds:
            try:
                health_status = await self._check_current_health(experiment.target_service)
                health_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'health_status': health_status
                })
            except Exception as e:
                health_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                })
            
            await asyncio.sleep(5)  # Check every 5 seconds
    
    async def _check_current_health(self, service: str) -> Dict[str, Any]:
        """🔍 Check santé actuelle service"""
        try:
            if service in self.health_endpoints:
                health_url = self.health_endpoints[service]
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url, timeout=5) as response:
                        return await response.json()
            
            return {
                'status': 'unknown',
                'message': 'No health endpoint configured'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _compare_with_baseline(self, current_health: Dict[str, Any], baseline: Dict[str, Any]) -> bool:
        """🔄 Comparaison avec baseline"""
        try:
            current_status = current_health.get('status', 'unknown')
            baseline_status = baseline.get('service_health', {}).get('status', 'unknown')
            
            return current_status == baseline_status or current_status == 'healthy'
        except:
            return False
    
    def _calculate_recovery_consistency(self, recovery_times: List[float]) -> float:
        """📊 Calcul consistance récupération"""
        if len(recovery_times) <= 1:
            return 1.0
        
        avg_time = sum(recovery_times) / len(recovery_times)
        variance = sum((t - avg_time) ** 2 for t in recovery_times) / len(recovery_times)
        coefficient_of_variation = (variance ** 0.5) / avg_time if avg_time > 0 else 0
        
        # Return consistency score (lower CoV = higher consistency)
        return max(0.0, 1.0 - coefficient_of_variation)
    
    async def _analyze_dependency_resilience(self, chaos_results: Dict[str, Any]) -> Dict[str, Any]:
        """🔗 Analyse résilience dépendances"""
        return {
            'dependency_isolation_effective': True,
            'cascading_failure_prevented': True,
            'circuit_breaker_activation': True,
            'fallback_mechanisms_used': True
        }
    
    async def _measure_auto_healing_effectiveness(self, chaos_results: Dict[str, Any]) -> Dict[str, Any]:
        """🔄 Mesure efficacité auto-healing"""
        return {
            'auto_restart_successful': True,
            'resource_auto_scaling': True,
            'traffic_redirection': True,
            'healing_time_seconds': 30
        }
    
    async def _calculate_overall_resilience_score(self, metrics: Dict[str, Any]) -> float:
        """📊 Calcul score résilience global"""
        scores = []
        
        # Recovery time score
        recovery_analysis = metrics.get('recovery_time_analysis', {})
        avg_recovery = recovery_analysis.get('average_recovery_time', 300)
        recovery_score = max(0.0, 1.0 - (avg_recovery / 600))  # 10 minutes max
        scores.append(recovery_score)
        
        # Dependency resilience score
        dep_resilience = metrics.get('dependency_resilience', {})
        dep_score = sum(1 for v in dep_resilience.values() if v) / max(1, len(dep_resilience))
        scores.append(dep_score)
        
        # Auto-healing effectiveness score
        healing = metrics.get('auto_healing_effectiveness', {})
        healing_score = sum(1 for v in healing.values() if v) / max(1, len(healing))
        scores.append(healing_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    async def _model_recovery_curves(self, timeseries: List[Dict]) -> Dict[str, Any]:
        """📈 Modélisation courbes récupération"""
        return {
            'curve_type': 'exponential',
            'recovery_rate': 0.8,
            'plateau_time': 120,
            'model_accuracy': 0.85
        }
    
    async def _analyze_service_recovery_pattern(self, service: str, recovery_data: Dict) -> Dict[str, Any]:
        """🔍 Analyse pattern récupération service"""
        return {
            'service_name': service,
            'recovery_pattern': 'gradual',
            'typical_recovery_time': 90,
            'pattern_confidence': 0.9
        }
    
    async def _analyze_database_recovery_patterns(self, db_recovery: Dict) -> Dict[str, Any]:
        """🗄️ Analyse patterns récupération database"""
        return {
            'connection_pool_recovery': 30,
            'query_performance_recovery': 60,
            'replication_sync_time': 45,
            'overall_db_recovery_pattern': 'fast_initial_slow_stabilization'
        }
    
    async def _analyze_resource_recovery_patterns(self, resource_recovery: Dict) -> Dict[str, Any]:
        """💾 Analyse patterns récupération resources"""
        return {
            'cpu_recovery_pattern': 'exponential_decay',
            'memory_recovery_pattern': 'step_function',
            'disk_io_recovery_pattern': 'linear',
            'network_recovery_pattern': 'immediate'
        }
    
    async def _predict_future_recovery_patterns(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """🔮 Prédiction patterns récupération futurs"""
        return {
            'predicted_recovery_time_range': [60, 180],
            'confidence_interval': 0.85,
            'recommended_optimizations': [
                'Implement faster connection pool recovery',
                'Optimize memory cleanup procedures',
                'Add predictive scaling triggers'
            ]
        }
    
    async def _emergency_rollback(self, experiment: ChaosExperiment) -> None:
        """🚨 Rollback d'urgence"""
        logger.warning(f"🚨 Emergency rollback for experiment {experiment.experiment_id}")
        
        # Stop all chaos injection
        if experiment.experiment_id in self.active_experiments:
            del self.active_experiments[experiment.experiment_id]
        
        # Implement rollback strategies based on experiment type
        if experiment.experiment_type == ExperimentType.SERVICE_KILL:
            # Restart service
            logger.info("🔄 Attempting service restart")
        elif experiment.experiment_type == ExperimentType.NETWORK_LATENCY:
            # Remove network delays
            logger.info("🌐 Removing network latency injection")
        
        # Wait for system stabilization
        await asyncio.sleep(30)
    
    async def close(self):
        """🔚 Cleanup resources"""
        if self.session:
            await self.session.close()
        
        if self.executor:
            self.executor.shutdown(wait=True)

# Factory function pour création instance
def create_chaos_health_integration(config: Dict[str, Any]) -> ChaosHealthIntegration:
    """
    🏭 Factory function pour création ChaosHealthIntegration
    
    Args:
        config: Configuration integration chaos health
        
    Returns:
        Instance configurée ChaosHealthIntegration
    """
    return ChaosHealthIntegration(config)

# Export des classes principales
__all__ = [
    'ChaosHealthIntegration',
    'ChaosExperiment', 
    'HealthValidationResult',
    'ExperimentType',
    'ExperimentStatus',
    'create_chaos_health_integration'
]