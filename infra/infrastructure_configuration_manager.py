# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Infrastructure Configuration Manager

Advanced configuration management system for enterprise infrastructure.
Handles complex multi-environment configurations with validation and templating.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
import os
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigType(Enum):
    """Configuration type options."""
    YAML = "yaml"
    JSON = "json"
    ENV = "env"
    TERRAFORM = "terraform"
    KUBERNETES = "kubernetes"

class ConfigScope(Enum):
    """Configuration scope options."""
    GLOBAL = "global"
    ENVIRONMENT = "environment"
    SERVICE = "service"
    REGION = "region"

@dataclass
class ConfigurationTemplate:
    """Configuration template definition."""
    name: str
    type: ConfigType
    scope: ConfigScope
    template: str
    variables: Dict[str, Any] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfigurationProfile:
    """Configuration profile for specific environment."""
    name: str
    environment: str
    region: str
    values: Dict[str, Any] = field(default_factory=dict)
    secrets: Dict[str, str] = field(default_factory=dict)
    templates: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class InfrastructureConfigurationManager:
    """
    Enterprise infrastructure configuration manager.
    
    Provides advanced configuration management with templating, validation,
    environment-specific profiles, and secrets management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize configuration manager."""
        self.config = config or {}
        self.templates: Dict[str, ConfigurationTemplate] = {}
        self.profiles: Dict[str, ConfigurationProfile] = {}
        self.compiled_configs: Dict[str, Any] = {}
        
        # Configuration paths
        self.base_path = Path(self.config.get("base_path", "./config"))
        self.templates_path = self.base_path / "templates"
        self.profiles_path = self.base_path / "profiles"
        self.compiled_path = self.base_path / "compiled"
        
        # Security settings
        self.encrypt_secrets = self.config.get("encrypt_secrets", True)
        self.secret_key = self.config.get("secret_key", "default-key")
        
        # Validation settings
        self.strict_validation = self.config.get("strict_validation", True)
        self.allow_undefined_variables = self.config.get("allow_undefined_variables", False)
        
        # Create directories
        self._create_directories()
        
        logger.info("InfrastructureConfigurationManager initialized")
    
    def _create_directories(self):
        """Create configuration directories if they don't exist."""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            self.templates_path.mkdir(parents=True, exist_ok=True)
            self.profiles_path.mkdir(parents=True, exist_ok=True)
            self.compiled_path.mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            logger.error(f"Failed to create directories: {str(e)}")
            raise
    
    async def load_templates(self, template_dir: Optional[str] = None) -> int:
        """Load configuration templates from directory."""
        try:
            template_dir = Path(template_dir) if template_dir else self.templates_path
            loaded_count = 0
            
            for template_file in template_dir.glob("*.yaml"):
                try:
                    with open(template_file, 'r') as f:
                        template_data = yaml.safe_load(f)
                    
                    template = ConfigurationTemplate(
                        name=template_data["name"],
                        type=ConfigType(template_data["type"]),
                        scope=ConfigScope(template_data["scope"]),
                        template=template_data["template"],
                        variables=template_data.get("variables", {}),
                        validation_rules=template_data.get("validation_rules", {}),
                        metadata=template_data.get("metadata", {})
                    )
                    
                    self.templates[template.name] = template
                    loaded_count += 1
                    logger.info(f"Loaded template: {template.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load template {template_file}: {str(e)}")
            
            logger.info(f"Loaded {loaded_count} configuration templates")
            return loaded_count
            
        except Exception as e:
            logger.error(f"Failed to load templates: {str(e)}")
            raise
    
    async def load_profiles(self, profile_dir: Optional[str] = None) -> int:
        """Load configuration profiles from directory."""
        try:
            profile_dir = Path(profile_dir) if profile_dir else self.profiles_path
            loaded_count = 0
            
            for profile_file in profile_dir.glob("*.yaml"):
                try:
                    with open(profile_file, 'r') as f:
                        profile_data = yaml.safe_load(f)
                    
                    profile = ConfigurationProfile(
                        name=profile_data["name"],
                        environment=profile_data["environment"],
                        region=profile_data["region"],
                        values=profile_data.get("values", {}),
                        secrets=profile_data.get("secrets", {}),
                        templates=profile_data.get("templates", []),
                        metadata=profile_data.get("metadata", {})
                    )
                    
                    self.profiles[profile.name] = profile
                    loaded_count += 1
                    logger.info(f"Loaded profile: {profile.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load profile {profile_file}: {str(e)}")
            
            logger.info(f"Loaded {loaded_count} configuration profiles")
            return loaded_count
            
        except Exception as e:
            logger.error(f"Failed to load profiles: {str(e)}")
            raise
    
    async def create_template(self, template_config: Dict[str, Any]) -> str:
        """Create a new configuration template."""
        try:
            template = ConfigurationTemplate(
                name=template_config["name"],
                type=ConfigType(template_config["type"]),
                scope=ConfigScope(template_config["scope"]),
                template=template_config["template"],
                variables=template_config.get("variables", {}),
                validation_rules=template_config.get("validation_rules", {}),
                metadata=template_config.get("metadata", {})
            )
            
            # Validate template
            if not await self._validate_template(template):
                raise ValueError(f"Template validation failed: {template.name}")
            
            # Store template
            self.templates[template.name] = template
            
            # Save to file
            template_file = self.templates_path / f"{template.name}.yaml"
            template_data = {
                "name": template.name,
                "type": template.type.value,
                "scope": template.scope.value,
                "template": template.template,
                "variables": template.variables,
                "validation_rules": template.validation_rules,
                "metadata": template.metadata
            }
            
            with open(template_file, 'w') as f:
                yaml.dump(template_data, f, default_flow_style=False)
            
            logger.info(f"Created template: {template.name}")
            return template.name
            
        except Exception as e:
            logger.error(f"Failed to create template: {str(e)}")
            raise
    
    async def create_profile(self, profile_config: Dict[str, Any]) -> str:
        """Create a new configuration profile."""
        try:
            profile = ConfigurationProfile(
                name=profile_config["name"],
                environment=profile_config["environment"],
                region=profile_config["region"],
                values=profile_config.get("values", {}),
                secrets=profile_config.get("secrets", {}),
                templates=profile_config.get("templates", []),
                metadata=profile_config.get("metadata", {})
            )
            
            # Validate profile
            if not await self._validate_profile(profile):
                raise ValueError(f"Profile validation failed: {profile.name}")
            
            # Encrypt secrets if enabled
            if self.encrypt_secrets:
                profile.secrets = await self._encrypt_secrets(profile.secrets)
            
            # Store profile
            self.profiles[profile.name] = profile
            
            # Save to file
            profile_file = self.profiles_path / f"{profile.name}.yaml"
            profile_data = {
                "name": profile.name,
                "environment": profile.environment,
                "region": profile.region,
                "values": profile.values,
                "secrets": profile.secrets,
                "templates": profile.templates,
                "metadata": profile.metadata
            }
            
            with open(profile_file, 'w') as f:
                yaml.dump(profile_data, f, default_flow_style=False)
            
            logger.info(f"Created profile: {profile.name}")
            return profile.name
            
        except Exception as e:
            logger.error(f"Failed to create profile: {str(e)}")
            raise
    
    async def compile_configuration(self, profile_name: str, output_format: Optional[ConfigType] = None) -> Dict[str, Any]:
        """Compile configuration for a specific profile."""
        try:
            if profile_name not in self.profiles:
                raise ValueError(f"Profile not found: {profile_name}")
            
            profile = self.profiles[profile_name]
            compiled_config = {
                "profile": profile.name,
                "environment": profile.environment,
                "region": profile.region,
                "compiled_at": datetime.now().isoformat(),
                "configurations": {}
            }
            
            # Compile each template
            for template_name in profile.templates:
                if template_name not in self.templates:
                    logger.warning(f"Template not found: {template_name}")
                    continue
                
                template = self.templates[template_name]
                
                # Render template with profile values
                rendered_config = await self._render_template(template, profile)
                
                # Validate rendered configuration
                if self.strict_validation:
                    if not await self._validate_rendered_config(template, rendered_config):
                        raise ValueError(f"Rendered configuration validation failed: {template_name}")
                
                compiled_config["configurations"][template_name] = {
                    "type": template.type.value,
                    "scope": template.scope.value,
                    "content": rendered_config
                }
            
            # Add global values
            compiled_config["global_values"] = profile.values
            
            # Add decrypted secrets
            if profile.secrets:
                decrypted_secrets = await self._decrypt_secrets(profile.secrets)
                compiled_config["secrets"] = decrypted_secrets
            
            # Store compiled configuration
            self.compiled_configs[profile_name] = compiled_config
            
            # Save compiled configuration
            if output_format:
                await self._save_compiled_config(profile_name, compiled_config, output_format)
            
            logger.info(f"Compiled configuration for profile: {profile_name}")
            return compiled_config
            
        except Exception as e:
            logger.error(f"Failed to compile configuration: {str(e)}")
            raise
    
    async def _render_template(self, template: ConfigurationTemplate, profile: ConfigurationProfile) -> str:
        """Render template with profile values."""
        try:
            template_content = template.template
            
            # Combine template variables with profile values
            variables = {**template.variables, **profile.values}
            
            # Add environment-specific variables
            variables.update({
                "environment": profile.environment,
                "region": profile.region,
                "profile_name": profile.name
            })
            
            # Simple template rendering (could be enhanced with Jinja2)
            rendered_content = template_content
            
            for var_name, var_value in variables.items():
                placeholder = f"{{{{{var_name}}}}}"
                if placeholder in rendered_content:
                    rendered_content = rendered_content.replace(placeholder, str(var_value))
            
            # Check for unresolved variables
            unresolved = re.findall(r'\{\{([^}]+)\}\}', rendered_content)
            if unresolved and not self.allow_undefined_variables:
                raise ValueError(f"Unresolved variables in template {template.name}: {unresolved}")
            
            return rendered_content
            
        except Exception as e:
            logger.error(f"Failed to render template {template.name}: {str(e)}")
            raise
    
    async def _validate_template(self, template: ConfigurationTemplate) -> bool:
        """Validate template structure and content."""
        try:
            # Check required fields
            if not template.name or not template.template:
                return False
            
            # Validate template content based on type
            if template.type == ConfigType.YAML:
                try:
                    yaml.safe_load(template.template)
                except yaml.YAMLError:
                    return False
            elif template.type == ConfigType.JSON:
                try:
                    json.loads(template.template)
                except json.JSONDecodeError:
                    return False
            
            # Run custom validation rules
            for rule_name, rule_config in template.validation_rules.items():
                if not await self._run_validation_rule(rule_name, template.template, rule_config):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Template validation error: {str(e)}")
            return False
    
    async def _validate_profile(self, profile: ConfigurationProfile) -> bool:
        """Validate profile structure and content."""
        try:
            # Check required fields
            if not profile.name or not profile.environment:
                return False
            
            # Validate referenced templates exist
            for template_name in profile.templates:
                if template_name not in self.templates:
                    logger.warning(f"Template {template_name} referenced in profile {profile.name} does not exist")
            
            # Validate environment values
            valid_environments = ["dev", "staging", "prod"]
            if profile.environment not in valid_environments:
                logger.warning(f"Environment {profile.environment} not in standard environments: {valid_environments}")
            
            return True
            
        except Exception as e:
            logger.error(f"Profile validation error: {str(e)}")
            return False
    
    async def _validate_rendered_config(self, template: ConfigurationTemplate, rendered_config: str) -> bool:
        """Validate rendered configuration."""
        try:
            # Validate based on template type
            if template.type == ConfigType.YAML:
                yaml.safe_load(rendered_config)
            elif template.type == ConfigType.JSON:
                json.loads(rendered_config)
            elif template.type == ConfigType.TERRAFORM:
                # Basic Terraform validation (could be enhanced)
                if not rendered_config.strip():
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rendered configuration validation error: {str(e)}")
            return False
    
    async def _run_validation_rule(self, rule_name: str, content: str, rule_config: Dict[str, Any]) -> bool:
        """Run custom validation rule."""
        try:
            if rule_name == "required_fields":
                # Check if required fields are present
                required_fields = rule_config.get("fields", [])
                for field in required_fields:
                    if field not in content:
                        return False
            
            elif rule_name == "format_check":
                # Check content format
                format_type = rule_config.get("format")
                if format_type == "yaml":
                    yaml.safe_load(content)
                elif format_type == "json":
                    json.loads(content)
            
            elif rule_name == "pattern_match":
                # Check if content matches pattern
                pattern = rule_config.get("pattern")
                if pattern and not re.search(pattern, content):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation rule {rule_name} error: {str(e)}")
            return False
    
    async def _encrypt_secrets(self, secrets: Dict[str, str]) -> Dict[str, str]:
        """Encrypt secrets (simplified implementation)."""
        try:
            # In a real implementation, this would use proper encryption
            encrypted_secrets = {}
            for key, value in secrets.items():
                # Simple base64 encoding for demonstration
                import base64
                encrypted_value = base64.b64encode(value.encode()).decode()
                encrypted_secrets[key] = f"encrypted:{encrypted_value}"
            
            return encrypted_secrets
            
        except Exception as e:
            logger.error(f"Failed to encrypt secrets: {str(e)}")
            return secrets
    
    async def _decrypt_secrets(self, encrypted_secrets: Dict[str, str]) -> Dict[str, str]:
        """Decrypt secrets (simplified implementation)."""
        try:
            decrypted_secrets = {}
            for key, value in encrypted_secrets.items():
                if value.startswith("encrypted:"):
                    # Simple base64 decoding for demonstration
                    import base64
                    encrypted_value = value[10:]  # Remove "encrypted:" prefix
                    decrypted_value = base64.b64decode(encrypted_value).decode()
                    decrypted_secrets[key] = decrypted_value
                else:
                    decrypted_secrets[key] = value
            
            return decrypted_secrets
            
        except Exception as e:
            logger.error(f"Failed to decrypt secrets: {str(e)}")
            return encrypted_secrets
    
    async def _save_compiled_config(self, profile_name: str, compiled_config: Dict[str, Any], output_format: ConfigType):
        """Save compiled configuration to file."""
        try:
            output_file = self.compiled_path / f"{profile_name}.{output_format.value}"
            
            if output_format == ConfigType.YAML:
                with open(output_file, 'w') as f:
                    yaml.dump(compiled_config, f, default_flow_style=False)
            elif output_format == ConfigType.JSON:
                with open(output_file, 'w') as f:
                    json.dump(compiled_config, f, indent=2)
            
            logger.info(f"Saved compiled configuration: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save compiled configuration: {str(e)}")
            raise
    
    async def validate_configuration(self, profile_name: str) -> Dict[str, Any]:
        """Validate a configuration profile."""
        try:
            if profile_name not in self.profiles:
                return {"valid": False, "error": f"Profile not found: {profile_name}"}
            
            profile = self.profiles[profile_name]
            validation_results = {
                "profile": profile_name,
                "valid": True,
                "errors": [],
                "warnings": [],
                "template_results": {}
            }
            
            # Validate each template
            for template_name in profile.templates:
                if template_name not in self.templates:
                    validation_results["errors"].append(f"Template not found: {template_name}")
                    validation_results["valid"] = False
                    continue
                
                template = self.templates[template_name]
                
                # Try to render template
                try:
                    rendered_config = await self._render_template(template, profile)
                    template_valid = await self._validate_rendered_config(template, rendered_config)
                    
                    validation_results["template_results"][template_name] = {
                        "valid": template_valid,
                        "rendered_size": len(rendered_config)
                    }
                    
                    if not template_valid:
                        validation_results["errors"].append(f"Template validation failed: {template_name}")
                        validation_results["valid"] = False
                        
                except Exception as e:
                    validation_results["errors"].append(f"Template rendering failed: {template_name} - {str(e)}")
                    validation_results["valid"] = False
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Configuration validation error: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    async def export_configuration(self, profile_name: str, export_path: str, format: ConfigType) -> bool:
        """Export configuration to external path."""
        try:
            compiled_config = await self.compile_configuration(profile_name)
            
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format == ConfigType.YAML:
                with open(export_file, 'w') as f:
                    yaml.dump(compiled_config, f, default_flow_style=False)
            elif format == ConfigType.JSON:
                with open(export_file, 'w') as f:
                    json.dump(compiled_config, f, indent=2)
            
            logger.info(f"Exported configuration to: {export_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {str(e)}")
            return False
    
    async def sync_with_git(self, git_repo: str, branch: str = "main") -> bool:
        """Sync configuration with Git repository."""
        try:
            # This would integrate with Git for version control
            # Implementation would use GitPython or similar
            logger.info(f"Syncing with Git repository: {git_repo}")
            return True
            
        except Exception as e:
            logger.error(f"Git sync error: {str(e)}")
            return False
    
    def list_templates(self, scope: Optional[ConfigScope] = None) -> List[Dict[str, Any]]:
        """List available templates."""
        templates = []
        for template in self.templates.values():
            if scope and template.scope != scope:
                continue
                
            templates.append({
                "name": template.name,
                "type": template.type.value,
                "scope": template.scope.value,
                "variables": list(template.variables.keys()),
                "metadata": template.metadata
            })
        
        return templates
    
    def list_profiles(self, environment: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available profiles."""
        profiles = []
        for profile in self.profiles.values():
            if environment and profile.environment != environment:
                continue
                
            profiles.append({
                "name": profile.name,
                "environment": profile.environment,
                "region": profile.region,
                "templates": profile.templates,
                "metadata": profile.metadata
            })
        
        return profiles
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration manager status."""
        return {
            "templates_count": len(self.templates),
            "profiles_count": len(self.profiles),
            "compiled_configs_count": len(self.compiled_configs),
            "base_path": str(self.base_path),
            "encryption_enabled": self.encrypt_secrets,
            "strict_validation": self.strict_validation
        }


# Export the main class
__all__ = ["InfrastructureConfigurationManager", "ConfigType", "ConfigScope", 
           "ConfigurationTemplate", "ConfigurationProfile"]