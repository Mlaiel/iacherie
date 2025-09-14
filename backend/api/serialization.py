"""Serialization - Data Serializers and Formatters
import asyncio

Consolidated serialization functionality for API data transformation.

This module consolidates serialization from:
- Response data serialization (JSON, XML, CSV, Excel)
- Data transformation and formatting
- API response standardization 
- Content-specific serializers (audio, video, image metadata)
- Export formatters for different platforms
- Data compression and optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Union, Type
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
import json
import csv
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO
import base64
import gzip

from fastapi import Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import pandas as pd

# ========================================
# SERIALIZATION ENUMS
# ========================================

class SerializationFormat(str, Enum):
    """Supported serialization formats"""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    EXCEL = "excel"
    YAML = "yaml"
    BINARY = "binary"

class CompressionType(str, Enum):
    """Supported compression types"""
    NONE = "none"
    GZIP = "gzip"
    DEFLATE = "deflate"
    BROTLI = "brotli"

# ========================================
# BASE SERIALIZATION MODELS
# ========================================

class BaseSerializationModel(BaseModel):
    """Base model for serialization with common fields"""
    
    class Config:
    """Config: class implementation"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            time: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
            set: lambda v: list(v)
        }
        
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to dictionary with proper serialization"""
        return self.dict(exclude_none=exclude_none, by_alias=True)

class APIResponse(BaseSerializationModel):
    """Standard API response format"""
    success: bool = Field(default=True, description="Request success status")
    message: str = Field(default="Operation completed successfully", description="Response message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="Response metadata")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(default=None, description="Request correlation ID")

class PaginatedResponse(BaseSerializationModel):
    """Paginated response format"""
    items: List[Dict[str, Any]] = Field(default_factory=list, description="Page items")
    total: int = Field(default=0, description="Total items available")
    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=20, description="Items per page")
    pages: int = Field(default=1, description="Total pages")
    has_next: bool = Field(default=False, description="Has next page")
    has_prev: bool = Field(default=False, description="Has previous page")

# ========================================
# CONTENT SERIALIZATION MODELS
# ========================================

class ContentMetadataSerializer(BaseSerializationModel):
    """Content metadata serialization"""
    id: str = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    content_type: str = Field(..., description="Type of content")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    duration: Optional[float] = Field(None, description="Duration for media content")
    dimensions: Optional[Dict[str, int]] = Field(None, description="Image/video dimensions")
    bitrate: Optional[int] = Field(None, description="Audio/video bitrate")
    frame_rate: Optional[float] = Field(None, description="Video frame rate")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    creator_id: str = Field(..., description="Content creator ID")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    is_public: bool = Field(default=True, description="Public visibility")

class UserProfileSerializer(BaseSerializationModel):
    """User profile serialization"""
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    creator_type: str = Field(..., description="Type of creator")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field(None, description="User biography")
    website: Optional[str] = Field(None, description="User website")
    social_links: Dict[str, str] = Field(default_factory=dict, description="Social media links")
    verification_status: str = Field(default="unverified", description="Account verification status")
    subscription_tier: str = Field(default="free", description="Subscription tier")
    created_at: datetime = Field(..., description="Account creation date")
    last_active: datetime = Field(..., description="Last activity timestamp")

class CollaborationSerializer(BaseSerializationModel):
    """Collaboration data serialization"""
    id: str = Field(..., description="Collaboration ID")
    title: str = Field(..., description="Collaboration title")
    description: str = Field(..., description="Collaboration description")
    status: str = Field(..., description="Collaboration status")
    creator_id: str = Field(..., description="Collaboration creator ID")
    collaborators: List[Dict[str, Any]] = Field(default_factory=list, description="Collaborators")
    revenue_split: Dict[str, Decimal] = Field(default_factory=dict, description="Revenue sharing")
    deadline: Optional[datetime] = Field(None, description="Collaboration deadline")
    budget: Optional[Decimal] = Field(None, description="Collaboration budget")
    requirements: List[str] = Field(default_factory=list, description="Collaboration requirements")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

# ========================================
# ANALYTICS SERIALIZATION MODELS
# ========================================

class AnalyticsDataSerializer(BaseSerializationModel):
    """Analytics data serialization"""
    metric_name: str = Field(..., description="Metric name")
    metric_value: Union[int, float, Decimal] = Field(..., description="Metric value")
    metric_type: str = Field(..., description="Type of metric (count, percentage, currency)")
    period: str = Field(..., description="Time period")
    timestamp: datetime = Field(..., description="Measurement timestamp")
    dimensions: Dict[str, Any] = Field(default_factory=dict, description="Additional dimensions")

class PerformanceReportSerializer(BaseSerializationModel):
    """Performance report serialization"""
    content_id: str = Field(..., description="Content ID")
    views: int = Field(default=0, description="Total views")
    likes: int = Field(default=0, description="Total likes")
    shares: int = Field(default=0, description="Total shares")
    comments: int = Field(default=0, description="Total comments")
    engagement_rate: float = Field(default=0.0, description="Engagement rate percentage")
    reach: int = Field(default=0, description="Total reach")
    impressions: int = Field(default=0, description="Total impressions")
    revenue: Decimal = Field(default=Decimal('0'), description="Generated revenue")
    period_start: datetime = Field(..., description="Report period start")
    period_end: datetime = Field(..., description="Report period end")

# ========================================
# SERIALIZATION SERVICE
# ========================================

class SerializationService:
    """Main serialization service"""
    
    def __init__(self) -> None:
        self.default_format = SerializationFormat.JSON
        self.compression_enabled = True
    
    def serialize_response(
        self, 
        data: Any, 
        format_type: SerializationFormat = SerializationFormat.JSON,
        compression: CompressionType = CompressionType.NONE
    ) -> Union[str, bytes]:
        """Serialize data to specified format"""
        
        if format_type == SerializationFormat.JSON:
            serialized = self._serialize_json(data)
        elif format_type == SerializationFormat.XML:
            serialized = self._serialize_xml(data)
        elif format_type == SerializationFormat.CSV:
            serialized = self._serialize_csv(data)
        elif format_type == SerializationFormat.EXCEL:
            serialized = self._serialize_excel(data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        # Apply compression if requested
        if compression != CompressionType.NONE:
            serialized = self._compress_data(serialized, compression)
        
        return serialized
    
    def _serialize_json(self, data: Any) -> str:
        """Serialize to JSON format"""
        if isinstance(data, BaseModel):
            return data.json(by_alias=True, exclude_none=True)
        
        return json.dumps(
            data,
            default=self._json_encoder,
            ensure_ascii=False,
            indent=None,
            separators=(',', ':')
        )
    
    def _serialize_xml(self, data: Any) -> str:
        """Serialize to XML format"""
        if isinstance(data, BaseModel):
            data = data.dict(by_alias=True, exclude_none=True)
        
        root = ET.Element("response")
        self._dict_to_xml(data, root)
        
        return ET.tostring(root, encoding='unicode', method='xml')
    
    def _serialize_csv(self, data: Any) -> str:
        """Serialize to CSV format"""
        if isinstance(data, BaseModel):
            data = data.dict(by_alias=True, exclude_none=True)
        
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # List of dictionaries - create CSV
            output = StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return output.getvalue()
        elif isinstance(data, dict):
            # Single dictionary - create simple CSV
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return output.getvalue()
        else:
            raise ValueError("Data must be a list of dictionaries or a dictionary for CSV serialization")
    
    def _serialize_excel(self, data: Any) -> bytes:
        """Serialize to Excel format"""
        if isinstance(data, BaseModel):
            data = data.dict(by_alias=True, exclude_none=True)
        
        output = BytesIO()
        
        if isinstance(data, list) and data and isinstance(data[0], dict):
            df = pd.DataFrame(data)
            df.to_excel(output, index=False, engine='openpyxl')
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
            df.to_excel(output, index=False, engine='openpyxl')
        else:
            raise ValueError("Data must be a list of dictionaries or a dictionary for Excel serialization")
        
        output.seek(0)
        return output.read()
    
    def _dict_to_xml(self, data -> None: Dict[str, Any], parent -> None: ET.Element) -> None:
        """Convert dictionary to XML elements"""
        for key, value in data.items():
            element = ET.SubElement(parent, str(key))
            
            if isinstance(value, dict):
                self._dict_to_xml(value, element)
            elif isinstance(value, list):
                for item in value:
                    item_element = ET.SubElement(element, "item")
                    if isinstance(item, dict):
                        self._dict_to_xml(item, item_element)
                    else:
                        item_element.text = str(item)
            else:
                element.text = str(value)
    
    def _json_encoder(self, obj: Any) -> Any:
        """Custom JSON encoder for special types"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, time):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, 'dict'):
            return obj.dict()
        
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _compress_data(self, data: Union[str, bytes], compression: CompressionType) -> bytes:
        """Compress data using specified compression type"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if compression == CompressionType.GZIP:
            return gzip.compress(data)
        elif compression == CompressionType.DEFLATE:
            import zlib
            return zlib.compress(data)
        elif compression == CompressionType.BROTLI:
            import brotli
            return brotli.compress(data)
        
        return data

# ========================================
# RESPONSE BUILDERS
# ========================================

class ResponseBuilder:
    """Builder for creating standardized API responses"""
    
    def __init__(self, serialization_service -> None: SerializationService = None) -> None:
        self.serializer = serialization_service or SerializationService()
    
    def success_response(
        self, 
        data: Any = None, 
        message: str = "Operation completed successfully",
        meta: Dict[str, Any] = None,
        request_id: str = None
    ) -> JSONResponse:
        """Create success response"""
        
        response_data = APIResponse(
            success=True,
            message=message,
            data=data,
            meta=meta,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_data.dict(exclude_none=True)
        )
    
    def error_response(
        self,
        message: str = "An error occurred",
        errors: List[str] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        request_id: str = None
    ) -> JSONResponse:
        """Create error response"""
        
        response_data = APIResponse(
            success=False,
            message=message,
            errors=errors or [],
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status_code,
            content=response_data.dict(exclude_none=True)
        )
    
    def paginated_response(
        self,
        items: List[Any],
        total: int,
        page: int,
        per_page: int,
        message: str = "Data retrieved successfully",
        request_id: str = None
    ) -> JSONResponse:
        """Create paginated response"""
        
        pages = (total + per_page - 1) // per_page
        has_next = page < pages
        has_prev = page > 1
        
        paginated_data = PaginatedResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        response_data = APIResponse(
            success=True,
            message=message,
            data=paginated_data.dict(),
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_data.dict(exclude_none=True)
        )
    
    def file_response(
        self,
        content: bytes,
        filename: str,
        mime_type: str = "application/octet-stream"
    ) -> StreamingResponse:
        """Create file download response"""
        
        def generate() -> None:
            yield content
        
        return StreamingResponse(
            generate(),
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(content))
            }
        )

# ========================================
# CONTENT-SPECIFIC SERIALIZERS
# ========================================

class AudioMetadataSerializer(BaseSerializationModel):
    """Audio content metadata serialization"""
    duration: float = Field(..., description="Audio duration in seconds")
    bitrate: int = Field(..., description="Audio bitrate")
    sample_rate: int = Field(..., description="Sample rate in Hz")
    channels: int = Field(..., description="Number of audio channels")
    format: str = Field(..., description="Audio format")
    artist: Optional[str] = Field(None, description="Artist name")
    album: Optional[str] = Field(None, description="Album name")
    genre: Optional[str] = Field(None, description="Music genre")

class VideoMetadataSerializer(BaseSerializationModel):
    """Video content metadata serialization"""
    duration: float = Field(..., description="Video duration in seconds")
    width: int = Field(..., description="Video width in pixels")
    height: int = Field(..., description="Video height in pixels")
    frame_rate: float = Field(..., description="Video frame rate")
    bitrate: int = Field(..., description="Video bitrate")
    codec: str = Field(..., description="Video codec")
    audio_codec: Optional[str] = Field(None, description="Audio codec")
    subtitle_tracks: List[str] = Field(default_factory=list, description="Available subtitle tracks")

class ImageMetadataSerializer(BaseSerializationModel):
    """Image content metadata serialization"""
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    format: str = Field(..., description="Image format")
    color_space: str = Field(..., description="Color space")
    has_transparency: bool = Field(default=False, description="Has transparency channel")
    dpi: Optional[int] = Field(None, description="Image DPI")
    camera_info: Optional[Dict[str, Any]] = Field(None, description="Camera EXIF data")


# ========================================
# ENTERPRISE PERFORMANCE SERIALIZATION
# ========================================

class HighPerformanceSerializer:
    """Enterprise high-performance serializer with optimizations"""
    
    def __init__(self) -> None:
        self.compression_engines = {
            CompressionType.GZIP: self._gzip_compress,
            CompressionType.BROTLI: self._brotli_compress,
            CompressionType.LZ4: self._lz4_compress,
            CompressionType.ZSTD: self._zstd_compress
        }
        self.serialization_cache = {}
        self.performance_monitor = SerializationPerformanceMonitor()
    
    async def serialize_with_optimization(
        self,
        data: Any,
        format_type: SerializationFormat = SerializationFormat.JSON,
        compression: CompressionType = CompressionType.GZIP,
        optimization_level: int = 1
    ) -> Dict[str, Any]:
        """Serialize data with performance optimizations"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(data, format_type, compression)
            if cache_key in self.serialization_cache:
                cached_result = self.serialization_cache[cache_key]
                await self.performance_monitor.record_cache_hit(cache_key)
                return cached_result
            
            # Serialize based on format
            if format_type == SerializationFormat.JSON:
                serialized = await self._optimize_json_serialization(data, optimization_level)
            elif format_type == SerializationFormat.MSGPACK:
                serialized = await self._optimize_msgpack_serialization(data)
            elif format_type == SerializationFormat.PROTOBUF:
                serialized = await self._optimize_protobuf_serialization(data)
            elif format_type == SerializationFormat.AVRO:
                serialized = await self._optimize_avro_serialization(data)
            else:
                serialized = json.dumps(data, default=str).encode()
            
            # Apply compression if requested
            if compression != CompressionType.NONE:
                compressed_data = await self.compression_engines[compression](serialized)
                compression_ratio = len(serialized) / len(compressed_data)
            else:
                compressed_data = serialized
                compression_ratio = 1.0
            
            # Build result
            result = {
                "data": compressed_data,
                "format": format_type.value,
                "compression": compression.value,
                "original_size": len(serialized),
                "compressed_size": len(compressed_data),
                "compression_ratio": compression_ratio,
                "serialization_time_ms": (time.time() - start_time) * 1000,
                "optimized": True
            }
            
            # Cache if beneficial
            if len(compressed_data) < 10 * 1024 * 1024:  # Cache only if < 10MB
                self.serialization_cache[cache_key] = result
            
            await self.performance_monitor.record_serialization(result)
            
            return result
            
        except Exception as e:
            return {
                "error": f"Serialization failed: {e}",
                "format": format_type.value,
                "serialization_time_ms": (time.time() - start_time) * 1000
            }
    
    async def _optimize_json_serialization(self, data: Any, optimization_level: int) -> bytes:
        """Optimized JSON serialization"""
        if optimization_level >= 2:
            # Use ujson for better performance if available
            try:
                import ujson
                return ujson.dumps(data, ensure_ascii=False).encode('utf-8')
            except ImportError:
                pass
        
        if optimization_level >= 1:
            # Remove whitespace, use compact separators
            return json.dumps(data, default=str, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
        
        # Standard JSON
        return json.dumps(data, default=str).encode('utf-8')
    
    async def _optimize_msgpack_serialization(self, data: Any) -> bytes:
        """MessagePack serialization for binary efficiency"""
        try:
            import msgpack
            return msgpack.packb(data, use_bin_type=True)
        except ImportError:
            # Fallback to JSON
            return json.dumps(data, default=str).encode('utf-8')
    
    async def _optimize_protobuf_serialization(self, data: Any) -> bytes:
        """Protocol Buffers serialization for schema-based efficiency"""
        # Mock implementation - would use actual protobuf schemas
        return json.dumps(data, default=str).encode('utf-8')
    
    async def _optimize_avro_serialization(self, data: Any) -> bytes:
        """Apache Avro serialization for schema evolution"""
        # Mock implementation - would use actual Avro schemas
        return json.dumps(data, default=str).encode('utf-8')
    
    async def _gzip_compress(self, data: bytes) -> bytes:
        """GZIP compression"""
        import gzip
        return gzip.compress(data, compresslevel=6)
    
    async def _brotli_compress(self, data: bytes) -> bytes:
        """Brotli compression for better ratios"""
        try:
            import brotli
            return brotli.compress(data, quality=6)
        except ImportError:
            return await self._gzip_compress(data)
    
    async def _lz4_compress(self, data: bytes) -> bytes:
        """LZ4 compression for speed"""
        try:
            import lz4.frame
            return lz4.frame.compress(data)
        except ImportError:
            return await self._gzip_compress(data)
    
    async def _zstd_compress(self, data: bytes) -> bytes:
        """Zstandard compression for balanced speed/ratio"""
        try:
            import zstd
            return zstd.compress(data, level=6)
        except ImportError:
            return await self._gzip_compress(data)
    
    def _generate_cache_key(self, data: Any, format_type: SerializationFormat, compression: CompressionType) -> str:
        """Generate cache key for serialization result"""
        import hashlib
        data_hash = hashlib.md5(str(data).encode()).hexdigest()
        return f"{format_type.value}_{compression.value}_{data_hash}"


class MultiFormatBatchSerializer:
    """Batch serializer for handling multiple formats efficiently"""
    
    def __init__(self) -> None:
        self.high_perf_serializer = HighPerformanceSerializer()
        self.batch_processor = BatchProcessor()
    
    async def serialize_batch(
        self,
        data_items: List[Dict[str, Any]],
        format_preferences: Dict[str, SerializationFormat] = None,
        compression_preferences: Dict[str, CompressionType] = None
    ) -> Dict[str, Any]:
        """Serialize multiple items in batch with format-specific optimizations"""
        try:
            # Group items by format requirements
            format_groups = self._group_by_format(data_items, format_preferences)
            
            # Process each format group
            results = {}
            for format_type, items in format_groups.items():
                compression = compression_preferences.get(format_type.value, CompressionType.GZIP)
                
                batch_result = await self.batch_processor.process_format_batch(
                    items, format_type, compression
                )
                results[format_type.value] = batch_result
            
            return {
                "batch_results": results,
                "total_items": len(data_items),
                "formats_used": list(results.keys()),
                "processing_time_ms": sum(r.get("processing_time_ms", 0) for r in results.values())
            }
            
        except Exception as e:
            return {"error": f"Batch serialization failed: {e}"}
    
    def _group_by_format(
        self, 
        data_items: List[Dict[str, Any]], 
        format_preferences: Dict[str, SerializationFormat]
    ) -> Dict[SerializationFormat, List[Dict[str, Any]]]:
        """Group data items by their preferred serialization format"""
        groups = {}
        
        for item in data_items:
            item_type = item.get("type", "default")
            format_type = format_preferences.get(item_type, SerializationFormat.JSON)
            
            if format_type not in groups:
                groups[format_type] = []
            groups[format_type].append(item)
        
        return groups


class SerializationPerformanceMonitor:
    """Monitor serialization performance and optimize accordingly"""
    
    def __init__(self) -> None:
        self.performance_stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_serializations": 0,
            "avg_serialization_time": 0.0,
            "compression_stats": {}
        }
    
    async def record_cache_hit(self, cache_key -> None: str) -> None:
        """Record cache hit for performance tracking"""
        self.performance_stats["cache_hits"] += 1
    
    async def record_serialization(self, result -> None: Dict[str, Any]) -> None:
        """Record serialization performance metrics"""
        self.performance_stats["total_serializations"] += 1
        self.performance_stats["cache_misses"] += 1
        
        # Update average serialization time
        current_avg = self.performance_stats["avg_serialization_time"]
        total_count = self.performance_stats["total_serializations"]
        new_time = result.get("serialization_time_ms", 0)
        
        self.performance_stats["avg_serialization_time"] = (
            (current_avg * (total_count - 1) + new_time) / total_count
        )
        
        # Track compression efficiency
        compression_type = result.get("compression", "none")
        if compression_type not in self.performance_stats["compression_stats"]:
            self.performance_stats["compression_stats"][compression_type] = {
                "usage_count": 0,
                "avg_ratio": 0.0,
                "total_size_saved": 0
            }
        
        compression_stat = self.performance_stats["compression_stats"][compression_type]
        compression_stat["usage_count"] += 1
        
        if "compression_ratio" in result:
            ratio = result["compression_ratio"]
            current_avg_ratio = compression_stat["avg_ratio"]
            usage_count = compression_stat["usage_count"]
            
            compression_stat["avg_ratio"] = (
                (current_avg_ratio * (usage_count - 1) + ratio) / usage_count
            )
            
            size_saved = result.get("original_size", 0) - result.get("compressed_size", 0)
            compression_stat["total_size_saved"] += size_saved
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        total_requests = self.performance_stats["cache_hits"] + self.performance_stats["cache_misses"]
        cache_hit_rate = (self.performance_stats["cache_hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_performance": {
                "hit_rate_percent": cache_hit_rate,
                "total_hits": self.performance_stats["cache_hits"],
                "total_misses": self.performance_stats["cache_misses"]
            },
            "serialization_performance": {
                "total_serializations": self.performance_stats["total_serializations"],
                "avg_time_ms": self.performance_stats["avg_serialization_time"]
            },
            "compression_analysis": self.performance_stats["compression_stats"]
        }


class BatchProcessor:
    """Process serialization in batches for better performance"""
    
    async def process_format_batch(
        self,
        items: List[Dict[str, Any]],
        format_type: SerializationFormat,
        compression: CompressionType
    ) -> Dict[str, Any]:
        """Process a batch of items with the same format"""
        start_time = time.time()
        
        try:
            # Serialize all items in the batch
            serialized_items = []
            total_original_size = 0
            total_compressed_size = 0
            
            for item in items:
                # Use high-performance serializer
                high_perf_serializer = HighPerformanceSerializer()
                result = await high_perf_serializer.serialize_with_optimization(
                    item, format_type, compression, optimization_level=2
                )
                
                if "error" not in result:
                    serialized_items.append(result)
                    total_original_size += result.get("original_size", 0)
                    total_compressed_size += result.get("compressed_size", 0)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "items_processed": len(serialized_items),
                "total_original_size": total_original_size,
                "total_compressed_size": total_compressed_size,
                "overall_compression_ratio": total_original_size / total_compressed_size if total_compressed_size > 0 else 1.0,
                "processing_time_ms": processing_time,
                "throughput_items_per_second": len(items) / (processing_time / 1000) if processing_time > 0 else 0,
                "serialized_data": serialized_items
            }
            
        except Exception as e:
            return {
                "error": f"Batch processing failed: {e}",
                "items_attempted": len(items),
                "processing_time_ms": (time.time() - start_time) * 1000
            }


# Add missing imports and compression types
import time

class CompressionType(str, Enum):
    """Enhanced compression types"""
    NONE = "none"
    GZIP = "gzip"
    BROTLI = "brotli"
    LZ4 = "lz4"
    ZSTD = "zstd"


# Create global instances
high_performance_serializer = HighPerformanceSerializer()
multi_format_batch_serializer = MultiFormatBatchSerializer()


# ========================================
# EXPORTS
# ========================================

__all__ = [
    "SerializationFormat",
    "CompressionType",
    "BaseSerializationModel",
    "APIResponse",
    "PaginatedResponse",
    "ContentMetadataSerializer",
    "UserProfileSerializer",
    "CollaborationSerializer",
    "AnalyticsDataSerializer",
    "PerformanceReportSerializer",
    "AudioMetadataSerializer",
    "VideoMetadataSerializer",
    "ImageMetadataSerializer",
    "SerializationService",
    "ResponseBuilder",
    "HighPerformanceSerializer",
    "MultiFormatBatchSerializer",
    "SerializationPerformanceMonitor",
    "BatchProcessor",
    "high_performance_serializer",
    "multi_format_batch_serializer"
]