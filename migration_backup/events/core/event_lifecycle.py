"""Event Lifecycle Management Module

Comprehensive event lifecycle management with creation, validation, tracking,
archiving, and cleanup capabilities for enterprise event processing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict

from .base_event import BaseEvent
from .event_priority import EventPriority
from .event_status import EventStatus
from .exceptions import EventValidationError, EventProcessingError

logger = logging.getLogger(__name__)


class LifecycleStage(Enum):
    """Event lifecycle stages"""
    CREATED = "created"
    VALIDATED = "validated"
    ENRICHED = "enriched"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"
    PURGED = "purged"


@dataclass
class EventLifecycleMetadata:
    """Extended metadata for event lifecycle tracking"""
    created_at: datetime
    created_by: Optional[str] = None
    validation_rules_applied: List[str] = field(default_factory=list)
    enrichment_history: List[Dict[str, Any]] = field(default_factory=list)
    processing_attempts: int = 0
    processing_history: List[Dict[str, Any]] = field(default_factory=list)
    archived_at: Optional[datetime] = None
    archive_location: Optional[str] = None
    retention_until: Optional[datetime] = None
    lifecycle_stage: LifecycleStage = LifecycleStage.CREATED


@dataclass
class ValidationRule:
    """Event validation rule definition"""
    name: str
    rule_function: Callable[[BaseEvent], bool]
    error_message: str
    critical: bool = False


class EventLifecycle:
    """
    Comprehensive event lifecycle management system.
    
    Handles event creation, validation, enrichment, tracking,
    archiving, and cleanup operations with full audit trails.
    """
    
    def __init__(self, 
                 default_retention_days: int = 90,
                 archive_after_days: int = 30,
                 enable_auto_cleanup: bool = True):
        self.default_retention_days = default_retention_days
        self.archive_after_days = archive_after_days
        self.enable_auto_cleanup = enable_auto_cleanup
        
        # Event tracking
        self._event_metadata: Dict[str, EventLifecycleMetadata] = {}
        self._validation_rules: Dict[str, List[ValidationRule]] = defaultdict(list)
        self._global_validation_rules: List[ValidationRule] = []
        
        # Lifecycle statistics
        self._lifecycle_stats = {
            'events_created': 0,
            'events_validated': 0,
            'events_enriched': 0,
            'events_archived': 0,
            'events_purged': 0,
            'validation_failures': 0
        }
        
        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        if enable_auto_cleanup:
            self._start_cleanup_task()
            
        logger.info(f"Event lifecycle manager initialized with {default_retention_days} day retention")
    
    async def create_event(self, 
                          event_type: str,
                          data: Dict[str, Any],
                          priority: EventPriority = EventPriority.MEDIUM,
                          metadata: Optional[Dict[str, Any]] = None,
                          created_by: Optional[str] = None,
                          retention_days: Optional[int] = None,
                          **kwargs) -> BaseEvent:
        """
        Create a new event with full lifecycle tracking.
        
        Args:
            event_type: Type of event to create
            data: Event data payload
            priority: Event priority level
            metadata: Additional metadata
            created_by: Creator identifier
            retention_days: Custom retention period
            **kwargs: Additional event parameters
            
        Returns:
            Created event with lifecycle metadata
        """
        # Create the base event
        event = BaseEvent(
            event_type=event_type,
            data=data,
            priority=priority,
            status=EventStatus.PENDING,
            metadata=metadata or {},
            **kwargs
        )
        
        # Calculate retention period
        retention_period = retention_days or self.default_retention_days
        retention_until = datetime.utcnow() + timedelta(days=retention_period)
        
        # Create lifecycle metadata
        lifecycle_metadata = EventLifecycleMetadata(
            created_at=datetime.utcnow(),
            created_by=created_by,
            retention_until=retention_until,
            lifecycle_stage=LifecycleStage.CREATED
        )
        
        # Store lifecycle tracking
        self._event_metadata[event.event_id] = lifecycle_metadata
        
        # Update statistics
        self._lifecycle_stats['events_created'] += 1
        
        logger.info(f"Event {event.event_id} created with lifecycle tracking")
        return event
    
    async def validate_event(self, event: BaseEvent) -> Dict[str, Any]:
        """
        Validate event against registered rules.
        
        Args:
            event: Event to validate
            
        Returns:
            Validation results with passed/failed rules
        """
        if event.event_id not in self._event_metadata:
            raise EventValidationError(f"Event {event.event_id} not found in lifecycle tracking")
        
        validation_start = datetime.utcnow()
        results = {
            'event_id': event.event_id,
            'validation_timestamp': validation_start.isoformat(),
            'rules_passed': [],
            'rules_failed': [],
            'critical_failures': [],
            'overall_status': 'unknown'
        }
        
        # Get applicable validation rules
        rules = self._global_validation_rules.copy()
        if event.event_type in self._validation_rules:
            rules.extend(self._validation_rules[event.event_type])
        
        # Execute validation rules
        for rule in rules:
            try:
                rule_passed = await self._execute_validation_rule(rule, event)
                
                if rule_passed:
                    results['rules_passed'].append(rule.name)
                else:
                    results['rules_failed'].append({
                        'rule_name': rule.name,
                        'error_message': rule.error_message,
                        'critical': rule.critical
                    })
                    
                    if rule.critical:
                        results['critical_failures'].append(rule.name)
                        
            except Exception as e:
                results['rules_failed'].append({
                    'rule_name': rule.name,
                    'error_message': f"Rule execution failed: {e}",
                    'critical': rule.critical
                })
                
                if rule.critical:
                    results['critical_failures'].append(rule.name)
        
        # Determine overall validation status
        if results['critical_failures']:
            results['overall_status'] = 'failed_critical'
            event.status = EventStatus.FAILED
            self._lifecycle_stats['validation_failures'] += 1
        elif results['rules_failed']:
            results['overall_status'] = 'failed_non_critical'
        else:
            results['overall_status'] = 'passed'
            self._lifecycle_stats['events_validated'] += 1
        
        # Update lifecycle metadata
        metadata = self._event_metadata[event.event_id]
        metadata.validation_rules_applied = [rule.name for rule in rules]
        metadata.lifecycle_stage = LifecycleStage.VALIDATED
        
        logger.info(f"Event {event.event_id} validation completed: {results['overall_status']}")
        return results
    
    async def enrich_metadata(self, 
                             event: BaseEvent, 
                             enrichment_data: Dict[str, Any],
                             enrichment_source: str) -> BaseEvent:
        """
        Enrich event with additional metadata.
        
        Args:
            event: Event to enrich
            enrichment_data: Data to add to event
            enrichment_source: Source of enrichment data
            
        Returns:
            Enriched event
        """
        if event.event_id not in self._event_metadata:
            raise EventProcessingError(f"Event {event.event_id} not found in lifecycle tracking")
        
        # Add enrichment data to event metadata
        event.metadata.update(enrichment_data)
        
        # Track enrichment in lifecycle
        enrichment_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'source': enrichment_source,
            'data_keys': list(enrichment_data.keys()),
            'data_size': len(json.dumps(enrichment_data, default=str))
        }
        
        metadata = self._event_metadata[event.event_id]
        metadata.enrichment_history.append(enrichment_record)
        metadata.lifecycle_stage = LifecycleStage.ENRICHED
        
        self._lifecycle_stats['events_enriched'] += 1
        
        logger.info(f"Event {event.event_id} enriched with {len(enrichment_data)} fields")
        return event
    
    async def track_processing(self, 
                              event: BaseEvent,
                              processor_id: str,
                              processing_result: Dict[str, Any],
                              success: bool) -> None:
        """
        Track event processing attempt and result.
        
        Args:
            event: Event being processed
            processor_id: Identifier of processor
            processing_result: Processing result data
            success: Whether processing succeeded
        """
        if event.event_id not in self._event_metadata:
            logger.warning(f"Event {event.event_id} not found in lifecycle tracking")
            return
        
        processing_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'processor_id': processor_id,
            'success': success,
            'result_summary': {
                'keys': list(processing_result.keys()) if processing_result else [],
                'success': success
            }
        }
        
        metadata = self._event_metadata[event.event_id]
        metadata.processing_attempts += 1
        metadata.processing_history.append(processing_record)
        
        if success:
            metadata.lifecycle_stage = LifecycleStage.COMPLETED
        else:
            metadata.lifecycle_stage = LifecycleStage.FAILED
        
        logger.debug(f"Processing tracked for event {event.event_id} by {processor_id}")
    
    async def archive_event(self, 
                           event: BaseEvent,
                           archive_location: str,
                           archive_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Archive event for long-term storage.
        
        Args:
            event: Event to archive
            archive_location: Storage location for archived event
            archive_metadata: Additional archive metadata
            
        Returns:
            Archive operation results
        """
        if event.event_id not in self._event_metadata:
            raise EventProcessingError(f"Event {event.event_id} not found in lifecycle tracking")
        
        archive_data = {
            'event': event.to_dict(),
            'lifecycle_metadata': self._serialize_lifecycle_metadata(
                self._event_metadata[event.event_id]
            ),
            'archive_metadata': archive_metadata or {},
            'archived_at': datetime.utcnow().isoformat()
        }
        
        # Update lifecycle metadata
        metadata = self._event_metadata[event.event_id]
        metadata.archived_at = datetime.utcnow()
        metadata.archive_location = archive_location
        metadata.lifecycle_stage = LifecycleStage.ARCHIVED
        
        # Update event status
        event.status = EventStatus.ARCHIVED
        
        self._lifecycle_stats['events_archived'] += 1
        
        logger.info(f"Event {event.event_id} archived to {archive_location}")
        
        return {
            'success': True,
            'event_id': event.event_id,
            'archive_location': archive_location,
            'archive_size': len(json.dumps(archive_data, default=str)),
            'archived_at': metadata.archived_at.isoformat()
        }
    
    async def cleanup_old_events(self, 
                                force_cleanup: bool = False,
                                dry_run: bool = False) -> Dict[str, Any]:
        """
        Clean up old events based on retention policies.
        
        Args:
            force_cleanup: Force cleanup regardless of settings
            dry_run: Simulate cleanup without actually removing events
            
        Returns:
            Cleanup operation results
        """
        if not self.enable_auto_cleanup and not force_cleanup:
            return {'status': 'skipped', 'reason': 'auto_cleanup_disabled'}
        
        cleanup_start = datetime.utcnow()
        current_time = datetime.utcnow()
        
        events_to_archive = []
        events_to_purge = []
        
        # Identify events for cleanup
        for event_id, metadata in self._event_metadata.items():
            # Archive old events
            if (metadata.lifecycle_stage not in [LifecycleStage.ARCHIVED, LifecycleStage.PURGED] and
                metadata.created_at < current_time - timedelta(days=self.archive_after_days)):
                events_to_archive.append(event_id)
            
            # Purge expired events
            if (metadata.retention_until and 
                metadata.retention_until < current_time):
                events_to_purge.append(event_id)
        
        results = {
            'cleanup_timestamp': cleanup_start.isoformat(),
            'dry_run': dry_run,
            'events_identified_for_archive': len(events_to_archive),
            'events_identified_for_purge': len(events_to_purge),
            'events_archived': 0,
            'events_purged': 0
        }
        
        if not dry_run:
            # Archive events (this would typically move to external storage)
            for event_id in events_to_archive:
                metadata = self._event_metadata[event_id]
                metadata.lifecycle_stage = LifecycleStage.ARCHIVED
                metadata.archived_at = current_time
                results['events_archived'] += 1
            
            # Purge expired events
            for event_id in events_to_purge:
                if event_id in self._event_metadata:
                    del self._event_metadata[event_id]
                    results['events_purged'] += 1
                    self._lifecycle_stats['events_purged'] += 1
        
        cleanup_duration = (datetime.utcnow() - cleanup_start).total_seconds()
        results['cleanup_duration_seconds'] = cleanup_duration
        
        logger.info(f"Cleanup completed: archived {results['events_archived']}, "
                   f"purged {results['events_purged']} events")
        
        return results
    
    def add_validation_rule(self, 
                           rule: ValidationRule,
                           event_types: Optional[List[str]] = None) -> None:
        """
        Add validation rule for specific event types or globally.
        
        Args:
            rule: Validation rule to add
            event_types: Event types to apply rule to (None for global)
        """
        if event_types:
            for event_type in event_types:
                self._validation_rules[event_type].append(rule)
            logger.info(f"Added validation rule '{rule.name}' for types: {event_types}")
        else:
            self._global_validation_rules.append(rule)
            logger.info(f"Added global validation rule '{rule.name}'")
    
    async def get_event_lifecycle_info(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive lifecycle information for an event"""
        if event_id not in self._event_metadata:
            return None
        
        metadata = self._event_metadata[event_id]
        return self._serialize_lifecycle_metadata(metadata)
    
    async def get_lifecycle_statistics(self) -> Dict[str, Any]:
        """Get lifecycle management statistics"""
        active_events = len(self._event_metadata)
        
        stage_counts = defaultdict(int)
        for metadata in self._event_metadata.values():
            stage_counts[metadata.lifecycle_stage.value] += 1
        
        return {
            **self._lifecycle_stats,
            'active_events_tracked': active_events,
            'events_by_stage': dict(stage_counts),
            'validation_rules_count': {
                'global': len(self._global_validation_rules),
                'event_specific': len(self._validation_rules)
            }
        }
    
    def _serialize_lifecycle_metadata(self, metadata: EventLifecycleMetadata) -> Dict[str, Any]:
        """Serialize lifecycle metadata to dictionary"""
        return {
            'created_at': metadata.created_at.isoformat(),
            'created_by': metadata.created_by,
            'validation_rules_applied': metadata.validation_rules_applied,
            'enrichment_history': metadata.enrichment_history,
            'processing_attempts': metadata.processing_attempts,
            'processing_history': metadata.processing_history,
            'archived_at': metadata.archived_at.isoformat() if metadata.archived_at else None,
            'archive_location': metadata.archive_location,
            'retention_until': metadata.retention_until.isoformat() if metadata.retention_until else None,
            'lifecycle_stage': metadata.lifecycle_stage.value
        }
    
    async def _execute_validation_rule(self, rule: ValidationRule, event: BaseEvent) -> bool:
        """Execute a validation rule asynchronously if needed"""
        try:
            result = rule.rule_function(event)
            if asyncio.iscoroutine(result):
                return await result
            return result
        except Exception as e:
            logger.error(f"Validation rule '{rule.name}' failed: {e}")
            return False
    
    def _start_cleanup_task(self):
        """Start automatic cleanup background task"""
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(3600)  # Run hourly
                    await self.cleanup_old_events()
                except Exception as e:
                    logger.error(f"Cleanup task error: {e}")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
        logger.info("Automatic cleanup task started")
    
    async def shutdown(self):
        """Shutdown lifecycle manager and cleanup tasks"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Event lifecycle manager shutdown completed")


# Export main classes
__all__ = [
    'EventLifecycle',
    'LifecycleStage', 
    'EventLifecycleMetadata',
    'ValidationRule'
]

logger.info("Event lifecycle module initialized successfully")