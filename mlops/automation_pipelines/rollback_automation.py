#!/usr/bin/env python3
"""
🚀 Rollback Automation - Enterprise MLOps Platform
DevOps Expertise: Automation de rollback intelligent avec détection d'anomalies

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import time
import numpy as np
from kubernetes import client, config as k8s_config
import docker
import git
import subprocess
import tempfile
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RollbackTrigger(Enum):
    """Déclencheurs de rollback"""
    MANUAL = "manual"
    HEALTH_CHECK_FAILURE = "health_check_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    ERROR_RATE_SPIKE = "error_rate_spike"
    SLA_VIOLATION = "sla_violation"
    SECURITY_INCIDENT = "security_incident"
    DEPENDENCY_FAILURE = "dependency_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    ANOMALY_DETECTION = "anomaly_detection"

class RollbackStrategy(Enum):
    """Stratégies de rollback"""
    INSTANT = "instant"
    GRADUAL = "gradual"
    CANARY_REVERSE = "canary_reverse"
    BLUE_GREEN_SWITCH = "blue_green_switch"
    ROLLING_BACK = "rolling_back"

class RollbackStatus(Enum):
    """Status du rollback"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"

@dataclass
class MetricThreshold:
    """Seuil de métrique pour déclenchement automatique"""
    metric_name: str
    threshold_value: float
    comparison_operator: str  # ">", "<", ">=", "<=", "=="
    window_size: int = 5  # Nombre de mesures consécutives
    severity: str = "high"  # low, medium, high, critical

@dataclass
class HealthCheck:
    """Configuration de health check"""
    endpoint: str
    expected_status: int = 200
    timeout: int = 10
    interval: int = 30
    failure_threshold: int = 3
    success_threshold: int = 2

@dataclass
class DeploymentVersion:
    """Version de déploiement"""
    version_id: str
    version_tag: str
    deployment_time: datetime
    image_uri: str
    configuration: Dict[str, Any]
    health_status: str = "unknown"
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    is_stable: bool = False
    rollback_count: int = 0

@dataclass
class RollbackPlan:
    """Plan de rollback"""
    plan_id: str
    current_version: str
    target_version: str
    strategy: RollbackStrategy
    trigger: RollbackTrigger
    steps: List[Dict[str, Any]]
    estimated_duration: int  # en secondes
    risk_assessment: Dict[str, Any]
    approval_required: bool = False
    auto_approved: bool = False

@dataclass
class RollbackExecution:
    """Exécution de rollback"""
    execution_id: str
    plan_id: str
    status: RollbackStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    current_step: int = 0
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)
    success_rate: float = 0.0

class AnomalyDetector:
    """Détecteur d'anomalies pour déclenchement automatique de rollback"""
    
    def __init__(self, sensitivity: float = 0.05):
        self.sensitivity = sensitivity
        self.baseline_metrics: Dict[str, List[float]] = {}
        self.anomaly_history: List[Dict[str, Any]] = []
        
    def add_baseline_metric(self, metric_name: str, values: List[float]):
        """Ajoute des métriques de référence"""
        self.baseline_metrics[metric_name] = values
        
    def detect_anomalies(self, current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Détecte les anomalies dans les métriques actuelles"""
        
        anomalies = []
        
        for metric_name, current_value in current_metrics.items():
            if metric_name not in self.baseline_metrics:
                continue
                
            baseline_values = self.baseline_metrics[metric_name]
            if len(baseline_values) < 5:
                continue
                
            # Calcul de statistiques de base
            mean = np.mean(baseline_values)
            std = np.std(baseline_values)
            
            # Détection d'anomalie (méthode simple)
            z_score = abs(current_value - mean) / (std + 1e-8)
            
            # Seuil basé sur la distribution normale
            threshold = 2.0  # 2 écarts-types
            
            if z_score > threshold:
                anomaly = {
                    'metric_name': metric_name,
                    'current_value': current_value,
                    'baseline_mean': mean,
                    'baseline_std': std,
                    'z_score': z_score,
                    'severity': self._calculate_severity(z_score),
                    'timestamp': datetime.now(),
                    'confidence': min(0.95, z_score / 5.0)
                }
                
                anomalies.append(anomaly)
        
        if anomalies:
            self.anomaly_history.extend(anomalies)
            # Garder seulement les 1000 dernières anomalies
            self.anomaly_history = self.anomaly_history[-1000:]
        
        return anomalies
    
    def _calculate_severity(self, z_score: float) -> str:
        """Calcule la sévérité basée sur le z-score"""
        if z_score > 4.0:
            return "critical"
        elif z_score > 3.0:
            return "high"
        elif z_score > 2.5:
            return "medium"
        else:
            return "low"
    
    def get_anomaly_trend(self, metric_name: str, hours: int = 24) -> Dict[str, Any]:
        """Analyse la tendance des anomalies"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_anomalies = [
            a for a in self.anomaly_history
            if a['metric_name'] == metric_name and a['timestamp'] >= cutoff_time
        ]
        
        if not recent_anomalies:
            return {'trend': 'stable', 'anomaly_count': 0}
        
        # Analyse de tendance simple
        severity_counts = {}
        for anomaly in recent_anomalies:
            severity = anomaly['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        total_anomalies = len(recent_anomalies)
        critical_ratio = severity_counts.get('critical', 0) / total_anomalies
        
        if critical_ratio > 0.3:
            trend = 'deteriorating'
        elif critical_ratio > 0.1:
            trend = 'concerning'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'anomaly_count': total_anomalies,
            'severity_distribution': severity_counts,
            'critical_ratio': critical_ratio
        }

class KubernetesRollbackExecutor:
    """Exécuteur de rollback Kubernetes"""
    
    def __init__(self):
        try:
            k8s_config.load_incluster_config()
        except:
            k8s_config.load_kube_config()
        
        self.apps_v1 = client.AppsV1Api()
        self.v1 = client.CoreV1Api()
        
    async def rollback_deployment(
        self, 
        deployment_name: str,
        namespace: str,
        target_revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """Rollback d'un déploiement Kubernetes"""
        
        try:
            # Récupération de l'historique des déploiements
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # Rollback vers la révision précédente ou spécifiée
            if target_revision is None:
                # Rollback vers la révision précédente
                rollback_body = {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "metadata": {
                        "name": deployment_name,
                        "namespace": namespace
                    },
                    "spec": {
                        "rollbackTo": {
                            "revision": 0  # 0 = révision précédente
                        }
                    }
                }
            else:
                rollback_body = {
                    "apiVersion": "apps/v1", 
                    "kind": "Deployment",
                    "metadata": {
                        "name": deployment_name,
                        "namespace": namespace
                    },
                    "spec": {
                        "rollbackTo": {
                            "revision": target_revision
                        }
                    }
                }
            
            # Simulation du rollback (dans une vraie implémentation)
            # self.apps_v1.create_namespaced_deployment_rollback(...)
            
            # Attente de la stabilisation
            await self._wait_for_rollout_completion(deployment_name, namespace)
            
            return {
                'success': True,
                'deployment_name': deployment_name,
                'namespace': namespace,
                'target_revision': target_revision,
                'message': 'Rollback completed successfully'
            }
            
        except Exception as e:
            logger.error(f"Erreur rollback Kubernetes: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _wait_for_rollout_completion(
        self, 
        deployment_name: str, 
        namespace: str,
        timeout: int = 300
    ):
        """Attend la completion du rollout"""
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                deployment = self.apps_v1.read_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace
                )
                
                # Vérification du statut
                conditions = deployment.status.conditions or []
                progressing_condition = None
                available_condition = None
                
                for condition in conditions:
                    if condition.type == "Progressing":
                        progressing_condition = condition
                    elif condition.type == "Available":
                        available_condition = condition
                
                # Vérification si le rollout est terminé
                if (progressing_condition and 
                    progressing_condition.status == "True" and
                    progressing_condition.reason == "NewReplicaSetAvailable" and
                    available_condition and
                    available_condition.status == "True"):
                    
                    logger.info(f"Rollout complété pour {deployment_name}")
                    return
                
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Erreur vérification rollout: {e}")
                await asyncio.sleep(5)
        
        raise TimeoutError(f"Timeout rollout pour {deployment_name}")

class DockerRollbackExecutor:
    """Exécuteur de rollback Docker"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        
    async def rollback_container(
        self, 
        container_name: str,
        target_image: str
    ) -> Dict[str, Any]:
        """Rollback d'un container Docker"""
        
        try:
            # Arrêt du container actuel
            try:
                current_container = self.docker_client.containers.get(container_name)
                current_container.stop()
                current_container.remove()
                logger.info(f"Container {container_name} arrêté et supprimé")
            except docker.errors.NotFound:
                logger.info(f"Container {container_name} non trouvé")
            
            # Redémarrage avec l'image cible
            new_container = self.docker_client.containers.run(
                image=target_image,
                name=container_name,
                detach=True,
                restart_policy={"Name": "always"}
            )
            
            # Attente du démarrage
            await asyncio.sleep(10)
            
            # Vérification de santé
            new_container.reload()
            if new_container.status == "running":
                return {
                    'success': True,
                    'container_id': new_container.id,
                    'container_name': container_name,
                    'target_image': target_image,
                    'status': 'running'
                }
            else:
                return {
                    'success': False,
                    'error': f"Container status: {new_container.status}"
                }
                
        except Exception as e:
            logger.error(f"Erreur rollback Docker: {e}")
            return {
                'success': False,
                'error': str(e)
            }

class GitRollbackExecutor:
    """Exécuteur de rollback Git"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        
    async def rollback_to_commit(
        self, 
        target_commit: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Rollback vers un commit spécifique"""
        
        try:
            # Sauvegarde de l'état actuel
            current_commit = self.repo.head.commit.hexsha
            
            # Checkout vers le commit cible
            self.repo.git.checkout(target_commit)
            
            # Création d'une nouvelle branche de rollback
            rollback_branch = f"rollback-{int(time.time())}"
            self.repo.create_head(rollback_branch)
            self.repo.heads[rollback_branch].checkout()
            
            return {
                'success': True,
                'current_commit': current_commit,
                'target_commit': target_commit,
                'rollback_branch': rollback_branch,
                'message': f'Rollback to commit {target_commit[:8]} completed'
            }
            
        except Exception as e:
            logger.error(f"Erreur rollback Git: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def rollback_to_tag(
        self, 
        target_tag: str
    ) -> Dict[str, Any]:
        """Rollback vers un tag spécifique"""
        
        try:
            # Vérification que le tag existe
            if target_tag not in [tag.name for tag in self.repo.tags]:
                return {
                    'success': False,
                    'error': f'Tag {target_tag} not found'
                }
            
            # Rollback vers le tag
            target_commit = self.repo.tags[target_tag].commit.hexsha
            return await self.rollback_to_commit(target_commit)
            
        except Exception as e:
            logger.error(f"Erreur rollback Git tag: {e}")
            return {
                'success': False,
                'error': str(e)
            }

class RollbackAutomation:
    """Automation de rollback intelligent avec détection d'anomalies"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.anomaly_detector = AnomalyDetector(
            sensitivity=config.get('anomaly_sensitivity', 0.05)
        )
        
        # Exécuteurs
        self.k8s_executor = KubernetesRollbackExecutor()
        self.docker_executor = DockerRollbackExecutor()
        
        # État
        self.deployment_versions: Dict[str, List[DeploymentVersion]] = {}
        self.active_rollbacks: Dict[str, RollbackExecution] = {}
        self.rollback_history: List[RollbackExecution] = []
        self.metric_thresholds: List[MetricThreshold] = []
        self.health_checks: List[HealthCheck] = []
        
        # Monitoring
        self.is_monitoring = False
        
    async def start_monitoring(self):
        """Démarre le monitoring automatique"""
        
        self.is_monitoring = True
        
        # Tâches de monitoring
        asyncio.create_task(self._anomaly_monitoring_loop())
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._metric_threshold_loop())
        
        logger.info("Monitoring de rollback automatique démarré")
    
    async def stop_monitoring(self):
        """Arrête le monitoring automatique"""
        
        self.is_monitoring = False
        logger.info("Monitoring de rollback automatique arrêté")
    
    def add_deployment_version(
        self, 
        service_name: str, 
        version: DeploymentVersion
    ):
        """Ajoute une version de déploiement"""
        
        if service_name not in self.deployment_versions:
            self.deployment_versions[service_name] = []
        
        self.deployment_versions[service_name].append(version)
        
        # Garde seulement les 10 dernières versions
        self.deployment_versions[service_name] = \
            self.deployment_versions[service_name][-10:]
        
        logger.info(f"Version {version.version_tag} ajoutée pour {service_name}")
    
    def add_metric_threshold(self, threshold: MetricThreshold):
        """Ajoute un seuil de métrique"""
        
        self.metric_thresholds.append(threshold)
        logger.info(f"Seuil ajouté: {threshold.metric_name} {threshold.comparison_operator} {threshold.threshold_value}")
    
    def add_health_check(self, health_check: HealthCheck):
        """Ajoute un health check"""
        
        self.health_checks.append(health_check)
        logger.info(f"Health check ajouté: {health_check.endpoint}")
    
    async def create_rollback_plan(
        self,
        service_name: str,
        trigger: RollbackTrigger,
        strategy: RollbackStrategy = RollbackStrategy.INSTANT,
        target_version: Optional[str] = None
    ) -> RollbackPlan:
        """Crée un plan de rollback"""
        
        # Récupération des versions disponibles
        versions = self.deployment_versions.get(service_name, [])
        if not versions:
            raise ValueError(f"Aucune version disponible pour {service_name}")
        
        current_version = versions[-1]
        
        # Sélection de la version cible
        if target_version:
            target_versions = [v for v in versions if v.version_tag == target_version]
            if not target_versions:
                raise ValueError(f"Version cible {target_version} non trouvée")
            target_version_obj = target_versions[0]
        else:
            # Version précédente stable
            stable_versions = [v for v in versions[:-1] if v.is_stable]
            if not stable_versions:
                raise ValueError("Aucune version stable disponible pour rollback")
            target_version_obj = stable_versions[-1]
        
        # Génération des étapes
        steps = self._generate_rollback_steps(
            service_name, current_version, target_version_obj, strategy
        )
        
        # Évaluation des risques
        risk_assessment = self._assess_rollback_risk(
            current_version, target_version_obj, trigger
        )
        
        plan = RollbackPlan(
            plan_id=f"rollback-{service_name}-{uuid.uuid4().hex[:8]}",
            current_version=current_version.version_tag,
            target_version=target_version_obj.version_tag,
            strategy=strategy,
            trigger=trigger,
            steps=steps,
            estimated_duration=self._estimate_rollback_duration(steps),
            risk_assessment=risk_assessment,
            approval_required=risk_assessment['risk_level'] in ['high', 'critical'],
            auto_approved=trigger in [RollbackTrigger.HEALTH_CHECK_FAILURE, RollbackTrigger.SECURITY_INCIDENT]
        )
        
        return plan
    
    def _generate_rollback_steps(
        self,
        service_name: str,
        current_version: DeploymentVersion,
        target_version: DeploymentVersion,
        strategy: RollbackStrategy
    ) -> List[Dict[str, Any]]:
        """Génère les étapes de rollback"""
        
        steps = []
        
        if strategy == RollbackStrategy.INSTANT:
            steps = [
                {
                    'step_id': 'pre_rollback_validation',
                    'name': 'Validation pré-rollback',
                    'executor': 'validation',
                    'config': {
                        'target_version': target_version.version_tag,
                        'checks': ['image_availability', 'configuration_validity']
                    },
                    'timeout': 60
                },
                {
                    'step_id': 'traffic_pause',
                    'name': 'Pause du trafic',
                    'executor': 'traffic',
                    'config': {
                        'service_name': service_name,
                        'action': 'pause'
                    },
                    'timeout': 30
                },
                {
                    'step_id': 'rollback_deployment',
                    'name': 'Rollback du déploiement',
                    'executor': 'kubernetes',
                    'config': {
                        'deployment_name': service_name,
                        'target_image': target_version.image_uri,
                        'target_config': target_version.configuration
                    },
                    'timeout': 300
                },
                {
                    'step_id': 'health_verification',
                    'name': 'Vérification de santé',
                    'executor': 'health_check',
                    'config': {
                        'service_name': service_name,
                        'max_wait_time': 120
                    },
                    'timeout': 180
                },
                {
                    'step_id': 'traffic_resume',
                    'name': 'Reprise du trafic',
                    'executor': 'traffic',
                    'config': {
                        'service_name': service_name,
                        'action': 'resume'
                    },
                    'timeout': 30
                },
                {
                    'step_id': 'post_rollback_validation',
                    'name': 'Validation post-rollback',
                    'executor': 'validation',
                    'config': {
                        'service_name': service_name,
                        'validation_suite': 'comprehensive'
                    },
                    'timeout': 300
                }
            ]
        
        elif strategy == RollbackStrategy.GRADUAL:
            steps = [
                {
                    'step_id': 'rollback_canary',
                    'name': 'Rollback canary (10%)',
                    'executor': 'kubernetes',
                    'config': {
                        'traffic_percentage': 10,
                        'target_version': target_version.version_tag
                    },
                    'timeout': 180
                },
                {
                    'step_id': 'validate_canary',
                    'name': 'Validation canary',
                    'executor': 'validation',
                    'config': {
                        'duration': 300,
                        'success_threshold': 0.95
                    },
                    'timeout': 360
                },
                {
                    'step_id': 'rollback_50_percent',
                    'name': 'Rollback 50%',
                    'executor': 'kubernetes',
                    'config': {
                        'traffic_percentage': 50,
                        'target_version': target_version.version_tag
                    },
                    'timeout': 180
                },
                {
                    'step_id': 'validate_50_percent',
                    'name': 'Validation 50%',
                    'executor': 'validation',
                    'config': {
                        'duration': 300,
                        'success_threshold': 0.95
                    },
                    'timeout': 360
                },
                {
                    'step_id': 'rollback_complete',
                    'name': 'Rollback complet',
                    'executor': 'kubernetes',
                    'config': {
                        'traffic_percentage': 100,
                        'target_version': target_version.version_tag
                    },
                    'timeout': 180
                }
            ]
        
        return steps
    
    def _assess_rollback_risk(
        self,
        current_version: DeploymentVersion,
        target_version: DeploymentVersion,
        trigger: RollbackTrigger
    ) -> Dict[str, Any]:
        """Évalue les risques du rollback"""
        
        risk_factors = []
        risk_score = 0
        
        # Âge de la version cible
        version_age = (datetime.now() - target_version.deployment_time).days
        if version_age > 30:
            risk_factors.append("Version cible ancienne (>30 jours)")
            risk_score += 2
        elif version_age > 7:
            risk_factors.append("Version cible relativement ancienne (>7 jours)")
            risk_score += 1
        
        # Historique de rollback de la version cible
        if target_version.rollback_count > 0:
            risk_factors.append(f"Version cible a déjà été rollbackée {target_version.rollback_count} fois")
            risk_score += target_version.rollback_count
        
        # Type de trigger
        high_risk_triggers = [
            RollbackTrigger.SECURITY_INCIDENT,
            RollbackTrigger.RESOURCE_EXHAUSTION
        ]
        
        if trigger in high_risk_triggers:
            risk_factors.append(f"Trigger à haut risque: {trigger.value}")
            risk_score += 3
        
        # Différence de configuration
        config_diff = self._calculate_config_difference(
            current_version.configuration,
            target_version.configuration
        )
        
        if config_diff > 0.5:
            risk_factors.append("Différences importantes de configuration")
            risk_score += 2
        elif config_diff > 0.2:
            risk_factors.append("Différences modérées de configuration")
            risk_score += 1
        
        # Détermination du niveau de risque
        if risk_score >= 6:
            risk_level = "critical"
        elif risk_score >= 4:
            risk_level = "high"
        elif risk_score >= 2:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'mitigation_strategies': self._suggest_mitigation_strategies(risk_factors),
            'rollback_probability_success': max(0.1, 1.0 - (risk_score * 0.1))
        }
    
    def _calculate_config_difference(
        self, 
        config1: Dict[str, Any], 
        config2: Dict[str, Any]
    ) -> float:
        """Calcule la différence entre deux configurations"""
        
        # Conversion en sets de clés pour comparaison simple
        keys1 = set(str(k) + str(v) for k, v in config1.items())
        keys2 = set(str(k) + str(v) for k, v in config2.items())
        
        if not keys1 and not keys2:
            return 0.0
        
        intersection = len(keys1.intersection(keys2))
        union = len(keys1.union(keys2))
        
        # Coefficient de Jaccard inversé (1 = identique, 0 = complètement différent)
        similarity = intersection / union if union > 0 else 1.0
        
        return 1.0 - similarity
    
    def _suggest_mitigation_strategies(self, risk_factors: List[str]) -> List[str]:
        """Suggère des stratégies d'atténuation des risques"""
        
        strategies = []
        
        for factor in risk_factors:
            if "ancienne" in factor:
                strategies.append("Effectuer des tests approfondis avant rollback")
                strategies.append("Préparer un plan de rollforward rapide")
            elif "rollbackée" in factor:
                strategies.append("Analyser les causes des rollbacks précédents")
                strategies.append("Valider la stabilité de la version cible")
            elif "configuration" in factor:
                strategies.append("Valider soigneusement les changements de configuration")
                strategies.append("Effectuer un rollback graduel")
            elif "risque" in factor:
                strategies.append("Obtenir une approbation manuelle")
                strategies.append("Préparer une équipe de support dédiée")
        
        return list(set(strategies))  # Suppression des doublons
    
    def _estimate_rollback_duration(self, steps: List[Dict[str, Any]]) -> int:
        """Estime la durée du rollback"""
        
        total_duration = 0
        
        for step in steps:
            step_timeout = step.get('timeout', 60)
            # Ajout d'une marge de sécurité de 20%
            total_duration += int(step_timeout * 1.2)
        
        return total_duration
    
    async def execute_rollback(self, plan: RollbackPlan) -> RollbackExecution:
        """Exécute un plan de rollback"""
        
        execution = RollbackExecution(
            execution_id=f"exec-{plan.plan_id}",
            plan_id=plan.plan_id,
            status=RollbackStatus.PENDING,
            start_time=datetime.now()
        )
        
        self.active_rollbacks[execution.execution_id] = execution
        
        try:
            execution.status = RollbackStatus.IN_PROGRESS
            logger.info(f"Début exécution rollback: {execution.execution_id}")
            
            # Collecte des métriques avant rollback
            execution.metrics_before = await self._collect_current_metrics()
            
            # Exécution des étapes
            for i, step in enumerate(plan.steps):
                execution.current_step = i
                
                step_result = await self._execute_rollback_step(step)
                
                if step_result['success']:
                    execution.completed_steps.append(step['step_id'])
                    execution.logs.append(f"✅ {step['name']}: {step_result.get('message', 'Completed')}")
                else:
                    execution.failed_steps.append(step['step_id'])
                    execution.logs.append(f"❌ {step['name']}: {step_result.get('error', 'Failed')}")
                    
                    # Arrêt en cas d'échec critique
                    if step.get('critical', True):
                        execution.status = RollbackStatus.FAILED
                        break
            
            # Finalisation
            if execution.status == RollbackStatus.IN_PROGRESS:
                if len(execution.failed_steps) == 0:
                    execution.status = RollbackStatus.COMPLETED
                elif len(execution.completed_steps) > len(execution.failed_steps):
                    execution.status = RollbackStatus.PARTIAL
                else:
                    execution.status = RollbackStatus.FAILED
            
            # Collecte des métriques après rollback
            execution.metrics_after = await self._collect_current_metrics()
            
            # Calcul du taux de succès
            total_steps = len(plan.steps)
            completed_steps = len(execution.completed_steps)
            execution.success_rate = completed_steps / total_steps if total_steps > 0 else 0.0
            
            logger.info(f"Rollback terminé: {execution.execution_id} - Status: {execution.status.value}")
            
        except Exception as e:
            execution.status = RollbackStatus.FAILED
            execution.logs.append(f"💥 Erreur critique: {str(e)}")
            logger.error(f"Erreur exécution rollback {execution.execution_id}: {e}")
            
        finally:
            execution.end_time = datetime.now()
            
            # Transfert vers l'historique
            self.rollback_history.append(execution)
            if execution.execution_id in self.active_rollbacks:
                del self.active_rollbacks[execution.execution_id]
        
        return execution
    
    async def _execute_rollback_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une étape de rollback"""
        
        executor_type = step.get('executor')
        step_config = step.get('config', {})
        timeout = step.get('timeout', 60)
        
        try:
            if executor_type == 'kubernetes':
                result = await asyncio.wait_for(
                    self.k8s_executor.rollback_deployment(
                        deployment_name=step_config.get('deployment_name'),
                        namespace=step_config.get('namespace', 'default')
                    ),
                    timeout=timeout
                )
            
            elif executor_type == 'docker':
                result = await asyncio.wait_for(
                    self.docker_executor.rollback_container(
                        container_name=step_config.get('container_name'),
                        target_image=step_config.get('target_image')
                    ),
                    timeout=timeout
                )
            
            elif executor_type == 'validation':
                result = await self._execute_validation_step(step_config)
            
            elif executor_type == 'traffic':
                result = await self._execute_traffic_step(step_config)
            
            elif executor_type == 'health_check':
                result = await self._execute_health_check_step(step_config)
            
            else:
                result = {
                    'success': False,
                    'error': f'Exécuteur non supporté: {executor_type}'
                }
            
            return result
            
        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': f'Timeout après {timeout}s'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_validation_step(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une étape de validation"""
        
        # Simulation de validation
        await asyncio.sleep(2)
        
        return {
            'success': True,
            'message': 'Validation completed',
            'details': config
        }
    
    async def _execute_traffic_step(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une étape de gestion du trafic"""
        
        action = config.get('action')
        service_name = config.get('service_name')
        
        # Simulation de gestion du trafic
        await asyncio.sleep(1)
        
        return {
            'success': True,
            'message': f'Traffic {action} for {service_name}',
            'details': config
        }
    
    async def _execute_health_check_step(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une étape de health check"""
        
        service_name = config.get('service_name')
        max_wait_time = config.get('max_wait_time', 120)
        
        # Simulation de health check
        await asyncio.sleep(3)
        
        # Simulation de résultat (80% de chance de succès)
        import random
        success = random.random() > 0.2
        
        return {
            'success': success,
            'message': f'Health check {"passed" if success else "failed"} for {service_name}',
            'details': {
                'service_name': service_name,
                'wait_time': 3,
                'max_wait_time': max_wait_time
            }
        }
    
    async def _collect_current_metrics(self) -> Dict[str, float]:
        """Collecte les métriques actuelles"""
        
        # Simulation de collecte de métriques
        import random
        
        return {
            'response_time_ms': random.uniform(100, 300),
            'error_rate_percent': random.uniform(0, 5),
            'cpu_utilization_percent': random.uniform(30, 80),
            'memory_utilization_percent': random.uniform(40, 85),
            'requests_per_second': random.uniform(50, 200),
            'availability_percent': random.uniform(95, 100)
        }
    
    async def _anomaly_monitoring_loop(self):
        """Boucle de monitoring des anomalies"""
        
        while self.is_monitoring:
            try:
                # Collecte des métriques actuelles
                current_metrics = await self._collect_current_metrics()
                
                # Détection d'anomalies
                anomalies = self.anomaly_detector.detect_anomalies(current_metrics)
                
                # Analyse des anomalies critiques
                critical_anomalies = [
                    a for a in anomalies 
                    if a['severity'] in ['critical', 'high']
                ]
                
                if critical_anomalies:
                    logger.warning(f"Anomalies critiques détectées: {len(critical_anomalies)}")
                    
                    # Déclenchement automatique de rollback si configuré
                    auto_rollback_enabled = self.config.get('auto_rollback_on_anomaly', False)
                    
                    if auto_rollback_enabled:
                        for service_name in self.deployment_versions.keys():
                            try:
                                plan = await self.create_rollback_plan(
                                    service_name=service_name,
                                    trigger=RollbackTrigger.ANOMALY_DETECTION,
                                    strategy=RollbackStrategy.INSTANT
                                )
                                
                                # Exécution automatique pour les anomalies critiques
                                if any(a['severity'] == 'critical' for a in critical_anomalies):
                                    await self.execute_rollback(plan)
                                    logger.info(f"Rollback automatique déclenché pour {service_name}")
                                
                            except Exception as e:
                                logger.error(f"Erreur rollback automatique pour {service_name}: {e}")
                
                await asyncio.sleep(30)  # Vérification toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"Erreur loop monitoring anomalies: {e}")
                await asyncio.sleep(30)
    
    async def _health_check_loop(self):
        """Boucle de health checks"""
        
        while self.is_monitoring:
            try:
                for health_check in self.health_checks:
                    # Simulation de health check
                    # En production, ceci ferait de vrais appels HTTP
                    
                    try:
                        import aiohttp
                        async with aiohttp.ClientSession() as session:
                            async with session.get(
                                health_check.endpoint,
                                timeout=health_check.timeout
                            ) as response:
                                
                                if response.status != health_check.expected_status:
                                    logger.warning(f"Health check failed: {health_check.endpoint}")
                                    
                                    # Déclenchement de rollback si configuré
                                    auto_rollback_enabled = self.config.get('auto_rollback_on_health_failure', True)
                                    
                                    if auto_rollback_enabled:
                                        # Ici on déclencherait un rollback
                                        pass
                                        
                    except Exception as e:
                        logger.debug(f"Erreur health check {health_check.endpoint}: {e}")
                
                await asyncio.sleep(60)  # Health checks toutes les minutes
                
            except Exception as e:
                logger.error(f"Erreur loop health checks: {e}")
                await asyncio.sleep(60)
    
    async def _metric_threshold_loop(self):
        """Boucle de vérification des seuils de métriques"""
        
        while self.is_monitoring:
            try:
                current_metrics = await self._collect_current_metrics()
                
                for threshold in self.metric_thresholds:
                    metric_value = current_metrics.get(threshold.metric_name)
                    
                    if metric_value is None:
                        continue
                    
                    # Évaluation du seuil
                    threshold_exceeded = self._evaluate_threshold(
                        metric_value, 
                        threshold.threshold_value, 
                        threshold.comparison_operator
                    )
                    
                    if threshold_exceeded:
                        logger.warning(f"Seuil dépassé: {threshold.metric_name} = {metric_value}")
                        
                        # Déclenchement de rollback selon la sévérité
                        if threshold.severity in ['critical', 'high']:
                            auto_rollback_enabled = self.config.get('auto_rollback_on_threshold', False)
                            
                            if auto_rollback_enabled:
                                # Ici on déclencherait un rollback
                                pass
                
                await asyncio.sleep(30)  # Vérification toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"Erreur loop seuils métriques: {e}")
                await asyncio.sleep(30)
    
    def _evaluate_threshold(
        self, 
        value: float, 
        threshold: float, 
        operator: str
    ) -> bool:
        """Évalue si un seuil est dépassé"""
        
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return abs(value - threshold) < 0.001
        else:
            return False
    
    def get_rollback_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'un rollback"""
        
        # Vérification des rollbacks actifs
        if execution_id in self.active_rollbacks:
            execution = self.active_rollbacks[execution_id]
            return {
                'execution_id': execution_id,
                'status': execution.status.value,
                'current_step': execution.current_step,
                'completed_steps': len(execution.completed_steps),
                'failed_steps': len(execution.failed_steps),
                'success_rate': execution.success_rate,
                'start_time': execution.start_time.isoformat(),
                'active': True
            }
        
        # Vérification de l'historique
        for execution in reversed(self.rollback_history):
            if execution.execution_id == execution_id:
                return {
                    'execution_id': execution_id,
                    'status': execution.status.value,
                    'completed_steps': len(execution.completed_steps),
                    'failed_steps': len(execution.failed_steps),
                    'success_rate': execution.success_rate,
                    'start_time': execution.start_time.isoformat(),
                    'end_time': execution.end_time.isoformat() if execution.end_time else None,
                    'duration': (execution.end_time - execution.start_time).total_seconds() if execution.end_time else None,
                    'active': False
                }
        
        return None
    
    def get_global_status(self) -> Dict[str, Any]:
        """Récupère le statut global du système de rollback"""
        
        active_rollbacks = len(self.active_rollbacks)
        recent_history = [
            r for r in self.rollback_history
            if r.start_time >= datetime.now() - timedelta(hours=24)
        ]
        
        successful_rollbacks = len([r for r in recent_history if r.status == RollbackStatus.COMPLETED])
        failed_rollbacks = len([r for r in recent_history if r.status == RollbackStatus.FAILED])
        
        return {
            'monitoring_active': self.is_monitoring,
            'active_rollbacks': active_rollbacks,
            'total_rollbacks_24h': len(recent_history),
            'successful_rollbacks_24h': successful_rollbacks,
            'failed_rollbacks_24h': failed_rollbacks,
            'success_rate_24h': (successful_rollbacks / len(recent_history) * 100) if recent_history else 0,
            'registered_services': len(self.deployment_versions),
            'metric_thresholds': len(self.metric_thresholds),
            'health_checks': len(self.health_checks),
            'anomaly_detection_enabled': True
        }

# Factory pour la création du système de rollback
def create_rollback_automation(config: Dict[str, Any]) -> RollbackAutomation:
    """Factory pour créer un système de rollback automatisé configuré"""
    return RollbackAutomation(config)

# Exemple d'utilisation
async def main():
    """Exemple d'utilisation du système de rollback automatisé"""
    
    # Configuration
    config = {
        'anomaly_sensitivity': 0.05,
        'auto_rollback_on_anomaly': True,
        'auto_rollback_on_health_failure': True,
        'auto_rollback_on_threshold': False
    }
    
    # Création du système de rollback
    rollback_system = create_rollback_automation(config)
    
    try:
        # Ajout d'une version de déploiement
        current_version = DeploymentVersion(
            version_id="v2.1.0",
            version_tag="v2.1.0",
            deployment_time=datetime.now(),
            image_uri="gcr.io/project/model:v2.1.0",
            configuration={"replicas": 3, "memory": "2Gi"},
            is_stable=False
        )
        
        stable_version = DeploymentVersion(
            version_id="v2.0.0",
            version_tag="v2.0.0",
            deployment_time=datetime.now() - timedelta(days=7),
            image_uri="gcr.io/project/model:v2.0.0",
            configuration={"replicas": 2, "memory": "1Gi"},
            is_stable=True
        )
        
        rollback_system.add_deployment_version("recommendation-service", stable_version)
        rollback_system.add_deployment_version("recommendation-service", current_version)
        
        # Ajout de seuils de métriques
        rollback_system.add_metric_threshold(
            MetricThreshold(
                metric_name="error_rate_percent",
                threshold_value=5.0,
                comparison_operator=">",
                severity="high"
            )
        )
        
        rollback_system.add_metric_threshold(
            MetricThreshold(
                metric_name="response_time_ms",
                threshold_value=500.0,
                comparison_operator=">",
                severity="medium"
            )
        )
        
        # Création d'un plan de rollback
        plan = await rollback_system.create_rollback_plan(
            service_name="recommendation-service",
            trigger=RollbackTrigger.PERFORMANCE_DEGRADATION,
            strategy=RollbackStrategy.INSTANT
        )
        
        print(f"Plan de rollback créé: {plan.plan_id}")
        print(f"  De: {plan.current_version} -> Vers: {plan.target_version}")
        print(f"  Stratégie: {plan.strategy.value}")
        print(f"  Risque: {plan.risk_assessment['risk_level']}")
        print(f"  Durée estimée: {plan.estimated_duration}s")
        
        # Exécution du rollback
        execution = await rollback_system.execute_rollback(plan)
        
        print(f"\nRollback terminé:")
        print(f"  ID: {execution.execution_id}")
        print(f"  Status: {execution.status.value}")
        print(f"  Taux de succès: {execution.success_rate:.1%}")
        print(f"  Étapes complétées: {len(execution.completed_steps)}")
        print(f"  Étapes échouées: {len(execution.failed_steps)}")
        
        # Démarrage du monitoring (simulation courte)
        await rollback_system.start_monitoring()
        print(f"\nMonitoring démarré...")
        
        await asyncio.sleep(10)  # Simulation de monitoring
        
        await rollback_system.stop_monitoring()
        
        # Statut global
        global_status = rollback_system.get_global_status()
        print(f"\nStatut global: {json.dumps(global_status, indent=2)}")
        
    except Exception as e:
        logger.error(f"Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main())