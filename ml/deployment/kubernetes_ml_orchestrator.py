"""🚀 Kubernetes ML Orchestrator - IA Influencer Agent Platform Enterprise
======================================================================
Module: backend/ml/deployment/kubernetes_ml_orchestrator.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ORCHESTRATEUR KUBERNETES POUR ML
Orchestration native Kubernetes pour modèles ML
- Déploiement automatisé avec auto-scaling HPA/VPA
- Service mesh integration et load balancing intelligent
- Blue-green et canary deployments
- Resource management et GPU allocation
"""

import asyncio
import logging
import time
import uuid
import yaml
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
from pathlib import Path
import tempfile

# Configuration
logger = logging.getLogger(__name__)

class DeploymentStrategy(Enum):
    """Stratégies de déploiement"""
    ROLLING_UPDATE = "rolling_update"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"

class ScalingType(Enum):
    """Types de scaling"""
    HPA = "horizontal_pod_autoscaler"
    VPA = "vertical_pod_autoscaler"
    CUSTOM = "custom"
    NONE = "none"

class ResourceType(Enum):
    """Types de ressources"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "nvidia.com/gpu"
    STORAGE = "storage"

class DeploymentStatus(Enum):
    """Statuts de déploiement"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    RUNNING = "running"
    UPDATING = "updating"
    SCALING = "scaling"
    FAILED = "failed"
    TERMINATING = "terminating"
    TERMINATED = "terminated"

@dataclass
class ResourceRequirements:
    """Exigences de ressources"""
    cpu_request: str = "100m"
    cpu_limit: str = "1000m"
    memory_request: str = "256Mi"
    memory_limit: str = "1Gi"
    gpu_count: int = 0
    storage_request: str = "1Gi"
    ephemeral_storage_limit: str = "2Gi"

@dataclass
class ScalingConfig:
    """Configuration de scaling"""
    scaling_type: ScalingType
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    target_memory_utilization: int = 80
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 300  # seconds
    custom_metrics: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class HealthCheckConfig:
    """Configuration des health checks"""
    readiness_path: str = "/health/ready"
    liveness_path: str = "/health/live"
    startup_path: str = "/health/startup"
    readiness_initial_delay: int = 30
    liveness_initial_delay: int = 60
    startup_initial_delay: int = 10
    readiness_period: int = 10
    liveness_period: int = 30
    startup_period: int = 5
    readiness_timeout: int = 5
    liveness_timeout: int = 10
    startup_timeout: int = 3
    readiness_failure_threshold: int = 3
    liveness_failure_threshold: int = 3
    startup_failure_threshold: int = 10

@dataclass
class ServiceConfig:
    """Configuration de service"""
    service_type: str = "ClusterIP"  # ClusterIP, NodePort, LoadBalancer
    port: int = 8080
    target_port: int = 8080
    expose_metrics: bool = True
    metrics_port: int = 9090
    enable_istio: bool = False
    traffic_policy: Optional[Dict[str, Any]] = None

@dataclass
class SecurityConfig:
    """Configuration de sécurité"""
    run_as_non_root: bool = True
    run_as_user: int = 1000
    run_as_group: int = 1000
    fs_group: int = 1000
    read_only_root_filesystem: bool = True
    allow_privilege_escalation: bool = False
    capabilities_drop: List[str] = field(default_factory=lambda: ["ALL"])
    seccomp_profile: str = "RuntimeDefault"
    service_account: Optional[str] = None

@dataclass
class MLModelDeployment:
    """Déploiement de modèle ML"""
    deployment_id: str
    model_name: str
    model_version: str
    image: str
    namespace: str = "ml-models"
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING_UPDATE
    replicas: int = 3
    resources: ResourceRequirements = field(default_factory=ResourceRequirements)
    scaling: ScalingConfig = field(default_factory=lambda: ScalingConfig(ScalingType.HPA))
    health_checks: HealthCheckConfig = field(default_factory=HealthCheckConfig)
    service: ServiceConfig = field(default_factory=ServiceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    config_maps: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    volumes: List[Dict[str, Any]] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    status: DeploymentStatus = DeploymentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class KubernetesMLOrchestrator:
    """Orchestrateur Kubernetes pour ML enterprise"""
    
    def __init__(self,
                 kubeconfig_path: Optional[str] = None,
                 default_namespace: str = "ml-models",
                 enable_istio: bool = True,
                 enable_prometheus: bool = True,
                 enable_grafana: bool = True):
        
        self.kubeconfig_path = kubeconfig_path
        self.default_namespace = default_namespace
        self.enable_istio = enable_istio
        self.enable_prometheus = enable_prometheus
        self.enable_grafana = enable_grafana
        
        # State management
        self.deployments: Dict[str, MLModelDeployment] = {}
        self.deployment_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Kubernetes client (mock pour cet exemple)
        self.k8s_client = None
        self.k8s_apps_client = None
        self.k8s_core_client = None
        self.k8s_autoscaling_client = None
        
        # Templates
        self.deployment_templates = {}
        self.service_templates = {}
        self.hpa_templates = {}
        self.ingress_templates = {}
        
        # Monitoring
        self.orchestration_metrics = {
            "total_deployments": 0,
            "active_deployments": 0,
            "failed_deployments": 0,
            "total_pods": 0,
            "total_cpu_allocated": 0.0,
            "total_memory_allocated": 0.0,
            "total_gpu_allocated": 0
        }
        
        # State management
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Callbacks
        self.deployment_callbacks: List[callable] = []
        self.scaling_callbacks: List[callable] = []
        self.error_callbacks: List[callable] = []
        
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialise les templates Kubernetes"""
        
        # Template de déploiement
        self.deployment_templates["default"] = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "",
                "namespace": "",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "replicas": 1,
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxUnavailable": "25%",
                        "maxSurge": "25%"
                    }
                },
                "selector": {
                    "matchLabels": {}
                },
                "template": {
                    "metadata": {
                        "labels": {},
                        "annotations": {}
                    },
                    "spec": {
                        "securityContext": {},
                        "containers": [{
                            "name": "",
                            "image": "",
                            "ports": [],
                            "env": [],
                            "resources": {
                                "requests": {},
                                "limits": {}
                            },
                            "readinessProbe": {},
                            "livenessProbe": {},
                            "startupProbe": {},
                            "securityContext": {},
                            "volumeMounts": []
                        }],
                        "volumes": [],
                        "serviceAccountName": "",
                        "imagePullSecrets": []
                    }
                }
            }
        }
        
        # Template de service
        self.service_templates["default"] = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "",
                "namespace": "",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "type": "ClusterIP",
                "ports": [],
                "selector": {}
            }
        }
        
        # Template HPA
        self.hpa_templates["default"] = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": "",
                "namespace": ""
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": ""
                },
                "minReplicas": 1,
                "maxReplicas": 10,
                "metrics": [],
                "behavior": {
                    "scaleUp": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [{
                            "type": "Percent",
                            "value": 100,
                            "periodSeconds": 15
                        }]
                    },
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [{
                            "type": "Percent",
                            "value": 100,
                            "periodSeconds": 15
                        }]
                    }
                }
            }
        }
    
    async def start(self):
        """Démarre l'orchestrateur"""
        try:
            self.is_running = True
            logger.info("Démarrage orchestrateur Kubernetes ML")
            
            # Initialiser les clients Kubernetes (mock)
            await self._initialize_kubernetes_clients()
            
            # Vérifier les namespaces
            await self._ensure_namespaces()
            
            # Démarrer les tâches de monitoring
            asyncio.create_task(self._monitoring_loop())
            asyncio.create_task(self._health_check_loop())
            asyncio.create_task(self._metrics_collection_loop())
            
            logger.info("Orchestrateur Kubernetes démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage orchestrateur Kubernetes: {e}")
            raise
    
    async def stop(self):
        """Arrête l'orchestrateur"""
        try:
            logger.info("Arrêt orchestrateur Kubernetes...")
            
            self.is_running = False
            self.shutdown_event.set()
            
            logger.info("Orchestrateur Kubernetes arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt orchestrateur Kubernetes: {e}")
    
    async def _initialize_kubernetes_clients(self):
        """Initialise les clients Kubernetes"""
        try:
            # En production, on utiliserait la vraie librairie kubernetes
            # from kubernetes import client, config
            # 
            # if self.kubeconfig_path:
            #     config.load_kube_config(config_file=self.kubeconfig_path)
            # else:
            #     config.load_incluster_config()
            # 
            # self.k8s_core_client = client.CoreV1Api()
            # self.k8s_apps_client = client.AppsV1Api()
            # self.k8s_autoscaling_client = client.AutoscalingV2Api()
            
            # Mock pour cette démonstration
            logger.info("Clients Kubernetes initialisés (mode simulation)")
            
        except Exception as e:
            logger.error(f"Erreur initialisation clients Kubernetes: {e}")
            raise
    
    async def _ensure_namespaces(self):
        """S'assure que les namespaces existent"""
        try:
            namespaces_to_create = [
                self.default_namespace,
                f"{self.default_namespace}-staging",
                f"{self.default_namespace}-canary"
            ]
            
            for namespace in namespaces_to_create:
                # En production: vérifier et créer le namespace
                logger.info(f"Namespace {namespace} vérifié")
                
        except Exception as e:
            logger.error(f"Erreur création namespaces: {e}")
    
    async def deploy_model(self, deployment_config: MLModelDeployment) -> bool:
        """Déploie un modèle ML"""
        try:
            if deployment_config.deployment_id in self.deployments:
                raise ValueError(f"Déploiement {deployment_config.deployment_id} existe déjà")
            
            logger.info(f"Début déploiement {deployment_config.deployment_id}")
            
            # Enregistrer le déploiement
            self.deployments[deployment_config.deployment_id] = deployment_config
            deployment_config.status = DeploymentStatus.DEPLOYING
            
            # Générer les manifests Kubernetes
            manifests = await self._generate_manifests(deployment_config)
            
            # Appliquer les manifests
            success = await self._apply_manifests(manifests, deployment_config)
            
            if success:
                deployment_config.status = DeploymentStatus.RUNNING
                deployment_config.updated_at = datetime.now()
                
                # Mettre à jour les métriques
                self.orchestration_metrics["total_deployments"] += 1
                self.orchestration_metrics["active_deployments"] += 1
                
                logger.info(f"Déploiement {deployment_config.deployment_id} réussi")
                
                # Appeler les callbacks
                for callback in self.deployment_callbacks:
                    try:
                        await callback(deployment_config, "deployed")
                    except Exception as e:
                        logger.error(f"Erreur callback déploiement: {e}")
                
                return True
            else:
                deployment_config.status = DeploymentStatus.FAILED
                self.orchestration_metrics["failed_deployments"] += 1
                return False
                
        except Exception as e:
            logger.error(f"Erreur déploiement {deployment_config.deployment_id}: {e}")
            if deployment_config.deployment_id in self.deployments:
                self.deployments[deployment_config.deployment_id].status = DeploymentStatus.FAILED
            return False
    
    async def _generate_manifests(self, deployment: MLModelDeployment) -> Dict[str, Dict]:
        """Génère les manifests Kubernetes"""
        
        manifests = {}
        
        try:
            # Labels communs
            common_labels = {
                "app": deployment.model_name,
                "version": deployment.model_version,
                "deployment-id": deployment.deployment_id,
                "managed-by": "ml-orchestrator"
            }
            common_labels.update(deployment.labels)
            
            # 1. Deployment manifest
            manifests["deployment"] = await self._generate_deployment_manifest(deployment, common_labels)
            
            # 2. Service manifest
            manifests["service"] = await self._generate_service_manifest(deployment, common_labels)
            
            # 3. HPA manifest (si activé)
            if deployment.scaling.scaling_type == ScalingType.HPA:
                manifests["hpa"] = await self._generate_hpa_manifest(deployment, common_labels)
            
            # 4. ConfigMap pour la configuration du modèle
            manifests["configmap"] = await self._generate_configmap_manifest(deployment, common_labels)
            
            # 5. ServiceMonitor pour Prometheus (si activé)
            if self.enable_prometheus and deployment.service.expose_metrics:
                manifests["servicemonitor"] = await self._generate_servicemonitor_manifest(deployment, common_labels)
            
            # 6. VirtualService pour Istio (si activé)
            if self.enable_istio and deployment.service.enable_istio:
                manifests["virtualservice"] = await self._generate_virtualservice_manifest(deployment, common_labels)
            
            return manifests
            
        except Exception as e:
            logger.error(f"Erreur génération manifests: {e}")
            raise
    
    async def _generate_deployment_manifest(self, deployment: MLModelDeployment, labels: Dict[str, str]) -> Dict:
        """Génère le manifest de déploiement"""
        
        manifest = self.deployment_templates["default"].copy()
        
        # Metadata
        manifest["metadata"]["name"] = f"{deployment.model_name}-{deployment.model_version}"
        manifest["metadata"]["namespace"] = deployment.namespace
        manifest["metadata"]["labels"] = labels.copy()
        manifest["metadata"]["annotations"] = deployment.annotations.copy()
        
        # Spec
        manifest["spec"]["replicas"] = deployment.replicas
        manifest["spec"]["selector"]["matchLabels"] = {"app": deployment.model_name}
        
        # Strategy
        if deployment.strategy == DeploymentStrategy.BLUE_GREEN:
            manifest["spec"]["strategy"] = {
                "type": "Recreate"
            }
        elif deployment.strategy == DeploymentStrategy.ROLLING_UPDATE:
            manifest["spec"]["strategy"] = {
                "type": "RollingUpdate",
                "rollingUpdate": {
                    "maxUnavailable": "25%",
                    "maxSurge": "25%"
                }
            }
        
        # Pod template
        container_spec = manifest["spec"]["template"]["spec"]["containers"][0]
        container_spec["name"] = deployment.model_name
        container_spec["image"] = deployment.image
        
        # Ports
        container_spec["ports"] = [
            {
                "name": "http",
                "containerPort": deployment.service.target_port,
                "protocol": "TCP"
            }
        ]
        
        if deployment.service.expose_metrics:
            container_spec["ports"].append({
                "name": "metrics",
                "containerPort": deployment.service.metrics_port,
                "protocol": "TCP"
            })
        
        # Environment variables
        container_spec["env"] = [
            {"name": k, "value": v} for k, v in deployment.environment_variables.items()
        ]
        
        # Resources
        container_spec["resources"] = {
            "requests": {
                "cpu": deployment.resources.cpu_request,
                "memory": deployment.resources.memory_request
            },
            "limits": {
                "cpu": deployment.resources.cpu_limit,
                "memory": deployment.resources.memory_limit,
                "ephemeral-storage": deployment.resources.ephemeral_storage_limit
            }
        }
        
        if deployment.resources.gpu_count > 0:
            container_spec["resources"]["limits"]["nvidia.com/gpu"] = str(deployment.resources.gpu_count)
        
        # Health checks
        container_spec["readinessProbe"] = {
            "httpGet": {
                "path": deployment.health_checks.readiness_path,
                "port": deployment.service.target_port
            },
            "initialDelaySeconds": deployment.health_checks.readiness_initial_delay,
            "periodSeconds": deployment.health_checks.readiness_period,
            "timeoutSeconds": deployment.health_checks.readiness_timeout,
            "failureThreshold": deployment.health_checks.readiness_failure_threshold
        }
        
        container_spec["livenessProbe"] = {
            "httpGet": {
                "path": deployment.health_checks.liveness_path,
                "port": deployment.service.target_port
            },
            "initialDelaySeconds": deployment.health_checks.liveness_initial_delay,
            "periodSeconds": deployment.health_checks.liveness_period,
            "timeoutSeconds": deployment.health_checks.liveness_timeout,
            "failureThreshold": deployment.health_checks.liveness_failure_threshold
        }
        
        container_spec["startupProbe"] = {
            "httpGet": {
                "path": deployment.health_checks.startup_path,
                "port": deployment.service.target_port
            },
            "initialDelaySeconds": deployment.health_checks.startup_initial_delay,
            "periodSeconds": deployment.health_checks.startup_period,
            "timeoutSeconds": deployment.health_checks.startup_timeout,
            "failureThreshold": deployment.health_checks.startup_failure_threshold
        }
        
        # Security context
        manifest["spec"]["template"]["spec"]["securityContext"] = {
            "runAsNonRoot": deployment.security.run_as_non_root,
            "runAsUser": deployment.security.run_as_user,
            "runAsGroup": deployment.security.run_as_group,
            "fsGroup": deployment.security.fs_group
        }
        
        container_spec["securityContext"] = {
            "allowPrivilegeEscalation": deployment.security.allow_privilege_escalation,
            "readOnlyRootFilesystem": deployment.security.read_only_root_filesystem,
            "capabilities": {
                "drop": deployment.security.capabilities_drop
            },
            "seccompProfile": {
                "type": deployment.security.seccomp_profile
            }
        }
        
        # Service account
        if deployment.security.service_account:
            manifest["spec"]["template"]["spec"]["serviceAccountName"] = deployment.security.service_account
        
        # Labels et annotations
        manifest["spec"]["template"]["metadata"]["labels"] = labels.copy()
        manifest["spec"]["template"]["metadata"]["annotations"] = deployment.annotations.copy()
        
        return manifest
    
    async def _generate_service_manifest(self, deployment: MLModelDeployment, labels: Dict[str, str]) -> Dict:
        """Génère le manifest de service"""
        
        manifest = self.service_templates["default"].copy()
        
        manifest["metadata"]["name"] = f"{deployment.model_name}-service"
        manifest["metadata"]["namespace"] = deployment.namespace
        manifest["metadata"]["labels"] = labels.copy()
        manifest["metadata"]["annotations"] = deployment.annotations.copy()
        
        manifest["spec"]["type"] = deployment.service.service_type
        manifest["spec"]["selector"] = {"app": deployment.model_name}
        
        # Ports
        manifest["spec"]["ports"] = [
            {
                "name": "http",
                "port": deployment.service.port,
                "targetPort": deployment.service.target_port,
                "protocol": "TCP"
            }
        ]
        
        if deployment.service.expose_metrics:
            manifest["spec"]["ports"].append({
                "name": "metrics",
                "port": deployment.service.metrics_port,
                "targetPort": deployment.service.metrics_port,
                "protocol": "TCP"
            })
        
        return manifest
    
    async def _generate_hpa_manifest(self, deployment: MLModelDeployment, labels: Dict[str, str]) -> Dict:
        """Génère le manifest HPA"""
        
        manifest = self.hpa_templates["default"].copy()
        
        manifest["metadata"]["name"] = f"{deployment.model_name}-hpa"
        manifest["metadata"]["namespace"] = deployment.namespace
        
        manifest["spec"]["scaleTargetRef"]["name"] = f"{deployment.model_name}-{deployment.model_version}"
        manifest["spec"]["minReplicas"] = deployment.scaling.min_replicas
        manifest["spec"]["maxReplicas"] = deployment.scaling.max_replicas
        
        # Métriques
        metrics = []
        
        # CPU utilization
        if deployment.scaling.target_cpu_utilization > 0:
            metrics.append({
                "type": "Resource",
                "resource": {
                    "name": "cpu",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": deployment.scaling.target_cpu_utilization
                    }
                }
            })
        
        # Memory utilization
        if deployment.scaling.target_memory_utilization > 0:
            metrics.append({
                "type": "Resource",
                "resource": {
                    "name": "memory",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": deployment.scaling.target_memory_utilization
                    }
                }
            })
        
        # Custom metrics
        metrics.extend(deployment.scaling.custom_metrics)
        
        manifest["spec"]["metrics"] = metrics
        
        # Scaling behavior
        manifest["spec"]["behavior"]["scaleUp"]["stabilizationWindowSeconds"] = deployment.scaling.scale_up_cooldown
        manifest["spec"]["behavior"]["scaleDown"]["stabilizationWindowSeconds"] = deployment.scaling.scale_down_cooldown
        
        return manifest
    
    async def _generate_configmap_manifest(self, deployment: MLModelDeployment, labels: Dict[str, str]) -> Dict:
        """Génère le manifest ConfigMap"""
        
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{deployment.model_name}-config",
                "namespace": deployment.namespace,
                "labels": labels
            },
            "data": {
                "model_name": deployment.model_name,
                "model_version": deployment.model_version,
                "deployment_id": deployment.deployment_id,
                "created_at": deployment.created_at.isoformat(),
                "config.yaml": yaml.dump({
                    "model": {
                        "name": deployment.model_name,
                        "version": deployment.model_version,
                        "image": deployment.image
                    },
                    "service": {
                        "port": deployment.service.port,
                        "metrics_port": deployment.service.metrics_port
                    },
                    "health_checks": {
                        "readiness_path": deployment.health_checks.readiness_path,
                        "liveness_path": deployment.health_checks.liveness_path,
                        "startup_path": deployment.health_checks.startup_path
                    }
                })
            }
        }
    
    async def _generate_servicemonitor_manifest(self, deployment: MLModelDeployment, labels: Dict[str, str]) -> Dict:
        """Génère le manifest ServiceMonitor pour Prometheus"""
        
        return {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": f"{deployment.model_name}-metrics",
                "namespace": deployment.namespace,
                "labels": labels
            },
            "spec": {
                "selector": {
                    "matchLabels": {"app": deployment.model_name}
                },
                "endpoints": [{
                    "port": "metrics",
                    "interval": "30s",
                    "path": "/metrics"
                }]
            }
        }
    
    async def _generate_virtualservice_manifest(self, deployment: MLModelDeployment, labels: Dict[str, str]) -> Dict:
        """Génère le manifest VirtualService pour Istio"""
        
        return {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": f"{deployment.model_name}-vs",
                "namespace": deployment.namespace,
                "labels": labels
            },
            "spec": {
                "hosts": [f"{deployment.model_name}.{deployment.namespace}.svc.cluster.local"],
                "http": [{
                    "match": [{"uri": {"prefix": "/"}}],
                    "route": [{
                        "destination": {
                            "host": f"{deployment.model_name}-service",
                            "port": {"number": deployment.service.port}
                        }
                    }],
                    "timeout": "30s",
                    "retries": {
                        "attempts": 3,
                        "perTryTimeout": "10s"
                    }
                }]
            }
        }
    
    async def _apply_manifests(self, manifests: Dict[str, Dict], deployment: MLModelDeployment) -> bool:
        """Applique les manifests Kubernetes"""
        
        try:
            # En production, on utiliserait les clients Kubernetes réels
            # pour appliquer chaque manifest
            
            for manifest_type, manifest in manifests.items():
                logger.info(f"Application manifest {manifest_type} pour {deployment.deployment_id}")
                
                # Simulation de l'application
                await asyncio.sleep(0.1)
                
                # En vrai:
                # if manifest_type == "deployment":
                #     self.k8s_apps_client.create_namespaced_deployment(
                #         namespace=deployment.namespace,
                #         body=manifest
                #     )
                # elif manifest_type == "service":
                #     self.k8s_core_client.create_namespaced_service(
                #         namespace=deployment.namespace,
                #         body=manifest
                #     )
                # etc.
            
            # Attendre que le déploiement soit prêt
            await self._wait_for_deployment_ready(deployment)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur application manifests: {e}")
            return False
    
    async def _wait_for_deployment_ready(self, deployment: MLModelDeployment, timeout: int = 300):
        """Attend que le déploiement soit prêt"""
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # En production: vérifier le statut réel du déploiement
            # deployment_status = self.k8s_apps_client.read_namespaced_deployment_status(
            #     name=f"{deployment.model_name}-{deployment.model_version}",
            #     namespace=deployment.namespace
            # )
            # 
            # if deployment_status.status.ready_replicas == deployment.replicas:
            #     return True
            
            # Simulation
            await asyncio.sleep(5)
            logger.info(f"Attente déploiement {deployment.deployment_id}...")
            
            # Simuler le succès après 10 secondes
            if time.time() - start_time > 10:
                return True
        
        raise TimeoutError(f"Timeout attente déploiement {deployment.deployment_id}")
    
    async def scale_deployment(self, deployment_id: str, replicas: int) -> bool:
        """Scale un déploiement"""
        try:
            if deployment_id not in self.deployments:
                raise ValueError(f"Déploiement {deployment_id} non trouvé")
            
            deployment = self.deployments[deployment_id]
            old_replicas = deployment.replicas
            
            deployment.status = DeploymentStatus.SCALING
            deployment.replicas = replicas
            deployment.updated_at = datetime.now()
            
            # En production: mettre à jour le déploiement Kubernetes
            # self.k8s_apps_client.patch_namespaced_deployment_scale(
            #     name=f"{deployment.model_name}-{deployment.model_version}",
            #     namespace=deployment.namespace,
            #     body={"spec": {"replicas": replicas}}
            # )
            
            logger.info(f"Scaling {deployment_id} de {old_replicas} à {replicas} replicas")
            
            # Attendre la completion du scaling
            await self._wait_for_deployment_ready(deployment)
            
            deployment.status = DeploymentStatus.RUNNING
            
            # Appeler les callbacks
            for callback in self.scaling_callbacks:
                try:
                    await callback(deployment, old_replicas, replicas)
                except Exception as e:
                    logger.error(f"Erreur callback scaling: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur scaling déploiement {deployment_id}: {e}")
            return False
    
    async def update_deployment(self, deployment_id: str, new_image: str, strategy: DeploymentStrategy = DeploymentStrategy.ROLLING_UPDATE) -> bool:
        """Met à jour un déploiement"""
        try:
            if deployment_id not in self.deployments:
                raise ValueError(f"Déploiement {deployment_id} non trouvé")
            
            deployment = self.deployments[deployment_id]
            old_image = deployment.image
            
            deployment.status = DeploymentStatus.UPDATING
            deployment.image = new_image
            deployment.updated_at = datetime.now()
            
            if strategy == DeploymentStrategy.BLUE_GREEN:
                success = await self._perform_blue_green_update(deployment, old_image, new_image)
            elif strategy == DeploymentStrategy.CANARY:
                success = await self._perform_canary_update(deployment, old_image, new_image)
            else:
                success = await self._perform_rolling_update(deployment, old_image, new_image)
            
            if success:
                deployment.status = DeploymentStatus.RUNNING
                logger.info(f"Mise à jour {deployment_id} réussie: {old_image} -> {new_image}")
            else:
                deployment.status = DeploymentStatus.FAILED
                deployment.image = old_image  # Rollback
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur mise à jour déploiement {deployment_id}: {e}")
            return False
    
    async def _perform_rolling_update(self, deployment: MLModelDeployment, old_image: str, new_image: str) -> bool:
        """Effectue un rolling update"""
        try:
            logger.info(f"Rolling update {deployment.deployment_id}: {old_image} -> {new_image}")
            
            # En production: mettre à jour l'image du déploiement
            # self.k8s_apps_client.patch_namespaced_deployment(
            #     name=f"{deployment.model_name}-{deployment.model_version}",
            #     namespace=deployment.namespace,
            #     body={
            #         "spec": {
            #             "template": {
            #                 "spec": {
            #                     "containers": [{
            #                         "name": deployment.model_name,
            #                         "image": new_image
            #                     }]
            #                 }
            #             }
            #         }
            #     }
            # )
            
            # Attendre que le rolling update se termine
            await self._wait_for_deployment_ready(deployment)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur rolling update: {e}")
            return False
    
    async def _perform_blue_green_update(self, deployment: MLModelDeployment, old_image: str, new_image: str) -> bool:
        """Effectue un blue-green deployment"""
        try:
            logger.info(f"Blue-green deployment {deployment.deployment_id}: {old_image} -> {new_image}")
            
            # 1. Créer le déploiement "green" avec la nouvelle image
            green_deployment = deployment.model_name + "-green"
            
            # 2. Attendre que le déploiement green soit prêt
            await asyncio.sleep(10)  # Simulation
            
            # 3. Tester le déploiement green
            health_check_passed = await self._health_check_deployment(deployment)
            
            if health_check_passed:
                # 4. Switcher le traffic vers green
                await self._switch_service_to_green(deployment)
                
                # 5. Supprimer l'ancien déploiement "blue"
                await self._cleanup_blue_deployment(deployment)
                
                return True
            else:
                # Rollback: supprimer le déploiement green
                await self._cleanup_green_deployment(deployment)
                return False
                
        except Exception as e:
            logger.error(f"Erreur blue-green deployment: {e}")
            return False
    
    async def _perform_canary_update(self, deployment: MLModelDeployment, old_image: str, new_image: str) -> bool:
        """Effectue un canary deployment"""
        try:
            logger.info(f"Canary deployment {deployment.deployment_id}: {old_image} -> {new_image}")
            
            # 1. Déployer la version canary (10% du traffic)
            await self._deploy_canary_version(deployment, new_image, traffic_percentage=10)
            
            # 2. Monitorer les métriques pendant 5 minutes
            await asyncio.sleep(300)  # 5 minutes
            
            # 3. Vérifier les métriques de santé
            canary_healthy = await self._check_canary_health(deployment)
            
            if canary_healthy:
                # 4. Augmenter progressivement le traffic canary
                for percentage in [25, 50, 75, 100]:
                    await self._update_canary_traffic(deployment, percentage)
                    await asyncio.sleep(120)  # 2 minutes entre chaque étape
                    
                    if not await self._check_canary_health(deployment):
                        # Rollback si problème détecté
                        await self._rollback_canary(deployment)
                        return False
                
                # 5. Finaliser le canary (100% traffic)
                await self._finalize_canary(deployment)
                return True
            else:
                # Rollback immédiat
                await self._rollback_canary(deployment)
                return False
                
        except Exception as e:
            logger.error(f"Erreur canary deployment: {e}")
            return False
    
    async def delete_deployment(self, deployment_id: str) -> bool:
        """Supprime un déploiement"""
        try:
            if deployment_id not in self.deployments:
                raise ValueError(f"Déploiement {deployment_id} non trouvé")
            
            deployment = self.deployments[deployment_id]
            deployment.status = DeploymentStatus.TERMINATING
            
            # En production: supprimer toutes les ressources Kubernetes
            # - Deployment
            # - Service  
            # - HPA
            # - ConfigMap
            # - ServiceMonitor
            # - VirtualService
            
            logger.info(f"Suppression déploiement {deployment_id}")
            
            # Simulation
            await asyncio.sleep(5)
            
            deployment.status = DeploymentStatus.TERMINATED
            deployment.updated_at = datetime.now()
            
            # Mettre à jour les métriques
            self.orchestration_metrics["active_deployments"] -= 1
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression déploiement {deployment_id}: {e}")
            return False
    
    # Helper methods (implementations simplifiées pour cette démo)
    
    async def _health_check_deployment(self, deployment: MLModelDeployment) -> bool:
        """Vérifie la santé d'un déploiement"""
        # Simulation d'un health check
        await asyncio.sleep(2)
        return True  # Toujours succès en simulation
    
    async def _switch_service_to_green(self, deployment: MLModelDeployment):
        """Switche le service vers la version green"""
        logger.info(f"Switching service to green for {deployment.deployment_id}")
        await asyncio.sleep(1)
    
    async def _cleanup_blue_deployment(self, deployment: MLModelDeployment):
        """Nettoie le déploiement blue"""
        logger.info(f"Cleaning up blue deployment for {deployment.deployment_id}")
        await asyncio.sleep(1)
    
    async def _cleanup_green_deployment(self, deployment: MLModelDeployment):
        """Nettoie le déploiement green"""
        logger.info(f"Cleaning up green deployment for {deployment.deployment_id}")
        await asyncio.sleep(1)
    
    async def _deploy_canary_version(self, deployment: MLModelDeployment, new_image: str, traffic_percentage: int):
        """Déploie la version canary"""
        logger.info(f"Deploying canary version for {deployment.deployment_id} with {traffic_percentage}% traffic")
        await asyncio.sleep(2)
    
    async def _check_canary_health(self, deployment: MLModelDeployment) -> bool:
        """Vérifie la santé du canary"""
        logger.info(f"Checking canary health for {deployment.deployment_id}")
        await asyncio.sleep(1)
        return True  # Simulation: toujours en bonne santé
    
    async def _update_canary_traffic(self, deployment: MLModelDeployment, percentage: int):
        """Met à jour le pourcentage de traffic canary"""
        logger.info(f"Updating canary traffic to {percentage}% for {deployment.deployment_id}")
        await asyncio.sleep(1)
    
    async def _rollback_canary(self, deployment: MLModelDeployment):
        """Rollback du canary"""
        logger.info(f"Rolling back canary for {deployment.deployment_id}")
        await asyncio.sleep(1)
    
    async def _finalize_canary(self, deployment: MLModelDeployment):
        """Finalise le canary deployment"""
        logger.info(f"Finalizing canary for {deployment.deployment_id}")
        await asyncio.sleep(1)
    
    # Boucles de monitoring
    
    async def _monitoring_loop(self):
        """Boucle de monitoring"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Toutes les minutes
                
                # Log des métriques
                logger.info(
                    f"K8s metrics - "
                    f"Deployments: {self.orchestration_metrics['active_deployments']}, "
                    f"Success rate: {self._calculate_success_rate():.2%}, "
                    f"Total CPU: {self.orchestration_metrics['total_cpu_allocated']:.2f}, "
                    f"Total Memory: {self.orchestration_metrics['total_memory_allocated']:.2f}GB"
                )
                
            except Exception as e:
                logger.error(f"Erreur boucle monitoring: {e}")
    
    async def _health_check_loop(self):
        """Boucle de health check"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Toutes les 30 secondes
                
                # Vérifier la santé de tous les déploiements actifs
                for deployment_id, deployment in self.deployments.items():
                    if deployment.status == DeploymentStatus.RUNNING:
                        is_healthy = await self._health_check_deployment(deployment)
                        if not is_healthy:
                            logger.warning(f"Déploiement {deployment_id} en mauvaise santé")
                            # Déclencher une alerte ou un redémarrage automatique
                
            except Exception as e:
                logger.error(f"Erreur boucle health check: {e}")
    
    async def _metrics_collection_loop(self):
        """Boucle de collecte de métriques"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Toutes les 5 minutes
                
                # Collecter les métriques des déploiements
                total_cpu = 0.0
                total_memory = 0.0
                total_gpu = 0
                
                for deployment in self.deployments.values():
                    if deployment.status == DeploymentStatus.RUNNING:
                        # Parser les ressources
                        cpu_value = float(deployment.resources.cpu_request.replace('m', '')) / 1000
                        memory_value = self._parse_memory(deployment.resources.memory_request)
                        
                        total_cpu += cpu_value * deployment.replicas
                        total_memory += memory_value * deployment.replicas
                        total_gpu += deployment.resources.gpu_count * deployment.replicas
                
                self.orchestration_metrics.update({
                    "total_cpu_allocated": total_cpu,
                    "total_memory_allocated": total_memory,
                    "total_gpu_allocated": total_gpu
                })
                
            except Exception as e:
                logger.error(f"Erreur collecte métriques: {e}")
    
    def _parse_memory(self, memory_str: str) -> float:
        """Parse une valeur de mémoire en GB"""
        if memory_str.endswith('Gi'):
            return float(memory_str[:-2])
        elif memory_str.endswith('Mi'):
            return float(memory_str[:-2]) / 1024
        elif memory_str.endswith('Ki'):
            return float(memory_str[:-2]) / (1024 * 1024)
        else:
            return 0.0
    
    def _calculate_success_rate(self) -> float:
        """Calcule le taux de succès des déploiements"""
        total = self.orchestration_metrics["total_deployments"]
        failed = self.orchestration_metrics["failed_deployments"]
        return (total - failed) / max(total, 1)
    
    # API publique
    
    def list_deployments(self) -> List[MLModelDeployment]:
        """Liste tous les déploiements"""
        return list(self.deployments.values())
    
    def get_deployment(self, deployment_id: str) -> Optional[MLModelDeployment]:
        """Récupère un déploiement"""
        return self.deployments.get(deployment_id)
    
    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques d'orchestration"""
        return self.orchestration_metrics.copy()
    
    def add_deployment_callback(self, callback: callable):
        """Ajoute un callback de déploiement"""
        self.deployment_callbacks.append(callback)
    
    def add_scaling_callback(self, callback: callable):
        """Ajoute un callback de scaling"""
        self.scaling_callbacks.append(callback)
    
    def add_error_callback(self, callback: callable):
        """Ajoute un callback d'erreur"""
        self.error_callbacks.append(callback)
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification de santé de l'orchestrateur"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "kubernetes_connected": self.k8s_client is not None,
            "active_deployments": self.orchestration_metrics["active_deployments"],
            "total_deployments": self.orchestration_metrics["total_deployments"],
            "success_rate": self._calculate_success_rate(),
            "resource_allocation": {
                "cpu": self.orchestration_metrics["total_cpu_allocated"],
                "memory": self.orchestration_metrics["total_memory_allocated"],
                "gpu": self.orchestration_metrics["total_gpu_allocated"]
            }
        }


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation de l'orchestrateur Kubernetes"""
    
    # Créer l'orchestrateur
    orchestrator = KubernetesMLOrchestrator(
        default_namespace="ml-models",
        enable_istio=True,
        enable_prometheus=True
    )
    
    try:
        await orchestrator.start()
        
        # Configuration de déploiement
        deployment_config = MLModelDeployment(
            deployment_id="text-classifier-v1",
            model_name="text-classifier",
            model_version="v1.0.0",
            image="my-registry/text-classifier:v1.0.0",
            namespace="ml-models",
            strategy=DeploymentStrategy.ROLLING_UPDATE,
            replicas=3,
            resources=ResourceRequirements(
                cpu_request="200m",
                cpu_limit="1000m",
                memory_request="512Mi",
                memory_limit="2Gi",
                gpu_count=0
            ),
            scaling=ScalingConfig(
                scaling_type=ScalingType.HPA,
                min_replicas=2,
                max_replicas=10,
                target_cpu_utilization=70,
                target_memory_utilization=80
            ),
            environment_variables={
                "MODEL_PATH": "/app/models/text_classifier.pkl",
                "LOG_LEVEL": "INFO",
                "WORKERS": "4"
            },
            labels={
                "team": "ml-platform",
                "environment": "production",
                "model-type": "classification"
            }
        )
        
        # Callbacks
        async def deployment_callback(deployment, action):
            print(f"Déploiement {deployment.deployment_id} - Action: {action}")
        
        async def scaling_callback(deployment, old_replicas, new_replicas):
            print(f"Scaling {deployment.deployment_id}: {old_replicas} -> {new_replicas}")
        
        orchestrator.add_deployment_callback(deployment_callback)
        orchestrator.add_scaling_callback(scaling_callback)
        
        # Déployer le modèle
        print("Déploiement du modèle...")
        success = await orchestrator.deploy_model(deployment_config)
        
        if success:
            print("Déploiement réussi!")
            
            # Attendre un peu
            await asyncio.sleep(5)
            
            # Scaler le déploiement
            print("Scaling à 5 replicas...")
            await orchestrator.scale_deployment("text-classifier-v1", 5)
            
            # Mettre à jour avec une nouvelle image
            print("Mise à jour avec nouvelle image...")
            await orchestrator.update_deployment(
                "text-classifier-v1",
                "my-registry/text-classifier:v1.1.0",
                DeploymentStrategy.CANARY
            )
            
            # Afficher les métriques
            metrics = orchestrator.get_orchestration_metrics()
            print(f"Métriques: {metrics}")
            
            # Lister les déploiements
            deployments = orchestrator.list_deployments()
            print(f"Déploiements actifs: {len(deployments)}")
            
            # Health check
            health = await orchestrator.health_check()
            print(f"Santé: {health}")
            
        else:
            print("Échec du déploiement")
        
    finally:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(example_usage())