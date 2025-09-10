"""
📄 Multi-format Serialization Manager
Enterprise serialization system for complex data structures

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union, Type, Protocol
from pydantic import BaseModel, Field
from enum import Enum
import json
import yaml
import pickle
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime, date
import uuid
import decimal


class SerializationFormat(str, Enum):
    """Supported serialization formats"""
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    PICKLE = "pickle"
    CSV = "csv"
    BINARY = "binary"
    PROTOBUF = "protobuf"
    MSGPACK = "msgpack"


class SerializationContext(BaseModel):
    """Serialization context and configuration"""
    format: SerializationFormat = Field(..., description="Target serialization format")
    include_metadata: bool = Field(default=True, description="Include metadata in serialization")
    compress: bool = Field(default=False, description="Apply compression")
    encryption_key: Optional[str] = Field(None, description="Encryption key for sensitive data")
    custom_encoders: Dict[str, Any] = Field(default_factory=dict, description="Custom type encoders")
    schema_version: str = Field(default="1.0", description="Schema version for compatibility")


class SerializationResult(BaseModel):
    """Result of serialization operation"""
    success: bool = Field(..., description="Whether serialization succeeded")
    format: SerializationFormat = Field(..., description="Serialization format used")
    data: Optional[Union[str, bytes]] = Field(None, description="Serialized data")
    size_bytes: int = Field(default=0, description="Size of serialized data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Serialization metadata")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class DeserializationResult(BaseModel):
    """Result of deserialization operation"""
    success: bool = Field(..., description="Whether deserialization succeeded")
    format: SerializationFormat = Field(..., description="Source format")
    data: Optional[Any] = Field(None, description="Deserialized data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Deserialization metadata")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class SerializationAdapter(ABC):
    """Abstract base for serialization adapters"""
    
    @abstractmethod
    async def serialize(self, data: Any, context: SerializationContext) -> SerializationResult:
        """Serialize data to specific format"""
        pass
    
    @abstractmethod
    async def deserialize(self, serialized_data: Union[str, bytes], context: SerializationContext) -> DeserializationResult:
        """Deserialize data from specific format"""
        pass
    
    @abstractmethod
    def supports_format(self, format: SerializationFormat) -> bool:
        """Check if adapter supports given format"""
        pass


class JSONSerializationAdapter(SerializationAdapter):
    """JSON serialization adapter with enhanced features"""
    
    def __init__(self):
        self.custom_encoders = {
            datetime: lambda x: x.isoformat(),
            date: lambda x: x.isoformat(),
            decimal.Decimal: lambda x: float(x),
            uuid.UUID: lambda x: str(x),
            set: lambda x: list(x),
            frozenset: lambda x: list(x),
        }
    
    async def serialize(self, data: Any, context: SerializationContext) -> SerializationResult:
        """Serialize to JSON format"""
        try:
            # Prepare data with custom encoders
            serializable_data = self._make_serializable(data, context)
            
            # Add metadata if requested
            if context.include_metadata:
                wrapped_data = {
                    "_metadata": {
                        "format": context.format.value,
                        "schema_version": context.schema_version,
                        "timestamp": datetime.utcnow().isoformat(),
                        "serializer": "JSONSerializationAdapter"
                    },
                    "data": serializable_data
                }
            else:
                wrapped_data = serializable_data
            
            # Serialize to JSON
            json_str = json.dumps(wrapped_data, ensure_ascii=False, indent=2 if not context.compress else None)
            json_bytes = json_str.encode('utf-8')
            
            # Apply compression if requested
            if context.compress:
                json_bytes = await self._compress_data(json_bytes)
            
            # Apply encryption if key provided
            if context.encryption_key:
                json_bytes = await self._encrypt_data(json_bytes, context.encryption_key)
            
            return SerializationResult(
                success=True,
                format=SerializationFormat.JSON,
                data=json_bytes.decode('utf-8') if not context.compress and not context.encryption_key else json_bytes,
                size_bytes=len(json_bytes),
                metadata={
                    "compressed": context.compress,
                    "encrypted": bool(context.encryption_key),
                    "encoding": "utf-8"
                }
            )
            
        except Exception as e:
            return SerializationResult(
                success=False,
                format=SerializationFormat.JSON,
                error_message=f"JSON serialization failed: {str(e)}"
            )
    
    async def deserialize(self, serialized_data: Union[str, bytes], context: SerializationContext) -> DeserializationResult:
        """Deserialize from JSON format"""
        try:
            # Convert to bytes if string
            if isinstance(serialized_data, str):
                data_bytes = serialized_data.encode('utf-8')
            else:
                data_bytes = serialized_data
            
            # Apply decryption if key provided
            if context.encryption_key:
                data_bytes = await self._decrypt_data(data_bytes, context.encryption_key)
            
            # Apply decompression if needed
            if context.compress:
                data_bytes = await self._decompress_data(data_bytes)
            
            # Parse JSON
            json_str = data_bytes.decode('utf-8')
            parsed_data = json.loads(json_str)
            
            # Extract data and metadata
            if isinstance(parsed_data, dict) and "_metadata" in parsed_data:
                actual_data = parsed_data["data"]
                metadata = parsed_data["_metadata"]
            else:
                actual_data = parsed_data
                metadata = {}
            
            return DeserializationResult(
                success=True,
                format=SerializationFormat.JSON,
                data=actual_data,
                metadata=metadata
            )
            
        except Exception as e:
            return DeserializationResult(
                success=False,
                format=SerializationFormat.JSON,
                error_message=f"JSON deserialization failed: {str(e)}"
            )
    
    def supports_format(self, format: SerializationFormat) -> bool:
        """Check if adapter supports JSON format"""
        return format == SerializationFormat.JSON
    
    def _make_serializable(self, obj: Any, context: SerializationContext) -> Any:
        """Convert object to JSON-serializable format"""
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        
        # Apply custom encoders
        obj_type = type(obj)
        if obj_type in self.custom_encoders:
            return self.custom_encoders[obj_type](obj)
        
        # Handle collections
        if isinstance(obj, (list, tuple)):
            return [self._make_serializable(item, context) for item in obj]
        
        if isinstance(obj, dict):
            return {
                key: self._make_serializable(value, context) 
                for key, value in obj.items()
            }
        
        # Handle Pydantic models
        if hasattr(obj, 'dict'):
            return self._make_serializable(obj.dict(), context)
        
        # Handle other objects by converting to dict
        if hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__, context)
        
        # Fallback: convert to string
        return str(obj)
    
    async def _compress_data(self, data: bytes) -> bytes:
        """Compress data using gzip"""
        import gzip
        return gzip.compress(data)
    
    async def _decompress_data(self, data: bytes) -> bytes:
        """Decompress data using gzip"""
        import gzip
        return gzip.decompress(data)
    
    async def _encrypt_data(self, data: bytes, key: str) -> bytes:
        """Encrypt data (placeholder implementation)"""
        # This would use a real encryption library like cryptography
        return data  # Placeholder
    
    async def _decrypt_data(self, data: bytes, key: str) -> bytes:
        """Decrypt data (placeholder implementation)"""
        # This would use a real encryption library like cryptography
        return data  # Placeholder


class YAMLSerializationAdapter(SerializationAdapter):
    """YAML serialization adapter"""
    
    async def serialize(self, data: Any, context: SerializationContext) -> SerializationResult:
        """Serialize to YAML format"""
        try:
            # Convert to serializable format
            serializable_data = self._make_yaml_serializable(data)
            
            # Add metadata if requested
            if context.include_metadata:
                wrapped_data = {
                    "_metadata": {
                        "format": context.format.value,
                        "schema_version": context.schema_version,
                        "timestamp": datetime.utcnow().isoformat(),
                        "serializer": "YAMLSerializationAdapter"
                    },
                    "data": serializable_data
                }
            else:
                wrapped_data = serializable_data
            
            # Serialize to YAML
            yaml_str = yaml.dump(wrapped_data, default_flow_style=False, allow_unicode=True)
            yaml_bytes = yaml_str.encode('utf-8')
            
            return SerializationResult(
                success=True,
                format=SerializationFormat.YAML,
                data=yaml_str,
                size_bytes=len(yaml_bytes),
                metadata={"encoding": "utf-8"}
            )
            
        except Exception as e:
            return SerializationResult(
                success=False,
                format=SerializationFormat.YAML,
                error_message=f"YAML serialization failed: {str(e)}"
            )
    
    async def deserialize(self, serialized_data: Union[str, bytes], context: SerializationContext) -> DeserializationResult:
        """Deserialize from YAML format"""
        try:
            # Convert to string if bytes
            if isinstance(serialized_data, bytes):
                yaml_str = serialized_data.decode('utf-8')
            else:
                yaml_str = serialized_data
            
            # Parse YAML
            parsed_data = yaml.safe_load(yaml_str)
            
            # Extract data and metadata
            if isinstance(parsed_data, dict) and "_metadata" in parsed_data:
                actual_data = parsed_data["data"]
                metadata = parsed_data["_metadata"]
            else:
                actual_data = parsed_data
                metadata = {}
            
            return DeserializationResult(
                success=True,
                format=SerializationFormat.YAML,
                data=actual_data,
                metadata=metadata
            )
            
        except Exception as e:
            return DeserializationResult(
                success=False,
                format=SerializationFormat.YAML,
                error_message=f"YAML deserialization failed: {str(e)}"
            )
    
    def supports_format(self, format: SerializationFormat) -> bool:
        """Check if adapter supports YAML format"""
        return format == SerializationFormat.YAML
    
    def _make_yaml_serializable(self, obj: Any) -> Any:
        """Convert object to YAML-serializable format"""
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        
        # Handle dates
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        
        # Handle UUID
        if isinstance(obj, uuid.UUID):
            return str(obj)
        
        # Handle Decimal
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        
        # Handle collections
        if isinstance(obj, (list, tuple)):
            return [self._make_yaml_serializable(item) for item in obj]
        
        if isinstance(obj, (set, frozenset)):
            return [self._make_yaml_serializable(item) for item in obj]
        
        if isinstance(obj, dict):
            return {
                key: self._make_yaml_serializable(value) 
                for key, value in obj.items()
            }
        
        # Handle Pydantic models
        if hasattr(obj, 'dict'):
            return self._make_yaml_serializable(obj.dict())
        
        # Handle other objects
        if hasattr(obj, '__dict__'):
            return self._make_yaml_serializable(obj.__dict__)
        
        # Fallback
        return str(obj)


class XMLSerializationAdapter(SerializationAdapter):
    """XML serialization adapter"""
    
    async def serialize(self, data: Any, context: SerializationContext) -> SerializationResult:
        """Serialize to XML format"""
        try:
            # Create root element
            root = ET.Element("data")
            
            # Add metadata if requested
            if context.include_metadata:
                metadata_elem = ET.SubElement(root, "metadata")
                ET.SubElement(metadata_elem, "format").text = context.format.value
                ET.SubElement(metadata_elem, "schema_version").text = context.schema_version
                ET.SubElement(metadata_elem, "timestamp").text = datetime.utcnow().isoformat()
                ET.SubElement(metadata_elem, "serializer").text = "XMLSerializationAdapter"
                
                # Create content element
                content_elem = ET.SubElement(root, "content")
            else:
                content_elem = root
            
            # Convert data to XML
            self._dict_to_xml(data, content_elem)
            
            # Generate XML string
            xml_str = ET.tostring(root, encoding='unicode', xml_declaration=True)
            xml_bytes = xml_str.encode('utf-8')
            
            return SerializationResult(
                success=True,
                format=SerializationFormat.XML,
                data=xml_str,
                size_bytes=len(xml_bytes),
                metadata={"encoding": "utf-8"}
            )
            
        except Exception as e:
            return SerializationResult(
                success=False,
                format=SerializationFormat.XML,
                error_message=f"XML serialization failed: {str(e)}"
            )
    
    async def deserialize(self, serialized_data: Union[str, bytes], context: SerializationContext) -> DeserializationResult:
        """Deserialize from XML format"""
        try:
            # Convert to string if bytes
            if isinstance(serialized_data, bytes):
                xml_str = serialized_data.decode('utf-8')
            else:
                xml_str = serialized_data
            
            # Parse XML
            root = ET.fromstring(xml_str)
            
            # Extract data and metadata
            if root.find('metadata') is not None:
                metadata_elem = root.find('metadata')
                metadata = {child.tag: child.text for child in metadata_elem}
                content_elem = root.find('content')
            else:
                metadata = {}
                content_elem = root
            
            # Convert XML to dict
            actual_data = self._xml_to_dict(content_elem)
            
            return DeserializationResult(
                success=True,
                format=SerializationFormat.XML,
                data=actual_data,
                metadata=metadata
            )
            
        except Exception as e:
            return DeserializationResult(
                success=False,
                format=SerializationFormat.XML,
                error_message=f"XML deserialization failed: {str(e)}"
            )
    
    def supports_format(self, format: SerializationFormat) -> bool:
        """Check if adapter supports XML format"""
        return format == SerializationFormat.XML
    
    def _dict_to_xml(self, data: Any, parent_elem: ET.Element, key_name: str = "item"):
        """Convert dictionary to XML elements"""
        if isinstance(data, dict):
            for key, value in data.items():
                elem = ET.SubElement(parent_elem, str(key))
                self._dict_to_xml(value, elem, key)
        elif isinstance(data, (list, tuple)):
            for i, item in enumerate(data):
                elem = ET.SubElement(parent_elem, f"{key_name}_{i}")
                self._dict_to_xml(item, elem, key_name)
        else:
            parent_elem.text = str(data)
    
    def _xml_to_dict(self, elem: ET.Element) -> Any:
        """Convert XML element to dictionary"""
        if len(elem) == 0:
            # Leaf node
            return elem.text
        
        result = {}
        for child in elem:
            child_data = self._xml_to_dict(child)
            
            # Handle multiple children with same tag
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result


class MultiFormatSerializationManager:
    """Central manager for multi-format serialization"""
    
    def __init__(self):
        self.adapters: Dict[SerializationFormat, SerializationAdapter] = {
            SerializationFormat.JSON: JSONSerializationAdapter(),
            SerializationFormat.YAML: YAMLSerializationAdapter(),
            SerializationFormat.XML: XMLSerializationAdapter(),
        }
        self.default_context = SerializationContext(format=SerializationFormat.JSON)
    
    async def serialize(
        self,
        data: Any,
        format: SerializationFormat,
        context: Optional[SerializationContext] = None
    ) -> SerializationResult:
        """Serialize data to specified format"""
        if context is None:
            context = SerializationContext(format=format)
        else:
            context.format = format
        
        adapter = self.adapters.get(format)
        if not adapter:
            return SerializationResult(
                success=False,
                format=format,
                error_message=f"No adapter available for format: {format}"
            )
        
        return await adapter.serialize(data, context)
    
    async def deserialize(
        self,
        serialized_data: Union[str, bytes],
        format: SerializationFormat,
        context: Optional[SerializationContext] = None
    ) -> DeserializationResult:
        """Deserialize data from specified format"""
        if context is None:
            context = SerializationContext(format=format)
        else:
            context.format = format
        
        adapter = self.adapters.get(format)
        if not adapter:
            return DeserializationResult(
                success=False,
                format=format,
                error_message=f"No adapter available for format: {format}"
            )
        
        return await adapter.deserialize(serialized_data, context)
    
    async def convert_format(
        self,
        data: Union[str, bytes],
        source_format: SerializationFormat,
        target_format: SerializationFormat,
        context: Optional[SerializationContext] = None
    ) -> SerializationResult:
        """Convert data from one format to another"""
        
        # Deserialize from source format
        deserialize_result = await self.deserialize(data, source_format, context)
        if not deserialize_result.success:
            return SerializationResult(
                success=False,
                format=target_format,
                error_message=f"Failed to deserialize source format: {deserialize_result.error_message}"
            )
        
        # Serialize to target format
        return await self.serialize(deserialize_result.data, target_format, context)
    
    def add_adapter(self, format: SerializationFormat, adapter: SerializationAdapter):
        """Add custom serialization adapter"""
        self.adapters[format] = adapter
    
    def get_supported_formats(self) -> List[SerializationFormat]:
        """Get list of supported serialization formats"""
        return list(self.adapters.keys())
    
    async def auto_detect_format(self, data: Union[str, bytes]) -> Optional[SerializationFormat]:
        """Auto-detect serialization format from data"""
        if isinstance(data, bytes):
            try:
                data_str = data.decode('utf-8')
            except UnicodeDecodeError:
                return SerializationFormat.BINARY
        else:
            data_str = data
        
        data_str = data_str.strip()
        
        # Try to detect JSON
        if data_str.startswith(('{', '[')):
            try:
                json.loads(data_str)
                return SerializationFormat.JSON
            except json.JSONDecodeError:
                pass
        
        # Try to detect XML
        if data_str.startswith('<?xml') or data_str.startswith('<'):
            try:
                ET.fromstring(data_str)
                return SerializationFormat.XML
            except ET.ParseError:
                pass
        
        # Try to detect YAML
        if ':' in data_str and not data_str.startswith(('<', '{')):
            try:
                yaml.safe_load(data_str)
                return SerializationFormat.YAML
            except yaml.YAMLError:
                pass
        
        return None


# Export classes for external use
__all__ = [
    'SerializationFormat',
    'SerializationContext',
    'SerializationResult',
    'DeserializationResult',
    'SerializationAdapter',
    'JSONSerializationAdapter',
    'YAMLSerializationAdapter',
    'XMLSerializationAdapter',
    'MultiFormatSerializationManager'
]