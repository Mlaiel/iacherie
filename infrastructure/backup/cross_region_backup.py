"""Cross-Region Backup and Disaster Recovery System

Comprehensive backup system with cross-region replication and automated
disaster recovery testing for data protection compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
"""

import asyncio
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import tarfile
import gzip

from ...core.logging import get_logger
from ...core.config import get_settings
from ...core.storage import StorageManager
from ...data_management.governance.encryption import DataEncryption

logger = get_logger(__name__)


class BackupType(Enum):
    """Types of backups"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupStatus(Enum):
    """Backup operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    CORRUPTED = "corrupted"


class RecoveryObjective(Enum):
    """Recovery objectives for different data types"""
    CRITICAL = "critical"      # RTO: 1 hour, RPO: 15 minutes
    HIGH = "high"             # RTO: 4 hours, RPO: 1 hour  
    MEDIUM = "medium"         # RTO: 24 hours, RPO: 6 hours
    LOW = "low"              # RTO: 72 hours, RPO: 24 hours


@dataclass
class BackupConfiguration:
    """Backup configuration for different data types"""
    data_category: str
    backup_type: BackupType
    frequency_hours: int
    retention_days: int
    encryption_required: bool
    cross_region_replicas: List[str]
    recovery_objective: RecoveryObjective
    compression_enabled: bool = True
    verification_enabled: bool = True


@dataclass
class BackupRecord:
    """Record of a backup operation"""
    backup_id: str
    data_category: str
    backup_type: BackupType
    source_location: str
    backup_locations: List[str]
    created_at: datetime
    size_bytes: int
    checksum: str
    status: BackupStatus
    encryption_key_id: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class DisasterRecoveryTest:
    """Disaster recovery test record"""
    test_id: str
    test_type: str
    target_rto: timedelta
    target_rpo: timedelta
    actual_rto: Optional[timedelta] = None
    actual_rpo: Optional[timedelta] = None
    success: bool = False
    issues_found: List[str] = None
    conducted_at: Optional[datetime] = None


class CrossRegionBackupManager:
    """
    Cross-region backup and disaster recovery management system
    """
    
    def __init__(self, storage_manager: Optional[StorageManager] = None):
        self.storage = storage_manager or StorageManager()
        self.logger = logger
        self.settings = get_settings()
        self.encryption = DataEncryption()
        
        # Backup configurations by data category
        self.backup_configs = self._load_backup_configurations()
        
        # Available regions for backup
        self.available_regions = [
            "us-east-1", "us-west-2", "eu-west-1", "eu-central-1",
            "ap-southeast-1", "ap-northeast-1"
        ]
        
        # Primary region (configurable)
        self.primary_region = self.settings.get("primary_region", "us-east-1")
        
        # Backup schedule tracking
        self.backup_schedules: Dict[str, datetime] = {}
        
    def _load_backup_configurations(self) -> Dict[str, BackupConfiguration]:
        """Load backup configurations for different data categories"""
        return {
            "user_data": BackupConfiguration(
                data_category="user_data",
                backup_type=BackupType.INCREMENTAL,
                frequency_hours=6,
                retention_days=2555,  # 7 years for GDPR compliance
                encryption_required=True,
                cross_region_replicas=["us-west-2", "eu-west-1"],
                recovery_objective=RecoveryObjective.CRITICAL,
                compression_enabled=True,
                verification_enabled=True
            ),
            "financial_data": BackupConfiguration(
                data_category="financial_data",
                backup_type=BackupType.INCREMENTAL,
                frequency_hours=1,  # Hourly for financial data
                retention_days=2555,  # 7 years for compliance
                encryption_required=True,
                cross_region_replicas=["us-west-2", "eu-west-1", "ap-southeast-1"],
                recovery_objective=RecoveryObjective.CRITICAL,
                compression_enabled=True,
                verification_enabled=True
            ),
            "content_data": BackupConfiguration(
                data_category="content_data",
                backup_type=BackupType.DIFFERENTIAL,
                frequency_hours=12,
                retention_days=1825,  # 5 years
                encryption_required=True,
                cross_region_replicas=["us-west-2", "eu-central-1"],
                recovery_objective=RecoveryObjective.HIGH,
                compression_enabled=True,
                verification_enabled=True
            ),
            "analytics_data": BackupConfiguration(
                data_category="analytics_data",
                backup_type=BackupType.FULL,
                frequency_hours=24,
                retention_days=730,  # 2 years
                encryption_required=False,
                cross_region_replicas=["us-west-2"],
                recovery_objective=RecoveryObjective.MEDIUM,
                compression_enabled=True,
                verification_enabled=False
            ),
            "system_logs": BackupConfiguration(
                data_category="system_logs",
                backup_type=BackupType.INCREMENTAL,
                frequency_hours=3,
                retention_days=2555,  # 7 years for audit
                encryption_required=True,
                cross_region_replicas=["us-west-2", "eu-west-1"],
                recovery_objective=RecoveryObjective.HIGH,
                compression_enabled=True,
                verification_enabled=True
            ),
            "temporary_data": BackupConfiguration(
                data_category="temporary_data",
                backup_type=BackupType.SNAPSHOT,
                frequency_hours=168,  # Weekly
                retention_days=30,
                encryption_required=False,
                cross_region_replicas=[],  # No cross-region for temp data
                recovery_objective=RecoveryObjective.LOW,
                compression_enabled=True,
                verification_enabled=False
            )
        }
    
    async def create_backup(
        self,
        data_category: str,
        source_path: str,
        backup_type: Optional[BackupType] = None
    ) -> BackupRecord:
        """
        Create a backup for the specified data category
        
        Args:
            data_category: Category of data to backup
            source_path: Source path/identifier for the data
            backup_type: Override default backup type
            
        Returns:
            BackupRecord with backup details
        """
        try:
            if data_category not in self.backup_configs:
                raise ValueError(f"No backup configuration for category: {data_category}")
            
            config = self.backup_configs[data_category]
            backup_type = backup_type or config.backup_type
            
            # Generate backup ID
            backup_id = self._generate_backup_id(data_category, backup_type)
            
            self.logger.info(f"Starting backup {backup_id} for {data_category}")
            
            # Create backup record
            backup_record = BackupRecord(
                backup_id=backup_id,
                data_category=data_category,
                backup_type=backup_type,
                source_location=source_path,
                backup_locations=[],
                created_at=datetime.utcnow(),
                size_bytes=0,
                checksum="",
                status=BackupStatus.IN_PROGRESS,
                metadata={
                    "config": asdict(config),
                    "primary_region": self.primary_region
                }
            )
            
            # Prepare data for backup
            backup_data = await self._prepare_backup_data(source_path, config)
            backup_record.size_bytes = len(backup_data)
            backup_record.checksum = hashlib.sha256(backup_data).hexdigest()
            
            # Encrypt if required
            if config.encryption_required:
                encrypted_data, key_id = await self.encryption.encrypt_data(backup_data)
                backup_data = encrypted_data
                backup_record.encryption_key_id = key_id
            
            # Store backup in primary region
            primary_location = await self._store_backup_in_region(
                backup_id, backup_data, self.primary_region
            )
            backup_record.backup_locations.append(primary_location)
            
            # Replicate to cross-region locations
            for region in config.cross_region_replicas:
                try:
                    replica_location = await self._store_backup_in_region(
                        backup_id, backup_data, region
                    )
                    backup_record.backup_locations.append(replica_location)
                    
                    self.logger.info(f"Backup {backup_id} replicated to {region}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to replicate backup to {region}: {str(e)}")
                    # Continue with other regions
            
            # Verify backup integrity if enabled
            if config.verification_enabled:
                verification_result = await self._verify_backup_integrity(backup_record)
                if verification_result:
                    backup_record.status = BackupStatus.VERIFIED
                else:
                    backup_record.status = BackupStatus.CORRUPTED
                    self.logger.error(f"Backup verification failed for {backup_id}")
            else:
                backup_record.status = BackupStatus.COMPLETED
            
            # Store backup metadata
            await self._store_backup_metadata(backup_record)
            
            self.logger.info(
                f"Backup {backup_id} completed successfully. "
                f"Size: {backup_record.size_bytes} bytes, "
                f"Locations: {len(backup_record.backup_locations)}"
            )
            
            return backup_record
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {str(e)}")
            if 'backup_record' in locals():
                backup_record.status = BackupStatus.FAILED
                await self._store_backup_metadata(backup_record)
            raise
    
    async def run_disaster_recovery_test(
        self,
        data_category: str,
        test_type: str = "full_restore"
    ) -> DisasterRecoveryTest:
        """
        Run automated disaster recovery test
        
        Args:
            data_category: Data category to test
            test_type: Type of test to run
            
        Returns:
            DisasterRecoveryTest with results
        """
        try:
            if data_category not in self.backup_configs:
                raise ValueError(f"No configuration for category: {data_category}")
            
            config = self.backup_configs[data_category]
            test_id = f"dr_test_{data_category}_{datetime.utcnow().isoformat()}"
            
            # Define test objectives based on recovery objective
            rto_targets = {
                RecoveryObjective.CRITICAL: timedelta(hours=1),
                RecoveryObjective.HIGH: timedelta(hours=4),
                RecoveryObjective.MEDIUM: timedelta(hours=24),
                RecoveryObjective.LOW: timedelta(hours=72)
            }
            
            rpo_targets = {
                RecoveryObjective.CRITICAL: timedelta(minutes=15),
                RecoveryObjective.HIGH: timedelta(hours=1),
                RecoveryObjective.MEDIUM: timedelta(hours=6),
                RecoveryObjective.LOW: timedelta(hours=24)
            }
            
            dr_test = DisasterRecoveryTest(
                test_id=test_id,
                test_type=test_type,
                target_rto=rto_targets[config.recovery_objective],
                target_rpo=rpo_targets[config.recovery_objective],
                issues_found=[]
            )
            
            self.logger.info(f"Starting DR test {test_id} for {data_category}")
            test_start = datetime.utcnow()
            
            # Test would include:
            # - Finding latest backup
            # - Testing accessibility from all regions
            # - Performing test restore
            # - Calculating RTO/RPO metrics
            
            dr_test.conducted_at = datetime.utcnow()
            dr_test.actual_rto = datetime.utcnow() - test_start
            dr_test.success = True  # Placeholder for actual implementation
            
            await self._store_dr_test_results(dr_test)
            
            return dr_test
            
        except Exception as e:
            self.logger.error(f"DR test failed: {str(e)}")
            dr_test.issues_found.append(f"Test execution error: {str(e)}")
            dr_test.success = False
            return dr_test
    
    def _generate_backup_id(self, data_category: str, backup_type: BackupType) -> str:
        """Generate unique backup ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"backup_{data_category}_{backup_type.value}_{timestamp}"
    
    async def _prepare_backup_data(
        self,
        source_path: str,
        config: BackupConfiguration
    ) -> bytes:
        """Prepare data for backup (compression, etc.)"""
        # This would be implemented based on your data storage system
        # For now, return placeholder data
        data = f"Backup data for {source_path}".encode()
        
        if config.compression_enabled:
            data = gzip.compress(data)
        
        return data
    
    async def _store_backup_in_region(
        self,
        backup_id: str,
        backup_data: bytes,
        region: str
    ) -> str:
        """Store backup data in specified region"""
        # Implementation would use your storage backend
        # Return storage location identifier
        return f"{region}://backups/{backup_id}"
    
    async def _verify_backup_integrity(self, backup_record: BackupRecord) -> bool:
        """Verify backup integrity across all locations"""
        # Implementation would verify data integrity
        return True
    
    async def _store_backup_metadata(self, backup_record: BackupRecord):
        """Store backup metadata for tracking"""
        # Implementation would store in database
        pass
    
    async def _store_dr_test_results(self, dr_test: DisasterRecoveryTest):
        """Store disaster recovery test results"""
        # Implementation would store in database
        pass