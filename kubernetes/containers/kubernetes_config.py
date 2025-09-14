"""⚓ Kubernetes Configuration Manager - IA-Influencer-Agent Infrastructure
=======================================================================
Expert: DevOps Engineer + Cloud Architect + Kubernetes Specialist
Creator: Fahed Mlaiel <mlaiel@live.de>
=======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional Kubernetes configuration and management for IA-Influencer-Agent platform.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import asyncio
import logging
import json
import yaml
import os
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import kubernetes
from kubernetes import client, config
import base64

logger = logging.getLogger(__name__)

class KubernetesResourceType(Enum):
    """
Kubernetes resource types"""

    DEPLOYMENT = "Deployment"
    SERVICE = "Service"
    CONFIGMAP = "ConfigMap"
    SECRET = "Secret"
    INGRESS = "Ingress"
    PVC = "PersistentVolumeClaim"
    HPA = "HorizontalPodAutoscaler"
    NETWORK_POLICY = "NetworkPolicy"
    SERVICE_ACCOUNT = "ServiceAccount"
    ROLE = "Role"
    ROLE_BINDING = "RoleBinding"

@dataclass
class KubernetesResource:
    """Kubernetes resource configuration"""
    api_version: str
    kind: str
    metadata: Dict[str, Any]
    spec: Dict[str, Any]
    namespace: str = "default"

@dataclass
class PodSpec:
    """Pod specification for Kubernetes deployments"""
    containers: List[Dict[str, Any]]
    volumes: List[Dict[str, Any]] = field(default_factory=list)
    node_selector: Dict[str, str] = field(default_factory=dict)
    tolerations: List[Dict[str, Any]] = field(default_factory=list)
    affinity: Dict[str, Any] = field(default_factory=dict)
    service_account: str = "default"
    security_context: Dict[str, Any] = field(default_factory=dict)
    restart_policy: str = "Always"

@dataclass
class DeploymentSpec:
    """Deployment specification"""
    replicas: int
    selector: Dict[str, Any]
    template: Dict[str, Any]
    strategy: Dict[str, Any] = field(default_factory=dict)
    min_ready_seconds: int = 0
    progress_deadline_seconds: int = 600

class KubernetesConfigManager:
    """
Professional Kubernetes configuration manager"""
    
    def __init__(self, config_path -> None: str = "/app/config/kubernetes", namespace -> None: str = "ia-influencer") -> None:
        self.config_path = Path(config_path)
        self.namespace = namespace
        self.k8s_client = None
        self.apps_v1_api = None
        self.core_v1_api = None
        self.networking_v1_api = None
        self.autoscaling_v1_api = None
        self.rbac_v1_api = None
        self.resources = {}
        self.initialized = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def initialize(self) -> bool:
        """Initialize Kubernetes configuration manager"""
        try:
            # Load Kubernetes configuration
            try:
                config.load_incluster_config()  # In-cluster config
                self.logger.info("📡 Using in-cluster Kubernetes configuration")
            except:
                config.load_kube_config()  # Local kubeconfig
                self.logger.info("🏠 Using local Kubernetes configuration")
            
            # Initialize API clients
            self.apps_v1_api = client.AppsV1Api()
            self.core_v1_api = client.CoreV1Api()
            self.networking_v1_api = client.NetworkingV1Api()
            self.autoscaling_v1_api = client.AutoscalingV1Api()
            self.rbac_v1_api = client.RbacAuthorizationV1Api()
            
            # Create config directory
            self.config_path.mkdir(parents=True, exist_ok=True)
            
            # Create namespace if it doesn't exist
            await self._create_namespace()
            
            # Generate default configurations
            await self._generate_default_resources()
            
            self.initialized = True
            self.logger.info("✅ KubernetesConfigManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing KubernetesConfigManager: {e}")
            return False
    
    async def _create_namespace(self) -> None:
        """Create namespace if it doesn't exist"""
        try:
            # Check if namespace exists
            try:
                self.core_v1_api.read_namespace(name=self.namespace)
                self.logger.info(f"📁 Namespace '{self.namespace}' already exists")
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    # Create namespace
                    namespace_body = client.V1Namespace(
                        metadata=client.V1ObjectMeta(
                            name=self.namespace,
                            labels={
                                "app": "ia-influencer-agent",
                                "environment": "production",
                                "managed-by": "ia-influencer-deployment"
                            }
                        )
                    )
                    
                    self.core_v1_api.create_namespace(body=namespace_body)
                    self.logger.info(f"✅ Created namespace: {self.namespace}")
                else:
                    raise e
                    
        except Exception as e:
            self.logger.error(f"❌ Error creating namespace: {e}")
    
    async def _generate_default_resources(self) -> None:
        """Generate default Kubernetes resources for IA-Influencer services"""
        
        # ConfigMap for application configuration
        config_map = KubernetesResource(
            api_version="v1",
            kind="ConfigMap",
            metadata={
                "name": "ia-influencer-config",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-agent",
                    "component": "configuration"
                }
            },
            spec={
                "data": {
                    "database_host": "ia-influencer-postgres",
                    "redis_host": "ia-influencer-redis",
                    "api_version": "v1",
                    "log_level": "INFO",
                    "max_workers": "4",
                    "fingerprint_engine": "chromaprint",
                    "audio_formats": "mp3,wav,flac,aac,ogg"
                }
            }
        )
        
        # Secret for sensitive data
        secret = KubernetesResource(
            api_version="v1",
            kind="Secret",
            metadata={
                "name": "ia-influencer-secrets",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-agent",
                    "component": "secrets"
                }
            },
            spec={
                "type": "Opaque",
                "data": {
                    "jwt_secret": base64.b64encode("your-jwt-secret-here".encode()).decode(),
                    "postgres_password": base64.b64encode("your-postgres-password".encode()).decode(),
                    "redis_password": base64.b64encode("your-redis-password".encode()).decode(),
                    "openai_api_key": base64.b64encode("your-openai-key".encode()).decode(),
                    "aws_access_key_id": base64.b64encode("your-aws-key".encode()).decode(),
                    "aws_secret_access_key": base64.b64encode("your-aws-secret".encode()).decode()
                }
            }
        )
        
        # Web API Deployment
        web_api_deployment = KubernetesResource(
            api_version="apps/v1",
            kind="Deployment",
            metadata={
                "name": "ia-influencer-web-api",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-agent",
                    "component": "web-api"
                }
            },
            spec={
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "ia-influencer-agent",
                        "component": "web-api"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "ia-influencer-agent",
                            "component": "web-api"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "web-api",
                            "image": "ia-influencer/web-api:latest",
                            "ports": [{"containerPort": 8000}],
                            "env": [
                                {"name": "DATABASE_HOST", "valueFrom": {"configMapKeyRef": {"name": "ia-influencer-config", "key": "database_host"}}},
                                {"name": "REDIS_HOST", "valueFrom": {"configMapKeyRef": {"name": "ia-influencer-config", "key": "redis_host"}}},
                                {"name": "JWT_SECRET", "valueFrom": {"secretKeyRef": {"name": "ia-influencer-secrets", "key": "jwt_secret"}}},
                                {"name": "POSTGRES_PASSWORD", "valueFrom": {"secretKeyRef": {"name": "ia-influencer-secrets", "key": "postgres_password"}}}
                            ],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "1Gi"},
                                "limits": {"cpu": "1000m", "memory": "2Gi"}
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8000},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": 8000},
                                "initialDelaySeconds": 10,
                                "periodSeconds": 5
                            },
                            "securityContext": {
                                "allowPrivilegeEscalation": False,
                                "runAsNonRoot": True,
                                "runAsUser": 1000
                            }
                        }],
                        "serviceAccountName": "ia-influencer-api",
                        "securityContext": {
                            "fsGroup": 1000
                        }
                    }
                },
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxUnavailable": 1,
                        "maxSurge": 1
                    }
                }
            }
        )
        
        # Web API Service
        web_api_service = KubernetesResource(
            api_version="v1",
            kind="Service",
            metadata={
                "name": "ia-influencer-web-api-service",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-agent",
                    "component": "web-api"
                }
            },
            spec={
                "selector": {
                    "app": "ia-influencer-agent",
                    "component": "web-api"
                },
                "ports": [{
                    "port": 80,
                    "targetPort": 8000,
                    "protocol": "TCP"
                }],
                "type": "ClusterIP"
            }
        )
        
        # AI Engine Deployment
        ai_engine_deployment = KubernetesResource(
            api_version="apps/v1",
            kind="Deployment",
            metadata={
                "name": "ia-influencer-ai-engine",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-agent",
                    "component": "ai-engine"
                }
            },
            spec={
                "replicas": 2,
                "selector": {
                    "matchLabels": {
                        "app": "ia-influencer-agent",
                        "component": "ai-engine"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "ia-influencer-agent",
                            "component": "ai-engine"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "ai-engine",
                            "image": "ia-influencer/ai-engine:latest",
                            "ports": [{"containerPort": 8001}],
                            "env": [
                                {"name": "OPENAI_API_KEY", "valueFrom": {"secretKeyRef": {"name": "ia-influencer-secrets", "key": "openai_api_key"}}},
                                {"name": "MODEL_CACHE_PATH", "value": "/app/models"},
                                {"name": "GPU_ENABLED", "value": "true"}
                            ],
                            "resources": {
                                "requests": {"cpu": "1000m", "memory": "4Gi"},
                                "limits": {"cpu": "2000m", "memory": "8Gi", "nvidia.com/gpu": "1"}
                            },
                            "volumeMounts": [{
                                "name": "model-cache",
                                "mountPath": "/app/models"
                            }]
                        }],
                        "volumes": [{
                            "name": "model-cache",
                            "persistentVolumeClaim": {
                                "claimName": "ai-model-cache-pvc"
                            }
                        }],
                        "nodeSelector": {
                            "accelerator": "nvidia-tesla-gpu"
                        }
                    }
                }
            }
        )
        
        # Content Protection Deployment
        protection_deployment = KubernetesResource(
            api_version="apps/v1",
            kind="Deployment",
            metadata={
                "name": "ia-influencer-content-protection",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-agent",
                    "component": "content-protection"
                }
            },
            spec={
                "replicas": 2,
                "selector": {
                    "matchLabels": {
                        "app": "ia-influencer-agent",
                        "component": "content-protection"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "ia-influencer-agent",
                            "component": "content-protection"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "content-protection",
                            "image": "ia-influencer/content-protection:latest",
                            "ports": [{"containerPort": 8002}],
                            "env": [
                                {"name": "FINGERPRINT_ENGINE", "valueFrom": {"configMapKeyRef": {"name": "ia-influencer-config", "key": "fingerprint_engine"}}},
                                {"name": "AWS_ACCESS_KEY_ID", "valueFrom": {"secretKeyRef": {"name": "ia-influencer-secrets", "key": "aws_access_key_id"}}},
                                {"name": "AWS_SECRET_ACCESS_KEY", "valueFrom": {"secretKeyRef": {"name": "ia-influencer-secrets", "key": "aws_secret_access_key"}}}
                            ],
                            "resources": {
                                "requests": {"cpu": "750m", "memory": "2Gi"},
                                "limits": {"cpu": "1500m", "memory": "4Gi"}
                            }
                        }]
                    }
                }
            }
        )
        
        # PostgreSQL StatefulSet
        postgres_statefulset = KubernetesResource(
            api_version="apps/v1",
            kind="StatefulSet",
            metadata={
                "name": "ia-influencer-postgres",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-agent",
                    "component": "database"
                }
            },
            spec={
                "serviceName": "ia-influencer-postgres-headless",
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "ia-influencer-agent",
                        "component": "database"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "ia-influencer-agent",
                            "component": "database"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "postgres",
                            "image": "postgres:15-alpine",
                            "ports": [{"containerPort": 5432}],
                            "env": [
                                {"name": "POSTGRES_DB", "value": "ia_influencer"},
                                {"name": "POSTGRES_USER", "value": "ia_user"},
                                {"name": "POSTGRES_PASSWORD", "valueFrom": {"secretKeyRef": {"name": "ia-influencer-secrets", "key": "postgres_password"}}}
                            ],
                            "volumeMounts": [{
                                "name": "postgres-storage",
                                "mountPath": "/var/lib/postgresql/data"
                            }],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "1Gi"},
                                "limits": {"cpu": "1000m", "memory": "2Gi"}
                            }
                        }]
                    }
                },
                "volumeClaimTemplates": [{
                    "metadata": {"name": "postgres-storage"},
                    "spec": {
                        "accessModes": ["ReadWriteOnce"],
                        "resources": {"requests": {"storage": "50Gi"}},
                        "storageClassName": "fast-ssd"
                    }
                }]
            }
        )
        
        # Ingress for external access
        ingress = KubernetesResource(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            metadata={
                "name": "ia-influencer-ingress",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-agent"
                },
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/force-ssl-redirect": "true"
                }
            },
            spec={
                "tls": [{
                    "hosts": ["api.ia-influencer-agent.com"],
                    "secretName": "ia-influencer-tls"
                }],
                "rules": [{
                    "host": "api.ia-influencer-agent.com",
                    "http": {
                        "paths": [{
                            "path": "/",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": "ia-influencer-web-api-service",
                                    "port": {"number": 80}
                                }
                            }
                        }]
                    }
                }]
            }
        )
        
        # HPA for auto-scaling
        hpa = KubernetesResource(
            api_version="autoscaling/v2",
            kind="HorizontalPodAutoscaler",
            metadata={
                "name": "ia-influencer-web-api-hpa",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-agent",
                    "component": "web-api"
                }
            },
            spec={
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": "ia-influencer-web-api"
                },
                "minReplicas": 2,
                "maxReplicas": 10,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 70
                            }
                        }
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 80
                            }
                        }
                    }
                ]
            }
        )
        
        # Store resources
        resources_to_store = {
            "configmap": config_map,
            "secret": secret,
            "web-api-deployment": web_api_deployment,
            "web-api-service": web_api_service,
            "ai-engine-deployment": ai_engine_deployment,
            "content-protection-deployment": protection_deployment,
            "postgres-statefulset": postgres_statefulset,
            "ingress": ingress,
            "hpa": hpa
        }
        
        for name, resource in resources_to_store.items():
            self.resources[name] = resource
            await self._save_resource(name, resource)
    
    async def _save_resource(self, name: str, resource: KubernetesResource) -> None:
        """Save Kubernetes resource to file"""
        try:
            resource_file = self.config_path / f"{name}.yaml"
            resource_dict = asdict(resource)
            
            # Create proper Kubernetes manifest
            manifest = {
                "apiVersion": resource_dict["api_version"],
                "kind": resource_dict["kind"],
                "metadata": resource_dict["metadata"],
                "spec": resource_dict["spec"]
            }
            
            with open(resource_file, 'w') as f:
                yaml.dump(manifest, f, default_flow_style=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving resource {name}: {e}")
    
    async def apply_resource(self, resource_name: str) -> bool:
        """Apply Kubernetes resource"""
        try:
            if resource_name not in self.resources:
                self.logger.error(f"❌ Resource {resource_name} not found")
                return False
            
            resource = self.resources[resource_name]
            
            if resource.kind == "Deployment":
                return await self._apply_deployment(resource)
            elif resource.kind == "Service":
                return await self._apply_service(resource)
            elif resource.kind == "ConfigMap":
                return await self._apply_configmap(resource)
            elif resource.kind == "Secret":
                return await self._apply_secret(resource)
            elif resource.kind == "Ingress":
                return await self._apply_ingress(resource)
            elif resource.kind == "HorizontalPodAutoscaler":
                return await self._apply_hpa(resource)
            else:
                self.logger.warning(f"⚠️ Unsupported resource type: {resource.kind}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error applying resource {resource_name}: {e}")
            return False
    
    async def _apply_deployment(self, resource: KubernetesResource) -> bool:
        """Apply Deployment resource"""
        try:
            deployment_body = client.V1Deployment(
                api_version=resource.api_version,
                kind=resource.kind,
                metadata=client.V1ObjectMeta(**resource.metadata),
                spec=client.V1DeploymentSpec(**resource.spec)
            )
            
            try:
                # Try to update existing deployment
                self.apps_v1_api.patch_namespaced_deployment(
                    name=resource.metadata["name"],
                    namespace=resource.namespace,
                    body=deployment_body
                )
                self.logger.info(f"✅ Updated deployment: {resource.metadata['name']}")
                
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    # Create new deployment
                    self.apps_v1_api.create_namespaced_deployment(
                        namespace=resource.namespace,
                        body=deployment_body
                    )
                    self.logger.info(f"✅ Created deployment: {resource.metadata['name']}")
                else:
                    raise e
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error applying deployment: {e}")
            return False
    
    async def _apply_service(self, resource: KubernetesResource) -> bool:
        """Apply Service resource"""
        try:
            service_body = client.V1Service(
                api_version=resource.api_version,
                kind=resource.kind,
                metadata=client.V1ObjectMeta(**resource.metadata),
                spec=client.V1ServiceSpec(**resource.spec)
            )
            
            try:
                self.core_v1_api.patch_namespaced_service(
                    name=resource.metadata["name"],
                    namespace=resource.namespace,
                    body=service_body
                )
                self.logger.info(f"✅ Updated service: {resource.metadata['name']}")
                
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    self.core_v1_api.create_namespaced_service(
                        namespace=resource.namespace,
                        body=service_body
                    )
                    self.logger.info(f"✅ Created service: {resource.metadata['name']}")
                else:
                    raise e
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error applying service: {e}")
            return False
    
    async def _apply_configmap(self, resource: KubernetesResource) -> bool:
        """Apply ConfigMap resource"""
        try:
            configmap_body = client.V1ConfigMap(
                api_version=resource.api_version,
                kind=resource.kind,
                metadata=client.V1ObjectMeta(**resource.metadata),
                data=resource.spec.get("data", {})
            )
            
            try:
                self.core_v1_api.patch_namespaced_config_map(
                    name=resource.metadata["name"],
                    namespace=resource.namespace,
                    body=configmap_body
                )
                self.logger.info(f"✅ Updated configmap: {resource.metadata['name']}")
                
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    self.core_v1_api.create_namespaced_config_map(
                        namespace=resource.namespace,
                        body=configmap_body
                    )
                    self.logger.info(f"✅ Created configmap: {resource.metadata['name']}")
                else:
                    raise e
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error applying configmap: {e}")
            return False
    
    async def _apply_secret(self, resource: KubernetesResource) -> bool:
        """Apply Secret resource"""
        try:
            secret_body = client.V1Secret(
                api_version=resource.api_version,
                kind=resource.kind,
                metadata=client.V1ObjectMeta(**resource.metadata),
                type=resource.spec.get("type", "Opaque"),
                data=resource.spec.get("data", {})
            )
            
            try:
                self.core_v1_api.patch_namespaced_secret(
                    name=resource.metadata["name"],
                    namespace=resource.namespace,
                    body=secret_body
                )
                self.logger.info(f"✅ Updated secret: {resource.metadata['name']}")
                
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    self.core_v1_api.create_namespaced_secret(
                        namespace=resource.namespace,
                        body=secret_body
                    )
                    self.logger.info(f"✅ Created secret: {resource.metadata['name']}")
                else:
                    raise e
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error applying secret: {e}")
            return False
    
    async def _apply_ingress(self, resource: KubernetesResource) -> bool:
        """Apply Ingress resource"""
        try:
            ingress_body = client.V1Ingress(
                api_version=resource.api_version,
                kind=resource.kind,
                metadata=client.V1ObjectMeta(**resource.metadata),
                spec=client.V1IngressSpec(**resource.spec)
            )
            
            try:
                self.networking_v1_api.patch_namespaced_ingress(
                    name=resource.metadata["name"],
                    namespace=resource.namespace,
                    body=ingress_body
                )
                self.logger.info(f"✅ Updated ingress: {resource.metadata['name']}")
                
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    self.networking_v1_api.create_namespaced_ingress(
                        namespace=resource.namespace,
                        body=ingress_body
                    )
                    self.logger.info(f"✅ Created ingress: {resource.metadata['name']}")
                else:
                    raise e
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error applying ingress: {e}")
            return False
    
    async def _apply_hpa(self, resource: KubernetesResource) -> bool:
        """Apply HorizontalPodAutoscaler resource"""
        try:
            hpa_body = client.V1HorizontalPodAutoscaler(
                api_version=resource.api_version,
                kind=resource.kind,
                metadata=client.V1ObjectMeta(**resource.metadata),
                spec=client.V1HorizontalPodAutoscalerSpec(**resource.spec)
            )
            
            try:
                self.autoscaling_v1_api.patch_namespaced_horizontal_pod_autoscaler(
                    name=resource.metadata["name"],
                    namespace=resource.namespace,
                    body=hpa_body
                )
                self.logger.info(f"✅ Updated HPA: {resource.metadata['name']}")
                
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    self.autoscaling_v1_api.create_namespaced_horizontal_pod_autoscaler(
                        namespace=resource.namespace,
                        body=hpa_body
                    )
                    self.logger.info(f"✅ Created HPA: {resource.metadata['name']}")
                else:
                    raise e
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error applying HPA: {e}")
            return False
    
    async def deploy_all_resources(self) -> bool:
        """Deploy all Kubernetes resources"""
        try:
            success_count = 0
            total_count = len(self.resources)
            
            # Deploy in order: ConfigMap, Secret, Services, Deployments, Ingress, HPA
            resource_order = [
                "configmap", "secret", 
                "web-api-service", 
                "postgres-statefulset", "web-api-deployment", "ai-engine-deployment", "content-protection-deployment",
                "ingress", "hpa"
            ]
            
            for resource_name in resource_order:
                if resource_name in self.resources:
                    if await self.apply_resource(resource_name):
                        success_count += 1
                        self.logger.info(f"✅ Successfully deployed: {resource_name}")
                    else:
                        self.logger.error(f"❌ Failed to deploy: {resource_name}")
            
            success_rate = (success_count / total_count) * 100
            self.logger.info(f"📊 Deployment completed: {success_count}/{total_count} resources ({success_rate:.1f}%)")
            
            return success_count == total_count
            
        except Exception as e:
            self.logger.error(f"❌ Error deploying all resources: {e}")
            return False
    
    async def get_resource_status(self, resource_name: str) -> Dict[str, Any]:
        """Get status of deployed resource"""
        try:
            if resource_name not in self.resources:
                return {"status": "not_found", "error": "Resource not configured"}
            
            resource = self.resources[resource_name]
            
            if resource.kind == "Deployment":
                deployment = self.apps_v1_api.read_namespaced_deployment_status(
                    name=resource.metadata["name"],
                    namespace=resource.namespace
                )
                return {
                    "status": "ready" if deployment.status.ready_replicas == deployment.status.replicas else "not_ready",
                    "replicas": deployment.status.replicas,
                    "ready_replicas": deployment.status.ready_replicas,
                    "updated_replicas": deployment.status.updated_replicas
                }
            
            elif resource.kind == "Service":
                service = self.core_v1_api.read_namespaced_service_status(
                    name=resource.metadata["name"],
                    namespace=resource.namespace
                )
                return {
                    "status": "ready",
                    "cluster_ip": service.spec.cluster_ip,
                    "ports": [{"port": port.port, "target_port": port.target_port} for port in service.spec.ports]
                }
            
            else:
                return {"status": "unknown", "kind": resource.kind}
                
        except client.exceptions.ApiException as e:
            if e.status == 404:
                return {"status": "not_deployed", "error": "Resource not found in cluster"}
            else:
                return {"status": "error", "error": str(e)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

class KubernetesDeploymentManager:
    """Professional Kubernetes deployment manager"""
    
    def __init__(self, config_manager -> None: KubernetesConfigManager) -> None:
        self.config_manager = config_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def rolling_update(self, deployment_name: str, new_image: str) -> bool:
        """Perform rolling update of deployment"""
        try:
            # Get current deployment
            deployment = self.config_manager.apps_v1_api.read_namespaced_deployment(
                name=deployment_name,
                namespace=self.config_manager.namespace
            )
            
            # Update image
            for container in deployment.spec.template.spec.containers:
                if container.name in deployment_name:
                    container.image = new_image
            
            # Apply update
            self.config_manager.apps_v1_api.patch_namespaced_deployment(
                name=deployment_name,
                namespace=self.config_manager.namespace,
                body=deployment
            )
            
            self.logger.info(f"✅ Started rolling update for {deployment_name} with image {new_image}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error performing rolling update: {e}")
            return False
    
    async def scale_deployment(self, deployment_name: str, replicas: int) -> bool:
        """Scale deployment to specified number of replicas"""
        try:
            # Scale deployment
            scale_body = client.V1Scale(
                spec=client.V1ScaleSpec(replicas=replicas)
            )
            
            self.config_manager.apps_v1_api.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace=self.config_manager.namespace,
                body=scale_body
            )
            
            self.logger.info(f"✅ Scaled {deployment_name} to {replicas} replicas")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error scaling deployment: {e}")
            return False

class KubernetesPodManager:
    """Professional Kubernetes pod manager"""
    
    def __init__(self, config_manager -> None: KubernetesConfigManager) -> None:
        self.config_manager = config_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def get_pods(self, label_selector: str = None) -> List[Dict[str, Any]]:
        """Get pods in namespace"""
        try:
            pods_list = self.config_manager.core_v1_api.list_namespaced_pod(
                namespace=self.config_manager.namespace,
                label_selector=label_selector
            )
            
            pods = []
            for pod in pods_list.items:
                pods.append({
                    "name": pod.metadata.name,
                    "status": pod.status.phase,
                    "ready": all(condition.status == "True" for condition in pod.status.conditions or [] if condition.type == "Ready"),
                    "restarts": sum(container.restart_count for container in pod.status.container_statuses or []),
                    "node": pod.spec.node_name,
                    "created": pod.metadata.creation_timestamp
                })
            
            return pods
            
        except Exception as e:
            self.logger.error(f"❌ Error getting pods: {e}")
            return []
    
    async def get_pod_logs(self, pod_name: str, container_name: str = None, lines: int = 100) -> str:
        """Get logs from pod"""
        try:
            logs = self.config_manager.core_v1_api.read_namespaced_pod_log(
                name=pod_name,
                namespace=self.config_manager.namespace,
                container=container_name,
                tail_lines=lines
            )
            
            return logs
            
        except Exception as e:
            self.logger.error(f"❌ Error getting pod logs: {e}")
            return ""
    
    async def execute_command(self, pod_name: str, command: List[str], container_name: str = None) -> str:
        """Execute command in pod"""
        try:
            from kubernetes.stream import stream
            
            exec_command = ['/bin/sh', '-c'] + command
            
            response = stream(
                self.config_manager.core_v1_api.connect_get_namespaced_pod_exec,
                name=pod_name,
                namespace=self.config_manager.namespace,
                container=container_name,
                command=exec_command,
                stderr=True, stdin=False, stdout=True, tty=False
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error executing command in pod: {e}")
            return ""

__all__ = [
    "KubernetesConfigManager", 
    "KubernetesDeploymentManager", 
    "KubernetesPodManager",
    "KubernetesResource",
    "KubernetesResourceType",
    "PodSpec",
    "DeploymentSpec"
]
