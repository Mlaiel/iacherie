"""Schema Validator for MongoDB Migrations
=======================================

Schema validation and compatibility checking for database migrations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Schema validation result."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    compatibility_score: float

class SchemaValidator:
    """MongoDB schema validation and compatibility checker."""
    
    def __init__(self):
        """Initialize schema validator."""
        self._validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load schema validation rules."""
        return {
            "required_fields": ["_id"],
            "forbidden_field_names": ["__proto__", "constructor"],
            "max_nesting_level": 20,
            "max_field_name_length": 127,
            "max_document_size_mb": 16
        }
    
    def validate_schema(self, schema: Dict[str, Any]) -> ValidationResult:
        """Validate MongoDB schema definition."""
        errors = []
        warnings = []
        
        # Basic validation
        if not isinstance(schema, dict):
            errors.append("Schema must be a dictionary")
            return ValidationResult(False, errors, warnings, 0.0)
        
        # Check for forbidden patterns
        self._check_forbidden_patterns(schema, errors, warnings)
        
        # Check nesting depth
        self._check_nesting_depth(schema, errors, warnings)
        
        # Check field names
        self._check_field_names(schema, errors, warnings)
        
        is_valid = len(errors) == 0
        compatibility_score = self._calculate_compatibility_score(schema, errors, warnings)
        
        return ValidationResult(is_valid, errors, warnings, compatibility_score)
    
    def _check_forbidden_patterns(self, schema: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Check for forbidden patterns in schema."""
        for field_name in schema.keys():
            if field_name in self._validation_rules["forbidden_field_names"]:
                errors.append(f"Forbidden field name: {field_name}")
    
    def _check_nesting_depth(self, schema: Dict[str, Any], errors: List[str], warnings: List[str], depth: int = 0):
        """Check schema nesting depth."""
        if depth > self._validation_rules["max_nesting_level"]:
            errors.append(f"Schema nesting too deep: {depth} levels")
            return
        
        for value in schema.values():
            if isinstance(value, dict):
                self._check_nesting_depth(value, errors, warnings, depth + 1)
    
    def _check_field_names(self, schema: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Check field name validity."""
        for field_name in schema.keys():
            if len(field_name) > self._validation_rules["max_field_name_length"]:
                errors.append(f"Field name too long: {field_name}")
            
            if field_name.startswith('$'):
                warnings.append(f"Field name starts with $: {field_name}")
    
    def _calculate_compatibility_score(self, schema: Dict[str, Any], errors: List[str], warnings: List[str]) -> float:
        """Calculate schema compatibility score."""
        base_score = 100.0
        penalty_per_error = 10.0
        penalty_per_warning = 2.0
        
        score = base_score - (len(errors) * penalty_per_error) - (len(warnings) * penalty_per_warning)
        return max(0.0, min(100.0, score))

_default_validator: Optional[SchemaValidator] = None

def get_schema_validator() -> SchemaValidator:
    global _default_validator
    if _default_validator is None:
        _default_validator = SchemaValidator()
    return _default_validator

__all__ = ['ValidationResult', 'SchemaValidator', 'get_schema_validator']