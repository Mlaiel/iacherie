"""MongoDB Backup Scheduler
========================

Automated backup scheduling with intelligent timing and resource management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import os
import subprocess
import threading
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pymongo import MongoClient
import schedule
import json

logger = logging.getLogger(__name__)

class BackupType(Enum):
    """Backup type enumeration."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    OPLOG = "oplog"

class BackupStatus(Enum):
    """Backup status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class BackupJob:
    """Backup job configuration."""
    job_id: str
    name: str
    backup_type: BackupType
    schedule_expression: str  # Cron-like expression
    databases: List[str]  # Empty list means all databases
    collections: List[str]  # Empty list means all collections
    output_directory: str
    compression_enabled: bool = True
    encryption_enabled: bool = False
    retention_days: int = 30
    enabled: bool = True
    
@dataclass
class BackupExecution:
    """Backup execution record."""
    execution_id: str
    job_id: str
    backup_type: BackupType
    start_time: datetime
    end_time: Optional[datetime] = None
    status: BackupStatus = BackupStatus.PENDING
    file_path: Optional[str] = None
    file_size_bytes: int = 0
    error_message: Optional[str] = None
    databases_backed_up: List[str] = None
    collections_backed_up: List[str] = None
    duration_seconds: float = 0.0

class BackupScheduler:
    """Advanced backup scheduler with intelligent timing and resource management."""
    
    def __init__(self, client -> None: MongoClient, config -> None: Dict[str, Any] = None) -> None:
        """Initialize backup scheduler.
        
        Args:
            client: MongoDB client instance
            config: Scheduler configuration
        """
        self.client = client
        self.config = config or {}
        
        # Backup jobs and executions
        self._backup_jobs: Dict[str, BackupJob] = {}
        self._execution_history: List[BackupExecution] = []
        self._active_executions: Dict[str, BackupExecution] = {}
        
        # Scheduler state
        self._scheduler_thread = None
        self._scheduler_running = False
        self._scheduler_lock = threading.RLock()
        
        # Configuration
        self._max_concurrent_backups = self.config.get('max_concurrent_backups', 2)
        self._backup_window_start = self.config.get('backup_window_start', '02:00')
        self._backup_window_end = self.config.get('backup_window_end', '06:00')
        self._resource_monitoring_enabled = self.config.get('resource_monitoring', True)
        self._cpu_threshold = self.config.get('cpu_threshold', 80)
        self._memory_threshold = self.config.get('memory_threshold', 85)
        
        # Callbacks
        self._completion_callbacks: List[Callable] = []
        self._failure_callbacks: List[Callable] = []
        
        # Tools paths
        self._mongodump_path = self.config.get('mongodump_path', 'mongodump')
        self._mongorestore_path = self.config.get('mongorestore_path', 'mongorestore')
        
        # Default output directory
        self._default_output_dir = self.config.get('output_directory', '/tmp/mongodb_backups')
        os.makedirs(self._default_output_dir, exist_ok=True)
    
    def add_backup_job(self, job: BackupJob) -> bool:
        """Add backup job to scheduler.
        
        Args:
            job: Backup job configuration
            
        Returns:
            True if job added successfully
        """
        with self._scheduler_lock:
            if job.job_id in self._backup_jobs:
                logger.warning(f"Backup job '{job.job_id}' already exists")
                return False
            
            # Validate job configuration
            if not self._validate_backup_job(job):
                return False
            
            self._backup_jobs[job.job_id] = job
            
            # Schedule the job
            if job.enabled:
                self._schedule_job(job)
            
            logger.info(f"Added backup job '{job.name}' ({job.job_id})")
            return True
    
    def remove_backup_job(self, job_id: str) -> bool:
        """Remove backup job from scheduler.
        
        Args:
            job_id: Job ID to remove
            
        Returns:
            True if job removed successfully
        """
        with self._scheduler_lock:
            if job_id not in self._backup_jobs:
                logger.warning(f"Backup job '{job_id}' not found")
                return False
            
            job = self._backup_jobs[job_id]
            
            # Remove from schedule
            schedule.clear(job_id)
            
            # Remove from jobs
            del self._backup_jobs[job_id]
            
            logger.info(f"Removed backup job '{job.name}' ({job_id})")
            return True
    
    def enable_backup_job(self, job_id: str) -> bool:
        """Enable backup job.
        
        Args:
            job_id: Job ID to enable
            
        Returns:
            True if job enabled successfully
        """
        with self._scheduler_lock:
            if job_id not in self._backup_jobs:
                return False
            
            job = self._backup_jobs[job_id]
            job.enabled = True
            self._schedule_job(job)
            
            logger.info(f"Enabled backup job '{job.name}'")
            return True
    
    def disable_backup_job(self, job_id: str) -> bool:
        """Disable backup job.
        
        Args:
            job_id: Job ID to disable
            
        Returns:
            True if job disabled successfully
        """
        with self._scheduler_lock:
            if job_id not in self._backup_jobs:
                return False
            
            job = self._backup_jobs[job_id]
            job.enabled = False
            schedule.clear(job_id)
            
            logger.info(f"Disabled backup job '{job.name}'")
            return True
    
    def execute_backup_now(self, job_id: str) -> str:
        """Execute backup job immediately.
        
        Args:
            job_id: Job ID to execute
            
        Returns:
            Execution ID
        """
        if job_id not in self._backup_jobs:
            raise ValueError(f"Backup job '{job_id}' not found")
        
        job = self._backup_jobs[job_id]
        execution_id = self._generate_execution_id()
        
        # Create execution record
        execution = BackupExecution(
            execution_id=execution_id,
            job_id=job_id,
            backup_type=job.backup_type,
            start_time=datetime.utcnow(),
            status=BackupStatus.PENDING
        )
        
        # Execute in background thread
        execution_thread = threading.Thread(
            target=self._execute_backup_job,
            args=(job, execution),
            daemon=True
        )
        execution_thread.start()
        
        logger.info(f"Started manual backup execution '{execution_id}' for job '{job.name}'")
        return execution_id
    
    def get_backup_jobs(self) -> List[BackupJob]:
        """Get list of all backup jobs.
        
        Returns:
            List of backup jobs
        """
        with self._scheduler_lock:
            return list(self._backup_jobs.values())
    
    def get_execution_history(self, job_id: str = None, limit: int = 100) -> List[BackupExecution]:
        """Get backup execution history.
        
        Args:
            job_id: Optional job ID to filter by
            limit: Maximum number of executions to return
            
        Returns:
            List of backup executions
        """
        executions = self._execution_history
        
        if job_id:
            executions = [e for e in executions if e.job_id == job_id]
        
        # Sort by start time descending
        executions.sort(key=lambda x: x.start_time, reverse=True)
        
        return executions[:limit]
    
    def get_active_executions(self) -> List[BackupExecution]:
        """Get currently active backup executions.
        
        Returns:
            List of active executions
        """
        return list(self._active_executions.values())
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel active backup execution.
        
        Args:
            execution_id: Execution ID to cancel
            
        Returns:
            True if execution cancelled successfully
        """
        if execution_id not in self._active_executions:
            return False
        
        execution = self._active_executions[execution_id]
        execution.status = BackupStatus.CANCELLED
        
        logger.info(f"Cancelled backup execution '{execution_id}'")
        return True
    
    def start_scheduler(self) -> None:
        """Start the backup scheduler."""
        if self._scheduler_running:
            logger.warning("Backup scheduler already running")
            return
        
        self._scheduler_running = True
        
        # Schedule existing enabled jobs
        for job in self._backup_jobs.values():
            if job.enabled:
                self._schedule_job(job)
        
        # Start scheduler thread
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True
        )
        self._scheduler_thread.start()
        
        logger.info("Backup scheduler started")
    
    def stop_scheduler(self) -> None:
        """Stop the backup scheduler."""
        self._scheduler_running = False
        
        # Clear all scheduled jobs
        schedule.clear()
        
        # Wait for scheduler thread to finish
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=30)
        
        logger.info("Backup scheduler stopped")
    
    def register_completion_callback(self, callback: Callable[[BackupExecution], None]) -> None:
        """Register callback for backup completion.
        
        Args:
            callback: Callback function to execute on completion
        """
        self._completion_callbacks.append(callback)
    
    def register_failure_callback(self, callback: Callable[[BackupExecution], None]) -> None:
        """Register callback for backup failure.
        
        Args:
            callback: Callback function to execute on failure
        """
        self._failure_callbacks.append(callback)
    
    def generate_backup_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate backup status report.
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Backup report
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_executions = [
            e for e in self._execution_history
            if e.start_time >= cutoff_date
        ]
        
        # Calculate statistics
        total_executions = len(recent_executions)
        successful_executions = len([e for e in recent_executions if e.status == BackupStatus.COMPLETED])
        failed_executions = len([e for e in recent_executions if e.status == BackupStatus.FAILED])
        
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Calculate total backup size
        total_backup_size = sum(e.file_size_bytes for e in recent_executions if e.file_size_bytes > 0)
        
        # Job-wise statistics
        job_stats = {}
        for job in self._backup_jobs.values():
            job_executions = [e for e in recent_executions if e.job_id == job.job_id]
            job_stats[job.job_id] = {
                'job_name': job.name,
                'total_executions': len(job_executions),
                'successful': len([e for e in job_executions if e.status == BackupStatus.COMPLETED]),
                'failed': len([e for e in job_executions if e.status == BackupStatus.FAILED]),
                'last_execution': max([e.start_time for e in job_executions]) if job_executions else None,
                'last_status': job_executions[0].status.value if job_executions else None
            }
        
        return {
            'report_period_days': days,
            'summary': {
                'total_backup_jobs': len(self._backup_jobs),
                'enabled_jobs': len([j for j in self._backup_jobs.values() if j.enabled]),
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'success_rate_percent': success_rate,
                'total_backup_size_gb': total_backup_size / (1024**3),
                'active_executions': len(self._active_executions)
            },
            'job_statistics': job_stats,
            'recent_failures': [
                {
                    'execution_id': e.execution_id,
                    'job_id': e.job_id,
                    'start_time': e.start_time.isoformat(),
                    'error_message': e.error_message
                }
                for e in recent_executions
                if e.status == BackupStatus.FAILED
            ][:10]  # Last 10 failures
        }
    
    def _validate_backup_job(self, job: BackupJob) -> bool:
        """Validate backup job configuration."""
        # Check required fields
        if not job.job_id or not job.name:
            logger.error("Job ID and name are required")
            return False
        
        # Check output directory
        if not job.output_directory:
            job.output_directory = self._default_output_dir
        
        try:
            os.makedirs(job.output_directory, exist_ok=True)
        except Exception as e:
            logger.error(f"Cannot create output directory '{job.output_directory}': {e}")
            return False
        
        # Validate schedule expression
        if not self._validate_schedule_expression(job.schedule_expression):
            logger.error(f"Invalid schedule expression: {job.schedule_expression}")
            return False
        
        return True
    
    def _validate_schedule_expression(self, expression: str) -> bool:
        """Validate schedule expression."""
        # Basic validation for common patterns
        valid_patterns = [
            'daily', 'hourly', 'weekly',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
        ]
        
        # Check if it's a time format
        try:
            time.strptime(expression, '%H:%M')
            return True
        except ValueError:
            pass
        
        # Check if it's a predefined pattern
        return expression.lower() in valid_patterns
    
    def _schedule_job(self, job: BackupJob) -> None:
        """Schedule backup job using schedule library."""
        expression = job.schedule_expression.lower()
        
        # Schedule based on expression type
        if expression == 'daily':
            schedule.every().day.at(self._backup_window_start).do(
                self._execute_scheduled_backup, job
            ).tag(job.job_id)
        elif expression == 'hourly':
            schedule.every().hour.do(
                self._execute_scheduled_backup, job
            ).tag(job.job_id)
        elif expression == 'weekly':
            schedule.every().week.do(
                self._execute_scheduled_backup, job
            ).tag(job.job_id)
        elif expression in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            getattr(schedule.every(), expression).at(self._backup_window_start).do(
                self._execute_scheduled_backup, job
            ).tag(job.job_id)
        else:
            # Try to parse as time
            try:
                schedule.every().day.at(expression).do(
                    self._execute_scheduled_backup, job
                ).tag(job.job_id)
            except Exception as e:
                logger.error(f"Failed to schedule job '{job.job_id}': {e}")
    
    def _execute_scheduled_backup(self, job: BackupJob) -> None:
        """Execute scheduled backup job."""
        # Check if backup window is active
        if not self._is_backup_window_active():
            logger.info(f"Skipping backup '{job.name}' - outside backup window")
            return
        
        # Check resource usage
        if self._resource_monitoring_enabled and not self._check_system_resources():
            logger.info(f"Skipping backup '{job.name}' - high resource usage")
            return
        
        # Check concurrent backup limit
        if len(self._active_executions) >= self._max_concurrent_backups:
            logger.info(f"Skipping backup '{job.name}' - max concurrent backups reached")
            return
        
        # Create execution record
        execution_id = self._generate_execution_id()
        execution = BackupExecution(
            execution_id=execution_id,
            job_id=job.job_id,
            backup_type=job.backup_type,
            start_time=datetime.utcnow(),
            status=BackupStatus.PENDING
        )
        
        # Execute backup
        self._execute_backup_job(job, execution)
    
    def _execute_backup_job(self, job: BackupJob, execution: BackupExecution) -> None:
        """Execute backup job."""
        execution.status = BackupStatus.RUNNING
        self._active_executions[execution.execution_id] = execution
        
        try:
            logger.info(f"Starting backup execution '{execution.execution_id}' for job '{job.name}'")
            
            # Generate output file path
            timestamp = execution.start_time.strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(
                job.output_directory,
                f"{job.name}_{job.backup_type.value}_{timestamp}"
            )
            
            # Execute backup based on type
            if job.backup_type == BackupType.FULL:
                self._execute_full_backup(job, execution, output_file)
            elif job.backup_type == BackupType.INCREMENTAL:
                self._execute_incremental_backup(job, execution, output_file)
            elif job.backup_type == BackupType.OPLOG:
                self._execute_oplog_backup(job, execution, output_file)
            else:
                raise ValueError(f"Unsupported backup type: {job.backup_type}")
            
            # Mark as completed
            execution.end_time = datetime.utcnow()
            execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()
            execution.status = BackupStatus.COMPLETED
            
            # Get file size
            if execution.file_path and os.path.exists(execution.file_path):
                execution.file_size_bytes = os.path.getsize(execution.file_path)
            
            logger.info(f"Backup execution '{execution.execution_id}' completed successfully")
            
            # Execute completion callbacks
            for callback in self._completion_callbacks:
                try:
                    callback(execution)
                except Exception as e:
                    logger.error(f"Completion callback error: {e}")
        
        except Exception as e:
            execution.status = BackupStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.utcnow()
            execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()
            
            logger.error(f"Backup execution '{execution.execution_id}' failed: {e}")
            
            # Execute failure callbacks
            for callback in self._failure_callbacks:
                try:
                    callback(execution)
                except Exception as e:
                    logger.error(f"Failure callback error: {e}")
        
        finally:
            # Remove from active executions and add to history
            self._active_executions.pop(execution.execution_id, None)
            self._execution_history.append(execution)
            
            # Keep only recent history (last 1000 executions)
            if len(self._execution_history) > 1000:
                self._execution_history = self._execution_history[-1000:]
    
    def _execute_full_backup(self, job: BackupJob, execution: BackupExecution, output_file: str) -> None:
        """Execute full backup using mongodump."""
        # Build mongodump command
        cmd = [self._mongodump_path]
        
        # Connection parameters
        if hasattr(self.client, 'HOST'):
            cmd.extend(['--host', self.client.HOST])
        if hasattr(self.client, 'PORT'):
            cmd.extend(['--port', str(self.client.PORT)])
        
        # Authentication
        # Note: In production, credentials should be handled securely
        # This is a simplified implementation
        
        # Database selection
        if job.databases:
            for db_name in job.databases:
                cmd.extend(['--db', db_name])
        
        # Output options
        if job.compression_enabled:
            cmd.append('--gzip')
            output_file += '.gz'
        
        cmd.extend(['--out', output_file])
        
        # Execute command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"mongodump failed: {result.stderr}")
        
        execution.file_path = output_file
        execution.databases_backed_up = job.databases or ['all']
    
    def _execute_incremental_backup(self, job: BackupJob, execution: BackupExecution, output_file: str) -> None:
        """Execute incremental backup."""
        # This is a simplified implementation
        # In practice, incremental backups would use oplog entries
        # or filesystem-level techniques
        
        # Implement proper incremental backup logic
        logger.info("Executing incremental backup")
        
        try:
            # Get the last full backup timestamp
            last_full_backup = self._get_last_full_backup_timestamp(job.job_id)
            
            if not last_full_backup:
                logger.warning("No previous full backup found, performing full backup instead")
                self._execute_full_backup(job, execution, output_file)
                return
            
            # Create incremental backup using oplog
            oplog_output = os.path.join(output_file, 'oplog_incremental')
            os.makedirs(oplog_output, exist_ok=True)
            
            # Build mongodump command for oplog since last backup
            cmd = [
                self._mongodump_path,
                '--db', 'local',
                '--collection', 'oplog.rs',
                '--query', f'{{"ts": {{"$gte": {last_full_backup}}}}}',
                '--out', oplog_output
            ]
            
            if job.compression_enabled:
                cmd.append('--gzip')
            
            # Execute incremental backup
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                execution.status = BackupStatus.COMPLETED
                execution.file_path = oplog_output
                execution.file_size_bytes = self._calculate_directory_size(oplog_output)
                logger.info(f"Incremental backup completed: {oplog_output}")
            else:
                execution.status = BackupStatus.FAILED
                execution.error_message = result.stderr
                logger.error(f"Incremental backup failed: {result.stderr}")
                
        except Exception as e:
            execution.status = BackupStatus.FAILED
            execution.error_message = str(e)
            logger.error(f"Incremental backup failed: {e}")
    
    def _get_last_full_backup_timestamp(self, job_id: str) -> Optional[dict]:
        """Get timestamp of last full backup for incremental backup.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Oplog timestamp of last full backup
        """
        try:
            # Find the most recent successful full backup
            for execution in reversed(self._execution_history):
                if (execution.job_id == job_id and 
                    execution.backup_type == BackupType.FULL and 
                    execution.status == BackupStatus.COMPLETED):
                    
                    # Return the oplog timestamp from when the backup started
                    return self._get_oplog_timestamp_for_time(execution.start_time)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get last backup timestamp: {e}")
            return None
    
    def _get_oplog_timestamp_for_time(self, backup_time: datetime) -> Optional[dict]:
        """Get oplog timestamp for a specific time.
        
        Args:
            backup_time: Backup start time
            
        Returns:
            Oplog timestamp
        """
        try:
            # Query oplog for entries around the backup time
            oplog = self.client.local.oplog.rs
            
            # Find the first oplog entry at or after the backup time
            query = {"ts": {"$gte": backup_time}}
            entry = oplog.find(query).sort([('ts', 1)]).limit(1)
            
            if entry:
                return list(entry)[0]['ts']
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get oplog timestamp: {e}")
            return None
    
    def _calculate_directory_size(self, directory: str) -> int:
        """Calculate total size of directory.
        
        Args:
            directory: Directory path
            
        Returns:
            Size in bytes
        """
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
        except Exception as e:
            logger.error(f"Failed to calculate directory size: {e}")
        
        return total_size
    
    def _execute_oplog_backup(self, job: BackupJob, execution: BackupExecution, output_file: str) -> None:
        """Execute oplog backup."""
        # Build mongodump command for oplog
        cmd = [
            self._mongodump_path,
            '--db', 'local',
            '--collection', 'oplog.rs',
            '--out', output_file
        ]
        
        if job.compression_enabled:
            cmd.append('--gzip')
            output_file += '.gz'
        
        # Execute command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"oplog backup failed: {result.stderr}")
        
        execution.file_path = output_file
        execution.databases_backed_up = ['local']
        execution.collections_backed_up = ['oplog.rs']
    
    def _is_backup_window_active(self) -> bool:
        """Check if current time is within backup window."""
        current_time = datetime.now().time()
        start_time = datetime.strptime(self._backup_window_start, '%H:%M').time()
        end_time = datetime.strptime(self._backup_window_end, '%H:%M').time()
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:
            # Window crosses midnight
            return current_time >= start_time or current_time <= end_time
    
    def _check_system_resources(self) -> bool:
        """Check if system resources are available for backup."""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            return cpu_percent < self._cpu_threshold and memory_percent < self._memory_threshold
        except Exception:
            # If can't check resources, assume OK
            return True
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self._scheduler_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                time.sleep(60)

# Global scheduler instance
_default_scheduler: Optional[BackupScheduler] = None

def get_backup_scheduler(client: MongoClient, **kwargs) -> BackupScheduler:
    """Get or create default backup scheduler."""
    global _default_scheduler
    if _default_scheduler is None:
        _default_scheduler = BackupScheduler(client, **kwargs)
    return _default_scheduler

__all__ = [
    'BackupScheduler', 'BackupJob', 'BackupExecution', 'BackupType', 'BackupStatus',
    'get_backup_scheduler'
]