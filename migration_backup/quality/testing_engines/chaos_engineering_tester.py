#!/usr/bin/env python3
"""
🧪 CHAOS ENGINEERING TESTER - ENTERPRISE RESILIENCE TESTING
==========================================================

Testeur enterprise pour l'ingénierie du chaos, validation de la résilience
système et détection des points de défaillance critiques.

© 2025 Fahed Mlaiel - Architecture Quality Assurance Propriétaire Ultra-Avancée
Tous droits réservés. Contact: mlaiel@live.de

🎯 FONCTIONNALITÉS ENTERPRISE:
- Tests de résilience automatisés
- Injection de pannes contrôlées
- Validation de la récupération
- Monitoring de la stabilité
- Reporting de résilience détaillé
"""

import asyncio
import logging
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class ChaosType(Enum):
    """Types de chaos engineering supportés"""
    SERVICE_FAILURE = "service_failure"
    NETWORK_LATENCY = "network_latency"
    NETWORK_PARTITION = "network_partition"
    CPU_STRESS = "cpu_stress"
    MEMORY_PRESSURE = "memory_pressure"
    DISK_FAILURE = "disk_failure"
    DATABASE_SLOWDOWN = "database_slowdown"
    DEPENDENCY_TIMEOUT = "dependency_timeout"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    TRAFFIC_SPIKE = "traffic_spike"

class ChaosImpact(Enum):
    """Impact des tests de chaos"""
    MINIMAL = "minimal"      # <5% impact
    LOW = "low"             # 5-15% impact
    MEDIUM = "medium"       # 15-30% impact
    HIGH = "high"           # 30-50% impact
    CRITICAL = "critical"   # >50% impact

@dataclass
class ChaosExperiment:
    """Expérience de chaos engineering"""
    experiment_id: str
    name: str
    chaos_type: ChaosType
    target_service: str
    duration_seconds: int
    impact_level: ChaosImpact
    parameters: Dict[str, Any] = field(default_factory=dict)
    preconditions: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    rollback_strategy: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass
class ChaosResult:
    """Résultat d'une expérience de chaos"""
    experiment_id: str
    success: bool
    start_time: datetime
    end_time: datetime
    duration: float
    impact_observed: ChaosImpact
    metrics_before: Dict[str, float]
    metrics_during: Dict[str, float]
    metrics_after: Dict[str, float]
    recovery_time: float
    issues_detected: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    resilience_score: float = 0.0

@dataclass
class ResilienceReport:
    """Rapport de résilience complet"""
    report_id: str
    timestamp: datetime
    total_experiments: int
    successful_experiments: int
    overall_resilience_score: float
    experiment_results: List[ChaosResult]
    critical_weaknesses: List[str] = field(default_factory=list)
    improvement_recommendations: List[str] = field(default_factory=list)
    system_stability_trend: str = "unknown"

class EnterpriseChaosEngineeringTester:
    """
    🏆 Testeur Enterprise Chaos Engineering Ultra-Avancé
    
    Fonctionnalités clés:
    - Injection contrôlée de pannes système
    - Validation automatique de la résilience
    - Tests de récupération et failover
    - Monitoring impact temps réel
    - Scoring de résilience intelligent
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration des expériences par défaut
        self.default_experiments = self._initialize_default_experiments()
        
        # Historique des expériences
        self.experiment_history: List[ChaosResult] = []
        
        # Métriques du testeur
        self.tester_metrics = {
            "total_experiments": 0,
            "successful_experiments": 0,
            "failures_detected": 0,
            "average_recovery_time": 0.0,
            "system_resilience_score": 0.0
        }
        
        # Configuration sécurité
        self.safety_limits = {
            "max_concurrent_experiments": 3,
            "max_experiment_duration": 300,  # 5 minutes
            "min_recovery_time": 30,         # 30 secondes
            "emergency_stop_threshold": 80   # 80% impact
        }
    
    def _initialize_default_experiments(self) -> List[ChaosExperiment]:
        """Initialise les expériences de chaos par défaut"""
        return [
            ChaosExperiment(
                experiment_id="service_failure_test",
                name="Service Failure Resilience Test",
                chaos_type=ChaosType.SERVICE_FAILURE,
                target_service="api_gateway",
                duration_seconds=60,
                impact_level=ChaosImpact.MEDIUM,
                parameters={"failure_rate": 0.3, "failure_type": "connection_refused"},
                preconditions=["system_healthy", "backup_services_available"],
                success_criteria=["failover_triggered", "recovery_time < 30s", "data_consistency_maintained"],
                rollback_strategy="restart_service",
                tags=["resilience", "failover", "critical"]
            ),
            ChaosExperiment(
                experiment_id="network_latency_test",
                name="Network Latency Impact Test",
                chaos_type=ChaosType.NETWORK_LATENCY,
                target_service="database",
                duration_seconds=120,
                impact_level=ChaosImpact.LOW,
                parameters={"added_latency_ms": 500, "jitter_ms": 100},
                preconditions=["normal_traffic_load"],
                success_criteria=["response_time_degradation < 50%", "no_timeouts", "circuit_breaker_not_triggered"],
                rollback_strategy="remove_latency_injection",
                tags=["network", "performance", "medium"]
            ),
            ChaosExperiment(
                experiment_id="cpu_stress_test",
                name="CPU Stress Resilience Test",
                chaos_type=ChaosType.CPU_STRESS,
                target_service="compute_service",
                duration_seconds=90,
                impact_level=ChaosImpact.HIGH,
                parameters={"cpu_load_percent": 85, "duration_variance": 0.2},
                preconditions=["auto_scaling_enabled"],
                success_criteria=["auto_scaling_triggered", "performance_degradation < 30%", "no_service_crashes"],
                rollback_strategy="reduce_cpu_load",
                tags=["cpu", "auto-scaling", "high"]
            ),
            ChaosExperiment(
                experiment_id="database_slowdown_test",
                name="Database Slowdown Impact Test",
                chaos_type=ChaosType.DATABASE_SLOWDOWN,
                target_service="main_database",
                duration_seconds=150,
                impact_level=ChaosImpact.MEDIUM,
                parameters={"query_delay_ms": 1000, "affected_operations": ["read", "write"]},
                preconditions=["database_replicas_healthy", "connection_pool_configured"],
                success_criteria=["connection_pool_not_exhausted", "read_replicas_utilized", "no_data_loss"],
                rollback_strategy="restore_normal_db_performance",
                tags=["database", "performance", "data"]
            )
        ]
    
    async def run_chaos_experiment(self, experiment: ChaosExperiment) -> ChaosResult:
        """
        Exécute une expérience de chaos engineering
        
        Args:
            experiment: Configuration de l'expérience à exécuter
            
        Returns:
            Résultat détaillé de l'expérience
        """
        start_time = datetime.now()
        self.logger.info(f"🧪 Démarrage expérience chaos: {experiment.name}")
        
        try:
            # Vérification des préconditions
            preconditions_met = await self._check_preconditions(experiment)
            if not preconditions_met:
                return self._create_failed_result(experiment, start_time, "Préconditions non remplies")
            
            # Collecte métriques baseline
            metrics_before = await self._collect_baseline_metrics(experiment.target_service)
            
            # Injection du chaos
            chaos_injection_success = await self._inject_chaos(experiment)
            if not chaos_injection_success:
                return self._create_failed_result(experiment, start_time, "Échec injection chaos")
            
            # Monitoring pendant l'expérience
            monitoring_task = asyncio.create_task(
                self._monitor_during_chaos(experiment, metrics_before)
            )
            
            # Attente durée expérience
            await asyncio.sleep(experiment.duration_seconds)
            
            # Collecte métriques pendant le chaos
            metrics_during = await self._collect_metrics_during_chaos(experiment.target_service)
            
            # Rollback/récupération
            recovery_start = time.time()
            rollback_success = await self._execute_rollback(experiment)
            
            # Attente récupération
            await self._wait_for_recovery(experiment.target_service)
            recovery_time = time.time() - recovery_start
            
            # Collecte métriques après récupération
            metrics_after = await self._collect_recovery_metrics(experiment.target_service)
            
            # Arrêt monitoring
            monitoring_task.cancel()
            
            # Évaluation résultats
            success = await self._evaluate_experiment_success(experiment, metrics_before, metrics_during, metrics_after)
            impact_observed = self._calculate_observed_impact(metrics_before, metrics_during)
            issues_detected = await self._analyze_issues(experiment, metrics_before, metrics_during, metrics_after)
            recommendations = await self._generate_recommendations(experiment, issues_detected)
            resilience_score = self._calculate_resilience_score(experiment, success, recovery_time, impact_observed)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = ChaosResult(
                experiment_id=experiment.experiment_id,
                success=success,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                impact_observed=impact_observed,
                metrics_before=metrics_before,
                metrics_during=metrics_during,
                metrics_after=metrics_after,
                recovery_time=recovery_time,
                issues_detected=issues_detected,
                recommendations=recommendations,
                resilience_score=resilience_score
            )
            
            # Mise à jour historique
            self.experiment_history.append(result)
            await self._update_tester_metrics(result)
            
            self.logger.info(f"✅ Expérience terminée: Score résilience {resilience_score:.1f}%")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur expérience chaos: {e}")
            return self._create_failed_result(experiment, start_time, str(e))
    
    async def run_chaos_suite(self, experiments: Optional[List[ChaosExperiment]] = None) -> ResilienceReport:
        """
        Exécute une suite complète d'expériences de chaos
        
        Args:
            experiments: Liste d'expériences (utilise les défauts si None)
            
        Returns:
            Rapport de résilience complet
        """
        if experiments is None:
            experiments = self.default_experiments
        
        self.logger.info(f"🚀 Démarrage suite chaos engineering: {len(experiments)} expériences")
        
        results = []
        for experiment in experiments:
            try:
                result = await self.run_chaos_experiment(experiment)
                results.append(result)
                
                # Pause sécurité entre expériences
                await asyncio.sleep(self.safety_limits["min_recovery_time"])
                
            except Exception as e:
                self.logger.error(f"Erreur expérience {experiment.experiment_id}: {e}")
        
        # Génération rapport global
        report = await self._generate_resilience_report(results)
        
        self.logger.info(f"📊 Suite terminée: Score global {report.overall_resilience_score:.1f}%")
        return report
    
    async def _check_preconditions(self, experiment: ChaosExperiment) -> bool:
        """Vérifie que les préconditions sont remplies"""
        for precondition in experiment.preconditions:
            if precondition == "system_healthy":
                # Simulation vérification santé système
                system_health = await self._check_system_health()
                if not system_health:
                    self.logger.warning(f"Précondition échouée: {precondition}")
                    return False
            
            elif precondition == "backup_services_available":
                # Simulation vérification services backup
                backup_available = random.choice([True, True, True, False])  # 75% chance
                if not backup_available:
                    self.logger.warning(f"Précondition échouée: {precondition}")
                    return False
        
        return True
    
    async def _check_system_health(self) -> bool:
        """Vérifie la santé globale du système"""
        # Simulation health check
        await asyncio.sleep(0.1)
        return random.choice([True, True, True, True, False])  # 80% healthy
    
    async def _collect_baseline_metrics(self, service: str) -> Dict[str, float]:
        """Collecte les métriques baseline avant l'expérience"""
        # Simulation collecte métriques
        await asyncio.sleep(0.05)
        
        return {
            "response_time_avg": random.uniform(100, 200),
            "response_time_p95": random.uniform(200, 300),
            "throughput_rps": random.uniform(800, 1200),
            "error_rate": random.uniform(0.1, 0.5),
            "cpu_utilization": random.uniform(40, 60),
            "memory_utilization": random.uniform(50, 70),
            "active_connections": random.randint(100, 300),
            "queue_depth": random.randint(5, 20)
        }
    
    async def _inject_chaos(self, experiment: ChaosExperiment) -> bool:
        """Injecte le chaos selon le type d'expérience"""
        self.logger.info(f"💥 Injection chaos: {experiment.chaos_type.value}")
        
        try:
            if experiment.chaos_type == ChaosType.SERVICE_FAILURE:
                return await self._inject_service_failure(experiment)
            elif experiment.chaos_type == ChaosType.NETWORK_LATENCY:
                return await self._inject_network_latency(experiment)
            elif experiment.chaos_type == ChaosType.CPU_STRESS:
                return await self._inject_cpu_stress(experiment)
            elif experiment.chaos_type == ChaosType.DATABASE_SLOWDOWN:
                return await self._inject_database_slowdown(experiment)
            else:
                self.logger.warning(f"Type de chaos non implémenté: {experiment.chaos_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur injection chaos: {e}")
            return False
    
    async def _inject_service_failure(self, experiment: ChaosExperiment) -> bool:
        """Injecte une panne de service"""
        failure_rate = experiment.parameters.get("failure_rate", 0.3)
        failure_type = experiment.parameters.get("failure_type", "connection_refused")
        
        self.logger.info(f"🔥 Simulation panne service: {failure_rate:.0%} {failure_type}")
        await asyncio.sleep(0.1)  # Simulation temps injection
        
        return True
    
    async def _inject_network_latency(self, experiment: ChaosExperiment) -> bool:
        """Injecte une latence réseau"""
        latency_ms = experiment.parameters.get("added_latency_ms", 500)
        jitter_ms = experiment.parameters.get("jitter_ms", 100)
        
        self.logger.info(f"🌐 Injection latence réseau: +{latency_ms}ms ±{jitter_ms}ms")
        await asyncio.sleep(0.1)
        
        return True
    
    async def _inject_cpu_stress(self, experiment: ChaosExperiment) -> bool:
        """Injecte un stress CPU"""
        cpu_load = experiment.parameters.get("cpu_load_percent", 85)
        
        self.logger.info(f"⚡ Injection stress CPU: {cpu_load}%")
        await asyncio.sleep(0.1)
        
        return True
    
    async def _inject_database_slowdown(self, experiment: ChaosExperiment) -> bool:
        """Injecte un ralentissement base de données"""
        delay_ms = experiment.parameters.get("query_delay_ms", 1000)
        
        self.logger.info(f"🗄️ Injection ralentissement DB: +{delay_ms}ms")
        await asyncio.sleep(0.1)
        
        return True
    
    async def _monitor_during_chaos(self, experiment: ChaosExperiment, baseline_metrics: Dict[str, float]):
        """Monitoring continu pendant l'expérience"""
        try:
            while True:
                current_metrics = await self._collect_current_metrics(experiment.target_service)
                
                # Vérification seuils d'urgence
                impact = self._calculate_current_impact(baseline_metrics, current_metrics)
                if impact > self.safety_limits["emergency_stop_threshold"]:
                    self.logger.critical(f"🚨 ARRÊT URGENCE: Impact {impact}% > seuil {self.safety_limits['emergency_stop_threshold']}%")
                    await self._emergency_stop(experiment)
                    break
                
                await asyncio.sleep(5)  # Monitoring toutes les 5 secondes
                
        except asyncio.CancelledError:
            self.logger.info("📊 Arrêt monitoring chaos")
        except Exception as e:
            self.logger.error(f"Erreur monitoring: {e}")
    
    async def _collect_metrics_during_chaos(self, service: str) -> Dict[str, float]:
        """Collecte métriques pendant le chaos"""
        await asyncio.sleep(0.05)
        
        # Simulation métriques dégradées
        return {
            "response_time_avg": random.uniform(200, 500),
            "response_time_p95": random.uniform(400, 800),
            "throughput_rps": random.uniform(400, 800),
            "error_rate": random.uniform(2, 8),
            "cpu_utilization": random.uniform(60, 90),
            "memory_utilization": random.uniform(70, 85),
            "active_connections": random.randint(50, 200),
            "queue_depth": random.randint(15, 50)
        }
    
    async def _collect_current_metrics(self, service: str) -> Dict[str, float]:
        """Collecte métriques courantes"""
        return await self._collect_metrics_during_chaos(service)
    
    async def _execute_rollback(self, experiment: ChaosExperiment) -> bool:
        """Exécute la stratégie de rollback"""
        self.logger.info(f"🔄 Rollback: {experiment.rollback_strategy}")
        
        # Simulation rollback
        await asyncio.sleep(0.2)
        return True
    
    async def _wait_for_recovery(self, service: str):
        """Attend la récupération du service"""
        self.logger.info("⏳ Attente récupération...")
        
        # Simulation temps de récupération
        recovery_time = random.uniform(5, 15)
        await asyncio.sleep(recovery_time)
    
    async def _collect_recovery_metrics(self, service: str) -> Dict[str, float]:
        """Collecte métriques après récupération"""
        await asyncio.sleep(0.05)
        
        # Simulation métriques récupérées
        return {
            "response_time_avg": random.uniform(90, 180),
            "response_time_p95": random.uniform(180, 280),
            "throughput_rps": random.uniform(850, 1150),
            "error_rate": random.uniform(0.1, 0.4),
            "cpu_utilization": random.uniform(35, 55),
            "memory_utilization": random.uniform(45, 65),
            "active_connections": random.randint(120, 280),
            "queue_depth": random.randint(3, 15)
        }
    
    async def _evaluate_experiment_success(self, experiment: ChaosExperiment, 
                                         before: Dict[str, float], 
                                         during: Dict[str, float], 
                                         after: Dict[str, float]) -> bool:
        """Évalue le succès de l'expérience selon les critères"""
        success_count = 0
        total_criteria = len(experiment.success_criteria)
        
        for criterion in experiment.success_criteria:
            if await self._evaluate_success_criterion(criterion, before, during, after):
                success_count += 1
        
        success_rate = success_count / total_criteria if total_criteria > 0 else 0
        return success_rate >= 0.75  # 75% des critères doivent être respectés
    
    async def _evaluate_success_criterion(self, criterion: str, 
                                        before: Dict[str, float], 
                                        during: Dict[str, float], 
                                        after: Dict[str, float]) -> bool:
        """Évalue un critère de succès spécifique"""
        if "recovery_time < 30s" in criterion:
            # Simulation vérification temps récupération
            return random.choice([True, True, False])  # 67% success
        
        elif "failover_triggered" in criterion:
            return random.choice([True, True, True, False])  # 75% success
        
        elif "response_time_degradation < 50%" in criterion:
            degradation = (during["response_time_avg"] - before["response_time_avg"]) / before["response_time_avg"]
            return degradation < 0.5
        
        elif "no_timeouts" in criterion:
            return during["error_rate"] < 5.0
        
        elif "auto_scaling_triggered" in criterion:
            return random.choice([True, True, False])  # 67% success
        
        elif "no_service_crashes" in criterion:
            return random.choice([True, True, True, True, False])  # 80% success
        
        elif "no_data_loss" in criterion:
            return random.choice([True, True, True, True, True, False])  # 83% success
        
        else:
            # Critère générique
            return random.choice([True, False])
    
    def _calculate_observed_impact(self, before: Dict[str, float], during: Dict[str, float]) -> ChaosImpact:
        """Calcule l'impact observé du chaos"""
        # Calcul impact basé sur dégradation performance
        response_time_impact = (during["response_time_avg"] - before["response_time_avg"]) / before["response_time_avg"]
        throughput_impact = (before["throughput_rps"] - during["throughput_rps"]) / before["throughput_rps"]
        error_rate_impact = (during["error_rate"] - before["error_rate"]) / max(before["error_rate"], 0.1)
        
        overall_impact = (response_time_impact + throughput_impact + error_rate_impact) / 3 * 100
        
        if overall_impact > 50:
            return ChaosImpact.CRITICAL
        elif overall_impact > 30:
            return ChaosImpact.HIGH
        elif overall_impact > 15:
            return ChaosImpact.MEDIUM
        elif overall_impact > 5:
            return ChaosImpact.LOW
        else:
            return ChaosImpact.MINIMAL
    
    def _calculate_current_impact(self, baseline: Dict[str, float], current: Dict[str, float]) -> float:
        """Calcule l'impact actuel en pourcentage"""
        response_time_impact = (current["response_time_avg"] - baseline["response_time_avg"]) / baseline["response_time_avg"]
        return max(0, response_time_impact * 100)
    
    async def _analyze_issues(self, experiment: ChaosExperiment,
                            before: Dict[str, float], 
                            during: Dict[str, float], 
                            after: Dict[str, float]) -> List[str]:
        """Analyse les problèmes détectés"""
        issues = []
        
        # Vérification récupération
        if after["response_time_avg"] > before["response_time_avg"] * 1.2:
            issues.append("Récupération incomplète des temps de réponse")
        
        if after["error_rate"] > before["error_rate"] * 2:
            issues.append("Taux d'erreur élevé persistant après récupération")
        
        # Vérification dégradation
        if during["error_rate"] > 10:
            issues.append("Taux d'erreur critique pendant le chaos")
        
        if during["throughput_rps"] < before["throughput_rps"] * 0.3:
            issues.append("Effondrement du débit pendant le chaos")
        
        return issues
    
    async def _generate_recommendations(self, experiment: ChaosExperiment, issues: List[str]) -> List[str]:
        """Génère des recommandations d'amélioration"""
        recommendations = []
        
        if "Récupération incomplète" in str(issues):
            recommendations.append("Implémenter un monitoring de santé plus robuste")
            recommendations.append("Optimiser les stratégies de récupération automatique")
        
        if "Taux d'erreur critique" in str(issues):
            recommendations.append("Renforcer les circuit breakers et retry mechanisms")
            recommendations.append("Améliorer la gestion d'erreurs en cascade")
        
        if "Effondrement du débit" in str(issues):
            recommendations.append("Configurer l'auto-scaling plus agressif")
            recommendations.append("Implémenter un load balancing plus intelligent")
        
        # Recommandations génériques par type de chaos
        if experiment.chaos_type == ChaosType.SERVICE_FAILURE:
            recommendations.append("Considérer l'implémentation de services de backup")
        elif experiment.chaos_type == ChaosType.NETWORK_LATENCY:
            recommendations.append("Optimiser les timeouts et connection pooling")
        elif experiment.chaos_type == ChaosType.CPU_STRESS:
            recommendations.append("Améliorer la distribution de charge CPU")
        
        return list(set(recommendations))  # Dédoublonnage
    
    def _calculate_resilience_score(self, experiment: ChaosExperiment, 
                                  success: bool, recovery_time: float, 
                                  impact: ChaosImpact) -> float:
        """Calcule le score de résilience"""
        base_score = 100.0
        
        # Pénalité échec
        if not success:
            base_score -= 40.0
        
        # Pénalité temps récupération
        if recovery_time > 60:
            base_score -= min(30.0, (recovery_time - 60) / 10 * 5)
        
        # Pénalité impact
        impact_penalties = {
            ChaosImpact.CRITICAL: 35.0,
            ChaosImpact.HIGH: 25.0,
            ChaosImpact.MEDIUM: 15.0,
            ChaosImpact.LOW: 5.0,
            ChaosImpact.MINIMAL: 0.0
        }
        base_score -= impact_penalties.get(impact, 0)
        
        return max(0.0, base_score)
    
    def _create_failed_result(self, experiment: ChaosExperiment, start_time: datetime, error: str) -> ChaosResult:
        """Crée un résultat d'échec"""
        return ChaosResult(
            experiment_id=experiment.experiment_id,
            success=False,
            start_time=start_time,
            end_time=datetime.now(),
            duration=0.0,
            impact_observed=ChaosImpact.MINIMAL,
            metrics_before={},
            metrics_during={},
            metrics_after={},
            recovery_time=0.0,
            issues_detected=[f"Échec expérience: {error}"],
            recommendations=["Vérifier la configuration et les préconditions"],
            resilience_score=0.0
        )
    
    async def _emergency_stop(self, experiment: ChaosExperiment):
        """Arrêt d'urgence de l'expérience"""
        self.logger.critical(f"🚨 ARRÊT URGENCE expérience {experiment.experiment_id}")
        await self._execute_rollback(experiment)
    
    async def _generate_resilience_report(self, results: List[ChaosResult]) -> ResilienceReport:
        """Génère un rapport de résilience complet"""
        if not results:
            return ResilienceReport(
                report_id=f"resilience_report_{int(time.time() * 1000)}",
                timestamp=datetime.now(),
                total_experiments=0,
                successful_experiments=0,
                overall_resilience_score=0.0,
                experiment_results=[]
            )
        
        successful_count = sum(1 for r in results if r.success)
        overall_score = sum(r.resilience_score for r in results) / len(results)
        
        # Identification faiblesses critiques
        critical_weaknesses = []
        for result in results:
            if not result.success or result.resilience_score < 50:
                critical_weaknesses.extend(result.issues_detected)
        
        # Recommandations globales
        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.recommendations)
        
        improvement_recommendations = list(set(all_recommendations))[:10]  # Top 10
        
        # Tendance stabilité
        if len(results) >= 3:
            recent_scores = [r.resilience_score for r in results[-3:]]
            if all(recent_scores[i] <= recent_scores[i+1] for i in range(len(recent_scores)-1)):
                stability_trend = "improving"
            elif all(recent_scores[i] >= recent_scores[i+1] for i in range(len(recent_scores)-1)):
                stability_trend = "declining"
            else:
                stability_trend = "stable"
        else:
            stability_trend = "insufficient_data"
        
        return ResilienceReport(
            report_id=f"resilience_report_{int(time.time() * 1000)}",
            timestamp=datetime.now(),
            total_experiments=len(results),
            successful_experiments=successful_count,
            overall_resilience_score=overall_score,
            experiment_results=results,
            critical_weaknesses=list(set(critical_weaknesses)),
            improvement_recommendations=improvement_recommendations,
            system_stability_trend=stability_trend
        )
    
    async def _update_tester_metrics(self, result: ChaosResult):
        """Met à jour les métriques du testeur"""
        self.tester_metrics["total_experiments"] += 1
        
        if result.success:
            self.tester_metrics["successful_experiments"] += 1
        
        if result.issues_detected:
            self.tester_metrics["failures_detected"] += len(result.issues_detected)
        
        # Moyenne temps récupération
        total_experiments = self.tester_metrics["total_experiments"]
        current_avg = self.tester_metrics["average_recovery_time"]
        self.tester_metrics["average_recovery_time"] = (
            (current_avg * (total_experiments - 1) + result.recovery_time) / total_experiments
        )
        
        # Score résilience système global
        if self.experiment_history:
            recent_scores = [r.resilience_score for r in self.experiment_history[-10:]]
            self.tester_metrics["system_resilience_score"] = sum(recent_scores) / len(recent_scores)
    
    def get_tester_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques du testeur"""
        success_rate = 0.0
        if self.tester_metrics["total_experiments"] > 0:
            success_rate = (self.tester_metrics["successful_experiments"] / 
                          self.tester_metrics["total_experiments"]) * 100
        
        return {
            **self.tester_metrics,
            "success_rate": success_rate,
            "experiments_history_size": len(self.experiment_history)
        }

# Instance singleton
chaos_engineering_tester = EnterpriseChaosEngineeringTester()

async def main():
    """Test du chaos engineering tester"""
    print("🧪 Test Enterprise Chaos Engineering Tester")
    
    # Test expérience simple
    experiment = ChaosExperiment(
        experiment_id="test_service_failure",
        name="Test Service Failure",
        chaos_type=ChaosType.SERVICE_FAILURE,
        target_service="api_gateway",
        duration_seconds=30,
        impact_level=ChaosImpact.MEDIUM,
        parameters={"failure_rate": 0.3},
        success_criteria=["failover_triggered", "recovery_time < 30s"]
    )
    
    print(f"\\n1. Test expérience individuelle...")
    result = await chaos_engineering_tester.run_chaos_experiment(experiment)
    print(f"   Succès: {result.success}")
    print(f"   Score résilience: {result.resilience_score:.1f}%")
    print(f"   Temps récupération: {result.recovery_time:.1f}s")
    print(f"   Impact observé: {result.impact_observed.value}")
    
    # Test suite complète
    print(f"\\n2. Test suite chaos engineering...")
    report = await chaos_engineering_tester.run_chaos_suite()
    print(f"   Expériences totales: {report.total_experiments}")
    print(f"   Expériences réussies: {report.successful_experiments}")
    print(f"   Score résilience global: {report.overall_resilience_score:.1f}%")
    print(f"   Tendance stabilité: {report.system_stability_trend}")
    
    if report.critical_weaknesses:
        print(f"   Faiblesses critiques: {len(report.critical_weaknesses)}")
        for weakness in report.critical_weaknesses[:3]:
            print(f"     • {weakness}")
    
    # Métriques testeur
    metrics = chaos_engineering_tester.get_tester_metrics()
    print(f"\\n📈 Métriques Testeur:")
    print(f"   Taux de succès: {metrics['success_rate']:.1f}%")
    print(f"   Score résilience système: {metrics['system_resilience_score']:.1f}%")
    print(f"   Temps récupération moyen: {metrics['average_recovery_time']:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())