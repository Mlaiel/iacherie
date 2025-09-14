"""Pod Security Standards Implementation
=====================================

Kubernetes Pod Security Standards with strict enforcement
for the Ainflue platform security hardening.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Pod security standard levels"""
    PRIVILEGED = "privileged"
    BASELINE = "baseline"
    RESTRICTED = "restricted"


class EnforcementMode(Enum):
    """Pod security policy enforcement modes"""
    ENFORCE = "enforce"
    AUDIT = "audit"
    WARN = "warn"


@dataclass
class PodSecurityStandard:
    """Pod Security Standard configuration"""
    namespace: str
    level: SecurityLevel
    mode: EnforcementMode
    version: str = "latest"
    exemptions: List[str] = field(default_factory=list)


class PodSecurityManager:
    """Manages Pod Security Standards and enforcement"""
    
    def __init__(self, namespace -> None: str = "ia-influencer") -> None:
        self.namespace = namespace
        self.standards: Dict[str, PodSecurityStandard] = {}
    
    def create_restricted_standard(self, namespace: str) -> PodSecurityStandard:
        """Create restricted security standard (highest security)"""
        return PodSecurityStandard(
            namespace=namespace,
            level=SecurityLevel.RESTRICTED,
            mode=EnforcementMode.ENFORCE,
            exemptions=[]  # No exemptions for production
        )
    
    def create_baseline_standard(self, namespace: str) -> PodSecurityStandard:
        """Create baseline security standard (moderate security)"""
        return PodSecurityStandard(
            namespace=namespace,
            level=SecurityLevel.BASELINE,
            mode=EnforcementMode.ENFORCE,
            exemptions=["system:serviceaccount:kube-system:*"]
        )
    
    def generate_namespace_with_security_labels(self, 
                                               namespace: str,
                                               security_standard: PodSecurityStandard) -> Dict[str, Any]:
        """Generate namespace with Pod Security Standards labels"""
        return {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "pod-security.kubernetes.io/enforce": security_standard.level.value,
                    "pod-security.kubernetes.io/audit": security_standard.level.value,
                    "pod-security.kubernetes.io/warn": security_standard.level.value,
                    "pod-security.kubernetes.io/enforce-version": security_standard.version,
                    "pod-security.kubernetes.io/audit-version": security_standard.version,
                    "pod-security.kubernetes.io/warn-version": security_standard.version
                },
                "annotations": {
                    "description": f"Namespace with {security_standard.level.value} pod security standard"
                }
            }
        }
    
    def create_pod_security_policy(self, name: str, 
                                 security_level: SecurityLevel) -> Dict[str, Any]:
        """Create Pod Security Policy (for older Kubernetes versions)"""
        if security_level == SecurityLevel.RESTRICTED:
            return {
                "apiVersion": "policy/v1beta1",
                "kind": "PodSecurityPolicy",
                "metadata": {
                    "name": name,
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "security-level": security_level.value
                    }
                },
                "spec": {
                    "privileged": False,
                    "allowPrivilegeEscalation": False,
                    "requiredDropCapabilities": ["ALL"],
                    "allowedCapabilities": [],
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
                    "runAsGroup": {
                        "rule": "MustRunAs",
                        "ranges": [{"min": 1000, "max": 65535}]
                    },
                    "seLinux": {
                        "rule": "RunAsAny"
                    },
                    "fsGroup": {
                        "rule": "MustRunAs",
                        "ranges": [{"min": 1000, "max": 65535}]
                    },
                    "seccompProfile": {
                        "type": "RuntimeDefault"
                    },
                    "readOnlyRootFilesystem": True,
                    "forbiddenSysctls": ["*"],
                    "allowedProcMountTypes": ["Default"]
                }
            }
        
        elif security_level == SecurityLevel.BASELINE:
            return {
                "apiVersion": "policy/v1beta1",
                "kind": "PodSecurityPolicy",
                "metadata": {
                    "name": name,
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "security-level": security_level.value
                    }
                },
                "spec": {
                    "privileged": False,
                    "allowPrivilegeEscalation": True,
                    "requiredDropCapabilities": ["NET_RAW"],
                    "allowedCapabilities": ["CHOWN", "DAC_OVERRIDE", "FOWNER", "SETGID", "SETUID"],
                    "volumes": [
                        "configMap",
                        "emptyDir",
                        "projected",
                        "secret",
                        "downwardAPI",
                        "persistentVolumeClaim",
                        "hostPath"
                    ],
                    "runAsUser": {
                        "rule": "RunAsAny"
                    },
                    "runAsGroup": {
                        "rule": "RunAsAny"
                    },
                    "seLinux": {
                        "rule": "RunAsAny"
                    },
                    "fsGroup": {
                        "rule": "RunAsAny"
                    },
                    "readOnlyRootFilesystem": False
                }
            }
        
        else:  # PRIVILEGED
            return {
                "apiVersion": "policy/v1beta1",
                "kind": "PodSecurityPolicy",
                "metadata": {
                    "name": name,
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "security-level": security_level.value
                    }
                },
                "spec": {
                    "privileged": True,
                    "allowPrivilegeEscalation": True,
                    "allowedCapabilities": ["*"],
                    "volumes": ["*"],
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
    
    def create_security_context_constraints(self, name: str,
                                           security_level: SecurityLevel) -> Dict[str, Any]:
        """Create Security Context Constraints (OpenShift)"""
        if security_level == SecurityLevel.RESTRICTED:
            return {
                "apiVersion": "security.openshift.io/v1",
                "kind": "SecurityContextConstraints",
                "metadata": {
                    "name": name,
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "security-level": security_level.value
                    }
                },
                "allowHostDirVolumePlugin": False,
                "allowHostIPC": False,
                "allowHostNetwork": False,
                "allowHostPID": False,
                "allowHostPorts": False,
                "allowPrivilegedContainer": False,
                "allowedCapabilities": [],
                "defaultAddCapabilities": [],
                "requiredDropCapabilities": ["ALL"],
                "readOnlyRootFilesystem": True,
                "runAsUser": {
                    "type": "MustRunAsNonRoot"
                },
                "seLinuxContext": {
                    "type": "MustRunAs"
                },
                "fsGroup": {
                    "type": "MustRunAs",
                    "ranges": [{"min": 1000, "max": 65535}]
                },
                "volumes": [
                    "configMap",
                    "downwardAPI",
                    "emptyDir",
                    "persistentVolumeClaim",
                    "projected",
                    "secret"
                ]
            }
        
        return {}
    
    def create_restricted_deployment_template(self) -> Dict[str, Any]:
        """Create deployment template with restricted security context"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "secure-app-template",
                "namespace": self.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "security-profile": "restricted"
                }
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "secure-app"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "secure-app",
                            "security-profile": "restricted"
                        }
                    },
                    "spec": {
                        "serviceAccountName": "restricted-service-account",
                        "securityContext": {
                            "runAsNonRoot": True,
                            "runAsUser": 1000,
                            "runAsGroup": 1000,
                            "fsGroup": 1000,
                            "seccompProfile": {
                                "type": "RuntimeDefault"
                            }
                        },
                        "containers": [
                            {
                                "name": "app",
                                "image": "registry.example.com/ia-influencer/app:latest",
                                "securityContext": {
                                    "allowPrivilegeEscalation": False,
                                    "readOnlyRootFilesystem": True,
                                    "runAsNonRoot": True,
                                    "runAsUser": 1000,
                                    "runAsGroup": 1000,
                                    "capabilities": {
                                        "drop": ["ALL"]
                                    },
                                    "seccompProfile": {
                                        "type": "RuntimeDefault"
                                    }
                                },
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
                                "volumeMounts": [
                                    {
                                        "name": "tmp",
                                        "mountPath": "/tmp"
                                    },
                                    {
                                        "name": "app-cache",
                                        "mountPath": "/app/cache"
                                    }
                                ]
                            }
                        ],
                        "volumes": [
                            {
                                "name": "tmp",
                                "emptyDir": {}
                            },
                            {
                                "name": "app-cache",
                                "emptyDir": {}
                            }
                        ]
                    }
                }
            }
        }
    
    def create_service_account_with_rbac(self, name: str) -> List[Dict[str, Any]]:
        """Create service account with minimal RBAC permissions"""
        return [
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": name,
                    "namespace": self.namespace,
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "security-profile": "restricted"
                    }
                },
                "automountServiceAccountToken": False
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "Role",
                "metadata": {
                    "name": f"{name}-role",
                    "namespace": self.namespace
                },
                "rules": [
                    {
                        "apiGroups": [""],
                        "resources": ["configmaps", "secrets"],
                        "verbs": ["get", "list"]
                    }
                ]
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "RoleBinding",
                "metadata": {
                    "name": f"{name}-binding",
                    "namespace": self.namespace
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": name,
                        "namespace": self.namespace
                    }
                ],
                "roleRef": {
                    "kind": "Role",
                    "name": f"{name}-role",
                    "apiGroup": "rbac.authorization.k8s.io"
                }
            }
        ]
    
    def generate_all_security_manifests(self) -> Dict[str, str]:
        """Generate all pod security manifests"""
        manifests = {}
        
        # Production namespace with restricted security
        production_ns = self.generate_namespace_with_security_labels(
            self.namespace,
            self.create_restricted_standard(self.namespace)
        )
        manifests["production-namespace"] = yaml.dump(production_ns, default_flow_style=False)
        
        # Development namespace with baseline security
        dev_ns = self.generate_namespace_with_security_labels(
            f"{self.namespace}-dev",
            self.create_baseline_standard(f"{self.namespace}-dev")
        )
        manifests["development-namespace"] = yaml.dump(dev_ns, default_flow_style=False)
        
        # Pod Security Policies
        restricted_psp = self.create_pod_security_policy(
            "ia-influencer-restricted",
            SecurityLevel.RESTRICTED
        )
        manifests["restricted-pod-security-policy"] = yaml.dump(restricted_psp, default_flow_style=False)
        
        baseline_psp = self.create_pod_security_policy(
            "ia-influencer-baseline",
            SecurityLevel.BASELINE
        )
        manifests["baseline-pod-security-policy"] = yaml.dump(baseline_psp, default_flow_style=False)
        
        # Secure deployment template
        secure_deployment = self.create_restricted_deployment_template()
        manifests["secure-deployment-template"] = yaml.dump(secure_deployment, default_flow_style=False)
        
        # Service account with RBAC
        rbac_resources = self.create_service_account_with_rbac("restricted-service-account")
        for i, resource in enumerate(rbac_resources):
            manifests[f"rbac-{i+1}"] = yaml.dump(resource, default_flow_style=False)
        
        return manifests
    
    def save_manifests_to_files(self, output_dir -> None: str = "./k8s-manifests/pod-security") -> None:
        """Save all pod security manifests to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        manifests = self.generate_all_security_manifests()
        
        for name, manifest in manifests.items():
            file_path = os.path.join(output_dir, f"{name}.yaml")
            with open(file_path, 'w') as f:
                f.write(manifest)
            logger.info(f"Pod security manifest saved: {file_path}")
        
        return len(manifests)


# Export main functionality
__all__ = ['PodSecurityManager', 'PodSecurityStandard', 'SecurityLevel', 'EnforcementMode']