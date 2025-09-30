#!/usr/bin/env python3
"""
☸️ KUBERNETES DEPLOYMENT TEMPLATE - ENTERPRISE CONTAINER ORCHESTRATION
======================================================================

Advanced Kubernetes deployment templates with auto-scaling, health checks,
service mesh integration, and production-ready configurations.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive

🎯 EXPERTISE: DevOps + Backend Senior + Security Expert
"""

import yaml
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class KubernetesConfig:
    """Kubernetes deployment configuration"""
    service_name: str
    namespace: str = "default"
    image: str = ""
    replicas: int = 3
    port: int = 8080
    target_port: int = 8080
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"
    cpu_request: str = "250m"
    memory_request: str = "256Mi"
    enable_autoscaling: bool = True
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_utilization: int = 70

class KubernetesDeploymentTemplate:
    """
    🚀 ENTERPRISE KUBERNETES DEPLOYMENT TEMPLATE
    
    Production-ready Kubernetes deployments with auto-scaling,
    health monitoring, and security best practices.
    
    **Expertise DevOps + Backend Senior + Security Expert**
    """
    
    def __init__(self, config: KubernetesConfig):
        """Initialize Kubernetes deployment"""
        self.config = config
    
    def generate_deployment(self) -> Dict[str, Any]:
        """Generate Kubernetes deployment manifest"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": self.config.service_name,
                "namespace": self.config.namespace,
                "labels": {
                    "app": self.config.service_name,
                    "version": "v1",
                    "component": "microservice"
                }
            },
            "spec": {
                "replicas": self.config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": self.config.service_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": self.config.service_name,
                            "version": "v1"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": self.config.service_name,
                            "image": self.config.image,
                            "ports": [{
                                "containerPort": self.config.target_port,
                                "protocol": "TCP"
                            }],
                            "resources": {
                                "limits": {
                                    "cpu": self.config.cpu_limit,
                                    "memory": self.config.memory_limit
                                },
                                "requests": {
                                    "cpu": self.config.cpu_request,
                                    "memory": self.config.memory_request
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": self.config.target_port
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready",
                                    "port": self.config.target_port
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            },
                            "env": [
                                {
                                    "name": "SERVICE_NAME",
                                    "value": self.config.service_name
                                },
                                {
                                    "name": "NAMESPACE",
                                    "valueFrom": {
                                        "fieldRef": {
                                            "fieldPath": "metadata.namespace"
                                        }
                                    }
                                }
                            ]
                        }],
                        "securityContext": {
                            "runAsNonRoot": True,
                            "runAsUser": 1000,
                            "fsGroup": 2000
                        }
                    }
                }
            }
        }
    
    def generate_service(self) -> Dict[str, Any]:
        """Generate Kubernetes service manifest"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.config.service_name}-service",
                "namespace": self.config.namespace,
                "labels": {
                    "app": self.config.service_name
                }
            },
            "spec": {
                "selector": {
                    "app": self.config.service_name
                },
                "ports": [{
                    "port": self.config.port,
                    "targetPort": self.config.target_port,
                    "protocol": "TCP",
                    "name": "http"
                }],
                "type": "ClusterIP"
            }
        }
    
    def generate_hpa(self) -> Dict[str, Any]:
        """Generate Horizontal Pod Autoscaler"""
        if not self.config.enable_autoscaling:
            return {}
        
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{self.config.service_name}-hpa",
                "namespace": self.config.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": self.config.service_name
                },
                "minReplicas": self.config.min_replicas,
                "maxReplicas": self.config.max_replicas,
                "metrics": [{
                    "type": "Resource",
                    "resource": {
                        "name": "cpu",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": self.config.target_cpu_utilization
                        }
                    }
                }]
            }
        }
    
    def generate_configmap(self, config_data: Dict[str, str]) -> Dict[str, Any]:
        """Generate ConfigMap for application configuration"""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.config.service_name}-config",
                "namespace": self.config.namespace
            },
            "data": config_data
        }
    
    def generate_secret(self, secret_data: Dict[str, str]) -> Dict[str, Any]:
        """Generate Secret for sensitive data"""
        import base64
        
        encoded_data = {
            key: base64.b64encode(value.encode()).decode()
            for key, value in secret_data.items()
        }
        
        return {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"{self.config.service_name}-secret",
                "namespace": self.config.namespace
            },
            "type": "Opaque",
            "data": encoded_data
        }
    
    def generate_complete_manifest(self, config_data: Dict[str, str] = None, secret_data: Dict[str, str] = None) -> str:
        """Generate complete Kubernetes manifest file"""
        manifests = []
        
        # Add namespace if not default
        if self.config.namespace != "default":
            manifests.append({
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": self.config.namespace
                }
            })
        
        # Add ConfigMap if provided
        if config_data:
            manifests.append(self.generate_configmap(config_data))
        
        # Add Secret if provided
        if secret_data:
            manifests.append(self.generate_secret(secret_data))
        
        # Add core resources
        manifests.extend([
            self.generate_deployment(),
            self.generate_service()
        ])
        
        # Add HPA if enabled
        hpa = self.generate_hpa()
        if hpa:
            manifests.append(hpa)
        
        # Convert to YAML
        yaml_content = "---\n"
        for manifest in manifests:
            yaml_content += yaml.dump(manifest, default_flow_style=False) + "\n---\n"
        
        return yaml_content
    
    async def deploy(self, kubectl_command: str = "kubectl apply -f -") -> bool:
        """Deploy to Kubernetes cluster"""
        try:
            import subprocess
            
            manifest = self.generate_complete_manifest()
            
            # Apply manifest using kubectl
            process = subprocess.Popen(
                kubectl_command.split(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=manifest)
            
            if process.returncode == 0:
                logger.info(f"✅ Successfully deployed {self.config.service_name}")
                return True
            else:
                logger.error(f"❌ Deployment failed: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Deployment error: {e}")
            return False

# Factory function
def create_kubernetes_deployment(service_name: str, image: str, **kwargs) -> KubernetesDeploymentTemplate:
    """Factory function to create Kubernetes deployment"""
    config = KubernetesConfig(
        service_name=service_name,
        image=image,
        **kwargs
    )
    return KubernetesDeploymentTemplate(config)