"""
Pool Configuration module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""Pool Configuration - Consolidated Configuration and Security Management
==========================================================================

Consolidated configuration and security management for all database pools
in the IA Influencer Agent + Content Protection Platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json
import base64
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for pool configuration"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    HARDENED = "hardened"
    GOVERNMENT = "government"
    FINANCIAL = "financial"

class DatabaseType(Enum):
    """Database types supported by the pool system"""
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"
    VECTOR_STORE = "vector_store"
    CACHE = "cache"

class ConnectionState(Enum):
    """Connection states for monitoring"""
    INITIALIZING = "initializing"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class DatabaseConnectionInfo:
    """Database connection information"""
    host: str
    port: int
    database: str = ""
    username: str = ""
    password: str = ""
    ssl_enabled: bool = False
    ssl_cert_path: str = ""
    connection_string: str = ""
    extra_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PoolConfig:
    """Complete pool configuration"""
    pool_id: str
    database_type: DatabaseType
    connection_info: DatabaseConnectionInfo
    min_connections: int = 5
    max_connections: int = 50
    connection_timeout: float = 30.0
    query_timeout: float = 60.0
    health_check_interval: float = 30.0
    auto_scaling_enabled: bool = True
    scaling_threshold: float = 0.8
    retry_attempts: int = 3
    retry_delay: float = 1.0
    security_level: SecurityLevel = SecurityLevel.STANDARD
    encryption_enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class SecurityConfiguration:
    """Security configuration for pools"""
    encryption_key: str = ""
    credential_rotation_enabled: bool = True
    rotation_interval_hours: int = 24
    access_control_enabled: bool = True
    audit_logging_enabled: bool = True
    ssl_verification: bool = True
    allowed_hosts: List[str] = field(default_factory=list)
    blocked_hosts: List[str] = field(default_factory=list)
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 15
    compliance_standards: List[str] = field(default_factory=list)

class CredentialManager:
    """Encrypted credential management"""
    
    def __init__(self, master_key -> None: str) -> None:
        self.master_key = master_key
        self._credentials_cache = {}
        logger.info("🔐 Credential manager initialized")

    def encrypt_credential(self, credential: str) -> str:
        """Encrypt credential with master key"""
        try:
            # Simple base64 encoding for demo (in production, use proper encryption)
            encoded = base64.b64encode(credential.encode()).decode()
            return f"enc_{encoded}"
        except Exception as e:
            logger.error(f"❌ Failed to encrypt credential: {e}")
            return credential

    def decrypt_credential(self, encrypted_credential: str) -> str:
        """Decrypt credential with master key"""
        try:
            if encrypted_credential.startswith("enc_"):
                encoded = encrypted_credential[4:]  # Remove "enc_" prefix
                decoded = base64.b64decode(encoded.encode()).decode()
                return decoded
            return encrypted_credential
        except Exception as e:
            logger.error(f"❌ Failed to decrypt credential: {e}")
            return encrypted_credential

    def store_credential(self, key: str, credential: str) -> bool:
        """Store encrypted credential"""
        try:
            encrypted = self.encrypt_credential(credential)
            self._credentials_cache[key] = {
                'value': encrypted,
                'created_at': datetime.now(timezone.utc),
                'accessed_count': 0
            }
            logger.debug(f"🔒 Credential stored for key: {key}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store credential for {key}: {e}")
            return False

    def get_credential(self, key: str) -> Optional[str]:
        """Get decrypted credential"""
        try:
            if key in self._credentials_cache:
                credential_data = self._credentials_cache[key]
                credential_data['accessed_count'] += 1
                credential_data['last_accessed'] = datetime.now(timezone.utc)
                return self.decrypt_credential(credential_data['value'])
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get credential for {key}: {e}")
            return None

class PoolConfigurationManager:
    """Central configuration manager for all database pools"""
    
    def __init__(self, master_key -> None: str = "default-demo-key") -> None:
        self.master_key = master_key
        self.credential_manager = CredentialManager(master_key)
        self.configurations: Dict[str, PoolConfig] = {}
        self.security_config = SecurityConfiguration()
        self.security_level = SecurityLevel.STANDARD
        self._config_history: List[Dict[str, Any]] = []
        
        logger.info("⚙️ Pool Configuration Manager initialized")

    def create_config(
        self, 
        pool_id: str,
        database_type: DatabaseType,
        connection_info: DatabaseConnectionInfo,
        **kwargs
    ) -> PoolConfig:
        """Create a new pool configuration"""
        try:
            # Encrypt sensitive information
            if connection_info.password:
                credential_key = f"{pool_id}_password"
                self.credential_manager.store_credential(credential_key, connection_info.password)
                connection_info.password = f"credential:{credential_key}"

            # Create configuration
            config = PoolConfig(
                pool_id=pool_id,
                database_type=database_type,
                connection_info=connection_info,
                created_at=datetime.now(timezone.utc),
                **kwargs
            )
            
            self.configurations[pool_id] = config
            
            # Log configuration creation
            self._log_config_change("create", pool_id, config)
            
            logger.info(f"✅ Configuration created for pool: {pool_id}")
            return config
            
        except Exception as e:
            logger.error(f"❌ Failed to create configuration for {pool_id}: {e}")
            raise

    def get_config(self, pool_id: str) -> Optional[PoolConfig]:
        """Get pool configuration by ID"""
        config = self.configurations.get(pool_id)
        if config:
            # Decrypt password if needed
            if config.connection_info.password.startswith("credential:"):
                credential_key = config.connection_info.password[11:]  # Remove "credential:" prefix
                decrypted_password = self.credential_manager.get_credential(credential_key)
                if decrypted_password:
                    # Create a copy with decrypted password
                    connection_info = DatabaseConnectionInfo(
                        host=config.connection_info.host,
                        port=config.connection_info.port,
                        database=config.connection_info.database,
                        username=config.connection_info.username,
                        password=decrypted_password,
                        ssl_enabled=config.connection_info.ssl_enabled,
                        ssl_cert_path=config.connection_info.ssl_cert_path,
                        connection_string=config.connection_info.connection_string,
                        extra_params=config.connection_info.extra_params
                    )
                    # Update config with decrypted info
                    config.connection_info = connection_info
        
        return config

    def update_config(self, pool_id: str, **updates) -> bool:
        """Update pool configuration"""
        try:
            if pool_id not in self.configurations:
                logger.error(f"❌ Configuration not found for pool: {pool_id}")
                return False
            
            config = self.configurations[pool_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            config.updated_at = datetime.now(timezone.utc)
            
            # Log configuration update
            self._log_config_change("update", pool_id, config, updates)
            
            logger.info(f"✅ Configuration updated for pool: {pool_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update configuration for {pool_id}: {e}")
            return False

    def delete_config(self, pool_id: str) -> bool:
        """Delete pool configuration"""
        try:
            if pool_id in self.configurations:
                config = self.configurations[pool_id]
                
                # Clean up credentials
                if config.connection_info.password.startswith("credential:"):
                    credential_key = config.connection_info.password[11:]
                    if credential_key in self.credential_manager._credentials_cache:
                        del self.credential_manager._credentials_cache[credential_key]
                
                del self.configurations[pool_id]
                
                # Log configuration deletion
                self._log_config_change("delete", pool_id, config)
                
                logger.info(f"✅ Configuration deleted for pool: {pool_id}")
                return True
            
            logger.warning(f"⚠️ Configuration not found for pool: {pool_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete configuration for {pool_id}: {e}")
            return False

    def list_configs(self, database_type: Optional[DatabaseType] = None) -> List[PoolConfig]:
        """List all pool configurations"""
        configs = list(self.configurations.values())
        
        if database_type:
            configs = [config for config in configs if config.database_type == database_type]
        
        return configs

    def set_security_level(self, level -> None: SecurityLevel) -> None:
        """Set global security level"""
        self.security_level = level
        
        # Update security configuration based on level
        if level == SecurityLevel.MINIMAL:
            self.security_config.access_control_enabled = False
            self.security_config.audit_logging_enabled = False
        elif level == SecurityLevel.STANDARD:
            self.security_config.access_control_enabled = True
            self.security_config.audit_logging_enabled = True
        elif level in [SecurityLevel.HARDENED, SecurityLevel.GOVERNMENT, SecurityLevel.FINANCIAL]:
            self.security_config.access_control_enabled = True
            self.security_config.audit_logging_enabled = True
            self.security_config.ssl_verification = True
            self.security_config.credential_rotation_enabled = True
            
            if level == SecurityLevel.FINANCIAL:
                self.security_config.compliance_standards = ['PCI_DSS', 'SOX', 'GLBA']
            elif level == SecurityLevel.GOVERNMENT:
                self.security_config.compliance_standards = ['FISMA', 'FedRAMP', 'NIST']
        
        logger.info(f"🔒 Security level set to: {level.value}")

    def validate_config(self, config: PoolConfig) -> List[str]:
        """Validate pool configuration"""
        errors = []
        
        # Basic validation
        if not config.pool_id:
            errors.append("Pool ID is required")
        
        if not config.connection_info.host:
            errors.append("Host is required")
        
        if config.connection_info.port <= 0:
            errors.append("Valid port is required")
        
        if config.min_connections < 1:
            errors.append("Minimum connections must be at least 1")
        
        if config.max_connections < config.min_connections:
            errors.append("Maximum connections must be >= minimum connections")
        
        # Security validation based on level
        if self.security_level in [SecurityLevel.HARDENED, SecurityLevel.GOVERNMENT, SecurityLevel.FINANCIAL]:
            if not config.connection_info.ssl_enabled:
                errors.append("SSL is required for this security level")
            
            if not config.connection_info.username:
                errors.append("Username is required for this security level")
            
            if not config.connection_info.password:
                errors.append("Password is required for this security level")
        
        return errors

    def _log_config_change(self, action -> None: str, pool_id -> None: str, config -> None: PoolConfig, details -> None: Optional[Dict] = None) -> None:
        """Log configuration changes for audit"""
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'action': action,
            'pool_id': pool_id,
            'database_type': config.database_type.value,
            'security_level': self.security_level.value,
            'details': details or {}
        }
        
        self._config_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self._config_history) > 1000:
            self._config_history = self._config_history[-1000:]

    def export_configs(self, file_path: str) -> bool:
        """Export configurations to file"""
        try:
            export_data = {
                'version': '1.0',
                'exported_at': datetime.now(timezone.utc).isoformat(),
                'security_level': self.security_level.value,
                'configurations': {}
            }
            
            for pool_id, config in self.configurations.items():
                # Don't export decrypted passwords
                config_dict = {
                    'pool_id': config.pool_id,
                    'database_type': config.database_type.value,
                    'connection_info': {
                        'host': config.connection_info.host,
                        'port': config.connection_info.port,
                        'database': config.connection_info.database,
                        'username': config.connection_info.username,
                        'password': '***ENCRYPTED***',  # Don't export passwords
                        'ssl_enabled': config.connection_info.ssl_enabled,
                        'ssl_cert_path': config.connection_info.ssl_cert_path
                    },
                    'min_connections': config.min_connections,
                    'max_connections': config.max_connections,
                    'security_level': config.security_level.value,
                    'created_at': config.created_at.isoformat() if config.created_at else None,
                    'tags': config.tags
                }
                export_data['configurations'][pool_id] = config_dict
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"✅ Configurations exported to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export configurations: {e}")
            return False

    def get_summary(self) -> Dict[str, Any]:
        """Get configuration manager summary"""
        return {
            'total_configs': len(self.configurations),
            'security_level': self.security_level.value,
            'database_types': list(set(config.database_type.value for config in self.configurations.values())),
            'encrypted_credentials': len(self.credential_manager._credentials_cache),
            'config_history_size': len(self._config_history),
            'security_features': {
                'credential_rotation_enabled': self.security_config.credential_rotation_enabled,
                'access_control_enabled': self.security_config.access_control_enabled,
                'audit_logging_enabled': self.security_config.audit_logging_enabled,
                'ssl_verification': self.security_config.ssl_verification
            }
        }

# Global configuration manager instance
_config_manager: Optional[PoolConfigurationManager] = None

def get_configuration_manager(master_key: str = "demo-key") -> PoolConfigurationManager:
    """Get the global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = PoolConfigurationManager(master_key)
    return _config_manager

# Export public interface
__all__ = [
    'PoolConfigurationManager',
    'get_configuration_manager',
    'PoolConfig',
    'DatabaseConnectionInfo',
    'SecurityConfiguration',
    'SecurityLevel',
    'DatabaseType',
    'ConnectionState',
    'CredentialManager'
]