#!/usr/bin/env python3
"""
🔐 RBAC Template - iacherie Creator Economy Platform
==================================================

Role-Based Access Control (RBAC) Templates for Kubernetes and Creator Economy
Author: Fahed Mlaiel <mlaiel@live.de>
Expert Roles: Security Specialist + DevOps Engineer + Kubernetes Architect

⚠️ PROTECTION PROPRIÉTÉ INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de> - TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
"""

import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class CreatorRole(Enum):
    """Creator Economy specific roles"""
    CREATOR = "creator"
    PREMIUM_CREATOR = "premium-creator"
    VERIFIED_CREATOR = "verified-creator"
    COLLABORATION_MANAGER = "collaboration-manager"
    CONTENT_MODERATOR = "content-moderator"
    MONETIZATION_MANAGER = "monetization-manager"
    AI_SPECIALIST = "ai-specialist"
    ADMIN = "admin"
    SUPER_ADMIN = "super-admin"

class ResourceType(Enum):
    """Kubernetes resource types for Creator Economy"""
    CONTENT = "content"
    AI_MODELS = "ai-models"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    ANALYTICS = "analytics"
    CREATORS = "creators"
    SETTINGS = "settings"
    SYSTEM = "system"

class ActionType(Enum):
    """RBAC actions"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    WATCH = "watch"
    EXECUTE = "execute"
    APPROVE = "approve"
    MODERATE = "moderate"

@dataclass
class RBACConfig:
    """Configuration for RBAC generation"""
    namespace: str = "iacherie"
    environment: str = "production"
    enable_creator_economy_roles: bool = True
    enable_ai_processing_roles: bool = True
    enable_monetization_roles: bool = True
    enable_collaboration_roles: bool = True

class RBACTemplate:
    """
    Enterprise RBAC Template Generator for Creator Economy Platform
    
    Features:
    - Creator-specific roles and permissions
    - Multi-tier creator access (basic, premium, verified)
    - AI processing permissions
    - Monetization access control
    - Collaboration permissions
    - Content moderation roles
    - Kubernetes resource access control
    - Service account management
    """
    
    def __init__(self):
        self.template_version = "1.0.0"
        self.author = "Fahed Mlaiel <mlaiel@live.de>"
        
    def generate_rbac_manifests(self, config: RBACConfig) -> Dict[str, Any]:
        """Generate complete RBAC manifests for Creator Economy"""
        
        manifests = {
            "service_accounts": self._generate_service_accounts(config),
            "cluster_roles": self._generate_cluster_roles(config),
            "roles": self._generate_namespaced_roles(config),
            "cluster_role_bindings": self._generate_cluster_role_bindings(config),
            "role_bindings": self._generate_role_bindings(config),
            "pod_security_policies": self._generate_pod_security_policies(config),
            "network_policies": self._generate_network_policies(config)
        }
        
        return manifests
    
    def _generate_service_accounts(self, config: RBACConfig) -> List[Dict[str, Any]]:
        """Generate service accounts for Creator Economy services"""
        service_accounts = []
        
        # Core Creator Economy services
        services = [
            "creator-api",
            "ai-processor", 
            "monetization-service",
            "collaboration-service",
            "content-moderator",
            "analytics-service",
            "notification-service"
        ]
        
        for service in services:
            sa = {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": service,
                    "namespace": config.namespace,
                    "labels": {
                        "app.kubernetes.io/name": service,
                        "app.kubernetes.io/part-of": "iacherie-creator-economy",
                        "app.kubernetes.io/component": "service-account"
                    },
                    "annotations": {
                        "description": f"Service account for {service}",
                        "creator-economy/service-type": self._get_service_type(service)
                    }
                },
                "automountServiceAccountToken": True
            }
            service_accounts.append(sa)
        
        return service_accounts
    
    def _generate_cluster_roles(self, config: RBACConfig) -> List[Dict[str, Any]]:
        """Generate cluster roles for Creator Economy"""
        cluster_roles = []
        
        # Creator Economy Admin Role
        creator_admin_role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRole",
            "metadata": {
                "name": "iacherie-creator-admin",
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy",
                    "rbac.authorization.k8s.io/aggregate-to-admin": "true"
                }
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods", "services", "configmaps", "secrets"],
                    "verbs": ["*"]
                },
                {
                    "apiGroups": ["apps"],
                    "resources": ["deployments", "replicasets", "statefulsets"],
                    "verbs": ["*"]
                },
                {
                    "apiGroups": ["networking.k8s.io"],
                    "resources": ["ingresses", "networkpolicies"],
                    "verbs": ["*"]
                },
                {
                    "apiGroups": ["autoscaling"],
                    "resources": ["horizontalpodautoscalers"],
                    "verbs": ["*"]
                },
                {
                    "apiGroups": ["monitoring.coreos.com"],
                    "resources": ["servicemonitors", "prometheusrules"],
                    "verbs": ["*"]
                }
            ]
        }
        cluster_roles.append(creator_admin_role)
        
        # AI Processing Role
        ai_processor_role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRole",
            "metadata": {
                "name": "iacherie-ai-processor",
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy",
                    "creator-economy/role-type": "ai-processing"
                }
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods"],
                    "verbs": ["get", "list", "watch"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["configmaps"],
                    "resourceNames": ["ai-models-config", "processing-config"],
                    "verbs": ["get", "watch"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["secrets"],
                    "resourceNames": ["ai-api-keys", "model-registry-auth"],
                    "verbs": ["get"]
                },
                {
                    "apiGroups": ["batch"],
                    "resources": ["jobs"],
                    "verbs": ["create", "get", "list", "watch", "delete"]
                },
                {
                    "apiGroups": ["metrics.k8s.io"],
                    "resources": ["pods", "nodes"],
                    "verbs": ["get", "list"]
                }
            ]
        }
        cluster_roles.append(ai_processor_role)
        
        # Monetization Service Role
        monetization_role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRole",
            "metadata": {
                "name": "iacherie-monetization",
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy",
                    "creator-economy/role-type": "monetization"
                }
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["secrets"],
                    "resourceNames": [
                        "stripe-api-key", 
                        "paypal-credentials",
                        "bank-account-info"
                    ],
                    "verbs": ["get"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["configmaps"],
                    "resourceNames": ["monetization-config", "payment-gateway-config"],
                    "verbs": ["get", "watch"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["events"],
                    "verbs": ["create"]
                }
            ]
        }
        cluster_roles.append(monetization_role)
        
        # Content Viewer Role (for creators)
        content_viewer_role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRole",
            "metadata": {
                "name": "iacherie-content-viewer",
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy",
                    "creator-economy/role-type": "content-access"
                }
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods"],
                    "verbs": ["get", "list"],
                    "resourceNames": ["creator-api-*", "content-processor-*"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["services"],
                    "verbs": ["get", "list"],
                    "resourceNames": ["creator-api", "content-api"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["configmaps"],
                    "resourceNames": ["content-types-config"],
                    "verbs": ["get"]
                }
            ]
        }
        cluster_roles.append(content_viewer_role)
        
        return cluster_roles
    
    def _generate_namespaced_roles(self, config: RBACConfig) -> List[Dict[str, Any]]:
        """Generate namespace-specific roles"""
        roles = []
        
        # Creator Content Manager Role
        content_manager_role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": "creator-content-manager",
                "namespace": config.namespace,
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy",
                    "creator-economy/access-level": "content-management"
                }
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods"],
                    "verbs": ["get", "list", "watch", "create", "delete"],
                    "resourceNames": ["content-processor-*", "ai-enhancer-*"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["configmaps"],
                    "verbs": ["get", "list", "watch", "create", "update", "patch"],
                    "resourceNames": ["content-*", "processing-*"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["secrets"],
                    "verbs": ["get"],
                    "resourceNames": ["content-storage-*", "ai-api-*"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["persistentvolumeclaims"],
                    "verbs": ["get", "list", "watch", "create"],
                    "resourceNames": ["content-storage-*"]
                }
            ]
        }
        roles.append(content_manager_role)
        
        # Collaboration Manager Role
        collaboration_manager_role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": "collaboration-manager",
                "namespace": config.namespace,
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy",
                    "creator-economy/access-level": "collaboration-management"
                }
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods", "services"],
                    "verbs": ["get", "list", "watch"],
                    "resourceNames": ["collaboration-*", "messaging-*", "notification-*"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["configmaps"],
                    "verbs": ["get", "list", "watch", "update", "patch"],
                    "resourceNames": ["collaboration-*", "team-*", "project-*"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["events"],
                    "verbs": ["create", "get", "list"]
                }
            ]
        }
        roles.append(collaboration_manager_role)
        
        # Analytics Viewer Role
        analytics_viewer_role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": "analytics-viewer",
                "namespace": config.namespace,
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy",
                    "creator-economy/access-level": "analytics-read"
                }
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods", "services"],
                    "verbs": ["get", "list"],
                    "resourceNames": ["analytics-*", "metrics-*"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["configmaps"],
                    "verbs": ["get"],
                    "resourceNames": ["analytics-config", "dashboard-config"]
                }
            ]
        }
        roles.append(analytics_viewer_role)
        
        return roles
    
    def _generate_cluster_role_bindings(self, config: RBACConfig) -> List[Dict[str, Any]]:
        """Generate cluster role bindings"""
        bindings = []
        
        # Bind AI Processor service account to AI Processor role
        ai_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": {
                "name": "iacherie-ai-processor-binding",
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy"
                }
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "ai-processor",
                    "namespace": config.namespace
                }
            ],
            "roleRef": {
                "kind": "ClusterRole",
                "name": "iacherie-ai-processor",
                "apiGroup": "rbac.authorization.k8s.io"
            }
        }
        bindings.append(ai_binding)
        
        # Bind Monetization service account to Monetization role
        monetization_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": {
                "name": "iacherie-monetization-binding",
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy"
                }
            },
            "subjects": [
                {
                    "kind": "ServiceAccount", 
                    "name": "monetization-service",
                    "namespace": config.namespace
                }
            ],
            "roleRef": {
                "kind": "ClusterRole",
                "name": "iacherie-monetization",
                "apiGroup": "rbac.authorization.k8s.io"
            }
        }
        bindings.append(monetization_binding)
        
        # Bind Creator API to Content Viewer role
        creator_api_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding", 
            "metadata": {
                "name": "iacherie-creator-api-binding",
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy"
                }
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "creator-api",
                    "namespace": config.namespace
                }
            ],
            "roleRef": {
                "kind": "ClusterRole",
                "name": "iacherie-content-viewer",
                "apiGroup": "rbac.authorization.k8s.io"
            }
        }
        bindings.append(creator_api_binding)
        
        return bindings
    
    def _generate_role_bindings(self, config: RBACConfig) -> List[Dict[str, Any]]:
        """Generate namespace role bindings"""
        bindings = []
        
        # Creator API to Content Manager
        creator_content_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": "creator-content-manager-binding",
                "namespace": config.namespace,
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy"
                }
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "creator-api",
                    "namespace": config.namespace
                }
            ],
            "roleRef": {
                "kind": "Role",
                "name": "creator-content-manager", 
                "apiGroup": "rbac.authorization.k8s.io"
            }
        }
        bindings.append(creator_content_binding)
        
        # Collaboration Service to Collaboration Manager
        collaboration_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": "collaboration-manager-binding",
                "namespace": config.namespace,
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy"
                }
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "collaboration-service",
                    "namespace": config.namespace
                }
            ],
            "roleRef": {
                "kind": "Role",
                "name": "collaboration-manager",
                "apiGroup": "rbac.authorization.k8s.io"
            }
        }
        bindings.append(collaboration_binding)
        
        # Analytics Service to Analytics Viewer
        analytics_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": "analytics-viewer-binding",
                "namespace": config.namespace,
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy"
                }
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "analytics-service",
                    "namespace": config.namespace
                }
            ],
            "roleRef": {
                "kind": "Role",
                "name": "analytics-viewer",
                "apiGroup": "rbac.authorization.k8s.io"
            }
        }
        bindings.append(analytics_binding)
        
        return bindings
    
    def _generate_pod_security_policies(self, config: RBACConfig) -> List[Dict[str, Any]]:
        """Generate pod security policies for Creator Economy"""
        policies = []
        
        # Restricted policy for general services
        restricted_policy = {
            "apiVersion": "policy/v1beta1",
            "kind": "PodSecurityPolicy",
            "metadata": {
                "name": "iacherie-restricted",
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy",
                    "security-level": "restricted"
                }
            },
            "spec": {
                "privileged": False,
                "allowPrivilegeEscalation": False,
                "requiredDropCapabilities": ["ALL"],
                "volumes": [
                    "configMap",
                    "emptyDir", 
                    "projected",
                    "secret",
                    "downwardAPI",
                    "persistentVolumeClaim"
                ],
                "runAsUser": {
                    "rule": "MustRunAsNonRoot"
                },
                "seLinux": {
                    "rule": "RunAsAny"
                },
                "fsGroup": {
                    "rule": "RunAsAny"
                },
                "readOnlyRootFilesystem": True
            }
        }
        policies.append(restricted_policy)
        
        # Privileged policy for AI processing (GPU access)
        ai_privileged_policy = {
            "apiVersion": "policy/v1beta1",
            "kind": "PodSecurityPolicy",
            "metadata": {
                "name": "iacherie-ai-privileged",
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy",
                    "security-level": "ai-processing"
                }
            },
            "spec": {
                "privileged": False,
                "allowPrivilegeEscalation": False,
                "allowedCapabilities": ["SYS_ADMIN"],  # For GPU access
                "volumes": [
                    "configMap",
                    "emptyDir",
                    "projected", 
                    "secret",
                    "downwardAPI",
                    "persistentVolumeClaim",
                    "hostPath"  # For GPU device access
                ],
                "allowedHostPaths": [
                    {"pathPrefix": "/dev/nvidia", "readOnly": False}
                ],
                "runAsUser": {
                    "rule": "RunAsAny"
                },
                "seLinux": {
                    "rule": "RunAsAny"
                },
                "fsGroup": {
                    "rule": "RunAsAny"
                }
            }
        }
        policies.append(ai_privileged_policy)
        
        return policies
    
    def _generate_network_policies(self, config: RBACConfig) -> List[Dict[str, Any]]:
        """Generate network policies for Creator Economy services"""
        policies = []
        
        # Default deny all policy
        deny_all_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "iacherie-deny-all",
                "namespace": config.namespace,
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy"
                }
            },
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress", "Egress"]
            }
        }
        policies.append(deny_all_policy)
        
        # Creator API network policy
        creator_api_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "creator-api-network-policy",
                "namespace": config.namespace,
                "labels": {
                    "app.kubernetes.io/part-of": "iacherie-creator-economy"
                }
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {
                        "app.kubernetes.io/component": "creator-api"
                    }
                },
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "name": "ingress-nginx"
                                    }
                                }
                            }
                        ],
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
                        "to": [
                            {
                                "podSelector": {
                                    "matchLabels": {
                                        "app.kubernetes.io/component": "postgresql"
                                    }
                                }
                            }
                        ],
                        "ports": [
                            {
                                "protocol": "TCP",
                                "port": 5432
                            }
                        ]
                    },
                    {
                        "to": [
                            {
                                "podSelector": {
                                    "matchLabels": {
                                        "app.kubernetes.io/component": "redis"
                                    }
                                }
                            }
                        ],
                        "ports": [
                            {
                                "protocol": "TCP",
                                "port": 6379
                            }
                        ]
                    }
                ]
            }
        }
        policies.append(creator_api_policy)
        
        return policies
    
    def _get_service_type(self, service_name: str) -> str:
        """Get service type based on service name"""
        service_types = {
            "creator-api": "api",
            "ai-processor": "ai-processing",
            "monetization-service": "monetization",
            "collaboration-service": "collaboration",
            "content-moderator": "moderation",
            "analytics-service": "analytics",
            "notification-service": "notification"
        }
        return service_types.get(service_name, "unknown")
    
    def export_rbac_manifests(self, manifests: Dict[str, Any], output_dir: str = "rbac-manifests") -> str:
        """Export RBAC manifests to YAML files"""
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for manifest_type, manifest_list in manifests.items():
            if manifest_list:
                filename = f"{manifest_type}.yaml"
                file_path = output_path / filename
                
                with open(file_path, 'w') as f:
                    f.write("# Creator Economy RBAC Manifests\n")
                    f.write(f"# Type: {manifest_type}\n")
                    f.write(f"# Author: {self.author}\n")
                    f.write("# Generated for iacherie Creator Economy Platform\n\n")
                    
                    for i, manifest in enumerate(manifest_list):
                        if i > 0:
                            f.write("---\n")
                        yaml.dump(manifest, f, default_flow_style=False, indent=2)
                        f.write("\n")
        
        return str(output_path)

# Example usage
def main():
    """Example usage of RBAC Template"""
    template = RBACTemplate()
    
    # Generate RBAC for production environment
    config = RBACConfig(
        namespace="iacherie",
        environment="production",
        enable_creator_economy_roles=True,
        enable_ai_processing_roles=True,
        enable_monetization_roles=True,
        enable_collaboration_roles=True
    )
    
    manifests = template.generate_rbac_manifests(config)
    output_dir = template.export_rbac_manifests(manifests)
    
    print("🔐 RBAC Template - Generation Complete!")
    print(f"Generated RBAC manifests in: {output_dir}")
    
    for manifest_type, manifest_list in manifests.items():
        count = len(manifest_list) if manifest_list else 0
        print(f"  ✅ {manifest_type}: {count} manifests")

if __name__ == "__main__":
    main()