"""Payload Transformer - Enterprise Data Transformation System

Industrial-grade webhook payload transformation and normalization engine
for multi-platform integrations with advanced mapping and validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written 
permission from Fahed Mlaiel <mlaiel@live.de> is strictly prohibited.
"""
import asyncio
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

import jsonschema
from jsonschema import validate, ValidationError as JSONSchemaValidationError

try:
    from core.exceptions import ValidationError, TransformationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ValidationError, TransformationError = globals().get('ValidationError, TransformationError', Exception)
from ...utils.performance_monitor import PerformanceMonitor
from ...security.encryption import ContentEncryption

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported webhook platforms"""
    GITHUB = "github"
    STRIPE = "stripe"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    TWITCH = "twitch"
    DISCORD = "discord"
    SLACK = "slack"
    WEBHOOK_GENERIC = "webhook_generic"
    CUSTOM = "custom"

class TransformationType(Enum):
    """Types of payload transformations"""
    NORMALIZE = "normalize"
    VALIDATE = "validate"
    ENRICH = "enrich"
    FILTER = "filter"
    MAP_FIELDS = "map_fields"
    SANITIZE = "sanitize"
    AGGREGATE = "aggregate"
    FORMAT = "format"

@dataclass
class TransformationRule:
    """Individual transformation rule configuration"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_name: str = None
    transformation_type: TransformationType = TransformationType.NORMALIZE
    source_field: str = None
    target_field: str = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    transformation_function: Optional[str] = None
    validation_schema: Optional[Dict[str, Any]] = None
    default_value: Any = None
    required: bool = False
    priority: int = 100
    enabled: bool = True

@dataclass
class PlatformMapping:
    """Platform-specific field mapping configuration"""
    platform: PlatformType
    mapping_version: str = "1.0"
    field_mappings: Dict[str, str] = field(default_factory=dict)
    transformation_rules: List[TransformationRule] = field(default_factory=list)
    validation_schema: Dict[str, Any] = field(default_factory=dict)
    preprocessing_rules: List[Dict[str, Any]] = field(default_factory=list)
    postprocessing_rules: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class TransformationContext:
    """Context information for payload transformation"""
    platform: PlatformType
    event_type: str
    source_payload: Dict[str, Any]
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None
    endpoint_id: Optional[str] = None
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class TransformationResult:
    """Result of payload transformation"""
    success: bool
    transformed_payload: Optional[Dict[str, Any]] = None
    original_payload: Optional[Dict[str, Any]] = None
    applied_rules: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class PayloadTransformer:
    """
    Industrial-grade webhook payload transformation engine
    
    Provides comprehensive payload transformation, normalization, and validation
    across multiple platforms with advanced mapping and business logic support.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.performance_monitor = PerformanceMonitor("payload_transformer")
        self.encryption = ContentEncryption()
        
        # Configuration
        self.max_payload_size = self.config.get('max_payload_size_bytes', 10 * 1024 * 1024)  # 10MB
        self.transformation_timeout = self.config.get('transformation_timeout_seconds', 30)
        self.enable_caching = self.config.get('enable_caching', True)
        self.cache_ttl = self.config.get('cache_ttl_seconds', 3600)
        
        # Internal state
        self._platform_mappings: Dict[PlatformType, PlatformMapping] = {}
        self._transformation_functions: Dict[str, Callable] = {}
        self._validation_schemas: Dict[str, Dict[str, Any]] = {}
        self._transformation_cache: Dict[str, TransformationResult] = {}
        
        # Initialize platform mappings
        self._initialize_platform_mappings()
        self._initialize_transformation_functions()
        self._initialize_validation_schemas()
        
        logger.info("PayloadTransformer initialized")

    async def transform_payload(
        self,
        context: TransformationContext,
        custom_rules: List[TransformationRule] = None
    ) -> TransformationResult:
        """
        Transform webhook payload according to platform mappings and rules
        
        Args:
            context: Transformation context with payload and metadata
            custom_rules: Optional custom transformation rules
            
        Returns:
            TransformationResult with transformed payload and metadata
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate input
            if not context.source_payload:
                raise ValidationError("Source payload is required")
            
            # Check payload size
            payload_size = len(json.dumps(context.source_payload).encode('utf-8'))
            if payload_size > self.max_payload_size:
                raise ValidationError(f"Payload size {payload_size} exceeds maximum {self.max_payload_size}")
            
            # Check cache first
            cache_key = self._generate_cache_key(context, custom_rules)
            if self.enable_caching and cache_key in self._transformation_cache:
                cached_result = self._transformation_cache[cache_key]
                logger.debug(f"Using cached transformation result for {cache_key}")
                return cached_result
            
            # Get platform mapping
            platform_mapping = self._platform_mappings.get(context.platform)
            if not platform_mapping:
                logger.warning(f"No mapping found for platform {context.platform}, using generic transformation")
                platform_mapping = self._get_generic_mapping()
            
            # Initialize result
            result = TransformationResult(
                success=False,
                original_payload=context.source_payload.copy(),
                metadata={
                    'platform': context.platform.value,
                    'event_type': context.event_type,
                    'request_id': context.request_id,
                    'transformation_timestamp': context.timestamp.isoformat()
                }
            )
            
            # Create working payload
            transformed_payload = context.source_payload.copy()
            applied_rules = []
            validation_errors = []
            warnings = []
            
            # Apply preprocessing rules
            transformed_payload, preprocessing_results = await self._apply_preprocessing_rules(
                transformed_payload, platform_mapping.preprocessing_rules, context
            )
            applied_rules.extend(preprocessing_results.get('applied_rules', []))
            warnings.extend(preprocessing_results.get('warnings', []))
            
            # Apply field mappings
            transformed_payload, mapping_results = await self._apply_field_mappings(
                transformed_payload, platform_mapping.field_mappings, context
            )
            applied_rules.extend(mapping_results.get('applied_rules', []))
            warnings.extend(mapping_results.get('warnings', []))
            
            # Apply transformation rules
            all_rules = platform_mapping.transformation_rules.copy()
            if custom_rules:
                all_rules.extend(custom_rules)
            
            # Sort rules by priority
            all_rules.sort(key=lambda r: r.priority)
            
            for rule in all_rules:
                if not rule.enabled:
                    continue
                
                try:
                    transformed_payload, rule_result = await self._apply_transformation_rule(
                        transformed_payload, rule, context
                    )
                    
                    if rule_result['applied']:
                        applied_rules.append(rule.rule_name or rule.rule_id)
                        warnings.extend(rule_result.get('warnings', []))
                        
                except Exception as e:
                    error_msg = f"Error applying rule {rule.rule_name or rule.rule_id}: {str(e)}"
                    logger.error(error_msg)
                    validation_errors.append(error_msg)
                    
                    if rule.required:
                        raise TransformationError(f"Required transformation rule failed: {error_msg}")
            
            # Apply postprocessing rules
            transformed_payload, postprocessing_results = await self._apply_postprocessing_rules(
                transformed_payload, platform_mapping.postprocessing_rules, context
            )
            applied_rules.extend(postprocessing_results.get('applied_rules', []))
            warnings.extend(postprocessing_results.get('warnings', []))
            
            # Validate transformed payload
            if platform_mapping.validation_schema:
                validation_result = await self._validate_payload(
                    transformed_payload, platform_mapping.validation_schema
                )
                if not validation_result['valid']:
                    validation_errors.extend(validation_result['errors'])
            
            # Enrich with metadata
            transformed_payload = await self._enrich_payload_metadata(
                transformed_payload, context
            )
            
            # Calculate processing time
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Update result
            result.success = len(validation_errors) == 0
            result.transformed_payload = transformed_payload
            result.applied_rules = applied_rules
            result.validation_errors = validation_errors
            result.warnings = warnings
            result.processing_time_ms = processing_time
            result.metadata.update({
                'transformation_rules_applied': len(applied_rules),
                'validation_errors_count': len(validation_errors),
                'warnings_count': len(warnings),
                'original_payload_size': payload_size,
                'transformed_payload_size': len(json.dumps(transformed_payload).encode('utf-8'))
            })
            
            # Cache result if successful
            if self.enable_caching and result.success:
                self._transformation_cache[cache_key] = result
            
            # Record metrics
            await self.performance_monitor.record_operation(
                operation="payload_transformation",
                duration_ms=processing_time,
                metadata={
                    'platform': context.platform.value,
                    'success': result.success,
                    'rules_applied': len(applied_rules)
                }
            )
            
            logger.info(f"Payload transformation completed for {context.platform.value} in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"Payload transformation failed: {e}")
            
            return TransformationResult(
                success=False,
                original_payload=context.source_payload.copy(),
                validation_errors=[str(e)],
                processing_time_ms=processing_time,
                metadata={
                    'error': str(e),
                    'platform': context.platform.value,
                    'event_type': context.event_type
                }
            )

    async def validate_payload(
        self,
        payload: Dict[str, Any],
        platform: PlatformType,
        event_type: str = None,
        custom_schema: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Validate payload against platform schema
        
        Args:
            payload: Payload to validate
            platform: Platform type
            event_type: Optional event type for specific validation
            custom_schema: Optional custom validation schema
            
        Returns:
            Validation result
        """
        try:
            # Determine validation schema
            validation_schema = custom_schema
            
            if not validation_schema:
                platform_mapping = self._platform_mappings.get(platform)
                if platform_mapping and platform_mapping.validation_schema:
                    validation_schema = platform_mapping.validation_schema
                else:
                    # Use event-specific schema if available
                    schema_key = f"{platform.value}_{event_type}" if event_type else platform.value
                    validation_schema = self._validation_schemas.get(schema_key)
            
            if not validation_schema:
                return {
                    'valid': True,
                    'message': 'No validation schema available'
                }
            
            # Perform validation
            return await self._validate_payload(payload, validation_schema)
            
        except Exception as e:
            logger.error(f"Payload validation failed: {e}")
            return {
                'valid': False,
                'errors': [str(e)]
            }

    async def add_platform_mapping(
        self,
        platform: PlatformType,
        mapping: PlatformMapping
    ) -> None:
        """Add or update platform mapping configuration"""
        self._platform_mappings[platform] = mapping
        logger.info(f"Platform mapping added/updated for {platform.value}")

    async def add_transformation_function(
        self,
        function_name: str,
        function: Callable
    ) -> None:
        """Add custom transformation function"""
        self._transformation_functions[function_name] = function
        logger.info(f"Transformation function registered: {function_name}")

    async def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return [platform.value for platform in self._platform_mappings.keys()]

    async def get_platform_mapping(
        self,
        platform: PlatformType
    ) -> Optional[PlatformMapping]:
        """Get platform mapping configuration"""
        return self._platform_mappings.get(platform)

    async def clear_cache(self) -> None:
        """Clear transformation cache"""
        self._transformation_cache.clear()
        logger.info("Transformation cache cleared")

    # Private methods
    
    def _initialize_platform_mappings(self) -> None:
        """Initialize default platform mappings"""
        
        # GitHub webhook mapping
        github_mapping = PlatformMapping(
            platform=PlatformType.GITHUB,
            field_mappings={
                'repository.full_name': 'repository_name',
                'repository.id': 'repository_id',
                'repository.owner.login': 'repository_owner',
                'sender.login': 'user_login',
                'sender.id': 'user_id',
                'action': 'event_action',
                'number': 'issue_number',
                'pull_request.number': 'pr_number'
            },
            transformation_rules=[
                TransformationRule(
                    rule_name="normalize_github_event",
                    transformation_type=TransformationType.NORMALIZE,
                    source_field="zen",
                    transformation_function="remove_field"
                ),
                TransformationRule(
                    rule_name="extract_repository_info",
                    transformation_type=TransformationType.ENRICH,
                    transformation_function="extract_github_repository_info"
                )
            ]
        )
        self._platform_mappings[PlatformType.GITHUB] = github_mapping
        
        # Stripe webhook mapping
        stripe_mapping = PlatformMapping(
            platform=PlatformType.STRIPE,
            field_mappings={
                'data.object.id': 'object_id',
                'data.object.object': 'object_type',
                'data.object.amount': 'amount_cents',
                'data.object.currency': 'currency',
                'data.object.customer': 'customer_id',
                'data.object.status': 'status',
                'type': 'event_type',
                'created': 'created_timestamp'
            },
            transformation_rules=[
                TransformationRule(
                    rule_name="convert_stripe_timestamp",
                    transformation_type=TransformationType.FORMAT,
                    source_field="created",
                    target_field="created_at",
                    transformation_function="timestamp_to_iso"
                ),
                TransformationRule(
                    rule_name="normalize_amount",
                    transformation_type=TransformationType.FORMAT,
                    source_field="amount_cents",
                    target_field="amount",
                    transformation_function="cents_to_dollars"
                )
            ]
        )
        self._platform_mappings[PlatformType.STRIPE] = stripe_mapping
        
        # YouTube webhook mapping
        youtube_mapping = PlatformMapping(
            platform=PlatformType.YOUTUBE,
            field_mappings={
                'snippet.channelId': 'channel_id',
                'snippet.channelTitle': 'channel_title',
                'snippet.videoId': 'video_id',
                'snippet.title': 'video_title',
                'snippet.description': 'video_description',
                'snippet.publishedAt': 'published_at',
                'statistics.viewCount': 'view_count',
                'statistics.likeCount': 'like_count',
                'statistics.commentCount': 'comment_count'
            },
            transformation_rules=[
                TransformationRule(
                    rule_name="normalize_youtube_metrics",
                    transformation_type=TransformationType.FORMAT,
                    transformation_function="convert_string_numbers"
                ),
                TransformationRule(
                    rule_name="extract_video_metadata",
                    transformation_type=TransformationType.ENRICH,
                    transformation_function="extract_youtube_metadata"
                )
            ]
        )
        self._platform_mappings[PlatformType.YOUTUBE] = youtube_mapping
        
        # Instagram webhook mapping
        instagram_mapping = PlatformMapping(
            platform=PlatformType.INSTAGRAM,
            field_mappings={
                'object': 'object_type',
                'entry[0].id': 'user_id',
                'entry[0].changes[0].field': 'changed_field',
                'entry[0].changes[0].value.media_id': 'media_id',
                'entry[0].changes[0].value.media_type': 'media_type',
                'entry[0].time': 'timestamp'
            },
            transformation_rules=[
                TransformationRule(
                    rule_name="normalize_instagram_entry",
                    transformation_type=TransformationType.NORMALIZE,
                    transformation_function="flatten_instagram_entry"
                )
            ]
        )
        self._platform_mappings[PlatformType.INSTAGRAM] = instagram_mapping
        
        # Generic webhook mapping
        generic_mapping = PlatformMapping(
            platform=PlatformType.WEBHOOK_GENERIC,
            field_mappings={},
            transformation_rules=[
                TransformationRule(
                    rule_name="add_metadata",
                    transformation_type=TransformationType.ENRICH,
                    transformation_function="add_generic_metadata"
                )
            ]
        )
        self._platform_mappings[PlatformType.WEBHOOK_GENERIC] = generic_mapping

    def _initialize_transformation_functions(self) -> None:
        """Initialize transformation functions"""
        
        self._transformation_functions.update({
            'remove_field': lambda payload, field: self._remove_field(payload, field),
            'timestamp_to_iso': lambda payload, field: self._timestamp_to_iso(payload, field),
            'cents_to_dollars': lambda payload, field: self._cents_to_dollars(payload, field),
            'convert_string_numbers': lambda payload: self._convert_string_numbers(payload),
            'flatten_instagram_entry': lambda payload: self._flatten_instagram_entry(payload),
            'extract_github_repository_info': lambda payload: self._extract_github_repository_info(payload),
            'extract_youtube_metadata': lambda payload: self._extract_youtube_metadata(payload),
            'add_generic_metadata': lambda payload: self._add_generic_metadata(payload),
            'sanitize_html': lambda payload, field: self._sanitize_html(payload, field),
            'validate_email': lambda payload, field: self._validate_email(payload, field),
            'normalize_url': lambda payload, field: self._normalize_url(payload, field),
            'format_phone_number': lambda payload, field: self._format_phone_number(payload, field)
        })

    def _initialize_validation_schemas(self) -> None:
        """Initialize validation schemas for platforms"""
        
        # GitHub event schema
        github_schema = {
            "type": "object",
            "required": ["action", "repository", "sender"],
            "properties": {
                "action": {"type": "string"},
                "repository": {
                    "type": "object",
                    "required": ["id", "name", "full_name"],
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "full_name": {"type": "string"}
                    }
                },
                "sender": {
                    "type": "object",
                    "required": ["id", "login"],
                    "properties": {
                        "id": {"type": "integer"},
                        "login": {"type": "string"}
                    }
                }
            }
        }
        self._validation_schemas["github"] = github_schema
        
        # Stripe event schema
        stripe_schema = {
            "type": "object",
            "required": ["type", "data"],
            "properties": {
                "type": {"type": "string"},
                "data": {
                    "type": "object",
                    "required": ["object"],
                    "properties": {
                        "object": {"type": "object"}
                    }
                },
                "created": {"type": "integer"}
            }
        }
        self._validation_schemas["stripe"] = stripe_schema
        
        # YouTube event schema
        youtube_schema = {
            "type": "object",
            "properties": {
                "snippet": {
                    "type": "object",
                    "properties": {
                        "channelId": {"type": "string"},
                        "videoId": {"type": "string"},
                        "title": {"type": "string"}
                    }
                }
            }
        }
        self._validation_schemas["youtube"] = youtube_schema

    async def _apply_preprocessing_rules(
        self,
        payload: Dict[str, Any],
        rules: List[Dict[str, Any]],
        context: TransformationContext
    ) -> tuple:
        """Apply preprocessing rules to payload"""
        applied_rules = []
        warnings = []
        
        for rule in rules:
            try:
                if rule.get('type') == 'remove_null_fields':
                    payload = self._remove_null_fields(payload)
                    applied_rules.append('remove_null_fields')
                    
                elif rule.get('type') == 'normalize_keys':
                    payload = self._normalize_keys(payload)
                    applied_rules.append('normalize_keys')
                    
                elif rule.get('type') == 'flatten_nested':
                    max_depth = rule.get('max_depth', 3)
                    payload = self._flatten_nested_dict(payload, max_depth)
                    applied_rules.append('flatten_nested')
                    
            except Exception as e:
                warning = f"Preprocessing rule {rule.get('type')} failed: {str(e)}"
                logger.warning(warning)
                warnings.append(warning)
        
        return payload, {
            'applied_rules': applied_rules,
            'warnings': warnings
        }

    async def _apply_field_mappings(
        self,
        payload: Dict[str, Any],
        mappings: Dict[str, str],
        context: TransformationContext
    ) -> tuple:
        """Apply field mappings to payload"""
        applied_rules = []
        warnings = []
        
        for source_field, target_field in mappings.items():
            try:
                value = self._get_nested_value(payload, source_field)
                if value is not None:
                    self._set_nested_value(payload, target_field, value)
                    applied_rules.append(f"map_{source_field}_to_{target_field}")
                    
                    # Remove original field if it's different from target
                    if source_field != target_field:
                        self._remove_nested_field(payload, source_field)
                        
            except Exception as e:
                warning = f"Field mapping {source_field} -> {target_field} failed: {str(e)}"
                logger.warning(warning)
                warnings.append(warning)
        
        return payload, {
            'applied_rules': applied_rules,
            'warnings': warnings
        }

    async def _apply_transformation_rule(
        self,
        payload: Dict[str, Any],
        rule: TransformationRule,
        context: TransformationContext
    ) -> tuple:
        """Apply individual transformation rule"""
        try:
            # Check conditions
            if rule.conditions and not self._check_conditions(payload, rule.conditions):
                return payload, {'applied': False}
            
            if rule.transformation_function and rule.transformation_function in self._transformation_functions:
                func = self._transformation_functions[rule.transformation_function]
                
                if rule.source_field:
                    payload = func(payload, rule.source_field)
                else:
                    payload = func(payload)
                
                return payload, {'applied': True}
            
            # Handle different transformation types
            if rule.transformation_type == TransformationType.NORMALIZE:
                payload = await self._apply_normalization(payload, rule)
            
            elif rule.transformation_type == TransformationType.VALIDATE:
                validation_result = await self._apply_validation_rule(payload, rule)
                if not validation_result['valid'] and rule.required:
                    raise ValidationError(f"Validation failed: {validation_result['errors']}")
            
            elif rule.transformation_type == TransformationType.ENRICH:
                payload = await self._apply_enrichment(payload, rule, context)
            
            elif rule.transformation_type == TransformationType.FILTER:
                payload = await self._apply_filter(payload, rule)
            
            elif rule.transformation_type == TransformationType.MAP_FIELDS:
                if rule.source_field and rule.target_field:
                    value = self._get_nested_value(payload, rule.source_field)
                    if value is not None:
                        self._set_nested_value(payload, rule.target_field, value)
            
            elif rule.transformation_type == TransformationType.SANITIZE:
                payload = await self._apply_sanitization(payload, rule)
            
            return payload, {'applied': True}
            
        except Exception as e:
            logger.error(f"Transformation rule {rule.rule_name} failed: {e}")
            return payload, {
                'applied': False,
                'error': str(e)
            }

    async def _apply_postprocessing_rules(
        self,
        payload: Dict[str, Any],
        rules: List[Dict[str, Any]],
        context: TransformationContext
    ) -> tuple:
        """Apply postprocessing rules to payload"""
        applied_rules = []
        warnings = []
        
        for rule in rules:
            try:
                if rule.get('type') == 'add_timestamps':
                    payload['processed_at'] = datetime.now(timezone.utc).isoformat()
                    applied_rules.append('add_timestamps')
                    
                elif rule.get('type') == 'calculate_checksums':
                    payload['payload_checksum'] = self._calculate_checksum(payload)
                    applied_rules.append('calculate_checksums')
                    
                elif rule.get('type') == 'add_version_info':
                    payload['transformation_version'] = '1.0.0'
                    applied_rules.append('add_version_info')
                    
            except Exception as e:
                warning = f"Postprocessing rule {rule.get('type')} failed: {str(e)}"
                logger.warning(warning)
                warnings.append(warning)
        
        return payload, {
            'applied_rules': applied_rules,
            'warnings': warnings
        }

    async def _validate_payload(
        self,
        payload: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate payload against JSON schema"""
        try:
            validate(payload, schema)
            return {'valid': True}
            
        except JSONSchemaValidationError as e:
            return {
                'valid': False,
                'errors': [str(e)]
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"]
            }

    async def _enrich_payload_metadata(
        self,
        payload: Dict[str, Any],
        context: TransformationContext
    ) -> Dict[str, Any]:
        """Enrich payload with transformation metadata"""
        payload['_metadata'] = {
            'transformation_id': str(uuid.uuid4()),
            'transformed_at': datetime.now(timezone.utc).isoformat(),
            'platform': context.platform.value,
            'event_type': context.event_type,
            'request_id': context.request_id,
            'version': '1.0.0'
        }
        
        if context.user_id:
            payload['_metadata']['user_id'] = context.user_id
            
        if context.endpoint_id:
            payload['_metadata']['endpoint_id'] = context.endpoint_id
        
        return payload

    def _generate_cache_key(
        self,
        context: TransformationContext,
        custom_rules: List[TransformationRule] = None
    ) -> str:
        """Generate cache key for transformation result"""
        key_components = [
            context.platform.value,
            context.event_type,
            str(hash(json.dumps(context.source_payload, sort_keys=True))),
        ]
        
        if custom_rules:
            rules_hash = str(hash(tuple(rule.rule_id for rule in custom_rules)))
            key_components.append(rules_hash)
        
        return ':'.join(key_components)

    def _get_generic_mapping(self) -> PlatformMapping:
        """Get generic platform mapping for unknown platforms"""
        return self._platform_mappings.get(PlatformType.WEBHOOK_GENERIC)

    # Utility methods for field operations
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = field_path.split('.')
        value = data
        
        for key in keys:
            # Handle array indices
            if '[' in key and ']' in key:
                key_name = key[:key.index('[')]
                index_str = key[key.index('[') + 1:key.index(']')]
                try:
                    index = int(index_str)
                    if key_name in value and isinstance(value[key_name], list):
                        if 0 <= index < len(value[key_name]):
                            value = value[key_name][index]
                        else:
                            return None
                    else:
                        return None
                except (ValueError, TypeError):
                    return None
            else:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
        
        return value

    def _set_nested_value(self, data: Dict[str, Any], field_path: str, value: Any) -> None:
        """Set value in nested dictionary using dot notation"""
        keys = field_path.split('.')
        current = data
        
        for i, key in enumerate(keys[:-1]):
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value

    def _remove_nested_field(self, data: Dict[str, Any], field_path: str) -> None:
        """Remove field from nested dictionary using dot notation"""
        keys = field_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return
        
        if isinstance(current, dict) and keys[-1] in current:
            del current[keys[-1]]

    def _remove_null_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove fields with null values"""
        if isinstance(data, dict):
            return {k: self._remove_null_fields(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [self._remove_null_fields(item) for item in data if item is not None]
        else:
            return data

    def _normalize_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize dictionary keys to snake_case"""
        if isinstance(data, dict):
            normalized = {}
            for key, value in data.items():
                # Convert camelCase/PascalCase to snake_case
                normalized_key = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
                normalized_key = re.sub('([a-z0-9])([A-Z])', r'\1_\2', normalized_key).lower()
                
                if isinstance(value, (dict, list)):
                    normalized[normalized_key] = self._normalize_keys(value)
                else:
                    normalized[normalized_key] = value
            return normalized
        elif isinstance(data, list):
            return [self._normalize_keys(item) for item in data]
        else:
            return data

    def _flatten_nested_dict(self, data: Dict[str, Any], max_depth: int, current_depth: int = 0) -> Dict[str, Any]:
        """Flatten nested dictionary up to max depth"""
        if current_depth >= max_depth or not isinstance(data, dict):
            return data
        
        flattened = {}
        for key, value in data.items():
            if isinstance(value, dict) and current_depth < max_depth:
                nested_flattened = self._flatten_nested_dict(value, max_depth, current_depth + 1)
                for nested_key, nested_value in nested_flattened.items():
                    flattened[f"{key}_{nested_key}"] = nested_value
            else:
                flattened[key] = value
        
        return flattened

    def _check_conditions(self, payload: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """Check if payload meets transformation conditions"""
        for field, expected_value in conditions.items():
            actual_value = self._get_nested_value(payload, field)
            
            if isinstance(expected_value, dict):
                # Handle operators
                if '$exists' in expected_value:
                    if expected_value['$exists'] and actual_value is None:
                        return False
                    if not expected_value['$exists'] and actual_value is not None:
                        return False
                
                if '$eq' in expected_value and actual_value != expected_value['$eq']:
                    return False
                
                if '$ne' in expected_value and actual_value == expected_value['$ne']:
                    return False
                
                if '$in' in expected_value and actual_value not in expected_value['$in']:
                    return False
                    
            else:
                if actual_value != expected_value:
                    return False
        
        return True

    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate checksum for payload"""
        import hashlib
        payload_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(payload_str.encode()).hexdigest()

    # Transformation function implementations
    
    def _remove_field(self, payload: Dict[str, Any], field: str) -> Dict[str, Any]:
        """Remove field from payload"""
        self._remove_nested_field(payload, field)
        return payload

    def _timestamp_to_iso(self, payload: Dict[str, Any], field: str) -> Dict[str, Any]:
        """Convert Unix timestamp to ISO format"""
        timestamp = self._get_nested_value(payload, field)
        if timestamp and isinstance(timestamp, (int, float)):
            iso_time = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
            self._set_nested_value(payload, field.replace('created', 'created_at'), iso_time)
        return payload

    def _cents_to_dollars(self, payload: Dict[str, Any], field: str) -> Dict[str, Any]:
        """Convert cents to dollars"""
        cents = self._get_nested_value(payload, field)
        if cents and isinstance(cents, (int, float)):
            dollars = cents / 100.0
            target_field = field.replace('cents', '').replace('_cents', '')
            self._set_nested_value(payload, target_field, dollars)
        return payload

    def _convert_string_numbers(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Convert string numbers to integers"""
        for key, value in payload.items():
            if isinstance(value, str) and value.isdigit():
                payload[key] = int(value)
            elif isinstance(value, dict):
                payload[key] = self._convert_string_numbers(value)
        return payload

    def _flatten_instagram_entry(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten Instagram webhook entry structure"""
        if 'entry' in payload and isinstance(payload['entry'], list) and payload['entry']:
            entry = payload['entry'][0]
            if 'changes' in entry and isinstance(entry['changes'], list) and entry['changes']:
                change = entry['changes'][0]
                payload.update({
                    'user_id': entry.get('id'),
                    'changed_field': change.get('field'),
                    'change_value': change.get('value'),
                    'timestamp': entry.get('time')
                })
        return payload

    def _extract_github_repository_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract GitHub repository information"""
        if 'repository' in payload:
            repo = payload['repository']
            payload['repository_info'] = {
                'name': repo.get('name'),
                'full_name': repo.get('full_name'),
                'private': repo.get('private', False),
                'owner': repo.get('owner', {}).get('login'),
                'default_branch': repo.get('default_branch', 'main')
            }
        return payload

    def _extract_youtube_metadata(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract YouTube video metadata"""
        if 'snippet' in payload:
            snippet = payload['snippet']
            payload['video_metadata'] = {
                'channel_id': snippet.get('channelId'),
                'video_id': snippet.get('videoId'),
                'title': snippet.get('title'),
                'description': snippet.get('description', '')[:500],  # Truncate description
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId')
            }
        return payload

    def _add_generic_metadata(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Add generic metadata to payload"""
        payload['_generic_metadata'] = {
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'payload_type': 'generic_webhook',
            'field_count': len(payload)
        }
        return payload

    def _sanitize_html(self, payload: Dict[str, Any], field: str) -> Dict[str, Any]:
        """Sanitize HTML content in field"""
        import html
        value = self._get_nested_value(payload, field)
        if value and isinstance(value, str):
            sanitized = html.escape(value)
            self._set_nested_value(payload, field, sanitized)
        return payload

    def _validate_email(self, payload: Dict[str, Any], field: str) -> Dict[str, Any]:
        """Validate email format"""
        email = self._get_nested_value(payload, field)
        if email and isinstance(email, str):
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            is_valid = re.match(email_pattern, email) is not None
            self._set_nested_value(payload, f"{field}_valid", is_valid)
        return payload

    def _normalize_url(self, payload: Dict[str, Any], field: str) -> Dict[str, Any]:
        """Normalize URL format"""
        url = self._get_nested_value(payload, field)
        if url and isinstance(url, str):
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            # Remove trailing slash
            url = url.rstrip('/')
            self._set_nested_value(payload, field, url)
        return payload

    def _format_phone_number(self, payload: Dict[str, Any], field: str) -> Dict[str, Any]:
        """Format phone number"""
        phone = self._get_nested_value(payload, field)
        if phone and isinstance(phone, str):
            # Remove non-digits
            digits = re.sub(r'\D', '', phone)
            # Format as US number if 10 digits
            if len(digits) == 10:
                formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                self._set_nested_value(payload, field, formatted)
        return payload

    async def _apply_normalization(self, payload: Dict[str, Any], rule: TransformationRule) -> Dict[str, Any]:
        """Apply normalization rule"""
        if rule.source_field:
            value = self._get_nested_value(payload, rule.source_field)
            if value is not None:
                # Apply default normalization
                if isinstance(value, str):
                    value = value.strip().lower()
                elif isinstance(value, list):
                    value = [item.strip().lower() if isinstance(item, str) else item for item in value]
                
                self._set_nested_value(payload, rule.target_field or rule.source_field, value)
        
        return payload

    async def _apply_validation_rule(self, payload: Dict[str, Any], rule: TransformationRule) -> Dict[str, Any]:
        """Apply validation rule"""
        if rule.validation_schema:
            return await self._validate_payload(payload, rule.validation_schema)
        return {'valid': True}

    async def _apply_enrichment(self, payload: Dict[str, Any], rule: TransformationRule, context: TransformationContext) -> Dict[str, Any]:
        """Apply enrichment rule"""
        if rule.target_field:
            enriched_value = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'platform': context.platform.value,
                'event_type': context.event_type
            }
            self._set_nested_value(payload, rule.target_field, enriched_value)
        
        return payload

    async def _apply_filter(self, payload: Dict[str, Any], rule: TransformationRule) -> Dict[str, Any]:
        """Apply filter rule"""
        if rule.conditions:
            # Remove fields that don't meet conditions
            for field, condition in rule.conditions.items():
                value = self._get_nested_value(payload, field)
                if value != condition:
                    self._remove_nested_field(payload, field)
        
        return payload

    async def _apply_sanitization(self, payload: Dict[str, Any], rule: TransformationRule) -> Dict[str, Any]:
        """Apply sanitization rule"""
        if rule.source_field:
            value = self._get_nested_value(payload, rule.source_field)
            if isinstance(value, str):
                # Basic sanitization
                sanitized = re.sub(r'[<>"\']', '', value)
                sanitized = sanitized.strip()
                self._set_nested_value(payload, rule.source_field, sanitized)
        
        return payload
