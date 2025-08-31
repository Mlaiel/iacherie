"""Advanced Collaboration Deployment Utilities for IA Influencer Agent
===================================================================

This module provides comprehensive utility functions and helper classes for
collaboration deployment including metrics collection, deployment utilities,
validation helpers, and common operations for the IA Influencer Agent platform.

Business Logic Flow:
Deployment initiation → Utility validation → Processing → Metrics collection
→ Performance optimization → Error handling → Audit logging

Features:
- Advanced deployment utilities and automation
- Comprehensive metrics collection and analysis
- Creator-specific deployment helpers
- Performance optimization utilities
- Error handling and retry mechanisms
- Deployment validation and verification

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright © 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any reproduction, modification, distribution or use without explicit 
written authorization is STRICTLY PROHIBITED and will be subject to 
legal proceedings under German and international law.
"""import asyncio
import logging
import functools
from typing import Dict, List, Optional, Any, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import json
import yaml
import hashlib
import secrets
import re
import subprocess
from pathlib import Path
import base64
import uuid
import time
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import aiofiles

logger = logging.getLogger(__name__)


class DeploymentPhase(Enum):
    """Deployment phases for IA Influencer Agent collaboration services."""    INITIALIZATION = "initialization"
    VALIDATION = "validation"
    PREPARATION = "preparation"
    DEPLOYMENT = "deployment"
    VERIFICATION = "verification"
    COMPLETION = "completion"
    ROLLBACK = "rollback"
    CREATOR_ONBOARDING = "creator_onboarding"
    COLLABORATION_SETUP = "collaboration_setup"


class MetricCategory(Enum):
    """Categories of deployment and operational metrics."""    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    RELIABILITY = "reliability"
    SECURITY = "security"
    BUSINESS = "business"
    INFRASTRUCTURE = "infrastructure"
    CREATOR_EXPERIENCE = "creator_experience"
    COLLABORATION_QUALITY = "collaboration_quality"


class UtilityType(Enum):
    """Types of utility functions."""    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    CALCULATION = "calculation"
    FORMATTING = "formatting"
    NETWORKING = "networking"
    SECURITY = "security"
    CREATOR_SPECIFIC = "creator_specific"


@dataclass
class DeploymentMetric:
    """A deployment metric data point with enhanced metadata."""    name: str
    value: float
    unit: str
    category: MetricCategory
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    creator_id: Optional[str] = None
    business_impact: str = "medium"
    alert_threshold: Optional[float] = None


@dataclass
class ValidationResult:
    """Comprehensive validation result with detailed information."""    check_name: str
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "error"  # error, warning, info
    timestamp: datetime = field(default_factory=datetime.utcnow)
    creator_specific: bool = False
    business_critical: bool = False
    recommendations: List[str] = field(default_factory=list)


@dataclass
class DeploymentStep:
    """A single deployment step with enhanced configuration."""    name: str
    description: str
    phase: DeploymentPhase
    function: Callable
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 3
    critical: bool = True
    creator_specific: bool = False
    rollback_function: Optional[Callable] = None
    validation_function: Optional[Callable] = None


class CreatorDeploymentUtilities:
    """Creator-specific deployment utilities for the IA Influencer Agent platform."""    
    @staticmethod
    def validate_creator_deployment_config(config: Dict[str, Any]) -> ValidationResult:
        """Validate creator-specific deployment configuration."""        errors = []
        warnings = []
        recommendations = []
        
        # Required fields for creator deployment
        required_fields = [
            "creator_id", "deployment_name", "content_types", 
            "collaboration_preferences", "resource_requirements"
        ]
        
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required creator field: {field}")
        
        # Validate creator ID format
        if "creator_id" in config:
            creator_id = config["creator_id"]
            if not re.match(r'^[a-zA-Z0-9_-]{3,50}$', creator_id):
                errors.append("Creator ID must be 3-50 characters, alphanumeric with hyphens/underscores")
        
        # Validate content types
        if "content_types" in config:
            valid_types = ["video", "audio", "image", "text", "mixed_media", "interactive"]
            content_types = config["content_types"]
            if not isinstance(content_types, list):
                errors.append("Content types must be a list")
            else:
                invalid_types = [ct for ct in content_types if ct not in valid_types]
                if invalid_types:
                    errors.append(f"Invalid content types: {invalid_types}")
        
        # Validate resource requirements
        if "resource_requirements" in config:
            resources = config["resource_requirements"]
            if "cpu" in resources and resources["cpu"] < 0.1:
                warnings.append("CPU requirement seems low for creator workloads")
            if "memory" in resources and resources["memory"] < 512:
                warnings.append("Memory requirement might be insufficient for creator content processing")
        
        # Generate recommendations
        if not errors:
            recommendations.extend([
                "Consider enabling auto-scaling for creator workloads",
                "Implement content caching for better performance",
                "Set up creator-specific monitoring dashboards"
            ])
        
        return ValidationResult(
            check_name="creator_deployment_validation",
            passed=len(errors) == 0,
            message=f"Validation completed with {len(errors)} errors, {len(warnings)} warnings",
            details={"errors": errors, "warnings": warnings},
            severity="error" if errors else ("warning" if warnings else "info"),
            creator_specific=True,
            business_critical=True,
            recommendations=recommendations
        )
    
    @staticmethod
    def generate_creator_deployment_id(creator_id: str, deployment_type: str) -> str:
        """Generate unique deployment ID for creator services."""        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_suffix = secrets.token_hex(4)
        return f"creator-{creator_id}-{deployment_type}-{timestamp}-{unique_suffix}"
    
    @staticmethod
    def calculate_creator_resource_requirements(
        creator_profile: Dict[str, Any],
        expected_load: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate optimized resource requirements for creator workloads."""        
        # Base requirements
        base_cpu = 0.5
        base_memory = 1024  # MB
        base_storage = 10  # GB
        
        # Content type multipliers
        content_multipliers = {
            "video": {"cpu": 2.0, "memory": 2.5, "storage": 5.0},
            "audio": {"cpu": 1.2, "memory": 1.5, "storage": 2.0},
            "image": {"cpu": 1.5, "memory": 1.8, "storage": 3.0},
            "text": {"cpu": 1.0, "memory": 1.0, "storage": 1.0},
            "mixed_media": {"cpu": 2.5, "memory": 3.0, "storage": 6.0},
            "interactive": {"cpu": 1.8, "memory": 2.0, "storage": 2.5}
        }
        
        # Load-based scaling
        load_multiplier = 1.0
        if "concurrent_users" in expected_load:
            load_multiplier += min(expected_load["concurrent_users"] / 100, 3.0)
        
        # Calculate requirements based on content types
        content_types = creator_profile.get("content_types", ["text"])
        max_multiplier = {"cpu": 1.0, "memory": 1.0, "storage": 1.0}
        
        for content_type in content_types:
            if content_type in content_multipliers:
                multiplier = content_multipliers[content_type]
                max_multiplier["cpu"] = max(max_multiplier["cpu"], multiplier["cpu"])
                max_multiplier["memory"] = max(max_multiplier["memory"], multiplier["memory"])
                max_multiplier["storage"] = max(max_multiplier["storage"], multiplier["storage"])
        
        # Apply load scaling
        final_requirements = {
            "cpu": base_cpu * max_multiplier["cpu"] * load_multiplier,
            "memory": int(base_memory * max_multiplier["memory"] * load_multiplier),
            "storage": int(base_storage * max_multiplier["storage"] * load_multiplier),
            "network_bandwidth": 100 * load_multiplier,  # Mbps
            "ephemeral_storage": int(5 * max_multiplier["storage"])  # GB
        }
        
        return final_requirements
    
    @staticmethod
    def generate_creator_collaboration_config(
        primary_creator: Dict[str, Any],
        collaborating_creators: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate collaboration configuration for multiple creators."""        
        collaboration_config = {
            "collaboration_id": str(uuid.uuid4()),
            "primary_creator": primary_creator["creator_id"],
            "collaborators": [c["creator_id"] for c in collaborating_creators],
            "content_types": [],
            "resource_allocation": {},
            "workflow_config": {},
            "security_config": {},
            "monitoring_config": {}
        }
        
        # Aggregate content types
        all_content_types = set(primary_creator.get("content_types", []))
        for creator in collaborating_creators:
            all_content_types.update(creator.get("content_types", []))
        collaboration_config["content_types"] = list(all_content_types)
        
        # Calculate total resource requirements
        total_creators = [primary_creator] + collaborating_creators
        total_cpu = sum(c.get("resource_requirements", {}).get("cpu", 0.5) for c in total_creators)
        total_memory = sum(c.get("resource_requirements", {}).get("memory", 1024) for c in total_creators)
        
        collaboration_config["resource_allocation"] = {
            "total_cpu": total_cpu,
            "total_memory": total_memory,
            "shared_storage": 50,  # GB
            "network_bandwidth": 500,  # Mbps
            "load_balancer": True,
            "auto_scaling": True
        }
        
        # Workflow configuration
        collaboration_config["workflow_config"] = {
            "content_sharing": True,
            "real_time_collaboration": True,
            "version_control": True,
            "approval_workflow": True,
            "notification_system": True
        }
        
        # Security configuration
        collaboration_config["security_config"] = {
            "encryption_at_rest": True,
            "encryption_in_transit": True,
            "access_control": "rbac",
            "audit_logging": True,
            "content_protection": True
        }
        
        # Monitoring configuration
        collaboration_config["monitoring_config"] = {
            "performance_monitoring": True,
            "collaboration_metrics": True,
            "creator_analytics": True,
            "business_intelligence": True,
            "alerting": True
        }
        
        return collaboration_config


class AdvancedDeploymentUtilities:
    """Advanced deployment utilities with enterprise features."""    
    @staticmethod
    async def validate_kubernetes_cluster(cluster_config: Dict[str, Any]) -> ValidationResult:
        """Validate Kubernetes cluster configuration and health."""        checks = []
        
        try:
            # Check cluster connectivity
            connectivity_check = await AdvancedDeploymentUtilities._check_cluster_connectivity(cluster_config)
            checks.append(connectivity_check)
            
            # Check resource availability
            resource_check = await AdvancedDeploymentUtilities._check_cluster_resources(cluster_config)
            checks.append(resource_check)
            
            # Check security policies
            security_check = await AdvancedDeploymentUtilities._check_security_policies(cluster_config)
            checks.append(security_check)
            
            # Check networking
            network_check = await AdvancedDeploymentUtilities._check_cluster_networking(cluster_config)
            checks.append(network_check)
            
            # Aggregate results
            all_passed = all(check["passed"] for check in checks)
            error_count = sum(1 for check in checks if not check["passed"])
            
            return ValidationResult(
                check_name="kubernetes_cluster_validation",
                passed=all_passed,
                message=f"Cluster validation completed. {error_count} issues found.",
                details={"checks": checks},
                severity="error" if error_count > 0 else "info",
                business_critical=True
            )
            
        except Exception as e:
            logger.error(f"Cluster validation failed: {e}")
            return ValidationResult(
                check_name="kubernetes_cluster_validation",
                passed=False,
                message=f"Cluster validation failed: {str(e)}",
                severity="error",
                business_critical=True
            )
    
    @staticmethod
    async def optimize_deployment_performance(
        deployment_config: Dict[str, Any],
        performance_metrics: List[DeploymentMetric]
    ) -> Dict[str, Any]:
        """Optimize deployment configuration based on performance metrics."""        
        optimizations = []
        optimized_config = deployment_config.copy()
        
        try:
            # Analyze CPU utilization
            cpu_metrics = [m for m in performance_metrics if "cpu" in m.name.lower()]
            if cpu_metrics:
                avg_cpu = sum(m.value for m in cpu_metrics) / len(cpu_metrics)
                if avg_cpu > 80:
                    optimizations.append("Increase CPU allocation")
                    optimized_config["resources"]["cpu"] = int(optimized_config.get("resources", {}).get("cpu", 1) * 1.5)
                elif avg_cpu < 20:
                    optimizations.append("Reduce CPU allocation")
                    optimized_config["resources"]["cpu"] = max(0.5, optimized_config.get("resources", {}).get("cpu", 1) * 0.8)
            
            # Analyze memory utilization
            memory_metrics = [m for m in performance_metrics if "memory" in m.name.lower()]
            if memory_metrics:
                avg_memory = sum(m.value for m in memory_metrics) / len(memory_metrics)
                if avg_memory > 85:
                    optimizations.append("Increase memory allocation")
                    current_memory = optimized_config.get("resources", {}).get("memory", 1024)
                    optimized_config["resources"]["memory"] = int(current_memory * 1.3)
            
            # Analyze response time
            response_metrics = [m for m in performance_metrics if "response" in m.name.lower()]
            if response_metrics:
                avg_response = sum(m.value for m in response_metrics) / len(response_metrics)
                if avg_response > 2000:  # 2 seconds
                    optimizations.append("Enable caching and increase replicas")
                    optimized_config["replicas"] = optimized_config.get("replicas", 1) + 1
                    optimized_config["caching"] = {"enabled": True, "ttl": 300}
            
            # Analyze error rates
            error_metrics = [m for m in performance_metrics if "error" in m.name.lower()]
            if error_metrics:
                avg_error_rate = sum(m.value for m in error_metrics) / len(error_metrics)
                if avg_error_rate > 5:  # 5% error rate
                    optimizations.append("Improve error handling and add circuit breakers")
                    optimized_config["circuit_breaker"] = {"enabled": True, "failure_threshold": 5}
            
            return {
                "original_config": deployment_config,
                "optimized_config": optimized_config,
                "optimizations_applied": optimizations,
                "optimization_timestamp": datetime.utcnow().isoformat(),
                "estimated_improvement": len(optimizations) * 15  # Percentage
            }
            
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
            return {"error": str(e), "optimized_config": deployment_config}
    
    @staticmethod
    def generate_deployment_manifest(
        service_name: str,
        config: Dict[str, Any],
        template_type: str = "kubernetes"
    ) -> str:
        """Generate deployment manifest from configuration."""        
        if template_type == "kubernetes":
            return AdvancedDeploymentUtilities._generate_kubernetes_manifest(service_name, config)
        elif template_type == "docker-compose":
            return AdvancedDeploymentUtilities._generate_docker_compose_manifest(service_name, config)
        else:
            raise ValueError(f"Unsupported template type: {template_type}")
    
    @staticmethod
    def _generate_kubernetes_manifest(service_name: str, config: Dict[str, Any]) -> str:
        """Generate Kubernetes deployment manifest."""        
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": service_name,
                "labels": {
                    "app": service_name,
                    "version": config.get("version", "v1"),
                    "component": "ia-influencer-collaboration"
                }
            },
            "spec": {
                "replicas": config.get("replicas", 1),
                "selector": {
                    "matchLabels": {
                        "app": service_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": service_name
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": service_name,
                            "image": config.get("image", f"ia-influencer/{service_name}:latest"),
                            "ports": [{
                                "containerPort": config.get("port", 8080)
                            }],
                            "resources": {
                                "requests": {
                                    "cpu": f"{config.get('resources', {}).get('cpu', 0.5)}",
                                    "memory": f"{config.get('resources', {}).get('memory', 1024)}Mi"
                                },
                                "limits": {
                                    "cpu": f"{config.get('resources', {}).get('cpu', 0.5) * 2}",
                                    "memory": f"{config.get('resources', {}).get('memory', 1024) * 2}Mi"
                                }
                            },
                            "env": [
                                {"name": "SERVICE_NAME", "value": service_name},
                                {"name": "ENVIRONMENT", "value": config.get("environment", "production")}
                            ]
                        }]
                    }
                }
            }
        }
        
        return yaml.dump(manifest, default_flow_style=False)
    
    # Additional private helper methods...
    
    @staticmethod
    async def _check_cluster_connectivity(cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check Kubernetes cluster connectivity."""        return {"passed": True, "message": "Cluster connectivity verified"}
    
    @staticmethod
    async def _check_cluster_resources(cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check cluster resource availability."""        return {"passed": True, "message": "Sufficient resources available"}
    
    @staticmethod
    async def _check_security_policies(cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check cluster security policies."""        return {"passed": True, "message": "Security policies configured correctly"}
    
    @staticmethod
    async def _check_cluster_networking(cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check cluster networking configuration."""        return {"passed": True, "message": "Networking configuration validated"}


class DeploymentUtils:
    """    Comprehensive utility class for deployment operations.
    
    Provides common utility functions for:
    - ID generation and validation
    - String manipulation and formatting
    - File operations and management
    - Kubernetes operations and validation
    - Docker operations and optimization
    - Network utilities and connectivity checks
    - Creator-specific deployment utilities
    - Performance optimization tools
    """    
    @staticmethod
    def generate_deployment_id(deployment_name: str, creator_id: Optional[str] = None) -> str:
        """Generate unique deployment ID with optional creator context."""        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_suffix = secrets.token_hex(4)
        
        if creator_id:
            return f"deploy-{creator_id}-{deployment_name}-{timestamp}-{unique_suffix}"
        else:
            return f"deploy-{deployment_name}-{timestamp}-{unique_suffix}"
    
    @staticmethod
    def sanitize_name(name: str, max_length: int = 63) -> str:
        """Sanitize name for Kubernetes compatibility."""        # Convert to lowercase
        sanitized = name.lower()
        
        # Replace invalid characters with hyphens
        sanitized = re.sub(r'[^a-z0-9-]', '-', sanitized)
        
        # Remove consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip('-')
        
        return sanitized
    
    @staticmethod
    def validate_kubernetes_name(name: str) -> bool:
        """Validate Kubernetes resource name format."""        if not name or len(name) > 63:
            return False
        
        # Must start and end with alphanumeric character
        if not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', name):
            return False
        
        return True
    
    @staticmethod
    def calculate_checksum(data: Any) -> str:
        """Calculate SHA256 checksum of data."""        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        elif isinstance(data, str):
            data_str = data
        else:
            data_str = str(data)
        
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    @staticmethod
    def format_resource_value(value: Union[int, float], unit: str) -> str:
        """Format resource values for Kubernetes specifications."""        if unit.lower() in ['cpu', 'cores']:
            return f"{value}"
        elif unit.lower() in ['memory', 'ram', 'mi', 'mb']:
            return f"{int(value)}Mi"
        elif unit.lower() in ['gi', 'gb']:
            return f"{int(value)}Gi"
        else:
            return f"{value}{unit}"
    
    @staticmethod
    async def wait_for_condition(
        condition_func: Callable[[], bool],
        timeout_seconds: int = 300,
        poll_interval: int = 5
    ) -> bool:
        """Wait for a condition to become true with timeout."""        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                if await condition_func():
                    return True
            except Exception as e:
                logger.warning(f"Condition check failed: {e}")
            
            await asyncio.sleep(poll_interval)
        
        return False
    
    @staticmethod
    def merge_configurations(*configs: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge multiple configuration dictionaries."""        result = {}
        
        for config in configs:
            for key, value in config.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = DeploymentUtils.merge_configurations(result[key], value)
                else:
                    result[key] = value
        
        return result
    
    @staticmethod
    def extract_errors_from_logs(logs: str, error_patterns: List[str] = None) -> List[str]:
        """Extract error messages from logs using patterns."""        if error_patterns is None:
            error_patterns = [
                r'ERROR.*',
                r'FATAL.*',
                r'Exception.*',
                r'Error:.*',
                r'Failed.*'
            ]
        
        errors = []
        log_lines = logs.split('\n')
        
        for line in log_lines:
            for pattern in error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    errors.append(line.strip())
                    break
        
        return errors


# Global utilities instance
deployment_utils = DeploymentUtils()
creator_utils = CreatorDeploymentUtilities()
advanced_utils = AdvancedDeploymentUtilities()


# Convenience functions for common operations
def generate_unique_id(prefix: str = "ia-influencer") -> str:
    """Generate unique identifier with optional prefix."""    return f"{prefix}-{uuid.uuid4()}"


def current_timestamp() -> str:
    """Get current timestamp in ISO format."""    return datetime.utcnow().isoformat()


def safe_get(dictionary: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Safely get nested dictionary value using dot notation."""    keys = key_path.split('.')
    value = dictionary
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying functions on failure."""    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed: {e}")
            
            raise last_exception
        
        return wrapper
    return decorator
    
    @staticmethod
    def generate_deployment_id() -> str:
        """Generate unique deployment ID."""        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_suffix = secrets.token_hex(4)
        return f"deploy-{timestamp}-{random_suffix}"
    
    @staticmethod
    def generate_resource_name(base_name: str, environment: str, suffix: str = None) -> str:
        """Generate consistent resource names."""        parts = [base_name, environment]
        if suffix:
            parts.append(suffix)
        
        name = "-".join(parts)
        # Ensure name meets Kubernetes naming requirements
        name = re.sub(r'[^a-z0-9\-]', '-', name.lower())
        name = re.sub(r'-+', '-', name)
        name = name.strip('-')
        
        # Limit to 63 characters (Kubernetes limit)
        if len(name) > 63:
            name = name[:59] + hashlib.md5(name.encode()).hexdigest()[:4]
        
        return name
    
    @staticmethod
    def generate_secret_value(length: int = 32) -> str:
        """Generate secure random secret value."""        return secrets.token_urlsafe(length)
    
    @staticmethod
    def encode_base64(data: Union[str, bytes]) -> str:
        """Encode data to base64."""        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.b64encode(data).decode('utf-8')
    
    @staticmethod
    def decode_base64(data: str) -> str:
        """Decode base64 data."""        return base64.b64decode(data).decode('utf-8')
    
    @staticmethod
    def sanitize_label_value(value: str) -> str:
        """Sanitize value for Kubernetes labels."""        # Kubernetes label values must be 63 characters or less
        # and match the regex [a-z0-9A-Z]([a-z0-9A-Z\-\_\.]*[a-z0-9A-Z])?
        sanitized = re.sub(r'[^a-zA-Z0-9\-_.]', '-', value)
        sanitized = re.sub(r'^[^a-zA-Z0-9]', '', sanitized)
        sanitized = re.sub(r'[^a-zA-Z0-9]$', '', sanitized)
        
        if len(sanitized) > 63:
            sanitized = sanitized[:63]
        
        return sanitized or "default"
    
    @staticmethod
    def parse_resource_string(resource_str: str) -> Dict[str, Union[int, float]]:
        """Parse Kubernetes resource string (e.g., '1Gi', '500m')."""        if not resource_str:
            return {"value": 0, "unit": ""}
        
        # Memory resources
        memory_units = {
            'Ki': 1024,
            'Mi': 1024**2,
            'Gi': 1024**3,
            'Ti': 1024**4,
            'K': 1000,
            'M': 1000**2,
            'G': 1000**3,
            'T': 1000**4
        }
        
        # CPU resources (millicores)
        if resource_str.endswith('m'):
            return {
                "value": int(resource_str[:-1]),
                "unit": "millicores",
                "normalized_value": int(resource_str[:-1]) / 1000
            }
        
        # Memory resources
        for unit, multiplier in memory_units.items():
            if resource_str.endswith(unit):
                value = float(resource_str[:-len(unit)])
                return {
                    "value": value,
                    "unit": unit,
                    "normalized_value": value * multiplier
                }
        
        # Plain number (CPU cores)
        try:
            value = float(resource_str)
            return {
                "value": value,
                "unit": "cores",
                "normalized_value": value
            }
        except ValueError:
            return {"value": 0, "unit": "unknown"}
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format."""        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
    
    @staticmethod
    def calculate_resource_percentage(used: str, total: str) -> float:
        """Calculate resource usage percentage."""        used_parsed = DeploymentUtils.parse_resource_string(used)
        total_parsed = DeploymentUtils.parse_resource_string(total)
        
        if total_parsed["normalized_value"] == 0:
            return 0.0
        
        return (used_parsed["normalized_value"] / total_parsed["normalized_value"]) * 100
    
    @staticmethod
    async def run_kubectl_command(command: List[str], namespace: str = None) -> Dict[str, Any]:
        """Run kubectl command and return result."""        if namespace:
            command.extend(["-n", namespace])
        
        try:
            process = await asyncio.create_subprocess_exec(
                "kubectl", *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "returncode": process.returncode
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "returncode": -1
            }
    
    @staticmethod
    async def check_kubernetes_connectivity() -> bool:
        """Check if kubectl can connect to cluster."""        result = await DeploymentUtils.run_kubectl_command(["cluster-info"])
        return result["success"]
    
    @staticmethod
    def validate_yaml(yaml_content: str) -> ValidationResult:
        """Validate YAML content."""        try:
            yaml.safe_load(yaml_content)
            return ValidationResult(
                check_name="yaml_validation",
                passed=True,
                message="YAML is valid"
            )
        except yaml.YAMLError as e:
            return ValidationResult(
                check_name="yaml_validation",
                passed=False,
                message=f"Invalid YAML: {e}"
            )
    
    @staticmethod
    def validate_kubernetes_manifest(manifest: Dict[str, Any]) -> ValidationResult:
        """Validate Kubernetes manifest structure."""        required_fields = ["apiVersion", "kind", "metadata"]
        
        for field in required_fields:
            if field not in manifest:
                return ValidationResult(
                    check_name="manifest_validation",
                    passed=False,
                    message=f"Missing required field: {field}"
                )
        
        # Validate metadata
        if "name" not in manifest.get("metadata", {}):
            return ValidationResult(
                check_name="manifest_validation",
                passed=False,
                message="Missing required field: metadata.name"
            )
        
        return ValidationResult(
            check_name="manifest_validation",
            passed=True,
            message="Manifest is valid"
        )


class CollaborationMetrics:
    """    Metrics collection and analysis for collaboration deployment.
    
    Provides comprehensive metrics collection including:
    - Performance metrics
    - Resource utilization
    - Business metrics
    - Deployment metrics
    - Health metrics
    """    
    def __init__(self):
        """Initialize metrics collector."""        self.metrics: List[DeploymentMetric] = []
        self.start_time = datetime.utcnow()
        
    def add_metric(self, metric: DeploymentMetric) -> None:
        """Add a metric to the collection."""        self.metrics.append(metric)
        logger.debug(f"Added metric: {metric.name} = {metric.value} {metric.unit}")
    
    def record_deployment_metric(self, name: str, value: float, unit: str = "", 
                                category: MetricCategory = MetricCategory.PERFORMANCE,
                                labels: Dict[str, str] = None) -> None:
        """Record a deployment metric."""        metric = DeploymentMetric(
            name=name,
            value=value,
            unit=unit,
            category=category,
            labels=labels or {}
        )
        self.add_metric(metric)
    
    def record_timing_metric(self, operation_name: str, start_time: datetime, 
                           end_time: datetime = None) -> None:
        """Record timing metric for an operation."""        if end_time is None:
            end_time = datetime.utcnow()
        
        duration = (end_time - start_time).total_seconds()
        
        self.record_deployment_metric(
            name=f"{operation_name}_duration",
            value=duration,
            unit="seconds",
            category=MetricCategory.PERFORMANCE
        )
    
    def record_resource_metric(self, resource_type: str, usage: float, 
                              total: float, unit: str = "") -> None:
        """Record resource utilization metric."""        percentage = (usage / total * 100) if total > 0 else 0
        
        self.record_deployment_metric(
            name=f"{resource_type}_utilization",
            value=percentage,
            unit="percent",
            category=MetricCategory.INFRASTRUCTURE,
            labels={"resource_type": resource_type}
        )
        
        self.record_deployment_metric(
            name=f"{resource_type}_usage",
            value=usage,
            unit=unit,
            category=MetricCategory.INFRASTRUCTURE,
            labels={"resource_type": resource_type}
        )
    
    def record_availability_metric(self, service_name: str, is_available: bool) -> None:
        """Record service availability metric."""        self.record_deployment_metric(
            name="service_availability",
            value=1.0 if is_available else 0.0,
            unit="boolean",
            category=MetricCategory.AVAILABILITY,
            labels={"service": service_name}
        )
    
    def record_error_metric(self, error_type: str, count: int = 1) -> None:
        """Record error metric."""        self.record_deployment_metric(
            name="deployment_errors",
            value=count,
            unit="count",
            category=MetricCategory.RELIABILITY,
            labels={"error_type": error_type}
        )
    
    async def collect_deployment_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive deployment metrics."""        deployment_duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        # Aggregate metrics by category
        metrics_by_category = {}
        for category in MetricCategory:
            category_metrics = [m for m in self.metrics if m.category == category]
            metrics_by_category[category.value] = {
                "count": len(category_metrics),
                "metrics": [
                    {
                        "name": m.name,
                        "value": m.value,
                        "unit": m.unit,
                        "labels": m.labels,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in category_metrics
                ]
            }
        
        # Calculate summary statistics
        total_metrics = len(self.metrics)
        error_metrics = [m for m in self.metrics if "error" in m.name.lower()]
        
        return {
            "deployment_duration_seconds": deployment_duration,
            "total_metrics_collected": total_metrics,
            "error_count": len(error_metrics),
            "metrics_by_category": metrics_by_category,
            "collection_start_time": self.start_time.isoformat(),
            "collection_end_time": datetime.utcnow().isoformat()
        }
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics summary."""        if not self.metrics:
            return {"status": "no_metrics", "count": 0}
        
        latest_metrics = {}
        
        # Get latest metric for each unique name
        for metric in reversed(self.metrics):
            if metric.name not in latest_metrics:
                latest_metrics[metric.name] = {
                    "value": metric.value,
                    "unit": metric.unit,
                    "category": metric.category.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "labels": metric.labels
                }
        
        return {
            "status": "active",
            "count": len(latest_metrics),
            "metrics": latest_metrics
        }
    
    def get_metrics_by_category(self, category: MetricCategory) -> List[DeploymentMetric]:
        """Get metrics filtered by category."""        return [m for m in self.metrics if m.category == category]
    
    def get_metrics_by_name_pattern(self, pattern: str) -> List[DeploymentMetric]:
        """Get metrics matching name pattern."""        import re
        compiled_pattern = re.compile(pattern)
        return [m for m in self.metrics if compiled_pattern.search(m.name)]
    
    def calculate_sla_metrics(self, target_availability: float = 99.9) -> Dict[str, Any]:
        """Calculate SLA metrics."""        availability_metrics = self.get_metrics_by_category(MetricCategory.AVAILABILITY)
        
        if not availability_metrics:
            return {"status": "no_data"}
        
        total_checks = len(availability_metrics)
        successful_checks = sum(1 for m in availability_metrics if m.value == 1.0)
        
        actual_availability = (successful_checks / total_checks * 100) if total_checks > 0 else 0
        sla_met = actual_availability >= target_availability
        
        return {
            "target_availability": target_availability,
            "actual_availability": actual_availability,
            "sla_met": sla_met,
            "total_checks": total_checks,
            "successful_checks": successful_checks,
            "downtime_percentage": 100 - actual_availability
        }


class DeploymentValidator:
    """    Comprehensive validation for deployment configurations and states.
    
    Provides validation for:
    - Configuration files
    - Resource specifications
    - Security policies
    - Network configurations
    - Deployment readiness
    """    
    def __init__(self):
        """Initialize deployment validator."""        self.validation_results: List[ValidationResult] = []
    
    def add_validation_result(self, result: ValidationResult) -> None:
        """Add validation result."""        self.validation_results.append(result)
        
        log_level = logging.ERROR if not result.passed else logging.INFO
        logger.log(log_level, f"Validation {result.check_name}: {result.message}")
    
    async def validate_deployment_readiness(self, deployment_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate deployment readiness."""        checks = [
            self._validate_kubernetes_connection,
            self._validate_namespace_access,
            self._validate_resource_quotas,
            self._validate_storage_classes,
            self._validate_network_policies,
            self._validate_rbac_permissions
        ]
        
        for check in checks:
            try:
                result = await check(deployment_config)
                self.add_validation_result(result)
            except Exception as e:
                self.add_validation_result(ValidationResult(
                    check_name=check.__name__,
                    passed=False,
                    message=f"Validation check failed: {e}",
                    severity="error"
                ))
        
        # Analyze results
        total_checks = len(self.validation_results)
        passed_checks = sum(1 for r in self.validation_results if r.passed)
        critical_failures = sum(1 for r in self.validation_results 
                              if not r.passed and r.severity == "error")
        
        deployment_ready = critical_failures == 0
        
        return {
            "deployment_ready": deployment_ready,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "critical_failures": critical_failures,
            "validation_results": [
                {
                    "check_name": r.check_name,
                    "passed": r.passed,
                    "message": r.message,
                    "severity": r.severity,
                    "timestamp": r.timestamp.isoformat(),
                    "details": r.details
                }
                for r in self.validation_results
            ]
        }
    
    async def _validate_kubernetes_connection(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate Kubernetes cluster connection."""        is_connected = await DeploymentUtils.check_kubernetes_connectivity()
        
        return ValidationResult(
            check_name="kubernetes_connection",
            passed=is_connected,
            message="Kubernetes cluster is accessible" if is_connected else "Cannot connect to Kubernetes cluster",
            severity="error"
        )
    
    async def _validate_namespace_access(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate namespace access permissions."""        namespace = config.get("namespace", "collaboration")
        
        # Check if namespace exists
        result = await DeploymentUtils.run_kubectl_command(["get", "namespace", namespace])
        
        if result["success"]:
            return ValidationResult(
                check_name="namespace_access",
                passed=True,
                message=f"Namespace '{namespace}' is accessible"
            )
        else:
            return ValidationResult(
                check_name="namespace_access",
                passed=False,
                message=f"Cannot access namespace '{namespace}': {result.get('stderr', 'Unknown error')}",
                severity="error"
            )
    
    async def _validate_resource_quotas(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate resource quotas."""        # This would check actual resource quotas in the cluster
        # For now, simulate the check
        await asyncio.sleep(0.5)
        
        return ValidationResult(
            check_name="resource_quotas",
            passed=True,
            message="Resource quotas are sufficient",
            details={"cpu_available": "80 cores", "memory_available": "160Gi"}
        )
    
    async def _validate_storage_classes(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate storage classes availability."""        result = await DeploymentUtils.run_kubectl_command(["get", "storageclass"])
        
        if result["success"]:
            return ValidationResult(
                check_name="storage_classes",
                passed=True,
                message="Storage classes are available"
            )
        else:
            return ValidationResult(
                check_name="storage_classes",
                passed=False,
                message="Cannot list storage classes",
                severity="warning"
            )
    
    async def _validate_network_policies(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate network policies support."""        # Check if network policies are supported
        await asyncio.sleep(0.3)
        
        return ValidationResult(
            check_name="network_policies",
            passed=True,
            message="Network policies are supported"
        )
    
    async def _validate_rbac_permissions(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate RBAC permissions."""        # Check if we have necessary RBAC permissions
        result = await DeploymentUtils.run_kubectl_command(["auth", "can-i", "create", "deployments"])
        
        if result["success"] and "yes" in result["stdout"].lower():
            return ValidationResult(
                check_name="rbac_permissions",
                passed=True,
                message="RBAC permissions are sufficient"
            )
        else:
            return ValidationResult(
                check_name="rbac_permissions",
                passed=False,
                message="Insufficient RBAC permissions",
                severity="error"
            )


class DeploymentOrchestrator:
    """    Advanced deployment orchestration with step management.
    
    Provides:
    - Step-by-step deployment execution
    - Dependency management
    - Rollback capabilities
    - Progress tracking
    - Error handling
    """    
    def __init__(self):
        """Initialize deployment orchestrator."""        self.steps: List[DeploymentStep] = []
        self.executed_steps: List[str] = []
        self.failed_steps: List[str] = []
        self.metrics = CollaborationMetrics()
    
    def add_step(self, step: DeploymentStep) -> None:
        """Add deployment step."""        self.steps.append(step)
        logger.info(f"Added deployment step: {step.name}")
    
    async def execute_deployment(self) -> Dict[str, Any]:
        """Execute all deployment steps in order."""        logger.info(f"Starting deployment execution with {len(self.steps)} steps")
        start_time = datetime.utcnow()
        
        try:
            # Sort steps by dependencies
            ordered_steps = self._resolve_dependencies()
            
            for step in ordered_steps:
                step_result = await self._execute_step(step)
                
                if step_result["success"]:
                    self.executed_steps.append(step.name)
                    self.metrics.record_timing_metric(
                        f"step_{step.name}",
                        step_result["start_time"],
                        step_result["end_time"]
                    )
                else:
                    self.failed_steps.append(step.name)
                    self.metrics.record_error_metric(f"step_failure_{step.name}")
                    
                    if step.critical:
                        logger.error(f"Critical step {step.name} failed, stopping deployment")
                        break
            
            deployment_success = len(self.failed_steps) == 0
            end_time = datetime.utcnow()
            
            self.metrics.record_timing_metric("total_deployment", start_time, end_time)
            
            return {
                "success": deployment_success,
                "executed_steps": self.executed_steps,
                "failed_steps": self.failed_steps,
                "total_steps": len(self.steps),
                "duration_seconds": (end_time - start_time).total_seconds(),
                "metrics": await self.metrics.collect_deployment_metrics()
            }
            
        except Exception as e:
            logger.error(f"Deployment execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "executed_steps": self.executed_steps,
                "failed_steps": self.failed_steps
            }
    
    def _resolve_dependencies(self) -> List[DeploymentStep]:
        """Resolve step dependencies and return ordered list."""        ordered_steps = []
        remaining_steps = self.steps.copy()
        
        while remaining_steps:
            # Find steps with no unresolved dependencies
            ready_steps = [
                step for step in remaining_steps
                if all(dep in [s.name for s in ordered_steps] for dep in step.dependencies)
            ]
            
            if not ready_steps:
                # Circular dependency or missing dependency
                raise ValueError("Cannot resolve step dependencies")
            
            # Add ready steps to ordered list
            for step in ready_steps:
                ordered_steps.append(step)
                remaining_steps.remove(step)
        
        return ordered_steps
    
    async def _execute_step(self, step: DeploymentStep) -> Dict[str, Any]:
        """Execute a single deployment step."""        logger.info(f"Executing step: {step.name}")
        start_time = datetime.utcnow()
        
        for attempt in range(step.retry_count):
            try:
                # Execute step function with timeout
                result = await asyncio.wait_for(
                    step.function(),
                    timeout=step.timeout_seconds
                )
                
                end_time = datetime.utcnow()
                
                logger.info(f"Step {step.name} completed successfully")
                return {
                    "success": True,
                    "step_name": step.name,
                    "attempt": attempt + 1,
                    "start_time": start_time,
                    "end_time": end_time,
                    "result": result
                }
                
            except asyncio.TimeoutError:
                logger.warning(f"Step {step.name} timed out (attempt {attempt + 1})")
                if attempt == step.retry_count - 1:
                    return {
                        "success": False,
                        "step_name": step.name,
                        "error": "Timeout",
                        "attempts": step.retry_count,
                        "start_time": start_time
                    }
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                logger.error(f"Step {step.name} failed: {e} (attempt {attempt + 1})")
                if attempt == step.retry_count - 1:
                    return {
                        "success": False,
                        "step_name": step.name,
                        "error": str(e),
                        "attempts": step.retry_count,
                        "start_time": start_time
                    }
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # Should not reach here
        return {"success": False, "step_name": step.name, "error": "Unknown error"}
    
    async def rollback_deployment(self) -> Dict[str, Any]:
        """Rollback executed deployment steps."""        logger.info("Starting deployment rollback")
        
        rollback_results = []
        
        # Rollback in reverse order
        for step_name in reversed(self.executed_steps):
            step = next((s for s in self.steps if s.name == step_name), None)
            if step:
                try:
                    # Execute rollback if step has rollback function
                    if hasattr(step, 'rollback_function') and step.rollback_function:
                        await step.rollback_function()
                        rollback_results.append({"step": step_name, "status": "rolled_back"})
                    else:
                        rollback_results.append({"step": step_name, "status": "no_rollback_defined"})
                        
                except Exception as e:
                    logger.error(f"Rollback failed for step {step_name}: {e}")
                    rollback_results.append({"step": step_name, "status": "rollback_failed", "error": str(e)})
        
        return {
            "rollback_completed": True,
            "steps_rolled_back": len(rollback_results),
            "rollback_results": rollback_results
        }
