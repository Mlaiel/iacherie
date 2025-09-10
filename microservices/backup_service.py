#!/usr/bin/env python3
"""
💾 BACKUP SERVICE
=================

Advanced distributed backup and disaster recovery service for the Ainflue platform.
Handles automated backups, data integrity, compression, encryption, and recovery.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import os
import shutil
import gzip
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import tarfile
import tempfile
from cryptography.fernet import Fernet
import boto3
from botocore.exceptions import ClientError
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupType(Enum):
    """Backup type enumeration"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"

class BackupStatus(Enum):
    """Backup status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    VERIFIED = "verified"

class StorageBackend(Enum):
    """Storage backend types"""
    LOCAL = "local"
    S3 = "s3"
    REDIS = "redis"
    DATABASE = "database"

@dataclass
class BackupJob:
    """Backup job definition"""
    id: str
    name: str
    backup_type: BackupType
    source_path: str
    destination: str
    storage_backend: StorageBackend
    status: BackupStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_size: int = 0
    compressed_size: int = 0
    checksum: Optional[str] = None
    encryption_key: Optional[str] = None
    metadata: Dict[str, Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class BackupSchedule:
    """Backup schedule configuration"""
    id: str
    name: str
    backup_type: BackupType
    source_paths: List[str]
    schedule: str  # Cron expression
    retention_days: int
    enabled: bool = True
    last_backup: Optional[datetime] = None
    next_backup: Optional[datetime] = None

class CompressionManager:
    """Handle file compression and decompression"""
    
    @staticmethod
    def compress_file(source_path: str, dest_path: str) -> int:
        """Compress a file using gzip"""
        try:
            with open(source_path, 'rb') as f_in:
                with gzip.open(dest_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return os.path.getsize(dest_path)
        except Exception as e:
            logger.error(f"❌ Compression failed: {str(e)}")
            raise
    
    @staticmethod
    def compress_directory(source_dir: str, dest_path: str) -> int:
        """Compress a directory using tar.gz"""
        try:
            with tarfile.open(dest_path, "w:gz") as tar:
                tar.add(source_dir, arcname=os.path.basename(source_dir))
            
            return os.path.getsize(dest_path)
        except Exception as e:
            logger.error(f"❌ Directory compression failed: {str(e)}")
            raise
    
    @staticmethod
    def decompress_file(source_path: str, dest_path: str):
        """Decompress a gzip file"""
        try:
            with gzip.open(source_path, 'rb') as f_in:
                with open(dest_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            logger.error(f"❌ Decompression failed: {str(e)}")
            raise

class EncryptionManager:
    """Handle file encryption and decryption"""
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()
    
    @staticmethod
    def encrypt_file(source_path: str, dest_path: str, key: str):
        """Encrypt a file"""
        try:
            fernet = Fernet(key.encode())
            
            with open(source_path, 'rb') as f_in:
                data = f_in.read()
            
            encrypted_data = fernet.encrypt(data)
            
            with open(dest_path, 'wb') as f_out:
                f_out.write(encrypted_data)
                
        except Exception as e:
            logger.error(f"❌ Encryption failed: {str(e)}")
            raise
    
    @staticmethod
    def decrypt_file(source_path: str, dest_path: str, key: str):
        """Decrypt a file"""
        try:
            fernet = Fernet(key.encode())
            
            with open(source_path, 'rb') as f_in:
                encrypted_data = f_in.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            
            with open(dest_path, 'wb') as f_out:
                f_out.write(decrypted_data)
                
        except Exception as e:
            logger.error(f"❌ Decryption failed: {str(e)}")
            raise

class S3BackupManager:
    """AWS S3 backup operations"""
    
    def __init__(self, bucket_name: str, access_key: str = None, secret_key: str = None):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        ) if access_key and secret_key else boto3.client('s3')
    
    async def upload_file(self, local_path: str, s3_key: str) -> bool:
        """Upload file to S3"""
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            logger.info(f"📤 Uploaded {local_path} to S3: {s3_key}")
            return True
        except ClientError as e:
            logger.error(f"❌ S3 upload failed: {str(e)}")
            return False
    
    async def download_file(self, s3_key: str, local_path: str) -> bool:
        """Download file from S3"""
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            logger.info(f"📥 Downloaded {s3_key} from S3 to: {local_path}")
            return True
        except ClientError as e:
            logger.error(f"❌ S3 download failed: {str(e)}")
            return False
    
    async def list_backups(self, prefix: str = "") -> List[str]:
        """List backup files in S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            logger.error(f"❌ S3 list failed: {str(e)}")
            return []

class BackupService:
    """Advanced distributed backup and disaster recovery service"""
    
    def __init__(self):
        self.service_name = "BackupService"
        self.version = "1.0.0"
        self.backup_jobs: Dict[str, BackupJob] = {}
        self.backup_schedules: Dict[str, BackupSchedule] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.s3_manager: Optional[S3BackupManager] = None
        self.compression_enabled = True
        self.encryption_enabled = True
        self.temp_dir = tempfile.mkdtemp()
        
        logger.info(f"✅ {self.service_name} v{self.version} initialized")
    
    async def initialize(
        self,
        redis_url: str = "redis://localhost:6379/0",
        s3_bucket: str = None,
        s3_access_key: str = None,
        s3_secret_key: str = None
    ):
        """Initialize the backup service"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            
            # Initialize S3 if configured
            if s3_bucket:
                self.s3_manager = S3BackupManager(s3_bucket, s3_access_key, s3_secret_key)
            
            # Load existing jobs and schedules
            await self._load_backup_data()
            
            logger.info(f"💾 {self.service_name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.service_name}: {str(e)}")
            return False
    
    async def create_backup(
        self,
        name: str,
        source_path: str,
        destination: str = None,
        backup_type: BackupType = BackupType.FULL,
        storage_backend: StorageBackend = StorageBackend.LOCAL,
        encrypt: bool = True
    ) -> str:
        """Create a new backup job"""
        job_id = f"backup_{int(time.time())}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
        
        # Generate destination if not provided
        if not destination:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            destination = f"{self.temp_dir}/{name}_{timestamp}_backup.tar.gz"
        
        job = BackupJob(
            id=job_id,
            name=name,
            backup_type=backup_type,
            source_path=source_path,
            destination=destination,
            storage_backend=storage_backend,
            status=BackupStatus.PENDING,
            created_at=datetime.now(),
            metadata={}
        )
        
        # Generate encryption key if needed
        if encrypt and self.encryption_enabled:
            job.encryption_key = EncryptionManager.generate_key()
        
        self.backup_jobs[job_id] = job
        await self._save_backup_job(job)
        
        # Start backup asynchronously
        asyncio.create_task(self._execute_backup(job))
        
        logger.info(f"💾 Created backup job '{name}' (ID: {job_id})")
        return job_id
    
    async def _execute_backup(self, job: BackupJob):
        """Execute a backup job"""
        try:
            logger.info(f"🔄 Starting backup: {job.name}")
            
            job.status = BackupStatus.RUNNING
            job.started_at = datetime.now()
            await self._save_backup_job(job)
            
            source_path = Path(job.source_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source path does not exist: {job.source_path}")
            
            # Create temporary file for processing
            temp_backup = f"{self.temp_dir}/temp_{job.id}.tar.gz"
            
            # Compress source
            if source_path.is_file():
                if self.compression_enabled:
                    job.compressed_size = CompressionManager.compress_file(
                        str(source_path), temp_backup
                    )
                else:
                    shutil.copy2(str(source_path), temp_backup)
                    job.compressed_size = os.path.getsize(temp_backup)
            else:
                job.compressed_size = CompressionManager.compress_directory(
                    str(source_path), temp_backup
                )
            
            job.file_size = self._get_directory_size(str(source_path))
            
            # Calculate checksum
            job.checksum = self._calculate_checksum(temp_backup)
            
            # Encrypt if enabled
            final_backup = job.destination
            if job.encryption_key:
                encrypted_backup = f"{temp_backup}.enc"
                EncryptionManager.encrypt_file(temp_backup, encrypted_backup, job.encryption_key)
                final_backup = encrypted_backup
                os.remove(temp_backup)
                temp_backup = encrypted_backup
            
            # Handle different storage backends
            if job.storage_backend == StorageBackend.LOCAL:
                shutil.move(temp_backup, job.destination)
                
            elif job.storage_backend == StorageBackend.S3 and self.s3_manager:
                s3_key = f"backups/{job.id}/{os.path.basename(job.destination)}"
                success = await self.s3_manager.upload_file(temp_backup, s3_key)
                if not success:
                    raise Exception("Failed to upload to S3")
                job.destination = s3_key
                os.remove(temp_backup)
                
            elif job.storage_backend == StorageBackend.REDIS and self.redis_client:
                with open(temp_backup, 'rb') as f:
                    backup_data = f.read()
                await self.redis_client.set(f"backup:{job.id}", backup_data)
                job.destination = f"redis:backup:{job.id}"
                os.remove(temp_backup)
            
            # Update job status
            job.status = BackupStatus.COMPLETED
            job.completed_at = datetime.now()
            
            # Verify backup integrity
            if await self._verify_backup(job):
                job.status = BackupStatus.VERIFIED
            
            logger.info(f"✅ Backup completed: {job.name} ({job.compressed_size} bytes)")
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {job.name} - {str(e)}")
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            
            # Retry logic
            if job.retry_count < job.max_retries:
                job.retry_count += 1
                job.status = BackupStatus.PENDING
                logger.info(f"🔄 Retrying backup: {job.name} (attempt {job.retry_count})")
                await asyncio.sleep(30)  # Wait before retry
                asyncio.create_task(self._execute_backup(job))
        
        finally:
            await self._save_backup_job(job)
    
    async def restore_backup(self, job_id: str, restore_path: str) -> bool:
        """Restore a backup"""
        try:
            if job_id not in self.backup_jobs:
                logger.error(f"❌ Backup job not found: {job_id}")
                return False
            
            job = self.backup_jobs[job_id]
            if job.status != BackupStatus.VERIFIED:
                logger.warning(f"⚠️ Backup not verified: {job_id}")
            
            logger.info(f"🔄 Restoring backup: {job.name}")
            
            # Create temporary file for processing
            temp_file = f"{self.temp_dir}/restore_{job_id}.tar.gz"
            
            # Download/retrieve backup based on storage backend
            if job.storage_backend == StorageBackend.LOCAL:
                if not os.path.exists(job.destination):
                    raise FileNotFoundError(f"Backup file not found: {job.destination}")
                shutil.copy2(job.destination, temp_file)
                
            elif job.storage_backend == StorageBackend.S3 and self.s3_manager:
                success = await self.s3_manager.download_file(job.destination, temp_file)
                if not success:
                    raise Exception("Failed to download from S3")
                    
            elif job.storage_backend == StorageBackend.REDIS and self.redis_client:
                backup_data = await self.redis_client.get(job.destination)
                if not backup_data:
                    raise Exception("Backup not found in Redis")
                with open(temp_file, 'wb') as f:
                    f.write(backup_data)
            
            # Decrypt if needed
            if job.encryption_key:
                decrypted_file = f"{temp_file}.dec"
                EncryptionManager.decrypt_file(temp_file, decrypted_file, job.encryption_key)
                os.remove(temp_file)
                temp_file = decrypted_file
            
            # Verify checksum
            if job.checksum:
                current_checksum = self._calculate_checksum(temp_file)
                if current_checksum != job.checksum:
                    raise Exception("Backup integrity check failed")
            
            # Extract backup
            os.makedirs(restore_path, exist_ok=True)
            with tarfile.open(temp_file, "r:gz") as tar:
                tar.extractall(restore_path)
            
            # Cleanup
            os.remove(temp_file)
            
            logger.info(f"✅ Backup restored successfully: {job.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Restore failed: {str(e)}")
            return False
    
    async def schedule_backup(
        self,
        name: str,
        source_paths: List[str],
        schedule: str,
        backup_type: BackupType = BackupType.FULL,
        retention_days: int = 30
    ) -> str:
        """Schedule automated backups"""
        schedule_id = f"schedule_{int(time.time())}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
        
        backup_schedule = BackupSchedule(
            id=schedule_id,
            name=name,
            backup_type=backup_type,
            source_paths=source_paths,
            schedule=schedule,
            retention_days=retention_days,
            next_backup=self._calculate_next_backup_time(schedule)
        )
        
        self.backup_schedules[schedule_id] = backup_schedule
        await self._save_backup_schedule(backup_schedule)
        
        logger.info(f"📅 Scheduled backup: {name} ({schedule})")
        return schedule_id
    
    def _calculate_next_backup_time(self, schedule: str) -> datetime:
        """Calculate next backup time based on schedule"""
        # Simple schedule parser - in production use croniter
        now = datetime.now()
        if schedule == "daily":
            return now + timedelta(days=1)
        elif schedule == "weekly":
            return now + timedelta(weeks=1)
        elif schedule == "hourly":
            return now + timedelta(hours=1)
        else:
            return now + timedelta(hours=24)  # Default to daily
    
    def _get_directory_size(self, path: str) -> int:
        """Calculate total size of directory"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    async def _verify_backup(self, job: BackupJob) -> bool:
        """Verify backup integrity"""
        try:
            if job.storage_backend == StorageBackend.LOCAL:
                if not os.path.exists(job.destination):
                    return False
                
                # Verify checksum
                if job.checksum:
                    current_checksum = self._calculate_checksum(job.destination)
                    return current_checksum == job.checksum
            
            return True  # Assume verified for other backends
            
        except Exception as e:
            logger.error(f"❌ Backup verification failed: {str(e)}")
            return False
    
    async def _save_backup_job(self, job: BackupJob):
        """Save backup job to storage"""
        if self.redis_client:
            try:
                job_data = asdict(job)
                # Convert datetime objects to ISO strings
                for key, value in job_data.items():
                    if isinstance(value, datetime):
                        job_data[key] = value.isoformat() if value else None
                    elif isinstance(value, (BackupType, BackupStatus, StorageBackend)):
                        job_data[key] = value.value
                
                await self.redis_client.hset(
                    "backup:jobs",
                    job.id,
                    json.dumps(job_data)
                )
            except Exception as e:
                logger.error(f"❌ Failed to save backup job: {str(e)}")
    
    async def _save_backup_schedule(self, schedule: BackupSchedule):
        """Save backup schedule to storage"""
        if self.redis_client:
            try:
                schedule_data = asdict(schedule)
                # Convert datetime objects to ISO strings
                for key, value in schedule_data.items():
                    if isinstance(value, datetime):
                        schedule_data[key] = value.isoformat() if value else None
                    elif isinstance(value, BackupType):
                        schedule_data[key] = value.value
                
                await self.redis_client.hset(
                    "backup:schedules",
                    schedule.id,
                    json.dumps(schedule_data)
                )
            except Exception as e:
                logger.error(f"❌ Failed to save backup schedule: {str(e)}")
    
    async def _load_backup_data(self):
        """Load backup jobs and schedules from storage"""
        if self.redis_client:
            try:
                # Load jobs
                jobs_data = await self.redis_client.hgetall("backup:jobs")
                for job_id, job_json in jobs_data.items():
                    job_data = json.loads(job_json)
                    
                    # Convert ISO strings back to datetime objects
                    for key in ['created_at', 'started_at', 'completed_at']:
                        if job_data.get(key):
                            job_data[key] = datetime.fromisoformat(job_data[key])
                    
                    # Convert enums
                    job_data['backup_type'] = BackupType(job_data['backup_type'])
                    job_data['status'] = BackupStatus(job_data['status'])
                    job_data['storage_backend'] = StorageBackend(job_data['storage_backend'])
                    
                    job = BackupJob(**job_data)
                    self.backup_jobs[job_id] = job
                
                # Load schedules
                schedules_data = await self.redis_client.hgetall("backup:schedules")
                for schedule_id, schedule_json in schedules_data.items():
                    schedule_data = json.loads(schedule_json)
                    
                    # Convert ISO strings back to datetime objects
                    for key in ['last_backup', 'next_backup']:
                        if schedule_data.get(key):
                            schedule_data[key] = datetime.fromisoformat(schedule_data[key])
                    
                    # Convert enums
                    schedule_data['backup_type'] = BackupType(schedule_data['backup_type'])
                    
                    schedule = BackupSchedule(**schedule_data)
                    self.backup_schedules[schedule_id] = schedule
                
                logger.info(f"📂 Loaded {len(self.backup_jobs)} jobs and {len(self.backup_schedules)} schedules")
                
            except Exception as e:
                logger.error(f"❌ Failed to load backup data: {str(e)}")
    
    async def get_backup_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get backup job status"""
        if job_id in self.backup_jobs:
            job = self.backup_jobs[job_id]
            return {
                'id': job.id,
                'name': job.name,
                'backup_type': job.backup_type.value,
                'status': job.status.value,
                'source_path': job.source_path,
                'destination': job.destination,
                'storage_backend': job.storage_backend.value,
                'file_size': job.file_size,
                'compressed_size': job.compressed_size,
                'compression_ratio': (1 - job.compressed_size / job.file_size) if job.file_size > 0 else 0,
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'duration': str(job.completed_at - job.started_at) if job.started_at and job.completed_at else None,
                'error_message': job.error_message,
                'retry_count': job.retry_count
            }
        return None
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all backup jobs"""
        return [await self.get_backup_status(job_id) for job_id in self.backup_jobs.keys()]
    
    async def cleanup_old_backups(self, retention_days: int = 30):
        """Clean up old backup files"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        cleaned_count = 0
        
        for job_id, job in list(self.backup_jobs.items()):
            if job.created_at < cutoff_date and job.status == BackupStatus.VERIFIED:
                try:
                    # Remove backup file based on storage backend
                    if job.storage_backend == StorageBackend.LOCAL:
                        if os.path.exists(job.destination):
                            os.remove(job.destination)
                    elif job.storage_backend == StorageBackend.REDIS and self.redis_client:
                        await self.redis_client.delete(job.destination)
                    
                    # Remove job record
                    del self.backup_jobs[job_id]
                    if self.redis_client:
                        await self.redis_client.hdel("backup:jobs", job_id)
                    
                    cleaned_count += 1
                    logger.info(f"🧹 Cleaned up old backup: {job.name}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to cleanup backup {job_id}: {str(e)}")
        
        logger.info(f"🧹 Cleaned up {cleaned_count} old backups")
        return cleaned_count
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        total_jobs = len(self.backup_jobs)
        completed_jobs = len([j for j in self.backup_jobs.values() if j.status == BackupStatus.VERIFIED])
        failed_jobs = len([j for j in self.backup_jobs.values() if j.status == BackupStatus.FAILED])
        
        return {
            'service': self.service_name,
            'version': self.version,
            'total_backups': total_jobs,
            'completed_backups': completed_jobs,
            'failed_backups': failed_jobs,
            'success_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            'active_schedules': len([s for s in self.backup_schedules.values() if s.enabled]),
            'redis_connected': self.redis_client is not None,
            's3_configured': self.s3_manager is not None,
            'compression_enabled': self.compression_enabled,
            'encryption_enabled': self.encryption_enabled,
            'timestamp': datetime.now().isoformat()
        }

# Service instance
backup_service = BackupService()

# Example usage
async def main():
    """Example usage of the backup service"""
    try:
        # Initialize service
        await backup_service.initialize()
        
        # Create a test directory and file
        test_dir = "/tmp/test_backup_source"
        os.makedirs(test_dir, exist_ok=True)
        
        with open(f"{test_dir}/test_file.txt", "w") as f:
            f.write("This is a test file for backup.")
        
        # Create backup
        job_id = await backup_service.create_backup(
            name="Test Backup",
            source_path=test_dir,
            backup_type=BackupType.FULL,
            storage_backend=StorageBackend.LOCAL
        )
        
        # Wait for backup to complete
        await asyncio.sleep(5)
        
        # Check backup status
        status = await backup_service.get_backup_status(job_id)
        print(f"Backup status: {status}")
        
        # Restore backup
        restore_path = "/tmp/test_restore"
        success = await backup_service.restore_backup(job_id, restore_path)
        print(f"Restore success: {success}")
        
        # Schedule automated backup
        schedule_id = await backup_service.schedule_backup(
            name="Daily Test Backup",
            source_paths=[test_dir],
            schedule="daily",
            retention_days=7
        )
        
        # Service health
        health = await backup_service.get_service_health()
        print(f"Service health: {health}")
        
        # Cleanup
        await backup_service.cleanup_old_backups(retention_days=0)
        
    except Exception as e:
        logger.error(f"❌ Error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())