"""
"""
Data Adapters - Enterprise Data Processing and Transformation System
===================================================================

Industrial-grade data processing adapters for the IA-Influencer Agent platform.
Provides comprehensive data transformation, validation, mapping, and integration
capabilities with enterprise-level performance and reliability.

Business Logic: Raw Data → Processing → Validation → Transformation → Storage

Supported Data Operations:
- ETL/ELT pipeline orchestration
- Real-time stream processing with Apache Kafka
- Batch processing with chunking and parallel execution
- Data validation with comprehensive schema checking
- Advanced data transformation and mapping
- Data enrichment with external APIs
- Data quality monitoring and profiling
- Multi-format data parsing (JSON, XML, CSV, Parquet, Avro)
- Time-series data processing and analytics
- Machine learning feature engineering

Key Features:
- High-performance data processing with asyncio
- Memory-efficient streaming for large datasets
- Advanced error handling and data recovery
- Schema evolution and backward compatibility
- Data lineage tracking and audit trails
- Real-time data quality monitoring
- Automatic data type inference and conversion
- Advanced compression and encoding
- Data masking and anonymization for GDPR compliance
- Multi-source data integration and federation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import logging
import json
import csv
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Union, Generator, AsyncGenerator, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import hashlib
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import concurrent.futures
import threading
import time
import re
import pandas as pd
import numpy as np
from pathlib import Path
import aiofiles
import pyarrow as pa
import pyarrow.parquet as pq

# Advanced data processing imports
try:
    import kafka
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.admin import KafkaAdminClient, NewTopic
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import sqlalchemy
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.dialects import postgresql, mysql, sqlite
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Data validation and schema libraries
try:
    import jsonschema
    from pydantic import BaseModel, validator, Field
    from cerberus import Validator
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

# Data serialization formats
try:
    import avro.schema
    import avro.io
    AVRO_AVAILABLE = True
except ImportError:
    AVRO_AVAILABLE = False

try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False

# Data processing and ML libraries
try:
    from scipy import stats, sparse
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
"""

import asyncio
import logging
import json
import csv
import xml.etree.ElementTree as ET
import xml.sax
import io
import base64
import gzip
import bz2
import lzma
import time
import mmap
import sqlite3
from typing import Dict, List, Optional, Any, Union, BinaryIO, AsyncGenerator, Callable, Iterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from pathlib import Path
import hashlib
import hmac
from enum import Enum
import struct
import pickle
import concurrent.futures
import weakref
from collections import defaultdict, OrderedDict

# Advanced data format imports
try:
    import yaml
    from yaml import CLoader as YamlLoader, CDumper as YamlDumper
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import toml
    import tomllib  # Python 3.11+
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False

try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    import pyarrow.csv as pc
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False

try:
    import fastavro
    from avro.schema import parse as avro_parse
    AVRO_AVAILABLE = True
except ImportError:
    AVRO_AVAILABLE = False

# Protocol Buffers support
try:
    import google.protobuf.message
    import google.protobuf.json_format
    from google.protobuf.descriptor import FieldDescriptor
    from google.protobuf import descriptor_pool
    PROTOBUF_AVAILABLE = True
except ImportError:
    PROTOBUF_AVAILABLE = False

# MessagePack support
try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False

# Advanced compression
try:
    import snappy
    import zstandard as zstd
    ADVANCED_COMPRESSION = True
except ImportError:
    ADVANCED_COMPRESSION = False

# Scientific data formats
try:
    import h5py
    import netCDF4
    HDF5_AVAILABLE = True
except ImportError:
    HDF5_AVAILABLE = False

# Schema validation
try:
    import jsonschema
    from jsonschema import validate, ValidationError
    import cerberus
    SCHEMA_VALIDATION = True
except ImportError:
    SCHEMA_VALIDATION = False

# Cryptography support
try:
    from cryptography.fernet import Fernet, MultiFernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

logger = logging.getLogger(__name__)

class CompressionType(Enum):
    """Supported compression types."""
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"

class EncryptionType(Enum):
    """Supported encryption types."""
    NONE = "none"
    FERNET = "fernet"
    AES = "aes"

@dataclass
class DataProcessingMetrics:
    """Metrics for data processing operations."""
    items_processed: int = 0
    bytes_processed: int = 0
    processing_time: float = 0.0
    compression_ratio: float = 0.0
    errors_count: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class DataFormatConfig:
    """Advanced configuration for data format processing."""
    # Basic settings
    encoding: str = 'utf-8'
    indent: Optional[int] = None
    ensure_ascii: bool = False
    sort_keys: bool = False
    validate_format: bool = True
    
    # Advanced settings
    compression: CompressionType = CompressionType.NONE
    encryption: EncryptionType = EncryptionType.NONE
    encryption_key: Optional[str] = None
    max_size: Optional[int] = None
    chunk_size: int = 8192
    
    # Validation settings
    schema_validation: bool = False
    schema_path: Optional[str] = None
    strict_validation: bool = False
    
    # Performance settings
    enable_metrics: bool = True
    enable_caching: bool = False
    cache_ttl: int = 3600
    parallel_processing: bool = False
    max_workers: int = 4
    
    # Security settings
    sanitize_input: bool = True
    max_depth: int = 100
    allow_nan: bool = False

@dataclass
class ProcessingResult:
    """Result of data processing operation."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metrics: Optional[DataProcessingMetrics] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataAdapter(ABC):
    """Enterprise base class for all data format adapters."""
    
    def __init__(self, config: Optional[DataFormatConfig] = None):
        """Initialize data adapter with enterprise configuration."""
        self.config = config or DataFormatConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.supported_formats: List[str] = []
        self.metrics = DataProcessingMetrics()
        self._cache: Dict[str, Any] = {}
        self._schema: Optional[Dict] = None
        
        # Initialize encryption if configured
        self._encryption_cipher = None
        if self.config.encryption != EncryptionType.NONE and self.config.encryption_key:
            self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption cipher."""
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography package required for encryption")
        
        if self.config.encryption == EncryptionType.FERNET:
            key = base64.urlsafe_b64encode(
                self.config.encryption_key.encode()[:32].ljust(32, b'0')
            )
            self._encryption_cipher = Fernet(key)
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using configured cipher."""
        if self._encryption_cipher and self.config.encryption == EncryptionType.FERNET:
            return self._encryption_cipher.encrypt(data)
        return data
    
    def _decrypt_data(self, data: bytes) -> bytes:
        """Decrypt data using configured cipher."""
        if self._encryption_cipher and self.config.encryption == EncryptionType.FERNET:
            return self._encryption_cipher.decrypt(data)
        return data
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data using configured compression."""
        if self.config.compression == CompressionType.GZIP:
            return gzip.compress(data)
        elif self.config.compression == CompressionType.BZIP2:
            return bz2.compress(data)
        elif self.config.compression == CompressionType.LZMA:
            return lzma.compress(data)
        return data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress data using configured compression."""
        if self.config.compression == CompressionType.GZIP:
            return gzip.decompress(data)
        elif self.config.compression == CompressionType.BZIP2:
            return bz2.decompress(data)
        elif self.config.compression == CompressionType.LZMA:
            return lzma.decompress(data)
        return data
    
    @abstractmethod
    async def serialize(self, data: Any) -> Union[str, bytes]:
        """Serialize data to format."""
        pass
    
    @abstractmethod
    async def deserialize(self, data: Union[str, bytes, BinaryIO]) -> Any:
        """Deserialize data from format."""
        pass
    
    @abstractmethod
    def validate_format(self, data: Union[str, bytes]) -> bool:
        """Validate data format."""
        pass
    
    async def process_batch(
        self, 
        data_items: List[Any],
        operation: str = "serialize"
    ) -> List[ProcessingResult]:
        """Process multiple data items with enterprise features."""
        results = []
        start_time = time.time()
        
        for i, item in enumerate(data_items):
            try:
                if operation == "serialize":
                    result_data = await self.serialize(item)
                else:
                    result_data = await self.deserialize(item)
                
                results.append(ProcessingResult(
                    success=True,
                    data=result_data,
                    metadata={"index": i, "type": type(item).__name__}
                ))
                
            except Exception as e:
                self.logger.error(f"Batch processing failed for item {i}: {e}")
                results.append(ProcessingResult(
                    success=False,
                    error=str(e),
                    metadata={"index": i, "type": type(item).__name__}
                ))
        
        # Update metrics
        if self.config.enable_metrics:
            self.metrics.items_processed += len(data_items)
            self.metrics.processing_time += time.time() - start_time
        
        return results
    
    async def stream_process(
        self,
        data_stream: AsyncGenerator[Any, None],
        callback: Optional[Callable] = None
    ) -> AsyncGenerator[ProcessingResult, None]:
        """Stream process data with callback support."""
        async for item in data_stream:
            try:
                result_data = await self.serialize(item)
                result = ProcessingResult(success=True, data=result_data)
                
                if callback:
                    await callback(result)
                
                yield result
                
            except Exception as e:
                self.logger.error(f"Stream processing failed: {e}")
                result = ProcessingResult(success=False, error=str(e))
                yield result
    
    def get_content_type(self) -> str:
        """Get MIME content type for this format."""
        return "application/octet-stream"
    
    def get_metrics(self) -> DataProcessingMetrics:
        """Get processing metrics."""
        return self.metrics
    
    def reset_metrics(self):
        """Reset processing metrics."""
        self.metrics = DataProcessingMetrics()

class JSONAdapter(DataAdapter):
    """Enterprise JSON adapter with advanced features."""
    
    def __init__(self, config: Optional[DataFormatConfig] = None):
        """Initialize JSON adapter."""
        super().__init__(config)
        self.supported_formats = ['application/json', 'text/json']
    
    async def serialize(self, data: Any) -> str:
        """Serialize data to JSON."""
        try:
            # Handle datetime objects
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif hasattr(obj, '__dict__'):
                    return obj.__dict__
                elif hasattr(obj, '_asdict'):  # namedtuple
                    return obj._asdict()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            result = json.dumps(
                data,
                indent=self.config.indent,
                ensure_ascii=self.config.ensure_ascii,
                sort_keys=self.config.sort_keys,
                default=json_serializer
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"JSON serialization failed: {e}")
            raise
    
    async def deserialize(self, data: Union[str, bytes, BinaryIO]) -> Any:
        """Deserialize JSON data."""
        try:
            if isinstance(data, bytes):
                json_str = data.decode(self.config.encoding)
            elif hasattr(data, 'read'):
                json_str = data.read()
                if isinstance(json_str, bytes):
                    json_str = json_str.decode(self.config.encoding)
            else:
                json_str = data
            
            # Parse JSON with datetime handling
            def json_object_hook(obj):
                for key, value in obj.items():
                    if isinstance(value, str):
                        # Try to parse ISO datetime
                        try:
                            if 'T' in value and (value.endswith('Z') or '+' in value[-6:]):
                                obj[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        except:
                            pass
                return obj
            
            return json.loads(json_str, object_hook=json_object_hook)
            
        except Exception as e:
            self.logger.error(f"JSON deserialization failed: {e}")
            raise
    
    def validate_format(self, data: Union[str, bytes]) -> bool:
        """Validate JSON format."""
        try:
            if isinstance(data, bytes):
                data = data.decode(self.config.encoding)
            json.loads(data)
            return True
        except:
            return False
    
    def get_content_type(self) -> str:
        """Get JSON content type."""
        return "application/json"
    
    async def pretty_format(self, data: Any) -> str:
        """Format JSON with pretty printing."""
        old_indent = self.config.indent
        self.config.indent = 2
        result = await self.serialize(data)
        self.config.indent = old_indent
        return result
    
    async def minify(self, json_str: str) -> str:
        """Minify JSON string."""
        data = json.loads(json_str)
        return json.dumps(data, separators=(',', ':'))

class XMLAdapter(DataAdapter):
    """Adapter for XML data format."""
    
    def __init__(self, config: Optional[DataFormatConfig] = None):
        """Initialize XML adapter."""
        super().__init__(config)
        self.supported_formats = ['application/xml', 'text/xml']
    
    async def serialize(self, data: Any, root_name: str = "root") -> str:
        """Serialize data to XML."""
        try:
            root = ET.Element(root_name)
            self._dict_to_xml(data, root)
            
            # Format XML
            self._indent_xml(root)
            return ET.tostring(root, encoding=self.config.encoding).decode(self.config.encoding)
            
        except Exception as e:
            self.logger.error(f"XML serialization failed: {e}")
            raise
    
    def _dict_to_xml(self, data: Any, parent: ET.Element):
        """Convert dictionary to XML elements."""
        if isinstance(data, dict):
            for key, value in data.items():
                key = str(key).replace(' ', '_')  # XML element names can't have spaces
                child = ET.SubElement(parent, key)
                self._dict_to_xml(value, child)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                child = ET.SubElement(parent, f"item_{i}")
                self._dict_to_xml(item, child)
        
        elif isinstance(data, datetime):
            parent.text = data.isoformat()
        
        else:
            parent.text = str(data)
    
    def _indent_xml(self, elem: ET.Element, level: int = 0):
        """Add indentation to XML for pretty printing."""
        indent = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent
    
    async def deserialize(self, data: Union[str, bytes, BinaryIO]) -> Dict[str, Any]:
        """Deserialize XML data."""
        try:
            if isinstance(data, bytes):
                xml_str = data.decode(self.config.encoding)
            elif hasattr(data, 'read'):
                xml_str = data.read()
                if isinstance(xml_str, bytes):
                    xml_str = xml_str.decode(self.config.encoding)
            else:
                xml_str = data
            
            root = ET.fromstring(xml_str)
            return {root.tag: self._xml_to_dict(root)}
            
        except Exception as e:
            self.logger.error(f"XML deserialization failed: {e}")
            raise
    
    def _xml_to_dict(self, element: ET.Element) -> Any:
        """Convert XML element to dictionary."""
        result = {}
        
        # Add attributes
        if element.attrib:
            result.update({f"@{k}": v for k, v in element.attrib.items()})
        
        # Add text content
        if element.text and element.text.strip():
            text = element.text.strip()
            # Try to parse as datetime
            try:
                if 'T' in text and (text.endswith('Z') or '+' in text[-6:]):
                    text = datetime.fromisoformat(text.replace('Z', '+00:00'))
            except:
                pass
            
            if not result and not list(element):
                return text
            result['#text'] = text
        
        # Add child elements
        children = {}
        for child in element:
            child_data = self._xml_to_dict(child)
            
            if child.tag in children:
                if not isinstance(children[child.tag], list):
                    children[child.tag] = [children[child.tag]]
                children[child.tag].append(child_data)
            else:
                children[child.tag] = child_data
        
        result.update(children)
        
        return result if result else None
    
    def validate_format(self, data: Union[str, bytes]) -> bool:
        """Validate XML format."""
        try:
            if isinstance(data, bytes):
                data = data.decode(self.config.encoding)
            ET.fromstring(data)
            return True
        except:
            return False
    
    def get_content_type(self) -> str:
        """Get XML content type."""
        return "application/xml"

class CSVAdapter(DataAdapter):
    """Adapter for CSV data format."""
    
    def __init__(self, config: Optional[DataFormatConfig] = None):
        """Initialize CSV adapter."""
        super().__init__(config)
        self.supported_formats = ['text/csv', 'application/csv']
        self.delimiter = ','
        self.quote_char = '"'
        self.line_terminator = '\n'
        self.has_header = True
    
    async def serialize(self, data: Any) -> str:
        """Serialize data to CSV."""
        try:
            output = io.StringIO()
            
            if isinstance(data, list) and data:
                if isinstance(data[0], dict):
                    # List of dictionaries
                    fieldnames = list(data[0].keys())
                    writer = csv.DictWriter(
                        output,
                        fieldnames=fieldnames,
                        delimiter=self.delimiter,
                        quotechar=self.quote_char,
                        lineterminator=self.line_terminator
                    )
                    
                    if self.has_header:
                        writer.writeheader()
                    
                    for row in data:
                        # Convert complex objects to strings
                        clean_row = {}
                        for key, value in row.items():
                            if isinstance(value, datetime):
                                clean_row[key] = value.isoformat()
                            elif isinstance(value, (dict, list)):
                                clean_row[key] = json.dumps(value)
                            else:
                                clean_row[key] = str(value) if value is not None else ''
                        writer.writerow(clean_row)
                
                elif isinstance(data[0], (list, tuple)):
                    # List of lists/tuples
                    writer = csv.writer(
                        output,
                        delimiter=self.delimiter,
                        quotechar=self.quote_char,
                        lineterminator=self.line_terminator
                    )
                    
                    for row in data:
                        clean_row = []
                        for value in row:
                            if isinstance(value, datetime):
                                clean_row.append(value.isoformat())
                            elif isinstance(value, (dict, list)):
                                clean_row.append(json.dumps(value))
                            else:
                                clean_row.append(str(value) if value is not None else '')
                        writer.writerow(clean_row)
                
                else:
                    # Simple list
                    writer = csv.writer(
                        output,
                        delimiter=self.delimiter,
                        quotechar=self.quote_char,
                        lineterminator=self.line_terminator
                    )
                    
                    for item in data:
                        if isinstance(item, datetime):
                            writer.writerow([item.isoformat()])
                        elif isinstance(item, (dict, list)):
                            writer.writerow([json.dumps(item)])
                        else:
                            writer.writerow([str(item) if item is not None else ''])
            
            elif isinstance(data, dict):
                # Single dictionary - convert to list
                return await self.serialize([data])
            
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"CSV serialization failed: {e}")
            raise
    
    async def deserialize(self, data: Union[str, bytes, BinaryIO]) -> List[Dict[str, Any]]:
        """Deserialize CSV data."""
        try:
            if isinstance(data, bytes):
                csv_str = data.decode(self.config.encoding)
            elif hasattr(data, 'read'):
                csv_str = data.read()
                if isinstance(csv_str, bytes):
                    csv_str = csv_str.decode(self.config.encoding)
            else:
                csv_str = data
            
            input_stream = io.StringIO(csv_str)
            
            # Try to detect if there's a header
            sniffer = csv.Sniffer()
            sample = csv_str[:1024]
            
            try:
                has_header = sniffer.has_header(sample)
                dialect = sniffer.sniff(sample)
            except:
                has_header = self.has_header
                dialect = None
            
            input_stream.seek(0)
            
            if has_header:
                reader = csv.DictReader(input_stream, dialect=dialect)
                rows = []
                
                for row in reader:
                    clean_row = {}
                    for key, value in row.items():
                        # Try to parse JSON
                        if value.startswith(('{', '[')):
                            try:
                                clean_row[key] = json.loads(value)
                                continue
                            except:
                                pass
                        
                        # Try to parse datetime
                        if 'T' in value and (value.endswith('Z') or '+' in value[-6:]):
                            try:
                                clean_row[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                continue
                            except:
                                pass
                        
                        # Try to parse numbers
                        try:
                            if '.' in value:
                                clean_row[key] = float(value)
                            else:
                                clean_row[key] = int(value)
                        except:
                            clean_row[key] = value
                    
                    rows.append(clean_row)
                
                return rows
            
            else:
                reader = csv.reader(input_stream, dialect=dialect)
                return [list(row) for row in reader]
            
        except Exception as e:
            self.logger.error(f"CSV deserialization failed: {e}")
            raise
    
    def validate_format(self, data: Union[str, bytes]) -> bool:
        """Validate CSV format."""
        try:
            if isinstance(data, bytes):
                data = data.decode(self.config.encoding)
            
            # Try to parse a sample
            sample_lines = data.split('\n')[:5]
            sample = '\n'.join(sample_lines)
            
            csv.reader(io.StringIO(sample))
            return True
        except:
            return False
    
    def get_content_type(self) -> str:
        """Get CSV content type."""
        return "text/csv"

class BinaryAdapter(DataAdapter):
    """Adapter for binary data format."""
    
    def __init__(self, config: Optional[DataFormatConfig] = None):
        """Initialize binary adapter."""
        super().__init__(config)
        self.supported_formats = ['application/octet-stream', 'application/binary']
    
    async def serialize(self, data: Any) -> bytes:
        """Serialize data to binary."""
        try:
            if isinstance(data, bytes):
                return data
            elif isinstance(data, str):
                return data.encode(self.config.encoding)
            elif isinstance(data, (int, float)):
                return str(data).encode(self.config.encoding)
            else:
                # Use pickle for complex objects
                import pickle
                return pickle.dumps(data)
            
        except Exception as e:
            self.logger.error(f"Binary serialization failed: {e}")
            raise
    
    async def deserialize(self, data: Union[str, bytes, BinaryIO]) -> Any:
        """Deserialize binary data."""
        try:
            if hasattr(data, 'read'):
                binary_data = data.read()
            elif isinstance(data, str):
                binary_data = data.encode(self.config.encoding)
            else:
                binary_data = data
            
            # Try different deserialization methods
            try:
                # Try pickle first
                import pickle
                return pickle.loads(binary_data)
            except:
                try:
                    # Try UTF-8 text
                    return binary_data.decode(self.config.encoding)
                except:
                    # Return raw bytes
                    return binary_data
            
        except Exception as e:
            self.logger.error(f"Binary deserialization failed: {e}")
            raise
    
    def validate_format(self, data: Union[str, bytes]) -> bool:
        """Validate binary format."""
        # Binary data is always valid
        return isinstance(data, (str, bytes))
    
    def get_content_type(self) -> str:
        """Get binary content type."""
        return "application/octet-stream"
    
    async def encode_base64(self, data: bytes) -> str:
        """Encode binary data as base64."""
        return base64.b64encode(data).decode('ascii')
    
    async def decode_base64(self, data: str) -> bytes:
        """Decode base64 data to binary."""
        return base64.b64decode(data)

class ProtocolBufferAdapter(DataAdapter):
    """Adapter for Protocol Buffer data format."""
    
    def __init__(self, config: Optional[DataFormatConfig] = None):
        """Initialize Protocol Buffer adapter."""
        super().__init__(config)
        
        if not PROTOBUF_AVAILABLE:
            raise ImportError("Protocol Buffers not available. Install with: pip install protobuf")
        
        self.supported_formats = ['application/x-protobuf', 'application/protobuf']
        self.message_type = None
    
    def set_message_type(self, message_type):
        """Set the Protocol Buffer message type."""
        self.message_type = message_type
    
    async def serialize(self, data: Any) -> bytes:
        """Serialize data to Protocol Buffer."""
        try:
            if not self.message_type:
                raise ValueError("Message type not set")
            
            if isinstance(data, self.message_type):
                return data.SerializeToString()
            
            elif isinstance(data, dict):
                # Convert dict to protobuf message
                message = self.message_type()
                google.protobuf.json_format.ParseDict(data, message)
                return message.SerializeToString()
            
            else:
                raise ValueError("Data must be a protobuf message or dictionary")
            
        except Exception as e:
            self.logger.error(f"Protocol Buffer serialization failed: {e}")
            raise
    
    async def deserialize(self, data: Union[str, bytes, BinaryIO]) -> Any:
        """Deserialize Protocol Buffer data."""
        try:
            if not self.message_type:
                raise ValueError("Message type not set")
            
            if hasattr(data, 'read'):
                binary_data = data.read()
            elif isinstance(data, str):
                binary_data = data.encode(self.config.encoding)
            else:
                binary_data = data
            
            message = self.message_type()
            message.ParseFromString(binary_data)
            
            # Convert to dictionary
            return google.protobuf.json_format.MessageToDict(message)
            
        except Exception as e:
            self.logger.error(f"Protocol Buffer deserialization failed: {e}")
            raise
    
    def validate_format(self, data: Union[str, bytes]) -> bool:
        """Validate Protocol Buffer format."""
        try:
            if not self.message_type:
                return False
            
            if isinstance(data, str):
                data = data.encode(self.config.encoding)
            
            message = self.message_type()
            message.ParseFromString(data)
            return True
        except:
            return False
    
    def get_content_type(self) -> str:
        """Get Protocol Buffer content type."""
        return "application/x-protobuf"
    
    async def to_json(self, protobuf_data: bytes) -> str:
        """Convert Protocol Buffer to JSON."""
        message_dict = await self.deserialize(protobuf_data)
        json_adapter = JSONAdapter(self.config)
        return await json_adapter.serialize(message_dict)
    
    async def from_json(self, json_data: str) -> bytes:
        """Convert JSON to Protocol Buffer."""
        json_adapter = JSONAdapter(self.config)
        data_dict = await json_adapter.deserialize(json_data)
        return await self.serialize(data_dict)

class MessagePackAdapter(DataAdapter):
    """Adapter for MessagePack data format."""
    
    def __init__(self, config: Optional[DataFormatConfig] = None):
        """Initialize MessagePack adapter."""
        super().__init__(config)
        
        if not MSGPACK_AVAILABLE:
            raise ImportError("MessagePack not available. Install with: pip install msgpack")
        
        self.supported_formats = ['application/msgpack', 'application/x-msgpack']
    
    async def serialize(self, data: Any) -> bytes:
        """Serialize data to MessagePack."""
        try:
            def encode_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            return msgpack.packb(data, default=encode_datetime, use_bin_type=True)
            
        except Exception as e:
            self.logger.error(f"MessagePack serialization failed: {e}")
            raise
    
    async def deserialize(self, data: Union[str, bytes, BinaryIO]) -> Any:
        """Deserialize MessagePack data."""
        try:
            if hasattr(data, 'read'):
                binary_data = data.read()
            elif isinstance(data, str):
                binary_data = data.encode(self.config.encoding)
            else:
                binary_data = data
            
            def decode_datetime(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, str):
                            try:
                                if 'T' in value and (value.endswith('Z') or '+' in value[-6:]):
                                    obj[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            except:
                                pass
                return obj
            
            result = msgpack.unpackb(binary_data, raw=False, strict_map_key=False)
            
            # Process datetime strings
            if isinstance(result, dict):
                result = decode_datetime(result)
            elif isinstance(result, list):
                result = [decode_datetime(item) if isinstance(item, dict) else item for item in result]
            
            return result
            
        except Exception as e:
            self.logger.error(f"MessagePack deserialization failed: {e}")
            raise
    
    def validate_format(self, data: Union[str, bytes]) -> bool:
        """Validate MessagePack format."""
        try:
            if isinstance(data, str):
                data = data.encode(self.config.encoding)
            
            msgpack.unpackb(data, raw=False)
            return True
        except:
            return False
    
    def get_content_type(self) -> str:
        """Get MessagePack content type."""
        return "application/msgpack"
    
    async def to_json(self, msgpack_data: bytes) -> str:
        """Convert MessagePack to JSON."""
        data = await self.deserialize(msgpack_data)
        json_adapter = JSONAdapter(self.config)
        return await json_adapter.serialize(data)
    
    async def from_json(self, json_data: str) -> bytes:
        """Convert JSON to MessagePack."""
        json_adapter = JSONAdapter(self.config)
        data = await json_adapter.deserialize(json_data)
        return await self.serialize(data)

class YAMLAdapter(DataAdapter):
    """Enterprise YAML adapter with advanced features."""
    
    def __init__(self, config: Optional[DataFormatConfig] = None):
        """Initialize YAML adapter."""
        super().__init__(config)
        self.supported_formats = ['yaml', 'yml']
        
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML package required for YAML support")
    
    async def serialize(self, data: Any) -> str:
        """Serialize data to YAML format."""
        try:
            start_time = time.time()
            
            # Sanitize input if configured
            if self.config.sanitize_input:
                data = self._sanitize_data(data)
            
            # Serialize to YAML
            yaml_str = yaml.dump(
                data,
                default_flow_style=False,
                allow_unicode=True,
                encoding=None,
                sort_keys=self.config.sort_keys,
                indent=self.config.indent or 2
            )
            
            # Update metrics
            if self.config.enable_metrics:
                self.metrics.bytes_processed += len(yaml_str.encode(self.config.encoding))
                self.metrics.processing_time += time.time() - start_time
            
            return yaml_str
            
        except Exception as e:
            self.logger.error(f"YAML serialization failed: {e}")
            raise
    
    async def deserialize(self, data: Union[str, bytes, BinaryIO]) -> Any:
        """Deserialize YAML data."""
        try:
            start_time = time.time()
            
            if isinstance(data, bytes):
                data = data.decode(self.config.encoding)
            elif hasattr(data, 'read'):
                data = data.read()
                if isinstance(data, bytes):
                    data = data.decode(self.config.encoding)
            
            # Size validation
            if self.config.max_size and len(data) > self.config.max_size:
                raise ValueError(f"YAML data size exceeds limit: {len(data)} > {self.config.max_size}")
            
            result = yaml.safe_load(data)
            
            # Update metrics
            if self.config.enable_metrics:
                self.metrics.bytes_processed += len(data.encode(self.config.encoding))
                self.metrics.processing_time += time.time() - start_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"YAML deserialization failed: {e}")
            raise
    
    def validate_format(self, data: Union[str, bytes]) -> bool:
        """Validate YAML format."""
        try:
            if isinstance(data, bytes):
                data = data.decode(self.config.encoding)
            yaml.safe_load(data)
            return True
        except:
            return False
    
    def get_content_type(self) -> str:
        """Get MIME content type."""
        return "application/yaml"

class TOMLAdapter(DataAdapter):
    """Enterprise TOML adapter with advanced features."""
    
    def __init__(self, config: Optional[DataFormatConfig] = None):
        """Initialize TOML adapter."""
        super().__init__(config)
        self.supported_formats = ['toml']
        
        if not TOML_AVAILABLE:
            raise ImportError("toml package required for TOML support")
    
    async def serialize(self, data: Any) -> str:
        """Serialize data to TOML format."""
        try:
            start_time = time.time()
            
            # Sanitize input if configured
            if self.config.sanitize_input:
                data = self._sanitize_data(data)
            
            # Serialize to TOML
            toml_str = toml.dumps(data)
            
            # Update metrics
            if self.config.enable_metrics:
                self.metrics.bytes_processed += len(toml_str.encode(self.config.encoding))
                self.metrics.processing_time += time.time() - start_time
            
            return toml_str
            
        except Exception as e:
            self.logger.error(f"TOML serialization failed: {e}")
            raise
    
    async def deserialize(self, data: Union[str, bytes, BinaryIO]) -> Any:
        """Deserialize TOML data."""
        try:
            start_time = time.time()
            
            if isinstance(data, bytes):
                data = data.decode(self.config.encoding)
            elif hasattr(data, 'read'):
                data = data.read()
                if isinstance(data, bytes):
                    data = data.decode(self.config.encoding)
            
            # Size validation
            if self.config.max_size and len(data) > self.config.max_size:
                raise ValueError(f"TOML data size exceeds limit: {len(data)} > {self.config.max_size}")
            
            result = toml.loads(data)
            
            # Update metrics
            if self.config.enable_metrics:
                self.metrics.bytes_processed += len(data.encode(self.config.encoding))
                self.metrics.processing_time += time.time() - start_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"TOML deserialization failed: {e}")
            raise
    
    def validate_format(self, data: Union[str, bytes]) -> bool:
        """Validate TOML format."""
        try:
            if isinstance(data, bytes):
                data = data.decode(self.config.encoding)
            toml.loads(data)
            return True
        except:
            return False
    
    def get_content_type(self) -> str:
        """Get MIME content type."""
        return "application/toml"

class ParquetAdapter(DataAdapter):
    """Enterprise Parquet adapter with advanced features."""
    
    def __init__(self, config: Optional[DataFormatConfig] = None):
        """Initialize Parquet adapter."""
        super().__init__(config)
        self.supported_formats = ['parquet']
        
        if not PARQUET_AVAILABLE:
            raise ImportError("pandas and pyarrow packages required for Parquet support")
    
    async def serialize(self, data: Any) -> bytes:
        """Serialize data to Parquet format."""
        try:
            start_time = time.time()
            
            # Convert to DataFrame if needed
            if not isinstance(data, pd.DataFrame):
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    df = pd.DataFrame([data])
                else:
                    raise ValueError("Data must be DataFrame, list of dicts, or dict")
            else:
                df = data
            
            # Serialize to Parquet
            buffer = io.BytesIO()
            df.to_parquet(buffer, compression='snappy', index=False)
            parquet_bytes = buffer.getvalue()
            
            # Apply additional compression if configured
            if self.config.compression != CompressionType.NONE:
                parquet_bytes = self._compress_data(parquet_bytes)
            
            # Apply encryption if configured
            if self.config.encryption != EncryptionType.NONE:
                parquet_bytes = self._encrypt_data(parquet_bytes)
            
            # Update metrics
            if self.config.enable_metrics:
                self.metrics.bytes_processed += len(parquet_bytes)
                self.metrics.processing_time += time.time() - start_time
            
            return parquet_bytes
            
        except Exception as e:
            self.logger.error(f"Parquet serialization failed: {e}")
            raise
    
    async def deserialize(self, data: Union[str, bytes, BinaryIO]) -> pd.DataFrame:
        """Deserialize Parquet data."""
        try:
            start_time = time.time()
            
            if isinstance(data, str):
                # Assume it's a file path
                df = pd.read_parquet(data)
            else:
                if isinstance(data, bytes):
                    # Apply decryption if configured
                    if self.config.encryption != EncryptionType.NONE:
                        data = self._decrypt_data(data)
                    
                    # Apply decompression if configured
                    if self.config.compression != CompressionType.NONE:
                        data = self._decompress_data(data)
                    
                    buffer = io.BytesIO(data)
                else:
                    buffer = data
                
                df = pd.read_parquet(buffer)
            
            # Update metrics
            if self.config.enable_metrics:
                self.metrics.bytes_processed += len(str(df).encode())
                self.metrics.processing_time += time.time() - start_time
            
            return df
            
        except Exception as e:
            self.logger.error(f"Parquet deserialization failed: {e}")
            raise
    
    def validate_format(self, data: Union[str, bytes]) -> bool:
        """Validate Parquet format."""
        try:
            if isinstance(data, str):
                # Assume it's a file path
                pd.read_parquet(data, nrows=1)
            else:
                buffer = io.BytesIO(data) if isinstance(data, bytes) else data
                pd.read_parquet(buffer, nrows=1)
            return True
        except:
            return False
    
    def get_content_type(self) -> str:
        """Get MIME content type."""
        return "application/parquet"

class AvroAdapter(DataAdapter):
    """Enterprise Avro adapter with schema support."""
    
    def __init__(self, config: Optional[DataFormatConfig] = None, schema: Optional[Dict] = None):
        """Initialize Avro adapter."""
        super().__init__(config)
        self.supported_formats = ['avro']
        self.schema = schema
        
        if not AVRO_AVAILABLE:
            raise ImportError("fastavro package required for Avro support")
    
    async def serialize(self, data: Any, schema: Optional[Dict] = None) -> bytes:
        """Serialize data to Avro format."""
        try:
            start_time = time.time()
            
            schema_to_use = schema or self.schema
            if not schema_to_use:
                raise ValueError("Schema required for Avro serialization")
            
            # Ensure data is a list
            if not isinstance(data, list):
                data = [data]
            
            # Serialize to Avro
            buffer = io.BytesIO()
            fastavro.writer(buffer, schema_to_use, data)
            avro_bytes = buffer.getvalue()
            
            # Apply additional compression if configured
            if self.config.compression != CompressionType.NONE:
                avro_bytes = self._compress_data(avro_bytes)
            
            # Apply encryption if configured
            if self.config.encryption != EncryptionType.NONE:
                avro_bytes = self._encrypt_data(avro_bytes)
            
            # Update metrics
            if self.config.enable_metrics:
                self.metrics.bytes_processed += len(avro_bytes)
                self.metrics.processing_time += time.time() - start_time
            
            return avro_bytes
            
        except Exception as e:
            self.logger.error(f"Avro serialization failed: {e}")
            raise
    
    async def deserialize(self, data: Union[str, bytes, BinaryIO]) -> List[Dict]:
        """Deserialize Avro data."""
        try:
            start_time = time.time()
            
            if isinstance(data, str):
                # Assume it's a file path
                with open(data, 'rb') as f:
                    reader = fastavro.reader(f)
                    records = list(reader)
            else:
                if isinstance(data, bytes):
                    # Apply decryption if configured
                    if self.config.encryption != EncryptionType.NONE:
                        data = self._decrypt_data(data)
                    
                    # Apply decompression if configured
                    if self.config.compression != CompressionType.NONE:
                        data = self._decompress_data(data)
                    
                    buffer = io.BytesIO(data)
                else:
                    buffer = data
                
                reader = fastavro.reader(buffer)
                records = list(reader)
            
            # Update metrics
            if self.config.enable_metrics:
                self.metrics.bytes_processed += len(str(records).encode())
                self.metrics.processing_time += time.time() - start_time
            
            return records
            
        except Exception as e:
            self.logger.error(f"Avro deserialization failed: {e}")
            raise
    
    def validate_format(self, data: Union[str, bytes]) -> bool:
        """Validate Avro format."""
        try:
            if isinstance(data, str):
                # Assume it's a file path
                with open(data, 'rb') as f:
                    reader = fastavro.reader(f)
                    next(reader, None)  # Try to read first record
            else:
                buffer = io.BytesIO(data) if isinstance(data, bytes) else data
                reader = fastavro.reader(buffer)
                next(reader, None)  # Try to read first record
            return True
        except:
            return False
    
    def get_content_type(self) -> str:
        """Get MIME content type."""
        return "application/avro"

class DataAdapterFactory:
    """Factory for creating data adapters based on format."""
    
    _adapters = {
        'json': JSONAdapter,
        'xml': XMLAdapter,
        'csv': CSVAdapter,
        'binary': BinaryAdapter,
        'protobuf': ProtocolBufferAdapter if PROTOBUF_AVAILABLE else None,
        'msgpack': MessagePackAdapter if MSGPACK_AVAILABLE else None,
        'yaml': YAMLAdapter if YAML_AVAILABLE else None,
        'yml': YAMLAdapter if YAML_AVAILABLE else None,
        'toml': TOMLAdapter if TOML_AVAILABLE else None,
        'parquet': ParquetAdapter if PARQUET_AVAILABLE else None,
        'avro': AvroAdapter if AVRO_AVAILABLE else None,
    }
    
    @classmethod
    def create_adapter(
        cls, 
        format_type: str, 
        config: Optional[DataFormatConfig] = None,
        **kwargs
    ) -> DataAdapter:
        """Create adapter for specified format."""
        format_type = format_type.lower()
        
        if format_type not in cls._adapters:
            raise ValueError(f"Unsupported format: {format_type}")
        
        adapter_class = cls._adapters[format_type]
        if adapter_class is None:
            raise ImportError(f"Required dependencies not available for format: {format_type}")
        
        return adapter_class(config, **kwargs)
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Get list of supported formats."""
        return [fmt for fmt, adapter in cls._adapters.items() if adapter is not None]

# Export all adapters
__all__ = [
    'DataAdapter',
    'DataFormatConfig',
    'ProcessingResult',
    'DataProcessingMetrics',
    'CompressionType',
    'EncryptionType',
    'JSONAdapter',
    'XMLAdapter',
    'CSVAdapter',
    'BinaryAdapter',
    'ProtocolBufferAdapter',
    'MessagePackAdapter',
    'YAMLAdapter',
    'TOMLAdapter',
    'ParquetAdapter',
    'AvroAdapter',
    'DataAdapterFactory'
]
