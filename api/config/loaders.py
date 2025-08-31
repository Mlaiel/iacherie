"""Configuration Loaders - IA Influencer Agent Platform
Advanced configuration loading system supporting multiple formats and sources

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""import os
import json
import yaml
import toml
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from abc import ABC, abstractmethod
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import redis
import requests
from urllib.parse import urlparse
import configparser
from dataclasses import asdict
import logging

logger = logging.getLogger(__name__)


class ConfigurationLoader(ABC):
    """Abstract base class for configuration loaders"""    
    @abstractmethod
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from source"""        pass
    
    @abstractmethod
    def supports(self, source: str) -> bool:
        """Check if loader supports the given source"""        pass
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries"""        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result


class YAMLConfigLoader(ConfigurationLoader):
    """YAML configuration file loader"""    
    def supports(self, source: str) -> bool:
        """Check if source is a YAML file"""        return source.lower().endswith(('.yaml', '.yml'))
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""        try:
            file_path = Path(source).expanduser()
            if not file_path.exists():
                raise FileNotFoundError(f"YAML config file not found: {source}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            logger.info(f"Loaded configuration from YAML file: {source}")
            return self._process_config(config)
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML config file {source}: {e}")
            raise ValueError(f"Invalid YAML syntax in {source}: {e}")
        except Exception as e:
            logger.error(f"Error loading YAML config file {source}: {e}")
            raise
    
    def _process_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process loaded configuration for environment variable substitution"""        return self._substitute_env_vars(config)
    
    def _substitute_env_vars(self, obj: Any) -> Any:
        """Recursively substitute environment variables in configuration"""        if isinstance(obj, dict):
            return {key: self._substitute_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            # Extract env var name and default value
            env_expr = obj[2:-1]  # Remove ${ and }
            if ':' in env_expr:
                env_var, default = env_expr.split(':', 1)
            else:
                env_var, default = env_expr, None
            
            return os.getenv(env_var, default)
        else:
            return obj


class JSONConfigLoader(ConfigurationLoader):
    """JSON configuration file loader"""    
    def supports(self, source: str) -> bool:
        """Check if source is a JSON file"""        return source.lower().endswith('.json')
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""        try:
            file_path = Path(source).expanduser()
            if not file_path.exists():
                raise FileNotFoundError(f"JSON config file not found: {source}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"Loaded configuration from JSON file: {source}")
            return self._process_config(config)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON config file {source}: {e}")
            raise ValueError(f"Invalid JSON syntax in {source}: {e}")
        except Exception as e:
            logger.error(f"Error loading JSON config file {source}: {e}")
            raise
    
    def _process_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process loaded configuration"""        return self._substitute_env_vars(config)
    
    def _substitute_env_vars(self, obj: Any) -> Any:
        """Recursively substitute environment variables in configuration"""        if isinstance(obj, dict):
            return {key: self._substitute_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            env_expr = obj[2:-1]
            if ':' in env_expr:
                env_var, default = env_expr.split(':', 1)
            else:
                env_var, default = env_expr, None
            return os.getenv(env_var, default)
        else:
            return obj


class TOMLConfigLoader(ConfigurationLoader):
    """TOML configuration file loader"""    
    def supports(self, source: str) -> bool:
        """Check if source is a TOML file"""        return source.lower().endswith('.toml')
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from TOML file"""        try:
            file_path = Path(source).expanduser()
            if not file_path.exists():
                raise FileNotFoundError(f"TOML config file not found: {source}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                config = toml.load(f)
            
            logger.info(f"Loaded configuration from TOML file: {source}")
            return self._process_config(config)
            
        except toml.TomlDecodeError as e:
            logger.error(f"Error parsing TOML config file {source}: {e}")
            raise ValueError(f"Invalid TOML syntax in {source}: {e}")
        except Exception as e:
            logger.error(f"Error loading TOML config file {source}: {e}")
            raise
    
    def _process_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process loaded configuration"""        return config  # TOML doesn't support env var substitution by default


class INIConfigLoader(ConfigurationLoader):
    """INI configuration file loader"""    
    def supports(self, source: str) -> bool:
        """Check if source is an INI file"""        return source.lower().endswith(('.ini', '.cfg', '.conf'))
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from INI file"""        try:
            file_path = Path(source).expanduser()
            if not file_path.exists():
                raise FileNotFoundError(f"INI config file not found: {source}")
            
            parser = configparser.ConfigParser()
            parser.read(file_path, encoding='utf-8')
            
            # Convert to nested dictionary
            config = {}
            for section_name in parser.sections():
                config[section_name] = dict(parser[section_name])
            
            logger.info(f"Loaded configuration from INI file: {source}")
            return self._process_config(config)
            
        except configparser.Error as e:
            logger.error(f"Error parsing INI config file {source}: {e}")
            raise ValueError(f"Invalid INI syntax in {source}: {e}")
        except Exception as e:
            logger.error(f"Error loading INI config file {source}: {e}")
            raise
    
    def _process_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process loaded configuration with type conversion"""        return self._convert_types(config)
    
    def _convert_types(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert string values to appropriate types"""        result = {}
        for key, value in config.items():
            if isinstance(value, dict):
                result[key] = self._convert_types(value)
            elif isinstance(value, str):
                result[key] = self._convert_string_value(value)
            else:
                result[key] = value
        return result
    
    def _convert_string_value(self, value: str) -> Any:
        """Convert string value to appropriate type"""        # Boolean conversion
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Numeric conversion
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # List conversion (comma-separated)
        if ',' in value:
            return [item.strip() for item in value.split(',')]
        
        return value


class EnvironmentConfigLoader(ConfigurationLoader):
    """Environment variables configuration loader"""    
    def __init__(self, prefix: str = "IA_INFLUENCER_", separator: str = "__"):
        """        Initialize environment loader
        
        Args:
            prefix: Environment variable prefix to filter
            separator: Separator for nested keys (e.g., DB__HOST -> db.host)
        """        self.prefix = prefix
        self.separator = separator
    
    def supports(self, source: str) -> bool:
        """Always supports environment loading"""        return source == "environment" or source.startswith("env:")
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from environment variables"""        config = {}
        
        for key, value in os.environ.items():
            if not key.startswith(self.prefix):
                continue
            
            # Remove prefix and convert to lowercase
            config_key = key[len(self.prefix):].lower()
            
            # Handle nested keys
            if self.separator in config_key:
                self._set_nested_value(config, config_key, value)
            else:
                config[config_key] = self._convert_env_value(value)
        
        logger.info(f"Loaded {len(config)} configuration values from environment")
        return config
    
    def _set_nested_value(self, config: Dict[str, Any], key_path: str, value: str):
        """Set nested configuration value"""        keys = key_path.split(self.separator)
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = self._convert_env_value(value)
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type"""        # Boolean conversion
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # JSON conversion (for complex values)
        if (value.startswith('{') and value.endswith('}')) or \
           (value.startswith('[') and value.endswith(']')):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # Numeric conversion
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # List conversion (comma-separated)
        if ',' in value and not (value.startswith('"') or value.startswith("'")):
            return [item.strip() for item in value.split(',')]
        
        return value


class S3ConfigLoader(ConfigurationLoader):
    """AWS S3 configuration file loader"""    
    def __init__(self, aws_access_key_id: str = None, aws_secret_access_key: str = None, 
                 region_name: str = None):
        """Initialize S3 loader with credentials"""        self.aws_access_key_id = aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = region_name or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    def supports(self, source: str) -> bool:
        """Check if source is an S3 URL"""        return source.startswith('s3://')
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from S3 object"""        try:
            # Parse S3 URL
            parsed = urlparse(source)
            bucket_name = parsed.netloc
            object_key = parsed.path.lstrip('/')
            
            # Create S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            # Download object
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            content = response['Body'].read().decode('utf-8')
            
            # Determine file format and parse
            if object_key.lower().endswith('.json'):
                config = json.loads(content)
            elif object_key.lower().endswith(('.yaml', '.yml')):
                config = yaml.safe_load(content)
            elif object_key.lower().endswith('.toml'):
                config = toml.loads(content)
            else:
                raise ValueError(f"Unsupported file format for S3 object: {object_key}")
            
            logger.info(f"Loaded configuration from S3: {source}")
            return config
            
        except ClientError as e:
            logger.error(f"AWS error loading config from S3 {source}: {e}")
            raise
        except NoCredentialsError:
            logger.error("AWS credentials not found for S3 config loading")
            raise
        except Exception as e:
            logger.error(f"Error loading config from S3 {source}: {e}")
            raise


class HTTPConfigLoader(ConfigurationLoader):
    """HTTP/HTTPS configuration loader"""    
    def __init__(self, timeout: int = 30, headers: Dict[str, str] = None):
        """Initialize HTTP loader"""        self.timeout = timeout
        self.headers = headers or {
            'User-Agent': 'IA-Influencer-Agent-Config-Loader/1.0'
        }
    
    def supports(self, source: str) -> bool:
        """Check if source is an HTTP URL"""        return source.startswith(('http://', 'https://'))
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from HTTP endpoint"""        try:
            response = requests.get(source, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' in content_type:
                config = response.json()
            elif 'application/x-yaml' in content_type or 'text/yaml' in content_type:
                config = yaml.safe_load(response.text)
            elif 'application/toml' in content_type:
                config = toml.loads(response.text)
            else:
                # Try to detect format from URL
                if source.lower().endswith('.json'):
                    config = response.json()
                elif source.lower().endswith(('.yaml', '.yml')):
                    config = yaml.safe_load(response.text)
                elif source.lower().endswith('.toml'):
                    config = toml.loads(response.text)
                else:
                    raise ValueError(f"Cannot determine config format from HTTP response: {source}")
            
            logger.info(f"Loaded configuration from HTTP: {source}")
            return config
            
        except requests.RequestException as e:
            logger.error(f"HTTP error loading config from {source}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading config from HTTP {source}: {e}")
            raise


class RedisConfigLoader(ConfigurationLoader):
    """Redis configuration loader"""    
    def __init__(self, redis_url: str = None):
        """Initialize Redis loader"""        self.redis_url = redis_url or os.getenv('REDIS_CONFIG_URL', 'redis://localhost:6379/10')
        self.redis_client = None
    
    def supports(self, source: str) -> bool:
        """Check if source is Redis"""        return source.startswith('redis://') or source == 'redis'
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from Redis"""        try:
            if not self.redis_client:
                redis_url = source if source.startswith('redis://') else self.redis_url
                self.redis_client = redis.from_url(redis_url)
            
            # Get all configuration keys
            pattern = "config:*"
            keys = self.redis_client.keys(pattern)
            
            config = {}
            for key in keys:
                # Remove prefix
                config_key = key.decode('utf-8').replace('config:', '')
                value = self.redis_client.get(key)
                
                if value:
                    value_str = value.decode('utf-8')
                    # Try to parse as JSON first
                    try:
                        config_value = json.loads(value_str)
                    except json.JSONDecodeError:
                        config_value = value_str
                    
                    # Handle nested keys
                    if '.' in config_key:
                        self._set_nested_value(config, config_key, config_value)
                    else:
                        config[config_key] = config_value
            
            logger.info(f"Loaded {len(config)} configuration values from Redis")
            return config
            
        except redis.RedisError as e:
            logger.error(f"Redis error loading config: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading config from Redis: {e}")
            raise
    
    def _set_nested_value(self, config: Dict[str, Any], key_path: str, value: Any):
        """Set nested configuration value"""        keys = key_path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value


class DatabaseConfigLoader(ConfigurationLoader):
    """Database configuration loader"""    
    def __init__(self, database_url: str):
        """Initialize database loader"""        self.database_url = database_url
    
    def supports(self, source: str) -> bool:
        """Check if source is database"""        return source.startswith(('postgresql://', 'mysql://', 'sqlite://')) or source == 'database'
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from database"""        try:
            from sqlalchemy import create_engine, text
            
            db_url = source if source.startswith(('postgresql://', 'mysql://', 'sqlite://')) else self.database_url
            engine = create_engine(db_url)
            
            with engine.connect() as conn:
                # Assuming a configuration table exists
                query = text("SELECT config_key, config_value FROM app_configuration WHERE active = true")
                result = conn.execute(query)
                
                config = {}
                for row in result:
                    config_key, config_value = row
                    
                    # Try to parse as JSON
                    try:
                        value = json.loads(config_value)
                    except json.JSONDecodeError:
                        value = config_value
                    
                    # Handle nested keys
                    if '.' in config_key:
                        self._set_nested_value(config, config_key, value)
                    else:
                        config[config_key] = value
            
            logger.info(f"Loaded {len(config)} configuration values from database")
            return config
            
        except Exception as e:
            logger.error(f"Error loading config from database: {e}")
            raise
    
    def _set_nested_value(self, config: Dict[str, Any], key_path: str, value: Any):
        """Set nested configuration value"""        keys = key_path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value


class ConfigLoaderRegistry:
    """Registry for configuration loaders"""    
    def __init__(self):
        self.loaders: List[ConfigurationLoader] = []
        self._register_default_loaders()
    
    def _register_default_loaders(self):
        """Register default configuration loaders"""        self.register(YAMLConfigLoader())
        self.register(JSONConfigLoader())
        self.register(TOMLConfigLoader())
        self.register(INIConfigLoader())
        self.register(EnvironmentConfigLoader())
        self.register(S3ConfigLoader())
        self.register(HTTPConfigLoader())
        self.register(RedisConfigLoader())
    
    def register(self, loader: ConfigurationLoader):
        """Register a configuration loader"""        self.loaders.append(loader)
    
    def get_loader(self, source: str) -> Optional[ConfigurationLoader]:
        """Get appropriate loader for source"""        for loader in self.loaders:
            if loader.supports(source):
                return loader
        return None
    
    def load_config(self, sources: List[str]) -> Dict[str, Any]:
        """Load configuration from multiple sources"""        merged_config = {}
        
        for source in sources:
            try:
                loader = self.get_loader(source)
                if not loader:
                    logger.warning(f"No loader found for source: {source}")
                    continue
                
                config = loader.load(source)
                merged_config = loader._merge_configs(merged_config, config)
                
            except Exception as e:
                logger.error(f"Failed to load config from {source}: {e}")
                # Continue with other sources
                continue
        
        return merged_config


# Global loader registry instance
loader_registry = ConfigLoaderRegistry()


def load_configuration(sources: Union[str, List[str]]) -> Dict[str, Any]:
    """Load configuration from one or more sources"""    if isinstance(sources, str):
        sources = [sources]
    
    return loader_registry.load_config(sources)


def register_custom_loader(loader: ConfigurationLoader):
    """Register a custom configuration loader"""    loader_registry.register(loader)


def create_config_from_dict(config_dict: Dict[str, Any], config_class=None):
    """Create configuration object from dictionary"""    if config_class is None:
        from .app_config import AppConfig
        config_class = AppConfig
    
    # Filter dictionary to only include fields that exist in the config class
    if hasattr(config_class, '__dataclass_fields__'):
        valid_fields = config_class.__dataclass_fields__.keys()
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_fields}
        return config_class(**filtered_dict)
    else:
        # For non-dataclass config objects
        config = config_class()
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
