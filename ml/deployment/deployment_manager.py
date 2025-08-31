"""
 Model Deployment System - IA Influencer Agent Platform Enterprise
===================================================================
Module: backend/ml/deployment/deployment_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
===================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

 GESTIONNAIRE DE DÉPLOIEMENT DE MODÈLES
Déploiement automatisé et monitoring des modèles ML
- Containerized deployment avec Docker/Kubernetes
- A/B testing et canary deployments
- Auto-scaling et load balancing
- Health checks et rollback automatique
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
import shutil
from pathlib import Path
import subprocess
import tempfile

# Configuration
logger = logging.getLogger(__name__)

class DeploymentType(Enum):
    """Types de déploiement"""
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    SERVERLESS = "serverless"
    EDGE = "edge"

class DeploymentStrategy(Enum):
    """Stratégies de déploiement"""
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING_UPDATE = "rolling_update"
    RECREATE = "recreate"

class DeploymentStatus(Enum):
    """Statuts de déploiement"""
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"
    ROLLING_BACK = "rolling_back"

@dataclass
class DeploymentConfig:
    """Configuration de déploiement"""
    model_name: str
    model_version: str
    deployment_type: DeploymentType
    strategy: DeploymentStrategy
    replicas: int = 3
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "256Mi"
    memory_limit: str = "1Gi"
    port: int = 8080
    health_check_path: str = "/health"
    environment_vars: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)

@dataclass
class DeploymentInfo:
    """Informations de déploiement"""
    deployment_id: str
    model_name: str
    model_version: str
    status: DeploymentStatus
    config: DeploymentConfig
    endpoint_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    health_status: str = "unknown"
    metrics: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)

@dataclass
class PerformanceMetrics:
    """Métriques de performance"""
    latency_p50: float
    latency_p95: float
    latency_p99: float
    throughput: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    timestamp: datetime

class ModelDeploymentManager:
    """Gestionnaire de déploiement de modèles"""
    
    def __init__(self, k8s_namespace: str = "ml-models"):
        self.k8s_namespace = k8s_namespace
        self.deployments: Dict[str, DeploymentInfo] = {}
        self.performance_history: Dict[str, List[PerformanceMetrics]] = {}
        
        # Mock des clients Docker/K8s pour éviter les dépendances
        self.docker_available = False
        self.k8s_available = False
        
        try:
            import docker
            self.docker_client = docker.from_env()
            self.docker_available = True
        except:
            logger.warning("Docker non disponible")
            
        try:
            import kubernetes
            self.k8s_available = True
        except:
            logger.warning("Kubernetes non disponible")
    
    async def deploy_model(self,
                         model_name: str,
                         model_version: str,
                         config: DeploymentConfig) -> str:
        """Déploie un modèle selon la configuration"""



        
        try:
            deployment_id = f"{model_name}-{model_version}-{uuid.uuid4().hex[:8]}"
            
            # Créer l'info de déploiement
            deployment_info = DeploymentInfo(
                deployment_id=deployment_id,
                model_name=model_name,
                model_version=model_version,
                status=DeploymentStatus.PENDING,
                config=config,
                created_at=datetime.now()
            )
            
            self.deployments[deployment_id] = deployment_info
            
            logger.info(f"Démarrage du déploiement: {deployment_id}")
            
            # Simulation du déploiement
            await self._simulate_deployment(deployment_info)
            
            return deployment_id
            
        except Exception as e:
            logger.error(f"Erreur déploiement {model_name} v{model_version}: {e}")
            if deployment_id in self.deployments:
                self.deployments[deployment_id].status = DeploymentStatus.FAILED
            raise
    
    async def _simulate_deployment(self, deployment_info: DeploymentInfo):
        """Simule un déploiement pour l'exemple"""



        
        try:
            # Simulation des phases
            deployment_info.status = DeploymentStatus.BUILDING
            await asyncio.sleep(2)  # Simulation build
            
            deployment_info.status = DeploymentStatus.DEPLOYING
            await asyncio.sleep(3)  # Simulation deploy
            
            # Création d'un endpoint simulé
            deployment_info.endpoint_url = f"http://localhost:808{len(self.deployments)}"
            deployment_info.status = DeploymentStatus.RUNNING
            deployment_info.health_status = "healthy"
            deployment_info.updated_at = datetime.now()
            
            logger.info(f"Déploiement simulé réussi: {deployment_info.deployment_id}")
            
        except Exception as e:
            deployment_info.status = DeploymentStatus.FAILED
            logger.error(f"Erreur simulation déploiement: {e}")
            raise
    
    def _generate_dockerfile(self, deployment_info: DeploymentInfo) -> str:
        """Génère un Dockerfile pour le modèle"""
        
        dockerfile = f"""
FROM python:3.9-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd --create-home --shell /bin/bash ml-user

# Répertoire de travail
WORKDIR /app

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le modèle et le code
COPY model/ ./model/
COPY server.py .

# Changer de propriétaire
RUN chown -R ml-user:ml-user /app

# Utiliser l'utilisateur non-root
USER ml-user

# Port d'exposition
EXPOSE {deployment_info.config.port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{deployment_info.config.port}{deployment_info.config.health_check_path} || exit 1

# Commande de démarrage
CMD ["python", "server.py"]
"""
        return dockerfile.strip()
    
    def _generate_model_server(self, deployment_info: DeploymentInfo) -> str:
        """Génère le code du serveur pour le modèle"""
        
        server_code = f"""
import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MODEL_NAME = "{deployment_info.model_name}"
MODEL_VERSION = "{deployment_info.model_version}"
PORT = {deployment_info.config.port}

# Serveur web simple sans dépendances
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import threading

class ModelHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {{"status": "healthy", "model": MODEL_NAME, "version": MODEL_VERSION}}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/predict':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Simulation de prédiction
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {{
                "predictions": [0.8, 0.2],  # Exemple
                "model_name": MODEL_NAME,
                "model_version": MODEL_VERSION,
                "timestamp": datetime.now().isoformat()
            }}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), ModelHandler) as httpd:
        print(f"Serveur démarré sur le port {{PORT}}")
        httpd.serve_forever()
"""
        return server_code.strip()
    
    def _generate_k8s_deployment(self, deployment_info: DeploymentInfo) -> Dict[str, Any]:
        """Génère le manifest de déploiement Kubernetes"""



        
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": deployment_info.deployment_id,
                "namespace": self.k8s_namespace,
                "labels": {
                    "app": deployment_info.deployment_id,
                    "model": deployment_info.model_name,
                    "version": deployment_info.model_version,
                    **deployment_info.config.labels
                },
                "annotations": deployment_info.config.annotations
            },
            "spec": {
                "replicas": deployment_info.config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": deployment_info.deployment_id
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": deployment_info.deployment_id,
                            "model": deployment_info.model_name,
                            "version": deployment_info.model_version
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "model-server",
                            "image": f"{deployment_info.model_name}:{deployment_info.model_version}",
                            "ports": [{
                                "containerPort": deployment_info.config.port,
                                "name": "http"
                            }],
                            "env": [
                                {"name": k, "value": v} 
                                for k, v in deployment_info.config.environment_vars.items()
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": deployment_info.config.cpu_request,
                                    "memory": deployment_info.config.memory_request
                                },
                                "limits": {
                                    "cpu": deployment_info.config.cpu_limit,
                                    "memory": deployment_info.config.memory_limit
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": deployment_info.config.health_check_path,
                                    "port": deployment_info.config.port
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": deployment_info.config.health_check_path,
                                    "port": deployment_info.config.port
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
    
    async def get_deployment_info(self, deployment_id: str) -> Optional[DeploymentInfo]:
        """Récupère les informations d'un déploiement"""



        return self.deployments.get(deployment_id)
    
    async def list_deployments(self, model_name: Optional[str] = None) -> List[DeploymentInfo]:
        """Liste les déploiements"""
        deployments = list(self.deployments.values())
        
        if model_name:
            deployments = [d for d in deployments if d.model_name == model_name]
        
        return deployments
    
    async def stop_deployment(self, deployment_id: str) -> bool:
        """Arrête un déploiement"""
        
        deployment_info = self.deployments.get(deployment_id)
        if not deployment_info:
            return False
        
        try:
            deployment_info.status = DeploymentStatus.STOPPED
            deployment_info.updated_at = datetime.now()
            
            logger.info(f"Déploiement arrêté: {deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur arrêt déploiement {deployment_id}: {e}")
            return False
    
    async def rollback_deployment(self, deployment_id: str) -> bool:
        """Rollback vers la version précédente"""
        
        deployment_info = self.deployments.get(deployment_id)
        if not deployment_info:
            return False
        
        try:
            deployment_info.status = DeploymentStatus.ROLLING_BACK
            await asyncio.sleep(2)  # Simulation
            deployment_info.status = DeploymentStatus.RUNNING
            
            logger.info(f"Rollback simulé pour {deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur rollback {deployment_id}: {e}")
            deployment_info.status = DeploymentStatus.FAILED
            return False
    
    async def collect_metrics(self, deployment_id: str) -> Optional[PerformanceMetrics]:
        """Collecte les métriques de performance"""
        
        deployment_info = self.deployments.get(deployment_id)
        if not deployment_info:
            return None
        
        try:
            # Métriques simulées
            import random
            
            metrics = PerformanceMetrics(
                latency_p50=random.uniform(0.05, 0.15),
                latency_p95=random.uniform(0.15, 0.30),
                latency_p99=random.uniform(0.30, 0.50),
                throughput=random.uniform(100, 500),
                error_rate=random.uniform(0, 0.05),
                cpu_usage=random.uniform(30, 80),
                memory_usage=random.uniform(100, 800),
                timestamp=datetime.now()
            )
            
            # Stocker dans l'historique
            if deployment_id not in self.performance_history:
                self.performance_history[deployment_id] = []
            
            self.performance_history[deployment_id].append(metrics)
            
            # Garder seulement les 1000 dernières métriques
            if len(self.performance_history[deployment_id]) > 1000:
                self.performance_history[deployment_id] = self.performance_history[deployment_id][-1000:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur collecte métriques {deployment_id}: {e}")
        
        return None
    
    async def auto_scale(self, deployment_id: str, target_cpu: float = 70.0) -> bool:
        """Auto-scaling basé sur CPU"""
        
        deployment_info = self.deployments.get(deployment_id)
        if not deployment_info:
            return False
        
        try:
            # Récupérer les métriques actuelles
            metrics = await self.collect_metrics(deployment_id)
            if not metrics:
                return False
            
            # Calculer le nombre de replicas nécessaires
            current_replicas = deployment_info.config.replicas
            current_cpu = metrics.cpu_usage
            
            if current_cpu > target_cpu:
                # Scale up
                new_replicas = min(current_replicas + 1, 10)  # Max 10 replicas
            elif current_cpu < target_cpu * 0.5:
                # Scale down
                new_replicas = max(current_replicas - 1, 1)  # Min 1 replica
            else:
                return True  # Pas de scaling nécessaire
            
            deployment_info.config.replicas = new_replicas
            
            logger.info(f"Auto-scaling {deployment_id}: {current_replicas} -> {new_replicas} replicas")
            return True
            
        except Exception as e:
            logger.error(f"Erreur auto-scaling {deployment_id}: {e}")
            return False
    
    async def canary_deployment(self, 
                               model_name: str,
                               new_version: str,
                               traffic_percentage: float = 10.0) -> str:
        """Déploiement canary avec répartition du trafic"""



        
        try:
            # Créer un déploiement canary
            canary_config = DeploymentConfig(
                model_name=model_name,
                model_version=new_version,
                deployment_type=DeploymentType.KUBERNETES,
                strategy=DeploymentStrategy.CANARY,
                replicas=1,  # Commencer petit
                labels={"deployment_type": "canary", "traffic_percentage": str(traffic_percentage)}
            )
            
            canary_id = await self.deploy_model(model_name, new_version, canary_config)
            
            logger.info(f"Déploiement canary créé: {canary_id} avec {traffic_percentage}% du trafic")
            
            return canary_id
            
        except Exception as e:
            logger.error(f"Erreur déploiement canary: {e}")
            raise
    
    async def promote_canary(self, canary_deployment_id: str) -> bool:
        """Promotion d'un déploiement canary vers production"""
        
        deployment_info = self.deployments.get(canary_deployment_id)
        if not deployment_info:
            return False
        
        try:
            # Vérifier que c'est bien un canary
            if deployment_info.config.labels.get("deployment_type") != "canary":
                logger.error(f"Le déploiement {canary_deployment_id} n'est pas un canary")
                return False
            
            # Simuler la promotion
            deployment_info.config.replicas = 3  # Scale up
            deployment_info.config.labels["deployment_type"] = "production"
            deployment_info.config.labels.pop("traffic_percentage", None)
            
            logger.info(f"Canary {canary_deployment_id} promu en production")
            return True
            
        except Exception as e:
            logger.error(f"Erreur promotion canary {canary_deployment_id}: {e}")
            return False
    
    async def blue_green_deployment(self, 
                                   model_name: str,
                                   new_version: str) -> Tuple[str, str]:
        """Déploiement blue-green"""



        
        try:
            # Identifier le déploiement actuel (blue)
            current_deployments = await self.list_deployments(model_name)
            blue_deployment = None
            for d in current_deployments:
                if d.status == DeploymentStatus.RUNNING:
                    blue_deployment = d
                    break
            
            # Créer le nouveau déploiement (green)
            green_config = DeploymentConfig(
                model_name=model_name,
                model_version=new_version,
                deployment_type=DeploymentType.KUBERNETES,
                strategy=DeploymentStrategy.BLUE_GREEN,
                replicas=3,
                labels={"deployment_color": "green"}
            )
            
            green_id = await self.deploy_model(model_name, new_version, green_config)
            
            # Attendre que le green soit prêt
            await asyncio.sleep(5)
            
            blue_id = blue_deployment.deployment_id if blue_deployment else None
            
            logger.info(f"Déploiement blue-green: Blue={blue_id}, Green={green_id}")
            
            return blue_id, green_id
            
        except Exception as e:
            logger.error(f"Erreur déploiement blue-green: {e}")
            raise
    
    async def switch_traffic(self, from_deployment: str, to_deployment: str) -> bool:
        """Bascule le trafic d'un déploiement à un autre"""



        
        try:
            from_info = self.deployments.get(from_deployment)
            to_info = self.deployments.get(to_deployment)
            
            if not from_info or not to_info:
                return False
            
            # Simuler la bascule de trafic
            logger.info(f"Bascule du trafic: {from_deployment} -> {to_deployment}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur bascule trafic: {e}")
            return False


# Factory pour créer des gestionnaires spécialisés
class DeploymentManagerFactory:
    """Factory pour créer des gestionnaires de déploiement"""
    
    @staticmethod
    def create_local_manager() -> ModelDeploymentManager:
        """Gestionnaire pour développement local"""



        return ModelDeploymentManager()
    
    @staticmethod
    def create_production_manager(k8s_namespace: str = "ml-production") -> ModelDeploymentManager:
        """Gestionnaire pour production"""



        return ModelDeploymentManager(k8s_namespace=k8s_namespace)


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation du gestionnaire de déploiement"""
    
    # Créer le gestionnaire
    manager = DeploymentManagerFactory.create_local_manager()
    
    # Configuration de déploiement
    config = DeploymentConfig(
        model_name="content_protection_classifier",
        model_version="1",
        deployment_type=DeploymentType.DOCKER,
        strategy=DeploymentStrategy.ROLLING_UPDATE,
        replicas=2,
        port=8080
    )
    
    # Déployer le modèle
    deployment_id = await manager.deploy_model(
        "content_protection_classifier",
        "1",
        config
    )
    
    print(f"Déploiement créé: {deployment_id}")
    
    # Attendre un peu puis vérifier le statut
    await asyncio.sleep(10)
    
    deployment_info = await manager.get_deployment_info(deployment_id)
    if deployment_info:
        print(f"Statut: {deployment_info.status}")
        print(f"Endpoint: {deployment_info.endpoint_url}")
        
        # Collecter des métriques
        metrics = await manager.collect_metrics(deployment_id)
        if metrics:
            print(f"Latence P95: {metrics.latency_p95:.3f}s")
            print(f"Throughput: {metrics.throughput:.2f} req/s")
            
        # Test auto-scaling
        scaled = await manager.auto_scale(deployment_id)
        print(f"Auto-scaling réussi: {scaled}")


if __name__ == "__main__":
    asyncio.run(example_usage())