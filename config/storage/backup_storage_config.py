"""Backup Storage Configuration for IA-Influencer Agent Platform
=============================================================

Professional backup and disaster recovery storage configuration.

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
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

class BackupType(Enum):
    """
Types of backup operations."""

    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"

class BackupStorage(Enum):
    """Backup storage locations."""

    LOCAL = "local"
    S3 = "s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    EXTERNAL_SFP = "external_sftp"

class RetentionPolicy(Enum):
    """Backup retention policies."""

    DAILY_7 = "daily_7_days"
    WEEKLY_4 = "weekly_4_weeks"
    MONTHLY_12 = "monthly_12_months"
    YEARLY_7 = "yearly_7_years"
    CUSTOM = "custom"

@dataclass
class BackupSchedule:
    """Backup schedule configuration."""
    
    name: str
    backup_type: BackupType
    frequency: str  # cron expression
    retention_policy: RetentionPolicy
    enabled: bool = True
    priority: int = 5  # 1-10, higher is more important
    
    # Data selection
    include_paths: List[str] = None
    exclude_paths: List[str] = None
    include_databases: List[str] = None
    
    # Storage settings
    primary_storage: BackupStorage = BackupStorage.S3
    secondary_storage: Optional[BackupStorage] = None
    compression_enabled: bool = True
    encryption_enabled: bool = True
    
    def __post_init__(self):
        if self.include_paths is None:
            self.include_paths = []
        if self.exclude_paths is None:
            self.exclude_paths = []
        if self.include_databases is None:
            self.include_databases = []

@dataclass
class BackupDestination:
    """
Backup destination configuration."""
    
    storage_type: BackupStorage
    location: str
    credentials: Dict[str, str]
    
    # Capacity settings
    max_size_gb: Optional[float] = None
    current_usage_gb: float = 0.0
    
    # Performance settings
    concurrent_uploads: int = 3
    chunk_size_mb: int = 64
    retry_attempts: int = 3
    
    # Security settings
    encryption_key: Optional[str] = None
    access_permissions: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.access_permissions is None:
            self.access_permissions = {
                'read': ['backup_service'],
                'write': ['backup_service'],
                'delete': ['admin']
            }

@dataclass
class BackupStorageConfig:
    """
    Comprehensive backup storage configuration for IA-Influencer Agent platform.
    Provides enterprise-grade backup and disaster recovery capabilities.
    """
    
    # Global backup settings
    enable_backups: bool = True
    backup_base_path: str = os.getenv('BACKUP_BASE_PATH', '/backups/ia-influencer')
    
    # Backup schedules
    schedules: Dict[str, BackupSchedule] = None
    
    # Backup destinations
    destinations: Dict[str, BackupDestination] = None
    
    # Retention settings
    default_retention_days: int = 90
    max_backup_age_days: int = 2555  # 7 years
    cleanup_frequency: str = "0 2 * * *"  # Daily at 2 AM
    
    # Performance settings
    max_concurrent_backups: int = 2
    backup_bandwidth_limit_mbps: Optional[int] = None
    enable_deduplication: bool = True
    
    # Monitoring settings
    enable_backup_monitoring: bool = True
    alert_on_failure: bool = True
    alert_on_quota_exceeded: bool = True
    health_check_interval: int = 3600  # 1 hour
    
    # Security settings
    global_encryption_enabled: bool = True
    encryption_algorithm: str = 'AES-256'
    backup_integrity_checks: bool = True
    
    # Disaster recovery settings
    enable_cross_region_replication: bool = True
    rpo_target_hours: int = 24  # Recovery Point Objective
    rto_target_hours: int = 4   # Recovery Time Objective
    
    def __post_init__(self):
        """Initialize backup configurations if not provided."""
        if self.schedules is None:
            self.schedules = self._get_default_schedules()
        
        if self.destinations is None:
            self.destinations = self._get_default_destinations()
    
    def _get_default_schedules(self) -> Dict[str, BackupSchedule]:
        """
Default backup schedule configurations."""
        return {
            'database_daily': BackupSchedule(
                name="Database Daily Backup",
                backup_type=BackupType.FULL,
                frequency="0 2 * * *",  # Daily at 2 AM
                retention_policy=RetentionPolicy.DAILY_7,
                priority=9,
                include_databases=['postgresql', 'redis', 'mongodb'],
                primary_storage=BackupStorage.S3,
                secondary_storage=BackupStorage.AZURE_BLOB
            ),
            'files_daily': BackupSchedule(
                name="Files Daily Backup",
                backup_type=BackupType.INCREMENTAL,
                frequency="0 3 * * *",  # Daily at 3 AM
                retention_policy=RetentionPolicy.DAILY_7,
                priority=8,
                include_paths=[
                    '/var/lib/ia-influencer/audio',
                    '/var/lib/ia-influencer/video',
                    '/var/lib/ia-influencer/images',
                    '/var/lib/ia-influencer/documents'
                ],
                exclude_paths=[
                    '/var/lib/ia-influencer/temp',
                    '/var/lib/ia-influencer/cache'
                ],
                primary_storage=BackupStorage.S3
            ),
            'config_daily': BackupSchedule(
                name="Configuration Daily Backup",
                backup_type=BackupType.FULL,
                frequency="0 1 * * *",  # Daily at 1 AM
                retention_policy=RetentionPolicy.WEEKLY_4,
                priority=10,
                include_paths=[
                    '/etc/ia-influencer',
                    '/var/lib/ia-influencer/config',
                    '/var/lib/ia-influencer/models'
                ],
                primary_storage=BackupStorage.S3,
                secondary_storage=BackupStorage.GOOGLE_CLOUD
            ),
            'ml_models_weekly': BackupSchedule(
                name="ML Models Weekly Backup",
                backup_type=BackupType.FULL,
                frequency="0 4 * * 0",  # Weekly on Sunday at 4 AM
                retention_policy=RetentionPolicy.MONTHLY_12,
                priority=7,
                include_paths=[
                    '/var/lib/ia-influencer/models',
                    '/var/lib/ia-influencer/fingerprints'
                ],
                primary_storage=BackupStorage.S3
            ),
            'user_data_hourly': BackupSchedule(
                name="User Data Hourly Backup",
                backup_type=BackupType.INCREMENTAL,
                frequency="0 * * * *",  # Every hour
                retention_policy=RetentionPolicy.DAILY_7,
                priority=8,
                include_paths=[
                    '/var/lib/ia-influencer/uploads',
                    '/var/lib/ia-influencer/processed'
                ],
                primary_storage=BackupStorage.S3
            ),
            'full_system_monthly': BackupSchedule(
                name="Full System Monthly Backup",
                backup_type=BackupType.FULL,
                frequency="0 5 1 * *",  # Monthly on 1st at 5 AM
                retention_policy=RetentionPolicy.YEARLY_7,
                priority=6,
                include_paths=['/var/lib/ia-influencer'],
                exclude_paths=[
                    '/var/lib/ia-influencer/temp',
                    '/var/lib/ia-influencer/cache',
                    '/var/lib/ia-influencer/logs'
                ],
                include_databases=['postgresql', 'redis', 'mongodb'],
                primary_storage=BackupStorage.S3,
                secondary_storage=BackupStorage.AZURE_BLOB
            )
        }
    
    def _get_default_destinations(self) -> Dict[str, BackupDestination]:
        """Default backup destination configurations."""
        env = os.getenv('ENVIRONMENT', 'development')
        
        return {
            's3_primary': BackupDestination(
                storage_type=BackupStorage.S3,
                location=f"s3://ia-influencer-backups-{env}/primary",
                credentials={
                    'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID', ''),
                    'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY', ''),
                    'region': os.getenv('AWS_DEFAULT_REGION', 'eu-central-1')
                },
                max_size_gb=1000.0,
                concurrent_uploads=5,
                chunk_size_mb=128,
                encryption_key=os.getenv('BACKUP_ENCRYPTION_KEY')
            ),
            'azure_secondary': BackupDestination(
                storage_type=BackupStorage.AZURE_BLOB,
                location=f"azure://iainfluencerbackups{env}/secondary",
                credentials={
                    'account_name': os.getenv('AZURE_STORAGE_ACCOUNT_NAME', ''),
                    'account_key': os.getenv('AZURE_STORAGE_ACCOUNT_KEY', ''),
                    'connection_string': os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
                },
                max_size_gb=500.0,
                concurrent_uploads=3,
                chunk_size_mb=64
            ),
            'gcs_archive': BackupDestination(
                storage_type=BackupStorage.GOOGLE_CLOUD,
                location=f"gs://ia-influencer-archive-{env}/longterm",
                credentials={
                    'project_id': os.getenv('GCP_PROJECT_ID', ''),
                    'credentials_json': os.getenv('GCP_CREDENTIALS_JSON', '')
                },
                max_size_gb=2000.0,
                concurrent_uploads=2,
                chunk_size_mb=256
            ),
            'local_emergency': BackupDestination(
                storage_type=BackupStorage.LOCAL,
                location=f"{self.backup_base_path}/emergency",
                credentials={},
                max_size_gb=100.0,
                concurrent_uploads=1,
                chunk_size_mb=32
            )
        }
    
    def get_active_schedules(self) -> Dict[str, BackupSchedule]:
        """Get all enabled backup schedules."""
        return {name: schedule for name, schedule in self.schedules.items() 
                if schedule.enabled}
    
    def get_schedule_by_priority(self) -> List[BackupSchedule]:
        """
Get backup schedules sorted by priority (highest first)."""
        active_schedules = list(self.get_active_schedules().values())
        return sorted(active_schedules, key=lambda x: x.priority, reverse=True)
    
    def get_destination_by_storage_type(self, storage_type: BackupStorage) -> Optional[BackupDestination]:
        """
Get first destination of specified storage type."""
        for destination in self.destinations.values():
            if destination.storage_type == storage_type:
                return destination
        return None
    
    def validate_configuration(self) -> bool:
        """
Validate backup configuration."""
        try:
            # Check if at least one schedule is enabled
            active_schedules = self.get_active_schedules()
            if not active_schedules:
                print("No active backup schedules configured")
                return False
            
            # Validate destinations
            for name, destination in self.destinations.items():
                if destination.storage_type in [BackupStorage.S3, BackupStorage.AZURE_BLOB, BackupStorage.GOOGLE_CLOUD]:
                    if not destination.credentials:
                        print(f"Missing credentials for destination: {name}")
                        return False
                
                # Check local paths
                if destination.storage_type == BackupStorage.LOCAL:
                    if not os.path.exists(os.path.dirname(destination.location)):
                        try:
                            os.makedirs(destination.location, exist_ok=True)
                        except OSError:
                            print(f"Cannot create backup directory: {destination.location}")
                            return False
            
            return True
        except Exception as e:
            print(f"Backup configuration validation failed: {e}")
            return False
    
    def get_retention_days(self, policy: RetentionPolicy) -> int:
        """Get number of retention days for policy."""
        retention_mapping = {
            RetentionPolicy.DAILY_7: 7,
            RetentionPolicy.WEEKLY_4: 28,
            RetentionPolicy.MONTHLY_12: 365,
            RetentionPolicy.YEARLY_7: 2555,
            RetentionPolicy.CUSTOM: self.default_retention_days
        }
        return retention_mapping.get(policy, self.default_retention_days)
    
    def calculate_backup_size_estimate(self, schedule_name: str) -> float:
        """
Estimate backup size in GB for a schedule."""
        schedule = self.schedules.get(schedule_name)
        if not schedule:
            return 0.0
        
        total_size = 0.0
        
        # Estimate file system paths
        for path in schedule.include_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.exists(file_path):
                            total_size += os.path.getsize(file_path)
        
        # Convert to GB
        size_gb = total_size / (1024**3)
        
        # Apply compression factor if enabled
        if schedule.compression_enabled:
            size_gb *= 0.6  # Assume 40% compression
        
        return round(size_gb, 2)
    
    def get_next_backup_times(self) -> Dict[str, datetime]:
        """
Get next scheduled backup times for all active schedules."""
        from croniter import croniter
        
        next_times = {}
        now = datetime.now()
        
        for name, schedule in self.get_active_schedules().items():
            try:
                cron = croniter(schedule.frequency, now)
                next_time = cron.get_next(datetime)
                next_times[name] = next_time
            except Exception as e:
                print(f"Invalid cron expression for {name}: {schedule.frequency}")
                continue
        
        return next_times
    
    def get_storage_usage_summary(self) -> Dict[str, Dict[str, float]]:
        """Get storage usage summary for all destinations."""
        summary = {}
        
        for name, destination in self.destinations.items():
            usage_pct = 0.0
            if destination.max_size_gb and destination.max_size_gb > 0:
                usage_pct = (destination.current_usage_gb / destination.max_size_gb) * 100
            
            summary[name] = {
                'current_usage_gb': destination.current_usage_gb,
                'max_size_gb': destination.max_size_gb or 0,
                'usage_percentage': round(usage_pct, 1),
                'available_gb': (destination.max_size_gb or 0) - destination.current_usage_gb,
                'storage_type': destination.storage_type.value
            }
        
        return summary
    
    def export_configuration(self) -> Dict[str, Any]:
        """
Export backup configuration to JSON-serializable format."""
        return {
            'enable_backups': self.enable_backups,
            'backup_base_path': self.backup_base_path,
            'default_retention_days': self.default_retention_days,
            'max_backup_age_days': self.max_backup_age_days,
            'max_concurrent_backups': self.max_concurrent_backups,
            'enable_deduplication': self.enable_deduplication,
            'global_encryption_enabled': self.global_encryption_enabled,
            'encryption_algorithm': self.encryption_algorithm,
            'enable_cross_region_replication': self.enable_cross_region_replication,
            'rpo_target_hours': self.rpo_target_hours,
            'rto_target_hours': self.rto_target_hours,
            'active_schedules': len(self.get_active_schedules()),
            'total_destinations': len(self.destinations)
        }

# Global backup storage configuration instance
backup_storage_config = BackupStorageConfig()
