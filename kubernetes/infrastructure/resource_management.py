"""Resource Quotas and Limit Ranges Manager
========================================

Kubernetes resource management with quotas and limits per namespace
for the Ainflue platform resource governance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """Environment types for resource allocation"""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"


class WorkloadType(Enum):
    """Workload types for resource optimization"""
    API_GATEWAY = "api-gateway"
    BACKEND = "backend"
    AI_PROCESSING = "ai-processing"
    DATABASE = "database"
    STORAGE = "storage"
    MONITORING = "monitoring"
    BATCH = "batch"


@dataclass
class ResourceSpec:
    """Resource specification"""
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "128Mi"
    memory_limit: str = "512Mi"
    storage_request: str = "1Gi"
    storage_limit: str = "10Gi"


@dataclass
class QuotaSpec:
    """Resource quota specification"""
    namespace: str
    environment: EnvironmentType
    cpu_requests: str = "4"
    cpu_limits: str = "8"
    memory_requests: str = "8Gi"
    memory_limits: str = "16Gi"
    storage_requests: str = "100Gi"
    pods: str = "50"
    services: str = "20"
    secrets: str = "50"
    configmaps: str = "50"
    persistentvolumeclaims: str = "20"


class ResourceManager:
    """Manages Kubernetes Resource Quotas and Limit Ranges"""
    
    def __init__(self, base_namespace -> None: str = "ia-influencer") -> None:
        self.base_namespace = base_namespace
        self.workload_specs = self._initialize_workload_specs()
        self.environment_quotas = self._initialize_environment_quotas()
    
    def _initialize_workload_specs(self) -> Dict[WorkloadType, ResourceSpec]:
        """Initialize resource specifications for different workload types"""
        return {
            WorkloadType.API_GATEWAY: ResourceSpec(
                cpu_request="200m",
                cpu_limit="1000m",
                memory_request="256Mi",
                memory_limit="1Gi",
                storage_request="1Gi",
                storage_limit="5Gi"
            ),
            WorkloadType.BACKEND: ResourceSpec(
                cpu_request="300m",
                cpu_limit="1500m",
                memory_request="512Mi",
                memory_limit="2Gi",
                storage_request="2Gi",
                storage_limit="10Gi"
            ),
            WorkloadType.AI_PROCESSING: ResourceSpec(
                cpu_request="1000m",
                cpu_limit="4000m",
                memory_request="2Gi",
                memory_limit="8Gi",
                storage_request="5Gi",
                storage_limit="50Gi"
            ),
            WorkloadType.DATABASE: ResourceSpec(
                cpu_request="500m",
                cpu_limit="2000m",
                memory_request="1Gi",
                memory_limit="4Gi",
                storage_request="10Gi",
                storage_limit="100Gi"
            ),
            WorkloadType.STORAGE: ResourceSpec(
                cpu_request="200m",
                cpu_limit="1000m",
                memory_request="512Mi",
                memory_limit="2Gi",
                storage_request="20Gi",
                storage_limit="200Gi"
            ),
            WorkloadType.MONITORING: ResourceSpec(
                cpu_request="300m",
                cpu_limit="1000m",
                memory_request="512Mi",
                memory_limit="2Gi",
                storage_request="5Gi",
                storage_limit="50Gi"
            ),
            WorkloadType.BATCH: ResourceSpec(
                cpu_request="100m",
                cpu_limit="2000m",
                memory_request="256Mi",
                memory_limit="4Gi",
                storage_request="1Gi",
                storage_limit="20Gi"
            )
        }
    
    def _initialize_environment_quotas(self) -> Dict[EnvironmentType, QuotaSpec]:
        """Initialize resource quotas for different environments"""
        return {
            EnvironmentType.PRODUCTION: QuotaSpec(
                namespace=self.base_namespace,
                environment=EnvironmentType.PRODUCTION,
                cpu_requests="20",
                cpu_limits="40",
                memory_requests="40Gi",
                memory_limits="80Gi",
                storage_requests="1Ti",
                pods="100",
                services="50",
                secrets="100",
                configmaps="100",
                persistentvolumeclaims="50"
            ),
            EnvironmentType.STAGING: QuotaSpec(
                namespace=f"{self.base_namespace}-staging",
                environment=EnvironmentType.STAGING,
                cpu_requests="10",
                cpu_limits="20",
                memory_requests="20Gi",
                memory_limits="40Gi",
                storage_requests="500Gi",
                pods="50",
                services="25",
                secrets="50",
                configmaps="50",
                persistentvolumeclaims="25"
            ),
            EnvironmentType.DEVELOPMENT: QuotaSpec(
                namespace=f"{self.base_namespace}-dev",
                environment=EnvironmentType.DEVELOPMENT,
                cpu_requests="5",
                cpu_limits="10",
                memory_requests="10Gi",
                memory_limits="20Gi",
                storage_requests="200Gi",
                pods="25",
                services="15",
                secrets="25",
                configmaps="25",
                persistentvolumeclaims="15"
            ),
            EnvironmentType.TESTING: QuotaSpec(
                namespace=f"{self.base_namespace}-test",
                environment=EnvironmentType.TESTING,
                cpu_requests="2",
                cpu_limits="5",
                memory_requests="4Gi",
                memory_limits="8Gi",
                storage_requests="50Gi",
                pods="15",
                services="10",
                secrets="15",
                configmaps="15",
                persistentvolumeclaims="10"
            )
        }
    
    def create_resource_quota(self, quota_spec: QuotaSpec) -> Dict[str, Any]:
        """Create ResourceQuota manifest"""
        return {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {
                "name": f"{quota_spec.namespace}-quota",
                "namespace": quota_spec.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "resource-quota",
                    "environment": quota_spec.environment.value
                },
                "annotations": {
                    "description": f"Resource quota for {quota_spec.environment.value} environment"
                }
            },
            "spec": {
                "hard": {
                    "requests.cpu": quota_spec.cpu_requests,
                    "limits.cpu": quota_spec.cpu_limits,
                    "requests.memory": quota_spec.memory_requests,
                    "limits.memory": quota_spec.memory_limits,
                    "requests.storage": quota_spec.storage_requests,
                    "pods": quota_spec.pods,
                    "services": quota_spec.services,
                    "secrets": quota_spec.secrets,
                    "configmaps": quota_spec.configmaps,
                    "persistentvolumeclaims": quota_spec.persistentvolumeclaims,
                    "count/deployments.apps": "20",
                    "count/replicasets.apps": "30",
                    "count/statefulsets.apps": "10",
                    "count/jobs.batch": "20",
                    "count/cronjobs.batch": "10",
                    "count/ingresses.networking.k8s.io": "10",
                    "count/networkpolicies.networking.k8s.io": "20"
                }
            }
        }
    
    def create_limit_range(self, namespace: str, 
                          workload_type: WorkloadType) -> Dict[str, Any]:
        """Create LimitRange manifest for specific workload type"""
        spec = self.workload_specs[workload_type]
        
        return {
            "apiVersion": "v1",
            "kind": "LimitRange",
            "metadata": {
                "name": f"{workload_type.value}-limits",
                "namespace": namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "limit-range",
                    "workload-type": workload_type.value
                },
                "annotations": {
                    "description": f"Limit range for {workload_type.value} workloads"
                }
            },
            "spec": {
                "limits": [
                    {
                        "type": "Container",
                        "default": {
                            "cpu": spec.cpu_limit,
                            "memory": spec.memory_limit,
                            "ephemeral-storage": spec.storage_limit
                        },
                        "defaultRequest": {
                            "cpu": spec.cpu_request,
                            "memory": spec.memory_request,
                            "ephemeral-storage": spec.storage_request
                        },
                        "max": {
                            "cpu": "8000m",
                            "memory": "16Gi",
                            "ephemeral-storage": "100Gi"
                        },
                        "min": {
                            "cpu": "10m",
                            "memory": "64Mi",
                            "ephemeral-storage": "100Mi"
                        }
                    },
                    {
                        "type": "Pod",
                        "max": {
                            "cpu": "16000m",
                            "memory": "32Gi",
                            "ephemeral-storage": "200Gi"
                        }
                    },
                    {
                        "type": "PersistentVolumeClaim",
                        "max": {
                            "storage": "1Ti"
                        },
                        "min": {
                            "storage": "1Gi"
                        }
                    }
                ]
            }
        }
    
    def create_default_limit_range(self, namespace: str) -> Dict[str, Any]:
        """Create default LimitRange for namespace"""
        return {
            "apiVersion": "v1",
            "kind": "LimitRange",
            "metadata": {
                "name": "default-limits",
                "namespace": namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "limit-range",
                    "workload-type": "default"
                },
                "annotations": {
                    "description": "Default limit range for all workloads"
                }
            },
            "spec": {
                "limits": [
                    {
                        "type": "Container",
                        "default": {
                            "cpu": "500m",
                            "memory": "512Mi",
                            "ephemeral-storage": "2Gi"
                        },
                        "defaultRequest": {
                            "cpu": "100m",
                            "memory": "128Mi",
                            "ephemeral-storage": "1Gi"
                        },
                        "max": {
                            "cpu": "4000m",
                            "memory": "8Gi",
                            "ephemeral-storage": "50Gi"
                        },
                        "min": {
                            "cpu": "10m",
                            "memory": "64Mi",
                            "ephemeral-storage": "100Mi"
                        }
                    },
                    {
                        "type": "Pod",
                        "max": {
                            "cpu": "8000m",
                            "memory": "16Gi",
                            "ephemeral-storage": "100Gi"
                        }
                    },
                    {
                        "type": "PersistentVolumeClaim",
                        "max": {
                            "storage": "500Gi"
                        },
                        "min": {
                            "storage": "1Gi"
                        }
                    }
                ]
            }
        }
    
    def create_priority_class(self, name: str, value: int, 
                            description: str = "") -> Dict[str, Any]:
        """Create PriorityClass for workload prioritization"""
        return {
            "apiVersion": "scheduling.k8s.io/v1",
            "kind": "PriorityClass",
            "metadata": {
                "name": name,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "priority-class"
                }
            },
            "value": value,
            "globalDefault": False,
            "description": description or f"Priority class {name} with value {value}"
        }
    
    def create_horizontal_pod_autoscaler(self, name: str, namespace: str,
                                       target_deployment: str,
                                       min_replicas: int = 2,
                                       max_replicas: int = 10,
                                       target_cpu_percent: int = 70) -> Dict[str, Any]:
        """Create HorizontalPodAutoscaler for automatic scaling"""
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": name,
                "namespace": namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "hpa"
                }
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": target_deployment
                },
                "minReplicas": min_replicas,
                "maxReplicas": max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": target_cpu_percent
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
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": 10,
                                "periodSeconds": 60
                            }
                        ]
                    },
                    "scaleUp": {
                        "stabilizationWindowSeconds": 60,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": 50,
                                "periodSeconds": 60
                            }
                        ]
                    }
                }
            }
        }
    
    def generate_all_resource_manifests(self) -> Dict[str, str]:
        """Generate all resource management manifests"""
        manifests = {}
        
        # Resource quotas for all environments
        for env_type, quota_spec in self.environment_quotas.items():
            quota = self.create_resource_quota(quota_spec)
            manifests[f"{env_type.value}-resource-quota"] = yaml.dump(quota, default_flow_style=False)
            
            # Default limit range for each namespace
            default_limits = self.create_default_limit_range(quota_spec.namespace)
            manifests[f"{env_type.value}-default-limits"] = yaml.dump(default_limits, default_flow_style=False)
            
            # Workload-specific limit ranges for production
            if env_type == EnvironmentType.PRODUCTION:
                for workload_type in WorkloadType:
                    workload_limits = self.create_limit_range(quota_spec.namespace, workload_type)
                    manifests[f"{workload_type.value}-limits"] = yaml.dump(workload_limits, default_flow_style=False)
        
        # Priority classes
        priority_classes = [
            ("critical", 1000, "Critical system workloads"),
            ("high", 500, "High priority application workloads"),
            ("medium", 100, "Medium priority workloads"),
            ("low", 10, "Low priority batch workloads")
        ]
        
        for name, value, description in priority_classes:
            priority_class = self.create_priority_class(f"ia-influencer-{name}", value, description)
            manifests[f"priority-class-{name}"] = yaml.dump(priority_class, default_flow_style=False)
        
        # Horizontal Pod Autoscalers for main workloads
        hpa_configs = [
            ("api-gateway-hpa", "api-gateway", 3, 15, 70),
            ("backend-hpa", "backend", 3, 20, 70),
            ("ai-processing-hpa", "ai-processing", 2, 10, 80),
            ("storage-hpa", "storage", 2, 8, 75)
        ]
        
        for hpa_name, deployment, min_rep, max_rep, cpu_target in hpa_configs:
            hpa = self.create_horizontal_pod_autoscaler(
                hpa_name, self.base_namespace, deployment, min_rep, max_rep, cpu_target
            )
            manifests[hpa_name] = yaml.dump(hpa, default_flow_style=False)
        
        return manifests
    
    def save_manifests_to_files(self, output_dir -> None: str = "./k8s-manifests/resource-management") -> None:
        """Save all resource management manifests to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        manifests = self.generate_all_resource_manifests()
        
        for name, manifest in manifests.items():
            file_path = os.path.join(output_dir, f"{name}.yaml")
            with open(file_path, 'w') as f:
                f.write(manifest)
            logger.info(f"Resource management manifest saved: {file_path}")
        
        return len(manifests)


# Export main functionality
__all__ = ['ResourceManager', 'ResourceSpec', 'QuotaSpec', 'EnvironmentType', 'WorkloadType']