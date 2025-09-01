"""Google Cloud Platform Configuration Module for IA-Influencer Agent Platform
===========================================================================

Professional GCP cloud infrastructure configuration
for enterprise-grade AI-powered content protection and monetization platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
from pathlib import Path


class GCPConfig:
    """
    Professional Google Cloud Platform configuration manager for IA-Influencer Agent Platform.
    
    Provides enterprise-grade GCP services integration:
    - GKE clusters for Kubernetes orchestration
    - Cloud SQL for PostgreSQL and Memorystore for Redis
    - Cloud Storage buckets for content and AI models
    - Cloud Run services for containerized microservices
    - Cloud Functions for serverless AI processing
    - API Gateway for external integrations
    - Cloud CDN for global content delivery
    - AI Platform and Vision API for content analysis
    - Cloud Monitoring for comprehensive observability
    - Secret Manager for secrets management
    """
    
    def __init__(self, environment: str = "development", region: str = "us-central1", project_id: str = "ia-influencer-agent"):
        self.environment = environment
        self.region = region
        self.project_id = project_id
        self.zone = f"{region}-a"
        
        # Common labels
        self.default_labels = {
            "project": "ia-influencer-agent",
            "environment": environment,
            "owner": "fahed-mlaiel",
            "email": "mlaiel-live-de",
            "managed-by": "terraform",
            "cost-center": "ia-platform",
            "compliance": "gdpr-ccpa"
        }
    
    def get_vpc_configuration(self) -> Dict[str, Any]:
        """Generate VPC network configuration"""
        return {
            "resource": {
                "google_compute_network": {
                    "vpc_network": {
                        "name": f"ia-influencer-vpc-{self.environment}",
                        "project": self.project_id,
                        "auto_create_subnetworks": False,
                        "description": f"VPC network for IA-Influencer Agent {self.environment} environment"
                    }
                },
                "google_compute_subnetwork": {
                    "gke_subnet": {
                        "name": f"ia-influencer-gke-subnet-{self.environment}",
                        "project": self.project_id,
                        "region": self.region,
                        "network": "${google_compute_network.vpc_network.id}",
                        "ip_cidr_range": "10.0.0.0/24",
                        "description": "Subnet for GKE cluster",
                        "secondary_ip_range": [
                            {
                                "range_name": "gke-pods",
                                "ip_cidr_range": "10.1.0.0/16"
                            },
                            {
                                "range_name": "gke-services",
                                "ip_cidr_range": "10.2.0.0/16"
                            }
                        ]
                    },
                    "database_subnet": {
                        "name": f"ia-influencer-db-subnet-{self.environment}",
                        "project": self.project_id,
                        "region": self.region,
                        "network": "${google_compute_network.vpc_network.id}",
                        "ip_cidr_range": "10.0.1.0/24",
                        "description": "Subnet for databases"
                    },
                    "cloud_run_subnet": {
                        "name": f"ia-influencer-run-subnet-{self.environment}",
                        "project": self.project_id,
                        "region": self.region,
                        "network": "${google_compute_network.vpc_network.id}",
                        "ip_cidr_range": "10.0.2.0/24",
                        "description": "Subnet for Cloud Run services"
                    }
                }
            }
        }
    
    def get_firewall_configuration(self) -> Dict[str, Any]:
        """Generate firewall rules configuration"""
        return {
            "resource": {
                "google_compute_firewall": {
                    "allow_internal": {
                        "name": f"ia-influencer-allow-internal-{self.environment}",
                        "project": self.project_id,
                        "network": "${google_compute_network.vpc_network.id}",
                        "description": "Allow internal communication",
                        "allow": [
                            {
                                "protocol": "tcp",
                                "ports": ["0-65535"]
                            },
                            {
                                "protocol": "udp",
                                "ports": ["0-65535"]
                            },
                            {
                                "protocol": "icmp"
                            }
                        ],
                        "source_ranges": ["10.0.0.0/8"]
                    },
                    "allow_http_https": {
                        "name": f"ia-influencer-allow-http-https-{self.environment}",
                        "project": self.project_id,
                        "network": "${google_compute_network.vpc_network.id}",
                        "description": "Allow HTTP and HTTPS traffic",
                        "allow": [
                            {
                                "protocol": "tcp",
                                "ports": ["80", "443", "8080"]
                            }
                        ],
                        "source_ranges": ["0.0.0.0/0"],
                        "target_tags": ["web-server"]
                    },
                    "allow_ssh": {
                        "name": f"ia-influencer-allow-ssh-{self.environment}",
                        "project": self.project_id,
                        "network": "${google_compute_network.vpc_network.id}",
                        "description": "Allow SSH access",
                        "allow": [
                            {
                                "protocol": "tcp",
                                "ports": ["22"]
                            }
                        ],
                        "source_ranges": ["0.0.0.0/0"],
                        "target_tags": ["ssh-access"]
                    }
                }
            }
        }
    
    def get_gke_configuration(self) -> Dict[str, Any]:
        """Generate GKE cluster configuration"""
        node_count = 1 if self.environment == "development" else 3
        min_nodes = 1
        max_nodes = 3 if self.environment == "development" else 10
        machine_type = "e2-standard-2" if self.environment == "development" else "e2-standard-4"
        
        return {
            "resource": {
                "google_service_account": {
                    "gke_service_account": {
                        "account_id": f"gke-sa-{self.environment}",
                        "display_name": f"GKE Service Account - {self.environment}",
                        "project": self.project_id
                    }
                },
                "google_project_iam_member": {
                    "gke_service_account_roles": [
                        {
                            "project": self.project_id,
                            "role": "roles/logging.logWriter",
                            "member": "serviceAccount:${google_service_account.gke_service_account.email}"
                        },
                        {
                            "project": self.project_id,
                            "role": "roles/monitoring.metricWriter",
                            "member": "serviceAccount:${google_service_account.gke_service_account.email}"
                        },
                        {
                            "project": self.project_id,
                            "role": "roles/monitoring.viewer",
                            "member": "serviceAccount:${google_service_account.gke_service_account.email}"
                        },
                        {
                            "project": self.project_id,
                            "role": "roles/storage.objectViewer",
                            "member": "serviceAccount:${google_service_account.gke_service_account.email}"
                        }
                    ]
                },
                "google_container_cluster": {
                    "gke_cluster": {
                        "name": f"ia-influencer-gke-{self.environment}",
                        "project": self.project_id,
                        "location": self.zone if self.environment == "development" else self.region,
                        "description": f"GKE cluster for IA-Influencer Agent {self.environment}",
                        "network": "${google_compute_network.vpc_network.id}",
                        "subnetwork": "${google_compute_subnetwork.gke_subnet.id}",
                        "initial_node_count": 1,
                        "remove_default_node_pool": True,
                        "deletion_protection": False if self.environment == "development" else True,
                        "ip_allocation_policy": {
                            "cluster_secondary_range_name": "gke-pods",
                            "services_secondary_range_name": "gke-services"
                        },
                        "network_policy": {
                            "enabled": True
                        },
                        "addons_config": {
                            "http_load_balancing": {
                                "disabled": False
                            },
                            "network_policy_config": {
                                "disabled": False
                            },
                            "gcp_filestore_csi_driver_config": {
                                "enabled": True
                            }
                        },
                        "workload_identity_config": {
                            "workload_pool": f"{self.project_id}.svc.id.goog"
                        },
                        "resource_labels": self.default_labels
                    }
                },
                "google_container_node_pool": {
                    "primary_nodes": {
                        "name": f"primary-node-pool-{self.environment}",
                        "project": self.project_id,
                        "location": self.zone if self.environment == "development" else self.region,
                        "cluster": "${google_container_cluster.gke_cluster.name}",
                        "node_count": node_count,
                        "autoscaling": {
                            "min_node_count": min_nodes,
                            "max_node_count": max_nodes
                        },
                        "node_config": {
                            "preemptible": True if self.environment == "development" else False,
                            "machine_type": machine_type,
                            "disk_size_gb": 50,
                            "disk_type": "pd-ssd",
                            "image_type": "COS_CONTAINERD",
                            "service_account": "${google_service_account.gke_service_account.email}",
                            "oauth_scopes": [
                                "https://www.googleapis.com/auth/cloud-platform"
                            ],
                            "labels": self.default_labels,
                            "tags": ["gke-node", f"gke-{self.environment}"],
                            "workload_metadata_config": {
                                "mode": "GKE_METADATA"
                            }
                        },
                        "management": {
                            "auto_repair": True,
                            "auto_upgrade": True
                        }
                    },
                    "gpu_nodes": {
                        "name": f"gpu-node-pool-{self.environment}",
                        "project": self.project_id,
                        "location": self.zone if self.environment == "development" else self.region,
                        "cluster": "${google_container_cluster.gke_cluster.name}",
                        "initial_node_count": 0 if self.environment == "development" else 1,
                        "autoscaling": {
                            "min_node_count": 0,
                            "max_node_count": 2 if self.environment == "development" else 5
                        },
                        "node_config": {
                            "preemptible": True if self.environment == "development" else False,
                            "machine_type": "n1-standard-4",
                            "disk_size_gb": 100,
                            "disk_type": "pd-ssd",
                            "image_type": "COS_CONTAINERD",
                            "service_account": "${google_service_account.gke_service_account.email}",
                            "oauth_scopes": [
                                "https://www.googleapis.com/auth/cloud-platform"
                            ],
                            "labels": {**self.default_labels, "node-type": "gpu"},
                            "tags": ["gke-gpu-node", f"gke-{self.environment}"],
                            "taint": [
                                {
                                    "key": "nvidia.com/gpu",
                                    "value": "true",
                                    "effect": "NO_SCHEDULE"
                                }
                            ],
                            "guest_accelerator": [
                                {
                                    "type": "nvidia-tesla-t4",
                                    "count": 1,
                                    "gpu_partition_size": "",
                                    "gpu_sharing_config": []
                                }
                            ],
                            "workload_metadata_config": {
                                "mode": "GKE_METADATA"
                            }
                        }
                    }
                }
            }
        }
    
    def get_cloud_sql_configuration(self) -> Dict[str, Any]:
        """Generate Cloud SQL PostgreSQL configuration"""
        return {
            "resource": {
                "google_sql_database_instance": {
                    "postgresql_instance": {
                        "name": f"ia-influencer-postgres-{self.environment}",
                        "project": self.project_id,
                        "region": self.region,
                        "database_version": "POSTGRES_15",
                        "deletion_protection": False if self.environment == "development" else True,
                        "settings": {
                            "tier": "db-f1-micro" if self.environment == "development" else "db-custom-4-16384",
                            "availability_type": "ZONAL" if self.environment == "development" else "REGIONAL",
                            "disk_type": "PD_SSD",
                            "disk_size": 20 if self.environment == "development" else 100,
                            "disk_autoresize": True,
                            "disk_autoresize_limit": 100 if self.environment == "development" else 1000,
                            "backup_configuration": {
                                "enabled": True,
                                "start_time": "03:00",
                                "location": self.region,
                                "backup_retention_settings": {
                                    "retained_backups": 7,
                                    "retention_unit": "COUNT"
                                }
                            },
                            "maintenance_window": {
                                "day": 7,
                                "hour": 4,
                                "update_track": "stable"
                            },
                            "database_flags": [
                                {
                                    "name": "log_checkpoints",
                                    "value": "on"
                                },
                                {
                                    "name": "log_connections",
                                    "value": "on"
                                },
                                {
                                    "name": "log_disconnections",
                                    "value": "on"
                                },
                                {
                                    "name": "log_lock_waits",
                                    "value": "on"
                                },
                                {
                                    "name": "log_min_duration_statement",
                                    "value": "1000"
                                }
                            ],
                            "ip_configuration": {
                                "ipv4_enabled": True,
                                "private_network": "${google_compute_network.vpc_network.id}",
                                "require_ssl": True,
                                "authorized_networks": []
                            },
                            "insights_config": {
                                "query_insights_enabled": True,
                                "record_application_tags": True,
                                "record_client_address": True
                            },
                            "user_labels": self.default_labels
                        }
                    }
                },
                "google_sql_database": {
                    "ia_influencer_db": {
                        "name": "ia_influencer",
                        "project": self.project_id,
                        "instance": "${google_sql_database_instance.postgresql_instance.name}",
                        "charset": "UTF8",
                        "collation": "en_US.UTF8"
                    }
                },
                "google_sql_user": {
                    "ia_admin": {
                        "name": "ia_admin",
                        "project": self.project_id,
                        "instance": "${google_sql_database_instance.postgresql_instance.name}",
                        "password": "${random_password.postgres_password.result}"
                    }
                },
                "random_password": {
                    "postgres_password": {
                        "length": 32,
                        "special": True
                    }
                }
            }
        }
    
    def get_memorystore_redis_configuration(self) -> Dict[str, Any]:
        """Generate Memorystore Redis configuration"""
        return {
            "resource": {
                "google_redis_instance": {
                    "redis_cache": {
                        "name": f"ia-influencer-redis-{self.environment}",
                        "project": self.project_id,
                        "region": self.region,
                        "memory_size_gb": 1 if self.environment == "development" else 5,
                        "tier": "BASIC" if self.environment == "development" else "STANDARD_HA",
                        "redis_version": "REDIS_7_0",
                        "display_name": f"IA-Influencer Redis - {self.environment}",
                        "reserved_ip_range": "10.0.3.0/29",
                        "authorized_network": "${google_compute_network.vpc_network.id}",
                        "connect_mode": "PRIVATE_SERVICE_ACCESS",
                        "auth_enabled": True,
                        "transit_encryption_mode": "SERVER_AUTHENTICATION",
                        "redis_configs": {
                            "maxmemory-policy": "allkeys-lru",
                            "notify-keyspace-events": "Ex"
                        },
                        "labels": self.default_labels
                    }
                }
            }
        }
    
    def get_cloud_storage_configuration(self) -> Dict[str, Any]:
        """Generate Cloud Storage buckets configuration"""
        return {
            "resource": {
                "google_storage_bucket": {
                    "content_storage": {
                        "name": f"ia-influencer-content-{self.environment}-{self.project_id}",
                        "project": self.project_id,
                        "location": self.region,
                        "storage_class": "STANDARD",
                        "force_destroy": True if self.environment == "development" else False,
                        "uniform_bucket_level_access": True,
                        "versioning": {
                            "enabled": True
                        },
                        "lifecycle_rule": [
                            {
                                "condition": {
                                    "age": 30
                                },
                                "action": {
                                    "type": "SetStorageClass",
                                    "storage_class": "NEARLINE"
                                }
                            },
                            {
                                "condition": {
                                    "age": 90
                                },
                                "action": {
                                    "type": "SetStorageClass",
                                    "storage_class": "COLDLINE"
                                }
                            }
                        ],
                        "cors": [
                            {
                                "origin": ["*"],
                                "method": ["GET", "HEAD", "PUT", "POST", "DELETE"],
                                "response_header": ["*"],
                                "max_age_seconds": 3600
                            }
                        ],
                        "labels": {**self.default_labels, "purpose": "content-storage"}
                    },
                    "ai_models_storage": {
                        "name": f"ia-influencer-models-{self.environment}-{self.project_id}",
                        "project": self.project_id,
                        "location": self.region,
                        "storage_class": "STANDARD",
                        "force_destroy": True if self.environment == "development" else False,
                        "uniform_bucket_level_access": True,
                        "versioning": {
                            "enabled": True
                        },
                        "labels": {**self.default_labels, "purpose": "ai-models"}
                    },
                    "backup_storage": {
                        "name": f"ia-influencer-backup-{self.environment}-{self.project_id}",
                        "project": self.project_id,
                        "location": self.region,
                        "storage_class": "COLDLINE",
                        "force_destroy": True if self.environment == "development" else False,
                        "uniform_bucket_level_access": True,
                        "versioning": {
                            "enabled": True
                        },
                        "lifecycle_rule": [
                            {
                                "condition": {
                                    "age": 7
                                },
                                "action": {
                                    "type": "SetStorageClass",
                                    "storage_class": "ARCHIVE"
                                }
                            }
                        ],
                        "labels": {**self.default_labels, "purpose": "backup"}
                    }
                }
            }
        }
    
    def get_cloud_functions_configuration(self) -> Dict[str, Any]:
        """Generate Cloud Functions configuration"""
        return {
            "resource": {
                "google_storage_bucket": {
                    "functions_source_bucket": {
                        "name": f"ia-influencer-functions-source-{self.environment}-{self.project_id}",
                        "project": self.project_id,
                        "location": self.region,
                        "storage_class": "STANDARD",
                        "uniform_bucket_level_access": True
                    }
                },
                "google_storage_bucket_object": {
                    "content_analysis_source": {
                        "name": "content-analysis-source.zip",
                        "bucket": "${google_storage_bucket.functions_source_bucket.name}",
                        "source": "./functions/content-analysis.zip"
                    }
                },
                "google_cloudfunctions2_function": {
                    "content_analysis_function": {
                        "name": f"ia-content-analysis-{self.environment}",
                        "project": self.project_id,
                        "location": self.region,
                        "description": "AI-powered content analysis function",
                        "build_config": {
                            "runtime": "python311",
                            "entry_point": "analyze_content",
                            "source": {
                                "storage_source": {
                                    "bucket": "${google_storage_bucket.functions_source_bucket.name}",
                                    "object": "${google_storage_bucket_object.content_analysis_source.name}"
                                }
                            }
                        },
                        "service_config": {
                            "max_instance_count": 10 if self.environment == "development" else 100,
                            "min_instance_count": 0,
                            "available_memory": "512Mi",
                            "timeout_seconds": 300,
                            "environment_variables": {
                                "ENVIRONMENT": self.environment,
                                "PROJECT_ID": self.project_id,
                                "VISION_API_ENDPOINT": "vision.googleapis.com"
                            },
                            "ingress_settings": "ALLOW_INTERNAL_AND_GCLB",
                            "all_traffic_on_latest_revision": True,
                            "service_account_email": "${google_service_account.functions_sa.email}"
                        },
                        "labels": self.default_labels
                    }
                },
                "google_service_account": {
                    "functions_sa": {
                        "account_id": f"functions-sa-{self.environment}",
                        "display_name": f"Cloud Functions Service Account - {self.environment}",
                        "project": self.project_id
                    }
                }
            }
        }
    
    def get_cloud_run_configuration(self) -> Dict[str, Any]:
        """Generate Cloud Run services configuration"""
        return {
            "resource": {
                "google_cloud_run_v2_service": {
                    "api_service": {
                        "name": f"ia-influencer-api-{self.environment}",
                        "project": self.project_id,
                        "location": self.region,
                        "description": "Main API service for IA-Influencer Agent",
                        "template": {
                            "containers": [
                                {
                                    "image": f"gcr.io/{self.project_id}/ia-influencer-api:{self.environment}",
                                    "ports": {
                                        "container_port": 8000
                                    },
                                    "resources": {
                                        "limits": {
                                            "cpu": "2000m",
                                            "memory": "2Gi"
                                        }
                                    },
                                    "env": [
                                        {
                                            "name": "ENVIRONMENT",
                                            "value": self.environment
                                        },
                                        {
                                            "name": "PROJECT_ID",
                                            "value": self.project_id
                                        }
                                    ]
                                }
                            ],
                            "scaling": {
                                "min_instance_count": 1 if self.environment == "development" else 3,
                                "max_instance_count": 5 if self.environment == "development" else 100
                            },
                            "vpc_access": {
                                "connector": "${google_vpc_access_connector.connector.id}",
                                "egress": "PRIVATE_RANGES_ONLY"
                            }
                        },
                        "traffic": [
                            {
                                "percent": 100,
                                "type": "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
                            }
                        ],
                        "labels": self.default_labels
                    },
                    "ai_processing_service": {
                        "name": f"ia-ai-processing-{self.environment}",
                        "project": self.project_id,
                        "location": self.region,
                        "description": "AI processing service for content analysis",
                        "template": {
                            "containers": [
                                {
                                    "image": f"gcr.io/{self.project_id}/ia-ai-processing:{self.environment}",
                                    "ports": {
                                        "container_port": 8001
                                    },
                                    "resources": {
                                        "limits": {
                                            "cpu": "4000m",
                                            "memory": "8Gi"
                                        }
                                    },
                                    "env": [
                                        {
                                            "name": "ENVIRONMENT",
                                            "value": self.environment
                                        },
                                        {
                                            "name": "GPU_ENABLED",
                                            "value": "false"
                                        }
                                    ]
                                }
                            ],
                            "scaling": {
                                "min_instance_count": 0,
                                "max_instance_count": 10
                            },
                            "execution_environment": "EXECUTION_ENVIRONMENT_GEN2"
                        },
                        "labels": self.default_labels
                    }
                },
                "google_vpc_access_connector": {
                    "connector": {
                        "name": f"ia-connector-{self.environment}",
                        "project": self.project_id,
                        "region": self.region,
                        "ip_cidr_range": "10.0.4.0/28",
                        "network": "${google_compute_network.vpc_network.name}",
                        "machine_type": "e2-micro",
                        "min_instances": 2,
                        "max_instances": 3 if self.environment == "development" else 10
                    }
                }
            }
        }
    
    def get_monitoring_configuration(self) -> Dict[str, Any]:
        """Generate Cloud Monitoring configuration"""
        return {
            "resource": {
                "google_monitoring_alert_policy": {
                    "high_cpu_usage": {
                        "display_name": f"High CPU Usage - {self.environment}",
                        "project": self.project_id,
                        "conditions": [
                            {
                                "display_name": "CPU usage above 80%",
                                "condition_threshold": {
                                    "filter": 'resource.type="k8s_container" AND metric.type="kubernetes.io/container/cpu/core_usage_time"',
                                    "duration": "300s",
                                    "comparison": "COMPARISON_GT",
                                    "threshold_value": 0.8,
                                    "aggregations": [
                                        {
                                            "alignment_period": "300s",
                                            "per_series_aligner": "ALIGN_RATE",
                                            "cross_series_reducer": "REDUCE_MEAN",
                                            "group_by_fields": ["resource.labels.pod_name"]
                                        }
                                    ]
                                }
                            }
                        ],
                        "combiner": "OR",
                        "enabled": True,
                        "notification_channels": ["${google_monitoring_notification_channel.email_channel.name}"]
                    },
                    "high_memory_usage": {
                        "display_name": f"High Memory Usage - {self.environment}",
                        "project": self.project_id,
                        "conditions": [
                            {
                                "display_name": "Memory usage above 90%",
                                "condition_threshold": {
                                    "filter": 'resource.type="k8s_container" AND metric.type="kubernetes.io/container/memory/used_bytes"',
                                    "duration": "300s",
                                    "comparison": "COMPARISON_GT",
                                    "threshold_value": 0.9,
                                    "aggregations": [
                                        {
                                            "alignment_period": "300s",
                                            "per_series_aligner": "ALIGN_MEAN"
                                        }
                                    ]
                                }
                            }
                        ],
                        "combiner": "OR",
                        "enabled": True
                    }
                },
                "google_monitoring_notification_channel": {
                    "email_channel": {
                        "display_name": f"Email Notifications - {self.environment}",
                        "project": self.project_id,
                        "type": "email",
                        "labels": {
                            "email_address": "mlaiel@live.de"
                        }
                    }
                }
            }
        }
    
    def generate_terraform_configuration(self, output_file: str = "gcp-infrastructure.tf") -> None:
        """Generate complete Terraform configuration"""
        terraform_config = {
            "terraform": {
                "required_version": ">= 1.0",
                "required_providers": {
                    "google": {
                        "source": "hashicorp/google",
                        "version": "~> 5.0"
                    },
                    "random": {
                        "source": "hashicorp/random",
                        "version": "~> 3.0"
                    }
                }
            },
            "provider": {
                "google": {
                    "project": self.project_id,
                    "region": self.region
                }
            },
            "locals": {
                "project_id": self.project_id,
                "environment": self.environment,
                "region": self.region,
                "labels": self.default_labels
            }
        }
        
        # Add all resource configurations
        terraform_config.update(self.get_vpc_configuration())
        terraform_config.update(self.get_firewall_configuration())
        terraform_config.update(self.get_gke_configuration())
        terraform_config.update(self.get_cloud_sql_configuration())
        terraform_config.update(self.get_memorystore_redis_configuration())
        terraform_config.update(self.get_cloud_storage_configuration())
        terraform_config.update(self.get_cloud_functions_configuration())
        terraform_config.update(self.get_cloud_run_configuration())
        terraform_config.update(self.get_monitoring_configuration())
        
        # Add outputs
        terraform_config["output"] = {
            "gke_cluster_name": {
                "description": "GKE Cluster Name",
                "value": "${google_container_cluster.gke_cluster.name}"
            },
            "gke_cluster_endpoint": {
                "description": "GKE Cluster Endpoint",
                "value": "${google_container_cluster.gke_cluster.endpoint}",
                "sensitive": True
            },
            "postgresql_connection_name": {
                "description": "PostgreSQL Connection Name",
                "value": "${google_sql_database_instance.postgresql_instance.connection_name}"
            },
            "redis_host": {
                "description": "Redis Host",
                "value": "${google_redis_instance.redis_cache.host}"
            },
            "content_storage_bucket": {
                "description": "Content Storage Bucket",
                "value": "${google_storage_bucket.content_storage.name}"
            }
        }
        
        # Write configuration to file
        with open(output_file, 'w') as f:
            f.write(f"# Terraform configuration for IA-Influencer Agent on GCP\n")
            f.write(f"# Author: Fahed Mlaiel <mlaiel@live.de>\n")
            f.write(f"# Environment: {self.environment}\n\n")
            
            import json
            # Convert to HCL-like format (simplified)
            for section, config in terraform_config.items():
                f.write(f"{section} {{\n")
                f.write(json.dumps(config, indent=2))
                f.write("\n}\n\n")
    
    def get_deployment_script(self) -> str:
        """Generate GCP deployment script"""
        return f'''#!/bin/bash
# GCP deployment script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -e

PROJECT_ID="{self.project_id}"
ENVIRONMENT="{self.environment}"
REGION="{self.region}"
ZONE="{self.zone}"

echo "🚀 Deploying IA-Influencer Agent to Google Cloud..."
echo "Project: $PROJECT_ID"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"

# Check prerequisites
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed"
    exit 1
fi

if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform is not installed"
    exit 1
fi

# Authenticate with GCP
echo "🔐 Authenticating with Google Cloud..."
gcloud auth application-default login

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable \\
    container.googleapis.com \\
    sqladmin.googleapis.com \\
    redis.googleapis.com \\
    storage-component.googleapis.com \\
    cloudfunctions.googleapis.com \\
    run.googleapis.com \\
    monitoring.googleapis.com \\
    logging.googleapis.com \\
    compute.googleapis.com \\
    vision.googleapis.com \\
    speech.googleapis.com

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Plan deployment
echo "📋 Planning Terraform deployment..."
terraform plan -var="project_id=$PROJECT_ID" -var="environment=$ENVIRONMENT"

# Apply deployment
echo "🚀 Applying Terraform deployment..."
terraform apply -var="project_id=$PROJECT_ID" -var="environment=$ENVIRONMENT" -auto-approve

# Get GKE credentials
echo "⚙️ Getting GKE credentials..."
gcloud container clusters get-credentials \\
    ia-influencer-gke-$ENVIRONMENT \\
    --zone=$ZONE \\
    --project=$PROJECT_ID

# Verify GKE connection
echo "🔍 Verifying GKE connection..."
kubectl get nodes

echo "✅ GCP infrastructure deployed successfully!"
echo "🎯 Next steps:"
echo "1. Deploy Kubernetes manifests: kubectl apply -f k8s-manifests/"
echo "2. Configure Cloud DNS: gcloud dns managed-zones create"
echo "3. Setup monitoring: Configure Cloud Monitoring"
echo "4. Configure CI/CD: Setup Cloud Build triggers"

# Display important endpoints
echo "📊 Important endpoints:"
terraform output
'''
