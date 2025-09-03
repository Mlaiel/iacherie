"""
Validation Framework for Ainflue Platform
Implements all validation criteria for final acceptance
"""

__version__ = "1.0.0"

# Export main validation functions
from .validator import validate_all_criteria, get_validation_criteria
from .performance import validate_api_performance, get_performance_tracker
from .security import validate_security_compliance, get_security_validator
from .scalability import validate_scalability_requirements, get_scalability_validator
from .quality import validate_quality_requirements, get_quality_validator

__all__ = [
    "validate_all_criteria",
    "get_validation_criteria", 
    "validate_api_performance",
    "get_performance_tracker",
    "validate_security_compliance",
    "get_security_validator",
    "validate_scalability_requirements", 
    "get_scalability_validator",
    "validate_quality_requirements",
    "get_quality_validator"
]