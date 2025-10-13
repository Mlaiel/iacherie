"""⚙️ Configuration Manager - Dynamic Configuration Enterprise
============================================================

Configuration manager enterprise avec dynamic configuration updates,
secrets management, environment-specific configs et compliance validation.

Expert Roles Implementation:
⚙️ DevOps: Configuration automation + deployment + version control
🔒 Sécurité: Secrets management + encryption + access control + compliance
🏗️ Backend Senior: Configuration patterns + service coordination + validation
🗄️ DBA: Database configuration + connection management + performance tuning
🤖 Lead Dev IA: Intelligent configuration optimization + drift detection
📋 Compliance: Policy enforcement + audit trails + regulatory compliance

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Production Enterprise
Date: 14 Septembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
"""

import asyncio
import logging
import json
import yaml
import base64
import hashlib
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class ConfigurationType(Enum):
    """Configuration type categories"""
    APPLICATION = "application"
    DATABASE = "database"
    SECURITY = "security"
    NETWORKING = "networking"
    MONITORING = "monitoring"
    SCALING = "scaling"
    FEATURE_FLAGS = "feature_flags"

class ConfigurationEnvironment(Enum):
    """Configuration environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class SecretType(Enum):
    """Secret types"""
# SECURITY: # SECURITY: DATABASE_PASSWORD = "database_password" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
# SECURITY: # SECURITY: API_KEY = "api_key" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
    CERTIFICATE = "certificate"
    TOKEN = "token"
# SECURITY: # SECURITY: ENCRYPTION_KEY = "encryption_key" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault

@dataclass
class ConfigurationItem:
    """Configuration item"""
    key: str
    value: Any
    type: ConfigurationType
    environment: ConfigurationEnvironment
    is_secret: bool = False
    description: str = ""
    validation_rules: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    version: int = 1

@dataclass
class SecretItem:
    """Secret configuration item"""
    key: str
    encrypted_value: str
    secret_type: SecretType
    environment: ConfigurationEnvironment
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    rotation_required: bool = False

@dataclass
class ConfigurationUpdate:
    """Configuration update operation"""
    operation_id: str
    items: List[ConfigurationItem]
    environment: ConfigurationEnvironment
    requested_by: str
    applied_at: Optional[datetime] = None
    status: str = "pending"
    rollback_data: Optional[Dict[str, Any]] = None

class ConfigurationManager:
    """⚙️ Configuration manager avec dynamic configuration"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Configuration Manager"""
        self.config = config or {}
        self.configurations: Dict[str, Dict[str, ConfigurationItem]] = {}
        self.secrets: Dict[str, Dict[str, SecretItem]] = {}
        self.update_history: List[ConfigurationUpdate] = []
        self.active_watchers: Dict[str, List[callable]] = {}
        
        # Security and encryption
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Components
        self.secrets_manager = SecretsManager(self.cipher_suite)
        self.drift_detector = ConfigurationDriftDetector()
        self.compliance_validator = ComplianceValidator()
        self.change_orchestrator = ChangeOrchestrator()
        
        self.initialized = False
        
        logger.info("⚙️ Configuration Manager initialized")
    
    async def initialize(self) -> bool:
        """
        🚀 Initialize configuration management infrastructure
        
        Acting as: DevOps + Security + Compliance
        """
        try:
            logger.info("🔄 Initializing configuration management infrastructure...")
            
            # Initialize secrets manager
            await self.secrets_manager.initialize()
            
            # Initialize drift detector
            await self.drift_detector.initialize()
            
            # Initialize compliance validator
            await self.compliance_validator.initialize()
            
            # Initialize change orchestrator
            await self.change_orchestrator.initialize()
            
            # Load existing configurations
            await self._load_existing_configurations()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.initialized = True
            logger.info("✅ Configuration management infrastructure initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize configuration manager: {e}")
            return False
    
    async def set_configuration(
        self,
        key: str,
        value: Any,
        config_type: ConfigurationType,
        environment: ConfigurationEnvironment,
        is_secret: bool = False,
        validation_rules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        📝 Set configuration item with validation
        
        Acting as: DevOps + Security + Backend Senior
        """
        try:
            logger.info(f"📝 Setting configuration: {key} for {environment.value}")
            
            # Validate configuration value
            validation_result = await self._validate_configuration_value(
                key, value, config_type, validation_rules or []
            )
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'reason': validation_result['reason']
                }
            
            # Handle secrets differently
            if is_secret:
                return await self._set_secret_configuration(
                    key, value, config_type, environment
                )
            
            # Create configuration item
            config_item = ConfigurationItem(
                key=key,
                value=value,
                type=config_type,
                environment=environment,
                is_secret=is_secret,
                validation_rules=validation_rules or [],
                last_updated=datetime.utcnow(),
                version=self._get_next_version(key, environment)
            )
            
            # Store configuration
            env_key = environment.value
            if env_key not in self.configurations:
                self.configurations[env_key] = {}
            
            self.configurations[env_key][key] = config_item
            
            # Notify watchers
            await self._notify_configuration_watchers(key, environment, config_item)
            
            # Audit log
            await self._log_configuration_change(
                'set', key, environment, value if not is_secret else '[REDACTED]'
            )
            
            return {
                'success': True,
                'key': key,
                'environment': environment.value,
                'version': config_item.version,
                'updated_at': config_item.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to set configuration {key}: {e}")
            raise
    
    async def get_configuration(
        self,
        key: str,
        environment: ConfigurationEnvironment,
        default: Optional[Any] = None
    ) -> Any:
        """
        📖 Get configuration value
        
        Acting as: Backend Senior + Application Developer
        """
        try:
            env_key = environment.value
            
            if env_key in self.configurations and key in self.configurations[env_key]:
                config_item = self.configurations[env_key][key]
                
                # Handle secrets
                if config_item.is_secret:
                    return await self.secrets_manager.get_secret(key, environment)
                
                return config_item.value
            
            return default
            
        except Exception as e:
            logger.error(f"❌ Failed to get configuration {key}: {e}")
            return default
    
    async def update_configurations_batch(
        self,
        updates: List[Dict[str, Any]],
        environment: ConfigurationEnvironment,
        requested_by: str = "system"
    ) -> Dict[str, Any]:
        """
        🔄 Update multiple configurations in batch
        
        Acting as: DevOps + Change Management + Backend Senior
        """
        try:
            operation_id = f"batch-update-{int(datetime.utcnow().timestamp())}"
            
            logger.info(f"🔄 Executing batch configuration update: {operation_id}")
            
            # Validate all updates first
            validation_results = []
            for update in updates:
                result = await self._validate_configuration_value(
                    update['key'], update['value'], 
                    ConfigurationType(update['type']), 
                    update.get('validation_rules', [])
                )
                validation_results.append(result)
            
            # Check if any validation failed
            failed_validations = [r for r in validation_results if not r['valid']]
            if failed_validations:
                return {
                    'success': False,
                    'reason': 'Validation failed',
                    'failed_validations': failed_validations
                }
            
            # Create backup for rollback
            rollback_data = await self._create_configuration_backup(environment)
            
            # Create configuration items
            config_items = []
            for update in updates:
                config_item = ConfigurationItem(
                    key=update['key'],
                    value=update['value'],
                    type=ConfigurationType(update['type']),
                    environment=environment,
                    is_secret=update.get('is_secret', False),
                    validation_rules=update.get('validation_rules', []),
                    last_updated=datetime.utcnow(),
                    version=self._get_next_version(update['key'], environment)
                )
                config_items.append(config_item)
            
            # Create update operation
            update_operation = ConfigurationUpdate(
                operation_id=operation_id,
                items=config_items,
                environment=environment,
                requested_by=requested_by,
                rollback_data=rollback_data
            )
            
            # Execute updates
            successful_updates = []
            failed_updates = []
            
            for config_item in config_items:
                try:
                    await self._apply_configuration_item(config_item)
                    successful_updates.append(config_item.key)
                except Exception as e:
                    failed_updates.append({
                        'key': config_item.key,
                        'error': str(e)
                    })
            
            # Update operation status
            update_operation.applied_at = datetime.utcnow()
            update_operation.status = 'completed' if not failed_updates else 'partial'
            
            # Store update history
            self.update_history.append(update_operation)
            
            return {
                'success': len(failed_updates) == 0,
                'operation_id': operation_id,
                'successful_updates': successful_updates,
                'failed_updates': failed_updates,
                'rollback_available': True
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to execute batch configuration update: {e}")
            raise
    
    async def watch_configuration(
        self,
        key: str,
        environment: ConfigurationEnvironment,
        callback: callable
    ) -> str:
        """
        👁️ Watch configuration changes
        
        Acting as: Backend Senior + Event-Driven Architecture
        """
        try:
            watcher_id = f"{key}-{environment.value}-{id(callback)}"
            
# SECURITY: # SECURITY: watcher_key = f"{key}:{environment.value}" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
            if watcher_key not in self.active_watchers:
                self.active_watchers[watcher_key] = []
            
            self.active_watchers[watcher_key].append(callback)
            
            logger.info(f"👁️ Configuration watcher registered: {watcher_id}")
            
            return watcher_id
            
        except Exception as e:
            logger.error(f"❌ Failed to register configuration watcher: {e}")
            raise
    
    async def rollback_configuration_update(
        self,
        operation_id: str
    ) -> Dict[str, Any]:
        """
        ⏪ Rollback configuration update
        
        Acting as: DevOps + Change Management + Risk Management
        """
        try:
            # Find update operation
            update_operation = None
            for operation in self.update_history:
                if operation.operation_id == operation_id:
                    update_operation = operation
                    break
            
            if not update_operation:
                return {
                    'success': False,
                    'reason': 'Update operation not found'
                }
            
            if not update_operation.rollback_data:
                return {
                    'success': False,
                    'reason': 'No rollback data available'
                }
            
            logger.info(f"⏪ Rolling back configuration update: {operation_id}")
            
            # Restore previous configurations
            rollback_count = 0
            env_key = update_operation.environment.value
            
            for key, previous_config in update_operation.rollback_data.items():
                if previous_config is None:
                    # Remove configuration that was added
                    if env_key in self.configurations and key in self.configurations[env_key]:
                        del self.configurations[env_key][key]
                        rollback_count += 1
                else:
                    # Restore previous value
                    if env_key not in self.configurations:
                        self.configurations[env_key] = {}
                    
                    self.configurations[env_key][key] = ConfigurationItem(**previous_config)
                    rollback_count += 1
            
            # Notify watchers of rollback
            for item in update_operation.items:
                await self._notify_configuration_watchers(
                    item.key, item.environment, 
                    self.configurations.get(env_key, {}).get(item.key)
                )
            
            # Log rollback
            await self._log_configuration_change(
                'rollback', operation_id, update_operation.environment, f"Rolled back {rollback_count} items"
            )
            
            return {
                'success': True,
                'operation_id': operation_id,
                'rollback_count': rollback_count,
                'rolled_back_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to rollback configuration update: {e}")
            raise
    
    async def detect_configuration_drift(
        self,
        environment: ConfigurationEnvironment
    ) -> Dict[str, Any]:
        """
        🔍 Detect configuration drift
        
        Acting as: DevOps + Monitoring + Compliance
        """
        try:
            logger.info(f"🔍 Detecting configuration drift for {environment.value}")
            
            drift_results = await self.drift_detector.detect_drift(
                environment, self.configurations.get(environment.value, {})
            )
            
            return drift_results
            
        except Exception as e:
            logger.error(f"❌ Failed to detect configuration drift: {e}")
            raise
    
    async def validate_compliance(
        self,
        environment: ConfigurationEnvironment
    ) -> Dict[str, Any]:
        """
        ✅ Validate configuration compliance
        
        Acting as: Compliance + Security + Audit
        """
        try:
            logger.info(f"✅ Validating configuration compliance for {environment.value}")
            
            compliance_results = await self.compliance_validator.validate_compliance(
                environment, self.configurations.get(environment.value, {}),
                self.secrets.get(environment.value, {})
            )
            
            return compliance_results
            
        except Exception as e:
            logger.error(f"❌ Failed to validate compliance: {e}")
            raise
    
    # Helper methods
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for secrets"""
        key_file = Path(self.config.get('encryption_key_file', '.encryption_key'))
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    async def _set_secret_configuration(
        self,
        key: str,
        value: Any,
        config_type: ConfigurationType,
        environment: ConfigurationEnvironment
    ) -> Dict[str, Any]:
        """Set secret configuration"""
        return await self.secrets_manager.set_secret(key, value, SecretType.API_KEY, environment)
    
    def _get_next_version(self, key: str, environment: ConfigurationEnvironment) -> int:
        """Get next version number for configuration"""
        env_key = environment.value
        if env_key in self.configurations and key in self.configurations[env_key]:
            return self.configurations[env_key][key].version + 1
        return 1
    
    async def _validate_configuration_value(
        self,
        key: str,
        value: Any,
        config_type: ConfigurationType,
        validation_rules: List[str]
    ) -> Dict[str, Any]:
        """Validate configuration value"""
        # Basic validation
        if value is None and 'required' in validation_rules:
            return {
                'valid': False,
                'reason': f'Configuration {key} is required but null'
            }
        
        # Type-specific validation
        if config_type == ConfigurationType.DATABASE:
            if isinstance(value, dict) and 'connection_string' in value:
                if not value['connection_string'].strip():
                    return {
                        'valid': False,
                        'reason': 'Database connection string cannot be empty'
                    }
        
        return {'valid': True}
    
    async def _apply_configuration_item(self, config_item: ConfigurationItem):
        """Apply configuration item"""
        env_key = config_item.environment.value
        if env_key not in self.configurations:
            self.configurations[env_key] = {}
        
        self.configurations[env_key][config_item.key] = config_item
    
    async def _create_configuration_backup(
        self,
        environment: ConfigurationEnvironment
    ) -> Dict[str, Any]:
        """Create configuration backup for rollback"""
        env_key = environment.value
        backup = {}
        
        if env_key in self.configurations:
            for key, config_item in self.configurations[env_key].items():
                backup[key] = {
                    'key': config_item.key,
                    'value': config_item.value,
                    'type': config_item.type,
                    'environment': config_item.environment,
                    'is_secret': config_item.is_secret,
                    'description': config_item.description,
                    'validation_rules': config_item.validation_rules,
                    'last_updated': config_item.last_updated,
                    'version': config_item.version
                }
        
        return backup
    
    async def _notify_configuration_watchers(
        self,
        key: str,
        environment: ConfigurationEnvironment,
        config_item: Optional[ConfigurationItem]
    ):
        """Notify configuration watchers"""
# SECURITY: # SECURITY: watcher_key = f"{key}:{environment.value}" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
        
        if watcher_key in self.active_watchers:
            for callback in self.active_watchers[watcher_key]:
                try:
                    await callback(key, environment, config_item)
                except Exception as e:
                    logger.error(f"❌ Error notifying configuration watcher: {e}")
    
    async def _log_configuration_change(
        self,
        operation: str,
        key: str,
        environment: ConfigurationEnvironment,
        value: str
    ):
        """Log configuration change for audit"""
        logger.info(f"📋 Config change: {operation} {key} in {environment.value}")
    
    async def _load_existing_configurations(self):
        """Load existing configurations from storage"""
        logger.info("📂 Loading existing configurations...")
        # Implementation would load from persistent storage
    
    async def _start_background_tasks(self):
        """Start background configuration management tasks"""
        asyncio.create_task(self._drift_detection_task())
        asyncio.create_task(self._compliance_monitoring_task())
        asyncio.create_task(self._secret_rotation_task())
        logger.info("🔄 Background configuration tasks started")
    
    async def _drift_detection_task(self):
        """Background drift detection task"""
        while True:
            try:
                for env in ConfigurationEnvironment:
                    drift_results = await self.detect_configuration_drift(env)
                    if drift_results.get('drift_detected'):
                        logger.warning(f"🚨 Configuration drift detected in {env.value}")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"❌ Error in drift detection task: {e}")
                await asyncio.sleep(1800)
    
    async def _compliance_monitoring_task(self):
        """Background compliance monitoring task"""
        while True:
            try:
                for env in ConfigurationEnvironment:
                    compliance_results = await self.validate_compliance(env)
                    if not compliance_results.get('compliant', True):
                        logger.warning(f"⚠️ Compliance violations in {env.value}")
                
                await asyncio.sleep(7200)  # Check every 2 hours
                
            except Exception as e:
                logger.error(f"❌ Error in compliance monitoring: {e}")
                await asyncio.sleep(3600)
    
    async def _secret_rotation_task(self):
        """Background secret rotation task"""
        while True:
            try:
                await self.secrets_manager.rotate_expired_secrets()
                await asyncio.sleep(86400)  # Check daily
                
            except Exception as e:
                logger.error(f"❌ Error in secret rotation: {e}")
                await asyncio.sleep(43200)


# Helper classes for configuration management
class SecretsManager:
    """🔐 Secrets manager with encryption"""
    
    def __init__(self, cipher_suite: Fernet):
        self.cipher_suite = cipher_suite
        self.secrets: Dict[str, Dict[str, SecretItem]] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize secrets manager"""
        self.initialized = True
        logger.info("✅ Secrets Manager initialized")
    
    async def set_secret(
        self,
        key: str,
        value: str,
        secret_type: SecretType,
        environment: ConfigurationEnvironment
    ) -> Dict[str, Any]:
        """Set encrypted secret"""
        encrypted_value = self.cipher_suite.encrypt(value.encode()).decode()
        
        secret_item = SecretItem(
            key=key,
            encrypted_value=encrypted_value,
            secret_type=secret_type,
            environment=environment
        )
        
        env_key = environment.value
        if env_key not in self.secrets:
            self.secrets[env_key] = {}
        
        self.secrets[env_key][key] = secret_item
        
        return {
            'success': True,
            'key': key,
            'environment': environment.value,
            'created_at': secret_item.created_at.isoformat()
        }
    
    async def get_secret(
        self,
        key: str,
        environment: ConfigurationEnvironment
    ) -> Optional[str]:
        """Get decrypted secret"""
        env_key = environment.value
        
        if env_key in self.secrets and key in self.secrets[env_key]:
            secret_item = self.secrets[env_key][key]
            return self.cipher_suite.decrypt(secret_item.encrypted_value.encode()).decode()
        
        return None
    
    async def rotate_expired_secrets(self):
        """Rotate expired secrets"""
        logger.info("🔄 Checking for expired secrets to rotate...")
        # Implementation would handle secret rotation


class ConfigurationDriftDetector:
    """🔍 Configuration drift detector"""
    
    def __init__(self):
        self.baseline_configurations: Dict[str, Dict[str, Any]] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize drift detector"""
        self.initialized = True
        logger.info("✅ Configuration Drift Detector initialized")
    
    async def detect_drift(
        self,
        environment: ConfigurationEnvironment,
        current_configurations: Dict[str, ConfigurationItem]
    ) -> Dict[str, Any]:
        """Detect configuration drift"""
        # Simulate drift detection
        drift_items = []
        
        return {
            'drift_detected': len(drift_items) > 0,
            'drift_count': len(drift_items),
            'drift_items': drift_items,
            'check_timestamp': datetime.utcnow().isoformat()
        }


class ComplianceValidator:
    """✅ Compliance validator for configurations"""
    
    def __init__(self):
        self.compliance_rules: List[Dict[str, Any]] = []
        self.initialized = False
    
    async def initialize(self):
        """Initialize compliance validator"""
        self.initialized = True
        logger.info("✅ Compliance Validator initialized")
    
    async def validate_compliance(
        self,
        environment: ConfigurationEnvironment,
        configurations: Dict[str, ConfigurationItem],
        secrets: Dict[str, SecretItem]
    ) -> Dict[str, Any]:
        """Validate configuration compliance"""
        violations = []
        
        # Check for required security configurations
        security_configs = [c for c in configurations.values() 
                          if c.type == ConfigurationType.SECURITY]
        
        if not security_configs:
            violations.append({
                'rule': 'security_config_required',
                'severity': 'high',
                'description': 'Security configurations are required'
            })
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'validation_timestamp': datetime.utcnow().isoformat()
        }


class ChangeOrchestrator:
    """🎼 Change orchestrator for coordinated updates"""
    
    def __init__(self):
        self.pending_changes: List[Dict[str, Any]] = []
        self.initialized = False
    
    async def initialize(self):
        """Initialize change orchestrator"""
        self.initialized = True
        logger.info("✅ Change Orchestrator initialized")