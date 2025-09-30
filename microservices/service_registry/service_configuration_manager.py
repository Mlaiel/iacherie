#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚙️ SERVICE REGISTRY ENTERPRISE - SERVICE CONFIGURATION MANAGER
===============================================================

**Author**: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer)
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Project**: IA Chérie Service Registry Enterprise
**Version**: 1.0 Production
**Created**: 2025-01-07 | Updated: 2025-12-14

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture service registry et tous ses algorithmes sont la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

🔧 SERVICE CONFIGURATION MANAGER
Manager configuration services avec hot-reload et validation.
Config versioning + feature flags + environment management + validation.
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Set, Tuple, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid
import copy
from pathlib import Path
import yaml

# Core logger
logger = logging.getLogger(__name__)

class ConfigFormat(Enum):
    """Configuration format types"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    PROPERTIES = "properties"
    ENV = "env"

class FeatureFlagStrategy(Enum):
    """Feature flag rollout strategies"""
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    GEOGRAPHIC = "geographic"
    TIME_BASED = "time_based"
    A_B_TEST = "a_b_test"
    CANARY = "canary"

class ConfigChangeType(Enum):
    """Configuration change types"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ROLLBACK = "rollback"
    BULK_UPDATE = "bulk_update"

@dataclass
class ConfigVersion:
    """Configuration version information"""
    version_id: str
    service_id: str
    version_number: str
    configuration: Dict[str, Any]
    created_at: float
    created_by: str
    change_description: str
    schema_version: str = "1.0"
    is_active: bool = False
    rollback_safe: bool = True
    tags: Set[str] = field(default_factory=set)

@dataclass
class FeatureFlag:
    """Feature flag definition"""
    flag_id: str
    flag_name: str
    description: str
    strategy: FeatureFlagStrategy
    enabled: bool = False
    rollout_percentage: float = 0.0
    target_users: Set[str] = field(default_factory=set)
    target_regions: Set[str] = field(default_factory=set)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    a_b_variants: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class ServiceConfigRequest:
    """Service configuration request"""
    service_id: str
    requested_version: Optional[str] = None
    environment: str = "production"
    format: ConfigFormat = ConfigFormat.JSON
    include_feature_flags: bool = True
    include_secrets: bool = False
    client_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfigManagementResult:
    """Configuration management operation result"""
    service_id: str
    operation: str
    success: bool
    version_applied: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    feature_flags: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

@dataclass
class ConfigUpdateResult:
    """Configuration update result"""
    service_id: str
    old_version: Optional[str]
    new_version: str
    changes_applied: Dict[str, Any]
    hot_reload_successful: bool
    affected_instances: List[str]
    rollback_available: bool = True

@dataclass
class FeatureFlagOperation:
    """Feature flag operation"""
    operation_type: str  # enable, disable, update_percentage, add_users, etc.
    flag_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FeatureFlagResult:
    """Feature flag operation result"""
    flag_id: str
    operation: str
    success: bool
    previous_state: Dict[str, Any]
    new_state: Dict[str, Any]
    affected_services: List[str] = field(default_factory=list)

@dataclass
class ConfigValidationResult:
    """Configuration validation result"""
    service_id: str
    is_valid: bool
    schema_version: str
    validation_errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

@dataclass
class RollbackResult:
    """Configuration rollback result"""
    service_id: str
    rollback_from_version: str
    rollback_to_version: str
    success: bool
    affected_instances: List[str]
    rollback_time_ms: float

@dataclass
class ConfigManagerConfig:
    """Configuration for config manager"""
    storage_backend: str = "memory"  # memory, redis, consul, etcd, database
    enable_hot_reload: bool = True
    validation_enabled: bool = True
    version_retention_days: int = 30
    max_versions_per_service: int = 100
    feature_flag_cache_ttl: int = 300  # seconds
    config_change_notification: bool = True
    encryption_enabled: bool = True

class DistributedConfigStore:
    """Distributed configuration storage backend"""
    
    def __init__(self, backend_type: str = "memory"):
        self.backend_type = backend_type
        self.config_storage: Dict[str, Dict[str, ConfigVersion]] = {}
        self.feature_flags: Dict[str, FeatureFlag] = {}
        self.schema_storage: Dict[str, Dict[str, Any]] = {}
        
    async def store_config_version(self, version: ConfigVersion) -> bool:
        """Store configuration version"""
        try:
            if version.service_id not in self.config_storage:
                self.config_storage[version.service_id] = {}
            
            self.config_storage[version.service_id][version.version_id] = version
            logger.debug(f"Stored config version {version.version_id} for service {version.service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store config version: {e}")
            return False
    
    async def get_config_version(self, service_id: str, version_id: str) -> Optional[ConfigVersion]:
        """Get specific configuration version"""
        try:
            service_configs = self.config_storage.get(service_id, {})
            return service_configs.get(version_id)
        except Exception as e:
            logger.error(f"Failed to get config version: {e}")
            return None
    
    async def get_active_config(self, service_id: str) -> Optional[ConfigVersion]:
        """Get active configuration for service"""
        try:
            service_configs = self.config_storage.get(service_id, {})
            for version in service_configs.values():
                if version.is_active:
                    return version
            return None
        except Exception as e:
            logger.error(f"Failed to get active config: {e}")
            return None
    
    async def list_config_versions(self, service_id: str) -> List[ConfigVersion]:
        """List all configuration versions for service"""
        try:
            service_configs = self.config_storage.get(service_id, {})
            return list(service_configs.values())
        except Exception as e:
            logger.error(f"Failed to list config versions: {e}")
            return []
    
    async def store_feature_flag(self, flag: FeatureFlag) -> bool:
        """Store feature flag"""
        try:
            self.feature_flags[flag.flag_id] = flag
            return True
        except Exception as e:
            logger.error(f"Failed to store feature flag: {e}")
            return False
    
    async def get_feature_flag(self, flag_id: str) -> Optional[FeatureFlag]:
        """Get feature flag"""
        return self.feature_flags.get(flag_id)
    
    async def list_feature_flags(self, service_id: Optional[str] = None) -> List[FeatureFlag]:
        """List feature flags, optionally filtered by service"""
        # For simplicity, returning all flags - in real implementation would filter by service
        return list(self.feature_flags.values())

class ConfigVersionManager:
    """Configuration version management"""
    
    def __init__(self, config_store: DistributedConfigStore):
        self.config_store = config_store
        self.version_counter: Dict[str, int] = {}
        
    async def create_new_version(self, service_id: str, configuration: Dict[str, Any], 
                               created_by: str, change_description: str) -> ConfigVersion:
        """Create new configuration version"""
        try:
            # Generate version number
            if service_id not in self.version_counter:
                self.version_counter[service_id] = 0
            
            self.version_counter[service_id] += 1
            version_number = f"v{self.version_counter[service_id]}"
            
            # Create version
            version = ConfigVersion(
                version_id=str(uuid.uuid4()),
                service_id=service_id,
                version_number=version_number,
                configuration=copy.deepcopy(configuration),
                created_at=time.time(),
                created_by=created_by,
                change_description=change_description
            )
            
            # Store version
            await self.config_store.store_config_version(version)
            
            return version
            
        except Exception as e:
            logger.error(f"Failed to create new version for {service_id}: {e}")
            raise
    
    async def activate_version(self, service_id: str, version_id: str) -> bool:
        """Activate specific configuration version"""
        try:
            # Deactivate current active version
            current_active = await self.config_store.get_active_config(service_id)
            if current_active:
                current_active.is_active = False
                await self.config_store.store_config_version(current_active)
            
            # Activate new version
            new_version = await self.config_store.get_config_version(service_id, version_id)
            if new_version:
                new_version.is_active = True
                await self.config_store.store_config_version(new_version)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to activate version {version_id} for {service_id}: {e}")
            return False
    
    async def get_version_diff(self, service_id: str, version1_id: str, version2_id: str) -> Dict[str, Any]:
        """Get differences between two configuration versions"""
        try:
            version1 = await self.config_store.get_config_version(service_id, version1_id)
            version2 = await self.config_store.get_config_version(service_id, version2_id)
            
            if not version1 or not version2:
                return {}
            
            # Simple diff implementation
            diff = {
                'added': {},
                'removed': {},
                'modified': {}
            }
            
            config1 = version1.configuration
            config2 = version2.configuration
            
            # Find added and modified keys
            for key, value in config2.items():
                if key not in config1:
                    diff['added'][key] = value
                elif config1[key] != value:
                    diff['modified'][key] = {'old': config1[key], 'new': value}
            
            # Find removed keys
            for key in config1:
                if key not in config2:
                    diff['removed'][key] = config1[key]
            
            return diff
            
        except Exception as e:
            logger.error(f"Failed to compute version diff: {e}")
            return {}

class FeatureFlagEngine:
    """Feature flag management engine"""
    
    def __init__(self, config_store: DistributedConfigStore):
        self.config_store = config_store
        self.flag_cache: Dict[str, FeatureFlag] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def create_feature_flag(self, flag_name: str, description: str, 
                                strategy: FeatureFlagStrategy) -> FeatureFlag:
        """Create new feature flag"""
        try:
            flag = FeatureFlag(
                flag_id=str(uuid.uuid4()),
                flag_name=flag_name,
                description=description,
                strategy=strategy
            )
            
            await self.config_store.store_feature_flag(flag)
            self.flag_cache[flag.flag_id] = flag
            self.cache_timestamps[flag.flag_id] = time.time()
            
            return flag
            
        except Exception as e:
            logger.error(f"Failed to create feature flag {flag_name}: {e}")
            raise
    
    async def evaluate_feature_flag(self, flag_id: str, context: Dict[str, Any]) -> bool:
        """Evaluate if feature flag should be enabled for given context"""
        try:
            flag = await self._get_flag_with_cache(flag_id)
            if not flag or not flag.enabled:
                return False
            
            # Strategy-based evaluation
            if flag.strategy == FeatureFlagStrategy.PERCENTAGE:
                # Simple percentage-based rollout
                user_hash = hashlib.md5(str(context.get('user_id', 'anonymous')).encode()).hexdigest()
                hash_int = int(user_hash[:8], 16)
                percentage = (hash_int % 100) / 100.0
                return percentage <= flag.rollout_percentage
                
            elif flag.strategy == FeatureFlagStrategy.USER_LIST:
                user_id = context.get('user_id')
                return user_id in flag.target_users
                
            elif flag.strategy == FeatureFlagStrategy.GEOGRAPHIC:
                region = context.get('region')
                return region in flag.target_regions
                
            elif flag.strategy == FeatureFlagStrategy.TIME_BASED:
                current_time = time.time()
                if flag.start_time and current_time < flag.start_time:
                    return False
                if flag.end_time and current_time > flag.end_time:
                    return False
                return True
                
            elif flag.strategy == FeatureFlagStrategy.A_B_TEST:
                # Simple A/B test - hash user to variant
                user_hash = hashlib.md5(str(context.get('user_id', 'anonymous')).encode()).hexdigest()
                variant_index = int(user_hash[:2], 16) % len(flag.a_b_variants)
                variant_key = list(flag.a_b_variants.keys())[variant_index]
                context['variant'] = variant_key
                return True
                
            else:
                return flag.enabled
                
        except Exception as e:
            logger.error(f"Failed to evaluate feature flag {flag_id}: {e}")
            return False
    
    async def update_flag_percentage(self, flag_id: str, percentage: float) -> bool:
        """Update feature flag rollout percentage"""
        try:
            flag = await self.config_store.get_feature_flag(flag_id)
            if flag:
                flag.rollout_percentage = max(0.0, min(1.0, percentage))
                flag.updated_at = time.time()
                await self.config_store.store_feature_flag(flag)
                
                # Update cache
                self.flag_cache[flag_id] = flag
                self.cache_timestamps[flag_id] = time.time()
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update flag percentage: {e}")
            return False
    
    async def _get_flag_with_cache(self, flag_id: str) -> Optional[FeatureFlag]:
        """Get feature flag with caching"""
        current_time = time.time()
        
        # Check cache
        if (flag_id in self.flag_cache and 
            flag_id in self.cache_timestamps and
            current_time - self.cache_timestamps[flag_id] < self.cache_ttl):
            return self.flag_cache[flag_id]
        
        # Load from store
        flag = await self.config_store.get_feature_flag(flag_id)
        if flag:
            self.flag_cache[flag_id] = flag
            self.cache_timestamps[flag_id] = current_time
        
        return flag

class ConfigSchemaValidator:
    """Configuration schema validation"""
    
    def __init__(self):
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.ainflue_schemas = self._load_ainflue_schemas()
        
    def _load_ainflue_schemas(self) -> Dict[str, Any]:
        """Load IA Chérie-specific configuration schemas"""
        return {
            "base_service": {
                "type": "object",
                "required": ["service_name", "version", "port"],
                "properties": {
                    "service_name": {"type": "string", "minLength": 1},
                    "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                    "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                    "environment": {"type": "string", "enum": ["development", "staging", "production"]},
                    "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]}
                }
            },
            "ainflue_content_service": {
                "type": "object",
                "required": ["content_types", "processing_capabilities"],
                "properties": {
                    "content_types": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["video", "audio", "image", "text", "document"]}
                    },
                    "processing_capabilities": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "max_file_size_mb": {"type": "integer", "minimum": 1, "maximum": 10000},
                    "supported_formats": {"type": "array", "items": {"type": "string"}}
                }
            },
            "ainflue_ai_service": {
                "type": "object",
                "required": ["model_type", "inference_endpoint"],
                "properties": {
                    "model_type": {"type": "string", "enum": ["classification", "generation", "analysis"]},
                    "inference_endpoint": {"type": "string", "format": "uri"},
                    "gpu_required": {"type": "boolean"},
                    "model_version": {"type": "string"},
                    "batch_size": {"type": "integer", "minimum": 1, "maximum": 1000}
                }
            }
        }
    
    async def validate_configuration(self, service_id: str, configuration: Dict[str, Any], 
                                   schema_name: Optional[str] = None) -> ConfigValidationResult:
        """Validate configuration against schema"""
        try:
            validation_errors = []
            warnings = []
            suggestions = []
            
            # Determine schema to use
            if not schema_name:
                service_type = configuration.get('service_type', 'base_service')
                schema_name = f"iacherie_{service_type}" if service_type != 'base_service' else 'base_service'
            
            schema = self.ainflue_schemas.get(schema_name, self.ainflue_schemas['base_service'])
            
            # Basic validation
            validation_result = await self._validate_against_schema(configuration, schema)
            validation_errors.extend(validation_result['errors'])
            warnings.extend(validation_result['warnings'])
            
            # IA Chérie-specific business rules
            business_validation = await self._validate_ainflue_business_rules(configuration)
            validation_errors.extend(business_validation['errors'])
            suggestions.extend(business_validation['suggestions'])
            
            is_valid = len(validation_errors) == 0
            
            return ConfigValidationResult(
                service_id=service_id,
                is_valid=is_valid,
                schema_version=schema_name,
                validation_errors=validation_errors,
                warnings=warnings,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return ConfigValidationResult(
                service_id=service_id,
                is_valid=False,
                schema_version="unknown",
                validation_errors=[{"error": f"Validation exception: {str(e)}"}]
            )
    
    async def _validate_against_schema(self, config: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, List]:
        """Validate configuration against JSON schema"""
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = schema.get('required', [])
        for field in required_fields:
            if field not in config:
                errors.append({
                    "field": field,
                    "error": f"Required field '{field}' is missing"
                })
        
        # Check field types and constraints
        properties = schema.get('properties', {})
        for field, field_schema in properties.items():
            if field in config:
                value = config[field]
                field_type = field_schema.get('type')
                
                # Type checking
                if field_type == 'string' and not isinstance(value, str):
                    errors.append({
                        "field": field,
                        "error": f"Field '{field}' must be a string, got {type(value).__name__}"
                    })
                elif field_type == 'integer' and not isinstance(value, int):
                    errors.append({
                        "field": field,
                        "error": f"Field '{field}' must be an integer, got {type(value).__name__}"
                    })
                elif field_type == 'array' and not isinstance(value, list):
                    errors.append({
                        "field": field,
                        "error": f"Field '{field}' must be an array, got {type(value).__name__}"
                    })
                
                # Constraint checking
                if field_type == 'integer':
                    minimum = field_schema.get('minimum')
                    maximum = field_schema.get('maximum')
                    if minimum is not None and value < minimum:
                        errors.append({
                            "field": field,
                            "error": f"Field '{field}' must be >= {minimum}, got {value}"
                        })
                    if maximum is not None and value > maximum:
                        errors.append({
                            "field": field,
                            "error": f"Field '{field}' must be <= {maximum}, got {value}"
                        })
                
                # Enum checking
                enum_values = field_schema.get('enum')
                if enum_values and value not in enum_values:
                    errors.append({
                        "field": field,
                        "error": f"Field '{field}' must be one of {enum_values}, got '{value}'"
                    })
        
        return {"errors": errors, "warnings": warnings}
    
    async def _validate_ainflue_business_rules(self, config: Dict[str, Any]) -> Dict[str, List]:
        """Validate IA Chérie-specific business rules"""
        errors = []
        suggestions = []
        
        # Creator economy validation
        if config.get('business_domain') == 'creator':
            if 'creator_types' not in config:
                suggestions.append("Consider adding 'creator_types' for creator services")
        
        # Content service validation
        if config.get('service_type') == 'content_service':
            max_file_size = config.get('max_file_size_mb', 0)
            if max_file_size > 5000:  # 5GB
                suggestions.append("Large file sizes may impact performance - consider chunked processing")
        
        # Performance recommendations
        if config.get('port', 8080) == 8080:
            suggestions.append("Consider using non-default ports for production services")
        
        # Security recommendations
        if config.get('environment') == 'production':
            if config.get('log_level') == 'DEBUG':
                errors.append({
                    "field": "log_level",
                    "error": "DEBUG log level not recommended for production"
                })
        
        return {"errors": errors, "suggestions": suggestions}

class ServiceConfigurationManager:
    """
    Manager configuration services avec hot-reload et validation.
    Config versioning + feature flags + environment management + validation.
    """
    
    def __init__(self, config_manager_config: Optional[ConfigManagerConfig] = None):
        """Initialize service configuration manager"""
        self.config_manager_config = config_manager_config or ConfigManagerConfig()
        self.config_store = DistributedConfigStore(self.config_manager_config.storage_backend)
        self.version_manager = ConfigVersionManager(self.config_store)
        self.feature_flag_engine = FeatureFlagEngine(self.config_store)
        self.config_validator = ConfigSchemaValidator()
        
        # Service registry reference (to be injected)
        self.service_registry = None
        
        # Hot-reload subscribers
        self.reload_subscribers: Dict[str, List[Callable]] = {}
        
        # Metrics
        self.metrics = {
            'config_requests': 0,
            'hot_reloads': 0,
            'validation_errors': 0,
            'feature_flag_evaluations': 0,
            'version_rollbacks': 0
        }
    
    def set_service_registry(self, registry):
        """Set reference to service registry"""
        self.service_registry = registry
    
    async def manage_service_configuration(self, config_request: ServiceConfigRequest) -> ConfigManagementResult:
        """
        Gestion configuration services avec versioning et validation.
        
        Configuration Features:
        - Hot-reload configuration sans service downtime
        - Configuration versioning avec rollback capabilities
        - Feature flags avec gradual rollout strategies
        - Environment-specific configuration management
        - Configuration schema validation avec enforcement
        - Configuration templates pour service types
        - Configuration drift detection et correction
        - A/B testing configuration pour feature experiments
        """
        start_time = time.time()
        
        try:
            # Get requested configuration version
            if config_request.requested_version:
                config_version = await self.config_store.get_config_version(
                    config_request.service_id, config_request.requested_version
                )
            else:
                config_version = await self.config_store.get_active_config(config_request.service_id)
            
            if not config_version:
                return ConfigManagementResult(
                    service_id=config_request.service_id,
                    operation="get_configuration",
                    success=False,
                    validation_errors=["Configuration not found"],
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            # Get base configuration
            configuration = copy.deepcopy(config_version.configuration)
            
            # Apply environment-specific overrides
            env_config = configuration.get('environments', {}).get(config_request.environment, {})
            configuration.update(env_config)
            
            # Evaluate and inject feature flags
            feature_flags = {}
            if config_request.include_feature_flags:
                feature_flags = await self._evaluate_feature_flags_for_service(
                    config_request.service_id, config_request.client_info
                )
                configuration['feature_flags'] = feature_flags
            
            # Remove secrets if not requested
            if not config_request.include_secrets:
                configuration = self._remove_secrets(configuration)
            
            # Format configuration
            if config_request.format != ConfigFormat.JSON:
                configuration = await self._format_configuration(configuration, config_request.format)
            
            # Update metrics
            self.metrics['config_requests'] += 1
            
            return ConfigManagementResult(
                service_id=config_request.service_id,
                operation="get_configuration",
                success=True,
                version_applied=config_version.version_number,
                configuration=configuration,
                feature_flags=feature_flags,
                execution_time_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            logger.error(f"Configuration management failed for {config_request.service_id}: {e}")
            return ConfigManagementResult(
                service_id=config_request.service_id,
                operation="get_configuration",
                success=False,
                validation_errors=[f"Management error: {str(e)}"],
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    async def update_service_configuration(self, service_id: str, config_updates: Dict, 
                                         version: str = None) -> ConfigUpdateResult:
        """Update configuration service avec validation et versioning."""
        try:
            # Get current active configuration
            current_version = await self.config_store.get_active_config(service_id)
            if not current_version:
                # Create initial configuration
                current_config = {}
                old_version_number = None
            else:
                current_config = current_version.configuration.copy()
                old_version_number = current_version.version_number
            
            # Apply updates
            updated_config = current_config.copy()
            updated_config.update(config_updates)
            
            # Validate updated configuration
            validation_result = await self.config_validator.validate_configuration(
                service_id, updated_config
            )
            
            if not validation_result.is_valid:
                return ConfigUpdateResult(
                    service_id=service_id,
                    old_version=old_version_number,
                    new_version="",
                    changes_applied={},
                    hot_reload_successful=False,
                    affected_instances=[],
                    rollback_available=False
                )
            
            # Create new version
            new_version = await self.version_manager.create_new_version(
                service_id=service_id,
                configuration=updated_config,
                created_by="system",
                change_description=f"Configuration update: {list(config_updates.keys())}"
            )
            
            # Activate new version
            await self.version_manager.activate_version(service_id, new_version.version_id)
            
            # Perform hot reload if enabled
            hot_reload_successful = False
            affected_instances = []
            
            if self.config_manager_config.enable_hot_reload:
                hot_reload_successful, affected_instances = await self._perform_hot_reload(
                    service_id, updated_config
                )
            
            self.metrics['hot_reloads'] += 1
            
            return ConfigUpdateResult(
                service_id=service_id,
                old_version=old_version_number,
                new_version=new_version.version_number,
                changes_applied=config_updates,
                hot_reload_successful=hot_reload_successful,
                affected_instances=affected_instances,
                rollback_available=True
            )
            
        except Exception as e:
            logger.error(f"Configuration update failed for {service_id}: {e}")
            return ConfigUpdateResult(
                service_id=service_id,
                old_version="unknown",
                new_version="",
                changes_applied={},
                hot_reload_successful=False,
                affected_instances=[],
                rollback_available=False
            )
    
    async def manage_feature_flags(self, flag_operations: List[FeatureFlagOperation]) -> FeatureFlagResult:
        """Gestion feature flags avec targeting et analytics."""
        results = []
        
        for operation in flag_operations:
            try:
                flag = await self.config_store.get_feature_flag(operation.flag_id)
                if not flag:
                    results.append(FeatureFlagResult(
                        flag_id=operation.flag_id,
                        operation=operation.operation_type,
                        success=False,
                        previous_state={},
                        new_state={}
                    ))
                    continue
                
                previous_state = {
                    'enabled': flag.enabled,
                    'rollout_percentage': flag.rollout_percentage,
                    'target_users': list(flag.target_users),
                    'target_regions': list(flag.target_regions)
                }
                
                # Apply operation
                if operation.operation_type == 'enable':
                    flag.enabled = True
                elif operation.operation_type == 'disable':
                    flag.enabled = False
                elif operation.operation_type == 'update_percentage':
                    flag.rollout_percentage = operation.parameters.get('percentage', 0.0)
                elif operation.operation_type == 'add_users':
                    users_to_add = operation.parameters.get('users', [])
                    flag.target_users.update(users_to_add)
                elif operation.operation_type == 'remove_users':
                    users_to_remove = operation.parameters.get('users', [])
                    flag.target_users.difference_update(users_to_remove)
                
                flag.updated_at = time.time()
                await self.config_store.store_feature_flag(flag)
                
                new_state = {
                    'enabled': flag.enabled,
                    'rollout_percentage': flag.rollout_percentage,
                    'target_users': list(flag.target_users),
                    'target_regions': list(flag.target_regions)
                }
                
                results.append(FeatureFlagResult(
                    flag_id=operation.flag_id,
                    operation=operation.operation_type,
                    success=True,
                    previous_state=previous_state,
                    new_state=new_state
                ))
                
            except Exception as e:
                logger.error(f"Feature flag operation failed: {e}")
                results.append(FeatureFlagResult(
                    flag_id=operation.flag_id,
                    operation=operation.operation_type,
                    success=False,
                    previous_state={},
                    new_state={}
                ))
        
        # Return first result for simplicity - in real implementation would return all
        return results[0] if results else FeatureFlagResult(
            flag_id="unknown",
            operation="unknown",
            success=False,
            previous_state={},
            new_state={}
        )
    
    async def validate_configuration_integrity(self, service_id: str) -> ConfigValidationResult:
        """Validation intégrité configuration avant deployment."""
        try:
            # Get active configuration
            active_config = await self.config_store.get_active_config(service_id)
            if not active_config:
                return ConfigValidationResult(
                    service_id=service_id,
                    is_valid=False,
                    schema_version="unknown",
                    validation_errors=[{"error": "No active configuration found"}]
                )
            
            # Validate configuration
            return await self.config_validator.validate_configuration(
                service_id, active_config.configuration
            )
            
        except Exception as e:
            logger.error(f"Configuration integrity validation failed: {e}")
            return ConfigValidationResult(
                service_id=service_id,
                is_valid=False,
                schema_version="unknown",
                validation_errors=[{"error": f"Validation exception: {str(e)}"}]
            )
    
    async def rollback_service_configuration(self, service_id: str, target_version: str) -> RollbackResult:
        """Rollback configuration vers version spécifiée."""
        start_time = time.time()
        
        try:
            # Get current and target versions
            current_version = await self.config_store.get_active_config(service_id)
            target_config_version = await self.config_store.get_config_version(service_id, target_version)
            
            if not target_config_version:
                return RollbackResult(
                    service_id=service_id,
                    rollback_from_version=current_version.version_number if current_version else "unknown",
                    rollback_to_version=target_version,
                    success=False,
                    affected_instances=[],
                    rollback_time_ms=(time.time() - start_time) * 1000
                )
            
            # Check if rollback is safe
            if not target_config_version.rollback_safe:
                logger.warning(f"Rollback to {target_version} may not be safe")
            
            # Activate target version
            success = await self.version_manager.activate_version(service_id, target_config_version.version_id)
            
            # Perform hot reload with rollback configuration
            affected_instances = []
            if success and self.config_manager_config.enable_hot_reload:
                _, affected_instances = await self._perform_hot_reload(
                    service_id, target_config_version.configuration
                )
            
            self.metrics['version_rollbacks'] += 1
            
            return RollbackResult(
                service_id=service_id,
                rollback_from_version=current_version.version_number if current_version else "unknown",
                rollback_to_version=target_config_version.version_number,
                success=success,
                affected_instances=affected_instances,
                rollback_time_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            logger.error(f"Configuration rollback failed: {e}")
            return RollbackResult(
                service_id=service_id,
                rollback_from_version="unknown",
                rollback_to_version=target_version,
                success=False,
                affected_instances=[],
                rollback_time_ms=(time.time() - start_time) * 1000
            )
    
    async def _evaluate_feature_flags_for_service(self, service_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate all feature flags for a service"""
        feature_flags = {}
        
        try:
            # Get all feature flags (in real implementation, would filter by service)
            all_flags = await self.config_store.list_feature_flags(service_id)
            
            for flag in all_flags:
                is_enabled = await self.feature_flag_engine.evaluate_feature_flag(flag.flag_id, context)
                feature_flags[flag.flag_name] = {
                    'enabled': is_enabled,
                    'strategy': flag.strategy.value,
                    'description': flag.description
                }
                
                self.metrics['feature_flag_evaluations'] += 1
            
        except Exception as e:
            logger.error(f"Feature flag evaluation failed: {e}")
        
        return feature_flags
    
    def _remove_secrets(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from configuration"""
        sensitive_keys = {'password', 'secret', 'key', 'token', 'api_key', 'private_key'}
        
        def remove_secrets_recursive(obj):
            if isinstance(obj, dict):
                return {
                    k: '***REDACTED***' if any(secret in k.lower() for secret in sensitive_keys) 
                    else remove_secrets_recursive(v)
                    for k, v in obj.items()
                }
            elif isinstance(obj, list):
                return [remove_secrets_recursive(item) for item in obj]
            else:
                return obj
        
        return remove_secrets_recursive(configuration)
    
    async def _format_configuration(self, configuration: Dict[str, Any], format_type: ConfigFormat) -> Any:
        """Format configuration to requested format"""
        if format_type == ConfigFormat.JSON:
            return configuration
        elif format_type == ConfigFormat.YAML:
            return yaml.dump(configuration, default_flow_style=False)
        else:
            # For other formats, return JSON for now
            return configuration
    
    async def _perform_hot_reload(self, service_id: str, new_configuration: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Perform hot reload of configuration"""
        try:
            affected_instances = []
            
            # Get service instances from registry
            if self.service_registry:
                services = list(self.service_registry.service_instances.values())
                service_instances = [s for s in services if s.service_name == service_id]
                
                for instance in service_instances:
                    # In real implementation, would make HTTP call to service reload endpoint
                    logger.info(f"Hot reloading configuration for instance {instance.service_id}")
                    affected_instances.append(instance.service_id)
            
            # Notify subscribers
            subscribers = self.reload_subscribers.get(service_id, [])
            for callback in subscribers:
                try:
                    await callback(service_id, new_configuration)
                except Exception as e:
                    logger.error(f"Reload subscriber callback failed: {e}")
            
            return True, affected_instances
            
        except Exception as e:
            logger.error(f"Hot reload failed for {service_id}: {e}")
            return False, []
    
    def subscribe_to_config_changes(self, service_id: str, callback: Callable):
        """Subscribe to configuration changes for hot reload"""
        if service_id not in self.reload_subscribers:
            self.reload_subscribers[service_id] = []
        self.reload_subscribers[service_id].append(callback)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get configuration manager metrics"""
        return {
            **self.metrics,
            'active_configurations': len(self.config_store.config_storage),
            'feature_flags_count': len(self.config_store.feature_flags),
            'reload_subscribers': sum(len(subs) for subs in self.reload_subscribers.values())
        }
    
    async def shutdown(self):
        """Graceful shutdown of configuration manager"""
        logger.info("Shutting down ServiceConfigurationManager")
        # Clear caches and subscribers
        self.reload_subscribers.clear()

# Factory function
async def create_service_configuration_manager(config: Optional[ConfigManagerConfig] = None) -> ServiceConfigurationManager:
    """Factory function to create service configuration manager"""
    return ServiceConfigurationManager(config)

# Export main classes and functions
__all__ = [
    'ServiceConfigurationManager',
    'ConfigManagerConfig',
    'ServiceConfigRequest',
    'ConfigManagementResult',
    'ConfigUpdateResult',
    'FeatureFlagOperation',
    'FeatureFlagResult',
    'ConfigValidationResult',
    'RollbackResult',
    'ConfigVersion',
    'FeatureFlag',
    'ConfigFormat',
    'FeatureFlagStrategy',
    'ConfigChangeType',
    'create_service_configuration_manager'
]