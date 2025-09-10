# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade Kubernetes Ingress Controller Management
# Multi-provider ingress support with advanced traffic management
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
import ssl
import certifi

@dataclass
class IngressConfig:
    """Ingress controller configuration"""
    name: str
    namespace: str
    controller_class: str
    provider: str  # nginx, traefik, istio, ambassador
    load_balancer_type: str
    ssl_config: Dict[str, Any]
    rate_limiting: Dict[str, int]
    annotations: Dict[str, str]

@dataclass
class RouteRule:
    """HTTP route rule definition"""
    host: str
    path: str
    service_name: str
    service_port: int
    tls_enabled: bool = True
    middleware: List[str] = None
    rate_limit: Optional[int] = None

class IngressControllerManager:
    """
    Enterprise Kubernetes Ingress Controller Manager
    
    Capabilities:
    - Multi-provider ingress controller management
    - Advanced traffic routing and load balancing
    - SSL/TLS certificate automation
    - Rate limiting and DDoS protection
    - Health checking and failover
    - Integration with service mesh
    """
    
    def __init__(self, cluster_config: Optional[str] = None):
        self.cluster_config = cluster_config
        self.k8s_client = None
        self.extensions_client = None
        self.networking_client = None
        self.logger = self._setup_logging()
        self.controllers: Dict[str, IngressConfig] = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger("IngressControllerManager")
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
            self.extensions_client = client.ExtensionsV1beta1Api()
            self.networking_client = client.NetworkingV1Api()
            
            self.logger.info("Kubernetes clients initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Kubernetes clients: {e}")
            return False
    
    async def deploy_nginx_ingress(self, namespace: str = "ingress-nginx") -> bool:
        """Deploy NGINX Ingress Controller"""
        try:
            # Create namespace
            await self._ensure_namespace(namespace)
            
            # NGINX Ingress configuration
            nginx_config = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "nginx-ingress-controller",
                    "namespace": namespace,
                    "labels": {
                        "app": "nginx-ingress",
                        "version": "v1.0.0"
                    }
                },
                "spec": {
                    "replicas": 3,
                    "selector": {
                        "matchLabels": {
                            "app": "nginx-ingress"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "nginx-ingress"
                            }
                        },
                        "spec": {
                            "serviceAccountName": "nginx-ingress-serviceaccount",
                            "containers": [
                                {
                                    "name": "nginx-ingress-controller",
                                    "image": "k8s.gcr.io/ingress-nginx/controller:v1.3.0",
                                    "args": [
                                        "/nginx-ingress-controller",
                                        "--configmap=$(POD_NAMESPACE)/nginx-configuration",
                                        "--tcp-services-configmap=$(POD_NAMESPACE)/tcp-services",
                                        "--udp-services-configmap=$(POD_NAMESPACE)/udp-services",
                                        "--publish-service=$(POD_NAMESPACE)/ingress-nginx",
                                        "--annotations-prefix=nginx.ingress.kubernetes.io"
                                    ],
                                    "env": [
                                        {
                                            "name": "POD_NAME",
                                            "valueFrom": {
                                                "fieldRef": {
                                                    "fieldPath": "metadata.name"
                                                }
                                            }
                                        },
                                        {
                                            "name": "POD_NAMESPACE",
                                            "valueFrom": {
                                                "fieldRef": {
                                                    "fieldPath": "metadata.namespace"
                                                }
                                            }
                                        }
                                    ],
                                    "ports": [
                                        {
                                            "name": "http",
                                            "containerPort": 80
                                        },
                                        {
                                            "name": "https",
                                            "containerPort": 443
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
                                    }
                                }
                            ]
                        }
                    }
                }
            }
            
            # Deploy NGINX controller
            apps_v1 = client.AppsV1Api()
            apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=nginx_config
            )
            
            # Create service
            await self._create_nginx_service(namespace)
            
            self.logger.info("NGINX Ingress Controller deployed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deploy NGINX Ingress: {e}")
            return False
    
    async def deploy_traefik_ingress(self, namespace: str = "traefik-system") -> bool:
        """Deploy Traefik Ingress Controller"""
        try:
            await self._ensure_namespace(namespace)
            
            traefik_config = {
                "apiVersion": "apps/v1",
                "kind": "DaemonSet",
                "metadata": {
                    "name": "traefik",
                    "namespace": namespace,
                    "labels": {
                        "app": "traefik"
                    }
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "app": "traefik"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "traefik"
                            }
                        },
                        "spec": {
                            "serviceAccountName": "traefik-ingress-controller",
                            "terminationGracePeriodSeconds": 60,
                            "containers": [
                                {
                                    "name": "traefik",
                                    "image": "traefik:v2.8",
                                    "args": [
                                        "--global.checknewversion=false",
                                        "--global.sendanonymoususage=false",
                                        "--entrypoints.web.address=:80",
                                        "--entrypoints.websecure.address=:443",
                                        "--providers.kubernetescrd",
                                        "--certificatesresolvers.myresolver.acme.email=mlaiel@live.de",
                                        "--certificatesresolvers.myresolver.acme.storage=/data/acme.json",
                                        "--certificatesresolvers.myresolver.acme.httpchallenge.entrypoint=web"
                                    ],
                                    "ports": [
                                        {
                                            "name": "web",
                                            "containerPort": 80,
                                            "hostPort": 80
                                        },
                                        {
                                            "name": "websecure",
                                            "containerPort": 443,
                                            "hostPort": 443
                                        },
                                        {
                                            "name": "admin",
                                            "containerPort": 8080
                                        }
                                    ],
                                    "resources": {
                                        "requests": {
                                            "cpu": "100m",
                                            "memory": "128Mi"
                                        },
                                        "limits": {
                                            "cpu": "300m",
                                            "memory": "256Mi"
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
            
            apps_v1 = client.AppsV1Api()
            apps_v1.create_namespaced_daemon_set(
                namespace=namespace,
                body=traefik_config
            )
            
            self.logger.info("Traefik Ingress Controller deployed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deploy Traefik Ingress: {e}")
            return False
    
    async def create_ingress_route(self, route: RouteRule, namespace: str = "default") -> bool:
        """Create ingress route for service"""
        try:
            ingress_config = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": f"{route.service_name}-ingress",
                    "namespace": namespace,
                    "annotations": {
                        "kubernetes.io/ingress.class": "nginx",
                        "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                        "nginx.ingress.kubernetes.io/use-regex": "true"
                    }
                },
                "spec": {
                    "rules": [
                        {
                            "host": route.host,
                            "http": {
                                "paths": [
                                    {
                                        "path": route.path,
                                        "pathType": "Prefix",
                                        "backend": {
                                            "service": {
                                                "name": route.service_name,
                                                "port": {
                                                    "number": route.service_port
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
            
            # Add TLS if enabled
            if route.tls_enabled:
                ingress_config["spec"]["tls"] = [
                    {
                        "hosts": [route.host],
                        "secretName": f"{route.service_name}-tls"
                    }
                ]
            
            # Add rate limiting if specified
            if route.rate_limit:
                ingress_config["metadata"]["annotations"].update({
                    "nginx.ingress.kubernetes.io/rate-limit": str(route.rate_limit),
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m"
                })
            
            self.networking_client.create_namespaced_ingress(
                namespace=namespace,
                body=ingress_config
            )
            
            self.logger.info(f"Ingress route created for {route.service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create ingress route: {e}")
            return False
    
    async def configure_ssl_termination(self, host: str, cert_data: str, key_data: str, namespace: str = "default") -> bool:
        """Configure SSL/TLS termination"""
        try:
            secret_config = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": f"{host.replace('.', '-')}-tls",
                    "namespace": namespace
                },
                "type": "kubernetes.io/tls",
                "data": {
                    "tls.crt": cert_data,
                    "tls.key": key_data
                }
            }
            
            self.k8s_client.create_namespaced_secret(
                namespace=namespace,
                body=secret_config
            )
            
            self.logger.info(f"SSL certificate configured for {host}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure SSL: {e}")
            return False
    
    async def enable_rate_limiting(self, ingress_name: str, namespace: str, requests_per_minute: int) -> bool:
        """Enable rate limiting on ingress"""
        try:
            # Update ingress annotations
            ingress = self.networking_client.read_namespaced_ingress(
                name=ingress_name,
                namespace=namespace
            )
            
            ingress.metadata.annotations.update({
                "nginx.ingress.kubernetes.io/rate-limit": str(requests_per_minute),
                "nginx.ingress.kubernetes.io/rate-limit-window": "1m",
                "nginx.ingress.kubernetes.io/rate-limit-status-code": "429"
            })
            
            self.networking_client.patch_namespaced_ingress(
                name=ingress_name,
                namespace=namespace,
                body=ingress
            )
            
            self.logger.info(f"Rate limiting enabled: {requests_per_minute} req/min")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable rate limiting: {e}")
            return False
    
    async def setup_load_balancer(self, service_name: str, namespace: str, lb_type: str = "nlb") -> bool:
        """Setup load balancer for ingress"""
        try:
            lb_service = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": f"{service_name}-lb",
                    "namespace": namespace,
                    "annotations": {
                        "service.beta.kubernetes.io/aws-load-balancer-type": lb_type,
                        "service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled": "true"
                    }
                },
                "spec": {
                    "type": "LoadBalancer",
                    "selector": {
                        "app": service_name
                    },
                    "ports": [
                        {
                            "name": "http",
                            "port": 80,
                            "targetPort": 80
                        },
                        {
                            "name": "https",
                            "port": 443,
                            "targetPort": 443
                        }
                    ]
                }
            }
            
            self.k8s_client.create_namespaced_service(
                namespace=namespace,
                body=lb_service
            )
            
            self.logger.info(f"Load balancer configured for {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup load balancer: {e}")
            return False
    
    async def monitor_ingress_health(self) -> Dict[str, Any]:
        """Monitor ingress controller health"""
        try:
            health_status = {
                "timestamp": datetime.utcnow().isoformat(),
                "controllers": {},
                "ingresses": {},
                "overall_status": "healthy"
            }
            
            # Check ingress controllers
            for namespace in ["ingress-nginx", "traefik-system"]:
                try:
                    deployments = client.AppsV1Api().list_namespaced_deployment(namespace=namespace)
                    for deployment in deployments.items:
                        health_status["controllers"][deployment.metadata.name] = {
                            "ready_replicas": deployment.status.ready_replicas or 0,
                            "replicas": deployment.spec.replicas,
                            "status": "healthy" if deployment.status.ready_replicas == deployment.spec.replicas else "degraded"
                        }
                except:
                    pass
            
            # Check ingress resources
            ingresses = self.networking_client.list_ingress_for_all_namespaces()
            for ingress in ingresses.items:
                ingress_name = f"{ingress.metadata.namespace}/{ingress.metadata.name}"
                health_status["ingresses"][ingress_name] = {
                    "rules_count": len(ingress.spec.rules) if ingress.spec.rules else 0,
                    "tls_enabled": bool(ingress.spec.tls),
                    "load_balancer_ingress": bool(ingress.status.load_balancer.ingress) if ingress.status.load_balancer else False
                }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Failed to monitor ingress health: {e}")
            return {"error": str(e)}
    
    async def _ensure_namespace(self, namespace: str) -> bool:
        """Ensure namespace exists"""
        try:
            self.k8s_client.read_namespace(name=namespace)
            return True
        except client.exceptions.ApiException as e:
            if e.status == 404:
                namespace_config = {
                    "apiVersion": "v1",
                    "kind": "Namespace",
                    "metadata": {
                        "name": namespace
                    }
                }
                self.k8s_client.create_namespace(body=namespace_config)
                return True
            raise
    
    async def _create_nginx_service(self, namespace: str) -> bool:
        """Create NGINX service"""
        try:
            service_config = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "ingress-nginx",
                    "namespace": namespace
                },
                "spec": {
                    "type": "LoadBalancer",
                    "selector": {
                        "app": "nginx-ingress"
                    },
                    "ports": [
                        {
                            "name": "http",
                            "port": 80,
                            "targetPort": 80
                        },
                        {
                            "name": "https",
                            "port": 443,
                            "targetPort": 443
                        }
                    ]
                }
            }
            
            self.k8s_client.create_namespaced_service(
                namespace=namespace,
                body=service_config
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create NGINX service: {e}")
            return False

# Factory function for easy instantiation
def create_ingress_manager(cluster_config: Optional[str] = None) -> IngressControllerManager:
    """Create and initialize ingress controller manager"""
    return IngressControllerManager(cluster_config)

# Enterprise ingress patterns
ENTERPRISE_INGRESS_PATTERNS = {
    "api_gateway": {
        "controller": "nginx",
        "features": ["rate_limiting", "ssl_termination", "load_balancing"],
        "annotations": {
            "nginx.ingress.kubernetes.io/rewrite-target": "/",
            "nginx.ingress.kubernetes.io/cors-allow-origin": "*"
        }
    },
    "microservices": {
        "controller": "traefik",
        "features": ["service_discovery", "circuit_breaker", "retry"],
        "middleware": ["auth", "rate-limit", "compress"]
    },
    "content_delivery": {
        "controller": "istio",
        "features": ["canary_deployment", "traffic_splitting", "observability"],
        "mesh_config": {
            "mTLS": True,
            "telemetry": True
        }
    }
}