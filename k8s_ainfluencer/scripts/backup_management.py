#!/usr/bin/env python3
"""Backup Management System
Comprehensive backup and restore operations for the IA Influencer Agent platform
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

import boto3
import psycopg2
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackupType(Enum):
    """
Backup type enumeration"""

    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupStatus(Enum):
    """Backup status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class StorageProvider(Enum):
    """Storage provider enumeration"""

    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE_BLOB = "azure_blob"
    LOCAL_STORAGE = "local_storage"
    MINIO = "minio"


@dataclass
class BackupConfig:
    """Backup configuration data class"""
    name: str
    backup_type: BackupType
    storage_provider: StorageProvider
    retention_days: int
    encryption_enabled: bool = True
    compression_enabled: bool = True
    notification_enabled: bool = True
    parallel_uploads: int = 4
    exclude_patterns: List[str] = None


@dataclass
class BackupJob:
    """
Backup job data class"""
    id: str
    config: BackupConfig
    status: BackupStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    size_bytes: int = 0
    error_message: Optional[str] = None
    file_count: int = 0
    progress_percentage: float = 0.0


class BackupManager:
    """
    Enterprise-grade backup management system
    Handles automated backups, retention, and disaster recovery
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
Initialize backup manager"""
        self.config_path = config_path or "/etc/backup/config.json"
        self.active_jobs: Dict[str, BackupJob] = {}
        self.completed_jobs: List[BackupJob] = []
        self.storage_clients = {}
        
        self._load_configuration()
        self._initialize_storage_clients()
        self._setup_backup_directories()
    
    def _load_configuration(self) -> None:
        """Load backup configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Loaded backup configuration from {self.config_path}")
            else:
                self.config = self._get_default_config()
                logger.warning("Using default backup configuration")
        except Exception as e:
            logger.error(f"Failed to load backup configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default backup configuration"""
        return {
            "database": {
                "host": "localhost",
                "port": 5432,
                "username": "postgres",
                "password": "password",
                "databases": ["ia_influencer", "analytics", "monitoring"]
            },
            "storage": {
                "provider": "aws_s3",
                "bucket": "ia-influencer-backups",
                "region": "eu-central-1",
                "encryption": True
            },
            "retention": {
                "daily": 7,
                "weekly": 4,
                "monthly": 12,
                "yearly": 5
            },
            "schedules": {
                "database_full": "0 2 * * 0",  # Weekly on Sunday at 2 AM
                "database_incremental": "0 2 * * 1-6",  # Daily except Sunday
                "application_files": "0 3 * * *",  # Daily at 3 AM
                "user_data": "0 4 * * *"  # Daily at 4 AM
            },
            "notifications": {
                "email": {
                    "enabled": True,
                    "recipients": ["admin@example.com"]
                },
                "slack": {
                    "enabled": False,
                    "webhook": None
                }
            }
        }
    
    def _initialize_storage_clients(self) -> None:
        """Initialize storage provider clients"""
        try:
            storage_config = self.config.get("storage", {})
            provider = storage_config.get("provider", "aws_s3")
            
            if provider == "aws_s3":
                self.storage_clients["s3"] = boto3.client(
                    's3',
                    region_name=storage_config.get("region", "eu-central-1")
                )
                logger.info("Initialized AWS S3 client")
            
            elif provider == "minio":
                self.storage_clients["minio"] = boto3.client(
                    's3',
                    endpoint_url=storage_config.get("endpoint"),
                    aws_access_key_id=storage_config.get("access_key"),
                    aws_secret_access_key=storage_config.get("secret_key"),
                    region_name=storage_config.get("region", "us-east-1")
                )
                logger.info("Initialized MinIO client")
                
        except Exception as e:
            logger.error(f"Failed to initialize storage clients: {e}")
    
    def _setup_backup_directories(self) -> None:
        """Setup backup directories"""
        backup_dirs = [
            "/tmp/backups",
            "/tmp/backups/database",
            "/tmp/backups/application",
            "/tmp/backups/user_data",
            "/tmp/backups/logs"
        ]
        
        for backup_dir in backup_dirs:
            os.makedirs(backup_dir, exist_ok=True)
        
        logger.info("Backup directories created")
    
    def create_backup_job(self, config: BackupConfig) -> str:
        """
        Create new backup job
        
        Args:
            config: Backup configuration
            
        Returns:
            str: Job ID
        """
        job_id = f"backup_{int(time.time())}_{config.name}"
        
        job = BackupJob(
            id=job_id,
            config=config,
            status=BackupStatus.PENDING
        )
        
        self.active_jobs[job_id] = job
        logger.info(f"Created backup job: {job_id}")
        
        return job_id
    
    def execute_backup_job(self, job_id: str) -> bool:
        """
        Execute backup job
        
        Args:
            job_id: Job identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        if job_id not in self.active_jobs:
            logger.error(f"Backup job not found: {job_id}")
            return False
        
        job = self.active_jobs[job_id]
        
        try:
            job.status = BackupStatus.IN_PROGRESS
            job.start_time = datetime.now()
            
            logger.info(f"Starting backup job: {job_id}")
            
            # Execute backup based on configuration
            success = False
            if "database" in job.config.name.lower():
                success = self._backup_database(job)
            elif "application" in job.config.name.lower():
                success = self._backup_application_files(job)
            elif "user_data" in job.config.name.lower():
                success = self._backup_user_data(job)
            else:
                success = self._backup_generic(job)
            
            # Update job status
            job.end_time = datetime.now()
            job.status = BackupStatus.COMPLETED if success else BackupStatus.FAILED
            
            # Move to completed jobs
            self.completed_jobs.append(job)
            del self.active_jobs[job_id]
            
            # Send notification
            if job.config.notification_enabled:
                self._send_backup_notification(job)
            
            # Clean up temporary files
            self._cleanup_temporary_files(job)
            
            logger.info(f"Backup job completed: {job_id} - {'SUCCESS' if success else 'FAILED'}")
            return success
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.end_time = datetime.now()
            
            logger.error(f"Backup job failed: {job_id} - {e}")
            return False
    
    def _backup_database(self, job: BackupJob) -> bool:
        """Backup database"""
        try:
            logger.info("Starting database backup")
            
            db_config = self.config.get("database", {})
            databases = db_config.get("databases", [])
            
            backup_files = []
            total_size = 0
            
            for database in databases:
                backup_file = f"/tmp/backups/database/{database}_{int(time.time())}.sql"
                
                # Create database dump
                pg_dump_cmd = [
                    "pg_dump",
                    "-h", db_config.get("host", "localhost"),
                    "-p", str(db_config.get("port", 5432)),
                    "-U", db_config.get("username", "postgres"),
                    "-f", backup_file,
                    "-v",
                    "--no-password",
                    database
                ]
                
                # Set password via environment variable
                env = os.environ.copy()
                env["PGPASSWORD"] = db_config.get("password", "")
                
                result = subprocess.run(pg_dump_cmd, env=env, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"pg_dump failed for {database}: {result.stderr}")
                    return False
                
                # Compress if enabled
                if job.config.compression_enabled:
                    compressed_file = f"{backup_file}.gz"
                    subprocess.run(["gzip", backup_file], check=True)
                    backup_file = compressed_file
                
                backup_files.append(backup_file)
                total_size += os.path.getsize(backup_file)
                
                logger.info(f"Database {database} backed up to {backup_file}")
            
            job.size_bytes = total_size
            job.file_count = len(backup_files)
            
            # Upload to storage
            return self._upload_to_storage(job, backup_files)
            
        except Exception as e:
            logger.error(f"Database backup error: {e}")
            return False
    
    def _backup_application_files(self, job: BackupJob) -> bool:
        """Backup application files"""
        try:
            logger.info("Starting application files backup")
            
            # Define application directories to backup
            app_dirs = [
                "/opt/ia-influencer/backend",
                "/opt/ia-influencer/config",
                "/opt/ia-influencer/logs",
                "/etc/ia-influencer"
            ]
            
            backup_archive = f"/tmp/backups/application/app_backup_{int(time.time())}.tar"
            
            # Create tar archive
            tar_cmd = ["tar", "-cf", backup_archive]
            
            # Add directories that exist
            for app_dir in app_dirs:
                if os.path.exists(app_dir):
                    tar_cmd.append(app_dir)
            
            # Add exclude patterns
            exclude_patterns = job.config.exclude_patterns or [
                "*.log",
                "*.tmp",
                "__pycache__",
                "*.pyc",
                ".git"
            ]
            
            for pattern in exclude_patterns:
                tar_cmd.extend(["--exclude", pattern])
            
            result = subprocess.run(tar_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"tar command failed: {result.stderr}")
                return False
            
            # Compress if enabled
            if job.config.compression_enabled:
                subprocess.run(["gzip", backup_archive], check=True)
                backup_archive = f"{backup_archive}.gz"
            
            job.size_bytes = os.path.getsize(backup_archive)
            job.file_count = 1
            
            logger.info(f"Application files backed up to {backup_archive}")
            
            # Upload to storage
            return self._upload_to_storage(job, [backup_archive])
            
        except Exception as e:
            logger.error(f"Application backup error: {e}")
            return False
    
    def _backup_user_data(self, job: BackupJob) -> bool:
        """Backup user data"""
        try:
            logger.info("Starting user data backup")
            
            # Define user data directories
            user_data_dirs = [
                "/data/uploads",
                "/data/user_content",
                "/data/fingerprints",
                "/data/analytics"
            ]
            
            backup_files = []
            total_size = 0
            
            for data_dir in user_data_dirs:
                if not os.path.exists(data_dir):
                    continue
                
                dir_name = os.path.basename(data_dir)
                backup_archive = f"/tmp/backups/user_data/{dir_name}_{int(time.time())}.tar"
                
                # Create tar archive
                tar_cmd = [
                    "tar", "-cf", backup_archive,
                    "-C", os.path.dirname(data_dir),
                    dir_name
                ]
                
                result = subprocess.run(tar_cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"tar command failed for {data_dir}: {result.stderr}")
                    continue
                
                # Compress if enabled
                if job.config.compression_enabled:
                    subprocess.run(["gzip", backup_archive], check=True)
                    backup_archive = f"{backup_archive}.gz"
                
                backup_files.append(backup_archive)
                total_size += os.path.getsize(backup_archive)
                
                logger.info(f"User data {data_dir} backed up to {backup_archive}")
            
            job.size_bytes = total_size
            job.file_count = len(backup_files)
            
            # Upload to storage
            return self._upload_to_storage(job, backup_files)
            
        except Exception as e:
            logger.error(f"User data backup error: {e}")
            return False
    
    def _backup_generic(self, job: BackupJob) -> bool:
        """Generic backup implementation"""
        try:
            logger.info(f"Starting generic backup: {job.config.name}")
            
            # This would be customized based on specific backup requirements
            # For now, create a placeholder backup
            backup_file = f"/tmp/backups/{job.config.name}_{int(time.time())}.txt"
            
            with open(backup_file, 'w') as f:
                f.write(f"Generic backup for {job.config.name}\n")
                f.write(f"Created at: {datetime.now()}\n")
            
            job.size_bytes = os.path.getsize(backup_file)
            job.file_count = 1
            
            # Upload to storage
            return self._upload_to_storage(job, [backup_file])
            
        except Exception as e:
            logger.error(f"Generic backup error: {e}")
            return False
    
    def _upload_to_storage(self, job: BackupJob, backup_files: List[str]) -> bool:
        """Upload backup files to storage"""
        try:
            logger.info("Uploading backup files to storage")
            
            storage_config = self.config.get("storage", {})
            provider = job.config.storage_provider.value
            
            if provider == "aws_s3" or provider == "minio":
                return self._upload_to_s3(job, backup_files, storage_config)
            elif provider == "local_storage":
                return self._upload_to_local(job, backup_files, storage_config)
            else:
                logger.error(f"Unsupported storage provider: {provider}")
                return False
                
        except Exception as e:
            logger.error(f"Storage upload error: {e}")
            return False
    
    def _upload_to_s3(self, job: BackupJob, backup_files: List[str], storage_config: Dict[str, Any]) -> bool:
        """Upload files to S3-compatible storage"""
        try:
            s3_client = self.storage_clients.get("s3") or self.storage_clients.get("minio")
            if not s3_client:
                logger.error("S3 client not initialized")
                return False
            
            bucket = storage_config.get("bucket", "ia-influencer-backups")
            
            # Ensure bucket exists
            try:
                s3_client.head_bucket(Bucket=bucket)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    s3_client.create_bucket(
                        Bucket=bucket,
                        CreateBucketConfiguration={
                            'LocationConstraint': storage_config.get("region", "eu-central-1")
                        }
                    )
                else:
                    raise
            
            uploaded_files = []
            
            for backup_file in backup_files:
                file_name = os.path.basename(backup_file)
                s3_key = f"{job.config.name}/{datetime.now().strftime('%Y/%m/%d')}/{file_name}"
                
                # Upload with encryption if enabled
                extra_args = {}
                if job.config.encryption_enabled:
                    extra_args['ServerSideEncryption'] = 'AES256'
                
                s3_client.upload_file(
                    backup_file,
                    bucket,
                    s3_key,
                    ExtraArgs=extra_args
                )
                
                uploaded_files.append(s3_key)
                logger.info(f"Uploaded {backup_file} to s3://{bucket}/{s3_key}")
            
            # Store upload information in job
            job.config.upload_paths = uploaded_files
            
            return True
            
        except Exception as e:
            logger.error(f"S3 upload error: {e}")
            return False
    
    def _upload_to_local(self, job: BackupJob, backup_files: List[str], storage_config: Dict[str, Any]) -> bool:
        """Upload files to local storage"""
        try:
            local_path = storage_config.get("path", "/backup/storage")
            backup_dir = os.path.join(local_path, job.config.name, datetime.now().strftime('%Y/%m/%d'))
            
            os.makedirs(backup_dir, exist_ok=True)
            
            uploaded_files = []
            
            for backup_file in backup_files:
                file_name = os.path.basename(backup_file)
                dest_path = os.path.join(backup_dir, file_name)
                
                # Copy file
                subprocess.run(["cp", backup_file, dest_path], check=True)
                
                uploaded_files.append(dest_path)
                logger.info(f"Copied {backup_file} to {dest_path}")
            
            job.config.upload_paths = uploaded_files
            
            return True
            
        except Exception as e:
            logger.error(f"Local storage error: {e}")
            return False
    
    def _send_backup_notification(self, job: BackupJob) -> None:
        """Send backup completion notification"""
        try:
            notification_config = self.config.get("notifications", {})
            
            message = self._create_notification_message(job)
            
            # Email notification
            if notification_config.get("email", {}).get("enabled", False):
                self._send_email_notification(message, notification_config["email"])
            
            # Slack notification
            if notification_config.get("slack", {}).get("enabled", False):
                self._send_slack_notification(message, notification_config["slack"])
            
            logger.info("Backup notification sent")
            
        except Exception as e:
            logger.error(f"Notification error: {e}")
    
    def _create_notification_message(self, job: BackupJob) -> str:
        """Create notification message"""
        status = "✅ SUCCESS" if job.status == BackupStatus.COMPLETED else "❌ FAILED"
        duration = (job.end_time - job.start_time).total_seconds() if job.end_time and job.start_time else 0
        
        size_mb = job.size_bytes / (1024 * 1024)
        
        message = f"""Backup Job {status}

Job ID: {job.id}
Name: {job.config.name}
Type: {job.config.backup_type.value}
Duration: {duration:.2f} seconds
Size: {size_mb:.2f} MB
Files: {job.file_count}
Start Time: {job.start_time}
End Time: {job.end_time}
"""
        
        if job.error_message:
            message += f"Error: {job.error_message}"
        
        return message
    
    def _send_email_notification(self, message: str, email_config: Dict[str, Any]) -> None:
        """Send email notification"""
        try:
            # This would integrate with email service (SES, SendGrid, etc.)
            logger.info("Email notification sent")
            
        except Exception as e:
            logger.error(f"Email notification error: {e}")
    
    def _send_slack_notification(self, message: str, slack_config: Dict[str, Any]) -> None:
        """Send Slack notification"""
        try:
            import requests
            
            webhook_url = slack_config.get("webhook")
            if webhook_url:
                requests.post(webhook_url, json={"text": message})
                logger.info("Slack notification sent")
            
        except Exception as e:
            logger.error(f"Slack notification error: {e}")
    
    def _cleanup_temporary_files(self, job: BackupJob) -> None:
        """Clean up temporary backup files"""
        try:
            # Remove temporary files from /tmp/backups
            for root, dirs, files in os.walk("/tmp/backups"):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Remove files older than 1 hour
                    if time.time() - os.path.getmtime(file_path) > 3600:
                        os.remove(file_path)
                        logger.debug(f"Removed temporary file: {file_path}")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def schedule_backup(self, config: BackupConfig, cron_expression: str) -> str:
        """
        Schedule recurring backup
        
        Args:
            config: Backup configuration
            cron_expression: Cron expression for scheduling
            
        Returns:
            str: Schedule ID
        """
        try:
            schedule_id = f"schedule_{int(time.time())}_{config.name}"
            
            # Store schedule information
            schedule_info = {
                "id": schedule_id,
                "config": config,
                "cron": cron_expression,
                "enabled": True,
                "created_at": datetime.now()
            }
            
            # In a real implementation, this would integrate with a scheduler
            # like Celery Beat, cron, or Kubernetes CronJobs
            
            logger.info(f"Scheduled backup: {schedule_id} with cron '{cron_expression}'")
            return schedule_id
            
        except Exception as e:
            logger.error(f"Schedule error: {e}")
            return ""
    
    def restore_backup(self, backup_path: str, restore_type: str = "full") -> bool:
        """
        Restore from backup
        
        Args:
            backup_path: Path to backup file/directory
            restore_type: Type of restore (full, partial, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Starting restore from {backup_path}")
            
            # Download backup if from remote storage
            local_backup_path = self._download_backup_if_needed(backup_path)
            
            if not local_backup_path:
                logger.error("Failed to access backup file")
                return False
            
            # Determine restore method based on backup type
            if "database" in backup_path:
                return self._restore_database(local_backup_path)
            elif "application" in backup_path:
                return self._restore_application(local_backup_path)
            elif "user_data" in backup_path:
                return self._restore_user_data(local_backup_path)
            else:
                logger.error(f"Unknown backup type: {backup_path}")
                return False
                
        except Exception as e:
            logger.error(f"Restore error: {e}")
            return False
    
    def _download_backup_if_needed(self, backup_path: str) -> Optional[str]:
        """Download backup from remote storage if needed"""
        try:
            if backup_path.startswith("s3://"):
                # Download from S3
                return self._download_from_s3(backup_path)
            elif os.path.exists(backup_path):
                # Local file
                return backup_path
            else:
                logger.error(f"Backup not found: {backup_path}")
                return None
                
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None
    
    def _download_from_s3(self, s3_path: str) -> Optional[str]:
        """Download backup from S3"""
        try:
            # Parse S3 path
            parts = s3_path.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1]
            
            # Download to local file
            local_file = f"/tmp/restore_{int(time.time())}_{os.path.basename(key)}"
            
            s3_client = self.storage_clients.get("s3")
            if not s3_client:
                logger.error("S3 client not available")
                return None
            
            s3_client.download_file(bucket, key, local_file)
            logger.info(f"Downloaded {s3_path} to {local_file}")
            
            return local_file
            
        except Exception as e:
            logger.error(f"S3 download error: {e}")
            return None
    
    def _restore_database(self, backup_file: str) -> bool:
        """Restore database from backup"""
        try:
            logger.info(f"Restoring database from {backup_file}")
            
            # Decompress if needed
            if backup_file.endswith(".gz"):
                subprocess.run(["gunzip", backup_file], check=True)
                backup_file = backup_file[:-3]  # Remove .gz extension
            
            db_config = self.config.get("database", {})
            
            # Restore using psql
            psql_cmd = [
                "psql",
                "-h", db_config.get("host", "localhost"),
                "-p", str(db_config.get("port", 5432)),
                "-U", db_config.get("username", "postgres"),
                "-f", backup_file
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = db_config.get("password", "")
            
            result = subprocess.run(psql_cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Database restore completed successfully")
                return True
            else:
                logger.error(f"Database restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Database restore error: {e}")
            return False
    
    def _restore_application(self, backup_file: str) -> bool:
        """Restore application files from backup"""
        try:
            logger.info(f"Restoring application from {backup_file}")
            
            # Extract archive
            if backup_file.endswith(".tar.gz"):
                tar_cmd = ["tar", "-xzf", backup_file, "-C", "/"]
            elif backup_file.endswith(".tar"):
                tar_cmd = ["tar", "-xf", backup_file, "-C", "/"]
            else:
                logger.error(f"Unsupported backup format: {backup_file}")
                return False
            
            result = subprocess.run(tar_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Application restore completed successfully")
                return True
            else:
                logger.error(f"Application restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Application restore error: {e}")
            return False
    
    def _restore_user_data(self, backup_file: str) -> bool:
        """Restore user data from backup"""
        try:
            logger.info(f"Restoring user data from {backup_file}")
            
            # Extract to data directory
            if backup_file.endswith(".tar.gz"):
                tar_cmd = ["tar", "-xzf", backup_file, "-C", "/data"]
            elif backup_file.endswith(".tar"):
                tar_cmd = ["tar", "-xf", backup_file, "-C", "/data"]
            else:
                logger.error(f"Unsupported backup format: {backup_file}")
                return False
            
            result = subprocess.run(tar_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("User data restore completed successfully")
                return True
            else:
                logger.error(f"User data restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"User data restore error: {e}")
            return False
    
    def cleanup_old_backups(self) -> None:
        """Clean up old backups based on retention policy"""
        try:
            logger.info("Starting backup cleanup")
            
            retention_config = self.config.get("retention", {})
            storage_config = self.config.get("storage", {})
            
            if storage_config.get("provider") == "aws_s3":
                self._cleanup_s3_backups(retention_config)
            elif storage_config.get("provider") == "local_storage":
                self._cleanup_local_backups(retention_config)
            
            logger.info("Backup cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def _cleanup_s3_backups(self, retention_config: Dict[str, int]) -> None:
        """Clean up old S3 backups"""
        try:
            s3_client = self.storage_clients.get("s3")
            if not s3_client:
                return
            
            bucket = self.config.get("storage", {}).get("bucket")
            if not bucket:
                return
            
            # Get all objects
            response = s3_client.list_objects_v2(Bucket=bucket)
            
            if 'Contents' not in response:
                return
            
            now = datetime.now()
            daily_retention = retention_config.get("daily", 7)
            
            for obj in response['Contents']:
                key = obj['Key']
                last_modified = obj['LastModified'].replace(tzinfo=None)
                
                # Calculate age in days
                age_days = (now - last_modified).days
                
                # Delete if older than retention period
                if age_days > daily_retention:
                    s3_client.delete_object(Bucket=bucket, Key=key)
                    logger.info(f"Deleted old backup: {key}")
                    
        except Exception as e:
            logger.error(f"S3 cleanup error: {e}")
    
    def _cleanup_local_backups(self, retention_config: Dict[str, int]) -> None:
        """Clean up old local backups"""
        try:
            local_path = self.config.get("storage", {}).get("path", "/backup/storage")
            
            if not os.path.exists(local_path):
                return
            
            now = time.time()
            daily_retention_seconds = retention_config.get("daily", 7) * 24 * 3600
            
            for root, dirs, files in os.walk(local_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check file age
                    file_age = now - os.path.getmtime(file_path)
                    
                    if file_age > daily_retention_seconds:
                        os.remove(file_path)
                        logger.info(f"Deleted old backup: {file_path}")
                        
        except Exception as e:
            logger.error(f"Local cleanup error: {e}")
    
    def get_backup_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get backup job status"""
        try:
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
            else:
                job = next((j for j in self.completed_jobs if j.id == job_id), None)
            
            if not job:
                return None
            
            return {
                "id": job.id,
                "name": job.config.name,
                "status": job.status.value,
                "start_time": job.start_time.isoformat() if job.start_time else None,
                "end_time": job.end_time.isoformat() if job.end_time else None,
                "size_bytes": job.size_bytes,
                "file_count": job.file_count,
                "progress_percentage": job.progress_percentage,
                "error_message": job.error_message
            }
            
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return None
    
    def list_backups(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent backups"""
        try:
            all_jobs = list(self.active_jobs.values()) + self.completed_jobs
            
            # Sort by start time (most recent first)
            sorted_jobs = sorted(
                all_jobs,
                key=lambda x: x.start_time or datetime.min,
                reverse=True
            )
            
            return [
                {
                    "id": job.id,
                    "name": job.config.name,
                    "status": job.status.value,
                    "start_time": job.start_time.isoformat() if job.start_time else None,
                    "size_bytes": job.size_bytes,
                    "file_count": job.file_count
                }
                for job in sorted_jobs[:limit]
            ]
            
        except Exception as e:
            logger.error(f"List backups error: {e}")
            return []


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup Management System")
    parser.add_argument("--action", required=True, choices=["backup", "restore", "cleanup", "status", "list"])
    parser.add_argument("--name", help="Backup name")
    parser.add_argument("--type", choices=["full", "incremental", "differential"], default="full")
    parser.add_argument("--storage", choices=["aws_s3", "local_storage"], default="aws_s3")
    parser.add_argument("--retention-days", type=int, default=7)
    parser.add_argument("--backup-path", help="Backup path for restore")
    parser.add_argument("--job-id", help="Job ID for status check")
    
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if args.action == "backup":
        if not args.name:
            print("Error: --name is required for backup")
            sys.exit(1)
        
        config = BackupConfig(
            name=args.name,
            backup_type=BackupType(args.type),
            storage_provider=StorageProvider(args.storage),
            retention_days=args.retention_days
        )
        
        job_id = manager.create_backup_job(config)
        success = manager.execute_backup_job(job_id)
        
        print(f"Backup {'completed' if success else 'failed'}: {job_id}")
        sys.exit(0 if success else 1)
    
    elif args.action == "restore":
        if not args.backup_path:
            print("Error: --backup-path is required for restore")
            sys.exit(1)
        
        success = manager.restore_backup(args.backup_path)
        print(f"Restore {'completed' if success else 'failed'}")
        sys.exit(0 if success else 1)
    
    elif args.action == "cleanup":
        manager.cleanup_old_backups()
        print("Cleanup completed")
    
    elif args.action == "status":
        if not args.job_id:
            print("Error: --job-id is required for status")
            sys.exit(1)
        
        status = manager.get_backup_status(args.job_id)
        if status:
            print(json.dumps(status, indent=2))
        else:
            print("Job not found")
            sys.exit(1)
    
    elif args.action == "list":
        backups = manager.list_backups()
        print(json.dumps(backups, indent=2))


if __name__ == "__main__":
    main()
