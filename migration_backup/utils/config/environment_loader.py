"""
Environment Configuration Loader
================================

Enterprise environment-aware configuration loading with automatic detection
and environment-specific overrides.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class Environment(Enum):
    """Supported environments."""
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"
    TESTING = "testing"
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    CLOUD = "cloud"

class EnvironmentLoader:
    """
    Enterprise environment configuration loader.
    
    Automatically detects environment and loads appropriate configurations.
    Supports multiple environment detection methods and override strategies.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path(__file__).parent
        self.current_environment = self._detect_environment()
        self._environment_configs = {}
        self._override_chain = []
        
    def _detect_environment(self) -> Environment:
        """
        Detect current environment using multiple detection strategies.
        
        Returns:
            Environment: Detected environment
        """
        # Priority order for environment detection
        detection_methods = [
            self._detect_from_env_var,
            self._detect_from_hostname,
            self._detect_from_platform,
            self._detect_from_file_markers
        ]
        
        for method in detection_methods:
            try:
                env = method()
                if env:
                    logger.info(f"Environment detected as {env.value} using {method.__name__}")
                    return env
            except Exception as e:
                logger.warning(f"Environment detection method {method.__name__} failed: {e}")
                
        # Default to development
        logger.info("Defaulting to development environment")
        return Environment.DEVELOPMENT
        
    def _detect_from_env_var(self) -> Optional[Environment]:
        """Detect environment from environment variables."""
        env_vars = [
            'IA CHÉRIES_ENV',
            'ENVIRONMENT', 
            'ENV',
            'STAGE',
            'DEPLOYMENT_ENV'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                try:
                    return Environment(value.lower())
                except ValueError:
                    # Try mapping common aliases
                    aliases = {
                        'dev': Environment.DEVELOPMENT,
                        'devel': Environment.DEVELOPMENT,
                        'develop': Environment.DEVELOPMENT,
                        'stage': Environment.STAGING,
                        'staging': Environment.STAGING,
                        'prod': Environment.PRODUCTION,
                        'production': Environment.PRODUCTION,
                        'test': Environment.TESTING,
                        'testing': Environment.TESTING
                    }
                    if value.lower() in aliases:
                        return aliases[value.lower()]
                        
        return None
        
    def _detect_from_hostname(self) -> Optional[Environment]:
        """Detect environment from hostname patterns."""
        import socket
        hostname = socket.gethostname().lower()
        
        patterns = {
            Environment.DEVELOPMENT: ['dev', 'development', 'local'],
            Environment.STAGING: ['stage', 'staging', 'stg'],
            Environment.PRODUCTION: ['prod', 'production', 'live'],
            Environment.TESTING: ['test', 'testing'],
            Environment.DOCKER: ['docker', 'container'],
            Environment.KUBERNETES: ['k8s', 'kubernetes', 'kube'],
            Environment.CLOUD: ['aws', 'azure', 'gcp', 'cloud']
        }
        
        for env, keywords in patterns.items():
            if any(keyword in hostname for keyword in keywords):
                return env
                
        return None
        
    def _detect_from_platform(self) -> Optional[Environment]:
        """Detect environment from platform indicators."""
        # Check for containerization
        if os.path.exists('/.dockerenv'):
            return Environment.DOCKER
            
        # Check for Kubernetes
        if os.getenv('KUBERNETES_SERVICE_HOST'):
            return Environment.KUBERNETES
            
        # Check for cloud providers
        cloud_indicators = {
            'AWS_REGION': Environment.CLOUD,
            'AZURE_RESOURCE_GROUP': Environment.CLOUD,
            'GOOGLE_CLOUD_PROJECT': Environment.CLOUD
        }
        
        for var, env in cloud_indicators.items():
            if os.getenv(var):
                return env
                
        return None
        
    def _detect_from_file_markers(self) -> Optional[Environment]:
        """Detect environment from file markers."""
        markers = {
            '.development': Environment.DEVELOPMENT,
            '.staging': Environment.STAGING,
            '.production': Environment.PRODUCTION,
            '.testing': Environment.TESTING,
            'docker-compose.yml': Environment.DOCKER,
            'deployment.yaml': Environment.KUBERNETES
        }
        
        # Check in current directory and parent directories
        current_path = Path.cwd()
        for _ in range(5):  # Check up to 5 levels up
            for marker, env in markers.items():
                if (current_path / marker).exists():
                    return env
            current_path = current_path.parent
            if current_path.parent == current_path:  # Reached root
                break
                
        return None
        
    def load_environment_config(self) -> Dict[str, Any]:
        """
        Load configuration for the current environment.
        
        Returns:
            Dict containing environment-specific configuration
        """
        config = {}
        
        # Load base environment configuration
        base_config = self._load_base_environment_config()
        if base_config:
            config.update(base_config)
            
        # Load specific environment configuration
        env_config = self._load_specific_environment_config()
        if env_config:
            self._deep_merge(config, env_config)
            
        # Apply overrides
        for override in self._override_chain:
            self._deep_merge(config, override)
            
        # Store loaded configuration
        self._environment_configs[self.current_environment] = config
        
        return config
        
    def _load_base_environment_config(self) -> Dict[str, Any]:
        """Load base environment configuration."""
        base_files = [
            'environment_config.yaml',
            'base_config.yaml',
            'default_config.yaml'
        ]
        
        for filename in base_files:
            config_path = self.base_path / filename
            if config_path.exists():
                return self._load_yaml_file(config_path)
                
        return {}
        
    def _load_specific_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration."""
        env_files = [
            f"{self.current_environment.value}_config.yaml",
            f"{self.current_environment.value}.yaml",
            f"config.{self.current_environment.value}.yaml"
        ]
        
        for filename in env_files:
            config_path = self.base_path / filename
            if config_path.exists():
                return self._load_yaml_file(config_path)
                
        return {}
        
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        try:
            import yaml
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove docstring if present
                if content.startswith('"""'):
                    lines = content.split('\n')
                    start_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip().endswith('"""') and i > 0:
                            start_idx = i + 1
                            break
                    content = '\n'.join(lines[start_idx:])
                    
                return yaml.safe_load(content) or {}
        except Exception as e:
            logger.error(f"Failed to load YAML file {file_path}: {e}")
            return {}
            
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
                
    def add_override(self, override_config: Dict[str, Any]) -> None:
        """Add configuration override."""
        self._override_chain.append(override_config)
        
    def clear_overrides(self) -> None:
        """Clear all configuration overrides."""
        self._override_chain.clear()
        
    def get_environment(self) -> Environment:
        """Get current environment."""
        return self.current_environment
        
    def set_environment(self, environment: Environment) -> None:
        """Set current environment."""
        self.current_environment = environment
        
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.current_environment == Environment.DEVELOPMENT
        
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.current_environment == Environment.STAGING
        
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.current_environment == Environment.PRODUCTION
        
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.current_environment == Environment.TESTING
        
    def get_environment_variables(self) -> Dict[str, str]:
        """Get all environment variables as dictionary."""
        return dict(os.environ)
        
    def get_required_env_vars(self) -> List[str]:
        """Get list of required environment variables."""
        required_vars = {
            Environment.DEVELOPMENT: [
                'IA CHÉRIES_DEV_DATABASE_URL',
                'IA CHÉRIES_DEV_REDIS_URL'
            ],
            Environment.STAGING: [
                'IA CHÉRIES_STAGING_DATABASE_URL',
                'IA CHÉRIES_STAGING_REDIS_URL'
            ],
            Environment.PRODUCTION: [
                'IA CHÉRIES_PROD_DATABASE_URL',
                'IA CHÉRIES_PROD_REDIS_URL',
                'IA CHÉRIES_SECRET_KEY',
                'IA CHÉRIES_JWT_SECRET'
            ],
            Environment.TESTING: [
                'IA CHÉRIES_TEST_DATABASE_URL'
            ]
        }
        
        return required_vars.get(self.current_environment, [])
        
    def validate_environment(self) -> bool:
        """Validate that environment is properly configured."""
        required_vars = self.get_required_env_vars()
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return False
            
        return True
        
    def get_config_for_environment(self, environment: Environment) -> Dict[str, Any]:
        """Get configuration for specific environment."""
        if environment in self._environment_configs:
            return self._environment_configs[environment]
            
        # Load configuration for the specified environment
        current_env = self.current_environment
        self.current_environment = environment
        config = self.load_environment_config()
        self.current_environment = current_env
        
        return config