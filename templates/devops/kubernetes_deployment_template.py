"""Kubernetes Deployment Template for iacherie Platform
Enterprise-grade container orchestration template for creator economy platform.

⚠️ PROTECTION PROPRIÉTÉ INTELLECTUELLE
© 2025 Fahed Mlaiel <mlaiel@live.de>
Tous droits réservés - Utilisation commerciale interdite sans autorisation écrite explicite

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2024-09-18
"""

import logging
import yaml
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Kubernetes resource types"""
    DEPLOYMENT = "Deployment"
    SERVICE = "Service"
    INGRESS = "Ingress"
    CONFIGMAP = "ConfigMap"
    SECRET = "Secret"
    HPA = "HorizontalPodAutoscaler"
    PVC = "PersistentVolumeClaim"
    NAMESPACE = "Namespace"


class ServiceType(Enum):
    """iacherie platform service types"""
    API_GATEWAY = "api-gateway"
    AUTH_SERVICE = "auth-service"
    CONTENT_PROCESSOR = "content-processor"
    AI_SERVICES = "ai-services"
    MEDIA_PROCESSOR = "media-processor"
    ANALYTICS_SERVICE = "analytics-service"


@dataclass
class KubernetesConfig:
    """Kubernetes deployment configuration"""
    project_name: str
    environment: str
    namespace: str
    image_registry: str = "ghcr.io/mlaiel"
    image_tag: str = "latest"
    
    # Resource limits
    cpu_limit: str = "1000m"
    memory_limit: str = "2Gi"
    cpu_request: str = "500m"
    memory_request: str = "1Gi"
    
    # Scaling
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_percentage: int = 70
    
    # iacherie specific
    enable_ai_processing: bool = True
    enable_gpu_support: bool = False
    enable_media_storage: bool = True
    enable_monitoring: bool = True


class KubernetesDeploymentTemplate:
    """Enterprise Kubernetes Deployment Template for iacherie Platform"""
    
    def __init__(self, config: KubernetesConfig):
        self.config = config
        
    def generate_namespace(self) -> Dict[str, Any]:
        """Generate namespace resource"""
        return {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.config.namespace,
                "labels": {
                    "name": self.config.namespace,
                    "project": self.config.project_name,
                    "environment": self.config.environment,
                    "managed-by": "kubernetes-template"
                }
            }
        }
    
    def generate_deployment(self, service_type: ServiceType) -> Dict[str, Any]:
        """Generate deployment resource for service"""
        service_name = service_type.value
        
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{self.config.project_name}-{service_name}",
                "namespace": self.config.namespace,
                "labels": self._generate_labels(service_name)
            },
            "spec": {
                "replicas": self.config.min_replicas,
                "selector": {
                    "matchLabels": self._generate_selector_labels(service_name)
                },
                "template": {
                    "metadata": {
                        "labels": self._generate_labels(service_name)
                    },
                    "spec": {
                        "containers": [self._generate_container_spec(service_type)],
                        "restartPolicy": "Always",
                        "imagePullSecrets": [{"name": "registry-secret"}]
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
        }
        
        # Add GPU support for AI services
        if service_type == ServiceType.AI_SERVICES and self.config.enable_gpu_support:
            deployment["spec"]["template"]["spec"]["nodeSelector"] = {
                "accelerator": "nvidia-tesla-k80"
            }
            deployment["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"]["nvidia.com/gpu"] = "1"
        
        return deployment
    
    def _generate_container_spec(self, service_type: ServiceType) -> Dict[str, Any]:
        """Generate container specification"""
        service_name = service_type.value
        
        container = {
            "name": service_name,
            "image": f"{self.config.image_registry}/{self.config.project_name}-{service_name}:{self.config.image_tag}",
            "imagePullPolicy": "Always",
            "ports": [{"containerPort": self._get_service_port(service_type)}],
            "env": self._generate_environment_variables(service_type),
            "resources": {
                "requests": {
                    "cpu": self.config.cpu_request,
                    "memory": self.config.memory_request
                },
                "limits": {
                    "cpu": self.config.cpu_limit,
                    "memory": self.config.memory_limit
                }
            },
            "livenessProbe": {
                "httpGet": {
                    "path": "/health",
                    "port": self._get_service_port(service_type)
                },
                "initialDelaySeconds": 30,
                "periodSeconds": 10,
                "timeoutSeconds": 5,
                "failureThreshold": 3
            },
            "readinessProbe": {
                "httpGet": {
                    "path": "/ready",
                    "port": self._get_service_port(service_type)
                },
                "initialDelaySeconds": 10,
                "periodSeconds": 5,
                "timeoutSeconds": 3,
                "failureThreshold": 3
            }
        }
        
        # Add volume mounts for specific services
        if service_type in [ServiceType.CONTENT_PROCESSOR, ServiceType.MEDIA_PROCESSOR]:
            container["volumeMounts"] = [
                {
                    "name": "media-storage",
                    "mountPath": "/app/media"
                }
            ]
        
        return container
    
    def _get_service_port(self, service_type: ServiceType) -> int:
        """Get port for service type"""
        port_mapping = {
            ServiceType.API_GATEWAY: 8000,
            ServiceType.AUTH_SERVICE: 8001,
            ServiceType.CONTENT_PROCESSOR: 8002,
            ServiceType.AI_SERVICES: 8003,
            ServiceType.MEDIA_PROCESSOR: 8004,
            ServiceType.ANALYTICS_SERVICE: 8005
        }
        return port_mapping.get(service_type, 8000)
    
    def _generate_environment_variables(self, service_type: ServiceType) -> List[Dict[str, Any]]:
        """Generate environment variables for service"""
        base_env = [
            {
                "name": "ENVIRONMENT",
                "value": self.config.environment
            },
            {
                "name": "PROJECT_NAME",
                "value": self.config.project_name
            },
            {
                "name": "SERVICE_NAME",
                "value": service_type.value
            },
            {
                "name": "DATABASE_URL",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": f"{self.config.project_name}-secrets",
                        "key": "database-url"
                    }
                }
            },
            {
                "name": "REDIS_URL",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": f"{self.config.project_name}-secrets",
                        "key": "redis-url"
                    }
                }
            },
            {
                "name": "JWT_SECRET",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": f"{self.config.project_name}-secrets",
                        "key": "jwt-secret"
                    }
                }
            }
        ]
        
        # Add service-specific environment variables
        if service_type == ServiceType.AI_SERVICES:
            base_env.extend([
                {
                    "name": "OPENAI_API_KEY",
                    "valueFrom": {
                        "secretKeyRef": {
                            "name": f"{self.config.project_name}-secrets",
                            "key": "openai-api-key"
                        }
                    }
                },
                {
                    "name": "CUDA_VISIBLE_DEVICES",
                    "value": "0" if self.config.enable_gpu_support else ""
                }
            ])
        
        return base_env
    
    def generate_service(self, service_type: ServiceType) -> Dict[str, Any]:
        """Generate service resource"""
        service_name = service_type.value
        
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.config.project_name}-{service_name}",
                "namespace": self.config.namespace,
                "labels": self._generate_labels(service_name)
            },
            "spec": {
                "selector": self._generate_selector_labels(service_name),
                "ports": [
                    {
                        "port": 80,
                        "targetPort": self._get_service_port(service_type),
                        "protocol": "TCP"
                    }
                ],
                "type": "ClusterIP"
            }
        }
    
    def generate_ingress(self) -> Dict[str, Any]:
        """Generate ingress resource for API Gateway"""
        domain = f"{self.config.project_name}-{self.config.environment}.iacherie.com"
        
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{self.config.project_name}-ingress",
                "namespace": self.config.namespace,
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/proxy-body-size": "100m",
                    "nginx.ingress.kubernetes.io/rate-limit": "100"
                }
            },
            "spec": {
                "tls": [
                    {
                        "hosts": [domain],
                        "secretName": f"{self.config.project_name}-tls"
                    }
                ],
                "rules": [
                    {
                        "host": domain,
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": f"{self.config.project_name}-api-gateway",
                                            "port": {"number": 80}
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    
    def generate_configmap(self) -> Dict[str, Any]:
        """Generate configmap resource"""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.config.project_name}-config",
                "namespace": self.config.namespace
            },
            "data": {
                "LOG_LEVEL": "INFO" if self.config.environment == "production" else "DEBUG",
                "MAX_WORKERS": "4",
                "ENABLE_METRICS": "true",
                "CORS_ORIGINS": "*" if self.config.environment == "development" else "https://iacherie.com",
                "FILE_UPLOAD_MAX_SIZE": "100MB",
                "AI_MODEL_CACHE_SIZE": "1GB",
                "MEDIA_PROCESSING_TIMEOUT": "300",
                "CREATOR_ANALYTICS_ENABLED": "true",
                "CONTENT_MODERATION_ENABLED": "true"
            }
        }
    
    def generate_secret_template(self) -> Dict[str, Any]:
        """Generate secret template (values should be base64 encoded)"""
        return {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"{self.config.project_name}-secrets",
                "namespace": self.config.namespace
            },
            "type": "Opaque",
            "data": {
                "database-url": "cG9zdGdyZXNxbDovL3VzZXI6cGFzc0Bsb2NhbGhvc3Q6NTQzMi9kYg==",  # Example
                "redis-url": "cmVkaXM6Ly9sb2NhbGhvc3Q6NjM3OS8w",  # Example
                "jwt-secret": "eW91ci1qd3Qtc2VjcmV0LWtleQ==",  # Example
                "openai-api-key": "eW91ci1vcGVuYWkta2V5",  # Example
                "stripe-secret-key": "eW91ci1zdHJpcGUta2V5",  # Example
                "aws-access-key-id": "eW91ci1hd3MtYWNjZXNzLWtleQ==",  # Example
                "aws-secret-access-key": "eW91ci1hd3Mtc2VjcmV0LWtleQ=="  # Example
            }
        }
    
    def generate_hpa(self, service_type: ServiceType) -> Dict[str, Any]:
        """Generate horizontal pod autoscaler"""
        service_name = service_type.value
        
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{self.config.project_name}-{service_name}-hpa",
                "namespace": self.config.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": f"{self.config.project_name}-{service_name}"
                },
                "minReplicas": self.config.min_replicas,
                "maxReplicas": self.config.max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": self.config.target_cpu_percentage
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
    
    def generate_pvc(self) -> Dict[str, Any]:
        """Generate persistent volume claim for media storage"""
        return {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": f"{self.config.project_name}-media-storage",
                "namespace": self.config.namespace
            },
            "spec": {
                "accessModes": ["ReadWriteMany"],
                "storageClassName": "efs-sc",
                "resources": {
                    "requests": {
                        "storage": "100Gi"
                    }
                }
            }
        }
    
    def _generate_labels(self, service_name: str) -> Dict[str, str]:
        """Generate common labels"""
        return {
            "app": f"{self.config.project_name}-{service_name}",
            "project": self.config.project_name,
            "environment": self.config.environment,
            "service": service_name,
            "version": self.config.image_tag,
            "managed-by": "kubernetes-template"
        }
    
    def _generate_selector_labels(self, service_name: str) -> Dict[str, str]:
        """Generate selector labels"""
        return {
            "app": f"{self.config.project_name}-{service_name}",
            "service": service_name
        }
    
    def generate_monitoring_resources(self) -> List[Dict[str, Any]]:
        """Generate monitoring resources (ServiceMonitor for Prometheus)"""
        if not self.config.enable_monitoring:
            return []
        
        return [
            {
                "apiVersion": "monitoring.coreos.com/v1",
                "kind": "ServiceMonitor",
                "metadata": {
                    "name": f"{self.config.project_name}-metrics",
                    "namespace": self.config.namespace,
                    "labels": {
                        "app": self.config.project_name,
                        "release": "prometheus"
                    }
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "project": self.config.project_name
                        }
                    },
                    "endpoints": [
                        {
                            "port": "metrics",
                            "path": "/metrics",
                            "interval": "30s"
                        }
                    ]
                }
            }
        ]
    
    def generate_complete_manifests(self) -> List[Dict[str, Any]]:
        """Generate complete Kubernetes manifests for iacherie platform"""
        manifests = []
        
        # Namespace
        manifests.append(self.generate_namespace())
        
        # ConfigMap and Secrets
        manifests.append(self.generate_configmap())
        manifests.append(self.generate_secret_template())
        
        # Storage
        if self.config.enable_media_storage:
            manifests.append(self.generate_pvc())
        
        # Services
        services = [
            ServiceType.API_GATEWAY,
            ServiceType.AUTH_SERVICE,
            ServiceType.CONTENT_PROCESSOR
        ]
        
        if self.config.enable_ai_processing:
            services.append(ServiceType.AI_SERVICES)
        
        for service_type in services:
            # Deployment
            manifests.append(self.generate_deployment(service_type))
            
            # Service
            manifests.append(self.generate_service(service_type))
            
            # HPA
            manifests.append(self.generate_hpa(service_type))
        
        # Ingress
        manifests.append(self.generate_ingress())
        
        # Monitoring
        manifests.extend(self.generate_monitoring_resources())
        
        return manifests
    
    def save_manifests(self, output_dir: str) -> None:
        """Save manifests to directory"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        manifests = self.generate_complete_manifests()
        
        # Save each manifest type to separate files
        grouped_manifests = {}
        for manifest in manifests:
            kind = manifest["kind"].lower()
            if kind not in grouped_manifests:
                grouped_manifests[kind] = []
            grouped_manifests[kind].append(manifest)
        
        for kind, manifest_list in grouped_manifests.items():
            with open(output_path / f"{kind}.yaml", 'w') as f:
                yaml.dump_all(manifest_list, f, default_flow_style=False, indent=2)
        
        logger.info(f"Kubernetes manifests saved to {output_dir}")


# Example usage
def create_production_config() -> KubernetesConfig:
    """Create production configuration"""
    return KubernetesConfig(
        project_name="iacherie-platform",
        environment="production",
        namespace="iacherie-prod",
        image_tag="v1.0.0",
        cpu_limit="2000m",
        memory_limit="4Gi",
        cpu_request="1000m",
        memory_request="2Gi",
        min_replicas=3,
        max_replicas=20,
        enable_ai_processing=True,
        enable_gpu_support=True,
        enable_media_storage=True,
        enable_monitoring=True
    )


def create_development_config() -> KubernetesConfig:
    """Create development configuration"""
    return KubernetesConfig(
        project_name="iacherie-dev",
        environment="development",
        namespace="iacherie-dev",
        image_tag="latest",
        cpu_limit="500m",
        memory_limit="1Gi",
        cpu_request="250m",
        memory_request="512Mi",
        min_replicas=1,
        max_replicas=3,
        enable_ai_processing=False,
        enable_gpu_support=False,
        enable_media_storage=True,
        enable_monitoring=False
    )


if __name__ == "__main__":
    prod_config = create_production_config()
    template = KubernetesDeploymentTemplate(prod_config)
    
    print("Kubernetes Deployment Template for iacherie Platform")
    print("Configuration:")
    print(f"- Environment: {prod_config.environment}")
    print(f"- Namespace: {prod_config.namespace}")
    print(f"- Min/Max Replicas: {prod_config.min_replicas}/{prod_config.max_replicas}")
    print(f"- AI Processing: {prod_config.enable_ai_processing}")
    print(f"- GPU Support: {prod_config.enable_gpu_support}")
    print(f"- Monitoring: {prod_config.enable_monitoring}")
