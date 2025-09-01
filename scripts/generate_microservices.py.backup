#!/usr/bin/env python3
"""
Comprehensive Microservices Deployment Generator
Creates production-ready Kubernetes manifests for all 9 core services
"""

import os
import yaml
from typing import Dict, List, Any

class MicroservicesDeploymentGenerator:
    """Generate production-ready Kubernetes manifests for microservices"""
    
    def __init__(self, base_path: str = "/home/runner/work/Ainflue/Ainflue/kubernetes/microservices"):
        self.base_path = base_path
        self.namespace = "production"
        
        # Service definitions
        self.services = {
            "protection-service": {
                "description": "Fingerprinting + monitoring",
                "port": 8000,
                "replicas": 2,
                "resources": {
                    "requests": {"memory": "512Mi", "cpu": "300m"},
                    "limits": {"memory": "1Gi", "cpu": "1000m"}
                },
                "env_secrets": ["database-secret:protection_db_url", "redis-secret:url"],
                "config_keys": ["fingerprinting_engines", "monitoring_settings"]
            },
            "collaboration-service": {
                "description": "Matching + projects", 
                "port": 8000,
                "replicas": 2,
                "resources": {
                    "requests": {"memory": "256Mi", "cpu": "200m"},
                    "limits": {"memory": "512Mi", "cpu": "500m"}
                },
                "env_secrets": ["database-secret:collaboration_db_url", "redis-secret:url"],
                "config_keys": ["matching_algorithms", "project_settings"]
            },
            "payment-service": {
                "description": "Transactions + billing",
                "port": 8000, 
                "replicas": 3,
                "resources": {
                    "requests": {"memory": "256Mi", "cpu": "200m"},
                    "limits": {"memory": "512Mi", "cpu": "500m"}
                },
                "env_secrets": ["database-secret:payment_db_url", "stripe-secret:api_key", "paypal-secret:client_id"],
                "config_keys": ["payment_processors", "billing_settings"]
            },
            "notification-service": {
                "description": "Alerts + communications",
                "port": 8000,
                "replicas": 2,
                "resources": {
                    "requests": {"memory": "128Mi", "cpu": "100m"}, 
                    "limits": {"memory": "256Mi", "cpu": "300m"}
                },
                "env_secrets": ["database-secret:notification_db_url", "smtp-secret:password", "sms-secret:api_key"],
                "config_keys": ["notification_channels", "delivery_settings"]
            },
            "analytics-service": {
                "description": "Metrics + reporting",
                "port": 8000,
                "replicas": 2,
                "resources": {
                    "requests": {"memory": "512Mi", "cpu": "300m"},
                    "limits": {"memory": "1Gi", "cpu": "1000m"}
                },
                "env_secrets": ["database-secret:analytics_db_url", "mongodb-secret:url"],
                "config_keys": ["analytics_engines", "reporting_settings"]
            }
        }
    
    def generate_deployment(self, service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment manifest for a service"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment", 
            "metadata": {
                "name": service_name,
                "namespace": self.namespace,
                "labels": {
                    "app": service_name,
                    "component": "backend",
                    "tier": "service",
                    "version": "v1.0.0"
                }
            },
            "spec": {
                "replicas": service_config["replicas"],
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxSurge": 1,
                        "maxUnavailable": 0
                    }
                },
                "selector": {
                    "matchLabels": {
                        "app": service_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": service_name,
                            "component": "backend", 
                            "tier": "service",
                            "version": "v1.0.0"
                        },
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": str(service_config["port"]),
                            "prometheus.io/path": "/metrics"
                        }
                    },
                    "spec": {
                        "serviceAccountName": service_name,
                        "containers": [{
                            "name": service_name,
                            "image": f"ainflue/{service_name}:latest",
                            "imagePullPolicy": "Always",
                            "ports": [{
                                "containerPort": service_config["port"],
                                "name": "http",
                                "protocol": "TCP"
                            }],
                            "env": self._generate_env_vars(service_config),
                            "resources": service_config["resources"],
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": service_config["port"]
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10,
                                "timeoutSeconds": 5,
                                "failureThreshold": 3
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready", 
                                    "port": service_config["port"]
                                },
                                "initialDelaySeconds": 10,
                                "periodSeconds": 5,
                                "timeoutSeconds": 5,
                                "failureThreshold": 3
                            },
                            "securityContext": {
                                "runAsNonRoot": True,
                                "runAsUser": 1000,
                                "allowPrivilegeEscalation": False,
                                "readOnlyRootFilesystem": True,
                                "capabilities": {
                                    "drop": ["ALL"]
                                }
                            },
                            "volumeMounts": [
                                {
                                    "name": "tmp",
                                    "mountPath": "/tmp"
                                },
                                {
                                    "name": "config",
                                    "mountPath": "/app/config",
                                    "readOnly": True
                                }
                            ]
                        }],
                        "volumes": [
                            {
                                "name": "tmp",
                                "emptyDir": {}
                            },
                            {
                                "name": "config",
                                "configMap": {
                                    "name": f"{service_name}-config"
                                }
                            }
                        ],
                        "affinity": {
                            "podAntiAffinity": {
                                "preferredDuringSchedulingIgnoredDuringExecution": [{
                                    "weight": 100,
                                    "podAffinityTerm": {
                                        "labelSelector": {
                                            "matchExpressions": [{
                                                "key": "app",
                                                "operator": "In",
                                                "values": [service_name]
                                            }]
                                        },
                                        "topologyKey": "kubernetes.io/hostname"
                                    }
                                }]
                            }
                        }
                    }
                }
            }
        }
    
    def _generate_env_vars(self, service_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate environment variables for service"""
        env_vars = [
            {"name": "ENVIRONMENT", "value": "production"},
            {"name": "LOG_LEVEL", "value": "INFO"},
            {"name": "ENABLE_METRICS", "value": "true"}
        ]
        
        # Add secret-based environment variables
        for secret_ref in service_config.get("env_secrets", []):
            secret_name, key = secret_ref.split(":")
            env_name = key.upper().replace("_", "_")
            if "url" in key.lower():
                env_name = f"{secret_name.replace('-', '_').upper()}_URL"
            
            env_vars.append({
                "name": env_name,
                "valueFrom": {
                    "secretKeyRef": {
                        "name": secret_name,
                        "key": key
                    }
                }
            })
        
        return env_vars
    
    def generate_service(self, service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate service manifest"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": service_name,
                "namespace": self.namespace,
                "labels": {
                    "app": service_name
                }
            },
            "spec": {
                "type": "ClusterIP",
                "ports": [{
                    "name": "http",
                    "port": service_config["port"],
                    "targetPort": service_config["port"],
                    "protocol": "TCP"
                }],
                "selector": {
                    "app": service_name
                }
            }
        }
    
    def generate_service_account(self, service_name: str) -> Dict[str, Any]:
        """Generate service account manifest"""
        return {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": service_name,
                "namespace": self.namespace,
                "labels": {
                    "app": service_name
                }
            }
        }
    
    def generate_hpa(self, service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate HPA manifest"""
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{service_name}-hpa",
                "namespace": self.namespace,
                "labels": {
                    "app": service_name
                }
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": service_name
                },
                "minReplicas": service_config["replicas"],
                "maxReplicas": service_config["replicas"] * 3,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 70
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
                    "scaleUp": {
                        "stabilizationWindowSeconds": 60,
                        "policies": [
                            {"type": "Pods", "value": 1, "periodSeconds": 60},
                            {"type": "Percent", "value": 50, "periodSeconds": 60}
                        ],
                        "selectPolicy": "Max"
                    },
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [
                            {"type": "Pods", "value": 1, "periodSeconds": 60},
                            {"type": "Percent", "value": 10, "periodSeconds": 60}
                        ],
                        "selectPolicy": "Min"
                    }
                }
            }
        }
    
    def write_manifest(self, manifest: Dict[str, Any], file_path: str):
        """Write manifest to YAML file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
    
    def generate_all_manifests(self):
        """Generate all microservice manifests"""
        for service_name, service_config in self.services.items():
            service_dir = os.path.join(self.base_path, service_name)
            
            # Generate deployment manifest
            deployment = self.generate_deployment(service_name, service_config)
            service_manifest = self.generate_service(service_name, service_config)
            service_account = self.generate_service_account(service_name)
            
            # Combine all resources in deployment.yaml
            combined_manifest = {
                "items": [deployment, service_manifest, service_account]
            }
            
            deployment_file = os.path.join(service_dir, "deployment.yaml")
            with open(deployment_file, 'w') as f:
                for i, item in enumerate([deployment, service_manifest, service_account]):
                    if i > 0:
                        f.write("---\n")
                    yaml.dump(item, f, default_flow_style=False, sort_keys=False)
            
            # Generate HPA
            hpa = self.generate_hpa(service_name, service_config)
            hpa_file = os.path.join(service_dir, "hpa.yaml")
            self.write_manifest(hpa, hpa_file)
            
            print(f"Generated manifests for {service_name}")

if __name__ == "__main__":
    generator = MicroservicesDeploymentGenerator()
    generator.generate_all_manifests()
    print("All microservice manifests generated successfully!")