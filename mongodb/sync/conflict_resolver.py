"""MongoDB Conflict Resolver
=========================

Advanced data conflict resolution algorithms for MongoDB synchronization
in the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
import hashlib

from . import ConflictResolution, SyncEvent

logger = logging.getLogger(__name__)

class ConflictType(Enum):
    """Types of synchronization conflicts."""
    UPDATE_UPDATE = "update_update"  # Both sides updated same document
    UPDATE_DELETE = "update_delete"  # One side updated, other deleted
    DELETE_DELETE = "delete_delete"  # Both sides deleted (not really a conflict)
    INSERT_INSERT = "insert_insert"  # Both sides inserted with same ID
    SCHEMA_MISMATCH = "schema_mismatch"  # Document structure differences

@dataclass
class ConflictData:
    """Data representing a synchronization conflict."""
    conflict_id: str
    conflict_type: ConflictType
    collection: str
    document_id: Any
    source_document: Optional[Dict[str, Any]]
    target_document: Optional[Dict[str, Any]]
    source_timestamp: datetime
    target_timestamp: datetime
    detected_at: datetime
    resolution_strategy: ConflictResolution
    resolved: bool = False
    resolution_result: Optional[Dict[str, Any]] = None
    resolution_timestamp: Optional[datetime] = None

class ConflictResolver:
    """Enterprise-grade MongoDB conflict resolution system."""
    
    def __init__(self, default_strategy: ConflictResolution = ConflictResolution.LATEST_WINS):
        """Initialize conflict resolver."""
        self.default_strategy = default_strategy
        self.conflict_history: List[ConflictData] = []
        self.custom_resolvers: Dict[str, Callable] = {}
        self.collection_strategies: Dict[str, ConflictResolution] = {}
        
        # Conflict detection configuration
        self.enable_field_level_resolution = True
        self.timestamp_fields = ['updated_at', 'modified_at', 'timestamp']
        self.version_fields = ['version', '__v', '_version']
        
        # Statistics
        self.resolution_stats = {
            'total_conflicts': 0,
            'resolved_conflicts': 0,
            'manual_conflicts': 0,
            'auto_resolved': 0
        }
    
    def set_collection_strategy(self, collection: str, strategy: ConflictResolution):
        """Set conflict resolution strategy for a specific collection."""
        self.collection_strategies[collection] = strategy
        logger.info(f"Set conflict strategy for {collection}: {strategy.value}")
    
    def register_custom_resolver(self, conflict_type: str, resolver: Callable):
        """Register a custom conflict resolver function."""
        self.custom_resolvers[conflict_type] = resolver
        logger.info(f"Registered custom resolver for: {conflict_type}")
    
    def detect_conflict(self, 
                       source_event: SyncEvent, 
                       target_document: Optional[Dict[str, Any]]) -> Optional[ConflictData]:
        """Detect if there's a conflict between source event and target state."""
        try:
            # Extract document information
            source_doc = source_event.data.get('document', {})
            source_timestamp = source_event.timestamp
            
            # Determine conflict type
            conflict_type = self._determine_conflict_type(source_event, target_document)
            
            if conflict_type is None:
                return None  # No conflict detected
            
            # Get target timestamp
            target_timestamp = self._extract_timestamp(target_document) if target_document else datetime.min
            
            # Create conflict data
            conflict = ConflictData(
                conflict_id=self._generate_conflict_id(source_event, target_document),
                conflict_type=conflict_type,
                collection=source_event.collection,
                document_id=source_event.document_id,
                source_document=source_doc,
                target_document=target_document,
                source_timestamp=source_timestamp,
                target_timestamp=target_timestamp,
                detected_at=datetime.now(),
                resolution_strategy=self._get_resolution_strategy(source_event.collection)
            )
            
            self.conflict_history.append(conflict)
            self.resolution_stats['total_conflicts'] += 1
            
            logger.warning(f"Conflict detected: {conflict.conflict_id} ({conflict_type.value})")
            return conflict
            
        except Exception as e:
            logger.error(f"Error detecting conflict: {e}")
            return None
    
    def _determine_conflict_type(self, 
                                source_event: SyncEvent, 
                                target_document: Optional[Dict[str, Any]]) -> Optional[ConflictType]:
        """Determine the type of conflict."""
        operation = source_event.operation_type
        
        if operation == 'insert':
            if target_document is not None:
                return ConflictType.INSERT_INSERT
        
        elif operation == 'update':
            if target_document is None:
                # Target was deleted
                return ConflictType.UPDATE_DELETE
            else:
                # Check if target was also updated after our last sync
                if self._was_recently_modified(target_document):
                    return ConflictType.UPDATE_UPDATE
        
        elif operation == 'delete':
            if target_document is not None:
                # Target still exists, might have been updated
                if self._was_recently_modified(target_document):
                    return ConflictType.UPDATE_DELETE
        
        # Check for schema mismatches
        if (operation in ['insert', 'update'] and target_document and
            self._has_schema_mismatch(source_event.data.get('document', {}), target_document)):
            return ConflictType.SCHEMA_MISMATCH
        
        return None  # No conflict
    
    def _was_recently_modified(self, document: Dict[str, Any]) -> bool:
        """Check if document was recently modified."""
        # Look for timestamp fields
        for field in self.timestamp_fields:
            if field in document:
                timestamp = document[field]
                if isinstance(timestamp, datetime):
                    # Consider modifications within last hour as recent
                    time_diff = datetime.now() - timestamp
                    if time_diff.total_seconds() < 3600:  # 1 hour
                        return True
        
        # Check version fields
        for field in self.version_fields:
            if field in document:
                # If version field exists, assume it's managed and recent
                return True
        
        return False
    
    def _has_schema_mismatch(self, source_doc: Dict[str, Any], target_doc: Dict[str, Any]) -> bool:
        """Check if there's a schema mismatch between documents."""
        source_fields = set(source_doc.keys())
        target_fields = set(target_doc.keys())
        
        # Significant difference in fields (more than 50% different)
        common_fields = source_fields & target_fields
        all_fields = source_fields | target_fields
        
        if len(all_fields) > 0:
            similarity = len(common_fields) / len(all_fields)
            return similarity < 0.5
        
        return False
    
    def _extract_timestamp(self, document: Dict[str, Any]) -> datetime:
        """Extract timestamp from document."""
        # Try common timestamp fields
        for field in self.timestamp_fields:
            if field in document:
                timestamp = document[field]
                if isinstance(timestamp, datetime):
                    return timestamp
        
        # Use MongoDB ObjectId timestamp if available
        if '_id' in document:
            try:
                from bson import ObjectId
                if isinstance(document['_id'], ObjectId):
                    return document['_id'].generation_time
            except:
                pass
        
        # Default to epoch
        return datetime.min
    
    def _generate_conflict_id(self, 
                            source_event: SyncEvent, 
                            target_document: Optional[Dict[str, Any]]) -> str:
        """Generate unique conflict ID."""
        content = f"{source_event.collection}:{source_event.document_id}:{source_event.timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _get_resolution_strategy(self, collection: str) -> ConflictResolution:
        """Get resolution strategy for a collection."""
        return self.collection_strategies.get(collection, self.default_strategy)
    
    def resolve_conflict(self, conflict: ConflictData) -> Optional[Dict[str, Any]]:
        """Resolve a detected conflict."""
        try:
            strategy = conflict.resolution_strategy
            resolution_result = None
            
            # Check for custom resolver first
            custom_key = f"{conflict.collection}:{conflict.conflict_type.value}"
            if custom_key in self.custom_resolvers:
                resolution_result = self.custom_resolvers[custom_key](conflict)
            else:
                # Use built-in resolution strategies
                if strategy == ConflictResolution.LATEST_WINS:
                    resolution_result = self._resolve_latest_wins(conflict)
                elif strategy == ConflictResolution.SOURCE_WINS:
                    resolution_result = self._resolve_source_wins(conflict)
                elif strategy == ConflictResolution.TARGET_WINS:
                    resolution_result = self._resolve_target_wins(conflict)
                elif strategy == ConflictResolution.MERGE:
                    resolution_result = self._resolve_merge(conflict)
                elif strategy == ConflictResolution.MANUAL:
                    resolution_result = self._resolve_manual(conflict)
            
            # Update conflict data
            conflict.resolved = True
            conflict.resolution_result = resolution_result
            conflict.resolution_timestamp = datetime.now()
            
            # Update statistics
            self.resolution_stats['resolved_conflicts'] += 1
            if strategy == ConflictResolution.MANUAL:
                self.resolution_stats['manual_conflicts'] += 1
            else:
                self.resolution_stats['auto_resolved'] += 1
            
            logger.info(f"Resolved conflict {conflict.conflict_id} using {strategy.value}")
            return resolution_result
            
        except Exception as e:
            logger.error(f"Error resolving conflict {conflict.conflict_id}: {e}")
            return None
    
    def _resolve_latest_wins(self, conflict: ConflictData) -> Dict[str, Any]:
        """Resolve conflict by choosing the document with latest timestamp."""
        if conflict.source_timestamp > conflict.target_timestamp:
            return {
                'action': 'use_source',
                'document': conflict.source_document,
                'reason': f'Source timestamp {conflict.source_timestamp} > target timestamp {conflict.target_timestamp}'
            }
        else:
            return {
                'action': 'use_target',
                'document': conflict.target_document,
                'reason': f'Target timestamp {conflict.target_timestamp} >= source timestamp {conflict.source_timestamp}'
            }
    
    def _resolve_source_wins(self, conflict: ConflictData) -> Dict[str, Any]:
        """Resolve conflict by always choosing source document."""
        return {
            'action': 'use_source',
            'document': conflict.source_document,
            'reason': 'Source wins strategy'
        }
    
    def _resolve_target_wins(self, conflict: ConflictData) -> Dict[str, Any]:
        """Resolve conflict by always choosing target document."""
        return {
            'action': 'use_target',
            'document': conflict.target_document,
            'reason': 'Target wins strategy'
        }
    
    def _resolve_merge(self, conflict: ConflictData) -> Dict[str, Any]:
        """Resolve conflict by merging source and target documents."""
        if not conflict.source_document or not conflict.target_document:
            # Can't merge if one document is missing
            return self._resolve_latest_wins(conflict)
        
        merged_doc = self._merge_documents(
            conflict.source_document,
            conflict.target_document,
            conflict.source_timestamp,
            conflict.target_timestamp
        )
        
        return {
            'action': 'use_merged',
            'document': merged_doc,
            'reason': 'Merged source and target documents'
        }
    
    def _merge_documents(self, 
                        source_doc: Dict[str, Any], 
                        target_doc: Dict[str, Any],
                        source_timestamp: datetime,
                        target_timestamp: datetime) -> Dict[str, Any]:
        """Merge two documents intelligently."""
        if self.enable_field_level_resolution:
            return self._merge_field_level(source_doc, target_doc, source_timestamp, target_timestamp)
        else:
            return self._merge_simple(source_doc, target_doc)
    
    def _merge_field_level(self, 
                          source_doc: Dict[str, Any], 
                          target_doc: Dict[str, Any],
                          source_timestamp: datetime,
                          target_timestamp: datetime) -> Dict[str, Any]:
        """Merge documents at field level."""
        merged = {}
        
        # Get all fields from both documents
        all_fields = set(source_doc.keys()) | set(target_doc.keys())
        
        for field in all_fields:
            source_value = source_doc.get(field)
            target_value = target_doc.get(field)
            
            if source_value is None:
                # Field only in target
                merged[field] = target_value
            elif target_value is None:
                # Field only in source
                merged[field] = source_value
            elif source_value == target_value:
                # Same value in both
                merged[field] = source_value
            else:
                # Different values - choose based on timestamp or field priority
                if self._is_priority_field(field):
                    # Use latest timestamp for priority fields
                    merged[field] = source_value if source_timestamp > target_timestamp else target_value
                else:
                    # For non-priority fields, prefer source
                    merged[field] = source_value
        
        # Add merge metadata
        merged['_merged_at'] = datetime.now()
        merged['_merge_source'] = 'field_level_resolution'
        
        return merged
    
    def _merge_simple(self, source_doc: Dict[str, Any], target_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Simple document merge - target + source overrides."""
        merged = target_doc.copy()
        merged.update(source_doc)
        
        # Add merge metadata
        merged['_merged_at'] = datetime.now()
        merged['_merge_source'] = 'simple_merge'
        
        return merged
    
    def _is_priority_field(self, field: str) -> bool:
        """Check if field should be treated with priority during merge."""
        priority_fields = [
            'status', 'state', 'active', 'enabled',
            'price', 'amount', 'quantity', 'count',
            'email', 'phone', 'address'
        ]
        
        return any(priority in field.lower() for priority in priority_fields)
    
    def _resolve_manual(self, conflict: ConflictData) -> Dict[str, Any]:
        """Mark conflict for manual resolution."""
        return {
            'action': 'manual_required',
            'document': None,
            'reason': 'Manual resolution required',
            'conflict_data': {
                'source': conflict.source_document,
                'target': conflict.target_document,
                'source_timestamp': conflict.source_timestamp,
                'target_timestamp': conflict.target_timestamp
            }
        }
    
    def get_unresolved_conflicts(self, collection: Optional[str] = None) -> List[ConflictData]:
        """Get list of unresolved conflicts."""
        conflicts = [c for c in self.conflict_history if not c.resolved]
        
        if collection:
            conflicts = [c for c in conflicts if c.collection == collection]
        
        return conflicts
    
    def manually_resolve_conflict(self, 
                                conflict_id: str, 
                                resolution_document: Dict[str, Any]) -> bool:
        """Manually resolve a conflict."""
        for conflict in self.conflict_history:
            if conflict.conflict_id == conflict_id and not conflict.resolved:
                conflict.resolved = True
                conflict.resolution_result = {
                    'action': 'manual_resolution',
                    'document': resolution_document,
                    'reason': 'Manually resolved by user'
                }
                conflict.resolution_timestamp = datetime.now()
                
                self.resolution_stats['resolved_conflicts'] += 1
                self.resolution_stats['manual_conflicts'] += 1
                
                logger.info(f"Manually resolved conflict: {conflict_id}")
                return True
        
        return False
    
    def get_conflict_statistics(self) -> Dict[str, Any]:
        """Get conflict resolution statistics."""
        stats = self.resolution_stats.copy()
        
        # Add additional metrics
        if stats['total_conflicts'] > 0:
            stats['resolution_rate'] = stats['resolved_conflicts'] / stats['total_conflicts']
            stats['auto_resolution_rate'] = stats['auto_resolved'] / stats['total_conflicts']
        else:
            stats['resolution_rate'] = 0
            stats['auto_resolution_rate'] = 0
        
        # Conflict type distribution
        type_distribution = {}
        for conflict in self.conflict_history:
            conflict_type = conflict.conflict_type.value
            type_distribution[conflict_type] = type_distribution.get(conflict_type, 0) + 1
        
        stats['conflict_type_distribution'] = type_distribution
        
        # Recent conflicts (last 24 hours)
        recent_cutoff = datetime.now() - datetime.timedelta(days=1)
        recent_conflicts = [c for c in self.conflict_history if c.detected_at > recent_cutoff]
        stats['recent_conflicts_24h'] = len(recent_conflicts)
        
        return stats
    
    def export_conflict_report(self) -> str:
        """Export detailed conflict report."""
        report = {
            'generated_at': datetime.now(),
            'statistics': self.get_conflict_statistics(),
            'unresolved_conflicts': [
                {
                    'conflict_id': c.conflict_id,
                    'type': c.conflict_type.value,
                    'collection': c.collection,
                    'document_id': str(c.document_id),
                    'detected_at': c.detected_at,
                    'strategy': c.resolution_strategy.value
                }
                for c in self.get_unresolved_conflicts()
            ],
            'resolution_strategies': {
                collection: strategy.value 
                for collection, strategy in self.collection_strategies.items()
            },
            'default_strategy': self.default_strategy.value
        }
        
        return json.dumps(report, default=str, indent=2)
    
    def clear_resolved_conflicts(self, older_than_days: int = 30):
        """Clear resolved conflicts older than specified days."""
        cutoff_date = datetime.now() - datetime.timedelta(days=older_than_days)
        
        initial_count = len(self.conflict_history)
        self.conflict_history = [
            c for c in self.conflict_history
            if not c.resolved or c.resolution_timestamp > cutoff_date
        ]
        
        cleared_count = initial_count - len(self.conflict_history)
        logger.info(f"Cleared {cleared_count} resolved conflicts older than {older_than_days} days")

# Export the main class
__all__ = ['ConflictResolver', 'ConflictData', 'ConflictType']