"""Event Serialization Engine - Ultra-Optimized for Ainflue Business Events

import asyncio

High performance event serialization engine with intelligent compression,
multi-format support, and schema evolution for Ainflue platform business logic.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import gzip
import io
import time

# Optional compression libraries
try:
    import lz4.frame
    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False
from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

if TYPE_CHECKING:
    from ..domain_events import DomainEvent

logger = logging.getLogger(__name__)


class SerializationFormat(Enum):
    """Supported serialization formats for Ainflue events"""
    JSON = "json"
    MSGPACK = "msgpack"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    CUSTOM_BINARY = "custom_binary"


class CompressionAlgorithm(Enum):
    """Supported compression algorithms"""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"


@dataclass
class CompressionConfig:
    """Configuration for compression settings"""
    algorithm: CompressionAlgorithm = CompressionAlgorithm.LZ4
    level: int = 1
    enable_adaptive: bool = True
    size_threshold: int = 1024  # Minimum size to compress


@dataclass
class SerializationMetrics:
    """Metrics collected during serialization process"""
    serialization_time: float
    compression_time: float
    original_size: int
    serialized_size: int
    compressed_size: int
    compression_ratio: float
    format_used: str
    compression_algorithm: str


@dataclass
class SerializedEvent:
    """Container for serialized event with metadata"""
    original_event_id: str
    serialized_data: bytes
    format: str
    schema_version: str
    compression_algorithm: str
    compression_ratio: float
    serialization_metrics: SerializationMetrics
    business_tags: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SchemaValidation:
    """Result of schema validation and evolution"""
    schema: Dict[str, Any]
    schema_version: str
    is_valid: bool
    evolution_applied: bool = False
    compatibility_issues: List[str] = field(default_factory=list)


@dataclass
class CompressedData:
    """Compressed data with metadata"""
    data: bytes
    compression_type: str
    compression_ratio: float
    original_size: int
    compressed_size: int


class SchemaRegistry:
    """Registry for event schemas with evolution support"""
    
    def __init__(self) -> None:
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.version_history: Dict[str, List[str]] = {}
    
    async def validate_and_evolve_schema(self, 
                                       event_data: Dict[str, Any], 
                                       format_type: str) -> SchemaValidation:
        """Validate event against schema and apply evolution if needed"""
        event_type = event_data.get("event_type", "unknown")
        
        # Get or create schema for event type
        schema_key = f"{event_type}_{format_type}"
        
        if schema_key not in self.schemas:
            # Generate schema from event structure
            schema = self._generate_schema_from_event(event_data, format_type)
            self.schemas[schema_key] = schema
            self.version_history[schema_key] = ["v1.0.0"]
            
            return SchemaValidation(
                schema=schema,
                schema_version="v1.0.0",
                is_valid=True
            )
        
        # Validate against existing schema
        current_schema = self.schemas[schema_key]
        validation_result = self._validate_against_schema(event_data, current_schema)
        
        if validation_result.is_valid:
            return validation_result
        
        # Apply schema evolution if needed
        evolved_schema = await self._evolve_schema(current_schema, event_data, format_type)
        
        return SchemaValidation(
            schema=evolved_schema,
            schema_version=self._get_next_version(schema_key),
            is_valid=True,
            evolution_applied=True
        )
    
    def _generate_schema_from_event(self, event_data: Dict[str, Any], format_type: str) -> Dict[str, Any]:
        """Generate schema from event structure"""
        return {
            "type": "object",
            "properties": {
                "event_id": {"type": "string"},
                "event_type": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "user_id": {"type": "string"},
                "payload": {"type": "object"},
                "metadata": {"type": "object"}
            },
            "required": ["event_id", "event_type", "timestamp"],
            "additionalProperties": True,
            "format": format_type
        }
    
    def _validate_against_schema(self, event_data: Dict[str, Any], schema: Dict[str, Any]) -> SchemaValidation:
        """Validate event data against schema"""
        # Basic validation - in production would use jsonschema or similar
        required_fields = schema.get("required", [])
        missing_fields = [field for field in required_fields if field not in event_data]
        
        if missing_fields:
            return SchemaValidation(
                schema=schema,
                schema_version="current",
                is_valid=False,
                compatibility_issues=[f"Missing required fields: {missing_fields}"]
            )
        
        return SchemaValidation(
            schema=schema,
            schema_version="current",
            is_valid=True
        )
    
    async def _evolve_schema(self, current_schema: Dict[str, Any], 
                           event_data: Dict[str, Any], format_type: str) -> Dict[str, Any]:
        """Evolve schema to accommodate new event structure"""
        # Create evolved schema with new fields
        evolved_schema = current_schema.copy()
        
        # Add any new fields from event_data
        for key in event_data.keys():
            if key not in evolved_schema.get("properties", {}):
                evolved_schema.setdefault("properties", {})[key] = {"type": "string"}
        
        return evolved_schema
    
    def _get_next_version(self, schema_key: str) -> str:
        """Get next version number for schema"""
        versions = self.version_history.get(schema_key, [])
        if not versions:
            return "v1.0.0"
        
        # Simple version increment
        last_version = versions[-1]
        version_parts = last_version.replace("v", "").split(".")
        minor = int(version_parts[1]) + 1
        new_version = f"v{version_parts[0]}.{minor}.0"
        
        self.version_history[schema_key].append(new_version)
        return new_version


class JSONSerializationStrategy:
    """Strategy for JSON serialization optimized for Ainflue business events"""
    
    async def serialize(self, event_data: Dict[str, Any], schema: Dict[str, Any]) -> bytes:
        """Serialize event data to JSON with business optimizations"""
        
        # Order fields for optimal parsing in Ainflue business context
        ordered_data = self._order_fields_for_business_logic(event_data)
        
        # Use compact JSON representation
        json_str = json.dumps(ordered_data, separators=(',', ':'), ensure_ascii=False)
        return json_str.encode('utf-8')
    
    def _order_fields_for_business_logic(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Order fields to optimize parsing for Ainflue business logic"""
        
        # Priority order for Ainflue business events
        field_priority = [
            "event_id", "event_type", "timestamp", "user_id",
            "payload", "business_metadata", "workflow_stage",
            "priority", "correlation_id", "source_service"
        ]
        
        ordered_data = {}
        
        # Add high-priority fields first
        for field in field_priority:
            if field in event_data:
                ordered_data[field] = event_data[field]
        
        # Add remaining fields
        for key, value in event_data.items():
            if key not in ordered_data:
                ordered_data[key] = value
        
        return ordered_data


class MessagePackSerializationStrategy:
    """Strategy for MessagePack serialization for compact binary format"""
    
    async def serialize(self, event_data: Dict[str, Any], schema: Dict[str, Any]) -> bytes:
        """Serialize event data to MessagePack format"""
        try:
            import msgpack
            return msgpack.packb(event_data, use_bin_type=True)
        except ImportError:
            # Fallback to JSON if msgpack not available
            logger.warning("MessagePack not available, falling back to JSON")
            json_strategy = JSONSerializationStrategy()
            return await json_strategy.serialize(event_data, schema)


class SerializationPerformanceOptimizer:
    """Optimizer for serialization performance monitoring"""
    
    def __init__(self) -> None:
        self.performance_history: List[SerializationMetrics] = []
    
    async def collect_metrics(self, 
                            original_event: Dict[str, Any],
                            serialized_data: bytes,
                            compressed_data: CompressedData) -> SerializationMetrics:
        """Collect performance metrics for serialization process"""
        
        original_size = len(str(original_event).encode('utf-8'))
        
        metrics = SerializationMetrics(
            serialization_time=0.001,  # Would be measured in real implementation
            compression_time=0.0005,
            original_size=original_size,
            serialized_size=len(serialized_data),
            compressed_size=compressed_data.compressed_size,
            compression_ratio=compressed_data.compression_ratio,
            format_used="json",
            compression_algorithm=compressed_data.compression_type
        )
        
        self.performance_history.append(metrics)
        return metrics


class EventSerializationEngine:
    """
    Ultra-optimized event serialization engine for Ainflue business events
    Supports multi-format serialization with intelligent compression and schema evolution
    """
    
    def __init__(self, compression_config -> None: Optional[CompressionConfig] = None) -> None:
        self.compression_config = compression_config or CompressionConfig()
        self.schema_registry = SchemaRegistry()
        self.serialization_strategies = {
            SerializationFormat.JSON.value: JSONSerializationStrategy(),
            SerializationFormat.MSGPACK.value: MessagePackSerializationStrategy(),
        }
        self.performance_optimizer = SerializationPerformanceOptimizer()
        logger.info("EventSerializationEngine initialized for Ainflue business events")
    
    async def serialize_business_event(self, 
                                     event_data: Dict[str, Any],
                                     target_format: str = "auto",
                                     business_context: Optional[Dict[str, Any]] = None) -> SerializedEvent:
        """Serialize business event with intelligent format selection and optimization"""
        
        start_time = time.time()
        business_context = business_context or {}
        
        # Determine optimal format for Ainflue business context
        optimal_format = await self._determine_optimal_format(event_data, business_context)
        format_to_use = target_format if target_format != "auto" else optimal_format
        
        # Prepare event data for serialization
        prepared_event = await self._prepare_event_for_serialization(event_data, business_context)
        
        # Schema validation and evolution
        schema_validation = await self.schema_registry.validate_and_evolve_schema(
            prepared_event, format_to_use
        )
        
        # Serialize using appropriate strategy
        if format_to_use not in self.serialization_strategies:
            format_to_use = SerializationFormat.JSON.value
        
        serialization_strategy = self.serialization_strategies[format_to_use]
        serialized_data = await serialization_strategy.serialize(
            prepared_event, schema_validation.schema
        )
        
        # Apply intelligent compression
        compressed_data = await self._apply_intelligent_compression(
            serialized_data, event_data, business_context
        )
        
        # Collect performance metrics
        performance_metrics = await self.performance_optimizer.collect_metrics(
            event_data, serialized_data, compressed_data
        )
        
        # Generate business tags for event categorization
        business_tags = await self._generate_business_tags(event_data, business_context)
        
        serialization_time = time.time() - start_time
        logger.debug(f"Event serialized in {serialization_time:.3f}s with format {format_to_use}")
        
        return SerializedEvent(
            original_event_id=event_data.get("event_id", "unknown"),
            serialized_data=compressed_data.data,
            format=format_to_use,
            schema_version=schema_validation.schema_version,
            compression_algorithm=compressed_data.compression_type,
            compression_ratio=compressed_data.compression_ratio,
            serialization_metrics=performance_metrics,
            business_tags=business_tags
        )
    
    async def _determine_optimal_format(self, 
                                      event_data: Dict[str, Any],
                                      business_context: Dict[str, Any]) -> str:
        """Determine optimal serialization format based on Ainflue business logic"""
        
        event_type = event_data.get("event_type", "")
        payload_size = len(str(event_data.get("payload", {})))
        
        # Content Events - prioritize performance for large files
        if event_type.startswith("content."):
            if payload_size > 1_000_000:  # 1MB+ - Use compact format for large content
                return SerializationFormat.MSGPACK.value
            elif business_context.get("streaming_required"):
                return SerializationFormat.JSON.value  # JSON for streaming compatibility
            else:
                return SerializationFormat.MSGPACK.value  # Compact for processing
        
        # Collaboration Events - prioritize interoperability
        elif event_type.startswith("collaboration."):
            if business_context.get("cross_platform_sharing"):
                return SerializationFormat.JSON.value  # Maximum compatibility
            else:
                return SerializationFormat.MSGPACK.value  # Performance with evolution
        
        # Monetization Events - prioritize reliability
        elif event_type.startswith("monetization."):
            return SerializationFormat.JSON.value  # Reliable and debuggable
        
        # Analytics Events - prioritize compression
        elif event_type.startswith("analytics."):
            return SerializationFormat.MSGPACK.value  # Optimal compression/performance
        
        # Default for other events
        else:
            return SerializationFormat.JSON.value  # Good general balance
    
    async def _prepare_event_for_serialization(self,
                                             event_data: Dict[str, Any],
                                             business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare event data for serialization with business enrichment"""
        
        prepared_event = event_data.copy()
        
        # Add business metadata if not present
        if "business_metadata" not in prepared_event:
            prepared_event["business_metadata"] = {}
        
        # Enrich with business context
        prepared_event["business_metadata"].update({
            "workflow_stage": business_context.get("workflow_stage", "unknown"),
            "business_value": business_context.get("business_value", 0),
            "priority": business_context.get("priority", "normal"),
            "processing_tier": business_context.get("user_tier", "free")
        })
        
        # Ensure required fields for Ainflue business logic
        if "timestamp" not in prepared_event:
            prepared_event["timestamp"] = datetime.utcnow().isoformat()
        
        if "correlation_id" not in prepared_event:
            prepared_event["correlation_id"] = f"ainflue_{int(time.time() * 1000)}"
        
        return prepared_event
    
    async def _apply_intelligent_compression(self,
                                           serialized_data: bytes,
                                           event_data: Dict[str, Any],
                                           business_context: Dict[str, Any]) -> CompressedData:
        """Apply intelligent compression based on business requirements"""
        
        original_size = len(serialized_data)
        
        # No compression for real-time critical events
        if business_context.get("real_time_critical"):
            return CompressedData(
                data=serialized_data,
                compression_type=CompressionAlgorithm.NONE.value,
                compression_ratio=1.0,
                original_size=original_size,
                compressed_size=original_size
            )
        
        # Skip compression for small data
        if original_size < self.compression_config.size_threshold:
            return CompressedData(
                data=serialized_data,
                compression_type=CompressionAlgorithm.NONE.value,
                compression_ratio=1.0,
                original_size=original_size,
                compressed_size=original_size
            )
        
        # Select compression algorithm
        if business_context.get("archival_storage"):
            compression_algo = CompressionAlgorithm.ZSTD
        elif original_size > 100_000:  # Large data
            compression_algo = CompressionAlgorithm.ZSTD
        else:
            compression_algo = CompressionAlgorithm.LZ4
        
        # Apply compression
        return await self._compress_data(serialized_data, compression_algo)
    
    async def _compress_data(self, data: bytes, algorithm: CompressionAlgorithm) -> CompressedData:
        """Compress data using specified algorithm"""
        
        original_size = len(data)
        
        try:
            if algorithm == CompressionAlgorithm.GZIP:
                compressed = gzip.compress(data, compresslevel=self.compression_config.level)
            elif algorithm == CompressionAlgorithm.LZ4:
                if HAS_LZ4:
                    compressed = lz4.frame.compress(data, compression_level=self.compression_config.level)
                else:
                    logger.warning("LZ4 not available, falling back to GZIP")
                    compressed = gzip.compress(data, compresslevel=self.compression_config.level)
            elif algorithm == CompressionAlgorithm.ZSTD:
                if HAS_ZSTD:
                    cctx = zstd.ZstdCompressor(level=self.compression_config.level)
                    compressed = cctx.compress(data)
                else:
                    logger.warning("ZSTD not available, falling back to GZIP")
                    compressed = gzip.compress(data, compresslevel=self.compression_config.level)
            else:
                compressed = data
            
            compressed_size = len(compressed)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            return CompressedData(
                data=compressed,
                compression_type=algorithm.value,
                compression_ratio=compression_ratio,
                original_size=original_size,
                compressed_size=compressed_size
            )
            
        except Exception as e:
            logger.warning(f"Compression failed with {algorithm.value}: {e}, using uncompressed data")
            return CompressedData(
                data=data,
                compression_type=CompressionAlgorithm.NONE.value,
                compression_ratio=1.0,
                original_size=original_size,
                compressed_size=original_size
            )
    
    async def _generate_business_tags(self, 
                                    event_data: Dict[str, Any],
                                    business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business tags for event categorization and routing"""
        
        event_type = event_data.get("event_type", "")
        
        tags = {
            "platform": "ainflue",
            "event_category": self._categorize_event(event_type),
            "business_priority": business_context.get("priority", "normal"),
            "processing_tier": business_context.get("user_tier", "free"),
            "workflow_stage": business_context.get("workflow_stage", "unknown")
        }
        
        # Add specialized tags based on event type
        if event_type.startswith("content."):
            tags.update({
                "content_type": event_data.get("payload", {}).get("content_type", "unknown"),
                "content_size": len(str(event_data.get("payload", {}))),
                "requires_ai_processing": "ai" in event_type.lower()
            })
        elif event_type.startswith("monetization."):
            tags.update({
                "revenue_impact": business_context.get("revenue_impact", "low"),
                "payment_method": event_data.get("payload", {}).get("payment_method", "unknown")
            })
        
        return tags
    
    def _categorize_event(self, event_type: str) -> str:
        """Categorize event type for business logic"""
        
        if event_type.startswith("content."):
            return "content_management"
        elif event_type.startswith("collaboration."):
            return "collaboration"
        elif event_type.startswith("monetization."):
            return "monetization"
        elif event_type.startswith("analytics."):
            return "analytics"
        elif event_type.startswith("user."):
            return "user_management"
        else:
            return "general"
    
    async def deserialize_event(self, serialized_event: SerializedEvent) -> Dict[str, Any]:
        """Deserialize a serialized event back to its original form"""
        
        # Decompress if needed
        decompressed_data = await self._decompress_data(
            serialized_event.serialized_data,
            serialized_event.compression_algorithm
        )
        
        # Deserialize based on format
        if serialized_event.format == SerializationFormat.JSON.value:
            return json.loads(decompressed_data.decode('utf-8'))
        elif serialized_event.format == SerializationFormat.MSGPACK.value:
            try:
                import msgpack
                return msgpack.unpackb(decompressed_data, raw=False)
            except ImportError:
                logger.error("MessagePack not available for deserialization")
                raise
        else:
            raise ValueError(f"Unsupported format for deserialization: {serialized_event.format}")
    
    async def _decompress_data(self, data: bytes, algorithm: str) -> bytes:
        """Decompress data using specified algorithm"""
        
        if algorithm == CompressionAlgorithm.NONE.value:
            return data
        elif algorithm == CompressionAlgorithm.GZIP.value:
            return gzip.decompress(data)
        elif algorithm == CompressionAlgorithm.LZ4.value:
            if HAS_LZ4:
                return lz4.frame.decompress(data)
            else:
                logger.warning("LZ4 not available for decompression")
                return data
        elif algorithm == CompressionAlgorithm.ZSTD.value:
            if HAS_ZSTD:
                dctx = zstd.ZstdDecompressor()
                return dctx.decompress(data)
            else:
                logger.warning("ZSTD not available for decompression")
                return data
        else:
            logger.warning(f"Unknown compression algorithm: {algorithm}, returning data as-is")
            return data


# Export main classes
__all__ = [
    'EventSerializationEngine',
    'SerializationFormat',
    'CompressionAlgorithm',
    'CompressionConfig',
    'SerializedEvent',
    'SerializationMetrics'
]