"""
Enterprise Backup Utilities - Comprehensive Data Backup and Recovery System
==========================================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Expert Roles: DBA Expert + Backend Senior + DevOps Expert + Security Expert
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive backup and recovery capabilities including
database backups, file system backups, automated scheduling, and disaster recovery.
"""

import asyncio
import bz2
import gzip
import hashlib
import json
import logging
import os
import shutil
import sqlite3
import subprocess
import tempfile
import threading
import time
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
import pickle
import secrets

# Third-party imports with fallbacks
try:
    import boto3
    from botocore.exceptions import NoCredentialsError, ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    import pymongo
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    import psycopg2
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@dataclass
class BackupMetadata:
    """Backup metadata information"""
    backup_id: str
    backup_type: str  # full, incremental, differential
    source: str
    destination: str
    start_time: datetime
    end_time: Optional[datetime] = None
    size_bytes: int = 0
    compressed_size_bytes: int = 0
    file_count: int = 0
    checksum: Optional[str] = None
    encryption_key_id: Optional[str] = None
    compression_type: str = "none"
    status: str = "running"  # running, completed, failed, cancelled
    error_message: Optional[str] = None
    retention_policy: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class BackupJob:
    """Backup job configuration"""
    job_id: str
    name: str
    backup_type: str
    source_config: Dict[str, Any]
    destination_config: Dict[str, Any]
    schedule: Optional[str] = None  # cron expression
    retention_days: int = 30
    compression: bool = True
    encryption: bool = False
    enabled: bool = True
    max_parallel_jobs: int = 1
    timeout_minutes: int = 60
    pre_backup_script: Optional[str] = None
    post_backup_script: Optional[str] = None
    notification_config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


@dataclass
class RestorePoint:
    """Recovery point information"""
    restore_id: str
    backup_id: str
    timestamp: datetime
    restore_type: str  # full, partial, point_in_time
    size_bytes: int
    location: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    verification_status: str = "unknown"  # verified, failed, unknown


@dataclass
class BackupStatistics:
    """Backup operation statistics"""
    total_backups: int = 0
    successful_backups: int = 0
    failed_backups: int = 0
    total_size_bytes: int = 0
    average_backup_time: float = 0.0
    success_rate: float = 0.0
    storage_efficiency: float = 0.0  # compression ratio
    oldest_backup: Optional[datetime] = None
    newest_backup: Optional[datetime] = None


class CompressionHandler:
    """Handle different compression algorithms"""
    
    COMPRESSION_TYPES = {
        'gzip': {'ext': '.gz', 'module': gzip, 'mode': 'wb'},
        'bzip2': {'ext': '.bz2', 'module': bz2, 'mode': 'wb'},
        'zip': {'ext': '.zip', 'handler': 'zipfile'},
        'none': {'ext': '', 'handler': 'none'}
    }
    
    @classmethod
    def compress_file(cls, source_path: Path, compression_type: str = 'gzip') -> Path:
        """Compress a file using specified algorithm"""
        if compression_type not in cls.COMPRESSION_TYPES:
            raise ValueError(f"Unsupported compression type: {compression_type}")
        
        config = cls.COMPRESSION_TYPES[compression_type]
        
        if compression_type == 'none':
            return source_path
        
        compressed_path = source_path.with_suffix(source_path.suffix + config['ext'])
        
        if compression_type == 'zip':
            with zipfile.ZipFile(compressed_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(source_path, source_path.name)
        else:
            with open(source_path, 'rb') as src:
                with config['module'].open(compressed_path, config['mode']) as dst:
                    shutil.copyfileobj(src, dst)
        
        return compressed_path
    
    @classmethod
    def decompress_file(cls, compressed_path: Path, output_path: Optional[Path] = None) -> Path:
        """Decompress a file"""
        if output_path is None:
            output_path = compressed_path.with_suffix('')
        
        # Detect compression type by extension
        compression_type = None
        for comp_type, config in cls.COMPRESSION_TYPES.items():
            if compressed_path.suffix == config['ext']:
                compression_type = comp_type
                break
        
        if compression_type is None or compression_type == 'none':
            return compressed_path
        
        config = cls.COMPRESSION_TYPES[compression_type]
        
        if compression_type == 'zip':
            with zipfile.ZipFile(compressed_path, 'r') as zf:
                zf.extractall(output_path.parent)
        else:
            with config['module'].open(compressed_path, 'rb') as src:
                with open(output_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
        
        return output_path


class EncryptionHandler:
    """Handle backup encryption and decryption"""
    
    def __init__(self, encryption_key -> None: Optional[bytes] = None) -> None:
        self.encryption_key = encryption_key or self._generate_key()
        self.key_id = hashlib.sha256(self.encryption_key).hexdigest()[:16]
    
    def _generate_key(self) -> bytes:
        """Generate a new encryption key"""
        return secrets.token_bytes(32)  # 256-bit key
    
    def encrypt_file(self, source_path: Path, encrypted_path: Optional[Path] = None) -> Tuple[Path, str]:
        """Encrypt a file (simplified implementation)"""
        if encrypted_path is None:
            encrypted_path = source_path.with_suffix(source_path.suffix + '.enc')
        
        # For demonstration - in production, use proper encryption like AES
        with open(source_path, 'rb') as src:
            data = src.read()
        
        # Simple XOR encryption (replace with proper encryption in production)
        encrypted_data = bytes(a ^ b for a, b in zip(data, self.encryption_key * (len(data) // len(self.encryption_key) + 1)))
        
        with open(encrypted_path, 'wb') as dst:
            # Write key ID first
            dst.write(self.key_id.encode())
            dst.write(b'\n')
            dst.write(encrypted_data)
        
        return encrypted_path, self.key_id
    
    def decrypt_file(self, encrypted_path: Path, output_path: Optional[Path] = None) -> Path:
        """Decrypt a file"""
        if output_path is None:
            output_path = encrypted_path.with_suffix('')
        
        with open(encrypted_path, 'rb') as src:
            # Read key ID
            key_id_line = src.readline()
            stored_key_id = key_id_line.decode().strip()
            
            if stored_key_id != self.key_id:
                raise ValueError("Invalid encryption key")
            
            encrypted_data = src.read()
        
        # Decrypt (reverse XOR)
        decrypted_data = bytes(a ^ b for a, b in zip(encrypted_data, self.encryption_key * (len(encrypted_data) // len(self.encryption_key) + 1)))
        
        with open(output_path, 'wb') as dst:
            dst.write(decrypted_data)
        
        return output_path


class DatabaseBackupHandler:
    """Handle database-specific backup operations"""
    
    def __init__(self) -> None:
        self.supported_databases = {
            'postgresql': self._backup_postgresql if POSTGRESQL_AVAILABLE else None,
            'mysql': self._backup_mysql if MYSQL_AVAILABLE else None,
            'mongodb': self._backup_mongodb if MONGODB_AVAILABLE else None,
            'sqlite': self._backup_sqlite,
            'redis': self._backup_redis if REDIS_AVAILABLE else None
        }
    
    def backup_database(self, db_config: Dict[str, Any], backup_path: Path) -> BackupMetadata:
        """Backup database based on type"""
        db_type = db_config.get('type', '').lower()
        
        if db_type not in self.supported_databases:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        backup_handler = self.supported_databases[db_type]
        if backup_handler is None:
            raise RuntimeError(f"Database driver for {db_type} not available")
        
        backup_id = f"{db_type}_backup_{int(time.time())}"
        start_time = datetime.now()
        
        try:
            result = backup_handler(db_config, backup_path)
            end_time = datetime.now()
            
            # Calculate backup size
            size_bytes = backup_path.stat().st_size if backup_path.exists() else 0
            
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type='full',
                source=f"{db_type}://{db_config.get('host', 'localhost')}/{db_config.get('database', '')}",
                destination=str(backup_path),
                start_time=start_time,
                end_time=end_time,
                size_bytes=size_bytes,
                compressed_size_bytes=size_bytes,
                status='completed',
                tags={'database_type': db_type}
            )
            
            return metadata
            
        except Exception as e:
            end_time = datetime.now()
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type='full',
                source=f"{db_type}://{db_config.get('host', 'localhost')}/{db_config.get('database', '')}",
                destination=str(backup_path),
                start_time=start_time,
                end_time=end_time,
                status='failed',
                error_message=str(e),
                tags={'database_type': db_type}
            )
            raise
    
    def _backup_postgresql(self, db_config: Dict[str, Any], backup_path: Path) -> Dict[str, Any]:
        """Backup PostgreSQL database using pg_dump"""
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 5432)
        database = db_config.get('database')
        username = db_config.get('username')
        password = db_config.get('password')
        
        if not database:
            raise ValueError("Database name is required for PostgreSQL backup")
        
        # Prepare pg_dump command
        cmd = [
            'pg_dump',
            f'--host={host}',
            f'--port={port}',
            f'--username={username}',
            '--format=custom',
            '--no-password',
            '--verbose',
            f'--file={backup_path}',
            database
        ]
        
        env = os.environ.copy()
        if password:
            env['PGPASSWORD'] = password
        
        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=3600)
            
            if result.returncode != 0:
                raise RuntimeError(f"pg_dump failed: {result.stderr}")
            
            return {'stdout': result.stdout, 'stderr': result.stderr}
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("PostgreSQL backup timed out")
        except FileNotFoundError:
            raise RuntimeError("pg_dump command not found. Please install PostgreSQL client tools.")
    
    def _backup_mysql(self, db_config: Dict[str, Any], backup_path: Path) -> Dict[str, Any]:
        """Backup MySQL database using mysqldump"""
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 3306)
        database = db_config.get('database')
        username = db_config.get('username')
        password = db_config.get('password')
        
        if not database:
            raise ValueError("Database name is required for MySQL backup")
        
        # Prepare mysqldump command
        cmd = [
            'mysqldump',
            f'--host={host}',
            f'--port={port}',
            f'--user={username}',
            '--single-transaction',
            '--routines',
            '--triggers',
            '--result-file=' + str(backup_path),
            database
        ]
        
        if password:
            cmd.append(f'--password={password}')
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode != 0:
                raise RuntimeError(f"mysqldump failed: {result.stderr}")
            
            return {'stdout': result.stdout, 'stderr': result.stderr}
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("MySQL backup timed out")
        except FileNotFoundError:
            raise RuntimeError("mysqldump command not found. Please install MySQL client tools.")
    
    def _backup_mongodb(self, db_config: Dict[str, Any], backup_path: Path) -> Dict[str, Any]:
        """Backup MongoDB database using mongodump"""
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 27017)
        database = db_config.get('database')
        username = db_config.get('username')
        password = db_config.get('password')
        
        # Prepare mongodump command
        cmd = [
            'mongodump',
            '--host', f'{host}:{port}',
            '--out', str(backup_path.parent),
        ]
        
        if database:
            cmd.extend(['--db', database])
        
        if username:
            cmd.extend(['--username', username])
        
        if password:
            cmd.extend(['--password', password])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode != 0:
                raise RuntimeError(f"mongodump failed: {result.stderr}")
            
            # mongodump creates a directory structure, compress it
            dump_dir = backup_path.parent / (database or 'dump')
            if dump_dir.exists():
                shutil.make_archive(str(backup_path.with_suffix('')), 'zip', dump_dir)
                shutil.rmtree(dump_dir)
            
            return {'stdout': result.stdout, 'stderr': result.stderr}
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("MongoDB backup timed out")
        except FileNotFoundError:
            raise RuntimeError("mongodump command not found. Please install MongoDB tools.")
    
    def _backup_sqlite(self, db_config: Dict[str, Any], backup_path: Path) -> Dict[str, Any]:
        """Backup SQLite database"""
        database_path = db_config.get('database_path')
        
        if not database_path or not os.path.exists(database_path):
            raise ValueError("Valid database_path is required for SQLite backup")
        
        try:
            # For SQLite, we can use the .backup() method or simple file copy
            source_conn = sqlite3.connect(database_path)
            backup_conn = sqlite3.connect(str(backup_path))
            
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            return {'method': 'sqlite_backup_api'}
            
        except Exception as e:
            # Fallback to file copy
            try:
                shutil.copy2(database_path, backup_path)
                return {'method': 'file_copy', 'fallback_reason': str(e)}
            except Exception as copy_error:
                raise RuntimeError(f"SQLite backup failed: {copy_error}")
    
    def _backup_redis(self, db_config: Dict[str, Any], backup_path: Path) -> Dict[str, Any]:
        """Backup Redis database"""
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 6379)
        password = db_config.get('password')
        db = db_config.get('db', 0)
        
        try:
            r = redis.Redis(host=host, port=port, password=password, db=db, decode_responses=True)
            
            # Get all keys and their values
            keys = r.keys('*')
            backup_data = {}
            
            for key in keys:
                key_type = r.type(key)
                
                if key_type == 'string':
                    backup_data[key] = {'type': 'string', 'value': r.get(key)}
                elif key_type == 'hash':
                    backup_data[key] = {'type': 'hash', 'value': r.hgetall(key)}
                elif key_type == 'list':
                    backup_data[key] = {'type': 'list', 'value': r.lrange(key, 0, -1)}
                elif key_type == 'set':
                    backup_data[key] = {'type': 'set', 'value': list(r.smembers(key))}
                elif key_type == 'zset':
                    backup_data[key] = {'type': 'zset', 'value': r.zrange(key, 0, -1, withscores=True)}
                
                # Get TTL if exists
                ttl = r.ttl(key)
                if ttl > 0:
                    backup_data[key]['ttl'] = ttl
            
            # Save to file
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            return {'keys_backed_up': len(keys)}
            
        except Exception as e:
            raise RuntimeError(f"Redis backup failed: {e}")


class FileSystemBackupHandler:
    """Handle file system backup operations"""
    
    def __init__(self) -> None:
        self.ignore_patterns = {
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '.git',
            '.svn',
            '.DS_Store',
            'Thumbs.db',
            '*.tmp',
            '*.temp',
            'node_modules',
            '.env'
        }
    
    def backup_directory(self, source_path: Path, backup_path: Path, 
                        backup_type: str = 'full', 
                        last_backup_time: Optional[datetime] = None) -> BackupMetadata:
        """Backup directory with support for full, incremental, and differential backups"""
        
        backup_id = f"fs_backup_{int(time.time())}"
        start_time = datetime.now()
        
        try:
            if backup_type == 'full':
                copied_files = self._full_backup(source_path, backup_path)
            elif backup_type == 'incremental':
                if last_backup_time is None:
                    raise ValueError("Last backup time required for incremental backup")
                copied_files = self._incremental_backup(source_path, backup_path, last_backup_time)
            elif backup_type == 'differential':
                if last_backup_time is None:
                    raise ValueError("Last backup time required for differential backup")
                copied_files = self._differential_backup(source_path, backup_path, last_backup_time)
            else:
                raise ValueError(f"Unsupported backup type: {backup_type}")
            
            end_time = datetime.now()
            
            # Calculate total size
            total_size = sum(f['size'] for f in copied_files)
            
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=backup_type,
                source=str(source_path),
                destination=str(backup_path),
                start_time=start_time,
                end_time=end_time,
                size_bytes=total_size,
                compressed_size_bytes=total_size,
                file_count=len(copied_files),
                status='completed',
                tags={'backup_method': 'filesystem'}
            )
            
            # Save file manifest
            manifest_path = backup_path / 'backup_manifest.json'
            with open(manifest_path, 'w') as f:
                json.dump({
                    'metadata': {
                        'backup_id': backup_id,
                        'backup_type': backup_type,
                        'start_time': start_time.isoformat(),
                        'end_time': end_time.isoformat(),
                        'source': str(source_path)
                    },
                    'files': copied_files
                }, f, indent=2)
            
            return metadata
            
        except Exception as e:
            end_time = datetime.now()
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=backup_type,
                source=str(source_path),
                destination=str(backup_path),
                start_time=start_time,
                end_time=end_time,
                status='failed',
                error_message=str(e)
            )
            raise
    
    def _full_backup(self, source_path: Path, backup_path: Path) -> List[Dict[str, Any]]:
        """Perform full backup"""
        backup_path.mkdir(parents=True, exist_ok=True)
        copied_files = []
        
        for item in source_path.rglob('*'):
            if self._should_ignore(item):
                continue
            
            if item.is_file():
                relative_path = item.relative_to(source_path)
                dest_path = backup_path / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file with metadata
                shutil.copy2(item, dest_path)
                
                file_info = {
                    'path': str(relative_path),
                    'size': item.stat().st_size,
                    'mtime': item.stat().st_mtime,
                    'checksum': self._calculate_checksum(item)
                }
                copied_files.append(file_info)
        
        return copied_files
    
    def _incremental_backup(self, source_path: Path, backup_path: Path, 
                          last_backup_time: datetime) -> List[Dict[str, Any]]:
        """Perform incremental backup (only files changed since last backup)"""
        backup_path.mkdir(parents=True, exist_ok=True)
        copied_files = []
        
        last_backup_timestamp = last_backup_time.timestamp()
        
        for item in source_path.rglob('*'):
            if self._should_ignore(item):
                continue
            
            if item.is_file() and item.stat().st_mtime > last_backup_timestamp:
                relative_path = item.relative_to(source_path)
                dest_path = backup_path / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(item, dest_path)
                
                file_info = {
                    'path': str(relative_path),
                    'size': item.stat().st_size,
                    'mtime': item.stat().st_mtime,
                    'checksum': self._calculate_checksum(item)
                }
                copied_files.append(file_info)
        
        return copied_files
    
    def _differential_backup(self, source_path: Path, backup_path: Path, 
                           last_full_backup_time: datetime) -> List[Dict[str, Any]]:
        """Perform differential backup (all files changed since last full backup)"""
        return self._incremental_backup(source_path, backup_path, last_full_backup_time)
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored based on patterns"""
        import fnmatch
        
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(str(path), pattern):
                return True
        
        return False
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()


class BackupStorage:
    """Handle backup storage to different destinations"""
    
    def __init__(self) -> None:
        self.storage_handlers = {
            'local': self._local_storage,
            's3': self._s3_storage if AWS_AVAILABLE else None,
            'ftp': self._ftp_storage,
            'sftp': self._sftp_storage
        }
    
    def store_backup(self, backup_path: Path, storage_config: Dict[str, Any]) -> str:
        """Store backup to configured destination"""
        storage_type = storage_config.get('type', 'local').lower()
        
        if storage_type not in self.storage_handlers:
            raise ValueError(f"Unsupported storage type: {storage_type}")
        
        handler = self.storage_handlers[storage_type]
        if handler is None:
            raise RuntimeError(f"Storage handler for {storage_type} not available")
        
        return handler(backup_path, storage_config)
    
    def _local_storage(self, backup_path: Path, config: Dict[str, Any]) -> str:
        """Store backup to local filesystem"""
        destination_path = Path(config['destination'])
        destination_path.mkdir(parents=True, exist_ok=True)
        
        final_path = destination_path / backup_path.name
        shutil.copy2(backup_path, final_path)
        
        return str(final_path)
    
    def _s3_storage(self, backup_path: Path, config: Dict[str, Any]) -> str:
        """Store backup to AWS S3"""
        bucket_name = config['bucket']
        key_prefix = config.get('prefix', 'backups/')
        
        try:
            s3_client = boto3.client('s3')
            
            # Upload file
            key = f"{key_prefix}{backup_path.name}"
            s3_client.upload_file(str(backup_path), bucket_name, key)
            
            return f"s3://{bucket_name}/{key}"
            
        except NoCredentialsError:
            raise RuntimeError("AWS credentials not configured")
        except ClientError as e:
            raise RuntimeError(f"S3 upload failed: {e}")
    
    def _ftp_storage(self, backup_path: Path, config: Dict[str, Any]) -> str:
        """Store backup to FTP server"""
        # This is a placeholder - implement FTP storage as needed
        raise NotImplementedError("FTP storage not implemented")
    
    def _sftp_storage(self, backup_path: Path, config: Dict[str, Any]) -> str:
        """Store backup to SFTP server"""
        # This is a placeholder - implement SFTP storage as needed
        raise NotImplementedError("SFTP storage not implemented")


class BackupScheduler:
    """Handle backup job scheduling and execution"""
    
    def __init__(self, backup_manager) -> None:
        self.backup_manager = backup_manager
        self.scheduled_jobs: Dict[str, BackupJob] = {}
        self.running_jobs: Dict[str, threading.Thread] = {}
        self.stop_event = threading.Event()
        self.scheduler_thread: Optional[threading.Thread] = None
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
    
    def add_job(self, job -> None: BackupJob) -> None:
        """Add a backup job to the scheduler"""
        self.scheduled_jobs[job.job_id] = job
        self._calculate_next_run(job)
        self.logger.info(f"Added backup job: {job.name} ({job.job_id})")
    
    def remove_job(self, job_id -> None: str) -> None:
        """Remove a backup job from the scheduler"""
        if job_id in self.scheduled_jobs:
            del self.scheduled_jobs[job_id]
            self.logger.info(f"Removed backup job: {job_id}")
        
        # Stop running job if exists
        if job_id in self.running_jobs:
            # Note: In a production system, you'd want to gracefully stop the thread
            self.logger.warning(f"Job {job_id} was running when removed")
    
    def start_scheduler(self) -> None:
        """Start the backup scheduler"""
        if self.scheduler_thread is not None and self.scheduler_thread.is_alive():
            return
        
        self.stop_event.clear()
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("Backup scheduler started")
    
    def stop_scheduler(self) -> None:
        """Stop the backup scheduler"""
        self.stop_event.set()
        
        if self.scheduler_thread is not None:
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Backup scheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while not self.stop_event.is_set():
            try:
                current_time = datetime.now()
                
                for job in list(self.scheduled_jobs.values()):
                    if (job.enabled and 
                        job.next_run is not None and 
                        current_time >= job.next_run and
                        job.job_id not in self.running_jobs):
                        
                        # Check if we can run more parallel jobs
                        active_jobs = sum(1 for t in self.running_jobs.values() if t.is_alive())
                        
                        if active_jobs < job.max_parallel_jobs:
                            self._run_job(job)
                
                # Clean up finished threads
                finished_jobs = [
                    job_id for job_id, thread in self.running_jobs.items()
                    if not thread.is_alive()
                ]
                
                for job_id in finished_jobs:
                    del self.running_jobs[job_id]
                
                # Sleep for a minute before next check
                self.stop_event.wait(60)
                
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                self.stop_event.wait(60)
    
    def _run_job(self, job -> None: BackupJob) -> None:
        """Run a backup job"""
        def job_runner() -> None:
            try:
                self.logger.info(f"Starting backup job: {job.name}")
                
                # Run pre-backup script if configured
                if job.pre_backup_script:
                    self._run_script(job.pre_backup_script)
                
                # Execute backup
                metadata = self.backup_manager.create_backup(
                    source_config=job.source_config,
                    destination_config=job.destination_config,
                    backup_type=job.backup_type,
                    compression=job.compression,
                    encryption=job.encryption
                )
                
                # Run post-backup script if configured
                if job.post_backup_script:
                    self._run_script(job.post_backup_script)
                
                # Update job timing
                job.last_run = datetime.now()
                self._calculate_next_run(job)
                
                # Send success notification
                self._send_notification(job, "success", metadata)
                
                self.logger.info(f"Backup job completed successfully: {job.name}")
                
            except Exception as e:
                self.logger.error(f"Backup job failed: {job.name} - {e}")
                
                # Send failure notification
                self._send_notification(job, "failure", None, str(e))
                
                # Still update next run time
                job.last_run = datetime.now()
                self._calculate_next_run(job)
        
        # Start job in background thread
        job_thread = threading.Thread(target=job_runner, daemon=True)
        job_thread.start()
        self.running_jobs[job.job_id] = job_thread
    
    def _calculate_next_run(self, job -> None: BackupJob) -> None:
        """Calculate next run time based on schedule"""
        if not job.schedule:
            job.next_run = None
            return
        
        # Simple scheduling - in production, use a proper cron parser
        current_time = datetime.now()
        
        # Parse simple schedule formats
        if job.schedule.startswith('daily'):
            job.next_run = current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif job.schedule.startswith('weekly'):
            days_ahead = 7 - current_time.weekday()
            job.next_run = current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
        elif job.schedule.startswith('hourly'):
            job.next_run = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        else:
            # Default to daily if unknown format
            job.next_run = current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    def _run_script(self, script_path -> None: str) -> None:
        """Run pre/post backup script"""
        try:
            result = subprocess.run([script_path], capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                self.logger.warning(f"Script {script_path} failed: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Failed to run script {script_path}: {e}")
    
    def _send_notification(self, job -> None: BackupJob, status -> None: str, metadata -> None: Optional[BackupMetadata], error -> None: Optional[str] = None) -> None:
        """Send backup completion notification"""
        notification_config = job.notification_config
        
        if not notification_config:
            return
        
        # Placeholder for notification implementation
        # In production, implement email, Slack, webhook notifications
        message = f"Backup job '{job.name}' {status}"
        if error:
            message += f": {error}"
        
        self.logger.info(f"Notification: {message}")


class BackupManager:
    """Main backup management class orchestrating all backup operations"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.database_handler = DatabaseBackupHandler()
        self.filesystem_handler = FileSystemBackupHandler()
        self.storage = BackupStorage()
        self.compression_handler = CompressionHandler()
        self.encryption_handler = EncryptionHandler()
        self.scheduler = BackupScheduler(self)
        
        # Backup metadata storage
        self.metadata_store: Dict[str, BackupMetadata] = {}
        self.restore_points: Dict[str, RestorePoint] = {}
        
        # Configure logging
        logging.basicConfig(
            level=self.config.get('log_level', logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load existing metadata
        self._load_metadata()
    
    def create_backup(self, source_config: Dict[str, Any], destination_config: Dict[str, Any],
                     backup_type: str = 'full', compression: bool = True, 
                     encryption: bool = False) -> BackupMetadata:
        """Create a backup based on configuration"""
        
        source_type = source_config.get('type', '').lower()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create initial backup
            if source_type in ['postgresql', 'mysql', 'mongodb', 'sqlite', 'redis']:
                backup_file = temp_path / f"backup_{int(time.time())}.{source_type}"
                metadata = self.database_handler.backup_database(source_config, backup_file)
                
            elif source_type == 'filesystem':
                backup_dir = temp_path / f"backup_{int(time.time())}"
                source_path = Path(source_config['path'])
                last_backup_time = source_config.get('last_backup_time')
                
                metadata = self.filesystem_handler.backup_directory(
                    source_path, backup_dir, backup_type, last_backup_time
                )
                backup_file = backup_dir
                
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
            
            # Apply compression if requested
            if compression and backup_file.is_file():
                compression_type = self.config.get('compression_type', 'gzip')
                compressed_file = self.compression_handler.compress_file(backup_file, compression_type)
                backup_file = compressed_file
                metadata.compression_type = compression_type
                metadata.compressed_size_bytes = backup_file.stat().st_size
            
            # Apply encryption if requested
            encryption_key_id = None
            if encryption:
                encrypted_file, encryption_key_id = self.encryption_handler.encrypt_file(backup_file)
                backup_file = encrypted_file
                metadata.encryption_key_id = encryption_key_id
            
            # Calculate checksum
            if backup_file.is_file():
                metadata.checksum = self._calculate_file_checksum(backup_file)
            
            # Store backup to destination
            try:
                final_location = self.storage.store_backup(backup_file, destination_config)
                metadata.destination = final_location
                
                # Store metadata
                self.metadata_store[metadata.backup_id] = metadata
                self._save_metadata()
                
                # Create restore point
                restore_point = RestorePoint(
                    restore_id=f"restore_{metadata.backup_id}",
                    backup_id=metadata.backup_id,
                    timestamp=metadata.end_time or metadata.start_time,
                    restore_type=backup_type,
                    size_bytes=metadata.size_bytes,
                    location=final_location
                )
                self.restore_points[restore_point.restore_id] = restore_point
                
                self.logger.info(f"Backup completed successfully: {metadata.backup_id}")
                return metadata
                
            except Exception as e:
                metadata.status = 'failed'
                metadata.error_message = str(e)
                self.logger.error(f"Backup storage failed: {e}")
                raise
    
    def restore_backup(self, backup_id: str, restore_config: Dict[str, Any]) -> bool:
        """Restore from a backup"""
        
        if backup_id not in self.metadata_store:
            raise ValueError(f"Backup not found: {backup_id}")
        
        metadata = self.metadata_store[backup_id]
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Download/copy backup file
                backup_file = self._retrieve_backup(metadata, temp_path)
                
                # Decrypt if necessary
                if metadata.encryption_key_id:
                    backup_file = self.encryption_handler.decrypt_file(backup_file)
                
                # Decompress if necessary
                if metadata.compression_type != 'none':
                    backup_file = self.compression_handler.decompress_file(backup_file)
                
                # Verify checksum if available
                if metadata.checksum:
                    if self._calculate_file_checksum(backup_file) != metadata.checksum:
                        raise RuntimeError("Backup file integrity check failed")
                
                # Perform restore based on backup type
                return self._restore_data(backup_file, metadata, restore_config)
                
        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
            raise
    
    def list_backups(self, filters: Optional[Dict[str, Any]] = None) -> List[BackupMetadata]:
        """List available backups with optional filtering"""
        backups = list(self.metadata_store.values())
        
        if filters:
            # Apply filters
            if 'status' in filters:
                backups = [b for b in backups if b.status == filters['status']]
            
            if 'backup_type' in filters:
                backups = [b for b in backups if b.backup_type == filters['backup_type']]
            
            if 'start_date' in filters:
                start_date = filters['start_date']
                backups = [b for b in backups if b.start_time >= start_date]
            
            if 'end_date' in filters:
                end_date = filters['end_date']
                backups = [b for b in backups if b.start_time <= end_date]
        
        return sorted(backups, key=lambda x: x.start_time, reverse=True)
    
    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup and its metadata"""
        if backup_id not in self.metadata_store:
            raise ValueError(f"Backup not found: {backup_id}")
        
        metadata = self.metadata_store[backup_id]
        
        try:
            # Delete backup file (implementation depends on storage type)
            self._delete_backup_file(metadata)
            
            # Remove from metadata store
            del self.metadata_store[backup_id]
            
            # Remove associated restore points
            restore_points_to_remove = [
                rp_id for rp_id, rp in self.restore_points.items()
                if rp.backup_id == backup_id
            ]
            
            for rp_id in restore_points_to_remove:
                del self.restore_points[rp_id]
            
            self._save_metadata()
            
            self.logger.info(f"Backup deleted: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete backup {backup_id}: {e}")
            return False
    
    def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """Clean up backups older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0
        
        backups_to_delete = [
            backup_id for backup_id, metadata in self.metadata_store.items()
            if metadata.start_time < cutoff_date
        ]
        
        for backup_id in backups_to_delete:
            try:
                self.delete_backup(backup_id)
                deleted_count += 1
            except Exception as e:
                self.logger.error(f"Failed to delete old backup {backup_id}: {e}")
        
        self.logger.info(f"Cleaned up {deleted_count} old backups")
        return deleted_count
    
    def get_backup_statistics(self) -> BackupStatistics:
        """Get backup statistics"""
        backups = list(self.metadata_store.values())
        
        if not backups:
            return BackupStatistics()
        
        successful_backups = [b for b in backups if b.status == 'completed']
        failed_backups = [b for b in backups if b.status == 'failed']
        
        total_size = sum(b.size_bytes for b in successful_backups)
        total_compressed_size = sum(b.compressed_size_bytes for b in successful_backups)
        
        backup_times = [
            (b.end_time - b.start_time).total_seconds()
            for b in successful_backups
            if b.end_time
        ]
        
        avg_backup_time = sum(backup_times) / len(backup_times) if backup_times else 0.0
        
        return BackupStatistics(
            total_backups=len(backups),
            successful_backups=len(successful_backups),
            failed_backups=len(failed_backups),
            total_size_bytes=total_size,
            average_backup_time=avg_backup_time,
            success_rate=(len(successful_backups) / len(backups)) * 100,
            storage_efficiency=(1 - (total_compressed_size / total_size)) * 100 if total_size > 0 else 0,
            oldest_backup=min(b.start_time for b in backups),
            newest_backup=max(b.start_time for b in backups)
        )
    
    def verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity"""
        if backup_id not in self.metadata_store:
            raise ValueError(f"Backup not found: {backup_id}")
        
        metadata = self.metadata_store[backup_id]
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Retrieve backup file
                backup_file = self._retrieve_backup(metadata, temp_path)
                
                # Verify checksum
                if metadata.checksum:
                    calculated_checksum = self._calculate_file_checksum(backup_file)
                    if calculated_checksum != metadata.checksum:
                        return False
                
                # Try to decompress/decrypt to verify structure
                if metadata.encryption_key_id:
                    backup_file = self.encryption_handler.decrypt_file(backup_file)
                
                if metadata.compression_type != 'none':
                    backup_file = self.compression_handler.decompress_file(backup_file)
                
                return True
                
        except Exception as e:
            self.logger.error(f"Backup verification failed: {e}")
            return False
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _retrieve_backup(self, metadata: BackupMetadata, temp_path: Path) -> Path:
        """Retrieve backup file from storage"""
        # This is a simplified implementation
        # In production, implement proper retrieval from different storage types
        
        if metadata.destination.startswith('s3://'):
            # S3 retrieval
            if not AWS_AVAILABLE:
                raise RuntimeError("AWS SDK not available for S3 retrieval")
            
            # Parse S3 URL
            s3_parts = metadata.destination.replace('s3://', '').split('/', 1)
            bucket = s3_parts[0]
            key = s3_parts[1]
            
            s3_client = boto3.client('s3')
            local_file = temp_path / Path(key).name
            s3_client.download_file(bucket, key, str(local_file))
            
            return local_file
        
        else:
            # Local file system
            source_path = Path(metadata.destination)
            local_file = temp_path / source_path.name
            shutil.copy2(source_path, local_file)
            
            return local_file
    
    def _restore_data(self, backup_file: Path, metadata: BackupMetadata, restore_config: Dict[str, Any]) -> bool:
        """Restore data from backup file"""
        # This is a simplified implementation
        # In production, implement proper restore logic for each backup type
        
        source_parts = metadata.source.split('://')
        if len(source_parts) == 2:
            source_type = source_parts[0]
            
            if source_type in ['postgresql', 'mysql', 'mongodb', 'sqlite', 'redis']:
                return self._restore_database(backup_file, source_type, restore_config)
            elif source_type == 'filesystem' or '/' in metadata.source:
                return self._restore_filesystem(backup_file, restore_config)
        
        raise ValueError(f"Unsupported restore source: {metadata.source}")
    
    def _restore_database(self, backup_file: Path, db_type: str, restore_config: Dict[str, Any]) -> bool:
        """Restore database from backup"""
        # Placeholder implementation
        # In production, implement proper database restore procedures
        self.logger.info(f"Restoring {db_type} database from {backup_file}")
        return True
    
    def _restore_filesystem(self, backup_file: Path, restore_config: Dict[str, Any]) -> bool:
        """Restore filesystem from backup"""
        # Placeholder implementation
        # In production, implement proper file system restore procedures
        restore_path = Path(restore_config['destination'])
        
        if backup_file.is_dir():
            shutil.copytree(backup_file, restore_path, dirs_exist_ok=True)
        else:
            # Handle archived backups
            if backup_file.suffix == '.zip':
                with zipfile.ZipFile(backup_file, 'r') as zf:
                    zf.extractall(restore_path)
        
        self.logger.info(f"Restored filesystem to {restore_path}")
        return True
    
    def _delete_backup_file(self, metadata -> None: BackupMetadata) -> None:
        """Delete backup file from storage"""
        # This is a simplified implementation
        if metadata.destination.startswith('s3://'):
            if AWS_AVAILABLE:
                s3_parts = metadata.destination.replace('s3://', '').split('/', 1)
                bucket = s3_parts[0]
                key = s3_parts[1]
                
                s3_client = boto3.client('s3')
                s3_client.delete_object(Bucket=bucket, Key=key)
        else:
            # Local file system
            backup_path = Path(metadata.destination)
            if backup_path.exists():
                if backup_path.is_dir():
                    shutil.rmtree(backup_path)
                else:
                    backup_path.unlink()
    
    def _load_metadata(self) -> None:
        """Load backup metadata from storage"""
        metadata_file = Path(self.config.get('metadata_file', 'backup_metadata.json'))
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                
                # Deserialize metadata
                for backup_id, metadata_dict in data.get('backups', {}).items():
                    metadata = BackupMetadata(**metadata_dict)
                    # Convert datetime strings back to datetime objects
                    metadata.start_time = datetime.fromisoformat(metadata_dict['start_time'])
                    if metadata_dict.get('end_time'):
                        metadata.end_time = datetime.fromisoformat(metadata_dict['end_time'])
                    
                    self.metadata_store[backup_id] = metadata
                
                # Deserialize restore points
                for restore_id, rp_dict in data.get('restore_points', {}).items():
                    restore_point = RestorePoint(**rp_dict)
                    restore_point.timestamp = datetime.fromisoformat(rp_dict['timestamp'])
                    
                    self.restore_points[restore_id] = restore_point
                
                self.logger.info(f"Loaded {len(self.metadata_store)} backup records")
                
            except Exception as e:
                self.logger.error(f"Failed to load metadata: {e}")
    
    def _save_metadata(self) -> None:
        """Save backup metadata to storage"""
        metadata_file = Path(self.config.get('metadata_file', 'backup_metadata.json'))
        
        try:
            data = {
                'backups': {},
                'restore_points': {}
            }
            
            # Serialize metadata
            for backup_id, metadata in self.metadata_store.items():
                metadata_dict = metadata.__dict__.copy()
                metadata_dict['start_time'] = metadata.start_time.isoformat()
                if metadata.end_time:
                    metadata_dict['end_time'] = metadata.end_time.isoformat()
                
                data['backups'][backup_id] = metadata_dict
            
            # Serialize restore points
            for restore_id, restore_point in self.restore_points.items():
                rp_dict = restore_point.__dict__.copy()
                rp_dict['timestamp'] = restore_point.timestamp.isoformat()
                
                data['restore_points'][restore_id] = rp_dict
            
            with open(metadata_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")


# Export main classes and utilities
__all__ = [
    'BackupManager',
    'BackupMetadata',
    'BackupJob',
    'RestorePoint',
    'BackupStatistics',
    'DatabaseBackupHandler',
    'FileSystemBackupHandler',
    'BackupStorage',
    'BackupScheduler',
    'CompressionHandler',
    'EncryptionHandler'
]