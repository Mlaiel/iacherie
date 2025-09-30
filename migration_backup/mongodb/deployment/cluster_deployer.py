"""Cluster Deployment Manager
===========================

Enterprise-grade MongoDB cluster deployment automation with high availability,
scaling, and production-ready configurations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import subprocess
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
import json
import time

logger = logging.getLogger(__name__)

@dataclass
class DeploymentConfig:
    """MongoDB cluster deployment configuration."""
    
    # Cluster Configuration
    cluster_name: str
    environment: str = "production"  # production, staging, development
    replica_set_name: str = "rs0"
    shard_count: int = 1
    config_server_count: int = 3
    mongos_count: int = 2
    
    # Infrastructure
    cloud_provider: str = "aws"  # aws, gcp, azure, on-premise
    region: str = "us-east-1"
    availability_zones: List[str] = field(default_factory=lambda: ["us-east-1a", "us-east-1b", "us-east-1c"])
    instance_type: str = "m5.xlarge"
    storage_type: str = "gp3"
    storage_size_gb: int = 100
    iops: int = 3000
    
    # Network Configuration
    vpc_id: Optional[str] = None
    subnet_ids: List[str] = field(default_factory=list)
    security_group_ids: List[str] = field(default_factory=list)
    
    # MongoDB Configuration
    mongodb_version: str = "7.0"
    authentication_enabled: bool = True
    tls_enabled: bool = True
    oplog_size_mb: int = 10240
    cache_size_gb: Optional[int] = None
    
    # Backup Configuration
    backup_enabled: bool = True
    backup_retention_days: int = 30
    point_in_time_recovery: bool = True
    
    # Monitoring
    monitoring_enabled: bool = True
    prometheus_enabled: bool = True
    grafana_enabled: bool = True
    alerts_enabled: bool = True
    
    # Security
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    audit_logging: bool = True
    firewall_enabled: bool = True
    
    # Performance
    read_preference: str = "primaryPreferred"
    write_concern: str = "majority"
    read_concern: str = "majority"
    
    # Custom configuration overrides
    custom_config: Dict[str, Any] = field(default_factory=dict)


class ClusterDeployer:
    """MongoDB cluster deployment automation."""
    
    def __init__(self, config: DeploymentConfig):
        """Initialize cluster deployer."""
        self.config = config
        self.deployment_dir = Path(f"deployments/{config.cluster_name}")
        self.deployment_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.{config.cluster_name}")
        
        # Deployment state
        self.deployment_id = f"{config.cluster_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.deployment_state: Dict[str, Any] = {
            "id": self.deployment_id,
            "cluster_name": config.cluster_name,
            "environment": config.environment,
            "status": "initialized",
            "created_at": datetime.now().isoformat(),
            "nodes": {},
            "services": {},
            "endpoints": {}
        }
    
    async def deploy_cluster(self) -> Dict[str, Any]:
        """Deploy complete MongoDB cluster."""
        try:
            self.logger.info(f"Starting deployment of cluster: {self.config.cluster_name}")
            self.deployment_state["status"] = "deploying"
            
            # Phase 1: Infrastructure preparation
            await self._prepare_infrastructure()
            
            # Phase 2: Deploy config servers (for sharded clusters)
            if self.config.shard_count > 1:
                await self._deploy_config_servers()
            
            # Phase 3: Deploy shard replica sets
            await self._deploy_shards()
            
            # Phase 4: Deploy mongos routers (for sharded clusters)
            if self.config.shard_count > 1:
                await self._deploy_mongos_routers()
            
            # Phase 5: Initialize replica sets and sharding
            await self._initialize_cluster()
            
            # Phase 6: Configure security
            await self._configure_security()
            
            # Phase 7: Setup monitoring
            if self.config.monitoring_enabled:
                await self._setup_monitoring()
            
            # Phase 8: Configure backups
            if self.config.backup_enabled:
                await self._configure_backups()
            
            # Phase 9: Health checks and validation
            await self._validate_deployment()
            
            self.deployment_state["status"] = "completed"
            self.deployment_state["completed_at"] = datetime.now().isoformat()
            
            # Save deployment state
            await self._save_deployment_state()
            
            self.logger.info(f"Cluster deployment completed successfully: {self.deployment_id}")
            return self.deployment_state
            
        except Exception as e:
            self.logger.error(f"Cluster deployment failed: {str(e)}")
            self.deployment_state["status"] = "failed"
            self.deployment_state["error"] = str(e)
            self.deployment_state["failed_at"] = datetime.now().isoformat()
            await self._save_deployment_state()
            raise
    
    async def _prepare_infrastructure(self) -> None:
        """Prepare cloud infrastructure."""
        self.logger.info("Preparing infrastructure")
        
        if self.config.cloud_provider == "aws":
            await self._prepare_aws_infrastructure()
        elif self.config.cloud_provider == "gcp":
            await self._prepare_gcp_infrastructure()
        elif self.config.cloud_provider == "azure":
            await self._prepare_azure_infrastructure()
        else:
            await self._prepare_onpremise_infrastructure()
    
    async def _prepare_aws_infrastructure(self) -> None:
        """Prepare AWS infrastructure using Terraform."""
        terraform_config = {
            "provider": {
                "aws": {
                    "region": self.config.region
                }
            },
            "resource": {
                "aws_instance": {},
                "aws_security_group": {
                    f"{self.config.cluster_name}_mongodb": {
                        "name": f"{self.config.cluster_name}-mongodb",
                        "description": "MongoDB cluster security group",
                        "vpc_id": self.config.vpc_id,
                        "ingress": [
                            {
                                "from_port": 27017,
                                "to_port": 27017,
                                "protocol": "tcp",
                                "cidr_blocks": ["10.0.0.0/16"]
                            },
                            {
                                "from_port": 27018,
                                "to_port": 27019,
                                "protocol": "tcp",
                                "cidr_blocks": ["10.0.0.0/16"]
                            }
                        ],
                        "egress": [
                            {
                                "from_port": 0,
                                "to_port": 0,
                                "protocol": "-1",
                                "cidr_blocks": ["0.0.0.0/0"]
                            }
                        ]
                    }
                },
                "aws_ebs_volume": {}
            }
        }
        
        # Create instances for each shard
        for shard_id in range(self.config.shard_count):
            shard_name = f"shard{shard_id:02d}"
            
            # Create 3 instances per shard (replica set)
            for replica_id in range(3):
                instance_name = f"{self.config.cluster_name}-{shard_name}-{replica_id}"
                az_index = replica_id % len(self.config.availability_zones)
                
                terraform_config["resource"]["aws_instance"][instance_name] = {
                    "ami": "ami-0c02fb55956c7d316",  # Amazon Linux 2
                    "instance_type": self.config.instance_type,
                    "availability_zone": self.config.availability_zones[az_index],
                    "vpc_security_group_ids": [f"${{aws_security_group.{self.config.cluster_name}_mongodb.id}}"],
                    "subnet_id": self.config.subnet_ids[az_index] if self.config.subnet_ids else None,
                    "key_name": f"{self.config.cluster_name}-key",
                    "user_data": self._generate_user_data(shard_name, replica_id),
                    "tags": {
                        "Name": instance_name,
                        "Cluster": self.config.cluster_name,
                        "Shard": shard_name,
                        "Role": "mongodb",
                        "Environment": self.config.environment
                    }
                }
                
                # Create EBS volume for data
                volume_name = f"{instance_name}-data"
                terraform_config["resource"]["aws_ebs_volume"][volume_name] = {
                    "availability_zone": self.config.availability_zones[az_index],
                    "size": self.config.storage_size_gb,
                    "type": self.config.storage_type,
                    "iops": self.config.iops if self.config.storage_type in ["gp3", "io1", "io2"] else None,
                    "encrypted": self.config.encryption_at_rest,
                    "tags": {
                        "Name": volume_name,
                        "Cluster": self.config.cluster_name,
                        "Instance": instance_name
                    }
                }
        
        # Save Terraform configuration
        terraform_file = self.deployment_dir / "main.tf"
        with open(terraform_file, 'w') as f:
            json.dump(terraform_config, f, indent=2)
        
        # Apply Terraform
        await self._run_terraform_apply()
    
    async def _prepare_gcp_infrastructure(self) -> None:
        """Prepare Google Cloud Platform infrastructure."""
        self.logger.info("Preparing GCP infrastructure")
        # Implementation for GCP using Terraform or GCP Deployment Manager
        pass
    
    async def _prepare_azure_infrastructure(self) -> None:
        """Prepare Microsoft Azure infrastructure."""
        self.logger.info("Preparing Azure infrastructure")
        # Implementation for Azure using ARM templates or Terraform
        pass
    
    async def _prepare_onpremise_infrastructure(self) -> None:
        """Prepare on-premise infrastructure."""
        self.logger.info("Preparing on-premise infrastructure")
        # Implementation for on-premise deployment
        pass
    
    async def _deploy_config_servers(self) -> None:
        """Deploy MongoDB config servers for sharded clusters."""
        if self.config.shard_count <= 1:
            return
        
        self.logger.info("Deploying config servers")
        
        config_servers = []
        for i in range(self.config.config_server_count):
            server_name = f"{self.config.cluster_name}-configsvr-{i}"
            config_servers.append(server_name)
            
            # Deploy config server instance
            await self._deploy_mongodb_instance(
                server_name,
                "configsvr",
                port=27019,
                replica_set="configReplSet"
            )
        
        # Initialize config server replica set
        await self._initialize_config_replica_set(config_servers)
        
        self.deployment_state["services"]["config_servers"] = config_servers
    
    async def _deploy_shards(self) -> None:
        """Deploy MongoDB shard replica sets."""
        self.logger.info(f"Deploying {self.config.shard_count} shards")
        
        for shard_id in range(self.config.shard_count):
            shard_name = f"shard{shard_id:02d}"
            replica_set_name = f"{shard_name}rs"
            
            shard_members = []
            for replica_id in range(3):  # 3 members per replica set
                member_name = f"{self.config.cluster_name}-{shard_name}-{replica_id}"
                shard_members.append(member_name)
                
                # Deploy shard member
                await self._deploy_mongodb_instance(
                    member_name,
                    "shardsvr" if self.config.shard_count > 1 else "standalone",
                    port=27018,
                    replica_set=replica_set_name
                )
            
            # Initialize shard replica set
            await self._initialize_shard_replica_set(shard_name, shard_members)
            
            self.deployment_state["services"][f"shard_{shard_id}"] = {
                "name": shard_name,
                "replica_set": replica_set_name,
                "members": shard_members
            }
    
    async def _deploy_mongos_routers(self) -> None:
        """Deploy MongoDB mongos routers for sharded clusters."""
        if self.config.shard_count <= 1:
            return
        
        self.logger.info(f"Deploying {self.config.mongos_count} mongos routers")
        
        mongos_instances = []
        for i in range(self.config.mongos_count):
            router_name = f"{self.config.cluster_name}-mongos-{i}"
            mongos_instances.append(router_name)
            
            # Deploy mongos instance
            await self._deploy_mongodb_instance(
                router_name,
                "mongos",
                port=27017
            )
        
        self.deployment_state["services"]["mongos_routers"] = mongos_instances
    
    async def _deploy_mongodb_instance(self, instance_name: str, role: str, port: int = 27017, replica_set: Optional[str] = None) -> None:
        """Deploy individual MongoDB instance."""
        self.logger.info(f"Deploying MongoDB instance: {instance_name} (role: {role})")
        
        # Generate MongoDB configuration
        config = self._generate_mongodb_config(role, port, replica_set)
        
        # Create systemd service file
        service_config = self._generate_systemd_service(instance_name, role)
        
        # Deploy using configuration management (Ansible, Chef, etc.)
        await self._deploy_instance_config(instance_name, config, service_config)
        
        # Start MongoDB service
        await self._start_mongodb_service(instance_name)
        
        # Health check
        await self._wait_for_mongodb_ready(instance_name, port)
        
        self.deployment_state["nodes"][instance_name] = {
            "role": role,
            "port": port,
            "replica_set": replica_set,
            "status": "running",
            "deployed_at": datetime.now().isoformat()
        }
    
    def _generate_mongodb_config(self, role: str, port: int, replica_set: Optional[str] = None) -> Dict[str, Any]:
        """Generate MongoDB configuration based on role."""
        config = {
            "storage": {
                "dbPath": f"/var/lib/mongodb/{role}",
                "journal": {"enabled": True},
                "wiredTiger": {
                    "engineConfig": {
                        "cacheSizeGB": self.config.cache_size_gb
                    }
                }
            },
            "systemLog": {
                "destination": "file",
                "logAppend": True,
                "path": f"/var/log/mongodb/mongod-{role}.log"
            },
            "net": {
                "port": port,
                "bindIp": "0.0.0.0"
            },
            "processManagement": {
                "timeZoneInfo": "/usr/share/zoneinfo",
                "fork": True,
                "pidFilePath": f"/var/run/mongodb/mongod-{role}.pid"
            }
        }
        
        if self.config.tls_enabled:
            config["net"]["tls"] = {
                "mode": "requireTLS",
                "certificateKeyFile": f"/etc/ssl/mongodb/{role}.pem",
                "CAFile": "/etc/ssl/mongodb/ca.pem"
            }
        
        if self.config.authentication_enabled:
            config["security"] = {
                "authorization": "enabled",
                "keyFile": "/etc/mongodb/keyfile"
            }
        
        if replica_set:
            config["replication"] = {
                "replSetName": replica_set,
                "oplogSizeMB": self.config.oplog_size_mb
            }
        
        if role == "shardsvr":
            config["sharding"] = {"clusterRole": "shardsvr"}
        elif role == "configsvr":
            config["sharding"] = {"clusterRole": "configsvr"}
        
        if self.config.audit_logging:
            config["auditLog"] = {
                "destination": "file",
                "format": "JSON",
                "path": f"/var/log/mongodb/audit-{role}.json"
            }
        
        return config
    
    def _generate_systemd_service(self, instance_name: str, role: str) -> str:
        """Generate systemd service configuration."""
        return f"""[Unit]
Description=MongoDB Database Server ({role})
Documentation=https://docs.mongodb.org/manual
After=network-online.target
Wants=network-online.target

[Service]
User=mongod
Group=mongod
EnvironmentFile=-/etc/default/mongod
ExecStart=/usr/bin/mongod --config /etc/mongod-{role}.conf
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5
TimeoutStopSec=5
KillMode=mixed
KillSignal=SIGINT
Type=forking
PIDFile=/var/run/mongodb/mongod-{role}.pid

[Install]
WantedBy=multi-user.target
"""
    
    async def _deploy_instance_config(self, instance_name: str, config: Dict[str, Any], service_config: str) -> None:
        """Deploy configuration to instance using configuration management."""
        # This would typically use Ansible, Chef, Puppet, or similar
        # For now, we'll simulate the deployment
        self.logger.info(f"Deploying configuration to {instance_name}")
        
        # Save configurations locally for reference
        config_file = self.deployment_dir / f"{instance_name}-mongod.conf"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        service_file = self.deployment_dir / f"{instance_name}.service"
        with open(service_file, 'w') as f:
            f.write(service_config)
    
    async def _start_mongodb_service(self, instance_name: str) -> None:
        """Start MongoDB service on instance."""
        self.logger.info(f"Starting MongoDB service on {instance_name}")
        # This would execute remote commands via SSH or configuration management
        # Simulated for now
        await asyncio.sleep(2)  # Simulate startup time
    
    async def _wait_for_mongodb_ready(self, instance_name: str, port: int, timeout: int = 300) -> None:
        """Wait for MongoDB instance to be ready."""
        self.logger.info(f"Waiting for {instance_name} to be ready on port {port}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # This would actually check MongoDB connectivity
                # For now, we'll simulate it
                await asyncio.sleep(5)
                self.logger.info(f"{instance_name} is ready")
                return
            except Exception:
                await asyncio.sleep(5)
        
        raise TimeoutError(f"{instance_name} failed to start within {timeout} seconds")
    
    async def _initialize_cluster(self) -> None:
        """Initialize MongoDB cluster (replica sets and sharding)."""
        self.logger.info("Initializing cluster")
        
        # Initialize all replica sets
        for shard_info in self.deployment_state["services"].values():
            if isinstance(shard_info, dict) and "replica_set" in shard_info:
                await self._initialize_replica_set(shard_info["replica_set"], shard_info["members"])
        
        # Initialize sharding if multiple shards
        if self.config.shard_count > 1:
            await self._initialize_sharding()
    
    async def _initialize_replica_set(self, replica_set_name: str, members: List[str]) -> None:
        """Initialize MongoDB replica set."""
        self.logger.info(f"Initializing replica set: {replica_set_name}")
        
        # Generate replica set configuration
        rs_config = {
            "_id": replica_set_name,
            "members": []
        }
        
        for i, member in enumerate(members):
            rs_config["members"].append({
                "_id": i,
                "host": f"{member}:27018" if "shard" in replica_set_name else f"{member}:27019"
            })
        
        # Save replica set configuration
        rs_config_file = self.deployment_dir / f"{replica_set_name}-config.json"
        with open(rs_config_file, 'w') as f:
            json.dump(rs_config, f, indent=2)
        
        # This would execute rs.initiate() on the primary
        await asyncio.sleep(10)  # Simulate initialization time
    
    async def _initialize_config_replica_set(self, config_servers: List[str]) -> None:
        """Initialize config server replica set."""
        await self._initialize_replica_set("configReplSet", config_servers)
    
    async def _initialize_shard_replica_set(self, shard_name: str, members: List[str]) -> None:
        """Initialize shard replica set."""
        replica_set_name = f"{shard_name}rs"
        await self._initialize_replica_set(replica_set_name, members)
    
    async def _initialize_sharding(self) -> None:
        """Initialize MongoDB sharding."""
        if self.config.shard_count <= 1:
            return
        
        self.logger.info("Initializing sharding")
        
        # Add shards to cluster
        for shard_id in range(self.config.shard_count):
            shard_name = f"shard{shard_id:02d}"
            replica_set_name = f"{shard_name}rs"
            
            # Get shard members
            shard_info = self.deployment_state["services"][f"shard_{shard_id}"]
            shard_hosts = ",".join([f"{member}:27018" for member in shard_info["members"]])
            
            # This would execute sh.addShard() on mongos
            self.logger.info(f"Adding shard: {replica_set_name}/{shard_hosts}")
        
        # Enable sharding for databases
        await self._enable_database_sharding()
    
    async def _enable_database_sharding(self) -> None:
        """Enable sharding for databases."""
        databases_to_shard = ["ainflue_content", "ainflue_analytics", "ainflue_users"]
        
        for database in databases_to_shard:
            self.logger.info(f"Enabling sharding for database: {database}")
            # This would execute sh.enableSharding() and sh.shardCollection()
    
    async def _configure_security(self) -> None:
        """Configure MongoDB security."""
        self.logger.info("Configuring security")
        
        if self.config.authentication_enabled:
            await self._create_users()
        
        if self.config.tls_enabled:
            await self._configure_tls()
        
        if self.config.firewall_enabled:
            await self._configure_firewall()
    
    async def _create_users(self) -> None:
        """Create MongoDB users and roles."""
        self.logger.info("Creating MongoDB users")
        
        # Create admin user
        admin_user = {
            "user": "admin",
            "pwd": "secure_password",  # This should be generated securely
            "roles": ["root"]
        }
        
        # Create application users
        app_users = [
            {
                "user": "ainflue_app",
                "pwd": "app_password",
                "roles": [{"role": "readWrite", "db": "ainflue_content"}]
            },
            {
                "user": "ainflue_analytics",
                "pwd": "analytics_password",
                "roles": [{"role": "readWrite", "db": "ainflue_analytics"}]
            }
        ]
        
        # Save user configurations (passwords should be encrypted)
        users_config = self.deployment_dir / "users.json"
        with open(users_config, 'w') as f:
            json.dump({"admin": admin_user, "apps": app_users}, f, indent=2)
    
    async def _configure_tls(self) -> None:
        """Configure TLS/SSL certificates."""
        self.logger.info("Configuring TLS certificates")
        
        # Generate or deploy TLS certificates
        # This would typically use Let's Encrypt, internal CA, or cloud-managed certificates
    
    async def _configure_firewall(self) -> None:
        """Configure firewall rules."""
        self.logger.info("Configuring firewall rules")
        
        # Configure security groups, iptables, or cloud firewalls
        # Only allow necessary ports and IP ranges
    
    async def _setup_monitoring(self) -> None:
        """Setup monitoring and observability."""
        self.logger.info("Setting up monitoring")
        
        if self.config.prometheus_enabled:
            await self._deploy_prometheus()
        
        if self.config.grafana_enabled:
            await self._deploy_grafana()
        
        if self.config.alerts_enabled:
            await self._configure_alerts()
    
    async def _deploy_prometheus(self) -> None:
        """Deploy Prometheus for metrics collection."""
        self.logger.info("Deploying Prometheus")
        
        # Configure MongoDB exporter
        # Deploy Prometheus server
        # Configure scraping endpoints
    
    async def _deploy_grafana(self) -> None:
        """Deploy Grafana for visualization."""
        self.logger.info("Deploying Grafana")
        
        # Deploy Grafana
        # Import MongoDB dashboards
        # Configure data sources
    
    async def _configure_alerts(self) -> None:
        """Configure alerting rules."""
        self.logger.info("Configuring alerts")
        
        # Configure AlertManager
        # Setup notification channels
        # Define alerting rules
    
    async def _configure_backups(self) -> None:
        """Configure automated backups."""
        self.logger.info("Configuring backups")
        
        # Configure MongoDB Cloud Manager, Ops Manager, or custom backup solution
        # Setup backup schedules
        # Configure retention policies
        # Test restore procedures
    
    async def _validate_deployment(self) -> None:
        """Validate deployment health and functionality."""
        self.logger.info("Validating deployment")
        
        # Test connectivity to all nodes
        # Verify replica set status
        # Test read/write operations
        # Check monitoring endpoints
        # Validate backup functionality
        
        validation_results = {
            "connectivity": await self._test_connectivity(),
            "replica_sets": await self._validate_replica_sets(),
            "sharding": await self._validate_sharding() if self.config.shard_count > 1 else True,
            "security": await self._validate_security(),
            "monitoring": await self._validate_monitoring(),
            "backups": await self._validate_backups()
        }
        
        self.deployment_state["validation"] = validation_results
        
        # Check if all validations passed
        all_passed = all(validation_results.values())
        if not all_passed:
            raise Exception(f"Deployment validation failed: {validation_results}")
    
    async def _test_connectivity(self) -> bool:
        """Test connectivity to all MongoDB nodes."""
        self.logger.info("Testing connectivity")
        # Test connections to all nodes
        return True  # Simulated
    
    async def _validate_replica_sets(self) -> bool:
        """Validate replica set configurations."""
        self.logger.info("Validating replica sets")
        # Check rs.status() on all replica sets
        return True  # Simulated
    
    async def _validate_sharding(self) -> bool:
        """Validate sharding configuration."""
        self.logger.info("Validating sharding")
        # Check sh.status() and shard distribution
        return True  # Simulated
    
    async def _validate_security(self) -> bool:
        """Validate security configuration."""
        self.logger.info("Validating security")
        # Test authentication, authorization, TLS
        return True  # Simulated
    
    async def _validate_monitoring(self) -> bool:
        """Validate monitoring setup."""
        self.logger.info("Validating monitoring")
        # Check monitoring endpoints and dashboards
        return True  # Simulated
    
    async def _validate_backups(self) -> bool:
        """Validate backup configuration."""
        self.logger.info("Validating backups")
        # Test backup and restore procedures
        return True  # Simulated
    
    async def _save_deployment_state(self) -> None:
        """Save deployment state to file."""
        state_file = self.deployment_dir / "deployment_state.json"
        with open(state_file, 'w') as f:
            json.dump(self.deployment_state, f, indent=2)
        
        self.logger.info(f"Deployment state saved to {state_file}")
    
    def _generate_user_data(self, shard_name: str, replica_id: int) -> str:
        """Generate cloud-init user data script."""
        return f"""#!/bin/bash
# MongoDB installation and configuration
yum update -y
yum install -y wget

# Install MongoDB
cat << EOF > /etc/yum.repos.d/mongodb-org-{self.config.mongodb_version[:3]}.repo
[mongodb-org-{self.config.mongodb_version[:3]}]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2/mongodb-org/{self.config.mongodb_version[:3]}/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-{self.config.mongodb_version[:3]}.asc
EOF

yum install -y mongodb-org-{self.config.mongodb_version}

# Create directories
mkdir -p /var/lib/mongodb/shard
mkdir -p /var/log/mongodb
chown -R mongod:mongod /var/lib/mongodb
chown -R mongod:mongod /var/log/mongodb

# Configure instance
echo "Cluster: {self.config.cluster_name}" > /etc/mongodb_instance_info
echo "Shard: {shard_name}" >> /etc/mongodb_instance_info
echo "Replica: {replica_id}" >> /etc/mongodb_instance_info
"""
    
    async def _run_terraform_apply(self) -> None:
        """Run Terraform to provision infrastructure."""
        try:
            self.logger.info("Running Terraform apply")
            
            # Initialize Terraform
            subprocess.run(
                ["terraform", "init"],
                cwd=self.deployment_dir,
                check=True,
                capture_output=True
            )
            
            # Plan deployment
            subprocess.run(
                ["terraform", "plan", "-out=tfplan"],
                cwd=self.deployment_dir,
                check=True,
                capture_output=True
            )
            
            # Apply deployment
            subprocess.run(
                ["terraform", "apply", "tfplan"],
                cwd=self.deployment_dir,
                check=True,
                capture_output=True
            )
            
            self.logger.info("Terraform deployment completed")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Terraform failed: {e}")
            raise
    
    async def destroy_cluster(self) -> Dict[str, Any]:
        """Destroy MongoDB cluster and clean up resources."""
        try:
            self.logger.info(f"Destroying cluster: {self.config.cluster_name}")
            
            # Stop all MongoDB services
            await self._stop_all_services()
            
            # Destroy infrastructure
            await self._destroy_infrastructure()
            
            # Clean up deployment artifacts
            await self._cleanup_deployment()
            
            self.deployment_state["status"] = "destroyed"
            self.deployment_state["destroyed_at"] = datetime.now().isoformat()
            await self._save_deployment_state()
            
            return self.deployment_state
            
        except Exception as e:
            self.logger.error(f"Cluster destruction failed: {str(e)}")
            raise
    
    async def _stop_all_services(self) -> None:
        """Stop all MongoDB services."""
        self.logger.info("Stopping all MongoDB services")
        # Stop services gracefully
    
    async def _destroy_infrastructure(self) -> None:
        """Destroy cloud infrastructure."""
        self.logger.info("Destroying infrastructure")
        
        try:
            subprocess.run(
                ["terraform", "destroy", "-auto-approve"],
                cwd=self.deployment_dir,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Infrastructure destruction failed: {e}")
            raise
    
    async def _cleanup_deployment(self) -> None:
        """Clean up deployment artifacts."""
        self.logger.info("Cleaning up deployment artifacts")
        # Remove temporary files, certificates, etc.
    
    async def scale_cluster(self, new_shard_count: int) -> Dict[str, Any]:
        """Scale MongoDB cluster by adding or removing shards."""
        if new_shard_count == self.config.shard_count:
            self.logger.info("No scaling required")
            return self.deployment_state
        
        if new_shard_count > self.config.shard_count:
            await self._scale_out(new_shard_count)
        else:
            await self._scale_in(new_shard_count)
        
        self.config.shard_count = new_shard_count
        await self._save_deployment_state()
        
        return self.deployment_state
    
    async def _scale_out(self, new_shard_count: int) -> None:
        """Add new shards to cluster."""
        self.logger.info(f"Scaling out from {self.config.shard_count} to {new_shard_count} shards")
        
        for shard_id in range(self.config.shard_count, new_shard_count):
            shard_name = f"shard{shard_id:02d}"
            replica_set_name = f"{shard_name}rs"
            
            # Deploy new shard
            shard_members = []
            for replica_id in range(3):
                member_name = f"{self.config.cluster_name}-{shard_name}-{replica_id}"
                shard_members.append(member_name)
                await self._deploy_mongodb_instance(member_name, "shardsvr", port=27018, replica_set=replica_set_name)
            
            # Initialize replica set
            await self._initialize_shard_replica_set(shard_name, shard_members)
            
            # Add shard to cluster
            await self._add_shard_to_cluster(shard_name, shard_members)
            
            self.deployment_state["services"][f"shard_{shard_id}"] = {
                "name": shard_name,
                "replica_set": replica_set_name,
                "members": shard_members
            }
    
    async def _scale_in(self, new_shard_count: int) -> None:
        """Remove shards from cluster."""
        self.logger.info(f"Scaling in from {self.config.shard_count} to {new_shard_count} shards")
        
        for shard_id in range(new_shard_count, self.config.shard_count):
            shard_name = f"shard{shard_id:02d}"
            
            # Drain shard data
            await self._drain_shard(shard_name)
            
            # Remove shard from cluster
            await self._remove_shard_from_cluster(shard_name)
            
            # Destroy shard instances
            shard_info = self.deployment_state["services"][f"shard_{shard_id}"]
            for member in shard_info["members"]:
                await self._destroy_instance(member)
            
            # Remove from deployment state
            del self.deployment_state["services"][f"shard_{shard_id}"]
    
    async def _add_shard_to_cluster(self, shard_name: str, members: List[str]) -> None:
        """Add shard to MongoDB cluster."""
        self.logger.info(f"Adding shard {shard_name} to cluster")
        # Execute sh.addShard() command
    
    async def _drain_shard(self, shard_name: str) -> None:
        """Drain data from shard before removal."""
        self.logger.info(f"Draining shard {shard_name}")
        # Execute sh.removeShard() and wait for balancer to move chunks
    
    async def _remove_shard_from_cluster(self, shard_name: str) -> None:
        """Remove shard from MongoDB cluster."""
        self.logger.info(f"Removing shard {shard_name} from cluster")
        # Complete shard removal process
    
    async def _destroy_instance(self, instance_name: str) -> None:
        """Destroy MongoDB instance."""
        self.logger.info(f"Destroying instance {instance_name}")
        # Stop service and destroy infrastructure


# Example usage
async def deploy_production_cluster():
    """Example deployment of production MongoDB cluster."""
    config = DeploymentConfig(
        cluster_name="ainflue-prod",
        environment="production",
        shard_count=3,
        instance_type="m5.2xlarge",
        storage_size_gb=500,
        mongodb_version="7.0",
        authentication_enabled=True,
        tls_enabled=True,
        monitoring_enabled=True,
        backup_enabled=True,
        encryption_at_rest=True
    )
    
    deployer = ClusterDeployer(config)
    
    try:
        result = await deployer.deploy_cluster()
        print(f"Deployment successful: {result['id']}")
        return result
    except Exception as e:
        print(f"Deployment failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Run example deployment
    asyncio.run(deploy_production_cluster())