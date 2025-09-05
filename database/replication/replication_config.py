"""🔧 Database Replication Configuration - Enterprise Configuration Management
==============================================================================
Module: database/replication/replication_config.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Database Replication & High Availability Architect
Type: Configuration & Topology Management - Enterprise Production-Ready
Responsibility: Centralized configuration and topology management for database replication
==================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This module provides comprehensive configuration management for database replication:
- Environment-specific replication topologies
- Security credentials and encryption management  
- Network optimization and performance tuning
- Disaster recovery configuration
- Multi-region synchronization settings
"""

import asyncio
import logging
import os
import json
import yaml
from typing import Dict, Any, Optional, List, Set, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import hashlib
import ssl
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Supported database types for replication."""
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"
    VECTOR_DB = "vector_db"

class ReplicationMode(Enum):
    """Replication modes."""
    STREAMING = "streaming"
    LOGICAL = "logical"
    MASTER_SLAVE = "master_slave"
    MASTER_MASTER = "master_master"
    CLUSTER = "cluster"

class FailoverStrategy(Enum):
    """Failover strategies."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"

class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategies."""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL_RESOLUTION = "manual_resolution"
    BUSINESS_LOGIC = "business_logic"

@dataclass
class DatabaseEndpoint:
    """Database connection endpoint configuration."""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_enabled: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    connection_timeout: int = 30
    max_connections: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReplicationTopology:
    """Replication topology configuration."""
    master: DatabaseEndpoint
    slaves: List[DatabaseEndpoint] = field(default_factory=list)
    replication_mode: ReplicationMode = ReplicationMode.STREAMING
    lag_threshold_ms: float = 1000.0
    max_slave_lag_ms: float = 5000.0
    health_check_interval: int = 30
    auto_promote_slave: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityConfig:
    """Security configuration for replication."""
    encryption_enabled: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    tls_version: str = "TLSv1.3"
    cert_validation: bool = True
    key_rotation_interval_days: int = 90
    access_control_enabled: bool = True
    audit_logging: bool = True
    security_headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NetworkConfig:
    """Network optimization configuration."""
    tcp_keepalive: bool = True
    tcp_nodelay: bool = True
    compression_enabled: bool = True
    compression_algorithm: str = "zstd"
    bandwidth_limit_mbps: Optional[float] = None
    latency_optimization: bool = True
    connection_pooling: bool = True
    pool_size: int = 10
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration."""
    metrics_enabled: bool = True
    metrics_interval_seconds: int = 60
    health_check_interval: int = 30
    performance_check_interval: int = 120
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'lag_threshold_ms': 1000.0,
        'error_rate_threshold': 0.05,
        'cpu_threshold': 0.8,
        'memory_threshold': 0.85,
        'disk_threshold': 0.9
    })
    notification_channels: List[str] = field(default_factory=list)
    dashboard_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DisasterRecoveryConfig:
    """Disaster recovery configuration."""
    backup_enabled: bool = True
    backup_interval_hours: int = 6
    backup_retention_days: int = 30
    point_in_time_recovery: bool = True
    cross_region_backup: bool = True
    backup_compression: bool = True
    backup_encryption: bool = True
    recovery_test_interval_days: int = 7
    rto_minutes: int = 60  # Recovery Time Objective
    rpo_minutes: int = 15  # Recovery Point Objective
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""
    optimization_enabled: bool = True
    optimization_interval: int = 300
    max_lag_threshold_ms: float = 1000.0
    max_error_threshold: int = 10
    connection_optimization: bool = True
    query_optimization: bool = True
    index_optimization: bool = True
    cache_optimization: bool = True
    batch_size: int = 1000
    parallel_workers: int = 4
    metadata: Dict[str, Any] = field(default_factory=dict)

class ReplicationConfig:
    """Comprehensive replication configuration."""
    
    def __init__(self, config_file: Optional[str] = None, **kwargs):
        """Initialize configuration from file or parameters."""
        
        # Default values
        self.environment = kwargs.get('environment', 'development')
        self.enabled_databases: Set[DatabaseType] = set(kwargs.get('enabled_databases', []))
        self.regions: List[str] = kwargs.get('regions', ['default'])
        self.primary_region: str = kwargs.get('primary_region', 'default')
        
        # Database configurations
        self.database_topologies: Dict[DatabaseType, ReplicationTopology] = {}
        
        # Configuration objects
        self.security = SecurityConfig(**kwargs.get('security', {}))
        self.network = NetworkConfig(**kwargs.get('network', {}))
        self.monitoring = MonitoringConfig(**kwargs.get('monitoring', {}))
        self.disaster_recovery = DisasterRecoveryConfig(**kwargs.get('disaster_recovery', {}))
        self.performance = PerformanceConfig(**kwargs.get('performance', {}))
        
        # Global settings
        self.auto_failover_enabled = kwargs.get('auto_failover_enabled', True)
        self.failover_strategy = FailoverStrategy(kwargs.get('failover_strategy', 'automatic'))
        self.conflict_resolution = ConflictResolutionStrategy(kwargs.get('conflict_resolution', 'last_write_wins'))
        
        # Timing configurations
        self.health_check_interval = kwargs.get('health_check_interval', 30)
        self.performance_check_interval = kwargs.get('performance_check_interval', 120)
        self.optimization_interval = kwargs.get('optimization_interval', 300)
        self.max_lag_threshold_ms = kwargs.get('max_lag_threshold_ms', 1000.0)
        self.max_error_threshold = kwargs.get('max_error_threshold', 10)
        
        # Load from file if provided
        if config_file:
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str):
        """Load configuration from YAML or JSON file."""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                logger.warning(f"Configuration file not found: {config_file}")
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
            
            self._merge_config(config_data)
            logger.info(f"✅ Loaded configuration from {config_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration from {config_file}: {e}")
            raise
    
    def _merge_config(self, config_data: Dict[str, Any]):
        """Merge configuration data into current config."""
        try:
            # Update basic settings
            self.environment = config_data.get('environment', self.environment)
            self.enabled_databases = set(DatabaseType(db) for db in config_data.get('enabled_databases', []))
            self.regions = config_data.get('regions', self.regions)
            self.primary_region = config_data.get('primary_region', self.primary_region)
            
            # Update configuration objects
            if 'security' in config_data:
                security_data = config_data['security']
                self.security = SecurityConfig(**{**asdict(self.security), **security_data})
            
            if 'network' in config_data:
                network_data = config_data['network']
                self.network = NetworkConfig(**{**asdict(self.network), **network_data})
            
            if 'monitoring' in config_data:
                monitoring_data = config_data['monitoring']
                self.monitoring = MonitoringConfig(**{**asdict(self.monitoring), **monitoring_data})
            
            if 'disaster_recovery' in config_data:
                dr_data = config_data['disaster_recovery']
                self.disaster_recovery = DisasterRecoveryConfig(**{**asdict(self.disaster_recovery), **dr_data})
            
            if 'performance' in config_data:
                perf_data = config_data['performance']
                self.performance = PerformanceConfig(**{**asdict(self.performance), **perf_data})
            
            # Update database topologies
            if 'database_topologies' in config_data:
                for db_type_str, topology_data in config_data['database_topologies'].items():
                    db_type = DatabaseType(db_type_str)
                    self.database_topologies[db_type] = self._create_topology_from_data(topology_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to merge configuration: {e}")
            raise
    
    def _create_topology_from_data(self, topology_data: Dict[str, Any]) -> ReplicationTopology:
        """Create ReplicationTopology from configuration data."""
        try:
            # Create master endpoint
            master_data = topology_data['master']
            master = DatabaseEndpoint(**master_data)
            
            # Create slave endpoints
            slaves = []
            for slave_data in topology_data.get('slaves', []):
                slaves.append(DatabaseEndpoint(**slave_data))
            
            # Create topology
            return ReplicationTopology(
                master=master,
                slaves=slaves,
                replication_mode=ReplicationMode(topology_data.get('replication_mode', 'streaming')),
                lag_threshold_ms=topology_data.get('lag_threshold_ms', 1000.0),
                max_slave_lag_ms=topology_data.get('max_slave_lag_ms', 5000.0),
                health_check_interval=topology_data.get('health_check_interval', 30),
                auto_promote_slave=topology_data.get('auto_promote_slave', True),
                metadata=topology_data.get('metadata', {})
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create topology from data: {e}")
            raise
    
    def save_to_file(self, config_file: str, format: str = 'yaml'):
        """Save current configuration to file."""
        try:
            config_data = self.to_dict()
            config_path = Path(config_file)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if format.lower() in ['yaml', 'yml']:
                    yaml.dump(config_data, f, default_flow_style=False, indent=2)
                elif format.lower() == 'json':
                    json.dump(config_data, f, indent=2, default=str)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"✅ Saved configuration to {config_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save configuration to {config_file}: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'environment': self.environment,
            'enabled_databases': [db.value for db in self.enabled_databases],
            'regions': self.regions,
            'primary_region': self.primary_region,
            'security': asdict(self.security),
            'network': asdict(self.network),
            'monitoring': asdict(self.monitoring),
            'disaster_recovery': asdict(self.disaster_recovery),
            'performance': asdict(self.performance),
            'database_topologies': {
                db.value: asdict(topology) for db, topology in self.database_topologies.items()
            },
            'auto_failover_enabled': self.auto_failover_enabled,
            'failover_strategy': self.failover_strategy.value,
            'conflict_resolution': self.conflict_resolution.value,
            'health_check_interval': self.health_check_interval,
            'performance_check_interval': self.performance_check_interval,
            'optimization_interval': self.optimization_interval,
            'max_lag_threshold_ms': self.max_lag_threshold_ms,
            'max_error_threshold': self.max_error_threshold
        }
    
    def validate(self) -> bool:
        """Validate configuration consistency and completeness."""
        try:
            errors = []
            
            # Validate enabled databases have topologies
            for db_type in self.enabled_databases:
                if db_type not in self.database_topologies:
                    errors.append(f"Missing topology for enabled database: {db_type.value}")
            
            # Validate primary region is in regions list
            if self.primary_region not in self.regions:
                errors.append(f"Primary region '{self.primary_region}' not in regions list")
            
            # Validate thresholds
            if self.max_lag_threshold_ms <= 0:
                errors.append("max_lag_threshold_ms must be positive")
            
            if self.max_error_threshold <= 0:
                errors.append("max_error_threshold must be positive")
            
            # Validate database endpoints
            for db_type, topology in self.database_topologies.items():
                if not self._validate_endpoint(topology.master):
                    errors.append(f"Invalid master endpoint for {db_type.value}")
                
                for i, slave in enumerate(topology.slaves):
                    if not self._validate_endpoint(slave):
                        errors.append(f"Invalid slave endpoint {i} for {db_type.value}")
            
            if errors:
                for error in errors:
                    logger.error(f"❌ Configuration validation error: {error}")
                return False
            
            logger.info("✅ Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration validation failed: {e}")
            return False
    
    def _validate_endpoint(self, endpoint: DatabaseEndpoint) -> bool:
        """Validate a database endpoint."""
        try:
            # Check required fields
            if not endpoint.host or not endpoint.port or not endpoint.database:
                return False
            
            # Check port range
            if not (1 <= endpoint.port <= 65535):
                return False
            
            # Check SSL configuration consistency
            if endpoint.ssl_enabled:
                if endpoint.ssl_cert_path and not Path(endpoint.ssl_cert_path).exists():
                    logger.warning(f"SSL cert file not found: {endpoint.ssl_cert_path}")
            
            return True
            
        except Exception:
            return False

class TopologyManager:
    """Manages replication topology and network configuration."""
    
    def __init__(self):
        self._config: Optional[ReplicationConfig] = None
        self._topology_cache: Dict[str, Any] = {}
        self._network_optimizer = NetworkOptimizer()
        self._security_manager = SecurityManager()
    
    async def initialize(self, config: ReplicationConfig):
        """Initialize topology manager."""
        try:
            self._config = config
            
            # Validate configuration
            if not config.validate():
                raise ValueError("Invalid replication configuration")
            
            # Initialize network optimizer
            await self._network_optimizer.initialize(config.network)
            
            # Initialize security manager
            await self._security_manager.initialize(config.security)
            
            logger.info("✅ Topology manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize topology manager: {e}")
            raise
    
    async def get_optimal_topology(self, db_type: DatabaseType) -> Optional[ReplicationTopology]:
        """Get optimal topology for a database type."""
        try:
            if not self._config or db_type not in self._config.database_topologies:
                return None
            
            topology = self._config.database_topologies[db_type]
            
            # Apply network optimizations
            optimized_topology = await self._network_optimizer.optimize_topology(topology)
            
            return optimized_topology
            
        except Exception as e:
            logger.error(f"❌ Failed to get optimal topology for {db_type}: {e}")
            return None
    
    async def update_topology(self, db_type: DatabaseType, topology: ReplicationTopology):
        """Update topology for a database type."""
        try:
            if not self._config:
                raise RuntimeError("Topology manager not initialized")
            
            self._config.database_topologies[db_type] = topology
            
            # Clear cache
            cache_key = f"topology_{db_type.value}"
            if cache_key in self._topology_cache:
                del self._topology_cache[cache_key]
            
            logger.info(f"✅ Updated topology for {db_type.value}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update topology for {db_type}: {e}")
            raise
    
    async def close(self):
        """Close topology manager."""
        try:
            if self._network_optimizer:
                await self._network_optimizer.close()
            if self._security_manager:
                await self._security_manager.close()
            logger.info("✅ Topology manager closed")
        except Exception as e:
            logger.error(f"❌ Error closing topology manager: {e}")

class NetworkOptimizer:
    """Optimizes network configuration for replication."""
    
    def __init__(self):
        self._config: Optional[NetworkConfig] = None
    
    async def initialize(self, config: NetworkConfig):
        """Initialize network optimizer."""
        self._config = config
        logger.info("✅ Network optimizer initialized")
    
    async def optimize_topology(self, topology: ReplicationTopology) -> ReplicationTopology:
        """Optimize network settings for a topology."""
        try:
            if not self._config:
                return topology
            
            # Apply optimizations (simplified implementation)
            optimized_topology = topology
            
            # TODO: Implement actual network optimizations
            # - Latency-based slave selection
            # - Bandwidth optimization
            # - Connection pooling optimization
            
            return optimized_topology
            
        except Exception as e:
            logger.error(f"❌ Network optimization failed: {e}")
            return topology
    
    async def close(self):
        """Close network optimizer."""
        pass

class SecurityManager:
    """Manages security configuration and credentials."""
    
    def __init__(self):
        self._config: Optional[SecurityConfig] = None
        self._ssl_context: Optional[ssl.SSLContext] = None
    
    async def initialize(self, config: SecurityConfig):
        """Initialize security manager."""
        try:
            self._config = config
            
            if config.encryption_enabled:
                self._ssl_context = ssl.create_default_context()
                
                # Configure SSL/TLS
                if config.tls_version == "TLSv1.3":
                    self._ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
                elif config.tls_version == "TLSv1.2":
                    self._ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
                
                self._ssl_context.check_hostname = config.cert_validation
                
            logger.info("✅ Security manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize security manager: {e}")
            raise
    
    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Get SSL context for secure connections."""
        return self._ssl_context
    
    def encrypt_credential(self, credential: str) -> str:
        """Encrypt a credential string."""
        try:
            if not self._config or not self._config.encryption_enabled:
                return credential
            
            # Simple hash for demonstration (use proper encryption in production)
            return hashlib.sha256(credential.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"❌ Credential encryption failed: {e}")
            return credential
    
    async def close(self):
        """Close security manager."""
        pass

def load_config_from_environment() -> ReplicationConfig:
    """Load configuration from environment variables."""
    try:
        config_data = {
            'environment': os.getenv('REPLICATION_ENVIRONMENT', 'development'),
            'enabled_databases': os.getenv('REPLICATION_DATABASES', 'postgresql,redis').split(','),
            'regions': os.getenv('REPLICATION_REGIONS', 'default').split(','),
            'primary_region': os.getenv('REPLICATION_PRIMARY_REGION', 'default'),
            'auto_failover_enabled': os.getenv('REPLICATION_AUTO_FAILOVER', 'true').lower() == 'true',
            'max_lag_threshold_ms': float(os.getenv('REPLICATION_MAX_LAG_MS', '1000')),
            'max_error_threshold': int(os.getenv('REPLICATION_MAX_ERRORS', '10')),
        }
        
        return ReplicationConfig(**config_data)
        
    except Exception as e:
        logger.error(f"❌ Failed to load config from environment: {e}")
        return ReplicationConfig()

def create_default_config() -> ReplicationConfig:
    """Create a default replication configuration."""
    return ReplicationConfig(
        environment='development',
        enabled_databases=[DatabaseType.POSTGRESQL, DatabaseType.REDIS],
        regions=['default'],
        primary_region='default',
        auto_failover_enabled=True,
        max_lag_threshold_ms=1000.0,
        max_error_threshold=10
    )