"""
Data Transformer Utilities - Enterprise Grade
============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Expert Roles: Lead Dev IA + Backend Senior + ML Engineer
Provides comprehensive data transformation for enterprise applications.
"""

import json
import csv
import xml.etree.ElementTree as ET
import logging
import re
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from datetime import datetime, date, timezone
from decimal import Decimal
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from pydantic import BaseModel
import asyncio
from concurrent.futures import ThreadPoolExecutor


@dataclass
class TransformationResult:
    """Result container for data transformations."""
    success: bool
    data: Any
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'data': self.data,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


class DataTransformer:
    """
    Enterprise-grade data transformation utility.
    
    Features:
    - Format conversions (JSON, XML, CSV, Parquet)
    - Data type transformations
    - Data normalization and standardization
    - Batch processing capabilities
    - Schema mapping and field transformation
    - Performance optimization with async processing
    - Memory-efficient streaming for large datasets
    """
    
    def __init__(self, max_workers: int = 4, chunk_size: int = 10000):
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Transformation registry
        self.transformers = {
            'string': self._transform_string,
            'number': self._transform_number,
            'boolean': self._transform_boolean,
            'date': self._transform_date,
            'email': self._transform_email,
            'phone': self._transform_phone,
            'url': self._transform_url,
            'json': self._transform_json,
            'array': self._transform_array,
            'object': self._transform_object
        }
    
    def transform_format(self, data: Any, from_format: str, to_format: str, 
                        config: Dict[str, Any] = None) -> TransformationResult:
        """Transform data between different formats."""
        config = config or {}
        
        try:
            # Parse input format
            if from_format == 'json' and isinstance(data, str):
                parsed_data = json.loads(data)
            elif from_format == 'csv' and isinstance(data, str):
                parsed_data = self._parse_csv(data, config)
            elif from_format == 'xml' and isinstance(data, str):
                parsed_data = self._parse_xml(data, config)
            else:
                parsed_data = data
            
            # Transform to output format
            if to_format == 'json':
                result_data = self._to_json(parsed_data, config)
            elif to_format == 'csv':
                result_data = self._to_csv(parsed_data, config)
            elif to_format == 'xml':
                result_data = self._to_xml(parsed_data, config)
            elif to_format == 'parquet':
                result_data = self._to_parquet(parsed_data, config)
            else:
                result_data = parsed_data
            
            return TransformationResult(
                success=True,
                data=result_data,
                errors=[],
                warnings=[],
                metadata={'from_format': from_format, 'to_format': to_format},
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.error(f"Format transformation failed: {str(e)}")
            return TransformationResult(
                success=False,
                data=None,
                errors=[str(e)],
                warnings=[],
                metadata={'from_format': from_format, 'to_format': to_format},
                timestamp=datetime.now(timezone.utc)
            )
    
    def transform_schema(self, data: Dict[str, Any], schema_map: Dict[str, Dict[str, Any]]) -> TransformationResult:
        """Transform data using schema mapping."""
        try:
            transformed_data = {}
            errors = []
            warnings = []
            
            for source_field, mapping in schema_map.items():
                if source_field not in data:
                    if mapping.get('required', False):
                        errors.append(f"Required field missing: {source_field}")
                    continue
                
                source_value = data[source_field]
                target_field = mapping.get('target_field', source_field)
                transform_type = mapping.get('type', 'string')
                default_value = mapping.get('default')
                
                # Apply transformation
                if transform_type in self.transformers:
                    try:
                        transformed_value = self.transformers[transform_type](
                            source_value, mapping.get('options', {})
                        )
                        transformed_data[target_field] = transformed_value
                    except Exception as e:
                        if default_value is not None:
                            transformed_data[target_field] = default_value
                            warnings.append(f"Used default for {source_field}: {str(e)}")
                        else:
                            errors.append(f"Transformation failed for {source_field}: {str(e)}")
                else:
                    warnings.append(f"Unknown transformation type: {transform_type}")
                    transformed_data[target_field] = source_value
            
            return TransformationResult(
                success=len(errors) == 0,
                data=transformed_data,
                errors=errors,
                warnings=warnings,
                metadata={'schema_fields': len(schema_map)},
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.error(f"Schema transformation failed: {str(e)}")
            return TransformationResult(
                success=False,
                data=None,
                errors=[str(e)],
                warnings=[],
                metadata={},
                timestamp=datetime.now(timezone.utc)
            )
    
    def normalize_data(self, data: List[Dict[str, Any]], 
                      normalization_rules: Dict[str, Any]) -> TransformationResult:
        """Normalize data using specified rules."""
        try:
            normalized_data = []
            
            for item in data:
                normalized_item = {}
                
                for field, value in item.items():
                    if field in normalization_rules:
                        rule = normalization_rules[field]
                        
                        if rule['type'] == 'lowercase':
                            normalized_item[field] = str(value).lower()
                        elif rule['type'] == 'uppercase':
                            normalized_item[field] = str(value).upper()
                        elif rule['type'] == 'trim':
                            normalized_item[field] = str(value).strip()
                        elif rule['type'] == 'remove_special':
                            normalized_item[field] = re.sub(r'[^a-zA-Z0-9\s]', '', str(value))
                        elif rule['type'] == 'standardize_phone':
                            normalized_item[field] = self._standardize_phone(str(value))
                        elif rule['type'] == 'standardize_email':
                            normalized_item[field] = str(value).lower().strip()
                        elif rule['type'] == 'numeric':
                            try:
                                normalized_item[field] = float(value)
                            except (ValueError, TypeError):
                                normalized_item[field] = 0.0
                        else:
                            normalized_item[field] = value
                    else:
                        normalized_item[field] = value
                
                normalized_data.append(normalized_item)
            
            return TransformationResult(
                success=True,
                data=normalized_data,
                errors=[],
                warnings=[],
                metadata={'items_processed': len(data)},
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.error(f"Data normalization failed: {str(e)}")
            return TransformationResult(
                success=False,
                data=None,
                errors=[str(e)],
                warnings=[],
                metadata={},
                timestamp=datetime.now(timezone.utc)
            )
    
    async def transform_batch_async(self, data_batch: List[Any], 
                                   transformation_func: Callable,
                                   **kwargs) -> List[TransformationResult]:
        """Transform data batch asynchronously."""
        async def transform_item(item):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.executor, transformation_func, item, **kwargs
            )
        
        tasks = [transform_item(item) for item in data_batch]
        return await asyncio.gather(*tasks)
    
    def transform_dataframe(self, df: pd.DataFrame, 
                           transformations: Dict[str, Dict[str, Any]]) -> TransformationResult:
        """Transform pandas DataFrame using specified transformations."""
        try:
            df_transformed = df.copy()
            
            for column, config in transformations.items():
                if column not in df_transformed.columns:
                    continue
                
                transform_type = config.get('type')
                
                if transform_type == 'normalize':
                    # Min-max normalization
                    min_val = df_transformed[column].min()
                    max_val = df_transformed[column].max()
                    df_transformed[column] = (df_transformed[column] - min_val) / (max_val - min_val)
                
                elif transform_type == 'standardize':
                    # Z-score standardization
                    mean_val = df_transformed[column].mean()
                    std_val = df_transformed[column].std()
                    df_transformed[column] = (df_transformed[column] - mean_val) / std_val
                
                elif transform_type == 'categorical':
                    # Convert to categorical
                    df_transformed[column] = pd.Categorical(df_transformed[column])
                
                elif transform_type == 'datetime':
                    # Convert to datetime
                    df_transformed[column] = pd.to_datetime(df_transformed[column])
                
                elif transform_type == 'one_hot':
                    # One-hot encoding
                    dummies = pd.get_dummies(df_transformed[column], prefix=column)
                    df_transformed = pd.concat([df_transformed.drop(column, axis=1), dummies], axis=1)
                
                elif transform_type == 'log':
                    # Log transformation
                    df_transformed[column] = np.log1p(df_transformed[column])
                
                elif transform_type == 'sqrt':
                    # Square root transformation
                    df_transformed[column] = np.sqrt(df_transformed[column])
            
            return TransformationResult(
                success=True,
                data=df_transformed,
                errors=[],
                warnings=[],
                metadata={'shape': df_transformed.shape},
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.error(f"DataFrame transformation failed: {str(e)}")
            return TransformationResult(
                success=False,
                data=None,
                errors=[str(e)],
                warnings=[],
                metadata={},
                timestamp=datetime.now(timezone.utc)
            )
    
    def aggregate_data(self, data: List[Dict[str, Any]], 
                      group_by: List[str], 
                      aggregations: Dict[str, str]) -> TransformationResult:
        """Aggregate data by specified fields."""
        try:
            df = pd.DataFrame(data)
            
            # Group by specified fields
            grouped = df.groupby(group_by)
            
            # Apply aggregations
            agg_result = {}
            for field, agg_type in aggregations.items():
                if field in df.columns:
                    if agg_type == 'sum':
                        agg_result[field] = grouped[field].sum()
                    elif agg_type == 'mean':
                        agg_result[field] = grouped[field].mean()
                    elif agg_type == 'count':
                        agg_result[field] = grouped[field].count()
                    elif agg_type == 'min':
                        agg_result[field] = grouped[field].min()
                    elif agg_type == 'max':
                        agg_result[field] = grouped[field].max()
                    elif agg_type == 'std':
                        agg_result[field] = grouped[field].std()
            
            result_df = pd.DataFrame(agg_result).reset_index()
            
            return TransformationResult(
                success=True,
                data=result_df.to_dict('records'),
                errors=[],
                warnings=[],
                metadata={'groups': len(result_df)},
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.error(f"Data aggregation failed: {str(e)}")
            return TransformationResult(
                success=False,
                data=None,
                errors=[str(e)],
                warnings=[],
                metadata={},
                timestamp=datetime.now(timezone.utc)
            )
    
    def pivot_data(self, data: List[Dict[str, Any]], 
                   index: str, columns: str, values: str) -> TransformationResult:
        """Pivot data table."""
        try:
            df = pd.DataFrame(data)
            pivot_df = df.pivot_table(
                index=index, 
                columns=columns, 
                values=values, 
                aggfunc='first'
            ).reset_index()
            
            return TransformationResult(
                success=True,
                data=pivot_df.to_dict('records'),
                errors=[],
                warnings=[],
                metadata={'shape': pivot_df.shape},
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.error(f"Data pivot failed: {str(e)}")
            return TransformationResult(
                success=False,
                data=None,
                errors=[str(e)],
                warnings=[],
                metadata={},
                timestamp=datetime.now(timezone.utc)
            )
    
    # Private transformation methods
    def _transform_string(self, value: Any, options: Dict[str, Any]) -> str:
        """Transform value to string."""
        str_value = str(value)
        
        if options.get('trim'):
            str_value = str_value.strip()
        
        if options.get('lowercase'):
            str_value = str_value.lower()
        
        if options.get('uppercase'):
            str_value = str_value.upper()
        
        if options.get('max_length'):
            str_value = str_value[:options['max_length']]
        
        return str_value
    
    def _transform_number(self, value: Any, options: Dict[str, Any]) -> Union[int, float]:
        """Transform value to number."""
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        
        if options.get('type') == 'int':
            return int(float(value))
        else:
            result = float(value)
            
            if options.get('round_to'):
                result = round(result, options['round_to'])
            
            return result
    
    def _transform_boolean(self, value: Any, options: Dict[str, Any]) -> bool:
        """Transform value to boolean."""
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ['true', 'yes', '1', 'on', 'enabled']
        
        if isinstance(value, (int, float)):
            return value != 0
        
        return bool(value)
    
    def _transform_date(self, value: Any, options: Dict[str, Any]) -> datetime:
        """Transform value to datetime."""
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, str):
            date_format = options.get('format', '%Y-%m-%d')
            return datetime.strptime(value, date_format)
        
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        
        raise ValueError(f"Cannot convert {type(value)} to datetime")
    
    def _transform_email(self, value: Any, options: Dict[str, Any]) -> str:
        """Transform and normalize email."""
        email = str(value).lower().strip()
        
        if options.get('validate'):
            # Basic email validation
            if '@' not in email or '.' not in email.split('@')[1]:
                raise ValueError("Invalid email format")
        
        return email
    
    def _transform_phone(self, value: Any, options: Dict[str, Any]) -> str:
        """Transform and normalize phone number."""
        phone = re.sub(r'[^\d+]', '', str(value))
        
        if options.get('country_code') and not phone.startswith('+'):
            phone = f"+{options['country_code']}{phone}"
        
        return phone
    
    def _transform_url(self, value: Any, options: Dict[str, Any]) -> str:
        """Transform and normalize URL."""
        url = str(value).strip()
        
        if not url.startswith(('http://', 'https://')):
            protocol = options.get('default_protocol', 'https')
            url = f"{protocol}://{url}"
        
        return url.lower()
    
    def _transform_json(self, value: Any, options: Dict[str, Any]) -> Any:
        """Transform JSON string to object."""
        if isinstance(value, str):
            return json.loads(value)
        return value
    
    def _transform_array(self, value: Any, options: Dict[str, Any]) -> List[Any]:
        """Transform value to array."""
        if isinstance(value, list):
            return value
        
        if isinstance(value, str):
            delimiter = options.get('delimiter', ',')
            return [item.strip() for item in value.split(delimiter)]
        
        return [value]
    
    def _transform_object(self, value: Any, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transform value to object."""
        if isinstance(value, dict):
            return value
        
        if isinstance(value, str):
            return json.loads(value)
        
        return {'value': value}
    
    def _parse_csv(self, csv_data: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse CSV data."""
        delimiter = config.get('delimiter', ',')
        has_header = config.get('has_header', True)
        
        lines = csv_data.strip().split('\n')
        
        if has_header:
            headers = [h.strip() for h in lines[0].split(delimiter)]
            data_lines = lines[1:]
        else:
            headers = [f'col_{i}' for i in range(len(lines[0].split(delimiter)))]
            data_lines = lines
        
        result = []
        for line in data_lines:
            values = [v.strip() for v in line.split(delimiter)]
            row = dict(zip(headers, values))
            result.append(row)
        
        return result
    
    def _parse_xml(self, xml_data: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse XML data."""
        root = ET.fromstring(xml_data)
        return self._xml_to_dict(root)
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}
        
        # Add attributes
        if element.attrib:
            result.update(element.attrib)
        
        # Add child elements
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        # Add text content
        if element.text and element.text.strip():
            if result:
                result['_text'] = element.text.strip()
            else:
                return element.text.strip()
        
        return result
    
    def _to_json(self, data: Any, config: Dict[str, Any]) -> str:
        """Convert data to JSON."""
        indent = config.get('indent', 2)
        ensure_ascii = config.get('ensure_ascii', False)
        
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, default=str)
    
    def _to_csv(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
        """Convert data to CSV."""
        if not data:
            return ""
        
        delimiter = config.get('delimiter', ',')
        include_header = config.get('include_header', True)
        
        headers = list(data[0].keys())
        lines = []
        
        if include_header:
            lines.append(delimiter.join(headers))
        
        for item in data:
            values = [str(item.get(header, '')) for header in headers]
            lines.append(delimiter.join(values))
        
        return '\n'.join(lines)
    
    def _to_xml(self, data: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Convert data to XML."""
        root_name = config.get('root_name', 'root')
        root = ET.Element(root_name)
        self._dict_to_xml(data, root)
        return ET.tostring(root, encoding='unicode')
    
    def _dict_to_xml(self, data: Any, parent: ET.Element):
        """Convert dictionary to XML element."""
        if isinstance(data, dict):
            for key, value in data.items():
                if key.startswith('_'):
                    continue
                
                child = ET.SubElement(parent, key)
                self._dict_to_xml(value, child)
        elif isinstance(data, list):
            for item in data:
                child = ET.SubElement(parent, 'item')
                self._dict_to_xml(item, child)
        else:
            parent.text = str(data)
    
    def _to_parquet(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> bytes:
        """Convert data to Parquet format."""
        df = pd.DataFrame(data)
        return df.to_parquet(engine='pyarrow')
    
    def _standardize_phone(self, phone: str) -> str:
        """Standardize phone number format."""
        # Remove all non-digit characters except +
        digits = re.sub(r'[^\d+]', '', phone)
        
        # Add country code if missing
        if not digits.startswith('+'):
            digits = '+1' + digits
        
        return digits


# Convenience functions
def transform_json_to_csv(json_data: str) -> str:
    """Quick JSON to CSV transformation."""
    transformer = DataTransformer()
    result = transformer.transform_format(json_data, 'json', 'csv')
    return result.data if result.success else ""


def normalize_email_list(emails: List[str]) -> List[str]:
    """Normalize list of email addresses."""
    transformer = DataTransformer()
    normalized = []
    
    for email in emails:
        try:
            normalized.append(transformer._transform_email(email, {'validate': True}))
        except ValueError:
            continue
    
    return normalized


def standardize_phone_numbers(phones: List[str]) -> List[str]:
    """Standardize list of phone numbers."""
    transformer = DataTransformer()
    return [transformer._standardize_phone(phone) for phone in phones]


# Example usage
if __name__ == "__main__":
    transformer = DataTransformer()
    
    # Test format transformation
    json_data = '{"name": "John", "age": 30, "email": "john@example.com"}'
    result = transformer.transform_format(json_data, 'json', 'csv')
    print(f"JSON to CSV: {result.to_dict()}")
    
    # Test schema transformation
    data = {"first_name": "john", "last_name": "doe", "age": "30"}
    schema_map = {
        "first_name": {"target_field": "name", "type": "string", "options": {"uppercase": True}},
        "age": {"target_field": "age", "type": "number", "options": {"type": "int"}}
    }
    
    schema_result = transformer.transform_schema(data, schema_map)
    print(f"Schema transformation: {schema_result.to_dict()}")