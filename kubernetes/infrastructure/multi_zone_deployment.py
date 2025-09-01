"""Multi-Zone Deployment for High Availability
===========================================

Kubernetes multi-zone deployment configuration for high availability
and disaster recovery for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DeploymentStrategy(Enum):
    """Deployment strategies for high availability"""
    ACTIVE_ACTIVE = "active-active"
    ACTIVE_PASSIVE = "active-passive"
    BLUE_GREEN = "blue-green"
    CANARY = "canary"


class ServiceDistribution(Enum):
    """Service distribution strategies"""
    ROUND_ROBIN = "round-robin"
    LEAST_CONNECTIONS = "least-connections"
    GEOLOCATION = "geolocation"
    LATENCY_BASED = "latency-based"


@dataclass
class ZoneConfig:
    """Availability zone configuration"""
    name: str
    region: str
    preferred: bool = False
    node_groups: List[str] = field(default_factory=list)
    storage_class: str = "general-purpose"
    backup_zone: Optional[str] = None


@dataclass
class MultiZoneConfig:
    """Multi-zone deployment configuration"""
    cluster_name: str = "ia-influencer-cluster"
    zones: List[ZoneConfig] = field(default_factory=list)
    strategy: DeploymentStrategy = DeploymentStrategy.ACTIVE_ACTIVE
    distribution: ServiceDistribution = ServiceDistribution.ROUND_ROBIN
    min_zones: int = 2
    cross_zone_load_balancing: bool = True
    zone_aware_hints: bool = True


class MultiZoneManager:
    """Manages multi-zone deployment configuration"""
    
    def __init__(self, config: MultiZoneConfig):
        self.config = config
        self.namespace = "ia-influencer"
        if not self.config.zones:
            self._initialize_default_zones()
    
    def _initialize_default_zones(self):
        """Initialize default availability zones"""
        self.config.zones = [
            ZoneConfig(
                name="eu-central-1a",
                region="eu-central-1",
                preferred=True,
                node_groups=["general-purpose", "compute-optimized"],
                storage_class="high-performance"
            ),
            ZoneConfig(
                name="eu-central-1b",
                region="eu-central-1",
                preferred=False,
                node_groups=["general-purpose", "memory-optimized"],
                storage_class="general-purpose",
                backup_zone="eu-central-1a"
            ),
            ZoneConfig(
                name="eu-central-1c",
                region="eu-central-1",
                preferred=False,
                node_groups=["general-purpose", "spot-instances"],
                storage_class="general-purpose",
                backup_zone="eu-central-1a"
            )
        ]
    
    def create_zone_aware_deployment(self, service_name: str, 
                                   replicas_per_zone: int = 2) -> Dict[str, Any]:
        """Create zone-aware deployment with pod anti-affinity"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{service_name}-multizone",
                "namespace": self.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": service_name,
                    "deployment-strategy": self.config.strategy.value
                }
            },
            "spec": {
                "replicas": len(self.config.zones) * replicas_per_zone,
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxUnavailable": "25%",
                        "maxSurge": "25%"
                    }
                },
                "selector": {
                    "matchLabels": {
                        "app": service_name,
                        "version": "v1"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": service_name,
                            "version": "v1",
                            "deployment-strategy": self.config.strategy.value
                        },
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": "8080"
                        }
                    },
                    "spec": {
                        "affinity": {
                            "podAntiAffinity": {
                                "requiredDuringSchedulingIgnoredDuringExecution": [
                                    {
                                        "labelSelector": {
                                            "matchExpressions": [
                                                {
                                                    "key": "app",
                                                    "operator": "In",
                                                    "values": [service_name]
                                                }
                                            ]
                                        },
                                        "topologyKey": "kubernetes.io/hostname"
                                    }
                                ],
                                "preferredDuringSchedulingIgnoredDuringExecution": [
                                    {
                                        "weight": 100,
                                        "podAffinityTerm": {
                                            "labelSelector": {
                                                "matchExpressions": [
                                                    {
                                                        "key": "app",
                                                        "operator": "In",
                                                        "values": [service_name]
                                                    }
                                                ]
                                            },
                                            "topologyKey": "topology.kubernetes.io/zone"
                                        }
                                    }
                                ]
                            }
                        },
                        "topologySpreadConstraints": [
                            {
                                "maxSkew": 1,
                                "topologyKey": "topology.kubernetes.io/zone",
                                "whenUnsatisfiable": "DoNotSchedule",
                                "labelSelector": {
                                    "matchLabels": {
                                        "app": service_name
                                    }
                                }
                            },
                            {
                                "maxSkew": 1,
                                "topologyKey": "kubernetes.io/hostname",
                                "whenUnsatisfiable": "ScheduleAnyway",
                                "labelSelector": {
                                    "matchLabels": {
                                        "app": service_name
                                    }
                                }
                            }
                        ],
                        "containers": [
                            {
                                "name": service_name,
                                "image": f"registry.ainflue.com/{service_name}:latest",
                                "ports": [
                                    {
                                        "containerPort": 8080,
                                        "name": "http"
                                    }
                                ],
                                "env": [
                                    {
                                        "name": "ZONE",
                                        "valueFrom": {
                                            "fieldRef": {
                                                "fieldPath": "metadata.annotations['topology.kubernetes.io/zone']"
                                            }
                                        }
                                    },
                                    {
                                        "name": "NODE_NAME",
                                        "valueFrom": {
                                            "fieldRef": {
                                                "fieldPath": "spec.nodeName"
                                            }
                                        }
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "128Mi"
                                    },
                                    "limits": {
                                        "cpu": "500m",
                                        "memory": "512Mi"
                                    }
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8080
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": 8080
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5
                                }
                            }
                        ]
                    }
                }
            }
        }
    
    def create_zone_aware_service(self, service_name: str) -> Dict[str, Any]:
        """Create zone-aware service with topology hints"""
        annotations = {}
        if self.config.zone_aware_hints:
            annotations["service.kubernetes.io/topology-aware-hints"] = "auto"
        
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{service_name}-multizone",
                "namespace": self.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": service_name
                },
                "annotations": annotations
            },
            "spec": {
                "selector": {
                    "app": service_name
                },
                "ports": [
                    {
                        "port": 80,
                        "targetPort": 8080,
                        "protocol": "TCP",
                        "name": "http"
                    }
                ],
                "type": "ClusterIP",
                "sessionAffinity": "None"
            }
        }
    
    def create_pod_disruption_budget(self, service_name: str, 
                                   min_available: str = "50%") -> Dict[str, Any]:
        """Create PodDisruptionBudget for high availability"""
        return {
            "apiVersion": "policy/v1",
            "kind": "PodDisruptionBudget",
            "metadata": {
                "name": f"{service_name}-pdb",
                "namespace": self.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": service_name
                }
            },
            "spec": {
                "minAvailable": min_available,
                "selector": {
                    "matchLabels": {
                        "app": service_name
                    }
                }
            }
        }
    
    def create_statefulset_multizone(self, service_name: str,
                                   replicas_per_zone: int = 1) -> Dict[str, Any]:
        """Create multi-zone StatefulSet for stateful services"""
        return {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": f"{service_name}-multizone",
                "namespace": self.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": service_name
                }
            },
            "spec": {
                "serviceName": f"{service_name}-multizone",
                "replicas": len(self.config.zones) * replicas_per_zone,
                "selector": {
                    "matchLabels": {
                        "app": service_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": service_name,
                            "version": "v1"
                        }
                    },
                    "spec": {
                        "affinity": {
                            "podAntiAffinity": {
                                "requiredDuringSchedulingIgnoredDuringExecution": [
                                    {
                                        "labelSelector": {
                                            "matchExpressions": [
                                                {
                                                    "key": "app",
                                                    "operator": "In",
                                                    "values": [service_name]
                                                }
                                            ]
                                        },
                                        "topologyKey": "kubernetes.io/hostname"
                                    }
                                ]
                            }
                        },
                        "topologySpreadConstraints": [
                            {
                                "maxSkew": 1,
                                "topologyKey": "topology.kubernetes.io/zone",
                                "whenUnsatisfiable": "DoNotSchedule",
                                "labelSelector": {
                                    "matchLabels": {
                                        "app": service_name
                                    }
                                }
                            }
                        ],
                        "containers": [
                            {
                                "name": service_name,
                                "image": f"registry.ainflue.com/{service_name}:latest",
                                "ports": [
                                    {
                                        "containerPort": 5432,
                                        "name": "postgres"
                                    }
                                ],
                                "env": [
                                    {
                                        "name": "POSTGRES_DB",
                                        "value": "ainflue"
                                    },
                                    {
                                        "name": "POSTGRES_USER",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": f"{service_name}-secret",
                                                "key": "username"
                                            }
                                        }
                                    },
                                    {
                                        "name": "POSTGRES_PASSWORD",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": f"{service_name}-secret",
                                                "key": "password"
                                            }
                                        }
                                    }
                                ],
                                "volumeMounts": [
                                    {
                                        "name": f"{service_name}-storage",
                                        "mountPath": "/var/lib/postgresql/data"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "500m",
                                        "memory": "1Gi"
                                    },
                                    "limits": {
                                        "cpu": "2000m",
                                        "memory": "4Gi"
                                    }
                                }
                            }
                        ]
                    }
                },
                "volumeClaimTemplates": [
                    {
                        "metadata": {
                            "name": f"{service_name}-storage"
                        },
                        "spec": {
                            "accessModes": ["ReadWriteOnce"],
                            "storageClassName": "ia-influencer-database",
                            "resources": {
                                "requests": {
                                    "storage": "100Gi"
                                }
                            }
                        }
                    }
                ],
                "podManagementPolicy": "Parallel"
            }
        }
    
    def create_zone_monitoring_service(self) -> Dict[str, Any]:
        """Create service for monitoring zone health"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "zone-health-monitor",
                "namespace": self.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "zone-monitor"
                }
            },
            "spec": {
                "selector": {
                    "app": "zone-health-monitor"
                },
                "ports": [
                    {
                        "port": 9090,
                        "targetPort": 9090,
                        "protocol": "TCP",
                        "name": "metrics"
                    }
                ]
            }
        }
    
    def create_zone_health_monitor_deployment(self) -> Dict[str, Any]:
        """Create deployment for monitoring zone health"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "zone-health-monitor",
                "namespace": self.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "zone-monitor"
                }
            },
            "spec": {
                "replicas": len(self.config.zones),
                "selector": {
                    "matchLabels": {
                        "app": "zone-health-monitor"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "zone-health-monitor"
                        }
                    },
                    "spec": {
                        "affinity": {
                            "podAntiAffinity": {
                                "requiredDuringSchedulingIgnoredDuringExecution": [
                                    {
                                        "labelSelector": {
                                            "matchExpressions": [
                                                {
                                                    "key": "app",
                                                    "operator": "In",
                                                    "values": ["zone-health-monitor"]
                                                }
                                            ]
                                        },
                                        "topologyKey": "topology.kubernetes.io/zone"
                                    }
                                ]
                            }
                        },
                        "containers": [
                            {
                                "name": "zone-monitor",
                                "image": "prom/node-exporter:v1.6.1",
                                "args": [
                                    "--path.procfs=/host/proc",
                                    "--path.sysfs=/host/sys",
                                    "--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)",
                                    "--web.listen-address=:9090"
                                ],
                                "ports": [
                                    {
                                        "containerPort": 9090,
                                        "name": "metrics"
                                    }
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "proc",
                                        "mountPath": "/host/proc",
                                        "readOnly": True
                                    },
                                    {
                                        "name": "sys",
                                        "mountPath": "/host/sys",
                                        "readOnly": True
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "50m",
                                        "memory": "128Mi"
                                    },
                                    "limits": {
                                        "cpu": "200m",
                                        "memory": "256Mi"
                                    }
                                }
                            }
                        ],
                        "volumes": [
                            {
                                "name": "proc",
                                "hostPath": {
                                    "path": "/proc"
                                }
                            },
                            {
                                "name": "sys",
                                "hostPath": {
                                    "path": "/sys"
                                }
                            }
                        ],
                        "hostNetwork": True,
                        "hostPID": True
                    }
                }
            }
        }
    
    def create_cross_zone_network_policy(self) -> Dict[str, Any]:
        """Create network policy for cross-zone communication"""
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "cross-zone-communication",
                "namespace": self.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "network-policy"
                }
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {
                        "app.kubernetes.io/name": "ia-influencer"
                    }
                },
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {
                                "podSelector": {
                                    "matchLabels": {
                                        "app.kubernetes.io/name": "ia-influencer"
                                    }
                                }
                            }
                        ]
                    }
                ],
                "egress": [
                    {
                        "to": [
                            {
                                "podSelector": {
                                    "matchLabels": {
                                        "app.kubernetes.io/name": "ia-influencer"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "to": [],
                        "ports": [
                            {"protocol": "TCP", "port": 53},
                            {"protocol": "UDP", "port": 53},
                            {"protocol": "TCP", "port": 443}
                        ]
                    }
                ]
            }
        }
    
    def generate_all_manifests(self) -> Dict[str, str]:
        """Generate all multi-zone deployment manifests"""
        manifests = {}
        
        # Core services with multi-zone deployment
        core_services = ["api-gateway", "backend", "ai-processing", "storage"]
        
        for service in core_services:
            # Zone-aware deployment
            deployment = self.create_zone_aware_deployment(service)
            manifests[f"{service}-multizone-deployment"] = yaml.dump(deployment, default_flow_style=False)
            
            # Zone-aware service
            service_manifest = self.create_zone_aware_service(service)
            manifests[f"{service}-multizone-service"] = yaml.dump(service_manifest, default_flow_style=False)
            
            # Pod disruption budget
            pdb = self.create_pod_disruption_budget(service)
            manifests[f"{service}-pdb"] = yaml.dump(pdb, default_flow_style=False)
        
        # Stateful services
        stateful_services = ["database", "redis"]
        for service in stateful_services:
            statefulset = self.create_statefulset_multizone(service)
            manifests[f"{service}-multizone-statefulset"] = yaml.dump(statefulset, default_flow_style=False)
            
            pdb = self.create_pod_disruption_budget(service, "1")
            manifests[f"{service}-pdb"] = yaml.dump(pdb, default_flow_style=False)
        
        # Zone health monitoring
        zone_monitor_deployment = self.create_zone_health_monitor_deployment()
        manifests["zone-health-monitor-deployment"] = yaml.dump(zone_monitor_deployment, default_flow_style=False)
        
        zone_monitor_service = self.create_zone_monitoring_service()
        manifests["zone-health-monitor-service"] = yaml.dump(zone_monitor_service, default_flow_style=False)
        
        # Cross-zone network policy
        network_policy = self.create_cross_zone_network_policy()
        manifests["cross-zone-network-policy"] = yaml.dump(network_policy, default_flow_style=False)
        
        return manifests
    
    def save_manifests_to_files(self, output_dir: str = "./k8s-manifests/multi-zone"):
        """Save all multi-zone manifests to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        manifests = self.generate_all_manifests()
        
        for name, manifest in manifests.items():
            file_path = os.path.join(output_dir, f"{name}.yaml")
            with open(file_path, 'w') as f:
                f.write(manifest)
            logger.info(f"Multi-zone manifest saved: {file_path}")
        
        return len(manifests)


# Export main functionality
__all__ = ['MultiZoneManager', 'MultiZoneConfig', 'ZoneConfig', 'DeploymentStrategy', 'ServiceDistribution']