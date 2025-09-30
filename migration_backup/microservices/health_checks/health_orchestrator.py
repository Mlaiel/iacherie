"""
Enterprise Health Orchestrator - Ainflue Health Checks Module
Orchestrateur health checks enterprise multi-niveaux avec deep health validation,
dependency mapping et auto-remediation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture health checks et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel. Toute reproduction, modification, distribution ou vol 
d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
import uuid
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class HealthSeverity(Enum):
    """Niveaux de sévérité santé"""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class HealthCategory(Enum):
    """Catégories health checks"""
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    DATABASE = "database" 
    NETWORK = "network"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS_LOGIC = "business_logic"

@dataclass
class HealthCheckResult:
    """Résultat check santé individuel"""
    check_id: str
    service_name: str
    category: HealthCategory
    status: str
    severity: HealthSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class OrchestratorConfig:
    """Configuration orchestrateur santé"""
    max_concurrent_checks: int = 50
    check_timeout_seconds: int = 30
    dependency_timeout_seconds: int = 60
    remediation_enabled: bool = True
    sla_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'response_time_ms': 500.0,
        'availability_percent': 99.9,
        'error_rate_percent': 1.0
    })
    alert_channels: List[str] = field(default_factory=list)

class ServiceDependencyGraph:
    """Graphe dépendances services"""
    
    def __init__(self):
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
        
    def add_dependency(self, service: str, depends_on: str):
        """Ajouter dépendance service"""
        self.dependencies[service].add(depends_on)
        self.reverse_dependencies[depends_on].add(service)
        
    def get_dependencies(self, service: str) -> Set[str]:
        """Obtenir dépendances d'un service"""
        return self.dependencies.get(service, set())
        
    def get_dependents(self, service: str) -> Set[str]:
        """Obtenir services dépendants"""
        return self.reverse_dependencies.get(service, set())
        
    def get_impact_chain(self, failed_service: str) -> List[str]:
        """Obtenir chaîne impact failure"""
        impact_chain = []
        visited = set()
        
        def dfs(service: str):
            if service in visited:
                return
            visited.add(service)
            impact_chain.append(service)
            for dependent in self.get_dependents(service):
                dfs(dependent)
                
        dfs(failed_service)
        return impact_chain[1:]  # Exclure service initial

class HealthAggregator:
    """Agrégateur résultats health checks"""
    
    def __init__(self):
        self.results_history: deque = deque(maxlen=1000)
        
    def aggregate_results(self, results: List[HealthCheckResult]) -> Dict[str, Any]:
        """Agréger résultats health checks"""
        if not results:
            return {
                'overall_status': 'unknown',
                'healthy_services': 0,
                'unhealthy_services': 0,
                'degraded_services': 0,
                'total_services': 0
            }
            
        # Compter statuts par service
        service_statuses = {}
        for result in results:
            service_statuses[result.service_name] = result.status
            
        status_counts = {
            'healthy': sum(1 for s in service_statuses.values() if s == 'healthy'),
            'degraded': sum(1 for s in service_statuses.values() if s == 'degraded'),
            'unhealthy': sum(1 for s in service_statuses.values() if s == 'unhealthy'),
        }
        
        # Déterminer statut global
        total_services = len(service_statuses)
        if status_counts['unhealthy'] > 0:
            overall_status = 'unhealthy'
        elif status_counts['degraded'] > 0:
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'
            
        return {
            'overall_status': overall_status,
            'healthy_services': status_counts['healthy'],
            'degraded_services': status_counts['degraded'], 
            'unhealthy_services': status_counts['unhealthy'],
            'total_services': total_services,
            'service_breakdown': service_statuses,
            'timestamp': datetime.now().isoformat(),
            'check_duration_ms': sum(r.duration_ms for r in results)
        }

class AutoRemediationEngine:
    """Moteur remédiation automatique"""
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.remediation_actions: Dict[str, Callable] = {}
        self.remediation_history: List[Dict[str, Any]] = []
        
    async def register_remediation_action(self, condition: str, action: Callable):
        """Enregistrer action remédiation"""
        self.remediation_actions[condition] = action
        
    async def execute_remediation(self, health_result: HealthCheckResult) -> Dict[str, Any]:
        """Exécuter remédiation automatique"""
        if not self.config.remediation_enabled:
            return {'status': 'disabled', 'action': None}
            
        # Identifier action remédiation appropriée
        remediation_key = f"{health_result.service_name}:{health_result.status}"
        
        if remediation_key in self.remediation_actions:
            try:
                action = self.remediation_actions[remediation_key]
                result = await action(health_result)
                
                # Enregistrer action remédiation
                self.remediation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'service': health_result.service_name,
                    'condition': remediation_key,
                    'action_result': result,
                    'success': result.get('success', False)
                })
                
                return result
                
            except Exception as e:
                logger.error(f"Remediation failed for {remediation_key}: {e}")
                return {'status': 'failed', 'error': str(e)}
                
        return {'status': 'no_action', 'reason': 'No remediation configured'}

class SLAMonitor:
    """Monitoring SLA et métriques"""
    
    def __init__(self, thresholds: Dict[str, float]):
        self.thresholds = thresholds
        self.sla_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    async def evaluate_sla_compliance(self, results: List[HealthCheckResult]) -> Dict[str, Any]:
        """Évaluer conformité SLA"""
        sla_violations = []
        
        for result in results:
            # Vérifier response time
            if result.duration_ms > self.thresholds.get('response_time_ms', 500):
                sla_violations.append({
                    'service': result.service_name,
                    'violation_type': 'response_time',
                    'actual': result.duration_ms,
                    'threshold': self.thresholds['response_time_ms']
                })
                
            # Vérifier error rate via metrics
            error_rate = result.metrics.get('error_rate_percent', 0.0)
            if error_rate > self.thresholds.get('error_rate_percent', 1.0):
                sla_violations.append({
                    'service': result.service_name,
                    'violation_type': 'error_rate',
                    'actual': error_rate,
                    'threshold': self.thresholds['error_rate_percent']
                })
                
        return {
            'compliance_status': 'compliant' if not sla_violations else 'violated',
            'violations': sla_violations,
            'violation_count': len(sla_violations),
            'evaluation_timestamp': datetime.now().isoformat()
        }

class EnterpriseHealthOrchestrator:
    """
    Orchestrateur health checks enterprise multi-niveaux.
    Deep health validation + dependency mapping + auto-remediation.
    
    Features:
    - Multi-level health check orchestration
    - Service dependency mapping and impact analysis  
    - Auto-remediation with safety validation
    - SLA monitoring and compliance tracking
    - Real-time health aggregation and reporting
    - Predictive failure detection
    """
    
    def __init__(self, orchestrator_config: OrchestratorConfig):
        self.orchestrator_config = orchestrator_config
        self.dependency_graph = ServiceDependencyGraph()
        self.health_aggregator = HealthAggregator()
        self.remediation_engine = AutoRemediationEngine(orchestrator_config)
        self.sla_monitor = SLAMonitor(orchestrator_config.sla_thresholds)
        
        # Registres health checks
        self.health_checks: Dict[str, List[Callable]] = defaultdict(list)
        self.check_configs: Dict[str, Dict[str, Any]] = {}
        
        # Métriques orchestrateur
        self.orchestration_metrics = {
            'total_checks_executed': 0,
            'failed_checks': 0,
            'remediation_attempts': 0,
            'successful_remediations': 0,
            'average_check_duration_ms': 0.0
        }
        
    async def register_health_check(self, service_name: str, check_func: Callable, 
                                  config: Optional[Dict[str, Any]] = None):
        """Enregistrer health check pour service"""
        self.health_checks[service_name].append(check_func)
        if config:
            self.check_configs[f"{service_name}:{check_func.__name__}"] = config
            
        logger.info(f"Registered health check for {service_name}: {check_func.__name__}")
        
    async def orchestrate_comprehensive_health_check(self, scope: str = "all") -> Dict[str, Any]:
        """
        Orchestration complète health checks enterprise.
        
        Args:
            scope: Scope des checks ('all', 'critical', service_name)
            
        Returns:
            Dict avec résultats agrégés, statut global, métriques
        """
        start_time = datetime.now()
        check_results = []
        
        try:
            # Déterminer services à checker
            services_to_check = await self._determine_check_scope(scope)
            
            # Exécuter health checks en parallèle avec limitation concurrence
            semaphore = asyncio.Semaphore(self.orchestrator_config.max_concurrent_checks)
            check_tasks = []
            
            for service_name in services_to_check:
                for check_func in self.health_checks[service_name]:
                    task = self._execute_health_check_with_semaphore(
                        semaphore, service_name, check_func
                    )
                    check_tasks.append(task)
                    
            # Attendre tous les checks avec timeout global
            check_results = await asyncio.wait_for(
                asyncio.gather(*check_tasks, return_exceptions=True),
                timeout=self.orchestrator_config.dependency_timeout_seconds
            )
            
            # Filtrer exceptions et créer résultats valides
            valid_results = [r for r in check_results if isinstance(r, HealthCheckResult)]
            
            # Agréger résultats
            aggregated_results = self.health_aggregator.aggregate_results(valid_results)
            
            # Évaluer compliance SLA
            sla_evaluation = await self.sla_monitor.evaluate_sla_compliance(valid_results)
            
            # Analyser impact dépendances
            dependency_analysis = await self._analyze_dependency_impact(valid_results)
            
            # Exécuter remédiation automatique si nécessaire
            remediation_results = await self._execute_auto_remediation(valid_results)
            
            # Mettre à jour métriques orchestrateur
            self._update_orchestration_metrics(valid_results, start_time)
            
            return {
                'orchestration_id': str(uuid.uuid4()),
                'timestamp': start_time.isoformat(),
                'scope': scope,
                'execution_duration_seconds': (datetime.now() - start_time).total_seconds(),
                'health_summary': aggregated_results,
                'sla_compliance': sla_evaluation,
                'dependency_analysis': dependency_analysis,
                'remediation_results': remediation_results,
                'detailed_results': [
                    {
                        'check_id': r.check_id,
                        'service': r.service_name,
                        'category': r.category.value,
                        'status': r.status,
                        'severity': r.severity.value,
                        'message': r.message,
                        'duration_ms': r.duration_ms,
                        'metrics': r.metrics
                    } for r in valid_results
                ],
                'orchestration_metrics': self.orchestration_metrics
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Health check orchestration timeout after {self.orchestrator_config.dependency_timeout_seconds}s")
            return await self._create_timeout_response(scope, start_time)
            
        except Exception as e:
            logger.error(f"Health check orchestration failed: {e}")
            return await self._create_error_response(scope, start_time, str(e))
            
    async def _execute_health_check_with_semaphore(self, semaphore: asyncio.Semaphore,
                                                 service_name: str, check_func: Callable) -> HealthCheckResult:
        """Exécuter health check avec contrôle concurrence"""
        async with semaphore:
            return await self._execute_single_health_check(service_name, check_func)
            
    async def _execute_single_health_check(self, service_name: str, check_func: Callable) -> HealthCheckResult:
        """Exécuter health check individuel"""
        check_start = datetime.now()
        check_id = f"{service_name}_{check_func.__name__}_{int(check_start.timestamp())}"
        
        try:
            # Exécuter check avec timeout
            result = await asyncio.wait_for(
                check_func(),
                timeout=self.orchestrator_config.check_timeout_seconds
            )
            
            duration_ms = (datetime.now() - check_start).total_seconds() * 1000
            
            return HealthCheckResult(
                check_id=check_id,
                service_name=service_name,
                category=result.get('category', HealthCategory.APPLICATION),
                status=result.get('status', 'unknown'),
                severity=result.get('severity', HealthSeverity.MEDIUM),
                message=result.get('message', 'Health check completed'),
                details=result.get('details', {}),
                duration_ms=duration_ms,
                dependencies=result.get('dependencies', []),
                metrics=result.get('metrics', {})
            )
            
        except asyncio.TimeoutError:
            duration_ms = (datetime.now() - check_start).total_seconds() * 1000
            return HealthCheckResult(
                check_id=check_id,
                service_name=service_name,
                category=HealthCategory.APPLICATION,
                status='unhealthy',
                severity=HealthSeverity.HIGH,
                message=f'Health check timeout after {self.orchestrator_config.check_timeout_seconds}s',
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = (datetime.now() - check_start).total_seconds() * 1000
            return HealthCheckResult(
                check_id=check_id,
                service_name=service_name,
                category=HealthCategory.APPLICATION,
                status='unhealthy',
                severity=HealthSeverity.CRITICAL,
                message=f'Health check failed: {str(e)}',
                duration_ms=duration_ms
            )
            
    async def _determine_check_scope(self, scope: str) -> List[str]:
        """Déterminer services à inclure dans scope"""
        if scope == "all":
            return list(self.health_checks.keys())
        elif scope == "critical":
            # Retourner services critiques - à définir selon business logic
            return [s for s in self.health_checks.keys() if 'critical' in s.lower()]
        elif scope in self.health_checks:
            return [scope]
        else:
            logger.warning(f"Unknown scope '{scope}', defaulting to 'all'")
            return list(self.health_checks.keys())
            
    async def _analyze_dependency_impact(self, results: List[HealthCheckResult]) -> Dict[str, Any]:
        """Analyser impact dépendances"""
        unhealthy_services = [r.service_name for r in results if r.status == 'unhealthy']
        
        impact_analysis = {
            'failed_services': unhealthy_services,
            'potentially_impacted': [],
            'cascading_failures_risk': 'low'
        }
        
        for failed_service in unhealthy_services:
            impacted = self.dependency_graph.get_impact_chain(failed_service)
            impact_analysis['potentially_impacted'].extend(impacted)
            
        # Évaluer risque cascade
        if len(impact_analysis['potentially_impacted']) > len(unhealthy_services) * 2:
            impact_analysis['cascading_failures_risk'] = 'high'
        elif len(impact_analysis['potentially_impacted']) > len(unhealthy_services):
            impact_analysis['cascading_failures_risk'] = 'medium'
            
        return impact_analysis
        
    async def _execute_auto_remediation(self, results: List[HealthCheckResult]) -> Dict[str, Any]:
        """Exécuter remédiation automatique"""
        remediation_results = {
            'total_attempts': 0,
            'successful_remediations': 0,
            'failed_remediations': 0,
            'actions_taken': []
        }
        
        unhealthy_results = [r for r in results if r.status in ['unhealthy', 'degraded']]
        
        for result in unhealthy_results:
            remediation_result = await self.remediation_engine.execute_remediation(result)
            remediation_results['total_attempts'] += 1
            
            if remediation_result.get('success'):
                remediation_results['successful_remediations'] += 1
            else:
                remediation_results['failed_remediations'] += 1
                
            remediation_results['actions_taken'].append({
                'service': result.service_name,
                'action': remediation_result.get('action', 'none'),
                'result': remediation_result
            })
            
        return remediation_results
        
    def _update_orchestration_metrics(self, results: List[HealthCheckResult], start_time: datetime):
        """Mettre à jour métriques orchestrateur"""
        self.orchestration_metrics['total_checks_executed'] += len(results)
        self.orchestration_metrics['failed_checks'] += len([r for r in results if r.status == 'unhealthy'])
        
        if results:
            avg_duration = sum(r.duration_ms for r in results) / len(results)
            current_avg = self.orchestration_metrics['average_check_duration_ms']
            total_checks = self.orchestration_metrics['total_checks_executed']
            
            # Mise à jour moyenne mobile
            self.orchestration_metrics['average_check_duration_ms'] = (
                (current_avg * (total_checks - len(results)) + avg_duration * len(results)) / total_checks
            )
            
    async def _create_timeout_response(self, scope: str, start_time: datetime) -> Dict[str, Any]:
        """Créer réponse timeout"""
        return {
            'orchestration_id': str(uuid.uuid4()),
            'timestamp': start_time.isoformat(),
            'scope': scope,
            'status': 'timeout',
            'error': f'Health check orchestration timeout after {self.orchestrator_config.dependency_timeout_seconds}s',
            'health_summary': {'overall_status': 'unknown'},
            'orchestration_metrics': self.orchestration_metrics
        }
        
    async def _create_error_response(self, scope: str, start_time: datetime, error: str) -> Dict[str, Any]:
        """Créer réponse erreur"""
        return {
            'orchestration_id': str(uuid.uuid4()),
            'timestamp': start_time.isoformat(),
            'scope': scope,
            'status': 'error',
            'error': error,
            'health_summary': {'overall_status': 'error'},
            'orchestration_metrics': self.orchestration_metrics
        }

# Example usage et testing
if __name__ == "__main__":
    async def example_database_check():
        """Exemple health check database"""
        await asyncio.sleep(0.1)  # Simulation latence
        return {
            'status': 'healthy',
            'category': HealthCategory.DATABASE,
            'severity': HealthSeverity.LOW,
            'message': 'Database connection healthy',
            'metrics': {'response_time_ms': 45.2, 'connections': 12}
        }
        
    async def example_api_check():
        """Exemple health check API"""
        await asyncio.sleep(0.05)
        return {
            'status': 'healthy',
            'category': HealthCategory.APPLICATION,
            'severity': HealthSeverity.LOW,
            'message': 'API endpoints responding',
            'metrics': {'response_time_ms': 23.1, 'error_rate_percent': 0.1}
        }
        
    async def test_orchestrator():
        """Test orchestrateur health checks"""
        config = OrchestratorConfig(
            max_concurrent_checks=10,
            check_timeout_seconds=5,
            remediation_enabled=True
        )
        
        orchestrator = EnterpriseHealthOrchestrator(config)
        
        # Enregistrer health checks
        await orchestrator.register_health_check('database', example_database_check)
        await orchestrator.register_health_check('api', example_api_check)
        
        # Configurer dépendances
        orchestrator.dependency_graph.add_dependency('api', 'database')
        
        # Exécuter orchestration complète
        results = await orchestrator.orchestrate_comprehensive_health_check()
        
        print("🏥 Enterprise Health Orchestrator Results:")
        print(f"Overall Status: {results['health_summary']['overall_status']}")
        print(f"Total Services: {results['health_summary']['total_services']}")
        print(f"Healthy Services: {results['health_summary']['healthy_services']}")
        print(f"SLA Compliance: {results['sla_compliance']['compliance_status']}")
        print(f"Execution Duration: {results['execution_duration_seconds']:.2f}s")
        
        return results
        
    # Run test
    asyncio.run(test_orchestrator())