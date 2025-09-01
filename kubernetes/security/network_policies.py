"""Network Policies for Kubernetes Micro-segmentation
====================================================

Comprehensive network policy implementation for secure micro-segmentation
of the Ainflue platform with zero-trust architecture.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Network policy types"""
    DENY_ALL = "deny-all"
    ALLOW_INGRESS = "allow-ingress"
    ALLOW_EGRESS = "allow-egress"
    DATABASE_ACCESS = "database-access"
    API_ACCESS = "api-access"
    MONITORING = "monitoring"


@dataclass
class NetworkPolicySpec:
    """Network policy specification"""
    name: str
    namespace: str
    policy_type: PolicyType
    pod_selector: Dict[str, Any] = field(default_factory=dict)
    ingress_rules: List[Dict[str, Any]] = field(default_factory=list)
    egress_rules: List[Dict[str, Any]] = field(default_factory=list)
    description: str = ""


class NetworkPolicyManager:
    """Manages Kubernetes Network Policies for micro-segmentation"""
    
    def __init__(self, namespace: str = "ia-influencer"):
        self.namespace = namespace
        self.policies: Dict[str, NetworkPolicySpec] = {}
        
    def create_deny_all_policy(self) -> NetworkPolicySpec:
        """Create default deny-all policy for zero-trust"""
        return NetworkPolicySpec(
            name="deny-all-default",
            namespace=self.namespace,
            policy_type=PolicyType.DENY_ALL,
            pod_selector={},  # Applies to all pods
            description="Default deny-all policy for zero-trust security"
        )
    
    def create_database_access_policy(self) -> NetworkPolicySpec:
        """Create policy for database access"""
        return NetworkPolicySpec(
            name="database-access-policy",
            namespace=self.namespace,
            policy_type=PolicyType.DATABASE_ACCESS,
            pod_selector={"matchLabels": {"tier": "database"}},
            ingress_rules=[
                {
                    "from": [
                        {"podSelector": {"matchLabels": {"component": "backend"}}},
                        {"podSelector": {"matchLabels": {"component": "ai-processing"}}},
                        {"podSelector": {"matchLabels": {"component": "analytics"}}}
                    ],
                    "ports": [
                        {"protocol": "TCP", "port": 5432},  # PostgreSQL
                        {"protocol": "TCP", "port": 6379},  # Redis
                        {"protocol": "TCP", "port": 27017}  # MongoDB
                    ]
                }
            ],
            description="Allow database access only from authorized backend services"
        )
    
    def create_api_gateway_policy(self) -> NetworkPolicySpec:
        """Create policy for API gateway"""
        return NetworkPolicySpec(
            name="api-gateway-policy",
            namespace=self.namespace,
            policy_type=PolicyType.API_ACCESS,
            pod_selector={"matchLabels": {"component": "api-gateway"}},
            ingress_rules=[
                {
                    "from": [
                        {"namespaceSelector": {"matchLabels": {"name": "nginx-ingress"}}},
                        {"namespaceSelector": {"matchLabels": {"name": "istio-system"}}}
                    ],
                    "ports": [
                        {"protocol": "TCP", "port": 8000},
                        {"protocol": "TCP", "port": 8080}
                    ]
                }
            ],
            egress_rules=[
                {
                    "to": [
                        {"podSelector": {"matchLabels": {"component": "backend"}}},
                        {"podSelector": {"matchLabels": {"component": "ai-processing"}}}
                    ],
                    "ports": [
                        {"protocol": "TCP", "port": 8000},
                        {"protocol": "TCP", "port": 8001}
                    ]
                },
                {
                    "to": [],  # External services
                    "ports": [
                        {"protocol": "TCP", "port": 443},  # HTTPS
                        {"protocol": "TCP", "port": 53},   # DNS
                        {"protocol": "UDP", "port": 53}    # DNS
                    ]
                }
            ],
            description="API gateway network access policy"
        )
    
    def create_backend_services_policy(self) -> NetworkPolicySpec:
        """Create policy for backend services"""
        return NetworkPolicySpec(
            name="backend-services-policy",
            namespace=self.namespace,
            policy_type=PolicyType.ALLOW_INGRESS,
            pod_selector={"matchLabels": {"component": "backend"}},
            ingress_rules=[
                {
                    "from": [
                        {"podSelector": {"matchLabels": {"component": "api-gateway"}}},
                        {"podSelector": {"matchLabels": {"component": "load-balancer"}}}
                    ],
                    "ports": [
                        {"protocol": "TCP", "port": 8000}
                    ]
                }
            ],
            egress_rules=[
                {
                    "to": [
                        {"podSelector": {"matchLabels": {"tier": "database"}}},
                        {"podSelector": {"matchLabels": {"component": "ai-processing"}}},
                        {"podSelector": {"matchLabels": {"component": "storage"}}}
                    ]
                },
                {
                    "to": [],  # External APIs
                    "ports": [
                        {"protocol": "TCP", "port": 443},
                        {"protocol": "TCP", "port": 80}
                    ]
                }
            ],
            description="Backend services communication policy"
        )
    
    def create_ai_processing_policy(self) -> NetworkPolicySpec:
        """Create policy for AI processing services"""
        return NetworkPolicySpec(
            name="ai-processing-policy",
            namespace=self.namespace,
            policy_type=PolicyType.ALLOW_INGRESS,
            pod_selector={"matchLabels": {"component": "ai-processing"}},
            ingress_rules=[
                {
                    "from": [
                        {"podSelector": {"matchLabels": {"component": "backend"}}},
                        {"podSelector": {"matchLabels": {"component": "api-gateway"}}}
                    ],
                    "ports": [
                        {"protocol": "TCP", "port": 8001}
                    ]
                }
            ],
            egress_rules=[
                {
                    "to": [
                        {"podSelector": {"matchLabels": {"tier": "database"}}},
                        {"podSelector": {"matchLabels": {"component": "storage"}}}
                    ]
                },
                {
                    "to": [],  # External ML APIs
                    "ports": [
                        {"protocol": "TCP", "port": 443}
                    ]
                }
            ],
            description="AI processing services network policy"
        )
    
    def create_monitoring_policy(self) -> NetworkPolicySpec:
        """Create policy for monitoring services"""
        return NetworkPolicySpec(
            name="monitoring-policy",
            namespace=self.namespace,
            policy_type=PolicyType.MONITORING,
            pod_selector={"matchLabels": {"component": "monitoring"}},
            ingress_rules=[
                {
                    "from": [
                        {"namespaceSelector": {"matchLabels": {"name": "monitoring"}}},
                        {"namespaceSelector": {"matchLabels": {"name": "prometheus"}}}
                    ],
                    "ports": [
                        {"protocol": "TCP", "port": 9090},  # Prometheus
                        {"protocol": "TCP", "port": 3000},  # Grafana
                        {"protocol": "TCP", "port": 8080}   # Metrics endpoint
                    ]
                }
            ],
            egress_rules=[
                {
                    "to": [],  # All pods for scraping metrics
                    "ports": [
                        {"protocol": "TCP", "port": 8080},  # Metrics
                        {"protocol": "TCP", "port": 9090}   # Prometheus
                    ]
                }
            ],
            description="Monitoring and observability network policy"
        )
    
    def create_storage_policy(self) -> NetworkPolicySpec:
        """Create policy for storage services"""
        return NetworkPolicySpec(
            name="storage-policy",
            namespace=self.namespace,
            policy_type=PolicyType.ALLOW_INGRESS,
            pod_selector={"matchLabels": {"component": "storage"}},
            ingress_rules=[
                {
                    "from": [
                        {"podSelector": {"matchLabels": {"component": "backend"}}},
                        {"podSelector": {"matchLabels": {"component": "ai-processing"}}}
                    ],
                    "ports": [
                        {"protocol": "TCP", "port": 9000},  # MinIO
                        {"protocol": "TCP", "port": 8080}   # Storage API
                    ]
                }
            ],
            description="Storage services network policy"
        )
    
    def generate_all_policies(self) -> Dict[str, NetworkPolicySpec]:
        """Generate all network policies"""
        policies = {
            "deny-all": self.create_deny_all_policy(),
            "database-access": self.create_database_access_policy(),
            "api-gateway": self.create_api_gateway_policy(),
            "backend-services": self.create_backend_services_policy(),
            "ai-processing": self.create_ai_processing_policy(),
            "monitoring": self.create_monitoring_policy(),
            "storage": self.create_storage_policy()
        }
        
        self.policies = policies
        return policies
    
    def to_yaml_manifest(self, policy: NetworkPolicySpec) -> str:
        """Convert policy to Kubernetes YAML manifest"""
        manifest = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": policy.name,
                "namespace": policy.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "network-policy",
                    "policy-type": policy.policy_type.value
                },
                "annotations": {
                    "description": policy.description
                }
            },
            "spec": {
                "podSelector": policy.pod_selector,
                "policyTypes": []
            }
        }
        
        # Add policy types and rules
        if policy.ingress_rules:
            manifest["spec"]["policyTypes"].append("Ingress")
            manifest["spec"]["ingress"] = policy.ingress_rules
        
        if policy.egress_rules:
            manifest["spec"]["policyTypes"].append("Egress")
            manifest["spec"]["egress"] = policy.egress_rules
        
        # For deny-all policy, just set policy types without rules
        if policy.policy_type == PolicyType.DENY_ALL:
            manifest["spec"]["policyTypes"] = ["Ingress", "Egress"]
        
        return yaml.dump(manifest, default_flow_style=False)
    
    def generate_all_manifests(self) -> Dict[str, str]:
        """Generate all network policy manifests"""
        policies = self.generate_all_policies()
        manifests = {}
        
        for name, policy in policies.items():
            manifests[f"{name}-network-policy"] = self.to_yaml_manifest(policy)
        
        return manifests
    
    def save_manifests_to_files(self, output_dir: str = "./k8s-manifests/network-policies"):
        """Save all network policy manifests to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        manifests = self.generate_all_manifests()
        
        for name, manifest in manifests.items():
            file_path = os.path.join(output_dir, f"{name}.yaml")
            with open(file_path, 'w') as f:
                f.write(manifest)
            logger.info(f"Network policy manifest saved: {file_path}")
        
        return len(manifests)


# Export main functionality
__all__ = ['NetworkPolicyManager', 'NetworkPolicySpec', 'PolicyType']