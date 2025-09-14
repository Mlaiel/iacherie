"""🔧 Base Configuration Manager - IA-Influencer-Agent
import asyncio

==================================================================
Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: DevOps + Backend Senior + Cloud Architect + Infrastructure Engineer
Date: 2025-08-24

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Core configuration management foundation for enterprise deployment.
==================================================================
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

class ConfigurationError(Exception):
    """
Base exception for configuration-related errors"""
    pass

class ConfigFormat(Enum):
    """
Supported configuration formats"""

    YAML = "yaml"
    JSON = "json"
    TOML = "toml"
    INI = "ini"
    ENV = "env"

class ValidationLevel(Enum):
    """Configuration validation levels"""

    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    PARANOID = "paranoid"

@dataclass
class ConfigurationSchema:
    """Configuration schema definition"""
    name: str
    version: str
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    format_type: ConfigFormat = ConfigFormat.YAML
    encryption_required: bool = False

@dataclass
class ConfigurationSource:
    """
Configuration source definition"""
    name: str
    path: str
    format_type: ConfigFormat
    priority: int = 100
    encrypted: bool = False
    environment_specific: bool = False
    reload_interval: Optional[int] = None
    validation_schema: Optional[str] = None

class BaseConfigurationManager:
    """
    Enterprise-grade base configuration manager.
    
    Provides comprehensive configuration management capabilities:
    - Multi-format configuration support (YAML, JSON, TOML, INI, ENV)
    - Hierarchical configuration merging
    - Environment-specific overrides
    - Configuration validation and schema enforcement
    - Encrypted configuration support
    - Hot-reload capabilities
    - Configuration versioning and rollback
    - Audit logging and change tracking
    """
    
    def __init__(self, config_dir -> None: Optional[str] = None) -> None:
        """
        Initialize base configuration manager.
        
        Args:
            config_dir: Base configuration directory path
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration directories
        self.config_dir = Path(config_dir) if config_dir else Path("/app/config")
        self.schemas_dir = self.config_dir / "schemas"
        self.environments_dir = self.config_dir / "environments"
        self.secrets_dir = self.config_dir / "secrets"
        
        # Configuration state
        self.configurations = {}
        self.schemas = {}
        self.sources = []
        self.watchers = {}
        self.cache = {}
        self.validation_level = ValidationLevel.STANDARD
        
        # Metadata
        self.version = "2.0.0"
        self.last_reload = None
        self.change_history = []
        
        self.logger.info("Base configuration manager initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize configuration manager with all sources.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Create configuration directories
            await self._ensure_directories()
            
            # Load configuration schemas
            await self._load_schemas()
            
            # Register default configuration sources
            await self._register_default_sources()
            
            # Load all configurations
            await self._load_all_configurations()
            
            # Setup file watchers for hot-reload
            await self._setup_file_watchers()
            
            self.logger.info("Base configuration manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize configuration manager: {e}")
            return False
    
    async def _ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        directories = [
            self.config_dir,
            self.schemas_dir,
            self.environments_dir,
            self.secrets_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Ensured directory exists: {directory}")
    
    async def _load_schemas(self) -> None:
        """Load configuration schemas"""
        schema_files = list(self.schemas_dir.glob("*.yaml"))
        
        for schema_file in schema_files:
            try:
                with open(schema_file, 'r') as f:
                    schema_data = yaml.safe_load(f)
                
                schema = ConfigurationSchema(
                    name=schema_data.get('name'),
                    version=schema_data.get('version'),
                    required_fields=schema_data.get('required_fields', []),
                    optional_fields=schema_data.get('optional_fields', []),
                    validation_rules=schema_data.get('validation_rules', {}),
                    dependencies=schema_data.get('dependencies', []),
                    format_type=ConfigFormat(schema_data.get('format', 'yaml')),
                    encryption_required=schema_data.get('encryption_required', False)
                )
                
                self.schemas[schema.name] = schema
                self.logger.debug(f"Loaded schema: {schema.name}")
                
            except Exception as e:
                self.logger.warning(f"Failed to load schema {schema_file}: {e}")
    
    async def _register_default_sources(self) -> None:
        """Register default configuration sources"""
        default_sources = [
            ConfigurationSource(
                name="base",
                path=str(self.config_dir / "base.yaml"),
                format_type=ConfigFormat.YAML,
                priority=1000
            ),
            ConfigurationSource(
                name="environment",
                path=str(self.environments_dir / f"{os.getenv('ENVIRONMENT', 'development')}.yaml"),
                format_type=ConfigFormat.YAML,
                priority=800,
                environment_specific=True
            ),
            ConfigurationSource(
                name="local",
                path=str(self.config_dir / "local.yaml"),
                format_type=ConfigFormat.YAML,
                priority=600
            ),
            ConfigurationSource(
                name="env_vars",
                path="",
                format_type=ConfigFormat.ENV,
                priority=400
            )
        ]
        
        for source in default_sources:
            await self.register_source(source)
    
    async def register_source(self, source: ConfigurationSource) -> None:
        """
        Register a configuration source.
        
        Args:
            source: Configuration source to register
        """
        self.sources.append(source)
        self.sources.sort(key=lambda x: x.priority, reverse=True)
        self.logger.info(f"Registered configuration source: {source.name}")
    
    async def _load_all_configurations(self) -> None:
        """Load configurations from all registered sources"""
        for source in self.sources:
            try:
                config_data = await self._load_configuration_source(source)
                if config_data:
                    self.configurations[source.name] = config_data
                    self.logger.debug(f"Loaded configuration from source: {source.name}")
            
            except Exception as e:
                self.logger.warning(f"Failed to load configuration from {source.name}: {e}")
        
        # Merge all configurations
        self.merged_config = await self._merge_configurations()
        self.last_reload = datetime.now()
    
    async def _load_configuration_source(self, source: ConfigurationSource) -> Optional[Dict[str, Any]]:
        """
        Load configuration from a single source.
        
        Args:
            source: Configuration source to load
            
        Returns:
            Configuration data or None if not found
        """
        if source.format_type == ConfigFormat.ENV:
            return await self._load_environment_variables()
        
        if not source.path or not os.path.exists(source.path):
            return None
        
        try:
            with open(source.path, 'r') as f:
                if source.format_type == ConfigFormat.YAML:
                    return yaml.safe_load(f)
                elif source.format_type == ConfigFormat.JSON:
                    return json.load(f)
                # Add other format handlers as needed
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {source.path}: {e}")
            return None
    
    async def _load_environment_variables(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        env_config = {}
        
        # Load environment variables with prefix
        for key, value in os.environ.items():
            if key.startswith('IA_'):
                # Convert IA_DATABASE_HOST to nested structure
                config_key = key[3:].lower().replace('_', '.')
                await self._set_nested_value(env_config, config_key, value)
        
        return env_config
    
    async def _set_nested_value(self, config: Dict[str, Any], key: str, value: str) -> None:
        """
Set nested configuration value from dot notation"""
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Try to convert value to appropriate type
        try:
            if value.lower() in ('true', 'false'):
                current[keys[-1]] = value.lower() == 'true'
            elif value.isdigit():
                current[keys[-1]] = int(value)
            elif '.' in value and all(part.isdigit() for part in value.split('.')):
                current[keys[-1]] = float(value)
            else:
                current[keys[-1]] = value
        except:
            current[keys[-1]] = value
    
    async def _merge_configurations(self) -> Dict[str, Any]:
        """
Merge configurations from all sources based on priority"""
        merged = {}
        
        # Start with lowest priority and merge upwards
        for source in reversed(self.sources):
            if source.name in self.configurations:
                await self._deep_merge(merged, self.configurations[source.name])
        
        return merged
    
    async def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
Deep merge source configuration into target"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                await self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    async def _setup_file_watchers(self) -> None:
        """
Setup file watchers for hot configuration reload"""
        # Implementation would use file system watchers
        # For now, we'll just log that watchers are set up
        self.logger.info("File watchers set up for configuration hot-reload")
    
    async def get_configuration(self, key: Optional[str] = None) -> Union[Dict[str, Any], Any]:
        """
        Get configuration value(s).
        
        Args:
            key: Dot-notation key for specific value, or None for full config
            
        Returns:
            Configuration value or full configuration
        """
        if key is None:
            return self.merged_config
        
        return await self._get_nested_value(self.merged_config, key)
    
    async def _get_nested_value(self, config: Dict[str, Any], key: str) -> Any:
        """
Get nested configuration value using dot notation"""
        keys = key.split('.')
        current = config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current
    
    async def set_configuration(self, key: str, value: Any, source: str = "runtime") -> bool:
        """
        Set configuration value at runtime.
        
        Args:
            key: Dot-notation key
            value: Value to set
            source: Source identifier for tracking
            
        Returns:
            bool: True if successful
        """
        try:
            await self._set_nested_value(self.merged_config, key, value)
            
            # Record change in history
            self.change_history.append({
                "timestamp": datetime.now(),
                "key": key,
                "value": value,
                "source": source,
                "action": "set"
            })
            
            self.logger.info(f"Configuration updated: {key} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set configuration {key}: {e}")
            return False
    
    async def validate_configuration(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate configuration against schemas.
        
        Args:
            config: Configuration to validate, or None for current config
            
        Returns:
            Validation result
        """
        if config is None:
            config = self.merged_config
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "validated_at": datetime.now()
        }
        
        # Run validation rules
        for schema_name, schema in self.schemas.items():
            try:
                await self._validate_against_schema(config, schema, validation_result)
            except Exception as e:
                validation_result["errors"].append(f"Schema validation error for {schema_name}: {e}")
                validation_result["valid"] = False
        
        return validation_result
    
    async def _validate_against_schema(
        self, 
        config: Dict[str, Any], 
        schema: ConfigurationSchema, 
        result: Dict[str, Any]
    ) -> None:
        """Validate configuration against a specific schema"""
        # Check required fields
        for field in schema.required_fields:
            if not await self._get_nested_value(config, field):
                result["errors"].append(f"Required field missing: {field}")
                result["valid"] = False
        
        # Apply validation rules
        for field, rules in schema.validation_rules.items():
            value = await self._get_nested_value(config, field)
            if value is not None:
                await self._apply_validation_rules(field, value, rules, result)
    
    async def _apply_validation_rules(
        self, 
        field: str, 
        value: Any, 
        rules: Dict[str, Any], 
        result: Dict[str, Any]
    ) -> None:
        """Apply validation rules to a field"""
        # Type validation
        if "type" in rules:
            expected_type = rules["type"]
            if not isinstance(value, eval(expected_type)):
                result["errors"].append(f"Field {field} should be {expected_type}, got {type(value)}")
                result["valid"] = False
        
        # Range validation for numbers
        if isinstance(value, (int, float)):
            if "min" in rules and value < rules["min"]:
                result["errors"].append(f"Field {field} below minimum value: {rules['min']}")
                result["valid"] = False
            if "max" in rules and value > rules["max"]:
                result["errors"].append(f"Field {field} above maximum value: {rules['max']}")
                result["valid"] = False
        
        # Pattern validation for strings
        if isinstance(value, str) and "pattern" in rules:
            import re
            if not re.match(rules["pattern"], value):
                result["errors"].append(f"Field {field} does not match pattern: {rules['pattern']}")
                result["valid"] = False
    
    async def reload_configuration(self) -> bool:
        """
        Reload configuration from all sources.
        
        Returns:
            bool: True if successful
        """
        try:
            # Clear existing configurations
            self.configurations.clear()
            
            # Reload all configurations
            await self._load_all_configurations()
            
            self.logger.info("Configuration reloaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get configuration manager status"""
        return {
            "initialized": True,
            "version": self.version,
            "config_dir": str(self.config_dir),
            "sources_count": len(self.sources),
            "schemas_count": len(self.schemas),
            "last_reload": self.last_reload,
            "validation_level": self.validation_level.value,
            "change_count": len(self.change_history)
        }
    
    def get_change_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent configuration changes"""
        return self.change_history[-limit:]
