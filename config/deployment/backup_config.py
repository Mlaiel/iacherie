"""
Backup Configuration Module for IA-Influencer Agent Platform
===========================================================

Professional backup and disaster recovery configuration
for multi-format content protection and AI-powered creator monetization platform.

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
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import yaml


class BackupType(Enum):
    """Backup types"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"
    CONTINUOUS = "continuous"


class BackupStorage(Enum):
    """Backup storage providers"""
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_STORAGE = "google_storage"
    LOCAL_NFS = "local_nfs"
    SFTP = "sftp"
    RSYNC = "rsync"


class RetentionPolicy(Enum):
    """Backup retention policies"""
    DAILY_30 = "daily_30"      # 30 daily backups
    WEEKLY_12 = "weekly_12"    # 12 weekly backups
    MONTHLY_12 = "monthly_12"  # 12 monthly backups
    YEARLY_7 = "yearly_7"      # 7 yearly backups
    CUSTOM = "custom"


@dataclass
class BackupSchedule:
    """Backup schedule configuration"""
    name: str
    cron_expression: str
    backup_type: BackupType
    retention_policy: RetentionPolicy
    retention_days: int = 30
    enabled: bool = True
    priority: int = 1
    max_parallel_jobs: int = 1
    timeout_minutes: int = 120
    notification_emails: List[str] = field(default_factory=lambda: ["mlaiel@live.de"])


@dataclass
class DatabaseBackupConfig:
    """Database backup configuration"""
    name: str
    engine: str  # postgresql, mysql, mongodb, redis
    host: str
    port: int
    database: str
    username: str
    password_env_var: str
    backup_format: str = "custom"  # custom, plain, tar
    compression: bool = True
    exclude_tables: List[str] = field(default_factory=list)
    include_blobs: bool = True
    parallel_jobs: int = 2


@dataclass
class FileSystemBackupConfig:
    """File system backup configuration"""
    name: str
    source_path: str
    exclude_patterns: List[str] = field(default_factory=list)
    include_patterns: List[str] = field(default_factory=lambda: ["*"])
    follow_symlinks: bool = False
    preserve_permissions: bool = True
    preserve_timestamps: bool = True
    compression: str = "gzip"  # gzip, bzip2, xz, none


@dataclass
class StorageConfig:
    """Backup storage configuration"""
    provider: BackupStorage
    bucket_name: str
    region: str = "eu-central-1"
    access_key_env_var: str = ""
    secret_key_env_var: str = ""
    encryption_enabled: bool = True
    encryption_key_env_var: str = ""
    versioning_enabled: bool = True
    lifecycle_rules: List[Dict[str, Any]] = field(default_factory=list)


class BackupConfig:
    """
    Professional backup configuration manager for IA-Influencer Agent Platform.
    
    Manages comprehensive backup strategies for:
    - PostgreSQL databases (user data, analytics, revenue)
    - Redis cache and sessions
    - MongoDB collections (ML models, fingerprints)
    - Elasticsearch indices (search data, logs)
    - File system assets (uploads, processed content)
    - AI model weights and configurations
    - Application configurations and secrets
    - Log files and audit trails
    """
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_name = "ia-influencer-agent"
        self.backup_storage = self._get_backup_storage()
        self.retention_strategy = self._get_retention_strategy()
        
    def _get_backup_storage(self) -> BackupStorage:
        """Get backup storage provider based on environment"""
        providers = {
            "development": BackupStorage.LOCAL_NFS,
            "staging": BackupStorage.AWS_S3,
            "production": BackupStorage.AWS_S3
        }
        return providers.get(self.environment, BackupStorage.LOCAL_NFS)
    
    def _get_retention_strategy(self) -> RetentionPolicy:
        """Get retention policy based on environment"""
        policies = {
            "development": RetentionPolicy.DAILY_30,
            "staging": RetentionPolicy.WEEKLY_12,
            "production": RetentionPolicy.YEARLY_7
        }
        return policies.get(self.environment, RetentionPolicy.DAILY_30)
    
    def get_database_backup_configs(self) -> List[DatabaseBackupConfig]:
        """Get database backup configurations"""
        return [
            # PostgreSQL main database
            DatabaseBackupConfig(
                name="postgresql_main",
                engine="postgresql",
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", "5432")),
                database=os.getenv("POSTGRES_DB", "ia_influencer"),
                username=os.getenv("POSTGRES_USER", "postgres"),
                password_env_var="POSTGRES_PASSWORD",
                backup_format="custom",
                compression=True,
                exclude_tables=["django_session", "celery_taskmeta", "celery_tasksetmeta"],
                parallel_jobs=4
            ),
            
            # PostgreSQL analytics database
            DatabaseBackupConfig(
                name="postgresql_analytics",
                engine="postgresql",
                host=os.getenv("ANALYTICS_POSTGRES_HOST", "localhost"),
                port=int(os.getenv("ANALYTICS_POSTGRES_PORT", "5432")),
                database=os.getenv("ANALYTICS_POSTGRES_DB", "analytics"),
                username=os.getenv("ANALYTICS_POSTGRES_USER", "analytics"),
                password_env_var="ANALYTICS_POSTGRES_PASSWORD",
                backup_format="custom",
                compression=True,
                parallel_jobs=2
            ),
            
            # Redis cache and sessions
            DatabaseBackupConfig(
                name="redis_main",
                engine="redis",
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                database="0",
                username="",
                password_env_var="REDIS_PASSWORD",
                backup_format="rdb",
                compression=True
            ),
            
            # MongoDB ML models and fingerprints
            DatabaseBackupConfig(
                name="mongodb_ml",
                engine="mongodb",
                host=os.getenv("MONGODB_HOST", "localhost"),
                port=int(os.getenv("MONGODB_PORT", "27017")),
                database=os.getenv("MONGODB_DB", "ml_data"),
                username=os.getenv("MONGODB_USER", "ml_user"),
                password_env_var="MONGODB_PASSWORD",
                backup_format="archive",
                compression=True,
                exclude_tables=["temp_collections", "cache_collections"],
                parallel_jobs=2
            )
        ]
    
    def get_filesystem_backup_configs(self) -> List[FileSystemBackupConfig]:
        """Get file system backup configurations"""
        return [
            # User uploads and media files
            FileSystemBackupConfig(
                name="user_uploads",
                source_path="/var/www/uploads",
                exclude_patterns=[
                    "*.tmp",
                    "*.temp", 
                    "*/.DS_Store",
                    "*/Thumbs.db",
                    "*/._*",
                    "temp/*",
                    "cache/*"
                ],
                compression="gzip",
                preserve_permissions=True
            ),
            
            # Processed AI content
            FileSystemBackupConfig(
                name="ai_processed",
                source_path="/var/www/ai-processed",
                exclude_patterns=[
                    "*.log",
                    "processing/*",
                    "temp/*"
                ],
                compression="xz",  # Better compression for AI data
                preserve_permissions=True
            ),
            
            # Static assets
            FileSystemBackupConfig(
                name="static_assets",
                source_path="/var/www/static",
                exclude_patterns=[
                    "*.map",
                    "dev/*",
                    "test/*"
                ],
                compression="gzip",
                preserve_permissions=False
            ),
            
            # Application configurations
            FileSystemBackupConfig(
                name="app_configs",
                source_path="/etc/ia-influencer-agent",
                exclude_patterns=[
                    "*.log",
                    "logs/*",
                    "cache/*",
                    "*.pid"
                ],
                compression="bzip2",
                preserve_permissions=True
            ),
            
            # ML model weights and checkpoints
            FileSystemBackupConfig(
                name="ml_models",
                source_path="/var/lib/ml-models",
                exclude_patterns=[
                    "*.tmp",
                    "training/*",
                    "temp_models/*"
                ],
                compression="xz",
                preserve_permissions=True
            ),
            
            # SSL certificates and keys
            FileSystemBackupConfig(
                name="ssl_certificates",
                source_path="/etc/ssl/certs/ia-influencer-agent",
                exclude_patterns=[],
                compression="gzip",
                preserve_permissions=True
            ),
            
            # Application logs (selective backup)
            FileSystemBackupConfig(
                name="application_logs",
                source_path="/var/log/ia-influencer-agent",
                include_patterns=[
                    "*.log",
                    "error_*.log",
                    "audit_*.log",
                    "security_*.log"
                ],
                exclude_patterns=[
                    "debug_*.log",
                    "temp_*.log",
                    "*.pid"
                ],
                compression="gzip",
                preserve_permissions=False
            )
        ]
    
    def get_backup_schedules(self) -> List[BackupSchedule]:
        """Get backup schedule configurations"""
        schedules = []
        
        if self.environment == "production":
            schedules = [
                # Critical databases - every 6 hours
                BackupSchedule(
                    name="critical_databases_frequent",
                    cron_expression="0 */6 * * *",  # Every 6 hours
                    backup_type=BackupType.INCREMENTAL,
                    retention_policy=RetentionPolicy.DAILY_30,
                    retention_days=30,
                    priority=1,
                    timeout_minutes=60
                ),
                
                # Full database backup - daily at 2 AM
                BackupSchedule(
                    name="full_database_backup",
                    cron_expression="0 2 * * *",  # Daily at 2 AM
                    backup_type=BackupType.FULL,
                    retention_policy=RetentionPolicy.MONTHLY_12,
                    retention_days=365,
                    priority=1,
                    timeout_minutes=180
                ),
                
                # File systems - daily at 3 AM
                BackupSchedule(
                    name="filesystem_backup",
                    cron_expression="0 3 * * *",  # Daily at 3 AM
                    backup_type=BackupType.INCREMENTAL,
                    retention_policy=RetentionPolicy.WEEKLY_12,
                    retention_days=90,
                    priority=2,
                    timeout_minutes=240
                ),
                
                # ML models - weekly on Sunday at 4 AM
                BackupSchedule(
                    name="ml_models_backup",
                    cron_expression="0 4 * * 0",  # Weekly on Sunday at 4 AM
                    backup_type=BackupType.FULL,
                    retention_policy=RetentionPolicy.MONTHLY_12,
                    retention_days=365,
                    priority=3,
                    timeout_minutes=120
                ),
                
                # Configuration backup - daily at 1 AM
                BackupSchedule(
                    name="config_backup",
                    cron_expression="0 1 * * *",  # Daily at 1 AM
                    backup_type=BackupType.FULL,
                    retention_policy=RetentionPolicy.WEEKLY_12,
                    retention_days=90,
                    priority=2,
                    timeout_minutes=30
                )
            ]
        elif self.environment == "staging":
            schedules = [
                # Databases - daily at 2 AM
                BackupSchedule(
                    name="database_backup",
                    cron_expression="0 2 * * *",
                    backup_type=BackupType.FULL,
                    retention_policy=RetentionPolicy.WEEKLY_12,
                    retention_days=90,
                    priority=1,
                    timeout_minutes=120
                ),
                
                # File systems - weekly
                BackupSchedule(
                    name="filesystem_backup",
                    cron_expression="0 3 * * 1",  # Monday at 3 AM
                    backup_type=BackupType.FULL,
                    retention_policy=RetentionPolicy.MONTHLY_12,
                    retention_days=90,
                    priority=2,
                    timeout_minutes=180
                )
            ]
        else:  # development
            schedules = [
                # Simple daily backup
                BackupSchedule(
                    name="dev_backup",
                    cron_expression="0 2 * * *",  # Daily at 2 AM
                    backup_type=BackupType.FULL,
                    retention_policy=RetentionPolicy.DAILY_30,
                    retention_days=30,
                    priority=1,
                    timeout_minutes=60
                )
            ]
        
        return schedules
    
    def get_storage_configs(self) -> Dict[str, StorageConfig]:
        """Get storage configurations for different backup destinations"""
        configs = {}
        
        if self.backup_storage == BackupStorage.AWS_S3:
            configs["primary"] = StorageConfig(
                provider=BackupStorage.AWS_S3,
                bucket_name=f"{self.project_name}-{self.environment}-backups",
                region="eu-central-1",
                access_key_env_var="AWS_ACCESS_KEY_ID",
                secret_key_env_var="AWS_SECRET_ACCESS_KEY",
                encryption_enabled=True,
                encryption_key_env_var="AWS_KMS_KEY_ID",
                versioning_enabled=True,
                lifecycle_rules=[
                    {
                        "id": "transition_to_ia",
                        "status": "Enabled",
                        "transitions": [
                            {
                                "days": 30,
                                "storage_class": "STANDARD_IA"
                            },
                            {
                                "days": 90,
                                "storage_class": "GLACIER"
                            },
                            {
                                "days": 365,
                                "storage_class": "DEEP_ARCHIVE"
                            }
                        ]
                    },
                    {
                        "id": "delete_old_versions",
                        "status": "Enabled",
                        "noncurrent_version_expiration": {
                            "noncurrent_days": 90
                        }
                    }
                ]
            )
            
            # Secondary backup location for critical data
            if self.environment == "production":
                configs["secondary"] = StorageConfig(
                    provider=BackupStorage.AWS_S3,
                    bucket_name=f"{self.project_name}-{self.environment}-backups-secondary",
                    region="us-west-2",  # Different region for disaster recovery
                    access_key_env_var="AWS_ACCESS_KEY_ID",
                    secret_key_env_var="AWS_SECRET_ACCESS_KEY",
                    encryption_enabled=True,
                    encryption_key_env_var="AWS_KMS_KEY_ID",
                    versioning_enabled=True
                )
        
        elif self.backup_storage == BackupStorage.AZURE_BLOB:
            configs["primary"] = StorageConfig(
                provider=BackupStorage.AZURE_BLOB,
                bucket_name=f"{self.project_name}{self.environment}backups",
                region="West Europe",
                access_key_env_var="AZURE_STORAGE_ACCOUNT",
                secret_key_env_var="AZURE_STORAGE_KEY",
                encryption_enabled=True,
                versioning_enabled=True
            )
        
        elif self.backup_storage == BackupStorage.LOCAL_NFS:
            configs["primary"] = StorageConfig(
                provider=BackupStorage.LOCAL_NFS,
                bucket_name=f"/mnt/backups/{self.project_name}/{self.environment}",
                region="local",
                encryption_enabled=True,
                encryption_key_env_var="BACKUP_ENCRYPTION_KEY"
            )
        
        return configs
    
    def generate_backup_script(self, schedule: BackupSchedule) -> str:
        """Generate backup script for a specific schedule"""
        db_configs = self.get_database_backup_configs()
        fs_configs = self.get_filesystem_backup_configs()
        storage_configs = self.get_storage_configs()
        
        script = f"""#!/bin/bash
# Backup Script: {schedule.name}
# IA-Influencer Agent Platform - {self.environment}
# Author: Fahed Mlaiel <mlaiel@live.de>

set -euo pipefail

# Configuration
BACKUP_NAME="{schedule.name}"
BACKUP_TYPE="{schedule.backup_type.value}"
ENVIRONMENT="{self.environment}"
PROJECT_NAME="{self.project_name}"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_DIR="/tmp/backup_${{TIMESTAMP}}"
LOG_FILE="/var/log/{self.project_name}/backup_${{BACKUP_NAME}}_${{TIMESTAMP}}.log"
TIMEOUT={schedule.timeout_minutes}m

# Notification settings
NOTIFICATION_EMAILS="{' '.join(schedule.notification_emails)}"
SLACK_WEBHOOK_URL="${{SLACK_WEBHOOK_URL:-}}"

# Create backup directory
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}}

# Error handling
handle_error() {{
    local exit_code=$?
    log "ERROR: Backup failed with exit code $exit_code"
    
    # Send failure notification
    if [[ -n "$NOTIFICATION_EMAILS" ]]; then
        echo "Backup $BACKUP_NAME failed at $(date)" | mail -s "Backup Failure - {self.project_name} {self.environment}" $NOTIFICATION_EMAILS
    fi
    
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        curl -X POST "$SLACK_WEBHOOK_URL" \
             -H 'Content-type: application/json' \
             --data "{{
                 \\"text\\": \\"🚨 Backup Failed: $BACKUP_NAME in {self.environment} environment\\"
             }}" || true
    fi
    
    # Cleanup
    rm -rf "$BACKUP_DIR"
    exit $exit_code
}}

trap handle_error ERR

log "Starting backup: $BACKUP_NAME ($BACKUP_TYPE)"

# Database backups
"""
        
        # Add database backup commands
        for db_config in db_configs:
            if db_config.engine == "postgresql":
                script += f"""
log "Backing up PostgreSQL database: {db_config.name}"
pg_dump -h {db_config.host} -p {db_config.port} -U {db_config.username} \\
        -d {db_config.database} -F {db_config.backup_format} \\
        {"--compress=9" if db_config.compression else ""} \\
        {"--jobs=" + str(db_config.parallel_jobs) if db_config.parallel_jobs > 1 else ""} \\
        -f "$BACKUP_DIR/{db_config.name}_${{TIMESTAMP}}.backup"

if [[ $? -eq 0 ]]; then
    log "PostgreSQL backup completed: {db_config.name}"
else
    log "ERROR: PostgreSQL backup failed: {db_config.name}"
    exit 1
fi
"""
            elif db_config.engine == "redis":
                script += f"""
log "Backing up Redis database: {db_config.name}"
redis-cli -h {db_config.host} -p {db_config.port} --rdb "$BACKUP_DIR/{db_config.name}_${{TIMESTAMP}}.rdb"

if [[ $? -eq 0 ]]; then
    log "Redis backup completed: {db_config.name}"
else
    log "ERROR: Redis backup failed: {db_config.name}"
    exit 1
fi
"""
            elif db_config.engine == "mongodb":
                script += f"""
log "Backing up MongoDB database: {db_config.name}"
mongodump --host {db_config.host}:{db_config.port} \\
          --db {db_config.database} \\
          --username {db_config.username} \\
          --authenticationDatabase admin \\
          --gzip \\
          --out "$BACKUP_DIR/{db_config.name}_${{TIMESTAMP}}"

if [[ $? -eq 0 ]]; then
    log "MongoDB backup completed: {db_config.name}"
else
    log "ERROR: MongoDB backup failed: {db_config.name}"
    exit 1
fi
"""
        
        # Add file system backup commands
        script += """
# File system backups
"""
        for fs_config in fs_configs:
            exclude_args = " ".join([f"--exclude='{pattern}'" for pattern in fs_config.exclude_patterns])
            script += f"""
log "Backing up file system: {fs_config.name}"
tar --create \\
    --{fs_config.compression} \\
    {"--preserve-permissions" if fs_config.preserve_permissions else ""} \\
    {exclude_args} \\
    --file "$BACKUP_DIR/{fs_config.name}_${{TIMESTAMP}}.tar.{fs_config.compression[:2]}" \\
    -C "$(dirname "{fs_config.source_path}")" \\
    "$(basename "{fs_config.source_path}")"

if [[ $? -eq 0 ]]; then
    log "File system backup completed: {fs_config.name}"
else
    log "ERROR: File system backup failed: {fs_config.name}"
    exit 1
fi
"""
        
        # Add upload to storage
        primary_storage = storage_configs.get("primary")
        if primary_storage and primary_storage.provider == BackupStorage.AWS_S3:
            script += f"""
# Upload to AWS S3
log "Uploading backups to S3..."
aws s3 sync "$BACKUP_DIR" s3://{primary_storage.bucket_name}/$(date '+%Y/%m/%d')/{schedule.name}/ \\
    --storage-class STANDARD \\
    {"--sse AES256" if primary_storage.encryption_enabled else ""} \\
    --only-show-errors

if [[ $? -eq 0 ]]; then
    log "S3 upload completed successfully"
else
    log "ERROR: S3 upload failed"
    exit 1
fi
"""
        
        # Add cleanup and notification
        script += f"""
# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "Backup completed successfully. Size: $BACKUP_SIZE"

# Send success notification
if [[ -n "$NOTIFICATION_EMAILS" ]]; then
    echo "Backup $BACKUP_NAME completed successfully at $(date). Size: $BACKUP_SIZE" | \\
    mail -s "Backup Success - {self.project_name} {self.environment}" $NOTIFICATION_EMAILS
fi

if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
    curl -X POST "$SLACK_WEBHOOK_URL" \\
         -H 'Content-type: application/json' \\
         --data "{{
             \\"text\\": \\"✅ Backup Completed: $BACKUP_NAME in {self.environment} environment. Size: $BACKUP_SIZE\\"
         }}" || true
fi

# Cleanup local backup files
log "Cleaning up local backup files..."
rm -rf "$BACKUP_DIR"

# Clean old backups based on retention policy
{self._generate_cleanup_commands(schedule)}

log "Backup process completed successfully"
"""
        
        return script
    
    def _generate_cleanup_commands(self, schedule: BackupSchedule) -> str:
        """Generate cleanup commands based on retention policy"""
        storage_configs = self.get_storage_configs()
        primary_storage = storage_configs.get("primary")
        
        if not primary_storage:
            return ""
        
        if primary_storage.provider == BackupStorage.AWS_S3:
            return f"""
log "Cleaning up old backups (retention: {schedule.retention_days} days)..."
aws s3 ls s3://{primary_storage.bucket_name}/{schedule.name}/ --recursive | \\
    while read -r line; do
        createDate=$(echo $line | awk '{{print $1" "$2}}')
        createDate=$(date -d "$createDate" +%s)
        olderThan=$(date -d "{schedule.retention_days} days ago" +%s)
        
        if [[ $createDate -lt $olderThan ]]; then
            fileName=$(echo $line | awk '{{print $4}}')
            if [[ -n "$fileName" ]]; then
                aws s3 rm s3://{primary_storage.bucket_name}/$fileName
                log "Deleted old backup: $fileName"
            fi
        fi
    done
"""
        else:
            return f"""
log "Cleaning up old local backups (retention: {schedule.retention_days} days)..."
find "{primary_storage.bucket_name}/{schedule.name}" -type f -mtime +{schedule.retention_days} -delete
"""
    
    def generate_restore_script(self, backup_date: str = "latest") -> str:
        """Generate restore script"""
        storage_configs = self.get_storage_configs()
        primary_storage = storage_configs.get("primary")
        
        script = f"""#!/bin/bash
# Restore Script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -euo pipefail

BACKUP_DATE="{backup_date}"
ENVIRONMENT="{self.environment}"
PROJECT_NAME="{self.project_name}"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
RESTORE_DIR="/tmp/restore_${{TIMESTAMP}}"
LOG_FILE="/var/log/{self.project_name}/restore_${{TIMESTAMP}}.log"

# Create restore directory
mkdir -p "$RESTORE_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}}

# Error handling
handle_error() {{
    local exit_code=$?
    log "ERROR: Restore failed with exit code $exit_code"
    rm -rf "$RESTORE_DIR"
    exit $exit_code
}}

trap handle_error ERR

log "Starting restore process for {self.environment} environment"

# Download backups from storage
"""
        
        if primary_storage and primary_storage.provider == BackupStorage.AWS_S3:
            script += f"""
log "Downloading backups from S3..."
if [[ "$BACKUP_DATE" == "latest" ]]; then
    BACKUP_PATH=$(aws s3 ls s3://{primary_storage.bucket_name}/ --recursive | sort | tail -n 1 | awk '{{print $4}}')
    BACKUP_PATH=$(dirname "$BACKUP_PATH")
else
    BACKUP_PATH=$(date -d "$BACKUP_DATE" +%Y/%m/%d)
fi

aws s3 sync s3://{primary_storage.bucket_name}/$BACKUP_PATH/ "$RESTORE_DIR/" --only-show-errors
"""
        
        script += """
# Stop services before restore
log "Stopping services..."
systemctl stop nginx || true
systemctl stop uwsgi || true
systemctl stop celery || true

# Database restore functions
restore_postgresql() {
    local backup_file=$1
    local db_name=$2
    local db_user=$3
    
    log "Restoring PostgreSQL database: $db_name"
    
    # Create backup of current database
    pg_dump -U $db_user -d $db_name -f "/tmp/${db_name}_backup_$(date +%s).sql" || true
    
    # Drop and recreate database
    dropdb -U $db_user $db_name || true
    createdb -U $db_user $db_name
    
    # Restore from backup
    pg_restore -U $db_user -d $db_name -v "$backup_file"
    
    log "PostgreSQL restore completed: $db_name"
}

restore_redis() {
    local backup_file=$1
    
    log "Restoring Redis database"
    
    # Stop Redis
    systemctl stop redis-server
    
    # Copy RDB file
    cp "$backup_file" /var/lib/redis/dump.rdb
    chown redis:redis /var/lib/redis/dump.rdb
    
    # Start Redis
    systemctl start redis-server
    
    log "Redis restore completed"
}

restore_mongodb() {
    local backup_dir=$1
    local db_name=$2
    local db_user=$3
    
    log "Restoring MongoDB database: $db_name"
    
    # Drop existing database
    mongo $db_name --eval "db.dropDatabase()" || true
    
    # Restore from backup
    mongorestore --host localhost:27017 --db $db_name --username $db_user --authenticationDatabase admin --gzip "$backup_dir"
    
    log "MongoDB restore completed: $db_name"
}

# Restore databases
"""
        
        db_configs = self.get_database_backup_configs()
        for db_config in db_configs:
            if db_config.engine == "postgresql":
                script += f"""
if [[ -f "$RESTORE_DIR/{db_config.name}_"*.backup ]]; then
    BACKUP_FILE=$(ls "$RESTORE_DIR/{db_config.name}_"*.backup | head -n 1)
    restore_postgresql "$BACKUP_FILE" "{db_config.database}" "{db_config.username}"
fi
"""
            elif db_config.engine == "redis":
                script += f"""
if [[ -f "$RESTORE_DIR/{db_config.name}_"*.rdb ]]; then
    BACKUP_FILE=$(ls "$RESTORE_DIR/{db_config.name}_"*.rdb | head -n 1)
    restore_redis "$BACKUP_FILE"
fi
"""
            elif db_config.engine == "mongodb":
                script += f"""
if [[ -d "$RESTORE_DIR/{db_config.name}_"* ]]; then
    BACKUP_DIR=$(ls -d "$RESTORE_DIR/{db_config.name}_"*/ | head -n 1)
    restore_mongodb "$BACKUP_DIR/{db_config.database}" "{db_config.database}" "{db_config.username}"
fi
"""
        
        script += """
# Restore file systems
"""
        fs_configs = self.get_filesystem_backup_configs()
        for fs_config in fs_configs:
            script += f"""
if [[ -f "$RESTORE_DIR/{fs_config.name}_"*.tar.* ]]; then
    BACKUP_FILE=$(ls "$RESTORE_DIR/{fs_config.name}_"*.tar.* | head -n 1)
    log "Restoring file system: {fs_config.name}"
    
    # Create backup of existing files
    if [[ -d "{fs_config.source_path}" ]]; then
        mv "{fs_config.source_path}" "{fs_config.source_path}.backup.$(date +%s)" || true
    fi
    
    # Extract backup
    mkdir -p "$(dirname "{fs_config.source_path}")"
    tar --extract --file "$BACKUP_FILE" -C "$(dirname "{fs_config.source_path}")"
    
    # Restore permissions
    {"chown -R www-data:www-data " + fs_config.source_path if fs_config.preserve_permissions else ""}
    
    log "File system restore completed: {fs_config.name}"
fi
"""
        
        script += f"""
# Start services
log "Starting services..."
systemctl start redis-server || true
systemctl start postgresql || true
systemctl start mongodb || true
sleep 5
systemctl start celery || true
systemctl start uwsgi || true
systemctl start nginx || true

# Verify services
log "Verifying services..."
systemctl is-active --quiet postgresql && log "PostgreSQL is running"
systemctl is-active --quiet redis-server && log "Redis is running"
systemctl is-active --quiet mongodb && log "MongoDB is running"
systemctl is-active --quiet nginx && log "Nginx is running"

# Run application health checks
if command -v python >/dev/null 2>&1; then
    python /opt/{self.project_name}/scripts/health_check.py || log "WARNING: Health check failed"
fi

# Cleanup
log "Cleaning up restore files..."
rm -rf "$RESTORE_DIR"

log "Restore process completed successfully"

echo "
================================
RESTORE COMPLETED SUCCESSFULLY
================================
Environment: {self.environment}
Backup Date: $BACKUP_DATE
Restore Log: $LOG_FILE

Please verify that all services are working correctly:
1. Check application logs
2. Verify database connectivity
3. Test critical functionality
4. Monitor system performance

If any issues are found, restore from the backup files created during this process.
"
"""
        
        return script
    
    def generate_monitoring_script(self) -> str:
        """Generate backup monitoring and alerting script"""
        return f"""#!/bin/bash
# Backup Monitoring Script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -euo pipefail

ENVIRONMENT="{self.environment}"
PROJECT_NAME="{self.project_name}"
LOG_FILE="/var/log/{self.project_name}/backup_monitoring.log"
NOTIFICATION_EMAILS="mlaiel@live.de"
SLACK_WEBHOOK_URL="${{SLACK_WEBHOOK_URL:-}}"

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}}

# Send notification
send_alert() {{
    local message="$1"
    local severity="$2"
    
    log "$message"
    
    # Email notification
    if [[ -n "$NOTIFICATION_EMAILS" ]]; then
        echo "$message" | mail -s "Backup Alert - {self.project_name} {self.environment} ($severity)" $NOTIFICATION_EMAILS
    fi
    
    # Slack notification
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        local emoji="⚠️"
        local color="warning"
        
        if [[ "$severity" == "CRITICAL" ]]; then
            emoji="🚨"
            color="danger"
        elif [[ "$severity" == "OK" ]]; then
            emoji="✅"
            color="good"
        fi
        
        curl -X POST "$SLACK_WEBHOOK_URL" \\
             -H 'Content-type: application/json' \\
             --data "{{
                 \\"text\\": \\"$emoji $message\\",
                 \\"color\\": \\"$color\\"
             }}" || true
    fi
}}

log "Starting backup monitoring check"

# Check recent backup completion
LAST_24H=$(date -d '24 hours ago' +%s)
BACKUP_LOG_DIR="/var/log/{self.project_name}"
RECENT_BACKUPS=0

if [[ -d "$BACKUP_LOG_DIR" ]]; then
    for log_file in "$BACKUP_LOG_DIR"/backup_*.log; do
        if [[ -f "$log_file" ]]; then
            file_time=$(stat -c %Y "$log_file")
            if [[ $file_time -gt $LAST_24H ]]; then
                if grep -q "Backup process completed successfully" "$log_file"; then
                    RECENT_BACKUPS=$((RECENT_BACKUPS + 1))
                fi
            fi
        fi
    done
fi

if [[ $RECENT_BACKUPS -eq 0 ]]; then
    send_alert "No successful backups found in the last 24 hours" "CRITICAL"
else
    log "Found $RECENT_BACKUPS successful backups in the last 24 hours"
fi

# Check backup storage space
"""
        
        storage_configs = self.get_storage_configs()
        primary_storage = storage_configs.get("primary")
        
        if primary_storage and primary_storage.provider == BackupStorage.AWS_S3:
            script += f"""
# Check S3 bucket size and costs
BUCKET_SIZE=$(aws s3 ls s3://{primary_storage.bucket_name} --recursive --summarize | grep "Total Size:" | awk '{{print $3}}')
if [[ -n "$BUCKET_SIZE" ]]; then
    BUCKET_SIZE_GB=$((BUCKET_SIZE / 1024 / 1024 / 1024))
    log "Current backup storage usage: ${{BUCKET_SIZE_GB}}GB"
    
    # Alert if over 500GB
    if [[ $BUCKET_SIZE_GB -gt 500 ]]; then
        send_alert "Backup storage usage is high: ${{BUCKET_SIZE_GB}}GB" "WARNING"
    fi
fi

# Check for failed uploads
FAILED_UPLOADS=$(aws logs filter-log-events \\
    --log-group-name "/aws/s3/{primary_storage.bucket_name}" \\
    --start-time $(date -d '24 hours ago' +%s)000 \\
    --filter-pattern "ERROR" \\
    --query 'events[*].message' \\
    --output text | wc -l)

if [[ $FAILED_UPLOADS -gt 0 ]]; then
    send_alert "Found $FAILED_UPLOADS failed S3 uploads in the last 24 hours" "WARNING"
fi
"""
        
        script += f"""
# Check database connectivity
DB_ISSUES=0

# PostgreSQL
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    send_alert "PostgreSQL is not accessible for backups" "CRITICAL"
    DB_ISSUES=$((DB_ISSUES + 1))
fi

# Redis
if ! redis-cli -h localhost -p 6379 ping >/dev/null 2>&1; then
    send_alert "Redis is not accessible for backups" "WARNING"
    DB_ISSUES=$((DB_ISSUES + 1))
fi

# MongoDB
if ! mongosh --host localhost:27017 --eval "db.runCommand('ping')" >/dev/null 2>&1; then
    send_alert "MongoDB is not accessible for backups" "WARNING"
    DB_ISSUES=$((DB_ISSUES + 1))
fi

if [[ $DB_ISSUES -eq 0 ]]; then
    log "All databases are accessible for backup"
fi

# Check disk space on backup locations
DISK_USAGE=$(df /var/log/{self.project_name} | tail -1 | awk '{{print $5}}' | sed 's/%//')
if [[ $DISK_USAGE -gt 85 ]]; then
    send_alert "High disk usage on backup log directory: ${{DISK_USAGE}}%" "WARNING"
fi

TEMP_USAGE=$(df /tmp | tail -1 | awk '{{print $5}}' | sed 's/%//')
if [[ $TEMP_USAGE -gt 80 ]]; then
    send_alert "High disk usage on temporary backup directory: ${{TEMP_USAGE}}%" "WARNING"
fi

# Verify backup integrity (random sampling)
BACKUP_VERIFICATION_PASSED=true

# Check if backup files are not corrupted
for backup_type in "postgresql_main" "redis_main" "user_uploads"; do
    if find /tmp -name "${{backup_type}}_*.backup" -o -name "${{backup_type}}_*.rdb" -o -name "${{backup_type}}_*.tar.*" -mtime -1 | head -1 | while read file; do
        if [[ -f "$file" ]]; then
            case "$file" in
                *.backup)
                    if ! pg_restore --list "$file" >/dev/null 2>&1; then
                        send_alert "Backup file appears corrupted: $file" "CRITICAL"
                        BACKUP_VERIFICATION_PASSED=false
                    fi
                    ;;
                *.rdb)
                    if ! redis-check-rdb "$file" >/dev/null 2>&1; then
                        send_alert "Redis backup file appears corrupted: $file" "CRITICAL"
                        BACKUP_VERIFICATION_PASSED=false
                    fi
                    ;;
                *.tar.*)
                    if ! tar --test-label --file "$file" >/dev/null 2>&1; then
                        send_alert "Archive backup file appears corrupted: $file" "CRITICAL"
                        BACKUP_VERIFICATION_PASSED=false
                    fi
                    ;;
            esac
        fi
    done
done

# Final status report
if [[ $RECENT_BACKUPS -gt 0 && $DB_ISSUES -eq 0 && "$BACKUP_VERIFICATION_PASSED" == "true" ]]; then
    log "All backup monitoring checks passed"
    if [[ $(date +%H) -eq 8 ]]; then  # Daily summary at 8 AM
        send_alert "Daily backup monitoring report: All systems operational. $RECENT_BACKUPS backups completed in last 24h." "OK"
    fi
else
    send_alert "Backup monitoring found issues. Please check logs." "WARNING"
fi

log "Backup monitoring check completed"
"""
        
        return script
    
    def export_configurations(self, output_dir: str = "./backup-configs") -> Dict[str, str]:
        """Export all backup configurations to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        configs = {}
        schedules = self.get_backup_schedules()
        
        # Export backup scripts
        for schedule in schedules:
            script_content = self.generate_backup_script(schedule)
            script_path = os.path.join(output_dir, f"backup_{schedule.name}_{self.environment}.sh")
            with open(script_path, 'w') as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)
            configs[f'backup_{schedule.name}'] = script_path
        
        # Export restore script
        restore_script = self.generate_restore_script()
        restore_path = os.path.join(output_dir, f"restore_{self.environment}.sh")
        with open(restore_path, 'w') as f:
            f.write(restore_script)
        os.chmod(restore_path, 0o755)
        configs['restore_script'] = restore_path
        
        # Export monitoring script
        monitoring_script = self.generate_monitoring_script()
        monitoring_path = os.path.join(output_dir, f"monitor_backups_{self.environment}.sh")
        with open(monitoring_path, 'w') as f:
            f.write(monitoring_script)
        os.chmod(monitoring_path, 0o755)
        configs['monitoring_script'] = monitoring_path
        
        # Export configuration summary
        config_summary = {
            "environment": self.environment,
            "project_name": self.project_name,
            "backup_storage": self.backup_storage.value,
            "retention_strategy": self.retention_strategy.value,
            "schedules": [
                {
                    "name": s.name,
                    "cron": s.cron_expression,
                    "type": s.backup_type.value,
                    "retention_days": s.retention_days
                }
                for s in schedules
            ],
            "databases": [
                {
                    "name": db.name,
                    "engine": db.engine,
                    "host": db.host,
                    "port": db.port,
                    "database": db.database
                }
                for db in self.get_database_backup_configs()
            ],
            "filesystems": [
                {
                    "name": fs.name,
                    "source_path": fs.source_path,
                    "compression": fs.compression
                }
                for fs in self.get_filesystem_backup_configs()
            ]
        }
        
        summary_path = os.path.join(output_dir, f"backup_config_{self.environment}.json")
        with open(summary_path, 'w') as f:
            json.dump(config_summary, f, indent=2)
        configs['config_summary'] = summary_path
        
        return configs
