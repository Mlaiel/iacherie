"""Kubernetes Configuration Module for IA-Influencer Agent Platform
===============================================================

Professional Kubernetes orchestration and deployment configuration
for enterprise-grade AI-powered content protection and monetization platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import yaml
from pathlib import Path


@dataclass
class KubernetesResourceLimits:
    """Resource limits configuration for Kubernetes pods"""    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "128Mi"
    memory_limit: str = "512Mi"
    ephemeral_storage_request: str = "1Gi"
    ephemeral_storage_limit: str = "2Gi"


@dataclass
class KubernetesService:
    """Kubernetes service configuration"""    name: str
    namespace: str = "ia-influencer"
    labels: Dict[str, str] = field(default_factory=dict)
    selector: Dict[str, str] = field(default_factory=dict)
    ports: List[Dict[str, Union[str, int]]] = field(default_factory=list)
    service_type: str = "ClusterIP"
    load_balancer_ip: Optional[str] = None


@dataclass
class KubernetesDeployment:
    """Kubernetes deployment configuration"""    name: str
    namespace: str = "ia-influencer"
    replicas: int = 1
    image: str = ""
    image_pull_policy: str = "Always"
    ports: List[int] = field(default_factory=list)
    env_vars: Dict[str, str] = field(default_factory=dict)
    env_secrets: List[str] = field(default_factory=list)
    volume_mounts: List[Dict[str, str]] = field(default_factory=list)
    resource_limits: KubernetesResourceLimits = field(default_factory=KubernetesResourceLimits)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    liveness_probe: Optional[Dict[str, Any]] = None
    readiness_probe: Optional[Dict[str, Any]] = None
    startup_probe: Optional[Dict[str, Any]] = None


class KubernetesConfig:
    """    Professional Kubernetes configuration manager for IA-Influencer Agent Platform.
    
    Provides enterprise-grade orchestration for:
    - AI processing microservices with GPU support
    - Content protection services with auto-scaling
    - Multi-database clusters with persistent storage
    - Revenue tracking and monetization engines
    - Web crawlers with scheduled workloads
    - Real-time processing pipelines
    - Load balancing and service mesh integration
    """    
    def __init__(self, environment: str = "development", cluster_name: str = "ia-influencer-cluster"):
        self.environment = environment
        self.cluster_name = cluster_name
        self.namespace = f"ia-influencer-{environment}"
        self.registry_url = self._get_registry_url()
        self.storage_class = self._get_storage_class()
        
    def _get_registry_url(self) -> str:
        """Get container registry URL based on environment"""        registry_map = {
            "development": "localhost:5000",
            "staging": "registry.staging.ia-influencer.com",
            "production": "registry.ia-influencer.com"
        }
        return registry_map.get(self.environment, "localhost:5000")
    
    def _get_storage_class(self) -> str:
        """Get storage class based on environment"""        storage_map = {
            "development": "standard",
            "staging": "fast-ssd",
            "production": "premium-ssd"
        }
        return storage_map.get(self.environment, "standard")
    
    def generate_namespace(self) -> Dict[str, Any]:
        """Generate namespace configuration"""        return {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.namespace,
                "labels": {
                    "name": self.namespace,
                    "project": "ia-influencer-agent",
                    "environment": self.environment,
                    "managed-by": "fahed-mlaiel"
                },
                "annotations": {
                    "author": "Fahed Mlaiel <mlaiel@live.de>",
                    "project": "IA-Influencer Agent Platform",
                    "version": "2.0"
                }
            }
        }
    
    def generate_config_maps(self) -> List[Dict[str, Any]]:
        """Generate configuration maps for all services"""        config_maps = []
        
        # Main API configuration
        api_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "api-config",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-api",
                    "component": "configuration"
                }
            },
            "data": {
                "ENVIRONMENT": self.environment,
                "LOG_LEVEL": "INFO" if self.environment == "production" else "DEBUG",
                "API_V1_PREFIX": "/api/v1",
                "API_V2_PREFIX": "/api/v2",
                "CORS_ORIGINS": "*" if self.environment == "development" else "https://ia-influencer.com",
                "MAX_UPLOAD_SIZE": "100MB",
                "RATE_LIMIT_REQUESTS": "100",
                "RATE_LIMIT_WINDOW": "60"
            }
        }
        config_maps.append(api_config)
        
        # Database configuration
        db_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "database-config",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-database",
                    "component": "configuration"
                }
            },
            "data": {
                "POSTGRES_DB": "ia_influencer",
                "POSTGRES_USER": "ia_user",
                "REDIS_DB": "0",
                "MONGO_DB": "ia_influencer",
                "POSTGRES_MAX_CONNECTIONS": "200",
                "REDIS_MAX_CONNECTIONS": "100"
            }
        }
        config_maps.append(db_config)
        
        # AI Services configuration
        ai_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "ai-services-config",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-ai",
                    "component": "configuration"
                }
            },
            "data": {
                "MODEL_CACHE_SIZE": "2GB",
                "BATCH_SIZE": "32",
                "MAX_CONCURRENT_REQUESTS": "10",
                "GPU_MEMORY_FRACTION": "0.8",
                "FINGERPRINT_THRESHOLD": "0.85",
                "VECTOR_DIMENSION": "512"
            }
        }
        config_maps.append(ai_config)
        
        return config_maps
    
    def generate_secrets(self) -> List[Dict[str, Any]]:
        """Generate secret configurations"""        secrets = []
        
        # Database secrets
        db_secrets = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "database-secrets",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-database",
                    "component": "secrets"
                }
            },
            "type": "Opaque",
            "data": {
                # Base64 encoded values - replace with actual secrets
                "POSTGRES_PASSWORD": "aWFfcG9zdGdyZXNfcGFzcw==",  # ia_postgres_pass
                "REDIS_PASSWORD": "aWFfcmVkaXNfcGFzcw==",        # ia_redis_pass
                "MONGO_ROOT_PASSWORD": "aWFfbW9uZ29fcGFzcw==",    # ia_mongo_pass
                "JWT_SECRET": "aWFfand0X3NlY3JldF9rZXlfMjAyNQ==", # ia_jwt_secret_key_2025
                "SECRET_KEY": "aWFfc2VjcmV0X2tleV8yMDI1",        # ia_secret_key_2025
            }
        }
        secrets.append(db_secrets)
        
        # Payment API secrets
        payment_secrets = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "payment-secrets",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-monetization",
                    "component": "secrets"
                }
            },
            "type": "Opaque",
            "data": {
                "STRIPE_API_KEY": "c2tfdGVzdF8xMjM0NTY3ODkw",      # sk_test_1234567890
                "STRIPE_WEBHOOK_SECRET": "d2hfc2VjXzEyMzQ1Njc4OTA=", # wh_sec_1234567890
                "PAYPAL_CLIENT_ID": "cGF5cGFsX2NsaWVudF9pZA==",     # paypal_client_id
                "PAYPAL_CLIENT_SECRET": "cGF5cGFsX2NsaWVudF9zZWNyZXQ=", # paypal_client_secret
                "WISE_API_KEY": "d2lzZV9hcGlfa2V5XzEyMzQ=",        # wise_api_key_1234
            }
        }
        secrets.append(payment_secrets)
        
        # External API secrets
        external_secrets = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "external-api-secrets",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-integrations",
                    "component": "secrets"
                }
            },
            "type": "Opaque",
            "data": {
                "SPOTIFY_CLIENT_ID": "c3BvdGlmeV9jbGllbnRfaWQ=",     # spotify_client_id
                "SPOTIFY_CLIENT_SECRET": "c3BvdGlmeV9jbGllbnRfc2VjcmV0", # spotify_client_secret
                "YOUTUBE_API_KEY": "eW91dHViZV9hcGlfa2V5XzEyMzQ=",   # youtube_api_key_1234
                "INSTAGRAM_ACCESS_TOKEN": "aWdfYWNjZXNzX3Rva2VuXzEyMzQ=", # ig_access_token_1234
                "TIKTOK_ACCESS_TOKEN": "dGlrdG9rX2FjY2Vzc190b2tlbl8xMjM0", # tiktok_access_token_1234
            }
        }
        secrets.append(external_secrets)
        
        return secrets
    
    def generate_persistent_volumes(self) -> List[Dict[str, Any]]:
        """Generate persistent volume configurations"""        volumes = []
        
        # Database volumes
        db_volumes = [
            {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {
                    "name": f"postgres-data-{self.environment}",
                    "namespace": self.namespace,
                    "labels": {
                        "app": "postgres",
                        "component": "database"
                    }
                },
                "spec": {
                    "accessModes": ["ReadWriteOnce"],
                    "storageClassName": self.storage_class,
                    "resources": {
                        "requests": {
                            "storage": "20Gi" if self.environment == "production" else "5Gi"
                        }
                    }
                }
            },
            {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {
                    "name": f"redis-data-{self.environment}",
                    "namespace": self.namespace,
                    "labels": {
                        "app": "redis",
                        "component": "cache"
                    }
                },
                "spec": {
                    "accessModes": ["ReadWriteOnce"],
                    "storageClassName": self.storage_class,
                    "resources": {
                        "requests": {
                            "storage": "10Gi" if self.environment == "production" else "2Gi"
                        }
                    }
                }
            },
            {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {
                    "name": f"mongo-data-{self.environment}",
                    "namespace": self.namespace,
                    "labels": {
                        "app": "mongodb",
                        "component": "database"
                    }
                },
                "spec": {
                    "accessModes": ["ReadWriteOnce"],
                    "storageClassName": self.storage_class,
                    "resources": {
                        "requests": {
                            "storage": "50Gi" if self.environment == "production" else "10Gi"
                        }
                    }
                }
            }
        ]
        volumes.extend(db_volumes)
        
        # Model storage for AI services
        model_volume = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": f"ai-models-{self.environment}",
                "namespace": self.namespace,
                "labels": {
                    "app": "ai-services",
                    "component": "model-storage"
                }
            },
            "spec": {
                "accessModes": ["ReadWriteMany"],
                "storageClassName": self.storage_class,
                "resources": {
                    "requests": {
                        "storage": "100Gi" if self.environment == "production" else "20Gi"
                    }
                }
            }
        }
        volumes.append(model_volume)
        
        # Content storage for protection services
        content_volume = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": f"content-storage-{self.environment}",
                "namespace": self.namespace,
                "labels": {
                    "app": "content-protection",
                    "component": "content-storage"
                }
            },
            "spec": {
                "accessModes": ["ReadWriteMany"],
                "storageClassName": self.storage_class,
                "resources": {
                    "requests": {
                        "storage": "200Gi" if self.environment == "production" else "50Gi"
                    }
                }
            }
        }
        volumes.append(content_volume)
        
        return volumes
    
    def generate_deployments(self) -> List[Dict[str, Any]]:
        """Generate deployment configurations for all services"""        deployments = []
        
        # Main API deployment
        api_deployment = self._create_deployment(
            KubernetesDeployment(
                name="ia-influencer-api",
                namespace=self.namespace,
                replicas=3 if self.environment == "production" else 1,
                image=f"{self.registry_url}/ia-influencer-agent-api:latest-{self.environment}",
                ports=[8000],
                env_vars={
                    "ENVIRONMENT": self.environment,
                    "DATABASE_URL": "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@postgres:5432/$(POSTGRES_DB)",
                    "REDIS_URL": "redis://:$(REDIS_PASSWORD)@redis:6379/$(REDIS_DB)",
                    "MONGODB_URL": "mongodb://$(MONGO_USER):$(MONGO_ROOT_PASSWORD)@mongo:27017/$(MONGO_DB)"
                },
                env_secrets=["database-secrets", "external-api-secrets"],
                resource_limits=KubernetesResourceLimits(
                    cpu_request="500m",
                    cpu_limit="2000m",
                    memory_request="512Mi",
                    memory_limit="2Gi"
                ),
                labels={
                    "app": "ia-influencer-api",
                    "component": "backend",
                    "tier": "api"
                },
                liveness_probe={
                    "httpGet": {
                        "path": "/health",
                        "port": 8000
                    },
                    "initialDelaySeconds": 30,
                    "periodSeconds": 10
                },
                readiness_probe={
                    "httpGet": {
                        "path": "/ready",
                        "port": 8000
                    },
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5
                }
            )
        )
        deployments.append(api_deployment)
        
        # AI Fingerprinting deployment
        ai_deployment = self._create_deployment(
            KubernetesDeployment(
                name="ia-ai-fingerprinting",
                namespace=self.namespace,
                replicas=2 if self.environment == "production" else 1,
                image=f"{self.registry_url}/ia-influencer-agent-ai-fingerprinting:latest-{self.environment}",
                ports=[8001],
                volume_mounts=[
                    {
                        "name": "ai-models",
                        "mountPath": "/app/models",
                        "readOnly": True
                    }
                ],
                resource_limits=KubernetesResourceLimits(
                    cpu_request="1000m",
                    cpu_limit="4000m",
                    memory_request="2Gi",
                    memory_limit="8Gi"
                ),
                labels={
                    "app": "ia-ai-fingerprinting",
                    "component": "ai-processing",
                    "tier": "ml"
                },
                annotations={
                    "gpu-required": "true",
                    "ml-workload": "true"
                }
            )
        )
        deployments.append(ai_deployment)
        
        # Content Protection deployment
        protection_deployment = self._create_deployment(
            KubernetesDeployment(
                name="ia-content-protection",
                namespace=self.namespace,
                replicas=2 if self.environment == "production" else 1,
                image=f"{self.registry_url}/ia-influencer-agent-content-protection:latest-{self.environment}",
                ports=[8002],
                volume_mounts=[
                    {
                        "name": "content-storage",
                        "mountPath": "/app/content"
                    }
                ],
                resource_limits=KubernetesResourceLimits(
                    cpu_request="500m",
                    cpu_limit="2000m",
                    memory_request="1Gi",
                    memory_limit="4Gi"
                ),
                labels={
                    "app": "ia-content-protection",
                    "component": "protection",
                    "tier": "processing"
                }
            )
        )
        deployments.append(protection_deployment)
        
        # Monetization Engine deployment
        monetization_deployment = self._create_deployment(
            KubernetesDeployment(
                name="ia-monetization-engine",
                namespace=self.namespace,
                replicas=2 if self.environment == "production" else 1,
                image=f"{self.registry_url}/ia-influencer-agent-monetization:latest-{self.environment}",
                ports=[8003],
                env_secrets=["payment-secrets"],
                resource_limits=KubernetesResourceLimits(
                    cpu_request="200m",
                    cpu_limit="1000m",
                    memory_request="256Mi",
                    memory_limit="1Gi"
                ),
                labels={
                    "app": "ia-monetization-engine",
                    "component": "monetization",
                    "tier": "business"
                }
            )
        )
        deployments.append(monetization_deployment)
        
        # Database deployments
        deployments.extend(self._generate_database_deployments())
        
        return deployments
    
    def _create_deployment(self, config: KubernetesDeployment) -> Dict[str, Any]:
        """Create deployment manifest from configuration"""        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace,
                "labels": config.labels,
                "annotations": config.annotations
            },
            "spec": {
                "replicas": config.replicas,
                "selector": {
                    "matchLabels": {"app": config.name}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": config.name, **config.labels},
                        "annotations": config.annotations
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": config.name,
                                "image": config.image,
                                "imagePullPolicy": config.image_pull_policy,
                                "ports": [{"containerPort": port} for port in config.ports],
                                "resources": {
                                    "requests": {
                                        "cpu": config.resource_limits.cpu_request,
                                        "memory": config.resource_limits.memory_request,
                                        "ephemeral-storage": config.resource_limits.ephemeral_storage_request
                                    },
                                    "limits": {
                                        "cpu": config.resource_limits.cpu_limit,
                                        "memory": config.resource_limits.memory_limit,
                                        "ephemeral-storage": config.resource_limits.ephemeral_storage_limit
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        
        # Add environment variables
        if config.env_vars or config.env_secrets:
            container["env"] = []
            
            for key, value in config.env_vars.items():
                container["env"].append({"name": key, "value": value})
            
            for secret_name in config.env_secrets:
                # Add all keys from secret
                for key in ["POSTGRES_PASSWORD", "REDIS_PASSWORD", "MONGO_ROOT_PASSWORD", 
                           "JWT_SECRET", "SECRET_KEY", "STRIPE_API_KEY", "SPOTIFY_CLIENT_ID"]:
                    container["env"].append({
                        "name": key,
                        "valueFrom": {
                            "secretKeyRef": {
                                "name": secret_name,
                                "key": key,
                                "optional": True
                            }
                        }
                    })
        
        # Add volume mounts
        if config.volume_mounts:
            container["volumeMounts"] = config.volume_mounts
            deployment["spec"]["template"]["spec"]["volumes"] = []
            
            for mount in config.volume_mounts:
                volume_name = mount["name"]
                deployment["spec"]["template"]["spec"]["volumes"].append({
                    "name": volume_name,
                    "persistentVolumeClaim": {
                        "claimName": f"{volume_name.replace('_', '-')}-{self.environment}"
                    }
                })
        
        # Add probes
        if config.liveness_probe:
            container["livenessProbe"] = config.liveness_probe
        
        if config.readiness_probe:
            container["readinessProbe"] = config.readiness_probe
        
        if config.startup_probe:
            container["startupProbe"] = config.startup_probe
        
        return deployment
    
    def _generate_database_deployments(self) -> List[Dict[str, Any]]:
        """Generate database deployment configurations"""        databases = []
        
        # PostgreSQL deployment
        postgres_deployment = self._create_deployment(
            KubernetesDeployment(
                name="postgres",
                namespace=self.namespace,
                replicas=1,  # Use StatefulSet for multi-replica
                image="postgres:15.4-alpine",
                ports=[5432],
                env_vars={
                    "POSTGRES_DB": "ia_influencer",
                    "POSTGRES_USER": "ia_user"
                },
                env_secrets=["database-secrets"],
                volume_mounts=[
                    {
                        "name": "postgres-data",
                        "mountPath": "/var/lib/postgresql/data"
                    }
                ],
                resource_limits=KubernetesResourceLimits(
                    cpu_request="500m",
                    cpu_limit="2000m",
                    memory_request="512Mi",
                    memory_limit="2Gi"
                ),
                labels={
                    "app": "postgres",
                    "component": "database",
                    "tier": "data"
                },
                liveness_probe={
                    "exec": {
                        "command": ["pg_isready", "-U", "ia_user", "-d", "ia_influencer"]
                    },
                    "initialDelaySeconds": 30,
                    "periodSeconds": 10
                }
            )
        )
        databases.append(postgres_deployment)
        
        # Redis deployment
        redis_deployment = self._create_deployment(
            KubernetesDeployment(
                name="redis",
                namespace=self.namespace,
                replicas=1,
                image="redis:7.2-alpine",
                ports=[6379],
                env_secrets=["database-secrets"],
                volume_mounts=[
                    {
                        "name": "redis-data",
                        "mountPath": "/data"
                    }
                ],
                resource_limits=KubernetesResourceLimits(
                    cpu_request="100m",
                    cpu_limit="500m",
                    memory_request="128Mi",
                    memory_limit="512Mi"
                ),
                labels={
                    "app": "redis",
                    "component": "cache",
                    "tier": "data"
                },
                liveness_probe={
                    "exec": {
                        "command": ["redis-cli", "ping"]
                    },
                    "initialDelaySeconds": 10,
                    "periodSeconds": 10
                }
            )
        )
        databases.append(redis_deployment)
        
        # MongoDB deployment
        mongo_deployment = self._create_deployment(
            KubernetesDeployment(
                name="mongodb",
                namespace=self.namespace,
                replicas=1,
                image="mongo:7.0-jammy",
                ports=[27017],
                env_vars={
                    "MONGO_INITDB_ROOT_USERNAME": "ia_admin",
                    "MONGO_INITDB_DATABASE": "ia_influencer"
                },
                env_secrets=["database-secrets"],
                volume_mounts=[
                    {
                        "name": "mongo-data",
                        "mountPath": "/data/db"
                    }
                ],
                resource_limits=KubernetesResourceLimits(
                    cpu_request="200m",
                    cpu_limit="1000m",
                    memory_request="256Mi",
                    memory_limit="1Gi"
                ),
                labels={
                    "app": "mongodb",
                    "component": "database",
                    "tier": "data"
                },
                liveness_probe={
                    "exec": {
                        "command": ["mongosh", "--eval", "db.adminCommand('ping')"]
                    },
                    "initialDelaySeconds": 30,
                    "periodSeconds": 10
                }
            )
        )
        databases.append(mongo_deployment)
        
        return databases
    
    def generate_services(self) -> List[Dict[str, Any]]:
        """Generate service configurations"""        services = []
        
        # API service with load balancer
        api_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "ia-influencer-api-service",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-api",
                    "component": "backend"
                },
                "annotations": {
                    "service.beta.kubernetes.io/aws-load-balancer-type": "nlb" if self.environment == "production" else ""
                }
            },
            "spec": {
                "selector": {
                    "app": "ia-influencer-api"
                },
                "ports": [
                    {
                        "port": 80,
                        "targetPort": 8000,
                        "protocol": "TCP",
                        "name": "http"
                    }
                ],
                "type": "LoadBalancer" if self.environment == "production" else "ClusterIP"
            }
        }
        services.append(api_service)
        
        # Internal services
        internal_services = [
            ("ia-ai-fingerprinting", "ia-ai-fingerprinting", 8001),
            ("ia-content-protection", "ia-content-protection", 8002),
            ("ia-monetization-engine", "ia-monetization-engine", 8003),
            ("postgres", "postgres", 5432),
            ("redis", "redis", 6379),
            ("mongodb", "mongodb", 27017)
        ]
        
        for service_name, app_name, port in internal_services:
            service = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": f"{service_name}-service",
                    "namespace": self.namespace,
                    "labels": {
                        "app": app_name
                    }
                },
                "spec": {
                    "selector": {
                        "app": app_name
                    },
                    "ports": [
                        {
                            "port": port,
                            "targetPort": port,
                            "protocol": "TCP"
                        }
                    ],
                    "type": "ClusterIP"
                }
            }
            services.append(service)
        
        return services
    
    def generate_ingress(self) -> Dict[str, Any]:
        """Generate ingress configuration"""        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "ia-influencer-ingress",
                "namespace": self.namespace,
                "labels": {
                    "app": "ia-influencer-platform"
                },
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "nginx.ingress.kubernetes.io/rewrite-target": "/",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/rate-limit": "100",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m"
                }
            },
            "spec": {
                "tls": [
                    {
                        "hosts": [f"api-{self.environment}.ia-influencer.com"],
                        "secretName": f"ia-influencer-tls-{self.environment}"
                    }
                ],
                "rules": [
                    {
                        "host": f"api-{self.environment}.ia-influencer.com",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "ia-influencer-api-service",
                                            "port": {
                                                "number": 80
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    
    def generate_horizontal_pod_autoscaler(self) -> List[Dict[str, Any]]:
        """Generate HPA configurations for auto-scaling"""        hpas = []
        
        # API HPA
        api_hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": "ia-influencer-api-hpa",
                "namespace": self.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": "ia-influencer-api"
                },
                "minReplicas": 1 if self.environment == "development" else 3,
                "maxReplicas": 5 if self.environment == "development" else 20,
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
        }
        hpas.append(api_hpa)
        
        # AI Processing HPA
        ai_hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": "ia-ai-fingerprinting-hpa",
                "namespace": self.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": "ia-ai-fingerprinting"
                },
                "minReplicas": 1,
                "maxReplicas": 3 if self.environment == "development" else 10,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 60
                            }
                        }
                    }
                ]
            }
        }
        hpas.append(ai_hpa)
        
        return hpas
    
    def generate_network_policies(self) -> List[Dict[str, Any]]:
        """Generate network security policies"""        policies = []
        
        # Database access policy
        db_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "database-access-policy",
                "namespace": self.namespace
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {
                        "tier": "data"
                    }
                },
                "policyTypes": ["Ingress"],
                "ingress": [
                    {
                        "from": [
                            {
                                "podSelector": {
                                    "matchLabels": {
                                        "component": "backend"
                                    }
                                }
                            },
                            {
                                "podSelector": {
                                    "matchLabels": {
                                        "component": "ai-processing"
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        }
        policies.append(db_policy)
        
        # External access policy
        external_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "external-access-policy",
                "namespace": self.namespace
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {
                        "component": "backend"
                    }
                },
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [],
                        "ports": [
                            {
                                "protocol": "TCP",
                                "port": 8000
                            }
                        ]
                    }
                ],
                "egress": [
                    {
                        "to": [],
                        "ports": [
                            {
                                "protocol": "TCP",
                                "port": 443  # HTTPS
                            },
                            {
                                "protocol": "TCP", 
                                "port": 80   # HTTP
                            }
                        ]
                    }
                ]
            }
        }
        policies.append(external_policy)
        
        return policies
    
    def generate_all_manifests(self, output_dir: str = "./k8s-manifests") -> None:
        """Generate all Kubernetes manifests"""        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        manifests = {
            "00-namespace.yaml": [self.generate_namespace()],
            "01-configmaps.yaml": self.generate_config_maps(),
            "02-secrets.yaml": self.generate_secrets(),
            "03-persistent-volumes.yaml": self.generate_persistent_volumes(),
            "04-deployments.yaml": self.generate_deployments(),
            "05-services.yaml": self.generate_services(),
            "06-ingress.yaml": [self.generate_ingress()],
            "07-hpa.yaml": self.generate_horizontal_pod_autoscaler(),
            "08-network-policies.yaml": self.generate_network_policies()
        }
        
        for filename, resources in manifests.items():
            filepath = Path(output_dir) / filename
            
            with open(filepath, 'w') as f:
                f.write(f"# Kubernetes manifests for IA-Influencer Agent Platform\n")
                f.write(f"# Author: Fahed Mlaiel <mlaiel@live.de>\n")
                f.write(f"# Environment: {self.environment}\n")
                f.write(f"# Generated automatically - DO NOT EDIT MANUALLY\n\n")
                
                for i, resource in enumerate(resources):
                    if i > 0:
                        f.write("---\n")
                    yaml.dump(resource, f, default_flow_style=False, sort_keys=False)
                    f.write("\n")
    
    def get_deployment_script(self) -> str:
        """Generate Kubernetes deployment script"""        return f'''#!/bin/bash
# Kubernetes deployment script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -e

NAMESPACE="{self.namespace}"
ENVIRONMENT="{self.environment}"
MANIFEST_DIR="./k8s-manifests"

echo "🚀 Deploying IA-Influencer Agent to Kubernetes..."
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"
echo "Cluster: {self.cluster_name}"

# Check prerequisites
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed"
    exit 1
fi

# Check cluster connectivity
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi

# Apply manifests in order
echo "📝 Applying Kubernetes manifests..."

for manifest in $MANIFEST_DIR/*.yaml; do
    if [ -f "$manifest" ]; then
        echo "Applying $(basename $manifest)..."
        kubectl apply -f "$manifest"
    fi
done

# Wait for deployments to be ready
echo "⏱️ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment -n $NAMESPACE --all

# Check service status
echo "📊 Checking service status..."
kubectl get all -n $NAMESPACE

# Get external IP (if LoadBalancer)
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🌐 Getting external IP..."
    kubectl get service ia-influencer-api-service -n $NAMESPACE -o jsonpath='{{.status.loadBalancer.ingress[0].ip}}'
fi

echo "✅ IA-Influencer Agent deployed successfully to Kubernetes!"
echo "🔍 Monitor with: kubectl get pods -n $NAMESPACE -w"
echo "📊 Logs: kubectl logs -f deployment/ia-influencer-api -n $NAMESPACE"
'''
    
    def get_monitoring_setup(self) -> str:
        """Generate monitoring and observability setup"""        return '''# Monitoring setup for IA-Influencer Agent Platform
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    
    scrape_configs:
      - job_name: 'ia-influencer-api'
        static_configs:
          - targets: ['ia-influencer-api-service.''' + self.namespace + ''':8000']
        metrics_path: '/metrics'
        scrape_interval: 30s
      
      - job_name: 'ia-ai-services'
        static_configs:
          - targets: ['ia-ai-fingerprinting-service.''' + self.namespace + ''':8001']
        metrics_path: '/metrics'
        scrape_interval: 60s
      
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true

---
# Grafana dashboard ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: ia-influencer-dashboard
  namespace: monitoring
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "IA-Influencer Agent Platform",
        "panels": [
          {
            "title": "API Request Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(http_requests_total[5m])",
                "legendFormat": "{{ method }} {{ status }}"
              }
            ]
          },
          {
            "title": "AI Processing Queue",
            "type": "graph", 
            "targets": [
              {
                "expr": "ai_processing_queue_size",
                "legendFormat": "Queue Size"
              }
            ]
          },
          {
            "title": "Content Protection Stats",
            "type": "stat",
            "targets": [
              {
                "expr": "content_protection_detections_total",
                "legendFormat": "Total Detections"
              }
            ]
          }
        ]
      }
    }
'''
