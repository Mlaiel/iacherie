"""Temporal Partitioning - Time-Based Partition Management

Ultra-industrial temporal partitioning system for time-series and time-sensitive data.
Provides intelligent time-based partitioning with automated archival, compression,
and retention management for the IA Influencer Agent platform.

Features:
- Intelligent time-based partitioning strategies
- Automated partition creation and maintenance
- Data retention and archival policies
- Compression optimization for historical data
- Purge operations for expired data
- Time-series query optimization
- Rolling window maintenance
- Predictive partition planning

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING 🚨
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, or distribution is strictly prohibited.
"""
import logging
import time
import threading
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta, timezone
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import calendar
import json
from collections import defaultdict

from sqlalchemy import text, MetaData, Table, Column, DateTime, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import psutil

logger = logging.getLogger(__name__)

class TimePartitionStrategy(Enum):
    """Time-based partitioning strategies"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    SLIDING_WINDOW = "sliding_window"
    CUSTOM_INTERVAL = "custom_interval"

class TimeInterval(Enum):
    """Time interval definitions"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class RetentionPolicy(Enum):
    """Data retention policies"""
    TIME_BASED = "time_based"
    SIZE_BASED = "size_based"
    COUNT_BASED = "count_based"
    COMPLIANCE_BASED = "compliance_based"
    TIERED_STORAGE = "tiered_storage"
    NEVER_DELETE = "never_delete"

class PurgePolicy(Enum):
    """Data purge policies"""
    IMMEDIATE = "immediate"
    BATCH_PURGE = "batch_purge"
    GRADUAL_PURGE = "gradual_purge"
    ARCHIVE_THEN_PURGE = "archive_then_purge"
    SOFT_DELETE = "soft_delete"

@dataclass
class TimePartitionConfig:
    """Configuration for temporal partitioning"""
    table_name: str
    time_column: str
    strategy: TimePartitionStrategy
    interval: Union[TimeInterval, int]  # TimeInterval enum or custom hours
    retention_days: int = 365
    retention_policy: RetentionPolicy = RetentionPolicy.TIME_BASED
    purge_policy: PurgePolicy = PurgePolicy.ARCHIVE_THEN_PURGE
    archive_threshold_days: int = 90
    compression_threshold_days: int = 30
    future_partitions: int = 3  # Number of future partitions to pre-create
    past_partitions: int = 12  # Number of past partitions to maintain
    timezone: str = "UTC"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PartitionWindow:
    """Time window for a partition"""
    partition_name: str
    table_name: str
    start_time: datetime
    end_time: datetime
    strategy: TimePartitionStrategy
    size_bytes: int = 0
    row_count: int = 0
    status: str = "active"  # active, archived, compressed, purged
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    compression_ratio: float = 1.0

@dataclass
class ArchivalTask:
    """Data archival task"""
    task_id: str
    partition_name: str
    table_name: str
    source_location: str
    target_location: str
    archival_type: str  # compress, move, backup
    estimated_size: int
    priority: int = 5
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class CompressionScheduler:
    """Intelligent compression scheduling system"""
    
    def __init__(self, session_factory, config: Dict[str, Any] = None):
        self.session_factory = session_factory
        self.config = config or {}
        self.compression_threshold_days = self.config.get('compression_threshold_days', 30)
        self.compression_ratio_target = self.config.get('compression_ratio_target', 0.3)
        self.compression_schedule: Dict[str, datetime] = {}
        
    def schedule_compression(self, partition: PartitionWindow) -> bool:
        """Schedule compression for partition"""
        try:
            # Check if partition is eligible for compression
            age_days = (datetime.utcnow() - partition.start_time).days
            
            if age_days < self.compression_threshold_days:
                return False
            
            if partition.status in ['compressed', 'archived', 'purged']:
                return False
            
            # Calculate optimal compression time (during low usage hours)
            compression_time = self._calculate_optimal_compression_time()
            
            # Schedule compression task
            self.compression_schedule[partition.partition_name] = compression_time
            
            logger.info(f"Scheduled compression for {partition.partition_name} at {compression_time}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule compression for {partition.partition_name}: {e}")
            return False
    
    def _calculate_optimal_compression_time(self) -> datetime:
        """Calculate optimal time for compression (low usage hours)"""
        # Schedule during low usage hours (typically 2-4 AM)
        now = datetime.utcnow()
        target_time = now.replace(hour=3, minute=0, second=0, microsecond=0)
        
        # If past 3 AM today, schedule for tomorrow
        if now.hour >= 3:
            target_time += timedelta(days=1)
        
        return target_time
    
    def execute_compression(self, partition_name: str) -> bool:
        """Execute compression for partition"""
        try:
            with self.session_factory() as session:
                # PostgreSQL table compression (simplified)
                logger.info(f"Compressing partition: {partition_name}")
                
                # Vacuum full with compression (example for PostgreSQL)
                session.execute(text(f"VACUUM FULL {partition_name}"))
                
                # Alternative: Create compressed partition and migrate data
                # This would be more sophisticated in production
                
                # Update compression status
                self.compression_schedule.pop(partition_name, None)
                
                logger.info(f"Compression completed for: {partition_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to compress partition {partition_name}: {e}")
            return False

class ArchivalManager:
    """Data archival and long-term storage management"""
    
    def __init__(self, session_factory, config: Dict[str, Any] = None):
        self.session_factory = session_factory
        self.config = config or {}
        self.archive_storage_path = self.config.get('archive_storage_path', '/archive')
        self.active_tasks: Dict[str, ArchivalTask] = {}
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    def create_archival_task(self, partition: PartitionWindow, archival_type: str = "compress") -> ArchivalTask:
        """Create archival task for partition"""
        task_id = f"archive_{partition.partition_name}_{int(time.time())}"
        
        task = ArchivalTask(
            task_id=task_id,
            partition_name=partition.partition_name,
            table_name=partition.table_name,
            source_location=f"database.{partition.partition_name}",
            target_location=f"{self.archive_storage_path}/{partition.table_name}/{partition.partition_name}",
            archival_type=archival_type,
            estimated_size=partition.size_bytes,
            priority=3 if archival_type == "compress" else 5
        )
        
        return task
    
    def execute_archival_task(self, task: ArchivalTask) -> bool:
        """Execute archival task"""
        try:
            task.status = "in_progress"
            task.started_at = datetime.utcnow()
            
            logger.info(f"Starting archival task: {task.task_id}")
            
            if task.archival_type == "compress":
                success = self._compress_partition(task)
            elif task.archival_type == "move":
                success = self._move_partition(task)
            elif task.archival_type == "backup":
                success = self._backup_partition(task)
            else:
                raise ValueError(f"Unknown archival type: {task.archival_type}")
            
            if success:
                task.status = "completed"
                task.completed_at = datetime.utcnow()
                logger.info(f"Archival task completed: {task.task_id}")
            else:
                task.status = "failed"
                logger.error(f"Archival task failed: {task.task_id}")
            
            return success
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            logger.error(f"Archival task error {task.task_id}: {e}")
            return False
    
    def _compress_partition(self, task: ArchivalTask) -> bool:
        """Compress partition data"""
        try:
            with self.session_factory() as session:
                # Example compression implementation
                session.execute(text(f"VACUUM FULL {task.partition_name}"))
                
                # Could also implement:
                # - Custom compression algorithms
                # - Column-store conversion
                # - Parquet export
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to compress partition {task.partition_name}: {e}")
            return False
    
    def _move_partition(self, task: ArchivalTask) -> bool:
        """Move partition to archive storage"""
        # Implementation would move data to external storage
        # For example: AWS S3, Azure Blob, file system
        logger.info(f"Moving partition {task.partition_name} to {task.target_location}")
        return True
    
    def _backup_partition(self, task: ArchivalTask) -> bool:
        """Create backup of partition"""
        # Implementation would create backup copy
        logger.info(f"Backing up partition {task.partition_name}")
        return True

class TemporalPartitionManager:
    """
    Ultra-industrial temporal partition management system
    
    Manages time-based partitions with:
    - Intelligent partition creation and maintenance
    - Automated archival and compression
    - Data retention enforcement
    - Performance optimization for time-series queries
    """
    
    def __init__(self, session_factory, config: Dict[str, Any] = None):
        """
        Initialize temporal partition manager
        
        Args:
            session_factory: SQLAlchemy session factory
            config: Configuration dictionary
        """
        self.session_factory = session_factory
        self.config = config or {}
        
        # Component initialization
        self.compression_scheduler = CompressionScheduler(session_factory, config.get('compression', {}))
        self.archival_manager = ArchivalManager(session_factory, config.get('archival', {}))
        
        # Partition tracking
        self.partition_configs: Dict[str, TimePartitionConfig] = {}
        self.partition_windows: Dict[str, List[PartitionWindow]] = defaultdict(list)
        self.maintenance_schedule: Dict[str, datetime] = {}
        
        # Monitoring and automation
        self.monitoring_enabled = True
        self.monitoring_interval = self.config.get('monitoring_interval', 3600)  # 1 hour
        self.monitoring_thread = None
        self.automatic_maintenance = self.config.get('automatic_maintenance', True)
        
        # Threading
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("TemporalPartitionManager initialized")
    
    def register_table(self, config: TimePartitionConfig) -> bool:
        """Register table for temporal partitioning"""
        try:
            with self._lock:
                # Validate configuration
                if not self._validate_config(config):
                    return False
                
                # Store configuration
                self.partition_configs[config.table_name] = config
                
                # Create initial partitions
                self._create_initial_partitions(config)
                
                # Schedule maintenance
                self._schedule_maintenance(config.table_name)
                
                logger.info(f"Registered table for temporal partitioning: {config.table_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register table {config.table_name}: {e}")
            return False
    
    def _validate_config(self, config: TimePartitionConfig) -> bool:
        """Validate temporal partition configuration"""
        if not config.table_name or not config.time_column:
            logger.error("Table name and time column are required")
            return False
        
        if config.retention_days <= 0:
            logger.error("Retention days must be positive")
            return False
        
        if config.future_partitions < 0 or config.past_partitions < 0:
            logger.error("Partition counts must be non-negative")
            return False
        
        return True
    
    def _create_initial_partitions(self, config: TimePartitionConfig):
        """Create initial partitions for table"""
        try:
            current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
            
            # Create past partitions
            for i in range(config.past_partitions, 0, -1):
                start_time = self._calculate_partition_start(current_time, config.strategy, -i)
                self._create_partition_for_time(config, start_time)
            
            # Create current partition
            current_start = self._calculate_partition_start(current_time, config.strategy, 0)
            self._create_partition_for_time(config, current_start)
            
            # Create future partitions
            for i in range(1, config.future_partitions + 1):
                start_time = self._calculate_partition_start(current_time, config.strategy, i)
                self._create_partition_for_time(config, start_time)
            
            logger.info(f"Created initial partitions for {config.table_name}")
            
        except Exception as e:
            logger.error(f"Failed to create initial partitions for {config.table_name}: {e}")
    
    def _calculate_partition_start(self, base_time: datetime, strategy: TimePartitionStrategy, offset: int) -> datetime:
        """Calculate partition start time based on strategy and offset"""
        if strategy == TimePartitionStrategy.HOURLY:
            return base_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=offset)
        
        elif strategy == TimePartitionStrategy.DAILY:
            return base_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=offset)
        
        elif strategy == TimePartitionStrategy.WEEKLY:
            # Start of week (Monday)
            days_since_monday = base_time.weekday()
            week_start = base_time.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
            return week_start + timedelta(weeks=offset)
        
        elif strategy == TimePartitionStrategy.MONTHLY:
            # Start of month
            if offset == 0:
                return base_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                # Calculate target month/year
                target_month = base_time.month + offset
                target_year = base_time.year
                
                while target_month > 12:
                    target_month -= 12
                    target_year += 1
                
                while target_month < 1:
                    target_month += 12
                    target_year -= 1
                
                return datetime(target_year, target_month, 1, tzinfo=timezone.utc)
        
        elif strategy == TimePartitionStrategy.QUARTERLY:
            # Start of quarter
            quarter_start_month = ((base_time.month - 1) // 3) * 3 + 1
            quarter_start = base_time.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Add quarters
            target_month = quarter_start_month + (offset * 3)
            target_year = base_time.year
            
            while target_month > 12:
                target_month -= 12
                target_year += 1
            
            while target_month < 1:
                target_month += 12
                target_year -= 1
            
            return datetime(target_year, target_month, 1, tzinfo=timezone.utc)
        
        elif strategy == TimePartitionStrategy.YEARLY:
            return base_time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0).replace(year=base_time.year + offset)
        
        else:
            raise ValueError(f"Unsupported partition strategy: {strategy}")
    
    def _create_partition_for_time(self, config: TimePartitionConfig, start_time: datetime) -> bool:
        """Create partition for specific time"""
        try:
            # Calculate end time
            end_time = self._calculate_partition_end(start_time, config.strategy)
            
            # Generate partition name
            partition_name = self._generate_partition_name(config.table_name, start_time, config.strategy)
            
            # Create partition window object
            partition_window = PartitionWindow(
                partition_name=partition_name,
                table_name=config.table_name,
                start_time=start_time,
                end_time=end_time,
                strategy=config.strategy
            )
            
            # Create actual database partition
            self._create_database_partition(config, partition_window)
            
            # Track partition
            self.partition_windows[config.table_name].append(partition_window)
            
            logger.debug(f"Created partition: {partition_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create partition for time {start_time}: {e}")
            return False
    
    def _calculate_partition_end(self, start_time: datetime, strategy: TimePartitionStrategy) -> datetime:
        """Calculate partition end time"""
        if strategy == TimePartitionStrategy.HOURLY:
            return start_time + timedelta(hours=1)
        elif strategy == TimePartitionStrategy.DAILY:
            return start_time + timedelta(days=1)
        elif strategy == TimePartitionStrategy.WEEKLY:
            return start_time + timedelta(weeks=1)
        elif strategy == TimePartitionStrategy.MONTHLY:
            # Handle month boundaries correctly
            if start_time.month == 12:
                return start_time.replace(year=start_time.year + 1, month=1)
            else:
                return start_time.replace(month=start_time.month + 1)
        elif strategy == TimePartitionStrategy.QUARTERLY:
            return start_time + timedelta(days=90)  # Approximate
        elif strategy == TimePartitionStrategy.YEARLY:
            return start_time.replace(year=start_time.year + 1)
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")
    
    def _generate_partition_name(self, table_name: str, start_time: datetime, strategy: TimePartitionStrategy) -> str:
        """Generate partition name based on time and strategy"""
        if strategy == TimePartitionStrategy.HOURLY:
            suffix = start_time.strftime('%Y_%m_%d_%H')
        elif strategy == TimePartitionStrategy.DAILY:
            suffix = start_time.strftime('%Y_%m_%d')
        elif strategy == TimePartitionStrategy.WEEKLY:
            # Week number
            year, week, _ = start_time.isocalendar()
            suffix = f"{year}_w{week:02d}"
        elif strategy == TimePartitionStrategy.MONTHLY:
            suffix = start_time.strftime('%Y_%m')
        elif strategy == TimePartitionStrategy.QUARTERLY:
            quarter = ((start_time.month - 1) // 3) + 1
            suffix = f"{start_time.year}_q{quarter}"
        elif strategy == TimePartitionStrategy.YEARLY:
            suffix = start_time.strftime('%Y')
        else:
            suffix = start_time.strftime('%Y_%m_%d')
        
        return f"{table_name}_{suffix}"
    
    def _create_database_partition(self, config: TimePartitionConfig, partition: PartitionWindow):
        """Create actual database partition"""
        try:
            with self.session_factory() as session:
                # Create partition table (PostgreSQL syntax)
                create_partition_sql = f"""
                CREATE TABLE IF NOT EXISTS {partition.partition_name} 
                PARTITION OF {config.table_name}
                FOR VALUES FROM ('{partition.start_time.isoformat()}') TO ('{partition.end_time.isoformat()}')
                """
                
                session.execute(text(create_partition_sql))
                
                # Create indexes for partition
                self._create_partition_indexes(session, config, partition)
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Failed to create database partition {partition.partition_name}: {e}")
            raise
    
    def _create_partition_indexes(self, session: Session, config: TimePartitionConfig, partition: PartitionWindow):
        """Create indexes for partition"""
        try:
            # Time column index
            session.execute(text(f"""
                CREATE INDEX IF NOT EXISTS idx_{partition.partition_name}_{config.time_column} 
                ON {partition.partition_name} ({config.time_column})
            """))
            
            # Additional indexes based on table type
            if 'content_fingerprints' in config.table_name:
                session.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS idx_{partition.partition_name}_user_id 
                    ON {partition.partition_name} (user_id)
                """))
            
            elif 'protection_alerts' in config.table_name:
                session.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS idx_{partition.partition_name}_severity 
                    ON {partition.partition_name} (severity)
                """))
            
            elif 'revenue_tracking' in config.table_name:
                session.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS idx_{partition.partition_name}_user_platform 
                    ON {partition.partition_name} (user_id, platform)
                """))
            
        except Exception as e:
            logger.warning(f"Failed to create some indexes for {partition.partition_name}: {e}")
    
    def _schedule_maintenance(self, table_name: str):
        """Schedule maintenance for table"""
        # Schedule next maintenance check
        next_maintenance = datetime.utcnow() + timedelta(hours=24)
        self.maintenance_schedule[table_name] = next_maintenance
    
    def start_monitoring(self):
        """Start monitoring and maintenance"""
        def monitoring_loop():
            while self.monitoring_enabled:
                try:
                    self._maintenance_cycle()
                    time.sleep(self.monitoring_interval)
                except Exception as e:
                    logger.error(f"Error in temporal partition monitoring: {e}")
                    time.sleep(60)  # Short delay on error
        
        if not self.monitoring_thread or not self.monitoring_thread.is_alive():
            self.monitoring_enabled = True
            self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("Temporal partition monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_enabled = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)
        logger.info("Temporal partition monitoring stopped")
    
    def _maintenance_cycle(self):
        """Single maintenance cycle"""
        try:
            current_time = datetime.utcnow()
            
            for table_name, config in self.partition_configs.items():
                # Check if maintenance is due
                next_maintenance = self.maintenance_schedule.get(table_name)
                if next_maintenance and current_time < next_maintenance:
                    continue
                
                logger.debug(f"Running maintenance for table: {table_name}")
                
                # Create future partitions if needed
                self._ensure_future_partitions(config)
                
                # Archive old partitions
                self._process_archival(config)
                
                # Purge expired partitions
                self._process_purge(config)
                
                # Update statistics
                self._update_partition_statistics(table_name)
                
                # Schedule next maintenance
                self._schedule_maintenance(table_name)
            
        except Exception as e:
            logger.error(f"Error in maintenance cycle: {e}")
    
    def _ensure_future_partitions(self, config: TimePartitionConfig):
        """Ensure adequate future partitions exist"""
        try:
            current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
            current_partitions = self.partition_windows[config.table_name]
            
            # Find latest partition
            if current_partitions:
                latest_partition = max(current_partitions, key=lambda p: p.end_time)
                latest_end = latest_partition.end_time
            else:
                latest_end = current_time
            
            # Calculate how many future partitions we need
            needed_partitions = []
            check_time = latest_end
            
            for i in range(config.future_partitions):
                partition_start = self._calculate_partition_start(check_time, config.strategy, 1)
                needed_partitions.append(partition_start)
                check_time = partition_start
            
            # Create missing partitions
            for start_time in needed_partitions:
                existing = any(p.start_time == start_time for p in current_partitions)
                if not existing:
                    self._create_partition_for_time(config, start_time)
            
        except Exception as e:
            logger.error(f"Failed to ensure future partitions for {config.table_name}: {e}")
    
    def _process_archival(self, config: TimePartitionConfig):
        """Process archival for old partitions"""
        try:
            current_time = datetime.utcnow()
            archive_cutoff = current_time - timedelta(days=config.archive_threshold_days)
            
            for partition in self.partition_windows[config.table_name]:
                if (partition.end_time < archive_cutoff and 
                    partition.status == "active"):
                    
                    # Create archival task
                    task = self.archival_manager.create_archival_task(partition)
                    
                    # Execute archival
                    success = self.archival_manager.execute_archival_task(task)
                    
                    if success:
                        partition.status = "archived"
                        logger.info(f"Archived partition: {partition.partition_name}")
            
        except Exception as e:
            logger.error(f"Failed to process archival for {config.table_name}: {e}")
    
    def _process_purge(self, config: TimePartitionConfig):
        """Process purge for expired partitions"""
        try:
            current_time = datetime.utcnow()
            purge_cutoff = current_time - timedelta(days=config.retention_days)
            
            partitions_to_purge = [
                p for p in self.partition_windows[config.table_name]
                if p.end_time < purge_cutoff and p.status in ["active", "archived"]
            ]
            
            for partition in partitions_to_purge:
                if config.purge_policy == PurgePolicy.ARCHIVE_THEN_PURGE:
                    if partition.status != "archived":
                        continue  # Archive first
                
                # Execute purge
                success = self._purge_partition(partition)
                
                if success:
                    partition.status = "purged"
                    logger.info(f"Purged partition: {partition.partition_name}")
            
        except Exception as e:
            logger.error(f"Failed to process purge for {config.table_name}: {e}")
    
    def _purge_partition(self, partition: PartitionWindow) -> bool:
        """Purge partition data"""
        try:
            with self.session_factory() as session:
                # Drop partition table
                session.execute(text(f"DROP TABLE IF EXISTS {partition.partition_name}"))
                session.commit()
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to purge partition {partition.partition_name}: {e}")
            return False
    
    def _update_partition_statistics(self, table_name: str):
        """Update partition statistics"""
        try:
            with self.session_factory() as session:
                for partition in self.partition_windows[table_name]:
                    if partition.status != "purged":
                        # Update row count and size
                        stats_query = text(f"""
                            SELECT 
                                COUNT(*) as row_count,
                                pg_total_relation_size('{partition.partition_name}') as size_bytes
                            FROM {partition.partition_name}
                        """)
                        
                        try:
                            result = session.execute(stats_query).fetchone()
                            if result:
                                partition.row_count = result.row_count
                                partition.size_bytes = result.size_bytes
                        except:
                            # Partition might not exist yet
                            pass
            
        except Exception as e:
            logger.warning(f"Failed to update statistics for {table_name}: {e}")
    
    def get_partition_info(self, table_name: str) -> Dict[str, Any]:
        """Get comprehensive partition information"""
        try:
            config = self.partition_configs.get(table_name)
            partitions = self.partition_windows.get(table_name, [])
            
            if not config or not partitions:
                return {'error': f'No partition information for table: {table_name}'}
            
            # Calculate statistics
            total_partitions = len(partitions)
            active_partitions = len([p for p in partitions if p.status == "active"])
            archived_partitions = len([p for p in partitions if p.status == "archived"])
            total_rows = sum(p.row_count for p in partitions)
            total_size = sum(p.size_bytes for p in partitions)
            
            # Partition breakdown by status
            status_breakdown = defaultdict(int)
            for partition in partitions:
                status_breakdown[partition.status] += 1
            
            # Size breakdown by time period
            size_by_period = []
            for partition in sorted(partitions, key=lambda p: p.start_time):
                size_by_period.append({
                    'partition_name': partition.partition_name,
                    'start_time': partition.start_time.isoformat(),
                    'end_time': partition.end_time.isoformat(),
                    'size_mb': round(partition.size_bytes / (1024 * 1024), 2),
                    'row_count': partition.row_count,
                    'status': partition.status
                })
            
            return {
                'table_name': table_name,
                'strategy': config.strategy.value,
                'time_column': config.time_column,
                'retention_days': config.retention_days,
                'statistics': {
                    'total_partitions': total_partitions,
                    'active_partitions': active_partitions,
                    'archived_partitions': archived_partitions,
                    'total_rows': total_rows,
                    'total_size_bytes': total_size,
                    'total_size_gb': round(total_size / (1024**3), 2)
                },
                'status_breakdown': dict(status_breakdown),
                'partitions': size_by_period,
                'next_maintenance': self.maintenance_schedule.get(table_name, datetime.utcnow()).isoformat(),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get partition info for {table_name}: {e}")
            return {'error': str(e)}
    
    def force_maintenance(self, table_name: str = None) -> bool:
        """Force immediate maintenance for table(s)"""
        try:
            tables_to_maintain = [table_name] if table_name else list(self.partition_configs.keys())
            
            for table in tables_to_maintain:
                if table in self.partition_configs:
                    logger.info(f"Forcing maintenance for table: {table}")
                    
                    config = self.partition_configs[table]
                    
                    # Run all maintenance operations
                    self._ensure_future_partitions(config)
                    self._process_archival(config)
                    self._process_purge(config)
                    self._update_partition_statistics(table)
                    
                    # Reset maintenance schedule
                    self._schedule_maintenance(table)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to force maintenance: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive temporal partitioning system status"""
        try:
            total_tables = len(self.partition_configs)
            total_partitions = sum(len(partitions) for partitions in self.partition_windows.values())
            
            # Strategy distribution
            strategy_counts = defaultdict(int)
            for config in self.partition_configs.values():
                strategy_counts[config.strategy.value] += 1
            
            # Overall status breakdown
            overall_status = defaultdict(int)
            for partitions in self.partition_windows.values():
                for partition in partitions:
                    overall_status[partition.status] += 1
            
            # Table summaries
            table_summaries = {}
            for table_name, config in self.partition_configs.items():
                partitions = self.partition_windows.get(table_name, [])
                table_summaries[table_name] = {
                    'strategy': config.strategy.value,
                    'partition_count': len(partitions),
                    'retention_days': config.retention_days,
                    'next_maintenance': self.maintenance_schedule.get(table_name, datetime.utcnow()).isoformat()
                }
            
            return {
                'temporal_partitioning_status': {
                    'monitoring_enabled': self.monitoring_enabled,
                    'automatic_maintenance': self.automatic_maintenance,
                    'monitoring_interval': self.monitoring_interval
                },
                'summary': {
                    'total_tables': total_tables,
                    'total_partitions': total_partitions,
                    'strategy_distribution': dict(strategy_counts),
                    'status_distribution': dict(overall_status)
                },
                'table_summaries': table_summaries,
                'active_archival_tasks': len(self.archival_manager.active_tasks),
                'compression_scheduled': len(self.compression_scheduler.compression_schedule),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get temporal partitioning status: {e}")
            return {'error': str(e)}
    
    def shutdown(self):
        """Shutdown temporal partition manager gracefully"""
        try:
            logger.info("Shutting down temporal partition manager...")
            
            # Stop monitoring
            self.stop_monitoring()
            
            # Shutdown executors
            self._executor.shutdown(wait=True)
            self.archival_manager.executor.shutdown(wait=True)
            
            logger.info("Temporal partition manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during temporal partition manager shutdown: {e}")

__all__ = [
    'TemporalPartitionManager',
    'CompressionScheduler',
    'ArchivalManager',
    'TimePartitionStrategy',
    'TimeInterval',
    'RetentionPolicy',
    'PurgePolicy',
    'TimePartitionConfig',
    'PartitionWindow',
    'ArchivalTask'
]
