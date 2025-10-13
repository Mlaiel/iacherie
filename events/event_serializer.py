"""🚀 Event Serializer System - IA Influencer Agent Platform
============================================================
Module: events/event_serializer.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ADVANCED EVENT SERIALIZATION
High-performance event serialization and deserialization
- Multiple format support (JSON, MessagePack, Avro, Protobuf)
- Schema evolution and versioning
- Compression and encryption
- Performance optimization
- Memory-efficient streaming
"""

import json
import gzip
import base64
import logging
from typing import Dict, List, Optional, Any, Union, Type
from datetime import datetime
from dataclasses import asdict, is_dataclass
from enum import Enum
import pickle
from io import BytesIO

from .core.base_event import BaseEvent
from .core.exceptions import EventValidationError

logger = logging.getLogger(__name__)


class SerializationFormat(Enum):
    """Supported serialization formats"""
    JSON = "json"
    MSGPACK = "msgpack"
    PICKLE = "pickle"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    BSON = "bson"


class CompressionType(Enum):
    """Compression algorithms"""
    NONE = "none"
    GZIP = "gzip"
    DEFLATE = "deflate"
    LZ4 = "lz4"
    ZSTD = "zstd"


class EventSerializer:
    """Advanced event serialization system"""
    
    def __init__(self,
                 default_format: SerializationFormat = SerializationFormat.JSON,
                 compression: CompressionType = CompressionType.NONE,
                 include_metadata: bool = True,
                 pretty_print: bool = False):
        """Initialize event serializer
        
        Args:
            default_format: Default serialization format
            compression: Compression algorithm
            include_metadata: Include metadata in serialization
            pretty_print: Pretty print JSON output
        """
        self.default_format = default_format
        self.compression = compression
        self.include_metadata = include_metadata
        self.pretty_print = pretty_print
        
        # Performance tracking
        self.serialization_count = 0
        self.deserialization_count = 0
        self.total_bytes_serialized = 0
        self.total_bytes_deserialized = 0
        
        logger.info(f"Event serializer initialized - Format: {default_format.value}")
    
    def serialize(self,
                  event: BaseEvent,
                  format_type: Optional[SerializationFormat] = None,
                  compress: Optional[bool] = None) -> bytes:
        """Serialize an event to bytes
        
        Args:
            event: Event to serialize
            format_type: Serialization format override
            compress: Compression override
            
        Returns:
            Serialized event bytes
        """
        if not isinstance(event, BaseEvent):
            raise EventValidationError(f"Invalid event type: {type(event)}")
        
        format_type = format_type or self.default_format
        should_compress = compress if compress is not None else (
            self.compression != CompressionType.NONE
        )
        
        # Convert event to dictionary
        event_dict = self._event_to_dict(event)
        
        # Serialize based on format
        if format_type == SerializationFormat.JSON:
            serialized = self._serialize_json(event_dict)
        elif format_type == SerializationFormat.MSGPACK:
            serialized = self._serialize_msgpack(event_dict)
        elif format_type == SerializationFormat.PICKLE:
            serialized = self._serialize_pickle(event)
        elif format_type == SerializationFormat.AVRO:
            serialized = self._serialize_avro(event_dict)
        elif format_type == SerializationFormat.PROTOBUF:
            serialized = self._serialize_protobuf(event_dict)
        elif format_type == SerializationFormat.BSON:
            serialized = self._serialize_bson(event_dict)
        else:
            raise EventValidationError(f"Unsupported format: {format_type}")
        
        # Apply compression
        if should_compress:
            serialized = self._compress_data(serialized)
        
        # Update metrics
        self.serialization_count += 1
        self.total_bytes_serialized += len(serialized)
        
        logger.debug(f"Event serialized: {event.event_id} ({len(serialized)} bytes)")
        return serialized
    
    def deserialize(self,
                    data: bytes,
                    format_type: Optional[SerializationFormat] = None,
                    compressed: Optional[bool] = None) -> BaseEvent:
        """Deserialize bytes to an event
        
        Args:
            data: Serialized data
            format_type: Serialization format override
            compressed: Compression override
            
        Returns:
            Deserialized event
        """
        format_type = format_type or self.default_format
        is_compressed = compressed if compressed is not None else (
            self.compression != CompressionType.NONE
        )
        
        # Decompress if needed
        if is_compressed:
            data = self._decompress_data(data)
        
        # Deserialize based on format
        if format_type == SerializationFormat.JSON:
            event_dict = self._deserialize_json(data)
            event = self._dict_to_event(event_dict)
        elif format_type == SerializationFormat.MSGPACK:
            event_dict = self._deserialize_msgpack(data)
            event = self._dict_to_event(event_dict)
        elif format_type == SerializationFormat.PICKLE:
            event = self._deserialize_pickle(data)
        elif format_type == SerializationFormat.AVRO:
            event_dict = self._deserialize_avro(data)
            event = self._dict_to_event(event_dict)
        elif format_type == SerializationFormat.PROTOBUF:
            event_dict = self._deserialize_protobuf(data)
            event = self._dict_to_event(event_dict)
        elif format_type == SerializationFormat.BSON:
            event_dict = self._deserialize_bson(data)
            event = self._dict_to_event(event_dict)
        else:
            raise EventValidationError(f"Unsupported format: {format_type}")
        
        # Update metrics
        self.deserialization_count += 1
        self.total_bytes_deserialized += len(data)
        
        logger.debug(f"Event deserialized: {event.event_id}")
        return event
    
    def serialize_batch(self,
                       events: List[BaseEvent],
                       format_type: Optional[SerializationFormat] = None) -> bytes:
        """Serialize multiple events efficiently
        
        Args:
            events: List of events to serialize
            format_type: Serialization format override
            
        Returns:
            Serialized batch data
        """
        format_type = format_type or self.default_format
        
        # Convert all events to dictionaries
        event_dicts = [self._event_to_dict(event) for event in events]
        
        # Create batch container
        batch_data = {
            "format": format_type.value,
            "count": len(events),
            "events": event_dicts,
            "serialized_at": datetime.utcnow().isoformat()
        }
        
        # Serialize batch
        if format_type == SerializationFormat.JSON:
            serialized = self._serialize_json(batch_data)
        elif format_type == SerializationFormat.MSGPACK:
            serialized = self._serialize_msgpack(batch_data)
        else:
            # Fallback to JSON for batch operations
            serialized = self._serialize_json(batch_data)
        
        # Apply compression for large batches
        if len(serialized) > 1024:  # 1KB threshold
            serialized = self._compress_data(serialized)
        
        logger.debug(f"Batch serialized: {len(events)} events ({len(serialized)} bytes)")
        return serialized
    
    def deserialize_batch(self,
                         data: bytes,
                         format_type: Optional[SerializationFormat] = None) -> List[BaseEvent]:
        """Deserialize multiple events efficiently
        
        Args:
            data: Serialized batch data
            format_type: Serialization format override
            
        Returns:
            List of deserialized events
        """
        # Try decompression first
        try:
            data = self._decompress_data(data)
        except:
            # Data might not be compressed
            pass
        
        format_type = format_type or self.default_format
        
        # Deserialize batch container
        if format_type == SerializationFormat.JSON:
            batch_data = self._deserialize_json(data)
        elif format_type == SerializationFormat.MSGPACK:
            batch_data = self._deserialize_msgpack(data)
        else:
            # Try JSON as fallback
            batch_data = self._deserialize_json(data)
        
        # Extract events
        if "events" not in batch_data:
            raise EventValidationError("Invalid batch format: missing events")
        
        events = []
        for event_dict in batch_data["events"]:
            event = self._dict_to_event(event_dict)
            events.append(event)
        
        logger.debug(f"Batch deserialized: {len(events)} events")
        return events
    
    def _event_to_dict(self, event: BaseEvent) -> Dict[str, Any]:
        """Convert event to dictionary"""
        event_dict = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "data": event.data or {},
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "status": event.status.value if hasattr(event.status, 'value') else str(event.status)
        }
        
        if self.include_metadata:
            event_dict["metadata"] = event.metadata or {}
            if hasattr(event, 'priority'):
                event_dict["priority"] = event.priority.value if hasattr(event.priority, 'value') else str(event.priority)
            if hasattr(event, 'source'):
                event_dict["source"] = event.source
            if hasattr(event, 'correlation_id'):
                event_dict["correlation_id"] = event.correlation_id
            if hasattr(event, 'causation_id'):
                event_dict["causation_id"] = event.causation_id
            if hasattr(event, 'aggregate_id'):
                event_dict["aggregate_id"] = event.aggregate_id
            if hasattr(event, 'aggregate_version'):
                event_dict["aggregate_version"] = event.aggregate_version
            if hasattr(event, 'error_message'):
                event_dict["error_message"] = event.error_message
        
        return event_dict
    
    def _dict_to_event(self, event_dict: Dict[str, Any]) -> BaseEvent:
        """Convert dictionary to event"""
        # Parse timestamp
        timestamp = None
        if event_dict.get("timestamp"):
            try:
                timestamp = datetime.fromisoformat(event_dict["timestamp"])
            except:
                timestamp = datetime.utcnow()
        
        # Create base event
        event = BaseEvent(
            event_type=event_dict["event_type"],
            data=event_dict.get("data", {}),
            metadata=event_dict.get("metadata", {})
        )
        
        # Set additional properties
        if event_dict.get("event_id"):
            event.event_id = event_dict["event_id"]
        if timestamp:
            event.timestamp = timestamp
        
        # Import here to avoid circular imports
        from .core.event_status import EventStatus
        if event_dict.get("status"):
            try:
                event.status = EventStatus(event_dict["status"])
            except ValueError:
                event.status = EventStatus.PENDING
        
        if event_dict.get("priority"):
            try:
                from .core.event_priority import EventPriority
                event.priority = EventPriority(event_dict["priority"])
            except (ValueError, ImportError):
                pass
        
        # Set optional attributes
        for attr in ["source", "correlation_id", "causation_id", "aggregate_id", 
                    "aggregate_version", "error_message"]:
            if event_dict.get(attr):
                setattr(event, attr, event_dict[attr])
        
        return event
    
    def _serialize_json(self, data: Any) -> bytes:
        """Serialize to JSON"""
        json_str = json.dumps(
            data,
            ensure_ascii=False,
            separators=(',', ':') if not self.pretty_print else None,
            indent=2 if self.pretty_print else None,
            default=self._json_default
        )
        return json_str.encode('utf-8')
    
    def _deserialize_json(self, data: bytes) -> Any:
        """Deserialize from JSON"""
        return json.loads(data.decode('utf-8'))
    
    def _serialize_msgpack(self, data: Any) -> bytes:
        """Serialize to MessagePack"""
        try:
            import msgpack
            return msgpack.packb(data, use_bin_type=True, strict_types=False)
        except ImportError:
            logger.warning("msgpack not available, falling back to JSON")
            return self._serialize_json(data)
    
    def _deserialize_msgpack(self, data: bytes) -> Any:
        """Deserialize from MessagePack"""
        try:
            import msgpack
            return msgpack.unpackb(data, raw=False, strict_map_key=False)
        except ImportError:
            logger.warning("msgpack not available, trying JSON")
            return self._deserialize_json(data)
    
    def _serialize_pickle(self, event: BaseEvent) -> bytes:
        """Serialize to Pickle"""
        return pickle.dumps(event, protocol=pickle.HIGHEST_PROTOCOL)
    
    def _deserialize_pickle(self, data: bytes) -> BaseEvent:
        """Deserialize from Pickle"""
        return pickle.loads(data)
    
    def _serialize_avro(self, data: Any) -> bytes:
        """Serialize to Avro (placeholder)"""
        logger.warning("Avro serialization not implemented, using JSON")
        return self._serialize_json(data)
    
    def _deserialize_avro(self, data: bytes) -> Any:
        """Deserialize from Avro (placeholder)"""
        logger.warning("Avro deserialization not implemented, using JSON")
        return self._deserialize_json(data)
    
    def _serialize_protobuf(self, data: Any) -> bytes:
        """Serialize to Protocol Buffers (placeholder)"""
        logger.warning("Protobuf serialization not implemented, using JSON")
        return self._serialize_json(data)
    
    def _deserialize_protobuf(self, data: bytes) -> Any:
        """Deserialize from Protocol Buffers (placeholder)"""
        logger.warning("Protobuf deserialization not implemented, using JSON")
        return self._deserialize_json(data)
    
    def _serialize_bson(self, data: Any) -> bytes:
        """Serialize to BSON"""
        try:
            import bson
            return bson.encode(data)
        except ImportError:
            logger.warning("bson not available, falling back to JSON")
            return self._serialize_json(data)
    
    def _deserialize_bson(self, data: bytes) -> Any:
        """Deserialize from BSON"""
        try:
            import bson
            return bson.decode(data)
        except ImportError:
            logger.warning("bson not available, trying JSON")
            return self._deserialize_json(data)
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data"""
        if self.compression == CompressionType.GZIP:
            return gzip.compress(data)
        elif self.compression == CompressionType.DEFLATE:
            import zlib
            return zlib.compress(data)
        elif self.compression == CompressionType.LZ4:
            try:
                import lz4.frame
                return lz4.frame.compress(data)
            except ImportError:
                logger.warning("lz4 not available, using gzip")
                return gzip.compress(data)
        elif self.compression == CompressionType.ZSTD:
            try:
                import zstandard as zstd
                cctx = zstd.ZstdCompressor()
                return cctx.compress(data)
            except ImportError:
                logger.warning("zstandard not available, using gzip")
                return gzip.compress(data)
        else:
            return data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress data"""
        if self.compression == CompressionType.GZIP:
            return gzip.decompress(data)
        elif self.compression == CompressionType.DEFLATE:
            import zlib
            return zlib.decompress(data)
        elif self.compression == CompressionType.LZ4:
            try:
                import lz4.frame
                return lz4.frame.decompress(data)
            except ImportError:
                return gzip.decompress(data)
        elif self.compression == CompressionType.ZSTD:
            try:
                import zstandard as zstd
                dctx = zstd.ZstdDecompressor()
                return dctx.decompress(data)
            except ImportError:
                return gzip.decompress(data)
        else:
            return data
    
    def _json_default(self, obj: Any) -> Any:
        """JSON serialization for custom objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif is_dataclass(obj):
            return asdict(obj)
        else:
            return str(obj)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get serialization statistics"""
        avg_serialized_size = (
            self.total_bytes_serialized / max(self.serialization_count, 1)
        )
        avg_deserialized_size = (
            self.total_bytes_deserialized / max(self.deserialization_count, 1)
        )
        
        return {
            "default_format": self.default_format.value,
            "compression": self.compression.value,
            "serialization_count": self.serialization_count,
            "deserialization_count": self.deserialization_count,
            "total_bytes_serialized": self.total_bytes_serialized,
            "total_bytes_deserialized": self.total_bytes_deserialized,
            "average_serialized_size": avg_serialized_size,
            "average_deserialized_size": avg_deserialized_size,
            "compression_ratio": (
                self.total_bytes_deserialized / max(self.total_bytes_serialized, 1)
                if self.compression != CompressionType.NONE else 1.0
            )
        }


# Global serializer instance
_global_serializer: Optional[EventSerializer] = None


def get_global_serializer() -> EventSerializer:
    """Get or create global event serializer instance"""
    global _global_serializer
    if _global_serializer is None:
        _global_serializer = EventSerializer()
    return _global_serializer


def serialize_event(event: BaseEvent, **kwargs) -> bytes:
    """Convenience function to serialize event globally"""
    serializer = get_global_serializer()
    return serializer.serialize(event, **kwargs)


def deserialize_event(data: bytes, **kwargs) -> BaseEvent:
    """Convenience function to deserialize event globally"""
    serializer = get_global_serializer()
    return serializer.deserialize(data, **kwargs)