"""🚀 Model Staging Manager - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/model_registry/model_staging_manager.py
Author: Fahed Mlaiel (mlaiel@live.de) - DBA + DevOps Expert
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 GESTIONNAIRE DE STAGING DE MODÈLES
Gestion des environnements de staging avec promotion automatique
- Dev, staging, production environments
- Automated promotion pipelines
- A/B testing support
- Rollback mechanisms
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
from pathlib import Path

import docker
import kubernetes
from kubernetes import client, config
import mlflow
from mlflow.tracking import MlflowClient

# Configuration
logger = logging.getLogger(__name__)

class Environment(Enum):
    """Environnements de staging"""
    DEV = "dev"
    STAGING = "staging" 
    PRODUCTION = "production"
    CANARY = "canary"
    BLUE = "blue"
    GREEN = "green"

class PromotionStrategy(Enum):
    """Stratégies de promotion"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    APPROVAL_REQUIRED = "approval_required"
    A_B_TEST = "a_b_test"

class DeploymentStatus(Enum):
    """Statuts de déploiement"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"

@dataclass
class EnvironmentConfig:
    """Configuration d'environnement"""
    name: str
    environment: Environment
    kubernetes_namespace: str
    resource_limits: Dict[str, str]
    environment_variables: Dict[str, str]
    health_check_endpoint: str
    promotion_criteria: Dict[str, Any]
    auto_scaling_config: Dict[str, Any]

@dataclass
class ModelDeployment:
    """Déploiement de modèle"""
    deployment_id: str
    model_id: str
    model_version: str
    environment: Environment
    status: DeploymentStatus
    created_at: datetime
    updated_at: datetime
    health_status: str
    performance_metrics: Dict[str, float]
    deployment_config: Dict[str, Any]
    rollback_version: Optional[str] = None

class ModelStagingManager:
    """🔧 Gestionnaire de staging de modèles ML"""
    
    def __init__(self, 
                 mlflow_tracking_uri -> None: str = "http -> None://localhost -> None:5000",
                 kubernetes_config_path -> None: Optional[str] = None) -> None:
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.kubernetes_config_path = kubernetes_config_path
        
        # Clients
        self.mlflow_client = None
        self.k8s_apps_v1 = None
        self.k8s_core_v1 = None
        self.docker_client = None
        
        # Configuration des environnements
        self.environments: Dict[Environment, EnvironmentConfig] = {}
        
        # Tracking des déploiements
        self.deployments: Dict[str, ModelDeployment] = {}
        self.promotion_queue: List[str] = []
        
        # Métriques
        self.deployment_count = 0
        self.successful_promotions = 0
        self.failed_promotions = 0
        
    async def initialize(self) -> None:
        """Initialise les clients et configurations"""
        try:
            # MLflow client
            mlflow.set_tracking_uri(self.mlflow_tracking_uri)
            self.mlflow_client = MlflowClient()
            
            # Kubernetes client
            if self.kubernetes_config_path:
                config.load_kube_config(config_file=self.kubernetes_config_path)
            else:
                config.load_incluster_config()
            
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            
            # Docker client
            self.docker_client = docker.from_env()
            
            # Configurer les environnements par défaut
            await self._setup_default_environments()
            
            logger.info("ModelStagingManager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ModelStagingManager: {e}")
            raise
    
    async def _setup_default_environments(self) -> None:
        """Configure les environnements par défaut"""
        self.environments = {
            Environment.DEV: EnvironmentConfig(
                name="development",
                environment=Environment.DEV,
                kubernetes_namespace="ainflue-ml-dev",
                resource_limits={"memory": "1Gi", "cpu": "500m"},
                environment_variables={"ENV": "dev", "LOG_LEVEL": "DEBUG"},
                health_check_endpoint="/health",
                promotion_criteria={
                    "min_accuracy": 0.85,
                    "max_latency_ms": 200,
                    "min_uptime_hours": 24
                },
                auto_scaling_config={
                    "min_replicas": 1,
                    "max_replicas": 3,
                    "target_cpu_utilization": 70
                }
            ),
            Environment.STAGING: EnvironmentConfig(
                name="staging",
                environment=Environment.STAGING,
                kubernetes_namespace="ainflue-ml-staging",
                resource_limits={"memory": "2Gi", "cpu": "1000m"},
                environment_variables={"ENV": "staging", "LOG_LEVEL": "INFO"},
                health_check_endpoint="/health",
                promotion_criteria={
                    "min_accuracy": 0.90,
                    "max_latency_ms": 150,
                    "min_uptime_hours": 72,
                    "min_success_rate": 0.99
                },
                auto_scaling_config={
                    "min_replicas": 2,
                    "max_replicas": 5,
                    "target_cpu_utilization": 60
                }
            ),
            Environment.PRODUCTION: EnvironmentConfig(
                name="production",
                environment=Environment.PRODUCTION,
                kubernetes_namespace="ainflue-ml-prod",
                resource_limits={"memory": "4Gi", "cpu": "2000m"},
                environment_variables={"ENV": "production", "LOG_LEVEL": "WARNING"},
                health_check_endpoint="/health",
                promotion_criteria={
                    "min_accuracy": 0.95,
                    "max_latency_ms": 100,
                    "min_uptime_hours": 168,
                    "min_success_rate": 0.999
                },
                auto_scaling_config={
                    "min_replicas": 3,
                    "max_replicas": 20,
                    "target_cpu_utilization": 50
                }
            )
        }
    
    async def deploy_model(self, 
                          model_id: str,
                          model_version: str,
                          target_environment: Environment,
                          deployment_config: Optional[Dict[str, Any]] = None) -> str:
        """Déploie un modèle dans un environnement"""
        try:
            deployment_id = f"deploy-{model_id}-{int(time.time())}"
            
            # Récupérer le modèle depuis MLflow
            model_uri = f"models:/{model_id}/{model_version}"
            model_info = self.mlflow_client.get_model_version(model_id, model_version)
            
            # Configuration d'environnement
            env_config = self.environments[target_environment]
            
            # Créer le déploiement
            deployment = ModelDeployment(
                deployment_id=deployment_id,
                model_id=model_id,
                model_version=model_version,
                environment=target_environment,
                status=DeploymentStatus.DEPLOYING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                health_status="unknown",
                performance_metrics={},
                deployment_config=deployment_config or {}
            )
            
            self.deployments[deployment_id] = deployment
            
            # Construire l'image Docker
            docker_image = await self._build_docker_image(model_uri, deployment_id)
            
            # Déployer sur Kubernetes
            k8s_deployment = await self._deploy_to_kubernetes(
                deployment_id, 
                docker_image, 
                env_config
            )
            
            # Mettre à jour le statut
            deployment.status = DeploymentStatus.DEPLOYED
            deployment.updated_at = datetime.utcnow()
            
            self.deployment_count += 1
            
            logger.info(f"Successfully deployed model {model_id} v{model_version} to {target_environment.value}")
            
            return deployment_id
            
        except Exception as e:
            logger.error(f"Failed to deploy model: {e}")
            if deployment_id in self.deployments:
                self.deployments[deployment_id].status = DeploymentStatus.FAILED
            raise
    
    async def _build_docker_image(self, model_uri: str, deployment_id: str) -> str:
        """Construit l'image Docker pour le modèle"""
        try:
            # Dockerfile template
            dockerfile_content = f"""
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install MLflow
RUN pip install mlflow[extras]

# Copy model serving script
COPY serve_model.py .

# Set model URI
ENV MODEL_URI="{model_uri}"
ENV DEPLOYMENT_ID="{deployment_id}"

EXPOSE 8080

CMD ["python", "serve_model.py"]
"""
            
            # Script de serving
            serve_script = """
import os
import mlflow
import mlflow.pyfunc
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load model
model_uri = os.getenv('MODEL_URI')
model = mlflow.pyfunc.load_model(model_uri)

@app.route('/health')
def health() -> None:
    return jsonify({'status': 'healthy', 'deployment_id': os.getenv('DEPLOYMENT_ID')})

@app.route('/predict', methods=['POST'])
def predict() -> None:
    try:
        data = request.json
        predictions = model.predict(data['input'])
        return jsonify({'predictions': predictions.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
"""
            
            # Créer un contexte de build temporaire
            build_context = Path(f"/tmp/{deployment_id}")
            build_context.mkdir(exist_ok=True)
            
            with open(build_context / "Dockerfile", "w") as f:
                f.write(dockerfile_content)
            
            with open(build_context / "serve_model.py", "w") as f:
                f.write(serve_script)
            
            with open(build_context / "requirements.txt", "w") as f:
                f.write("mlflow\nflask\nnumpy\npandas\nscikit-learn")
            
            # Build image
            image_name = f"ainflue-ml/{deployment_id}:latest"
            image, build_logs = self.docker_client.images.build(
                path=str(build_context),
                tag=image_name,
                rm=True
            )
            
            logger.info(f"Built Docker image: {image_name}")
            return image_name
            
        except Exception as e:
            logger.error(f"Failed to build Docker image: {e}")
            raise
    
    async def _deploy_to_kubernetes(self, 
                                  deployment_id: str,
                                  docker_image: str,
                                  env_config: EnvironmentConfig) -> str:
        """Déploie sur Kubernetes"""
        try:
            # Deployment manifest
            deployment_manifest = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": f"ml-model-{deployment_id}",
                    "namespace": env_config.kubernetes_namespace,
                    "labels": {
                        "app": f"ml-model-{deployment_id}",
                        "environment": env_config.environment.value
                    }
                },
                "spec": {
                    "replicas": env_config.auto_scaling_config["min_replicas"],
                    "selector": {
                        "matchLabels": {
                            "app": f"ml-model-{deployment_id}"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": f"ml-model-{deployment_id}"
                            }
                        },
                        "spec": {
                            "containers": [{
                                "name": "ml-model",
                                "image": docker_image,
                                "ports": [{"containerPort": 8080}],
                                "env": [
                                    {"name": k, "value": v} 
                                    for k, v in env_config.environment_variables.items()
                                ],
                                "resources": {
                                    "limits": env_config.resource_limits,
                                    "requests": {
                                        k: v for k, v in env_config.resource_limits.items()
                                    }
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": env_config.health_check_endpoint,
                                        "port": 8080
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": env_config.health_check_endpoint,
                                        "port": 8080
                                    },
                                    "initialDelaySeconds": 10,
                                    "periodSeconds": 5
                                }
                            }]
                        }
                    }
                }
            }
            
            # Service manifest
            service_manifest = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": f"ml-model-{deployment_id}-service",
                    "namespace": env_config.kubernetes_namespace
                },
                "spec": {
                    "selector": {
                        "app": f"ml-model-{deployment_id}"
                    },
                    "ports": [{
                        "port": 80,
                        "targetPort": 8080
                    }],
                    "type": "ClusterIP"
                }
            }
            
            # Créer le namespace s'il n'existe pas
            try:
                self.k8s_core_v1.create_namespace(
                    body=client.V1Namespace(
                        metadata=client.V1ObjectMeta(name=env_config.kubernetes_namespace)
                    )
                )
            except kubernetes.client.exceptions.ApiException as e:
                if e.status != 409:  # Ignore si namespace existe déjà
                    raise
            
            # Créer le deployment
            self.k8s_apps_v1.create_namespaced_deployment(
                namespace=env_config.kubernetes_namespace,
                body=deployment_manifest
            )
            
            # Créer le service
            self.k8s_core_v1.create_namespaced_service(
                namespace=env_config.kubernetes_namespace,
                body=service_manifest
            )
            
            # HPA (Horizontal Pod Autoscaler)
            hpa_manifest = {
                "apiVersion": "autoscaling/v2",
                "kind": "HorizontalPodAutoscaler",
                "metadata": {
                    "name": f"ml-model-{deployment_id}-hpa",
                    "namespace": env_config.kubernetes_namespace
                },
                "spec": {
                    "scaleTargetRef": {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": f"ml-model-{deployment_id}"
                    },
                    "minReplicas": env_config.auto_scaling_config["min_replicas"],
                    "maxReplicas": env_config.auto_scaling_config["max_replicas"],
                    "metrics": [{
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": env_config.auto_scaling_config["target_cpu_utilization"]
                            }
                        }
                    }]
                }
            }
            
            # Créer l'HPA
            k8s_autoscaling_v2 = client.AutoscalingV2Api()
            k8s_autoscaling_v2.create_namespaced_horizontal_pod_autoscaler(
                namespace=env_config.kubernetes_namespace,
                body=hpa_manifest
            )
            
            logger.info(f"Deployed to Kubernetes: {deployment_id}")
            return f"ml-model-{deployment_id}"
            
        except Exception as e:
            logger.error(f"Failed to deploy to Kubernetes: {e}")
            raise
    
    async def promote_model(self, 
                           deployment_id: str,
                           target_environment: Environment,
                           strategy: PromotionStrategy = PromotionStrategy.AUTOMATIC) -> bool:
        """Promeut un modèle vers un environnement supérieur"""
        try:
            deployment = self.deployments.get(deployment_id)
            if not deployment:
                raise ValueError(f"Deployment {deployment_id} not found")
            
            # Vérifier les critères de promotion
            current_env = deployment.environment
            target_env_config = self.environments[target_environment]
            
            if not await self._check_promotion_criteria(deployment, target_env_config):
                logger.warning(f"Promotion criteria not met for {deployment_id}")
                return False
            
            # Stratégies de promotion
            if strategy == PromotionStrategy.MANUAL:
                self.promotion_queue.append(deployment_id)
                logger.info(f"Model {deployment_id} queued for manual promotion")
                return True
            
            elif strategy == PromotionStrategy.A_B_TEST:
                # Déploiement A/B avec traffic splitting
                await self._deploy_ab_test(deployment, target_environment)
                
            else:  # AUTOMATIC
                # Promotion automatique
                new_deployment_id = await self.deploy_model(
                    deployment.model_id,
                    deployment.model_version,
                    target_environment,
                    deployment.deployment_config
                )
                
                # Attendre la santé du nouveau déploiement
                await self._wait_for_health(new_deployment_id)
                
                # Traffic switch graduel
                await self._gradual_traffic_switch(deployment_id, new_deployment_id)
            
            self.successful_promotions += 1
            logger.info(f"Successfully promoted {deployment_id} to {target_environment.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to promote model: {e}")
            self.failed_promotions += 1
            return False
    
    async def _check_promotion_criteria(self, 
                                      deployment: ModelDeployment,
                                      target_env_config: EnvironmentConfig) -> bool:
        """Vérifie les critères de promotion"""
        try:
            criteria = target_env_config.promotion_criteria
            
            # Vérifier l'accuracy
            current_accuracy = deployment.performance_metrics.get("accuracy", 0)
            if current_accuracy < criteria.get("min_accuracy", 0):
                return False
            
            # Vérifier la latence
            current_latency = deployment.performance_metrics.get("latency_ms", float('inf'))
            if current_latency > criteria.get("max_latency_ms", float('inf')):
                return False
            
            # Vérifier l'uptime
            uptime_hours = (datetime.utcnow() - deployment.created_at).total_seconds() / 3600
            if uptime_hours < criteria.get("min_uptime_hours", 0):
                return False
            
            # Vérifier le success rate
            success_rate = deployment.performance_metrics.get("success_rate", 0)
            if success_rate < criteria.get("min_success_rate", 0):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check promotion criteria: {e}")
            return False
    
    async def rollback_deployment(self, deployment_id: str) -> bool:
        """Rollback d'un déploiement"""
        try:
            deployment = self.deployments.get(deployment_id)
            if not deployment:
                raise ValueError(f"Deployment {deployment_id} not found")
            
            if not deployment.rollback_version:
                logger.warning(f"No rollback version available for {deployment_id}")
                return False
            
            # Marquer comme rollback en cours
            deployment.status = DeploymentStatus.ROLLING_BACK
            deployment.updated_at = datetime.utcnow()
            
            # Déployer la version de rollback
            rollback_deployment_id = await self.deploy_model(
                deployment.model_id,
                deployment.rollback_version,
                deployment.environment,
                deployment.deployment_config
            )
            
            # Supprimer l'ancien déploiement
            await self._delete_deployment(deployment_id)
            
            logger.info(f"Successfully rolled back {deployment_id} to version {deployment.rollback_version}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback deployment: {e}")
            return False
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[ModelDeployment]:
        """Obtient le statut d'un déploiement"""
        return self.deployments.get(deployment_id)
    
    async def list_deployments(self, environment: Optional[Environment] = None) -> List[ModelDeployment]:
        """Liste les déploiements"""
        deployments = list(self.deployments.values())
        
        if environment:
            deployments = [d for d in deployments if d.environment == environment]
        
        return sorted(deployments, key=lambda x: x.created_at, reverse=True)
    
    async def get_promotion_stats(self) -> Dict[str, Any]:
        """Obtient les statistiques de promotion"""
        total_promotions = self.successful_promotions + self.failed_promotions
        success_rate = (self.successful_promotions / total_promotions * 100) if total_promotions > 0 else 0
        
        env_distribution = {}
        for deployment in self.deployments.values():
            env = deployment.environment.value
            env_distribution[env] = env_distribution.get(env, 0) + 1
        
        return {
            "total_deployments": self.deployment_count,
            "successful_promotions": self.successful_promotions,
            "failed_promotions": self.failed_promotions,
            "promotion_success_rate": success_rate,
            "pending_promotions": len(self.promotion_queue),
            "environment_distribution": env_distribution
        }
    
    async def _wait_for_health(self, deployment_id -> None: str, timeout_seconds -> None: int = 300) -> None:
        """Attend que le déploiement soit healthy"""
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            deployment = self.deployments.get(deployment_id)
            if deployment and deployment.health_status == "healthy":
                return True
            
            await asyncio.sleep(10)
        
        raise TimeoutError(f"Deployment {deployment_id} did not become healthy within {timeout_seconds}s")
    
    async def _gradual_traffic_switch(self, old_deployment_id -> None: str, new_deployment_id -> None: str) -> None:
        """Bascule graduelle du traffic"""
        # Simulation d'une bascule graduelle
        traffic_percentages = [10, 25, 50, 75, 100]
        
        for percentage in traffic_percentages:
            logger.info(f"Switching {percentage}% traffic to new deployment")
            await asyncio.sleep(30)  # Attendre entre chaque étape
            
            # Ici on pourrait implémenter la logique de traffic splitting
            # avec Istio, Nginx, ou un autre load balancer
        
        # Supprimer l'ancien déploiement une fois le traffic complètement basculé
        await self._delete_deployment(old_deployment_id)
    
    async def _delete_deployment(self, deployment_id -> None: str) -> None:
        """Supprime un déploiement Kubernetes"""
        try:
            deployment = self.deployments.get(deployment_id)
            if not deployment:
                return
            
            env_config = self.environments[deployment.environment]
            namespace = env_config.kubernetes_namespace
            
            # Supprimer le deployment
            self.k8s_apps_v1.delete_namespaced_deployment(
                name=f"ml-model-{deployment_id}",
                namespace=namespace
            )
            
            # Supprimer le service
            self.k8s_core_v1.delete_namespaced_service(
                name=f"ml-model-{deployment_id}-service",
                namespace=namespace
            )
            
            # Supprimer l'HPA
            k8s_autoscaling_v2 = client.AutoscalingV2Api()
            k8s_autoscaling_v2.delete_namespaced_horizontal_pod_autoscaler(
                name=f"ml-model-{deployment_id}-hpa",
                namespace=namespace
            )
            
            # Supprimer du tracking
            if deployment_id in self.deployments:
                del self.deployments[deployment_id]
            
            logger.info(f"Deleted deployment {deployment_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete deployment: {e}")

# Usage example
async def demo_staging_manager() -> None:
    """Démo du gestionnaire de staging"""
    manager = ModelStagingManager()
    await manager.initialize()
    
    # Déployer en dev
    deployment_id = await manager.deploy_model(
        "musician-classifier",
        "1.0",
        Environment.DEV
    )
    
    print(f"✅ Deployed to dev: {deployment_id}")
    
    # Simuler des métriques de performance
    deployment = manager.deployments[deployment_id]
    deployment.performance_metrics = {
        "accuracy": 0.92,
        "latency_ms": 85,
        "success_rate": 0.995
    }
    deployment.health_status = "healthy"
    
    # Promouvoir vers staging
    promoted = await manager.promote_model(deployment_id, Environment.STAGING)
    print(f"✅ Promoted to staging: {promoted}")
    
    # Statistiques
    stats = await manager.get_promotion_stats()
    print(f"✅ Promotion stats: {stats}")

if __name__ == "__main__":
    asyncio.run(demo_staging_manager())