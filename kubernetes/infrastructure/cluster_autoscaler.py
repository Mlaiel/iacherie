"""Cluster Autoscaling with Intelligent Policies
==============================================

Kubernetes cluster autoscaling configuration with intelligent policies
for the Ainflue platform optimal resource utilization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CloudProvider(Enum):
    """Cloud provider types"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class NodePoolType(Enum):
    """Node pool types for different workloads"""
    GENERAL = "general"
    COMPUTE_OPTIMIZED = "compute-optimized"
    MEMORY_OPTIMIZED = "memory-optimized"
    GPU_ENABLED = "gpu-enabled"
    SPOT_INSTANCES = "spot-instances"


@dataclass
class NodePoolConfig:
    """Node pool configuration"""
    name: str
    pool_type: NodePoolType
    instance_types: List[str]
    min_size: int = 0
    max_size: int = 10
    desired_size: int = 2
    labels: Dict[str, str] = field(default_factory=dict)
    taints: List[Dict[str, str]] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class AutoscalingConfig:
    """Cluster autoscaling configuration"""
    cloud_provider: CloudProvider = CloudProvider.AWS
    cluster_name: str = "ia-influencer-cluster"
    region: str = "eu-central-1"
    scale_down_enabled: bool = True
    scale_down_delay_after_add: str = "10m"
    scale_down_unneeded_time: str = "10m"
    scale_down_utilization_threshold: float = 0.5
    max_node_provision_time: str = "15m"
    node_pools: List[NodePoolConfig] = field(default_factory=list)


class ClusterAutoscalerManager:
    """Manages cluster autoscaling configuration"""
    
    def __init__(self, config -> None: AutoscalingConfig) -> None:
        self.config = config
        self._initialize_default_node_pools()
    
    def _initialize_default_node_pools(self) -> None:
        """Initialize default node pools if none provided"""
        if not self.config.node_pools:
            self.config.node_pools = self._create_default_node_pools()
    
    def _create_default_node_pools(self) -> List[NodePoolConfig]:
        """Create default node pool configurations"""
        if self.config.cloud_provider == CloudProvider.AWS:
            return [
                NodePoolConfig(
                    name="general-purpose",
                    pool_type=NodePoolType.GENERAL,
                    instance_types=["t3.medium", "t3.large", "t3.xlarge"],
                    min_size=2,
                    max_size=20,
                    desired_size=3,
                    labels={
                        "node.kubernetes.io/instance-type": "general",
                        "workload-type": "general"
                    },
                    tags={
                        "k8s.io/cluster-autoscaler/enabled": "true",
                        "k8s.io/cluster-autoscaler/ia-influencer-cluster": "owned"
                    }
                ),
                NodePoolConfig(
                    name="compute-optimized",
                    pool_type=NodePoolType.COMPUTE_OPTIMIZED,
                    instance_types=["c5.large", "c5.xlarge", "c5.2xlarge"],
                    min_size=0,
                    max_size=10,
                    desired_size=1,
                    labels={
                        "node.kubernetes.io/instance-type": "compute-optimized",
                        "workload-type": "cpu-intensive"
                    },
                    taints=[
                        {
                            "key": "workload-type",
                            "value": "cpu-intensive",
                            "effect": "NoSchedule"
                        }
                    ],
                    tags={
                        "k8s.io/cluster-autoscaler/enabled": "true",
                        "k8s.io/cluster-autoscaler/ia-influencer-cluster": "owned"
                    }
                ),
                NodePoolConfig(
                    name="memory-optimized",
                    pool_type=NodePoolType.MEMORY_OPTIMIZED,
                    instance_types=["r5.large", "r5.xlarge", "r5.2xlarge"],
                    min_size=0,
                    max_size=8,
                    desired_size=1,
                    labels={
                        "node.kubernetes.io/instance-type": "memory-optimized",
                        "workload-type": "memory-intensive"
                    },
                    taints=[
                        {
                            "key": "workload-type",
                            "value": "memory-intensive",
                            "effect": "NoSchedule"
                        }
                    ],
                    tags={
                        "k8s.io/cluster-autoscaler/enabled": "true",
                        "k8s.io/cluster-autoscaler/ia-influencer-cluster": "owned"
                    }
                ),
                NodePoolConfig(
                    name="gpu-enabled",
                    pool_type=NodePoolType.GPU_ENABLED,
                    instance_types=["g4dn.xlarge", "g4dn.2xlarge"],
                    min_size=0,
                    max_size=5,
                    desired_size=0,
                    labels={
                        "node.kubernetes.io/instance-type": "gpu-enabled",
                        "workload-type": "ai-ml",
                        "accelerator": "nvidia-tesla-t4"
                    },
                    taints=[
                        {
                            "key": "workload-type",
                            "value": "ai-ml",
                            "effect": "NoSchedule"
                        },
                        {
                            "key": "nvidia.com/gpu",
                            "value": "true",
                            "effect": "NoSchedule"
                        }
                    ],
                    tags={
                        "k8s.io/cluster-autoscaler/enabled": "true",
                        "k8s.io/cluster-autoscaler/ia-influencer-cluster": "owned"
                    }
                ),
                NodePoolConfig(
                    name="spot-instances",
                    pool_type=NodePoolType.SPOT_INSTANCES,
                    instance_types=["m5.large", "m5.xlarge", "m5a.large", "m5a.xlarge"],
                    min_size=0,
                    max_size=15,
                    desired_size=2,
                    labels={
                        "node.kubernetes.io/instance-type": "spot",
                        "workload-type": "batch-processing",
                        "capacity-type": "spot"
                    },
                    taints=[
                        {
                            "key": "capacity-type",
                            "value": "spot",
                            "effect": "NoSchedule"
                        }
                    ],
                    tags={
                        "k8s.io/cluster-autoscaler/enabled": "true",
                        "k8s.io/cluster-autoscaler/ia-influencer-cluster": "owned"
                    }
                )
            ]
        
        # Default node pools for other providers
        return [
            NodePoolConfig(
                name="default",
                pool_type=NodePoolType.GENERAL,
                instance_types=["standard"],
                min_size=2,
                max_size=10,
                desired_size=3
            )
        ]
    
    def create_cluster_autoscaler_service_account(self) -> List[Dict[str, Any]]:
        """Create service account for cluster autoscaler"""
        return [
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": "cluster-autoscaler",
                    "namespace": "kube-system",
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "cluster-autoscaler"
                    },
                    "annotations": {
                        "eks.amazonaws.com/role-arn": f"arn:aws:iam::ACCOUNT:role/AmazonEKSClusterAutoscalerRole"
                    } if self.config.cloud_provider == CloudProvider.AWS else {}
                }
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "name": "cluster-autoscaler",
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "cluster-autoscaler"
                    }
                },
                "rules": [
                    {
                        "apiGroups": [""],
                        "resources": ["events", "endpoints"],
                        "verbs": ["create", "patch"]
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["pods/eviction"],
                        "verbs": ["create"]
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["pods/status"],
                        "verbs": ["update"]
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["endpoints"],
                        "resourceNames": ["cluster-autoscaler"],
                        "verbs": ["get", "update"]
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["nodes"],
                        "verbs": ["watch", "list", "get", "update"]
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["pods", "services", "replicationcontrollers", "persistentvolumeclaims", "persistentvolumes"],
                        "verbs": ["watch", "list", "get"]
                    },
                    {
                        "apiGroups": ["extensions"],
                        "resources": ["replicasets", "daemonsets"],
                        "verbs": ["watch", "list", "get"]
                    },
                    {
                        "apiGroups": ["policy"],
                        "resources": ["poddisruptionbudgets"],
                        "verbs": ["watch", "list"]
                    },
                    {
                        "apiGroups": ["apps"],
                        "resources": ["statefulsets", "replicasets", "daemonsets"],
                        "verbs": ["watch", "list", "get"]
                    },
                    {
                        "apiGroups": ["storage.k8s.io"],
                        "resources": ["storageclasses", "csinodes", "csidrivers", "csistoragecapacities"],
                        "verbs": ["watch", "list", "get"]
                    },
                    {
                        "apiGroups": ["batch", "extensions"],
                        "resources": ["jobs"],
                        "verbs": ["get", "list", "watch", "patch"]
                    },
                    {
                        "apiGroups": ["coordination.k8s.io"],
                        "resources": ["leases"],
                        "verbs": ["create"]
                    },
                    {
                        "apiGroups": ["coordination.k8s.io"],
                        "resourceNames": ["cluster-autoscaler"],
                        "resources": ["leases"],
                        "verbs": ["get", "update"]
                    }
                ]
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "Role",
                "metadata": {
                    "name": "cluster-autoscaler",
                    "namespace": "kube-system",
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "cluster-autoscaler"
                    }
                },
                "rules": [
                    {
                        "apiGroups": [""],
                        "resources": ["configmaps"],
                        "verbs": ["create", "list", "watch"]
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["configmaps"],
                        "resourceNames": ["cluster-autoscaler-status", "cluster-autoscaler-priority-expander"],
                        "verbs": ["delete", "get", "update", "watch"]
                    }
                ]
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRoleBinding",
                "metadata": {
                    "name": "cluster-autoscaler",
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "cluster-autoscaler"
                    }
                },
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "ClusterRole",
                    "name": "cluster-autoscaler"
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": "cluster-autoscaler",
                        "namespace": "kube-system"
                    }
                ]
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "RoleBinding",
                "metadata": {
                    "name": "cluster-autoscaler",
                    "namespace": "kube-system",
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "cluster-autoscaler"
                    }
                },
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "Role",
                    "name": "cluster-autoscaler"
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": "cluster-autoscaler",
                        "namespace": "kube-system"
                    }
                ]
            }
        ]
    
    def create_cluster_autoscaler_deployment(self) -> Dict[str, Any]:
        """Create cluster autoscaler deployment"""
        # Build command arguments
        command_args = [
            "/cluster-autoscaler",
            f"--v=4",
            f"--stderrthreshold=info",
            f"--cloud-provider={self.config.cloud_provider.value}",
            f"--skip-nodes-with-local-storage=false",
            f"--expander=priority",
            f"--node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/{self.config.cluster_name}",
            f"--balance-similar-node-groups",
            f"--skip-nodes-with-system-pods=false",
            f"--scale-down-enabled={str(self.config.scale_down_enabled).lower()}",
            f"--scale-down-delay-after-add={self.config.scale_down_delay_after_add}",
            f"--scale-down-unneeded-time={self.config.scale_down_unneeded_time}",
            f"--scale-down-utilization-threshold={self.config.scale_down_utilization_threshold}",
            f"--max-node-provision-time={self.config.max_node_provision_time}",
            "--new-pod-scale-up-delay=10s",
            "--scan-interval=10s"
        ]
        
        # Add node group configurations
        for pool in self.config.node_pools:
            command_args.append(f"--nodes={pool.min_size}:{pool.max_size}:{pool.name}")
        
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "cluster-autoscaler",
                "namespace": "kube-system",
                "labels": {
                    "app": "cluster-autoscaler",
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "cluster-autoscaler"
                }
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "cluster-autoscaler"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "cluster-autoscaler",
                            "app.kubernetes.io/name": "ia-influencer",
                            "app.kubernetes.io/component": "cluster-autoscaler"
                        },
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": "8085"
                        }
                    },
                    "spec": {
                        "priorityClassName": "system-cluster-critical",
                        "securityContext": {
                            "runAsNonRoot": True,
                            "runAsUser": 65534,
                            "fsGroup": 65534
                        },
                        "serviceAccountName": "cluster-autoscaler",
                        "containers": [
                            {
                                "name": "cluster-autoscaler",
                                "image": "k8s.gcr.io/autoscaling/cluster-autoscaler:v1.27.3",
                                "command": command_args,
                                "resources": {
                                    "limits": {
                                        "cpu": "100m",
                                        "memory": "600Mi"
                                    },
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "600Mi"
                                    }
                                },
                                "env": [
                                    {
                                        "name": "AWS_REGION",
                                        "value": self.config.region
                                    }
                                ] if self.config.cloud_provider == CloudProvider.AWS else [],
                                "ports": [
                                    {
                                        "name": "http",
                                        "containerPort": 8085,
                                        "protocol": "TCP"
                                    }
                                ],
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health-check",
                                        "port": 8085
                                    },
                                    "periodSeconds": 60,
                                    "timeoutSeconds": 5
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/health-check",
                                        "port": 8085
                                    },
                                    "periodSeconds": 10,
                                    "timeoutSeconds": 5
                                }
                            }
                        ],
                        "nodeSelector": {
                            "kubernetes.io/os": "linux"
                        },
                        "tolerations": [
                            {
                                "key": "CriticalAddonsOnly",
                                "operator": "Exists"
                            },
                            {
                                "key": "node-role.kubernetes.io/control-plane",
                                "effect": "NoSchedule"
                            }
                        ]
                    }
                }
            }
        }
    
    def create_priority_expander_configmap(self) -> Dict[str, Any]:
        """Create priority expander configuration"""
        priority_config = {
            "priorities": {
                "10": [
                    ".*general-purpose.*"
                ],
                "50": [
                    ".*compute-optimized.*",
                    ".*memory-optimized.*"
                ],
                "100": [
                    ".*spot-instances.*"
                ],
                "1": [
                    ".*gpu-enabled.*"
                ]
            }
        }
        
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "cluster-autoscaler-priority-expander",
                "namespace": "kube-system",
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "cluster-autoscaler"
                }
            },
            "data": {
                "priorities": yaml.dump(priority_config, default_flow_style=False)
            }
        }
    
    def create_vertical_pod_autoscaler(self) -> Dict[str, Any]:
        """Create VPA for cluster autoscaler"""
        return {
            "apiVersion": "autoscaling.k8s.io/v1",
            "kind": "VerticalPodAutoscaler",
            "metadata": {
                "name": "cluster-autoscaler-vpa",
                "namespace": "kube-system",
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "cluster-autoscaler"
                }
            },
            "spec": {
                "targetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": "cluster-autoscaler"
                },
                "updatePolicy": {
                    "updateMode": "Auto"
                },
                "resourcePolicy": {
                    "containerPolicies": [
                        {
                            "containerName": "cluster-autoscaler",
                            "minAllowed": {
                                "cpu": "50m",
                                "memory": "300Mi"
                            },
                            "maxAllowed": {
                                "cpu": "500m",
                                "memory": "2Gi"
                            },
                            "controlledResources": ["cpu", "memory"]
                        }
                    ]
                }
            }
        }
    
    def create_service_monitor(self) -> Dict[str, Any]:
        """Create ServiceMonitor for Prometheus"""
        return {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": "cluster-autoscaler",
                "namespace": "kube-system",
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "cluster-autoscaler"
                }
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": "cluster-autoscaler"
                    }
                },
                "endpoints": [
                    {
                        "port": "http",
                        "interval": "30s",
                        "path": "/metrics"
                    }
                ]
            }
        }
    
    def create_service(self) -> Dict[str, Any]:
        """Create service for cluster autoscaler"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "cluster-autoscaler",
                "namespace": "kube-system",
                "labels": {
                    "app": "cluster-autoscaler",
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "cluster-autoscaler"
                }
            },
            "spec": {
                "selector": {
                    "app": "cluster-autoscaler"
                },
                "ports": [
                    {
                        "name": "http",
                        "port": 8085,
                        "targetPort": 8085,
                        "protocol": "TCP"
                    }
                ]
            }
        }
    
    def generate_all_manifests(self) -> Dict[str, str]:
        """Generate all cluster autoscaler manifests"""
        manifests = {}
        
        # Service account and RBAC
        rbac_resources = self.create_cluster_autoscaler_service_account()
        for i, resource in enumerate(rbac_resources):
            manifests[f"cluster-autoscaler-rbac-{i+1}"] = yaml.dump(resource, default_flow_style=False)
        
        # Priority expander ConfigMap
        priority_config = self.create_priority_expander_configmap()
        manifests["cluster-autoscaler-priority-configmap"] = yaml.dump(priority_config, default_flow_style=False)
        
        # Cluster autoscaler deployment
        deployment = self.create_cluster_autoscaler_deployment()
        manifests["cluster-autoscaler-deployment"] = yaml.dump(deployment, default_flow_style=False)
        
        # Service
        service = self.create_service()
        manifests["cluster-autoscaler-service"] = yaml.dump(service, default_flow_style=False)
        
        # VPA
        vpa = self.create_vertical_pod_autoscaler()
        manifests["cluster-autoscaler-vpa"] = yaml.dump(vpa, default_flow_style=False)
        
        # ServiceMonitor
        service_monitor = self.create_service_monitor()
        manifests["cluster-autoscaler-servicemonitor"] = yaml.dump(service_monitor, default_flow_style=False)
        
        return manifests
    
    def save_manifests_to_files(self, output_dir -> None: str = "./k8s-manifests/cluster-autoscaler") -> None:
        """Save all cluster autoscaler manifests to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        manifests = self.generate_all_manifests()
        
        for name, manifest in manifests.items():
            file_path = os.path.join(output_dir, f"{name}.yaml")
            with open(file_path, 'w') as f:
                f.write(manifest)
            logger.info(f"Cluster autoscaler manifest saved: {file_path}")
        
        return len(manifests)


# Export main functionality
__all__ = ['ClusterAutoscalerManager', 'AutoscalingConfig', 'NodePoolConfig', 'CloudProvider', 'NodePoolType']