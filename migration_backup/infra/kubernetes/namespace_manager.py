# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade Kubernetes Namespace Management
# Multi-tenant namespace orchestration with resource quotas and security policies
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from kubernetes import client, config
import yaml
import logging
from datetime import datetime
from enum import Enum

class NamespaceType(Enum):
    """Namespace types for different environments"""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"
    MONITORING = "monitoring"
    SECURITY = "security"
    AI_PROCESSING = "ai-processing"
    CONTENT_DELIVERY = "content-delivery"

@dataclass
class NamespaceConfig:
    """Namespace configuration with enterprise features"""
    name: str
    namespace_type: NamespaceType
    resource_quotas: Dict[str, str]
    network_policies: List[str]
    rbac_enabled: bool = True
    monitoring_enabled: bool = True
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None

@dataclass
class ResourceQuota:
    """Resource quota specification"""
    cpu_requests: str
    cpu_limits: str
    memory_requests: str
    memory_limits: str
    storage_requests: str
    pods_limit: int
    services_limit: int
    secrets_limit: int
    configmaps_limit: int

class NamespaceManager:
    """
    Enterprise Kubernetes Namespace Manager
    
    Capabilities:
    - Multi-tenant namespace creation and management
    - Resource quota enforcement
    - Network policy automation
    - RBAC integration
    - Monitoring and alerting setup
    - Lifecycle management
    - Compliance and security
    """
    
    def __init__(self, cluster_config: Optional[str] = None):
        self.cluster_config = cluster_config
        self.k8s_client = None
        self.rbac_client = None
        self.policy_client = None
        self.logger = self._setup_logging()
        self.namespaces: Dict[str, NamespaceConfig] = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger("NamespaceManager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def initialize(self) -> bool:
        """Initialize Kubernetes clients"""
        try:
            if self.cluster_config:
                config.load_kube_config(config_file=self.cluster_config)
            else:
                config.load_incluster_config()
                
            self.k8s_client = client.CoreV1Api()
            self.rbac_client = client.RbacAuthorizationV1Api()
            self.policy_client = client.NetworkingV1Api()
            
            self.logger.info("Kubernetes clients initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Kubernetes clients: {e}")
            return False
    
    async def create_namespace(self, namespace_config: NamespaceConfig) -> bool:
        """Create namespace with enterprise configuration"""
        try:
            # Prepare namespace manifest
            namespace_manifest = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": namespace_config.name,
                    "labels": {
                        "name": namespace_config.name,
                        "type": namespace_config.namespace_type.value,
                        "managed-by": "ainflue-infrastructure",
                        "environment": namespace_config.namespace_type.value,
                        **(namespace_config.labels or {})
                    },
                    "annotations": {
                        "kubectl.kubernetes.io/last-applied-configuration": "",
                        "ainflue.io/created": datetime.utcnow().isoformat(),
                        "ainflue.io/managed": "true",
                        **(namespace_config.annotations or {})
                    }
                }
            }
            
            # Create namespace
            self.k8s_client.create_namespace(body=namespace_manifest)
            self.logger.info(f"Namespace {namespace_config.name} created successfully")
            
            # Setup resource quotas
            if namespace_config.resource_quotas:
                await self._create_resource_quota(namespace_config)
            
            # Setup network policies
            if namespace_config.network_policies:
                await self._create_network_policies(namespace_config)
            
            # Setup RBAC
            if namespace_config.rbac_enabled:
                await self._setup_rbac(namespace_config)
            
            # Setup monitoring
            if namespace_config.monitoring_enabled:
                await self._setup_monitoring(namespace_config)
            
            # Store configuration
            self.namespaces[namespace_config.name] = namespace_config
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create namespace {namespace_config.name}: {e}")
            return False
    
    async def create_production_namespace(self, app_name: str) -> bool:
        """Create production namespace with strict policies"""
        config = NamespaceConfig(
            name=f"{app_name}-production",
            namespace_type=NamespaceType.PRODUCTION,
            resource_quotas={
                "requests.cpu": "4",
                "requests.memory": "8Gi",
                "limits.cpu": "8",
                "limits.memory": "16Gi",
                "persistentvolumeclaims": "10",
                "pods": "50",
                "services": "20"
            },
            network_policies=["deny-all", "allow-same-namespace", "allow-monitoring"],
            rbac_enabled=True,
            monitoring_enabled=True,
            labels={
                "security.istio.io/tlsMode": "istio",
                "network-policy": "restricted"
            },
            annotations={
                "scheduler.alpha.kubernetes.io/node-selector": "environment=production"
            }
        )
        
        return await self.create_namespace(config)
    
    async def create_ai_processing_namespace(self, model_name: str) -> bool:
        """Create AI processing namespace with GPU resources"""
        config = NamespaceConfig(
            name=f"ai-{model_name}",
            namespace_type=NamespaceType.AI_PROCESSING,
            resource_quotas={
                "requests.cpu": "8",
                "requests.memory": "32Gi",
                "limits.cpu": "16",
                "limits.memory": "64Gi",
                "requests.nvidia.com/gpu": "4",
                "limits.nvidia.com/gpu": "8",
                "pods": "20",
                "services": "10"
            },
            network_policies=["allow-ai-traffic", "allow-storage-access"],
            rbac_enabled=True,
            monitoring_enabled=True,
            labels={
                "workload-type": "ai-processing",
                "gpu-enabled": "true",
                "node-selector": "gpu=true"
            }
        )
        
        return await self.create_namespace(config)
    
    async def create_development_namespace(self, developer: str, project: str) -> bool:
        """Create development namespace with relaxed policies"""
        config = NamespaceConfig(
            name=f"dev-{developer}-{project}",
            namespace_type=NamespaceType.DEVELOPMENT,
            resource_quotas={
                "requests.cpu": "1",
                "requests.memory": "2Gi",
                "limits.cpu": "2",
                "limits.memory": "4Gi",
                "pods": "20",
                "services": "10"
            },
            network_policies=["allow-development"],
            rbac_enabled=True,
            monitoring_enabled=True,
            labels={
                "developer": developer,
                "project": project,
                "auto-cleanup": "enabled"
            },
            annotations={
                "ainflue.io/ttl": "7d",  # Auto-cleanup after 7 days
                "ainflue.io/owner": developer
            }
        )
        
        return await self.create_namespace(config)
    
    async def setup_multi_tenant_isolation(self, tenant_id: str, services: List[str]) -> bool:
        """Setup multi-tenant namespace isolation"""
        try:
            # Create tenant namespace
            tenant_config = NamespaceConfig(
                name=f"tenant-{tenant_id}",
                namespace_type=NamespaceType.PRODUCTION,
                resource_quotas={
                    "requests.cpu": "2",
                    "requests.memory": "4Gi",
                    "limits.cpu": "4",
                    "limits.memory": "8Gi",
                    "pods": "30"
                },
                network_policies=["tenant-isolation", "allow-egress"],
                rbac_enabled=True,
                monitoring_enabled=True,
                labels={
                    "tenant-id": tenant_id,
                    "isolation": "strict"
                }
            )
            
            await self.create_namespace(tenant_config)
            
            # Create service-specific namespaces
            for service in services:
                service_config = NamespaceConfig(
                    name=f"tenant-{tenant_id}-{service}",
                    namespace_type=NamespaceType.PRODUCTION,
                    resource_quotas={
                        "requests.cpu": "500m",
                        "requests.memory": "1Gi",
                        "limits.cpu": "1",
                        "limits.memory": "2Gi",
                        "pods": "10"
                    },
                    network_policies=[f"allow-{service}", "deny-cross-service"],
                    rbac_enabled=True,
                    monitoring_enabled=True,
                    labels={
                        "tenant-id": tenant_id,
                        "service": service
                    }
                )
                
                await self.create_namespace(service_config)
            
            self.logger.info(f"Multi-tenant isolation setup for tenant {tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup multi-tenant isolation: {e}")
            return False
    
    async def apply_security_policies(self, namespace: str) -> bool:
        """Apply comprehensive security policies"""
        try:
            # Pod Security Policy
            psp_manifest = {
                "apiVersion": "policy/v1beta1",
                "kind": "PodSecurityPolicy",
                "metadata": {
                    "name": f"{namespace}-psp"
                },
                "spec": {
                    "privileged": False,
                    "allowPrivilegeEscalation": False,
                    "requiredDropCapabilities": ["ALL"],
                    "volumes": ["configMap", "secret", "emptyDir", "persistentVolumeClaim"],
                    "runAsUser": {
                        "rule": "MustRunAsNonRoot"
                    },
                    "seLinux": {
                        "rule": "RunAsAny"
                    },
                    "fsGroup": {
                        "rule": "RunAsAny"
                    }
                }
            }
            
            # Network Security Policy
            network_policy = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": f"{namespace}-security-policy",
                    "namespace": namespace
                },
                "spec": {
                    "podSelector": {},
                    "policyTypes": ["Ingress", "Egress"],
                    "ingress": [
                        {
                            "from": [
                                {
                                    "namespaceSelector": {
                                        "matchLabels": {
                                            "name": namespace
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
                                    "namespaceSelector": {
                                        "matchLabels": {
                                            "name": "monitoring"
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
            
            self.policy_client.create_namespaced_network_policy(
                namespace=namespace,
                body=network_policy
            )
            
            self.logger.info(f"Security policies applied to namespace {namespace}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply security policies: {e}")
            return False
    
    async def monitor_namespace_resources(self, namespace: str) -> Dict[str, Any]:
        """Monitor namespace resource usage"""
        try:
            # Get resource quota status
            quotas = self.k8s_client.list_namespaced_resource_quota(namespace=namespace)
            
            # Get pod metrics
            pods = self.k8s_client.list_namespaced_pod(namespace=namespace)
            
            # Get service metrics
            services = self.k8s_client.list_namespaced_service(namespace=namespace)
            
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "namespace": namespace,
                "resource_usage": {},
                "quotas": {},
                "pods": {
                    "total": len(pods.items),
                    "running": len([p for p in pods.items if p.status.phase == "Running"]),
                    "pending": len([p for p in pods.items if p.status.phase == "Pending"]),
                    "failed": len([p for p in pods.items if p.status.phase == "Failed"])
                },
                "services": {
                    "total": len(services.items),
                    "loadbalancer": len([s for s in services.items if s.spec.type == "LoadBalancer"]),
                    "clusterip": len([s for s in services.items if s.spec.type == "ClusterIP"])
                }
            }
            
            # Extract quota information
            for quota in quotas.items:
                if quota.status.hard:
                    for resource, limit in quota.status.hard.items():
                        used = quota.status.used.get(resource, "0") if quota.status.used else "0"
                        metrics["quotas"][resource] = {
                            "limit": limit,
                            "used": used,
                            "utilization": self._calculate_utilization(used, limit)
                        }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to monitor namespace resources: {e}")
            return {"error": str(e)}
    
    async def cleanup_expired_namespaces(self) -> List[str]:
        """Cleanup expired development namespaces"""
        try:
            cleaned_namespaces = []
            namespaces = self.k8s_client.list_namespace()
            
            for namespace in namespaces.items:
                annotations = namespace.metadata.annotations or {}
                ttl = annotations.get("ainflue.io/ttl")
                created = annotations.get("ainflue.io/created")
                
                if ttl and created:
                    if self._is_expired(created, ttl):
                        self.k8s_client.delete_namespace(name=namespace.metadata.name)
                        cleaned_namespaces.append(namespace.metadata.name)
                        self.logger.info(f"Cleaned up expired namespace: {namespace.metadata.name}")
            
            return cleaned_namespaces
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired namespaces: {e}")
            return []
    
    async def _create_resource_quota(self, namespace_config: NamespaceConfig) -> bool:
        """Create resource quota for namespace"""
        try:
            quota_manifest = {
                "apiVersion": "v1",
                "kind": "ResourceQuota",
                "metadata": {
                    "name": f"{namespace_config.name}-quota",
                    "namespace": namespace_config.name
                },
                "spec": {
                    "hard": namespace_config.resource_quotas
                }
            }
            
            self.k8s_client.create_namespaced_resource_quota(
                namespace=namespace_config.name,
                body=quota_manifest
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create resource quota: {e}")
            return False
    
    async def _create_network_policies(self, namespace_config: NamespaceConfig) -> bool:
        """Create network policies for namespace"""
        try:
            for policy_name in namespace_config.network_policies:
                policy_manifest = self._get_network_policy_template(
                    policy_name, 
                    namespace_config.name
                )
                
                if policy_manifest:
                    self.policy_client.create_namespaced_network_policy(
                        namespace=namespace_config.name,
                        body=policy_manifest
                    )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create network policies: {e}")
            return False
    
    async def _setup_rbac(self, namespace_config: NamespaceConfig) -> bool:
        """Setup RBAC for namespace"""
        try:
            # Create service account
            sa_manifest = {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": f"{namespace_config.name}-sa",
                    "namespace": namespace_config.name
                }
            }
            
            self.k8s_client.create_namespaced_service_account(
                namespace=namespace_config.name,
                body=sa_manifest
            )
            
            # Create role binding
            rb_manifest = {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "RoleBinding",
                "metadata": {
                    "name": f"{namespace_config.name}-binding",
                    "namespace": namespace_config.name
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": f"{namespace_config.name}-sa",
                        "namespace": namespace_config.name
                    }
                ],
                "roleRef": {
                    "kind": "ClusterRole",
                    "name": "edit",
                    "apiGroup": "rbac.authorization.k8s.io"
                }
            }
            
            self.rbac_client.create_namespaced_role_binding(
                namespace=namespace_config.name,
                body=rb_manifest
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup RBAC: {e}")
            return False
    
    async def _setup_monitoring(self, namespace_config: NamespaceConfig) -> bool:
        """Setup monitoring for namespace"""
        try:
            # Create ServiceMonitor for Prometheus
            service_monitor = {
                "apiVersion": "monitoring.coreos.com/v1",
                "kind": "ServiceMonitor",
                "metadata": {
                    "name": f"{namespace_config.name}-monitor",
                    "namespace": namespace_config.name,
                    "labels": {
                        "app": "prometheus"
                    }
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "monitoring": "enabled"
                        }
                    },
                    "endpoints": [
                        {
                            "port": "metrics",
                            "interval": "30s"
                        }
                    ]
                }
            }
            
            # Note: This would require custom resource definitions
            # In a real implementation, you'd use the appropriate API client
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup monitoring: {e}")
            return False
    
    def _get_network_policy_template(self, policy_name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get network policy template"""
        templates = {
            "deny-all": {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": "deny-all",
                    "namespace": namespace
                },
                "spec": {
                    "podSelector": {},
                    "policyTypes": ["Ingress", "Egress"]
                }
            },
            "allow-same-namespace": {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": "allow-same-namespace",
                    "namespace": namespace
                },
                "spec": {
                    "podSelector": {},
                    "policyTypes": ["Ingress"],
                    "ingress": [
                        {
                            "from": [
                                {
                                    "namespaceSelector": {
                                        "matchLabels": {
                                            "name": namespace
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        }
        
        return templates.get(policy_name)
    
    def _calculate_utilization(self, used: str, limit: str) -> float:
        """Calculate resource utilization percentage"""
        try:
            # Handle different resource formats
            used_val = self._parse_resource_value(used)
            limit_val = self._parse_resource_value(limit)
            
            if limit_val > 0:
                return (used_val / limit_val) * 100
            return 0.0
            
        except:
            return 0.0
    
    def _parse_resource_value(self, value: str) -> float:
        """Parse Kubernetes resource value"""
        if value.endswith('m'):
            return float(value[:-1]) / 1000
        elif value.endswith('Gi'):
            return float(value[:-2]) * 1024 * 1024 * 1024
        elif value.endswith('Mi'):
            return float(value[:-2]) * 1024 * 1024
        elif value.endswith('Ki'):
            return float(value[:-2]) * 1024
        else:
            return float(value)
    
    def _is_expired(self, created: str, ttl: str) -> bool:
        """Check if namespace is expired based on TTL"""
        try:
            from datetime import datetime, timedelta
            
            created_time = datetime.fromisoformat(created.replace('Z', '+00:00'))
            
            # Parse TTL (e.g., "7d", "24h", "30m")
            if ttl.endswith('d'):
                delta = timedelta(days=int(ttl[:-1]))
            elif ttl.endswith('h'):
                delta = timedelta(hours=int(ttl[:-1]))
            elif ttl.endswith('m'):
                delta = timedelta(minutes=int(ttl[:-1]))
            else:
                return False
            
            return datetime.utcnow() > (created_time + delta)
            
        except:
            return False

# Factory function for easy instantiation
def create_namespace_manager(cluster_config: Optional[str] = None) -> NamespaceManager:
    """Create and initialize namespace manager"""
    return NamespaceManager(cluster_config)

# Enterprise namespace templates
ENTERPRISE_NAMESPACE_TEMPLATES = {
    "microservices": {
        "api": NamespaceType.PRODUCTION,
        "worker": NamespaceType.PRODUCTION,
        "cache": NamespaceType.PRODUCTION,
        "monitoring": NamespaceType.MONITORING
    },
    "ai_platform": {
        "inference": NamespaceType.AI_PROCESSING,
        "training": NamespaceType.AI_PROCESSING,
        "storage": NamespaceType.PRODUCTION,
        "monitoring": NamespaceType.MONITORING
    },
    "content_platform": {
        "api": NamespaceType.PRODUCTION,
        "processing": NamespaceType.AI_PROCESSING,
        "delivery": NamespaceType.CONTENT_DELIVERY,
        "storage": NamespaceType.PRODUCTION
    }
}