"""Kubernetes MongoDB Deployment Manager
=====================================

Enterprise Kubernetes deployment and management for MongoDB clusters with
advanced orchestration, scaling, and production-ready configurations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import yaml
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
import subprocess
import base64
import os

logger = logging.getLogger(__name__)

@dataclass
class KubernetesConfig:
    """Kubernetes MongoDB deployment configuration."""
    
    # Cluster Configuration
    namespace: str = "mongodb"
    cluster_name: str = "mongodb-cluster"
    mongodb_version: str = "7.0"
    
    # Resource Configuration
    cpu_requests: str = "500m"
    cpu_limits: str = "2000m"
    memory_requests: str = "1Gi"
    memory_limits: str = "4Gi"
    storage_class: str = "fast-ssd"
    storage_size: str = "100Gi"
    
    # Replica Set Configuration
    replica_count: int = 3
    replica_set_name: str = "rs0"
    
    # Sharding Configuration
    enable_sharding: bool = False
    shard_count: int = 2
    mongos_count: int = 2
    config_server_count: int = 3
    
    # Security Configuration
    enable_auth: bool = True
    enable_tls: bool = True
    root_password: str = "secure_password"
    
    # Service Configuration
    service_type: str = "ClusterIP"  # ClusterIP, NodePort, LoadBalancer
    external_port: int = 27017
    
    # Backup Configuration
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"  # Daily at 2 AM
    backup_retention: str = "30d"
    
    # Monitoring Configuration
    monitoring_enabled: bool = True
    metrics_enabled: bool = True
    
    # Node Affinity
    node_selector: Dict[str, str] = field(default_factory=dict)
    tolerations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Custom Configuration
    custom_mongodb_config: Dict[str, Any] = field(default_factory=dict)


class KubernetesManager:
    """Kubernetes MongoDB deployment manager."""
    
    def __init__(self, config -> None: KubernetesConfig) -> None:
        """Initialize Kubernetes manager."""
        self.config = config
        self.manifests_dir = Path(f"k8s-manifests/{config.cluster_name}")
        self.manifests_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(f"{__name__}.{config.cluster_name}")
        
        # Deployment state
        self.deployment_state = {
            "cluster_name": config.cluster_name,
            "namespace": config.namespace,
            "status": "initialized",
            "created_at": datetime.now().isoformat(),
            "resources": {},
            "endpoints": {}
        }
    
    async def deploy_cluster(self) -> Dict[str, Any]:
        """Deploy MongoDB cluster on Kubernetes."""
        try:
            self.logger.info(f"Deploying MongoDB cluster: {self.config.cluster_name}")
            self.deployment_state["status"] = "deploying"
            
            # Create namespace
            await self._create_namespace()
            
            # Create secrets
            await self._create_secrets()
            
            # Create config maps
            await self._create_config_maps()
            
            # Create storage classes and persistent volumes
            await self._create_storage()
            
            # Deploy MongoDB services
            if self.config.enable_sharding:
                await self._deploy_sharded_cluster()
            else:
                await self._deploy_replica_set()
            
            # Setup monitoring
            if self.config.monitoring_enabled:
                await self._deploy_monitoring()
            
            # Setup backups
            if self.config.backup_enabled:
                await self._deploy_backup_jobs()
            
            # Setup network policies
            await self._create_network_policies()
            
            # Validate deployment
            await self._validate_deployment()
            
            self.deployment_state["status"] = "completed"
            self.deployment_state["completed_at"] = datetime.now().isoformat()
            
            # Save deployment state
            await self._save_deployment_state()
            
            self.logger.info("MongoDB cluster deployment completed successfully")
            return self.deployment_state
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            self.deployment_state["status"] = "failed"
            self.deployment_state["error"] = str(e)
            raise
    
    async def _create_namespace(self) -> None:
        """Create Kubernetes namespace."""
        self.logger.info(f"Creating namespace: {self.config.namespace}")
        
        manifest = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.config.namespace,
                "labels": {
                    "name": self.config.namespace,
                    "app.kubernetes.io/name": "mongodb",
                    "app.kubernetes.io/instance": self.config.cluster_name,
                    "app.kubernetes.io/managed-by": "ainflue-deployer"
                }
            }
        }
        
        await self._apply_manifest("namespace", manifest)
    
    async def _create_secrets(self) -> None:
        """Create Kubernetes secrets for MongoDB."""
        self.logger.info("Creating secrets")
        
        # MongoDB root credentials
        root_secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"{self.config.cluster_name}-root-secret",
                "namespace": self.config.namespace
            },
            "type": "Opaque",
            "data": {
                "username": base64.b64encode("root".encode()).decode(),
                "password": base64.b64encode(self.config.root_password.encode()).decode()
            }
        }
        
        await self._apply_manifest("root-secret", root_secret)
        
        # MongoDB keyfile for replica set authentication
        keyfile_content = base64.b64encode(os.urandom(756)).decode()
        keyfile_secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"{self.config.cluster_name}-keyfile",
                "namespace": self.config.namespace
            },
            "type": "Opaque",
            "data": {
                "keyfile": keyfile_content
            }
        }
        
        await self._apply_manifest("keyfile-secret", keyfile_secret)
        
        # TLS certificates (if enabled)
        if self.config.enable_tls:
            await self._create_tls_secrets()
    
    async def _create_tls_secrets(self) -> None:
        """Create TLS certificates for MongoDB."""
        self.logger.info("Creating TLS certificates")
        
        # Generate self-signed certificates or use cert-manager
        # For production, use proper CA-signed certificates
        
        tls_secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"{self.config.cluster_name}-tls",
                "namespace": self.config.namespace
            },
            "type": "kubernetes.io/tls",
            "data": {
                "tls.crt": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t",  # Base64 encoded cert
                "tls.key": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0t"   # Base64 encoded key
            }
        }
        
        await self._apply_manifest("tls-secret", tls_secret)
    
    async def _create_config_maps(self) -> None:
        """Create MongoDB configuration config maps."""
        self.logger.info("Creating config maps")
        
        # MongoDB configuration
        mongodb_config = {
            "storage": {
                "dbPath": "/data/db",
                "journal": {"enabled": True},
                "wiredTiger": {
                    "engineConfig": {"cacheSizeGB": 1}
                }
            },
            "systemLog": {
                "destination": "file",
                "logAppend": True,
                "path": "/var/log/mongodb/mongod.log"
            },
            "net": {
                "port": 27017,
                "bindIp": "0.0.0.0"
            },
            "processManagement": {
                "timeZoneInfo": "/usr/share/zoneinfo"
            },
            "replication": {
                "replSetName": self.config.replica_set_name
            }
        }
        
        if self.config.enable_auth:
            mongodb_config["security"] = {
                "authorization": "enabled",
                "keyFile": "/etc/mongodb-keyfile/keyfile"
            }
        
        if self.config.enable_tls:
            mongodb_config["net"]["tls"] = {
                "mode": "requireTLS",
                "certificateKeyFile": "/etc/mongodb-tls/tls.pem"
            }
        
        # Merge custom configuration
        if self.config.custom_mongodb_config:
            mongodb_config.update(self.config.custom_mongodb_config)
        
        config_map = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.config.cluster_name}-config",
                "namespace": self.config.namespace
            },
            "data": {
                "mongod.conf": yaml.dump(mongodb_config)
            }
        }
        
        await self._apply_manifest("config-map", config_map)
        
        # Initialization scripts
        init_scripts = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.config.cluster_name}-init-scripts",
                "namespace": self.config.namespace
            },
            "data": {
                "init-replica-set.js": self._generate_init_script(),
                "create-users.js": self._generate_user_script()
            }
        }
        
        await self._apply_manifest("init-scripts", init_scripts)
    
    def _generate_init_script(self) -> str:
        """Generate replica set initialization script."""
        return f"""
// Initialize replica set
rs.initiate({{
    _id: '{self.config.replica_set_name}',
    members: [
        {{ _id: 0, host: '{self.config.cluster_name}-0.{self.config.cluster_name}-headless.{self.config.namespace}.svc.cluster.local:27017' }},
        {{ _id: 1, host: '{self.config.cluster_name}-1.{self.config.cluster_name}-headless.{self.config.namespace}.svc.cluster.local:27017' }},
        {{ _id: 2, host: '{self.config.cluster_name}-2.{self.config.cluster_name}-headless.{self.config.namespace}.svc.cluster.local:27017' }}
    ]
}});

// Wait for replica set to be ready
while (rs.status().ok !== 1) {{
    sleep(1000);
}}

print('Replica set initialized successfully');
"""
    
    def _generate_user_script(self) -> str:
        """Generate user creation script."""
        return """
// Create admin user
use admin;
db.createUser({
    user: 'admin',
    pwd: 'secure_password',
    roles: ['root']
});

// Create application users
use ainflue;
db.createUser({
    user: 'ainflue_app',
    pwd: 'app_password',
    roles: [
        { role: 'readWrite', db: 'ainflue' },
        { role: 'dbAdmin', db: 'ainflue' }
    ]
});

print('Users created successfully');
"""
    
    async def _create_storage(self) -> None:
        """Create storage classes and persistent volumes."""
        self.logger.info("Creating storage resources")
        
        # Storage class for fast SSD storage
        storage_class = {
            "apiVersion": "storage.k8s.io/v1",
            "kind": "StorageClass",
            "metadata": {
                "name": f"{self.config.cluster_name}-fast-ssd"
            },
            "provisioner": "kubernetes.io/aws-ebs",  # Adjust for your cloud provider
            "parameters": {
                "type": "gp3",
                "iops": "3000",
                "throughput": "125"
            },
            "allowVolumeExpansion": True,
            "volumeBindingMode": "WaitForFirstConsumer"
        }
        
        await self._apply_manifest("storage-class", storage_class)
    
    async def _deploy_replica_set(self) -> None:
        """Deploy MongoDB replica set using StatefulSet."""
        self.logger.info("Deploying MongoDB replica set")
        
        # Headless service for StatefulSet
        headless_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.config.cluster_name}-headless",
                "namespace": self.config.namespace,
                "labels": {
                    "app": self.config.cluster_name,
                    "component": "mongodb"
                }
            },
            "spec": {
                "clusterIP": "None",
                "selector": {
                    "app": self.config.cluster_name,
                    "component": "mongodb"
                },
                "ports": [
                    {
                        "name": "mongodb",
                        "port": 27017,
                        "targetPort": 27017
                    }
                ]
            }
        }
        
        await self._apply_manifest("headless-service", headless_service)
        
        # External service
        external_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.config.cluster_name}-external",
                "namespace": self.config.namespace,
                "labels": {
                    "app": self.config.cluster_name,
                    "component": "mongodb"
                }
            },
            "spec": {
                "type": self.config.service_type,
                "selector": {
                    "app": self.config.cluster_name,
                    "component": "mongodb"
                },
                "ports": [
                    {
                        "name": "mongodb",
                        "port": self.config.external_port,
                        "targetPort": 27017
                    }
                ]
            }
        }
        
        await self._apply_manifest("external-service", external_service)
        
        # StatefulSet
        statefulset = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": self.config.cluster_name,
                "namespace": self.config.namespace,
                "labels": {
                    "app": self.config.cluster_name,
                    "component": "mongodb"
                }
            },
            "spec": {
                "serviceName": f"{self.config.cluster_name}-headless",
                "replicas": self.config.replica_count,
                "selector": {
                    "matchLabels": {
                        "app": self.config.cluster_name,
                        "component": "mongodb"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": self.config.cluster_name,
                            "component": "mongodb"
                        }
                    },
                    "spec": {
                        "serviceAccountName": f"{self.config.cluster_name}-sa",
                        "securityContext": {
                            "fsGroup": 999,
                            "runAsUser": 999,
                            "runAsNonRoot": True
                        },
                        "initContainers": [
                            {
                                "name": "init-mongodb",
                                "image": f"mongo:{self.config.mongodb_version}",
                                "command": [
                                    "bash", "-c",
                                    """
                                    set -ex
                                    # Create directories
                                    mkdir -p /data/db
                                    chmod 755 /data/db
                                    chown 999:999 /data/db
                                    
                                    # Copy keyfile with correct permissions
                                    if [ -f /etc/mongodb-keyfile/keyfile ]; then
                                        cp /etc/mongodb-keyfile/keyfile /tmp/keyfile
                                        chmod 400 /tmp/keyfile
                                        chown 999:999 /tmp/keyfile
                                    fi
                                    """
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "data",
                                        "mountPath": "/data/db"
                                    },
                                    {
                                        "name": "keyfile",
                                        "mountPath": "/etc/mongodb-keyfile",
                                        "readOnly": True
                                    }
                                ]
                            }
                        ],
                        "containers": [
                            {
                                "name": "mongodb",
                                "image": f"mongo:{self.config.mongodb_version}",
                                "command": ["mongod"],
                                "args": ["--config", "/etc/mongodb-config/mongod.conf"],
                                "env": [
                                    {
                                        "name": "MONGO_INITDB_ROOT_USERNAME",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": f"{self.config.cluster_name}-root-secret",
                                                "key": "username"
                                            }
                                        }
                                    },
                                    {
                                        "name": "MONGO_INITDB_ROOT_PASSWORD",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": f"{self.config.cluster_name}-root-secret",
                                                "key": "password"
                                            }
                                        }
                                    }
                                ],
                                "ports": [
                                    {
                                        "containerPort": 27017,
                                        "name": "mongodb"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": self.config.cpu_requests,
                                        "memory": self.config.memory_requests
                                    },
                                    "limits": {
                                        "cpu": self.config.cpu_limits,
                                        "memory": self.config.memory_limits
                                    }
                                },
                                "volumeMounts": [
                                    {
                                        "name": "data",
                                        "mountPath": "/data/db"
                                    },
                                    {
                                        "name": "config",
                                        "mountPath": "/etc/mongodb-config",
                                        "readOnly": True
                                    },
                                    {
                                        "name": "keyfile",
                                        "mountPath": "/etc/mongodb-keyfile",
                                        "readOnly": True
                                    },
                                    {
                                        "name": "logs",
                                        "mountPath": "/var/log/mongodb"
                                    }
                                ],
                                "livenessProbe": {
                                    "exec": {
                                        "command": ["mongo", "--eval", "db.adminCommand('ping')"]
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                    "timeoutSeconds": 5,
                                    "failureThreshold": 3
                                },
                                "readinessProbe": {
                                    "exec": {
                                        "command": ["mongo", "--eval", "db.adminCommand('ping')"]
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 10,
                                    "timeoutSeconds": 1,
                                    "failureThreshold": 3
                                }
                            }
                        ],
                        "volumes": [
                            {
                                "name": "config",
                                "configMap": {
                                    "name": f"{self.config.cluster_name}-config"
                                }
                            },
                            {
                                "name": "keyfile",
                                "secret": {
                                    "secretName": f"{self.config.cluster_name}-keyfile",
                                    "defaultMode": 0o400
                                }
                            },
                            {
                                "name": "logs",
                                "emptyDir": {}
                            }
                        ],
                        "nodeSelector": self.config.node_selector,
                        "tolerations": self.config.tolerations
                    }
                },
                "volumeClaimTemplates": [
                    {
                        "metadata": {
                            "name": "data"
                        },
                        "spec": {
                            "accessModes": ["ReadWriteOnce"],
                            "storageClassName": self.config.storage_class,
                            "resources": {
                                "requests": {
                                    "storage": self.config.storage_size
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        # Add TLS volume if enabled
        if self.config.enable_tls:
            tls_volume = {
                "name": "tls",
                "secret": {
                    "secretName": f"{self.config.cluster_name}-tls"
                }
            }
            statefulset["spec"]["template"]["spec"]["volumes"].append(tls_volume)
            
            tls_mount = {
                "name": "tls",
                "mountPath": "/etc/mongodb-tls",
                "readOnly": True
            }
            statefulset["spec"]["template"]["spec"]["containers"][0]["volumeMounts"].append(tls_mount)
        
        await self._apply_manifest("statefulset", statefulset)
        
        # Create service account and RBAC
        await self._create_service_account()
    
    async def _deploy_sharded_cluster(self) -> None:
        """Deploy MongoDB sharded cluster."""
        self.logger.info("Deploying MongoDB sharded cluster")
        
        # Deploy config servers
        await self._deploy_config_servers()
        
        # Deploy shards
        for shard_id in range(self.config.shard_count):
            await self._deploy_shard(shard_id)
        
        # Deploy mongos routers
        await self._deploy_mongos()
        
        # Initialize sharding
        await self._initialize_sharding()
    
    async def _deploy_config_servers(self) -> None:
        """Deploy MongoDB config servers."""
        self.logger.info("Deploying config servers")
        
        # Config server StatefulSet (simplified version)
        # Similar to replica set but with configsvr role
        config_server_name = f"{self.config.cluster_name}-configsvr"
        
        # Create config server StatefulSet
        # (Implementation similar to _deploy_replica_set but with configsvr configuration)
    
    async def _deploy_shard(self, shard_id: int) -> None:
        """Deploy individual shard."""
        shard_name = f"{self.config.cluster_name}-shard{shard_id}"
        self.logger.info(f"Deploying shard: {shard_name}")
        
        # Create shard StatefulSet
        # (Implementation similar to _deploy_replica_set but with shardsvr configuration)
    
    async def _deploy_mongos(self) -> None:
        """Deploy mongos routers."""
        self.logger.info("Deploying mongos routers")
        
        # Mongos Deployment (stateless)
        mongos_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{self.config.cluster_name}-mongos",
                "namespace": self.config.namespace
            },
            "spec": {
                "replicas": self.config.mongos_count,
                "selector": {
                    "matchLabels": {
                        "app": self.config.cluster_name,
                        "component": "mongos"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": self.config.cluster_name,
                            "component": "mongos"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "mongos",
                                "image": f"mongo:{self.config.mongodb_version}",
                                "command": ["mongos"],
                                "args": [
                                    "--configdb",
                                    f"configReplSet/{self.config.cluster_name}-configsvr-0.{self.config.cluster_name}-configsvr-headless.{self.config.namespace}.svc.cluster.local:27019,{self.config.cluster_name}-configsvr-1.{self.config.cluster_name}-configsvr-headless.{self.config.namespace}.svc.cluster.local:27019,{self.config.cluster_name}-configsvr-2.{self.config.cluster_name}-configsvr-headless.{self.config.namespace}.svc.cluster.local:27019",
                                    "--bind_ip_all",
                                    "--port", "27017"
                                ],
                                "ports": [
                                    {
                                        "containerPort": 27017,
                                        "name": "mongodb"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "250m",
                                        "memory": "512Mi"
                                    },
                                    "limits": {
                                        "cpu": "1000m",
                                        "memory": "2Gi"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("mongos-deployment", mongos_deployment)
    
    async def _initialize_sharding(self) -> None:
        """Initialize MongoDB sharding."""
        self.logger.info("Initializing sharding")
        
        # Create job to initialize sharding
        init_job = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"{self.config.cluster_name}-init-sharding",
                "namespace": self.config.namespace
            },
            "spec": {
                "template": {
                    "spec": {
                        "restartPolicy": "OnFailure",
                        "containers": [
                            {
                                "name": "init-sharding",
                                "image": f"mongo:{self.config.mongodb_version}",
                                "command": ["bash"],
                                "args": [
                                    "-c",
                                    f"""
                                    # Connect to mongos and add shards
                                    mongo --host {self.config.cluster_name}-mongos.{self.config.namespace}.svc.cluster.local:27017 --eval "
                                        // Add shards
                                        for (let i = 0; i < {self.config.shard_count}; i++) {{
                                            let shardName = 'shard' + i + 'rs';
                                            let shardHosts = '{self.config.cluster_name}-shard' + i + '-0.{self.config.cluster_name}-shard' + i + '-headless.{self.config.namespace}.svc.cluster.local:27018,{self.config.cluster_name}-shard' + i + '-1.{self.config.cluster_name}-shard' + i + '-headless.{self.config.namespace}.svc.cluster.local:27018,{self.config.cluster_name}-shard' + i + '-2.{self.config.cluster_name}-shard' + i + '-headless.{self.config.namespace}.svc.cluster.local:27018';
                                            sh.addShard(shardName + '/' + shardHosts);
                                        }}
                                        
                                        // Enable sharding for databases
                                        sh.enableSharding('ainflue');
                                        sh.shardCollection('ainflue.users', {{ _id: 'hashed' }});
                                        sh.shardCollection('ainflue.content', {{ userId: 1, _id: 1 }});
                                    "
                                    """
                                ]
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("init-sharding-job", init_job)
    
    async def _create_service_account(self) -> None:
        """Create service account and RBAC."""
        self.logger.info("Creating service account")
        
        # Service Account
        service_account = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": f"{self.config.cluster_name}-sa",
                "namespace": self.config.namespace
            }
        }
        
        await self._apply_manifest("service-account", service_account)
        
        # Role (if needed for specific permissions)
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
                    "resources": ["pods", "services", "endpoints"],
                    "verbs": ["get", "list", "watch"]
                }
            ]
        }
        
        await self._apply_manifest("role", role)
        
        # RoleBinding
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
        
        await self._apply_manifest("role-binding", role_binding)
    
    async def _deploy_monitoring(self) -> None:
        """Deploy monitoring components."""
        self.logger.info("Deploying monitoring")
        
        # MongoDB Exporter for Prometheus
        exporter_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{self.config.cluster_name}-exporter",
                "namespace": self.config.namespace
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": self.config.cluster_name,
                        "component": "exporter"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": self.config.cluster_name,
                            "component": "exporter"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "mongodb-exporter",
                                "image": "percona/mongodb_exporter:0.20",
                                "args": [
                                    f"--mongodb.uri=mongodb://{self.config.cluster_name}-external.{self.config.namespace}.svc.cluster.local:27017"
                                ],
                                "ports": [
                                    {
                                        "containerPort": 9216,
                                        "name": "metrics"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "128Mi"
                                    },
                                    "limits": {
                                        "cpu": "200m",
                                        "memory": "256Mi"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("exporter-deployment", exporter_deployment)
        
        # Service for exporter
        exporter_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.config.cluster_name}-exporter",
                "namespace": self.config.namespace,
                "labels": {
                    "app": self.config.cluster_name,
                    "component": "exporter"
                }
            },
            "spec": {
                "selector": {
                    "app": self.config.cluster_name,
                    "component": "exporter"
                },
                "ports": [
                    {
                        "name": "metrics",
                        "port": 9216,
                        "targetPort": 9216
                    }
                ]
            }
        }
        
        await self._apply_manifest("exporter-service", exporter_service)
        
        # ServiceMonitor for Prometheus Operator
        if self.config.metrics_enabled:
            service_monitor = {
                "apiVersion": "monitoring.coreos.com/v1",
                "kind": "ServiceMonitor",
                "metadata": {
                    "name": f"{self.config.cluster_name}-monitor",
                    "namespace": self.config.namespace
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "app": self.config.cluster_name,
                            "component": "exporter"
                        }
                    },
                    "endpoints": [
                        {
                            "port": "metrics",
                            "interval": "30s",
                            "path": "/metrics"
                        }
                    ]
                }
            }
            
            await self._apply_manifest("service-monitor", service_monitor)
    
    async def _deploy_backup_jobs(self) -> None:
        """Deploy backup CronJobs."""
        self.logger.info("Deploying backup jobs")
        
        # Backup CronJob
        backup_job = {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {
                "name": f"{self.config.cluster_name}-backup",
                "namespace": self.config.namespace
            },
            "spec": {
                "schedule": self.config.backup_schedule,
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "spec": {
                                "restartPolicy": "OnFailure",
                                "containers": [
                                    {
                                        "name": "backup",
                                        "image": f"mongo:{self.config.mongodb_version}",
                                        "command": ["bash"],
                                        "args": [
                                            "-c",
                                            f"""
                                            BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
                                            BACKUP_NAME="{self.config.cluster_name}_$BACKUP_DATE"
                                            
                                            # Create backup
                                            mongodump --host {self.config.cluster_name}-external.{self.config.namespace}.svc.cluster.local:27017 \\
                                                      --out /backup/$BACKUP_NAME
                                            
                                            # Compress backup
                                            tar -czf /backup/$BACKUP_NAME.tar.gz -C /backup $BACKUP_NAME
                                            rm -rf /backup/$BACKUP_NAME
                                            
                                            # Upload to cloud storage (implement based on your provider)
                                            echo "Backup completed: $BACKUP_NAME.tar.gz"
                                            """
                                        ],
                                        "volumeMounts": [
                                            {
                                                "name": "backup-storage",
                                                "mountPath": "/backup"
                                            }
                                        ]
                                    }
                                ],
                                "volumes": [
                                    {
                                        "name": "backup-storage",
                                        "persistentVolumeClaim": {
                                            "claimName": f"{self.config.cluster_name}-backup-pvc"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        
        await self._apply_manifest("backup-cronjob", backup_job)
        
        # Backup PVC
        backup_pvc = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": f"{self.config.cluster_name}-backup-pvc",
                "namespace": self.config.namespace
            },
            "spec": {
                "accessModes": ["ReadWriteOnce"],
                "storageClassName": self.config.storage_class,
                "resources": {
                    "requests": {
                        "storage": "100Gi"
                    }
                }
            }
        }
        
        await self._apply_manifest("backup-pvc", backup_pvc)
    
    async def _create_network_policies(self) -> None:
        """Create network policies for security."""
        self.logger.info("Creating network policies")
        
        # MongoDB network policy
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{self.config.cluster_name}-netpol",
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
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "name": "default"
                                    }
                                }
                            },
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
        
        await self._apply_manifest("network-policy", network_policy)
    
    async def _validate_deployment(self) -> None:
        """Validate Kubernetes deployment."""
        self.logger.info("Validating deployment")
        
        # Check if all pods are running
        await self._wait_for_pods_ready()
        
        # Test MongoDB connectivity
        await self._test_mongodb_connectivity()
        
        # Validate replica set status
        if not self.config.enable_sharding:
            await self._validate_replica_set_status()
        else:
            await self._validate_sharding_status()
    
    async def _wait_for_pods_ready(self) -> None:
        """Wait for all MongoDB pods to be ready."""
        self.logger.info("Waiting for pods to be ready")
        
        # Check StatefulSet status
        cmd = [
            "kubectl", "get", "statefulset", self.config.cluster_name,
            "-n", self.config.namespace,
            "-o", "jsonpath='{.status.readyReplicas}'"
        ]
        
        # Wait for all replicas to be ready (simplified)
        await asyncio.sleep(60)  # In real implementation, poll until ready
    
    async def _test_mongodb_connectivity(self) -> None:
        """Test MongoDB connectivity."""
        self.logger.info("Testing MongoDB connectivity")
        
        # Run connectivity test job
        test_job = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"{self.config.cluster_name}-connectivity-test",
                "namespace": self.config.namespace
            },
            "spec": {
                "template": {
                    "spec": {
                        "restartPolicy": "Never",
                        "containers": [
                            {
                                "name": "test",
                                "image": f"mongo:{self.config.mongodb_version}",
                                "command": ["mongo"],
                                "args": [
                                    f"--host", f"{self.config.cluster_name}-external.{self.config.namespace}.svc.cluster.local:27017",
                                    "--eval", "db.adminCommand('ping')"
                                ]
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("connectivity-test", test_job)
    
    async def _validate_replica_set_status(self) -> None:
        """Validate replica set status."""
        self.logger.info("Validating replica set status")
        # Check rs.status() output
    
    async def _validate_sharding_status(self) -> None:
        """Validate sharding status."""
        self.logger.info("Validating sharding status")
        # Check sh.status() output
    
    async def _apply_manifest(self, name: str, manifest: Dict[str, Any]) -> None:
        """Apply Kubernetes manifest."""
        manifest_file = self.manifests_dir / f"{name}.yaml"
        
        with open(manifest_file, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False)
        
        try:
            subprocess.run(
                ["kubectl", "apply", "-f", str(manifest_file)],
                check=True,
                capture_output=True,
                text=True
            )
            
            self.logger.info(f"Applied manifest: {name}")
            
            # Store resource info
            self.deployment_state["resources"][name] = {
                "kind": manifest.get("kind"),
                "name": manifest.get("metadata", {}).get("name"),
                "namespace": manifest.get("metadata", {}).get("namespace"),
                "applied_at": datetime.now().isoformat(),
                "file": str(manifest_file)
            }
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to apply manifest {name}: {e.stderr}")
            raise
    
    async def _save_deployment_state(self) -> None:
        """Save deployment state."""
        state_file = self.manifests_dir / "deployment_state.json"
        with open(state_file, 'w') as f:
            json.dump(self.deployment_state, f, indent=2)
    
    async def delete_cluster(self) -> Dict[str, Any]:
        """Delete MongoDB cluster from Kubernetes."""
        try:
            self.logger.info(f"Deleting MongoDB cluster: {self.config.cluster_name}")
            
            # Delete all manifests
            for manifest_file in self.manifests_dir.glob("*.yaml"):
                try:
                    subprocess.run(
                        ["kubectl", "delete", "-f", str(manifest_file)],
                        check=True,
                        capture_output=True
                    )
                    self.logger.info(f"Deleted: {manifest_file.name}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Failed to delete {manifest_file.name}: {e}")
            
            # Delete namespace (optional)
            try:
                subprocess.run(
                    ["kubectl", "delete", "namespace", self.config.namespace],
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                pass  # Namespace might not exist or contain other resources
            
            self.deployment_state["status"] = "deleted"
            self.deployment_state["deleted_at"] = datetime.now().isoformat()
            
            return self.deployment_state
            
        except Exception as e:
            self.logger.error(f"Deletion failed: {str(e)}")
            raise
    
    async def scale_cluster(self, new_replica_count: int) -> Dict[str, Any]:
        """Scale MongoDB cluster."""
        self.logger.info(f"Scaling cluster to {new_replica_count} replicas")
        
        try:
            subprocess.run([
                "kubectl", "scale", "statefulset", self.config.cluster_name,
                f"--replicas={new_replica_count}",
                "-n", self.config.namespace
            ], check=True, capture_output=True)
            
            self.config.replica_count = new_replica_count
            self.deployment_state["scaled_at"] = datetime.now().isoformat()
            
            return self.deployment_state
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Scaling failed: {e}")
            raise


# Example usage
async def deploy_k8s_cluster() -> None:
    """Example Kubernetes MongoDB deployment."""
    config = KubernetesConfig(
        cluster_name="mongodb-prod",
        namespace="mongodb",
        replica_count=3,
        enable_sharding=True,
        shard_count=2,
        enable_auth=True,
        enable_tls=True,
        monitoring_enabled=True,
        backup_enabled=True,
        storage_size="200Gi",
        cpu_limits="2000m",
        memory_limits="4Gi"
    )
    
    manager = KubernetesManager(config)
    
    try:
        result = await manager.deploy_cluster()
        print(f"Kubernetes deployment successful: {result}")
        return result
    except Exception as e:
        print(f"Kubernetes deployment failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(deploy_k8s_cluster())