"""Data Transformation Engine - Advanced Data Processing and Mapping
=================================================================

Enterprise data transformation engine for converting and mapping data
between different platform formats and schemas.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Optional, Any, Callable, Union, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal
import dateutil.parser

import jsonschema
import jinja2
import xmltodict
import pandas as pd
from lxml import etree
import yaml


class TransformationType(Enum):
    """Data transformation types."""
    FIELD_MAPPING = "field_mapping"
    DATA_TYPE_CONVERSION = "data_type_conversion"
    VALUE_TRANSFORMATION = "value_transformation"
    CONDITIONAL_TRANSFORMATION = "conditional_transformation"
    AGGREGATION = "aggregation"
    FILTERING = "filtering"
    TEMPLATING = "templating"
    CUSTOM_FUNCTION = "custom_function"


class DataFormat(Enum):
    """Supported data formats."""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    EXCEL = "excel"
    PARQUET = "parquet"
    AVRO = "avro"


@dataclass
class TransformationRule:
    """Data transformation rule configuration."""
    id: str
    name: str
    type: TransformationType
    source_field: Optional[str] = None
    target_field: Optional[str] = None
    source_format: Optional[DataFormat] = None
    target_format: Optional[DataFormat] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None  # Python expression
    template: Optional[str] = None  # Jinja2 template
    custom_function: Optional[Callable] = None
    enabled: bool = True
    priority: int = 0  # Higher priority rules executed first


@dataclass
class TransformationSchema:
    """Data transformation schema definition."""
    id: str
    name: str
    source_schema: Dict[str, Any]
    target_schema: Dict[str, Any]
    transformation_rules: List[TransformationRule]
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    error_handling: str = "strict"  # strict, lenient, skip


@dataclass
class TransformationContext:
    """Transformation execution context."""
    source_data: Any
    target_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class DataTransformationEngine:
    """Advanced data transformation engine."""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Transformation state
        self.schemas: Dict[str, TransformationSchema] = {}
        self.custom_functions: Dict[str, Callable] = {}
        self.format_converters: Dict[DataFormat, Dict[str, Callable]] = {}
        
        # Jinja2 environment for templating
        self.jinja_env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            autoescape=False
        )
        
        # Performance tracking
        self.transformation_metrics = {
            'total_transformations': 0,
            'successful_transformations': 0,
            'failed_transformations': 0,
            'average_processing_time': 0.0
        }
        
        self._setup_built_in_functions()
        self._setup_format_converters()
    
    def _setup_built_in_functions(self) -> None:
        """Setup built-in transformation functions."""
        self.custom_functions.update({
            'to_uppercase': lambda x: str(x).upper() if x is not None else None,
            'to_lowercase': lambda x: str(x).lower() if x is not None else None,
            'to_title_case': lambda x: str(x).title() if x is not None else None,
            'strip_whitespace': lambda x: str(x).strip() if x is not None else None,
            'format_phone': self._format_phone_number,
            'format_email': self._format_email,
            'parse_date': self._parse_date,
            'format_currency': self._format_currency,
            'extract_domain': self._extract_domain,
            'slugify': self._slugify,
            'mask_sensitive': self._mask_sensitive_data,
            'calculate_age': self._calculate_age,
            'generate_uuid': lambda: str(uuid.uuid4()),
            'current_timestamp': lambda: datetime.now().isoformat(),
        })
    
    def _setup_format_converters(self) -> None:
        """Setup format conversion functions."""
        self.format_converters = {
            DataFormat.JSON: {
                'encode': json.dumps,
                'decode': json.loads
            },
            DataFormat.XML: {
                'encode': self._dict_to_xml,
                'decode': self._xml_to_dict
            },
            DataFormat.YAML: {
                'encode': yaml.dump,
                'decode': yaml.safe_load
            },
            DataFormat.CSV: {
                'encode': self._dict_to_csv,
                'decode': self._csv_to_dict
            }
        }
    
    def register_custom_function(self, name -> None: str, function -> None: Callable) -> None:
        """Register custom transformation function."""
        self.custom_functions[name] = function
        self.logger.info(f"Registered custom function: {name}")
    
    def add_transformation_schema(self, schema -> None: TransformationSchema) -> None:
        """Add transformation schema."""
        self.schemas[schema.id] = schema
        self.logger.info(f"Added transformation schema: {schema.name}")
    
    async def transform_data(
        self, 
        schema_id: str, 
        source_data: Any,
        context_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transform data using specified schema."""
        if schema_id not in self.schemas:
            raise ValueError(f"Transformation schema not found: {schema_id}")
        
        schema = self.schemas[schema_id]
        start_time = datetime.now()
        
        try:
            # Create transformation context
            context = TransformationContext(
                source_data=source_data,
                variables=context_variables or {}
            )
            
            # Validate source data
            if schema.source_schema:
                self._validate_data(source_data, schema.source_schema, "source")
            
            # Sort transformation rules by priority
            sorted_rules = sorted(
                [rule for rule in schema.transformation_rules if rule.enabled],
                key=lambda r: r.priority,
                reverse=True
            )
            
            # Apply transformation rules
            for rule in sorted_rules:
                try:
                    await self._apply_transformation_rule(rule, context)
                except Exception as e:
                    error_msg = f"Rule '{rule.name}' failed: {str(e)}"
                    
                    if schema.error_handling == "strict":
                        raise Exception(error_msg)
                    elif schema.error_handling == "lenient":
                        context.errors.append(error_msg)
                        self.logger.warning(error_msg)
                    # skip mode continues without error
            
            # Validate target data
            if schema.target_schema:
                self._validate_data(context.target_data, schema.target_schema, "target")
            
            # Apply validation rules
            if schema.validation_rules:
                self._apply_validation_rules(context.target_data, schema.validation_rules)
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(processing_time, success=True)
            
            return {
                'data': context.target_data,
                'metadata': context.metadata,
                'errors': context.errors,
                'warnings': context.warnings,
                'processing_time': processing_time
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(processing_time, success=False)
            
            self.logger.error(f"Transformation failed for schema {schema_id}: {e}")
            raise
    
    async def _apply_transformation_rule(
        self, 
        rule -> None: TransformationRule, 
        context -> None: TransformationContext
    ) -> None:
        """Apply single transformation rule."""
        # Check condition if specified
        if rule.condition and not self._evaluate_condition(rule.condition, context):
            return
        
        if rule.type == TransformationType.FIELD_MAPPING:
            await self._apply_field_mapping(rule, context)
        elif rule.type == TransformationType.DATA_TYPE_CONVERSION:
            await self._apply_data_type_conversion(rule, context)
        elif rule.type == TransformationType.VALUE_TRANSFORMATION:
            await self._apply_value_transformation(rule, context)
        elif rule.type == TransformationType.CONDITIONAL_TRANSFORMATION:
            await self._apply_conditional_transformation(rule, context)
        elif rule.type == TransformationType.AGGREGATION:
            await self._apply_aggregation(rule, context)
        elif rule.type == TransformationType.FILTERING:
            await self._apply_filtering(rule, context)
        elif rule.type == TransformationType.TEMPLATING:
            await self._apply_templating(rule, context)
        elif rule.type == TransformationType.CUSTOM_FUNCTION:
            await self._apply_custom_function(rule, context)
        else:
            raise ValueError(f"Unknown transformation type: {rule.type}")
    
    async def _apply_field_mapping(
        self, 
        rule -> None: TransformationRule, 
        context -> None: TransformationContext
    ) -> None:
        """Apply field mapping transformation."""
        source_value = self._get_nested_value(context.source_data, rule.source_field)
        
        if source_value is not None:
            self._set_nested_value(context.target_data, rule.target_field, source_value)
    
    async def _apply_data_type_conversion(
        self, 
        rule -> None: TransformationRule, 
        context -> None: TransformationContext
    ) -> None:
        """Apply data type conversion."""
        source_value = self._get_nested_value(context.source_data, rule.source_field)
        target_type = rule.parameters.get('target_type')
        
        if source_value is not None and target_type:
            converted_value = self._convert_data_type(source_value, target_type)
            self._set_nested_value(context.target_data, rule.target_field, converted_value)
    
    async def _apply_value_transformation(
        self, 
        rule -> None: TransformationRule, 
        context -> None: TransformationContext
    ) -> None:
        """Apply value transformation using function."""
        source_value = self._get_nested_value(context.source_data, rule.source_field)
        function_name = rule.parameters.get('function')
        
        if source_value is not None and function_name in self.custom_functions:
            function = self.custom_functions[function_name]
            
            # Pass additional parameters if specified
            if 'function_params' in rule.parameters:
                transformed_value = function(source_value, **rule.parameters['function_params'])
            else:
                transformed_value = function(source_value)
            
            self._set_nested_value(context.target_data, rule.target_field, transformed_value)
    
    async def _apply_conditional_transformation(
        self, 
        rule -> None: TransformationRule, 
        context -> None: TransformationContext
    ) -> None:
        """Apply conditional transformation."""
        condition = rule.parameters.get('condition')
        true_value = rule.parameters.get('true_value')
        false_value = rule.parameters.get('false_value')
        
        if condition and self._evaluate_condition(condition, context):
            value = true_value
        else:
            value = false_value
        
        if value is not None:
            self._set_nested_value(context.target_data, rule.target_field, value)
    
    async def _apply_aggregation(
        self, 
        rule -> None: TransformationRule, 
        context -> None: TransformationContext
    ) -> None:
        """Apply aggregation transformation."""
        source_data = self._get_nested_value(context.source_data, rule.source_field)
        aggregation_type = rule.parameters.get('type')
        
        if isinstance(source_data, list) and aggregation_type:
            if aggregation_type == 'sum':
                result = sum(source_data)
            elif aggregation_type == 'avg':
                result = sum(source_data) / len(source_data)
            elif aggregation_type == 'min':
                result = min(source_data)
            elif aggregation_type == 'max':
                result = max(source_data)
            elif aggregation_type == 'count':
                result = len(source_data)
            elif aggregation_type == 'concat':
                separator = rule.parameters.get('separator', '')
                result = separator.join(str(item) for item in source_data)
            else:
                raise ValueError(f"Unknown aggregation type: {aggregation_type}")
            
            self._set_nested_value(context.target_data, rule.target_field, result)
    
    async def _apply_filtering(
        self, 
        rule -> None: TransformationRule, 
        context -> None: TransformationContext
    ) -> None:
        """Apply filtering transformation."""
        source_data = self._get_nested_value(context.source_data, rule.source_field)
        filter_condition = rule.parameters.get('condition')
        
        if isinstance(source_data, list) and filter_condition:
            filtered_data = []
            for item in source_data:
                temp_context = TransformationContext(source_data=item)
                if self._evaluate_condition(filter_condition, temp_context):
                    filtered_data.append(item)
            
            self._set_nested_value(context.target_data, rule.target_field, filtered_data)
    
    async def _apply_templating(
        self, 
        rule -> None: TransformationRule, 
        context -> None: TransformationContext
    ) -> None:
        """Apply Jinja2 templating transformation."""
        if rule.template:
            template = self.jinja_env.from_string(rule.template)
            
            template_context = {
                'source': context.source_data,
                'target': context.target_data,
                'variables': context.variables,
                'metadata': context.metadata
            }
            
            result = template.render(**template_context)
            self._set_nested_value(context.target_data, rule.target_field, result)
    
    async def _apply_custom_function(
        self, 
        rule -> None: TransformationRule, 
        context -> None: TransformationContext
    ) -> None:
        """Apply custom function transformation."""
        if rule.custom_function:
            result = await rule.custom_function(context, rule.parameters)
            if rule.target_field:
                self._set_nested_value(context.target_data, rule.target_field, result)
    
    def _get_nested_value(self, data: Any, field_path: str) -> Any:
        """Get nested value using dot notation."""
        if not field_path or data is None:
            return data
        
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                current = current[index] if 0 <= index < len(current) else None
            else:
                return None
            
            if current is None:
                return None
        
        return current
    
    def _set_nested_value(self, data -> None: Dict[str, Any], field_path -> None: str, value -> None: Any) -> None:
        """Set nested value using dot notation."""
        if not field_path:
            return
        
        keys = field_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _convert_data_type(self, value: Any, target_type: str) -> Any:
        """Convert value to target data type."""
        if target_type == 'string':
            return str(value)
        elif target_type == 'integer':
            return int(float(value))
        elif target_type == 'float':
            return float(value)
        elif target_type == 'boolean':
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        elif target_type == 'datetime':
            if isinstance(value, str):
                return dateutil.parser.parse(value)
            return value
        elif target_type == 'decimal':
            return Decimal(str(value))
        elif target_type == 'list':
            if isinstance(value, str):
                return json.loads(value)
            return list(value)
        elif target_type == 'dict':
            if isinstance(value, str):
                return json.loads(value)
            return dict(value)
        else:
            raise ValueError(f"Unknown target type: {target_type}")
    
    def _evaluate_condition(self, condition: str, context: TransformationContext) -> bool:
        """Evaluate condition expression."""
        try:
            evaluation_context = {
                'source': context.source_data,
                'target': context.target_data,
                'variables': context.variables,
                'metadata': context.metadata
            }
            
            return bool(eval(condition, {"__builtins__": {}}, evaluation_context))
        except Exception as e:
            self.logger.warning(f"Condition evaluation failed: {e}")
            return False
    
    def _validate_data(self, data -> None: Any, schema -> None: Dict[str, Any], data_type -> None: str) -> None:
        """Validate data against JSON schema."""
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"{data_type} data validation failed: {e.message}")
    
    def _apply_validation_rules(self, data -> None: Dict[str, Any], rules -> None: Dict[str, Any]) -> None:
        """Apply custom validation rules."""
        for rule_name, rule_config in rules.items():
            field = rule_config.get('field')
            rule_type = rule_config.get('type')
            
            value = self._get_nested_value(data, field)
            
            if rule_type == 'required' and value is None:
                raise ValueError(f"Required field missing: {field}")
            elif rule_type == 'min_length' and isinstance(value, str):
                min_length = rule_config.get('value', 0)
                if len(value) < min_length:
                    raise ValueError(f"Field {field} too short (min: {min_length})")
            elif rule_type == 'max_length' and isinstance(value, str):
                max_length = rule_config.get('value', 0)
                if len(value) > max_length:
                    raise ValueError(f"Field {field} too long (max: {max_length})")
            elif rule_type == 'regex' and isinstance(value, str):
                pattern = rule_config.get('value')
                if not re.match(pattern, value):
                    raise ValueError(f"Field {field} does not match pattern: {pattern}")
    
    def _update_metrics(self, processing_time -> None: float, success -> None: bool) -> None:
        """Update transformation metrics."""
        self.transformation_metrics['total_transformations'] += 1
        
        if success:
            self.transformation_metrics['successful_transformations'] += 1
        else:
            self.transformation_metrics['failed_transformations'] += 1
        
        # Update average processing time
        total = self.transformation_metrics['total_transformations']
        current_avg = self.transformation_metrics['average_processing_time']
        self.transformation_metrics['average_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    # Built-in transformation functions
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number."""
        if not phone:
            return phone
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Format as (XXX) XXX-XXXX for US numbers
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return phone  # Return original if can't format
    
    def _format_email(self, email: str) -> str:
        """Format email address."""
        if not email:
            return email
        
        return email.lower().strip()
    
    def _parse_date(self, date_str: str, format_str: Optional[str] = None) -> str:
        """Parse date string to ISO format."""
        if not date_str:
            return date_str
        
        if format_str:
            parsed_date = datetime.strptime(date_str, format_str)
        else:
            parsed_date = dateutil.parser.parse(date_str)
        
        return parsed_date.isoformat()
    
    def _format_currency(self, amount: Union[int, float, str], currency: str = 'USD') -> str:
        """Format currency amount."""
        try:
            amount_float = float(amount)
            return f"{amount_float:.2f} {currency}"
        except (ValueError, TypeError):
            return str(amount)
    
    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address."""
        if not email or '@' not in email:
            return ''
        
        return email.split('@')[1]
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        if not text:
            return ''
        
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def _mask_sensitive_data(self, data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
        """Mask sensitive data keeping only last few characters visible."""
        if not data or len(data) <= visible_chars:
            return data
        
        masked_length = len(data) - visible_chars
        return mask_char * masked_length + data[-visible_chars:]
    
    def _calculate_age(self, birth_date: str, reference_date: Optional[str] = None) -> int:
        """Calculate age from birth date."""
        birth = dateutil.parser.parse(birth_date)
        reference = dateutil.parser.parse(reference_date) if reference_date else datetime.now()
        
        age = reference.year - birth.year
        if reference.month < birth.month or (reference.month == birth.month and reference.day < birth.day):
            age -= 1
        
        return age
    
    # Format conversion helpers
    def _dict_to_xml(self, data: Dict[str, Any], root_tag: str = 'root') -> str:
        """Convert dictionary to XML string."""
        def dict_to_xml_recursive(tag, d) -> None:
            elem = etree.Element(tag)
            for key, val in d.items():
                if isinstance(val, dict):
                    elem.append(dict_to_xml_recursive(key, val))
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict):
                            elem.append(dict_to_xml_recursive(key, item))
                        else:
                            child = etree.SubElement(elem, key)
                            child.text = str(item)
                else:
                    child = etree.SubElement(elem, key)
                    child.text = str(val)
            return elem
        
        root = dict_to_xml_recursive(root_tag, data)
        return etree.tostring(root, encoding='unicode', pretty_print=True)
    
    def _xml_to_dict(self, xml_str: str) -> Dict[str, Any]:
        """Convert XML string to dictionary."""
        return xmltodict.parse(xml_str)
    
    def _dict_to_csv(self, data: List[Dict[str, Any]]) -> str:
        """Convert list of dictionaries to CSV string."""
        if not data:
            return ''
        
        df = pd.DataFrame(data)
        return df.to_csv(index=False)
    
    def _csv_to_dict(self, csv_str: str) -> List[Dict[str, Any]]:
        """Convert CSV string to list of dictionaries."""
        from io import StringIO
        df = pd.read_csv(StringIO(csv_str))
        return df.to_dict('records')
    
    def get_transformation_metrics(self) -> Dict[str, Any]:
        """Get transformation metrics."""
        return self.transformation_metrics.copy()
    
    def export_schema(self, schema_id: str) -> Dict[str, Any]:
        """Export transformation schema to dictionary."""
        if schema_id not in self.schemas:
            raise ValueError(f"Schema not found: {schema_id}")
        
        schema = self.schemas[schema_id]
        return {
            'id': schema.id,
            'name': schema.name,
            'source_schema': schema.source_schema,
            'target_schema': schema.target_schema,
            'transformation_rules': [
                {
                    'id': rule.id,
                    'name': rule.name,
                    'type': rule.type.value,
                    'source_field': rule.source_field,
                    'target_field': rule.target_field,
                    'parameters': rule.parameters,
                    'condition': rule.condition,
                    'template': rule.template,
                    'enabled': rule.enabled,
                    'priority': rule.priority
                }
                for rule in schema.transformation_rules
            ],
            'validation_rules': schema.validation_rules,
            'error_handling': schema.error_handling
        }
    
    def import_schema(self, schema_data -> None: Dict[str, Any]) -> None:
        """Import transformation schema from dictionary."""
        transformation_rules = []
        for rule_data in schema_data.get('transformation_rules', []):
            rule = TransformationRule(
                id=rule_data['id'],
                name=rule_data['name'],
                type=TransformationType(rule_data['type']),
                source_field=rule_data.get('source_field'),
                target_field=rule_data.get('target_field'),
                parameters=rule_data.get('parameters', {}),
                condition=rule_data.get('condition'),
                template=rule_data.get('template'),
                enabled=rule_data.get('enabled', True),
                priority=rule_data.get('priority', 0)
            )
            transformation_rules.append(rule)
        
        schema = TransformationSchema(
            id=schema_data['id'],
            name=schema_data['name'],
            source_schema=schema_data.get('source_schema', {}),
            target_schema=schema_data.get('target_schema', {}),
            transformation_rules=transformation_rules,
            validation_rules=schema_data.get('validation_rules', {}),
            error_handling=schema_data.get('error_handling', 'strict')
        )
        
        self.add_transformation_schema(schema)


# Example usage
if __name__ == "__main__":
    async def main() -> None:
        # Initialize transformation engine
        engine = DataTransformationEngine()
        
        # Create transformation rules
        rules = [
            TransformationRule(
                id="map_user_name",
                name="Map user name",
                type=TransformationType.FIELD_MAPPING,
                source_field="full_name",
                target_field="name"
            ),
            TransformationRule(
                id="format_email",
                name="Format email",
                type=TransformationType.VALUE_TRANSFORMATION,
                source_field="email",
                target_field="email_address",
                parameters={'function': 'format_email'}
            ),
            TransformationRule(
                id="calculate_user_age",
                name="Calculate age",
                type=TransformationType.VALUE_TRANSFORMATION,
                source_field="birth_date",
                target_field="age",
                parameters={'function': 'calculate_age'}
            )
        ]
        
        # Create transformation schema
        schema = TransformationSchema(
            id="user_profile_transform",
            name="User Profile Transformation",
            source_schema={},
            target_schema={},
            transformation_rules=rules
        )
        
        engine.add_transformation_schema(schema)
        
        # Transform data
        source_data = {
            "full_name": "John Doe",
            "email": "JOHN.DOE@EXAMPLE.COM",
            "birth_date": "1990-01-15"
        }
        
        result = await engine.transform_data("user_profile_transform", source_data)
        print("Transformation result:", json.dumps(result, indent=2))
    
    asyncio.run(main())