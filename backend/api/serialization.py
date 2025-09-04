"""Serialization - Data Serializers and Formatters
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
    
    def __init__(self):
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
    
    def _dict_to_xml(self, data: Dict[str, Any], parent: ET.Element):
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
    
    def __init__(self, serialization_service: SerializationService = None):
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
        
        def generate():
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
    "ResponseBuilder"
]