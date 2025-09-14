"""Ingress Controller with Automatic TLS Management
===============================================

Kubernetes Ingress Controller configuration with cert-manager
for automatic TLS certificate management for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IngressControllerType(Enum):
    """Ingress controller types"""
    NGINX = "nginx"
    TRAEFIK = "traefik"
    ISTIO = "istio"
    CONTOUR = "contour"


class CertificateIssuer(Enum):
    """Certificate issuer types"""
    LETS_ENCRYPT = "letsencrypt"
    LETS_ENCRYPT_STAGING = "letsencrypt-staging"
    SELF_SIGNED = "self-signed"
    CA_ISSUER = "ca-issuer"


@dataclass
class TLSConfig:
    """TLS configuration"""
    enabled: bool = True
    issuer_type: CertificateIssuer = CertificateIssuer.LETS_ENCRYPT
    email: str = "admin@ainflue.com"
    domains: List[str] = field(default_factory=lambda: ["*.ainflue.com", "ainflue.com"])
    staging: bool = False


@dataclass
class IngressConfig:
    """Ingress configuration"""
    name: str
    namespace: str = "ia-influencer"
    controller_type: IngressControllerType = IngressControllerType.NGINX
    tls_config: TLSConfig = field(default_factory=TLSConfig)
    annotations: Dict[str, str] = field(default_factory=dict)


class IngressTLSManager:
    """Manages Ingress Controller with automatic TLS"""
    
    def __init__(self, config -> None: IngressConfig) -> None:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def create_cert_manager_installation(self) -> Dict[str, Any]:
        """Create cert-manager installation"""
        return {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": {
                "name": "cert-manager",
                "namespace": "argocd"
            },
            "spec": {
                "project": "default",
                "source": {
                    "repoURL": "https://charts.jetstack.io",
                    "chart": "cert-manager",
                    "targetRevision": "v1.13.x",
                    "helm": {
                        "values": yaml.dump({
                            "installCRDs": True,
                            "replicaCount": 2,
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
                            "webhook": {
                                "replicaCount": 2,
                                "resources": {
                                    "requests": {
                                        "cpu": "50m",
                                        "memory": "64Mi"
                                    },
                                    "limits": {
                                        "cpu": "200m",
                                        "memory": "256Mi"
                                    }
                                }
                            },
                            "cainjector": {
                                "replicaCount": 2,
                                "resources": {
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "128Mi"
                                    },
                                    "limits": {
                                        "cpu": "500m",
                                        "memory": "512Mi"
                                    }
                                }
                            },
                            "podDisruptionBudget": {
                                "enabled": True,
                                "minAvailable": 1
                            }
                        }, default_flow_style=False)
                    }
                },
                "destination": {
                    "server": "https://kubernetes.default.svc",
                    "namespace": "cert-manager"
                },
                "syncPolicy": {
                    "automated": {
                        "prune": True,
                        "selfHeal": True
                    },
                    "syncOptions": [
                        "CreateNamespace=true"
                    ]
                }
            }
        }
    
    def create_cluster_issuer(self, issuer_type: CertificateIssuer) -> Dict[str, Any]:
        """Create ClusterIssuer for certificate management"""
        if issuer_type in [CertificateIssuer.LETS_ENCRYPT, CertificateIssuer.LETS_ENCRYPT_STAGING]:
            server = "https://acme-v02.api.letsencrypt.org/directory"
            if issuer_type == CertificateIssuer.LETS_ENCRYPT_STAGING:
                server = "https://acme-staging-v02.api.letsencrypt.org/directory"
            
            return {
                "apiVersion": "cert-manager.io/v1",
                "kind": "ClusterIssuer",
                "metadata": {
                    "name": issuer_type.value,
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "cert-manager"
                    }
                },
                "spec": {
                    "acme": {
                        "server": server,
                        "email": self.config.tls_config.email,
                        "privateKeySecretRef": {
                            "name": f"{issuer_type.value}-private-key"
                        },
                        "solvers": [
                            {
                                "http01": {
                                    "ingress": {
                                        "class": "nginx"
                                    }
                                }
                            },
                            {
                                "dns01": {
                                    "route53": {
                                        "region": "us-east-1",
                                        "accessKeyID": "AKIAIOSFODNN7EXAMPLE",
                                        "secretAccessKeySecretRef": {
                                            "name": "route53-credentials",
                                            "key": "secret-access-key"
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        
        elif issuer_type == CertificateIssuer.SELF_SIGNED:
            return {
                "apiVersion": "cert-manager.io/v1",
                "kind": "ClusterIssuer",
                "metadata": {
                    "name": issuer_type.value,
                    "labels": {
                        "app.kubernetes.io/name": "ia-influencer",
                        "app.kubernetes.io/component": "cert-manager"
                    }
                },
                "spec": {
                    "selfSigned": {}
                }
            }
        
        return {}
    
    def create_wildcard_certificate(self) -> Dict[str, Any]:
        """Create wildcard certificate for the domain"""
        return {
            "apiVersion": "cert-manager.io/v1",
            "kind": "Certificate",
            "metadata": {
                "name": "ainflue-wildcard-cert",
                "namespace": self.config.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "certificate"
                }
            },
            "spec": {
                "secretName": "ainflue-wildcard-tls",
                "issuerRef": {
                    "name": self.config.tls_config.issuer_type.value,
                    "kind": "ClusterIssuer"
                },
                "dnsNames": self.config.tls_config.domains,
                "usages": [
                    "digital signature",
                    "key encipherment"
                ]
            }
        }
    
    def create_nginx_ingress_controller(self) -> Dict[str, Any]:
        """Create NGINX Ingress Controller"""
        return {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": {
                "name": "nginx-ingress",
                "namespace": "argocd"
            },
            "spec": {
                "project": "default",
                "source": {
                    "repoURL": "https://kubernetes.github.io/ingress-nginx",
                    "chart": "ingress-nginx",
                    "targetRevision": "4.8.x",
                    "helm": {
                        "values": yaml.dump({
                            "controller": {
                                "replicaCount": 3,
                                "metrics": {
                                    "enabled": True,
                                    "serviceMonitor": {
                                        "enabled": True
                                    }
                                },
                                "config": {
                                    "use-http2": "true",
                                    "ssl-protocols": "TLSv1.2 TLSv1.3",
                                    "ssl-ciphers": "ECDHE-ECDSA-AES128-GCM-SHA256,ECDHE-RSA-AES128-GCM-SHA256,ECDHE-ECDSA-AES256-GCM-SHA384,ECDHE-RSA-AES256-GCM-SHA384",
                                    "enable-real-ip": "true",
                                    "proxy-real-ip-cidr": "0.0.0.0/0",
                                    "use-forwarded-headers": "true",
                                    "compute-full-forwarded-for": "true",
                                    "hsts": "true",
                                    "hsts-max-age": "31536000",
                                    "hsts-include-subdomains": "true",
                                    "hsts-preload": "true",
                                    "server-tokens": "false",
                                    "client-header-buffer-size": "64k",
                                    "large-client-header-buffers": "4 64k",
                                    "proxy-buffer-size": "16k",
                                    "proxy-body-size": "50m"
                                },
                                "service": {
                                    "type": "LoadBalancer",
                                    "annotations": {
                                        "service.beta.kubernetes.io/aws-load-balancer-type": "nlb",
                                        "service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled": "true",
                                        "service.beta.kubernetes.io/aws-load-balancer-backend-protocol": "tcp"
                                    }
                                },
                                "resources": {
                                    "requests": {
                                        "cpu": "200m",
                                        "memory": "256Mi"
                                    },
                                    "limits": {
                                        "cpu": "1000m",
                                        "memory": "1Gi"
                                    }
                                },
                                "autoscaling": {
                                    "enabled": True,
                                    "minReplicas": 3,
                                    "maxReplicas": 10,
                                    "targetCPUUtilizationPercentage": 70,
                                    "targetMemoryUtilizationPercentage": 80
                                },
                                "podDisruptionBudget": {
                                    "enabled": True,
                                    "minAvailable": 2
                                },
                                "affinity": {
                                    "podAntiAffinity": {
                                        "requiredDuringSchedulingIgnoredDuringExecution": [
                                            {
                                                "labelSelector": {
                                                    "matchExpressions": [
                                                        {
                                                            "key": "app.kubernetes.io/name",
                                                            "operator": "In",
                                                            "values": ["ingress-nginx"]
                                                        }
                                                    ]
                                                },
                                                "topologyKey": "kubernetes.io/hostname"
                                            }
                                        ]
                                    }
                                }
                            },
                            "defaultBackend": {
                                "enabled": True,
                                "image": {
                                    "repository": "defaultbackend-amd64",
                                    "tag": "1.5"
                                }
                            }
                        }, default_flow_style=False)
                    }
                },
                "destination": {
                    "server": "https://kubernetes.default.svc",
                    "namespace": "nginx-ingress"
                },
                "syncPolicy": {
                    "automated": {
                        "prune": True,
                        "selfHeal": True
                    },
                    "syncOptions": [
                        "CreateNamespace=true"
                    ]
                }
            }
        }
    
    def create_main_ingress(self) -> Dict[str, Any]:
        """Create main ingress for the application"""
        annotations = {
            "kubernetes.io/ingress.class": "nginx",
            "cert-manager.io/cluster-issuer": self.config.tls_config.issuer_type.value,
            "nginx.ingress.kubernetes.io/ssl-redirect": "true",
            "nginx.ingress.kubernetes.io/force-ssl-redirect": "true",
            "nginx.ingress.kubernetes.io/use-regex": "true",
            "nginx.ingress.kubernetes.io/proxy-body-size": "50m",
            "nginx.ingress.kubernetes.io/proxy-read-timeout": "300",
            "nginx.ingress.kubernetes.io/proxy-send-timeout": "300",
            "nginx.ingress.kubernetes.io/proxy-connect-timeout": "300",
            "nginx.ingress.kubernetes.io/configuration-snippet": """
                more_set_headers "X-Frame-Options: SAMEORIGIN";
                more_set_headers "X-Content-Type-Options: nosniff";
                more_set_headers "X-XSS-Protection: 1; mode=block";
                more_set_headers "Referrer-Policy: strict-origin-when-cross-origin";
                more_set_headers "Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: https:; media-src 'self' blob:; object-src 'none'; frame-ancestors 'self'";
            """.strip(),
            "nginx.ingress.kubernetes.io/rate-limit": "100",
            "nginx.ingress.kubernetes.io/rate-limit-window": "1m"
        }
        
        annotations.update(self.config.annotations)
        
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{self.config.name}-ingress",
                "namespace": self.config.namespace,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "ingress"
                },
                "annotations": annotations
            },
            "spec": {
                "tls": [
                    {
                        "hosts": self.config.tls_config.domains,
                        "secretName": "ainflue-wildcard-tls"
                    }
                ],
                "rules": [
                    {
                        "host": "api.ainflue.com",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "api-gateway",
                                            "port": {
                                                "number": 8000
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "host": "app.ainflue.com",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "frontend",
                                            "port": {
                                                "number": 3000
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "host": "admin.ainflue.com",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "admin-dashboard",
                                            "port": {
                                                "number": 3001
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "host": "storage.ainflue.com",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "storage-api",
                                            "port": {
                                                "number": 9000
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    
    def create_middleware_configurations(self) -> List[Dict[str, Any]]:
        """Create middleware configurations for Traefik"""
        if self.config.controller_type != IngressControllerType.TRAEFIK:
            return []
        
        return [
            {
                "apiVersion": "traefik.containo.us/v1alpha1",
                "kind": "Middleware",
                "metadata": {
                    "name": "security-headers",
                    "namespace": self.config.namespace
                },
                "spec": {
                    "headers": {
                        "customRequestHeaders": {
                            "X-Forwarded-Proto": "https"
                        },
                        "customResponseHeaders": {
                            "X-Frame-Options": "SAMEORIGIN",
                            "X-Content-Type-Options": "nosniff",
                            "X-XSS-Protection": "1; mode=block",
                            "Referrer-Policy": "strict-origin-when-cross-origin"
                        },
                        "contentSecurityPolicy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
                    }
                }
            },
            {
                "apiVersion": "traefik.containo.us/v1alpha1",
                "kind": "Middleware",
                "metadata": {
                    "name": "rate-limit",
                    "namespace": self.config.namespace
                },
                "spec": {
                    "rateLimit": {
                        "average": 100,
                        "period": "1m",
                        "burst": 200
                    }
                }
            },
            {
                "apiVersion": "traefik.containo.us/v1alpha1",
                "kind": "Middleware",
                "metadata": {
                    "name": "compression",
                    "namespace": self.config.namespace
                },
                "spec": {
                    "compress": {}
                }
            }
        ]
    
    def generate_all_ingress_manifests(self) -> Dict[str, str]:
        """Generate all ingress and TLS manifests"""
        manifests = {}
        
        # Cert-manager installation
        cert_manager = self.create_cert_manager_installation()
        manifests["cert-manager-installation"] = yaml.dump(cert_manager, default_flow_style=False)
        
        # Cluster issuers
        for issuer_type in [CertificateIssuer.LETS_ENCRYPT, CertificateIssuer.LETS_ENCRYPT_STAGING]:
            cluster_issuer = self.create_cluster_issuer(issuer_type)
            manifests[f"cluster-issuer-{issuer_type.value}"] = yaml.dump(cluster_issuer, default_flow_style=False)
        
        # Wildcard certificate
        certificate = self.create_wildcard_certificate()
        manifests["wildcard-certificate"] = yaml.dump(certificate, default_flow_style=False)
        
        # Ingress controller
        if self.config.controller_type == IngressControllerType.NGINX:
            nginx_controller = self.create_nginx_ingress_controller()
            manifests["nginx-ingress-controller"] = yaml.dump(nginx_controller, default_flow_style=False)
        
        # Main ingress
        main_ingress = self.create_main_ingress()
        manifests["main-ingress"] = yaml.dump(main_ingress, default_flow_style=False)
        
        # Middleware configurations (for Traefik)
        middlewares = self.create_middleware_configurations()
        for i, middleware in enumerate(middlewares):
            manifests[f"middleware-{i+1}"] = yaml.dump(middleware, default_flow_style=False)
        
        return manifests
    
    def save_manifests_to_files(self, output_dir -> None: str = "./k8s-manifests/ingress-tls") -> None:
        """Save all ingress and TLS manifests to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        manifests = self.generate_all_ingress_manifests()
        
        for name, manifest in manifests.items():
            file_path = os.path.join(output_dir, f"{name}.yaml")
            with open(file_path, 'w') as f:
                f.write(manifest)
            logger.info(f"Ingress TLS manifest saved: {file_path}")
        
        return len(manifests)


# Export main functionality
__all__ = ['IngressTLSManager', 'IngressConfig', 'TLSConfig', 'IngressControllerType', 'CertificateIssuer']