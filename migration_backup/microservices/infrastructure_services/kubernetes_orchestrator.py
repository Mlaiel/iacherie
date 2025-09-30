"""
🚀 Kubernetes Orchestrator for Ainflue Microservices
🎖️ Multi-Expert Implementation: DevOps + Microservices + Security + Backend Senior

Enterprise Kubernetes deployment with:
- Service mesh integration (Istio)
- Advanced monitoring (Prometheus/Grafana)
- Security policies
- Auto-scaling
- Multi-environment support

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import yaml
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class DeploymentEnvironment(str, Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ServiceType(str, Enum):
    """Microservice types"""
    API_GATEWAY = "api-gateway"
    CONTENT_SERVICE = "content-service"
    AI_SERVICE = "ai-service"
    SECURITY_SERVICE = "security-service"
    BUSINESS_SERVICE = "business-service"
    PLATFORM_SERVICE = "platform-service"
    ANALYTICS_SERVICE = "analytics-service"


@dataclass
class KubernetesResource:
    """Kubernetes resource definition"""
    api_version: str
    kind: str
    metadata: Dict[str, Any]
    spec: Dict[str, Any]
    
    def to_yaml(self) -> str:
        """Convert to YAML format"""
        resource = {
            "apiVersion": self.api_version,
            "kind": self.kind,
            "metadata": self.metadata,
            "spec": self.spec
        }
        return yaml.dump(resource, default_flow_style=False)


@dataclass
class MicroserviceConfig:
    """Microservice configuration"""
    name: str
    service_type: ServiceType
    image: str
    port: int
    environment: DeploymentEnvironment
    replicas: int = 3
    resource_requests: Dict[str, str] = field(default_factory=lambda: {"cpu": "100m", "memory": "128Mi"})
    resource_limits: Dict[str, str] = field(default_factory=lambda: {"cpu": "500m", "memory": "512Mi"})
    env_vars: Dict[str, str] = field(default_factory=dict)
    health_check_path: str = "/health"
    readiness_check_path: str = "/ready"
    service_mesh_enabled: bool = True
    monitoring_enabled: bool = True
    auto_scaling: bool = True
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_utilization: int = 70


class KubernetesOrchestrator:
    """
    🚀 Kubernetes Orchestrator for Enterprise Microservices
    🎖️ Production-ready deployment automation
    """
    
    def __init__(self, environment: DeploymentEnvironment = DeploymentEnvironment.PRODUCTION):
        self.environment = environment
        self.namespace = f"ainflue-{environment.value}"
        self.output_dir = Path(f"kubernetes/{environment.value}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Enterprise configurations
        self.istio_enabled = True
        self.monitoring_enabled = True
        self.security_policies_enabled = True
        
    def generate_namespace(self) -> KubernetesResource:
        """Generate namespace resource"""
        return KubernetesResource(
            api_version="v1",
            kind="Namespace",
            metadata={
                "name": self.namespace,
                "labels": {
                    "environment": self.environment.value,
                    "project": "ainflue",
                    "managed-by": "enterprise-orchestrator"
                },
                "annotations": {
                    "description": f"Ainflue microservices - {self.environment.value}",
                    "contact": "mlaiel@live.de"
                }
            },
            spec={}
        )
    
    def generate_deployment(self, config: MicroserviceConfig) -> KubernetesResource:
        """Generate deployment resource"""
        labels = {
            "app": config.name,
            "service-type": config.service_type.value,
            "environment": config.environment.value,
            "version": "v1"
        }
        
        # Container spec
        container_spec = {
            "name": config.name,
            "image": config.image,
            "ports": [
                {
                    "name": "http",
                    "containerPort": config.port,
                    "protocol": "TCP"
                }
            ],
            "env": [
                {"name": k, "value": v} for k, v in config.env_vars.items()
            ],
            "resources": {
                "requests": config.resource_requests,
                "limits": config.resource_limits
            },
            "livenessProbe": {
                "httpGet": {
                    "path": config.health_check_path,
                    "port": config.port
                },
                "initialDelaySeconds": 30,
                "periodSeconds": 10,
                "timeoutSeconds": 5,
                "failureThreshold": 3
            },
            "readinessProbe": {
                "httpGet": {
                    "path": config.readiness_check_path,
                    "port": config.port
                },
                "initialDelaySeconds": 10,
                "periodSeconds": 5,
                "timeoutSeconds": 3,
                "failureThreshold": 3
            },
            "securityContext": {
                "runAsNonRoot": True,
                "runAsUser": 1001,
                "readOnlyRootFilesystem": True,
                "allowPrivilegeEscalation": False,
                "capabilities": {
                    "drop": ["ALL"]
                }
            }
        }
        
        # Pod template
        pod_template = {
            "metadata": {
                "labels": labels,
                "annotations": {
                    "prometheus.io/scrape": "true" if config.monitoring_enabled else "false",
                    "prometheus.io/port": str(config.port),
                    "prometheus.io/path": "/metrics"
                }
            },
            "spec": {
                "serviceAccountName": f"{config.name}-sa",
                "securityContext": {
                    "fsGroup": 1001,
                    "runAsGroup": 1001
                },
                "containers": [container_spec],
                "restartPolicy": "Always",
                "terminationGracePeriodSeconds": 30
            }
        }
        
        # Add Istio sidecar if enabled
        if config.service_mesh_enabled and self.istio_enabled:
            pod_template["metadata"]["annotations"]["sidecar.istio.io/inject"] = "true"
            pod_template["metadata"]["annotations"]["sidecar.istio.io/proxyCPU"] = "10m"
            pod_template["metadata"]["annotations"]["sidecar.istio.io/proxyMemory"] = "64Mi"
        
        return KubernetesResource(
            api_version="apps/v1",
            kind="Deployment",
            metadata={
                "name": config.name,
                "namespace": self.namespace,
                "labels": labels,
                "annotations": {
                    "deployment.kubernetes.io/revision": "1",
                    "description": f"{config.service_type.value} microservice"
                }
            },
            spec={
                "replicas": config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": config.name,
                        "version": "v1"
                    }
                },
                "template": pod_template,
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxUnavailable": 1,
                        "maxSurge": 1
                    }
                }
            }
        )
    
    def generate_service(self, config: MicroserviceConfig) -> KubernetesResource:
        """Generate service resource"""
        labels = {
            "app": config.name,
            "service-type": config.service_type.value,
            "environment": config.environment.value
        }
        
        return KubernetesResource(
            api_version="v1",
            kind="Service",
            metadata={
                "name": config.name,
                "namespace": self.namespace,
                "labels": labels,
                "annotations": {
                    "service.beta.kubernetes.io/aws-load-balancer-type": "nlb" if self.environment == DeploymentEnvironment.PRODUCTION else "",
                    "prometheus.io/scrape": "true" if config.monitoring_enabled else "false",
                    "prometheus.io/port": str(config.port)
                }
            },
            spec={
                "selector": {
                    "app": config.name
                },
                "ports": [
                    {
                        "name": "http",
                        "port": config.port,
                        "targetPort": config.port,
                        "protocol": "TCP"
                    }
                ],
                "type": "ClusterIP"
            }
        )
    
    def generate_service_account(self, config: MicroserviceConfig) -> KubernetesResource:
        """Generate service account"""
        return KubernetesResource(
            api_version="v1",
            kind="ServiceAccount",
            metadata={
                "name": f"{config.name}-sa",
                "namespace": self.namespace,
                "labels": {
                    "app": config.name,
                    "service-type": config.service_type.value
                }
            },
            spec={}
        )
    
    def generate_hpa(self, config: MicroserviceConfig) -> Optional[KubernetesResource]:
        """Generate Horizontal Pod Autoscaler"""
        if not config.auto_scaling:
            return None
        
        return KubernetesResource(
            api_version="autoscaling/v2",
            kind="HorizontalPodAutoscaler",
            metadata={
                "name": f"{config.name}-hpa",
                "namespace": self.namespace,
                "labels": {
                    "app": config.name,
                    "service-type": config.service_type.value
                }
            },
            spec={
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": config.name
                },
                "minReplicas": config.min_replicas,
                "maxReplicas": config.max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": config.target_cpu_utilization
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
                ],
                "behavior": {
                    "scaleUp": {
                        "stabilizationWindowSeconds": 60,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": 100,
                                "periodSeconds": 15
                            }
                        ]
                    },
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": 10,
                                "periodSeconds": 60
                            }
                        ]
                    }
                }
            }
        )
    
    def generate_istio_virtual_service(self, config: MicroserviceConfig) -> Optional[KubernetesResource]:
        """Generate Istio VirtualService"""
        if not self.istio_enabled or not config.service_mesh_enabled:
            return None
        
        return KubernetesResource(
            api_version="networking.istio.io/v1beta1",
            kind="VirtualService",
            metadata={
                "name": f"{config.name}-vs",
                "namespace": self.namespace,
                "labels": {
                    "app": config.name,
                    "service-type": config.service_type.value
                }
            },
            spec={
                "hosts": [f"{config.name}.{self.namespace}.svc.cluster.local"],
                "http": [
                    {
                        "match": [
                            {
                                "uri": {
                                    "prefix": "/"
                                }
                            }
                        ],
                        "route": [
                            {
                                "destination": {
                                    "host": f"{config.name}.{self.namespace}.svc.cluster.local",
                                    "port": {
                                        "number": config.port
                                    }
                                }
                            }
                        ],
                        "timeout": "30s",
                        "retries": {
                            "attempts": 3,
                            "perTryTimeout": "10s",
                            "retryOn": "gateway-error,connect-failure,refused-stream"
                        }
                    }
                ]
            }
        )
    
    def generate_istio_destination_rule(self, config: MicroserviceConfig) -> Optional[KubernetesResource]:
        """Generate Istio DestinationRule"""
        if not self.istio_enabled or not config.service_mesh_enabled:
            return None
        
        return KubernetesResource(
            api_version="networking.istio.io/v1beta1",
            kind="DestinationRule",
            metadata={
                "name": f"{config.name}-dr",
                "namespace": self.namespace,
                "labels": {
                    "app": config.name,
                    "service-type": config.service_type.value
                }
            },
            spec={
                "host": f"{config.name}.{self.namespace}.svc.cluster.local",
                "trafficPolicy": {
                    "tls": {
                        "mode": "ISTIO_MUTUAL"
                    },
                    "loadBalancer": {
                        "simple": "LEAST_CONN"
                    },
                    "connectionPool": {
                        "tcp": {
                            "maxConnections": 100
                        },
                        "http": {
                            "http1MaxPendingRequests": 50,
                            "http2MaxRequests": 100,
                            "maxRequestsPerConnection": 10,
                            "maxRetries": 3,
                            "connectTimeout": "30s"
                        }
                    },
                    "circuitBreaker": {
                        "consecutiveGatewayErrors": 5,
                        "consecutive5xxErrors": 5,
                        "interval": "30s",
                        "baseEjectionTime": "30s",
                        "maxEjectionPercent": 50
                    }
                }
            }
        )
    
    def generate_network_policy(self, config: MicroserviceConfig) -> Optional[KubernetesResource]:
        """Generate NetworkPolicy for security"""
        if not self.security_policies_enabled:
            return None
        
        # Define allowed traffic based on service type
        ingress_rules = []
        
        if config.service_type == ServiceType.API_GATEWAY:
            # API Gateway can receive traffic from anywhere
            ingress_rules.append({
                "from": [],
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": config.port
                    }
                ]
            })
        else:
            # Other services only accept traffic from API Gateway and same namespace
            ingress_rules.append({
                "from": [
                    {
                        "namespaceSelector": {
                            "matchLabels": {
                                "name": self.namespace
                            }
                        }
                    }
                ],
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": config.port
                    }
                ]
            })
        
        return KubernetesResource(
            api_version="networking.k8s.io/v1",
            kind="NetworkPolicy",
            metadata={
                "name": f"{config.name}-netpol",
                "namespace": self.namespace,
                "labels": {
                    "app": config.name,
                    "service-type": config.service_type.value
                }
            },
            spec={
                "podSelector": {
                    "matchLabels": {
                        "app": config.name
                    }
                },
                "policyTypes": ["Ingress", "Egress"],
                "ingress": ingress_rules,
                "egress": [
                    {
                        "to": [],
                        "ports": [
                            {"protocol": "TCP", "port": 53},
                            {"protocol": "UDP", "port": 53},
                            {"protocol": "TCP", "port": 443},
                            {"protocol": "TCP", "port": 80}
                        ]
                    }
                ]
            }
        )
    
    def generate_pod_disruption_budget(self, config: MicroserviceConfig) -> KubernetesResource:
        """Generate PodDisruptionBudget"""
        min_available = max(1, config.min_replicas // 2)
        
        return KubernetesResource(
            api_version="policy/v1",
            kind="PodDisruptionBudget",
            metadata={
                "name": f"{config.name}-pdb",
                "namespace": self.namespace,
                "labels": {
                    "app": config.name,
                    "service-type": config.service_type.value
                }
            },
            spec={
                "minAvailable": min_available,
                "selector": {
                    "matchLabels": {
                        "app": config.name
                    }
                }
            }
        )
    
    def generate_configmap(self, config: MicroserviceConfig, config_data: Dict[str, str]) -> KubernetesResource:
        """Generate ConfigMap for application configuration"""
        return KubernetesResource(
            api_version="v1",
            kind="ConfigMap",
            metadata={
                "name": f"{config.name}-config",
                "namespace": self.namespace,
                "labels": {
                    "app": config.name,
                    "service-type": config.service_type.value
                }
            },
            spec={
                "data": config_data
            }
        )
    
    def deploy_microservice(self, config: MicroserviceConfig, config_data: Optional[Dict[str, str]] = None) -> List[str]:
        """Deploy a microservice with all necessary resources"""
        resources = []
        
        # Core resources
        resources.append(self.generate_service_account(config))
        resources.append(self.generate_deployment(config))
        resources.append(self.generate_service(config))
        
        # ConfigMap if provided
        if config_data:
            resources.append(self.generate_configmap(config, config_data))
        
        # Auto-scaling
        hpa = self.generate_hpa(config)
        if hpa:
            resources.append(hpa)
        
        # Istio resources
        vs = self.generate_istio_virtual_service(config)
        if vs:
            resources.append(vs)
        
        dr = self.generate_istio_destination_rule(config)
        if dr:
            resources.append(dr)
        
        # Security
        netpol = self.generate_network_policy(config)
        if netpol:
            resources.append(netpol)
        
        resources.append(self.generate_pod_disruption_budget(config))
        
        # Save to files
        saved_files = []
        for resource in resources:
            filename = f"{config.name}-{resource.kind.lower()}.yaml"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(resource.to_yaml())
            
            saved_files.append(str(filepath))
            logger.info(f"Generated {resource.kind} for {config.name}: {filepath}")
        
        return saved_files
    
    def deploy_ainflue_microservices(self) -> Dict[str, List[str]]:
        """Deploy all Ainflue microservices"""
        deployed_files = {}
        
        # Generate namespace first
        namespace_resource = self.generate_namespace()
        namespace_file = self.output_dir / "namespace.yaml"
        with open(namespace_file, 'w') as f:
            f.write(namespace_resource.to_yaml())
        deployed_files["namespace"] = [str(namespace_file)]
        
        # Define microservices configurations
        microservices = [
            MicroserviceConfig(
                name="api-gateway",
                service_type=ServiceType.API_GATEWAY,
                image="ainflue/api-gateway:latest",
                port=8080,
                environment=self.environment,
                replicas=3,
                resource_limits={"cpu": "1000m", "memory": "1Gi"},
                auto_scaling=True,
                min_replicas=2,
                max_replicas=10
            ),
            MicroserviceConfig(
                name="content-upload-service",
                service_type=ServiceType.CONTENT_SERVICE,
                image="ainflue/content-upload:latest",
                port=8001,
                environment=self.environment,
                replicas=3,
                auto_scaling=True
            ),
            MicroserviceConfig(
                name="content-processing-service",
                service_type=ServiceType.CONTENT_SERVICE,
                image="ainflue/content-processing:latest",
                port=8002,
                environment=self.environment,
                replicas=4,
                resource_limits={"cpu": "2000m", "memory": "2Gi"},
                auto_scaling=True,
                max_replicas=15
            ),
            MicroserviceConfig(
                name="ai-inference-service",
                service_type=ServiceType.AI_SERVICE,
                image="ainflue/ai-inference:latest",
                port=8003,
                environment=self.environment,
                replicas=3,
                resource_limits={"cpu": "4000m", "memory": "4Gi"},
                auto_scaling=True,
                target_cpu_utilization=60
            ),
            MicroserviceConfig(
                name="ai-orchestration-service",
                service_type=ServiceType.AI_SERVICE,
                image="ainflue/ai-orchestration:latest",
                port=8004,
                environment=self.environment,
                replicas=2,
                auto_scaling=True
            ),
            MicroserviceConfig(
                name="auth-service",
                service_type=ServiceType.SECURITY_SERVICE,
                image="ainflue/auth-service:latest",
                port=8005,
                environment=self.environment,
                replicas=3,
                auto_scaling=True
            ),
            MicroserviceConfig(
                name="authz-service",
                service_type=ServiceType.SECURITY_SERVICE,
                image="ainflue/authz-service:latest",
                port=8006,
                environment=self.environment,
                replicas=2,
                auto_scaling=True
            ),
            MicroserviceConfig(
                name="creator-workflow-service",
                service_type=ServiceType.BUSINESS_SERVICE,
                image="ainflue/creator-workflow:latest",
                port=8007,
                environment=self.environment,
                replicas=3,
                auto_scaling=True
            ),
            MicroserviceConfig(
                name="platform-sync-service",
                service_type=ServiceType.PLATFORM_SERVICE,
                image="ainflue/platform-sync:latest",
                port=8008,
                environment=self.environment,
                replicas=2,
                auto_scaling=True
            ),
            MicroserviceConfig(
                name="analytics-service",
                service_type=ServiceType.ANALYTICS_SERVICE,
                image="ainflue/analytics:latest",
                port=8009,
                environment=self.environment,
                replicas=2,
                auto_scaling=True
            )
        ]
        
        # Deploy each microservice
        for microservice in microservices:
            files = self.deploy_microservice(microservice)
            deployed_files[microservice.name] = files
        
        logger.info(f"Deployed {len(microservices)} microservices to {self.environment.value}")
        return deployed_files


def main():
    """Main deployment function"""
    # Deploy to all environments
    environments = [
        DeploymentEnvironment.DEVELOPMENT,
        DeploymentEnvironment.STAGING,
        DeploymentEnvironment.PRODUCTION
    ]
    
    all_deployments = {}
    
    for env in environments:
        logger.info(f"Deploying to {env.value} environment...")
        orchestrator = KubernetesOrchestrator(env)
        deployment_files = orchestrator.deploy_ainflue_microservices()
        all_deployments[env.value] = deployment_files
        
        # Generate deployment summary
        total_files = sum(len(files) for files in deployment_files.values())
        logger.info(f"✅ {env.value} deployment complete: {total_files} files generated")
    
    # Generate deployment summary
    summary = {
        "deployment_timestamp": datetime.utcnow().isoformat(),
        "environments": list(all_deployments.keys()),
        "total_microservices": len(all_deployments.get("production", {})) - 1,  # Exclude namespace
        "deployment_files": all_deployments,
        "notes": [
            "All microservices deployed with enterprise security",
            "Istio service mesh integration enabled",
            "Auto-scaling configured for all services",
            "Network policies applied for security",
            "Monitoring and observability enabled"
        ]
    }
    
    # Save deployment summary
    summary_file = Path("kubernetes/deployment_summary.json")
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("🚀 Kubernetes deployment complete!")
    print(f"📋 Summary saved to: {summary_file}")
    print(f"📁 Deployment files in: kubernetes/")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()