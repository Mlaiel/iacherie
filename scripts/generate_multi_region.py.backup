#!/usr/bin/env python3
"""
Multi-Region Kubernetes Deployment Manager
Handles deployment across multiple AWS regions for high availability
"""

import os
import yaml
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class RegionType(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    DISASTER_RECOVERY = "disaster_recovery"

@dataclass
class Region:
    name: str
    code: str
    type: RegionType
    cluster_name: str
    availability_zones: List[str]
    node_pools: Dict[str, Any] = field(default_factory=dict)
    database_endpoint: Optional[str] = None
    redis_endpoint: Optional[str] = None
    s3_bucket: Optional[str] = None

class MultiRegionDeploymentManager:
    """Manage multi-region Kubernetes deployments"""
    
    def __init__(self):
        self.regions = {
            "us-east-1": Region(
                name="US East (N. Virginia)",
                code="us-east-1", 
                type=RegionType.PRIMARY,
                cluster_name="ainflue-prod-us-east-1",
                availability_zones=["us-east-1a", "us-east-1b", "us-east-1c"],
                node_pools={
                    "general": {
                        "instance_type": "t3.large",
                        "min_size": 3,
                        "max_size": 10,
                        "desired_size": 5
                    },
                    "gpu": {
                        "instance_type": "p3.2xlarge", 
                        "min_size": 0,
                        "max_size": 3,
                        "desired_size": 1
                    },
                    "memory": {
                        "instance_type": "r5.xlarge",
                        "min_size": 0,
                        "max_size": 5,
                        "desired_size": 2
                    }
                },
                database_endpoint="ainflue-prod-us-east-1.cluster-abc123.us-east-1.rds.amazonaws.com",
                redis_endpoint="ainflue-prod-cache-us-east-1.abc123.cache.amazonaws.com",
                s3_bucket="ainflue-content-us-east-1"
            ),
            "us-west-2": Region(
                name="US West (Oregon)",
                code="us-west-2",
                type=RegionType.SECONDARY,
                cluster_name="ainflue-prod-us-west-2", 
                availability_zones=["us-west-2a", "us-west-2b", "us-west-2c"],
                node_pools={
                    "general": {
                        "instance_type": "t3.large",
                        "min_size": 2,
                        "max_size": 8,
                        "desired_size": 3
                    },
                    "gpu": {
                        "instance_type": "p3.2xlarge",
                        "min_size": 0,
                        "max_size": 2,
                        "desired_size": 0
                    }
                },
                database_endpoint="ainflue-prod-us-west-2.cluster-def456.us-west-2.rds.amazonaws.com",
                redis_endpoint="ainflue-prod-cache-us-west-2.def456.cache.amazonaws.com",
                s3_bucket="ainflue-content-us-west-2"
            ),
            "eu-west-1": Region(
                name="EU West (Ireland)",
                code="eu-west-1",
                type=RegionType.SECONDARY,
                cluster_name="ainflue-prod-eu-west-1",
                availability_zones=["eu-west-1a", "eu-west-1b", "eu-west-1c"],
                node_pools={
                    "general": {
                        "instance_type": "t3.large",
                        "min_size": 2,
                        "max_size": 6,
                        "desired_size": 3
                    }
                },
                database_endpoint="ainflue-prod-eu-west-1.cluster-ghi789.eu-west-1.rds.amazonaws.com",
                redis_endpoint="ainflue-prod-cache-eu-west-1.ghi789.cache.amazonaws.com", 
                s3_bucket="ainflue-content-eu-west-1"
            ),
            "ap-southeast-1": Region(
                name="AP Southeast (Singapore)",
                code="ap-southeast-1",
                type=RegionType.SECONDARY,
                cluster_name="ainflue-prod-ap-southeast-1",
                availability_zones=["ap-southeast-1a", "ap-southeast-1b", "ap-southeast-1c"],
                node_pools={
                    "general": {
                        "instance_type": "t3.medium",
                        "min_size": 1,
                        "max_size": 4,
                        "desired_size": 2
                    }
                },
                database_endpoint="ainflue-prod-ap-southeast-1.cluster-jkl012.ap-southeast-1.rds.amazonaws.com",
                redis_endpoint="ainflue-prod-cache-ap-southeast-1.jkl012.cache.amazonaws.com",
                s3_bucket="ainflue-content-ap-southeast-1"
            )
        }
        
        self.services = [
            "api-gateway", "user-service", "content-service", "ai-service",
            "protection-service", "collaboration-service", "payment-service", 
            "notification-service", "analytics-service"
        ]
    
    def generate_region_config(self, region_code: str) -> Dict[str, Any]:
        """Generate region-specific configuration"""
        region = self.regions[region_code]
        
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"region-config-{region_code}",
                "namespace": "production",
                "labels": {
                    "region": region_code,
                    "type": region.type.value
                }
            },
            "data": {
                "region_code": region_code,
                "region_name": region.name,
                "cluster_name": region.cluster_name,
                "region_type": region.type.value,
                "availability_zones": ",".join(region.availability_zones),
                "database_endpoint": region.database_endpoint or "",
                "redis_endpoint": region.redis_endpoint or "",
                "s3_bucket": region.s3_bucket or "",
                "cdn_endpoint": f"https://cdn-{region_code}.ainflue.com",
                "api_endpoint": f"https://api-{region_code}.ainflue.com" if region.type != RegionType.PRIMARY else "https://api.ainflue.com"
            }
        }
    
    def generate_cluster_autoscaler_config(self, region_code: str) -> Dict[str, Any]:
        """Generate cluster autoscaler configuration for region"""
        region = self.regions[region_code]
        
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "cluster-autoscaler",
                "namespace": "kube-system",
                "labels": {
                    "app": "cluster-autoscaler",
                    "region": region_code
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
                            "app": "cluster-autoscaler"
                        },
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": "8085"
                        }
                    },
                    "spec": {
                        "serviceAccountName": "cluster-autoscaler",
                        "containers": [{
                            "name": "cluster-autoscaler",
                            "image": "k8s.gcr.io/autoscaling/cluster-autoscaler:v1.21.0",
                            "resources": {
                                "limits": {
                                    "cpu": "100m",
                                    "memory": "300Mi"
                                },
                                "requests": {
                                    "cpu": "100m", 
                                    "memory": "300Mi"
                                }
                            },
                            "command": [
                                "./cluster-autoscaler",
                                "--v=4",
                                "--stderrthreshold=info",
                                "--cloud-provider=aws",
                                f"--node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/{region.cluster_name}",
                                "--balance-similar-node-groups",
                                "--skip-nodes-with-local-storage=false",
                                "--expander=least-waste",
                                f"--node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/{region.cluster_name}"
                            ],
                            "env": [
                                {
                                    "name": "AWS_REGION",
                                    "value": region_code
                                }
                            ]
                        }],
                        "nodeSelector": {
                            "kubernetes.io/os": "linux"
                        }
                    }
                }
            }
        }
    
    def generate_ingress_config(self, region_code: str) -> Dict[str, Any]:
        """Generate ingress configuration for region"""
        region = self.regions[region_code]
        
        # Use region-specific hostname for non-primary regions
        hostname = "api.ainflue.com" if region.type == RegionType.PRIMARY else f"api-{region_code}.ainflue.com"
        
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"ainflue-ingress-{region_code}",
                "namespace": "production",
                "labels": {
                    "region": region_code
                },
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/force-ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/rate-limit": "1000",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m",
                    "nginx.ingress.kubernetes.io/proxy-body-size": "1g",
                    "nginx.ingress.kubernetes.io/proxy-read-timeout": "300",
                    "nginx.ingress.kubernetes.io/proxy-send-timeout": "300"
                }
            },
            "spec": {
                "tls": [{
                    "hosts": [hostname],
                    "secretName": f"ainflue-tls-{region_code}"
                }],
                "rules": [{
                    "host": hostname,
                    "http": {
                        "paths": [{
                            "path": "/",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": "api-gateway-service",
                                    "port": {
                                        "number": 80
                                    }
                                }
                            }
                        }]
                    }
                }]
            }
        }
    
    def generate_regional_secrets(self, region_code: str) -> Dict[str, Any]:
        """Generate region-specific secrets template"""
        region = self.regions[region_code]
        
        return {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"region-secrets-{region_code}",
                "namespace": "production",
                "labels": {
                    "region": region_code
                }
            },
            "type": "Opaque",
            "data": {
                # Base64 encoded placeholder values - should be replaced with actual secrets
                "database_url": "cGxhY2Vob2xkZXI=",  # placeholder
                "redis_url": "cGxhY2Vob2xkZXI=",     # placeholder
                "s3_access_key": "cGxhY2Vob2xkZXI=",  # placeholder
                "s3_secret_key": "cGxhY2Vob2xkZXI="   # placeholder
            }
        }
    
    def generate_monitoring_config(self, region_code: str) -> Dict[str, Any]:
        """Generate region-specific monitoring configuration"""
        region = self.regions[region_code]
        
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"monitoring-config-{region_code}",
                "namespace": "production",
                "labels": {
                    "region": region_code,
                    "component": "monitoring"
                }
            },
            "data": {
                "prometheus.yml": f"""
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    region: '{region_code}'
    cluster: '{region.cluster_name}'
    environment: 'production'

rule_files:
  - "/etc/prometheus/rules/*.yml"

scrape_configs:
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
    - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
    - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
      action: keep
      regex: default;kubernetes;https

  - job_name: 'microservices'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
    - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\\d+)?;(\\d+)
      replacement: $1:$2
      target_label: __address__
"""
            }
        }
    
    def write_yaml(self, obj: Any, file_path: str):
        """Write object to YAML file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            yaml.dump(obj, f, default_flow_style=False, sort_keys=False)
    
    def generate_all_regional_configs(self, output_dir: str = "/home/runner/work/Ainflue/Ainflue/kubernetes/multi-region"):
        """Generate all regional configurations"""
        for region_code, region in self.regions.items():
            region_dir = os.path.join(output_dir, region_code)
            
            # Generate region config
            region_config = self.generate_region_config(region_code)
            self.write_yaml(region_config, os.path.join(region_dir, "region-config.yaml"))
            
            # Generate cluster autoscaler
            autoscaler_config = self.generate_cluster_autoscaler_config(region_code)
            self.write_yaml(autoscaler_config, os.path.join(region_dir, "cluster-autoscaler.yaml"))
            
            # Generate ingress
            ingress_config = self.generate_ingress_config(region_code)
            self.write_yaml(ingress_config, os.path.join(region_dir, "ingress.yaml"))
            
            # Generate secrets template
            secrets_config = self.generate_regional_secrets(region_code)
            self.write_yaml(secrets_config, os.path.join(region_dir, "secrets-template.yaml"))
            
            # Generate monitoring config
            monitoring_config = self.generate_monitoring_config(region_code)
            self.write_yaml(monitoring_config, os.path.join(region_dir, "monitoring.yaml"))
            
            print(f"Generated regional configs for {region_code} ({region.name})")
    
    def generate_global_load_balancer_config(self) -> Dict[str, Any]:
        """Generate global load balancer configuration"""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "global-load-balancer-config",
                "namespace": "production"
            },
            "data": {
                "nginx.conf": """
upstream primary_region {
    server api-us-east-1.ainflue.com max_fails=3 fail_timeout=30s;
}

upstream secondary_regions {
    server api-us-west-2.ainflue.com max_fails=3 fail_timeout=30s backup;
    server api-eu-west-1.ainflue.com max_fails=3 fail_timeout=30s backup;
    server api-ap-southeast-1.ainflue.com max_fails=3 fail_timeout=30s backup;
}

map $http_cf_ipcountry $region_backend {
    default primary_region;
    US primary_region;
    CA primary_region;
    GB secondary_regions;
    DE secondary_regions;
    FR secondary_regions;
    SG secondary_regions;
    JP secondary_regions;
    AU secondary_regions;
}

server {
    listen 80;
    server_name api.ainflue.com;
    
    location /health {
        access_log off;
        return 200 "healthy";
        add_header Content-Type text/plain;
    }
    
    location / {
        proxy_pass http://$region_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Region $http_cf_ipcountry;
        
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        proxy_next_upstream error timeout http_502 http_503 http_504;
        proxy_next_upstream_tries 3;
    }
}
"""
            }
        }

if __name__ == "__main__":
    manager = MultiRegionDeploymentManager()
    manager.generate_all_regional_configs()
    
    # Generate global load balancer config
    global_config = manager.generate_global_load_balancer_config()
    manager.write_yaml(global_config, "/home/runner/work/Ainflue/Ainflue/kubernetes/multi-region/global-lb-config.yaml")
    
    print("Multi-region deployment configurations generated successfully!")