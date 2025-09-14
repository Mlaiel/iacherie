"""
🎯 GATEWAY TRANSFORMATION SERVICE - ENTERPRISE MICROSERVICE
Request/response transformation service for API gateway with protocol conversion.

Author: Fahed Mlaiel
Copyright: © 2024-2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import aioredis
import yaml
import re

logger = logging.getLogger(__name__)

class TransformationType(Enum):
    """Transformation types"""
    JSON_TO_XML = "json_to_xml"
    XML_TO_JSON = "xml_to_json"
    FIELD_MAPPING = "field_mapping"
    FORMAT_CONVERSION = "format_conversion"
    PROTOCOL_CONVERSION = "protocol_conversion"
    DATA_ENRICHMENT = "data_enrichment"
    SCHEMA_VALIDATION = "schema_validation"
    CUSTOM_TRANSFORMATION = "custom_transformation"

@dataclass
class TransformationRule:
    """Transformation rule configuration"""
    id: str
    name: str
    endpoint_pattern: str
    method: Optional[str] = None
    transformation_type: TransformationType = TransformationType.FIELD_MAPPING
    enabled: bool = True
    priority: int = 0
    source_format: str = "json"
    target_format: str = "json"
    field_mappings: Dict[str, str] = None
    custom_script: Optional[str] = None
    validation_schema: Optional[Dict[str, Any]] = None
    enrichment_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.field_mappings is None:
            self.field_mappings = {}
        if self.enrichment_data is None:
            self.enrichment_data = {}

@dataclass
class TransformationContext:
    """Context for transformation execution"""
    request_id: str
    endpoint: str
    method: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    user_id: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class GatewayTransformation:
    """
    🎯 Gateway Transformation Service
    
    Comprehensive request/response transformation service with support for
    multiple data formats, field mapping, protocol conversion, and data enrichment.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        
        # Transformation rules
        self.transformation_rules: List[TransformationRule] = []
        self.compiled_patterns: Dict[str, re.Pattern] = {}
        
        # Custom transformers
        self.custom_transformers: Dict[str, Callable] = {}
        
        # Transformation metrics
        self.transformation_metrics = {
            'total_transformations': 0,
            'successful_transformations': 0,
            'failed_transformations': 0,
            'transformations_by_type': {t.value: 0 for t in TransformationType},
            'transformations_by_endpoint': {}
        }
        
        self.running = False
        
    async def initialize(self):
        """Initialize transformation service"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            
            # Load transformation rules
            await self._load_transformation_rules()
            
            # Register built-in transformers
            self._register_builtin_transformers()
            
            # Start background tasks
            asyncio.create_task(self._metrics_update_task())
            asyncio.create_task(self._rules_watch_task())
            
            self.running = True
            logger.info("Gateway Transformation service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize gateway transformation: {e}")
            raise
            
    async def _load_transformation_rules(self):
        """Load transformation rules from Redis"""
        try:
            rules_data = await self.redis.get("gateway:transformation:rules")
            if rules_data:
                rules_config = json.loads(rules_data)
                self.transformation_rules = [
                    TransformationRule(**rule) for rule in rules_config
                ]
                self._compile_patterns()
                
        except Exception as e:
            logger.error(f"Failed to load transformation rules: {e}")
            
    def _compile_patterns(self):
        """Compile regex patterns for endpoint matching"""
        self.compiled_patterns = {}
        for rule in self.transformation_rules:
            if rule.enabled:
                try:
                    # Convert path pattern to regex
                    pattern = rule.endpoint_pattern
                    # Replace path parameters like {id} with regex groups
                    pattern = re.sub(r'\{([^}]+)\}', r'(?P<\1>[^/]+)', pattern)
                    # Replace wildcards
                    pattern = pattern.replace('*', '.*')
                    
                    self.compiled_patterns[rule.id] = re.compile(f"^{pattern}$")
                except re.error as e:
                    logger.error(f"Invalid regex pattern for rule {rule.id}: {e}")
                    
    def _register_builtin_transformers(self):
        """Register built-in transformation functions"""
        self.custom_transformers.update({
            'uppercase_fields': self._uppercase_fields_transformer,
            'lowercase_fields': self._lowercase_fields_transformer,
            'remove_null_fields': self._remove_null_fields_transformer,
            'flatten_object': self._flatten_object_transformer,
            'add_timestamp': self._add_timestamp_transformer,
            'format_dates': self._format_dates_transformer,
            'sanitize_html': self._sanitize_html_transformer,
            'encrypt_sensitive': self._encrypt_sensitive_transformer
        })
        
    async def add_transformation_rule(self, rule: TransformationRule):
        """Add a new transformation rule"""
        # Remove existing rule with same ID
        self.transformation_rules = [r for r in self.transformation_rules if r.id != rule.id]
        
        # Add new rule
        self.transformation_rules.append(rule)
        
        # Sort by priority (higher priority first)
        self.transformation_rules.sort(key=lambda r: r.priority, reverse=True)
        
        # Recompile patterns
        self._compile_patterns()
        
        # Save to Redis
        await self._save_transformation_rules()
        
        logger.info(f"Added transformation rule {rule.id}")
        
    async def _save_transformation_rules(self):
        """Save transformation rules to Redis"""
        try:
            rules_config = [asdict(rule) for rule in self.transformation_rules]
            await self.redis.set(
                "gateway:transformation:rules", 
                json.dumps(rules_config, default=str)
            )
        except Exception as e:
            logger.error(f"Failed to save transformation rules: {e}")
            
    async def transform_request(self, data: Any, context: TransformationContext) -> Any:
        """Transform request data"""
        return await self._apply_transformations(data, context, "request")
        
    async def transform_response(self, data: Any, context: TransformationContext) -> Any:
        """Transform response data"""
        return await self._apply_transformations(data, context, "response")
        
    async def _apply_transformations(self, data: Any, context: TransformationContext, 
                                   direction: str) -> Any:
        """Apply transformation rules to data"""
        matching_rules = await self._find_matching_rules(context)
        
        if not matching_rules:
            return data
            
        transformed_data = data
        
        for rule in matching_rules:
            try:
                self.transformation_metrics['total_transformations'] += 1
                
                # Apply transformation based on type
                if rule.transformation_type == TransformationType.FIELD_MAPPING:
                    transformed_data = await self._apply_field_mapping(transformed_data, rule)
                    
                elif rule.transformation_type == TransformationType.JSON_TO_XML:
                    transformed_data = await self._json_to_xml(transformed_data, rule)
                    
                elif rule.transformation_type == TransformationType.XML_TO_JSON:
                    transformed_data = await self._xml_to_json(transformed_data, rule)
                    
                elif rule.transformation_type == TransformationType.FORMAT_CONVERSION:
                    transformed_data = await self._format_conversion(transformed_data, rule)
                    
                elif rule.transformation_type == TransformationType.DATA_ENRICHMENT:
                    transformed_data = await self._data_enrichment(transformed_data, rule, context)
                    
                elif rule.transformation_type == TransformationType.SCHEMA_VALIDATION:
                    await self._validate_schema(transformed_data, rule)
                    
                elif rule.transformation_type == TransformationType.CUSTOM_TRANSFORMATION:
                    transformed_data = await self._custom_transformation(transformed_data, rule, context)
                    
                self.transformation_metrics['successful_transformations'] += 1
                self.transformation_metrics['transformations_by_type'][rule.transformation_type.value] += 1
                
                # Update endpoint metrics
                endpoint = context.endpoint
                if endpoint not in self.transformation_metrics['transformations_by_endpoint']:
                    self.transformation_metrics['transformations_by_endpoint'][endpoint] = 0
                self.transformation_metrics['transformations_by_endpoint'][endpoint] += 1
                
            except Exception as e:
                self.transformation_metrics['failed_transformations'] += 1
                logger.error(f"Transformation failed for rule {rule.id}: {e}")
                # Continue with next rule instead of failing completely
                
        return transformed_data
        
    async def _find_matching_rules(self, context: TransformationContext) -> List[TransformationRule]:
        """Find transformation rules matching the context"""
        matching_rules = []
        
        for rule in self.transformation_rules:
            if not rule.enabled:
                continue
                
            # Check method match
            if rule.method and rule.method.upper() != context.method.upper():
                continue
                
            # Check endpoint pattern match
            pattern = self.compiled_patterns.get(rule.id)
            if pattern and pattern.match(context.endpoint):
                matching_rules.append(rule)
                
        return matching_rules
        
    async def _apply_field_mapping(self, data: Any, rule: TransformationRule) -> Any:
        """Apply field mapping transformation"""
        if not isinstance(data, dict) or not rule.field_mappings:
            return data
            
        transformed = {}
        
        for source_field, target_field in rule.field_mappings.items():
            if source_field in data:
                # Support nested field access with dot notation
                if '.' in target_field:
                    self._set_nested_field(transformed, target_field, data[source_field])
                else:
                    transformed[target_field] = data[source_field]
                    
        # Copy unmapped fields if not explicitly excluded
        for key, value in data.items():
            if key not in rule.field_mappings and key not in transformed:
                transformed[key] = value
                
        return transformed
        
    def _set_nested_field(self, obj: dict, field_path: str, value: Any):
        """Set nested field using dot notation"""
        keys = field_path.split('.')
        current = obj
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        current[keys[-1]] = value
        
    async def _json_to_xml(self, data: Any, rule: TransformationRule) -> str:
        """Convert JSON to XML"""
        if not isinstance(data, dict):
            return data
            
        root_name = rule.enrichment_data.get('root_element', 'root')
        root = ET.Element(root_name)
        
        def dict_to_xml(parent, dictionary):
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    element = ET.SubElement(parent, key)
                    dict_to_xml(element, value)
                elif isinstance(value, list):
                    for item in value:
                        element = ET.SubElement(parent, key)
                        if isinstance(item, dict):
                            dict_to_xml(element, item)
                        else:
                            element.text = str(item)
                else:
                    element = ET.SubElement(parent, key)
                    element.text = str(value)
                    
        dict_to_xml(root, data)
        return ET.tostring(root, encoding='unicode')
        
    async def _xml_to_json(self, data: str, rule: TransformationRule) -> dict:
        """Convert XML to JSON"""
        if not isinstance(data, str):
            return data
            
        try:
            root = ET.fromstring(data)
            
            def xml_to_dict(element):
                result = {}
                
                # Handle attributes
                if element.attrib:
                    result['@attributes'] = element.attrib
                    
                # Handle text content
                if element.text and element.text.strip():
                    if len(element) == 0:  # No children
                        return element.text.strip()
                    else:
                        result['#text'] = element.text.strip()
                        
                # Handle child elements
                for child in element:
                    child_data = xml_to_dict(child)
                    
                    if child.tag in result:
                        # Multiple elements with same tag - convert to array
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child_data)
                    else:
                        result[child.tag] = child_data
                        
                return result if result else None
                
            return {root.tag: xml_to_dict(root)}
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            return data
            
    async def _format_conversion(self, data: Any, rule: TransformationRule) -> Any:
        """Apply format conversion"""
        if rule.source_format == "yaml" and rule.target_format == "json":
            if isinstance(data, str):
                try:
                    return yaml.safe_load(data)
                except yaml.YAMLError:
                    return data
                    
        elif rule.source_format == "json" and rule.target_format == "yaml":
            if isinstance(data, (dict, list)):
                return yaml.dump(data, default_flow_style=False)
                
        return data
        
    async def _data_enrichment(self, data: Any, rule: TransformationRule, 
                             context: TransformationContext) -> Any:
        """Apply data enrichment"""
        if not isinstance(data, dict):
            return data
            
        enriched_data = data.copy()
        
        # Add enrichment data from rule
        for key, value in rule.enrichment_data.items():
            enriched_data[key] = value
            
        # Add context information
        enriched_data['_meta'] = {
            'request_id': context.request_id,
            'timestamp': context.timestamp.isoformat(),
            'endpoint': context.endpoint,
            'method': context.method
        }
        
        if context.user_id:
            enriched_data['_meta']['user_id'] = context.user_id
            
        return enriched_data
        
    async def _validate_schema(self, data: Any, rule: TransformationRule):
        """Validate data against schema"""
        if not rule.validation_schema:
            return
            
        # Simple schema validation (in production, use jsonschema library)
        def validate_field(value, schema):
            field_type = schema.get('type')
            if field_type == 'string' and not isinstance(value, str):
                raise ValueError(f"Expected string, got {type(value)}")
            elif field_type == 'number' and not isinstance(value, (int, float)):
                raise ValueError(f"Expected number, got {type(value)}")
            elif field_type == 'boolean' and not isinstance(value, bool):
                raise ValueError(f"Expected boolean, got {type(value)}")
                
        if isinstance(data, dict) and isinstance(rule.validation_schema, dict):
            required_fields = rule.validation_schema.get('required', [])
            properties = rule.validation_schema.get('properties', {})
            
            # Check required fields
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Required field '{field}' is missing")
                    
            # Validate field types
            for field, value in data.items():
                if field in properties:
                    validate_field(value, properties[field])
                    
    async def _custom_transformation(self, data: Any, rule: TransformationRule, 
                                   context: TransformationContext) -> Any:
        """Apply custom transformation"""
        if rule.custom_script and rule.custom_script in self.custom_transformers:
            transformer = self.custom_transformers[rule.custom_script]
            return await transformer(data, rule, context)
            
        return data
        
    # Built-in transformer functions
    async def _uppercase_fields_transformer(self, data: Any, rule: TransformationRule, 
                                          context: TransformationContext) -> Any:
        """Transform string fields to uppercase"""
        if isinstance(data, dict):
            fields = rule.enrichment_data.get('fields', [])
            for field in fields:
                if field in data and isinstance(data[field], str):
                    data[field] = data[field].upper()
        return data
        
    async def _lowercase_fields_transformer(self, data: Any, rule: TransformationRule, 
                                         context: TransformationContext) -> Any:
        """Transform string fields to lowercase"""
        if isinstance(data, dict):
            fields = rule.enrichment_data.get('fields', [])
            for field in fields:
                if field in data and isinstance(data[field], str):
                    data[field] = data[field].lower()
        return data
        
    async def _remove_null_fields_transformer(self, data: Any, rule: TransformationRule, 
                                            context: TransformationContext) -> Any:
        """Remove fields with null values"""
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if v is not None}
        return data
        
    async def _flatten_object_transformer(self, data: Any, rule: TransformationRule, 
                                        context: TransformationContext) -> Any:
        """Flatten nested object structure"""
        if not isinstance(data, dict):
            return data
            
        def flatten(obj, parent_key='', sep='_'):
            items = []
            for k, v in obj.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
            
        return flatten(data)
        
    async def _add_timestamp_transformer(self, data: Any, rule: TransformationRule, 
                                       context: TransformationContext) -> Any:
        """Add timestamp field"""
        if isinstance(data, dict):
            field_name = rule.enrichment_data.get('timestamp_field', 'timestamp')
            data[field_name] = datetime.utcnow().isoformat()
        return data
        
    async def _format_dates_transformer(self, data: Any, rule: TransformationRule, 
                                      context: TransformationContext) -> Any:
        """Format date fields"""
        if isinstance(data, dict):
            date_fields = rule.enrichment_data.get('date_fields', [])
            date_format = rule.enrichment_data.get('date_format', '%Y-%m-%d %H:%M:%S')
            
            for field in date_fields:
                if field in data:
                    try:
                        if isinstance(data[field], str):
                            # Parse and reformat
                            dt = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                            data[field] = dt.strftime(date_format)
                    except (ValueError, AttributeError):
                        continue
        return data
        
    async def _sanitize_html_transformer(self, data: Any, rule: TransformationRule, 
                                       context: TransformationContext) -> Any:
        """Sanitize HTML in string fields"""
        if isinstance(data, dict):
            html_fields = rule.enrichment_data.get('html_fields', [])
            for field in html_fields:
                if field in data and isinstance(data[field], str):
                    # Simple HTML tag removal (use bleach library in production)
                    import re
                    data[field] = re.sub('<[^<]+?>', '', data[field])
        return data
        
    async def _encrypt_sensitive_transformer(self, data: Any, rule: TransformationRule, 
                                           context: TransformationContext) -> Any:
        """Encrypt sensitive fields"""
        if isinstance(data, dict):
            sensitive_fields = rule.enrichment_data.get('sensitive_fields', [])
            for field in sensitive_fields:
                if field in data and isinstance(data[field], str):
                    # Simple masking (use proper encryption in production)
                    data[field] = '*' * len(data[field])
        return data
        
    def register_custom_transformer(self, name: str, transformer: Callable):
        """Register a custom transformer function"""
        self.custom_transformers[name] = transformer
        logger.info(f"Registered custom transformer: {name}")
        
    async def get_transformation_metrics(self) -> Dict[str, Any]:
        """Get transformation metrics"""
        return {
            **self.transformation_metrics,
            'active_rules': len([r for r in self.transformation_rules if r.enabled]),
            'total_rules': len(self.transformation_rules),
            'custom_transformers': len(self.custom_transformers)
        }
        
    async def _metrics_update_task(self):
        """Background task for updating transformation metrics"""
        while self.running:
            try:
                metrics = await self.get_transformation_metrics()
                await self.redis.setex(
                    "gateway:transformation:metrics", 
                    60, 
                    json.dumps(metrics, default=str)
                )
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in transformation metrics update task: {e}")
                await asyncio.sleep(60)
                
    async def _rules_watch_task(self):
        """Background task for watching transformation rule changes"""
        while self.running:
            try:
                # Check for rule updates
                rules_version = await self.redis.get("gateway:transformation:version")
                if rules_version:
                    stored_version = getattr(self, '_rules_version', None)
                    if rules_version != stored_version:
                        await self._load_transformation_rules()
                        self._rules_version = rules_version
                        logger.info("Transformation rules updated")
                        
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in transformation rules watch task: {e}")
                await asyncio.sleep(30)
                
    async def health_check(self) -> Dict[str, Any]:
        """Health check for transformation service"""
        try:
            await self.redis.ping()
            redis_status = "healthy"
        except Exception as e:
            redis_status = f"unhealthy: {e}"
            
        success_rate = 0
        if self.transformation_metrics['total_transformations'] > 0:
            success_rate = (
                self.transformation_metrics['successful_transformations'] / 
                self.transformation_metrics['total_transformations'] * 100
            )
            
        return {
            'service': 'gateway_transformation',
            'status': 'healthy' if redis_status == "healthy" and success_rate >= 95 else 'degraded',
            'redis': redis_status,
            'total_transformations': self.transformation_metrics['total_transformations'],
            'success_rate': success_rate,
            'active_rules': len([r for r in self.transformation_rules if r.enabled]),
            'custom_transformers': len(self.custom_transformers)
        }
        
    async def shutdown(self):
        """Shutdown transformation service"""
        self.running = False
        
        if self.redis:
            await self.redis.close()
            
        logger.info("Gateway Transformation service shut down")

# Example usage
async def create_gateway_transformation():
    """Factory function to create gateway transformation service"""
    transformation = GatewayTransformation()
    await transformation.initialize()
    
    return transformation

if __name__ == "__main__":
    async def main():
        transformation = await create_gateway_transformation()
        
        # Example transformation rule
        rule = TransformationRule(
            id="creator_field_mapping",
            name="Creator API Field Mapping",
            endpoint_pattern="/api/v1/creators.*",
            transformation_type=TransformationType.FIELD_MAPPING,
            field_mappings={
                "user_name": "username",
                "user_email": "email",
                "user_profile": "profile.info"
            }
        )
        
        await transformation.add_transformation_rule(rule)
        
        # Example data transformation
        context = TransformationContext(
            request_id="req_123",
            endpoint="/api/v1/creators/456",
            method="GET",
            headers={"Content-Type": "application/json"},
            query_params={}
        )
        
        request_data = {
            "user_name": "john_doe",
            "user_email": "john@example.com",
            "user_profile": {"bio": "Creator"},
            "other_field": "unchanged"
        }
        
        transformed_data = await transformation.transform_request(request_data, context)
        print("Transformed Data:", transformed_data)
        
        # Get metrics
        metrics = await transformation.get_transformation_metrics()
        print("Transformation Metrics:", metrics)
        
        await transformation.shutdown()
        
    asyncio.run(main())