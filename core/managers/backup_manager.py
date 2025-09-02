"""Backup Manager - Enterprise-Grade Data Backup and Recovery System
=====================================================================

Industrial-strength backup management system with automated scheduling,
multi-tier backup strategies, and disaster recovery capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY CODE - UNAUTHORIZED USE PROHIBITED ⚠️
This implementation is the exclusive intellectual property of Fahed Mlaiel.
"""

import asyncio
import logging
import os
import json
import gzip
import tarfile
import shutil
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import tempfile
import hashlib

try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Types of backup operations"""
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
    CORRUPTED = "corrupted"


class BackupDestination(Enum):
    """Backup storage destinations"""
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCP = "gcp"
    SFTP = "sftp"


@dataclass
class BackupConfig:
    """Backup configuration settings"""
    name: str
    backup_type: BackupType
    source_paths: List[str]
    destination: BackupDestination
    destination_config: Dict[str, Any]
    schedule_cron: Optional[str] = None
    retention_days: int = 30
    compression: bool = True
    encryption: bool = True
    verification: bool = True
    max_parallel_jobs: int = 3


@dataclass
class BackupJob:
    """Individual backup job"""
    job_id: str
    config: BackupConfig
    status: BackupStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_count: int = 0
    total_size: int = 0
    compressed_size: int = 0
    error_message: Optional[str] = None
    backup_path: Optional[str] = None
    checksum: Optional[str] = None


class BackupManager:
    """Enterprise-grade backup management system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize backup manager"""
        self.configs: Dict[str, BackupConfig] = {}
        self.active_jobs: Dict[str, BackupJob] = {}
        self.job_history: List[BackupJob] = []
        self.redis_client = None
        self.s3_client = None
        
        # Initialize storage backends
        self._initialize_storage_backends()
        
        # Load configuration
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
        
        logger.info("BackupManager initialized successfully")
    
    def _initialize_storage_backends(self):
        """Initialize storage backend clients"""
        try:
            if REDIS_AVAILABLE:
                self.redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    decode_responses=True
                )
                logger.info("Redis client initialized for backup metadata")
            
            if AWS_AVAILABLE:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('AWS_REGION', 'us-east-1')
                )
                logger.info("S3 client initialized for cloud backups")
                
        except Exception as e:
            logger.warning(f"Failed to initialize some storage backends: {e}")
    
    def _load_config(self, config_path: str):
        """Load backup configurations from file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            for name, config in config_data.get('backup_configs', {}).items():
                self.configs[name] = BackupConfig(
                    name=name,
                    backup_type=BackupType(config['backup_type']),
                    source_paths=config['source_paths'],
                    destination=BackupDestination(config['destination']),
                    destination_config=config['destination_config'],
                    schedule_cron=config.get('schedule_cron'),
                    retention_days=config.get('retention_days', 30),
                    compression=config.get('compression', True),
                    encryption=config.get('encryption', True),
                    verification=config.get('verification', True),
                    max_parallel_jobs=config.get('max_parallel_jobs', 3)
                )
            
            logger.info(f"Loaded {len(self.configs)} backup configurations")
            
        except Exception as e:
            logger.error(f"Failed to load backup config: {e}")
    
    async def create_backup(self, config_name: str) -> str:
        """Create a backup job"""
        if config_name not in self.configs:
            raise ValueError(f"Backup configuration '{config_name}' not found")
        
        config = self.configs[config_name]
        job_id = f"backup_{config_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        job = BackupJob(
            job_id=job_id,
            config=config,
            status=BackupStatus.PENDING,
            created_at=datetime.now(timezone.utc)
        )
        
        self.active_jobs[job_id] = job
        
        # Start backup process asynchronously
        asyncio.create_task(self._execute_backup(job))
        
        logger.info(f"Backup job {job_id} created and queued")
        return job_id
    
    async def _execute_backup(self, job: BackupJob):
        """Execute backup operation"""
        try:
            job.status = BackupStatus.IN_PROGRESS
            job.started_at = datetime.now(timezone.utc)
            
            logger.info(f"Starting backup job {job.job_id}")
            
            # Create temporary working directory
            with tempfile.TemporaryDirectory() as temp_dir:
                backup_path = os.path.join(temp_dir, f"{job.job_id}.tar.gz")
                
                # Collect and archive files
                await self._create_archive(job, backup_path)
                
                # Verify backup integrity
                if job.config.verification:
                    await self._verify_backup(job, backup_path)
                
                # Upload to destination
                final_path = await self._upload_backup(job, backup_path)
                job.backup_path = final_path
                
                # Update job status
                job.status = BackupStatus.COMPLETED
                job.completed_at = datetime.now(timezone.utc)
                
                # Store metadata
                await self._store_backup_metadata(job)
                
                logger.info(f"Backup job {job.job_id} completed successfully")
        
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            logger.error(f"Backup job {job.job_id} failed: {e}")
        
        finally:
            # Move from active to history
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
            self.job_history.append(job)
    
    async def _create_archive(self, job: BackupJob, backup_path: str):
        """Create backup archive from source paths"""
        total_size = 0
        file_count = 0
        
        mode = 'w:gz' if job.config.compression else 'w'
        
        with tarfile.open(backup_path, mode) as tar:
            for source_path in job.config.source_paths:
                if os.path.exists(source_path):
                    if os.path.isfile(source_path):
                        tar.add(source_path, arcname=os.path.basename(source_path))
                        total_size += os.path.getsize(source_path)
                        file_count += 1
                    elif os.path.isdir(source_path):
                        for root, dirs, files in os.walk(source_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                if os.path.exists(file_path):
                                    arcname = os.path.relpath(file_path, os.path.dirname(source_path))
                                    tar.add(file_path, arcname=arcname)
                                    total_size += os.path.getsize(file_path)
                                    file_count += 1
        
        job.total_size = total_size
        job.file_count = file_count
        job.compressed_size = os.path.getsize(backup_path)
        
        # Calculate checksum
        job.checksum = await self._calculate_checksum(backup_path)
        
        logger.info(f"Archive created: {file_count} files, {total_size} bytes -> {job.compressed_size} bytes")
    
    async def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of backup file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    async def _verify_backup(self, job: BackupJob, backup_path: str):
        """Verify backup integrity"""
        try:
            # Test archive can be opened
            mode = 'r:gz' if job.config.compression else 'r'
            with tarfile.open(backup_path, mode) as tar:
                # Verify all members can be read
                for member in tar.getmembers():
                    if member.isfile():
                        try:
                            tar.extractfile(member).read(1024)  # Read first KB
                        except Exception as e:
                            raise Exception(f"Failed to read member {member.name}: {e}")
            
            logger.info(f"Backup verification successful for {job.job_id}")
            
        except Exception as e:
            raise Exception(f"Backup verification failed: {e}")
    
    async def _upload_backup(self, job: BackupJob, backup_path: str) -> str:
        """Upload backup to configured destination"""
        destination = job.config.destination
        
        if destination == BackupDestination.LOCAL:
            return await self._upload_to_local(job, backup_path)
        elif destination == BackupDestination.S3:
            return await self._upload_to_s3(job, backup_path)
        elif destination == BackupDestination.AZURE:
            return await self._upload_to_azure(job, backup_path)
        elif destination == BackupDestination.GCP:
            return await self._upload_to_gcp(job, backup_path)
        elif destination == BackupDestination.SFTP:
            return await self._upload_to_sftp(job, backup_path)
        else:
            raise ValueError(f"Unsupported backup destination: {destination}")
    
    async def _upload_to_local(self, job: BackupJob, backup_path: str) -> str:
        """Upload backup to local filesystem"""
        dest_config = job.config.destination_config
        dest_dir = dest_config.get('path', '/tmp/backups')
        
        # Ensure destination directory exists
        os.makedirs(dest_dir, exist_ok=True)
        
        # Copy backup file
        dest_path = os.path.join(dest_dir, os.path.basename(backup_path))
        shutil.copy2(backup_path, dest_path)
        
        logger.info(f"Backup uploaded to local path: {dest_path}")
        return dest_path
    
    async def _upload_to_s3(self, job: BackupJob, backup_path: str) -> str:
        """Upload backup to Amazon S3"""
        if not self.s3_client:
            raise Exception("S3 client not initialized")
        
        dest_config = job.config.destination_config
        bucket = dest_config.get('bucket')
        prefix = dest_config.get('prefix', 'backups')
        
        if not bucket:
            raise ValueError("S3 bucket not configured")
        
        # Upload file
        key = f"{prefix}/{job.job_id}/{os.path.basename(backup_path)}"
        
        try:
            self.s3_client.upload_file(backup_path, bucket, key)
            s3_path = f"s3://{bucket}/{key}"
            logger.info(f"Backup uploaded to S3: {s3_path}")
            return s3_path
            
        except ClientError as e:
            raise Exception(f"S3 upload failed: {e}")
    
    async def _upload_to_azure(self, job: BackupJob, backup_path: str) -> str:
        """Upload backup to Azure Blob Storage"""
        try:
            from azure.storage.blob.aio import BlobServiceClient
        except ImportError:
            raise Exception("Azure Storage library not installed. Install with: pip install azure-storage-blob")
        
        dest_config = job.config.destination_config
        connection_string = dest_config.get('connection_string')
        container_name = dest_config.get('container', 'backups')
        
        if not connection_string:
            raise ValueError("Azure connection string not configured")
        
        blob_name = f"{job.job_id}/{os.path.basename(backup_path)}"
        
        try:
            async with BlobServiceClient.from_connection_string(connection_string) as blob_service_client:
                blob_client = blob_service_client.get_blob_client(
                    container=container_name, 
                    blob=blob_name
                )
                
                with open(backup_path, 'rb') as data:
                    await blob_client.upload_blob(data, overwrite=True)
                
                azure_path = f"azure://{container_name}/{blob_name}"
                logger.info(f"Backup uploaded to Azure: {azure_path}")
                return azure_path
                
        except Exception as e:
            raise Exception(f"Azure upload failed: {e}")
    
    async def _upload_to_gcp(self, job: BackupJob, backup_path: str) -> str:
        """Upload backup to Google Cloud Storage"""
        try:
            from google.cloud import storage
        except ImportError:
            raise Exception("Google Cloud Storage library not installed. Install with: pip install google-cloud-storage")
        
        dest_config = job.config.destination_config
        bucket_name = dest_config.get('bucket')
        credentials_path = dest_config.get('credentials_path')
        
        if not bucket_name:
            raise ValueError("GCP bucket name not configured")
        
        # Initialize client
        if credentials_path and os.path.exists(credentials_path):
            client = storage.Client.from_service_account_json(credentials_path)
        else:
            # Use default credentials
            client = storage.Client()
        
        blob_name = f"{job.job_id}/{os.path.basename(backup_path)}"
        
        try:
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            blob.upload_from_filename(backup_path)
            
            gcp_path = f"gs://{bucket_name}/{blob_name}"
            logger.info(f"Backup uploaded to GCP: {gcp_path}")
            return gcp_path
            
        except Exception as e:
            raise Exception(f"GCP upload failed: {e}")
    
    async def _upload_to_sftp(self, job: BackupJob, backup_path: str) -> str:
        """Upload backup to SFTP server"""
        try:
            import asyncssh
        except ImportError:
            raise Exception("AsyncSSH library not installed. Install with: pip install asyncssh")
        
        dest_config = job.config.destination_config
        host = dest_config.get('host')
        port = dest_config.get('port', 22)
        username = dest_config.get('username')
        password = dest_config.get('password')
        private_key = dest_config.get('private_key')
        remote_path = dest_config.get('remote_path', '/backups')
        
        if not host or not username:
            raise ValueError("SFTP host and username must be configured")
        
        remote_file_path = f"{remote_path}/{job.job_id}/{os.path.basename(backup_path)}"
        
        try:
            # Setup connection options
            connect_kwargs = {
                'host': host,
                'port': port,
                'username': username,
                'known_hosts': None  # Skip host key verification for simplicity
            }
            
            if private_key:
                connect_kwargs['client_keys'] = [private_key]
            elif password:
                connect_kwargs['password'] = password
            else:
                raise ValueError("Either password or private key must be provided for SFTP")
            
            async with asyncssh.connect(**connect_kwargs) as conn:
                async with conn.start_sftp_client() as sftp:
                    # Create remote directory if needed
                    remote_dir = os.path.dirname(remote_file_path)
                    try:
                        await sftp.makedirs(remote_dir)
                    except Exception:
                        pass  # Directory might already exist
                    
                    # Upload file
                    await sftp.put(backup_path, remote_file_path)
                    
                    sftp_path = f"sftp://{host}:{port}{remote_file_path}"
                    logger.info(f"Backup uploaded to SFTP: {sftp_path}")
                    return sftp_path
                    
        except Exception as e:
            raise Exception(f"SFTP upload failed: {e}")
    
    async def _store_backup_metadata(self, job: BackupJob):
        """Store backup metadata for tracking"""
        metadata = {
            'job_id': job.job_id,
            'config_name': job.config.name,
            'status': job.status.value,
            'created_at': job.created_at.isoformat(),
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'file_count': job.file_count,
            'total_size': job.total_size,
            'compressed_size': job.compressed_size,
            'backup_path': job.backup_path,
            'checksum': job.checksum
        }
        
        if self.redis_client:
            try:
                await self.redis_client.hset(
                    f"backup_metadata:{job.job_id}",
                    mapping=metadata
                )
                await self.redis_client.expire(
                    f"backup_metadata:{job.job_id}",
                    job.config.retention_days * 24 * 3600
                )
                logger.info(f"Backup metadata stored for {job.job_id}")
            except Exception as e:
                logger.warning(f"Failed to store backup metadata: {e}")
    
    async def get_backup_status(self, job_id: str) -> Optional[BackupJob]:
        """Get status of a backup job"""
        # Check active jobs first
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        
        # Check job history
        for job in self.job_history:
            if job.job_id == job_id:
                return job
        
        return None
    
    async def list_backups(self, config_name: Optional[str] = None) -> List[BackupJob]:
        """List backup jobs, optionally filtered by configuration"""
        all_jobs = list(self.active_jobs.values()) + self.job_history
        
        if config_name:
            return [job for job in all_jobs if job.config.name == config_name]
        
        return all_jobs
    
    async def restore_backup(self, job_id: str, restore_path: str) -> bool:
        """Restore from a backup"""
        job = await self.get_backup_status(job_id)
        if not job or job.status != BackupStatus.COMPLETED:
            logger.error(f"Backup job {job_id} not found or not completed")
            return False
        
        try:
            # Download backup if needed
            backup_file = await self._download_backup(job)
            
            # Extract backup
            mode = 'r:gz' if job.config.compression else 'r'
            with tarfile.open(backup_file, mode) as tar:
                tar.extractall(restore_path)
            
            logger.info(f"Backup {job_id} restored to {restore_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup {job_id}: {e}")
            return False
    
    async def _download_backup(self, job: BackupJob) -> str:
        """Download backup file from storage destination"""
        if job.config.destination == BackupDestination.LOCAL:
            return job.backup_path
        elif job.config.destination == BackupDestination.S3:
            return await self._download_from_s3(job)
        elif job.config.destination == BackupDestination.AZURE:
            return await self._download_from_azure(job)
        elif job.config.destination == BackupDestination.GCP:
            return await self._download_from_gcp(job)
        elif job.config.destination == BackupDestination.SFTP:
            return await self._download_from_sftp(job)
        else:
            raise NotImplementedError(f"Download from {job.config.destination} not implemented")
    
    async def _download_from_s3(self, job: BackupJob) -> str:
        """Download backup from S3 to temporary file"""
        if not self.s3_client:
            raise Exception("S3 client not initialized")
        
        # Parse S3 path
        s3_path = job.backup_path
        if not s3_path.startswith('s3://'):
            raise ValueError(f"Invalid S3 path: {s3_path}")
        
        path_parts = s3_path[5:].split('/', 1)
        bucket = path_parts[0]
        key = path_parts[1]
        
        # Download to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz')
        temp_file.close()
        
        try:
            self.s3_client.download_file(bucket, key, temp_file.name)
            return temp_file.name
        except ClientError as e:
            os.unlink(temp_file.name)
            raise Exception(f"Failed to download from S3: {e}")
    
    async def _download_from_azure(self, job: BackupJob) -> str:
        """Download backup from Azure Blob Storage to temporary file"""
        try:
            from azure.storage.blob.aio import BlobServiceClient
        except ImportError:
            raise Exception("Azure Storage library not installed")
        
        # Parse Azure path
        azure_path = job.backup_path
        if not azure_path.startswith('azure://'):
            raise ValueError(f"Invalid Azure path: {azure_path}")
        
        path_parts = azure_path[8:].split('/', 1)
        container = path_parts[0]
        blob_name = path_parts[1]
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz')
        temp_file.close()
        
        try:
            dest_config = job.config.destination_config
            connection_string = dest_config.get('connection_string')
            
            async with BlobServiceClient.from_connection_string(connection_string) as blob_service_client:
                blob_client = blob_service_client.get_blob_client(
                    container=container, 
                    blob=blob_name
                )
                
                with open(temp_file.name, 'wb') as download_file:
                    download_stream = await blob_client.download_blob()
                    async for chunk in download_stream.chunks():
                        download_file.write(chunk)
                
                return temp_file.name
                
        except Exception as e:
            os.unlink(temp_file.name)
            raise Exception(f"Failed to download from Azure: {e}")
    
    async def _download_from_gcp(self, job: BackupJob) -> str:
        """Download backup from Google Cloud Storage to temporary file"""
        try:
            from google.cloud import storage
        except ImportError:
            raise Exception("Google Cloud Storage library not installed")
        
        # Parse GCP path
        gcp_path = job.backup_path
        if not gcp_path.startswith('gs://'):
            raise ValueError(f"Invalid GCP path: {gcp_path}")
        
        path_parts = gcp_path[5:].split('/', 1)
        bucket_name = path_parts[0]
        blob_name = path_parts[1]
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz')
        temp_file.close()
        
        try:
            dest_config = job.config.destination_config
            credentials_path = dest_config.get('credentials_path')
            
            # Initialize client
            if credentials_path and os.path.exists(credentials_path):
                client = storage.Client.from_service_account_json(credentials_path)
            else:
                client = storage.Client()
            
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            blob.download_to_filename(temp_file.name)
            return temp_file.name
            
        except Exception as e:
            os.unlink(temp_file.name)
            raise Exception(f"Failed to download from GCP: {e}")
    
    async def _download_from_sftp(self, job: BackupJob) -> str:
        """Download backup from SFTP server to temporary file"""
        try:
            import asyncssh
        except ImportError:
            raise Exception("AsyncSSH library not installed")
        
        # Parse SFTP path
        sftp_path = job.backup_path
        if not sftp_path.startswith('sftp://'):
            raise ValueError(f"Invalid SFTP path: {sftp_path}")
        
        # Extract host, port, and file path
        path_without_protocol = sftp_path[7:]  # Remove sftp://
        if ':' in path_without_protocol:
            host_port, file_path = path_without_protocol.split('/', 1)
            if ':' in host_port:
                host, port = host_port.split(':')
                port = int(port)
            else:
                host = host_port
                port = 22
            file_path = '/' + file_path
        else:
            parts = path_without_protocol.split('/', 1)
            host = parts[0]
            port = 22
            file_path = '/' + parts[1] if len(parts) > 1 else '/'
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz')
        temp_file.close()
        
        try:
            dest_config = job.config.destination_config
            username = dest_config.get('username')
            password = dest_config.get('password')
            private_key = dest_config.get('private_key')
            
            # Setup connection options
            connect_kwargs = {
                'host': host,
                'port': port,
                'username': username,
                'known_hosts': None
            }
            
            if private_key:
                connect_kwargs['client_keys'] = [private_key]
            elif password:
                connect_kwargs['password'] = password
            
            async with asyncssh.connect(**connect_kwargs) as conn:
                async with conn.start_sftp_client() as sftp:
                    await sftp.get(file_path, temp_file.name)
                    return temp_file.name
                    
        except Exception as e:
            os.unlink(temp_file.name)
            raise Exception(f"Failed to download from SFTP: {e}")
    
    async def cleanup_old_backups(self):
        """Clean up old backups based on retention policies"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)  # Default retention
        
        for config in self.configs.values():
            retention_cutoff = datetime.now(timezone.utc) - timedelta(days=config.retention_days)
            
            # Clean up completed jobs older than retention period
            jobs_to_remove = []
            for job in self.job_history:
                if (job.config.name == config.name and 
                    job.status == BackupStatus.COMPLETED and 
                    job.completed_at and 
                    job.completed_at < retention_cutoff):
                    
                    try:
                        # Delete backup file
                        await self._delete_backup_file(job)
                        jobs_to_remove.append(job)
                        logger.info(f"Cleaned up old backup: {job.job_id}")
                    except Exception as e:
                        logger.error(f"Failed to clean up backup {job.job_id}: {e}")
            
            # Remove from history
            for job in jobs_to_remove:
                self.job_history.remove(job)
    
    async def _delete_backup_file(self, job: BackupJob):
        """Delete backup file from storage"""
        if job.config.destination == BackupDestination.LOCAL:
            if job.backup_path and os.path.exists(job.backup_path):
                os.unlink(job.backup_path)
        elif job.config.destination == BackupDestination.S3:
            await self._delete_from_s3(job)
        elif job.config.destination == BackupDestination.AZURE:
            await self._delete_from_azure(job)
        elif job.config.destination == BackupDestination.GCP:
            await self._delete_from_gcp(job)
        elif job.config.destination == BackupDestination.SFTP:
            await self._delete_from_sftp(job)
    
    async def _delete_from_s3(self, job: BackupJob):
        """Delete backup from S3"""
        if not self.s3_client or not job.backup_path:
            return
        
        try:
            # Parse S3 path
            s3_path = job.backup_path
            path_parts = s3_path[5:].split('/', 1)
            bucket = path_parts[0]
            key = path_parts[1]
            
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            
        except ClientError as e:
            logger.error(f"Failed to delete S3 backup: {e}")
    
    async def _delete_from_azure(self, job: BackupJob):
        """Delete backup from Azure Blob Storage"""
        try:
            from azure.storage.blob.aio import BlobServiceClient
        except ImportError:
            logger.error("Azure Storage library not installed")
            return
        
        if not job.backup_path:
            return
        
        try:
            # Parse Azure path
            azure_path = job.backup_path
            path_parts = azure_path[8:].split('/', 1)  # Remove azure://
            container = path_parts[0]
            blob_name = path_parts[1]
            
            dest_config = job.config.destination_config
            connection_string = dest_config.get('connection_string')
            
            async with BlobServiceClient.from_connection_string(connection_string) as blob_service_client:
                blob_client = blob_service_client.get_blob_client(
                    container=container, 
                    blob=blob_name
                )
                await blob_client.delete_blob()
                
        except Exception as e:
            logger.error(f"Failed to delete Azure backup: {e}")
    
    async def _delete_from_gcp(self, job: BackupJob):
        """Delete backup from Google Cloud Storage"""
        try:
            from google.cloud import storage
        except ImportError:
            logger.error("Google Cloud Storage library not installed")
            return
        
        if not job.backup_path:
            return
        
        try:
            # Parse GCP path
            gcp_path = job.backup_path
            path_parts = gcp_path[5:].split('/', 1)  # Remove gs://
            bucket_name = path_parts[0]
            blob_name = path_parts[1]
            
            dest_config = job.config.destination_config
            credentials_path = dest_config.get('credentials_path')
            
            # Initialize client
            if credentials_path and os.path.exists(credentials_path):
                client = storage.Client.from_service_account_json(credentials_path)
            else:
                client = storage.Client()
            
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()
            
        except Exception as e:
            logger.error(f"Failed to delete GCP backup: {e}")
    
    async def _delete_from_sftp(self, job: BackupJob):
        """Delete backup from SFTP server"""
        try:
            import asyncssh
        except ImportError:
            logger.error("AsyncSSH library not installed")
            return
        
        if not job.backup_path:
            return
        
        try:
            # Parse SFTP path (similar to download)
            sftp_path = job.backup_path
            path_without_protocol = sftp_path[7:]  # Remove sftp://
            
            if ':' in path_without_protocol:
                host_port, file_path = path_without_protocol.split('/', 1)
                if ':' in host_port:
                    host, port = host_port.split(':')
                    port = int(port)
                else:
                    host = host_port
                    port = 22
                file_path = '/' + file_path
            else:
                parts = path_without_protocol.split('/', 1)
                host = parts[0]
                port = 22
                file_path = '/' + parts[1] if len(parts) > 1 else '/'
            
            dest_config = job.config.destination_config
            username = dest_config.get('username')
            password = dest_config.get('password')
            private_key = dest_config.get('private_key')
            
            # Setup connection options
            connect_kwargs = {
                'host': host,
                'port': port,
                'username': username,
                'known_hosts': None
            }
            
            if private_key:
                connect_kwargs['client_keys'] = [private_key]
            elif password:
                connect_kwargs['password'] = password
            
            async with asyncssh.connect(**connect_kwargs) as conn:
                async with conn.start_sftp_client() as sftp:
                    await sftp.remove(file_path)
                    
        except Exception as e:
            logger.error(f"Failed to delete SFTP backup: {e}")


# Global backup manager instance
_backup_manager = None


def get_backup_manager() -> BackupManager:
    """Get singleton backup manager instance"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager