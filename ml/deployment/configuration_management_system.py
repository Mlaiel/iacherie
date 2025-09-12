"""🔧 Configuration Management System - Enterprise Config Management
=====================================================================
Module: ml/deployment/configuration_management_system.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE CONFIGURATION MANAGEMENT
Centralized configuration management for ML deployments
- Environment-specific configurations (dev, staging, prod)
- Secret management avec encryption
- Creator-specific configuration profiles
- Configuration validation et rollback
"""

import asyncio
import logging
import time
import uuid
import json
import yaml
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import base64
from cryptography.fernet import Fernet
from collections import defaultdict
import os

# Configuration
logger = logging.getLogger(__name__)

class Environment(Enum):
    """Environnements de déploiement"""
    
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    EDGE = "edge"

class ConfigType(Enum):
    """Types de configuration"""
    
    MODEL = "model"
    DEPLOYMENT = "deployment"
    FEATURE = "feature"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    CREATOR_PROFILE = "creator_profile"

class SecretType(Enum):
    """Types de secrets"""
    
    API_KEY = "api_key"
    DATABASE_PASSWORD = "database_password"
    CERTIFICATE = "certificate"
    ENCRYPTION_KEY = "encryption_key"
    OAUTH_TOKEN = "oauth_token"

@dataclass
class ConfigurationItem:
    """Item de configuration"""
    
    config_id: str
    name: str
    config_type: ConfigType
    environment: Environment
    value: Any
    description: str
    creator_types: List[str] = field(default_factory=list)
    is_secret: bool = False
    is_encrypted: bool = False
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    validation_schema: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'config_id': self.config_id,
            'name': self.name,
            'config_type': self.config_type.value,
            'environment': self.environment.value,
            'value': self.value if not self.is_secret else "[HIDDEN]",
            'description': self.description,
            'creator_types': self.creator_types,
            'is_secret': self.is_secret,
            'is_encrypted': self.is_encrypted,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'tags': self.tags,
            'dependencies': self.dependencies,
            'validation_schema': self.validation_schema
        }

@dataclass
class ConfigurationProfile:
    """Profil de configuration pour un creator type"""
    
    profile_id: str
    creator_type: str
    environment: Environment
    configurations: Dict[str, str]  # config_name -> config_id
    overrides: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'profile_id': self.profile_id,
            'creator_type': self.creator_type,
            'environment': self.environment.value,
            'configurations': self.configurations,
            'overrides': self.overrides,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class ConfigurationChange:
    """Historique des changements"""
    
    change_id: str
    config_id: str
    old_value: Any
    new_value: Any
    changed_by: str
    change_reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    rollback_available: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'change_id': self.change_id,
            'config_id': self.config_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'changed_by': self.changed_by,
            'change_reason': self.change_reason,
            'timestamp': self.timestamp.isoformat(),
            'rollback_available': self.rollback_available
        }

class ConfigurationManagementSystem:
    """
    🔧 Configuration Management System
    
    Système de gestion de configuration avec:
    - Configuration centralisée multi-environnement
    - Gestion sécurisée des secrets
    - Profils creator-specific
    - Validation et rollback automatique
    """
    
    def __init__(
        self,
        storage_path: str = "config",
        enable_encryption: bool = True,
        config_validation: bool = True,
        auto_backup: bool = True
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.enable_encryption = enable_encryption
        self.config_validation = config_validation
        self.auto_backup = auto_backup
        
        # Stockage des configurations
        self.configurations: Dict[str, ConfigurationItem] = {}
        self.profiles: Dict[str, ConfigurationProfile] = {}
        self.change_history: List[ConfigurationChange] = []
        
        # Index pour recherche rapide
        self.config_by_env: Dict[Environment, List[str]] = defaultdict(list)
        self.config_by_type: Dict[ConfigType, List[str]] = defaultdict(list)
        self.config_by_creator: Dict[str, List[str]] = defaultdict(list)
        
        # Gestion de l'encryption
        if self.enable_encryption:
            self.encryption_key = self._load_or_create_encryption_key()
            self.cipher_suite = Fernet(self.encryption_key)
        
        # Schémas de validation par défaut
        self.default_schemas = {
            ConfigType.MODEL: {
                "type": "object",
                "properties": {
                    "model_name": {"type": "string"},
                    "version": {"type": "string"},
                    "parameters": {"type": "object"}
                },
                "required": ["model_name", "version"]
            },
            ConfigType.DEPLOYMENT: {
                "type": "object",
                "properties": {
                    "replicas": {"type": "integer", "minimum": 1},
                    "cpu_limit": {"type": "string"},
                    "memory_limit": {"type": "string"}
                },
                "required": ["replicas"]
            }
        }
        
        # Configurations par défaut par creator type
        self.creator_defaults = {
            'musician': {
                'model_timeout_seconds': 30,
                'max_audio_length_seconds': 300,
                'supported_formats': ['mp3', 'wav', 'flac'],
                'quality_threshold': 0.85
            },
            'blogger': {
                'model_timeout_seconds': 15,
                'max_text_length': 10000,
                'supported_languages': ['en', 'fr', 'de', 'es'],
                'quality_threshold': 0.80
            },
            'photographer': {
                'model_timeout_seconds': 45,
                'max_image_size_mb': 50,
                'supported_formats': ['jpg', 'png', 'tiff', 'raw'],
                'quality_threshold': 0.90
            },
            'influencer': {
                'model_timeout_seconds': 20,
                'max_posts_per_batch': 100,
                'supported_platforms': ['instagram', 'tiktok', 'youtube'],
                'quality_threshold': 0.75
            }
        }
        
        # Charger les configurations existantes
        asyncio.create_task(self._load_existing_configurations())
        
        logger.info("🔧 Configuration Management System initialized")
    
    async def create_configuration(
        self,
        name: str,
        config_type: ConfigType,
        environment: Environment,
        value: Any,
        description: str,
        creator_types: Optional[List[str]] = None,
        is_secret: bool = False,
        created_by: str = "",
        tags: Optional[List[str]] = None,
        validation_schema: Optional[Dict[str, Any]] = None
    ) -> str:
        """Créer une nouvelle configuration"""
        
        config_id = f"config_{uuid.uuid4().hex[:8]}"
        
        # Validation
        if self.config_validation:
            await self._validate_configuration_value(config_type, value, validation_schema)
        
        # Encryption si nécessaire
        final_value = value
        is_encrypted = False
        
        if is_secret and self.enable_encryption:
            final_value = self._encrypt_value(value)
            is_encrypted = True
        
        # Créer l'item de configuration
        config_item = ConfigurationItem(
            config_id=config_id,
            name=name,
            config_type=config_type,
            environment=environment,
            value=final_value,
            description=description,
            creator_types=creator_types or [],
            is_secret=is_secret,
            is_encrypted=is_encrypted,
            created_by=created_by,
            tags=tags or [],
            validation_schema=validation_schema or self.default_schemas.get(config_type)
        )
        
        # Stocker
        self.configurations[config_id] = config_item
        
        # Mettre à jour les index
        self.config_by_env[environment].append(config_id)
        self.config_by_type[config_type].append(config_id)
        for creator_type in config_item.creator_types:
            self.config_by_creator[creator_type].append(config_id)
        
        # Persister
        await self._persist_configuration(config_item)
        
        # Backup automatique
        if self.auto_backup:
            await self._create_backup()
        
        logger.info(f"🔧 Created configuration: {name} [{config_id}]")
        return config_id
    
    async def update_configuration(
        self,
        config_id: str,
        new_value: Any,
        changed_by: str,
        change_reason: str = "Configuration update"
    ) -> bool:
        """Mettre à jour une configuration"""
        
        if config_id not in self.configurations:
            raise ValueError(f"Configuration not found: {config_id}")
        
        config_item = self.configurations[config_id]
        old_value = config_item.value
        
        # Validation
        if self.config_validation:
            await self._validate_configuration_value(
                config_item.config_type, 
                new_value, 
                config_item.validation_schema
            )
        
        # Enregistrer le changement
        change = ConfigurationChange(
            change_id=f"change_{uuid.uuid4().hex[:8]}",
            config_id=config_id,
            old_value=old_value if not config_item.is_secret else "[HIDDEN]",
            new_value=new_value if not config_item.is_secret else "[HIDDEN]",
            changed_by=changed_by,
            change_reason=change_reason
        )
        
        self.change_history.append(change)
        
        # Encryption si nécessaire
        final_value = new_value
        if config_item.is_secret and self.enable_encryption:
            final_value = self._encrypt_value(new_value)
        
        # Mettre à jour
        config_item.value = final_value
        config_item.updated_at = datetime.now()
        
        # Persister
        await self._persist_configuration(config_item)
        await self._persist_change(change)
        
        logger.info(f"🔄 Updated configuration: {config_item.name}")
        return True
    
    async def get_configuration(
        self,
        config_id: str,
        decrypt_secrets: bool = False
    ) -> Optional[ConfigurationItem]:
        """Récupérer une configuration"""
        
        if config_id not in self.configurations:
            return None
        
        config_item = self.configurations[config_id]
        
        # Déchiffrer si demandé et autorisé
        if decrypt_secrets and config_item.is_secret and config_item.is_encrypted:
            decrypted_value = self._decrypt_value(config_item.value)
            # Créer une copie avec la valeur déchiffrée
            decrypted_item = ConfigurationItem(**config_item.__dict__)
            decrypted_item.value = decrypted_value
            return decrypted_item
        
        return config_item
    
    async def get_configuration_by_name(
        self,
        name: str,
        environment: Environment,
        decrypt_secrets: bool = False
    ) -> Optional[ConfigurationItem]:
        """Récupérer une configuration par nom et environnement"""
        
        for config_item in self.configurations.values():
            if config_item.name == name and config_item.environment == environment:
                return await self.get_configuration(config_item.config_id, decrypt_secrets)
        
        return None
    
    async def create_creator_profile(
        self,
        creator_type: str,
        environment: Environment,
        base_configurations: Optional[Dict[str, Any]] = None
    ) -> str:
        """Créer un profil de configuration pour un creator type"""
        
        profile_id = f"profile_{uuid.uuid4().hex[:8]}"
        
        # Configurations de base pour ce creator type
        base_configs = base_configurations or self.creator_defaults.get(creator_type, {})
        
        # Créer les configurations individuelles
        configurations = {}
        
        for config_name, config_value in base_configs.items():
            config_id = await self.create_configuration(
                name=f"{creator_type}_{config_name}",
                config_type=ConfigType.CREATOR_PROFILE,
                environment=environment,
                value=config_value,
                description=f"Default {config_name} for {creator_type}",
                creator_types=[creator_type],
                created_by="system"
            )
            configurations[config_name] = config_id
        
        # Créer le profil
        profile = ConfigurationProfile(
            profile_id=profile_id,
            creator_type=creator_type,
            environment=environment,
            configurations=configurations
        )
        
        self.profiles[profile_id] = profile
        
        # Persister
        await self._persist_profile(profile)
        
        logger.info(f"👤 Created creator profile: {creator_type} [{environment.value}]")
        return profile_id
    
    async def get_creator_configuration(
        self,
        creator_type: str,
        environment: Environment,
        config_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Récupérer la configuration complète pour un creator type"""
        
        # Trouver le profil
        profile = None
        for p in self.profiles.values():
            if p.creator_type == creator_type and p.environment == environment:
                profile = p
                break
        
        if not profile:
            # Créer un profil par défaut
            profile_id = await self.create_creator_profile(creator_type, environment)
            profile = self.profiles[profile_id]
        
        # Récupérer toutes les configurations
        config_values = {}
        
        for config_key, config_id in profile.configurations.items():
            if config_name is None or config_key == config_name:
                config_item = await self.get_configuration(config_id, decrypt_secrets=True)
                if config_item:
                    config_values[config_key] = config_item.value
        
        # Appliquer les overrides
        config_values.update(profile.overrides)
        
        return config_values
    
    async def list_configurations(
        self,
        environment: Optional[Environment] = None,
        config_type: Optional[ConfigType] = None,
        creator_type: Optional[str] = None,
        include_secrets: bool = False
    ) -> List[Dict[str, Any]]:
        """Lister les configurations selon des critères"""
        
        filtered_configs = []
        
        for config_item in self.configurations.values():
            # Filtres
            if environment and config_item.environment != environment:
                continue
            
            if config_type and config_item.config_type != config_type:
                continue
            
            if creator_type and creator_type not in config_item.creator_types:
                continue
            
            if config_item.is_secret and not include_secrets:
                continue
            
            filtered_configs.append(config_item.to_dict())
        
        return filtered_configs
    
    async def rollback_configuration(
        self,
        config_id: str,
        target_change_id: str,
        changed_by: str
    ) -> bool:
        """Effectuer un rollback vers un changement spécifique"""
        
        if config_id not in self.configurations:
            raise ValueError(f"Configuration not found: {config_id}")
        
        # Trouver le changement cible
        target_change = None
        for change in self.change_history:
            if change.change_id == target_change_id and change.config_id == config_id:
                target_change = change
                break
        
        if not target_change or not target_change.rollback_available:
            raise ValueError(f"Rollback not available for change: {target_change_id}")
        
        # Effectuer le rollback
        await self.update_configuration(
            config_id=config_id,
            new_value=target_change.old_value,
            changed_by=changed_by,
            change_reason=f"Rollback to change {target_change_id}"
        )
        
        logger.info(f"🔄 Rolled back configuration {config_id} to change {target_change_id}")
        return True
    
    async def validate_environment_configs(
        self,
        environment: Environment
    ) -> Dict[str, Any]:
        """Valider toutes les configurations d'un environnement"""
        
        env_configs = [
            config_id for config_id in self.config_by_env[environment]
            if config_id in self.configurations
        ]
        
        validation_results = {
            'total_configs': len(env_configs),
            'valid_configs': 0,
            'invalid_configs': 0,
            'issues': []
        }
        
        for config_id in env_configs:
            config_item = self.configurations[config_id]
            
            try:
                await self._validate_configuration_value(
                    config_item.config_type,
                    config_item.value,
                    config_item.validation_schema
                )
                validation_results['valid_configs'] += 1
            except Exception as e:
                validation_results['invalid_configs'] += 1
                validation_results['issues'].append({
                    'config_id': config_id,
                    'config_name': config_item.name,
                    'error': str(e)
                })
        
        return validation_results
    
    def _load_or_create_encryption_key(self) -> bytes:
        """Charger ou créer la clé d'encryption"""
        
        key_file = self.storage_path / ".encryption_key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Créer une nouvelle clé
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Permissions restrictives
            os.chmod(key_file, 0o600)
            return key
    
    def _encrypt_value(self, value: Any) -> str:
        """Chiffrer une valeur"""
        
        if not self.enable_encryption:
            return value
        
        # Sérialiser en JSON puis chiffrer
        json_value = json.dumps(value)
        encrypted_bytes = self.cipher_suite.encrypt(json_value.encode())
        return base64.b64encode(encrypted_bytes).decode()
    
    def _decrypt_value(self, encrypted_value: str) -> Any:
        """Déchiffrer une valeur"""
        
        if not self.enable_encryption:
            return encrypted_value
        
        # Décoder base64 puis déchiffrer
        encrypted_bytes = base64.b64decode(encrypted_value.encode())
        decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
        json_value = decrypted_bytes.decode()
        return json.loads(json_value)
    
    async def _validate_configuration_value(
        self,
        config_type: ConfigType,
        value: Any,
        schema: Optional[Dict[str, Any]]
    ):
        """Valider une valeur de configuration"""
        
        if not self.config_validation or not schema:
            return
        
        # Validation basique par type
        if config_type == ConfigType.MODEL:
            if not isinstance(value, dict):
                raise ValueError("Model configuration must be a dictionary")
            
            if 'model_name' not in value:
                raise ValueError("Model configuration must include 'model_name'")
        
        elif config_type == ConfigType.DEPLOYMENT:
            if not isinstance(value, dict):
                raise ValueError("Deployment configuration must be a dictionary")
            
            if 'replicas' in value and not isinstance(value['replicas'], int):
                raise ValueError("Replicas must be an integer")
            
            if 'replicas' in value and value['replicas'] < 1:
                raise ValueError("Replicas must be at least 1")
    
    async def _persist_configuration(self, config_item: ConfigurationItem):
        """Persister une configuration"""
        
        config_file = self.storage_path / f"configs/{config_item.config_id}.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config_item.to_dict(), f, indent=2)
    
    async def _persist_profile(self, profile: ConfigurationProfile):
        """Persister un profil"""
        
        profile_file = self.storage_path / f"profiles/{profile.profile_id}.json"
        profile_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(profile_file, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
    
    async def _persist_change(self, change: ConfigurationChange):
        """Persister un changement"""
        
        change_file = self.storage_path / f"changes/{change.change_id}.json"
        change_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(change_file, 'w') as f:
            json.dump(change.to_dict(), f, indent=2)
    
    async def _create_backup(self):
        """Créer un backup automatique"""
        
        backup_dir = self.storage_path / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup des configurations (sans les secrets)
        backup_data = {
            'configurations': [
                config.to_dict() for config in self.configurations.values()
            ],
            'profiles': [
                profile.to_dict() for profile in self.profiles.values()
            ]
        }
        
        backup_file = backup_dir / "configuration_backup.json"
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        logger.debug(f"💾 Configuration backup created: {backup_file}")
    
    async def _load_existing_configurations(self):
        """Charger les configurations existantes"""
        
        configs_dir = self.storage_path / "configs"
        if not configs_dir.exists():
            return
        
        for config_file in configs_dir.glob("*.json"):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                
                # Reconstruire l'objet ConfigurationItem
                config_item = ConfigurationItem(
                    config_id=data['config_id'],
                    name=data['name'],
                    config_type=ConfigType(data['config_type']),
                    environment=Environment(data['environment']),
                    value=data['value'],
                    description=data['description'],
                    creator_types=data.get('creator_types', []),
                    is_secret=data.get('is_secret', False),
                    is_encrypted=data.get('is_encrypted', False),
                    version=data.get('version', '1.0.0'),
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at']),
                    created_by=data.get('created_by', ''),
                    tags=data.get('tags', []),
                    dependencies=data.get('dependencies', []),
                    validation_schema=data.get('validation_schema')
                )
                
                self.configurations[config_item.config_id] = config_item
                
                # Mettre à jour les index
                self.config_by_env[config_item.environment].append(config_item.config_id)
                self.config_by_type[config_item.config_type].append(config_item.config_id)
                for creator_type in config_item.creator_types:
                    self.config_by_creator[creator_type].append(config_item.config_id)
                
            except Exception as e:
                logger.warning(f"Failed to load configuration file {config_file}: {e}")
        
        logger.info(f"🔧 Loaded {len(self.configurations)} existing configurations")
    
    async def get_configuration_analytics(self) -> Dict[str, Any]:
        """Obtenir les analytics de configuration"""
        
        # Statistiques par environnement
        env_stats = {}
        for env in Environment:
            configs = self.config_by_env[env]
            env_stats[env.value] = {
                'total_configs': len(configs),
                'secret_configs': len([
                    c for c in configs 
                    if c in self.configurations and self.configurations[c].is_secret
                ]),
                'config_types': len(set(
                    self.configurations[c].config_type 
                    for c in configs if c in self.configurations
                ))
            }
        
        # Statistiques par creator type
        creator_stats = {}
        for creator_type in self.creator_defaults.keys():
            configs = self.config_by_creator[creator_type]
            creator_stats[creator_type] = {
                'total_configs': len(configs),
                'profiles': len([
                    p for p in self.profiles.values() 
                    if p.creator_type == creator_type
                ])
            }
        
        # Changements récents
        recent_changes = [
            c for c in self.change_history 
            if (datetime.now() - c.timestamp).days <= 7
        ]
        
        return {
            'summary': {
                'total_configurations': len(self.configurations),
                'total_profiles': len(self.profiles),
                'total_changes': len(self.change_history),
                'recent_changes': len(recent_changes)
            },
            'environment_breakdown': env_stats,
            'creator_breakdown': creator_stats,
            'security': {
                'encrypted_configs': len([
                    c for c in self.configurations.values() if c.is_encrypted
                ]),
                'secret_configs': len([
                    c for c in self.configurations.values() if c.is_secret
                ])
            }
        }

# Usage Example
async def main():
    """Exemple d'utilisation du Configuration Management System"""
    
    cms = ConfigurationManagementSystem(
        storage_path="config",
        enable_encryption=True,
        config_validation=True
    )
    
    # Créer des configurations
    model_config_id = await cms.create_configuration(
        name="musician_classification_model",
        config_type=ConfigType.MODEL,
        environment=Environment.PRODUCTION,
        value={
            "model_name": "audio_classifier_v2",
            "version": "2.1.0",
            "parameters": {
                "max_length": 300,
                "sample_rate": 44100
            }
        },
        description="Configuration for music classification model",
        creator_types=["musician"],
        created_by="ml_engineer"
    )
    
    # Créer un secret
    api_key_id = await cms.create_configuration(
        name="openai_api_key",
        config_type=ConfigType.SECURITY,
        environment=Environment.PRODUCTION,
        value="sk-1234567890abcdef",
        description="OpenAI API key for text processing",
        is_secret=True,
        created_by="security_admin"
    )
    
    # Créer un profil creator
    profile_id = await cms.create_creator_profile(
        creator_type="musician",
        environment=Environment.PRODUCTION
    )
    
    # Récupérer la configuration d'un creator
    musician_config = await cms.get_creator_configuration(
        creator_type="musician",
        environment=Environment.PRODUCTION
    )
    
    print(f"Musician configuration: {musician_config}")
    
    # Analytics
    analytics = await cms.get_configuration_analytics()
    print(f"Configuration analytics: {analytics['summary']}")

if __name__ == "__main__":
    asyncio.run(main())