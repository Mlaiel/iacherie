#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Storage Configuration Module
======================================

Enterprise-grade storage configuration for the Ainflue platform.
Comprehensive storage management with multi-cloud support, hierarchical storage,
automated lifecycle management, backup strategies, and intelligent tiering.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
import json
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib

class StorageProvider(str, Enum):
    """Storage providers"""
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    DIGITALOCEAN_SPACES = "digitalocean_spaces"
    CLOUDFLARE_R2 = "cloudflare_r2"
    BACKBLAZE_B2 = "backblaze_b2"
    WASABI = "wasabi"
    MINIO = "minio"
    LOCAL_FILESYSTEM = "local_filesystem"
    NFS = "nfs"
    SFTP = "sftp"
    CUSTOM = "custom"

class StorageTier(str, Enum):
    """Storage tiers based on access patterns"""
    HOT = "hot"                   # Frequently accessed (< 30 days)
    WARM = "warm"                 # Occasionally accessed (30-90 days)
    COOL = "cool"                 # Rarely accessed (90-365 days)
    COLD = "cold"                 # Archive storage (1+ years)
    FROZEN = "frozen"             # Deep archive (7+ years)
    INTELLIGENT = "intelligent"   # Auto-tiering based on access patterns

class StorageClass(str, Enum):
    """Storage classes for cost optimization"""
    STANDARD = "standard"         # Standard storage
    STANDARD_IA = "standard_ia"   # Infrequent Access
    ONEZONE_IA = "onezone_ia"     # One Zone Infrequent Access
    GLACIER = "glacier"           # Glacier archive
    GLACIER_IR = "glacier_ir"     # Glacier Instant Retrieval
    GLACIER_FLEXIBLE = "glacier_flexible"  # Glacier Flexible Retrieval
    GLACIER_DEEP = "glacier_deep" # Glacier Deep Archive
    REDUCED_REDUNDANCY = "reduced_redundancy"  # Reduced Redundancy

class AccessPattern(str, Enum):
    """Access patterns for storage optimization"""
    FREQUENT = "frequent"         # Daily access
    OCCASIONAL = "occasional"     # Weekly access
    RARE = "rare"                # Monthly access
    ARCHIVE = "archive"          # Yearly or less
    UNKNOWN = "unknown"          # Pattern not determined

class CompressionType(str, Enum):
    """Compression algorithms"""
    NONE = "none"
    GZIP = "gzip"
    BROTLI = "brotli"
    LZ4 = "lz4"
    ZSTD = "zstd"
    SNAPPY = "snappy"
    XZ = "xz"

class EncryptionType(str, Enum):
    """Encryption types"""
    NONE = "none"
    AES_256 = "aes_256"
    AES_256_GCM = "aes_256_gcm"
    CHACHA20 = "chacha20"
    SERVER_SIDE = "server_side"
    CLIENT_SIDE = "client_side"
    ENVELOPE = "envelope"

class ReplicationStrategy(str, Enum):
    """Replication strategies"""
    NONE = "none"
    SINGLE_REGION = "single_region"
    CROSS_REGION = "cross_region"
    MULTI_CLOUD = "multi_cloud"
    GLOBAL = "global"
    CUSTOM = "custom"

@dataclass
class StorageEndpoint:
    """Storage endpoint configuration"""
    endpoint_id: str
    name: str
    provider: StorageProvider
    
    # Connection settings
    region: str = "us-east-1"
    endpoint_url: str = ""
    bucket_name: str = ""
    path_prefix: str = ""
    
    # Authentication
    access_key_id: str = ""
    secret_access_key: str = ""
    session_token: str = ""
    use_iam_role: bool = False
    
    # Configuration
    storage_class: StorageClass = StorageClass.STANDARD
    tier: StorageTier = StorageTier.HOT
    
    # Features
    versioning_enabled: bool = True
    encryption_enabled: bool = True
    encryption_type: EncryptionType = EncryptionType.AES_256
    compression_enabled: bool = False
    compression_type: CompressionType = CompressionType.GZIP
    
    # Performance settings
    multipart_threshold: int = 64 * 1024 * 1024  # 64MB
    multipart_chunksize: int = 16 * 1024 * 1024  # 16MB
    max_concurrency: int = 10
    timeout_seconds: int = 300
    
    # Cost optimization
    lifecycle_enabled: bool = True
    intelligent_tiering: bool = True
    cost_optimization: bool = True
    
    # Limits
    max_file_size_bytes: Optional[int] = None
    max_total_size_bytes: Optional[int] = None
    bandwidth_limit_mbps: Optional[int] = None
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    enabled: bool = True
    priority: int = 5  # 1-10, higher = preferred
    
    def get_connection_url(self) -> str:
        """Get connection URL"""
        if self.endpoint_url:
            return self.endpoint_url
        
        # Generate provider-specific URLs
        if self.provider == StorageProvider.AWS_S3:
            if self.region == "us-east-1":
                return f"https://s3.amazonaws.com"
            else:
                return f"https://s3.{self.region}.amazonaws.com"
        
        elif self.provider == StorageProvider.AZURE_BLOB:
            return f"https://{self.bucket_name}.blob.core.windows.net"
        
        elif self.provider == StorageProvider.GOOGLE_CLOUD:
            return "https://storage.googleapis.com"
        
        elif self.provider == StorageProvider.DIGITALOCEAN_SPACES:
            return f"https://{self.region}.digitaloceanspaces.com"
        
        elif self.provider == StorageProvider.CLOUDFLARE_R2:
            return f"https://{self.bucket_name}.r2.cloudflarestorage.com"
        
        return self.endpoint_url
    
    def get_full_path(self, object_key: str) -> str:
        """Get full object path"""
        if self.path_prefix:
            return f"{self.path_prefix.rstrip('/')}/{object_key.lstrip('/')}"
        return object_key
    
    def calculate_cost_estimate(self, size_bytes: int, operations: int = 0) -> Dict[str, float]:
        """Calculate estimated storage cost"""
        
        # Simplified cost calculation (provider-specific pricing would be more complex)
        cost_per_gb = {
            StorageClass.STANDARD: 0.023,
            StorageClass.STANDARD_IA: 0.0125,
            StorageClass.ONEZONE_IA: 0.01,
            StorageClass.GLACIER: 0.004,
            StorageClass.GLACIER_IR: 0.012,
            StorageClass.GLACIER_FLEXIBLE: 0.0036,
            StorageClass.GLACIER_DEEP: 0.00099
        }.get(self.storage_class, 0.023)
        
        size_gb = size_bytes / (1024 ** 3)
        storage_cost = size_gb * cost_per_gb
        
        # Request costs (simplified)
        request_cost = operations * 0.0004 / 1000  # $0.0004 per 1000 requests
        
        return {
            "storage_cost_monthly": storage_cost,
            "request_cost": request_cost,
            "total_cost": storage_cost + request_cost,
            "cost_per_gb": cost_per_gb
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test storage endpoint connection"""
        
        result = {
            "success": False,
            "latency_ms": 0,
            "available_space_bytes": 0,
            "permissions": [],
            "error": None
        }
        
        try:
            # Simulate connection test
            import random
            import time
            
            start_time = time.time()
            
            # Simulate network latency
            latency = random.uniform(10, 100)
            time.sleep(latency / 1000)  # Convert to seconds
            
            end_time = time.time()
            
            result.update({
                "success": True,
                "latency_ms": int((end_time - start_time) * 1000),
                "available_space_bytes": 1024 ** 4,  # 1TB
                "permissions": ["read", "write", "delete", "list"]
            })
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "endpoint_id": self.endpoint_id,
            "name": self.name,
            "provider": self.provider.value,
            "region": self.region,
            "endpoint_url": self.endpoint_url,
            "bucket_name": self.bucket_name,
            "path_prefix": self.path_prefix,
            "storage_class": self.storage_class.value,
            "tier": self.tier.value,
            "versioning_enabled": self.versioning_enabled,
            "encryption_enabled": self.encryption_enabled,
            "encryption_type": self.encryption_type.value,
            "compression_enabled": self.compression_enabled,
            "compression_type": self.compression_type.value,
            "multipart_threshold": self.multipart_threshold,
            "multipart_chunksize": self.multipart_chunksize,
            "max_concurrency": self.max_concurrency,
            "timeout_seconds": self.timeout_seconds,
            "lifecycle_enabled": self.lifecycle_enabled,
            "intelligent_tiering": self.intelligent_tiering,
            "cost_optimization": self.cost_optimization,
            "max_file_size_bytes": self.max_file_size_bytes,
            "max_total_size_bytes": self.max_total_size_bytes,
            "bandwidth_limit_mbps": self.bandwidth_limit_mbps,
            "created_date": self.created_date.isoformat(),
            "enabled": self.enabled,
            "priority": self.priority
        }

@dataclass
class LifecycleRule:
    """Storage lifecycle management rule"""
    rule_id: str
    name: str
    description: str
    
    # Matching criteria
    path_prefix: str = ""
    file_extensions: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    min_size_bytes: Optional[int] = None
    max_size_bytes: Optional[int] = None
    
    # Transition rules
    transitions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Expiration rules
    expiration_days: Optional[int] = None
    delete_incomplete_multipart_days: int = 7
    
    # Versioning
    noncurrent_version_expiration_days: Optional[int] = None
    noncurrent_version_transitions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    enabled: bool = True
    priority: int = 5
    created_date: datetime = field(default_factory=datetime.now)
    
    def matches_object(self, object_key: str, object_size: int = 0, 
                      object_tags: Dict[str, str] = None) -> bool:
        """Check if rule matches object"""
        
        # Check path prefix
        if self.path_prefix and not object_key.startswith(self.path_prefix):
            return False
        
        # Check file extensions
        if self.file_extensions:
            import os
            file_ext = os.path.splitext(object_key)[1].lower()
            if file_ext not in [ext.lower() for ext in self.file_extensions]:
                return False
        
        # Check size constraints
        if self.min_size_bytes is not None and object_size < self.min_size_bytes:
            return False
        
        if self.max_size_bytes is not None and object_size > self.max_size_bytes:
            return False
        
        # Check tags
        if self.tags and object_tags:
            for key, value in self.tags.items():
                if object_tags.get(key) != value:
                    return False
        
        return True
    
    def get_transition_for_age(self, age_days: int) -> Optional[Dict[str, Any]]:
        """Get transition rule for object age"""
        
        # Sort transitions by days (ascending)
        sorted_transitions = sorted(self.transitions, key=lambda x: x.get("days", 0))
        
        # Find the appropriate transition
        for transition in sorted_transitions:
            if age_days >= transition.get("days", 0):
                return transition
        
        return None
    
    def should_expire(self, age_days: int) -> bool:
        """Check if object should be expired"""
        return self.expiration_days is not None and age_days >= self.expiration_days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "path_prefix": self.path_prefix,
            "file_extensions": self.file_extensions,
            "tags": self.tags,
            "min_size_bytes": self.min_size_bytes,
            "max_size_bytes": self.max_size_bytes,
            "transitions": self.transitions,
            "expiration_days": self.expiration_days,
            "delete_incomplete_multipart_days": self.delete_incomplete_multipart_days,
            "noncurrent_version_expiration_days": self.noncurrent_version_expiration_days,
            "noncurrent_version_transitions": self.noncurrent_version_transitions,
            "enabled": self.enabled,
            "priority": self.priority,
            "created_date": self.created_date.isoformat()
        }

@dataclass
class BackupPolicy:
    """Backup policy configuration"""
    policy_id: str
    name: str
    description: str
    
    # Backup schedule
    enabled: bool = True
    backup_frequency: str = "daily"  # hourly, daily, weekly, monthly
    backup_time: str = "02:00"  # HH:MM format
    timezone: str = "UTC"
    
    # Retention policy
    retain_hourly: int = 24  # Keep hourly backups for 24 hours
    retain_daily: int = 30   # Keep daily backups for 30 days
    retain_weekly: int = 12  # Keep weekly backups for 12 weeks
    retain_monthly: int = 12 # Keep monthly backups for 12 months
    retain_yearly: int = 5   # Keep yearly backups for 5 years
    
    # Backup targets
    source_endpoints: List[str] = field(default_factory=list)
    backup_endpoints: List[str] = field(default_factory=list)
    
    # Backup options
    incremental_backup: bool = True
    compression_enabled: bool = True
    encryption_enabled: bool = True
    verify_backup: bool = True
    
    # Filters
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    max_file_size_bytes: Optional[int] = None
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    last_backup: Optional[datetime] = None
    backup_count: int = 0
    
    def should_backup_now(self) -> bool:
        """Check if backup should run now"""
        
        if not self.enabled:
            return False
        
        now = datetime.now()
        
        # If no previous backup, run now
        if not self.last_backup:
            return True
        
        # Check frequency
        if self.backup_frequency == "hourly":
            return (now - self.last_backup).total_seconds() >= 3600
        
        elif self.backup_frequency == "daily":
            return (now - self.last_backup).days >= 1
        
        elif self.backup_frequency == "weekly":
            return (now - self.last_backup).days >= 7
        
        elif self.backup_frequency == "monthly":
            return (now - self.last_backup).days >= 30
        
        return False
    
    def get_retention_policy(self) -> Dict[str, int]:
        """Get retention policy"""
        return {
            "hourly": self.retain_hourly,
            "daily": self.retain_daily,
            "weekly": self.retain_weekly,
            "monthly": self.retain_monthly,
            "yearly": self.retain_yearly
        }
    
    def calculate_backup_size_estimate(self, source_size_bytes: int) -> Dict[str, Any]:
        """Calculate estimated backup size"""
        
        # Base size
        backup_size = source_size_bytes
        
        # Compression reduction
        if self.compression_enabled:
            compression_ratio = 0.7  # 30% reduction
            backup_size = int(backup_size * compression_ratio)
        
        # Incremental backup reduction (after first backup)
        if self.incremental_backup and self.backup_count > 0:
            incremental_ratio = 0.1  # Only 10% of data changes typically
            backup_size = int(backup_size * incremental_ratio)
        
        # Encryption overhead
        if self.encryption_enabled:
            encryption_overhead = 1.02  # 2% overhead
            backup_size = int(backup_size * encryption_overhead)
        
        return {
            "estimated_size_bytes": backup_size,
            "compression_enabled": self.compression_enabled,
            "incremental": self.incremental_backup and self.backup_count > 0,
            "reduction_factor": backup_size / source_size_bytes if source_size_bytes > 0 else 1.0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "backup_frequency": self.backup_frequency,
            "backup_time": self.backup_time,
            "timezone": self.timezone,
            "retain_hourly": self.retain_hourly,
            "retain_daily": self.retain_daily,
            "retain_weekly": self.retain_weekly,
            "retain_monthly": self.retain_monthly,
            "retain_yearly": self.retain_yearly,
            "source_endpoints": self.source_endpoints,
            "backup_endpoints": self.backup_endpoints,
            "incremental_backup": self.incremental_backup,
            "compression_enabled": self.compression_enabled,
            "encryption_enabled": self.encryption_enabled,
            "verify_backup": self.verify_backup,
            "include_patterns": self.include_patterns,
            "exclude_patterns": self.exclude_patterns,
            "max_file_size_bytes": self.max_file_size_bytes,
            "created_date": self.created_date.isoformat(),
            "last_backup": self.last_backup.isoformat() if self.last_backup else None,
            "backup_count": self.backup_count
        }

@dataclass
class StoragePool:
    """Storage pool configuration for load balancing and redundancy"""
    pool_id: str
    name: str
    description: str
    
    # Pool members
    endpoints: List[str] = field(default_factory=list)  # endpoint IDs
    
    # Load balancing
    load_balancing_strategy: str = "round_robin"  # round_robin, least_used, weighted, performance
    weights: Dict[str, int] = field(default_factory=dict)  # endpoint_id -> weight
    
    # Replication
    replication_strategy: ReplicationStrategy = ReplicationStrategy.SINGLE_REGION
    min_replicas: int = 1
    max_replicas: int = 3
    
    # Health monitoring
    health_check_enabled: bool = True
    health_check_interval: int = 300  # seconds
    unhealthy_threshold: int = 3
    healthy_threshold: int = 2
    
    # Failover
    failover_enabled: bool = True
    auto_failover: bool = True
    failover_timeout: int = 30  # seconds
    
    # Performance
    preferred_regions: List[str] = field(default_factory=list)
    latency_threshold_ms: int = 1000
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    enabled: bool = True
    
    def get_available_endpoints(self, excluded: List[str] = None) -> List[str]:
        """Get available endpoints"""
        
        if excluded is None:
            excluded = []
        
        return [ep_id for ep_id in self.endpoints if ep_id not in excluded]
    
    def select_endpoint_for_write(self, storage_config) -> Optional[str]:
        """Select endpoint for write operation"""
        
        available_endpoints = self.get_available_endpoints()
        
        if not available_endpoints:
            return None
        
        if self.load_balancing_strategy == "round_robin":
            # Simple round-robin (would need state tracking in real implementation)
            return available_endpoints[0]
        
        elif self.load_balancing_strategy == "weighted":
            # Weighted selection based on weights
            total_weight = sum(self.weights.get(ep_id, 1) for ep_id in available_endpoints)
            
            if total_weight > 0:
                import random
                rand_weight = random.randint(1, total_weight)
                current_weight = 0
                
                for ep_id in available_endpoints:
                    current_weight += self.weights.get(ep_id, 1)
                    if rand_weight <= current_weight:
                        return ep_id
        
        elif self.load_balancing_strategy == "performance":
            # Select endpoint with best performance (would need metrics in real implementation)
            # For now, return first endpoint
            return available_endpoints[0]
        
        # Default: return first available
        return available_endpoints[0]
    
    def get_replication_endpoints(self, primary_endpoint: str, storage_config) -> List[str]:
        """Get endpoints for replication"""
        
        available_endpoints = self.get_available_endpoints([primary_endpoint])
        
        # Determine number of replicas needed
        replica_count = min(self.max_replicas - 1, len(available_endpoints))
        
        if replica_count <= 0:
            return []
        
        # Select based on replication strategy
        if self.replication_strategy == ReplicationStrategy.CROSS_REGION:
            # Prefer endpoints in different regions
            primary_region = None
            if primary_endpoint in storage_config.endpoints:
                primary_region = storage_config.endpoints[primary_endpoint].region
            
            # Sort by region diversity
            region_endpoints = {}
            for ep_id in available_endpoints:
                if ep_id in storage_config.endpoints:
                    region = storage_config.endpoints[ep_id].region
                    if region != primary_region:
                        if region not in region_endpoints:
                            region_endpoints[region] = []
                        region_endpoints[region].append(ep_id)
            
            # Select one from each region
            selected = []
            for region_eps in region_endpoints.values():
                if len(selected) < replica_count:
                    selected.append(region_eps[0])
            
            # Fill remaining with any available
            for ep_id in available_endpoints:
                if len(selected) < replica_count and ep_id not in selected:
                    selected.append(ep_id)
            
            return selected[:replica_count]
        
        else:
            # Simple selection
            return available_endpoints[:replica_count]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pool_id": self.pool_id,
            "name": self.name,
            "description": self.description,
            "endpoints": self.endpoints,
            "load_balancing_strategy": self.load_balancing_strategy,
            "weights": self.weights,
            "replication_strategy": self.replication_strategy.value,
            "min_replicas": self.min_replicas,
            "max_replicas": self.max_replicas,
            "health_check_enabled": self.health_check_enabled,
            "health_check_interval": self.health_check_interval,
            "unhealthy_threshold": self.unhealthy_threshold,
            "healthy_threshold": self.healthy_threshold,
            "failover_enabled": self.failover_enabled,
            "auto_failover": self.auto_failover,
            "failover_timeout": self.failover_timeout,
            "preferred_regions": self.preferred_regions,
            "latency_threshold_ms": self.latency_threshold_ms,
            "created_date": self.created_date.isoformat(),
            "enabled": self.enabled
        }

class StorageConfiguration:
    """Main storage configuration manager"""
    
    def __init__(self):
        """Initialize storage configuration"""
        # Data storage
        self.endpoints: Dict[str, StorageEndpoint] = {}
        self.pools: Dict[str, StoragePool] = {}
        self.lifecycle_rules: Dict[str, LifecycleRule] = {}
        self.backup_policies: Dict[str, BackupPolicy] = {}
        
        # Global settings
        self.storage_enabled = True
        self.auto_tiering = True
        self.intelligent_caching = True
        self.global_replication = True
        
        # Default settings
        self.default_settings = {
            "default_storage_class": "standard",
            "default_encryption": True,
            "default_compression": False,
            "default_versioning": True,
            "default_lifecycle": True,
            "default_backup": True
        }
        
        # Performance settings
        self.performance_settings = {
            "multipart_threshold": 64 * 1024 * 1024,  # 64MB
            "multipart_chunksize": 16 * 1024 * 1024,  # 16MB
            "max_concurrent_uploads": 10,
            "max_concurrent_downloads": 20,
            "connection_timeout": 300,
            "read_timeout": 300,
            "retry_attempts": 3,
            "retry_backoff_factor": 2.0
        }
        
        # Cost optimization
        self.cost_settings = {
            "intelligent_tiering": True,
            "lifecycle_management": True,
            "compression_optimization": True,
            "regional_optimization": True,
            "cost_monitoring": True,
            "budget_alerts": True,
            "cost_threshold_monthly": 1000.0
        }
        
        # Security settings
        self.security_settings = {
            "encryption_at_rest": True,
            "encryption_in_transit": True,
            "access_logging": True,
            "audit_trail": True,
            "secure_delete": True,
            "data_integrity_checks": True,
            "access_control": True
        }
        
        # Monitoring settings
        self.monitoring_settings = {
            "performance_monitoring": True,
            "capacity_monitoring": True,
            "cost_monitoring": True,
            "health_monitoring": True,
            "alert_on_failures": True,
            "alert_on_capacity": True,
            "alert_on_cost": True,
            "metrics_retention_days": 90
        }
        
        # Initialize default configuration
        self._initialize_default_configuration()
    
    def _initialize_default_configuration(self):
        """Initialize default storage configuration"""
        
        # Primary S3 endpoint
        s3_primary = StorageEndpoint(
            endpoint_id="s3_primary",
            name="AWS S3 Primary",
            provider=StorageProvider.AWS_S3,
            region="us-east-1",
            bucket_name="ainflue-primary",
            storage_class=StorageClass.STANDARD,
            tier=StorageTier.HOT,
            priority=9
        )
        
        # S3 backup endpoint
        s3_backup = StorageEndpoint(
            endpoint_id="s3_backup",
            name="AWS S3 Backup",
            provider=StorageProvider.AWS_S3,
            region="us-west-2",
            bucket_name="ainflue-backup",
            storage_class=StorageClass.STANDARD_IA,
            tier=StorageTier.WARM,
            priority=7
        )
        
        # Cloudflare R2 for cost optimization
        r2_endpoint = StorageEndpoint(
            endpoint_id="r2_archive",
            name="Cloudflare R2 Archive",
            provider=StorageProvider.CLOUDFLARE_R2,
            bucket_name="ainflue-archive",
            storage_class=StorageClass.STANDARD,
            tier=StorageTier.COOL,
            priority=6
        )
        
        # Local storage for temporary files
        local_endpoint = StorageEndpoint(
            endpoint_id="local_temp",
            name="Local Temporary Storage",
            provider=StorageProvider.LOCAL_FILESYSTEM,
            path_prefix="/tmp/ainflue",
            storage_class=StorageClass.STANDARD,
            tier=StorageTier.HOT,
            priority=5
        )
        
        # Add endpoints
        self.endpoints.update({
            s3_primary.endpoint_id: s3_primary,
            s3_backup.endpoint_id: s3_backup,
            r2_endpoint.endpoint_id: r2_endpoint,
            local_endpoint.endpoint_id: local_endpoint
        })
        
        # Create storage pools
        production_pool = StoragePool(
            pool_id="production",
            name="Production Storage Pool",
            description="Primary storage pool for production content",
            endpoints=["s3_primary", "s3_backup"],
            load_balancing_strategy="weighted",
            weights={"s3_primary": 80, "s3_backup": 20},
            replication_strategy=ReplicationStrategy.CROSS_REGION,
            min_replicas=1,
            max_replicas=2
        )
        
        archive_pool = StoragePool(
            pool_id="archive",
            name="Archive Storage Pool",
            description="Cost-optimized storage for archived content",
            endpoints=["r2_archive"],
            load_balancing_strategy="round_robin",
            replication_strategy=ReplicationStrategy.SINGLE_REGION,
            min_replicas=1,
            max_replicas=1
        )
        
        self.pools.update({
            production_pool.pool_id: production_pool,
            archive_pool.pool_id: archive_pool
        })
        
        # Create lifecycle rules
        video_lifecycle = LifecycleRule(
            rule_id="video_lifecycle",
            name="Video Content Lifecycle",
            description="Lifecycle management for video content",
            file_extensions=[".mp4", ".webm", ".mov", ".avi"],
            transitions=[
                {"days": 30, "storage_class": "standard_ia"},
                {"days": 90, "storage_class": "glacier"},
                {"days": 365, "storage_class": "glacier_deep"}
            ],
            expiration_days=2555,  # 7 years
            priority=9
        )
        
        image_lifecycle = LifecycleRule(
            rule_id="image_lifecycle",
            name="Image Content Lifecycle",
            description="Lifecycle management for image content",
            file_extensions=[".jpg", ".jpeg", ".png", ".webp"],
            transitions=[
                {"days": 60, "storage_class": "standard_ia"},
                {"days": 180, "storage_class": "glacier"}
            ],
            expiration_days=1825,  # 5 years
            priority=8
        )
        
        temp_cleanup = LifecycleRule(
            rule_id="temp_cleanup",
            name="Temporary File Cleanup",
            description="Cleanup temporary and processing files",
            path_prefix="temp/",
            expiration_days=7,
            priority=10
        )
        
        self.lifecycle_rules.update({
            video_lifecycle.rule_id: video_lifecycle,
            image_lifecycle.rule_id: image_lifecycle,
            temp_cleanup.rule_id: temp_cleanup
        })
        
        # Create backup policies
        daily_backup = BackupPolicy(
            policy_id="daily_backup",
            name="Daily Backup Policy",
            description="Daily backup of critical data",
            backup_frequency="daily",
            backup_time="02:00",
            source_endpoints=["s3_primary"],
            backup_endpoints=["s3_backup", "r2_archive"],
            incremental_backup=True,
            compression_enabled=True,
            encryption_enabled=True
        )
        
        weekly_archive = BackupPolicy(
            policy_id="weekly_archive",
            name="Weekly Archive Policy",
            description="Weekly full backup for archival",
            backup_frequency="weekly",
            backup_time="01:00",
            source_endpoints=["s3_primary", "s3_backup"],
            backup_endpoints=["r2_archive"],
            incremental_backup=False,
            compression_enabled=True,
            encryption_enabled=True,
            retain_weekly=52,  # 1 year
            retain_monthly=24  # 2 years
        )
        
        self.backup_policies.update({
            daily_backup.policy_id: daily_backup,
            weekly_archive.policy_id: weekly_archive
        })
    
    def create_storage_endpoint(self, endpoint_data: Dict[str, Any]) -> StorageEndpoint:
        """Create new storage endpoint"""
        
        endpoint = StorageEndpoint(
            endpoint_id=endpoint_data.get("endpoint_id", f"storage_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            name=endpoint_data["name"],
            provider=StorageProvider(endpoint_data["provider"]),
            region=endpoint_data.get("region", "us-east-1"),
            bucket_name=endpoint_data.get("bucket_name", ""),
            path_prefix=endpoint_data.get("path_prefix", ""),
            storage_class=StorageClass(endpoint_data.get("storage_class", "standard")),
            tier=StorageTier(endpoint_data.get("tier", "hot")),
            encryption_enabled=endpoint_data.get("encryption_enabled", True),
            compression_enabled=endpoint_data.get("compression_enabled", False),
            priority=endpoint_data.get("priority", 5)
        )
        
        self.endpoints[endpoint.endpoint_id] = endpoint
        return endpoint
    
    def get_optimal_storage_endpoint(self, file_size: int, access_pattern: AccessPattern,
                                   content_type: str = "", region: str = "") -> Optional[StorageEndpoint]:
        """Get optimal storage endpoint based on requirements"""
        
        # Filter available endpoints
        available_endpoints = [ep for ep in self.endpoints.values() if ep.enabled]
        
        if not available_endpoints:
            return None
        
        # Score endpoints based on criteria
        endpoint_scores = []
        
        for endpoint in available_endpoints:
            score = 0.0
            
            # Base priority score
            score += endpoint.priority
            
            # Size compatibility
            if endpoint.max_file_size_bytes and file_size > endpoint.max_file_size_bytes:
                continue  # Skip if file too large
            
            # Access pattern optimization
            if access_pattern == AccessPattern.FREQUENT and endpoint.tier == StorageTier.HOT:
                score += 5.0
            elif access_pattern == AccessPattern.OCCASIONAL and endpoint.tier == StorageTier.WARM:
                score += 3.0
            elif access_pattern == AccessPattern.RARE and endpoint.tier == StorageTier.COOL:
                score += 3.0
            elif access_pattern == AccessPattern.ARCHIVE and endpoint.tier == StorageTier.COLD:
                score += 5.0
            
            # Region preference
            if region and endpoint.region == region:
                score += 2.0
            
            # Cost optimization for large files
            if file_size > 100 * 1024 * 1024:  # 100MB+
                if endpoint.storage_class in [StorageClass.STANDARD_IA, StorageClass.GLACIER]:
                    score += 1.0
            
            endpoint_scores.append((endpoint, score))
        
        # Sort by score (highest first)
        endpoint_scores.sort(key=lambda x: x[1], reverse=True)
        
        return endpoint_scores[0][0] if endpoint_scores else None
    
    def store_file(self, file_path: str, content_type: str = "", 
                  storage_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Store file with optimal configuration"""
        
        if storage_options is None:
            storage_options = {}
        
        result = {
            "success": False,
            "stored_locations": [],
            "primary_endpoint": None,
            "backup_endpoints": [],
            "storage_cost_estimate": 0.0,
            "error": None
        }
        
        try:
            # Get file information
            import os
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            access_pattern = AccessPattern(storage_options.get("access_pattern", "unknown"))
            region = storage_options.get("region", "")
            
            # Get optimal endpoint
            primary_endpoint = self.get_optimal_storage_endpoint(file_size, access_pattern, content_type, region)
            
            if not primary_endpoint:
                result["error"] = "No suitable storage endpoint found"
                return result
            
            result["primary_endpoint"] = primary_endpoint.endpoint_id
            result["stored_locations"].append(primary_endpoint.endpoint_id)
            
            # Calculate cost estimate
            cost_estimate = primary_endpoint.calculate_cost_estimate(file_size)
            result["storage_cost_estimate"] = cost_estimate["total_cost"]
            
            # Handle replication if configured
            replication_strategy = storage_options.get("replication", "none")
            
            if replication_strategy != "none":
                # Find backup endpoints
                backup_endpoints = []
                
                for endpoint in self.endpoints.values():
                    if (endpoint.enabled and 
                        endpoint.endpoint_id != primary_endpoint.endpoint_id and
                        endpoint.region != primary_endpoint.region):
                        backup_endpoints.append(endpoint.endpoint_id)
                
                if backup_endpoints:
                    result["backup_endpoints"] = backup_endpoints[:2]  # Max 2 backups
                    result["stored_locations"].extend(result["backup_endpoints"])
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_lifecycle_actions(self, object_key: str, object_age_days: int,
                             object_size: int = 0, object_tags: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """Get lifecycle actions for object"""
        
        actions = []
        
        # Get matching lifecycle rules
        matching_rules = []
        for rule in self.lifecycle_rules.values():
            if rule.enabled and rule.matches_object(object_key, object_size, object_tags):
                matching_rules.append(rule)
        
        # Sort by priority (highest first)
        matching_rules.sort(key=lambda x: x.priority, reverse=True)
        
        # Apply rules in priority order
        for rule in matching_rules:
            # Check for transition
            transition = rule.get_transition_for_age(object_age_days)
            if transition:
                actions.append({
                    "action": "transition",
                    "rule_id": rule.rule_id,
                    "storage_class": transition["storage_class"],
                    "reason": f"Object age {object_age_days} days meets transition rule"
                })
            
            # Check for expiration
            if rule.should_expire(object_age_days):
                actions.append({
                    "action": "delete",
                    "rule_id": rule.rule_id,
                    "reason": f"Object age {object_age_days} days meets expiration rule"
                })
        
        return actions
    
    def run_backup_policies(self) -> Dict[str, Any]:
        """Run scheduled backup policies"""
        
        result = {
            "success": False,
            "policies_executed": 0,
            "policies_skipped": 0,
            "total_backup_size": 0,
            "results": {},
            "error": None
        }
        
        try:
            for policy in self.backup_policies.values():
                policy_result = {
                    "executed": False,
                    "skipped_reason": None,
                    "backup_size": 0,
                    "duration_seconds": 0
                }
                
                if policy.should_backup_now():
                    # Simulate backup execution
                    import time
                    start_time = time.time()
                    
                    # Calculate backup size
                    source_size = 1024 * 1024 * 1024  # 1GB placeholder
                    backup_estimate = policy.calculate_backup_size_estimate(source_size)
                    
                    # Update policy
                    policy.last_backup = datetime.now()
                    policy.backup_count += 1
                    
                    end_time = time.time()
                    
                    policy_result.update({
                        "executed": True,
                        "backup_size": backup_estimate["estimated_size_bytes"],
                        "duration_seconds": int(end_time - start_time)
                    })
                    
                    result["policies_executed"] += 1
                    result["total_backup_size"] += backup_estimate["estimated_size_bytes"]
                
                else:
                    policy_result["skipped_reason"] = "Not scheduled to run now"
                    result["policies_skipped"] += 1
                
                result["results"][policy.policy_id] = policy_result
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        
        # Count by provider
        provider_count = {}
        for endpoint in self.endpoints.values():
            provider = endpoint.provider.value
            provider_count[provider] = provider_count.get(provider, 0) + 1
        
        # Count by tier
        tier_count = {}
        for endpoint in self.endpoints.values():
            tier = endpoint.tier.value
            tier_count[tier] = tier_count.get(tier, 0) + 1
        
        # Pool statistics
        pool_endpoints = {}
        for pool in self.pools.values():
            pool_endpoints[pool.pool_id] = len(pool.endpoints)
        
        return {
            "endpoints": {
                "total": len(self.endpoints),
                "enabled": len([ep for ep in self.endpoints.values() if ep.enabled]),
                "by_provider": provider_count,
                "by_tier": tier_count
            },
            "pools": {
                "total": len(self.pools),
                "enabled": len([p for p in self.pools.values() if p.enabled]),
                "endpoints_per_pool": pool_endpoints
            },
            "lifecycle_rules": {
                "total": len(self.lifecycle_rules),
                "enabled": len([r for r in self.lifecycle_rules.values() if r.enabled])
            },
            "backup_policies": {
                "total": len(self.backup_policies),
                "enabled": len([p for p in self.backup_policies.values() if p.enabled])
            }
        }
    
    def test_all_endpoints(self) -> Dict[str, Any]:
        """Test all storage endpoints"""
        
        results = {}
        
        for endpoint_id, endpoint in self.endpoints.items():
            if endpoint.enabled:
                test_result = endpoint.test_connection()
                results[endpoint_id] = test_result
        
        # Calculate summary
        total_tested = len(results)
        successful = len([r for r in results.values() if r["success"]])
        
        return {
            "summary": {
                "total_tested": total_tested,
                "successful": successful,
                "failed": total_tested - successful,
                "success_rate": (successful / total_tested * 100) if total_tested > 0 else 0
            },
            "results": results
        }
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete storage configuration"""
        return {
            "storage_statistics": self.get_storage_statistics(),
            "endpoints": {ep_id: ep.to_dict() for ep_id, ep in self.endpoints.items()},
            "pools": {pool_id: pool.to_dict() for pool_id, pool in self.pools.items()},
            "lifecycle_rules": {rule_id: rule.to_dict() for rule_id, rule in self.lifecycle_rules.items()},
            "backup_policies": {policy_id: policy.to_dict() for policy_id, policy in self.backup_policies.items()},
            "global_settings": {
                "storage_enabled": self.storage_enabled,
                "auto_tiering": self.auto_tiering,
                "intelligent_caching": self.intelligent_caching,
                "global_replication": self.global_replication
            },
            "default_settings": self.default_settings,
            "performance_settings": self.performance_settings,
            "cost_settings": self.cost_settings,
            "security_settings": self.security_settings,
            "monitoring_settings": self.monitoring_settings
        }

# Global storage configuration instance
storage_config = StorageConfiguration()

# Export main classes
__all__ = [
    "StorageConfiguration",
    "StorageProvider",
    "StorageTier",
    "StorageClass",
    "AccessPattern",
    "CompressionType",
    "EncryptionType",
    "ReplicationStrategy",
    "StorageEndpoint",
    "LifecycleRule",
    "BackupPolicy",
    "StoragePool",
    "storage_config"
]
