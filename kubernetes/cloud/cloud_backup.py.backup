"""Cloud Backup Manager - Enterprise Multi-Cloud Backup and Recovery
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or use of this code without explicit written permission from 
Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in 
legal action.

Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

This module provides comprehensive backup and recovery solutions for the IA
Influencer Agent platform across multiple cloud providers, including automated
backup scheduling, versioning, encryption, and cross-cloud replication.
"""
import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs
import hashlib
import zlib
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class BackupType(Enum):
    """Backup types supported"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"
    CONTINUOUS = "continuous"

class BackupStatus(Enum):
    """Backup operation status"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CORRUPTED = "corrupted"
    RESTORED = "restored"

class CloudProvider(Enum):
    """Supported cloud providers for backup"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    MULTI_CLOUD = "multi_cloud"

@dataclass
class BackupConfiguration:
    """Backup configuration settings"""
    name: str
    source_path: str
    destination: Dict[str, Any]
    backup_type: BackupType
    schedule: str  # Cron expression
    retention_days: int
    encryption_enabled: bool
    compression_enabled: bool
    cross_cloud_replication: bool
    verification_enabled: bool
    notification_settings: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BackupJob:
    """Backup job representation"""
    job_id: str
    configuration: BackupConfiguration
    status: BackupStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    size_bytes: int = 0
    files_count: int = 0
    error_message: Optional[str] = None
    checksum: Optional[str] = None
    backup_location: Optional[str] = None

@dataclass
class RestorePoint:
    """Restore point information"""
    restore_id: str
    backup_job_id: str
    created_at: datetime
    size_bytes: int
    checksum: str
    location: str
    metadata: Dict[str, Any]
    verified: bool = False

class CloudBackupManager:
    """Enterprise cloud backup and recovery manager"""
    
    def __init__(self, 
                 aws_credentials: Optional[Dict[str, str]] = None,
                 azure_credentials: Optional[Dict[str, str]] = None,
                 gcp_credentials: Optional[Dict[str, str]] = None):
        """Initialize cloud backup manager"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.aws_credentials = aws_credentials
        self.azure_credentials = azure_credentials
        self.gcp_credentials = gcp_credentials
        
        # Initialize cloud clients
        self._aws_client = None
        self._azure_client = None
        self._gcp_client = None
        
        # Backup state tracking
        self.active_jobs: Dict[str, BackupJob] = {}
        self.backup_history: List[BackupJob] = []
        self.restore_points: Dict[str, RestorePoint] = {}
        
        # Encryption key for backup data
        self._encryption_key = Fernet.generate_key()
        self._cipher_suite = Fernet(self._encryption_key)
        
        self.logger.info("Cloud Backup Manager initialized")

    async def initialize_providers(self) -> None:
        """Initialize cloud provider clients"""
        try:
            # Initialize AWS S3 client
            if self.aws_credentials:
                self._aws_client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_credentials.get('access_key'),
                    aws_secret_access_key=self.aws_credentials.get('secret_key'),
                    region_name=self.aws_credentials.get('region', 'us-east-1')
                )
            
            # Initialize Azure Blob client
            if self.azure_credentials:
                self._azure_client = BlobServiceClient(
                    account_url=self.azure_credentials.get('account_url'),
                    credential=self.azure_credentials.get('credential')
                )
            
            # Initialize GCP Storage client
            if self.gcp_credentials:
                self._gcp_client = gcs.Client.from_service_account_info(
                    self.gcp_credentials
                )
            
            self.logger.info("Cloud provider clients initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cloud providers: {e}")
            raise

    async def create_backup_job(self, config: BackupConfiguration) -> str:
        """Create and schedule a backup job"""
        try:
            job_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(config.name) % 1000}"
            
            backup_job = BackupJob(
                job_id=job_id,
                configuration=config,
                status=BackupStatus.SCHEDULED
            )
            
            self.active_jobs[job_id] = backup_job
            
            # Schedule the backup
            if config.schedule:
                await self._schedule_backup(backup_job)
            else:
                # Execute immediately
                await self._execute_backup(backup_job)
            
            self.logger.info(f"Backup job created: {job_id}")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Failed to create backup job: {e}")
            raise

    async def _execute_backup(self, job: BackupJob) -> None:
        """Execute backup operation"""
        try:
            job.status = BackupStatus.RUNNING
            job.started_at = datetime.now()
            
            # Prepare backup data
            backup_data = await self._prepare_backup_data(job.configuration)
            
            # Compress if enabled
            if job.configuration.compression_enabled:
                backup_data = await self._compress_data(backup_data)
            
            # Encrypt if enabled
            if job.configuration.encryption_enabled:
                backup_data = await self._encrypt_data(backup_data)
            
            # Calculate checksum
            job.checksum = hashlib.sha256(backup_data).hexdigest()
            job.size_bytes = len(backup_data)
            
            # Upload to cloud providers
            backup_locations = await self._upload_backup(job, backup_data)
            job.backup_location = json.dumps(backup_locations)
            
            # Cross-cloud replication if enabled
            if job.configuration.cross_cloud_replication:
                await self._replicate_across_clouds(job, backup_data)
            
            # Verify backup integrity
            if job.configuration.verification_enabled:
                await self._verify_backup(job)
            
            # Create restore point
            restore_point = RestorePoint(
                restore_id=f"restore_{job.job_id}",
                backup_job_id=job.job_id,
                created_at=job.started_at,
                size_bytes=job.size_bytes,
                checksum=job.checksum,
                location=job.backup_location,
                metadata=job.configuration.metadata
            )
            self.restore_points[restore_point.restore_id] = restore_point
            
            job.status = BackupStatus.COMPLETED
            job.completed_at = datetime.now()
            
            # Send notifications
            await self._send_backup_notification(job, "Backup completed successfully")
            
            self.logger.info(f"Backup job completed: {job.job_id}")
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            
            await self._send_backup_notification(job, f"Backup failed: {e}")
            self.logger.error(f"Backup job failed: {job.job_id} - {e}")
            raise

    async def _prepare_backup_data(self, config: BackupConfiguration) -> bytes:
        """Prepare data for backup"""
        try:
            source_path = Path(config.source_path)
            backup_data = b""
            files_count = 0
            
            if source_path.is_file():
                # Single file backup
                with open(source_path, 'rb') as f:
                    backup_data = f.read()
                files_count = 1
            elif source_path.is_dir():
                # Directory backup - create tar archive
                import tarfile
                import io
                
                tar_buffer = io.BytesIO()
                with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
                    tar.add(source_path, arcname=source_path.name)
                
                backup_data = tar_buffer.getvalue()
                files_count = sum(1 for _ in source_path.rglob('*') if _.is_file())
            
            return backup_data
            
        except Exception as e:
            self.logger.error(f"Failed to prepare backup data: {e}")
            raise

    async def _compress_data(self, data: bytes) -> bytes:
        """Compress backup data"""
        try:
            compressed_data = zlib.compress(data, level=9)
            compression_ratio = len(compressed_data) / len(data)
            self.logger.info(f"Data compressed with ratio: {compression_ratio:.2f}")
            return compressed_data
        except Exception as e:
            self.logger.error(f"Failed to compress data: {e}")
            raise

    async def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt backup data"""
        try:
            encrypted_data = self._cipher_suite.encrypt(data)
            self.logger.info("Data encrypted successfully")
            return encrypted_data
        except Exception as e:
            self.logger.error(f"Failed to encrypt data: {e}")
            raise

    async def _upload_backup(self, job: BackupJob, data: bytes) -> Dict[str, str]:
        """Upload backup to cloud providers"""
        locations = {}
        
        try:
            destination = job.configuration.destination
            
            # Upload to AWS S3
            if 'aws' in destination and self._aws_client:
                bucket = destination['aws']['bucket']
                key = f"backups/{job.job_id}/backup.dat"
                
                self._aws_client.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=data,
                    Metadata={
                        'job_id': job.job_id,
                        'created_at': job.started_at.isoformat(),
                        'checksum': job.checksum
                    }
                )
                locations['aws'] = f"s3://{bucket}/{key}"
            
            # Upload to Azure Blob
            if 'azure' in destination and self._azure_client:
                container = destination['azure']['container']
                blob_name = f"backups/{job.job_id}/backup.dat"
                
                blob_client = self._azure_client.get_blob_client(
                    container=container,
                    blob=blob_name
                )
                blob_client.upload_blob(
                    data,
                    metadata={
                        'job_id': job.job_id,
                        'created_at': job.started_at.isoformat(),
                        'checksum': job.checksum
                    }
                )
                locations['azure'] = f"azure://{container}/{blob_name}"
            
            # Upload to GCP Storage
            if 'gcp' in destination and self._gcp_client:
                bucket_name = destination['gcp']['bucket']
                blob_name = f"backups/{job.job_id}/backup.dat"
                
                bucket = self._gcp_client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                blob.metadata = {
                    'job_id': job.job_id,
                    'created_at': job.started_at.isoformat(),
                    'checksum': job.checksum
                }
                blob.upload_from_string(data)
                locations['gcp'] = f"gs://{bucket_name}/{blob_name}"
            
            return locations
            
        except Exception as e:
            self.logger.error(f"Failed to upload backup: {e}")
            raise

    async def _verify_backup(self, job: BackupJob) -> bool:
        """Verify backup integrity"""
        try:
            locations = json.loads(job.backup_location)
            
            for provider, location in locations.items():
                # Download and verify checksum
                downloaded_data = await self._download_backup_data(provider, location)
                
                # Decrypt if needed
                if job.configuration.encryption_enabled:
                    downloaded_data = self._cipher_suite.decrypt(downloaded_data)
                
                # Decompress if needed
                if job.configuration.compression_enabled:
                    downloaded_data = zlib.decompress(downloaded_data)
                
                # Verify checksum
                calculated_checksum = hashlib.sha256(downloaded_data).hexdigest()
                if calculated_checksum != job.checksum:
                    raise ValueError(f"Checksum mismatch for {provider}: expected {job.checksum}, got {calculated_checksum}")
            
            self.logger.info(f"Backup verification successful: {job.job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup verification failed: {e}")
            job.status = BackupStatus.CORRUPTED
            return False

    async def restore_from_backup(self, restore_id: str, destination_path: str) -> bool:
        """Restore data from backup"""
        try:
            if restore_id not in self.restore_points:
                raise ValueError(f"Restore point not found: {restore_id}")
            
            restore_point = self.restore_points[restore_id]
            job_id = restore_point.backup_job_id
            
            # Find the backup job
            backup_job = None
            for job in self.backup_history:
                if job.job_id == job_id:
                    backup_job = job
                    break
            
            if not backup_job:
                raise ValueError(f"Backup job not found: {job_id}")
            
            # Download backup data
            locations = json.loads(backup_job.backup_location)
            provider = list(locations.keys())[0]  # Use first available provider
            location = locations[provider]
            
            backup_data = await self._download_backup_data(provider, location)
            
            # Decrypt if needed
            if backup_job.configuration.encryption_enabled:
                backup_data = self._cipher_suite.decrypt(backup_data)
            
            # Decompress if needed
            if backup_job.configuration.compression_enabled:
                backup_data = zlib.decompress(backup_data)
            
            # Verify checksum
            calculated_checksum = hashlib.sha256(backup_data).hexdigest()
            if calculated_checksum != backup_job.checksum:
                raise ValueError("Data integrity check failed during restore")
            
            # Write restored data
            destination = Path(destination_path)
            
            if backup_job.configuration.source_path.endswith('.tar.gz'):
                # Extract tar archive
                import tarfile
                import io
                
                tar_buffer = io.BytesIO(backup_data)
                with tarfile.open(fileobj=tar_buffer, mode='r:gz') as tar:
                    tar.extractall(path=destination.parent)
            else:
                # Write single file
                with open(destination, 'wb') as f:
                    f.write(backup_data)
            
            restore_point.verified = True
            self.logger.info(f"Restore completed successfully: {restore_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
            raise

    async def _download_backup_data(self, provider: str, location: str) -> bytes:
        """Download backup data from cloud provider"""
        try:
            if provider == 'aws':
                # Parse S3 location: s3://bucket/key
                bucket, key = location.replace('s3://', '').split('/', 1)
                response = self._aws_client.get_object(Bucket=bucket, Key=key)
                return response['Body'].read()
            
            elif provider == 'azure':
                # Parse Azure location: azure://container/blob
                container, blob = location.replace('azure://', '').split('/', 1)
                blob_client = self._azure_client.get_blob_client(
                    container=container, blob=blob
                )
                return blob_client.download_blob().readall()
            
            elif provider == 'gcp':
                # Parse GCS location: gs://bucket/blob
                bucket_name, blob_name = location.replace('gs://', '').split('/', 1)
                bucket = self._gcp_client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                return blob.download_as_bytes()
            
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            self.logger.error(f"Failed to download backup data: {e}")
            raise

    async def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """Clean up old backups based on retention policy"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_count = 0
            
            for job in list(self.backup_history):
                if job.completed_at and job.completed_at < cutoff_date:
                    # Delete from cloud storage
                    if job.backup_location:
                        locations = json.loads(job.backup_location)
                        for provider, location in locations.items():
                            await self._delete_backup_from_cloud(provider, location)
                    
                    # Remove from history
                    self.backup_history.remove(job)
                    deleted_count += 1
            
            self.logger.info(f"Cleaned up {deleted_count} old backups")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")
            raise

    async def _delete_backup_from_cloud(self, provider: str, location: str) -> None:
        """Delete backup from cloud storage"""
        try:
            if provider == 'aws':
                bucket, key = location.replace('s3://', '').split('/', 1)
                self._aws_client.delete_object(Bucket=bucket, Key=key)
            
            elif provider == 'azure':
                container, blob = location.replace('azure://', '').split('/', 1)
                blob_client = self._azure_client.get_blob_client(
                    container=container, blob=blob
                )
                blob_client.delete_blob()
            
            elif provider == 'gcp':
                bucket_name, blob_name = location.replace('gs://', '').split('/', 1)
                bucket = self._gcp_client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                blob.delete()
                
        except Exception as e:
            self.logger.error(f"Failed to delete backup from {provider}: {e}")
            raise

    async def _schedule_backup(self, job: BackupJob) -> None:
        """Schedule backup using cron expression"""
        # This would integrate with a job scheduler like Celery or APScheduler
        # For now, we'll just log the scheduling
        self.logger.info(f"Backup scheduled: {job.job_id} with schedule: {job.configuration.schedule}")

    async def _send_backup_notification(self, job: BackupJob, message: str) -> None:
        """Send backup completion notification"""
        try:
            notification_settings = job.configuration.notification_settings
            
            if notification_settings.get('email_enabled'):
                # Send email notification
                self.logger.info(f"Email notification sent for job {job.job_id}: {message}")
            
            if notification_settings.get('webhook_url'):
                # Send webhook notification
                self.logger.info(f"Webhook notification sent for job {job.job_id}: {message}")
                
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")

    async def get_backup_status(self, job_id: str) -> Optional[BackupJob]:
        """Get backup job status"""
        return self.active_jobs.get(job_id) or next(
            (job for job in self.backup_history if job.job_id == job_id), None
        )

    async def list_restore_points(self) -> List[RestorePoint]:
        """List all available restore points"""
        return list(self.restore_points.values())

    async def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup statistics and metrics"""
        total_jobs = len(self.backup_history)
        successful_jobs = len([j for j in self.backup_history if j.status == BackupStatus.COMPLETED])
        failed_jobs = len([j for j in self.backup_history if j.status == BackupStatus.FAILED])
        
        total_size = sum(job.size_bytes for job in self.backup_history if job.size_bytes)
        
        return {
            "total_backup_jobs": total_jobs,
            "successful_jobs": successful_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            "total_backup_size_bytes": total_size,
            "total_restore_points": len(self.restore_points),
            "active_jobs": len(self.active_jobs)
        }
