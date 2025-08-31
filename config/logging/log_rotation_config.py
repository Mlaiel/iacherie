"""
Log Rotation Configuration for IA-Influencer Agent Platform
==========================================================

Advanced log rotation management with compression, archiving,
and intelligent cleanup for high-volume content processing logs.

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
import gzip
import bz2
import lzma
import shutil
import threading
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import logging.handlers
import glob
import stat

import psutil


class CompressionType(str, Enum):
    """Supported compression types"""
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"


class RotationTrigger(str, Enum):
    """Log rotation triggers"""
    SIZE = "size"
    TIME = "time"
    HYBRID = "hybrid"  # Both size and time
    DISK_SPACE = "disk_space"


class ArchiveStrategy(str, Enum):
    """Archive storage strategies"""
    LOCAL = "local"
    S3 = "s3"
    AZURE_BLOB = "azure_blob"
    GCS = "gcs"
    FTP = "ftp"


@dataclass
class RotationPolicy:
    """Log rotation policy configuration"""
    name: str
    log_pattern: str  # Glob pattern to match log files
    
    # Size-based rotation
    max_file_size: Optional[str] = "100MB"  # e.g., "100MB", "1GB"
    
    # Time-based rotation
    rotation_interval: Optional[str] = "daily"  # daily, weekly, monthly
    rotation_time: Optional[str] = "00:00"  # Time to rotate (HH:MM)
    
    # Retention settings
    backup_count: int = 30  # Number of rotated files to keep
    max_age_days: Optional[int] = None  # Delete files older than N days
    
    # Compression settings
    compression: CompressionType = CompressionType.GZIP
    compress_after_days: int = 1  # Compress files after N days
    
    # Archiving settings
    archive_enabled: bool = False
    archive_strategy: ArchiveStrategy = ArchiveStrategy.LOCAL
    archive_after_days: int = 30
    archive_path: Optional[str] = None
    
    # Cleanup settings
    delete_after_archive: bool = False
    cleanup_empty_dirs: bool = True
    
    # Performance settings
    async_compression: bool = True
    compression_level: int = 6  # 1-9 for gzip/bzip2, 0-9 for lzma
    
    # Monitoring settings
    notify_on_rotation: bool = False
    notification_webhook: Optional[str] = None


@dataclass
class DiskSpaceMonitor:
    """Disk space monitoring configuration"""
    enabled: bool = True
    check_interval: int = 300  # Seconds between checks
    warning_threshold: float = 0.85  # Warn when disk is 85% full
    critical_threshold: float = 0.95  # Critical when disk is 95% full
    emergency_cleanup: bool = True  # Enable emergency cleanup
    min_free_space: str = "1GB"  # Minimum free space to maintain


class LogRotationConfig:
    """
    Enterprise log rotation configuration for IA-Influencer platform.
    
    Provides intelligent log rotation with compression, archiving, cleanup,
    and disk space monitoring for high-volume content processing operations.
    """
    
    def __init__(
        self,
        base_log_path: str = "/var/log/ia_influencer",
        policies: Optional[List[RotationPolicy]] = None,
        disk_monitor: Optional[DiskSpaceMonitor] = None,
        global_compression: CompressionType = CompressionType.GZIP,
        enable_scheduling: bool = True,
        max_concurrent_operations: int = 3,
        operation_timeout: int = 300,  # 5 minutes
        enable_notifications: bool = False,
        webhook_url: Optional[str] = None
    ):
        """
        Initialize log rotation configuration.
        
        Args:
            base_log_path: Base directory for log files
            policies: List of rotation policies
            disk_monitor: Disk space monitoring configuration
            global_compression: Default compression type
            enable_scheduling: Enable automatic rotation scheduling
            max_concurrent_operations: Max concurrent rotation operations
            operation_timeout: Timeout for rotation operations
            enable_notifications: Enable rotation notifications
            webhook_url: Webhook URL for notifications
        """
        self.base_log_path = Path(base_log_path)
        self.policies = policies or self._create_default_policies()
        self.disk_monitor = disk_monitor or DiskSpaceMonitor()
        self.global_compression = global_compression
        self.enable_scheduling = enable_scheduling
        self.max_concurrent_operations = max_concurrent_operations
        self.operation_timeout = operation_timeout
        self.enable_notifications = enable_notifications
        self.webhook_url = webhook_url
        
        # Initialize components
        self._initialize_directories()
        self._active_operations: Dict[str, threading.Thread] = {}
        self._operation_lock = threading.Lock()
        self._scheduler_thread = None
        self._stop_event = threading.Event()
        
        # Initialize rotation handlers
        self._handlers: Dict[str, logging.handlers.RotatingFileHandler] = {}
        self._initialize_handlers()
        
        # Start scheduler if enabled
        if self.enable_scheduling:
            self.start_scheduler()
    
    def _create_default_policies(self) -> List[RotationPolicy]:
        """Create default rotation policies for platform components"""



        return [
            # Main application logs
            RotationPolicy(
                name="platform_logs",
                log_pattern="ia_influencer_platform_*.log",
                max_file_size="200MB",
                rotation_interval="daily",
                backup_count=30,
                compression=CompressionType.GZIP,
                compress_after_days=1,
                archive_enabled=True,
                archive_after_days=30
            ),
            
            # API access logs
            RotationPolicy(
                name="api_logs",
                log_pattern="ia_influencer_api_*.log",
                max_file_size="500MB",
                rotation_interval="daily",
                backup_count=60,
                compression=CompressionType.GZIP,
                compress_after_days=1,
                archive_enabled=True,
                archive_after_days=30
            ),
            
            # Error logs - high retention
            RotationPolicy(
                name="error_logs",
                log_pattern="errors_*.log",
                max_file_size="100MB",
                rotation_interval="daily",
                backup_count=90,
                compression=CompressionType.GZIP,
                compress_after_days=1,
                archive_enabled=True,
                archive_after_days=90,
                max_age_days=365
            ),
            
            # Security logs - compliance retention
            RotationPolicy(
                name="security_logs",
                log_pattern="security_*.log",
                max_file_size="100MB",
                rotation_interval="daily",
                backup_count=365,
                compression=CompressionType.GZIP,
                compress_after_days=1,
                archive_enabled=True,
                archive_after_days=30,
                max_age_days=2555  # 7 years
            ),
            
            # Audit logs - long retention
            RotationPolicy(
                name="audit_logs",
                log_pattern="audit_*.log",
                max_file_size="100MB",
                rotation_interval="daily",
                backup_count=365,
                compression=CompressionType.GZIP,
                compress_after_days=1,
                archive_enabled=True,
                archive_after_days=30,
                max_age_days=2555  # 7 years
            ),
            
            # Performance logs
            RotationPolicy(
                name="performance_logs",
                log_pattern="performance_*.log",
                max_file_size="250MB",
                rotation_interval="daily",
                backup_count=30,
                compression=CompressionType.GZIP,
                compress_after_days=1,
                archive_enabled=False
            ),
            
            # AI processing logs
            RotationPolicy(
                name="ai_processing_logs",
                log_pattern="ia_influencer_ai_*_*.log",
                max_file_size="300MB",
                rotation_interval="daily",
                backup_count=14,
                compression=CompressionType.GZIP,
                compress_after_days=1,
                archive_enabled=True,
                archive_after_days=14
            ),
            
            # Content protection logs
            RotationPolicy(
                name="protection_logs",
                log_pattern="ia_influencer_*protection*.log",
                max_file_size="200MB",
                rotation_interval="daily",
                backup_count=60,
                compression=CompressionType.GZIP,
                compress_after_days=1,
                archive_enabled=True,
                archive_after_days=30
            ),
            
            # External integration logs
            RotationPolicy(
                name="integration_logs",
                log_pattern="ia_influencer_*_api_*.log",
                max_file_size="150MB",
                rotation_interval="daily",
                backup_count=30,
                compression=CompressionType.GZIP,
                compress_after_days=1,
                archive_enabled=False
            )
        ]
    
    def _initialize_directories(self) -> None:
        """Initialize log and archive directories"""
        self.base_log_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different log types
        subdirs = ['archive', 'temp', 'compressed']
        for subdir in subdirs:
            (self.base_log_path / subdir).mkdir(exist_ok=True)
    
    def _initialize_handlers(self) -> None:
        """Initialize rotating file handlers"""
        for policy in self.policies:
            try:
                self._create_handler_for_policy(policy)
            except Exception as e:
                logging.error(f"Failed to initialize handler for policy {policy.name}: {e}")
    
    def _create_handler_for_policy(self, policy: RotationPolicy) -> None:
        """Create rotating file handler for a policy"""
        # Find matching log files
        log_files = list(self.base_log_path.glob(policy.log_pattern))
        
        for log_file in log_files:
            handler_key = f"{policy.name}_{log_file.stem}"
            
            if policy.max_file_size:
                # Size-based rotation
                max_bytes = self._parse_size(policy.max_file_size)
                handler = logging.handlers.RotatingFileHandler(
                    filename=log_file,
                    maxBytes=max_bytes,
                    backupCount=policy.backup_count,
                    encoding='utf-8'
                )
            else:
                # Time-based rotation
                when = self._parse_rotation_interval(policy.rotation_interval)
                handler = logging.handlers.TimedRotatingFileHandler(
                    filename=log_file,
                    when=when,
                    interval=1,
                    backupCount=policy.backup_count,
                    encoding='utf-8'
                )
            
            self._handlers[handler_key] = handler
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string to bytes"""
        size_str = size_str.upper().strip()
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024**2,
            'GB': 1024**3,
            'TB': 1024**4
        }
        
        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                try:
                    number = float(size_str[:-len(suffix)])
                    return int(number * multiplier)
                except ValueError:
                    break
        
        # Default to MB if no suffix
        try:
            return int(float(size_str) * 1024**2)
        except ValueError:
            return 100 * 1024**2  # 100MB default
    
    def _parse_rotation_interval(self, interval: str) -> str:
        """Parse rotation interval to logging format"""
        interval_map = {
            'daily': 'D',
            'weekly': 'W0',  # Monday
            'monthly': 'midnight',
            'hourly': 'H'
        }
        
        return interval_map.get(interval.lower(), 'D')
    
    def rotate_logs(self, policy_name: Optional[str] = None) -> Dict[str, bool]:
        """
        Manually trigger log rotation.
        
        Args:
            policy_name: Specific policy to rotate (None for all)
            
        Returns:
            Dictionary of rotation results by policy name
        """
        results = {}
        
        policies_to_rotate = [p for p in self.policies if p.name == policy_name] if policy_name else self.policies
        
        for policy in policies_to_rotate:
            try:
                success = self._rotate_policy_logs(policy)
                results[policy.name] = success
                
                if self.enable_notifications and policy.notify_on_rotation:
                    self._send_rotation_notification(policy.name, success)
                    
            except Exception as e:
                logging.error(f"Failed to rotate logs for policy {policy.name}: {e}")
                results[policy.name] = False
        
        return results
    
    def _rotate_policy_logs(self, policy: RotationPolicy) -> bool:
        """Rotate logs for a specific policy"""



        try:
            # Find matching log files
            log_files = list(self.base_log_path.glob(policy.log_pattern))
            
            if not log_files:
                logging.debug(f"No log files found for policy {policy.name}")
                return True
            
            for log_file in log_files:
                # Check if rotation is needed
                if self._should_rotate_file(log_file, policy):
                    self._rotate_single_file(log_file, policy)
            
            # Perform cleanup
            self._cleanup_old_files(policy)
            
            # Compress files if needed
            if policy.compression != CompressionType.NONE:
                self._compress_old_files(policy)
            
            # Archive files if enabled
            if policy.archive_enabled:
                self._archive_old_files(policy)
            
            return True
            
        except Exception as e:
            logging.error(f"Error rotating logs for policy {policy.name}: {e}")
            return False
    
    def _should_rotate_file(self, log_file: Path, policy: RotationPolicy) -> bool:
        """Check if a log file should be rotated"""
        if not log_file.exists():
            return False
        
        file_stat = log_file.stat()
        
        # Size-based check
        if policy.max_file_size:
            max_bytes = self._parse_size(policy.max_file_size)
            if file_stat.st_size >= max_bytes:
                return True
        
        # Time-based check
        if policy.rotation_interval:
            file_age = datetime.now() - datetime.fromtimestamp(file_stat.st_mtime)
            
            if policy.rotation_interval == "daily" and file_age.days >= 1:
                return True
            elif policy.rotation_interval == "weekly" and file_age.days >= 7:
                return True
            elif policy.rotation_interval == "monthly" and file_age.days >= 30:
                return True
        
        return False
    
    def _rotate_single_file(self, log_file: Path, policy: RotationPolicy) -> None:
        """Rotate a single log file"""
        if not log_file.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
        rotated_path = log_file.parent / rotated_name
        
        try:
            # Move current log file to rotated name
            shutil.move(str(log_file), str(rotated_path))
            
            # Create new empty log file with proper permissions
            log_file.touch()
            os.chmod(log_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)
            
            logging.info(f"Rotated log file: {log_file} -> {rotated_path}")
            
        except Exception as e:
            logging.error(f"Failed to rotate file {log_file}: {e}")
            raise
    
    def _cleanup_old_files(self, policy: RotationPolicy) -> None:
        """Clean up old log files based on retention policy"""
        pattern = policy.log_pattern.replace('*', '*_[0-9]*')
        old_files = list(self.base_log_path.glob(pattern))
        
        # Sort by modification time (oldest first)
        old_files.sort(key=lambda f: f.stat().st_mtime)
        
        # Remove files exceeding backup count
        if len(old_files) > policy.backup_count:
            files_to_remove = old_files[:-policy.backup_count]
            
            for file_to_remove in files_to_remove:
                try:
                    file_to_remove.unlink()
                    logging.debug(f"Cleaned up old log file: {file_to_remove}")
                except Exception as e:
                    logging.error(f"Failed to remove old log file {file_to_remove}: {e}")
        
        # Remove files exceeding max age
        if policy.max_age_days:
            cutoff_date = datetime.now() - timedelta(days=policy.max_age_days)
            
            for old_file in old_files:
                if datetime.fromtimestamp(old_file.stat().st_mtime) < cutoff_date:
                    try:
                        old_file.unlink()
                        logging.debug(f"Cleaned up aged log file: {old_file}")
                    except Exception as e:
                        logging.error(f"Failed to remove aged log file {old_file}: {e}")
    
    def _compress_old_files(self, policy: RotationPolicy) -> None:
        """Compress old log files based on policy"""
        if policy.compression == CompressionType.NONE:
            return
        
        # Find uncompressed rotated files
        pattern = policy.log_pattern.replace('*', '*_[0-9]*')
        files_to_compress = []
        
        for file_path in self.base_log_path.glob(pattern):
            if not any(file_path.name.endswith(ext) for ext in ['.gz', '.bz2', '.xz']):
                file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age.days >= policy.compress_after_days:
                    files_to_compress.append(file_path)
        
        # Compress files
        for file_path in files_to_compress:
            if policy.async_compression:
                thread = threading.Thread(
                    target=self._compress_file,
                    args=(file_path, policy.compression, policy.compression_level),
                    daemon=True
                )
                thread.start()
            else:
                self._compress_file(file_path, policy.compression, policy.compression_level)
    
    def _compress_file(self, file_path: Path, compression: CompressionType, level: int) -> None:
        """Compress a single file"""



        try:
            if compression == CompressionType.GZIP:
                compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb', compresslevel=level) as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif compression == CompressionType.BZIP2:
                compressed_path = file_path.with_suffix(file_path.suffix + '.bz2')
                with open(file_path, 'rb') as f_in:
                    with bz2.open(compressed_path, 'wb', compresslevel=level) as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif compression == CompressionType.LZMA:
                compressed_path = file_path.with_suffix(file_path.suffix + '.xz')
                with open(file_path, 'rb') as f_in:
                    with lzma.open(compressed_path, 'wb', preset=level) as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            else:
                return
            
            # Verify compressed file and remove original
            if compressed_path.exists() and compressed_path.stat().st_size > 0:
                file_path.unlink()
                logging.debug(f"Compressed log file: {file_path} -> {compressed_path}")
            else:
                if compressed_path.exists():
                    compressed_path.unlink()
                raise Exception("Compressed file is empty or invalid")
                
        except Exception as e:
            logging.error(f"Failed to compress file {file_path}: {e}")
    
    def _archive_old_files(self, policy: RotationPolicy) -> None:
        """Archive old log files to external storage"""
        if not policy.archive_enabled:
            return
        
        # Find files to archive
        cutoff_date = datetime.now() - timedelta(days=policy.archive_after_days)
        pattern = policy.log_pattern.replace('*', '*_[0-9]*')
        
        files_to_archive = []
        for file_path in self.base_log_path.glob(pattern):
            if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_date:
                files_to_archive.append(file_path)
        
        if not files_to_archive:
            return
        
        # Archive based on strategy
        if policy.archive_strategy == ArchiveStrategy.LOCAL:
            self._archive_to_local(files_to_archive, policy)
        elif policy.archive_strategy == ArchiveStrategy.S3:
            self._archive_to_s3(files_to_archive, policy)
        # Add other archive strategies as needed
    
    def _archive_to_local(self, files: List[Path], policy: RotationPolicy) -> None:
        """Archive files to local directory"""
        archive_dir = self.base_log_path / 'archive' / policy.name
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in files:
            try:
                archive_path = archive_dir / file_path.name
                shutil.move(str(file_path), str(archive_path))
                logging.debug(f"Archived log file: {file_path} -> {archive_path}")
                
            except Exception as e:
                logging.error(f"Failed to archive file {file_path}: {e}")
    
    def _archive_to_s3(self, files: List[Path], policy: RotationPolicy) -> None:
        """Archive files to AWS S3"""
        # Implementation would use boto3 to upload files to S3
        # This is a placeholder for the actual implementation
        logging.info(f"Would archive {len(files)} files to S3 for policy {policy.name}")
    
    def check_disk_space(self) -> Dict[str, Any]:
        """Check disk space and return status"""
        if not self.disk_monitor.enabled:
            return {"enabled": False}
        
        try:
            disk_usage = psutil.disk_usage(str(self.base_log_path))
            
            total = disk_usage.total
            used = disk_usage.used
            free = disk_usage.free
            percent_used = used / total
            
            status = "normal"
            if percent_used >= self.disk_monitor.critical_threshold:
                status = "critical"
            elif percent_used >= self.disk_monitor.warning_threshold:
                status = "warning"
            
            result = {
                "enabled": True,
                "status": status,
                "total_bytes": total,
                "used_bytes": used,
                "free_bytes": free,
                "percent_used": percent_used,
                "warning_threshold": self.disk_monitor.warning_threshold,
                "critical_threshold": self.disk_monitor.critical_threshold
            }
            
            # Trigger emergency cleanup if critical
            if status == "critical" and self.disk_monitor.emergency_cleanup:
                self._emergency_cleanup()
                result["emergency_cleanup_triggered"] = True
            
            return result
            
        except Exception as e:
            logging.error(f"Failed to check disk space: {e}")
            return {"enabled": True, "error": str(e)}
    
    def _emergency_cleanup(self) -> None:
        """Perform emergency cleanup when disk space is critical"""
        logging.warning("Performing emergency log cleanup due to low disk space")
        
        try:
            # Force rotation of all large files
            for policy in self.policies:
                self._emergency_rotate_policy(policy)
            
            # Compress all uncompressed files immediately
            self._emergency_compress_all()
            
            # Clean up temporary files
            temp_dir = self.base_log_path / 'temp'
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                temp_dir.mkdir()
            
        except Exception as e:
            logging.error(f"Emergency cleanup failed: {e}")
    
    def _emergency_rotate_policy(self, policy: RotationPolicy) -> None:
        """Emergency rotation for a policy - more aggressive cleanup"""



        try:
            # Reduce backup count temporarily for emergency cleanup
            original_backup_count = policy.backup_count
            policy.backup_count = max(1, policy.backup_count // 2)
            
            self._rotate_policy_logs(policy)
            
            # Restore original backup count
            policy.backup_count = original_backup_count
            
        except Exception as e:
            logging.error(f"Emergency rotation failed for policy {policy.name}: {e}")
    
    def _emergency_compress_all(self) -> None:
        """Emergency compression of all uncompressed log files"""



        try:
            for policy in self.policies:
                if policy.compression != CompressionType.NONE:
                    # Compress files immediately regardless of age
                    original_compress_after_days = policy.compress_after_days
                    policy.compress_after_days = 0
                    
                    self._compress_old_files(policy)
                    
                    # Restore original setting
                    policy.compress_after_days = original_compress_after_days
                    
        except Exception as e:
            logging.error(f"Emergency compression failed: {e}")
    
    def _send_rotation_notification(self, policy_name: str, success: bool) -> None:
        """Send rotation notification"""
        if not self.enable_notifications or not self.webhook_url:
            return
        
        try:
            import requests
            
            message = f"Log rotation {'succeeded' if success else 'failed'} for policy: {policy_name}"
            payload = {
                "text": message,
                "policy": policy_name,
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
        except Exception as e:
            logging.error(f"Failed to send rotation notification: {e}")
    
    def start_scheduler(self) -> None:
        """Start the automatic rotation scheduler"""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()
        
        logging.info("Log rotation scheduler started")
    
    def stop_scheduler(self) -> None:
        """Stop the automatic rotation scheduler"""
        if self._scheduler_thread:
            self._stop_event.set()
            self._scheduler_thread.join(timeout=10)
        
        logging.info("Log rotation scheduler stopped")
    
    def _run_scheduler(self) -> None:
        """Run the rotation scheduler"""
        # Schedule rotation jobs
        schedule.every().day.at("00:00").do(self._scheduled_rotation)
        schedule.every().hour.do(self._scheduled_disk_check)
        
        while not self._stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logging.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def _scheduled_rotation(self) -> None:
        """Scheduled rotation job"""



        try:
            results = self.rotate_logs()
            logging.info(f"Scheduled rotation completed: {results}")
        except Exception as e:
            logging.error(f"Scheduled rotation failed: {e}")
    
    def _scheduled_disk_check(self) -> None:
        """Scheduled disk space check"""



        try:
            status = self.check_disk_space()
            if status.get("status") in ["warning", "critical"]:
                logging.warning(f"Disk space check: {status}")
        except Exception as e:
            logging.error(f"Scheduled disk check failed: {e}")
    
    def get_rotation_status(self) -> Dict[str, Any]:
        """Get current rotation status and statistics"""
        status = {
            "enabled": True,
            "base_path": str(self.base_log_path),
            "policies_count": len(self.policies),
            "active_operations": len(self._active_operations),
            "scheduler_running": self._scheduler_thread and self._scheduler_thread.is_alive(),
            "policies": []
        }
        
        for policy in self.policies:
            policy_status = {
                "name": policy.name,
                "pattern": policy.log_pattern,
                "compression": policy.compression.value,
                "backup_count": policy.backup_count,
                "archive_enabled": policy.archive_enabled
            }
            
            # Count matching files
            matching_files = list(self.base_log_path.glob(policy.log_pattern))
            policy_status["file_count"] = len(matching_files)
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in matching_files if f.exists())
            policy_status["total_size"] = total_size
            
            status["policies"].append(policy_status)
        
        # Add disk space info
        disk_status = self.check_disk_space()
        status["disk_space"] = disk_status
        
        return status
    
    def add_policy(self, policy: RotationPolicy) -> None:
        """Add a new rotation policy"""
        self.policies.append(policy)
        self._create_handler_for_policy(policy)
        logging.info(f"Added rotation policy: {policy.name}")
    
    def remove_policy(self, policy_name: str) -> bool:
        """Remove a rotation policy"""
        policy = next((p for p in self.policies if p.name == policy_name), None)
        if policy:
            self.policies.remove(policy)
            
            # Remove associated handlers
            handlers_to_remove = [k for k in self._handlers.keys() if k.startswith(policy_name)]
            for handler_key in handlers_to_remove:
                del self._handlers[handler_key]
            
            logging.info(f"Removed rotation policy: {policy_name}")
            return True
        
        return False
    
    def update_policy(self, policy_name: str, **kwargs) -> bool:
        """Update an existing rotation policy"""
        policy = next((p for p in self.policies if p.name == policy_name), None)
        if policy:
            for key, value in kwargs.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
            
            # Recreate handlers for updated policy
            handlers_to_remove = [k for k in self._handlers.keys() if k.startswith(policy_name)]
            for handler_key in handlers_to_remove:
                del self._handlers[handler_key]
            
            self._create_handler_for_policy(policy)
            
            logging.info(f"Updated rotation policy: {policy_name}")
            return True
        
        return False


# Global log rotation configuration instance
_rotation_config: Optional[LogRotationConfig] = None


def initialize_log_rotation(
    config: Optional[LogRotationConfig] = None
) -> LogRotationConfig:
    """
    Initialize global log rotation configuration.
    
    Args:
        config: Custom LogRotationConfig instance
        
    Returns:
        Initialized log rotation configuration
    """
    global _rotation_config
    
    if config:
        _rotation_config = config
    else:
        _rotation_config = LogRotationConfig()
    
    return _rotation_config


def get_rotation_config() -> LogRotationConfig:
    """Get the global log rotation configuration"""
    if not _rotation_config:
        initialize_log_rotation()
    
    return _rotation_config


def rotate_logs(policy_name: Optional[str] = None) -> Dict[str, bool]:
    """
    Trigger log rotation using global configuration.
    
    Args:
        policy_name: Specific policy to rotate (None for all)
        
    Returns:
        Dictionary of rotation results by policy name
    """
    config = get_rotation_config()
    return config.rotate_logs(policy_name)
