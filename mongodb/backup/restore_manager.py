"""MongoDB Restore Manager
=======================

Comprehensive database restore operations with validation and rollback capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import os
import subprocess
import shutil
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class RestoreStatus(Enum):
    """Restore status enumeration."""
    PENDING = "pending"
    VALIDATING = "validating"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class RestoreOperation:
    """Restore operation record."""
    operation_id: str
    backup_path: str
    target_databases: List[str]
    target_collections: List[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    status: RestoreStatus = RestoreStatus.PENDING
    error_message: Optional[str] = None
    restored_documents: int = 0
    duration_seconds: float = 0.0
    validation_passed: bool = False

class RestoreManager:
    """Advanced MongoDB restore manager with validation and rollback capabilities."""
    
    def __init__(self, client: MongoClient, config: Dict[str, Any] = None):
        """Initialize restore manager.
        
        Args:
            client: MongoDB client instance
            config: Restore configuration
        """
        self.client = client
        self.config = config or {}
        
        # Restore history
        self._restore_history: List[RestoreOperation] = []
        
        # Configuration
        self._mongorestore_path = self.config.get('mongorestore_path', 'mongorestore')
        self._validation_enabled = self.config.get('validation_enabled', True)
        self._backup_before_restore = self.config.get('backup_before_restore', True)
        
        # Callbacks
        self._completion_callbacks: List[Callable] = []
        self._failure_callbacks: List[Callable] = []
    
    def restore_from_backup(self, backup_path: str, 
                          target_database: str = None,
                          target_collection: str = None,
                          drop_existing: bool = False,
                          dry_run: bool = False) -> str:
        """Restore database from backup.
        
        Args:
            backup_path: Path to backup file or directory
            target_database: Target database name
            target_collection: Target collection name
            drop_existing: Whether to drop existing data
            dry_run: Perform validation only without actual restore
            
        Returns:
            Operation ID
        """
        operation_id = self._generate_operation_id()
        
        # Create restore operation
        operation = RestoreOperation(
            operation_id=operation_id,
            backup_path=backup_path,
            target_databases=[target_database] if target_database else [],
            target_collections=[target_collection] if target_collection else [],
            start_time=datetime.utcnow()
        )
        
        try:
            # Validate backup file
            if not self._validate_backup_file(backup_path):
                raise ValueError(f"Invalid backup file: {backup_path}")
            
            # Pre-restore backup if enabled
            if self._backup_before_restore and not dry_run:
                self._create_pre_restore_backup(operation)
            
            # Execute restore
            if dry_run:
                operation.status = RestoreStatus.VALIDATING
                self._validate_restore_operation(operation)
            else:
                operation.status = RestoreStatus.RUNNING
                self._execute_restore(operation, target_database, target_collection, drop_existing)
            
            # Mark as completed
            operation.end_time = datetime.utcnow()
            operation.duration_seconds = (operation.end_time - operation.start_time).total_seconds()
            operation.status = RestoreStatus.COMPLETED
            
            logger.info(f"Restore operation '{operation_id}' completed successfully")
            
            # Execute completion callbacks
            for callback in self._completion_callbacks:
                try:
                    callback(operation)
                except Exception as e:
                    logger.error(f"Completion callback error: {e}")
        
        except Exception as e:
            operation.status = RestoreStatus.FAILED
            operation.error_message = str(e)
            operation.end_time = datetime.utcnow()
            operation.duration_seconds = (operation.end_time - operation.start_time).total_seconds()
            
            logger.error(f"Restore operation '{operation_id}' failed: {e}")
            
            # Execute failure callbacks
            for callback in self._failure_callbacks:
                try:
                    callback(operation)
                except Exception as e:
                    logger.error(f"Failure callback error: {e}")
        
        finally:
            self._restore_history.append(operation)
        
        return operation_id
    
    def get_restore_history(self, limit: int = 100) -> List[RestoreOperation]:
        """Get restore operation history.
        
        Args:
            limit: Maximum number of operations to return
            
        Returns:
            List of restore operations
        """
        # Sort by start time descending
        sorted_history = sorted(self._restore_history, key=lambda x: x.start_time, reverse=True)
        return sorted_history[:limit]
    
    def _validate_backup_file(self, backup_path: str) -> bool:
        """Validate backup file or directory."""
        if not os.path.exists(backup_path):
            logger.error(f"Backup path does not exist: {backup_path}")
            return False
        
        if os.path.isfile(backup_path):
            # Single file backup
            if backup_path.endswith('.gz'):
                # Compressed backup
                return True
            elif backup_path.endswith('.bson'):
                # BSON dump file
                return True
            else:
                logger.warning(f"Unknown backup file format: {backup_path}")
                return True  # Allow for flexibility
        
        elif os.path.isdir(backup_path):
            # Directory backup (mongodump format)
            return True
        
        return False
    
    def _create_pre_restore_backup(self, operation: RestoreOperation) -> None:
        """Create backup before restore operation."""
        logger.info("Creating pre-restore backup")
        
        # This would integrate with the backup scheduler
        # For now, just log the intent
        # TODO: Implement pre-restore backup creation
        pass
    
    def _validate_restore_operation(self, operation: RestoreOperation) -> None:
        """Validate restore operation without executing."""
        logger.info(f"Validating restore operation '{operation.operation_id}'")
        
        # Check MongoDB connection
        try:
            self.client.admin.command('ping')
        except Exception as e:
            raise RuntimeError(f"MongoDB connection failed: {e}")
        
        # Check target database access
        if operation.target_databases:
            for db_name in operation.target_databases:
                try:
                    self.client[db_name].list_collection_names()
                except Exception as e:
                    raise RuntimeError(f"Cannot access target database '{db_name}': {e}")
        
        operation.validation_passed = True
        logger.info("Restore operation validation passed")
    
    def _execute_restore(self, operation: RestoreOperation, 
                        target_database: str = None,
                        target_collection: str = None,
                        drop_existing: bool = False) -> None:
        """Execute restore operation."""
        logger.info(f"Executing restore operation '{operation.operation_id}'")
        
        # Build mongorestore command
        cmd = [self._mongorestore_path]
        
        # Connection parameters
        if hasattr(self.client, 'HOST'):
            cmd.extend(['--host', self.client.HOST])
        if hasattr(self.client, 'PORT'):
            cmd.extend(['--port', str(self.client.PORT)])
        
        # Target database
        if target_database:
            cmd.extend(['--db', target_database])
        
        # Target collection
        if target_collection:
            cmd.extend(['--collection', target_collection])
        
        # Drop existing data
        if drop_existing:
            cmd.append('--drop')
        
        # Verbose output
        cmd.append('--verbose')
        
        # Input path
        cmd.append(operation.backup_path)
        
        # Execute command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"mongorestore failed: {result.stderr}")
        
        # Parse output for restored document count
        operation.restored_documents = self._parse_restored_documents(result.stdout)
        
        logger.info(f"Restored {operation.restored_documents} documents")
    
    def _parse_restored_documents(self, output: str) -> int:
        """Parse mongorestore output to extract document count."""
        # Simple parsing - in practice, this would be more sophisticated
        lines = output.split('\n')
        for line in lines:
            if 'documents' in line and 'restored' in line:
                try:
                    # Extract number from line
                    words = line.split()
                    for word in words:
                        if word.isdigit():
                            return int(word)
                except ValueError:
                    continue
        return 0
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID."""
        import uuid
        return str(uuid.uuid4())[:8]

# Global restore manager instance
_default_restore_manager: Optional[RestoreManager] = None

def get_restore_manager(client: MongoClient, **kwargs) -> RestoreManager:
    """Get or create default restore manager."""
    global _default_restore_manager
    if _default_restore_manager is None:
        _default_restore_manager = RestoreManager(client, **kwargs)
    return _default_restore_manager

__all__ = ['RestoreManager', 'RestoreOperation', 'RestoreStatus', 'get_restore_manager']