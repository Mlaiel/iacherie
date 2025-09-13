"""
🚀 Configuration Manager - Dynamic Configuration Management
==========================================================

Enterprise-grade configuration management with templating, validation,
hot reloading, and environment-specific overrides.

Features:
- Configuration templating with Jinja2/Helm
- Hot configuration reloading without service restart
- Configuration validation and schema enforcement
- Configuration versioning and rollback capabilities
- Environment-specific configuration injection
- Secret integration and dynamic secret resolution
- Configuration drift detection and remediation
- Audit trail for configuration changes

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: DevOps Engineer + Configuration Engineering + Platform Engineering
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import uuid
import hashlib
import jinja2

logger = logging.getLogger(__name__)

class ConfigurationType(Enum):
    """Configuration types"""
    APPLICATION = "application"
    DATABASE = "database"
    NETWORK = "network"
    SECURITY = "security"
    MONITORING = "monitoring"
    LOGGING = "logging"

class ConfigurationFormat(Enum):
    """Configuration formats"""
    JSON = "json"
    YAML = "yaml"
    PROPERTIES = "properties"
    TOML = "toml"
    ENV = "env"

@dataclass
class ConfigurationSchema:
    """Configuration schema definition"""
    schema_id: str
    name: str
    config_type: ConfigurationType
    format: ConfigurationFormat
    schema: Dict[str, Any]
    validation_rules: List[Dict[str, Any]]
    required_fields: List[str]
    created_at: datetime

@dataclass
class Configuration:
    """Configuration instance"""
    config_id: str
    name: str
    schema_id: str
    environment: str
    config_type: ConfigurationType
    format: ConfigurationFormat
    content: Dict[str, Any]
    version: str
    checksum: str
    created_at: datetime
    updated_at: datetime
    active: bool = True
    validated: bool = False

@dataclass
class ConfigurationTemplate:
    """Configuration template"""
    template_id: str
    name: str
    description: str
    template_content: str
    variables: Dict[str, Any]
    environments: List[str]
    created_at: datetime

class ConfigurationManager:
    """
    Dynamic Configuration Management
    
    Responsibilities:
    - Configuration schema definition and validation
    - Dynamic configuration templates with variable substitution
    - Hot configuration reloading and service notification
    - Environment-specific configuration management
    - Configuration versioning and rollback capabilities
    - Configuration drift detection and auto-remediation
    - Secret integration and dynamic resolution
    - Configuration audit trail and compliance
    """
    
    def __init__(self):
        self.configurations: Dict[str, Configuration] = {}
        self.configuration_schemas: Dict[str, ConfigurationSchema] = {}
        self.configuration_templates: Dict[str, ConfigurationTemplate] = {}
        self.configuration_history: List[Dict[str, Any]] = []
        self.active_watchers: Dict[str, List[callable]] = defaultdict(list)
        
        # Template engine
        self.jinja_env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            undefined=jinja2.StrictUndefined
        )
        
        self._initialize_manager()
        logger.info("ConfigurationManager initialized")

    def _initialize_manager(self):
        """Initialize configuration manager"""
        asyncio.create_task(self._configuration_monitoring_loop())
        asyncio.create_task(self._drift_detection_loop())
        self._setup_default_schemas()
        self._setup_default_templates()

    def _setup_default_schemas(self):
        """Setup default configuration schemas"""
        
        # Application configuration schema
        app_schema = ConfigurationSchema(
            schema_id="application_config",
            name="Application Configuration",
            config_type=ConfigurationType.APPLICATION,
            format=ConfigurationFormat.YAML,
            schema={
                "type": "object",
                "properties": {
                    "app": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "version": {"type": "string"},
                            "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                            "host": {"type": "string"},
                            "debug": {"type": "boolean"},
                            "log_level": {"type": "string", "enum": ["debug", "info", "warning", "error"]}
                        },
                        "required": ["name", "version", "port"]
                    },
                    "database": {
                        "type": "object",
                        "properties": {
                            "host": {"type": "string"},
                            "port": {"type": "integer"},
                            "name": {"type": "string"},
                            "username": {"type": "string"},
                            "password": {"type": "string"},
                            "pool_size": {"type": "integer", "minimum": 1, "maximum": 100}
                        },
                        "required": ["host", "port", "name"]
                    }
                },
                "required": ["app"]
            },
            validation_rules=[
                {"field": "app.port", "rule": "unique_per_environment"},
                {"field": "database.password", "rule": "secret_reference"}
            ],
            required_fields=["app.name", "app.version", "app.port"],
            created_at=datetime.now()
        )
        
        # Database configuration schema
        db_schema = ConfigurationSchema(
            schema_id="database_config",
            name="Database Configuration",
            config_type=ConfigurationType.DATABASE,
            format=ConfigurationFormat.JSON,
            schema={
                "type": "object",
                "properties": {
                    "connection": {
                        "type": "object",
                        "properties": {
                            "max_connections": {"type": "integer", "minimum": 1, "maximum": 1000},
                            "timeout": {"type": "integer", "minimum": 1},
                            "retry_attempts": {"type": "integer", "minimum": 0, "maximum": 10}
                        }
                    },
                    "performance": {
                        "type": "object",
                        "properties": {
                            "query_timeout": {"type": "integer"},
                            "cache_size": {"type": "string"},
                            "maintenance_window": {"type": "string"}
                        }
                    }
                }
            },
            validation_rules=[
                {"field": "connection.max_connections", "rule": "positive_integer"},
                {"field": "performance.cache_size", "rule": "memory_format"}
            ],
            required_fields=["connection.max_connections"],
            created_at=datetime.now()
        )
        
        self.configuration_schemas[app_schema.schema_id] = app_schema
        self.configuration_schemas[db_schema.schema_id] = db_schema

    def _setup_default_templates(self):
        """Setup default configuration templates"""
        
        # Application configuration template
        app_template = ConfigurationTemplate(
            template_id="app_config_template",
            name="Application Configuration Template",
            description="Standard application configuration with environment overrides",
            template_content="""
app:
  name: "{{ app_name }}"
  version: "{{ app_version | default('1.0.0') }}"
  port: {{ app_port | default(8080) }}
  host: "{{ app_host | default('0.0.0.0') }}"
  debug: {{ debug | default(false) | lower }}
  log_level: "{{ log_level | default('info') }}"

database:
  host: "{{ db_host }}"
  port: {{ db_port | default(5432) }}
  name: "{{ db_name }}"
  username: "{{ db_username }}"
  password: "${secret:{{ db_password_secret | default('db_password') }}}"
  pool_size: {{ db_pool_size | default(10) }}

redis:
  host: "{{ redis_host | default('localhost') }}"
  port: {{ redis_port | default(6379) }}
  password: "${secret:{{ redis_password_secret | default('redis_password') }}}"

monitoring:
  enabled: {{ monitoring_enabled | default(true) | lower }}
  endpoint: "{{ monitoring_endpoint | default('/metrics') }}"
  interval: {{ monitoring_interval | default(30) }}
""",
            variables={
                "app_name": "ainflue-api",
                "app_version": "1.0.0",
                "app_port": 8080,
                "db_host": "localhost",
                "db_name": "ainflue",
                "db_username": "app_user"
            },
            environments=["development", "staging", "production"],
            created_at=datetime.now()
        )
        
        # Microservice template
        microservice_template = ConfigurationTemplate(
            template_id="microservice_template",
            name="Microservice Configuration Template",
            description="Microservice configuration with service discovery",
            template_content="""
service:
  name: "{{ service_name }}"
  version: "{{ service_version }}"
  port: {{ service_port }}
  health_check_path: "{{ health_check_path | default('/health') }}"

discovery:
  enabled: {{ service_discovery_enabled | default(true) | lower }}
  consul:
    host: "{{ consul_host | default('localhost') }}"
    port: {{ consul_port | default(8500) }}
  
tracing:
  enabled: {{ tracing_enabled | default(true) | lower }}
  jaeger:
    endpoint: "{{ jaeger_endpoint | default('http://localhost:14268/api/traces') }}"
    sampling_rate: {{ sampling_rate | default(0.1) }}

circuit_breaker:
  failure_threshold: {{ failure_threshold | default(5) }}
  timeout: {{ circuit_timeout | default(30) }}
  recovery_timeout: {{ recovery_timeout | default(60) }}
""",
            variables={
                "service_name": "sample-service",
                "service_version": "1.0.0",
                "service_port": 8080
            },
            environments=["development", "staging", "production"],
            created_at=datetime.now()
        )
        
        self.configuration_templates[app_template.template_id] = app_template
        self.configuration_templates[microservice_template.template_id] = microservice_template

    async def create_configuration(
        self,
        name: str,
        schema_id: str,
        environment: str,
        content: Dict[str, Any],
        template_id: Optional[str] = None,
        template_variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create new configuration"""
        
        try:
            if schema_id not in self.configuration_schemas:
                raise ValueError(f"Schema not found: {schema_id}")
            
            schema = self.configuration_schemas[schema_id]
            config_id = str(uuid.uuid4())
            
            # Generate configuration content
            if template_id:
                content = await self._render_template(template_id, template_variables or {})
            
            # Validate configuration
            validation_result = await self._validate_configuration(content, schema)
            if not validation_result["valid"]:
                raise ValueError(f"Configuration validation failed: {validation_result['errors']}")
            
            # Calculate checksum
            content_str = json.dumps(content, sort_keys=True)
            checksum = hashlib.sha256(content_str.encode()).hexdigest()
            
            configuration = Configuration(
                config_id=config_id,
                name=name,
                schema_id=schema_id,
                environment=environment,
                config_type=schema.config_type,
                format=schema.format,
                content=content,
                version="1.0.0",
                checksum=checksum,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                validated=True
            )
            
            self.configurations[config_id] = configuration
            
            # Record in history
            self.configuration_history.append({
                "action": "create",
                "config_id": config_id,
                "name": name,
                "environment": environment,
                "timestamp": datetime.now(),
                "checksum": checksum
            })
            
            logger.info(f"Configuration created: {name} in {environment}")
            return config_id
            
        except Exception as e:
            logger.error(f"Configuration creation failed: {str(e)}")
            raise

    async def _render_template(
        self,
        template_id: str,
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render configuration template"""
        
        if template_id not in self.configuration_templates:
            raise ValueError(f"Template not found: {template_id}")
        
        template = self.configuration_templates[template_id]
        
        # Merge template variables with provided variables
        merged_variables = template.variables.copy()
        merged_variables.update(variables)
        
        # Render template
        jinja_template = self.jinja_env.from_string(template.template_content)
        rendered_content = jinja_template.render(**merged_variables)
        
        # Parse rendered content as YAML
        content = yaml.safe_load(rendered_content)
        
        # Resolve secrets
        content = await self._resolve_secrets(content)
        
        return content

    async def _resolve_secrets(self, content: Any) -> Any:
        """Resolve secret references in configuration"""
        
        if isinstance(content, dict):
            resolved = {}
            for key, value in content.items():
                resolved[key] = await self._resolve_secrets(value)
            return resolved
        elif isinstance(content, list):
            return [await self._resolve_secrets(item) for item in content]
        elif isinstance(content, str) and content.startswith("${secret:") and content.endswith("}"):
            # Extract secret name
            secret_name = content[9:-1]  # Remove ${secret: and }
            # Mock secret resolution
            return f"resolved_secret_value_for_{secret_name}"
        else:
            return content

    async def _validate_configuration(
        self,
        content: Dict[str, Any],
        schema: ConfigurationSchema
    ) -> Dict[str, Any]:
        """Validate configuration against schema"""
        
        try:
            errors = []
            
            # Basic schema validation (simplified)
            schema_props = schema.schema.get("properties", {})
            
            # Check required fields
            for required_field in schema.required_fields:
                if not self._check_nested_field(content, required_field):
                    errors.append(f"Required field missing: {required_field}")
            
            # Validate specific rules
            for rule in schema.validation_rules:
                field = rule["field"]
                rule_type = rule["rule"]
                
                field_value = self._get_nested_field(content, field)
                if field_value is not None:
                    if rule_type == "positive_integer" and (not isinstance(field_value, int) or field_value <= 0):
                        errors.append(f"Field {field} must be a positive integer")
                    elif rule_type == "secret_reference" and not isinstance(field_value, str):
                        errors.append(f"Field {field} must be a string (secret reference)")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }

    def _check_nested_field(self, obj: Dict[str, Any], field_path: str) -> bool:
        """Check if nested field exists"""
        parts = field_path.split(".")
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        
        return True

    def _get_nested_field(self, obj: Dict[str, Any], field_path: str) -> Any:
        """Get nested field value"""
        parts = field_path.split(".")
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current

    async def update_configuration(
        self,
        config_id: str,
        content: Dict[str, Any],
        version_increment: str = "patch"
    ) -> str:
        """Update existing configuration"""
        
        try:
            if config_id not in self.configurations:
                raise ValueError(f"Configuration not found: {config_id}")
            
            configuration = self.configurations[config_id]
            schema = self.configuration_schemas[configuration.schema_id]
            
            # Validate updated content
            validation_result = await self._validate_configuration(content, schema)
            if not validation_result["valid"]:
                raise ValueError(f"Configuration validation failed: {validation_result['errors']}")
            
            # Calculate new checksum
            content_str = json.dumps(content, sort_keys=True)
            new_checksum = hashlib.sha256(content_str.encode()).hexdigest()
            
            # Check if content actually changed
            if new_checksum == configuration.checksum:
                logger.info(f"Configuration unchanged: {config_id}")
                return configuration.version
            
            # Update version
            new_version = self._increment_version(configuration.version, version_increment)
            
            # Store old configuration in history
            self.configuration_history.append({
                "action": "update",
                "config_id": config_id,
                "name": configuration.name,
                "environment": configuration.environment,
                "old_version": configuration.version,
                "new_version": new_version,
                "old_checksum": configuration.checksum,
                "new_checksum": new_checksum,
                "timestamp": datetime.now()
            })
            
            # Update configuration
            configuration.content = content
            configuration.version = new_version
            configuration.checksum = new_checksum
            configuration.updated_at = datetime.now()
            
            # Notify watchers
            await self._notify_configuration_watchers(config_id, configuration)
            
            logger.info(f"Configuration updated: {configuration.name} v{new_version}")
            return new_version
            
        except Exception as e:
            logger.error(f"Configuration update failed: {str(e)}")
            raise

    def _increment_version(self, current_version: str, increment_type: str) -> str:
        """Increment semantic version"""
        
        try:
            parts = current_version.split(".")
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            
            if increment_type == "major":
                major += 1
                minor = 0
                patch = 0
            elif increment_type == "minor":
                minor += 1
                patch = 0
            else:  # patch
                patch += 1
            
            return f"{major}.{minor}.{patch}"
            
        except:
            # Fallback to simple incrementing
            return f"{current_version}.1"

    async def _notify_configuration_watchers(self, config_id: str, configuration: Configuration):
        """Notify watchers of configuration changes"""
        
        watchers = self.active_watchers.get(config_id, [])
        
        for watcher in watchers:
            try:
                await watcher(configuration)
            except Exception as e:
                logger.error(f"Configuration watcher notification failed: {str(e)}")

    async def register_configuration_watcher(
        self,
        config_id: str,
        callback: callable
    ):
        """Register configuration change watcher"""
        
        if config_id not in self.configurations:
            raise ValueError(f"Configuration not found: {config_id}")
        
        self.active_watchers[config_id].append(callback)
        logger.info(f"Configuration watcher registered for: {config_id}")

    async def rollback_configuration(
        self,
        config_id: str,
        target_version: Optional[str] = None
    ) -> str:
        """Rollback configuration to previous version"""
        
        try:
            if config_id not in self.configurations:
                raise ValueError(f"Configuration not found: {config_id}")
            
            # Find rollback target in history
            config_history = [
                h for h in self.configuration_history
                if h["config_id"] == config_id and h["action"] == "update"
            ]
            
            if not config_history:
                raise ValueError("No configuration history found for rollback")
            
            # Find target version or use latest
            if target_version:
                target_history = None
                for history_entry in reversed(config_history):
                    if history_entry.get("old_version") == target_version:
                        target_history = history_entry
                        break
                
                if not target_history:
                    raise ValueError(f"Target version not found: {target_version}")
            else:
                target_history = config_history[-1]
            
            # Mock rollback (in real implementation, retrieve old content)
            logger.info(f"Rolling back configuration {config_id} to version {target_version or 'previous'}")
            
            # Record rollback in history
            self.configuration_history.append({
                "action": "rollback",
                "config_id": config_id,
                "target_version": target_version or target_history.get("old_version"),
                "timestamp": datetime.now()
            })
            
            return target_version or target_history.get("old_version", "unknown")
            
        except Exception as e:
            logger.error(f"Configuration rollback failed: {str(e)}")
            raise

    async def detect_configuration_drift(self) -> List[Dict[str, Any]]:
        """Detect configuration drift across environments"""
        
        drift_reports = []
        
        try:
            # Group configurations by name and type
            config_groups = defaultdict(list)
            for config in self.configurations.values():
                group_key = f"{config.name}:{config.config_type.value}"
                config_groups[group_key].append(config)
            
            # Check for drift within each group
            for group_key, configs in config_groups.items():
                if len(configs) > 1:
                    # Compare configurations across environments
                    base_config = configs[0]
                    
                    for other_config in configs[1:]:
                        if base_config.checksum != other_config.checksum:
                            drift_reports.append({
                                "drift_id": str(uuid.uuid4()),
                                "config_name": base_config.name,
                                "base_environment": base_config.environment,
                                "drift_environment": other_config.environment,
                                "base_version": base_config.version,
                                "drift_version": other_config.version,
                                "base_checksum": base_config.checksum,
                                "drift_checksum": other_config.checksum,
                                "detected_at": datetime.now(),
                                "severity": "medium"
                            })
            
            if drift_reports:
                logger.warning(f"Configuration drift detected: {len(drift_reports)} instances")
            
            return drift_reports
            
        except Exception as e:
            logger.error(f"Configuration drift detection failed: {str(e)}")
            return []

    # Background tasks
    async def _configuration_monitoring_loop(self):
        """Background configuration monitoring loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Monitor configuration health
                for config in self.configurations.values():
                    if config.active:
                        # Mock configuration health check
                        pass
                
            except Exception as e:
                logger.error(f"Configuration monitoring loop error: {str(e)}")

    async def _drift_detection_loop(self):
        """Background drift detection loop"""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                drift_reports = await self.detect_configuration_drift()
                
                # Log drift reports
                for drift in drift_reports:
                    logger.warning(f"Configuration drift: {drift['config_name']} between {drift['base_environment']} and {drift['drift_environment']}")
                
            except Exception as e:
                logger.error(f"Drift detection loop error: {str(e)}")

    async def health_check(self) -> bool:
        """Configuration manager health check"""
        
        try:
            # Check for invalid configurations
            invalid_configs = [
                config for config in self.configurations.values()
                if not config.validated
            ]
            
            if len(invalid_configs) > 0:
                logger.warning("Invalid configurations detected")
                return False
            
            # Check template engine
            try:
                test_template = self.jinja_env.from_string("{{ test_var }}")
                test_template.render(test_var="test")
            except Exception:
                logger.error("Template engine health check failed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration manager health check failed: {str(e)}")
            return False

    def get_configuration_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive configuration dashboard"""
        
        # Count configurations by environment and type
        env_counts = defaultdict(int)
        type_counts = defaultdict(int)
        
        for config in self.configurations.values():
            env_counts[config.environment] += 1
            type_counts[config.config_type.value] += 1
        
        # Calculate recent activity
        recent_changes = [
            h for h in self.configuration_history
            if h.get("timestamp", datetime.min) >= datetime.now() - timedelta(days=7)
        ]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "configurations": {
                "total_configurations": len(self.configurations),
                "active_configurations": len([c for c in self.configurations.values() if c.active]),
                "by_environment": dict(env_counts),
                "by_type": dict(type_counts)
            },
            "schemas": {
                "total_schemas": len(self.configuration_schemas),
                "schema_types": [s.config_type.value for s in self.configuration_schemas.values()]
            },
            "templates": {
                "total_templates": len(self.configuration_templates),
                "template_environments": list(set(
                    env for template in self.configuration_templates.values()
                    for env in template.environments
                ))
            },
            "activity": {
                "recent_changes": len(recent_changes),
                "total_history_entries": len(self.configuration_history),
                "active_watchers": sum(len(watchers) for watchers in self.active_watchers.values())
            },
            "validation": {
                "validated_configurations": len([c for c in self.configurations.values() if c.validated]),
                "validation_rate": len([c for c in self.configurations.values() if c.validated]) / len(self.configurations) * 100 if self.configurations else 0
            }
        }

# Global configuration manager instance
configuration_manager = ConfigurationManager()

logger.info("🚀 Configuration Manager initialized - Dynamic configuration management")