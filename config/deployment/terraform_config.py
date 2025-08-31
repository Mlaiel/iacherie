"""Terraform Configuration Module for IA-Influencer Agent Platform
===============================================================

Professional Terraform infrastructure-as-code configuration
for enterprise-grade multi-cloud AI-powered content protection platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml


@dataclass
class TerraformProvider:
    """Terraform provider configuration"""    name: str
    source: str
    version: str
    configuration: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TerraformModule:
    """Terraform module configuration"""    name: str
    source: str
    version: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TerraformResource:
    """Terraform resource configuration"""    type: str
    name: str
    configuration: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)


class TerraformConfig:
    """    Professional Terraform configuration manager for IA-Influencer Agent Platform.
    
    Provides enterprise-grade infrastructure automation:
    - Multi-cloud provider support (AWS, Azure, GCP)
    - Kubernetes cluster provisioning and management
    - Database clusters with high availability
    - Storage solutions for content and AI models
    - Networking and security configurations
    - Monitoring and logging infrastructure
    - CI/CD pipeline integration
    - State management and workspace separation
    """    
    def __init__(self, environment: str = "development", cloud_provider: str = "aws"):
        self.environment = environment
        self.cloud_provider = cloud_provider.lower()
        self.project_name = "ia-influencer-agent"
        self.terraform_version = "~> 1.5"
        
        # Common variables
        self.common_variables = {
            "project_name": {
                "description": "Project name",
                "type": "string",
                "default": self.project_name
            },
            "environment": {
                "description": "Environment name",
                "type": "string",
                "default": environment
            },
            "region": {
                "description": "Cloud region",
                "type": "string",
                "default": self._get_default_region()
            },
            "availability_zones": {
                "description": "Availability zones",
                "type": "list(string)",
                "default": self._get_default_azs()
            },
            "tags": {
                "description": "Common resource tags",
                "type": "map(string)",
                "default": {
                    "Project": "IA-Influencer-Agent",
                    "Environment": environment,
                    "Owner": "Fahed Mlaiel",
                    "Email": "mlaiel@live.de",
                    "ManagedBy": "Terraform",
                    "CostCenter": "IA-Platform",
                    "Compliance": "GDPR-CCPA"
                }
            }
        }
    
    def _get_default_region(self) -> str:
        """Get default region based on cloud provider"""        region_map = {
            "aws": "us-east-1",
            "azure": "East US",
            "gcp": "us-central1"
        }
        return region_map.get(self.cloud_provider, "us-east-1")
    
    def _get_default_azs(self) -> List[str]:
        """Get default availability zones"""        az_map = {
            "aws": ["us-east-1a", "us-east-1b", "us-east-1c"],
            "azure": ["1", "2", "3"],
            "gcp": ["us-central1-a", "us-central1-b", "us-central1-c"]
        }
        return az_map.get(self.cloud_provider, ["us-east-1a", "us-east-1b"])
    
    def get_terraform_configuration(self) -> Dict[str, Any]:
        """Generate main Terraform configuration"""        return {
            "terraform": {
                "required_version": self.terraform_version,
                "required_providers": self._get_required_providers(),
                "backend": self._get_backend_configuration()
            }
        }
    
    def _get_required_providers(self) -> Dict[str, Dict[str, str]]:
        """Get required providers based on cloud provider"""        base_providers = {
            "random": {
                "source": "hashicorp/random",
                "version": "~> 3.4"
            },
            "tls": {
                "source": "hashicorp/tls",
                "version": "~> 4.0"
            },
            "local": {
                "source": "hashicorp/local",
                "version": "~> 2.4"
            },
            "null": {
                "source": "hashicorp/null",
                "version": "~> 3.2"
            }
        }
        
        cloud_providers = {
            "aws": {
                "aws": {
                    "source": "hashicorp/aws",
                    "version": "~> 5.0"
                },
                "kubernetes": {
                    "source": "hashicorp/kubernetes",
                    "version": "~> 2.23"
                },
                "helm": {
                    "source": "hashicorp/helm",
                    "version": "~> 2.11"
                }
            },
            "azure": {
                "azurerm": {
                    "source": "hashicorp/azurerm",
                    "version": "~> 3.0"
                },
                "azuread": {
                    "source": "hashicorp/azuread",
                    "version": "~> 2.0"
                },
                "kubernetes": {
                    "source": "hashicorp/kubernetes",
                    "version": "~> 2.23"
                }
            },
            "gcp": {
                "google": {
                    "source": "hashicorp/google",
                    "version": "~> 5.0"
                },
                "google-beta": {
                    "source": "hashicorp/google-beta",
                    "version": "~> 5.0"
                },
                "kubernetes": {
                    "source": "hashicorp/kubernetes",
                    "version": "~> 2.23"
                }
            }
        }
        
        providers = {**base_providers, **cloud_providers.get(self.cloud_provider, {})}
        return providers
    
    def _get_backend_configuration(self) -> Dict[str, Any]:
        """Get backend configuration based on cloud provider"""        backend_configs = {
            "aws": {
                "s3": {
                    "bucket": f"{self.project_name}-terraform-state-{self.environment}",
                    "key": f"{self.environment}/terraform.tfstate",
                    "region": "us-east-1",
                    "encrypt": True,
                    "dynamodb_table": f"{self.project_name}-terraform-locks-{self.environment}"
                }
            },
            "azure": {
                "azurerm": {
                    "resource_group_name": f"{self.project_name}-terraform-rg",
                    "storage_account_name": f"{self.project_name.replace('-', '')}terraform{self.environment}",
                    "container_name": "tfstate",
                    "key": f"{self.environment}.terraform.tfstate"
                }
            },
            "gcp": {
                "gcs": {
                    "bucket": f"{self.project_name}-terraform-state-{self.environment}",
                    "prefix": f"terraform/{self.environment}"
                }
            }
        }
        
        return backend_configs.get(self.cloud_provider, {})
    
    def get_provider_configurations(self) -> Dict[str, Any]:
        """Generate provider configurations"""        provider_configs = {
            "aws": {
                "provider": {
                    "aws": {
                        "region": "${var.region}",
                        "default_tags": {
                            "tags": "${var.tags}"
                        }
                    },
                    "kubernetes": {
                        "host": "${module.eks.cluster_endpoint}",
                        "cluster_ca_certificate": "${base64decode(module.eks.cluster_certificate_authority_data)}",
                        "token": "${data.aws_eks_cluster_auth.cluster.token}"
                    }
                }
            },
            "azure": {
                "provider": {
                    "azurerm": {
                        "features": {}
                    },
                    "kubernetes": {
                        "host": "${module.aks.kube_config.0.host}",
                        "client_certificate": "${base64decode(module.aks.kube_config.0.client_certificate)}",
                        "client_key": "${base64decode(module.aks.kube_config.0.client_key)}",
                        "cluster_ca_certificate": "${base64decode(module.aks.kube_config.0.cluster_ca_certificate)}"
                    }
                }
            },
            "gcp": {
                "provider": {
                    "google": {
                        "project": "${var.project_id}",
                        "region": "${var.region}"
                    },
                    "kubernetes": {
                        "host": "https://${module.gke.endpoint}",
                        "token": "${data.google_client_config.default.access_token}",
                        "cluster_ca_certificate": "${base64decode(module.gke.ca_certificate)}"
                    }
                }
            }
        }
        
        return provider_configs.get(self.cloud_provider, {})
    
    def get_data_sources(self) -> Dict[str, Any]:
        """Generate data sources"""        data_sources = {
            "aws": {
                "data": {
                    "aws_caller_identity": {
                        "current": {}
                    },
                    "aws_region": {
                        "current": {}
                    },
                    "aws_availability_zones": {
                        "available": {
                            "state": "available"
                        }
                    },
                    "aws_eks_cluster_auth": {
                        "cluster": {
                            "name": "${module.eks.cluster_name}"
                        }
                    }
                }
            },
            "azure": {
                "data": {
                    "azurerm_client_config": {
                        "current": {}
                    }
                }
            },
            "gcp": {
                "data": {
                    "google_client_config": {
                        "default": {}
                    },
                    "google_project": {
                        "current": {}
                    }
                }
            }
        }
        
        return data_sources.get(self.cloud_provider, {})
    
    def get_modules_configuration(self) -> Dict[str, Any]:
        """Generate modules configuration"""        modules = {
            "aws": self._get_aws_modules(),
            "azure": self._get_azure_modules(),
            "gcp": self._get_gcp_modules()
        }
        
        return {"module": modules.get(self.cloud_provider, {})}
    
    def _get_aws_modules(self) -> Dict[str, Any]:
        """Get AWS-specific modules"""        return {
            "vpc": {
                "source": "terraform-aws-modules/vpc/aws",
                "version": "~> 5.0",
                "name": "${var.project_name}-vpc-${var.environment}",
                "cidr": "10.0.0.0/16",
                "azs": "${var.availability_zones}",
                "private_subnets": ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
                "public_subnets": ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"],
                "database_subnets": ["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"],
                "enable_nat_gateway": True,
                "enable_vpn_gateway": False,
                "enable_dns_hostnames": True,
                "enable_dns_support": True,
                "public_subnet_tags": {
                    "kubernetes.io/role/elb": "1"
                },
                "private_subnet_tags": {
                    "kubernetes.io/role/internal-elb": "1"
                },
                "tags": "${var.tags}"
            },
            "eks": {
                "source": "terraform-aws-modules/eks/aws",
                "version": "~> 19.0",
                "cluster_name": "${var.project_name}-eks-${var.environment}",
                "cluster_version": "1.28",
                "vpc_id": "${module.vpc.vpc_id}",
                "subnet_ids": "${module.vpc.private_subnets}",
                "cluster_endpoint_public_access": True,
                "cluster_endpoint_private_access": True,
                "cluster_addons": {
                    "coredns": {
                        "most_recent": True
                    },
                    "kube-proxy": {
                        "most_recent": True
                    },
                    "vpc-cni": {
                        "most_recent": True
                    },
                    "aws-ebs-csi-driver": {
                        "most_recent": True
                    }
                },
                "eks_managed_node_groups": {
                    "main": {
                        "min_size": 1 if self.environment == "development" else 3,
                        "max_size": 3 if self.environment == "development" else 10,
                        "desired_size": 2 if self.environment == "development" else 6,
                        "instance_types": ["t3.medium"] if self.environment == "development" else ["m5.large"],
                        "capacity_type": "ON_DEMAND",
                        "ami_type": "AL2_x86_64",
                        "disk_size": 50,
                        "tags": "${var.tags}"
                    }
                },
                "tags": "${var.tags}"
            },
            "rds": {
                "source": "terraform-aws-modules/rds/aws",
                "version": "~> 6.0",
                "identifier": "${var.project_name}-postgres-${var.environment}",
                "engine": "postgres",
                "engine_version": "15.4",
                "family": "postgres15",
                "major_engine_version": "15",
                "instance_class": "db.t3.micro" if self.environment == "development" else "db.r5.large",
                "allocated_storage": 20 if self.environment == "development" else 100,
                "max_allocated_storage": 100 if self.environment == "development" else 1000,
                "storage_encrypted": True,
                "db_name": "ia_influencer",
                "username": "ia_admin",
                "manage_master_user_password": True,
                "port": 5432,
                "multi_az": False if self.environment == "development" else True,
                "db_subnet_group_name": "${module.vpc.database_subnet_group}",
                "vpc_security_group_ids": ["${module.security_group.security_group_id}"],
                "backup_retention_period": 7,
                "backup_window": "03:00-04:00",
                "maintenance_window": "sun:04:00-sun:05:00",
                "enabled_cloudwatch_logs_exports": ["postgresql", "upgrade"],
                "create_cloudwatch_log_group": True,
                "skip_final_snapshot": True if self.environment == "development" else False,
                "deletion_protection": False if self.environment == "development" else True,
                "performance_insights_enabled": True,
                "performance_insights_retention_period": 7,
                "create_monitoring_role": True,
                "monitoring_interval": 60,
                "tags": "${var.tags}"
            },
            "elasticache": {
                "source": "terraform-aws-modules/elasticache/aws",
                "version": "~> 1.0",
                "replication_group_id": "${var.project_name}-redis-${var.environment}",
                "description": "Redis cluster for IA-Influencer Agent",
                "node_type": "cache.t3.micro" if self.environment == "development" else "cache.r6g.large",
                "port": 6379,
                "parameter_group_name": "default.redis7",
                "num_cache_clusters": 1 if self.environment == "development" else 2,
                "automatic_failover_enabled": False if self.environment == "development" else True,
                "multi_az_enabled": False if self.environment == "development" else True,
                "engine_version": "7.0",
                "at_rest_encryption_enabled": True,
                "transit_encryption_enabled": True,
                "auth_token": "${random_password.redis_auth_token.result}",
                "subnet_group_name": "${module.vpc.elasticache_subnet_group}",
                "security_group_ids": ["${module.security_group.security_group_id}"],
                "tags": "${var.tags}"
            },
            "s3_bucket": {
                "source": "terraform-aws-modules/s3-bucket/aws",
                "version": "~> 3.0",
                "bucket": "${var.project_name}-content-${var.environment}-${random_id.bucket_suffix.hex}",
                "versioning": {
                    "enabled": True
                },
                "server_side_encryption_configuration": {
                    "rule": {
                        "apply_server_side_encryption_by_default": {
                            "sse_algorithm": "AES256"
                        }
                    }
                },
                "lifecycle_configuration": {
                    "rule": [
                        {
                            "id": "transition_to_ia",
                            "status": "Enabled",
                            "transition": [
                                {
                                    "days": 30,
                                    "storage_class": "STANDARD_IA"
                                },
                                {
                                    "days": 90,
                                    "storage_class": "GLACIER"
                                }
                            ]
                        }
                    ]
                },
                "tags": "${var.tags}"
            }
        }
    
    def _get_azure_modules(self) -> Dict[str, Any]:
        """Get Azure-specific modules"""        return {
            "resource_group": {
                "source": "Azure/resourcegroup/azurerm",
                "version": "~> 1.0",
                "location": "${var.region}",
                "name": "${var.project_name}-rg-${var.environment}",
                "tags": "${var.tags}"
            },
            "network": {
                "source": "Azure/network/azurerm",
                "version": "~> 5.0",
                "resource_group_name": "${module.resource_group.name}",
                "address_spaces": ["10.0.0.0/16"],
                "subnet_prefixes": ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
                "subnet_names": ["aks-subnet", "database-subnet", "storage-subnet"],
                "depends_on": ["module.resource_group"],
                "tags": "${var.tags}"
            },
            "aks": {
                "source": "Azure/aks/azurerm",
                "version": "~> 7.0",
                "resource_group_name": "${module.resource_group.name}",
                "cluster_name": "${var.project_name}-aks-${var.environment}",
                "kubernetes_version": "1.28.3",
                "orchestrator_version": "1.28.3",
                "prefix": "${var.project_name}-${var.environment}",
                "network_plugin": "azure",
                "vnet_subnet_id": "${module.network.vnet_subnets[0]}",
                "os_disk_size_gb": 50,
                "sku_tier": "Free" if self.environment == "development" else "Standard",
                "enable_role_based_access_control": True,
                "rbac_aad_managed": True,
                "private_cluster_enabled": False,
                "enable_http_application_routing": True,
                "enable_azure_policy": True,
                "enable_auto_scaling": True,
                "enable_host_encryption": True,
                "log_analytics_workspace_enabled": True,
                "agents_min_count": 1,
                "agents_max_count": 3 if self.environment == "development" else 10,
                "agents_count": 2 if self.environment == "development" else 6,
                "agents_max_pods": 100,
                "agents_pool_name": "system",
                "agents_availability_zones": ["1", "2", "3"],
                "agents_type": "VirtualMachineScaleSets",
                "agents_size": "Standard_DS2_v2" if self.environment == "development" else "Standard_DS3_v2",
                "tags": "${var.tags}"
            },
            "postgresql": {
                "source": "Azure/postgresql/azurerm",
                "version": "~> 3.0",
                "resource_group_name": "${module.resource_group.name}",
                "location": "${var.region}",
                "server_name": "${var.project_name}-postgres-${var.environment}",
                "sku_name": "B_Standard_B1ms" if self.environment == "development" else "GP_Standard_D2s_v3",
                "storage_mb": 32768 if self.environment == "development" else 131072,
                "backup_retention_days": 7,
                "geo_redundant_backup_enabled": False if self.environment == "development" else True,
                "administrator_login": "ia_admin",
                "administrator_password": "${random_password.postgres_password.result}",
                "server_version": "15",
                "ssl_enforcement_enabled": True,
                "ssl_minimal_tls_version_enforced": "TLS1_2",
                "db_names": ["ia_influencer"],
                "db_charset": "UTF8",
                "db_collation": "English_United States.1252",
                "tags": "${var.tags}"
            }
        }
    
    def _get_gcp_modules(self) -> Dict[str, Any]:
        """Get GCP-specific modules"""        return {
            "vpc": {
                "source": "terraform-google-modules/network/google",
                "version": "~> 7.0",
                "project_id": "${var.project_id}",
                "network_name": "${var.project_name}-vpc-${var.environment}",
                "routing_mode": "REGIONAL",
                "subnets": [
                    {
                        "subnet_name": "gke-subnet",
                        "subnet_ip": "10.0.0.0/24",
                        "subnet_region": "${var.region}",
                        "subnet_private_access": "true",
                        "subnet_flow_logs": "true",
                        "description": "Subnet for GKE cluster"
                    },
                    {
                        "subnet_name": "database-subnet",
                        "subnet_ip": "10.0.1.0/24",
                        "subnet_region": "${var.region}",
                        "subnet_private_access": "true",
                        "description": "Subnet for databases"
                    }
                ],
                "secondary_ranges": {
                    "gke-subnet": [
                        {
                            "range_name": "gke-pods",
                            "ip_cidr_range": "10.1.0.0/16"
                        },
                        {
                            "range_name": "gke-services",
                            "ip_cidr_range": "10.2.0.0/16"
                        }
                    ]
                }
            },
            "gke": {
                "source": "terraform-google-modules/kubernetes-engine/google//modules/safer-cluster",
                "version": "~> 29.0",
                "project_id": "${var.project_id}",
                "name": "${var.project_name}-gke-${var.environment}",
                "region": "${var.region}",
                "network": "${module.vpc.network_name}",
                "subnetwork": "${module.vpc.subnets_names[0]}",
                "ip_range_pods": "gke-pods",
                "ip_range_services": "gke-services",
                "kubernetes_version": "1.28.3",
                "release_channel": "STABLE",
                "enable_private_endpoint": False,
                "enable_private_nodes": True,
                "master_ipv4_cidr_block": "172.16.0.0/28",
                "node_pools": [
                    {
                        "name": "main-pool",
                        "machine_type": "e2-standard-2" if self.environment == "development" else "e2-standard-4",
                        "node_locations": "${var.region}-a,${var.region}-b,${var.region}-c",
                        "min_count": 1,
                        "max_count": 3 if self.environment == "development" else 10,
                        "local_ssd_count": 0,
                        "spot": True if self.environment == "development" else False,
                        "disk_size_gb": 50,
                        "disk_type": "pd-ssd",
                        "image_type": "COS_CONTAINERD",
                        "enable_gcfs": False,
                        "enable_gvnic": False,
                        "auto_repair": True,
                        "auto_upgrade": True,
                        "preemptible": True if self.environment == "development" else False
                    }
                ]
            },
            "postgresql": {
                "source": "GoogleCloudPlatform/sql-db/google//modules/postgresql",
                "version": "~> 16.0",
                "project_id": "${var.project_id}",
                "name": "${var.project_name}-postgres-${var.environment}",
                "region": "${var.region}",
                "zone": "${var.region}-a",
                "database_version": "POSTGRES_15",
                "tier": "db-f1-micro" if self.environment == "development" else "db-custom-4-16384",
                "availability_type": "ZONAL" if self.environment == "development" else "REGIONAL",
                "disk_type": "PD_SSD",
                "disk_size": 20 if self.environment == "development" else 100,
                "disk_autoresize": True,
                "disk_autoresize_limit": 100 if self.environment == "development" else 1000,
                "backup_configuration": {
                    "enabled": True,
                    "start_time": "03:00",
                    "location": "${var.region}",
                    "backup_retention_settings": {
                        "retained_backups": 7,
                        "retention_unit": "COUNT"
                    }
                },
                "ip_configuration": {
                    "ipv4_enabled": True,
                    "private_network": "${module.vpc.network_self_link}",
                    "require_ssl": True
                },
                "database_flags": [
                    {
                        "name": "log_checkpoints",
                        "value": "on"
                    },
                    {
                        "name": "log_connections",
                        "value": "on"
                    }
                ],
                "user_labels": "${var.tags}"
            }
        }
    
    def get_random_resources(self) -> Dict[str, Any]:
        """Generate random resources for unique naming"""        return {
            "resource": {
                "random_id": {
                    "bucket_suffix": {
                        "byte_length": 4
                    }
                },
                "random_password": {
                    "postgres_password": {
                        "length": 32,
                        "special": True
                    },
                    "redis_auth_token": {
                        "length": 64,
                        "special": False
                    }
                }
            }
        }
    
    def get_outputs_configuration(self) -> Dict[str, Any]:
        """Generate outputs configuration"""        outputs = {
            "aws": {
                "vpc_id": {
                    "description": "VPC ID",
                    "value": "${module.vpc.vpc_id}"
                },
                "eks_cluster_name": {
                    "description": "EKS cluster name",
                    "value": "${module.eks.cluster_name}"
                },
                "eks_cluster_endpoint": {
                    "description": "EKS cluster endpoint",
                    "value": "${module.eks.cluster_endpoint}",
                    "sensitive": True
                },
                "rds_endpoint": {
                    "description": "RDS endpoint",
                    "value": "${module.rds.db_instance_endpoint}"
                },
                "elasticache_endpoint": {
                    "description": "ElastiCache endpoint",
                    "value": "${module.elasticache.primary_endpoint_address}"
                },
                "s3_bucket_name": {
                    "description": "S3 bucket name",
                    "value": "${module.s3_bucket.s3_bucket_id}"
                }
            },
            "azure": {
                "resource_group_name": {
                    "description": "Resource group name",
                    "value": "${module.resource_group.name}"
                },
                "aks_cluster_name": {
                    "description": "AKS cluster name",
                    "value": "${module.aks.aks_name}"
                },
                "aks_cluster_fqdn": {
                    "description": "AKS cluster FQDN",
                    "value": "${module.aks.aks_fqdn}",
                    "sensitive": True
                },
                "postgresql_fqdn": {
                    "description": "PostgreSQL FQDN",
                    "value": "${module.postgresql.server_fqdn}"
                }
            },
            "gcp": {
                "project_id": {
                    "description": "GCP Project ID",
                    "value": "${var.project_id}"
                },
                "gke_cluster_name": {
                    "description": "GKE cluster name",
                    "value": "${module.gke.name}"
                },
                "gke_cluster_endpoint": {
                    "description": "GKE cluster endpoint",
                    "value": "${module.gke.endpoint}",
                    "sensitive": True
                },
                "postgresql_connection_name": {
                    "description": "PostgreSQL connection name",
                    "value": "${module.postgresql.instance_connection_name}"
                }
            }
        }
        
        return {"output": outputs.get(self.cloud_provider, {})}
    
    def generate_main_tf(self, output_file: str = "main.tf") -> None:
        """Generate main.tf file"""        config = {}
        
        # Add terraform configuration
        config.update(self.get_terraform_configuration())
        
        # Add provider configurations
        config.update(self.get_provider_configurations())
        
        # Add data sources
        config.update(self.get_data_sources())
        
        # Add random resources
        config.update(self.get_random_resources())
        
        # Add modules
        config.update(self.get_modules_configuration())
        
        # Add outputs
        config.update(self.get_outputs_configuration())
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(f"# Terraform configuration for IA-Influencer Agent Platform\n")
            f.write(f"# Author: Fahed Mlaiel <mlaiel@live.de>\n")
            f.write(f"# Environment: {self.environment}\n")
            f.write(f"# Cloud Provider: {self.cloud_provider.upper()}\n\n")
            
            self._write_hcl_block(f, config)
    
    def generate_variables_tf(self, output_file: str = "variables.tf") -> None:
        """Generate variables.tf file"""        with open(output_file, 'w') as f:
            f.write("# Variables for IA-Influencer Agent Platform\n")
            f.write(f"# Author: Fahed Mlaiel <mlaiel@live.de>\n\n")
            
            for name, config in self.common_variables.items():
                f.write(f'variable "{name}" {{\n')
                f.write(f'  description = "{config["description"]}"\n')
                f.write(f'  type        = {config["type"]}\n')
                
                if "default" in config:
                    if isinstance(config["default"], str):
                        f.write(f'  default     = "{config["default"]}"\n')
                    elif isinstance(config["default"], (list, dict)):
                        f.write(f'  default     = {json.dumps(config["default"])}\n')
                    else:
                        f.write(f'  default     = {config["default"]}\n')
                
                f.write("}\n\n")
            
            # Add cloud-specific variables
            if self.cloud_provider == "gcp":
                f.write('variable "project_id" {\n')
                f.write('  description = "GCP Project ID"\n')
                f.write('  type        = string\n')
                f.write("}\n\n")
    
    def generate_terraform_tfvars(self, output_file: str = f"terraform.tfvars") -> None:
        """Generate terraform.tfvars file"""        with open(output_file, 'w') as f:
            f.write("# Terraform variables for IA-Influencer Agent Platform\n")
            f.write(f"# Author: Fahed Mlaiel <mlaiel@live.de>\n")
            f.write(f"# Environment: {self.environment}\n\n")
            
            f.write(f'project_name = "{self.project_name}"\n')
            f.write(f'environment = "{self.environment}"\n')
            f.write(f'region = "{self._get_default_region()}"\n')
            f.write(f'availability_zones = {json.dumps(self._get_default_azs())}\n\n')
            
            f.write('tags = {\n')
            for key, value in self.common_variables["tags"]["default"].items():
                f.write(f'  {key} = "{value}"\n')
            f.write('}\n\n')
            
            if self.cloud_provider == "gcp":
                f.write(f'project_id = "ia-influencer-agent-{self.environment}"\n')
    
    def _write_hcl_block(self, file, config: Dict[str, Any], indent: int = 0) -> None:
        """Write HCL block to file"""        for key, value in config.items():
            if isinstance(value, dict) and any(isinstance(v, dict) for v in value.values()):
                # This is a configuration block
                file.write("  " * indent + f"{key} {{\n")
                self._write_hcl_block(file, value, indent + 1)
                file.write("  " * indent + "}\n\n")
            elif isinstance(value, dict):
                # This is a simple key-value block
                file.write("  " * indent + f'{key} = {{\n')
                for k, v in value.items():
                    if isinstance(v, str):
                        file.write("  " * (indent + 1) + f'{k} = "{v}"\n')
                    else:
                        file.write("  " * (indent + 1) + f'{k} = {json.dumps(v)}\n')
                file.write("  " * indent + "}\n\n")
            elif isinstance(value, (list, str, int, bool)):
                if isinstance(value, str):
                    file.write("  " * indent + f'{key} = "{value}"\n')
                else:
                    file.write("  " * indent + f'{key} = {json.dumps(value)}\n')
    
    def get_deployment_scripts(self) -> Dict[str, str]:
        """Generate deployment scripts"""        return {
            "deploy.sh": self._get_deployment_script(),
            "destroy.sh": self._get_destroy_script(),
            "plan.sh": self._get_plan_script(),
            "init.sh": self._get_init_script()
        }
    
    def _get_deployment_script(self) -> str:
        """Generate deployment script"""        return f'''#!/bin/bash
# Terraform deployment script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -e

ENVIRONMENT="{self.environment}"
CLOUD_PROVIDER="{self.cloud_provider.upper()}"

echo "🚀 Deploying IA-Influencer Agent infrastructure..."
echo "Environment: $ENVIRONMENT"
echo "Cloud Provider: $CLOUD_PROVIDER"

# Check prerequisites
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform is not installed"
    exit 1
fi

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Validate configuration
echo "✅ Validating Terraform configuration..."
terraform validate

# Plan deployment
echo "📋 Planning deployment..."
terraform plan -var-file="terraform.tfvars" -out="tfplan"

# Apply deployment
echo "🚀 Applying deployment..."
terraform apply "tfplan"

# Show outputs
echo "📊 Deployment outputs:"
terraform output

echo "✅ Infrastructure deployed successfully!"
echo "🎯 Next steps:"
echo "1. Configure kubectl/az/gcloud CLI"
echo "2. Deploy Kubernetes manifests"
echo "3. Setup monitoring and alerting"
echo "4. Configure CI/CD pipelines"
'''
    
    def _get_destroy_script(self) -> str:
        """Generate destroy script"""        return f'''#!/bin/bash
# Terraform destroy script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -e

ENVIRONMENT="{self.environment}"

echo "⚠️  WARNING: This will destroy ALL infrastructure!"
echo "Environment: $ENVIRONMENT"
echo ""
read -p "Are you sure you want to proceed? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment destruction cancelled"
    exit 0
fi

echo "💥 Destroying infrastructure..."

# Plan destroy
terraform plan -destroy -var-file="terraform.tfvars" -out="destroy-plan"

# Apply destroy
terraform apply "destroy-plan"

echo "✅ Infrastructure destroyed successfully"
'''
    
    def _get_plan_script(self) -> str:
        """Generate plan script"""        return f'''#!/bin/bash
# Terraform plan script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -e

ENVIRONMENT="{self.environment}"

echo "📋 Planning Terraform deployment..."
echo "Environment: $ENVIRONMENT"

# Initialize if needed
if [ ! -d ".terraform" ]; then
    echo "📦 Initializing Terraform..."
    terraform init
fi

# Validate configuration
terraform validate

# Plan deployment
terraform plan -var-file="terraform.tfvars"

echo "✅ Plan completed successfully"
'''
    
    def _get_init_script(self) -> str:
        """Generate init script"""        return f'''#!/bin/bash
# Terraform initialization script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -e

ENVIRONMENT="{self.environment}"
CLOUD_PROVIDER="{self.cloud_provider.upper()}"

echo "🔧 Initializing Terraform for IA-Influencer Agent..."
echo "Environment: $ENVIRONMENT"
echo "Cloud Provider: $CLOUD_PROVIDER"

# Create backend resources if needed
case "$CLOUD_PROVIDER" in
    "AWS")
        echo "Creating S3 backend resources..."
        aws s3 mb s3://{self.project_name}-terraform-state-{self.environment} || true
        aws dynamodb create-table \\
            --table-name {self.project_name}-terraform-locks-{self.environment} \\
            --attribute-definitions AttributeName=LockID,AttributeType=S \\
            --key-schema AttributeName=LockID,KeyType=HASH \\
            --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 || true
        ;;
    "AZURE")
        echo "Creating Azure backend resources..."
        az group create --name {self.project_name}-terraform-rg --location "{self._get_default_region()}" || true
        az storage account create \\
            --resource-group {self.project_name}-terraform-rg \\
            --name {self.project_name.replace('-', '')}terraform{self.environment} \\
            --sku Standard_LRS \\
            --encryption-services blob || true
        az storage container create \\
            --name tfstate \\
            --account-name {self.project_name.replace('-', '')}terraform{self.environment} || true
        ;;
    "GCP")
        echo "Creating GCS backend resources..."
        gsutil mb gs://{self.project_name}-terraform-state-{self.environment} || true
        gsutil versioning set on gs://{self.project_name}-terraform-state-{self.environment} || true
        ;;
esac

# Initialize Terraform
terraform init

echo "✅ Terraform initialized successfully"
'''
    
    def generate_all_files(self, output_dir: str = "./terraform") -> None:
        """Generate all Terraform files"""        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate main configuration files
        self.generate_main_tf(f"{output_dir}/main.tf")
        self.generate_variables_tf(f"{output_dir}/variables.tf")
        self.generate_terraform_tfvars(f"{output_dir}/terraform.tfvars")
        
        # Generate deployment scripts
        scripts = self.get_deployment_scripts()
        for script_name, script_content in scripts.items():
            script_path = Path(output_dir) / script_name
            script_path.write_text(script_content)
            script_path.chmod(0o755)  # Make executable
        
        # Generate README
        readme_content = f"""# Terraform Infrastructure for IA-Influencer Agent Platform

## Overview
This directory contains Terraform configuration for deploying IA-Influencer Agent Platform on {self.cloud_provider.upper()}.

**Author**: Fahed Mlaiel <mlaiel@live.de>
**Environment**: {self.environment}
**Cloud Provider**: {self.cloud_provider.upper()}

## Prerequisites
- Terraform >= 1.5
- {self.cloud_provider.upper()} CLI configured
- Appropriate cloud credentials

## Usage

### 1. Initialize
```bash
./init.sh
```

### 2. Plan
```bash
./plan.sh
```

### 3. Deploy
```bash
./deploy.sh
```

### 4. Destroy (when needed)
```bash
./destroy.sh
```

## Files
- `main.tf` - Main Terraform configuration
- `variables.tf` - Variable definitions
- `terraform.tfvars` - Variable values
- `deploy.sh` - Deployment script
- `destroy.sh` - Destruction script
- `plan.sh` - Planning script
- `init.sh` - Initialization script

## Security
This infrastructure includes:
- Network security groups/firewalls
- Encryption at rest and in transit
- RBAC for Kubernetes
- Private networking where possible
- Monitoring and logging

## Support
For issues or questions, contact: mlaiel@live.de
"""        
        with open(f"{output_dir}/README.md", 'w') as f:
            f.write(readme_content)
