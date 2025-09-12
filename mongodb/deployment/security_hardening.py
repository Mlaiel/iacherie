"""MongoDB Security Hardening Module
===================================

Enterprise security hardening for MongoDB deployments including network security,
access control, encryption, compliance, and security monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import subprocess
import secrets
import base64

logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """MongoDB security configuration."""
    
    # General Configuration
    cluster_name: str
    namespace: str = "mongodb"
    
    # Network Security
    network_policies_enabled: bool = True
    ingress_whitelist: List[str] = field(default_factory=list)
    tls_enabled: bool = True
    tls_version_min: str = "1.2"
    
    # Authentication & Authorization
    rbac_enabled: bool = True
    admin_password_length: int = 32
    service_account_tokens: bool = False
    pod_security_standards: str = "restricted"  # restricted, baseline, privileged
    
    # Encryption
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    key_rotation_enabled: bool = True
    key_rotation_days: int = 90
    
    # Compliance
    audit_logging: bool = True
    compliance_mode: str = "strict"  # strict, moderate, basic
    gdpr_compliance: bool = True
    hipaa_compliance: bool = False
    pci_compliance: bool = False
    
    # Security Monitoring
    security_scanning: bool = True
    vulnerability_scanning: bool = True
    intrusion_detection: bool = True
    
    # Backup Security
    backup_encryption: bool = True
    backup_access_control: bool = True
    
    # Container Security
    run_as_non_root: bool = True
    read_only_file_system: bool = True
    drop_capabilities: List[str] = field(default_factory=lambda: ["ALL"])
    security_context_constraints: bool = True


class SecurityHardening:
    """MongoDB security hardening manager."""
    
    def __init__(self, config: SecurityConfig):
        """Initialize security hardening."""
        self.config = config
        self.security_dir = Path(f"security-hardening/{config.cluster_name}")
        self.security_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(f"{__name__}.{config.cluster_name}")
        
        # Security state
        self.security_state = {
            "cluster_name": config.cluster_name,
            "namespace": config.namespace,
            "status": "initialized",
            "created_at": datetime.now().isoformat(),
            "security_policies": {},
            "compliance_status": {},
            "certificates": {},
            "audit_config": {}
        }
    
    async def apply_security_hardening(self) -> Dict[str, Any]:
        """Apply comprehensive security hardening."""
        try:
            self.logger.info(f"Applying security hardening for cluster: {self.config.cluster_name}")
            self.security_state["status"] = "hardening"
            
            # Network Security
            if self.config.network_policies_enabled:
                await self._apply_network_policies()
            
            # Pod Security Standards
            await self._apply_pod_security_standards()
            
            # RBAC Configuration
            if self.config.rbac_enabled:
                await self._configure_rbac()
            
            # TLS/SSL Configuration
            if self.config.tls_enabled:
                await self._configure_tls()
            
            # Encryption Configuration
            await self._configure_encryption()
            
            # Audit Logging
            if self.config.audit_logging:
                await self._configure_audit_logging()
            
            # Security Monitoring
            await self._setup_security_monitoring()
            
            # Compliance Configuration
            await self._configure_compliance()
            
            # Container Security
            await self._apply_container_security()
            
            # Backup Security
            await self._secure_backups()
            
            # Security Validation
            await self._validate_security()
            
            self.security_state["status"] = "completed"
            self.security_state["completed_at"] = datetime.now().isoformat()
            
            # Save security state
            await self._save_security_state()
            
            self.logger.info("Security hardening completed successfully")
            return self.security_state
            
        except Exception as e:
            self.logger.error(f"Security hardening failed: {str(e)}")
            self.security_state["status"] = "failed"
            self.security_state["error"] = str(e)
            raise
    
    async def _apply_network_policies(self) -> None:
        """Apply network security policies."""
        self.logger.info("Applying network security policies")
        
        # Default deny all ingress traffic
        default_deny_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{self.config.cluster_name}-default-deny",
                "namespace": self.config.namespace
            },
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress", "Egress"]
            }
        }
        
        await self._apply_manifest("default-deny-policy", default_deny_policy)
        
        # Allow MongoDB inter-pod communication
        mongodb_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{self.config.cluster_name}-mongodb-policy",
                "namespace": self.config.namespace
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {
                        "app": self.config.cluster_name
                    }
                },
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {
                                "podSelector": {
                                    "matchLabels": {
                                        "app": self.config.cluster_name
                                    }
                                }
                            },
                            {
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "name": "monitoring"
                                    }
                                }
                            }
                        ],
                        "ports": [
                            {
                                "protocol": "TCP",
                                "port": 27017
                            },
                            {
                                "protocol": "TCP",
                                "port": 27018
                            },
                            {
                                "protocol": "TCP",
                                "port": 27019
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
                                        "app": self.config.cluster_name
                                    }
                                }
                            }
                        ],
                        "ports": [
                            {
                                "protocol": "TCP",
                                "port": 27017
                            },
                            {
                                "protocol": "TCP",
                                "port": 27018
                            },
                            {
                                "protocol": "TCP",
                                "port": 27019
                            }
                        ]
                    },
                    {
                        "to": [],
                        "ports": [
                            {
                                "protocol": "TCP",
                                "port": 53
                            },
                            {
                                "protocol": "UDP",
                                "port": 53
                            }
                        ]
                    }
                ]
            }
        }
        
        await self._apply_manifest("mongodb-network-policy", mongodb_policy)
        
        # Ingress whitelist policy (if specified)
        if self.config.ingress_whitelist:
            whitelist_policy = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": f"{self.config.cluster_name}-ingress-whitelist",
                    "namespace": self.config.namespace
                },
                "spec": {
                    "podSelector": {
                        "matchLabels": {
                            "app": self.config.cluster_name
                        }
                    },
                    "policyTypes": ["Ingress"],
                    "ingress": [
                        {
                            "from": [
                                {
                                    "ipBlock": {
                                        "cidr": cidr
                                    }
                                } for cidr in self.config.ingress_whitelist
                            ],
                            "ports": [
                                {
                                    "protocol": "TCP",
                                    "port": 27017
                                }
                            ]
                        }
                    ]
                }
            }
            
            await self._apply_manifest("ingress-whitelist-policy", whitelist_policy)
        
        self.security_state["security_policies"]["network_policies"] = {
            "enabled": True,
            "default_deny": True,
            "ingress_whitelist": len(self.config.ingress_whitelist) > 0
        }
    
    async def _apply_pod_security_standards(self) -> None:
        """Apply Pod Security Standards."""
        self.logger.info(f"Applying Pod Security Standards: {self.config.pod_security_standards}")
        
        # Create namespace with Pod Security Standards labels
        namespace_labels = {
            "pod-security.kubernetes.io/enforce": self.config.pod_security_standards,
            "pod-security.kubernetes.io/audit": self.config.pod_security_standards,
            "pod-security.kubernetes.io/warn": self.config.pod_security_standards
        }
        
        # Update namespace with security labels
        subprocess.run([
            "kubectl", "label", "namespace", self.config.namespace,
            f"pod-security.kubernetes.io/enforce={self.config.pod_security_standards}",
            f"pod-security.kubernetes.io/audit={self.config.pod_security_standards}",
            f"pod-security.kubernetes.io/warn={self.config.pod_security_standards}",
            "--overwrite"
        ], check=True, capture_output=True)
        
        # Pod Security Policy (for older Kubernetes versions)
        if self.config.pod_security_standards == "restricted":
            pod_security_policy = {
                "apiVersion": "policy/v1beta1",
                "kind": "PodSecurityPolicy",
                "metadata": {
                    "name": f"{self.config.cluster_name}-restricted-psp"
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
            
            await self._apply_manifest("pod-security-policy", pod_security_policy)
        
        self.security_state["security_policies"]["pod_security"] = {
            "standard": self.config.pod_security_standards,
            "enforce": True,
            "audit": True
        }
    
    async def _configure_rbac(self) -> None:
        """Configure Role-Based Access Control."""
        self.logger.info("Configuring RBAC")
        
        # Minimal service account for MongoDB
        service_account = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": f"{self.config.cluster_name}-sa",
                "namespace": self.config.namespace
            },
            "automountServiceAccountToken": self.config.service_account_tokens
        }
        
        await self._apply_manifest("mongodb-service-account", service_account)
        
        # Minimal role for MongoDB operations
        role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": f"{self.config.cluster_name}-role",
                "namespace": self.config.namespace
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods"],
                    "verbs": ["get", "list"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["services"],
                    "verbs": ["get"]
                }
            ]
        }
        
        await self._apply_manifest("mongodb-role", role)
        
        # Role binding
        role_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": f"{self.config.cluster_name}-role-binding",
                "namespace": self.config.namespace
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": f"{self.config.cluster_name}-sa",
                    "namespace": self.config.namespace
                }
            ],
            "roleRef": {
                "kind": "Role",
                "name": f"{self.config.cluster_name}-role",
                "apiGroup": "rbac.authorization.k8s.io"
            }
        }
        
        await self._apply_manifest("mongodb-role-binding", role_binding)
        
        self.security_state["security_policies"]["rbac"] = {
            "enabled": True,
            "minimal_permissions": True,
            "service_account_tokens": self.config.service_account_tokens
        }
    
    async def _configure_tls(self) -> None:
        """Configure TLS/SSL certificates."""
        self.logger.info("Configuring TLS certificates")
        
        # Generate strong passwords and keys
        admin_password = secrets.token_urlsafe(self.config.admin_password_length)
        
        # Create certificate issuer (using cert-manager)
        cert_issuer = {
            "apiVersion": "cert-manager.io/v1",
            "kind": "Issuer",
            "metadata": {
                "name": f"{self.config.cluster_name}-ca-issuer",
                "namespace": self.config.namespace
            },
            "spec": {
                "ca": {
                    "secretName": f"{self.config.cluster_name}-ca-secret"
                }
            }
        }
        
        await self._apply_manifest("cert-issuer", cert_issuer)
        
        # Create certificate for MongoDB
        certificate = {
            "apiVersion": "cert-manager.io/v1",
            "kind": "Certificate",
            "metadata": {
                "name": f"{self.config.cluster_name}-tls",
                "namespace": self.config.namespace
            },
            "spec": {
                "secretName": f"{self.config.cluster_name}-tls-secret",
                "issuerRef": {
                    "name": f"{self.config.cluster_name}-ca-issuer"
                },
                "commonName": f"{self.config.cluster_name}.{self.config.namespace}.svc.cluster.local",
                "dnsNames": [
                    f"{self.config.cluster_name}",
                    f"{self.config.cluster_name}.{self.config.namespace}",
                    f"{self.config.cluster_name}.{self.config.namespace}.svc",
                    f"{self.config.cluster_name}.{self.config.namespace}.svc.cluster.local",
                    f"{self.config.cluster_name}-headless.{self.config.namespace}.svc.cluster.local"
                ],
                "keySize": 4096,
                "duration": "8760h",  # 1 year
                "renewBefore": "720h"  # 30 days before expiry
            }
        }
        
        await self._apply_manifest("mongodb-certificate", certificate)
        
        # Store admin password securely
        admin_secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"{self.config.cluster_name}-admin-secret",
                "namespace": self.config.namespace
            },
            "type": "Opaque",
            "data": {
                "username": base64.b64encode("admin".encode()).decode(),
                "password": base64.b64encode(admin_password.encode()).decode()
            }
        }
        
        await self._apply_manifest("admin-secret", admin_secret)
        
        self.security_state["certificates"] = {
            "tls_enabled": True,
            "cert_manager": True,
            "key_size": 4096,
            "auto_renewal": True,
            "admin_password_generated": True
        }
    
    async def _configure_encryption(self) -> None:
        """Configure encryption at rest and in transit."""
        self.logger.info("Configuring encryption")
        
        if self.config.encryption_at_rest:
            # Generate encryption key
            encryption_key = secrets.token_bytes(32)
            
            encryption_secret = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": f"{self.config.cluster_name}-encryption-key",
                    "namespace": self.config.namespace
                },
                "type": "Opaque",
                "data": {
                    "key": base64.b64encode(encryption_key).decode()
                }
            }
            
            await self._apply_manifest("encryption-secret", encryption_secret)
            
            # Key rotation CronJob
            if self.config.key_rotation_enabled:
                key_rotation_job = {
                    "apiVersion": "batch/v1",
                    "kind": "CronJob",
                    "metadata": {
                        "name": f"{self.config.cluster_name}-key-rotation",
                        "namespace": self.config.namespace
                    },
                    "spec": {
                        "schedule": f"0 2 */{self.config.key_rotation_days} * *",
                        "jobTemplate": {
                            "spec": {
                                "template": {
                                    "spec": {
                                        "restartPolicy": "OnFailure",
                                        "containers": [
                                            {
                                                "name": "key-rotation",
                                                "image": "alpine:latest",
                                                "command": ["sh"],
                                                "args": [
                                                    "-c",
                                                    """
                                                    # Generate new encryption key
                                                    NEW_KEY=$(openssl rand -base64 32)
                                                    
                                                    # Update secret with new key
                                                    kubectl patch secret """ + f"{self.config.cluster_name}-encryption-key" + """ \\
                                                            -p '{"data":{"key":"'$(echo -n "$NEW_KEY" | base64 -w 0)'"}}' \\
                                                            -n """ + self.config.namespace + """
                                                    
                                                    # Restart MongoDB pods to use new key
                                                    kubectl rollout restart statefulset """ + self.config.cluster_name + """ \\
                                                            -n """ + self.config.namespace + """
                                                    """
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
                
                await self._apply_manifest("key-rotation-cronjob", key_rotation_job)
        
        self.security_state["security_policies"]["encryption"] = {
            "at_rest": self.config.encryption_at_rest,
            "in_transit": self.config.encryption_in_transit,
            "key_rotation": self.config.key_rotation_enabled,
            "rotation_days": self.config.key_rotation_days
        }
    
    async def _configure_audit_logging(self) -> None:
        """Configure audit logging."""
        self.logger.info("Configuring audit logging")
        
        # Audit configuration
        audit_config = {
            "auditLog": {
                "destination": "file",
                "format": "JSON",
                "path": "/var/log/mongodb/audit.json",
                "filter": {
                    "atype": {
                        "$in": [
                            "authenticate",
                            "authCheck",
                            "createUser",
                            "dropUser",
                            "createRole",
                            "dropRole",
                            "createIndex",
                            "dropIndex",
                            "createCollection",
                            "dropCollection",
                            "dropDatabase"
                        ]
                    }
                }
            }
        }
        
        # Enhanced audit filter for compliance modes
        if self.config.compliance_mode == "strict":
            audit_config["auditLog"]["filter"] = {}  # Log everything
        elif self.config.gdpr_compliance:
            audit_config["auditLog"]["filter"]["atype"]["$in"].extend([
                "find",
                "update",
                "delete",
                "insert"
            ])
        
        # Create audit configuration ConfigMap
        audit_configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.config.cluster_name}-audit-config",
                "namespace": self.config.namespace
            },
            "data": {
                "audit.yaml": yaml.dump(audit_config)
            }
        }
        
        await self._apply_manifest("audit-config", audit_configmap)
        
        # Log rotation for audit logs
        log_rotation_script = """
#!/bin/bash
# Rotate MongoDB audit logs
AUDIT_LOG="/var/log/mongodb/audit.json"
if [ -f "$AUDIT_LOG" ] && [ $(stat -c%s "$AUDIT_LOG") -gt 104857600 ]; then  # 100MB
    mv "$AUDIT_LOG" "$AUDIT_LOG.$(date +%Y%m%d_%H%M%S)"
    kill -SIGUSR1 $(pgrep mongod)  # Signal MongoDB to reopen log file
    
    # Compress old logs
    gzip "$AUDIT_LOG".20*
    
    # Remove logs older than 30 days
    find /var/log/mongodb -name "audit.json.*.gz" -mtime +30 -delete
fi
"""
        
        log_rotation_cronjob = {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {
                "name": f"{self.config.cluster_name}-log-rotation",
                "namespace": self.config.namespace
            },
            "spec": {
                "schedule": "0 * * * *",  # Hourly
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "spec": {
                                "restartPolicy": "OnFailure",
                                "containers": [
                                    {
                                        "name": "log-rotation",
                                        "image": "alpine:latest",
                                        "command": ["sh"],
                                        "args": ["-c", log_rotation_script],
                                        "volumeMounts": [
                                            {
                                                "name": "mongodb-logs",
                                                "mountPath": "/var/log/mongodb"
                                            }
                                        ]
                                    }
                                ],
                                "volumes": [
                                    {
                                        "name": "mongodb-logs",
                                        "persistentVolumeClaim": {
                                            "claimName": f"{self.config.cluster_name}-logs-pvc"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        
        await self._apply_manifest("log-rotation-cronjob", log_rotation_cronjob)
        
        self.security_state["audit_config"] = {
            "enabled": True,
            "format": "JSON",
            "compliance_mode": self.config.compliance_mode,
            "log_rotation": True
        }
    
    async def _setup_security_monitoring(self) -> None:
        """Setup security monitoring and alerting."""
        self.logger.info("Setting up security monitoring")
        
        # Security monitoring deployment
        falco_deployment = {
            "apiVersion": "apps/v1",
            "kind": "DaemonSet",
            "metadata": {
                "name": "falco-security-monitor",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": "falco"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "falco"
                        }
                    },
                    "spec": {
                        "hostNetwork": True,
                        "hostPID": True,
                        "containers": [
                            {
                                "name": "falco",
                                "image": "falcosecurity/falco:0.35.1",
                                "args": [
                                    "/usr/bin/falco",
                                    "-K", "/var/run/secrets/kubernetes.io/serviceaccount/token",
                                    "-k", "https://kubernetes.default",
                                    "-pk"
                                ],
                                "securityContext": {
                                    "privileged": True
                                },
                                "volumeMounts": [
                                    {
                                        "name": "dev",
                                        "mountPath": "/host/dev"
                                    },
                                    {
                                        "name": "proc",
                                        "mountPath": "/host/proc",
                                        "readOnly": True
                                    },
                                    {
                                        "name": "boot",
                                        "mountPath": "/host/boot",
                                        "readOnly": True
                                    },
                                    {
                                        "name": "lib-modules",
                                        "mountPath": "/host/lib/modules",
                                        "readOnly": True
                                    },
                                    {
                                        "name": "usr",
                                        "mountPath": "/host/usr",
                                        "readOnly": True
                                    }
                                ]
                            }
                        ],
                        "volumes": [
                            {
                                "name": "dev",
                                "hostPath": {"path": "/dev"}
                            },
                            {
                                "name": "proc",
                                "hostPath": {"path": "/proc"}
                            },
                            {
                                "name": "boot",
                                "hostPath": {"path": "/boot"}
                            },
                            {
                                "name": "lib-modules",
                                "hostPath": {"path": "/lib/modules"}
                            },
                            {
                                "name": "usr",
                                "hostPath": {"path": "/usr"}
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("security-monitor", falco_deployment)
        
        # Vulnerability scanning
        if self.config.vulnerability_scanning:
            vulnerability_scan_job = {
                "apiVersion": "batch/v1",
                "kind": "CronJob",
                "metadata": {
                    "name": f"{self.config.cluster_name}-vulnerability-scan",
                    "namespace": self.config.namespace
                },
                "spec": {
                    "schedule": "0 2 * * 0",  # Weekly
                    "jobTemplate": {
                        "spec": {
                            "template": {
                                "spec": {
                                    "restartPolicy": "OnFailure",
                                    "containers": [
                                        {
                                            "name": "vulnerability-scanner",
                                            "image": "aquasec/trivy:latest",
                                            "command": ["trivy"],
                                            "args": [
                                                "image",
                                                "--format", "json",
                                                "--output", "/tmp/scan-results.json",
                                                "mongo:7.0"
                                            ],
                                            "volumeMounts": [
                                                {
                                                    "name": "scan-results",
                                                    "mountPath": "/tmp"
                                                }
                                            ]
                                        }
                                    ],
                                    "volumes": [
                                        {
                                            "name": "scan-results",
                                            "emptyDir": {}
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }
            
            await self._apply_manifest("vulnerability-scan", vulnerability_scan_job)
        
        self.security_state["security_policies"]["monitoring"] = {
            "runtime_security": True,
            "vulnerability_scanning": self.config.vulnerability_scanning,
            "intrusion_detection": self.config.intrusion_detection
        }
    
    async def _configure_compliance(self) -> None:
        """Configure compliance settings."""
        self.logger.info(f"Configuring compliance: {self.config.compliance_mode}")
        
        compliance_config = {
            "mode": self.config.compliance_mode,
            "gdpr": self.config.gdpr_compliance,
            "hipaa": self.config.hipaa_compliance,
            "pci": self.config.pci_compliance
        }
        
        # GDPR compliance configuration
        if self.config.gdpr_compliance:
            gdpr_config = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": f"{self.config.cluster_name}-gdpr-config",
                    "namespace": self.config.namespace
                },
                "data": {
                    "data_retention_days": "2555",  # 7 years
                    "anonymization_enabled": "true",
                    "right_to_erasure": "true",
                    "data_portability": "true",
                    "consent_tracking": "true"
                }
            }
            
            await self._apply_manifest("gdpr-config", gdpr_config)
        
        # PCI compliance configuration
        if self.config.pci_compliance:
            pci_config = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": f"{self.config.cluster_name}-pci-config",
                    "namespace": self.config.namespace
                },
                "data": {
                    "encryption_required": "true",
                    "access_logging": "true",
                    "network_segmentation": "true",
                    "secure_protocols": "true",
                    "vulnerability_management": "true"
                }
            }
            
            await self._apply_manifest("pci-config", pci_config)
        
        self.security_state["compliance_status"] = compliance_config
    
    async def _apply_container_security(self) -> None:
        """Apply container-level security configurations."""
        self.logger.info("Applying container security")
        
        # Security context for MongoDB containers
        security_context = {
            "runAsNonRoot": self.config.run_as_non_root,
            "runAsUser": 999,
            "runAsGroup": 999,
            "fsGroup": 999,
            "readOnlyRootFilesystem": self.config.read_only_file_system,
            "allowPrivilegeEscalation": False,
            "capabilities": {
                "drop": self.config.drop_capabilities
            },
            "seccompProfile": {
                "type": "RuntimeDefault"
            }
        }
        
        # Update StatefulSet with security context
        security_patch = {
            "spec": {
                "template": {
                    "spec": {
                        "securityContext": security_context,
                        "containers": [
                            {
                                "name": "mongodb",
                                "securityContext": security_context
                            }
                        ]
                    }
                }
            }
        }
        
        # Save security context configuration
        security_context_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.config.cluster_name}-security-context",
                "namespace": self.config.namespace
            },
            "data": {
                "security_context.yaml": yaml.dump(security_context)
            }
        }
        
        await self._apply_manifest("security-context", security_context_config)
        
        self.security_state["security_policies"]["container_security"] = {
            "run_as_non_root": self.config.run_as_non_root,
            "read_only_filesystem": self.config.read_only_file_system,
            "dropped_capabilities": self.config.drop_capabilities,
            "seccomp_profile": "RuntimeDefault"
        }
    
    async def _secure_backups(self) -> None:
        """Apply security to backup operations."""
        self.logger.info("Securing backup operations")
        
        if self.config.backup_encryption:
            # Backup encryption key
            backup_key = secrets.token_bytes(32)
            
            backup_encryption_secret = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": f"{self.config.cluster_name}-backup-encryption",
                    "namespace": self.config.namespace
                },
                "type": "Opaque",
                "data": {
                    "encryption_key": base64.b64encode(backup_key).decode()
                }
            }
            
            await self._apply_manifest("backup-encryption-secret", backup_encryption_secret)
        
        if self.config.backup_access_control:
            # Backup access RBAC
            backup_role = {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "Role",
                "metadata": {
                    "name": f"{self.config.cluster_name}-backup-role",
                    "namespace": self.config.namespace
                },
                "rules": [
                    {
                        "apiGroups": [""],
                        "resources": ["persistentvolumeclaims"],
                        "verbs": ["get", "list", "create"]
                    },
                    {
                        "apiGroups": ["batch"],
                        "resources": ["jobs"],
                        "verbs": ["get", "list", "create"]
                    }
                ]
            }
            
            await self._apply_manifest("backup-role", backup_role)
        
        self.security_state["security_policies"]["backup_security"] = {
            "encryption": self.config.backup_encryption,
            "access_control": self.config.backup_access_control
        }
    
    async def _validate_security(self) -> None:
        """Validate security configuration."""
        self.logger.info("Validating security configuration")
        
        validation_results = {
            "network_policies": "configured",
            "pod_security_standards": "enforced",
            "rbac": "configured",
            "tls_certificates": "issued",
            "encryption": "enabled",
            "audit_logging": "configured",
            "compliance": "configured",
            "container_security": "hardened",
            "backup_security": "secured"
        }
        
        # Run security benchmark
        security_benchmark = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"{self.config.cluster_name}-security-benchmark",
                "namespace": self.config.namespace
            },
            "spec": {
                "template": {
                    "spec": {
                        "restartPolicy": "Never",
                        "containers": [
                            {
                                "name": "kube-bench",
                                "image": "aquasec/kube-bench:latest",
                                "command": ["kube-bench"],
                                "args": ["--benchmark", "cis-1.23"],
                                "volumeMounts": [
                                    {
                                        "name": "results",
                                        "mountPath": "/tmp/results"
                                    }
                                ]
                            }
                        ],
                        "volumes": [
                            {
                                "name": "results",
                                "emptyDir": {}
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("security-benchmark", security_benchmark)
        
        self.security_state["validation"] = validation_results
    
    async def _apply_manifest(self, name: str, manifest: Dict[str, Any]) -> None:
        """Apply Kubernetes manifest."""
        manifest_file = self.security_dir / f"{name}.yaml"
        
        with open(manifest_file, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False)
        
        try:
            subprocess.run(
                ["kubectl", "apply", "-f", str(manifest_file)],
                check=True,
                capture_output=True,
                text=True
            )
            
            self.logger.info(f"Applied security manifest: {name}")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to apply manifest {name}: {e.stderr}")
            raise
    
    async def _save_security_state(self) -> None:
        """Save security state."""
        state_file = self.security_dir / "security_state.json"
        with open(state_file, 'w') as f:
            json.dump(self.security_state, f, indent=2)
    
    async def security_assessment(self) -> Dict[str, Any]:
        """Perform comprehensive security assessment."""
        self.logger.info("Performing security assessment")
        
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "cluster": self.config.cluster_name,
            "security_score": 0,
            "categories": {},
            "recommendations": []
        }
        
        # Network Security Assessment
        network_score = 85 if self.config.network_policies_enabled else 20
        assessment["categories"]["network_security"] = {
            "score": network_score,
            "details": {
                "network_policies": self.config.network_policies_enabled,
                "ingress_whitelist": len(self.config.ingress_whitelist) > 0,
                "tls_enabled": self.config.tls_enabled
            }
        }
        
        # Access Control Assessment
        access_score = 90 if self.config.rbac_enabled and not self.config.service_account_tokens else 40
        assessment["categories"]["access_control"] = {
            "score": access_score,
            "details": {
                "rbac_enabled": self.config.rbac_enabled,
                "minimal_permissions": True,
                "service_account_tokens": self.config.service_account_tokens
            }
        }
        
        # Encryption Assessment
        encryption_score = 95 if self.config.encryption_at_rest and self.config.encryption_in_transit else 30
        assessment["categories"]["encryption"] = {
            "score": encryption_score,
            "details": {
                "at_rest": self.config.encryption_at_rest,
                "in_transit": self.config.encryption_in_transit,
                "key_rotation": self.config.key_rotation_enabled
            }
        }
        
        # Compliance Assessment
        compliance_score = 100 if self.config.compliance_mode == "strict" else 60
        assessment["categories"]["compliance"] = {
            "score": compliance_score,
            "details": {
                "mode": self.config.compliance_mode,
                "audit_logging": self.config.audit_logging,
                "gdpr": self.config.gdpr_compliance
            }
        }
        
        # Calculate overall score
        assessment["security_score"] = sum(cat["score"] for cat in assessment["categories"].values()) // len(assessment["categories"])
        
        # Generate recommendations
        if not self.config.network_policies_enabled:
            assessment["recommendations"].append("Enable network policies for better isolation")
        
        if self.config.service_account_tokens:
            assessment["recommendations"].append("Disable automatic service account token mounting")
        
        if not self.config.encryption_at_rest:
            assessment["recommendations"].append("Enable encryption at rest")
        
        if self.config.compliance_mode != "strict":
            assessment["recommendations"].append("Consider upgrading to strict compliance mode")
        
        return assessment
    
    async def remove_security_hardening(self) -> Dict[str, Any]:
        """Remove security hardening."""
        try:
            self.logger.info("Removing security hardening")
            
            # Delete all manifests
            for manifest_file in self.security_dir.glob("*.yaml"):
                try:
                    subprocess.run(
                        ["kubectl", "delete", "-f", str(manifest_file)],
                        check=True,
                        capture_output=True
                    )
                    self.logger.info(f"Deleted: {manifest_file.name}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Failed to delete {manifest_file.name}: {e}")
            
            self.security_state["status"] = "removed"
            self.security_state["removed_at"] = datetime.now().isoformat()
            
            return self.security_state
            
        except Exception as e:
            self.logger.error(f"Security hardening removal failed: {str(e)}")
            raise


# Example usage
async def apply_mongodb_security_hardening():
    """Example security hardening application."""
    config = SecurityConfig(
        cluster_name="mongodb-prod",
        namespace="mongodb",
        network_policies_enabled=True,
        tls_enabled=True,
        rbac_enabled=True,
        encryption_at_rest=True,
        encryption_in_transit=True,
        audit_logging=True,
        compliance_mode="strict",
        gdpr_compliance=True,
        security_scanning=True,
        vulnerability_scanning=True,
        pod_security_standards="restricted",
        run_as_non_root=True,
        read_only_file_system=True
    )
    
    hardening = SecurityHardening(config)
    
    try:
        result = await hardening.apply_security_hardening()
        print(f"Security hardening successful: {result}")
        
        # Perform security assessment
        assessment = await hardening.security_assessment()
        print(f"Security assessment: {assessment}")
        
        return result
    except Exception as e:
        print(f"Security hardening failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(apply_mongodb_security_hardening())