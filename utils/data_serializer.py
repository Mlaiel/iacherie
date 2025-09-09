"""Data Serialization Utilities
Enterprise-grade data serialization with multiple formats and compression.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import pickle
import base64
import gzip
import bz2
import zlib
from typing import Any, Dict, List, Optional, Union, Type
from datetime import datetime, date
from dataclasses import dataclass, asdict, is_dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SerializationFormat(Enum):
    """Supported serialization formats"""
    JSON = "json"
    PICKLE = "pickle"
    MSGPACK = "msgpack"
    YAML = "yaml"
    XML = "xml"
    CSV = "csv"


class CompressionType(Enum):
    """Supported compression types"""
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    ZLIB = "zlib"
    LZ4 = "lz4"


@dataclass
class SerializationResult:
    """Result of serialization operation"""
    data: bytes
    format: SerializationFormat
    compression: CompressionType
    size_original: int
    size_compressed: int
    compression_ratio: float


class DataSerializer:
    """
    Enterprise-grade data serialization system with multiple formats,
    compression, and custom type handling.
    """
    
    def __init__(self):
        self.custom_serializers: Dict[Type, callable] = {}
        self.custom_deserializers: Dict[Type, callable] = {}
        
        # Register built-in serializers
        self._register_builtin_serializers()
        
        logger.info("DataSerializer initialized")
    
    def _register_builtin_serializers(self):
        """Register built-in type serializers"""
        self.custom_serializers.update({
            datetime: lambda dt: dt.isoformat(),
            date: lambda d: d.isoformat(),
            set: list,
            frozenset: list,
            complex: lambda c: {"real": c.real, "imag": c.imag},
            bytes: lambda b: base64.b64encode(b).decode('ascii'),
        })
        
        self.custom_deserializers.update({
            datetime: datetime.fromisoformat,
            date: date.fromisoformat,
            set: set,
            frozenset: frozenset,
            complex: lambda d: complex(d["real"], d["imag"]),
            bytes: lambda s: base64.b64decode(s.encode('ascii')),
        })
    
    def register_serializer(self, data_type: Type, serializer: callable, deserializer: callable):
        """Register custom type serializer"""
        self.custom_serializers[data_type] = serializer
        self.custom_deserializers[data_type] = deserializer
        logger.info(f"Registered custom serializer for {data_type.__name__}")
    
    def serialize(self, data: Any, format: SerializationFormat = SerializationFormat.JSON,
                 compression: CompressionType = CompressionType.NONE,
                 **kwargs) -> SerializationResult:
        """
        Serialize data with specified format and compression
        
        Args:
            data: Data to serialize
            format: Serialization format
            compression: Compression type
            **kwargs: Format-specific options
            
        Returns:
            SerializationResult with serialized data and metadata
        """
        try:
            # Pre-process data for custom types
            processed_data = self._preprocess_data(data)
            
            # Serialize based on format
            if format == SerializationFormat.JSON:
                serialized = self._serialize_json(processed_data, **kwargs)
            elif format == SerializationFormat.PICKLE:
                serialized = self._serialize_pickle(processed_data, **kwargs)
            elif format == SerializationFormat.MSGPACK:
                serialized = self._serialize_msgpack(processed_data, **kwargs)
            elif format == SerializationFormat.YAML:
                serialized = self._serialize_yaml(processed_data, **kwargs)
            elif format == SerializationFormat.XML:
                serialized = self._serialize_xml(processed_data, **kwargs)
            elif format == SerializationFormat.CSV:
                serialized = self._serialize_csv(processed_data, **kwargs)
            else:
                raise ValueError(f"Unsupported serialization format: {format}")
            
            original_size = len(serialized)
            
            # Apply compression
            if compression != CompressionType.NONE:
                compressed_data = self._compress_data(serialized, compression)
                compressed_size = len(compressed_data)
                compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            else:
                compressed_data = serialized
                compressed_size = original_size
                compression_ratio = 1.0
            
            return SerializationResult(
                data=compressed_data,
                format=format,
                compression=compression,
                size_original=original_size,
                size_compressed=compressed_size,
                compression_ratio=compression_ratio
            )
            
        except Exception as e:
            logger.error(f"Serialization failed: {e}")
            raise
    
    def deserialize(self, serialized_result: Union[SerializationResult, bytes],
                   format: Optional[SerializationFormat] = None,
                   compression: Optional[CompressionType] = None,
                   target_type: Optional[Type] = None) -> Any:
        """
        Deserialize data from SerializationResult or raw bytes
        
        Args:
            serialized_result: SerializationResult or raw bytes
            format: Serialization format (required if using raw bytes)
            compression: Compression type (required if using raw bytes)
            target_type: Target type for deserialization
            
        Returns:
            Deserialized data
        """
        try:
            if isinstance(serialized_result, SerializationResult):
                data = serialized_result.data
                format = serialized_result.format
                compression = serialized_result.compression
            else:
                data = serialized_result
                if format is None or compression is None:
                    raise ValueError("Format and compression must be specified for raw bytes")
            
            # Decompress if needed
            if compression != CompressionType.NONE:
                decompressed_data = self._decompress_data(data, compression)
            else:
                decompressed_data = data
            
            # Deserialize based on format
            if format == SerializationFormat.JSON:
                deserialized = self._deserialize_json(decompressed_data)
            elif format == SerializationFormat.PICKLE:
                deserialized = self._deserialize_pickle(decompressed_data)
            elif format == SerializationFormat.MSGPACK:
                deserialized = self._deserialize_msgpack(decompressed_data)
            elif format == SerializationFormat.YAML:
                deserialized = self._deserialize_yaml(decompressed_data)
            elif format == SerializationFormat.XML:
                deserialized = self._deserialize_xml(decompressed_data)
            elif format == SerializationFormat.CSV:
                deserialized = self._deserialize_csv(decompressed_data)
            else:
                raise ValueError(f"Unsupported deserialization format: {format}")
            
            # Post-process data for custom types
            result = self._postprocess_data(deserialized, target_type)
            
            return result
            
        except Exception as e:
            logger.error(f"Deserialization failed: {e}")
            raise
    
    def _preprocess_data(self, data: Any) -> Any:
        """Preprocess data for serialization (handle custom types)"""
        if data is None:
            return None
        elif isinstance(data, (str, int, float, bool)):
            return data
        elif isinstance(data, (list, tuple)):
            return [self._preprocess_data(item) for item in data]
        elif isinstance(data, dict):
            return {key: self._preprocess_data(value) for key, value in data.items()}
        elif is_dataclass(data):
            return {"__dataclass__": data.__class__.__name__, "data": asdict(data)}
        elif type(data) in self.custom_serializers:
            return {"__custom_type__": type(data).__name__, "data": self.custom_serializers[type(data)](data)}
        else:
            # Try to convert to dict if object has __dict__
            if hasattr(data, '__dict__'):
                return {"__object__": data.__class__.__name__, "data": data.__dict__}
            else:
                return str(data)
    
    def _postprocess_data(self, data: Any, target_type: Optional[Type] = None) -> Any:
        """Postprocess data after deserialization (restore custom types)"""
        if data is None:
            return None
        elif isinstance(data, (str, int, float, bool)):
            return data
        elif isinstance(data, list):
            return [self._postprocess_data(item, target_type) for item in data]
        elif isinstance(data, dict):
            if "__dataclass__" in data:
                # Restore dataclass (would need type registry for full support)
                return data["data"]
            elif "__custom_type__" in data:
                type_name = data["__custom_type__"]
                # Restore custom type (would need type registry for full support)
                return data["data"]
            elif "__object__" in data:
                # Restore object (would need type registry for full support)
                return data["data"]
            else:
                return {key: self._postprocess_data(value, target_type) for key, value in data.items()}
        else:
            return data
    
    # Format-specific serialization methods
    
    def _serialize_json(self, data: Any, **kwargs) -> bytes:
        """Serialize to JSON"""
        indent = kwargs.get('indent', None)
        ensure_ascii = kwargs.get('ensure_ascii', False)
        
        json_str = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, default=str)
        return json_str.encode('utf-8')
    
    def _deserialize_json(self, data: bytes) -> Any:
        """Deserialize from JSON"""
        return json.loads(data.decode('utf-8'))
    
    def _serialize_pickle(self, data: Any, **kwargs) -> bytes:
        """Serialize to Pickle"""
        protocol = kwargs.get('protocol', pickle.HIGHEST_PROTOCOL)
        return pickle.dumps(data, protocol=protocol)
    
    def _deserialize_pickle(self, data: bytes) -> Any:
        """Deserialize from Pickle"""
        return pickle.loads(data)
    
    def _serialize_msgpack(self, data: Any, **kwargs) -> bytes:
        """Serialize to MessagePack"""
        try:
            import msgpack
            return msgpack.packb(data, **kwargs)
        except ImportError:
            raise ImportError("msgpack-python package required for MessagePack serialization")
    
    def _deserialize_msgpack(self, data: bytes) -> Any:
        """Deserialize from MessagePack"""
        try:
            import msgpack
            return msgpack.unpackb(data, raw=False)
        except ImportError:
            raise ImportError("msgpack-python package required for MessagePack deserialization")
    
    def _serialize_yaml(self, data: Any, **kwargs) -> bytes:
        """Serialize to YAML"""
        try:
            import yaml
            yaml_str = yaml.dump(data, **kwargs)
            return yaml_str.encode('utf-8')
        except ImportError:
            raise ImportError("PyYAML package required for YAML serialization")
    
    def _deserialize_yaml(self, data: bytes) -> Any:
        """Deserialize from YAML"""
        try:
            import yaml
            return yaml.safe_load(data.decode('utf-8'))
        except ImportError:
            raise ImportError("PyYAML package required for YAML deserialization")
    
    def _serialize_xml(self, data: Any, **kwargs) -> bytes:
        """Serialize to XML"""
        import xml.etree.ElementTree as ET
        
        def dict_to_xml(d, root_name="data"):
            root = ET.Element(root_name)
            
            def add_items(parent, items):
                if isinstance(items, dict):
                    for key, value in items.items():
                        child = ET.SubElement(parent, str(key))
                        add_items(child, value)
                elif isinstance(items, list):
                    for i, item in enumerate(items):
                        child = ET.SubElement(parent, f"item_{i}")
                        add_items(child, item)
                else:
                    parent.text = str(items)
            
            add_items(root, data)
            return ET.tostring(root, encoding='utf-8')
        
        return dict_to_xml(data)
    
    def _deserialize_xml(self, data: bytes) -> Any:
        """Deserialize from XML"""
        import xml.etree.ElementTree as ET
        
        def xml_to_dict(element):
            if len(element) == 0:
                return element.text
            
            result = {}
            for child in element:
                child_data = xml_to_dict(child)
                if child.tag in result:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = child_data
            
            return result
        
        root = ET.fromstring(data)
        return xml_to_dict(root)
    
    def _serialize_csv(self, data: Any, **kwargs) -> bytes:
        """Serialize to CSV (for list of dicts)"""
        import csv
        import io
        
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise ValueError("CSV serialization requires a list of dictionaries")
        
        if not data:
            return b""
        
        output = io.StringIO()
        fieldnames = data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames, **kwargs)
        
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        
        return output.getvalue().encode('utf-8')
    
    def _deserialize_csv(self, data: bytes) -> List[Dict[str, Any]]:
        """Deserialize from CSV"""
        import csv
        import io
        
        content = data.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        
        return list(reader)
    
    # Compression methods
    
    def _compress_data(self, data: bytes, compression: CompressionType) -> bytes:
        """Compress data using specified method"""
        if compression == CompressionType.GZIP:
            return gzip.compress(data)
        elif compression == CompressionType.BZIP2:
            return bz2.compress(data)
        elif compression == CompressionType.ZLIB:
            return zlib.compress(data)
        elif compression == CompressionType.LZ4:
            try:
                import lz4.frame
                return lz4.frame.compress(data)
            except ImportError:
                raise ImportError("lz4 package required for LZ4 compression")
        else:
            raise ValueError(f"Unsupported compression type: {compression}")
    
    def _decompress_data(self, data: bytes, compression: CompressionType) -> bytes:
        """Decompress data using specified method"""
        if compression == CompressionType.GZIP:
            return gzip.decompress(data)
        elif compression == CompressionType.BZIP2:
            return bz2.decompress(data)
        elif compression == CompressionType.ZLIB:
            return zlib.decompress(data)
        elif compression == CompressionType.LZ4:
            try:
                import lz4.frame
                return lz4.frame.decompress(data)
            except ImportError:
                raise ImportError("lz4 package required for LZ4 decompression")
        else:
            raise ValueError(f"Unsupported compression type: {compression}")


# Utility functions for common serialization tasks

def serialize_to_json(data: Any, compress: bool = False) -> bytes:
    """Quick JSON serialization"""
    serializer = DataSerializer()
    compression = CompressionType.GZIP if compress else CompressionType.NONE
    result = serializer.serialize(data, SerializationFormat.JSON, compression)
    return result.data


def deserialize_from_json(data: bytes, compressed: bool = False) -> Any:
    """Quick JSON deserialization"""
    serializer = DataSerializer()
    compression = CompressionType.GZIP if compressed else CompressionType.NONE
    return serializer.deserialize(data, SerializationFormat.JSON, compression)


def serialize_to_pickle(data: Any, compress: bool = False) -> bytes:
    """Quick Pickle serialization"""
    serializer = DataSerializer()
    compression = CompressionType.GZIP if compress else CompressionType.NONE
    result = serializer.serialize(data, SerializationFormat.PICKLE, compression)
    return result.data


def deserialize_from_pickle(data: bytes, compressed: bool = False) -> Any:
    """Quick Pickle deserialization"""
    serializer = DataSerializer()
    compression = CompressionType.GZIP if compressed else CompressionType.NONE
    return serializer.deserialize(data, SerializationFormat.PICKLE, compression)


# Global serializer instance
_global_serializer: Optional[DataSerializer] = None


def get_global_serializer() -> DataSerializer:
    """Get global data serializer instance"""
    global _global_serializer
    if _global_serializer is None:
        _global_serializer = DataSerializer()
    return _global_serializer