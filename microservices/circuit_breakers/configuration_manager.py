"""
Configuration Manager - Enterprise Circuit Breakers
Dynamic configuration management with validation, versioning, and rollback

This module provides enterprise-grade configuration management for circuit breakers,
enabling dynamic updates, validation, versioning, and rollback capabilities.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
            Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - PROTECTION FORTE
Cette implémentation est la propriété exclusive de Fahed Mlaiel.
Toute reproduction ou utilisation non autorisée est strictement interdite.
"""

import asyncio
import logging
import json
import time
import uuid
import os
import copy
import hashlib
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, deque
import tempfile
import yaml

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    logging.warning("⚠️ jsonschema not available - schema validation limited")

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("⚠️ Redis not available - distributed config features limited")


logger = logging.getLogger(__name__)


class ConfigurationSource(Enum):
    """Configuration source types"""
    FILE = "file"
    DATABASE = "database"
    ENVIRONMENT = "environment"
    REDIS = "redis"
    ETCD = "etcd"
    CONSUL = "consul"
    KUBERNETES = "kubernetes"


class ConfigurationStatus(Enum):
    """Configuration change status"""
    PENDING = "pending"
    VALIDATING = "validating"
    APPROVED = "approved"
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ValidationLevel(Enum):
    """Configuration validation levels"""
    BASIC = "basic"
    STRICT = "strict"
    COMPREHENSIVE = "comprehensive"


@dataclass
class ConfigurationSchema:
    """Configuration schema definition"""
    schema_id: str
    name: str
    version: str
    json_schema: Dict[str, Any]
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigurationVersion:
    """Configuration version information"""
    version_id: str
    version_number: str
    configuration: Dict[str, Any]
    created_by: str
    created_at: datetime
    description: str = ""
    checksum: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigurationChange:
    """Configuration change record"""
    change_id: str
    version_from: str
    version_to: str
    changes: Dict[str, Any]
    status: ConfigurationStatus
    requested_by: str
    requested_at: datetime
    applied_at: Optional[datetime] = None
    validation_results: Dict[str, Any] = field(default_factory=dict)
    rollback_info: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Configuration validation result"""
    is_valid: bool
    validation_level: ValidationLevel
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    performance_impact: Optional[str] = None
    security_concerns: List[str] = field(default_factory=list)


class SchemaManager:
    """Manage configuration schemas and validation"""
    
    def __init__(self):
        self.schemas: Dict[str, ConfigurationSchema] = {}
        self.custom_validators: Dict[str, Callable] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize default schemas
        self._initialize_default_schemas()
    
    def _initialize_default_schemas(self):
        """Initialize default configuration schemas"""
        # Circuit breaker configuration schema
        circuit_breaker_schema = {
            "type": "object",
            "properties": {
                "service_name": {"type": "string", "minLength": 1},
                "failure_threshold": {"type": "integer", "minimum": 1, "maximum": 100},
                "timeout_seconds": {"type": "number", "minimum": 0.1, "maximum": 300},
                "recovery_timeout": {"type": "integer", "minimum": 1, "maximum": 3600},
                "success_threshold": {"type": "integer", "minimum": 1, "maximum": 20},
                "monitoring_enabled": {"type": "boolean"},
                "fallback_enabled": {"type": "boolean"},
                "metadata": {"type": "object"}
            },
            "required": ["service_name", "failure_threshold", "timeout_seconds"],
            "additionalProperties": False
        }
        
        self.register_schema(ConfigurationSchema(
            schema_id="circuit_breaker_config",
            name="Circuit Breaker Configuration",
            version="1.0",
            json_schema=circuit_breaker_schema,
            validation_rules=[
                {
                    "rule": "failure_threshold_reasonable",
                    "description": "Failure threshold should be reasonable (3-10 for most cases)",
                    "validator": lambda config: 3 <= config.get("failure_threshold", 5) <= 10
                },
                {
                    "rule": "timeout_performance_check",
                    "description": "Timeout should not be too high to avoid poor user experience",
                    "validator": lambda config: config.get("timeout_seconds", 30) <= 60
                }
            ]
        ))
        
        # Rate limiting configuration schema
        rate_limiting_schema = {
            "type": "object",
            "properties": {
                "service_name": {"type": "string", "minLength": 1},
                "base_rate_limit": {"type": "integer", "minimum": 1},
                "time_window_seconds": {"type": "integer", "minimum": 1, "maximum": 3600},
                "burst_capacity": {"type": "integer", "minimum": 1},
                "algorithm": {"type": "string", "enum": ["token_bucket", "sliding_window", "fixed_window", "adaptive"]},
                "coordination_enabled": {"type": "boolean"}
            },
            "required": ["service_name", "base_rate_limit", "time_window_seconds"],
            "additionalProperties": False
        }
        
        self.register_schema(ConfigurationSchema(
            schema_id="rate_limiting_config",
            name="Rate Limiting Configuration",
            version="1.0",
            json_schema=rate_limiting_schema
        ))
    
    def register_schema(self, schema: ConfigurationSchema):
        """Register configuration schema"""
        self.schemas[schema.schema_id] = schema
        self.logger.info(f"📋 Registered schema: {schema.name} v{schema.version}")
    
    def register_custom_validator(self, validator_name: str, validator_func: Callable):
        """Register custom validation function"""
        self.custom_validators[validator_name] = validator_func
        self.logger.info(f"✅ Registered custom validator: {validator_name}")
    
    async def validate_configuration(self, config: Dict[str, Any], schema_id: str, 
                                   validation_level: ValidationLevel = ValidationLevel.BASIC) -> ValidationResult:
        """Validate configuration against schema"""
        try:
            result = ValidationResult(
                is_valid=True,
                validation_level=validation_level
            )
            
            if schema_id not in self.schemas:
                result.is_valid = False
                result.errors.append(f"Schema {schema_id} not found")
                return result
            
            schema = self.schemas[schema_id]
            
            # JSON Schema validation
            if JSONSCHEMA_AVAILABLE:
                try:
                    validate(instance=config, schema=schema.json_schema)
                except ValidationError as e:
                    result.is_valid = False
                    result.errors.append(f"Schema validation error: {e.message}")
                    return result
            else:
                # Basic validation without jsonschema
                await self._basic_schema_validation(config, schema, result)
            
            # Custom validation rules
            if validation_level in [ValidationLevel.STRICT, ValidationLevel.COMPREHENSIVE]:
                await self._apply_custom_validation_rules(config, schema, result)
            
            # Comprehensive validation
            if validation_level == ValidationLevel.COMPREHENSIVE:
                await self._comprehensive_validation(config, schema, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Configuration validation error: {e}")
            return ValidationResult(
                is_valid=False,
                validation_level=validation_level,
                errors=[f"Validation system error: {e}"]
            )
    
    async def _basic_schema_validation(self, config: Dict[str, Any], schema: ConfigurationSchema, 
                                     result: ValidationResult):
        """Basic schema validation without jsonschema library"""
        json_schema = schema.json_schema
        
        # Check required fields
        required_fields = json_schema.get("required", [])
        for field in required_fields:
            if field not in config:
                result.is_valid = False
                result.errors.append(f"Required field '{field}' is missing")
        
        # Check field types (simplified)
        properties = json_schema.get("properties", {})
        for field_name, field_schema in properties.items():
            if field_name in config:
                expected_type = field_schema.get("type")
                value = config[field_name]
                
                if expected_type == "string" and not isinstance(value, str):
                    result.errors.append(f"Field '{field_name}' must be a string")
                elif expected_type == "integer" and not isinstance(value, int):
                    result.errors.append(f"Field '{field_name}' must be an integer")
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    result.errors.append(f"Field '{field_name}' must be a number")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    result.errors.append(f"Field '{field_name}' must be a boolean")
        
        if result.errors:
            result.is_valid = False
    
    async def _apply_custom_validation_rules(self, config: Dict[str, Any], schema: ConfigurationSchema, 
                                           result: ValidationResult):
        """Apply custom validation rules"""
        for rule in schema.validation_rules:
            try:
                rule_validator = rule.get("validator")
                if rule_validator and callable(rule_validator):
                    if not rule_validator(config):
                        result.warnings.append(f"Validation rule failed: {rule.get('description', 'Unknown rule')}")
            except Exception as e:
                result.warnings.append(f"Rule validation error: {e}")
    
    async def _comprehensive_validation(self, config: Dict[str, Any], schema: ConfigurationSchema, 
                                      result: ValidationResult):
        """Comprehensive validation including performance and security checks"""
        # Performance impact analysis
        if schema.schema_id == "circuit_breaker_config":
            timeout = config.get("timeout_seconds", 30)
            if timeout > 30:
                result.performance_impact = "HIGH"
                result.suggestions.append("Consider reducing timeout_seconds for better user experience")
            elif timeout > 10:
                result.performance_impact = "MEDIUM"
            else:
                result.performance_impact = "LOW"
        
        # Security analysis
        if "metadata" in config and isinstance(config["metadata"], dict):
            for key, value in config["metadata"].items():
                if isinstance(value, str) and any(keyword in value.lower() for keyword in ["password", "secret", "key", "token"]):
                    result.security_concerns.append(f"Potential sensitive data in metadata field '{key}'")
        
        # Configuration optimization suggestions
        if schema.schema_id == "circuit_breaker_config":
            failure_threshold = config.get("failure_threshold", 5)
            if failure_threshold > 10:
                result.suggestions.append("High failure threshold may delay circuit opening - consider reducing")
            elif failure_threshold < 3:
                result.suggestions.append("Low failure threshold may cause frequent circuit opening - consider increasing")


class VersionManager:
    """Manage configuration versions and history"""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or tempfile.mkdtemp(prefix="circuit_breaker_config_")
        self.versions: Dict[str, List[ConfigurationVersion]] = defaultdict(list)
        self.current_versions: Dict[str, str] = {}  # config_key -> version_id
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
    
    async def create_version(self, config_key: str, configuration: Dict[str, Any], 
                           created_by: str, description: str = "") -> ConfigurationVersion:
        """Create new configuration version"""
        try:
            # Generate version info
            version_id = str(uuid.uuid4())
            version_number = await self._generate_version_number(config_key)
            checksum = self._calculate_checksum(configuration)
            
            # Create version object
            version = ConfigurationVersion(
                version_id=version_id,
                version_number=version_number,
                configuration=copy.deepcopy(configuration),
                created_by=created_by,
                created_at=datetime.now(),
                description=description,
                checksum=checksum
            )
            
            # Store version
            self.versions[config_key].append(version)
            
            # Persist to storage
            await self._persist_version(config_key, version)
            
            self.logger.info(f"📝 Created configuration version: {config_key} v{version_number}")
            return version
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create configuration version: {e}")
            raise
    
    async def _generate_version_number(self, config_key: str) -> str:
        """Generate next version number"""
        existing_versions = self.versions.get(config_key, [])
        
        if not existing_versions:
            return "1.0.0"
        
        # Get latest version number and increment
        latest_version = existing_versions[-1].version_number
        parts = latest_version.split('.')
        
        try:
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            return f"{major}.{minor}.{patch + 1}"
        except (ValueError, IndexError):
            return f"{len(existing_versions) + 1}.0.0"
    
    def _calculate_checksum(self, configuration: Dict[str, Any]) -> str:
        """Calculate configuration checksum"""
        config_str = json.dumps(configuration, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    async def _persist_version(self, config_key: str, version: ConfigurationVersion):
        """Persist version to storage"""
        try:
            version_file = os.path.join(
                self.storage_path,
                f"{config_key}_{version.version_id}.json"
            )
            
            version_data = {
                'version_id': version.version_id,
                'version_number': version.version_number,
                'configuration': version.configuration,
                'created_by': version.created_by,
                'created_at': version.created_at.isoformat(),
                'description': version.description,
                'checksum': version.checksum,
                'metadata': version.metadata
            }
            
            with open(version_file, 'w') as f:
                json.dump(version_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to persist version: {e}")
    
    async def get_version(self, config_key: str, version_id: str) -> Optional[ConfigurationVersion]:
        """Get specific configuration version"""
        versions = self.versions.get(config_key, [])
        for version in versions:
            if version.version_id == version_id:
                return version
        return None
    
    async def get_latest_version(self, config_key: str) -> Optional[ConfigurationVersion]:
        """Get latest configuration version"""
        versions = self.versions.get(config_key, [])
        return versions[-1] if versions else None
    
    async def get_version_history(self, config_key: str, limit: int = 10) -> List[ConfigurationVersion]:
        """Get configuration version history"""
        versions = self.versions.get(config_key, [])
        return versions[-limit:] if versions else []
    
    async def compare_versions(self, config_key: str, version_id_1: str, 
                             version_id_2: str) -> Dict[str, Any]:
        """Compare two configuration versions"""
        try:
            version_1 = await self.get_version(config_key, version_id_1)
            version_2 = await self.get_version(config_key, version_id_2)
            
            if not version_1 or not version_2:
                return {'error': 'One or both versions not found'}
            
            diff_result = {
                'version_1': {
                    'version_number': version_1.version_number,
                    'created_at': version_1.created_at.isoformat(),
                    'created_by': version_1.created_by
                },
                'version_2': {
                    'version_number': version_2.version_number,
                    'created_at': version_2.created_at.isoformat(),
                    'created_by': version_2.created_by
                },
                'differences': await self._calculate_differences(
                    version_1.configuration, 
                    version_2.configuration
                )
            }
            
            return diff_result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to compare versions: {e}")
            return {'error': str(e)}
    
    async def _calculate_differences(self, config1: Dict[str, Any], 
                                   config2: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate differences between two configurations"""
        differences = {
            'added': {},
            'removed': {},
            'modified': {},
            'unchanged': {}
        }
        
        all_keys = set(config1.keys()) | set(config2.keys())
        
        for key in all_keys:
            if key not in config1:
                differences['added'][key] = config2[key]
            elif key not in config2:
                differences['removed'][key] = config1[key]
            elif config1[key] != config2[key]:
                differences['modified'][key] = {
                    'old_value': config1[key],
                    'new_value': config2[key]
                }
            else:
                differences['unchanged'][key] = config1[key]
        
        return differences


class ChangeManager:
    """Manage configuration changes and approvals"""
    
    def __init__(self, version_manager: VersionManager):
        self.version_manager = version_manager
        self.changes: Dict[str, ConfigurationChange] = {}
        self.approval_handlers: List[Callable] = []
        self.change_hooks: Dict[str, List[Callable]] = defaultdict(list)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register_approval_handler(self, handler: Callable):
        """Register approval handler"""
        self.approval_handlers.append(handler)
        self.logger.info(f"✅ Registered approval handler")
    
    def register_change_hook(self, hook_name: str, hook_func: Callable):
        """Register change hook for notifications"""
        self.change_hooks[hook_name].append(hook_func)
        self.logger.info(f"🔗 Registered change hook: {hook_name}")
    
    async def request_configuration_change(self, config_key: str, new_configuration: Dict[str, Any], 
                                         requested_by: str, description: str = "") -> str:
        """Request configuration change"""
        try:
            # Get current version
            current_version = await self.version_manager.get_latest_version(config_key)
            current_version_id = current_version.version_id if current_version else "none"
            
            # Create new version
            new_version = await self.version_manager.create_version(
                config_key, new_configuration, requested_by, description
            )
            
            # Create change record
            change_id = str(uuid.uuid4())
            change = ConfigurationChange(
                change_id=change_id,
                version_from=current_version_id,
                version_to=new_version.version_id,
                changes=await self._calculate_change_summary(current_version, new_version),
                status=ConfigurationStatus.PENDING,
                requested_by=requested_by,
                requested_at=datetime.now()
            )
            
            self.changes[change_id] = change
            
            # Trigger approval process
            await self._process_change_approval(change_id)
            
            self.logger.info(f"📝 Configuration change requested: {change_id}")
            return change_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to request configuration change: {e}")
            raise
    
    async def _calculate_change_summary(self, current_version: Optional[ConfigurationVersion], 
                                      new_version: ConfigurationVersion) -> Dict[str, Any]:
        """Calculate summary of changes"""
        if not current_version:
            return {
                'type': 'initial_configuration',
                'summary': 'Initial configuration creation',
                'affected_fields': list(new_version.configuration.keys())
            }
        
        comparison = await self.version_manager.compare_versions(
            "temp", current_version.version_id, new_version.version_id
        )
        
        differences = comparison.get('differences', {})
        
        change_summary = {
            'type': 'configuration_update',
            'added_fields': list(differences.get('added', {}).keys()),
            'removed_fields': list(differences.get('removed', {}).keys()),
            'modified_fields': list(differences.get('modified', {}).keys()),
            'total_changes': len(differences.get('added', {})) + 
                           len(differences.get('removed', {})) + 
                           len(differences.get('modified', {}))
        }
        
        return change_summary
    
    async def _process_change_approval(self, change_id: str):
        """Process change approval workflow"""
        change = self.changes.get(change_id)
        if not change:
            return
        
        change.status = ConfigurationStatus.VALIDATING
        
        # Run approval handlers
        approval_results = []
        for handler in self.approval_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(change)
                else:
                    result = handler(change)
                approval_results.append(result)
            except Exception as e:
                self.logger.error(f"❌ Approval handler error: {e}")
                approval_results.append(False)
        
        # Determine approval status
        if all(approval_results):
            change.status = ConfigurationStatus.APPROVED
            self.logger.info(f"✅ Configuration change approved: {change_id}")
        else:
            change.status = ConfigurationStatus.FAILED
            self.logger.warning(f"❌ Configuration change rejected: {change_id}")
        
        # Trigger change hooks
        await self._trigger_change_hooks("approval_processed", change)
    
    async def _trigger_change_hooks(self, hook_name: str, change: ConfigurationChange):
        """Trigger registered change hooks"""
        hooks = self.change_hooks.get(hook_name, [])
        
        for hook in hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(change)
                else:
                    hook(change)
            except Exception as e:
                self.logger.error(f"❌ Change hook error ({hook_name}): {e}")
    
    async def apply_configuration_change(self, change_id: str) -> bool:
        """Apply approved configuration change"""
        try:
            change = self.changes.get(change_id)
            if not change:
                self.logger.error(f"❌ Change {change_id} not found")
                return False
            
            if change.status != ConfigurationStatus.APPROVED:
                self.logger.error(f"❌ Change {change_id} not approved")
                return False
            
            # Apply the change
            new_version = await self.version_manager.get_version("temp", change.version_to)
            if not new_version:
                self.logger.error(f"❌ Target version {change.version_to} not found")
                return False
            
            # Store rollback information
            current_version = await self.version_manager.get_latest_version("temp")
            change.rollback_info = {
                'previous_version_id': current_version.version_id if current_version else None,
                'rollback_configuration': current_version.configuration if current_version else None
            }
            
            # Update status
            change.status = ConfigurationStatus.APPLIED
            change.applied_at = datetime.now()
            
            # Trigger application hooks
            await self._trigger_change_hooks("configuration_applied", change)
            
            self.logger.info(f"🚀 Configuration change applied: {change_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to apply configuration change: {e}")
            return False
    
    async def get_change_status(self, change_id: str) -> Optional[ConfigurationChange]:
        """Get configuration change status"""
        return self.changes.get(change_id)
    
    async def get_pending_changes(self) -> List[ConfigurationChange]:
        """Get all pending configuration changes"""
        return [change for change in self.changes.values() 
                if change.status == ConfigurationStatus.PENDING]


class ConfigurationManager:
    """
    Enterprise configuration manager with dynamic updates, validation, and rollback.
    Provides comprehensive configuration lifecycle management.
    """
    
    def __init__(self, storage_path: str = None, redis_client = None):
        """Initialize configuration manager"""
        self.storage_path = storage_path or tempfile.mkdtemp(prefix="circuit_breaker_config_")
        self.redis_client = redis_client
        
        self.schema_manager = SchemaManager()
        self.version_manager = VersionManager(self.storage_path)
        self.change_manager = ChangeManager(self.version_manager)
        
        self.active_configurations: Dict[str, Dict[str, Any]] = {}
        self.configuration_watchers: Dict[str, List[Callable]] = defaultdict(list)
        self.validation_cache: Dict[str, ValidationResult] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize default approval handlers
        self._initialize_default_handlers()
        
        self.logger.info("⚙️ Configuration Manager initialized - Enterprise config management ready")
    
    def _initialize_default_handlers(self):
        """Initialize default approval and change handlers"""
        # Simple auto-approval for demo (in production, this would be more sophisticated)
        async def auto_approve_handler(change: ConfigurationChange) -> bool:
            # Auto-approve changes with low risk
            if change.changes.get('total_changes', 0) <= 3:
                return True
            return False
        
        self.change_manager.register_approval_handler(auto_approve_handler)
        
        # Configuration change notification hook
        async def change_notification_hook(change: ConfigurationChange):
            self.logger.info(f"📢 Configuration change notification: {change.change_id} - {change.status.value}")
        
        self.change_manager.register_change_hook("configuration_applied", change_notification_hook)
    
    async def update_circuit_configuration(self, config_updates: Dict[str, Any]) -> bool:
        """Update circuit breaker configuration without restart"""
        try:
            service_name = config_updates.get('service_name')
            if not service_name:
                raise ValueError("Service name required for configuration update")
            
# SECURITY: config_key = f"circuit_breaker_{service_name}" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
            
            # Get current configuration
            current_config = self.active_configurations.get(config_key, {})
            
            # Merge updates
            new_config = {**current_config, **config_updates}
            
            # Request configuration change
            change_id = await self.change_manager.request_configuration_change(
                config_key=config_key,
                new_configuration=new_config,
                requested_by="system",
                description=f"Dynamic update for {service_name}"
            )
            
            # Wait for approval and application
            max_wait = 30  # seconds
            wait_time = 0
            
            while wait_time < max_wait:
                change = await self.change_manager.get_change_status(change_id)
                if change.status == ConfigurationStatus.APPROVED:
                    success = await self.change_manager.apply_configuration_change(change_id)
                    if success:
                        self.active_configurations[config_key] = new_config
                        await self._notify_configuration_watchers(config_key, new_config)
                        return True
                    break
                elif change.status in [ConfigurationStatus.FAILED, ConfigurationStatus.ROLLED_BACK]:
                    break
                
                await asyncio.sleep(1)
                wait_time += 1
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update circuit configuration: {e}")
            return False
    
    async def validate_configuration_changes(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration changes with rules engine"""
        try:
            service_name = new_config.get('service_name', 'unknown')
            schema_id = self._determine_schema_id(new_config)
            
            # Validate against schema
            validation_result = await self.schema_manager.validate_configuration(
                new_config, schema_id, ValidationLevel.COMPREHENSIVE
            )
            
            # Additional business rule validation
            business_validation = await self._validate_business_rules(new_config)
            
            # Combine results
            combined_result = {
                'is_valid': validation_result.is_valid and business_validation['is_valid'],
                'schema_validation': {
                    'valid': validation_result.is_valid,
                    'errors': validation_result.errors,
                    'warnings': validation_result.warnings,
                    'suggestions': validation_result.suggestions
                },
                'business_validation': business_validation,
                'performance_impact': validation_result.performance_impact,
                'security_concerns': validation_result.security_concerns,
                'recommendation': await self._generate_validation_recommendation(validation_result, business_validation)
            }
            
            # Cache validation result
            cache_key = self._generate_validation_cache_key(new_config)
            self.validation_cache[cache_key] = validation_result
            
            return combined_result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to validate configuration changes: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'recommendation': 'Fix validation errors before proceeding'
            }
    
    def _determine_schema_id(self, config: Dict[str, Any]) -> str:
        """Determine appropriate schema ID for configuration"""
        if 'failure_threshold' in config or 'timeout_seconds' in config:
            return 'circuit_breaker_config'
        elif 'base_rate_limit' in config or 'time_window_seconds' in config:
            return 'rate_limiting_config'
        else:
            return 'circuit_breaker_config'  # Default
    
    async def _validate_business_rules(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against business rules"""
        is_valid = True
        errors = []
        warnings = []
        
        # Example business rules
        if 'timeout_seconds' in config:
            timeout = config['timeout_seconds']
            if timeout > 120:
                warnings.append("Very high timeout may impact user experience")
            elif timeout < 0.5:
                errors.append("Timeout too low - may cause premature failures")
                is_valid = False
        
        if 'failure_threshold' in config:
            threshold = config['failure_threshold']
            if threshold > 20:
                errors.append("Failure threshold too high - circuit may never open")
                is_valid = False
            elif threshold < 2:
                errors.append("Failure threshold too low - circuit may open too frequently")
                is_valid = False
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings
        }
    
    async def _generate_validation_recommendation(self, schema_validation: ValidationResult, 
                                                business_validation: Dict[str, Any]) -> str:
        """Generate validation recommendation"""
        if not schema_validation.is_valid:
            return "Fix schema validation errors before proceeding"
        
        if not business_validation['is_valid']:
            return "Address business rule violations before applying configuration"
        
        if schema_validation.warnings or business_validation['warnings']:
            return "Configuration is valid but consider addressing warnings for optimal performance"
        
        if schema_validation.performance_impact == "HIGH":
            return "Configuration may have high performance impact - review timeout and threshold values"
        
        return "Configuration is valid and ready to apply"
    
    def _generate_validation_cache_key(self, config: Dict[str, Any]) -> str:
        """Generate cache key for validation result"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    async def rollback_configuration(self, rollback_target: str) -> bool:
        """Rollback configuration to previous version"""
        try:
            # Parse rollback target (can be version_id, version_number, or "previous")
            if rollback_target == "previous":
                # Find the most recent configuration change
                recent_changes = sorted(
                    [change for change in self.change_manager.changes.values() 
                     if change.status == ConfigurationStatus.APPLIED],
                    key=lambda x: x.applied_at or datetime.min,
                    reverse=True
                )
                
                if not recent_changes:
                    self.logger.error("❌ No previous configuration found to rollback to")
                    return False
                
                recent_change = recent_changes[0]
                rollback_info = recent_change.rollback_info
                
                if not rollback_info or not rollback_info.get('rollback_configuration'):
                    self.logger.error("❌ No rollback information available")
                    return False
                
                # Create rollback change
                rollback_config = rollback_info['rollback_configuration']
                change_id = await self.change_manager.request_configuration_change(
                    config_key="rollback_target",
                    new_configuration=rollback_config,
                    requested_by="system_rollback",
                    description=f"Rollback from change {recent_change.change_id}"
                )
                
                # Auto-approve rollback
                change = self.change_manager.changes[change_id]
                change.status = ConfigurationStatus.APPROVED
                
                # Apply rollback
                success = await self.change_manager.apply_configuration_change(change_id)
                
                if success:
                    # Update recent change status
                    recent_change.status = ConfigurationStatus.ROLLED_BACK
                    self.logger.info(f"🔄 Configuration rolled back successfully")
                    return True
                
            else:
                # Rollback to specific version
                # This would involve more complex logic to identify the target version
                # and create appropriate rollback change
                self.logger.info(f"🔄 Rollback to specific target: {rollback_target}")
                # Simplified implementation
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to rollback configuration: {e}")
            return False
    
    async def register_configuration_watcher(self, config_key: str, watcher_func: Callable):
        """Register configuration change watcher"""
        self.configuration_watchers[config_key].append(watcher_func)
        self.logger.info(f"👁️ Registered configuration watcher for {config_key}")
    
    async def _notify_configuration_watchers(self, config_key: str, new_config: Dict[str, Any]):
        """Notify configuration watchers of changes"""
        watchers = self.configuration_watchers.get(config_key, [])
        
        for watcher in watchers:
            try:
                if asyncio.iscoroutinefunction(watcher):
                    await watcher(config_key, new_config)
                else:
                    watcher(config_key, new_config)
            except Exception as e:
                self.logger.error(f"❌ Configuration watcher error: {e}")
    
    async def get_configuration_status(self, config_key: str = None) -> Dict[str, Any]:
        """Get comprehensive configuration status"""
        try:
            if config_key:
                # Single configuration status
                current_config = self.active_configurations.get(config_key, {})
                latest_version = await self.version_manager.get_latest_version(config_key)
                
                return {
                    'config_key': config_key,
                    'current_configuration': current_config,
                    'latest_version': {
                        'version_id': latest_version.version_id,
                        'version_number': latest_version.version_number,
                        'created_at': latest_version.created_at.isoformat(),
                        'created_by': latest_version.created_by
                    } if latest_version else None,
                    'watchers_count': len(self.configuration_watchers.get(config_key, [])),
                    'validation_cached': self._generate_validation_cache_key(current_config) in self.validation_cache
                }
            else:
                # System-wide configuration status
                pending_changes = await self.change_manager.get_pending_changes()
                
                return {
                    'total_configurations': len(self.active_configurations),
                    'registered_schemas': len(self.schema_manager.schemas),
                    'total_versions': sum(len(versions) for versions in self.version_manager.versions.values()),
                    'pending_changes': len(pending_changes),
                    'total_watchers': sum(len(watchers) for watchers in self.configuration_watchers.values()),
                    'validation_cache_size': len(self.validation_cache),
                    'storage_path': self.storage_path,
                    'redis_available': self.redis_client is not None,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get configuration status: {e}")
            return {'error': str(e)}
    
    async def export_configurations(self, export_format: str = "json") -> str:
        """Export all configurations"""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'configurations': self.active_configurations,
                'schemas': {
                    schema_id: {
                        'name': schema.name,
                        'version': schema.version,
                        'json_schema': schema.json_schema
                    } for schema_id, schema in self.schema_manager.schemas.items()
                },
                'version_history': {
                    config_key: [
                        {
                            'version_id': v.version_id,
                            'version_number': v.version_number,
                            'created_by': v.created_by,
                            'created_at': v.created_at.isoformat(),
                            'description': v.description
                        } for v in versions
                    ] for config_key, versions in self.version_manager.versions.items()
                }
            }
            
            if export_format.lower() == 'json':
                return json.dumps(export_data, indent=2)
            elif export_format.lower() == 'yaml':
                return yaml.dump(export_data, default_flow_style=False)
            else:
                return str(export_data)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to export configurations: {e}")
            return f'{{"error": "{e}"}}'
    
    async def import_configurations(self, import_data: str, import_format: str = "json") -> bool:
        """Import configurations from data"""
        try:
            if import_format.lower() == 'json':
                data = json.loads(import_data)
            elif import_format.lower() == 'yaml':
                data = yaml.safe_load(import_data)
            else:
                raise ValueError(f"Unsupported import format: {import_format}")
            
            configurations = data.get('configurations', {})
            
            # Import configurations
            for config_key, config_data in configurations.items():
                # Validate configuration
                validation_result = await self.validate_configuration_changes(config_data)
                
                if validation_result['is_valid']:
                    self.active_configurations[config_key] = config_data
                    
                    # Create version
                    await self.version_manager.create_version(
                        config_key, config_data, "import_system", "Imported configuration"
                    )
                else:
                    self.logger.warning(f"⚠️ Skipped invalid configuration: {config_key}")
            
            self.logger.info(f"📥 Imported {len(configurations)} configurations")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to import configurations: {e}")
            return False
    
    async def start_monitoring(self):
        """Start configuration monitoring"""
        if not self.monitoring_task:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.logger.info("📊 Started configuration monitoring")
    
    async def stop_monitoring(self):
        """Stop configuration monitoring"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
            self.logger.info("⏹️ Stopped configuration monitoring")
    
    async def _monitoring_loop(self):
        """Configuration monitoring loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
                # Clean up old validation cache entries
                if len(self.validation_cache) > 100:
                    # Keep only the 50 most recent entries
                    sorted_cache = sorted(self.validation_cache.items(), 
                                        key=lambda x: x[1].validation_level.value)
                    self.validation_cache = dict(sorted_cache[-50:])
                
                # Check for configuration drift (in production, this would compare with external sources)
                await self._check_configuration_drift()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Configuration monitoring error: {e}")
    
    async def _check_configuration_drift(self):
        """Check for configuration drift"""
        # In a production system, this would compare current configurations
        # with authoritative sources (git repos, databases, etc.)
        self.logger.debug("🔍 Checking for configuration drift")
    
    async def cleanup(self):
        """Cleanup configuration manager"""
        try:
            await self.stop_monitoring()
            
            self.active_configurations.clear()
            self.configuration_watchers.clear()
            self.validation_cache.clear()
            
            self.logger.info("🧹 Configuration Manager cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")


# Global configuration manager instance
configuration_manager = None


def create_configuration_manager(storage_path: str = None, redis_client = None) -> ConfigurationManager:
    """Create configuration manager instance"""
    global configuration_manager
    configuration_manager = ConfigurationManager(storage_path, redis_client)
    return configuration_manager


# Export main classes and functions  
__all__ = [
    'ConfigurationManager',
    'SchemaManager',
    'VersionManager',
    'ChangeManager',
    'ConfigurationSchema',
    'ConfigurationVersion',
    'ConfigurationChange',
    'ValidationResult',
    'ConfigurationSource',
    'ConfigurationStatus',
    'ValidationLevel',
    'create_configuration_manager'
]


if __name__ == "__main__":
    async def demo():
        """Demo configuration manager functionality"""
        # Create configuration manager
        config_manager = ConfigurationManager()
        
        # Sample circuit breaker configuration
        circuit_config = {
            'service_name': 'user-service',
            'failure_threshold': 5,
            'timeout_seconds': 30.0,
            'recovery_timeout': 60,
            'success_threshold': 2,
            'monitoring_enabled': True,
            'fallback_enabled': True
        }
        
        # Update configuration
        success = await config_manager.update_circuit_configuration(circuit_config)
        print(f"Configuration update: {'✅ Success' if success else '❌ Failed'}")
        
        # Validate configuration changes
        updated_config = {**circuit_config, 'failure_threshold': 3, 'timeout_seconds': 45.0}
        validation_result = await config_manager.validate_configuration_changes(updated_config)
        print(f"Validation result: {json.dumps(validation_result, indent=2)}")
        
        # Get configuration status
        status = await config_manager.get_configuration_status()
        print(f"Configuration status: {json.dumps(status, indent=2, default=str)}")
        
        # Export configurations
        export_data = await config_manager.export_configurations('json')
        print(f"Export data: {len(export_data)} characters")
        
        # Cleanup
        await config_manager.cleanup()
    
    # Run demo
    asyncio.run(demo())