"""
Configuration Manager - Enterprise Configuration Management
========================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: Backend Senior + DevOps + Security + DBA
**Module**: Core Services - Configuration Management
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade configuration management with hot reloading, secrets management,
environment-specific configs, and secure distribution.
"""

import asyncio
import json
import logging
import os
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import aioredis
import aiofiles
from pathlib import Path
import hashlib
import base64
from cryptography.fernet import Fernet


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigSource(Enum):
    """Configuration source types"""
    FILE = "file"
    ENVIRONMENT = "environment" 
    REDIS = "redis"
    VAULT = "vault"
    DATABASE = "database"
    REMOTE = "remote"


class ConfigFormat(Enum):
    """Configuration format types"""
    JSON = "json"
    YAML = "yaml"
    ENV = "env"
    TOML = "toml"
    XML = "xml"


@dataclass
class ConfigUpdate:
    """Configuration update event"""
    config_key: str
    old_value: Any
    new_value: Any
    source: ConfigSource
    timestamp: datetime = field(default_factory=datetime.now)
    user: Optional[str] = None
    reason: Optional[str] = None


@dataclass
class ConfigSchema:
    """Configuration schema definition"""
    key: str
    data_type: type
    required: bool = True
    default_value: Any = None
    description: str = ""
    validation_rules: List[str] = field(default_factory=list)
    sensitive: bool = False
    environment_specific: bool = False


class SecretManager:
    """
    Secure secrets management with encryption
    
    **Roles**: Security + DevOps
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or self._generate_key()
        self.cipher = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
        self.secrets: Dict[str, str] = {}
    
    def _generate_key(self) -> bytes:
        """Generate encryption key"""
        return Fernet.generate_key()
    
    def encrypt_secret(self, value: str) -> str:
        """Encrypt a secret value"""
        return self.cipher.encrypt(value.encode()).decode()
    
    def decrypt_secret(self, encrypted_value: str) -> str:
        """Decrypt a secret value"""
        return self.cipher.decrypt(encrypted_value.encode()).decode()
    
    def store_secret(self, key: str, value: str) -> None:
        """Store an encrypted secret"""
        self.secrets[key] = self.encrypt_secret(value)
    
    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve and decrypt a secret"""
        encrypted_value = self.secrets.get(key)
        if encrypted_value:
            return self.decrypt_secret(encrypted_value)
        return None
    
    def delete_secret(self, key: str) -> bool:
        """Delete a secret"""
        if key in self.secrets:
            del self.secrets[key]
            return True
        return False


class ConfigManager:
    """
    Enterprise Configuration Manager with Hot Reloading & Secrets Management
    
    **Expert Roles Implemented:**
    - Backend Senior: Robust async configuration management, caching
    - DevOps: Environment management, hot reloading, observability
    - Security: Secrets encryption, secure access, audit logging
    - DBA: Configuration persistence, schema validation
    """
    
    def __init__(
        self,
        config_dir: str = "./config",
        redis_url: str = "redis://localhost:6379",
        environment: str = "production",
        enable_hot_reload: bool = True,
        reload_interval: int = 30,
        enable_caching: bool = True,
        cache_ttl: int = 300
    ):
        self.config_dir = Path(config_dir)
        self.redis_url = redis_url
        self.environment = environment
        self.enable_hot_reload = enable_hot_reload
        self.reload_interval = reload_interval
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        
        # Storage
        self.redis_client: Optional[aioredis.Redis] = None
        self.configurations: Dict[str, Any] = {}
        self.config_schemas: Dict[str, ConfigSchema] = {}
        self.config_cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # Security
        self.secret_manager = SecretManager()
        
        # Monitoring
        self.config_updates: List[ConfigUpdate] = []
        self.update_callbacks: Dict[str, List[Callable]] = {}
        self.file_watchers: Dict[str, Any] = {}
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.running = False
        
    async def initialize(self) -> None:
        """Initialize configuration manager"""
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize Redis connection
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Load configurations
            await self._load_configurations()
            
            # Load schemas
            await self._load_schemas()
            
            # Start background tasks
            if self.enable_hot_reload:
                self.running = True
                self.background_tasks = [
                    asyncio.create_task(self._hot_reload_loop()),
                    asyncio.create_task(self._cache_cleanup_loop()),
                    asyncio.create_task(self._sync_with_redis_loop())
                ]
            
            logger.info("Configuration Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Configuration Manager: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""
        self.running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Configuration Manager shutdown completed")
    
    async def get_config(
        self,
        key: str,
        default: Any = None,
        use_cache: bool = True,
        decrypt_secrets: bool = True
    ) -> Any:
        """
        Get configuration value
        
        **Roles**: Backend Senior + Security + DBA
        """
        try:
            # Check cache first
            if use_cache and self.enable_caching:
                cached_value = self._get_from_cache(key)
                if cached_value is not None:
                    return cached_value
            
            # Get from configurations
            value = self._get_nested_config(key, default)
            
            # Decrypt if it's a secret
            if decrypt_secrets and self._is_secret_key(key):
                if isinstance(value, str):
                    try:
                        value = self.secret_manager.decrypt_secret(value)
                    except Exception:
                        # If decryption fails, assume it's not encrypted
                        pass
            
            # Cache the value
            if use_cache and self.enable_caching:
                self._set_cache(key, value)
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to get config {key}: {e}")
            return default
    
    async def set_config(
        self,
        key: str,
        value: Any,
        source: ConfigSource = ConfigSource.REDIS,
        user: Optional[str] = None,
        reason: Optional[str] = None,
        encrypt_if_secret: bool = True
    ) -> bool:
        """
        Set configuration value
        
        **Roles**: Backend Senior + Security + DevOps
        """
        try:
            # Get old value for audit
            old_value = await self.get_config(key, decrypt_secrets=False)
            
            # Validate against schema
            if not self._validate_config(key, value):
                return False
            
            # Encrypt if it's a secret
            if encrypt_if_secret and self._is_secret_key(key):
                if isinstance(value, str):
                    value = self.secret_manager.encrypt_secret(value)
            
            # Update configuration
            self._set_nested_config(key, value)
            
            # Persist to storage
            await self._persist_config(key, value, source)
            
            # Clear cache
            self._clear_cache(key)
            
            # Record update
            update = ConfigUpdate(
                config_key=key,
                old_value=old_value,
                new_value=value,
                source=source,
                user=user,
                reason=reason
            )
            self.config_updates.append(update)
            
            # Trigger callbacks
            await self._trigger_update_callbacks(key, old_value, value)
            
            logger.info(f"Configuration updated: {key} by {user or 'system'}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set config {key}: {e}")
            return False
    
    async def delete_config(self, key: str, user: Optional[str] = None) -> bool:
        """Delete configuration value"""
        try:
            if key not in self.configurations:
                return False
            
            old_value = self.configurations[key]
            del self.configurations[key]
            
            # Remove from Redis
            if self.redis_client:
                await self.redis_client.delete(f"config:{key}")
            
            # Clear cache
            self._clear_cache(key)
            
            # Record update
            update = ConfigUpdate(
                config_key=key,
                old_value=old_value,
                new_value=None,
                source=ConfigSource.REDIS,
                user=user,
                reason="Configuration deleted"
            )
            self.config_updates.append(update)
            
            logger.info(f"Configuration deleted: {key} by {user or 'system'}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete config {key}: {e}")
            return False
    
    async def load_config_file(
        self,
        file_path: str,
        format_type: ConfigFormat = ConfigFormat.YAML,
        namespace: Optional[str] = None
    ) -> bool:
        """
        Load configuration from file
        
        **Roles**: DevOps + Backend Senior
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.warning(f"Config file not found: {file_path}")
                return False
            
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
            
            # Parse based on format
            if format_type == ConfigFormat.YAML:
                config_data = yaml.safe_load(content)
            elif format_type == ConfigFormat.JSON:
                config_data = json.loads(content)
            elif format_type == ConfigFormat.ENV:
                config_data = self._parse_env_format(content)
            else:
                logger.error(f"Unsupported config format: {format_type}")
                return False
            
            # Apply namespace if specified
            if namespace:
                config_data = {namespace: config_data}
            
            # Merge with existing configuration
            self._merge_configs(config_data)
            
            # Set up file watching for hot reload
            if self.enable_hot_reload:
                await self._setup_file_watcher(str(file_path), format_type, namespace)
            
            logger.info(f"Config file loaded: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load config file {file_path}: {e}")
            return False
    
    async def save_config_file(
        self,
        file_path: str,
        config_subset: Optional[Dict[str, Any]] = None,
        format_type: ConfigFormat = ConfigFormat.YAML
    ) -> bool:
        """Save configuration to file"""
        try:
            data = config_subset or self.configurations
            
            if format_type == ConfigFormat.YAML:
                content = yaml.dump(data, default_flow_style=False)
            elif format_type == ConfigFormat.JSON:
                content = json.dumps(data, indent=2)
            else:
                logger.error(f"Unsupported save format: {format_type}")
                return False
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(content)
            
            logger.info(f"Config saved to file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config file {file_path}: {e}")
            return False
    
    def register_update_callback(self, key_pattern: str, callback: Callable) -> None:
        """Register callback for configuration updates"""
        if key_pattern not in self.update_callbacks:
            self.update_callbacks[key_pattern] = []
        self.update_callbacks[key_pattern].append(callback)
    
    def unregister_update_callback(self, key_pattern: str, callback: Callable) -> None:
        """Unregister callback for configuration updates"""
        if key_pattern in self.update_callbacks:
            if callback in self.update_callbacks[key_pattern]:
                self.update_callbacks[key_pattern].remove(callback)
    
    def register_schema(self, schema: ConfigSchema) -> None:
        """
        Register configuration schema
        
        **Roles**: DBA + Backend Senior
        """
        self.config_schemas[schema.key] = schema
        logger.debug(f"Schema registered for: {schema.key}")
    
    async def get_all_configs(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Get all configurations"""
        configs = self.configurations.copy()
        
        if not include_secrets:
            # Filter out secret configurations
            filtered_configs = {}
            for key, value in configs.items():
                if not self._is_secret_key(key):
                    filtered_configs[key] = value
            return filtered_configs
        
        return configs
    
    async def get_config_history(self, key: Optional[str] = None) -> List[ConfigUpdate]:
        """Get configuration update history"""
        if key:
            return [update for update in self.config_updates if update.config_key == key]
        return self.config_updates.copy()
    
    def _get_nested_config(self, key: str, default: Any = None) -> Any:
        """Get nested configuration value using dot notation"""
        keys = key.split('.')
        value = self.configurations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def _set_nested_config(self, key: str, value: Any) -> None:
        """Set nested configuration value using dot notation"""
        keys = key.split('.')
        config = self.configurations
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def _is_secret_key(self, key: str) -> bool:
        """Check if a configuration key represents a secret"""
        secret_patterns = [
            'password', 'secret', 'key', 'token', 'api_key',
            'private_key', 'cert', 'credential'
        ]
        
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in secret_patterns)
    
    def _validate_config(self, key: str, value: Any) -> bool:
        """Validate configuration against schema"""
        if key not in self.config_schemas:
            return True  # No schema, allow any value
        
        schema = self.config_schemas[key]
        
        # Type validation
        if not isinstance(value, schema.data_type):
            logger.error(f"Config {key} type mismatch. Expected {schema.data_type}, got {type(value)}")
            return False
        
        # Custom validation rules
        for rule in schema.validation_rules:
            if not self._apply_validation_rule(value, rule):
                logger.error(f"Config {key} failed validation rule: {rule}")
                return False
        
        return True
    
    def _apply_validation_rule(self, value: Any, rule: str) -> bool:
        """Apply validation rule to a value"""
        try:
            # Simple validation rules
            if rule.startswith("min_length:"):
                min_len = int(rule.split(":")[1])
                return len(str(value)) >= min_len
            
            elif rule.startswith("max_length:"):
                max_len = int(rule.split(":")[1])
                return len(str(value)) <= max_len
            
            elif rule.startswith("pattern:"):
                import re
                pattern = rule.split(":", 1)[1]
                return bool(re.match(pattern, str(value)))
            
            elif rule == "not_empty":
                return bool(value)
            
            return True
            
        except Exception:
            return False
    
    def _get_from_cache(self, key: str) -> Any:
        """Get value from cache if not expired"""
        if key not in self.config_cache:
            return None
        
        if key not in self.cache_timestamps:
            return None
        
        # Check if cache is expired
        if datetime.now() - self.cache_timestamps[key] > timedelta(seconds=self.cache_ttl):
            del self.config_cache[key]
            del self.cache_timestamps[key]
            return None
        
        return self.config_cache[key]
    
    def _set_cache(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self.config_cache[key] = value
        self.cache_timestamps[key] = datetime.now()
    
    def _clear_cache(self, key: str) -> None:
        """Clear cache for a specific key"""
        if key in self.config_cache:
            del self.config_cache[key]
        if key in self.cache_timestamps:
            del self.cache_timestamps[key]
    
    def _parse_env_format(self, content: str) -> Dict[str, str]:
        """Parse environment file format"""
        config = {}
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        return config
    
    def _merge_configs(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration with existing"""
        def merge_dict(existing: Dict, new: Dict) -> Dict:
            for key, value in new.items():
                if key in existing and isinstance(existing[key], dict) and isinstance(value, dict):
                    merge_dict(existing[key], value)
                else:
                    existing[key] = value
            return existing
        
        merge_dict(self.configurations, new_config)
    
    async def _load_configurations(self) -> None:
        """Load configurations from various sources"""
        # Load from environment variables
        await self._load_from_environment()
        
        # Load from config files
        config_files = [
            (self.config_dir / "config.yaml", ConfigFormat.YAML),
            (self.config_dir / f"config.{self.environment}.yaml", ConfigFormat.YAML),
            (self.config_dir / ".env", ConfigFormat.ENV)
        ]
        
        for file_path, format_type in config_files:
            if file_path.exists():
                await self.load_config_file(str(file_path), format_type)
        
        # Load from Redis
        await self._load_from_redis()
    
    async def _load_from_environment(self) -> None:
        """Load configuration from environment variables"""
        env_configs = {}
        
        # Look for variables with specific prefixes
        prefixes = ['AINFLUE_', 'APP_', 'SERVICE_']
        
        for key, value in os.environ.items():
            for prefix in prefixes:
                if key.startswith(prefix):
                    config_key = key[len(prefix):].lower().replace('_', '.')
                    env_configs[config_key] = value
                    break
        
        if env_configs:
            self._merge_configs(env_configs)
            logger.info(f"Loaded {len(env_configs)} configs from environment")
    
    async def _load_from_redis(self) -> None:
        """Load configuration from Redis"""
        if not self.redis_client:
            return
        
        try:
            keys = await self.redis_client.keys("config:*")
            redis_configs = {}
            
            for key in keys:
                config_key = key.decode().replace("config:", "")
                value = await self.redis_client.get(key)
                if value:
                    try:
                        redis_configs[config_key] = json.loads(value)
                    except json.JSONDecodeError:
                        redis_configs[config_key] = value.decode()
            
            if redis_configs:
                self._merge_configs(redis_configs)
                logger.info(f"Loaded {len(redis_configs)} configs from Redis")
        
        except Exception as e:
            logger.error(f"Failed to load configs from Redis: {e}")
    
    async def _load_schemas(self) -> None:
        """Load configuration schemas"""
        schema_file = self.config_dir / "schemas.yaml"
        if schema_file.exists():
            try:
                async with aiofiles.open(schema_file, 'r') as f:
                    content = await f.read()
                
                schemas_data = yaml.safe_load(content)
                for key, schema_config in schemas_data.items():
                    schema = ConfigSchema(
                        key=key,
                        data_type=eval(schema_config.get('type', 'str')),
                        required=schema_config.get('required', True),
                        default_value=schema_config.get('default'),
                        description=schema_config.get('description', ''),
                        validation_rules=schema_config.get('validation_rules', []),
                        sensitive=schema_config.get('sensitive', False),
                        environment_specific=schema_config.get('environment_specific', False)
                    )
                    self.register_schema(schema)
                
                logger.info(f"Loaded {len(schemas_data)} configuration schemas")
            
            except Exception as e:
                logger.error(f"Failed to load schemas: {e}")
    
    async def _persist_config(self, key: str, value: Any, source: ConfigSource) -> None:
        """Persist configuration to storage"""
        if source == ConfigSource.REDIS and self.redis_client:
            try:
                serialized_value = json.dumps(value)
                await self.redis_client.set(f"config:{key}", serialized_value)
            except Exception as e:
                logger.error(f"Failed to persist config to Redis: {e}")
    
    async def _setup_file_watcher(
        self,
        file_path: str,
        format_type: ConfigFormat,
        namespace: Optional[str]
    ) -> None:
        """Set up file watcher for hot reload"""
        # This would integrate with a file watching library like watchdog
        # For now, we'll store the file info for periodic checking
        self.file_watchers[file_path] = {
            'format': format_type,
            'namespace': namespace,
            'last_modified': os.path.getmtime(file_path)
        }
    
    async def _trigger_update_callbacks(self, key: str, old_value: Any, new_value: Any) -> None:
        """Trigger registered callbacks for configuration updates"""
        import fnmatch
        
        for pattern, callbacks in self.update_callbacks.items():
            if fnmatch.fnmatch(key, pattern):
                for callback in callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(key, old_value, new_value)
                        else:
                            callback(key, old_value, new_value)
                    except Exception as e:
                        logger.error(f"Config callback error for {key}: {e}")
    
    async def _hot_reload_loop(self) -> None:
        """Background hot reload loop"""
        while self.running:
            try:
                await self._check_file_changes()
                await asyncio.sleep(self.reload_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Hot reload error: {e}")
                await asyncio.sleep(10)
    
    async def _check_file_changes(self) -> None:
        """Check for file changes and reload if needed"""
        for file_path, info in self.file_watchers.items():
            try:
                current_mtime = os.path.getmtime(file_path)
                if current_mtime > info['last_modified']:
                    logger.info(f"Config file changed, reloading: {file_path}")
                    await self.load_config_file(
                        file_path,
                        info['format'],
                        info['namespace']
                    )
                    info['last_modified'] = current_mtime
            except FileNotFoundError:
                logger.warning(f"Watched config file not found: {file_path}")
            except Exception as e:
                logger.error(f"Error checking file {file_path}: {e}")
    
    async def _cache_cleanup_loop(self) -> None:
        """Background cache cleanup loop"""
        while self.running:
            try:
                await self._cleanup_expired_cache()
                await asyncio.sleep(60)  # Cleanup every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
                await asyncio.sleep(10)
    
    async def _cleanup_expired_cache(self) -> None:
        """Clean up expired cache entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, timestamp in self.cache_timestamps.items():
            if current_time - timestamp > timedelta(seconds=self.cache_ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            self._clear_cache(key)
    
    async def _sync_with_redis_loop(self) -> None:
        """Background Redis synchronization loop"""
        while self.running:
            try:
                await self._sync_with_redis()
                await asyncio.sleep(300)  # Sync every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Redis sync error: {e}")
                await asyncio.sleep(30)
    
    async def _sync_with_redis(self) -> None:
        """Synchronize local configs with Redis"""
        if not self.redis_client:
            return
        
        try:
            # Check for new/updated configs in Redis
            keys = await self.redis_client.keys("config:*")
            
            for key in keys:
                config_key = key.decode().replace("config:", "")
                redis_value = await self.redis_client.get(key)
                
                if redis_value:
                    try:
                        value = json.loads(redis_value)
                    except json.JSONDecodeError:
                        value = redis_value.decode()
                    
                    local_value = self._get_nested_config(config_key)
                    
                    # Update if different
                    if local_value != value:
                        self._set_nested_config(config_key, value)
                        self._clear_cache(config_key)
                        
                        # Trigger callbacks
                        await self._trigger_update_callbacks(config_key, local_value, value)
        
        except Exception as e:
            logger.error(f"Error syncing with Redis: {e}")
    
    async def export_config(
        self,
        output_path: str,
        format_type: ConfigFormat = ConfigFormat.YAML,
        include_secrets: bool = False,
        filter_pattern: Optional[str] = None
    ) -> bool:
        """Export configuration to file"""
        try:
            configs = await self.get_all_configs(include_secrets)
            
            # Apply filter if specified
            if filter_pattern:
                import fnmatch
                filtered_configs = {
                    k: v for k, v in configs.items()
                    if fnmatch.fnmatch(k, filter_pattern)
                }
                configs = filtered_configs
            
            return await self.save_config_file(output_path, configs, format_type)
            
        except Exception as e:
            logger.error(f"Failed to export config: {e}")
            return False
    
    async def import_config(
        self,
        file_path: str,
        format_type: ConfigFormat = ConfigFormat.YAML,
        merge: bool = True,
        user: Optional[str] = None
    ) -> bool:
        """Import configuration from file"""
        try:
            if not merge:
                # Clear existing configs
                self.configurations.clear()
            
            success = await self.load_config_file(file_path, format_type)
            
            if success:
                # Record bulk update
                update = ConfigUpdate(
                    config_key="*",
                    old_value="bulk_import",
                    new_value=file_path,
                    source=ConfigSource.FILE,
                    user=user,
                    reason="Configuration import"
                )
                self.config_updates.append(update)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to import config: {e}")
            return False