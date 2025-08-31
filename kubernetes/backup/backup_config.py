"""Backup Configuration Management for IA Influencer Agent Platform.

Provides comprehensive configuration management for all backup operations
including storage, encryption, scheduling, and monitoring settings.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution is strictly prohibited and will result
in immediate legal action under German and international law.
"""
import os
import yaml
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum

from ...core.config import BaseConfig
from ...core.exceptions import ConfigurationError


class StorageBackend(Enum):
    """Storage backend types."""    LOCAL_FILESYSTEM = "local_filesystem"
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud_storage"
    SFTP = "sftp"
    FTP = "ftp"


class CompressionAlgorithm(Enum):
    """Compression algorithm types."""    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"
    ZSTD = "zstd"
    LZ4 = "lz4"


@dataclass
class StorageConfig:
    """Storage configuration."""    backend: StorageBackend
    connection_params: Dict[str, Any] = field(default_factory=dict)
    path_prefix: str = "ia_influencer_backups"
    max_storage_gb: int = 1000
    retention_days: int = 30
    redundancy_enabled: bool = True
    redundancy_locations: List[str] = field(default_factory=list)
    compression: CompressionAlgorithm = CompressionAlgorithm.GZIP
    compression_level: int = 6


@dataclass
class EncryptionConfig:
    """Encryption configuration."""    enabled: bool = True
    algorithm: str = "AES-256-GCM"
    key_derivation_method: str = "PBKDF2"
    key_rotation_enabled: bool = True
    key_rotation_interval_days: int = 90
    master_key_path: Optional[str] = None
    key_storage_backend: str = "secure_vault"
    integrity_verification: bool = True


@dataclass
class SchedulingConfig:
    """Backup scheduling configuration."""    enabled: bool = True
    full_backup_cron: str = "0 2 * * 0"  # Weekly at 2 AM Sunday
    incremental_backup_cron: str = "0 2 * * 1-6"  # Daily at 2 AM Mon-Sat
    content_backup_cron: str = "0 4 * * *"  # Daily at 4 AM
    user_backup_cron: str = "0 6 * * *"  # Daily at 6 AM
    system_backup_cron: str = "0 1 * * *"  # Daily at 1 AM
    timezone: str = "UTC"
    max_concurrent_jobs: int = 3
    job_timeout_hours: int = 24


@dataclass
class MonitoringConfig:
    """Backup monitoring configuration."""    enabled: bool = True
    metrics_enabled: bool = True
    alerting_enabled: bool = True
    prometheus_endpoint: Optional[str] = None
    grafana_dashboard_enabled: bool = True
    alert_webhooks: List[str] = field(default_factory=list)
    email_notifications: List[str] = field(default_factory=list)
    slack_webhook: Optional[str] = None
    backup_failure_alert_threshold: int = 1
    storage_usage_alert_threshold: float = 0.85


@dataclass
class ValidationConfig:
    """Backup validation configuration."""    enabled: bool = True
    integrity_checks: bool = True
    checksum_algorithm: str = "SHA-256"
    deep_validation: bool = True
    restoration_testing: bool = False
    restoration_test_frequency_days: int = 7
    validation_timeout_minutes: int = 60


@dataclass
class RecoveryConfig:
    """Recovery configuration."""    point_in_time_enabled: bool = True
    rollback_enabled: bool = True
    emergency_recovery_enabled: bool = True
    recovery_verification: bool = True
    parallel_recovery: bool = True
    max_parallel_streams: int = 4
    recovery_timeout_hours: int = 48


@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""    parallel_backups: bool = True
    max_parallel_operations: int = 3
    chunk_size_mb: int = 64
    memory_limit_gb: int = 8
    network_timeout_seconds: int = 300
    retry_attempts: int = 3
    retry_delay_seconds: int = 30
    bandwidth_limit_mbps: Optional[int] = None


class BackupConfig(BaseConfig):
    """    Comprehensive backup configuration management.
    
    Manages all backup-related configurations including storage, encryption,
    scheduling, monitoring, validation, and performance settings.
    """
    def __init__(self, config_path: Optional[str] = None):
        """        Initialize backup configuration.
        
        Args:
            config_path: Path to configuration file
        """        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or self._get_default_config_path()
        
        # Configuration sections
        self.storage: StorageConfig = StorageConfig(StorageBackend.LOCAL_FILESYSTEM)
        self.encryption: EncryptionConfig = EncryptionConfig()
        self.scheduling: SchedulingConfig = SchedulingConfig()
        self.monitoring: MonitoringConfig = MonitoringConfig()
        self.validation: ValidationConfig = ValidationConfig()
        self.recovery: RecoveryConfig = RecoveryConfig()
        self.performance: PerformanceConfig = PerformanceConfig()
        
        # Load configuration
        self._load_configuration()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""        return os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "config",
            "backup_config.yml"
        )

    def _load_configuration(self) -> None:
        """Load configuration from file."""        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    if self.config_path.endswith('.yml') or self.config_path.endswith('.yaml'):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                self._apply_configuration(config_data)
                self.logger.info(f"Backup configuration loaded from {self.config_path}")
            else:
                self.logger.warning(f"Configuration file not found: {self.config_path}")
                self._create_default_configuration()
                
        except Exception as e:
            self.logger.error(f"Failed to load backup configuration: {e}")
            raise ConfigurationError(f"Configuration loading failed: {e}")

    def _apply_configuration(self, config_data: Dict[str, Any]) -> None:
        """Apply configuration data to settings."""        # Storage configuration
        if "storage" in config_data:
            storage_data = config_data["storage"]
            self.storage = StorageConfig(
                backend=StorageBackend(storage_data.get("backend", "local_filesystem")),
                connection_params=storage_data.get("connection_params", {}),
                path_prefix=storage_data.get("path_prefix", "ia_influencer_backups"),
                max_storage_gb=storage_data.get("max_storage_gb", 1000),
                retention_days=storage_data.get("retention_days", 30),
                redundancy_enabled=storage_data.get("redundancy_enabled", True),
                redundancy_locations=storage_data.get("redundancy_locations", []),
                compression=CompressionAlgorithm(storage_data.get("compression", "gzip")),
                compression_level=storage_data.get("compression_level", 6)
            )
        
        # Encryption configuration
        if "encryption" in config_data:
            enc_data = config_data["encryption"]
            self.encryption = EncryptionConfig(
                enabled=enc_data.get("enabled", True),
                algorithm=enc_data.get("algorithm", "AES-256-GCM"),
                key_derivation_method=enc_data.get("key_derivation_method", "PBKDF2"),
                key_rotation_enabled=enc_data.get("key_rotation_enabled", True),
                key_rotation_interval_days=enc_data.get("key_rotation_interval_days", 90),
                master_key_path=enc_data.get("master_key_path"),
                key_storage_backend=enc_data.get("key_storage_backend", "secure_vault"),
                integrity_verification=enc_data.get("integrity_verification", True)
            )
        
        # Scheduling configuration
        if "scheduling" in config_data:
            sched_data = config_data["scheduling"]
            self.scheduling = SchedulingConfig(
                enabled=sched_data.get("enabled", True),
                full_backup_cron=sched_data.get("full_backup_cron", "0 2 * * 0"),
                incremental_backup_cron=sched_data.get("incremental_backup_cron", "0 2 * * 1-6"),
                content_backup_cron=sched_data.get("content_backup_cron", "0 4 * * *"),
                user_backup_cron=sched_data.get("user_backup_cron", "0 6 * * *"),
                system_backup_cron=sched_data.get("system_backup_cron", "0 1 * * *"),
                timezone=sched_data.get("timezone", "UTC"),
                max_concurrent_jobs=sched_data.get("max_concurrent_jobs", 3),
                job_timeout_hours=sched_data.get("job_timeout_hours", 24)
            )
        
        # Monitoring configuration
        if "monitoring" in config_data:
            mon_data = config_data["monitoring"]
            self.monitoring = MonitoringConfig(
                enabled=mon_data.get("enabled", True),
                metrics_enabled=mon_data.get("metrics_enabled", True),
                alerting_enabled=mon_data.get("alerting_enabled", True),
                prometheus_endpoint=mon_data.get("prometheus_endpoint"),
                grafana_dashboard_enabled=mon_data.get("grafana_dashboard_enabled", True),
                alert_webhooks=mon_data.get("alert_webhooks", []),
                email_notifications=mon_data.get("email_notifications", []),
                slack_webhook=mon_data.get("slack_webhook"),
                backup_failure_alert_threshold=mon_data.get("backup_failure_alert_threshold", 1),
                storage_usage_alert_threshold=mon_data.get("storage_usage_alert_threshold", 0.85)
            )
        
        # Validation configuration
        if "validation" in config_data:
            val_data = config_data["validation"]
            self.validation = ValidationConfig(
                enabled=val_data.get("enabled", True),
                integrity_checks=val_data.get("integrity_checks", True),
                checksum_algorithm=val_data.get("checksum_algorithm", "SHA-256"),
                deep_validation=val_data.get("deep_validation", True),
                restoration_testing=val_data.get("restoration_testing", False),
                restoration_test_frequency_days=val_data.get("restoration_test_frequency_days", 7),
                validation_timeout_minutes=val_data.get("validation_timeout_minutes", 60)
            )
        
        # Recovery configuration
        if "recovery" in config_data:
            rec_data = config_data["recovery"]
            self.recovery = RecoveryConfig(
                point_in_time_enabled=rec_data.get("point_in_time_enabled", True),
                rollback_enabled=rec_data.get("rollback_enabled", True),
                emergency_recovery_enabled=rec_data.get("emergency_recovery_enabled", True),
                recovery_verification=rec_data.get("recovery_verification", True),
                parallel_recovery=rec_data.get("parallel_recovery", True),
                max_parallel_streams=rec_data.get("max_parallel_streams", 4),
                recovery_timeout_hours=rec_data.get("recovery_timeout_hours", 48)
            )
        
        # Performance configuration
        if "performance" in config_data:
            perf_data = config_data["performance"]
            self.performance = PerformanceConfig(
                parallel_backups=perf_data.get("parallel_backups", True),
                max_parallel_operations=perf_data.get("max_parallel_operations", 3),
                chunk_size_mb=perf_data.get("chunk_size_mb", 64),
                memory_limit_gb=perf_data.get("memory_limit_gb", 8),
                network_timeout_seconds=perf_data.get("network_timeout_seconds", 300),
                retry_attempts=perf_data.get("retry_attempts", 3),
                retry_delay_seconds=perf_data.get("retry_delay_seconds", 30),
                bandwidth_limit_mbps=perf_data.get("bandwidth_limit_mbps")
            )

    def _create_default_configuration(self) -> None:
        """Create default configuration file."""        try:
            default_config = self.get_default_configuration()
            
            # Ensure directory exists
            config_dir = Path(self.config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Write configuration file
            with open(self.config_path, 'w') as f:
                if self.config_path.endswith('.yml') or self.config_path.endswith('.yaml'):
                    yaml.safe_dump(default_config, f, indent=2)
                else:
                    json.dump(default_config, f, indent=2)
            
            self.logger.info(f"Default backup configuration created: {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create default configuration: {e}")
            raise ConfigurationError(f"Default configuration creation failed: {e}")

    def get_default_configuration(self) -> Dict[str, Any]:
        """Get default configuration dictionary."""        return {
            "storage": asdict(self.storage),
            "encryption": asdict(self.encryption),
            "scheduling": asdict(self.scheduling),
            "monitoring": asdict(self.monitoring),
            "validation": asdict(self.validation),
            "recovery": asdict(self.recovery),
            "performance": asdict(self.performance)
        }

    def validate_configuration(self) -> List[str]:
        """        Validate current configuration.
        
        Returns:
            List of validation errors
        """        errors = []
        
        # Validate storage configuration
        if not self.storage.connection_params and self.storage.backend != StorageBackend.LOCAL_FILESYSTEM:
            errors.append("Storage connection parameters required for non-local backends")
        
        if self.storage.max_storage_gb <= 0:
            errors.append("Maximum storage size must be positive")
        
        if self.storage.retention_days <= 0:
            errors.append("Retention days must be positive")
        
        # Validate encryption configuration
        if self.encryption.enabled and not self.encryption.master_key_path:
            errors.append("Master key path required when encryption is enabled")
        
        # Validate scheduling configuration
        if self.scheduling.max_concurrent_jobs <= 0:
            errors.append("Maximum concurrent jobs must be positive")
        
        if self.scheduling.job_timeout_hours <= 0:
            errors.append("Job timeout must be positive")
        
        # Validate performance configuration
        if self.performance.max_parallel_operations <= 0:
            errors.append("Maximum parallel operations must be positive")
        
        if self.performance.chunk_size_mb <= 0:
            errors.append("Chunk size must be positive")
        
        if self.performance.memory_limit_gb <= 0:
            errors.append("Memory limit must be positive")
        
        return errors

    def save_configuration(self, path: Optional[str] = None) -> None:
        """        Save current configuration to file.
        
        Args:
            path: Optional custom save path
        """        save_path = path or self.config_path
        
        try:
            config_data = {
                "storage": asdict(self.storage),
                "encryption": asdict(self.encryption),
                "scheduling": asdict(self.scheduling),
                "monitoring": asdict(self.monitoring),
                "validation": asdict(self.validation),
                "recovery": asdict(self.recovery),
                "performance": asdict(self.performance),
                "metadata": {
                    "saved_at": datetime.now().isoformat(),
                    "version": "2.0.0"
                }
            }
            
            # Ensure directory exists
            config_dir = Path(save_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Write configuration
            with open(save_path, 'w') as f:
                if save_path.endswith('.yml') or save_path.endswith('.yaml'):
                    yaml.safe_dump(config_data, f, indent=2)
                else:
                    json.dump(config_data, f, indent=2)
            
            self.logger.info(f"Backup configuration saved to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise ConfigurationError(f"Configuration save failed: {e}")

    def get_storage_connection_string(self) -> str:
        """Get storage connection string based on backend."""        if self.storage.backend == StorageBackend.LOCAL_FILESYSTEM:
            return self.storage.connection_params.get("path", "/var/backups/ia_influencer")
        
        elif self.storage.backend == StorageBackend.AWS_S3:
            bucket = self.storage.connection_params.get("bucket", "ia-influencer-backups")
            region = self.storage.connection_params.get("region", "us-east-1")
            return f"s3://{bucket}/{self.storage.path_prefix}?region={region}"
        
        elif self.storage.backend == StorageBackend.AZURE_BLOB:
            account = self.storage.connection_params.get("account_name")
            container = self.storage.connection_params.get("container", "backups")
            return f"azure://{account}.blob.core.windows.net/{container}/{self.storage.path_prefix}"
        
        elif self.storage.backend == StorageBackend.GOOGLE_CLOUD:
            bucket = self.storage.connection_params.get("bucket", "ia-influencer-backups")
            return f"gs://{bucket}/{self.storage.path_prefix}"
        
        else:
            return f"{self.storage.backend.value}://{self.storage.path_prefix}"

    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for backup configuration."""        env_vars = {
            "BACKUP_STORAGE_BACKEND": self.storage.backend.value,
            "BACKUP_COMPRESSION": self.storage.compression.value,
            "BACKUP_COMPRESSION_LEVEL": str(self.storage.compression_level),
            "BACKUP_ENCRYPTION_ENABLED": str(self.encryption.enabled),
            "BACKUP_ENCRYPTION_ALGORITHM": self.encryption.algorithm,
            "BACKUP_MONITORING_ENABLED": str(self.monitoring.enabled),
            "BACKUP_VALIDATION_ENABLED": str(self.validation.enabled),
            "BACKUP_PARALLEL_OPERATIONS": str(self.performance.max_parallel_operations),
            "BACKUP_CHUNK_SIZE_MB": str(self.performance.chunk_size_mb),
            "BACKUP_MEMORY_LIMIT_GB": str(self.performance.memory_limit_gb)
        }
        
        # Add storage-specific environment variables
        if self.storage.backend == StorageBackend.AWS_S3:
            env_vars.update({
                "AWS_S3_BUCKET": self.storage.connection_params.get("bucket", ""),
                "AWS_REGION": self.storage.connection_params.get("region", "us-east-1")
            })
        
        elif self.storage.backend == StorageBackend.AZURE_BLOB:
            env_vars.update({
                "AZURE_ACCOUNT_NAME": self.storage.connection_params.get("account_name", ""),
                "AZURE_CONTAINER": self.storage.connection_params.get("container", "backups")
            })
        
        elif self.storage.backend == StorageBackend.GOOGLE_CLOUD:
            env_vars.update({
                "GCS_BUCKET": self.storage.connection_params.get("bucket", ""),
                "GCS_PROJECT_ID": self.storage.connection_params.get("project_id", "")
            })
        
        return env_vars

    def update_from_environment(self) -> None:
        """Update configuration from environment variables."""        # Storage backend
        if "BACKUP_STORAGE_BACKEND" in os.environ:
            self.storage.backend = StorageBackend(os.environ["BACKUP_STORAGE_BACKEND"])
        
        # Compression
        if "BACKUP_COMPRESSION" in os.environ:
            self.storage.compression = CompressionAlgorithm(os.environ["BACKUP_COMPRESSION"])
        
        if "BACKUP_COMPRESSION_LEVEL" in os.environ:
            self.storage.compression_level = int(os.environ["BACKUP_COMPRESSION_LEVEL"])
        
        # Encryption
        if "BACKUP_ENCRYPTION_ENABLED" in os.environ:
            self.encryption.enabled = os.environ["BACKUP_ENCRYPTION_ENABLED"].lower() == "true"
        
        if "BACKUP_ENCRYPTION_ALGORITHM" in os.environ:
            self.encryption.algorithm = os.environ["BACKUP_ENCRYPTION_ALGORITHM"]
        
        # Performance
        if "BACKUP_PARALLEL_OPERATIONS" in os.environ:
            self.performance.max_parallel_operations = int(os.environ["BACKUP_PARALLEL_OPERATIONS"])
        
        if "BACKUP_CHUNK_SIZE_MB" in os.environ:
            self.performance.chunk_size_mb = int(os.environ["BACKUP_CHUNK_SIZE_MB"])
        
        if "BACKUP_MEMORY_LIMIT_GB" in os.environ:
            self.performance.memory_limit_gb = int(os.environ["BACKUP_MEMORY_LIMIT_GB"])

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get configuration summary for monitoring."""        return {
            "storage_backend": self.storage.backend.value,
            "encryption_enabled": self.encryption.enabled,
            "scheduling_enabled": self.scheduling.enabled,
            "monitoring_enabled": self.monitoring.enabled,
            "validation_enabled": self.validation.enabled,
            "max_storage_gb": self.storage.max_storage_gb,
            "retention_days": self.storage.retention_days,
            "max_parallel_operations": self.performance.max_parallel_operations,
            "compression_algorithm": self.storage.compression.value,
            "last_updated": datetime.now().isoformat()
        }


# Global configuration instance
backup_config = BackupConfig()


def get_backup_config() -> BackupConfig:
    """Get global backup configuration instance."""    return backup_config


def reload_backup_config(config_path: Optional[str] = None) -> BackupConfig:
    """Reload backup configuration from file."""    global backup_config
    backup_config = BackupConfig(config_path)
    return backup_config
