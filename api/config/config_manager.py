"""
Configuration Managers - IA Influencer Agent Platform
Advanced configuration management utilities and managers

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import os
import json
import yaml
from typing import Dict, List, Optional, Any, Union, Type
from dataclasses import dataclass, field
from pathlib import Path
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import redis
import threading
import time
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

from .app_config import AppConfig
from .environments import get_config


class SingletonMeta(type):
    """Metaclass for singleton pattern"""
    _instances = {}
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass
class ConfigurationSource:
    """Configuration source definition"""
    name: str
    source_type: str  # file, env, s3, redis, database
    location: str
    priority: int = 0  # Higher number = higher priority
    enabled: bool = True
    refresh_interval: int = 3600  # seconds
    last_refresh: Optional[datetime] = None
    encrypted: bool = False


class ConfigManager(metaclass=SingletonMeta):
    """Centralized configuration manager"""
    
    def __init__(self):
        self._config_cache: Dict[str, Any] = {}
        self._sources: List[ConfigurationSource] = []
        self._watchers: Dict[str, callable] = {}
        self._lock = threading.RLock()
        self._refresh_thread = None
        self._stop_refresh = False
        
        # Initialize default configuration
        self._initialize_default_sources()
        self._start_auto_refresh()
    
    def _initialize_default_sources(self):
        """Initialize default configuration sources"""
        # Environment variables (highest priority)
        self.add_source(ConfigurationSource(
            name="environment",
            source_type="env",
            location="",
            priority=100,
            refresh_interval=0  # No refresh needed for env vars
        ))
        
        # Local configuration files
        config_files = [
            "config.yaml",
            "config.yml", 
            "config.json",
            "/etc/ia-influencer-agent/config.yaml",
            "~/.ia-influencer-agent/config.yaml"
        ]
        
        for i, config_file in enumerate(config_files):
            if os.path.exists(os.path.expanduser(config_file)):
                self.add_source(ConfigurationSource(
                    name=f"file_{i}",
                    source_type="file",
                    location=os.path.expanduser(config_file),
                    priority=50 - i  # Earlier files have higher priority
                ))
        
        # AWS Parameter Store / Secrets Manager
        if os.getenv("AWS_CONFIG_ENABLED", "false").lower() == "true":
            self.add_source(ConfigurationSource(
                name="aws_ssm",
                source_type="aws_ssm",
                location=os.getenv("AWS_SSM_PREFIX", "/ia-influencer-agent/"),
                priority=80
            ))
        
        # Redis configuration store
        if os.getenv("REDIS_CONFIG_ENABLED", "false").lower() == "true":
            self.add_source(ConfigurationSource(
                name="redis_config",
                source_type="redis",
                location=os.getenv("REDIS_CONFIG_URL", "redis://localhost:6379/10"),
                priority=60
            ))
    
    def add_source(self, source: ConfigurationSource):
        """Add a configuration source"""
        with self._lock:
            # Remove existing source with same name
            self._sources = [s for s in self._sources if s.name != source.name]
            self._sources.append(source)
            # Sort by priority (highest first)
            self._sources.sort(key=lambda x: x.priority, reverse=True)
    
    def remove_source(self, name: str):
        """Remove a configuration source"""
        with self._lock:
            self._sources = [s for s in self._sources if s.name != name]
    
    def get(self, key: str, default: Any = None, refresh: bool = False) -> Any:
        """Get configuration value with cascading priority"""
        if refresh or key not in self._config_cache:
            self._refresh_key(key)
        
        return self._config_cache.get(key, default)
    
    def set(self, key: str, value: Any, source_name: str = "runtime"):
        """Set configuration value in cache"""
        with self._lock:
            self._config_cache[key] = value
            self._notify_watchers(key, value)
    
    def _refresh_key(self, key: str):
        """Refresh a specific configuration key from sources"""
        with self._lock:
            for source in self._sources:
                if not source.enabled:
                    continue
                
                try:
                    value = self._load_from_source(source, key)
                    if value is not None:
                        self._config_cache[key] = value
                        return
                except Exception as e:
                    print(f"Error loading {key} from {source.name}: {e}")
                    continue
    
    def _load_from_source(self, source: ConfigurationSource, key: str) -> Any:
        """Load configuration value from a specific source"""
        if source.source_type == "env":
            return os.getenv(key.upper())
        
        elif source.source_type == "file":
            return self._load_from_file(source.location, key)
        
        elif source.source_type == "aws_ssm":
            return self._load_from_aws_ssm(source.location + key)
        
        elif source.source_type == "redis":
            return self._load_from_redis(source.location, key)
        
        elif source.source_type == "s3":
            return self._load_from_s3(source.location, key)
        
        return None
    
    def _load_from_file(self, file_path: str, key: str) -> Any:
        """Load configuration from file"""



        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.json'):
                    data = json.load(f)
                elif file_path.endswith(('.yaml', '.yml')):
                    data = yaml.safe_load(f)
                else:
                    return None
                
                # Navigate nested keys using dot notation
                keys = key.split('.')
                value = data
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return None
                return value
        except (FileNotFoundError, json.JSONDecodeError, yaml.YAMLError):
            return None
    
    def _load_from_aws_ssm(self, parameter_name: str) -> Any:
        """Load configuration from AWS Systems Manager Parameter Store"""



        try:
            import boto3
            ssm = boto3.client('ssm')
            response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
            value = response['Parameter']['Value']
            
            # Try to parse as JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except (ClientError, NoCredentialsError):
            return None
    
    def _load_from_redis(self, redis_url: str, key: str) -> Any:
        """Load configuration from Redis"""



        try:
            r = redis.from_url(redis_url)
            value = r.get(key)
            if value:
                value = value.decode('utf-8')
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
        except (redis.RedisError, ConnectionError):
            return None
    
    def _load_from_s3(self, s3_path: str, key: str) -> Any:
        """Load configuration from S3"""



        try:
            import boto3
            # Parse S3 path: s3://bucket/path/file.json
            parts = s3_path.replace('s3://', '').split('/', 1)
            bucket = parts[0]
            object_key = parts[1] if len(parts) > 1 else key
            
            s3 = boto3.client('s3')
            response = s3.get_object(Bucket=bucket, Key=object_key)
            content = response['Body'].read().decode('utf-8')
            
            if object_key.endswith('.json'):
                data = json.loads(content)
            elif object_key.endswith(('.yaml', '.yml')):
                data = yaml.safe_load(content)
            else:
                return content
            
            # Navigate nested keys
            keys = key.split('.')
            value = data
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return None
            return value
        except (ClientError, NoCredentialsError, json.JSONDecodeError, yaml.YAMLError):
            return None
    
    def _start_auto_refresh(self):
        """Start automatic configuration refresh thread"""
        if self._refresh_thread and self._refresh_thread.is_alive():
            return
        
        self._refresh_thread = threading.Thread(target=self._auto_refresh_worker, daemon=True)
        self._refresh_thread.start()
    
    def _auto_refresh_worker(self):
        """Auto-refresh worker thread"""
        while not self._stop_refresh:
            try:
                current_time = datetime.now()
                for source in self._sources:
                    if (source.refresh_interval > 0 and 
                        (source.last_refresh is None or 
                         current_time - source.last_refresh > timedelta(seconds=source.refresh_interval))):
                        
                        self._refresh_source(source)
                        source.last_refresh = current_time
                
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Error in auto-refresh worker: {e}")
                time.sleep(60)
    
    def _refresh_source(self, source: ConfigurationSource):
        """Refresh all configurations from a specific source"""
        # This would reload all keys from the source
        # Implementation depends on source type
        pass
    
    def watch(self, key: str, callback: callable):
        """Watch for configuration changes"""
        with self._lock:
            if key not in self._watchers:
                self._watchers[key] = []
            self._watchers[key].append(callback)
    
    def _notify_watchers(self, key: str, value: Any):
        """Notify watchers of configuration changes"""
        if key in self._watchers:
            for callback in self._watchers[key]:
                try:
                    callback(key, value)
                except Exception as e:
                    print(f"Error in config watcher callback: {e}")
    
    @staticmethod
    def get_current_environment() -> str:
        """Get current environment"""



        return os.getenv("ENVIRONMENT", "development").lower()
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""



        return dict(self._config_cache)
    
    def reload(self):
        """Reload all configuration from sources"""
        with self._lock:
            self._config_cache.clear()
            for source in self._sources:
                source.last_refresh = None
    
    def stop(self):
        """Stop the configuration manager"""
        self._stop_refresh = True
        if self._refresh_thread:
            self._refresh_thread.join(timeout=5)


class EnvironmentManager:
    """Environment-specific configuration management"""
    
    def __init__(self):
        self._current_env = None
        self._config_cache: Dict[str, AppConfig] = {}
    
    def get_current_environment(self) -> str:
        """Get current environment name"""
        if self._current_env is None:
            self._current_env = os.getenv("ENVIRONMENT", "development").lower()
        return self._current_env
    
    def set_environment(self, environment: str):
        """Set current environment"""
        self._current_env = environment.lower()
        # Clear config cache to force reload
        self._config_cache.clear()
    
    def get_config(self, environment: str = None) -> AppConfig:
        """Get configuration for specific environment"""
        env = environment or self.get_current_environment()
        
        if env not in self._config_cache:
            self._config_cache[env] = get_config(env)
        
        return self._config_cache[env]
    
    def validate_environment(self, environment: str = None) -> Dict[str, Any]:
        """Validate environment configuration"""
        from .environments import validate_environment_config
        env = environment or self.get_current_environment()
        config = self.get_config(env)
        return validate_environment_config(config)
    
    def list_environments(self) -> List[str]:
        """List available environments"""



        return ["development", "testing", "staging", "production"]
    
    def is_production(self) -> bool:
        """Check if running in production"""



        return self.get_current_environment() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""



        return self.get_current_environment() == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing"""



        return self.get_current_environment() == "testing"


class SecretManager:
    """Secure secrets management"""
    
    def __init__(self):
        self._encryption_key = self._get_or_create_encryption_key()
        self._cipher_suite = Fernet(self._encryption_key)
        self._secrets_cache: Dict[str, str] = {}
        self._aws_enabled = os.getenv("AWS_SECRETS_ENABLED", "false").lower() == "true"
        self._redis_enabled = os.getenv("REDIS_SECRETS_ENABLED", "false").lower() == "true"
        
        if self._redis_enabled:
            self._redis_client = redis.from_url(
                os.getenv("SECRETS_REDIS_URL", "redis://localhost:6379/15")
            )
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        key = os.getenv("SECRETS_ENCRYPTION_KEY")
        if key:
            return key.encode()
        
        # Try to load from file
        key_file = os.path.expanduser("~/.ia-influencer-agent/encryption.key")
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        
        # Generate new key
        new_key = Fernet.generate_key()
        
        # Save to file
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, 'wb') as f:
            f.write(new_key)
        os.chmod(key_file, 0o600)
        
        return new_key
    
    def store_secret(self, name: str, value: str, encrypted: bool = True) -> bool:
        """Store a secret securely"""



        try:
            if encrypted:
                value = self.encrypt(value)
            
            # Try AWS Secrets Manager first
            if self._aws_enabled:
                if self._store_in_aws_secrets_manager(name, value):
                    return True
            
            # Try Redis
            if self._redis_enabled:
                if self._store_in_redis(name, value):
                    return True
            
            # Fallback to local encrypted storage
            return self._store_locally(name, value)
            
        except Exception as e:
            print(f"Error storing secret {name}: {e}")
            return False
    
    def get_secret(self, name: str, default: str = None, encrypted: bool = True) -> Optional[str]:
        """Get a secret securely"""
        # Check cache first
        if name in self._secrets_cache:
            return self._secrets_cache[name]
        
        value = None
        
        # Try AWS Secrets Manager first
        if self._aws_enabled:
            value = self._get_from_aws_secrets_manager(name)
        
        # Try Redis
        if value is None and self._redis_enabled:
            value = self._get_from_redis(name)
        
        # Try local storage
        if value is None:
            value = self._get_locally(name)
        
        # Try environment variable
        if value is None:
            value = os.getenv(name.upper())
        
        if value is None:
            return default
        
        # Decrypt if needed
        if encrypted and value:
            try:
                value = self.decrypt(value)
            except Exception:
                # If decryption fails, assume it's already decrypted
                pass
        
        # Cache the result
        self._secrets_cache[name] = value
        return value
    
    def _store_in_aws_secrets_manager(self, name: str, value: str) -> bool:
        """Store secret in AWS Secrets Manager"""



        try:
            import boto3
            secrets_client = boto3.client('secretsmanager')
            
            secret_name = f"ia-influencer-agent/{name}"
            secrets_client.create_secret(Name=secret_name, SecretString=value)
            return True
        except Exception:
            return False
    
    def _get_from_aws_secrets_manager(self, name: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager"""



        try:
            import boto3
            secrets_client = boto3.client('secretsmanager')
            
            secret_name = f"ia-influencer-agent/{name}"
            response = secrets_client.get_secret_value(SecretId=secret_name)
            return response['SecretString']
        except Exception:
            return None
    
    def _store_in_redis(self, name: str, value: str) -> bool:
        """Store secret in Redis"""



        try:
            key = f"secrets:{name}"
            self._redis_client.set(key, value, ex=86400)  # 24 hour expiry
            return True
        except Exception:
            return False
    
    def _get_from_redis(self, name: str) -> Optional[str]:
        """Get secret from Redis"""



        try:
            key = f"secrets:{name}"
            value = self._redis_client.get(key)
            return value.decode('utf-8') if value else None
        except Exception:
            return None
    
    def _store_locally(self, name: str, value: str) -> bool:
        """Store secret locally"""



        try:
            secrets_dir = os.path.expanduser("~/.ia-influencer-agent/secrets")
            os.makedirs(secrets_dir, exist_ok=True)
            
            secret_file = os.path.join(secrets_dir, f"{name}.secret")
            with open(secret_file, 'w') as f:
                f.write(value)
            os.chmod(secret_file, 0o600)
            return True
        except Exception:
            return False
    
    def _get_locally(self, name: str) -> Optional[str]:
        """Get secret from local storage"""



        try:
            secrets_dir = os.path.expanduser("~/.ia-influencer-agent/secrets")
            secret_file = os.path.join(secrets_dir, f"{name}.secret")
            
            if os.path.exists(secret_file):
                with open(secret_file, 'r') as f:
                    return f.read().strip()
        except Exception:
            pass
        return None
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string"""



        return self._cipher_suite.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string"""



        return self._cipher_suite.decrypt(ciphertext.encode()).decode()
    
    def rotate_encryption_key(self) -> bool:
        """Rotate the encryption key (re-encrypt all secrets)"""



        try:
            # Generate new key
            new_key = Fernet.generate_key()
            new_cipher = Fernet(new_key)
            
            # Re-encrypt all cached secrets
            for name, value in self._secrets_cache.items():
                # Decrypt with old key
                decrypted = self.decrypt(value)
                # Encrypt with new key  
                encrypted = new_cipher.encrypt(decrypted.encode()).decode()
                # Store with new encryption
                self.store_secret(name, decrypted, encrypted=False)
            
            # Update cipher
            self._encryption_key = new_key
            self._cipher_suite = new_cipher
            
            # Save new key
            key_file = os.path.expanduser("~/.ia-influencer-agent/encryption.key")
            with open(key_file, 'wb') as f:
                f.write(new_key)
            
            return True
        except Exception as e:
            print(f"Error rotating encryption key: {e}")
            return False


class FeatureToggleManager:
    """Feature toggle management system"""
    
    def __init__(self):
        self._config_manager = ConfigManager()
        self._feature_cache: Dict[str, bool] = {}
        self._rollout_cache: Dict[str, Dict[str, Any]] = {}
        
        # Default features
        self._default_features = {
            "content_protection": True,
            "ai_fingerprinting": True,
            "web_crawling": True,
            "monetization": True,
            "blockchain_integration": False,
            "advanced_analytics": True,
            "real_time_notifications": True,
            "batch_processing": True,
            "multi_language_support": False,
            "premium_features": False
        }
    
    def is_enabled(self, feature_name: str, user_id: str = None, 
                   context: Dict[str, Any] = None) -> bool:
        """Check if a feature is enabled for a user/context"""
        # Check cache first
        cache_key = f"{feature_name}:{user_id or 'global'}"
        if cache_key in self._feature_cache:
            return self._feature_cache[cache_key]
        
        # Get feature configuration
        feature_config = self._get_feature_config(feature_name)
        
        if not feature_config:
            # Default to environment-based toggle
            result = self._config_manager.get(f"enable_{feature_name}", 
                                            self._default_features.get(feature_name, False))
        else:
            result = self._evaluate_feature_rules(feature_config, user_id, context)
        
        # Cache result
        self._feature_cache[cache_key] = result
        return result
    
    def _get_feature_config(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """Get feature configuration from config manager"""



        return self._config_manager.get(f"features.{feature_name}")
    
    def _evaluate_feature_rules(self, feature_config: Dict[str, Any], 
                               user_id: str = None, 
                               context: Dict[str, Any] = None) -> bool:
        """Evaluate feature toggle rules"""
        # Global enable/disable
        if not feature_config.get("enabled", True):
            return False
        
        # Percentage rollout
        rollout_percentage = feature_config.get("rollout_percentage", 100)
        if rollout_percentage < 100:
            if user_id:
                # Consistent hash-based rollout
                user_hash = hash(user_id) % 100
                if user_hash >= rollout_percentage:
                    return False
            else:
                import random
                if random.randint(0, 99) >= rollout_percentage:
                    return False
        
        # User whitelist/blacklist
        whitelist = feature_config.get("whitelist", [])
        blacklist = feature_config.get("blacklist", [])
        
        if user_id:
            if blacklist and user_id in blacklist:
                return False
            if whitelist and user_id not in whitelist:
                return False
        
        # Context-based rules
        rules = feature_config.get("rules", [])
        for rule in rules:
            if not self._evaluate_rule(rule, context):
                return False
        
        return True
    
    def _evaluate_rule(self, rule: Dict[str, Any], context: Dict[str, Any] = None) -> bool:
        """Evaluate a single feature rule"""
        if not context:
            context = {}
        
        rule_type = rule.get("type")
        
        if rule_type == "environment":
            required_env = rule.get("environment")
            current_env = self._config_manager.get_current_environment()
            return current_env == required_env
        
        elif rule_type == "time_range":
            from datetime import datetime
            start_time = datetime.fromisoformat(rule.get("start_time"))
            end_time = datetime.fromisoformat(rule.get("end_time"))
            now = datetime.now()
            return start_time <= now <= end_time
        
        elif rule_type == "context_match":
            field = rule.get("field")
            expected_value = rule.get("value")
            operator = rule.get("operator", "equals")
            
            actual_value = context.get(field)
            
            if operator == "equals":
                return actual_value == expected_value
            elif operator == "in":
                return actual_value in expected_value
            elif operator == "greater_than":
                return float(actual_value) > float(expected_value)
            elif operator == "less_than":
                return float(actual_value) < float(expected_value)
        
        return True
    
    def enable_feature(self, feature_name: str, user_id: str = None):
        """Enable a feature for a user or globally"""
        cache_key = f"{feature_name}:{user_id or 'global'}"
        self._feature_cache[cache_key] = True
    
    def disable_feature(self, feature_name: str, user_id: str = None):
        """Disable a feature for a user or globally"""
        cache_key = f"{feature_name}:{user_id or 'global'}"
        self._feature_cache[cache_key] = False
    
    def set_rollout_percentage(self, feature_name: str, percentage: int):
        """Set rollout percentage for a feature"""
        if feature_name not in self._rollout_cache:
            self._rollout_cache[feature_name] = {}
        self._rollout_cache[feature_name]["rollout_percentage"] = percentage
        
        # Clear cache to force re-evaluation
        keys_to_remove = [k for k in self._feature_cache.keys() if k.startswith(f"{feature_name}:")]
        for key in keys_to_remove:
            del self._feature_cache[key]
    
    def get_feature_status(self, user_id: str = None) -> Dict[str, bool]:
        """Get status of all features for a user"""
        status = {}
        for feature_name in self._default_features:
            status[feature_name] = self.is_enabled(feature_name, user_id)
        return status
    
    def clear_cache(self):
        """Clear feature toggle cache"""
        self._feature_cache.clear()
        self._rollout_cache.clear()
