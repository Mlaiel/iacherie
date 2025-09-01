#!/usr/bin/env python3
"""
Production-ready multi-region HA Kubernetes deployment manager
Enhanced with enterprise-grade high availability configurations
"""

import os
import yaml
import json
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional


class RegionType(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    DISASTER_RECOVERY = "disaster_recovery"


@dataclass
class HANodeGroup:
    """High Availability Node Group configuration"""
    name: str
    instance_type: str
    min_size: int
    max_size: int
    desired_size: int
    availability_zones: List[str]
    spot_enabled: bool = False
    gpu_enabled: bool = False
    labels: Dict[str, str] = None
    taints: List[Dict[str, str]] = None


@dataclass
class RegionConfig:
    """Enhanced region configuration with HA support"""
    name: str
    code: str
    cluster_name: str
    type: RegionType
    availability_zones: List[str]
    node_groups: List[HANodeGroup]
    database_endpoint: Optional[str] = None
    redis_endpoint: Optional[str] = None
    s3_bucket: Optional[str] = None
    load_balancer_scheme: str = "internet-facing"
    backup_region: Optional[str] = None


class ProductionMultiRegionManager:
    """Production-ready multi-region Kubernetes deployment manager"""
    
    def __init__(self):
        self.regions = self._initialize_production_regions()
    
    def _initialize_production_regions(self) -> Dict[str, RegionConfig]:
        """Initialize production-ready multi-region configuration with HA"""
        
        # Define node groups for different workload types
        api_node_group = HANodeGroup(
            name="api-nodes",
            instance_type="m5.large",
            min_size=3,
            max_size=10,
            desired_size=3,
            availability_zones=[],  # Will be set per region
            labels={"workload": "api", "tier": "frontend"}
        )
        
        worker_node_group = HANodeGroup(
            name="worker-nodes", 
            instance_type="c5.xlarge",
            min_size=2,
            max_size=20,
            desired_size=3,
            availability_zones=[],
            spot_enabled=True,
            labels={"workload": "processing", "tier": "backend"}
        )
        
        ai_node_group = HANodeGroup(
            name="ai-nodes",
            instance_type="g4dn.xlarge", 
            min_size=1,
            max_size=5,
            desired_size=2,
            availability_zones=[],
            gpu_enabled=True,
            labels={"workload": "ai", "tier": "compute"},
            taints=[{"key": "nvidia.com/gpu", "value": "true", "effect": "NoSchedule"}]
        )
        
        return {
            "us-east-1": RegionConfig(
                name="US East (N. Virginia)",
                code="us-east-1", 
                cluster_name="ainflue-prod-us-east-1",
                type=RegionType.PRIMARY,
                availability_zones=["us-east-1a", "us-east-1b", "us-east-1c"],
                node_groups=[
                    self._configure_node_group_for_region(api_node_group, ["us-east-1a", "us-east-1b", "us-east-1c"]),
                    self._configure_node_group_for_region(worker_node_group, ["us-east-1a", "us-east-1b", "us-east-1c"]),
                    self._configure_node_group_for_region(ai_node_group, ["us-east-1a", "us-east-1b"])
                ],
                database_endpoint="ainflue-primary.cluster-xyz.us-east-1.rds.amazonaws.com",
                redis_endpoint="ainflue-primary.abc123.cache.amazonaws.com",
                s3_bucket="ainflue-prod-primary-us-east-1",
                backup_region="us-west-2"
            ),
            "us-west-2": RegionConfig(
                name="US West (Oregon)",
                code="us-west-2",
                cluster_name="ainflue-prod-us-west-2", 
                type=RegionType.SECONDARY,
                availability_zones=["us-west-2a", "us-west-2b", "us-west-2c"],
                node_groups=[
                    self._configure_node_group_for_region(api_node_group, ["us-west-2a", "us-west-2b", "us-west-2c"]),
                    self._configure_node_group_for_region(worker_node_group, ["us-west-2a", "us-west-2b"])
                ],
                database_endpoint="ainflue-secondary.cluster-xyz.us-west-2.rds.amazonaws.com",
                redis_endpoint="ainflue-secondary.def456.cache.amazonaws.com", 
                s3_bucket="ainflue-prod-secondary-us-west-2",
                backup_region="us-east-1"
            ),
            "eu-west-1": RegionConfig(
                name="EU West (Ireland)",
                code="eu-west-1",
                cluster_name="ainflue-prod-eu-west-1",
                type=RegionType.SECONDARY,
                availability_zones=["eu-west-1a", "eu-west-1b", "eu-west-1c"],
                node_groups=[
                    self._configure_node_group_for_region(api_node_group, ["eu-west-1a", "eu-west-1b", "eu-west-1c"]),
                    self._configure_node_group_for_region(worker_node_group, ["eu-west-1a", "eu-west-1b"])
                ],
                database_endpoint="ainflue-eu.cluster-xyz.eu-west-1.rds.amazonaws.com",
                redis_endpoint="ainflue-eu.ghi789.cache.amazonaws.com",
                s3_bucket="ainflue-prod-eu-west-1"
            ),
            "ap-southeast-1": RegionConfig(
                name="AP Southeast (Singapore)",
                code="ap-southeast-1",
                cluster_name="ainflue-prod-ap-southeast-1",
                type=RegionType.SECONDARY,
                availability_zones=["ap-southeast-1a", "ap-southeast-1b", "ap-southeast-1c"],
                node_groups=[
                    self._configure_node_group_for_region(api_node_group, ["ap-southeast-1a", "ap-southeast-1b"]),
                    self._configure_node_group_for_region(worker_node_group, ["ap-southeast-1a", "ap-southeast-1b"])
                ],
                database_endpoint="ainflue-apac.cluster-xyz.ap-southeast-1.rds.amazonaws.com",
                redis_endpoint="ainflue-apac.jkl012.cache.amazonaws.com",
                s3_bucket="ainflue-prod-apac-ap-southeast-1"
            )
        }
    
    def _configure_node_group_for_region(self, node_group: HANodeGroup, azs: List[str]) -> HANodeGroup:
        """Configure node group for specific region availability zones"""
        import copy
        configured_group = copy.deepcopy(node_group)
        configured_group.availability_zones = azs
        return configured_group
    
    def generate_ha_cluster_config(self, region_code: str) -> Dict[str, Any]:
        """Generate high availability cluster configuration"""
        region = self.regions[region_code]
        
        return {
            "apiVersion": "eksctl.io/v1alpha5",
            "kind": "ClusterConfig",
            "metadata": {
                "name": region.cluster_name,
                "region": region_code,
                "version": "1.28",
                "tags": {
                    "Environment": "production",
                    "Project": "ainflue",
                    "Region": region_code,
                    "RegionType": region.type.value,
                    "ManagedBy": "eksctl"
                }
            },
            "vpc": {
                "enableDnsHostnames": True,
                "enableDnsSupport": True,
                "cidr": "10.0.0.0/16",
                "subnets": {
                    "private": {
                        f"private-{az}": {
                            "id": f"subnet-{hash(az) % 1000000:06d}",
                            "az": az,
                            "cidr": f"10.0.{i*16}.0/20"
                        } for i, az in enumerate(region.availability_zones)
                    },
                    "public": {
                        f"public-{az}": {
                            "id": f"subnet-pub-{hash(az) % 1000000:06d}",
                            "az": az, 
                            "cidr": f"10.0.{100 + i*16}.0/20"
                        } for i, az in enumerate(region.availability_zones)
                    }
                },
                "nat": {
                    "gateway": "HighlyAvailable"
                }
            },
            "iam": {
                "withOIDC": True,
                "serviceAccounts": [
                    {
                        "metadata": {
                            "name": "cluster-autoscaler",
                            "namespace": "kube-system"
                        },
                        "wellKnownPolicies": {
                            "autoScaler": True
                        }
                    },
                    {
                        "metadata": {
                            "name": "aws-load-balancer-controller",
                            "namespace": "kube-system"
                        },
                        "wellKnownPolicies": {
                            "awsLoadBalancerController": True
                        }
                    }
                ]
            },
            "managedNodeGroups": [
                self._generate_managed_node_group_config(ng, region_code) 
                for ng in region.node_groups
            ],
            "addons": [
                {
                    "name": "vpc-cni",
                    "version": "latest"
                },
                {
                    "name": "coredns", 
                    "version": "latest"
                },
                {
                    "name": "kube-proxy",
                    "version": "latest"
                },
                {
                    "name": "aws-ebs-csi-driver",
                    "version": "latest",
                    "wellKnownPolicies": {
                        "ebsCSIController": True
                    }
                }
            ],
            "cloudWatch": {
                "clusterLogging": {
                    "enable": ["audit", "authenticator", "controllerManager", "scheduler", "api"],
                    "logRetentionInDays": 30
                }
            },
            "secretsEncryption": {
                "keyARN": f"arn:aws:kms:{region_code}:123456789012:key/12345678-1234-1234-1234-123456789012"
            }
        }
    
    def _generate_managed_node_group_config(self, node_group: HANodeGroup, region_code: str) -> Dict[str, Any]:
        """Generate managed node group configuration"""
        config = {
            "name": node_group.name,
            "instanceTypes": [node_group.instance_type],
            "minSize": node_group.min_size,
            "maxSize": node_group.max_size,
            "desiredCapacity": node_group.desired_size,
            "availabilityZones": node_group.availability_zones,
            "privateNetworking": True,
            "volumeType": "gp3",
            "volumeSize": 100,
            "volumeEncrypted": True,
            "amiFamily": "AmazonLinux2",
            "iam": {
                "withAddonPolicies": {
                    "imageBuilder": True,
                    "autoScaler": True,
                    "externalDNS": True,
                    "certManager": True,
                    "appMesh": True,
                    "appMeshPreview": True,
                    "ebs": True,
                    "fsx": True,
                    "efs": True,
                    "awsLoadBalancerController": True,
                    "xRay": True,
                    "cloudWatch": True
                }
            },
            "labels": node_group.labels or {},
            "tags": {
                "Environment": "production",
                "NodeGroup": node_group.name,
                "Region": region_code,
                "k8s.io/cluster-autoscaler/enabled": "true",
                f"k8s.io/cluster-autoscaler/ainflue-prod-{region_code}": "owned"
            },
            "securityGroups": {
                "withShared": True,
                "withLocal": True
            },
            "ssh": {
                "allow": False
            }
        }
        
        if node_group.spot_enabled:
            config["spot"] = True
            config["instancesDistribution"] = {
                "maxPrice": 0.10,
                "instanceTypes": [node_group.instance_type, "m5.xlarge", "c5.large"],
                "onDemandBaseCapacity": 1,
                "onDemandPercentageAboveBaseCapacity": 20,
                "spotInstancePools": 3
            }
        
        if node_group.gpu_enabled:
            config["amiFamily"] = "AmazonLinux2"
            config["instanceTypes"] = ["g4dn.xlarge", "g4dn.2xlarge"]
            
        if node_group.taints:
            config["taints"] = node_group.taints
            
        return config
    
    def generate_production_ingress_config(self, region_code: str) -> Dict[str, Any]:
        """Generate production-ready ingress configuration with HA"""
        region = self.regions[region_code]
        
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"ainflue-ingress-{region_code}",
                "namespace": "production",
                "annotations": {
                    "kubernetes.io/ingress.class": "alb",
                    "alb.ingress.kubernetes.io/scheme": region.load_balancer_scheme,
                    "alb.ingress.kubernetes.io/target-type": "ip",
                    "alb.ingress.kubernetes.io/healthcheck-protocol": "HTTP",
                    "alb.ingress.kubernetes.io/healthcheck-port": "traffic-port",
                    "alb.ingress.kubernetes.io/healthcheck-path": "/health",
                    "alb.ingress.kubernetes.io/healthcheck-interval-seconds": "15",
                    "alb.ingress.kubernetes.io/healthcheck-timeout-seconds": "5",
                    "alb.ingress.kubernetes.io/healthy-threshold-count": "2",
                    "alb.ingress.kubernetes.io/unhealthy-threshold-count": "2",
                    "alb.ingress.kubernetes.io/ssl-redirect": "443",
                    "alb.ingress.kubernetes.io/certificate-arn": f"arn:aws:acm:{region_code}:123456789012:certificate/12345678-1234-1234-1234-123456789012",
                    "alb.ingress.kubernetes.io/ssl-policy": "ELBSecurityPolicy-TLS-1-2-2017-01",
                    "alb.ingress.kubernetes.io/backend-protocol": "HTTP",
                    "alb.ingress.kubernetes.io/load-balancer-attributes": "access_logs.s3.enabled=true,access_logs.s3.bucket=ainflue-alb-logs,access_logs.s3.prefix=prod",
                    "external-dns.alpha.kubernetes.io/hostname": f"api-{region_code}.ainflue.com",
                    "nginx.ingress.kubernetes.io/rate-limit-rps": "100",
                    "nginx.ingress.kubernetes.io/rate-limit-connections": "10"
                },
                "labels": {
                    "app": "ainflue",
                    "environment": "production",
                    "region": region_code,
                    "tier": "frontend"
                }
            },
            "spec": {
                "ingressClassName": "alb",
                "rules": [
                    {
                        "host": f"api-{region_code}.ainflue.com",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "ainflue-api",
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
                        "host": f"app-{region_code}.ainflue.com",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix", 
                                    "backend": {
                                        "service": {
                                            "name": "ainflue-frontend",
                                            "port": {
                                                "number": 3000
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ],
                "tls": [
                    {
                        "hosts": [
                            f"api-{region_code}.ainflue.com",
                            f"app-{region_code}.ainflue.com"
                        ],
                        "secretName": f"ainflue-tls-{region_code}"
                    }
                ]
            }
        }
    
    def generate_disaster_recovery_config(self, region_code: str) -> Dict[str, Any]:
        """Generate disaster recovery configuration"""
        region = self.regions[region_code]
        
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"disaster-recovery-{region_code}",
                "namespace": "production",
                "labels": {
                    "component": "disaster-recovery",
                    "region": region_code
                }
            },
            "data": {
                "rto_target_minutes": "15",  # Recovery Time Objective
                "rpo_target_minutes": "5",   # Recovery Point Objective
                "backup_region": region.backup_region or "",
                "backup_frequency_hours": "6",
                "backup_retention_days": "30",
                "failover_strategy": "automatic" if region.type == RegionType.PRIMARY else "manual",
                "health_check_url": f"https://api-{region_code}.ainflue.com/health",
                "monitoring_endpoints": json.dumps([
                    f"https://api-{region_code}.ainflue.com/metrics",
                    f"https://api-{region_code}.ainflue.com/health"
                ]),
                "backup_storage": region.s3_bucket + "-backups" if region.s3_bucket else "",
                "database_backup_enabled": "true",
                "cross_region_replication": "true" if region.backup_region else "false"
            }
        }
    
    def generate_global_load_balancer_config(self) -> Dict[str, Any]:
        """Generate enhanced global load balancer configuration with health checks"""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "global-load-balancer-config",
                "namespace": "production",
                "labels": {
                    "component": "global-load-balancer",
                    "tier": "infrastructure"
                }
            },
            "data": {
                "nginx.conf": """
# Global Load Balancer Configuration for Ainflue
upstream primary_region {
    least_conn;
    server api-us-east-1.ainflue.com:443 max_fails=3 fail_timeout=30s weight=10;
    keepalive 32;
}

upstream secondary_regions {
    least_conn;
    server api-us-west-2.ainflue.com:443 max_fails=3 fail_timeout=30s weight=8 backup;
    server api-eu-west-1.ainflue.com:443 max_fails=3 fail_timeout=30s weight=6 backup;
    server api-ap-southeast-1.ainflue.com:443 max_fails=3 fail_timeout=30s weight=4 backup;
    keepalive 16;
}

# Geolocation-based routing
map $http_cf_ipcountry $region_backend {
    default primary_region;
    US primary_region;
    CA primary_region;
    EU secondary_regions;
    GB secondary_regions;
    FR secondary_regions;
    DE secondary_regions;
    SG secondary_regions;
    JP secondary_regions;
    AU secondary_regions;
    IN secondary_regions;
}

# Health check configuration
upstream_conf {
    server;
    check interval=5000 rise=2 fall=3 timeout=3000 default_down=true type=http;
    check_http_send "GET /health HTTP/1.1\\r\\nHost: api.ainflue.com\\r\\n\\r\\n";
    check_http_expect_alive http_2xx http_3xx;
}

server {
    listen 80;
    listen 443 ssl http2;
    server_name api.ainflue.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/ainflue.crt;
    ssl_certificate_key /etc/ssl/private/ainflue.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
    
    # Main application
    location / {
        proxy_pass https://$region_backend;
        proxy_ssl_verify off;
        proxy_ssl_server_name on;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Region $region_backend;
        
        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        
        # Circuit breaker
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
        proxy_next_upstream_tries 3;
        proxy_next_upstream_timeout 10s;
    }
    
    # Status page
    location /status {
        stub_status on;
        access_log off;
        allow 127.0.0.1;
        allow 10.0.0.0/8;
        deny all;
    }
}
""",
                "health_check_config": json.dumps({
                    "check_interval": 5,
                    "timeout": 3,
                    "healthy_threshold": 2,
                    "unhealthy_threshold": 3,
                    "endpoints": [
                        "https://api-us-east-1.ainflue.com/health",
                        "https://api-us-west-2.ainflue.com/health", 
                        "https://api-eu-west-1.ainflue.com/health",
                        "https://api-ap-southeast-1.ainflue.com/health"
                    ]
                })
            }
        }
    
    def generate_all_production_configs(self, output_dir: str = "/home/runner/work/Ainflue/Ainflue/kubernetes/multi-region-ha"):
        """Generate all production-ready regional configurations with HA"""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate global configurations
        global_lb_config = self.generate_global_load_balancer_config()
        self.write_yaml(global_lb_config, os.path.join(output_dir, "global-load-balancer.yaml"))
        
        # Generate regional configurations
        for region_code, region in self.regions.items():
            region_dir = os.path.join(output_dir, region_code)
            os.makedirs(region_dir, exist_ok=True)
            
            # Generate HA cluster configuration
            cluster_config = self.generate_ha_cluster_config(region_code)
            self.write_yaml(cluster_config, os.path.join(region_dir, "ha-cluster-config.yaml"))
            
            # Generate production ingress
            ingress_config = self.generate_production_ingress_config(region_code)
            self.write_yaml(ingress_config, os.path.join(region_dir, "production-ingress.yaml"))
            
            # Generate disaster recovery config
            dr_config = self.generate_disaster_recovery_config(region_code)
            self.write_yaml(dr_config, os.path.join(region_dir, "disaster-recovery.yaml"))
            
            print(f"✅ Generated production HA configs for {region_code} ({region.name})")
        
        print(f"\n🎉 Production multi-region HA configurations generated successfully!")
        print(f"📁 Output directory: {output_dir}")
        print(f"🌍 Regions configured: {', '.join(self.regions.keys())}")
        print(f"🔄 High Availability: Enabled")
        print(f"🛡️ Disaster Recovery: Configured")
        print(f"⚖️ Load Balancing: Global with geo-routing")
    
    def write_yaml(self, obj: Any, file_path: str):
        """Write object to YAML file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            yaml.dump(obj, f, default_flow_style=False, sort_keys=False, indent=2)


if __name__ == "__main__":
    manager = ProductionMultiRegionManager()
    manager.generate_all_production_configs()