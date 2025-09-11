"""
🏗️ Composite Data Types for Complex Structures
Enterprise-grade composite types and nested data structures

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.

🎯 Backend Senior + ML Engineer Role: Complex data structures and AI data types
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Generic, TypeVar
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
from decimal import Decimal
import json

from .base import BaseSchema, TimestampSchema, UUIDSchema
from .primitive_types import EnhancedString, EnhancedInteger, EnhancedFloat, EnhancedDecimal, SecurityLevel


T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


class DataStructureType(str, Enum):
    """Types of composite data structures"""
    RECORD = "record"
    TUPLE = "tuple"
    UNION = "union"
    MAP = "map"
    SET = "set"
    GRAPH = "graph"
    TREE = "tree"
    MATRIX = "matrix"
    TENSOR = "tensor"
    TIME_SERIES = "time_series"
    GEOSPATIAL = "geospatial"


class ValidationMode(str, Enum):
    """Validation modes for composite types"""
    STRICT = "strict"
    LENIENT = "lenient"
    ADAPTIVE = "adaptive"
    LAZY = "lazy"


class Address(BaseSchema):
    """Professional address composite type"""
    street_address: str = Field(description="Street address line 1")
    street_address_2: Optional[str] = Field(None, description="Street address line 2")
    city: str = Field(description="City name")
    state_province: Optional[str] = Field(None, description="State or province")
    postal_code: str = Field(description="Postal/ZIP code")
    country_code: str = Field(description="ISO country code", regex=r'^[A-Z]{2}$')
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    address_type: str = Field(default="general", description="Address type")
    is_verified: bool = Field(default=False, description="Address verification status")


class ContactInfo(BaseSchema):
    """Professional contact information composite"""
    primary_email: EnhancedString = Field(description="Primary email address")
    secondary_email: Optional[EnhancedString] = Field(None, description="Secondary email")
    primary_phone: Optional[str] = Field(None, description="Primary phone number")
    secondary_phone: Optional[str] = Field(None, description="Secondary phone number")
    website: Optional[str] = Field(None, description="Website URL")
    social_links: Dict[str, str] = Field(default_factory=dict, description="Social media links")
    preferred_contact_method: str = Field(default="email", description="Preferred contact method")
    
    @validator('social_links')
    def validate_social_links(cls, v):
        """Validate social media links"""
        allowed_platforms = {
            'twitter', 'linkedin', 'facebook', 'instagram', 
            'youtube', 'tiktok', 'github', 'behance'
        }
        for platform in v.keys():
            if platform not in allowed_platforms:
                raise ValueError(f'Unsupported social platform: {platform}')
        return v


class Money(BaseSchema):
    """Professional money/currency composite type"""
    amount: EnhancedDecimal = Field(description="Monetary amount")
    currency: str = Field(description="Currency code (ISO 4217)", regex=r'^[A-Z]{3}$')
    precision: int = Field(default=2, ge=0, le=8, description="Decimal precision")
    exchange_rate: Optional[Decimal] = Field(None, description="Exchange rate to base currency")
    exchange_date: Optional[datetime] = Field(None, description="Exchange rate date")
    
    @validator('currency')
    def validate_currency_code(cls, v):
        """Validate ISO 4217 currency codes"""
        # Common currency codes - in production would use full ISO list
        valid_currencies = {
            'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR', 'BRL'
        }
        if v not in valid_currencies:
            raise ValueError(f'Unsupported currency code: {v}')
        return v


class Coordinate(BaseSchema):
    """Geospatial coordinate composite type"""
    latitude: float = Field(ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(ge=-180, le=180, description="Longitude in degrees")
    altitude: Optional[float] = Field(None, description="Altitude in meters")
    accuracy: Optional[float] = Field(None, ge=0, description="Position accuracy in meters")
    timestamp: Optional[datetime] = Field(None, description="Coordinate timestamp")
    coordinate_system: str = Field(default="WGS84", description="Coordinate reference system")


class TimeRange(BaseSchema):
    """Time range composite type"""
    start_time: datetime = Field(description="Range start time")
    end_time: datetime = Field(description="Range end time")
    timezone: str = Field(default="UTC", description="Timezone")
    include_start: bool = Field(default=True, description="Include start time in range")
    include_end: bool = Field(default=False, description="Include end time in range")
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        """Ensure end time is after start time"""
        start_time = values.get('start_time')
        if start_time and v <= start_time:
            raise ValueError('End time must be after start time')
        return v
    
    @property
    def duration(self) -> timedelta:
        """Get duration of time range"""
        return self.end_time - self.start_time


class DataPoint(BaseSchema, Generic[T]):
    """Generic data point for time series and analytics"""
    timestamp: datetime = Field(description="Data point timestamp")
    value: T = Field(description="Data point value")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    quality_score: float = Field(default=1.0, ge=0, le=1, description="Data quality score")
    source: Optional[str] = Field(None, description="Data source identifier")
    tags: List[str] = Field(default_factory=list, description="Data point tags")


class TimeSeries(BaseSchema, Generic[T]):
    """Time series data composite type"""
    name: str = Field(description="Time series name")
    description: Optional[str] = Field(None, description="Time series description")
    data_points: List[DataPoint[T]] = Field(description="Time series data points")
    sampling_rate: Optional[str] = Field(None, description="Sampling rate/frequency")
    unit: Optional[str] = Field(None, description="Value unit")
    aggregation_type: Optional[str] = Field(None, description="Aggregation method")
    
    @validator('data_points')
    def validate_chronological_order(cls, v):
        """Ensure data points are in chronological order"""
        if len(v) > 1:
            for i in range(1, len(v)):
                if v[i].timestamp <= v[i-1].timestamp:
                    raise ValueError('Data points must be in chronological order')
        return v
    
    @property
    def start_time(self) -> Optional[datetime]:
        """Get time series start time"""
        return self.data_points[0].timestamp if self.data_points else None
    
    @property
    def end_time(self) -> Optional[datetime]:
        """Get time series end time"""
        return self.data_points[-1].timestamp if self.data_points else None


class Matrix(BaseSchema, Generic[T]):
    """Matrix data structure for ML and analytics"""
    data: List[List[T]] = Field(description="Matrix data as nested lists")
    rows: int = Field(ge=1, description="Number of rows")
    columns: int = Field(ge=1, description="Number of columns")
    data_type: str = Field(description="Matrix element data type")
    sparse: bool = Field(default=False, description="Whether matrix is sparse")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Matrix metadata")
    
    @validator('data')
    def validate_matrix_dimensions(cls, v, values):
        """Validate matrix dimensions"""
        rows = values.get('rows')
        columns = values.get('columns')
        
        if rows and len(v) != rows:
            raise ValueError(f'Matrix has {len(v)} rows, expected {rows}')
        
        if columns:
            for i, row in enumerate(v):
                if len(row) != columns:
                    raise ValueError(f'Row {i} has {len(row)} columns, expected {columns}')
        
        return v


class Graph(BaseSchema):
    """Graph data structure for relationships and networks"""
    nodes: List[Dict[str, Any]] = Field(description="Graph nodes")
    edges: List[Dict[str, Any]] = Field(description="Graph edges") 
    directed: bool = Field(default=True, description="Whether graph is directed")
    weighted: bool = Field(default=False, description="Whether edges are weighted")
    node_attributes: List[str] = Field(default_factory=list, description="Node attribute names")
    edge_attributes: List[str] = Field(default_factory=list, description="Edge attribute names")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Graph metadata")
    
    @validator('edges')
    def validate_edge_references(cls, v, values):
        """Validate edge node references"""
        nodes = values.get('nodes', [])
        node_ids = {node.get('id') for node in nodes if 'id' in node}
        
        for edge in v:
            source = edge.get('source')
            target = edge.get('target')
            
            if source not in node_ids:
                raise ValueError(f'Edge source {source} not found in nodes')
            if target not in node_ids:
                raise ValueError(f'Edge target {target} not found in nodes')
        
        return v


class Tree(BaseSchema, Generic[T]):
    """Tree data structure for hierarchical data"""
    root: T = Field(description="Root node value")
    children: List['Tree[T]'] = Field(default_factory=list, description="Child nodes")
    node_id: str = Field(description="Unique node identifier")
    parent_id: Optional[str] = Field(None, description="Parent node identifier")
    depth: int = Field(default=0, ge=0, description="Node depth in tree")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Node metadata")
    
    @property
    def is_leaf(self) -> bool:
        """Check if node is a leaf"""
        return len(self.children) == 0
    
    @property
    def is_root(self) -> bool:
        """Check if node is root"""
        return self.parent_id is None


class ValidationResult(BaseSchema):
    """Validation result for composite types"""
    is_valid: bool = Field(description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    field_path: str = Field(description="Path to validated field")
    validation_time: datetime = Field(default_factory=datetime.utcnow)


class SchemaDefinition(BaseSchema):
    """Schema definition for composite types"""
    name: str = Field(description="Schema name")
    version: str = Field(description="Schema version")
    structure_type: DataStructureType = Field(description="Data structure type")
    fields: Dict[str, Any] = Field(description="Field definitions")
    constraints: List[Dict[str, Any]] = Field(default_factory=list, description="Schema constraints")
    validation_mode: ValidationMode = Field(default=ValidationMode.STRICT)
    security_level: SecurityLevel = Field(default=SecurityLevel.PUBLIC)


class CompositeTypeValidator:
    """Validator for composite data types"""
    
    def __init__(self):
        self.validators = {
            DataStructureType.RECORD: self._validate_record,
            DataStructureType.TUPLE: self._validate_tuple,
            DataStructureType.UNION: self._validate_union,
            DataStructureType.MAP: self._validate_map,
            DataStructureType.SET: self._validate_set,
            DataStructureType.TIME_SERIES: self._validate_time_series,
            DataStructureType.MATRIX: self._validate_matrix,
            DataStructureType.GRAPH: self._validate_graph,
            DataStructureType.TREE: self._validate_tree,
        }
    
    def validate(self, data: Any, schema: SchemaDefinition) -> ValidationResult:
        """Validate data against composite type schema"""
        validator_func = self.validators.get(schema.structure_type)
        if not validator_func:
            return ValidationResult(
                is_valid=False,
                errors=[f"No validator for structure type: {schema.structure_type}"],
                field_path="root"
            )
        
        return validator_func(data, schema)
    
    def _validate_record(self, data: Any, schema: SchemaDefinition) -> ValidationResult:
        """Validate record structure"""
        errors = []
        warnings = []
        
        if not isinstance(data, dict):
            errors.append("Record must be a dictionary")
        else:
            # Check required fields
            required_fields = [name for name, field_def in schema.fields.items() 
                             if field_def.get('required', False)]
            
            missing_fields = set(required_fields) - set(data.keys())
            if missing_fields:
                errors.append(f"Missing required fields: {missing_fields}")
            
            # Check extra fields if strict mode
            if schema.validation_mode == ValidationMode.STRICT:
                extra_fields = set(data.keys()) - set(schema.fields.keys())
                if extra_fields:
                    errors.append(f"Extra fields not allowed: {extra_fields}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            field_path="record"
        )
    
    def _validate_tuple(self, data: Any, schema: SchemaDefinition) -> ValidationResult:
        """Validate tuple structure"""
        errors = []
        
        if not isinstance(data, (list, tuple)):
            errors.append("Tuple must be a list or tuple")
        else:
            expected_length = schema.fields.get('length')
            if expected_length and len(data) != expected_length:
                errors.append(f"Tuple length {len(data)} != expected {expected_length}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            field_path="tuple"
        )
    
    def _validate_union(self, data: Any, schema: SchemaDefinition) -> ValidationResult:
        """Validate union type"""
        allowed_types = schema.fields.get('types', [])
        data_type = type(data).__name__
        
        if data_type not in allowed_types:
            return ValidationResult(
                is_valid=False,
                errors=[f"Type {data_type} not in allowed union types: {allowed_types}"],
                field_path="union"
            )
        
        return ValidationResult(is_valid=True, errors=[], field_path="union")
    
    def _validate_map(self, data: Any, schema: SchemaDefinition) -> ValidationResult:
        """Validate map/dictionary structure"""
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Map must be a dictionary")
        else:
            max_size = schema.fields.get('max_size')
            if max_size and len(data) > max_size:
                errors.append(f"Map size {len(data)} exceeds maximum {max_size}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            field_path="map"
        )
    
    def _validate_set(self, data: Any, schema: SchemaDefinition) -> ValidationResult:
        """Validate set structure"""
        errors = []
        
        if not isinstance(data, (set, list)):
            errors.append("Set must be a set or list")
        else:
            if isinstance(data, list):
                if len(data) != len(set(data)):
                    errors.append("List contains duplicate values, not a valid set")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            field_path="set"
        )
    
    def _validate_time_series(self, data: Any, schema: SchemaDefinition) -> ValidationResult:
        """Validate time series structure"""
        errors = []
        
        if not isinstance(data, dict) or 'data_points' not in data:
            errors.append("Time series must have data_points field")
        else:
            data_points = data['data_points']
            if not isinstance(data_points, list):
                errors.append("data_points must be a list")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            field_path="time_series"
        )
    
    def _validate_matrix(self, data: Any, schema: SchemaDefinition) -> ValidationResult:
        """Validate matrix structure"""
        errors = []
        
        if not isinstance(data, dict) or 'data' not in data:
            errors.append("Matrix must have data field")
        else:
            matrix_data = data['data']
            if not isinstance(matrix_data, list):
                errors.append("Matrix data must be a list of lists")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            field_path="matrix"
        )
    
    def _validate_graph(self, data: Any, schema: SchemaDefinition) -> ValidationResult:
        """Validate graph structure"""
        errors = []
        
        required_fields = ['nodes', 'edges']
        for field in required_fields:
            if field not in data:
                errors.append(f"Graph must have {field} field")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            field_path="graph"
        )
    
    def _validate_tree(self, data: Any, schema: SchemaDefinition) -> ValidationResult:
        """Validate tree structure"""
        errors = []
        
        if not isinstance(data, dict) or 'root' not in data:
            errors.append("Tree must have root field")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            field_path="tree"
        )


# Type aliases for convenience
AinflueAddress = Address
AinflueContactInfo = ContactInfo
AinflueMoney = Money
AinflueCoordinate = Coordinate
AinflueTimeRange = TimeRange
AinflueDataPoint = DataPoint
AinflueTimeSeries = TimeSeries
AinflueMatrix = Matrix
AinflueGraph = Graph
AinflueTree = Tree

# Fix forward reference for Tree
Tree.model_rebuild()

# Export all types
__all__ = [
    'DataStructureType',
    'ValidationMode',
    'Address',
    'ContactInfo',
    'Money',
    'Coordinate',
    'TimeRange',
    'DataPoint',
    'TimeSeries',
    'Matrix',
    'Graph',
    'Tree',
    'ValidationResult',
    'SchemaDefinition',
    'CompositeTypeValidator',
    'AinflueAddress',
    'AinflueContactInfo',
    'AinflueMoney',
    'AinflueCoordinate',
    'AinflueTimeRange',
    'AinflueDataPoint',
    'AinflueTimeSeries',
    'AinflueMatrix',
    'AinflueGraph',
    'AinflueTree'
]