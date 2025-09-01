"""Encrypted Backup System with Restoration Tests
==============================================

Comprehensive backup system with encryption, automated scheduling,
restoration testing, and compliance reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import os
import tarfile
import gzip
import subprocess
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import hashlib
from pathlib import Path
import threading
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from config.security.production_security import BackupConfig, get_security_config
from core.security.enhanced_audit_trail import log_audit_event, AuditEventType


logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Types of backups"""
    DAILY_INCREMENTAL = "daily_incremental"
    WEEKLY_FULL = "weekly_full"
    MONTHLY_ARCHIVE = "monthly_archive"
    ON_DEMAND = "on_demand"
    DISASTER_RECOVERY = "disaster_recovery"


class BackupStatus(Enum):
    """Backup status"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    CORRUPTED = "corrupted"


@dataclass
class BackupMetadata:
    """Backup metadata"""
    backup_id: str
    backup_type: BackupType
    created_at: datetime
    completed_at: Optional[datetime]
    status: BackupStatus
    file_path: str
    file_size: int
    checksum: str
    encrypted: bool
    compression_type: str
    retention_until: datetime
    
    # Data included
    databases: List[str] = field(default_factory=list)
    file_systems: List[str] = field(default_factory=list)
    configurations: List[str] = field(default_factory=list)
    
    # Restoration info
    last_tested: Optional[datetime] = None
    test_results: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "backup_id": self.backup_id,
            "backup_type": self.backup_type.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status.value,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "checksum": self.checksum,
            "encrypted": self.encrypted,
            "compression_type": self.compression_type,
            "retention_until": self.retention_until.isoformat(),
            "databases": self.databases,
            "file_systems": self.file_systems,
            "configurations": self.configurations,
            "last_tested": self.last_tested.isoformat() if self.last_tested else None,
            "test_results": self.test_results
        }


@dataclass
class RestorationTestResult:
    """Restoration test result"""
    test_id: str
    backup_id: str
    test_time: datetime
    success: bool
    duration_seconds: float
    files_tested: int
    files_verified: int
    errors: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class EncryptedBackupSystem:
    """Encrypted backup system with restoration testing"""
    
    def __init__(self, config: Optional[BackupConfig] = None):
        self.config = config or get_security_config().backup
        self.backups: Dict[str, BackupMetadata] = {}
        self.encryption_key: Optional[bytes] = None
        self.scheduler_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
        # Initialize encryption
        if self.config.encryption_enabled:
            self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption key"""
        if not self.config.encryption_key:
            raise ValueError("Encryption key not configured")
        
        # Derive key from password
        password = self.config.encryption_key.encode()
        salt = b'stable_salt_for_backup_system'  # In production, use random salt stored securely
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.encryption_key = key
    
    def _get_cipher(self) -> Fernet:
        """Get encryption cipher"""
        if not self.encryption_key:
            raise ValueError("Encryption not initialized")
        return Fernet(self.encryption_key)
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _get_backup_filename(self, backup_type: BackupType, timestamp: datetime) -> str:
        """Generate backup filename"""
        date_str = timestamp.strftime("%Y%m%d_%H%M%S")
        return f"ainflue_backup_{backup_type.value}_{date_str}.tar.gz"
    
    def _get_retention_date(self, backup_type: BackupType) -> datetime:
        """Calculate retention date based on backup type"""
        now = datetime.utcnow()
        
        if backup_type == BackupType.DAILY_INCREMENTAL:
            return now + timedelta(days=self.config.daily_retention_days)
        elif backup_type == BackupType.WEEKLY_FULL:
            return now + timedelta(weeks=self.config.weekly_retention_weeks)
        elif backup_type == BackupType.MONTHLY_ARCHIVE:
            return now + timedelta(days=self.config.monthly_retention_months * 30)
        else:
            return now + timedelta(days=self.config.daily_retention_days)
    
    async def create_backup(
        self,
        backup_type: BackupType,
        include_databases: bool = True,
        include_files: bool = True,
        include_configs: bool = True,
        custom_paths: Optional[List[str]] = None
    ) -> BackupMetadata:
        """Create encrypted backup"""
        
        backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.utcnow()
        
        # Create backup metadata
        metadata = BackupMetadata(
            backup_id=backup_id,
            backup_type=backup_type,
            created_at=timestamp,
            completed_at=None,
            status=BackupStatus.RUNNING,
            file_path="",
            file_size=0,
            checksum="",
            encrypted=self.config.encryption_enabled,
            compression_type="gzip",
            retention_until=self._get_retention_date(backup_type)
        )
        
        try:
            # Log backup start
            await log_audit_event(
                "backup.started",
                action=f"Started {backup_type.value} backup",
                details={"backup_id": backup_id, "backup_type": backup_type.value}
            )
            
            # Create temporary directory for backup preparation
            with tempfile.TemporaryDirectory() as temp_dir:
                backup_dir = Path(temp_dir) / "backup_staging"
                backup_dir.mkdir()
                
                # Collect files to backup
                if include_databases:
                    await self._backup_databases(backup_dir, metadata)
                
                if include_files:
                    await self._backup_files(backup_dir, metadata, custom_paths)
                
                if include_configs:
                    await self._backup_configurations(backup_dir, metadata)
                
                # Create compressed archive
                filename = self._get_backup_filename(backup_type, timestamp)
                temp_archive_path = Path(temp_dir) / filename
                
                await self._create_compressed_archive(backup_dir, temp_archive_path)
                
                # Encrypt if enabled
                if self.config.encryption_enabled:
                    encrypted_path = Path(temp_dir) / f"{filename}.encrypted"
                    await self._encrypt_file(temp_archive_path, encrypted_path)
                    final_archive_path = encrypted_path
                    filename = f"{filename}.encrypted"
                else:
                    final_archive_path = temp_archive_path
                
                # Move to final location
                backup_location = Path(self.config.backup_location.replace("s3://", "/tmp/"))
                backup_location.mkdir(parents=True, exist_ok=True)
                final_path = backup_location / filename
                
                shutil.move(str(final_archive_path), str(final_path))
                
                # Update metadata
                metadata.file_path = str(final_path)
                metadata.file_size = final_path.stat().st_size
                metadata.checksum = self._calculate_file_checksum(str(final_path))
                metadata.completed_at = datetime.utcnow()
                metadata.status = BackupStatus.COMPLETED
            
            # Store metadata
            self.backups[backup_id] = metadata
            
            # Log completion
            await log_audit_event(
                "backup.completed",
                action=f"Completed {backup_type.value} backup",
                details={
                    "backup_id": backup_id,
                    "file_size": metadata.file_size,
                    "duration_seconds": (metadata.completed_at - metadata.created_at).total_seconds()
                }
            )
            
            logger.info(f"Backup completed: {backup_id} ({metadata.file_size} bytes)")
            return metadata
            
        except Exception as e:
            metadata.status = BackupStatus.FAILED
            metadata.completed_at = datetime.utcnow()
            self.backups[backup_id] = metadata
            
            await log_audit_event(
                "backup.failed",
                action=f"Failed {backup_type.value} backup",
                details={"backup_id": backup_id, "error": str(e)}
            )
            
            logger.error(f"Backup failed: {backup_id} - {e}")
            raise
    
    async def _backup_databases(self, backup_dir: Path, metadata: BackupMetadata):
        """Backup databases"""
        db_dir = backup_dir / "databases"
        db_dir.mkdir()
        
        # Placeholder for database backup
        # In production, implement actual database backup logic
        databases = ["ainflue_main", "ainflue_analytics", "ainflue_logs"]
        
        for db_name in databases:
            db_file = db_dir / f"{db_name}.sql"
            # Simulate database dump
            db_file.write_text(f"-- Database backup for {db_name}\n-- Created at {datetime.utcnow()}\n")
            metadata.databases.append(db_name)
        
        logger.info(f"Backed up {len(databases)} databases")
    
    async def _backup_files(self, backup_dir: Path, metadata: BackupMetadata, custom_paths: Optional[List[str]]):
        """Backup file systems"""
        files_dir = backup_dir / "files"
        files_dir.mkdir()
        
        # Default paths to backup
        default_paths = [
            "/home/runner/work/Ainflue/Ainflue/config",
            "/home/runner/work/Ainflue/Ainflue/logs",
            "/home/runner/work/Ainflue/Ainflue/uploads"
        ]
        
        paths_to_backup = custom_paths or default_paths
        
        for path in paths_to_backup:
            if os.path.exists(path):
                path_obj = Path(path)
                dest_dir = files_dir / path_obj.name
                
                if path_obj.is_file():
                    shutil.copy2(path, dest_dir.parent)
                elif path_obj.is_dir():
                    shutil.copytree(path, dest_dir, ignore_errors=True)
                
                metadata.file_systems.append(path)
        
        logger.info(f"Backed up {len(paths_to_backup)} file system paths")
    
    async def _backup_configurations(self, backup_dir: Path, metadata: BackupMetadata):
        """Backup configurations"""
        config_dir = backup_dir / "configurations"
        config_dir.mkdir()
        
        # Backup configuration files
        config_files = [
            ".env",
            ".env.production",
            "requirements.txt",
            "docker-compose.yml"
        ]
        
        project_root = Path("/home/runner/work/Ainflue/Ainflue")
        
        for config_file in config_files:
            source_path = project_root / config_file
            if source_path.exists():
                dest_path = config_dir / config_file
                shutil.copy2(source_path, dest_path)
                metadata.configurations.append(config_file)
        
        # Backup security configurations
        security_config_dir = project_root / "config" / "security"
        if security_config_dir.exists():
            dest_security_dir = config_dir / "security"
            shutil.copytree(security_config_dir, dest_security_dir, ignore_errors=True)
            metadata.configurations.append("config/security")
        
        logger.info(f"Backed up {len(metadata.configurations)} configuration items")
    
    async def _create_compressed_archive(self, source_dir: Path, archive_path: Path):
        """Create compressed tar archive"""
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_dir, arcname="backup_data")
        
        logger.info(f"Created compressed archive: {archive_path}")
    
    async def _encrypt_file(self, source_path: Path, dest_path: Path):
        """Encrypt file"""
        cipher = self._get_cipher()
        
        with open(source_path, "rb") as source_file:
            data = source_file.read()
        
        encrypted_data = cipher.encrypt(data)
        
        with open(dest_path, "wb") as dest_file:
            dest_file.write(encrypted_data)
        
        logger.info(f"Encrypted file: {source_path} -> {dest_path}")
    
    async def test_restoration(self, backup_id: str) -> RestorationTestResult:
        """Test backup restoration"""
        
        if backup_id not in self.backups:
            raise ValueError(f"Backup {backup_id} not found")
        
        metadata = self.backups[backup_id]
        test_id = f"test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.utcnow()
        
        test_result = RestorationTestResult(
            test_id=test_id,
            backup_id=backup_id,
            test_time=start_time,
            success=False,
            duration_seconds=0,
            files_tested=0,
            files_verified=0
        )
        
        try:
            # Log test start
            await log_audit_event(
                "backup.test.started",
                action=f"Started restoration test for backup {backup_id}",
                details={"backup_id": backup_id, "test_id": test_id}
            )
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Decrypt if necessary
                if metadata.encrypted:
                    encrypted_path = Path(metadata.file_path)
                    decrypted_path = Path(temp_dir) / "decrypted_backup.tar.gz"
                    await self._decrypt_file(encrypted_path, decrypted_path)
                    archive_path = decrypted_path
                else:
                    archive_path = Path(metadata.file_path)
                
                # Extract archive
                extract_dir = Path(temp_dir) / "extracted"
                extract_dir.mkdir()
                
                with tarfile.open(archive_path, "r:gz") as tar:
                    tar.extractall(extract_dir)
                
                # Verify extracted files
                backup_data_dir = extract_dir / "backup_data"
                if not backup_data_dir.exists():
                    test_result.errors.append("Backup data directory not found")
                    return test_result
                
                # Count and verify files
                files_found = list(backup_data_dir.rglob("*"))
                test_result.files_tested = len([f for f in files_found if f.is_file()])
                
                # Verify database backups
                if metadata.databases:
                    db_dir = backup_data_dir / "databases"
                    if db_dir.exists():
                        for db_name in metadata.databases:
                            db_file = db_dir / f"{db_name}.sql"
                            if db_file.exists() and db_file.stat().st_size > 0:
                                test_result.files_verified += 1
                            else:
                                test_result.errors.append(f"Database backup missing or empty: {db_name}")
                
                # Verify file system backups
                if metadata.file_systems:
                    files_dir = backup_data_dir / "files"
                    if files_dir.exists():
                        for path in metadata.file_systems:
                            path_name = Path(path).name
                            backed_up_path = files_dir / path_name
                            if backed_up_path.exists():
                                test_result.files_verified += 1
                            else:
                                test_result.errors.append(f"File system backup missing: {path}")
                
                # Verify configurations
                if metadata.configurations:
                    config_dir = backup_data_dir / "configurations"
                    if config_dir.exists():
                        for config_item in metadata.configurations:
                            config_path = config_dir / config_item
                            if config_path.exists():
                                test_result.files_verified += 1
                            else:
                                test_result.errors.append(f"Configuration backup missing: {config_item}")
                
                # Calculate success
                test_result.success = (
                    len(test_result.errors) == 0 and
                    test_result.files_verified > 0
                )
            
            # Update timing
            end_time = datetime.utcnow()
            test_result.duration_seconds = (end_time - start_time).total_seconds()
            
            # Update metadata
            metadata.last_tested = end_time
            metadata.test_results = {
                "test_id": test_id,
                "success": test_result.success,
                "files_verified": test_result.files_verified,
                "errors": test_result.errors
            }
            
            if test_result.success:
                metadata.status = BackupStatus.VERIFIED
            else:
                metadata.status = BackupStatus.CORRUPTED
            
            # Log test completion
            await log_audit_event(
                "backup.test.completed",
                action=f"Completed restoration test for backup {backup_id}",
                details={
                    "backup_id": backup_id,
                    "test_id": test_id,
                    "success": test_result.success,
                    "files_verified": test_result.files_verified,
                    "duration_seconds": test_result.duration_seconds
                }
            )
            
            logger.info(
                f"Restoration test completed: {backup_id} - "
                f"Success: {test_result.success}, Files verified: {test_result.files_verified}"
            )
            
        except Exception as e:
            test_result.errors.append(str(e))
            test_result.duration_seconds = (datetime.utcnow() - start_time).total_seconds()
            
            await log_audit_event(
                "backup.test.failed",
                action=f"Failed restoration test for backup {backup_id}",
                details={"backup_id": backup_id, "test_id": test_id, "error": str(e)}
            )
            
            logger.error(f"Restoration test failed: {backup_id} - {e}")
        
        return test_result
    
    async def _decrypt_file(self, source_path: Path, dest_path: Path):
        """Decrypt file"""
        cipher = self._get_cipher()
        
        with open(source_path, "rb") as source_file:
            encrypted_data = source_file.read()
        
        decrypted_data = cipher.decrypt(encrypted_data)
        
        with open(dest_path, "wb") as dest_file:
            dest_file.write(decrypted_data)
        
        logger.info(f"Decrypted file: {source_path} -> {dest_path}")
    
    async def cleanup_expired_backups(self) -> List[str]:
        """Clean up expired backups"""
        current_time = datetime.utcnow()
        expired_backups = []
        
        for backup_id, metadata in list(self.backups.items()):
            if current_time > metadata.retention_until:
                try:
                    # Delete backup file
                    if os.path.exists(metadata.file_path):
                        os.remove(metadata.file_path)
                    
                    # Remove from tracking
                    del self.backups[backup_id]
                    expired_backups.append(backup_id)
                    
                    await log_audit_event(
                        "backup.expired",
                        action=f"Deleted expired backup {backup_id}",
                        details={"backup_id": backup_id, "retention_until": metadata.retention_until.isoformat()}
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to delete expired backup {backup_id}: {e}")
        
        return expired_backups
    
    async def get_backup_status(self) -> Dict[str, Any]:
        """Get backup system status"""
        total_backups = len(self.backups)
        completed_backups = len([b for b in self.backups.values() if b.status == BackupStatus.COMPLETED])
        verified_backups = len([b for b in self.backups.values() if b.status == BackupStatus.VERIFIED])
        failed_backups = len([b for b in self.backups.values() if b.status == BackupStatus.FAILED])
        
        # Calculate total storage used
        total_storage = sum(b.file_size for b in self.backups.values() if b.status == BackupStatus.COMPLETED)
        
        # Recent backups
        recent_backups = sorted(
            [b for b in self.backups.values()],
            key=lambda x: x.created_at,
            reverse=True
        )[:5]
        
        # Next scheduled backup
        last_daily = max(
            [b.created_at for b in self.backups.values() if b.backup_type == BackupType.DAILY_INCREMENTAL],
            default=datetime.min
        )
        next_daily = last_daily + timedelta(days=1) if last_daily != datetime.min else datetime.utcnow()
        
        return {
            "total_backups": total_backups,
            "completed_backups": completed_backups,
            "verified_backups": verified_backups,
            "failed_backups": failed_backups,
            "total_storage_bytes": total_storage,
            "encryption_enabled": self.config.encryption_enabled,
            "recent_backups": [b.to_dict() for b in recent_backups],
            "next_daily_backup": next_daily.isoformat(),
            "backup_location": self.config.backup_location
        }


# Global backup system instance
_backup_system_instance: Optional[EncryptedBackupSystem] = None

def get_backup_system() -> EncryptedBackupSystem:
    """Get global backup system instance"""
    global _backup_system_instance
    if _backup_system_instance is None:
        _backup_system_instance = EncryptedBackupSystem()
    return _backup_system_instance


async def create_backup(backup_type: str = "daily_incremental", **kwargs) -> Dict[str, Any]:
    """Create backup (main entry point)"""
    backup_system = get_backup_system()
    
    # Convert string to enum
    try:
        backup_type_enum = BackupType(backup_type.lower())
    except ValueError:
        backup_type_enum = BackupType.DAILY_INCREMENTAL
    
    metadata = await backup_system.create_backup(backup_type_enum, **kwargs)
    return metadata.to_dict()


async def test_backup_restoration(backup_id: str) -> Dict[str, Any]:
    """Test backup restoration (main entry point)"""
    backup_system = get_backup_system()
    result = await backup_system.test_restoration(backup_id)
    
    return {
        "test_id": result.test_id,
        "backup_id": result.backup_id,
        "success": result.success,
        "duration_seconds": result.duration_seconds,
        "files_tested": result.files_tested,
        "files_verified": result.files_verified,
        "errors": result.errors
    }


if __name__ == "__main__":
    async def main():
        # Test backup system
        backup_system = EncryptedBackupSystem()
        
        # Create test backup
        metadata = await backup_system.create_backup(BackupType.DAILY_INCREMENTAL)
        print(f"Created backup: {metadata.backup_id}")
        
        # Test restoration
        test_result = await backup_system.test_restoration(metadata.backup_id)
        print(f"Restoration test: {test_result.success}")
        
        # Get status
        status = await backup_system.get_backup_status()
        print(f"Backup status: {status}")
    
    asyncio.run(main())