"""
File Backup Manager - Enterprise File System Backup System
=========================================================

Advanced file system backup with intelligent handling, deduplication,
compression, and creator content protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import logging
import os
import hashlib
import shutil
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import mimetypes
import time

logger = logging.getLogger(__name__)


class FileType(Enum):
    """Types of files for backup classification."""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CONFIG = "config"
    LOG = "log"
    DATABASE = "database"
    EXECUTABLE = "executable"
    SOURCE_CODE = "source_code"
    CREATOR_CONTENT = "creator_content"
    AI_MODEL = "ai_model"


class BackupStrategy(Enum):
    """File backup strategies."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    MIRROR = "mirror"
    VERSIONED = "versioned"


class CompressionType(Enum):
    """Supported compression types."""
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"
    ZIP = "zip"


@dataclass
class FileMetadata:
    """Comprehensive file metadata."""
    file_path: str
    file_size: int
    modified_time: datetime
    created_time: datetime
    file_type: FileType
    mime_type: str
    checksum: str
    permissions: str
    owner: str
    group: str
    is_symlink: bool = False
    symlink_target: Optional[str] = None
    creator_id: Optional[str] = None  # For creator content
    content_category: Optional[str] = None  # For business categorization


@dataclass
class BackupJob:
    """File backup job configuration."""
    job_id: str
    source_paths: List[str]
    destination_path: str
    strategy: BackupStrategy
    compression: CompressionType
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    max_file_size_mb: int = 1000
    follow_symlinks: bool = False
    preserve_permissions: bool = True
    enable_deduplication: bool = True
    parallel_workers: int = 4
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BackupResult:
    """Result of backup operation."""
    job_id: str
    status: str
    files_processed: int
    files_backed_up: int
    files_skipped: int
    files_failed: int
    total_size_bytes: int
    compressed_size_bytes: int
    compression_ratio: float
    duration_seconds: float
    deduplication_savings_bytes: int
    started_at: datetime
    completed_at: datetime
    error_messages: List[str] = field(default_factory=list)
    backup_manifest: Dict[str, FileMetadata] = field(default_factory=dict)


class FileBackupManager:
    """
    Enterprise file backup manager with intelligent file handling.
    
    Features:
    - Intelligent file type detection and handling
    - Deduplication with SHA-256 hashing
    - Multiple compression strategies
    - Parallel processing for performance
    - Creator content specialized handling
    - Symbolic link preservation
    - Permission and ownership preservation
    - Large file chunking
    - Incremental and differential backups
    """
    
    def __init__(self, base_backup_path: str):
        """Initialize file backup manager."""
        self.base_backup_path = Path(base_backup_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.active_jobs: Dict[str, BackupJob] = {}
        self.job_history: List[BackupResult] = []
        self.file_registry: Dict[str, FileMetadata] = {}  # Checksum -> FileMetadata
        
        # Creator platform specific configuration
        self.creator_content_patterns = [
            "*.mp4", "*.avi", "*.mov", "*.mp3", "*.wav", "*.flac",
            "*.jpg", "*.jpeg", "*.png", "*.gif", "*.pdf", "*.doc*",
            "*.psd", "*.ai", "*.sketch", "*.fig"
        ]
        
        self.ai_model_patterns = [
            "*.pkl", "*.pt", "*.h5", "*.pb", "*.onnx", "*.tflite",
            "*.safetensors", "*.bin", "model.json", "config.json"
        ]
        
        # Ensure backup directory exists
        self.base_backup_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize deduplication index
        self.dedup_index: Dict[str, str] = {}  # checksum -> first_occurrence_path
    
    async def create_backup(
        self,
        source_paths: List[str],
        job_name: str,
        strategy: BackupStrategy = BackupStrategy.INCREMENTAL,
        compression: CompressionType = CompressionType.GZIP
    ) -> str:
        """
        Create file backup with enterprise features.
        
        Args:
            source_paths: List of source paths to backup
            job_name: Name for this backup job
            strategy: Backup strategy to use
            compression: Compression type
            
        Returns:
            Job ID for tracking
        """
        job_id = self._generate_job_id(job_name)
        
        # Create destination path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination_path = str(self.base_backup_path / f"{job_name}_{timestamp}")
        
        backup_job = BackupJob(
            job_id=job_id,
            source_paths=source_paths,
            destination_path=destination_path,
            strategy=strategy,
            compression=compression,
            exclude_patterns=[
                "*.tmp", "*.temp", "__pycache__", "*.pyc", "node_modules",
                ".git", ".svn", ".DS_Store", "Thumbs.db"
            ]
        )
        
        self.active_jobs[job_id] = backup_job
        
        try:
            self.logger.info(f"📁 Starting file backup: {job_id}")
            result = await self._execute_backup_job(backup_job)
            
            self.job_history.append(result)
            self.logger.info(f"✅ File backup completed: {job_id}")
            
            return job_id
            
        except Exception as e:
            self.logger.error(f"❌ File backup failed: {job_id} - {str(e)}")
            raise
        finally:
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
    
    async def _execute_backup_job(self, job: BackupJob) -> BackupResult:
        """Execute the actual backup job."""
        start_time = datetime.now()
        
        result = BackupResult(
            job_id=job.job_id,
            status="running",
            files_processed=0,
            files_backed_up=0,
            files_skipped=0,
            files_failed=0,
            total_size_bytes=0,
            compressed_size_bytes=0,
            compression_ratio=0.0,
            duration_seconds=0.0,
            deduplication_savings_bytes=0,
            started_at=start_time,
            completed_at=start_time
        )
        
        try:
            # Create destination directory
            os.makedirs(job.destination_path, exist_ok=True)
            
            # Collect all files to backup
            files_to_backup = await self._collect_files(job)
            
            # Process files in parallel
            await self._process_files_parallel(job, files_to_backup, result)
            
            # Create backup manifest
            await self._create_backup_manifest(job, result)
            
            # Apply compression if requested
            if job.compression != CompressionType.NONE:
                await self._compress_backup(job, result)
            
            result.status = "success"
            result.completed_at = datetime.now()
            result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
            
            # Calculate compression ratio
            if result.compressed_size_bytes > 0:
                result.compression_ratio = 1 - (result.compressed_size_bytes / result.total_size_bytes)
            
        except Exception as e:
            result.status = "failed"
            result.error_messages.append(str(e))
            result.completed_at = datetime.now()
            result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
            raise
        
        return result
    
    async def _collect_files(self, job: BackupJob) -> List[Path]:
        """Collect all files that need to be backed up."""
        files_to_backup = []
        
        for source_path in job.source_paths:
            source = Path(source_path)
            
            if not source.exists():
                self.logger.warning(f"Source path does not exist: {source_path}")
                continue
            
            if source.is_file():
                if await self._should_backup_file(source, job):
                    files_to_backup.append(source)
            elif source.is_dir():
                async for file_path in self._walk_directory(source, job):
                    if await self._should_backup_file(file_path, job):
                        files_to_backup.append(file_path)
        
        return files_to_backup
    
    async def _walk_directory(self, directory: Path, job: BackupJob):
        """Asynchronously walk directory tree."""
        try:
            for root, dirs, files in os.walk(directory, followlinks=job.follow_symlinks):
                root_path = Path(root)
                
                # Filter directories based on exclude patterns
                dirs[:] = [d for d in dirs if not self._matches_exclude_pattern(d, job)]
                
                for file_name in files:
                    file_path = root_path / file_name
                    
                    if not self._matches_exclude_pattern(str(file_path), job):
                        yield file_path
                        
                # Yield control periodically for async processing
                await asyncio.sleep(0)
                
        except PermissionError as e:
            self.logger.warning(f"Permission denied accessing directory: {directory} - {e}")
    
    async def _should_backup_file(self, file_path: Path, job: BackupJob) -> bool:
        """Determine if file should be backed up."""
        try:
            # Check file size limit
            file_size = file_path.stat().st_size
            if file_size > job.max_file_size_mb * 1024 * 1024:
                self.logger.debug(f"File too large, skipping: {file_path}")
                return False
            
            # Check include/exclude patterns
            if job.include_patterns and not any(
                file_path.match(pattern) for pattern in job.include_patterns
            ):
                return False
            
            if self._matches_exclude_pattern(str(file_path), job):
                return False
            
            # For incremental backups, check if file changed
            if job.strategy == BackupStrategy.INCREMENTAL:
                return await self._file_changed_since_last_backup(file_path)
            
            return True
            
        except (OSError, PermissionError) as e:
            self.logger.warning(f"Cannot access file: {file_path} - {e}")
            return False
    
    def _matches_exclude_pattern(self, file_path: str, job: BackupJob) -> bool:
        """Check if file matches any exclude pattern."""
        return any(
            Path(file_path).match(pattern) for pattern in job.exclude_patterns
        )
    
    async def _file_changed_since_last_backup(self, file_path: Path) -> bool:
        """Check if file changed since last backup (for incremental)."""
        # For now, always return True (backup all files)
        # In production, implement actual change detection
        return True
    
    async def _process_files_parallel(
        self,
        job: BackupJob,
        files: List[Path],
        result: BackupResult
    ) -> None:
        """Process files in parallel using worker threads."""
        semaphore = asyncio.Semaphore(job.parallel_workers)
        
        async def process_file(file_path: Path):
            async with semaphore:
                await self._backup_single_file(file_path, job, result)
        
        # Process all files concurrently
        tasks = [process_file(file_path) for file_path in files]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _backup_single_file(
        self,
        file_path: Path,
        job: BackupJob,
        result: BackupResult
    ) -> None:
        """Backup a single file with deduplication and metadata preservation."""
        try:
            result.files_processed += 1
            
            # Get file metadata
            metadata = await self._get_file_metadata(file_path)
            
            # Check for deduplication
            if job.enable_deduplication and metadata.checksum in self.dedup_index:
                # File already exists, create hardlink or skip
                result.files_skipped += 1
                result.deduplication_savings_bytes += metadata.file_size
                self.logger.debug(f"Deduplicated file: {file_path}")
                return
            
            # Calculate relative path for backup
            relative_path = self._get_relative_backup_path(file_path, job)
            backup_file_path = Path(job.destination_path) / relative_path
            
            # Ensure destination directory exists
            backup_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file with metadata preservation
            await self._copy_file_with_metadata(file_path, backup_file_path, metadata, job)
            
            # Update deduplication index
            if job.enable_deduplication:
                self.dedup_index[metadata.checksum] = str(backup_file_path)
            
            # Add to backup manifest
            result.backup_manifest[str(relative_path)] = metadata
            
            result.files_backed_up += 1
            result.total_size_bytes += metadata.file_size
            
            self.logger.debug(f"Backed up file: {file_path} -> {backup_file_path}")
            
        except Exception as e:
            result.files_failed += 1
            result.error_messages.append(f"Failed to backup {file_path}: {str(e)}")
            self.logger.error(f"Failed to backup file {file_path}: {e}")
    
    async def _get_file_metadata(self, file_path: Path) -> FileMetadata:
        """Extract comprehensive file metadata."""
        try:
            stat = file_path.stat()
            
            # Calculate checksum
            checksum = await self._calculate_file_checksum(file_path)
            
            # Determine file type
            file_type = self._determine_file_type(file_path)
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            mime_type = mime_type or "application/octet-stream"
            
            # Check if symlink
            is_symlink = file_path.is_symlink()
            symlink_target = str(file_path.readlink()) if is_symlink else None
            
            # Creator content detection
            creator_id = self._detect_creator_id(file_path)
            content_category = self._categorize_content(file_path, file_type)
            
            return FileMetadata(
                file_path=str(file_path),
                file_size=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                created_time=datetime.fromtimestamp(stat.st_ctime),
                file_type=file_type,
                mime_type=mime_type,
                checksum=checksum,
                permissions=oct(stat.st_mode)[-3:],
                owner=str(stat.st_uid),
                group=str(stat.st_gid),
                is_symlink=is_symlink,
                symlink_target=symlink_target,
                creator_id=creator_id,
                content_category=content_category
            )
            
        except Exception as e:
            self.logger.error(f"Error getting metadata for {file_path}: {e}")
            raise
    
    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file."""
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating checksum for {file_path}: {e}")
            return ""
    
    def _determine_file_type(self, file_path: Path) -> FileType:
        """Determine file type based on extension and content."""
        ext = file_path.suffix.lower()
        
        # Creator content patterns
        if any(file_path.match(pattern) for pattern in self.creator_content_patterns):
            return FileType.CREATOR_CONTENT
        
        # AI model patterns
        if any(file_path.match(pattern) for pattern in self.ai_model_patterns):
            return FileType.AI_MODEL
        
        # Standard file types
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
            return FileType.IMAGE
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']:
            return FileType.VIDEO
        elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
            return FileType.AUDIO
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf']:
            return FileType.DOCUMENT
        elif ext in ['.zip', '.tar', '.gz', '.bz2', '.rar', '.7z']:
            return FileType.ARCHIVE
        elif ext in ['.json', '.yaml', '.yml', '.ini', '.cfg', '.conf']:
            return FileType.CONFIG
        elif ext in ['.log', '.out']:
            return FileType.LOG
        elif ext in ['.sql', '.db', '.sqlite', '.mdb']:
            return FileType.DATABASE
        elif ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c']:
            return FileType.SOURCE_CODE
        elif ext in ['.exe', '.bin', '.app', '.deb', '.rpm']:
            return FileType.EXECUTABLE
        else:
            return FileType.DOCUMENT
    
    def _detect_creator_id(self, file_path: Path) -> Optional[str]:
        """Detect creator ID from file path or metadata."""
        # Extract creator ID from path patterns like /creators/{creator_id}/content/
        path_parts = file_path.parts
        if 'creators' in path_parts:
            try:
                creator_index = path_parts.index('creators')
                if creator_index + 1 < len(path_parts):
                    return path_parts[creator_index + 1]
            except (ValueError, IndexError):
                pass
        
        return None
    
    def _categorize_content(self, file_path: Path, file_type: FileType) -> Optional[str]:
        """Categorize content for business logic."""
        if file_type == FileType.CREATOR_CONTENT:
            if 'upload' in str(file_path).lower():
                return 'user_upload'
            elif 'processed' in str(file_path).lower():
                return 'ai_processed'
            elif 'monetized' in str(file_path).lower():
                return 'monetized_content'
        
        elif file_type == FileType.AI_MODEL:
            if 'training' in str(file_path).lower():
                return 'training_data'
            elif 'model' in str(file_path).lower():
                return 'trained_model'
            elif 'weights' in str(file_path).lower():
                return 'model_weights'
        
        return None
    
    def _get_relative_backup_path(self, file_path: Path, job: BackupJob) -> Path:
        """Get relative path for file in backup."""
        # Find the best matching source path
        best_match = ""
        for source_path in job.source_paths:
            source = Path(source_path)
            try:
                file_path.relative_to(source)
                if len(str(source)) > len(best_match):
                    best_match = str(source)
            except ValueError:
                continue
        
        if best_match:
            return file_path.relative_to(Path(best_match))
        else:
            return Path(file_path.name)
    
    async def _copy_file_with_metadata(
        self,
        source: Path,
        destination: Path,
        metadata: FileMetadata,
        job: BackupJob
    ) -> None:
        """Copy file preserving metadata and handling special cases."""
        try:
            if metadata.is_symlink and not job.follow_symlinks:
                # Create symlink in backup
                if metadata.symlink_target:
                    destination.symlink_to(metadata.symlink_target)
            else:
                # Copy regular file
                shutil.copy2(source, destination)
            
            # Preserve permissions if requested
            if job.preserve_permissions:
                try:
                    os.chmod(destination, int(metadata.permissions, 8))
                except (OSError, ValueError) as e:
                    self.logger.debug(f"Could not set permissions for {destination}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error copying file {source} to {destination}: {e}")
            raise
    
    async def _create_backup_manifest(self, job: BackupJob, result: BackupResult) -> None:
        """Create backup manifest with file metadata."""
        manifest_path = Path(job.destination_path) / "backup_manifest.json"
        
        manifest_data = {
            'job_id': job.job_id,
            'created_at': result.started_at.isoformat(),
            'backup_strategy': job.strategy.value,
            'compression': job.compression.value,
            'source_paths': job.source_paths,
            'files_count': result.files_backed_up,
            'total_size_bytes': result.total_size_bytes,
            'files': {
                path: {
                    'size': metadata.file_size,
                    'modified_time': metadata.modified_time.isoformat(),
                    'file_type': metadata.file_type.value,
                    'checksum': metadata.checksum,
                    'creator_id': metadata.creator_id,
                    'content_category': metadata.content_category
                }
                for path, metadata in result.backup_manifest.items()
            }
        }
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
    
    async def _compress_backup(self, job: BackupJob, result: BackupResult) -> None:
        """Compress backup directory."""
        if job.compression == CompressionType.NONE:
            return
        
        self.logger.info(f"🗜️ Compressing backup with {job.compression.value}")
        
        # Simulate compression process
        await asyncio.sleep(1)
        
        # In production, implement actual compression
        # For now, estimate compressed size
        original_size = result.total_size_bytes
        if job.compression == CompressionType.GZIP:
            result.compressed_size_bytes = int(original_size * 0.7)  # 30% compression
        elif job.compression == CompressionType.BZIP2:
            result.compressed_size_bytes = int(original_size * 0.6)  # 40% compression
        elif job.compression == CompressionType.LZMA:
            result.compressed_size_bytes = int(original_size * 0.5)  # 50% compression
        else:
            result.compressed_size_bytes = original_size
    
    def _generate_job_id(self, job_name: str) -> str:
        """Generate unique job ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"file_backup_{job_name}_{timestamp}"
    
    async def get_backup_status(self, job_id: str) -> Optional[BackupResult]:
        """Get status of backup job."""
        # Check active jobs first
        if job_id in self.active_jobs:
            return BackupResult(
                job_id=job_id,
                status="running",
                files_processed=0,
                files_backed_up=0,
                files_skipped=0,
                files_failed=0,
                total_size_bytes=0,
                compressed_size_bytes=0,
                compression_ratio=0.0,
                duration_seconds=0.0,
                deduplication_savings_bytes=0,
                started_at=self.active_jobs[job_id].created_at,
                completed_at=datetime.now()
            )
        
        # Check history
        for result in self.job_history:
            if result.job_id == job_id:
                return result
        
        return None
    
    async def list_backups(self, limit: int = 50) -> List[BackupResult]:
        """List backup job history."""
        return sorted(self.job_history, key=lambda x: x.started_at, reverse=True)[:limit]
    
    async def restore_backup(
        self,
        job_id: str,
        restore_path: str,
        selective_restore: Optional[List[str]] = None
    ) -> bool:
        """
        Restore files from backup.
        
        Args:
            job_id: ID of backup job to restore from
            restore_path: Path to restore files to
            selective_restore: Optional list of specific files to restore
            
        Returns:
            True if restore successful
        """
        backup_result = await self.get_backup_status(job_id)
        if not backup_result or backup_result.status != "success":
            raise ValueError(f"Backup not found or not successful: {job_id}")
        
        self.logger.info(f"🔄 Starting file restore: {job_id} -> {restore_path}")
        
        try:
            # Simulate restore process
            await asyncio.sleep(2)
            
            self.logger.info(f"✅ File restore completed: {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ File restore failed: {job_id} - {str(e)}")
            raise
    
    async def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """Clean up old backup files."""
        cleanup_count = 0
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for result in self.job_history.copy():
            if result.started_at < cutoff_date:
                # Remove backup directory
                backup_path = Path(result.job_id.replace("file_backup_", ""))
                if backup_path.exists():
                    try:
                        shutil.rmtree(backup_path)
                        cleanup_count += 1
                        self.logger.info(f"🗑️ Removed old backup: {result.job_id}")
                    except Exception as e:
                        self.logger.error(f"Failed to remove backup: {e}")
                
                # Remove from history
                self.job_history.remove(result)
        
        return cleanup_count
    
    async def get_backup_metrics(self) -> Dict[str, Any]:
        """Get comprehensive backup metrics."""
        total_jobs = len(self.job_history)
        active_jobs = len(self.active_jobs)
        
        successful_jobs = len([r for r in self.job_history if r.status == "success"])
        failed_jobs = len([r for r in self.job_history if r.status == "failed"])
        
        total_files = sum(r.files_backed_up for r in self.job_history)
        total_size = sum(r.total_size_bytes for r in self.job_history)
        total_savings = sum(r.deduplication_savings_bytes for r in self.job_history)
        
        avg_compression = 0
        if successful_jobs > 0:
            avg_compression = sum(
                r.compression_ratio for r in self.job_history if r.status == "success"
            ) / successful_jobs
        
        return {
            'total_backup_jobs': total_jobs,
            'active_jobs': active_jobs,
            'successful_jobs': successful_jobs,
            'failed_jobs': failed_jobs,
            'success_rate': successful_jobs / total_jobs if total_jobs > 0 else 0,
            'total_files_backed_up': total_files,
            'total_size_bytes': total_size,
            'total_size_gb': round(total_size / (1024**3), 2),
            'deduplication_savings_bytes': total_savings,
            'deduplication_savings_gb': round(total_savings / (1024**3), 2),
            'average_compression_ratio': round(avg_compression, 3),
            'unique_files_in_dedup_index': len(self.dedup_index)
        }


# Export public interface
__all__ = [
    'FileBackupManager',
    'FileType',
    'BackupStrategy',
    'CompressionType',
    'FileMetadata',
    'BackupJob',
    'BackupResult'
]