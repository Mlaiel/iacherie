"""Data Transformation Utilities
Enterprise-grade data transformation and mapping for Ainflue Platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import copy
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime, date
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TransformationRule:
    """Represents a data transformation rule"""
    source_field: str
    target_field: str
    transform_func: Callable
    condition: Optional[Callable] = None
    default_value: Any = None


class DataTransformer:
    """
    Enterprise-grade data transformation system with mapping rules,
    type conversion, and complex data restructuring capabilities.
    """
    
    def __init__(self):
        self.transformation_rules: List[TransformationRule] = []
        self.type_converters: Dict[str, Callable] = {}
        self.custom_transforms: Dict[str, Callable] = {}
        
        # Register built-in type converters
        self._register_builtin_converters()
        
        # Register built-in transforms
        self._register_builtin_transforms()
        
        logger.info("DataTransformer initialized with built-in converters and transforms")
    
    def _register_builtin_converters(self):
        """Register built-in type conversion functions"""
        self.type_converters.update({
            "string": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "datetime": self._to_datetime,
            "date": self._to_date,
            "json": self._to_json,
            "lowercase": lambda x: str(x).lower(),
            "uppercase": lambda x: str(x).upper(),
            "strip": lambda x: str(x).strip(),
            "title": lambda x: str(x).title(),
        })
    
    def _register_builtin_transforms(self):
        """Register built-in transformation functions"""
        self.custom_transforms.update({
            "split": self._transform_split,
            "join": self._transform_join,
            "replace": self._transform_replace,
            "extract": self._transform_extract,
            "flatten": self._transform_flatten,
            "nest": self._transform_nest,
            "filter": self._transform_filter,
            "map": self._transform_map,
            "format": self._transform_format,
            "calculate": self._transform_calculate,
            "lookup": self._transform_lookup,
            "aggregate": self._transform_aggregate,
        })
    
    def add_transformation_rule(self, source_field: str, target_field: str, 
                              transform_func: Union[str, Callable], 
                              condition: Optional[Callable] = None,
                              default_value: Any = None):
        """Add a transformation rule"""
        if isinstance(transform_func, str):
            if transform_func in self.type_converters:
                transform_func = self.type_converters[transform_func]
            elif transform_func in self.custom_transforms:
                transform_func = self.custom_transforms[transform_func]
            else:
                raise ValueError(f"Unknown transformation function: {transform_func}")
        
        rule = TransformationRule(
            source_field=source_field,
            target_field=target_field,
            transform_func=transform_func,
            condition=condition,
            default_value=default_value
        )
        
        self.transformation_rules.append(rule)
        logger.info(f"Added transformation rule: {source_field} -> {target_field}")
    
    def register_converter(self, name: str, converter_func: Callable):
        """Register custom type converter"""
        self.type_converters[name] = converter_func
        logger.info(f"Registered type converter: {name}")
    
    def register_transform(self, name: str, transform_func: Callable):
        """Register custom transformation function"""
        self.custom_transforms[name] = transform_func
        logger.info(f"Registered transform function: {name}")
    
    def transform(self, data: Dict[str, Any], rules: Optional[List[TransformationRule]] = None) -> Dict[str, Any]:
        """
        Transform data using registered rules
        
        Args:
            data: Source data to transform
            rules: Optional specific rules to use (defaults to all registered rules)
            
        Returns:
            Transformed data dictionary
        """
        if rules is None:
            rules = self.transformation_rules
        
        transformed_data = {}
        
        for rule in rules:
            try:
                # Check condition if specified
                if rule.condition and not rule.condition(data):
                    continue
                
                # Get source value
                source_value = self._get_nested_value(data, rule.source_field)
                
                if source_value is None and rule.default_value is not None:
                    source_value = rule.default_value
                
                # Apply transformation
                if source_value is not None:
                    transformed_value = rule.transform_func(source_value)
                    self._set_nested_value(transformed_data, rule.target_field, transformed_value)
                
            except Exception as e:
                logger.error(f"Transformation error for rule {rule.source_field} -> {rule.target_field}: {e}")
                continue
        
        return transformed_data
    
    def transform_simple(self, data: Dict[str, Any], mapping: Dict[str, Union[str, Dict]]) -> Dict[str, Any]:
        """
        Simple transformation using field mapping
        
        Args:
            data: Source data
            mapping: Field mapping dictionary
                     - string values: direct field mapping
                     - dict values: transformation with options
        
        Returns:
            Transformed data
        """
        transformed_data = {}
        
        for source_field, target_config in mapping.items():
            try:
                source_value = self._get_nested_value(data, source_field)
                
                if isinstance(target_config, str):
                    # Simple field rename
                    self._set_nested_value(transformed_data, target_config, source_value)
                
                elif isinstance(target_config, dict):
                    # Complex transformation
                    target_field = target_config.get("field", source_field)
                    transform_type = target_config.get("transform", "string")
                    default_value = target_config.get("default")
                    
                    if source_value is None and default_value is not None:
                        source_value = default_value
                    
                    if source_value is not None:
                        if transform_type in self.type_converters:
                            transformed_value = self.type_converters[transform_type](source_value)
                        elif transform_type in self.custom_transforms:
                            transform_args = target_config.get("args", {})
                            transformed_value = self.custom_transforms[transform_type](source_value, **transform_args)
                        else:
                            transformed_value = source_value
                        
                        self._set_nested_value(transformed_data, target_field, transformed_value)
                
            except Exception as e:
                logger.error(f"Simple transformation error for field {source_field}: {e}")
                continue
        
        return transformed_data
    
    def batch_transform(self, data_list: List[Dict[str, Any]], 
                       mapping: Dict[str, Union[str, Dict]]) -> List[Dict[str, Any]]:
        """Transform a list of data objects"""
        return [self.transform_simple(data, mapping) for data in data_list]
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        if '.' not in field_path:
            return data.get(field_path)
        
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _set_nested_value(self, data: Dict[str, Any], field_path: str, value: Any):
        """Set value in nested dictionary using dot notation"""
        if '.' not in field_path:
            data[field_path] = value
            return
        
        keys = field_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    # Built-in type converters
    
    def _to_datetime(self, value: Any) -> Optional[datetime]:
        """Convert value to datetime"""
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            # Try common datetime formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            
            # Try parsing timestamp
            try:
                return datetime.fromtimestamp(float(value))
            except (ValueError, TypeError):
                pass
        
        return None
    
    def _to_date(self, value: Any) -> Optional[date]:
        """Convert value to date"""
        dt = self._to_datetime(value)
        return dt.date() if dt else None
    
    def _to_json(self, value: Any) -> Optional[str]:
        """Convert value to JSON string"""
        try:
            return json.dumps(value)
        except (TypeError, ValueError):
            return None
    
    # Built-in transformation functions
    
    def _transform_split(self, value: Any, delimiter: str = ",", max_split: int = -1) -> List[str]:
        """Split string into list"""
        return str(value).split(delimiter, max_split)
    
    def _transform_join(self, value: Any, delimiter: str = ",") -> str:
        """Join list into string"""
        if isinstance(value, list):
            return delimiter.join(str(item) for item in value)
        return str(value)
    
    def _transform_replace(self, value: Any, old: str, new: str) -> str:
        """Replace substring in string"""
        return str(value).replace(old, new)
    
    def _transform_extract(self, value: Any, pattern: str, group: int = 0) -> Optional[str]:
        """Extract substring using regex"""
        import re
        match = re.search(pattern, str(value))
        return match.group(group) if match else None
    
    def _transform_flatten(self, value: Any) -> Dict[str, Any]:
        """Flatten nested dictionary"""
        def _flatten_dict(d, parent_key='', sep='.'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(_flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        if isinstance(value, dict):
            return _flatten_dict(value)
        return value
    
    def _transform_nest(self, value: Any, structure: Dict[str, str]) -> Dict[str, Any]:
        """Nest flat dictionary according to structure"""
        if not isinstance(value, dict):
            return value
        
        nested = {}
        for flat_key, nested_path in structure.items():
            if flat_key in value:
                self._set_nested_value(nested, nested_path, value[flat_key])
        
        return nested
    
    def _transform_filter(self, value: Any, condition: Callable) -> Any:
        """Filter items based on condition"""
        if isinstance(value, list):
            return [item for item in value if condition(item)]
        elif isinstance(value, dict):
            return {k: v for k, v in value.items() if condition(v)}
        return value
    
    def _transform_map(self, value: Any, map_func: Callable) -> Any:
        """Map function to items"""
        if isinstance(value, list):
            return [map_func(item) for item in value]
        elif isinstance(value, dict):
            return {k: map_func(v) for k, v in value.items()}
        return map_func(value)
    
    def _transform_format(self, value: Any, template: str) -> str:
        """Format value using template string"""
        if isinstance(value, dict):
            return template.format(**value)
        else:
            return template.format(value)
    
    def _transform_calculate(self, value: Any, expression: str, variables: Dict[str, Any] = None) -> Any:
        """Calculate value using expression"""
        try:
            # Basic calculator with limited eval for safety
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "len": len, "sum": sum, "int": int, "float": float,
                "str": str, "bool": bool
            }
            
            if variables:
                allowed_names.update(variables)
            
            if isinstance(value, (int, float)):
                allowed_names["value"] = value
            
            # Simple expression evaluation (be careful with eval)
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return result
            
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return value
    
    def _transform_lookup(self, value: Any, lookup_table: Dict[Any, Any], default: Any = None) -> Any:
        """Lookup value in table"""
        return lookup_table.get(value, default)
    
    def _transform_aggregate(self, value: Any, operation: str) -> Any:
        """Aggregate list of values"""
        if not isinstance(value, list):
            return value
        
        if operation == "sum":
            return sum(value)
        elif operation == "avg":
            return sum(value) / len(value) if value else 0
        elif operation == "min":
            return min(value) if value else None
        elif operation == "max":
            return max(value) if value else None
        elif operation == "count":
            return len(value)
        else:
            return value


# Utility functions for common transformations

def normalize_phone_number(phone: str) -> str:
    """Normalize phone number format"""
    import re
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    return cleaned


def normalize_email(email: str) -> str:
    """Normalize email address"""
    return email.lower().strip()


def parse_name(full_name: str) -> Dict[str, str]:
    """Parse full name into components"""
    parts = full_name.strip().split()
    
    if len(parts) == 1:
        return {"first_name": parts[0], "last_name": ""}
    elif len(parts) == 2:
        return {"first_name": parts[0], "last_name": parts[1]}
    else:
        return {
            "first_name": parts[0],
            "middle_name": " ".join(parts[1:-1]),
            "last_name": parts[-1]
        }


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


# Global transformer instance
_global_transformer: Optional[DataTransformer] = None


def get_global_transformer() -> DataTransformer:
    """Get global data transformer instance"""
    global _global_transformer
    if _global_transformer is None:
        _global_transformer = DataTransformer()
    return _global_transformer


def transform_data(data: Dict[str, Any], mapping: Dict[str, Union[str, Dict]]) -> Dict[str, Any]:
    """Quick transformation using global transformer"""
    return get_global_transformer().transform_simple(data, mapping)