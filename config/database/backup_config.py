"""
Database Backup Configuration for IA-Influencer Agent Platform
=============================================================

Professional database backup and disaster recovery management for PostgreSQL,
MongoDB, Redis data persistence, and FAISS index backups across environments.

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
import json
import shutil
import subprocess
import gzip
import tarfile
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import logging
import threading
import schedule
from concurrent.futures import ThreadPoolExecutor
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs

logger = logging.getLogger(__name__)


class BackupEnvironment(Enum):
    """Backup environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class BackupType(Enum):
    """Backup operation types"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    POINT_IN_TIME = "point_in_time"


class BackupStatus(Enum):
    """Backup operation status"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class StorageProvider(Enum):
    """Cloud storage providers"""
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    SFTP = "sftp"


class DatabaseSystem(Enum):
    """Supported database systems for backup"""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    FAISS = "faiss"
    ELASTICSEARCH = "elasticsearch"


@dataclass
class BackupSchedule:
    """Backup schedule configuration"""
    backup_type: BackupType
    frequency: str  # cron-like: "daily", "weekly", "monthly", "0 2 * * *"
    retention_days: int = 30
    enabled: bool = True
    time_window: Optional[str] = None  # "02:00-04:00"
    max_parallel_backups: int = 3


@dataclass
class StorageConfig:
    """Storage configuration for different providers"""
    provider: StorageProvider
    local_path: Optional[str] = None
    aws_bucket: Optional[str] = None
    aws_region: Optional[str] = None
    azure_container: Optional[str] = None
    azure_account: Optional[str] = None
    gcp_bucket: Optional[str] = None
    gcp_project: Optional[str] = None
    encryption_enabled: bool = True
    compression_enabled: bool = True
    credentials: Dict[str, str] = field(default_factory=dict)


@dataclass
class BackupRecord:
    """Backup operation record"""
    backup_id: str
    database_system: DatabaseSystem
    backup_type: BackupType
    backup_name: str
    status: BackupStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PostgreSQLBackupManager:
    """PostgreSQL backup management using pg_dump/pg_restore"""
    
    def __init__(self, connection_string: str, config: StorageConfig):
        self.connection_string = connection_string
        self.config = config
        self.logger = logging.getLogger("postgresql_backup")

    def create_backup(self, backup_name: str, backup_type: BackupType = BackupType.FULL) -> BackupRecord:
        """Create PostgreSQL backup"""
        record = BackupRecord(
            backup_id=f"pg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{backup_name}",
            database_system=DatabaseSystem.POSTGRESQL,
            backup_type=backup_type,
            backup_name=backup_name,
            status=BackupStatus.RUNNING,
            started_at=datetime.now()
        )
        
        try:
            # Prepare backup file path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"postgresql_{backup_name}_{timestamp}.sql"
            
            if self.config.compression_enabled:
                filename += ".gz"
            
            backup_path = Path(self.config.local_path) / "postgresql" / filename
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare pg_dump command
            cmd = [
                "pg_dump",
                "--no-password",
                "--verbose",
                "--format=plain",
                "--no-owner",
                "--no-privileges"
            ]
            
            if backup_type == BackupType.FULL:
                cmd.extend(["--data-only", "--schema-only"])
            elif backup_type == BackupType.INCREMENTAL:
                # PostgreSQL doesn't have native incremental backup
                # This would require WAL-E or similar tools
                self.logger.warning("Incremental backup not natively supported, performing full backup")
            
            cmd.extend([
                "--file", str(backup_path) if not self.config.compression_enabled else "-",
                self.connection_string
            ])
            
            # Execute backup
            if self.config.compression_enabled:
                # Pipe to gzip
                pg_dump_process = subprocess.Popen(cmd[:-1] + [self.connection_string], 
                                                 stdout=subprocess.PIPE)
                
                with gzip.open(backup_path, 'wb') as f:
                    shutil.copyfileobj(pg_dump_process.stdout, f)
                
                pg_dump_process.wait()
                
                if pg_dump_process.returncode != 0:
                    raise subprocess.CalledProcessError(pg_dump_process.returncode, cmd)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Get file size
            file_size = backup_path.stat().st_size
            
            # Calculate checksum
            import hashlib
            checksum = hashlib.md5()
            with open(backup_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    checksum.update(chunk)
            
            # Update record
            record.status = BackupStatus.COMPLETED
            record.completed_at = datetime.now()
            record.duration_seconds = (record.completed_at - record.started_at).total_seconds()
            record.file_size_bytes = file_size
            record.file_path = str(backup_path)
            record.checksum = checksum.hexdigest()
            record.metadata = {
                "compression": self.config.compression_enabled,
                "format": "plain",
                "pg_dump_version": self._get_pg_dump_version()
            }
            
            self.logger.info(f"PostgreSQL backup completed: {record.backup_id}")
            
            # Upload to cloud storage if configured
            if self.config.provider != StorageProvider.LOCAL:
                self._upload_to_storage(backup_path, record)
            
            return record
            
        except Exception as e:
            record.status = BackupStatus.FAILED
            record.error_message = str(e)
            record.completed_at = datetime.now()
            record.duration_seconds = (record.completed_at - record.started_at).total_seconds()
            
            self.logger.error(f"PostgreSQL backup failed: {str(e)}")
            raise

    def restore_backup(self, backup_path: str, target_database: Optional[str] = None) -> bool:
        """Restore PostgreSQL backup"""
        try:
            # Prepare psql command
            cmd = ["psql", "--no-password", "--quiet"]
            
            if target_database:
                cmd.extend(["--dbname", target_database])
            else:
                cmd.append(self.connection_string)
            
            # Handle compressed files
            if backup_path.endswith('.gz'):
                with gzip.open(backup_path, 'rt') as f:
                    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True)
                    process.communicate(input=f.read())
                    
                    if process.returncode != 0:
                        raise subprocess.CalledProcessError(process.returncode, cmd)
            else:
                cmd.extend(["--file", backup_path])
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            self.logger.info(f"PostgreSQL restore completed: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"PostgreSQL restore failed: {str(e)}")
            raise

    def _get_pg_dump_version(self) -> str:
        """Get pg_dump version"""
        try:
            result = subprocess.run(["pg_dump", "--version"], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def _upload_to_storage(self, local_path: Path, record: BackupRecord) -> None:
        """Upload backup to cloud storage"""
        try:
            if self.config.provider == StorageProvider.AWS_S3:
                self._upload_to_s3(local_path, record)
            elif self.config.provider == StorageProvider.AZURE_BLOB:
                self._upload_to_azure(local_path, record)
            elif self.config.provider == StorageProvider.GOOGLE_CLOUD:
                self._upload_to_gcp(local_path, record)
        except Exception as e:
            self.logger.error(f"Cloud upload failed: {str(e)}")

    def _upload_to_s3(self, local_path: Path, record: BackupRecord) -> None:
        """Upload to AWS S3"""
        s3_client = boto3.client(
            's3',
            region_name=self.config.aws_region,
            aws_access_key_id=self.config.credentials.get('aws_access_key_id'),
            aws_secret_access_key=self.config.credentials.get('aws_secret_access_key')
        )
        
        s3_key = f"backups/postgresql/{record.backup_id}/{local_path.name}"
        s3_client.upload_file(str(local_path), self.config.aws_bucket, s3_key)
        
        record.metadata['cloud_path'] = f"s3://{self.config.aws_bucket}/{s3_key}"

    def _upload_to_azure(self, local_path: Path, record: BackupRecord) -> None:
        """Upload to Azure Blob Storage"""
        blob_service = BlobServiceClient(
            account_url=f"https://{self.config.azure_account}.blob.core.windows.net",
            credential=self.config.credentials.get('azure_key')
        )
        
        blob_name = f"backups/postgresql/{record.backup_id}/{local_path.name}"
        blob_client = blob_service.get_blob_client(
            container=self.config.azure_container, 
            blob=blob_name
        )
        
        with open(local_path, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)
        
        record.metadata['cloud_path'] = f"azure://{self.config.azure_account}/{self.config.azure_container}/{blob_name}"

    def _upload_to_gcp(self, local_path: Path, record: BackupRecord) -> None:
        """Upload to Google Cloud Storage"""
        client = gcs.Client(project=self.config.gcp_project)
        bucket = client.bucket(self.config.gcp_bucket)
        
        blob_name = f"backups/postgresql/{record.backup_id}/{local_path.name}"
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(local_path))
        
        record.metadata['cloud_path'] = f"gs://{self.config.gcp_bucket}/{blob_name}"


class MongoDBBackupManager:
    """MongoDB backup management using mongodump/mongorestore"""
    
    def __init__(self, connection_string: str, config: StorageConfig):
        self.connection_string = connection_string
        self.config = config
        self.logger = logging.getLogger("mongodb_backup")

    def create_backup(self, backup_name: str, 
                     database_name: Optional[str] = None,
                     collection_names: Optional[List[str]] = None) -> BackupRecord:
        """Create MongoDB backup"""
        record = BackupRecord(
            backup_id=f"mongo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{backup_name}",
            database_system=DatabaseSystem.MONGODB,
            backup_type=BackupType.FULL,
            backup_name=backup_name,
            status=BackupStatus.RUNNING,
            started_at=datetime.now()
        )
        
        try:
            # Prepare backup directory
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = Path(self.config.local_path) / "mongodb" / f"{backup_name}_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare mongodump command
            cmd = [
                "mongodump",
                "--uri", self.connection_string,
                "--out", str(backup_dir)
            ]
            
            if database_name:
                cmd.extend(["--db", database_name])
            
            if collection_names:
                for collection in collection_names:
                    cmd.extend(["--collection", collection])
            
            # Execute backup
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Compress backup if enabled
            if self.config.compression_enabled:
                archive_path = backup_dir.with_suffix('.tar.gz')
                with tarfile.open(archive_path, 'w:gz') as tar:
                    tar.add(backup_dir, arcname=backup_dir.name)
                
                # Remove uncompressed directory
                shutil.rmtree(backup_dir)
                final_path = archive_path
            else:
                final_path = backup_dir
            
            # Get file size
            if final_path.is_file():
                file_size = final_path.stat().st_size
            else:
                file_size = sum(f.stat().st_size for f in final_path.rglob('*') if f.is_file())
            
            # Update record
            record.status = BackupStatus.COMPLETED
            record.completed_at = datetime.now()
            record.duration_seconds = (record.completed_at - record.started_at).total_seconds()
            record.file_size_bytes = file_size
            record.file_path = str(final_path)
            record.metadata = {
                "compression": self.config.compression_enabled,
                "database": database_name,
                "collections": collection_names,
                "mongodump_version": self._get_mongodump_version()
            }
            
            self.logger.info(f"MongoDB backup completed: {record.backup_id}")
            return record
            
        except Exception as e:
            record.status = BackupStatus.FAILED
            record.error_message = str(e)
            record.completed_at = datetime.now()
            record.duration_seconds = (record.completed_at - record.started_at).total_seconds()
            
            self.logger.error(f"MongoDB backup failed: {str(e)}")
            raise

    def _get_mongodump_version(self) -> str:
        """Get mongodump version"""
        try:
            result = subprocess.run(["mongodump", "--version"], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            return "unknown"


class RedisBackupManager:
    """Redis backup management using RDB/AOF files"""
    
    def __init__(self, redis_client: Any, config: StorageConfig):
        self.redis_client = redis_client
        self.config = config
        self.logger = logging.getLogger("redis_backup")

    def create_backup(self, backup_name: str) -> BackupRecord:
        """Create Redis backup"""
        record = BackupRecord(
            backup_id=f"redis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{backup_name}",
            database_system=DatabaseSystem.REDIS,
            backup_type=BackupType.FULL,
            backup_name=backup_name,
            status=BackupStatus.RUNNING,
            started_at=datetime.now()
        )
        
        try:
            # Trigger BGSAVE
            self.redis_client.bgsave()
            
            # Wait for BGSAVE to complete
            import time
            while True:
                if self.redis_client.execute_command('LASTSAVE') != self.redis_client.execute_command('LASTSAVE'):
                    break
                time.sleep(1)
            
            # Copy RDB file
            redis_info = self.redis_client.config_get('dir')
            redis_dbfilename = self.redis_client.config_get('dbfilename')
            
            source_rdb = Path(redis_info['dir']) / redis_dbfilename['dbfilename']
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"redis_{backup_name}_{timestamp}.rdb"
            
            if self.config.compression_enabled:
                backup_filename += ".gz"
            
            backup_path = Path(self.config.local_path) / "redis" / backup_filename
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.config.compression_enabled:
                with open(source_rdb, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(source_rdb, backup_path)
            
            # Update record
            record.status = BackupStatus.COMPLETED
            record.completed_at = datetime.now()
            record.duration_seconds = (record.completed_at - record.started_at).total_seconds()
            record.file_size_bytes = backup_path.stat().st_size
            record.file_path = str(backup_path)
            record.metadata = {
                "compression": self.config.compression_enabled,
                "redis_version": self.redis_client.info()['redis_version']
            }
            
            self.logger.info(f"Redis backup completed: {record.backup_id}")
            return record
            
        except Exception as e:
            record.status = BackupStatus.FAILED
            record.error_message = str(e)
            record.completed_at = datetime.now()
            record.duration_seconds = (record.completed_at - record.started_at).total_seconds()
            
            self.logger.error(f"Redis backup failed: {str(e)}")
            raise


class BackupConfig:
    """
    Main backup configuration manager for IA-Influencer Agent Platform
    
    Orchestrates backup operations across all database systems with
    scheduling, retention management, and cloud storage integration.
    """
    
    def __init__(self, 
                 environment: BackupEnvironment = BackupEnvironment.DEVELOPMENT,
                 storage_config: Optional[StorageConfig] = None):
        self.environment = environment
        self.storage_config = storage_config or self._get_default_storage_config()
        self.schedules: Dict[str, BackupSchedule] = {}
        self.backup_managers: Dict[DatabaseSystem, Any] = {}
        self._backup_records: List[BackupRecord] = []
        self._scheduler_running = False
        self._executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="backup")
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup backup logging"""
        self.logger = logging.getLogger(f"backup_config.{self.environment.value}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _get_default_storage_config(self) -> StorageConfig:
        """Get default storage configuration"""
        if self.environment == BackupEnvironment.PRODUCTION:
            # Use cloud storage for production
            provider = StorageProvider.AWS_S3  # or based on environment variables
        else:
            provider = StorageProvider.LOCAL
        
        return StorageConfig(
            provider=provider,
            local_path=f"/data/backups/{self.environment.value}",
            compression_enabled=True,
            encryption_enabled=True
        )

    def register_postgresql_manager(self, connection_string: str) -> None:
        """Register PostgreSQL backup manager"""
        manager = PostgreSQLBackupManager(connection_string, self.storage_config)
        self.backup_managers[DatabaseSystem.POSTGRESQL] = manager
        self.logger.info("PostgreSQL backup manager registered")

    def register_mongodb_manager(self, connection_string: str) -> None:
        """Register MongoDB backup manager"""
        manager = MongoDBBackupManager(connection_string, self.storage_config)
        self.backup_managers[DatabaseSystem.MONGODB] = manager
        self.logger.info("MongoDB backup manager registered")

    def register_redis_manager(self, redis_client: Any) -> None:
        """Register Redis backup manager"""
        manager = RedisBackupManager(redis_client, self.storage_config)
        self.backup_managers[DatabaseSystem.REDIS] = manager
        self.logger.info("Redis backup manager registered")

    def add_backup_schedule(self, 
                           name: str, 
                           database_system: DatabaseSystem,
                           schedule: BackupSchedule) -> None:
        """Add backup schedule"""
        schedule_key = f"{database_system.value}_{name}"
        self.schedules[schedule_key] = schedule
        
        # Register with scheduler
        if schedule.frequency == "daily":
            schedule_obj = schedule
            schedule_time = "02:00"  # Default time
            
            # Extract time from time_window if provided
            if schedule.time_window:
                schedule_time = schedule.time_window.split('-')[0]
            
            def backup_job():
                self._execute_backup(database_system, name, schedule.backup_type)
            
            schedule.every().day.at(schedule_time).do(backup_job)
        
        self.logger.info(f"Backup schedule added: {schedule_key}")

    def _execute_backup(self, 
                       database_system: DatabaseSystem, 
                       backup_name: str,
                       backup_type: BackupType) -> None:
        """Execute backup operation"""
        try:
            if database_system not in self.backup_managers:
                raise ValueError(f"No backup manager registered for {database_system.value}")
            
            manager = self.backup_managers[database_system]
            
            # Submit backup task to executor
            future = self._executor.submit(
                manager.create_backup, 
                backup_name, 
                backup_type
            )
            
            # Store record
            record = future.result(timeout=3600)  # 1 hour timeout
            self._backup_records.append(record)
            
            # Cleanup old backups based on retention policy
            self._cleanup_old_backups(database_system, backup_name)
            
        except Exception as e:
            self.logger.error(f"Backup execution failed: {str(e)}")

    def _cleanup_old_backups(self, database_system: DatabaseSystem, backup_name: str) -> None:
        """Cleanup old backups based on retention policy"""
        try:
            schedule_key = f"{database_system.value}_{backup_name}"
            if schedule_key not in self.schedules:
                return
            
            retention_days = self.schedules[schedule_key].retention_days
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Find old backup records
            old_records = [
                record for record in self._backup_records
                if (record.database_system == database_system and
                    record.backup_name == backup_name and
                    record.started_at < cutoff_date and
                    record.status == BackupStatus.COMPLETED)
            ]
            
            # Remove old backup files
            for record in old_records:
                try:
                    if record.file_path and Path(record.file_path).exists():
                        if Path(record.file_path).is_file():
                            Path(record.file_path).unlink()
                        else:
                            shutil.rmtree(record.file_path)
                        
                        record.status = BackupStatus.EXPIRED
                        self.logger.info(f"Removed expired backup: {record.backup_id}")
                
                except Exception as e:
                    self.logger.error(f"Failed to remove backup {record.backup_id}: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {str(e)}")

    def start_scheduler(self) -> None:
        """Start backup scheduler"""
        if self._scheduler_running:
            return
        
        self._scheduler_running = True
        
        def scheduler_loop():
            while self._scheduler_running:
                schedule.run_pending()
                import time
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True, name="backup_scheduler")
        scheduler_thread.start()
        
        self.logger.info("Backup scheduler started")

    def stop_scheduler(self) -> None:
        """Stop backup scheduler"""
        self._scheduler_running = False
        self.logger.info("Backup scheduler stopped")

    def get_backup_status(self) -> Dict[str, Any]:
        """Get comprehensive backup status"""
        status = {
            "environment": self.environment.value,
            "scheduler_running": self._scheduler_running,
            "total_backups": len(self._backup_records),
            "backup_by_system": {},
            "backup_by_status": {},
            "recent_backups": [],
            "storage_config": {
                "provider": self.storage_config.provider.value,
                "compression": self.storage_config.compression_enabled,
                "encryption": self.storage_config.encryption_enabled
            }
        }
        
        # Count by system
        for record in self._backup_records:
            system = record.database_system.value
            status["backup_by_system"][system] = status["backup_by_system"].get(system, 0) + 1
            
            record_status = record.status.value
            status["backup_by_status"][record_status] = status["backup_by_status"].get(record_status, 0) + 1
        
        # Recent backups (last 10)
        recent_backups = sorted(self._backup_records, key=lambda x: x.started_at, reverse=True)[:10]
        status["recent_backups"] = [
            {
                "backup_id": record.backup_id,
                "system": record.database_system.value,
                "status": record.status.value,
                "started_at": record.started_at.isoformat(),
                "duration_seconds": record.duration_seconds,
                "file_size_mb": round(record.file_size_bytes / 1024 / 1024, 2) if record.file_size_bytes else None
            }
            for record in recent_backups
        ]
        
        return status

    def health_check(self) -> Dict[str, Any]:
        """Perform backup system health check"""
        health_status = {
            "status": "healthy",
            "environment": self.environment.value,
            "managers": {},
            "storage": {},
            "scheduler": {
                "running": self._scheduler_running,
                "active_schedules": len(self.schedules)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Check storage accessibility
            storage_path = Path(self.storage_config.local_path)
            if not storage_path.exists():
                storage_path.mkdir(parents=True, exist_ok=True)
            
            # Test write access
            test_file = storage_path / "health_check.tmp"
            test_file.write_text("test")
            test_file.unlink()
            
            health_status["storage"] = {
                "status": "healthy",
                "local_path": str(storage_path),
                "writable": True
            }
            
            # Check managers
            for db_system, manager in self.backup_managers.items():
                health_status["managers"][db_system.value] = {
                    "status": "healthy",
                    "registered": True
                }
            
            return health_status
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self.logger.error(f"Backup health check failed: {str(e)}")
            return health_status

    def close(self) -> None:
        """Close backup configuration and cleanup resources"""
        self.stop_scheduler()
        self._executor.shutdown(wait=True)
        self.logger.info("Backup configuration closed")
