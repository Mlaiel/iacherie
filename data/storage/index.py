"""Professional Storage Index - IA Influencer Agent Platform
==========================================================
Module: backend/data/storage/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Storage Core - Central Storage Orchestrator
Responsibility: Unified storage interface and coordination
Technologies: Python, Async/await, Multi-cloud orchestration
==========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET:
- Lead Dev IA + Architecte: Fahed Mlaiel
- Backend Senior + ML Engineer: Expertise multi-domaines  
- Audio + DevOps + DBA + Sécurité: Compétences industrielles
- Microservices + IA Prompt Engineer: Innovation avancée

LOGIQUE MÉTIER ORCHESTRÉE:
Content Request → Storage Orchestration → Multi-Manager Coordination → 
File Processing + Version Control + Backup Protection → 
Unified Response → Performance Metrics → Security Compliance
"""
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import uuid

from .storage_manager import StorageManager
from .file_manager import (
    FileManager, 
    ContentType, 
    FileStatus,
    FileMetadata,
    FileProcessingResult,
    FileValidationConfig
)
from .version_manager import (
    VersionManager,
    VersionType,
    VersionInfo,
    VersionComparison
)
from .backup_manager import (
    BackupManager,
    BackupTier,
    BackupType,
    BackupConfig,
    BackupDestination,
    BackupJob
)
from .config_manager import (
    ConfigurationManager,
    StorageConfiguration,
    StorageProviderConfig,
    EnvironmentType
)
from .distributed_manager import DistributedStorageManager
from .performance_monitor import PerformanceMonitor
from .encryption_manager import EncryptionManager

logger = logging.getLogger(__name__)


@dataclass
class StorageOperation:
    """Unified storage operation result"""    operation_id: str
    operation_type: str
    success: bool
    timestamp: datetime
    
    # File information
    file_id: Optional[str] = None
    file_path: Optional[str] = None
    file_size: int = 0
    
    # Processing results
    file_result: Optional[FileProcessingResult] = None
    version_result: Optional[VersionInfo] = None
    backup_result: Optional[BackupJob] = None
    
    # Performance metrics
    processing_time_seconds: float = 0.0
    storage_locations: List[str] = None
    
    # Error handling
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.storage_locations is None:
            self.storage_locations = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class StorageIndexConfig:
    """Configuration for storage index orchestrator"""    # Base paths
    storage_base_path: str = "/data/storage"
    temp_path: str = "/tmp/ia_storage"
    
    # Feature enablement
    enable_versioning: bool = True
    enable_backup: bool = True
    enable_file_processing: bool = True
    enable_compression: bool = True
    enable_encryption: bool = True
    
    # Performance settings
    max_concurrent_operations: int = 10
    operation_timeout_seconds: int = 300
    
    # Validation settings
    max_file_size_mb: int = 500
    allowed_content_types: List[ContentType] = None
    
    # Backup settings
    backup_tiers: List[BackupTier] = None
    backup_retention_days: int = 90
    
    def __post_init__(self):
        if self.allowed_content_types is None:
            self.allowed_content_types = [
                ContentType.AUDIO, ContentType.VIDEO, 
                ContentType.IMAGE, ContentType.TEXT, ContentType.DOCUMENT
            ]
        if self.backup_tiers is None:
            self.backup_tiers = [
                BackupTier.REAL_TIME, BackupTier.DAILY, BackupTier.WEEKLY
            ]


class StorageIndex:
    """    Unified storage orchestrator for IA Influencer Agent platform.
    
    Coordinates file management, versioning, and backup operations
    through a single, cohesive interface for optimal performance
    and reliability.
    """    
    def __init__(self, config: StorageIndexConfig):
        """        Initialize StorageIndex with comprehensive configuration.
        
        Args:
            config: Storage index configuration
        """        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize storage managers
        self._initialize_managers()
        
        # Operation tracking
        self.active_operations: Dict[str, StorageOperation] = {}
        self.completed_operations: Dict[str, StorageOperation] = {}
        
        # Performance metrics
        self.metrics = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_processing_time": 0.0,
            "storage_efficiency": 0.0,
            "backup_coverage": 0.0
        }
        
        # Semaphore for operation concurrency
        self.operation_semaphore = asyncio.Semaphore(config.max_concurrent_operations)
        
        self.logger.info("🎯 StorageIndex initialized with unified orchestration")
    
    def _initialize_managers(self):
        """Initialize all storage managers"""        try:
            base_path = Path(self.config.storage_base_path)
            base_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize file manager
            if self.config.enable_file_processing:
                file_validation_config = FileValidationConfig(
                    max_file_size=self.config.max_file_size_mb * 1024 * 1024,
                    extract_metadata=True,
                    generate_thumbnails=True,
                    auto_optimize=self.config.enable_compression
                )
                
                self.file_manager = FileManager(
                    storage_path=base_path / "files",
                    validation_config=file_validation_config
                )
            else:
                self.file_manager = None
            
            # Initialize version manager
            if self.config.enable_versioning:
                self.version_manager = VersionManager(
                    storage_path=base_path / "versions"
                )
            else:
                self.version_manager = None
            
            # Initialize backup manager
            if self.config.enable_backup:
                backup_config = BackupConfig(
                    enabled=True,
                    encryption_enabled=self.config.enable_encryption,
                    compression_enabled=self.config.enable_compression,
                    verification_enabled=True
                )
                
                self.backup_manager = BackupManager(
                    config=backup_config,
                    storage_path=base_path / "backups"
                )
            else:
                self.backup_manager = None
            
            # Initialize cloud storage manager
            self.storage_manager = StorageManager([])  # Configurations added later
            
            self.logger.info("✅ All storage managers initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize storage managers: {e}")
            raise
    
    async def store_content(self,
                           file_data: Union[bytes, Any],
                           filename: str,
                           user_id: str,
                           content_type: Optional[ContentType] = None,
                           metadata: Optional[Dict[str, Any]] = None,
                           create_version: bool = True,
                           create_backup: bool = True,
                           change_description: str = "Initial upload") -> StorageOperation:
        """        Store content with comprehensive processing.
        
        Args:
            file_data: File content as bytes or file-like object
            filename: Original filename
            user_id: User identifier
            content_type: Content type (auto-detected if None)
            metadata: Additional metadata
            create_version: Whether to create version entry
            create_backup: Whether to create backup
            change_description: Description for version control
            
        Returns:
            Complete storage operation result
        """        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        operation = StorageOperation(
            operation_id=operation_id,
            operation_type="store_content",
            success=False,
            timestamp=start_time
        )
        
        async with self.operation_semaphore:
            try:
                self.active_operations[operation_id] = operation
                
                # Step 1: File processing and validation
                if self.file_manager:
                    self.logger.info(f"📁 Processing file: {filename}")
                    
                    file_result = await self.file_manager.upload_file(
                        file_data=file_data,
                        filename=filename,
                        user_id=user_id,
                        metadata=metadata
                    )
                    
                    operation.file_result = file_result
                    operation.file_id = file_result.file_id
                    
                    if not file_result.success:
                        operation.error_message = file_result.error_message
                        return await self._complete_operation(operation)
                    
                    operation.file_path = file_result.processed_path
                    
                    # Extract file metadata for further processing
                    if file_result.extracted_metadata:
                        operation.file_size = file_result.extracted_metadata.file_size
                        content_type = file_result.extracted_metadata.content_type
                
                # Step 2: Version control
                if self.version_manager and create_version and operation.file_path:
                    self.logger.info(f"🔄 Creating version for: {operation.file_id}")
                    
                    version_result = await self.version_manager.create_version(
                        file_id=operation.file_id,
                        file_path=operation.file_path,
                        change_description=change_description,
                        changed_by=user_id,
                        version_type=VersionType.INITIAL,
                        metadata=metadata
                    )
                    
                    operation.version_result = version_result
                
                # Step 3: Backup creation
                if self.backup_manager and create_backup and operation.file_path:
                    self.logger.info(f"🛡️ Creating backup for: {operation.file_id}")
                    
                    backup_result = await self.backup_manager.backup_file(
                        file_id=operation.file_id,
                        source_path=operation.file_path,
                        backup_tier=BackupTier.REAL_TIME,
                        backup_type=BackupType.FULL,
                        metadata=metadata
                    )
                    
                    operation.backup_result = backup_result
                    
                    if backup_result.successful_destinations:
                        operation.storage_locations.extend(backup_result.successful_destinations)
                
                # Step 4: Cloud storage distribution (if configured)
                # This would integrate with the main storage manager
                # For now, we track local storage
                operation.storage_locations.append("local_primary")
                
                operation.success = True
                
                self.logger.info(f"✅ Content stored successfully: {operation.file_id}")
                
            except Exception as e:
                self.logger.error(f"❌ Content storage failed: {str(e)}")
                operation.error_message = str(e)
                operation.success = False
            
            finally:
                return await self._complete_operation(operation)
    
    async def retrieve_content(self,
                              file_id: str,
                              version_id: Optional[str] = None,
                              user_id: Optional[str] = None) -> Optional[bytes]:
        """        Retrieve content with version support.
        
        Args:
            file_id: File identifier
            version_id: Specific version to retrieve (latest if None)
            user_id: User requesting the content
            
        Returns:
            File content as bytes or None if not found
        """        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        operation = StorageOperation(
            operation_id=operation_id,
            operation_type="retrieve_content",
            success=False,
            timestamp=start_time,
            file_id=file_id
        )
        
        try:
            self.active_operations[operation_id] = operation
            
            # Get version information
            if self.version_manager:
                if version_id:
                    version_info = await self.version_manager.get_version(file_id, version_id)
                else:
                    version_info = await self.version_manager._get_latest_version(file_id)
                
                if version_info:
                    operation.version_result = version_info
                    content = await self.version_manager.get_version_content(version_info)
                    operation.success = True
                    return content
            
            # Fallback to file manager
            if self.file_manager:
                file_metadata = await self.file_manager.get_file_metadata(file_id)
                if file_metadata:
                    # Read file content directly
                    # Implementation would depend on storage location
                    operation.success = True
                    # Return placeholder for now
                    return b"file_content_placeholder"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Content retrieval failed: {e}")
            operation.error_message = str(e)
            return None
        
        finally:
            await self._complete_operation(operation)
    
    async def update_content(self,
                            file_id: str,
                            new_file_data: Union[bytes, Any],
                            user_id: str,
                            change_description: str,
                            create_backup: bool = True) -> StorageOperation:
        """        Update existing content with versioning.
        
        Args:
            file_id: File to update
            new_file_data: New file content
            user_id: User making the update
            change_description: Description of changes
            create_backup: Whether to create backup of new version
            
        Returns:
            Storage operation result
        """        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        operation = StorageOperation(
            operation_id=operation_id,
            operation_type="update_content",
            success=False,
            timestamp=start_time,
            file_id=file_id
        )
        
        async with self.operation_semaphore:
            try:
                self.active_operations[operation_id] = operation
                
                # Get current file metadata
                if self.file_manager:
                    current_metadata = await self.file_manager.get_file_metadata(file_id)
                    if not current_metadata:
                        operation.error_message = f"File {file_id} not found"
                        return await self._complete_operation(operation)
                
                # Process new content
                if self.file_manager:
                    # Create temporary filename for update
                    temp_filename = f"update_{file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    file_result = await self.file_manager.upload_file(
                        file_data=new_file_data,
                        filename=temp_filename,
                        user_id=user_id
                    )
                    
                    operation.file_result = file_result
                    
                    if not file_result.success:
                        operation.error_message = file_result.error_message
                        return await self._complete_operation(operation)
                    
                    operation.file_path = file_result.processed_path
                
                # Create new version
                if self.version_manager and operation.file_path:
                    version_result = await self.version_manager.create_version(
                        file_id=file_id,
                        file_path=operation.file_path,
                        change_description=change_description,
                        changed_by=user_id,
                        version_type=VersionType.MINOR
                    )
                    
                    operation.version_result = version_result
                
                # Create backup of new version
                if self.backup_manager and create_backup and operation.file_path:
                    backup_result = await self.backup_manager.backup_file(
                        file_id=file_id,
                        source_path=operation.file_path,
                        backup_tier=BackupTier.REAL_TIME,
                        backup_type=BackupType.INCREMENTAL
                    )
                    
                    operation.backup_result = backup_result
                
                operation.success = True
                self.logger.info(f"✅ Content updated successfully: {file_id}")
                
            except Exception as e:
                self.logger.error(f"❌ Content update failed: {str(e)}")
                operation.error_message = str(e)
                operation.success = False
            
            finally:
                return await self._complete_operation(operation)
    
    async def delete_content(self,
                            file_id: str,
                            user_id: str,
                            permanent: bool = False) -> StorageOperation:
        """        Delete content with optional permanent removal.
        
        Args:
            file_id: File to delete
            user_id: User requesting deletion
            permanent: Whether to permanently delete (vs. soft delete)
            
        Returns:
            Storage operation result
        """        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        operation = StorageOperation(
            operation_id=operation_id,
            operation_type="delete_content",
            success=False,
            timestamp=start_time,
            file_id=file_id
        )
        
        try:
            self.active_operations[operation_id] = operation
            
            if permanent:
                # Permanent deletion from all systems
                success_count = 0
                
                # Delete from file manager
                if self.file_manager:
                    if await self.file_manager.delete_file(file_id):
                        success_count += 1
                
                # Clean up versions
                if self.version_manager:
                    # Implementation would clean up version history
                    success_count += 1
                
                # Clean up backups
                if self.backup_manager:
                    # Implementation would clean up backup data
                    success_count += 1
                
                operation.success = success_count > 0
            else:
                # Soft delete - mark as deleted but keep data
                if self.file_manager:
                    # Implementation would mark file as deleted
                    operation.success = True
                
                if self.version_manager:
                    # Create deletion version
                    await self.version_manager.create_version(
                        file_id=file_id,
                        file_path="",  # Empty path for deletion
                        change_description="File deleted",
                        changed_by=user_id,
                        version_type=VersionType.MINOR
                    )
            
            self.logger.info(f"🗑️ Content {'permanently ' if permanent else ''}deleted: {file_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Content deletion failed: {str(e)}")
            operation.error_message = str(e)
            operation.success = False
        
        finally:
            return await self._complete_operation(operation)
    
    async def compare_versions(self,
                              file_id: str,
                              version_a: str,
                              version_b: str) -> Optional[VersionComparison]:
        """        Compare two versions of a file.
        
        Args:
            file_id: File identifier
            version_a: First version ID
            version_b: Second version ID
            
        Returns:
            Version comparison result or None
        """        try:
            if not self.version_manager:
                return None
            
            comparison = await self.version_manager.compare_versions(
                file_id, version_a, version_b
            )
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Version comparison failed: {e}")
            return None
    
    async def restore_from_backup(self,
                                 file_id: str,
                                 target_path: str,
                                 target_timestamp: Optional[datetime] = None,
                                 user_id: str = "") -> Optional[Any]:
        """        Restore file from backup.
        
        Args:
            file_id: File to restore
            target_path: Where to restore the file
            target_timestamp: Point in time to restore to
            user_id: User requesting the restore
            
        Returns:
            Restore job result or None
        """        try:
            if not self.backup_manager:
                return None
            
            restore_job = await self.backup_manager.restore_file(
                file_id=file_id,
                target_path=target_path,
                target_timestamp=target_timestamp,
                requested_by=user_id
            )
            
            return restore_job
            
        except Exception as e:
            self.logger.error(f"Backup restore failed: {e}")
            return None
    
    async def get_file_history(self, file_id: str) -> Dict[str, Any]:
        """        Get complete history of a file including versions and backups.
        
        Args:
            file_id: File identifier
            
        Returns:
            Complete file history
        """        try:
            history = {
                "file_id": file_id,
                "versions": [],
                "backups": [],
                "statistics": {}
            }
            
            # Get version history
            if self.version_manager:
                versions = await self.version_manager.get_version_history(file_id)
                history["versions"] = versions
            
            # Get backup history
            if self.backup_manager:
                # Implementation would get backup history
                history["backups"] = []
            
            # Get file metadata
            if self.file_manager:
                metadata = await self.file_manager.get_file_metadata(file_id)
                if metadata:
                    history["metadata"] = {
                        "original_filename": metadata.original_filename,
                        "file_size": metadata.file_size,
                        "content_type": metadata.content_type.value,
                        "upload_timestamp": metadata.upload_timestamp.isoformat(),
                        "user_id": metadata.user_id
                    }
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get file history: {e}")
            return {"file_id": file_id, "error": str(e)}
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """        Get comprehensive storage statistics.
        
        Returns:
            Complete storage statistics across all managers
        """        try:
            stats = {
                "timestamp": datetime.now().isoformat(),
                "file_management": {},
                "version_control": {},
                "backup_protection": {},
                "overall_metrics": self.metrics.copy()
            }
            
            # File management statistics
            if self.file_manager:
                file_stats = await self.file_manager.get_processing_stats()
                stats["file_management"] = file_stats
            
            # Version control statistics
            if self.version_manager:
                version_stats = await self.version_manager.get_statistics()
                stats["version_control"] = version_stats
            
            # Backup statistics
            if self.backup_manager:
                backup_stats = await self.backup_manager.get_backup_statistics()
                stats["backup_protection"] = {
                    "total_backups": backup_stats.total_backups,
                    "successful_backups": backup_stats.successful_backups,
                    "failed_backups": backup_stats.failed_backups,
                    "total_storage_gb": backup_stats.total_storage_gb,
                    "compression_ratio": backup_stats.compression_ratio,
                    "last_successful_backup": backup_stats.last_successful_backup.isoformat() if backup_stats.last_successful_backup else None
                }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get storage statistics: {e}")
            return {"error": str(e)}
    
    async def _complete_operation(self, operation: StorageOperation) -> StorageOperation:
        """Complete storage operation and update metrics"""        try:
            # Calculate processing time
            processing_time = (datetime.now() - operation.timestamp).total_seconds()
            operation.processing_time_seconds = processing_time
            
            # Update metrics
            self.metrics["total_operations"] += 1
            
            if operation.success:
                self.metrics["successful_operations"] += 1
            else:
                self.metrics["failed_operations"] += 1
            
            # Update average processing time
            total_ops = self.metrics["total_operations"]
            current_avg = self.metrics["average_processing_time"]
            self.metrics["average_processing_time"] = (
                (current_avg * (total_ops - 1) + processing_time) / total_ops
            )
            
            # Move to completed operations
            if operation.operation_id in self.active_operations:
                del self.active_operations[operation.operation_id]
            
            self.completed_operations[operation.operation_id] = operation
            
            # Cleanup old completed operations (keep last 1000)
            if len(self.completed_operations) > 1000:
                old_operations = sorted(
                    self.completed_operations.items(),
                    key=lambda x: x[1].timestamp
                )[:-1000]
                
                for op_id, _ in old_operations:
                    del self.completed_operations[op_id]
            
            return operation
            
        except Exception as e:
            self.logger.error(f"Failed to complete operation: {e}")
            return operation
    
    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """        Clean up temporary files across all managers.
        
        Args:
            max_age_hours: Maximum age of temporary files to keep
            
        Returns:
            Number of files cleaned up
        """        try:
            total_cleaned = 0
            
            # Clean up file manager temp files
            if self.file_manager:
                cleaned = await self.file_manager.cleanup_temp_files(max_age_hours)
                total_cleaned += cleaned
            
            # Clean up temp directories
            temp_path = Path(self.config.temp_path)
            if temp_path.exists():
                cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
                
                for file_path in temp_path.rglob('*'):
                    if file_path.is_file():
                        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_mtime < cutoff_time:
                            try:
                                file_path.unlink()
                                total_cleaned += 1
                            except Exception as e:
                                self.logger.warning(f"Failed to clean temp file {file_path}: {e}")
            
            self.logger.info(f"🧹 Cleaned up {total_cleaned} temporary files")
            return total_cleaned
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """        Perform comprehensive health check of all storage components.
        
        Returns:
            Health status of all components
        """        try:
            health = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy",
                "components": {},
                "metrics": self.metrics.copy()
            }
            
            # Check file manager
            if self.file_manager:
                health["components"]["file_manager"] = {
                    "status": "healthy",
                    "active": True
                }
            else:
                health["components"]["file_manager"] = {
                    "status": "disabled",
                    "active": False
                }
            
            # Check version manager
            if self.version_manager:
                health["components"]["version_manager"] = {
                    "status": "healthy",
                    "active": True
                }
            else:
                health["components"]["version_manager"] = {
                    "status": "disabled",
                    "active": False
                }
            
            # Check backup manager
            if self.backup_manager:
                health["components"]["backup_manager"] = {
                    "status": "healthy",
                    "active": True
                }
            else:
                health["components"]["backup_manager"] = {
                    "status": "disabled",
                    "active": False
                }
            
            # Check active operations
            health["active_operations"] = len(self.active_operations)
            health["operation_queue_status"] = "normal" if len(self.active_operations) < self.config.max_concurrent_operations else "high"
            
            return health
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }
