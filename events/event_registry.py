"""🚀 Event Registry System - IA Influencer Agent Platform
==========================================================
Module: events/event_registry.py
Author: Fahed Mlaiel (mlaiel@live.de)
==========================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 EVENT REGISTRY
Central registry for all event types in the system
- Dynamic event type registration and validation
- Schema management and versioning
- Event discovery and documentation
- Type safety and validation rules
"""

import json
import logging
from typing import Dict, List, Optional, Any, Type, Set, Union
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import jsonschema
from pathlib import Path

from .core.base_event import BaseEvent
from .core.exceptions import EventValidationError

logger = logging.getLogger(__name__)


class EventCategory(Enum):
    """Event categories for organization"""
    DOMAIN = "domain"
    INTEGRATION = "integration"
    SYSTEM = "system"
    USER = "user"
    AI_PROCESSING = "ai_processing"
    AUDIO = "audio"
    ANALYTICS = "analytics"
    SECURITY = "security"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"


@dataclass
class EventSchema:
    """Event schema definition"""
    event_type: str
    version: str
    category: EventCategory
    description: str
    schema: Dict[str, Any]
    required_fields: List[str] = field(default_factory=list)
    deprecated: bool = False
    deprecated_since: Optional[str] = None
    replacement_event: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def validate_event_data(self, data: Dict[str, Any]) -> bool:
        """Validate event data against schema"""
        try:
            jsonschema.validate(data, self.schema)
            return True
        except jsonschema.ValidationError as e:
            logger.error(f"Schema validation failed for {self.event_type}: {e}")
            return False


@dataclass
class EventTypeMetadata:
    """Metadata for event types"""
    event_type: str
    handler_count: int = 0
    total_published: int = 0
    total_processed: int = 0
    avg_processing_time: float = 0.0
    last_published: Optional[datetime] = None
    last_processed: Optional[datetime] = None


class EventRegistry:
    """Central registry for event types and schemas"""
    
    def __init__(self):
        """Initialize event registry"""
        self.schemas: Dict[str, EventSchema] = {}
        self.metadata: Dict[str, EventTypeMetadata] = {}
        self.categories: Dict[EventCategory, Set[str]] = {
            category: set() for category in EventCategory
        }
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize with core event types
        self._register_core_events()
        
        logger.info("Event registry initialized")
    
    def register_event_type(self,
                           event_type: str,
                           schema: Dict[str, Any],
                           category: EventCategory,
                           description: str,
                           version: str = "1.0.0",
                           required_fields: Optional[List[str]] = None) -> bool:
        """Register a new event type
        
        Args:
            event_type: Unique event type identifier
            schema: JSON schema for validation
            category: Event category
            description: Human-readable description
            version: Schema version
            required_fields: List of required fields
            
        Returns:
            True if registration successful
        """
        if event_type in self.schemas:
            logger.warning(f"Event type already registered: {event_type}")
            return False
        
        # Validate schema format
        if not self._validate_schema_format(schema):
            raise EventValidationError(f"Invalid schema format for {event_type}")
        
        # Create event schema
        event_schema = EventSchema(
            event_type=event_type,
            version=version,
            category=category,
            description=description,
            schema=schema,
            required_fields=required_fields or []
        )
        
        # Register schema
        self.schemas[event_type] = event_schema
        self.categories[category].add(event_type)
        
        # Initialize metadata
        self.metadata[event_type] = EventTypeMetadata(event_type=event_type)
        
        # Cache compiled schema
        self._schema_cache[event_type] = schema
        
        logger.info(f"Event type registered: {event_type} (v{version}) in {category.value}")
        return True
    
    def unregister_event_type(self, event_type: str) -> bool:
        """Unregister an event type
        
        Args:
            event_type: Event type to remove
            
        Returns:
            True if unregistration successful
        """
        if event_type not in self.schemas:
            logger.warning(f"Event type not found: {event_type}")
            return False
        
        schema = self.schemas[event_type]
        
        # Remove from category
        self.categories[schema.category].discard(event_type)
        
        # Remove from registry
        del self.schemas[event_type]
        del self.metadata[event_type]
        
        # Remove from cache
        self._schema_cache.pop(event_type, None)
        
        logger.info(f"Event type unregistered: {event_type}")
        return True
    
    def get_event_schema(self, event_type: str) -> Optional[EventSchema]:
        """Get event schema by type
        
        Args:
            event_type: Event type identifier
            
        Returns:
            Event schema or None if not found
        """
        return self.schemas.get(event_type)
    
    def validate_event(self, event: BaseEvent) -> bool:
        """Validate an event against its registered schema
        
        Args:
            event: Event to validate
            
        Returns:
            True if valid
        """
        schema = self.get_event_schema(event.event_type)
        if not schema:
            logger.warning(f"No schema found for event type: {event.event_type}")
            return False
        
        if schema.deprecated:
            logger.warning(f"Event type is deprecated: {event.event_type}")
            if schema.replacement_event:
                logger.warning(f"Use {schema.replacement_event} instead")
        
        # Validate event data
        if event.data and not schema.validate_event_data(event.data):
            return False
        
        # Check required fields
        if event.data:
            for field in schema.required_fields:
                if field not in event.data:
                    logger.error(f"Missing required field '{field}' in {event.event_type}")
                    return False
        
        return True
    
    def get_events_by_category(self, category: EventCategory) -> List[str]:
        """Get all event types in a category
        
        Args:
            category: Event category
            
        Returns:
            List of event types
        """
        return list(self.categories.get(category, set()))
    
    def get_all_event_types(self) -> List[str]:
        """Get all registered event types
        
        Returns:
            List of all event types
        """
        return list(self.schemas.keys())
    
    def deprecate_event_type(self,
                           event_type: str,
                           replacement_event: Optional[str] = None,
                           deprecated_since: Optional[str] = None) -> bool:
        """Mark an event type as deprecated
        
        Args:
            event_type: Event type to deprecate
            replacement_event: Optional replacement event type
            deprecated_since: Version when deprecated
            
        Returns:
            True if deprecation successful
        """
        schema = self.get_event_schema(event_type)
        if not schema:
            logger.error(f"Event type not found: {event_type}")
            return False
        
        schema.deprecated = True
        schema.replacement_event = replacement_event
        schema.deprecated_since = deprecated_since or "unknown"
        schema.updated_at = datetime.utcnow()
        
        logger.info(f"Event type deprecated: {event_type}")
        if replacement_event:
            logger.info(f"Replacement event: {replacement_event}")
        
        return True
    
    def update_event_metadata(self,
                            event_type: str,
                            handler_count: Optional[int] = None,
                            published: bool = False,
                            processed: bool = False,
                            processing_time: Optional[float] = None) -> None:
        """Update event type metadata
        
        Args:
            event_type: Event type to update
            handler_count: Number of handlers
            published: Event was published
            processed: Event was processed
            processing_time: Processing time in seconds
        """
        if event_type not in self.metadata:
            self.metadata[event_type] = EventTypeMetadata(event_type=event_type)
        
        metadata = self.metadata[event_type]
        
        if handler_count is not None:
            metadata.handler_count = handler_count
        
        if published:
            metadata.total_published += 1
            metadata.last_published = datetime.utcnow()
        
        if processed:
            metadata.total_processed += 1
            metadata.last_processed = datetime.utcnow()
            
            if processing_time is not None:
                # Update rolling average
                total_processed = metadata.total_processed
                current_avg = metadata.avg_processing_time
                metadata.avg_processing_time = (
                    (current_avg * (total_processed - 1) + processing_time) / total_processed
                )
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get comprehensive event statistics
        
        Returns:
            Dictionary with statistics
        """
        total_schemas = len(self.schemas)
        deprecated_count = sum(1 for s in self.schemas.values() if s.deprecated)
        
        category_stats = {
            category.value: len(events) 
            for category, events in self.categories.items()
        }
        
        # Processing statistics
        total_published = sum(m.total_published for m in self.metadata.values())
        total_processed = sum(m.total_processed for m in self.metadata.values())
        
        avg_processing_time = 0.0
        if self.metadata:
            avg_processing_time = sum(
                m.avg_processing_time for m in self.metadata.values()
            ) / len(self.metadata)
        
        return {
            "total_registered_types": total_schemas,
            "deprecated_types": deprecated_count,
            "active_types": total_schemas - deprecated_count,
            "category_distribution": category_stats,
            "processing_stats": {
                "total_published": total_published,
                "total_processed": total_processed,
                "average_processing_time": avg_processing_time,
                "success_rate": total_processed / max(total_published, 1)
            }
        }
    
    def export_schemas(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Export all schemas to JSON
        
        Args:
            file_path: Optional file path to save schemas
            
        Returns:
            Dictionary with all schemas
        """
        export_data = {
            "exported_at": datetime.utcnow().isoformat(),
            "schemas": {
                event_type: {
                    "version": schema.version,
                    "category": schema.category.value,
                    "description": schema.description,
                    "schema": schema.schema,
                    "required_fields": schema.required_fields,
                    "deprecated": schema.deprecated,
                    "deprecated_since": schema.deprecated_since,
                    "replacement_event": schema.replacement_event,
                    "created_at": schema.created_at.isoformat(),
                    "updated_at": schema.updated_at.isoformat()
                }
                for event_type, schema in self.schemas.items()
            }
        }
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Schemas exported to: {file_path}")
        
        return export_data
    
    def import_schemas(self, file_path: str) -> int:
        """Import schemas from JSON file
        
        Args:
            file_path: Path to JSON file with schemas
            
        Returns:
            Number of schemas imported
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            schemas_data = import_data.get("schemas", {})
            imported_count = 0
            
            for event_type, schema_data in schemas_data.items():
                try:
                    success = self.register_event_type(
                        event_type=event_type,
                        schema=schema_data["schema"],
                        category=EventCategory(schema_data["category"]),
                        description=schema_data["description"],
                        version=schema_data["version"],
                        required_fields=schema_data.get("required_fields", [])
                    )
                    
                    if success:
                        # Update additional properties
                        schema = self.schemas[event_type]
                        schema.deprecated = schema_data.get("deprecated", False)
                        schema.deprecated_since = schema_data.get("deprecated_since")
                        schema.replacement_event = schema_data.get("replacement_event")
                        
                        imported_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to import schema for {event_type}: {e}")
            
            logger.info(f"Imported {imported_count} schemas from {file_path}")
            return imported_count
            
        except Exception as e:
            logger.error(f"Failed to import schemas from {file_path}: {e}")
            return 0
    
    def _validate_schema_format(self, schema: Dict[str, Any]) -> bool:
        """Validate JSON schema format"""
        try:
            # Basic JSON schema validation
            jsonschema.Draft7Validator.check_schema(schema)
            return True
        except jsonschema.SchemaError as e:
            logger.error(f"Invalid JSON schema: {e}")
            return False
    
    def _register_core_events(self) -> None:
        """Register core system event types"""
        # Domain events
        self.register_event_type(
            event_type="user.created",
            schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "username": {"type": "string"},
                    "creator_type": {"type": "string"}
                },
                "required": ["user_id", "email", "username"]
            },
            category=EventCategory.DOMAIN,
            description="User account created",
            required_fields=["user_id", "email", "username"]
        )
        
        self.register_event_type(
            event_type="content.uploaded",
            schema={
                "type": "object",
                "properties": {
                    "content_id": {"type": "string"},
                    "user_id": {"type": "string"},
                    "content_type": {"type": "string"},
                    "file_size": {"type": "integer"},
                    "duration": {"type": "number"}
                },
                "required": ["content_id", "user_id", "content_type"]
            },
            category=EventCategory.DOMAIN,
            description="Content uploaded to platform",
            required_fields=["content_id", "user_id", "content_type"]
        )
        
        # AI Processing events
        self.register_event_type(
            event_type="ai.analysis.started",
            schema={
                "type": "object",
                "properties": {
                    "content_id": {"type": "string"},
                    "analysis_type": {"type": "string"},
                    "ai_model": {"type": "string"}
                },
                "required": ["content_id", "analysis_type"]
            },
            category=EventCategory.AI_PROCESSING,
            description="AI analysis started for content",
            required_fields=["content_id", "analysis_type"]
        )
        
        # System events
        self.register_event_type(
            event_type="system.error",
            schema={
                "type": "object",
                "properties": {
                    "error_code": {"type": "string"},
                    "error_message": {"type": "string"},
                    "component": {"type": "string"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                },
                "required": ["error_code", "error_message", "component"]
            },
            category=EventCategory.SYSTEM,
            description="System error occurred",
            required_fields=["error_code", "error_message", "component"]
        )


# Global registry instance
_global_registry: Optional[EventRegistry] = None


def get_global_registry() -> EventRegistry:
    """Get or create global event registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = EventRegistry()
    return _global_registry


def register_event_type(event_type: str, 
                       schema: Dict[str, Any],
                       category: EventCategory,
                       description: str,
                       **kwargs) -> bool:
    """Convenience function to register event type globally"""
    registry = get_global_registry()
    return registry.register_event_type(
        event_type, schema, category, description, **kwargs
    )


def validate_event(event: BaseEvent) -> bool:
    """Convenience function to validate event globally"""
    registry = get_global_registry()
    return registry.validate_event(event)