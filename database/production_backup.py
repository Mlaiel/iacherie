"""Production Database Backup System with 30-day Retention

This module implements automated daily backups with comprehensive retention
management for the Ainflue production database.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import os
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import boto3
from botocore.exceptions import ClientError
import schedule
import time

logger = logging.getLogger(__name__)

class BackupType(str, Enum):
    """Types of database backups."""
    FULL = "full"
    INCREMENTAL = "incremental"
    WAL_ARCHIVE = "wal_archive"
    POINT_IN_TIME = "point_in_time"

class BackupStatus(str, Enum):
    """Backup operation status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class BackupConfig:
    """Production backup configuration."""
    # Database connection
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "ainflue_production"
    database_user: str = "backup_user"
    database_password: str = ""
    
    # Backup settings
    backup_type: BackupType = BackupType.FULL
    retention_days: int = 30
    backup_directory: Path = Path("/backup/postgresql")
    compression_level: int = 9
    parallel_jobs: int = 4
    
    # Schedule settings
    daily_backup_time: str = "02:00"  # 2 AM UTC
    enable_incremental: bool = True
    incremental_interval_hours: int = 6
    
    # Storage settings
    enable_remote_storage: bool = True
    s3_bucket: Optional[str] = None
    s3_prefix: str = "database_backups"
    s3_storage_class: str = "STANDARD_IA"
    
    # Verification settings
    verify_backups: bool = True
    test_restore_frequency_days: int = 7
    
    # Monitoring
    enable_monitoring: bool = True
    alert_on_failure: bool = True
    health_check_url: Optional[str] = None

@dataclass
class BackupRecord:
    """Record of a backup operation."""
    backup_id: str
    backup_type: BackupType
    start_time: datetime
    end_time: Optional[datetime] = None
    status: BackupStatus = BackupStatus.PENDING
    file_path: Optional[Path] = None
    file_size_bytes: int = 0
    compressed_size_bytes: int = 0
    s3_location: Optional[str] = None
    verification_status: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ProductionBackupManager:
    """Production database backup manager with 30-day retention."""
    
    def __init__(self, config: BackupConfig):
        self.config = config
        self.backup_records: List[BackupRecord] = []
        self.s3_client = None
        
        # Ensure backup directory exists
        self.config.backup_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize S3 client if remote storage is enabled
        if self.config.enable_remote_storage and self.config.s3_bucket:
            self.s3_client = boto3.client('s3')
    
    def _generate_backup_id(self, backup_type: BackupType) -> str:
        """Generate unique backup ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"ainflue_{backup_type.value}_{timestamp}"
    
    def _get_backup_filename(self, backup_id: str, backup_type: BackupType) -> str:
        """Get backup filename."""
        extension = "sql.gz" if backup_type == BackupType.FULL else "tar.gz"
        return f"{backup_id}.{extension}"
    
    async def create_full_backup(self) -> BackupRecord:
        """Create a full database backup."""
        backup_id = self._generate_backup_id(BackupType.FULL)
        filename = self._get_backup_filename(backup_id, BackupType.FULL)
        file_path = self.config.backup_directory / filename
        
        record = BackupRecord(
            backup_id=backup_id,
            backup_type=BackupType.FULL,
            start_time=datetime.utcnow(),
            file_path=file_path
        )
        
        logger.info(f"Starting full backup: {backup_id}")
        
        try:
            record.status = BackupStatus.RUNNING
            
            # Prepare pg_dump command
            cmd = [
                'pg_dump',
                '--host', self.config.database_host,
                '--port', str(self.config.database_port),
                '--username', self.config.database_user,
                '--dbname', self.config.database_name,
                '--format', 'custom',
                '--compress', str(self.config.compression_level),
                '--jobs', str(self.config.parallel_jobs),
                '--verbose',
                '--no-password'  # Use .pgpass or environment variable
            ]
            
            # Set environment variables
            env = os.environ.copy()
            if self.config.database_password:
                env['PGPASSWORD'] = self.config.database_password
            
            # Execute backup
            with open(file_path, 'wb') as backup_file:
                process = subprocess.Popen(
                    cmd,
                    stdout=backup_file,
                    stderr=subprocess.PIPE,
                    env=env
                )
                
                _, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"pg_dump failed: {stderr.decode()}")
            
            # Get file size
            record.file_size_bytes = file_path.stat().st_size
            record.compressed_size_bytes = record.file_size_bytes
            
            # Upload to S3 if configured
            if self.s3_client and self.config.s3_bucket:
                s3_key = f"{self.config.s3_prefix}/{filename}"
                await self._upload_to_s3(file_path, s3_key)
                record.s3_location = f"s3://{self.config.s3_bucket}/{s3_key}"
            
            # Verify backup if enabled
            if self.config.verify_backups:
                record.verification_status = await self._verify_backup(file_path)
            
            record.status = BackupStatus.COMPLETED
            record.end_time = datetime.utcnow()
            
            logger.info(f"Full backup completed: {backup_id}, size: {record.file_size_bytes} bytes")
            
        except Exception as e:
            record.status = BackupStatus.FAILED
            record.error_message = str(e)
            record.end_time = datetime.utcnow()
            logger.error(f"Full backup failed: {e}")
            
            # Clean up failed backup file
            if file_path.exists():
                file_path.unlink()
        
        self.backup_records.append(record)
        return record
    
    async def create_wal_archive_backup(self, wal_file: str) -> BackupRecord:
        """Create WAL archive backup."""
        backup_id = self._generate_backup_id(BackupType.WAL_ARCHIVE)
        
        record = BackupRecord(
            backup_id=backup_id,
            backup_type=BackupType.WAL_ARCHIVE,
            start_time=datetime.utcnow(),
            metadata={"wal_file": wal_file}
        )
        
        try:
            record.status = BackupStatus.RUNNING
            
            # Compress and archive WAL file
            wal_path = Path(f"/var/lib/postgresql/data/pg_wal/{wal_file}")
            archive_path = self.config.backup_directory / "wal_archives" / f"{wal_file}.gz"
            
            # Ensure WAL archive directory exists
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Compress WAL file
            with open(wal_path, 'rb') as f_in:
                with gzip.open(archive_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            record.file_path = archive_path
            record.file_size_bytes = wal_path.stat().st_size
            record.compressed_size_bytes = archive_path.stat().st_size
            
            # Upload to S3 if configured
            if self.s3_client and self.config.s3_bucket:
                s3_key = f"{self.config.s3_prefix}/wal_archives/{wal_file}.gz"
                await self._upload_to_s3(archive_path, s3_key)
                record.s3_location = f"s3://{self.config.s3_bucket}/{s3_key}"
            
            record.status = BackupStatus.COMPLETED
            record.end_time = datetime.utcnow()
            
            logger.info(f"WAL archive completed: {wal_file}")
            
        except Exception as e:
            record.status = BackupStatus.FAILED
            record.error_message = str(e)
            record.end_time = datetime.utcnow()
            logger.error(f"WAL archive failed: {e}")
        
        self.backup_records.append(record)
        return record
    
    async def _upload_to_s3(self, file_path: Path, s3_key: str):
        """Upload backup file to S3."""
        try:
            self.s3_client.upload_file(
                str(file_path),
                self.config.s3_bucket,
                s3_key,
                ExtraArgs={
                    'StorageClass': self.config.s3_storage_class,
                    'ServerSideEncryption': 'AES256'
                }
            )
            logger.info(f"Uploaded to S3: s3://{self.config.s3_bucket}/{s3_key}")
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise
    
    async def _verify_backup(self, backup_file: Path) -> bool:
        """Verify backup integrity."""
        try:
            # For custom format backups, use pg_restore to list contents
            cmd = [
                'pg_restore',
                '--list',
                str(backup_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                logger.info(f"Backup verification successful: {backup_file}")
                return True
            else:
                logger.error(f"Backup verification failed: {backup_file}")
                return False
                
        except Exception as e:
            logger.error(f"Backup verification error: {e}")
            return False
    
    async def cleanup_old_backups(self):
        """Clean up backups older than retention period."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)
        
        # Clean up local files
        removed_count = 0
        for backup_file in self.config.backup_directory.glob("*.sql.gz"):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                backup_file.unlink()
                removed_count += 1
                logger.info(f"Removed old backup: {backup_file}")
        
        # Clean up WAL archives
        wal_archive_dir = self.config.backup_directory / "wal_archives"
        if wal_archive_dir.exists():
            for wal_file in wal_archive_dir.glob("*.gz"):
                if wal_file.stat().st_mtime < cutoff_date.timestamp():
                    wal_file.unlink()
                    removed_count += 1
        
        # Clean up S3 objects if configured
        if self.s3_client and self.config.s3_bucket:
            await self._cleanup_s3_backups(cutoff_date)
        
        # Update backup records
        active_records = [
            record for record in self.backup_records
            if record.start_time > cutoff_date
        ]
        expired_count = len(self.backup_records) - len(active_records)
        
        for record in self.backup_records:
            if record.start_time <= cutoff_date:
                record.status = BackupStatus.EXPIRED
        
        logger.info(f"Cleanup completed: {removed_count} files removed, {expired_count} records expired")
    
    async def _cleanup_s3_backups(self, cutoff_date: datetime):
        """Clean up old S3 backup objects."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.config.s3_bucket,
                Prefix=self.config.s3_prefix
            )
            
            if 'Contents' not in response:
                return
            
            objects_to_delete = []
            for obj in response['Contents']:
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                    objects_to_delete.append({'Key': obj['Key']})
            
            if objects_to_delete:
                self.s3_client.delete_objects(
                    Bucket=self.config.s3_bucket,
                    Delete={'Objects': objects_to_delete}
                )
                logger.info(f"Deleted {len(objects_to_delete)} old S3 backup objects")
                
        except ClientError as e:
            logger.error(f"S3 cleanup failed: {e}")
    
    async def schedule_daily_backups(self):
        """Schedule daily backup jobs."""
        logger.info(f"Scheduling daily backups at {self.config.daily_backup_time}")
        
        # Schedule full backup
        schedule.every().day.at(self.config.daily_backup_time).do(
            asyncio.create_task, self.run_daily_backup()
        )
        
        # Schedule incremental backups if enabled
        if self.config.enable_incremental:
            schedule.every(self.config.incremental_interval_hours).hours.do(
                asyncio.create_task, self.create_wal_archive_backup("current")
            )
        
        # Schedule cleanup
        schedule.every().day.at("04:00").do(
            asyncio.create_task, self.cleanup_old_backups()
        )
        
        logger.info("Backup schedules configured")
    
    async def run_daily_backup(self):
        """Run the daily backup routine."""
        logger.info("Starting daily backup routine")
        
        try:
            # Create full backup
            backup_record = await self.create_full_backup()
            
            if backup_record.status == BackupStatus.COMPLETED:
                logger.info("Daily backup completed successfully")
                
                # Send health check ping if configured
                if self.config.health_check_url:
                    await self._send_health_check_ping(True)
            else:
                logger.error("Daily backup failed")
                if self.config.alert_on_failure:
                    await self._send_failure_alert(backup_record)
                
                if self.config.health_check_url:
                    await self._send_health_check_ping(False)
        
        except Exception as e:
            logger.error(f"Daily backup routine failed: {e}")
            if self.config.alert_on_failure:
                await self._send_failure_alert(None, str(e))
    
    async def _send_health_check_ping(self, success: bool):
        """Send health check ping."""
        # This would integrate with your monitoring system
        pass
    
    async def _send_failure_alert(self, backup_record: Optional[BackupRecord], error: Optional[str] = None):
        """Send failure alert."""
        # This would integrate with your alerting system
        pass
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup statistics."""
        completed_backups = [r for r in self.backup_records if r.status == BackupStatus.COMPLETED]
        failed_backups = [r for r in self.backup_records if r.status == BackupStatus.FAILED]
        
        total_size = sum(r.file_size_bytes for r in completed_backups)
        total_compressed_size = sum(r.compressed_size_bytes for r in completed_backups)
        
        return {
            'total_backups': len(self.backup_records),
            'completed_backups': len(completed_backups),
            'failed_backups': len(failed_backups),
            'success_rate': len(completed_backups) / len(self.backup_records) * 100 if self.backup_records else 0,
            'total_data_backed_up_bytes': total_size,
            'total_compressed_size_bytes': total_compressed_size,
            'compression_ratio': (1 - total_compressed_size / total_size) * 100 if total_size > 0 else 0,
            'retention_days': self.config.retention_days,
            'latest_backup': max((r.start_time for r in completed_backups), default=None),
            'oldest_backup': min((r.start_time for r in completed_backups), default=None)
        }

# Global backup manager instance
_backup_manager: Optional[ProductionBackupManager] = None

def get_backup_manager() -> ProductionBackupManager:
    """Get or create backup manager instance."""
    global _backup_manager
    
    if _backup_manager is None:
        config = BackupConfig(
            database_host=os.getenv('POSTGRES_HOST_PRODUCTION', 'localhost'),
            database_port=int(os.getenv('POSTGRES_PORT_PRODUCTION', '5432')),
            database_name=os.getenv('POSTGRES_DB_PRODUCTION', 'ainflue_production'),
            database_user=os.getenv('POSTGRES_BACKUP_USER', 'backup_user'),
            database_password=os.getenv('POSTGRES_BACKUP_PASSWORD', ''),
            s3_bucket=os.getenv('BACKUP_S3_BUCKET'),
            retention_days=int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
        )
        
        _backup_manager = ProductionBackupManager(config)
    
    return _backup_manager

async def main():
    """Main function for running backup scheduler."""
    backup_manager = get_backup_manager()
    await backup_manager.schedule_daily_backups()
    
    logger.info("Backup scheduler running. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Backup scheduler stopped")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())