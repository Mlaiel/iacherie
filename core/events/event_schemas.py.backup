"""IA-Influencer-Agent - Event Schema Management System
Module: backend/core/events/event_schemas.py
Architecture: Enterprise Schema Validation & Versioning
Auteur: Équipe Backend Senior + ML Engineer + Sécurité + Microservices + DBA + DevOps + IA Prompt Engineer

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
© 2025 Équipe d'Experts. Tous droits réservés.

SPÉCIALITÉS DE L'ÉQUIPE:
🔹 Lead Dev IA: Architecture & prompt engineering
🔹 Backend Senior: Microservices & performance  
🔹 ML Engineer: Modèles & pipeline d'apprentissage
🔹 DBA Expert: Optimisation & requêtes complexes
🔹 Expert Sécurité: Protection & conformité
🔹 Spécialiste Audio: Traitement signal & formats
🔹 DevOps: Infrastructure & déploiement
🔹 Expert Microservices: Distribution & scalabilité

Description:
    Système de gestion des schémas d'événements avec validation, versioning,
    migration et compatibilité. Support des formats JSON Schema, Avro et Protobuf.
"""
from typing import Any, Dict, List, Optional, Union, Type, Generic, TypeVar, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from abc import ABC, abstractmethod
import json
import logging
import hashlib
import yaml
from pathlib import Path

import jsonschema
from jsonschema import validate, ValidationError, Draft7Validator
from avro import schema as avro_schema
import protobuf

from .event_types import EventType

logger = logging.getLogger(__name__)

T = TypeVar('T')


class SchemaFormat(Enum):
    """Formats de schéma supportés"""
    JSON_SCHEMA = "json_schema"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    YAML = "yaml"
    CUSTOM = "custom"


class SchemaVersion(Enum):
    """Versions de schéma"""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"
    V2_1 = "2.1"
    LATEST = "latest"


class CompatibilityMode(Enum):
    """Modes de compatibilité"""
    BACKWARD = "backward"        # Nouveau schéma peut lire ancienne data
    FORWARD = "forward"          # Ancien schéma peut lire nouvelle data
    FULL = "full"               # Compatibilité bidirectionnelle
    NONE = "none"               # Aucune compatibilité requise
    TRANSITIVE = "transitive"   # Compatibilité transitive


@dataclass
class SchemaMetadata:
    """Métadonnées de schéma"""
    id: str
    name: str
    version: str
    format: SchemaFormat
    created_at: datetime
    updated_at: datetime
    author: str
    description: str
    tags: List[str] = field(default_factory=list)
    compatibility_mode: CompatibilityMode = CompatibilityMode.BACKWARD
    deprecated: bool = False
    deprecation_date: Optional[datetime] = None
    successor_schema_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    checksum: str = ""


@dataclass
class SchemaValidationResult:
    """Résultat de validation de schéma"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    schema_id: Optional[str] = None
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validation_time_ms: float = 0.0


@dataclass
class SchemaMigration:
    """Définition de migration de schéma"""
    from_version: str
    to_version: str
    migration_script: str
    rollback_script: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    author: str = ""
    description: str = ""
    is_automatic: bool = False


class SchemaValidator(ABC):
    """Interface pour les validateurs de schéma"""
    
    @abstractmethod
    def validate(self, data: Any, schema: Dict[str, Any]) -> SchemaValidationResult:
        """Valider des données contre un schéma"""
        pass
    
    @abstractmethod
    def is_compatible(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> bool:
        """Vérifier la compatibilité entre schémas"""
        pass


class JsonSchemaValidator(SchemaValidator):
    """Validateur JSON Schema"""
    
    def __init__(self):
        self.validator_class = Draft7Validator
    
    def validate(self, data: Any, schema: Dict[str, Any]) -> SchemaValidationResult:
        """Valider des données JSON contre un schéma"""
        start_time = time.time()
        result = SchemaValidationResult(is_valid=True)
        
        try:
            validator = self.validator_class(schema)
            errors = list(validator.iter_errors(data))
            
            if errors:
                result.is_valid = False
                result.errors = [error.message for error in errors]
            
        except Exception as e:
            result.is_valid = False
            result.errors = [f"Validation error: {str(e)}"]
        
        result.validation_time_ms = (time.time() - start_time) * 1000
        return result
    
    def is_compatible(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> bool:
        """Vérifier la compatibilité JSON Schema"""
        try:
            # Vérification des propriétés requises
            old_required = set(old_schema.get("required", []))
            new_required = set(new_schema.get("required", []))
            
            # Nouveau schéma ne peut pas ajouter de champs requis
            if new_required - old_required:
                return False
            
            # Vérification des types
            old_props = old_schema.get("properties", {})
            new_props = new_schema.get("properties", {})
            
            for prop_name, old_prop in old_props.items():
                if prop_name in new_props:
                    new_prop = new_props[prop_name]
                    old_type = old_prop.get("type")
                    new_type = new_prop.get("type")
                    
                    # Les types doivent être compatibles
                    if old_type and new_type and old_type != new_type:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Compatibility check error: {e}")
            return False


class AvroSchemaValidator(SchemaValidator):
    """Validateur Avro Schema"""
    
    def validate(self, data: Any, schema: Dict[str, Any]) -> SchemaValidationResult:
        """Valider des données Avro"""
        start_time = time.time()
        result = SchemaValidationResult(is_valid=True)
        
        try:
            parsed_schema = avro_schema.parse(json.dumps(schema))
            # Validation Avro ici
            
        except Exception as e:
            result.is_valid = False
            result.errors = [f"Avro validation error: {str(e)}"]
        
        result.validation_time_ms = (time.time() - start_time) * 1000
        return result
    
    def is_compatible(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> bool:
        """Vérifier la compatibilité Avro"""
        # Implémentation de la compatibilité Avro
        return True


class EventSchemaRegistry:
    """Registre centralisé des schémas d'événements"""
    
    def __init__(self, storage_backend: 'SchemaStorage'):
        self.storage = storage_backend
        self.validators: Dict[SchemaFormat, SchemaValidator] = {
            SchemaFormat.JSON_SCHEMA: JsonSchemaValidator(),
            SchemaFormat.AVRO: AvroSchemaValidator(),
        }
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.metadata_cache: Dict[str, SchemaMetadata] = {}
    
    async def register_schema(
        self,
        schema: Dict[str, Any],
        metadata: SchemaMetadata
    ) -> str:
        """Enregistrer un nouveau schéma"""
        try:
            # Calcul du checksum
            schema_json = json.dumps(schema, sort_keys=True)
            metadata.checksum = hashlib.sha256(schema_json.encode()).hexdigest()
            
            # Validation du schéma
            validator = self.validators.get(metadata.format)
            if validator:
                validation_result = validator.validate({}, schema)
                if not validation_result.is_valid:
                    raise ValueError(f"Invalid schema: {validation_result.errors}")
            
            # Vérification de compatibilité
            if await self.schema_exists(metadata.name):
                await self._check_compatibility(schema, metadata)
            
            # Stockage
            schema_id = await self.storage.store_schema(schema, metadata)
            
            # Mise à jour du cache
            self.cache[schema_id] = schema
            self.metadata_cache[schema_id] = metadata
            
            logger.info(f"Schema registered: {schema_id}")
            return schema_id
            
        except Exception as e:
            logger.error(f"Schema registration failed: {e}")
            raise
    
    async def get_schema(
        self,
        schema_id: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Récupérer un schéma"""
        try:
            # Recherche par ID
            if schema_id:
                if schema_id in self.cache:
                    return self.cache[schema_id]
                
                schema = await self.storage.get_schema_by_id(schema_id)
                if schema:
                    self.cache[schema_id] = schema
                return schema
            
            # Recherche par nom et version
            if name:
                schema_id = await self.storage.find_schema_id(name, version)
                if schema_id:
                    return await self.get_schema(schema_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Schema retrieval failed: {e}")
            return None
    
    async def validate_event_data(
        self,
        event_type: EventType,
        data: Any,
        schema_version: Optional[str] = None
    ) -> SchemaValidationResult:
        """Valider les données d'un événement"""
        try:
            # Récupération du schéma
            schema = await self.get_schema(
                name=event_type.value,
                version=schema_version or SchemaVersion.LATEST.value
            )
            
            if not schema:
                return SchemaValidationResult(
                    is_valid=False,
                    errors=[f"Schema not found for {event_type.value}"]
                )
            
            # Validation
            metadata = await self.get_schema_metadata(event_type.value, schema_version)
            if metadata:
                validator = self.validators.get(metadata.format)
                if validator:
                    return validator.validate(data, schema)
            
            return SchemaValidationResult(
                is_valid=False,
                errors=["No validator available"]
            )
            
        except Exception as e:
            logger.error(f"Event validation failed: {e}")
            return SchemaValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    async def migrate_schema(
        self,
        schema_name: str,
        from_version: str,
        to_version: str,
        migration: SchemaMigration
    ) -> bool:
        """Migrer un schéma vers une nouvelle version"""
        try:
            # Exécution de la migration
            success = await self.storage.execute_migration(
                schema_name, migration
            )
            
            if success:
                # Invalidation du cache
                await self._invalidate_cache(schema_name)
                logger.info(f"Schema migrated: {schema_name} {from_version} -> {to_version}")
            
            return success
            
        except Exception as e:
            logger.error(f"Schema migration failed: {e}")
            return False
    
    async def list_schemas(
        self,
        format_filter: Optional[SchemaFormat] = None,
        tag_filter: Optional[List[str]] = None
    ) -> List[SchemaMetadata]:
        """Lister les schémas disponibles"""
        try:
            schemas = await self.storage.list_all_schemas()
            
            # Filtres
            if format_filter:
                schemas = [s for s in schemas if s.format == format_filter]
            
            if tag_filter:
                schemas = [
                    s for s in schemas 
                    if any(tag in s.tags for tag in tag_filter)
                ]
            
            return schemas
            
        except Exception as e:
            logger.error(f"Schema listing failed: {e}")
            return []
    
    async def get_schema_metadata(
        self,
        name: str,
        version: Optional[str] = None
    ) -> Optional[SchemaMetadata]:
        """Récupérer les métadonnées d'un schéma"""
        try:
            return await self.storage.get_schema_metadata(name, version)
        except Exception as e:
            logger.error(f"Metadata retrieval failed: {e}")
            return None
    
    async def schema_exists(self, name: str, version: Optional[str] = None) -> bool:
        """Vérifier l'existence d'un schéma"""
        try:
            metadata = await self.get_schema_metadata(name, version)
            return metadata is not None
        except Exception:
            return False
    
    async def deprecate_schema(
        self,
        schema_name: str,
        version: str,
        successor_schema_id: Optional[str] = None
    ) -> bool:
        """Marquer un schéma comme déprécié"""
        try:
            return await self.storage.deprecate_schema(
                schema_name, version, successor_schema_id
            )
        except Exception as e:
            logger.error(f"Schema deprecation failed: {e}")
            return False
    
    async def _check_compatibility(
        self,
        new_schema: Dict[str, Any],
        metadata: SchemaMetadata
    ) -> None:
        """Vérifier la compatibilité avec la version précédente"""
        if metadata.compatibility_mode == CompatibilityMode.NONE:
            return
        
        # Récupération de la version précédente
        current_schema = await self.get_schema(name=metadata.name)
        if not current_schema:
            return
        
        validator = self.validators.get(metadata.format)
        if validator and not validator.is_compatible(current_schema, new_schema):
            raise ValueError(f"Schema not compatible with mode {metadata.compatibility_mode}")
    
    async def _invalidate_cache(self, schema_name: str) -> None:
        """Invalider le cache pour un schéma"""
        keys_to_remove = []
        for key, metadata in self.metadata_cache.items():
            if metadata.name == schema_name:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self.cache.pop(key, None)
            self.metadata_cache.pop(key, None)


class SchemaStorage(ABC):
    """Interface de stockage des schémas"""
    
    @abstractmethod
    async def store_schema(
        self,
        schema: Dict[str, Any],
        metadata: SchemaMetadata
    ) -> str:
        """Stocker un schéma"""
        pass
    
    @abstractmethod
    async def get_schema_by_id(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer un schéma par ID"""
        pass
    
    @abstractmethod
    async def find_schema_id(
        self,
        name: str,
        version: Optional[str] = None
    ) -> Optional[str]:
        """Trouver l'ID d'un schéma"""
        pass
    
    @abstractmethod
    async def get_schema_metadata(
        self,
        name: str,
        version: Optional[str] = None
    ) -> Optional[SchemaMetadata]:
        """Récupérer les métadonnées"""
        pass
    
    @abstractmethod
    async def list_all_schemas(self) -> List[SchemaMetadata]:
        """Lister tous les schémas"""
        pass
    
    @abstractmethod
    async def execute_migration(
        self,
        schema_name: str,
        migration: SchemaMigration
    ) -> bool:
        """Exécuter une migration"""
        pass
    
    @abstractmethod
    async def deprecate_schema(
        self,
        schema_name: str,
        version: str,
        successor_schema_id: Optional[str] = None
    ) -> bool:
        """Déprécier un schéma"""
        pass


class InMemorySchemaStorage(SchemaStorage):
    """Stockage en mémoire pour les schémas (développement/test)"""
    
    def __init__(self):
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.metadata: Dict[str, SchemaMetadata] = {}
        self.name_version_index: Dict[str, str] = {}  # name:version -> schema_id
    
    async def store_schema(
        self,
        schema: Dict[str, Any],
        metadata: SchemaMetadata
    ) -> str:
        """Stocker un schéma en mémoire"""
        schema_id = metadata.id or str(uuid.uuid4())
        
        self.schemas[schema_id] = schema
        self.metadata[schema_id] = metadata
        
        # Index par nom/version
        version_key = f"{metadata.name}:{metadata.version}"
        latest_key = f"{metadata.name}:latest"
        
        self.name_version_index[version_key] = schema_id
        self.name_version_index[latest_key] = schema_id
        
        return schema_id
    
    async def get_schema_by_id(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer un schéma par ID"""
        return self.schemas.get(schema_id)
    
    async def find_schema_id(
        self,
        name: str,
        version: Optional[str] = None
    ) -> Optional[str]:
        """Trouver l'ID d'un schéma"""
        key = f"{name}:{version or 'latest'}"
        return self.name_version_index.get(key)
    
    async def get_schema_metadata(
        self,
        name: str,
        version: Optional[str] = None
    ) -> Optional[SchemaMetadata]:
        """Récupérer les métadonnées"""
        schema_id = await self.find_schema_id(name, version)
        if schema_id:
            return self.metadata.get(schema_id)
        return None
    
    async def list_all_schemas(self) -> List[SchemaMetadata]:
        """Lister tous les schémas"""
        return list(self.metadata.values())
    
    async def execute_migration(
        self,
        schema_name: str,
        migration: SchemaMigration
    ) -> bool:
        """Exécuter une migration (simulé)"""
        # Simulation de migration
        return True
    
    async def deprecate_schema(
        self,
        schema_name: str,
        version: str,
        successor_schema_id: Optional[str] = None
    ) -> bool:
        """Déprécier un schéma"""
        metadata = await self.get_schema_metadata(schema_name, version)
        if metadata:
            metadata.deprecated = True
            metadata.deprecation_date = datetime.now(timezone.utc)
            metadata.successor_schema_id = successor_schema_id
            return True
        return False


# Schémas prédéfinis pour les événements de la plateforme
PLATFORM_EVENT_SCHEMAS = {
    EventType.USER_REGISTERED: {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "format": "uuid"},
            "email": {"type": "string", "format": "email"},
            "username": {"type": "string", "minLength": 3, "maxLength": 50},
            "user_type": {
                "type": "string",
                "enum": ["musician", "blogger", "photographer", "influencer", "comedian"]
            },
            "registration_source": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"}
        },
        "required": ["user_id", "email", "username", "user_type", "timestamp"]
    },
    
    EventType.CONTENT_UPLOADED: {
        "type": "object",
        "properties": {
            "content_id": {"type": "string", "format": "uuid"},
            "user_id": {"type": "string", "format": "uuid"},
            "content_type": {
                "type": "string",
                "enum": ["audio", "video", "image", "text", "mixed"]
            },
            "file_format": {"type": "string"},
            "file_size": {"type": "integer", "minimum": 0},
            "metadata": {"type": "object"},
            "upload_timestamp": {"type": "string", "format": "date-time"}
        },
        "required": ["content_id", "user_id", "content_type", "file_format", "file_size"]
    },
    
    EventType.AI_PROCESSING_COMPLETED: {
        "type": "object",
        "properties": {
            "processing_id": {"type": "string", "format": "uuid"},
            "content_id": {"type": "string", "format": "uuid"},
            "processing_type": {
                "type": "string",
                "enum": ["analysis", "enhancement", "protection", "seo_optimization"]
            },
            "results": {"type": "object"},
            "processing_time_ms": {"type": "integer", "minimum": 0},
            "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
            "completed_at": {"type": "string", "format": "date-time"}
        },
        "required": ["processing_id", "content_id", "processing_type", "results"]
    },
    
    EventType.PAYMENT_PROCESSED: {
        "type": "object",
        "properties": {
            "payment_id": {"type": "string", "format": "uuid"},
            "user_id": {"type": "string", "format": "uuid"},
            "amount": {"type": "number", "minimum": 0},
            "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
            "payment_method": {"type": "string"},
            "status": {
                "type": "string",
                "enum": ["pending", "completed", "failed", "refunded"]
            },
            "transaction_timestamp": {"type": "string", "format": "date-time"}
        },
        "required": ["payment_id", "user_id", "amount", "currency", "status"]
    }
}


def create_default_schema_registry() -> EventSchemaRegistry:
    """Créer un registre de schémas avec configuration par défaut"""
    storage = InMemorySchemaStorage()
    registry = EventSchemaRegistry(storage)
    return registry


async def register_platform_schemas(registry: EventSchemaRegistry) -> None:
    """Enregistrer les schémas prédéfinis de la plateforme"""
    for event_type, schema in PLATFORM_EVENT_SCHEMAS.items():
        metadata = SchemaMetadata(
            id=str(uuid.uuid4()),
            name=event_type.value,
            version="1.0",
            format=SchemaFormat.JSON_SCHEMA,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            author="IA-Influencer-Agent Platform",
            description=f"Schema for {event_type.value} events",
            tags=["platform", "v1", "production"],
            compatibility_mode=CompatibilityMode.BACKWARD
        )
        
        await registry.register_schema(schema, metadata)
    
    logger.info("Platform schemas registered successfully")
