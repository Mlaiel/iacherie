"""Module Index - Audit Trail Agent Components Registry

Centralized index for all audit trail agent modules providing quick access,
initialization coordination, and service discovery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and intellectual property belong exclusively to Fahed Mlaiel.
Unauthorized use, distribution, or commercialization is strictly prohibited.
"""

from typing import Dict, List, Optional, Any, Type
import logging

from .audit_trail_agent import AuditTrailAgent
from .security_monitor import SecurityAuditMonitor
from .compliance_tracker import ComplianceTracker
from .forensic_analyzer import ForensicAnalyzer
from .activity_logger import ActivityLogger
from .event_correlator import EventCorrelator

logger = logging.getLogger(__name__)

# Module Registry
AUDIT_MODULES = {
    "audit_trail_agent": {
        "class": AuditTrailAgent,
        "description": "Main audit trail orchestration agent",
        "capabilities": [
            "comprehensive_audit_logging",
            "security_event_monitoring",
            "compliance_verification",
            "forensic_investigation_support"
        ],
        "priority": 1
    },
    "security_monitor": {
        "class": SecurityAuditMonitor,
        "description": "Advanced security event detection and monitoring",
        "capabilities": [
            "threat_detection",
            "brute_force_detection",
            "api_abuse_monitoring",
            "insider_threat_detection"
        ],
        "priority": 2
    },
    "compliance_tracker": {
        "class": ComplianceTracker,
        "description": "Multi-framework regulatory compliance management",
        "capabilities": [
            "gdpr_compliance",
            "sox_compliance",
            "hipaa_compliance",
            "data_retention_management",
            "consent_tracking"
        ],
        "priority": 3
    },
    "forensic_analyzer": {
        "class": ForensicAnalyzer,
        "description": "Digital forensics and incident investigation",
        "capabilities": [
            "evidence_collection",
            "timeline_reconstruction",
            "threat_attribution",
            "forensic_reporting"
        ],
        "priority": 4
    },
    "activity_logger": {
        "class": ActivityLogger,
        "description": "High-performance activity tracking and logging",
        "capabilities": [
            "real_time_logging",
            "batch_processing",
            "activity_analytics",
            "performance_optimization"
        ],
        "priority": 5
    },
    "event_correlator": {
        "class": EventCorrelator,
        "description": "Advanced event correlation and pattern analysis",
        "capabilities": [
            "pattern_detection",
            "event_correlation",
            "anomaly_detection",
            "predictive_analysis"
        ],
        "priority": 6
    }
}

# Service Dependencies
MODULE_DEPENDENCIES = {
    "audit_trail_agent": [],  # No dependencies - core module
    "security_monitor": ["activity_logger"],
    "compliance_tracker": ["activity_logger", "event_correlator"],
    "forensic_analyzer": ["security_monitor", "event_correlator"],
    "activity_logger": [],  # No dependencies - foundational module
    "event_correlator": ["activity_logger"]
}

def get_module_info(module_name: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific audit module
    
    Args:
        module_name: Name of the module
        
    Returns:
        Module information dictionary or None if not found
    """
    return AUDIT_MODULES.get(module_name)

def get_all_modules() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all available audit modules
    
    Returns:
        Dictionary of all module information
    """
    return AUDIT_MODULES.copy()

def get_module_class(module_name: str) -> Optional[Type]:
    """
    Get the class for a specific audit module
    
    Args:
        module_name: Name of the module
        
    Returns:
        Module class or None if not found
    """
    module_info = AUDIT_MODULES.get(module_name)
    return module_info["class"] if module_info else None

def get_initialization_order() -> List[str]:
    """
    Get the recommended initialization order for audit modules
    
    Returns:
        List of module names in initialization order
    """
    return sorted(AUDIT_MODULES.keys(), key=lambda x: AUDIT_MODULES[x]["priority"])

def get_module_dependencies(module_name: str) -> List[str]:
    """
    Get the dependencies for a specific module
    
    Args:
        module_name: Name of the module
        
    Returns:
        List of dependency module names
    """
    return MODULE_DEPENDENCIES.get(module_name, [])

def validate_module_dependencies() -> Dict[str, List[str]]:
    """
    Validate all module dependencies and identify any issues
    
    Returns:
        Dictionary of validation issues by module
    """
    issues = {}
    
    for module_name, dependencies in MODULE_DEPENDENCIES.items():
        module_issues = []
        
        if module_name not in AUDIT_MODULES:
            module_issues.append(f"Module {module_name} not found in registry")
        
        for dependency in dependencies:
            if dependency not in AUDIT_MODULES:
                module_issues.append(f"Dependency {dependency} not found in registry")
        
        if module_issues:
            issues[module_name] = module_issues
    
    return issues

# Module Capability Matrix
CAPABILITY_MATRIX = {
    "audit_logging": ["audit_trail_agent", "activity_logger"],
    "security_monitoring": ["security_monitor", "audit_trail_agent"],
    "compliance_management": ["compliance_tracker", "audit_trail_agent"],
    "forensic_investigation": ["forensic_analyzer", "audit_trail_agent"],
    "pattern_detection": ["event_correlator", "forensic_analyzer"],
    "threat_detection": ["security_monitor", "event_correlator"],
    "data_retention": ["compliance_tracker", "activity_logger"],
    "performance_monitoring": ["activity_logger", "audit_trail_agent"]
}

def get_modules_by_capability(capability: str) -> List[str]:
    """
    Get modules that provide a specific capability
    
    Args:
        capability: Capability name
        
    Returns:
        List of module names that provide the capability
    """
    return CAPABILITY_MATRIX.get(capability, [])

def get_all_capabilities() -> List[str]:
    """
    Get all available capabilities across audit modules
    
    Returns:
        List of all capability names
    """
    return list(CAPABILITY_MATRIX.keys())

# Module Status Tracking
module_status = {
    module_name: {
        "initialized": False,
        "healthy": False,
        "last_check": None,
        "error_count": 0
    }
    for module_name in AUDIT_MODULES.keys()
}

def update_module_status(module_name: str, status_update: Dict[str, Any]) -> None:
    """
    Update the status of a specific module
    
    Args:
        module_name: Name of the module
        status_update: Status update dictionary
    """
    if module_name in module_status:
        module_status[module_name].update(status_update)
        logger.info(f"Module status updated: {module_name} - {status_update}")

def get_module_status(module_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the current status of a specific module
    
    Args:
        module_name: Name of the module
        
    Returns:
        Module status dictionary or None if not found
    """
    return module_status.get(module_name)

def get_all_module_statuses() -> Dict[str, Dict[str, Any]]:
    """
    Get the current status of all modules
    
    Returns:
        Dictionary of all module statuses
    """
    return module_status.copy()

def get_healthy_modules() -> List[str]:
    """
    Get list of all healthy/operational modules
    
    Returns:
        List of healthy module names
    """
    return [
        name for name, status in module_status.items()
        if status.get("healthy", False) and status.get("initialized", False)
    ]

def get_unhealthy_modules() -> List[str]:
    """
    Get list of all unhealthy/problematic modules
    
    Returns:
        List of unhealthy module names
    """
    return [
        name for name, status in module_status.items()
        if not status.get("healthy", False) or not status.get("initialized", False)
    ]

# Configuration Templates
MODULE_CONFIG_TEMPLATES = {
    "audit_trail_agent": {
        "retention_period_days": 2555,  # 7 years
        "encryption_enabled": True,
        "real_time_alerts": True,
        "compliance_monitoring": True
    },
    "security_monitor": {
        "enable_real_time_monitoring": True,
        "enable_behavioral_analysis": True,
        "max_failed_login_attempts": 5,
        "brute_force_window_minutes": 15
    },
    "compliance_tracker": {
        "enabled_frameworks": ["GDPR", "SOX", "HIPAA"],
        "auto_anonymization": True,
        "consent_tracking": True,
        "data_retention_enforcement": True
    },
    "forensic_analyzer": {
        "evidence_retention_days": 2555,
        "chain_of_custody_enabled": True,
        "hash_verification_enabled": True,
        "automated_attribution": True
    },
    "activity_logger": {
        "enable_real_time_logging": True,
        "enable_batch_processing": True,
        "batch_size": 1000,
        "retention_days": 365
    },
    "event_correlator": {
        "enable_real_time_correlation": True,
        "enable_pattern_learning": True,
        "correlation_threshold": 0.7,
        "time_window_minutes": 60
    }
}

def get_module_config_template(module_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the configuration template for a specific module
    
    Args:
        module_name: Name of the module
        
    Returns:
        Configuration template dictionary or None if not found
    """
    return MODULE_CONFIG_TEMPLATES.get(module_name, {}).copy()

def get_all_config_templates() -> Dict[str, Dict[str, Any]]:
    """
    Get configuration templates for all modules
    
    Returns:
        Dictionary of all configuration templates
    """
    return {name: template.copy() for name, template in MODULE_CONFIG_TEMPLATES.items()}

# Export all public components
__all__ = [
    "AUDIT_MODULES",
    "MODULE_DEPENDENCIES", 
    "CAPABILITY_MATRIX",
    "get_module_info",
    "get_all_modules",
    "get_module_class",
    "get_initialization_order",
    "get_module_dependencies",
    "validate_module_dependencies",
    "get_modules_by_capability",
    "get_all_capabilities",
    "update_module_status",
    "get_module_status", 
    "get_all_module_statuses",
    "get_healthy_modules",
    "get_unhealthy_modules",
    "get_module_config_template",
    "get_all_config_templates"
]
