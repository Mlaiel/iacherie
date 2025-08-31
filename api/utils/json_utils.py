"""JSON Processing Utilities for IA Influencer Agent Platform
Advanced JSON handling, schema validation, and data serialization

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""import json
import jsonschema
from typing import Dict, Any, List, Optional, Union, Type, Callable
from dataclasses import dataclass, field, asdict, is_dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from pathlib import Path
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import gzip
import pickle
import yaml
import xml.etree.ElementTree as ET
import csv
import io

logger = logging.getLogger(__name__)


class SerializationFormat(Enum):
    """Serialization format enumeration"""    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    CSV = "csv"
    PICKLE = "pickle"


@dataclass
class ValidationResult:
    """JSON validation result"""    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    schema_version: Optional[str] = None
    validation_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return asdict(self)


@dataclass
class ProcessingStats:
    """JSON processing statistics"""    files_processed: int = 0
    records_processed: int = 0
    processing_time: float = 0.0
    compression_ratio: Optional[float] = None
    memory_usage: int = 0
    errors: List[str] = field(default_factory=list)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for complex data types"""    
    def default(self, obj):
        """Handle custom object serialization"""        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif is_dataclass(obj):
            return asdict(obj)
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return super().default(obj)


class JSONProcessor:
    """Advanced JSON processing with validation and transformation"""    
    def __init__(self, use_compression: bool = False):
        self.use_compression = use_compression
        self.custom_encoders = {}
        self.custom_decoders = {}
        self.schemas = {}
        self.processing_stats = ProcessingStats()
        
    def register_custom_encoder(self, obj_type: Type, encoder_func: Callable):
        """Register custom encoder for specific type"""        self.custom_encoders[obj_type] = encoder_func
    
    def register_custom_decoder(self, type_name: str, decoder_func: Callable):
        """Register custom decoder for specific type"""        self.custom_decoders[type_name] = decoder_func
    
    async def process_json_data(self, data: Any, 
                              validate_schema: Optional[str] = None) -> Dict[str, Any]:
        """Process JSON data with optional validation"""        try:
            start_time = datetime.utcnow()
            
            # Convert to JSON string
            json_string = self.serialize_to_json(data)
            
            # Validate against schema if provided
            validation_result = None
            if validate_schema and validate_schema in self.schemas:
                validation_result = await self.validate_against_schema(
                    json.loads(json_string), validate_schema
                )
            
            # Compress if enabled
            compressed_size = None
            if self.use_compression:
                compressed_data = gzip.compress(json_string.encode('utf-8'))
                compressed_size = len(compressed_data)
            
            # Update statistics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.processing_stats.records_processed += 1
            self.processing_stats.processing_time += processing_time
            
            if compressed_size:
                original_size = len(json_string.encode('utf-8'))
                self.processing_stats.compression_ratio = compressed_size / original_size
            
            return {
                'success': True,
                'json_string': json_string,
                'size_bytes': len(json_string.encode('utf-8')),
                'compressed_size': compressed_size,
                'validation_result': validation_result.to_dict() if validation_result else None,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"JSON processing failed: {str(e)}")
            self.processing_stats.errors.append(str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    def serialize_to_json(self, data: Any, indent: Optional[int] = None) -> str:
        """Serialize data to JSON string with custom encoders"""        class ExtendedJSONEncoder(CustomJSONEncoder):
            def default(self, obj):
                # Check custom encoders first
                obj_type = type(obj)
                if obj_type in self.custom_encoders:
                    return self.custom_encoders[obj_type](obj)
                
                return super().default(obj)
        
        ExtendedJSONEncoder.custom_encoders = self.custom_encoders
        
        return json.dumps(data, cls=ExtendedJSONEncoder, indent=indent, ensure_ascii=False)
    
    def deserialize_from_json(self, json_string: str) -> Any:
        """Deserialize JSON string with custom decoders"""        def custom_decoder(dct):
            # Apply custom decoders
            for key, value in dct.items():
                if key in self.custom_decoders:
                    dct[key] = self.custom_decoders[key](value)
            return dct
        
        return json.loads(json_string, object_hook=custom_decoder)
    
    async def validate_against_schema(self, data: Dict[str, Any], 
                                    schema_name: str) -> ValidationResult:
        """Validate JSON data against registered schema"""        try:
            start_time = datetime.utcnow()
            
            if schema_name not in self.schemas:
                return ValidationResult(
                    valid=False,
                    errors=[f"Schema '{schema_name}' not found"]
                )
            
            schema = self.schemas[schema_name]
            
            # Perform validation
            try:
                jsonschema.validate(instance=data, schema=schema)
                validation_result = ValidationResult(
                    valid=True,
                    schema_version=schema.get('version', 'unknown')
                )
            except jsonschema.ValidationError as e:
                validation_result = ValidationResult(
                    valid=False,
                    errors=[str(e)]
                )
            except jsonschema.SchemaError as e:
                validation_result = ValidationResult(
                    valid=False,
                    errors=[f"Schema error: {str(e)}"]
                )
            
            validation_result.validation_time = (
                datetime.utcnow() - start_time
            ).total_seconds()
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Schema validation failed: {str(e)}")
            return ValidationResult(
                valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    async def batch_process_files(self, file_paths: List[str],
                                output_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """Process multiple JSON files in batch"""        results = []
        
        async def process_file(file_path: str) -> Dict[str, Any]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                result = await self.process_json_data(data)
                result['input_file'] = file_path
                
                # Save processed result if output directory provided
                if output_dir and result['success']:
                    output_path = Path(output_dir) / f"processed_{Path(file_path).name}"
                    await self.save_json_file(data, str(output_path))
                    result['output_file'] = str(output_path)
                
                return result
                
            except Exception as e:
                return {
                    'success': False,
                    'input_file': file_path,
                    'error': str(e)
                }
        
        # Process files concurrently
        tasks = [process_file(file_path) for file_path in file_paths]
        results = await asyncio.gather(*tasks)
        
        # Update batch statistics
        self.processing_stats.files_processed += len(file_paths)
        
        return results
    
    async def save_json_file(self, data: Any, file_path: str, 
                           indent: int = 2, create_backup: bool = True) -> bool:
        """Save data to JSON file with backup option"""        try:
            file_path_obj = Path(file_path)
            
            # Create backup if file exists
            if create_backup and file_path_obj.exists():
                backup_path = file_path_obj.with_suffix(f'.bak.{file_path_obj.suffix}')
                file_path_obj.rename(backup_path)
            
            # Ensure directory exists
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON file
            json_string = self.serialize_to_json(data, indent=indent)
            
            if self.use_compression:
                # Write compressed file
                compressed_data = gzip.compress(json_string.encode('utf-8'))
                with open(f"{file_path}.gz", 'wb') as f:
                    f.write(compressed_data)
            else:
                # Write regular file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(json_string)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save JSON file {file_path}: {str(e)}")
            return False
    
    def load_json_file(self, file_path: str) -> Optional[Any]:
        """Load data from JSON file"""        try:
            file_path_obj = Path(file_path)
            
            if file_path.endswith('.gz') or file_path_obj.with_suffix(f'{file_path_obj.suffix}.gz').exists():
                # Load compressed file
                gz_path = file_path if file_path.endswith('.gz') else f"{file_path}.gz"
                with gzip.open(gz_path, 'rt', encoding='utf-8') as f:
                    json_string = f.read()
            else:
                # Load regular file
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_string = f.read()
            
            return self.deserialize_from_json(json_string)
            
        except Exception as e:
            logger.error(f"Failed to load JSON file {file_path}: {str(e)}")
            return None


class SchemaValidator:
    """JSON Schema validation and management"""    
    def __init__(self):
        self.schemas = {}
        self.validator_cache = {}
        
    def register_schema(self, name: str, schema: Dict[str, Any]):
        """Register JSON schema"""        try:
            # Validate schema itself
            jsonschema.Draft7Validator.check_schema(schema)
            self.schemas[name] = schema
            
            # Create validator instance
            self.validator_cache[name] = jsonschema.Draft7Validator(schema)
            
            logger.info(f"Schema '{name}' registered successfully")
            
        except jsonschema.SchemaError as e:
            logger.error(f"Invalid schema '{name}': {str(e)}")
            raise
    
    def load_schema_from_file(self, name: str, file_path: str):
        """Load schema from JSON file"""        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            self.register_schema(name, schema)
            
        except Exception as e:
            logger.error(f"Failed to load schema from {file_path}: {str(e)}")
            raise
    
    def validate(self, data: Any, schema_name: str) -> ValidationResult:
        """Validate data against schema"""        try:
            if schema_name not in self.validator_cache:
                return ValidationResult(
                    valid=False,
                    errors=[f"Schema '{schema_name}' not found"]
                )
            
            validator = self.validator_cache[schema_name]
            start_time = datetime.utcnow()
            
            errors = list(validator.iter_errors(data))
            
            validation_time = (datetime.utcnow() - start_time).total_seconds()
            
            if errors:
                error_messages = [f"{error.json_path}: {error.message}" for error in errors]
                return ValidationResult(
                    valid=False,
                    errors=error_messages,
                    validation_time=validation_time
                )
            else:
                return ValidationResult(
                    valid=True,
                    schema_version=self.schemas[schema_name].get('version'),
                    validation_time=validation_time
                )
                
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return ValidationResult(
                valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    def create_influencer_schema(self) -> Dict[str, Any]:
        """Create schema for influencer data"""        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "Influencer Profile Schema",
            "version": "1.0",
            "required": ["user_id", "username", "content_types", "primary_platforms"],
            "properties": {
                "user_id": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "minLength": 3,
                    "maxLength": 50
                },
                "username": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100
                },
                "display_name": {
                    "type": "string",
                    "maxLength": 200
                },
                "content_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["audio", "video", "image", "text", "mixed"]
                    },
                    "minItems": 1,
                    "uniqueItems": True
                },
                "primary_platforms": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["spotify", "youtube", "instagram", "tiktok", "twitter", "facebook"]
                    },
                    "minItems": 1,
                    "uniqueItems": True
                },
                "follower_count": {
                    "type": "object",
                    "patternProperties": {
                        "^(spotify|youtube|instagram|tiktok|twitter|facebook)$": {
                            "type": "integer",
                            "minimum": 0
                        }
                    }
                },
                "engagement_rates": {
                    "type": "object",
                    "patternProperties": {
                        "^(spotify|youtube|instagram|tiktok|twitter|facebook)$": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1
                        }
                    }
                },
                "collaboration_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                },
                "monetization_tier": {
                    "type": "string",
                    "enum": ["basic", "premium", "enterprise", "celebrity"]
                },
                "verified_status": {
                    "type": "boolean"
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time"
                }
            }
        }
    
    def create_content_schema(self) -> Dict[str, Any]:
        """Create schema for content data"""        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "Content Schema",
            "version": "1.0",
            "required": ["content_id", "content_type", "owner_id"],
            "properties": {
                "content_id": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9_-]+$"
                },
                "content_type": {
                    "type": "string",
                    "enum": ["audio", "video", "image", "text"]
                },
                "owner_id": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9_-]+$"
                },
                "title": {
                    "type": "string",
                    "maxLength": 500
                },
                "description": {
                    "type": "string",
                    "maxLength": 5000
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "maxLength": 50
                    },
                    "maxItems": 20
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "duration": {"type": "number", "minimum": 0},
                        "file_size": {"type": "integer", "minimum": 0},
                        "format": {"type": "string"},
                        "dimensions": {"type": "string"}
                    }
                },
                "protection_enabled": {
                    "type": "boolean"
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time"
                }
            }
        }


class DataSerializer:
    """Multi-format data serialization"""    
    def __init__(self):
        self.serializers = {
            SerializationFormat.JSON: self._serialize_json,
            SerializationFormat.YAML: self._serialize_yaml,
            SerializationFormat.XML: self._serialize_xml,
            SerializationFormat.CSV: self._serialize_csv,
            SerializationFormat.PICKLE: self._serialize_pickle
        }
        
        self.deserializers = {
            SerializationFormat.JSON: self._deserialize_json,
            SerializationFormat.YAML: self._deserialize_yaml,
            SerializationFormat.XML: self._deserialize_xml,
            SerializationFormat.CSV: self._deserialize_csv,
            SerializationFormat.PICKLE: self._deserialize_pickle
        }
    
    def serialize(self, data: Any, format_type: SerializationFormat) -> str:
        """Serialize data to specified format"""        try:
            serializer = self.serializers.get(format_type)
            if not serializer:
                raise ValueError(f"Unsupported serialization format: {format_type}")
            
            return serializer(data)
            
        except Exception as e:
            logger.error(f"Serialization failed: {str(e)}")
            raise
    
    def deserialize(self, data_string: str, format_type: SerializationFormat) -> Any:
        """Deserialize data from specified format"""        try:
            deserializer = self.deserializers.get(format_type)
            if not deserializer:
                raise ValueError(f"Unsupported deserialization format: {format_type}")
            
            return deserializer(data_string)
            
        except Exception as e:
            logger.error(f"Deserialization failed: {str(e)}")
            raise
    
    def _serialize_json(self, data: Any) -> str:
        """Serialize to JSON"""        return json.dumps(data, cls=CustomJSONEncoder, indent=2, ensure_ascii=False)
    
    def _deserialize_json(self, data_string: str) -> Any:
        """Deserialize from JSON"""        return json.loads(data_string)
    
    def _serialize_yaml(self, data: Any) -> str:
        """Serialize to YAML"""        return yaml.dump(data, default_flow_style=False, allow_unicode=True)
    
    def _deserialize_yaml(self, data_string: str) -> Any:
        """Deserialize from YAML"""        return yaml.safe_load(data_string)
    
    def _serialize_xml(self, data: Any, root_name: str = "root") -> str:
        """Serialize to XML"""        def dict_to_xml(element, data_dict):
            for key, value in data_dict.items():
                child = ET.SubElement(element, str(key))
                if isinstance(value, dict):
                    dict_to_xml(child, value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            dict_to_xml(child, item)
                        else:
                            item_elem = ET.SubElement(child, "item")
                            item_elem.text = str(item)
                else:
                    child.text = str(value)
        
        root = ET.Element(root_name)
        
        if isinstance(data, dict):
            dict_to_xml(root, data)
        else:
            root.text = str(data)
        
        return ET.tostring(root, encoding='unicode')
    
    def _deserialize_xml(self, data_string: str) -> Dict[str, Any]:
        """Deserialize from XML"""        def xml_to_dict(element):
            result = {}
            
            for child in element:
                if len(child) == 0:
                    # Leaf node
                    if child.tag in result:
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child.text)
                    else:
                        result[child.tag] = child.text
                else:
                    # Branch node
                    child_dict = xml_to_dict(child)
                    if child.tag in result:
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child_dict)
                    else:
                        result[child.tag] = child_dict
            
            return result
        
        root = ET.fromstring(data_string)
        return xml_to_dict(root)
    
    def _serialize_csv(self, data: List[Dict[str, Any]]) -> str:
        """Serialize list of dictionaries to CSV"""        if not data or not isinstance(data, list):
            raise ValueError("CSV serialization requires list of dictionaries")
        
        output = io.StringIO()
        
        if data:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                # Convert complex objects to strings
                processed_row = {}
                for key, value in row.items():
                    if isinstance(value, (dict, list)):
                        processed_row[key] = json.dumps(value)
                    elif isinstance(value, datetime):
                        processed_row[key] = value.isoformat()
                    else:
                        processed_row[key] = str(value)
                
                writer.writerow(processed_row)
        
        return output.getvalue()
    
    def _deserialize_csv(self, data_string: str) -> List[Dict[str, Any]]:
        """Deserialize CSV to list of dictionaries"""        input_stream = io.StringIO(data_string)
        reader = csv.DictReader(input_stream)
        
        result = []
        for row in reader:
            # Try to parse JSON strings back to objects
            processed_row = {}
            for key, value in row.items():
                try:
                    # Try to parse as JSON
                    parsed_value = json.loads(value)
                    processed_row[key] = parsed_value
                except (json.JSONDecodeError, TypeError):
                    # Keep as string
                    processed_row[key] = value
            
            result.append(processed_row)
        
        return result
    
    def _serialize_pickle(self, data: Any) -> str:
        """Serialize to pickle (base64 encoded)"""        pickled_data = pickle.dumps(data)
        import base64
        return base64.b64encode(pickled_data).decode('ascii')
    
    def _deserialize_pickle(self, data_string: str) -> Any:
        """Deserialize from pickle (base64 encoded)"""        import base64
        pickled_data = base64.b64decode(data_string.encode('ascii'))
        return pickle.loads(pickled_data)


class ConfigParser:
    """Configuration file parser supporting multiple formats"""    
    def __init__(self):
        self.serializer = DataSerializer()
        self.config_cache = {}
        
    def load_config(self, file_path: str, 
                   format_type: Optional[SerializationFormat] = None) -> Dict[str, Any]:
        """Load configuration from file"""        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                raise FileNotFoundError(f"Configuration file not found: {file_path}")
            
            # Auto-detect format if not specified
            if format_type is None:
                format_type = self._detect_format(file_path_obj)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            config_data = self.serializer.deserialize(content, format_type)
            
            # Cache configuration
            self.config_cache[file_path] = {
                'data': config_data,
                'format': format_type,
                'last_modified': file_path_obj.stat().st_mtime
            }
            
            return config_data
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {str(e)}")
            raise
    
    def save_config(self, config_data: Dict[str, Any], file_path: str,
                   format_type: SerializationFormat = SerializationFormat.JSON) -> bool:
        """Save configuration to file"""        try:
            serialized_data = self.serializer.serialize(config_data, format_type)
            
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(serialized_data)
            
            # Update cache
            self.config_cache[file_path] = {
                'data': config_data,
                'format': format_type,
                'last_modified': file_path_obj.stat().st_mtime
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {file_path}: {str(e)}")
            return False
    
    def _detect_format(self, file_path: Path) -> SerializationFormat:
        """Auto-detect configuration file format"""        suffix = file_path.suffix.lower()
        
        format_map = {
            '.json': SerializationFormat.JSON,
            '.yaml': SerializationFormat.YAML,
            '.yml': SerializationFormat.YAML,
            '.xml': SerializationFormat.XML,
            '.csv': SerializationFormat.CSV
        }
        
        return format_map.get(suffix, SerializationFormat.JSON)
    
    def reload_if_changed(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Reload configuration if file has been modified"""        try:
            file_path_obj = Path(file_path)
            
            if file_path not in self.config_cache:
                return self.load_config(file_path)
            
            current_mtime = file_path_obj.stat().st_mtime
            cached_mtime = self.config_cache[file_path]['last_modified']
            
            if current_mtime > cached_mtime:
                logger.info(f"Reloading modified configuration: {file_path}")
                return self.load_config(file_path, self.config_cache[file_path]['format'])
            
            return self.config_cache[file_path]['data']
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {str(e)}")
            return None


class MetadataExtractor:
    """Extract and manage metadata from various data sources"""    
    def __init__(self):
        self.extractors = {
            'file': self._extract_file_metadata,
            'json': self._extract_json_metadata,
            'content': self._extract_content_metadata
        }
    
    def extract_metadata(self, data: Any, source_type: str) -> Dict[str, Any]:
        """Extract metadata based on source type"""        try:
            extractor = self.extractors.get(source_type)
            if not extractor:
                return {'error': f'Unsupported source type: {source_type}'}
            
            return extractor(data)
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return {'error': str(e)}
    
    def _extract_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract file system metadata"""        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            return {'error': 'File not found'}
        
        stat = file_path_obj.stat()
        
        return {
            'filename': file_path_obj.name,
            'extension': file_path_obj.suffix,
            'size_bytes': stat.st_size,
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'accessed_at': datetime.fromtimestamp(stat.st_atime).isoformat(),
            'is_file': file_path_obj.is_file(),
            'is_directory': file_path_obj.is_dir(),
            'parent_directory': str(file_path_obj.parent),
            'absolute_path': str(file_path_obj.absolute())
        }
    
    def _extract_json_metadata(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from JSON structure"""        metadata = {
            'total_keys': len(json_data) if isinstance(json_data, dict) else 0,
            'data_types': {},
            'nested_levels': 0,
            'array_count': 0,
            'null_count': 0
        }
        
        def analyze_structure(obj, level=0):
            metadata['nested_levels'] = max(metadata['nested_levels'], level)
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    value_type = type(value).__name__
                    metadata['data_types'][value_type] = metadata['data_types'].get(value_type, 0) + 1
                    
                    if value is None:
                        metadata['null_count'] += 1
                    elif isinstance(value, (dict, list)):
                        analyze_structure(value, level + 1)
                        if isinstance(value, list):
                            metadata['array_count'] += 1
                            
            elif isinstance(obj, list):
                metadata['array_count'] += 1
                for item in obj:
                    analyze_structure(item, level + 1)
        
        analyze_structure(json_data)
        
        return metadata
    
    def _extract_content_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from content string"""        lines = content.split('\n')
        words = content.split()
        
        return {
            'character_count': len(content),
            'word_count': len(words),
            'line_count': len(lines),
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'average_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            'whitespace_count': sum(1 for char in content if char.isspace()),
            'digit_count': sum(1 for char in content if char.isdigit()),
            'alpha_count': sum(1 for char in content if char.isalpha()),
            'unique_words': len(set(word.lower() for word in words)),
            'encoding': 'utf-8',  # Assuming UTF-8 encoding
            'estimated_reading_time': max(1, len(words) // 200)  # Words per minute
        }


class JSONProcessingError(Exception):
    """Custom exception for JSON processing errors"""    pass
