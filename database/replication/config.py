"""
Replication Configuration Manager - IA Influencer Agent Platform

Centralized configuration management for database replication across all
supported systems. Handles environment-specific settings, security credentials,
and topology configurations for the content creator platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from cryptography.fernet import Fernet
import secrets
import json


@dataclass
class DatabaseConfig:
    """Database-specific configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_enabled: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    pool_size: int = 20
    max_overflow: int = 30
    timeout: int = 30
    charset: str = "utf8mb4"
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplicationTopologyConfig:
    """Replication topology configuration"""
    primary_region: str
    secondary_regions: List[str]
    failover_strategy: str = "automatic"
    conflict_resolution: str = "last_write_wins"
    sync_mode: str = "async"
    lag_threshold: int = 1000  # milliseconds
    health_check_interval: int = 30  # seconds
    monitoring_enabled: bool = True


@dataclass
class SecurityConfig:
    """Security configuration for replication"""
    encryption_enabled: bool = True
    encryption_algorithm: str = "AES-256"
    tls_version: str = "1.3"
    certificate_validation: bool = True
    audit_logging: bool = True
    access_control_enabled: bool = True
    allowed_networks: List[str] = field(default_factory=list)
    blacklisted_ips: List[str] = field(default_factory=list)


class ReplicationConfig:
    """
    Comprehensive configuration manager for database replication.
    
    Handles all configuration aspects including database connections,
    topology, security, monitoring, and performance tuning for the
    IA Influencer Agent platform.
    """
    
    def __init__(self, config_path: Optional[str] = None, environment: str = "production"):
        """
        Initialize replication configuration.
        
        Args:
            config_path: Path to configuration file
            environment: Environment name (development, staging, production)
        """
        self.environment = environment
        self.logger = logging.getLogger(f"{__name__}.ReplicationConfig")
        
        # Configuration paths
        self.config_path = config_path or self._get_default_config_path()
        self.secrets_path = self._get_secrets_path()
        
        # Configuration data
        self.config_data: Dict[str, Any] = {}
        self.secrets_data: Dict[str, Any] = {}
        self.database_configs: Dict[str, DatabaseConfig] = {}
        self.topology_config: Optional[ReplicationTopologyConfig] = None
        self.security_config: Optional[SecurityConfig] = None
        
        # Encryption for secrets
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Load configuration
        self._load_configuration()
        
        self.logger.info(f"ReplicationConfig initialized for environment: {environment}")
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        base_path = Path(__file__).parent
        return str(base_path / "config.yml")
    
    def _get_secrets_path(self) -> str:
        """Get secrets file path"""
        base_path = Path(__file__).parent
        return str(base_path / f"secrets_{self.environment}.enc")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for secrets"""
        key_file = Path(__file__).parent / ".encryption_key"
        
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            key_file.chmod(0o600)  # Restrict permissions
            return key
    
    def _load_configuration(self) -> None:
        """Load configuration from files"""



        try:
            # Load main configuration
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config_data = yaml.safe_load(f) or {}
            else:
                self.logger.warning(f"Configuration file not found: {self.config_path}")
                self.config_data = self._get_default_config()
            
            # Load encrypted secrets
            self._load_secrets()
            
            # Parse configuration sections
            self._parse_database_configs()
            self._parse_topology_config()
            self._parse_security_config()
            
            self.logger.info("Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            # Use default configuration as fallback
            self.config_data = self._get_default_config()
            self._parse_database_configs()
            self._parse_topology_config()
            self._parse_security_config()
    
    def _load_secrets(self) -> None:
        """Load and decrypt secrets"""



        try:
            if os.path.exists(self.secrets_path):
                with open(self.secrets_path, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                self.secrets_data = json.loads(decrypted_data.decode())
            else:
                self.logger.warning(f"Secrets file not found: {self.secrets_path}")
                self.secrets_data = {}
                
        except Exception as e:
            self.logger.error(f"Failed to load secrets: {e}")
            self.secrets_data = {}
    
    def _save_secrets(self) -> None:
        """Encrypt and save secrets"""



        try:
            json_data = json.dumps(self.secrets_data).encode()
            encrypted_data = self.cipher.encrypt(json_data)
            
            with open(self.secrets_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Restrict file permissions
            os.chmod(self.secrets_path, 0o600)
            
        except Exception as e:
            self.logger.error(f"Failed to save secrets: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""



        return {
            "environment": self.environment,
            "replication": {
                "mode": "master_slave",
                "topology": {
                    "primary_region": "eu-west-1",
                    "secondary_regions": ["us-east-1"],
                    "failover_strategy": "automatic",
                    "conflict_resolution": "last_write_wins",
                    "sync_mode": "async",
                    "lag_threshold": 1000,
                    "health_check_interval": 30,
                    "monitoring_enabled": True
                },
                "security": {
                    "encryption_enabled": True,
                    "encryption_algorithm": "AES-256",
                    "tls_version": "1.3",
                    "certificate_validation": True,
                    "audit_logging": True,
                    "access_control_enabled": True,
                    "allowed_networks": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
                    "blacklisted_ips": []
                }
            },
            "databases": {
                "postgresql": {
                    "enabled": True,
                    "replication_type": "streaming",
                    "logical_replication": True,
                    "connection_pool_size": 20,
                    "max_connections": 100
                },
                "redis": {
                    "enabled": True,
                    "replication_type": "sentinel",
                    "cluster_enabled": True,
                    "sentinel_nodes": 3
                },
                "mongodb": {
                    "enabled": True,
                    "replication_type": "replica_set",
                    "read_preference": "secondaryPreferred",
                    "write_concern": "majority"
                },
                "elasticsearch": {
                    "enabled": True,
                    "replication_type": "cross_cluster",
                    "shard_allocation": "balanced",
                    "replica_count": 2
                },
                "vector_store": {
                    "enabled": True,
                    "replication_type": "backup_sync",
                    "backup_frequency": "daily",
                    "compression_enabled": True
                }
            },
            "monitoring": {
                "health_check_interval": 30,
                "metrics_collection_interval": 10,
                "alert_threshold": 0.01,
                "lag_threshold": 1000,
                "max_error_count": 5,
                "monitoring_interval": 60
            },
            "performance": {
                "batch_size": 1000,
                "parallel_workers": 4,
                "memory_limit": "1GB",
                "disk_space_threshold": 0.9,
                "network_timeout": 30
            }
        }
    
    def _parse_database_configs(self) -> None:
        """Parse database configurations"""
        databases_config = self.config_data.get("databases", {})
        
        for db_type, db_config in databases_config.items():
            if not db_config.get("enabled", False):
                continue
            
            # Get connection details from secrets or environment
            connection_config = self._get_database_connection_config(db_type)
            
            if connection_config:
                self.database_configs[db_type] = DatabaseConfig(**connection_config)
    
    def _get_database_connection_config(self, db_type: str) -> Optional[Dict[str, Any]]:
        """Get database connection configuration"""
        # Try to get from secrets first
        secrets_key = f"{db_type}_connection"
        if secrets_key in self.secrets_data:
            return self.secrets_data[secrets_key]
        
        # Try environment variables
        env_mapping = {
            "postgresql": {
                "host": f"POSTGRES_HOST",
                "port": f"POSTGRES_PORT",
                "database": f"POSTGRES_DB",
                "username": f"POSTGRES_USER",
                "password": f"POSTGRES_PASSWORD"
            },
            "redis": {
                "host": f"REDIS_HOST",
                "port": f"REDIS_PORT",
                "database": "0",
                "username": f"REDIS_USER",
                "password": f"REDIS_PASSWORD"
            },
            "mongodb": {
                "host": f"MONGODB_HOST",
                "port": f"MONGODB_PORT",
                "database": f"MONGODB_DB",
                "username": f"MONGODB_USER",
                "password": f"MONGODB_PASSWORD"
            },
            "elasticsearch": {
                "host": f"ELASTICSEARCH_HOST",
                "port": f"ELASTICSEARCH_PORT",
                "database": "",
                "username": f"ELASTICSEARCH_USER",
                "password": f"ELASTICSEARCH_PASSWORD"
            }
        }
        
        if db_type in env_mapping:
            config = {}
            for key, env_var in env_mapping[db_type].items():
                value = os.getenv(env_var)
                if value:
                    config[key] = int(value) if key == "port" else value
            
            if len(config) >= 4:  # At least host, port, username, password
                return config
        
        return None
    
    def _parse_topology_config(self) -> None:
        """Parse topology configuration"""
        topology_data = self.config_data.get("replication", {}).get("topology", {})
        
        self.topology_config = ReplicationTopologyConfig(
            primary_region=topology_data.get("primary_region", "eu-west-1"),
            secondary_regions=topology_data.get("secondary_regions", ["us-east-1"]),
            failover_strategy=topology_data.get("failover_strategy", "automatic"),
            conflict_resolution=topology_data.get("conflict_resolution", "last_write_wins"),
            sync_mode=topology_data.get("sync_mode", "async"),
            lag_threshold=topology_data.get("lag_threshold", 1000),
            health_check_interval=topology_data.get("health_check_interval", 30),
            monitoring_enabled=topology_data.get("monitoring_enabled", True)
        )
    
    def _parse_security_config(self) -> None:
        """Parse security configuration"""
        security_data = self.config_data.get("replication", {}).get("security", {})
        
        self.security_config = SecurityConfig(
            encryption_enabled=security_data.get("encryption_enabled", True),
            encryption_algorithm=security_data.get("encryption_algorithm", "AES-256"),
            tls_version=security_data.get("tls_version", "1.3"),
            certificate_validation=security_data.get("certificate_validation", True),
            audit_logging=security_data.get("audit_logging", True),
            access_control_enabled=security_data.get("access_control_enabled", True),
            allowed_networks=security_data.get("allowed_networks", []),
            blacklisted_ips=security_data.get("blacklisted_ips", [])
        )
    
    def get_database_config(self, database_type: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for specific database type.
        
        Args:
            database_type: Type of database
            
        Returns:
            Database configuration or None if not found
        """
        db_config = self.database_configs.get(database_type)
        if not db_config:
            return None
        
        # Convert dataclass to dict and add general config
        config_dict = {
            "host": db_config.host,
            "port": db_config.port,
            "database": db_config.database,
            "username": db_config.username,
            "password": db_config.password,
            "ssl_enabled": db_config.ssl_enabled,
            "ssl_cert_path": db_config.ssl_cert_path,
            "ssl_key_path": db_config.ssl_key_path,
            "ssl_ca_path": db_config.ssl_ca_path,
            "pool_size": db_config.pool_size,
            "max_overflow": db_config.max_overflow,
            "timeout": db_config.timeout,
            "charset": db_config.charset,
            **db_config.additional_params
        }
        
        # Add database-specific configuration
        db_specific = self.config_data.get("databases", {}).get(database_type, {})
        config_dict.update(db_specific)
        
        return config_dict
    
    def get_topology_config(self) -> Dict[str, Any]:
        """Get topology configuration as dictionary"""
        if not self.topology_config:
            return {}
        
        return {
            "primary_region": self.topology_config.primary_region,
            "secondary_regions": self.topology_config.secondary_regions,
            "failover_strategy": self.topology_config.failover_strategy,
            "conflict_resolution": self.topology_config.conflict_resolution,
            "sync_mode": self.topology_config.sync_mode,
            "lag_threshold": self.topology_config.lag_threshold,
            "health_check_interval": self.topology_config.health_check_interval,
            "monitoring_enabled": self.topology_config.monitoring_enabled,
            "databases": self.config_data.get("databases", {})
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration as dictionary"""
        if not self.security_config:
            return {}
        
        return {
            "encryption_enabled": self.security_config.encryption_enabled,
            "encryption_algorithm": self.security_config.encryption_algorithm,
            "tls_version": self.security_config.tls_version,
            "certificate_validation": self.security_config.certificate_validation,
            "audit_logging": self.security_config.audit_logging,
            "access_control_enabled": self.security_config.access_control_enabled,
            "allowed_networks": self.security_config.allowed_networks,
            "blacklisted_ips": self.security_config.blacklisted_ips
        }
    
    def set_database_credentials(self, database_type: str, credentials: Dict[str, Any]) -> None:
        """
        Set encrypted database credentials.
        
        Args:
            database_type: Type of database
            credentials: Database connection credentials
        """
        secrets_key = f"{database_type}_connection"
        self.secrets_data[secrets_key] = credentials
        self._save_secrets()
        
        # Update in-memory config
        if database_type not in self.database_configs:
            self.database_configs[database_type] = DatabaseConfig(**credentials)
        else:
            # Update existing config
            for key, value in credentials.items():
                setattr(self.database_configs[database_type], key, value)
        
        self.logger.info(f"Credentials updated for {database_type}")
    
    def update_topology(self, topology_config: Dict[str, Any]) -> None:
        """
        Update topology configuration.
        
        Args:
            topology_config: New topology configuration
        """
        self.config_data.setdefault("replication", {})["topology"] = topology_config
        self._parse_topology_config()
        self._save_configuration()
        
        self.logger.info("Topology configuration updated")
    
    def _save_configuration(self) -> None:
        """Save configuration to file"""



        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False)
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    # Property accessors for commonly used values
    @property
    def health_check_interval(self) -> int:
        """Get health check interval in seconds"""



        return self.config_data.get("monitoring", {}).get("health_check_interval", 30)
    
    @property
    def lag_threshold(self) -> int:
        """Get replication lag threshold in milliseconds"""



        return self.config_data.get("monitoring", {}).get("lag_threshold", 1000)
    
    @property
    def max_error_count(self) -> int:
        """Get maximum error count before recovery"""



        return self.config_data.get("monitoring", {}).get("max_error_count", 5)
    
    @property
    def monitoring_interval(self) -> int:
        """Get monitoring interval in seconds"""



        return self.config_data.get("monitoring", {}).get("monitoring_interval", 60)
    
    @property
    def automatic_failover_enabled(self) -> bool:
        """Check if automatic failover is enabled"""



        return (self.topology_config and 
                self.topology_config.failover_strategy == "automatic")
    
    @property
    def batch_size(self) -> int:
        """Get batch size for replication operations"""



        return self.config_data.get("performance", {}).get("batch_size", 1000)
    
    @property
    def parallel_workers(self) -> int:
        """Get number of parallel workers"""



        return self.config_data.get("performance", {}).get("parallel_workers", 4)
    
    def validate_configuration(self) -> List[str]:
        """
        Validate configuration and return list of issues.
        
        Returns:
            List of validation error messages
        """
        issues = []
        
        # Check database configurations
        for db_type, db_config in self.database_configs.items():
            if not db_config.host:
                issues.append(f"Missing host for {db_type}")
            if not db_config.username:
                issues.append(f"Missing username for {db_type}")
            if not db_config.password:
                issues.append(f"Missing password for {db_type}")
        
        # Check topology configuration
        if not self.topology_config:
            issues.append("Missing topology configuration")
        elif not self.topology_config.primary_region:
            issues.append("Missing primary region in topology")
        
        # Check security configuration
        if not self.security_config:
            issues.append("Missing security configuration")
        
        # Check environment variables for sensitive data
        sensitive_env_vars = [
            "POSTGRES_PASSWORD", "REDIS_PASSWORD", "MONGODB_PASSWORD"
        ]
        for env_var in sensitive_env_vars:
            if env_var in os.environ:
                issues.append(f"Sensitive environment variable {env_var} should be in secrets")
        
        return issues
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get configuration summary for logging/debugging"""



        return {
            "environment": self.environment,
            "databases_configured": list(self.database_configs.keys()),
            "primary_region": self.topology_config.primary_region if self.topology_config else None,
            "secondary_regions": self.topology_config.secondary_regions if self.topology_config else [],
            "security_enabled": self.security_config.encryption_enabled if self.security_config else False,
            "monitoring_enabled": self.topology_config.monitoring_enabled if self.topology_config else False,
            "automatic_failover": self.automatic_failover_enabled
        }
