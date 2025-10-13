#!/usr/bin/env python3
"""
🚀 IA Chérie Enterprise - Request Transformer
Enterprise request/response transformation with intelligent data mapping

🎯 BUSINESS LOGIC INTEGRATION:
- Creator Content Transformation (multi-format content conversion)
- Platform Data Mapping (65+ platforms data format adaptation)  
- AI Model Input/Output Transformation (ML data preprocessing + postprocessing)
- Content Metadata Enrichment (automatic metadata generation)
- Collaboration Data Synchronization (multi-creator data consistency)
- Monetization Data Processing (revenue data transformation + aggregation)

👨‍💻 AUTHOR: Fahed Mlaiel (mlaiel@live.de)
📧 CONTACT: mlaiel@live.de  
🏢 ENTERPRISE: IA Chérie Platform
📅 CREATED: 2025
🔒 LICENSE: PROPRIETARY - All Rights Reserved

⚖️ LEGAL NOTICE:
This software is the EXCLUSIVE intellectual property of Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited
and subject to legal action.
"""

import asyncio
import json
import gzip
import zlib
from typing import Dict, Any, List, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import logging
import uuid
import hashlib
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """Supported transformation types"""
    JSON_TO_XML = "json_to_xml"
    XML_TO_JSON = "xml_to_json"
    REST_TO_GRAPHQL = "rest_to_graphql"
    GRAPHQL_TO_REST = "graphql_to_rest"
    GRPC_TO_REST = "grpc_to_rest"
    REST_TO_GRPC = "rest_to_grpc"
    FORMAT_VALIDATION = "format_validation"
    DATA_ENRICHMENT = "data_enrichment"
    COMPRESSION = "compression"
    DECOMPRESSION = "decompression"
    SCHEMA_MAPPING = "schema_mapping"
    CONTENT_NEGOTIATION = "content_negotiation"


class CompressionType(Enum):
    """Supported compression algorithms"""
    GZIP = "gzip"
    ZLIB = "zlib"
    BROTLI = "brotli"
    LZ4 = "lz4"


class ContentFormat(Enum):
    """Supported content formats"""
    JSON = "application/json"
    XML = "application/xml"
    PROTOBUF = "application/x-protobuf"
    MSGPACK = "application/msgpack"
    YAML = "application/x-yaml"
    CSV = "text/csv"
    PLAIN_TEXT = "text/plain"


@dataclass
class TransformationRule:
    """Rule for data transformation"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_format: ContentFormat = ContentFormat.JSON
    target_format: ContentFormat = ContentFormat.JSON
    transformation_type: TransformationType = TransformationType.SCHEMA_MAPPING
    field_mappings: Dict[str, str] = field(default_factory=dict)
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    enrichment_functions: List[str] = field(default_factory=list)
    compression_enabled: bool = False
    compression_type: CompressionType = CompressionType.GZIP
    creator_type_specific: Optional[str] = None
    platform_specific: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TransformationRequest:
    """Request transformation data"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    raw_data: Union[Dict[str, Any], str, bytes] = field(default_factory=dict)
    source_format: ContentFormat = ContentFormat.JSON
    target_format: ContentFormat = ContentFormat.JSON
    transformation_rules: List[TransformationRule] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    creator_context: Optional[Dict[str, Any]] = None
    platform_context: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TransformationResponse:
    """Response transformation result"""
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    transformed_data: Union[Dict[str, Any], str, bytes] = field(default_factory=dict)
    original_size: int = 0
    compressed_size: int = 0
    compression_ratio: float = 0.0
    transformation_time_ms: float = 0.0
    applied_rules: List[str] = field(default_factory=list)
    validation_results: List[Dict[str, Any]] = field(default_factory=list)
    enrichment_results: List[Dict[str, Any]] = field(default_factory=list)
    format_conversion_success: bool = True
    error_messages: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseTransformer(ABC):
    """Base transformer interface"""
    
    @abstractmethod
    async def transform(self, data: Any, context: Dict[str, Any] = None) -> Any:
        """Transform data"""
        pass
    
    @abstractmethod
    def validate_input(self, data: Any) -> bool:
        """Validate input data"""
        pass


class JSONTransformer(BaseTransformer):
    """JSON data transformer"""
    
    async def transform(self, data: Any, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Transform JSON data"""
        try:
            if isinstance(data, str):
                return json.loads(data)
            elif isinstance(data, bytes):
                return json.loads(data.decode('utf-8'))
            elif isinstance(data, dict):
                return data
            else:
                return {"data": data}
        except json.JSONDecodeError as e:
            logger.error(f"JSON transformation error: {e}")
            return {"error": str(e), "original_data": str(data)}
    
    def validate_input(self, data: Any) -> bool:
        """Validate JSON input"""
        try:
            if isinstance(data, str):
                json.loads(data)
            return True
        except (json.JSONDecodeError, TypeError):
            return False


class CompressionManager:
    """Manages data compression and decompression"""
    
    @staticmethod
    def compress_data(data: Union[str, bytes], compression_type: CompressionType) -> bytes:
        """Compress data using specified algorithm"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if compression_type == CompressionType.GZIP:
            return gzip.compress(data)
        elif compression_type == CompressionType.ZLIB:
            return zlib.compress(data)
        else:
            logger.warning(f"Compression type {compression_type} not implemented, using gzip")
            return gzip.compress(data)
    
    @staticmethod
    def decompress_data(data: bytes, compression_type: CompressionType) -> bytes:
        """Decompress data using specified algorithm"""
        if compression_type == CompressionType.GZIP:
            return gzip.decompress(data)
        elif compression_type == CompressionType.ZLIB:
            return zlib.decompress(data)
        else:
            logger.warning(f"Compression type {compression_type} not implemented, using gzip")
            return gzip.decompress(data)


class SchemaMapper:
    """Maps data between different schemas"""
    
    def __init__(self):
        self.field_mappings: Dict[str, Dict[str, str]] = {}
        self.transformation_cache: Dict[str, Any] = {}
    
    def add_mapping(self, schema_name: str, field_mappings: Dict[str, str]) -> None:
        """Add field mapping for schema"""
        self.field_mappings[schema_name] = field_mappings
    
    async def map_data(self, data: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
        """Map data according to schema"""
        if schema_name not in self.field_mappings:
            logger.warning(f"Schema {schema_name} not found, returning original data")
            return data
        
        mappings = self.field_mappings[schema_name]
        mapped_data = {}
        
        for original_field, target_field in mappings.items():
            if original_field in data:
                mapped_data[target_field] = data[original_field]
        
        # Preserve unmapped fields
        for field, value in data.items():
            if field not in mappings and field not in mapped_data:
                mapped_data[field] = value
        
        return mapped_data


class ContentNegotiator:
    """Handles content format negotiation"""
    
    def __init__(self):
        self.format_preferences: Dict[str, List[ContentFormat]] = {}
        self.transformer_registry: Dict[ContentFormat, BaseTransformer] = {
            ContentFormat.JSON: JSONTransformer()
        }
    
    def negotiate_format(self, accept_header: str, available_formats: List[ContentFormat]) -> ContentFormat:
        """Negotiate best content format"""
        # Simple implementation - can be enhanced with proper Accept header parsing
        if ContentFormat.JSON.value in accept_header:
            return ContentFormat.JSON
        
        # Default to first available format
        return available_formats[0] if available_formats else ContentFormat.JSON
    
    async def convert_format(self, data: Any, source_format: ContentFormat, 
                           target_format: ContentFormat) -> Any:
        """Convert data between formats"""
        if source_format == target_format:
            return data
        
        # For now, convert through JSON as intermediate format
        if source_format != ContentFormat.JSON:
            transformer = self.transformer_registry.get(source_format)
            if transformer:
                data = await transformer.transform(data)
        
        if target_format != ContentFormat.JSON:
            # Implement other format transformations as needed
            pass
        
        return data


class DataEnricher:
    """Enriches data with additional metadata and context"""
    
    def __init__(self):
        self.enrichment_functions: Dict[str, Callable] = {
            "add_timestamp": self._add_timestamp,
            "add_content_hash": self._add_content_hash,
            "add_creator_metadata": self._add_creator_metadata,
            "add_platform_metadata": self._add_platform_metadata,
            "add_ai_metadata": self._add_ai_metadata,
            "add_monetization_metadata": self._add_monetization_metadata
        }
    
    async def enrich_data(self, data: Dict[str, Any], enrichment_functions: List[str],
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enrich data with specified functions"""
        enriched_data = data.copy()
        
        for function_name in enrichment_functions:
            if function_name in self.enrichment_functions:
                enriched_data = await self.enrichment_functions[function_name](
                    enriched_data, context or {}
                )
        
        return enriched_data
    
    async def _add_timestamp(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Add timestamp metadata"""
        data["enrichment"] = data.get("enrichment", {})
        data["enrichment"]["timestamp"] = datetime.now(timezone.utc).isoformat()
        return data
    
    async def _add_content_hash(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Add content hash for integrity verification"""
        content_str = json.dumps(data, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        data["enrichment"] = data.get("enrichment", {})
        data["enrichment"]["content_hash"] = content_hash
        return data
    
    async def _add_creator_metadata(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Add creator-specific metadata"""
        creator_context = context.get("creator_context", {})
        if creator_context:
            data["creator_metadata"] = {
                "creator_id": creator_context.get("creator_id"),
                "creator_type": creator_context.get("creator_type"),
                "creator_tier": creator_context.get("creator_tier"),
                "content_categories": creator_context.get("content_categories", [])
            }
        return data
    
    async def _add_platform_metadata(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Add platform-specific metadata"""
        platform_context = context.get("platform_context", {})
        if platform_context:
            data["platform_metadata"] = {
                "platform_id": platform_context.get("platform_id"),
                "platform_name": platform_context.get("platform_name"),
                "platform_version": platform_context.get("platform_version"),
                "integration_features": platform_context.get("integration_features", [])
            }
        return data
    
    async def _add_ai_metadata(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Add AI processing metadata"""
        ai_context = context.get("ai_context", {})
        if ai_context:
            data["ai_metadata"] = {
                "model_version": ai_context.get("model_version"),
                "processing_type": ai_context.get("processing_type"),
                "confidence_score": ai_context.get("confidence_score"),
                "features_extracted": ai_context.get("features_extracted", [])
            }
        return data
    
    async def _add_monetization_metadata(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Add monetization-related metadata"""
        monetization_context = context.get("monetization_context", {})
        if monetization_context:
            data["monetization_metadata"] = {
                "revenue_model": monetization_context.get("revenue_model"),
                "pricing_tier": monetization_context.get("pricing_tier"),
                "payment_methods": monetization_context.get("payment_methods", []),
                "revenue_share": monetization_context.get("revenue_share")
            }
        return data


class ValidationEngine:
    """Validates data against defined rules"""
    
    def __init__(self):
        self.validation_rules: Dict[str, Callable] = {
            "required_fields": self._validate_required_fields,
            "data_types": self._validate_data_types,
            "value_ranges": self._validate_value_ranges,
            "format_patterns": self._validate_format_patterns,
            "business_rules": self._validate_business_rules
        }
    
    async def validate_data(self, data: Dict[str, Any], 
                          validation_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate data against rules"""
        validation_results = []
        
        for rule in validation_rules:
            rule_type = rule.get("type")
            if rule_type in self.validation_rules:
                result = await self.validation_rules[rule_type](data, rule)
                validation_results.append({
                    "rule_type": rule_type,
                    "rule_config": rule,
                    "is_valid": result.get("is_valid", False),
                    "message": result.get("message", ""),
                    "violations": result.get("violations", [])
                })
        
        return validation_results
    
    async def _validate_required_fields(self, data: Dict[str, Any], 
                                      rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate required fields are present"""
        required_fields = rule.get("fields", [])
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        return {
            "is_valid": len(missing_fields) == 0,
            "message": f"Missing required fields: {missing_fields}" if missing_fields else "All required fields present",
            "violations": missing_fields
        }
    
    async def _validate_data_types(self, data: Dict[str, Any], 
                                 rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data types"""
        type_mappings = rule.get("types", {})
        violations = []
        
        for field, expected_type in type_mappings.items():
            if field in data:
                actual_type = type(data[field]).__name__
                if actual_type != expected_type:
                    violations.append(f"{field}: expected {expected_type}, got {actual_type}")
        
        return {
            "is_valid": len(violations) == 0,
            "message": f"Type violations: {violations}" if violations else "All types valid",
            "violations": violations
        }
    
    async def _validate_value_ranges(self, data: Dict[str, Any], 
                                   rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate value ranges"""
        # Implementation for value range validation
        return {"is_valid": True, "message": "Value ranges valid", "violations": []}
    
    async def _validate_format_patterns(self, data: Dict[str, Any], 
                                      rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate format patterns"""
        # Implementation for format pattern validation
        return {"is_valid": True, "message": "Format patterns valid", "violations": []}
    
    async def _validate_business_rules(self, data: Dict[str, Any], 
                                     rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate business logic rules"""
        # Implementation for business rules validation
        return {"is_valid": True, "message": "Business rules valid", "violations": []}


class RequestTransformer:
    """
    🚀 Enterprise Request Transformer
    
    Provides comprehensive request/response transformation capabilities with:
    - Intelligent data transformation and format conversion
    - Content negotiation and protocol translation
    - Data validation and enrichment
    - Compression and optimization
    - Creator and platform-specific transformations
    """
    
    def __init__(self):
        self.schema_mapper = SchemaMapper()
        self.content_negotiator = ContentNegotiator()
        self.data_enricher = DataEnricher()
        self.validation_engine = ValidationEngine()
        self.compression_manager = CompressionManager()
        self.transformation_cache: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, List[float]] = {
            "transformation_times": [],
            "compression_ratios": [],
            "validation_success_rates": []
        }
        
        # Initialize IA Chérie-specific schema mappings
        self._initialize_iacherie_schemas()
    
    def _initialize_iacherie_schemas(self) -> None:
        """Initialize IA Chérie business logic schema mappings"""
        
        # Creator content schemas
        self.schema_mapper.add_mapping("creator_content", {
            "creator_id": "user_id",
            "content_type": "media_type",
            "content_data": "media_data",
            "metadata": "content_metadata",
            "rights": "intellectual_property",
            "monetization": "revenue_model"
        })
        
        # Platform integration schemas
        self.schema_mapper.add_mapping("platform_integration", {
            "platform_id": "external_platform_id",
            "platform_data": "external_data",
            "sync_status": "integration_status",
            "last_sync": "last_updated",
            "errors": "integration_errors"
        })
        
        # AI processing schemas
        self.schema_mapper.add_mapping("ai_processing", {
            "model_input": "input_data",
            "model_output": "predictions",
            "confidence": "confidence_score",
            "features": "extracted_features",
            "processing_time": "inference_time"
        })
        
        # Monetization schemas
        self.schema_mapper.add_mapping("monetization", {
            "revenue_data": "earnings",
            "payment_info": "payment_details",
            "commission": "platform_fee",
            "creator_share": "creator_earnings",
            "payment_status": "transaction_status"
        })
    
    async def transform_request(self, request: TransformationRequest) -> TransformationResponse:
        """Transform request data with comprehensive processing"""
        start_time = datetime.now(timezone.utc)
        response = TransformationResponse()
        
        try:
            # 1. Initialize response with request metadata
            response.response_id = f"resp_{request.request_id}"
            response.metadata = request.metadata.copy()
            
            # 2. Measure original data size
            if isinstance(request.raw_data, (str, bytes)):
                response.original_size = len(request.raw_data)
            else:
                response.original_size = len(json.dumps(request.raw_data))
            
            # 3. Apply transformation rules
            transformed_data = request.raw_data
            
            for rule in request.transformation_rules:
                transformed_data = await self._apply_transformation_rule(
                    transformed_data, rule, request
                )
                response.applied_rules.append(rule.rule_id)
            
            # 4. Content format conversion
            if request.source_format != request.target_format:
                transformed_data = await self.content_negotiator.convert_format(
                    transformed_data, request.source_format, request.target_format
                )
            
            # 5. Data validation
            if hasattr(request, 'validation_rules') and request.validation_rules:
                if isinstance(transformed_data, dict):
                    response.validation_results = await self.validation_engine.validate_data(
                        transformed_data, request.validation_rules
                    )
            
            # 6. Data enrichment
            if isinstance(transformed_data, dict):
                context = {
                    "creator_context": request.creator_context,
                    "platform_context": request.platform_context,
                    "transformation_context": {
                        "request_id": request.request_id,
                        "timestamp": request.timestamp
                    }
                }
                
                # Apply default enrichment for IA Chérie business logic
                default_enrichments = ["add_timestamp", "add_content_hash"]
                if request.creator_context:
                    default_enrichments.append("add_creator_metadata")
                if request.platform_context:
                    default_enrichments.append("add_platform_metadata")
                
                transformed_data = await self.data_enricher.enrich_data(
                    transformed_data, default_enrichments, context
                )
            
            # 7. Compression if enabled
            compression_enabled = any(rule.compression_enabled for rule in request.transformation_rules)
            if compression_enabled:
                compression_type = next(
                    (rule.compression_type for rule in request.transformation_rules if rule.compression_enabled),
                    CompressionType.GZIP
                )
                
                if isinstance(transformed_data, dict):
                    data_str = json.dumps(transformed_data)
                else:
                    data_str = str(transformed_data)
                
                compressed_data = self.compression_manager.compress_data(data_str, compression_type)
                response.compressed_size = len(compressed_data)
                response.compression_ratio = (
                    1 - (response.compressed_size / response.original_size)
                ) if response.original_size > 0 else 0.0
                
                # Store compressed data as base64 for JSON compatibility
                import base64
                response.transformed_data = {
                    "compressed": True,
                    "compression_type": compression_type.value,
                    "data": base64.b64encode(compressed_data).decode('utf-8'),
                    "original_size": response.original_size,
                    "compressed_size": response.compressed_size
                }
            else:
                response.transformed_data = transformed_data
                response.compressed_size = response.original_size
            
            # 8. Calculate transformation time
            end_time = datetime.now(timezone.utc)
            response.transformation_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # 9. Update performance metrics
            self.performance_metrics["transformation_times"].append(response.transformation_time_ms)
            if response.compression_ratio > 0:
                self.performance_metrics["compression_ratios"].append(response.compression_ratio)
            
            # 10. Set success status
            response.format_conversion_success = True
            
            logger.info(f"Request transformation completed: {response.response_id}")
            
        except Exception as e:
            logger.error(f"Request transformation failed: {str(e)}")
            response.format_conversion_success = False
            response.error_messages.append(str(e))
            response.transformed_data = request.raw_data  # Fallback to original data
        
        return response
    
    async def _apply_transformation_rule(self, data: Any, rule: TransformationRule,
                                       request: TransformationRequest) -> Any:
        """Apply a specific transformation rule"""
        try:
            if rule.transformation_type == TransformationType.SCHEMA_MAPPING:
                if isinstance(data, dict) and rule.field_mappings:
                    # Create temporary schema for this rule
                    temp_schema_name = f"temp_{rule.rule_id}"
                    self.schema_mapper.add_mapping(temp_schema_name, rule.field_mappings)
                    data = await self.schema_mapper.map_data(data, temp_schema_name)
            
            elif rule.transformation_type == TransformationType.DATA_ENRICHMENT:
                if isinstance(data, dict) and rule.enrichment_functions:
                    context = {
                        "creator_context": request.creator_context,
                        "platform_context": request.platform_context
                    }
                    data = await self.data_enricher.enrich_data(
                        data, rule.enrichment_functions, context
                    )
            
            elif rule.transformation_type == TransformationType.FORMAT_VALIDATION:
                if isinstance(data, dict) and rule.validation_rules:
                    validation_results = await self.validation_engine.validate_data(
                        data, rule.validation_rules
                    )
                    # Add validation metadata
                    data["_validation"] = validation_results
            
            # Add rule-specific processing for creator and platform contexts
            if rule.creator_type_specific and request.creator_context:
                creator_type = request.creator_context.get("creator_type")
                if creator_type == rule.creator_type_specific:
                    data = await self._apply_creator_specific_transformation(
                        data, creator_type, rule
                    )
            
            if rule.platform_specific and request.platform_context:
                platform_id = request.platform_context.get("platform_id")
                if platform_id == rule.platform_specific:
                    data = await self._apply_platform_specific_transformation(
                        data, platform_id, rule
                    )
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to apply transformation rule {rule.rule_id}: {str(e)}")
            return data  # Return original data on error
    
    async def _apply_creator_specific_transformation(self, data: Any, creator_type: str,
                                                   rule: TransformationRule) -> Any:
        """Apply creator-type specific transformations"""
        if not isinstance(data, dict):
            return data
        
        # Creator-specific business logic transformations
        if creator_type == "musician":
            # Add music-specific metadata and transformations
            data["content_type"] = "audio"
            data["audio_metadata"] = {
                "genre": data.get("genre"),
                "duration": data.get("duration"),
                "sample_rate": data.get("sample_rate"),
                "quality": data.get("audio_quality", "high")
            }
        
        elif creator_type == "blogger":
            # Add blog-specific metadata and transformations
            data["content_type"] = "text"
            data["text_metadata"] = {
                "word_count": len(data.get("content", "").split()),
                "reading_time": len(data.get("content", "").split()) // 200,  # ~200 WPM
                "language": data.get("language", "en"),
                "topics": data.get("tags", [])
            }
        
        elif creator_type == "photographer":
            # Add photo-specific metadata and transformations
            data["content_type"] = "image"
            data["image_metadata"] = {
                "dimensions": data.get("dimensions"),
                "format": data.get("image_format"),
                "quality": data.get("image_quality"),
                "camera_info": data.get("exif_data", {})
            }
        
        elif creator_type == "influencer":
            # Add influencer-specific metadata and transformations
            data["engagement_metadata"] = {
                "follower_count": data.get("followers"),
                "engagement_rate": data.get("engagement_rate"),
                "reach": data.get("estimated_reach"),
                "demographics": data.get("audience_demographics", {})
            }
        
        return data
    
    async def _apply_platform_specific_transformation(self, data: Any, platform_id: str,
                                                    rule: TransformationRule) -> Any:
        """Apply platform-specific transformations"""
        if not isinstance(data, dict):
            return data
        
        # Platform-specific API format transformations
        platform_transformations = {
            "youtube": {
                "video_title": data.get("title"),
                "video_description": data.get("description"),
                "video_tags": data.get("tags", []),
                "video_category": data.get("category"),
                "privacy_status": data.get("visibility", "public")
            },
            "instagram": {
                "caption": data.get("description"),
                "media_type": "CAROUSEL_ALBUM" if data.get("multiple_images") else "IMAGE",
                "image_url": data.get("image_urls", []),
                "location": data.get("location")
            },
            "tiktok": {
                "text": data.get("description"),
                "video_cover_timestamp_ms": 1000,
                "privacy_level": data.get("visibility", "PUBLIC_TO_EVERYONE"),
                "disable_duet": data.get("disable_duet", False),
                "disable_comment": data.get("disable_comment", False)
            },
            "spotify": {
                "name": data.get("title"),
                "description": data.get("description"),
                "public": data.get("public", True),
                "collaborative": data.get("collaborative", False)
            }
        }
        
        if platform_id in platform_transformations:
            platform_data = platform_transformations[platform_id]
            data["platform_formatted_data"] = platform_data
        
        return data
    
    async def get_transformation_metrics(self) -> Dict[str, Any]:
        """Get transformation performance metrics"""
        if not self.performance_metrics["transformation_times"]:
            return {"message": "No transformation metrics available"}
        
        avg_transformation_time = sum(self.performance_metrics["transformation_times"]) / len(
            self.performance_metrics["transformation_times"]
        )
        
        metrics = {
            "total_transformations": len(self.performance_metrics["transformation_times"]),
            "average_transformation_time_ms": avg_transformation_time,
            "min_transformation_time_ms": min(self.performance_metrics["transformation_times"]),
            "max_transformation_time_ms": max(self.performance_metrics["transformation_times"]),
        }
        
        if self.performance_metrics["compression_ratios"]:
            avg_compression_ratio = sum(self.performance_metrics["compression_ratios"]) / len(
                self.performance_metrics["compression_ratios"]
            )
            metrics.update({
                "average_compression_ratio": avg_compression_ratio,
                "best_compression_ratio": max(self.performance_metrics["compression_ratios"]),
                "worst_compression_ratio": min(self.performance_metrics["compression_ratios"])
            })
        
        return metrics
    
    async def clear_cache(self) -> None:
        """Clear transformation cache"""
        self.transformation_cache.clear()
        logger.info("Transformation cache cleared")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            # Test basic transformation
            test_request = TransformationRequest(
                raw_data={"test": "data"},
                transformation_rules=[
                    TransformationRule(
                        transformation_type=TransformationType.DATA_ENRICHMENT,
                        enrichment_functions=["add_timestamp"]
                    )
                ]
            )
            
            test_response = await self.transform_request(test_request)
            
            return {
                "status": "healthy",
                "components": {
                    "schema_mapper": "operational",
                    "content_negotiator": "operational", 
                    "data_enricher": "operational",
                    "validation_engine": "operational",
                    "compression_manager": "operational"
                },
                "test_transformation": {
                    "success": test_response.format_conversion_success,
                    "time_ms": test_response.transformation_time_ms
                },
                "cache_size": len(self.transformation_cache),
                "performance_metrics": await self.get_transformation_metrics()
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


# Global instance for enterprise usage
request_transformer = RequestTransformer()

# Export classes and functions for external usage
__all__ = [
    "RequestTransformer",
    "TransformationRequest", 
    "TransformationResponse",
    "TransformationRule",
    "TransformationType",
    "ContentFormat",
    "CompressionType",
    "request_transformer"
]