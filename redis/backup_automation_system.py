#!/usr/bin/env python3
"""
Redis Backup Automation System - Ainflue Platform
=================================================

Advanced backup automation with intelligent scheduling, compression,
encryption, and multi-tier storage management.

Author: Fahed Mlaiel (mlaiel@live.de)
Roles: Lead Dev IA + Backend Senior + DBA + DevOps + Sécurité
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import os
import gzip
import lz4.frame
import hashlib
import base64
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from redis.asyncio.cluster import RedisCluster
import boto3
import aiofiles
import aiohttp
from datetime import datetime, timedelta
import yaml
from cryptography.fernet import Fernet
import schedule
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BackupStatus(Enum):
    """Backup status enumeration"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    VERIFYING = "verifying"


class CompressionType(Enum):
    """Compression algorithm types"""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"


class StorageTier(Enum):
    """Storage tier types"""
    HOT = "hot"          # Fast access, high cost
    WARM = "warm"        # Medium access, medium cost
    COLD = "cold"        # Slow access, low cost
    ARCHIVE = "archive"  # Very slow access, very low cost


@dataclass
class BackupSchedule:
    """Backup schedule configuration"""
    schedule_id: str
    name: str
    cron_expression: str
    backup_type: str
    enabled: bool
    retention_days: int
    compression: CompressionType
    encryption: bool
    storage_tier: StorageTier
    notification_on_failure: bool
    notification_on_success: bool
    max_parallel_backups: int
    timeout_minutes: int
    last_run: Optional[float] = None
    next_run: Optional[float] = None


@dataclass
class BackupTask:
    """Individual backup task"""
    task_id: str
    schedule_id: str
    backup_type: str
    status: BackupStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    file_path: Optional[str] = None
    file_size: int = 0
    compressed_size: int = 0
    checksum: Optional[str] = None
    storage_location: Optional[str] = None
    storage_tier: Optional[StorageTier] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = None


@dataclass
class BackupMetrics:
    """Backup system metrics"""
    total_backups: int
    successful_backups: int
    failed_backups: int
    total_size_bytes: int
    compression_ratio: float
    average_duration: float
    last_backup_time: Optional[float]
    next_scheduled_backup: Optional[float]
    storage_usage_by_tier: Dict[StorageTier, int]


class RedisBackupAutomationSystem:
    """
    Advanced Redis Backup Automation System
    
    Features:
    - Intelligent backup scheduling
    - Multiple compression algorithms
    - Encryption and security
    - Multi-tier storage management
    - Automatic retention management
    - Parallel backup execution
    - Comprehensive monitoring
    - Disaster recovery integration
    """

    def __init__(self, cluster_client: RedisCluster, config: Dict[str, Any] = None):
        """Initialize backup automation system"""
        self.cluster_client = cluster_client
        self.config = config or self._get_default_config()
        
        # Backup management
        self.backup_schedules: Dict[str, BackupSchedule] = {}
        self.active_tasks: Dict[str, BackupTask] = {}
        self.task_history: List[BackupTask] = []
        
        # Encryption
        self.encryption_key = None
        if self.config.get('encryption', {}).get('enabled', True):
            self._initialize_encryption()
        
        # Storage clients
        self.storage_clients = {}
        
        # Monitoring
        self.monitoring_tasks: List[asyncio.Task] = []
        self.metrics: Optional[BackupMetrics] = None
        
        # Scheduler
        self.scheduler_thread = None
        self.scheduler_running = False

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'storage': {
                'primary': {
                    'type': 's3',
                    'bucket': 'ainflue-redis-backups',
                    'region': 'us-west-2',
                    'storage_class': 'STANDARD'
                },
                'archive': {
                    'type': 's3',
                    'bucket': 'ainflue-redis-archive',
                    'region': 'us-west-2',
                    'storage_class': 'GLACIER'
                }
            },
            'compression': {
                'default_algorithm': 'lz4',
                'compression_level': 6
            },
            'encryption': {
                'enabled': True,
                'key_rotation_days': 90
            },
            'retention': {
                'default_days': 30,
                'hot_tier_days': 7,
                'warm_tier_days': 30,
                'cold_tier_days': 90,
                'archive_tier_days': 365
            },
            'parallelism': {
                'max_concurrent_backups': 3,
                'max_parallel_uploads': 5
            },
            'monitoring': {
                'metrics_enabled': True,
                'alerts_enabled': True,
                'webhook_url': None
            },
            'validation': {
                'checksum_verification': True,
                'test_restore_frequency': 7  # days
            }
        }

    def _initialize_encryption(self) -> None:
        """Initialize encryption system"""
        try:
            # Generate or load encryption key
            key_file = self.config.get('encryption', {}).get('key_file', '/etc/redis/backup.key')
            
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                # Generate new key
                self.encryption_key = Fernet.generate_key()
                
                # Save key securely
                os.makedirs(os.path.dirname(key_file), exist_ok=True)
                with open(key_file, 'wb') as f:
                    f.write(self.encryption_key)
                os.chmod(key_file, 0o600)
            
            logger.info("Encryption system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            self.encryption_key = None

    async def initialize(self) -> None:
        """Initialize backup automation system"""
        try:
            # Initialize storage clients
            await self._initialize_storage_clients()
            
            # Load backup schedules
            await self._load_backup_schedules()
            
            # Start scheduler
            await self._start_scheduler()
            
            # Start monitoring
            await self._start_monitoring()
            
            logger.info("Backup automation system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize backup automation system: {e}")
            raise

    async def _initialize_storage_clients(self) -> None:
        """Initialize storage clients"""
        try:
            storage_config = self.config.get('storage', {})
            
            for tier, config in storage_config.items():
                if config.get('type') == 's3':
                    self.storage_clients[tier] = boto3.client(
                        's3',
                        region_name=config.get('region', 'us-west-2')
                    )
                    
                    # Ensure bucket exists
                    bucket_name = config.get('bucket')
                    try:
                        self.storage_clients[tier].head_bucket(Bucket=bucket_name)
                    except:
                        # Create bucket
                        self.storage_clients[tier].create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={
                                'LocationConstraint': config.get('region', 'us-west-2')
                            }
                        )
            
            logger.info(f"Storage clients initialized for {len(self.storage_clients)} tiers")
            
        except Exception as e:
            logger.error(f"Failed to initialize storage clients: {e}")

    async def _load_backup_schedules(self) -> None:
        """Load backup schedules"""
        try:
            # Load from configuration or create defaults
            schedules_config = self.config.get('schedules', [])
            
            if not schedules_config:
                schedules_config = self._get_default_schedules()
            
            for schedule_config in schedules_config:
                schedule = BackupSchedule(
                    schedule_id=schedule_config['schedule_id'],
                    name=schedule_config['name'],
                    cron_expression=schedule_config['cron_expression'],
                    backup_type=schedule_config['backup_type'],
                    enabled=schedule_config.get('enabled', True),
                    retention_days=schedule_config.get('retention_days', 30),
                    compression=CompressionType(schedule_config.get('compression', 'lz4')),
                    encryption=schedule_config.get('encryption', True),
                    storage_tier=StorageTier(schedule_config.get('storage_tier', 'hot')),
                    notification_on_failure=schedule_config.get('notification_on_failure', True),
                    notification_on_success=schedule_config.get('notification_on_success', False),
                    max_parallel_backups=schedule_config.get('max_parallel_backups', 1),
                    timeout_minutes=schedule_config.get('timeout_minutes', 60)
                )
                
                self.backup_schedules[schedule.schedule_id] = schedule
            
            logger.info(f"Loaded {len(self.backup_schedules)} backup schedules")
            
        except Exception as e:
            logger.error(f"Failed to load backup schedules: {e}")

    def _get_default_schedules(self) -> List[Dict[str, Any]]:
        """Get default backup schedules"""
        return [
            {
                'schedule_id': 'full_daily',
                'name': 'Daily Full Backup',
                'cron_expression': '0 2 * * *',  # 2 AM daily
                'backup_type': 'full',
                'enabled': True,
                'retention_days': 30,
                'compression': 'lz4',
                'encryption': True,
                'storage_tier': 'warm',
                'notification_on_failure': True,
                'timeout_minutes': 120
            },
            {
                'schedule_id': 'incremental_hourly',
                'name': 'Hourly Incremental Backup',
                'cron_expression': '0 * * * *',  # Every hour
                'backup_type': 'incremental',
                'enabled': True,
                'retention_days': 7,
                'compression': 'lz4',
                'encryption': True,
                'storage_tier': 'hot',
                'notification_on_failure': True,
                'timeout_minutes': 30
            },
            {
                'schedule_id': 'snapshot_frequent',
                'name': 'Frequent Snapshots',
                'cron_expression': '*/15 * * * *',  # Every 15 minutes
                'backup_type': 'snapshot',
                'enabled': True,
                'retention_days': 1,
                'compression': 'lz4',
                'encryption': False,
                'storage_tier': 'hot',
                'notification_on_failure': False,
                'timeout_minutes': 10
            },
            {
                'schedule_id': 'weekly_archive',
                'name': 'Weekly Archive Backup',
                'cron_expression': '0 1 * * 0',  # 1 AM every Sunday
                'backup_type': 'full',
                'enabled': True,
                'retention_days': 365,
                'compression': 'gzip',
                'encryption': True,
                'storage_tier': 'archive',
                'notification_on_success': True,
                'timeout_minutes': 240
            }
        ]

    async def _start_scheduler(self) -> None:
        """Start backup scheduler"""
        try:
            # Configure schedules
            for schedule in self.backup_schedules.values():
                if schedule.enabled:
                    self._schedule_backup_job(schedule)
            
            # Start scheduler thread
            self.scheduler_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            logger.info("Backup scheduler started")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")

    def _schedule_backup_job(self, backup_schedule: BackupSchedule) -> None:
        """Schedule a backup job"""
        try:
            # Parse cron expression and schedule job
            # This is simplified - in production would use proper cron parsing
            cron_parts = backup_schedule.cron_expression.split()
            
            if len(cron_parts) == 5:
                minute, hour, day, month, weekday = cron_parts
                
                # Convert to schedule syntax
                if minute == '*' and hour == '*':
                    # Every minute (for testing)
                    schedule.every().minute.do(self._trigger_backup, backup_schedule.schedule_id)
                elif minute.startswith('*/'):
                    # Every N minutes
                    interval = int(minute[2:])
                    schedule.every(interval).minutes.do(self._trigger_backup, backup_schedule.schedule_id)
                elif hour == '*':
                    # Every hour at specific minute
                    schedule.every().hour.at(f":{minute.zfill(2)}").do(self._trigger_backup, backup_schedule.schedule_id)
                elif day == '*' and month == '*' and weekday == '*':
                    # Daily at specific time
                    schedule.every().day.at(f"{hour.zfill(2)}:{minute.zfill(2)}").do(self._trigger_backup, backup_schedule.schedule_id)
                elif weekday != '*':
                    # Weekly on specific day
                    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                    weekday_name = weekdays[int(weekday)]
                    getattr(schedule.every(), weekday_name).at(f"{hour.zfill(2)}:{minute.zfill(2)}").do(self._trigger_backup, backup_schedule.schedule_id)
                
                logger.debug(f"Scheduled backup job: {backup_schedule.name}")
                
        except Exception as e:
            logger.error(f"Failed to schedule backup job {backup_schedule.schedule_id}: {e}")

    def _run_scheduler(self) -> None:
        """Run the scheduler thread"""
        while self.scheduler_running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")

    def _trigger_backup(self, schedule_id: str) -> None:
        """Trigger backup execution"""
        try:
            if schedule_id in self.backup_schedules:
                # Create async task for backup execution
                asyncio.create_task(self._execute_backup(schedule_id))
        except Exception as e:
            logger.error(f"Failed to trigger backup {schedule_id}: {e}")

    async def _start_monitoring(self) -> None:
        """Start monitoring tasks"""
        try:
            # Metrics collection task
            metrics_task = asyncio.create_task(self._metrics_collection_loop())
            self.monitoring_tasks.append(metrics_task)
            
            # Task monitoring task
            task_monitor_task = asyncio.create_task(self._task_monitoring_loop())
            self.monitoring_tasks.append(task_monitor_task)
            
            # Retention management task
            retention_task = asyncio.create_task(self._retention_management_loop())
            self.monitoring_tasks.append(retention_task)
            
            # Storage tier management task
            tier_management_task = asyncio.create_task(self._storage_tier_management_loop())
            self.monitoring_tasks.append(tier_management_task)
            
            logger.info(f"Started {len(self.monitoring_tasks)} monitoring tasks")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")

    async def _execute_backup(self, schedule_id: str) -> BackupTask:
        """Execute backup task"""
        try:
            if schedule_id not in self.backup_schedules:
                raise ValueError(f"Schedule {schedule_id} not found")
            
            backup_schedule = self.backup_schedules[schedule_id]
            
            # Check parallel backup limit
            active_count = len([task for task in self.active_tasks.values() 
                              if task.schedule_id == schedule_id and task.status == BackupStatus.RUNNING])
            
            if active_count >= backup_schedule.max_parallel_backups:
                logger.warning(f"Parallel backup limit reached for schedule {schedule_id}")
                return None
            
            # Create backup task
            task_id = f"backup_{schedule_id}_{int(time.time())}"
            
            backup_task = BackupTask(
                task_id=task_id,
                schedule_id=schedule_id,
                backup_type=backup_schedule.backup_type,
                status=BackupStatus.SCHEDULED,
                created_at=time.time(),
                metadata={
                    'schedule_name': backup_schedule.name,
                    'compression': backup_schedule.compression.value,
                    'encryption': backup_schedule.encryption,
                    'storage_tier': backup_schedule.storage_tier.value
                }
            )
            
            self.active_tasks[task_id] = backup_task
            
            # Execute backup
            await self._perform_backup(backup_task, backup_schedule)
            
            return backup_task
            
        except Exception as e:
            logger.error(f"Backup execution failed for schedule {schedule_id}: {e}")
            if 'backup_task' in locals():
                backup_task.status = BackupStatus.FAILED
                backup_task.error_message = str(e)
                backup_task.completed_at = time.time()
            return None

    async def _perform_backup(self, backup_task: BackupTask, backup_schedule: BackupSchedule) -> None:
        """Perform the actual backup"""
        try:
            backup_task.status = BackupStatus.RUNNING
            backup_task.started_at = time.time()
            
            logger.info(f"Starting backup task {backup_task.task_id}")
            
            # Create backup data based on type
            if backup_task.backup_type == 'full':
                backup_data = await self._create_full_backup()
            elif backup_task.backup_type == 'incremental':
                backup_data = await self._create_incremental_backup()
            elif backup_task.backup_type == 'snapshot':
                backup_data = await self._create_snapshot_backup()
            else:
                raise ValueError(f"Unknown backup type: {backup_task.backup_type}")
            
            backup_task.file_size = len(backup_data)
            
            # Compress data
            if backup_schedule.compression != CompressionType.NONE:
                backup_data = await self._compress_data(backup_data, backup_schedule.compression)
                backup_task.compressed_size = len(backup_data)
            else:
                backup_task.compressed_size = backup_task.file_size
            
            # Encrypt data
            if backup_schedule.encryption and self.encryption_key:
                backup_data = await self._encrypt_data(backup_data)
            
            # Calculate checksum
            backup_task.checksum = hashlib.sha256(backup_data).hexdigest()
            
            # Store backup
            storage_location = await self._store_backup_data(backup_task, backup_data, backup_schedule)
            backup_task.storage_location = storage_location
            backup_task.storage_tier = backup_schedule.storage_tier
            
            # Verify backup
            backup_task.status = BackupStatus.VERIFYING
            verification_success = await self._verify_backup(backup_task)
            
            if verification_success:
                backup_task.status = BackupStatus.COMPLETED
                backup_task.completed_at = time.time()
                
                # Update schedule
                backup_schedule.last_run = backup_task.completed_at
                
                logger.info(f"Backup task {backup_task.task_id} completed successfully")
                
                # Send success notification if configured
                if backup_schedule.notification_on_success:
                    await self._send_notification(backup_task, "Backup completed successfully")
            else:
                backup_task.status = BackupStatus.FAILED
                backup_task.error_message = "Backup verification failed"
                backup_task.completed_at = time.time()
                
                logger.error(f"Backup task {backup_task.task_id} verification failed")
            
            # Move to history
            self.task_history.append(backup_task)
            if backup_task.task_id in self.active_tasks:
                del self.active_tasks[backup_task.task_id]
                
        except Exception as e:
            logger.error(f"Backup task {backup_task.task_id} failed: {e}")
            backup_task.status = BackupStatus.FAILED
            backup_task.error_message = str(e)
            backup_task.completed_at = time.time()
            
            # Send failure notification
            if backup_schedule.notification_on_failure:
                await self._send_notification(backup_task, f"Backup failed: {str(e)}")

    async def _create_full_backup(self) -> bytes:
        """Create full backup"""
        try:
            # Get all data from cluster
            backup_data = {
                'timestamp': time.time(),
                'backup_type': 'full',
                'cluster_config': await self._get_cluster_configuration(),
                'data': {}
            }
            
            # Get data from all master nodes
            nodes_info = await self.cluster_client.cluster_nodes()
            
            for line in nodes_info.split('\n'):
                if line.strip() and 'master' in line:
                    parts = line.split()
                    if len(parts) >= 8:
                        node_id = parts[0]
                        endpoint = parts[1].split('@')[0]
                        host, port = endpoint.split(':')
                        
                        # Get node data
                        node_data = await self._backup_node_data(host, int(port))
                        backup_data['data'][node_id] = node_data
            
            return json.dumps(backup_data, default=str).encode('utf-8')
            
        except Exception as e:
            logger.error(f"Full backup creation failed: {e}")
            raise

    async def _create_incremental_backup(self) -> bytes:
        """Create incremental backup"""
        try:
            # Find last full backup
            last_full_backup = None
            for task in reversed(self.task_history):
                if task.backup_type == 'full' and task.status == BackupStatus.COMPLETED:
                    last_full_backup = task
                    break
            
            if not last_full_backup:
                # No full backup, create one instead
                return await self._create_full_backup()
            
            # Create incremental backup data
            backup_data = {
                'timestamp': time.time(),
                'backup_type': 'incremental',
                'base_backup': last_full_backup.task_id,
                'changes': await self._get_incremental_changes(last_full_backup.completed_at)
            }
            
            return json.dumps(backup_data, default=str).encode('utf-8')
            
        except Exception as e:
            logger.error(f"Incremental backup creation failed: {e}")
            raise

    async def _create_snapshot_backup(self) -> bytes:
        """Create snapshot backup"""
        try:
            # Trigger snapshots on all nodes
            snapshot_data = {
                'timestamp': time.time(),
                'backup_type': 'snapshot',
                'snapshots': {}
            }
            
            nodes_info = await self.cluster_client.cluster_nodes()
            
            for line in nodes_info.split('\n'):
                if line.strip() and 'master' in line:
                    parts = line.split()
                    if len(parts) >= 8:
                        node_id = parts[0]
                        endpoint = parts[1].split('@')[0]
                        host, port = endpoint.split(':')
                        
                        # Trigger snapshot
                        snapshot_info = await self._create_node_snapshot(host, int(port))
                        snapshot_data['snapshots'][node_id] = snapshot_info
            
            return json.dumps(snapshot_data, default=str).encode('utf-8')
            
        except Exception as e:
            logger.error(f"Snapshot backup creation failed: {e}")
            raise

    async def _backup_node_data(self, host: str, port: int) -> Dict[str, Any]:
        """Backup data from a specific node"""
        try:
            node_client = redis.Redis(
                host=host,
                port=port,
                decode_responses=False,
                socket_timeout=30.0
            )
            
            node_data = {}
            cursor = 0
            
            while True:
                cursor, keys = await node_client.scan(cursor, count=1000)
                
                for key in keys:
                    try:
                        key_type = await node_client.type(key)
                        ttl = await node_client.ttl(key)
                        
                        if key_type == b'string':
                            value = await node_client.get(key)
                        elif key_type == b'hash':
                            value = await node_client.hgetall(key)
                        elif key_type == b'list':
                            value = await node_client.lrange(key, 0, -1)
                        elif key_type == b'set':
                            value = await node_client.smembers(key)
                        elif key_type == b'zset':
                            value = await node_client.zrange(key, 0, -1, withscores=True)
                        else:
                            continue
                        
                        node_data[base64.b64encode(key).decode()] = {
                            'type': key_type.decode(),
                            'value': base64.b64encode(json.dumps(value, default=str).encode()).decode(),
                            'ttl': ttl if ttl > 0 else None
                        }
                        
                    except Exception:
                        continue
                
                if cursor == 0:
                    break
            
            await node_client.close()
            return node_data
            
        except Exception as e:
            logger.error(f"Node backup failed for {host}:{port}: {e}")
            return {}

    async def _get_incremental_changes(self, since_timestamp: float) -> Dict[str, Any]:
        """Get incremental changes since timestamp"""
        # This is simplified - in production would parse AOF files
        return {'changes': [], 'since': since_timestamp}

    async def _create_node_snapshot(self, host: str, port: int) -> Dict[str, Any]:
        """Create snapshot for a specific node"""
        try:
            node_client = redis.Redis(
                host=host,
                port=port,
                decode_responses=True,
                socket_timeout=30.0
            )
            
            # Trigger background save
            await node_client.bgsave()
            
            # Get snapshot info
            info = await node_client.info('persistence')
            
            await node_client.close()
            
            return {
                'rdb_last_save_time': info.get('rdb_last_save_time', 0),
                'rdb_last_bgsave_status': info.get('rdb_last_bgsave_status', 'unknown'),
                'rdb_changes_since_last_save': info.get('rdb_changes_since_last_save', 0)
            }
            
        except Exception as e:
            logger.error(f"Snapshot creation failed for {host}:{port}: {e}")
            return {}

    async def _get_cluster_configuration(self) -> Dict[str, Any]:
        """Get cluster configuration"""
        try:
            nodes_info = await self.cluster_client.cluster_nodes()
            cluster_info = await self.cluster_client.info('cluster')
            
            return {
                'nodes': nodes_info,
                'cluster_info': cluster_info
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster configuration: {e}")
            return {}

    async def _compress_data(self, data: bytes, compression_type: CompressionType) -> bytes:
        """Compress backup data"""
        try:
            if compression_type == CompressionType.GZIP:
                return gzip.compress(data, compresslevel=self.config.get('compression', {}).get('compression_level', 6))
            elif compression_type == CompressionType.LZ4:
                return lz4.frame.compress(data)
            else:
                return data
                
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return data

    async def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt backup data"""
        try:
            if self.encryption_key:
                fernet = Fernet(self.encryption_key)
                return fernet.encrypt(data)
            return data
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data

    async def _store_backup_data(self, backup_task: BackupTask, data: bytes, 
                               backup_schedule: BackupSchedule) -> str:
        """Store backup data to configured storage"""
        try:
            storage_tier = backup_schedule.storage_tier.value
            
            if storage_tier not in self.storage_clients:
                raise ValueError(f"Storage tier {storage_tier} not configured")
            
            # Generate storage key
            date_path = datetime.now().strftime('%Y/%m/%d')
            storage_key = f"backups/{backup_task.backup_type}/{date_path}/{backup_task.task_id}.backup"
            
            # Get storage configuration
            storage_config = self.config.get('storage', {}).get(storage_tier, {})
            bucket_name = storage_config.get('bucket')
            
            if not bucket_name:
                raise ValueError(f"No bucket configured for storage tier {storage_tier}")
            
            # Upload to S3
            extra_args = {}
            
            if storage_config.get('storage_class'):
                extra_args['StorageClass'] = storage_config['storage_class']
            
            if backup_schedule.encryption:
                extra_args['ServerSideEncryption'] = 'AES256'
            
            # Add metadata
            extra_args['Metadata'] = {
                'task-id': backup_task.task_id,
                'backup-type': backup_task.backup_type,
                'compression': backup_schedule.compression.value,
                'checksum': backup_task.checksum or ''
            }
            
            self.storage_clients[storage_tier].put_object(
                Bucket=bucket_name,
                Key=storage_key,
                Body=data,
                **extra_args
            )
            
            return f"s3://{bucket_name}/{storage_key}"
            
        except Exception as e:
            logger.error(f"Backup storage failed: {e}")
            raise

    async def _verify_backup(self, backup_task: BackupTask) -> bool:
        """Verify backup integrity"""
        try:
            if not self.config.get('validation', {}).get('checksum_verification', True):
                return True
            
            # Download and verify checksum
            storage_location = backup_task.storage_location
            
            if storage_location.startswith('s3://'):
                # Parse S3 location
                bucket_key = storage_location[5:]
                bucket, key = bucket_key.split('/', 1)
                
                # Get storage tier
                storage_tier = backup_task.storage_tier.value
                
                if storage_tier not in self.storage_clients:
                    return False
                
                # Download data
                response = self.storage_clients[storage_tier].get_object(Bucket=bucket, Key=key)
                data = response['Body'].read()
                
                # Verify checksum
                calculated_checksum = hashlib.sha256(data).hexdigest()
                return calculated_checksum == backup_task.checksum
            
            return True
            
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return False

    async def _send_notification(self, backup_task: BackupTask, message: str) -> None:
        """Send backup notification"""
        try:
            webhook_url = self.config.get('monitoring', {}).get('webhook_url')
            if not webhook_url:
                return
            
            payload = {
                'task_id': backup_task.task_id,
                'schedule_id': backup_task.schedule_id,
                'backup_type': backup_task.backup_type,
                'status': backup_task.status.value,
                'message': message,
                'timestamp': backup_task.completed_at or time.time(),
                'file_size': backup_task.file_size,
                'compressed_size': backup_task.compressed_size,
                'duration': (backup_task.completed_at - backup_task.started_at) if backup_task.completed_at and backup_task.started_at else 0
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.debug(f"Notification sent for task {backup_task.task_id}")
                    else:
                        logger.warning(f"Notification failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    async def _metrics_collection_loop(self) -> None:
        """Metrics collection loop"""
        while True:
            try:
                await self._update_metrics()
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(300)

    async def _update_metrics(self) -> None:
        """Update backup metrics"""
        try:
            total_backups = len(self.task_history)
            successful_backups = sum(1 for task in self.task_history if task.status == BackupStatus.COMPLETED)
            failed_backups = sum(1 for task in self.task_history if task.status == BackupStatus.FAILED)
            
            total_size = sum(task.file_size for task in self.task_history if task.file_size > 0)
            compressed_size = sum(task.compressed_size for task in self.task_history if task.compressed_size > 0)
            compression_ratio = compressed_size / total_size if total_size > 0 else 0
            
            completed_tasks = [task for task in self.task_history if task.status == BackupStatus.COMPLETED and task.started_at and task.completed_at]
            average_duration = sum(task.completed_at - task.started_at for task in completed_tasks) / len(completed_tasks) if completed_tasks else 0
            
            last_backup_time = max((task.completed_at for task in self.task_history if task.completed_at), default=None)
            
            # Calculate next scheduled backup
            next_scheduled = None
            for schedule in self.backup_schedules.values():
                if schedule.enabled and schedule.next_run:
                    if not next_scheduled or schedule.next_run < next_scheduled:
                        next_scheduled = schedule.next_run
            
            # Storage usage by tier
            storage_usage = {}
            for tier in StorageTier:
                usage = sum(task.compressed_size for task in self.task_history 
                          if task.storage_tier == tier and task.compressed_size > 0)
                storage_usage[tier] = usage
            
            self.metrics = BackupMetrics(
                total_backups=total_backups,
                successful_backups=successful_backups,
                failed_backups=failed_backups,
                total_size_bytes=total_size,
                compression_ratio=compression_ratio,
                average_duration=average_duration,
                last_backup_time=last_backup_time,
                next_scheduled_backup=next_scheduled,
                storage_usage_by_tier=storage_usage
            )
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")

    async def _task_monitoring_loop(self) -> None:
        """Task monitoring loop"""
        while True:
            try:
                # Check for stuck tasks
                current_time = time.time()
                
                for task in list(self.active_tasks.values()):
                    if task.status == BackupStatus.RUNNING:
                        # Check timeout
                        schedule = self.backup_schedules.get(task.schedule_id)
                        if schedule:
                            timeout_seconds = schedule.timeout_minutes * 60
                            if task.started_at and (current_time - task.started_at) > timeout_seconds:
                                task.status = BackupStatus.FAILED
                                task.error_message = "Backup timed out"
                                task.completed_at = current_time
                                
                                # Move to history
                                self.task_history.append(task)
                                del self.active_tasks[task.task_id]
                                
                                logger.warning(f"Backup task {task.task_id} timed out")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Task monitoring error: {e}")
                await asyncio.sleep(60)

    async def _retention_management_loop(self) -> None:
        """Retention management loop"""
        while True:
            try:
                await self._cleanup_old_backups()
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Retention management error: {e}")
                await asyncio.sleep(3600)

    async def _cleanup_old_backups(self) -> None:
        """Cleanup old backups based on retention policies"""
        try:
            current_time = time.time()
            
            # Group tasks by schedule
            tasks_by_schedule = {}
            for task in self.task_history:
                if task.schedule_id not in tasks_by_schedule:
                    tasks_by_schedule[task.schedule_id] = []
                tasks_by_schedule[task.schedule_id].append(task)
            
            # Apply retention policies
            for schedule_id, schedule in self.backup_schedules.items():
                if schedule_id not in tasks_by_schedule:
                    continue
                
                retention_seconds = schedule.retention_days * 86400
                cutoff_time = current_time - retention_seconds
                
                tasks_to_delete = [
                    task for task in tasks_by_schedule[schedule_id]
                    if task.completed_at and task.completed_at < cutoff_time
                ]
                
                for task in tasks_to_delete:
                    await self._delete_backup_task(task)
                    self.task_history.remove(task)
                
                if tasks_to_delete:
                    logger.info(f"Cleaned up {len(tasks_to_delete)} old backups for schedule {schedule_id}")
                    
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")

    async def _delete_backup_task(self, backup_task: BackupTask) -> None:
        """Delete backup task and its storage"""
        try:
            if backup_task.storage_location and backup_task.storage_location.startswith('s3://'):
                # Parse S3 location
                bucket_key = backup_task.storage_location[5:]
                bucket, key = bucket_key.split('/', 1)
                
                # Get storage tier
                storage_tier = backup_task.storage_tier.value if backup_task.storage_tier else 'primary'
                
                if storage_tier in self.storage_clients:
                    self.storage_clients[storage_tier].delete_object(Bucket=bucket, Key=key)
                    
        except Exception as e:
            logger.error(f"Failed to delete backup {backup_task.task_id}: {e}")

    async def _storage_tier_management_loop(self) -> None:
        """Storage tier management loop"""
        while True:
            try:
                await self._manage_storage_tiers()
                await asyncio.sleep(86400)  # Run daily
                
            except Exception as e:
                logger.error(f"Storage tier management error: {e}")
                await asyncio.sleep(86400)

    async def _manage_storage_tiers(self) -> None:
        """Manage storage tier transitions"""
        try:
            current_time = time.time()
            retention_config = self.config.get('retention', {})
            
            # Define tier transition rules
            hot_to_warm_days = retention_config.get('hot_tier_days', 7)
            warm_to_cold_days = retention_config.get('warm_tier_days', 30)
            cold_to_archive_days = retention_config.get('cold_tier_days', 90)
            
            for task in self.task_history:
                if not task.completed_at or not task.storage_location:
                    continue
                
                age_days = (current_time - task.completed_at) / 86400
                
                # Determine target tier
                target_tier = None
                
                if age_days > cold_to_archive_days and task.storage_tier != StorageTier.ARCHIVE:
                    target_tier = StorageTier.ARCHIVE
                elif age_days > warm_to_cold_days and task.storage_tier not in [StorageTier.COLD, StorageTier.ARCHIVE]:
                    target_tier = StorageTier.COLD
                elif age_days > hot_to_warm_days and task.storage_tier not in [StorageTier.WARM, StorageTier.COLD, StorageTier.ARCHIVE]:
                    target_tier = StorageTier.WARM
                
                if target_tier:
                    await self._transition_storage_tier(task, target_tier)
                    
        except Exception as e:
            logger.error(f"Storage tier management failed: {e}")

    async def _transition_storage_tier(self, backup_task: BackupTask, target_tier: StorageTier) -> None:
        """Transition backup to different storage tier"""
        try:
            # This is simplified - in production would implement actual tier transitions
            logger.info(f"Transitioning backup {backup_task.task_id} to {target_tier.value} tier")
            backup_task.storage_tier = target_tier
            
        except Exception as e:
            logger.error(f"Storage tier transition failed for {backup_task.task_id}: {e}")

    async def manual_backup(self, schedule_id: str) -> Dict[str, Any]:
        """Trigger manual backup"""
        try:
            task = await self._execute_backup(schedule_id)
            
            if task:
                return {
                    'success': task.status == BackupStatus.COMPLETED,
                    'task_id': task.task_id,
                    'status': task.status.value,
                    'file_size': task.file_size,
                    'compressed_size': task.compressed_size,
                    'error': task.error_message
                }
            else:
                return {'success': False, 'error': 'Failed to create backup task'}
                
        except Exception as e:
            logger.error(f"Manual backup failed: {e}")
            return {'success': False, 'error': str(e)}

    async def get_backup_status(self) -> Dict[str, Any]:
        """Get comprehensive backup status"""
        return {
            'schedules': {
                schedule_id: asdict(schedule) 
                for schedule_id, schedule in self.backup_schedules.items()
            },
            'active_tasks': {
                task_id: asdict(task) 
                for task_id, task in self.active_tasks.items()
            },
            'recent_history': [
                asdict(task) for task in self.task_history[-20:]
            ],
            'metrics': asdict(self.metrics) if self.metrics else None,
            'configuration': {
                'encryption_enabled': self.encryption_key is not None,
                'storage_tiers': list(self.storage_clients.keys()),
                'max_concurrent': self.config.get('parallelism', {}).get('max_concurrent_backups', 3)
            }
        }

    async def shutdown(self) -> None:
        """Shutdown backup automation system"""
        try:
            # Stop scheduler
            self.scheduler_running = False
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.monitoring_tasks:
                await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            logger.info("Backup automation system shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Example usage
async def main():
    """Example usage of Backup Automation System"""
    try:
        # This would normally be initialized with actual cluster client
        print("Backup Automation System Demo")
        print("Note: This would require actual Redis cluster connection")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())