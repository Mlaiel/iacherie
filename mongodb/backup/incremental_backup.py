"""MongoDB Incremental Backup
===========================

Efficient incremental backup implementation using oplog and change streams.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import OperationFailure

logger = logging.getLogger(__name__)

@dataclass
class IncrementalBackupMetadata:
    """Incremental backup metadata."""
    backup_id: str
    timestamp: datetime
    last_oplog_time: Dict[str, Any]  # MongoDB timestamp
    collections_included: List[str]
    file_path: str
    file_size_bytes: int
    change_count: int

class IncrementalBackup:
    """Advanced incremental backup using MongoDB oplog and change streams."""
    
    def __init__(self, client: MongoClient, config: Dict[str, Any] = None):
        """Initialize incremental backup system.
        
        Args:
            client: MongoDB client instance
            config: Backup configuration
        """
        self.client = client
        self.config = config or {}
        
        # Configuration
        self._output_directory = self.config.get('output_directory', '/tmp/incremental_backups')
        self._metadata_file = os.path.join(self._output_directory, 'metadata.json')
        
        # Create output directory
        os.makedirs(self._output_directory, exist_ok=True)
        
        # Load existing metadata
        self._metadata: Dict[str, IncrementalBackupMetadata] = self._load_metadata()
        
        # Track last backup timestamp
        self._last_backup_timestamp = self._get_last_backup_timestamp()
    
    def create_incremental_backup(self, databases: List[str] = None,
                                 collections: List[str] = None) -> str:
        """Create incremental backup.
        
        Args:
            databases: List of databases to backup
            collections: List of collections to backup
            
        Returns:
            Backup ID
        """
        backup_id = self._generate_backup_id()
        logger.info(f"Starting incremental backup '{backup_id}'")
        
        try:
            # Get current oplog position
            current_oplog_time = self._get_current_oplog_time()
            
            # Query oplog for changes since last backup
            changes = self._get_oplog_changes(
                self._last_backup_timestamp,
                current_oplog_time,
                databases,
                collections
            )
            
            # Create backup file
            backup_file = os.path.join(self._output_directory, f"incremental_{backup_id}.json")
            file_size = self._write_changes_to_file(changes, backup_file)
            
            # Create metadata
            metadata = IncrementalBackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.utcnow(),
                last_oplog_time=current_oplog_time,
                collections_included=collections or [],
                file_path=backup_file,
                file_size_bytes=file_size,
                change_count=len(changes)
            )
            
            # Save metadata
            self._metadata[backup_id] = metadata
            self._save_metadata()
            
            # Update last backup timestamp
            self._last_backup_timestamp = current_oplog_time
            
            logger.info(f"Incremental backup '{backup_id}' completed with {len(changes)} changes")
            return backup_id
            
        except Exception as e:
            logger.error(f"Incremental backup '{backup_id}' failed: {e}")
            raise
    
    def restore_incremental_backup(self, backup_id: str, target_time: datetime = None) -> bool:
        """Restore from incremental backup.
        
        Args:
            backup_id: Backup ID to restore
            target_time: Point in time to restore to
            
        Returns:
            True if restore successful
        """
        if backup_id not in self._metadata:
            raise ValueError(f"Backup '{backup_id}' not found")
        
        metadata = self._metadata[backup_id]
        logger.info(f"Restoring incremental backup '{backup_id}'")
        
        try:
            # Load changes from backup file
            changes = self._load_changes_from_file(metadata.file_path)
            
            # Filter changes by target time if specified
            if target_time:
                changes = [
                    change for change in changes
                    if self._extract_timestamp_from_change(change) <= target_time
                ]
            
            # Apply changes to database
            self._apply_changes_to_database(changes)
            
            logger.info(f"Successfully restored {len(changes)} changes from backup '{backup_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore incremental backup '{backup_id}': {e}")
            return False
    
    def get_backup_list(self) -> List[IncrementalBackupMetadata]:
        """Get list of all incremental backups.
        
        Returns:
            List of backup metadata
        """
        return list(self._metadata.values())
    
    def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """Clean up old incremental backups.
        
        Args:
            retention_days: Number of days to retain backups
            
        Returns:
            Number of backups cleaned up
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        cleaned_count = 0
        
        backups_to_remove = []
        for backup_id, metadata in self._metadata.items():
            if metadata.timestamp < cutoff_date:
                backups_to_remove.append(backup_id)
        
        for backup_id in backups_to_remove:
            metadata = self._metadata[backup_id]
            
            # Remove backup file
            try:
                if os.path.exists(metadata.file_path):
                    os.remove(metadata.file_path)
                
                # Remove from metadata
                del self._metadata[backup_id]
                cleaned_count += 1
                
                logger.info(f"Cleaned up old backup '{backup_id}'")
                
            except Exception as e:
                logger.error(f"Failed to clean up backup '{backup_id}': {e}")
        
        # Save updated metadata
        if cleaned_count > 0:
            self._save_metadata()
        
        logger.info(f"Cleaned up {cleaned_count} old incremental backups")
        return cleaned_count
    
    def _get_current_oplog_time(self) -> Dict[str, Any]:
        """Get current oplog timestamp."""
        try:
            # Get the most recent oplog entry
            oplog = self.client.local.oplog.rs.find().sort([('ts', -1)]).limit(1)
            entry = next(oplog)
            return entry['ts'].__dict__
        except Exception as e:
            logger.warning(f"Could not get oplog timestamp: {e}")
            # Fallback to current time
            return {'time': int(datetime.utcnow().timestamp()), 'inc': 1}
    
    def _get_oplog_changes(self, start_time: Dict[str, Any], end_time: Dict[str, Any],
                          databases: List[str] = None, collections: List[str] = None) -> List[Dict[str, Any]]:
        """Get oplog changes between timestamps."""
        changes = []
        
        try:
            # Build query for oplog
            query = {}
            
            # Time range filter
            if start_time:
                query['ts'] = {'$gt': start_time}
            if end_time:
                if 'ts' in query:
                    query['ts']['$lte'] = end_time
                else:
                    query['ts'] = {'$lte': end_time}
            
            # Database/collection filter
            if databases or collections:
                ns_conditions = []
                
                if databases:
                    for db in databases:
                        ns_conditions.append({'ns': {'$regex': f'^{db}\\.'}})
                
                if collections:
                    for collection in collections:
                        ns_conditions.append({'ns': collection})
                
                if ns_conditions:
                    query['$or'] = ns_conditions
            
            # Query oplog
            oplog_cursor = self.client.local.oplog.rs.find(query).sort([('ts', 1)])
            
            for entry in oplog_cursor:
                # Convert BSON to JSON-serializable format
                change = self._serialize_oplog_entry(entry)
                changes.append(change)
            
            logger.debug(f"Found {len(changes)} changes in oplog")
            
        except Exception as e:
            logger.error(f"Failed to query oplog: {e}")
            # Fallback: return empty changes
            changes = []
        
        return changes
    
    def _serialize_oplog_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize oplog entry for JSON storage."""
        serialized = {}
        
        for key, value in entry.items():
            if key == 'ts':
                # Convert timestamp to serializable format
                serialized[key] = {'time': value.time, 'inc': value.inc}
            elif hasattr(value, 'to_dict'):
                serialized[key] = value.to_dict()
            else:
                try:
                    json.dumps(value)  # Test if JSON serializable
                    serialized[key] = value
                except (TypeError, ValueError):
                    serialized[key] = str(value)
        
        return serialized
    
    def _write_changes_to_file(self, changes: List[Dict[str, Any]], file_path: str) -> int:
        """Write changes to backup file."""
        with open(file_path, 'w') as f:
            json.dump(changes, f, indent=2, default=str)
        
        return os.path.getsize(file_path)
    
    def _load_changes_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load changes from backup file."""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _apply_changes_to_database(self, changes: List[Dict[str, Any]]) -> None:
        """Apply changes to database."""
        logger.info(f"Applying {len(changes)} changes to database")
        
        for change in changes:
            try:
                self._apply_single_change(change)
            except Exception as e:
                logger.error(f"Failed to apply change {change.get('ts', 'unknown')}: {e}")
    
    def _apply_single_change(self, change: Dict[str, Any]) -> None:
        """Apply single oplog change to database."""
        op_type = change.get('op')
        namespace = change.get('ns', '')
        
        if not namespace or '.' not in namespace:
            return  # Skip invalid namespace
        
        db_name, collection_name = namespace.split('.', 1)
        collection = self.client[db_name][collection_name]
        
        if op_type == 'i':  # Insert
            doc = change.get('o')
            if doc:
                collection.insert_one(doc)
        
        elif op_type == 'u':  # Update
            filter_doc = change.get('o2')
            update_doc = change.get('o')
            if filter_doc and update_doc:
                collection.replace_one(filter_doc, update_doc, upsert=True)
        
        elif op_type == 'd':  # Delete
            filter_doc = change.get('o')
            if filter_doc:
                collection.delete_one(filter_doc)
        
        elif op_type == 'c':  # Command
            # Handle database commands
            command = change.get('o')
            if command:
                self.client[db_name].command(command)
    
    def _extract_timestamp_from_change(self, change: Dict[str, Any]) -> datetime:
        """Extract timestamp from oplog change."""
        ts = change.get('ts', {})
        if isinstance(ts, dict) and 'time' in ts:
            return datetime.fromtimestamp(ts['time'])
        return datetime.utcnow()
    
    def _get_last_backup_timestamp(self) -> Optional[Dict[str, Any]]:
        """Get timestamp of last backup."""
        if not self._metadata:
            return None
        
        # Find most recent backup
        latest_backup = max(
            self._metadata.values(),
            key=lambda m: m.timestamp,
            default=None
        )
        
        return latest_backup.last_oplog_time if latest_backup else None
    
    def _load_metadata(self) -> Dict[str, IncrementalBackupMetadata]:
        """Load metadata from file."""
        if not os.path.exists(self._metadata_file):
            return {}
        
        try:
            with open(self._metadata_file, 'r') as f:
                data = json.load(f)
            
            metadata = {}
            for backup_id, metadata_dict in data.items():
                # Convert timestamp string back to datetime
                metadata_dict['timestamp'] = datetime.fromisoformat(metadata_dict['timestamp'])
                metadata[backup_id] = IncrementalBackupMetadata(**metadata_dict)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return {}
    
    def _save_metadata(self) -> None:
        """Save metadata to file."""
        try:
            # Convert metadata to serializable format
            data = {}
            for backup_id, metadata in self._metadata.items():
                metadata_dict = asdict(metadata)
                metadata_dict['timestamp'] = metadata.timestamp.isoformat()
                data[backup_id] = metadata_dict
            
            with open(self._metadata_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _generate_backup_id(self) -> str:
        """Generate unique backup ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        import uuid
        return f"inc_{timestamp}_{str(uuid.uuid4())[:8]}"

# Global incremental backup instance
_default_incremental_backup: Optional[IncrementalBackup] = None

def get_incremental_backup(client: MongoClient, **kwargs) -> IncrementalBackup:
    """Get or create default incremental backup instance."""
    global _default_incremental_backup
    if _default_incremental_backup is None:
        _default_incremental_backup = IncrementalBackup(client, **kwargs)
    return _default_incremental_backup

__all__ = ['IncrementalBackup', 'IncrementalBackupMetadata', 'get_incremental_backup']