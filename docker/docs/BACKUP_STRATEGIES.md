# Backup Strategies Guide

## Comprehensive Backup Solutions for Ainflue Docker Platform

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 3.0  
**Date:** September 2025

### Backup Overview

Multi-layered backup strategy for data protection, configuration preservation, and disaster recovery across all Ainflue services.

### Database Backups

#### 1. PostgreSQL Automated Backups
```bash
#!/bin/bash
# postgresql-backup.sh

BACKUP_DIR="/backup/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker exec ainflue-postgres pg_dump -U ainflue -d ainflue_prod > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://ainflue-backups/postgresql/

# Cleanup old backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
```

#### 2. MongoDB Backup Strategy
```bash
#!/bin/bash
# mongodb-backup.sh

BACKUP_DIR="/backup/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)

# MongoDB dump
docker exec ainflue-mongodb mongodump --db ainflue --out $BACKUP_DIR/$DATE

# Create archive
tar -czf $BACKUP_DIR/mongodb_backup_$DATE.tar.gz -C $BACKUP_DIR $DATE

# Upload to cloud storage
rclone copy $BACKUP_DIR/mongodb_backup_$DATE.tar.gz remote:ainflue-backups/mongodb/

# Cleanup
rm -rf $BACKUP_DIR/$DATE
```

#### 3. Redis Persistence Backup
```yaml
# Redis backup configuration
services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --appendfsync everysec
    volumes:
      - redis-data:/data
      - ./backup:/backup

# Backup script
version: '3.8'
services:
  redis-backup:
    image: redis:7-alpine
    volumes:
      - redis-data:/data:ro
      - ./backup:/backup
    command: sh -c "cp /data/appendonly.aof /backup/redis_$(date +%Y%m%d_%H%M%S).aof"
```

### Volume and File System Backups

#### 1. Docker Volume Backup
```bash
#!/bin/bash
# volume-backup.sh

VOLUMES=$(docker volume ls -q)
BACKUP_DIR="/backup/volumes"
DATE=$(date +%Y%m%d_%H%M%S)

for volume in $VOLUMES; do
    echo "Backing up volume: $volume"
    
    # Create backup directory
    mkdir -p $BACKUP_DIR/$volume
    
    # Backup volume using temporary container
    docker run --rm \
        -v $volume:/data:ro \
        -v $BACKUP_DIR/$volume:/backup \
        alpine tar -czf /backup/backup_$DATE.tar.gz -C /data .
    
    # Upload to cloud storage
    aws s3 cp $BACKUP_DIR/$volume/backup_$DATE.tar.gz \
        s3://ainflue-backups/volumes/$volume/
done
```

#### 2. Configuration Backup
```bash
#!/bin/bash
# config-backup.sh

CONFIG_DIRS=("/etc/docker" "/var/lib/docker/swarm" "/opt/ainflue/configs")
BACKUP_DIR="/backup/configs"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup Docker configs
docker config ls --format "{{.Name}}" | while read config; do
    docker config inspect $config > $BACKUP_DIR/docker-configs/$config.json
done

# Backup Docker secrets (metadata only)
docker secret ls --format "{{.Name}}" | while read secret; do
    docker secret inspect $secret > $BACKUP_DIR/docker-secrets/$secret.json
done

# Backup configuration directories
for dir in "${CONFIG_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        tar -czf $BACKUP_DIR/$(basename $dir)_$DATE.tar.gz -C $(dirname $dir) $(basename $dir)
    fi
done
```

### Application Data Backup

#### 1. Media Files Backup
```python
# media-backup.py
import os
import boto3
from datetime import datetime, timedelta

class MediaBackup:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'ainflue-media-backups'
        
    def backup_media_files(self, source_path, prefix):
        """Backup media files to S3"""
        for root, dirs, files in os.walk(source_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, source_path)
                s3_key = f"{prefix}/{relative_path}"
                
                # Check if file already exists and is unchanged
                if not self._file_changed(file_path, s3_key):
                    continue
                    
                self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
                print(f"Uploaded: {s3_key}")
    
    def _file_changed(self, local_path, s3_key):
        """Check if local file differs from S3 version"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            local_mtime = os.path.getmtime(local_path)
            s3_mtime = response['LastModified'].timestamp()
            return local_mtime > s3_mtime
        except:
            return True  # File doesn't exist in S3

# Usage
backup = MediaBackup()
backup.backup_media_files('/app/media/audio', 'audio')
backup.backup_media_files('/app/media/images', 'images')
```

### Incremental Backup Strategy

#### 1. Rsync-based Incremental Backups
```bash
#!/bin/bash
# incremental-backup.sh

SOURCE_DIR="/var/lib/docker/volumes"
BACKUP_BASE="/backup/incremental"
CURRENT_BACKUP="$BACKUP_BASE/current"
PREVIOUS_BACKUP="$BACKUP_BASE/previous"

# Create backup directories
mkdir -p $CURRENT_BACKUP $PREVIOUS_BACKUP

# Perform incremental backup
rsync -av --delete --link-dest=$PREVIOUS_BACKUP $SOURCE_DIR/ $CURRENT_BACKUP/

# Rotate backups
if [ -d "$PREVIOUS_BACKUP" ]; then
    rm -rf $BACKUP_BASE/old
    mv $PREVIOUS_BACKUP $BACKUP_BASE/old
fi
mv $CURRENT_BACKUP $PREVIOUS_BACKUP

echo "Incremental backup completed: $(date)"
```

#### 2. Git-based Configuration Backup
```bash
#!/bin/bash
# git-config-backup.sh

CONFIG_REPO="/backup/config-repo"
cd $CONFIG_REPO

# Copy current configurations
cp -r /opt/ainflue/configs/* .
cp /etc/docker/daemon.json docker/
cp -r /var/lib/docker/swarm/docker-state.json docker/

# Commit changes
git add .
git commit -m "Automated backup: $(date)"
git push origin main

echo "Configuration backup committed to Git"
```

### Automated Backup Orchestration

#### 1. Backup Scheduler Service
```yaml
# backup-scheduler service
version: '3.8'
services:
  backup-scheduler:
    image: alpine:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /backup:/backup
      - ./scripts:/scripts
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    command: crond -f
    configs:
      - source: backup-crontab
        target: /etc/crontabs/root

configs:
  backup-crontab:
    content: |
      # Daily database backups at 2 AM
      0 2 * * * /scripts/postgresql-backup.sh
      15 2 * * * /scripts/mongodb-backup.sh
      
      # Hourly incremental backups
      0 * * * * /scripts/incremental-backup.sh
      
      # Weekly full system backup
      0 3 * * 0 /scripts/full-system-backup.sh
```

#### 2. Backup Monitoring
```python
# backup-monitor.py
import os
import time
from datetime import datetime, timedelta
from prometheus_client import Gauge, Counter

BACKUP_AGE = Gauge('backup_age_hours', 'Age of last backup in hours', ['backup_type'])
BACKUP_SIZE = Gauge('backup_size_bytes', 'Size of last backup in bytes', ['backup_type'])
BACKUP_SUCCESS = Counter('backup_success_total', 'Successful backups', ['backup_type'])
BACKUP_FAILURE = Counter('backup_failure_total', 'Failed backups', ['backup_type'])

def monitor_backups():
    backup_paths = {
        'postgresql': '/backup/postgresql',
        'mongodb': '/backup/mongodb',
        'volumes': '/backup/volumes'
    }
    
    for backup_type, path in backup_paths.items():
        try:
            # Find latest backup file
            files = [f for f in os.listdir(path) if f.endswith('.gz')]
            if not files:
                continue
                
            latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(path, x)))
            file_path = os.path.join(path, latest_file)
            
            # Calculate age
            mtime = os.path.getmtime(file_path)
            age_hours = (time.time() - mtime) / 3600
            
            # Get size
            size_bytes = os.path.getsize(file_path)
            
            # Update metrics
            BACKUP_AGE.labels(backup_type=backup_type).set(age_hours)
            BACKUP_SIZE.labels(backup_type=backup_type).set(size_bytes)
            
        except Exception as e:
            print(f"Error monitoring {backup_type} backup: {e}")
```

### Backup Verification

#### 1. Automated Backup Testing
```bash
#!/bin/bash
# verify-backup.sh

BACKUP_FILE=$1
TEST_CONTAINER="backup-test"

echo "Verifying backup: $BACKUP_FILE"

# Test PostgreSQL backup
if [[ $BACKUP_FILE == *"postgresql"* ]]; then
    docker run --name $TEST_CONTAINER -d postgres:15
    docker exec $TEST_CONTAINER createdb test_restore
    docker exec -i $TEST_CONTAINER psql -d test_restore < $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        echo "PostgreSQL backup verification: PASSED"
    else
        echo "PostgreSQL backup verification: FAILED"
    fi
    
    docker rm -f $TEST_CONTAINER
fi

# Test volume backup
if [[ $BACKUP_FILE == *"volume"* ]]; then
    docker run --name $TEST_CONTAINER -v test-volume:/data alpine sh -c "tar -xzf - -C /data" < $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        echo "Volume backup verification: PASSED"
    else
        echo "Volume backup verification: FAILED"
    fi
    
    docker rm -f $TEST_CONTAINER
    docker volume rm test-volume
fi
```

### Cloud Backup Integration

#### 1. Multi-Cloud Backup Strategy
```python
# multi-cloud-backup.py
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage

class MultiCloudBackup:
    def __init__(self):
        # AWS S3
        self.s3_client = boto3.client('s3')
        
        # Azure Blob Storage
        self.azure_client = BlobServiceClient.from_connection_string(
            os.environ['AZURE_STORAGE_CONNECTION_STRING']
        )
        
        # Google Cloud Storage
        self.gcs_client = storage.Client()
    
    def upload_to_all_clouds(self, file_path, key):
        """Upload backup to all cloud providers"""
        
        # Upload to AWS S3
        self.s3_client.upload_file(file_path, 'ainflue-backups-aws', key)
        
        # Upload to Azure
        blob_client = self.azure_client.get_blob_client(
            container='ainflue-backups', blob=key
        )
        with open(file_path, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)
        
        # Upload to Google Cloud
        bucket = self.gcs_client.bucket('ainflue-backups-gcp')
        blob = bucket.blob(key)
        blob.upload_from_filename(file_path)
        
        print(f"Backup {key} uploaded to all cloud providers")
```

### Recovery Testing

#### 1. Disaster Recovery Simulation
```bash
#!/bin/bash
# disaster-recovery-test.sh

echo "Starting disaster recovery simulation..."

# Stop all services
docker stack rm ainflue

# Clear volumes (simulation of data loss)
docker volume prune -f

# Restore from backup
./restore-from-backup.sh latest

# Restart services
docker stack deploy -c docker-compose.production.yml ainflue

# Verify services are healthy
sleep 60
docker service ls --filter "label=com.docker.stack.namespace=ainflue"

echo "Disaster recovery simulation completed"
```

### Backup Best Practices

1. **3-2-1 Rule**: 3 copies of data, 2 different media types, 1 offsite
2. **Regular Testing**: Test backup restoration procedures regularly
3. **Encryption**: Encrypt backups both in transit and at rest
4. **Monitoring**: Monitor backup success/failure and age
5. **Documentation**: Maintain detailed recovery procedures
6. **Automation**: Automate backup processes to reduce human error
7. **Retention Policy**: Implement appropriate backup retention policies