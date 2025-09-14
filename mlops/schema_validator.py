"""
Schema Validator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🗃️ Schema Validator - Enterprise MLOps Platform
DBA Expertise: Validation schéma automatique avec évolution et compatibility checks

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
import hashlib
import re
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchemaChangeType(Enum):
    """Types de changements de schéma"""
    ADD_COLUMN = "add_column"
    DROP_COLUMN = "drop_column"
    MODIFY_COLUMN = "modify_column"
    ADD_TABLE = "add_table"
    DROP_TABLE = "drop_table"
    ADD_INDEX = "add_index"
    DROP_INDEX = "drop_index"
    ADD_CONSTRAINT = "add_constraint"
    DROP_CONSTRAINT = "drop_constraint"
    RENAME_COLUMN = "rename_column"
    RENAME_TABLE = "rename_table"

class CompatibilityLevel(Enum):
    """Niveaux de compatibilité"""
    FULLY_COMPATIBLE = "fully_compatible"      # Pas de breaking changes
    BACKWARD_COMPATIBLE = "backward_compatible" # Compatible avec anciennes versions
    BREAKING_CHANGE = "breaking_change"        # Changements incompatibles
    UNKNOWN = "unknown"                        # Compatibilité non déterminée

class CreatorDataType(Enum):
    """Types de données par créateur"""
    MUSICIAN_AUDIO_METADATA = "musician_audio_metadata"
    MUSICIAN_PERFORMANCE_DATA = "musician_performance_data"
    BLOGGER_CONTENT_DATA = "blogger_content_data"
    BLOGGER_SEO_METRICS = "blogger_seo_metrics"
    PHOTOGRAPHER_IMAGE_METADATA = "photographer_image_metadata"
    PHOTOGRAPHER_PORTFOLIO_DATA = "photographer_portfolio_data"
    INFLUENCER_ENGAGEMENT_DATA = "influencer_engagement_data"
    INFLUENCER_ANALYTICS_DATA = "influencer_analytics_data"
    COMEDIAN_PERFORMANCE_DATA = "comedian_performance_data"
    COMEDIAN_AUDIENCE_DATA = "comedian_audience_data"

@dataclass
class ColumnDefinition:
    """Définition d'une colonne"""
    name: str
    data_type: str
    nullable: bool = True
    default_value: Optional[Any] = None
    constraints: List[str] = field(default_factory=list)
    description: Optional[str] = None
    creator_specific: bool = False
    sensitive_data: bool = False

@dataclass
class TableSchema:
    """Schéma d'une table"""
    table_name: str
    columns: Dict[str, ColumnDefinition]
    primary_key: List[str] = field(default_factory=list)
    foreign_keys: Dict[str, str] = field(default_factory=dict)  # column -> referenced_table.column
    indexes: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    creator_type: Optional[CreatorDataType] = None
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    description: Optional[str] = None

@dataclass
class SchemaVersion:
    """Version d'un schéma"""
    version_id: str
    schemas: Dict[str, TableSchema]
    version_number: str
    created_at: datetime
    created_by: str
    description: str
    compatibility_with_previous: CompatibilityLevel = CompatibilityLevel.UNKNOWN
    migration_script: Optional[str] = None
    rollback_script: Optional[str] = None

@dataclass
class SchemaChange:
    """Changement de schéma"""
    change_id: str
    change_type: SchemaChangeType
    table_name: str
    column_name: Optional[str] = None
    old_definition: Optional[Any] = None
    new_definition: Optional[Any] = None
    compatibility_impact: CompatibilityLevel = CompatibilityLevel.UNKNOWN
    migration_required: bool = False
    rollback_possible: bool = True
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ValidationResult:
    """Résultat de validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    compatibility_level: CompatibilityLevel = CompatibilityLevel.UNKNOWN
    required_migrations: List[str] = field(default_factory=list)
    validation_time_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

class SchemaValidator:
    """
    Validateur de schéma enterprise avec évolution automatique
    
    Fonctionnalités:
    - Validation automatique des changements de schéma
    - Détection de compatibilité backward/forward
    - Génération automatique de scripts de migration
    - Validation spécialisée par type de créateur
    - Audit trail complet des changements
    - Detection d'impact sur les performances
    """
    
    def __init__(self,
                 db_path -> None: str = "/tmp/schema_validator.db",
                 max_versions_history -> None: int = 50) -> None:
        self.db_path = db_path
        self.max_versions_history = max_versions_history
        
        # Stockage des schémas et versions
        self.current_schemas: Dict[str, TableSchema] = {}
        self.schema_versions: Dict[str, SchemaVersion] = {}
        self.pending_changes: List[SchemaChange] = []
        
        # Cache de validation
        self.validation_cache: Dict[str, ValidationResult] = {}
        
        # Règles de validation par type de créateur
        self.creator_validation_rules = {
            CreatorDataType.MUSICIAN_AUDIO_METADATA: {
                "required_columns": ["file_path", "duration", "sample_rate", "format"],
                "recommended_indexes": ["file_path", "created_at"],
                "sensitive_columns": ["file_path", "metadata"],
                "performance_columns": ["duration", "sample_rate"]
            },
            CreatorDataType.BLOGGER_CONTENT_DATA: {
                "required_columns": ["title", "content", "author_id", "status"],
                "recommended_indexes": ["author_id", "status", "created_at"],
                "sensitive_columns": ["author_id", "personal_data"],
                "performance_columns": ["word_count", "read_time"]
            },
            CreatorDataType.PHOTOGRAPHER_IMAGE_METADATA: {
                "required_columns": ["image_path", "camera_model", "exposure", "iso"],
                "recommended_indexes": ["image_path", "camera_model", "created_at"],
                "sensitive_columns": ["location_data", "image_path"],
                "performance_columns": ["file_size", "resolution"]
            },
            CreatorDataType.INFLUENCER_ENGAGEMENT_DATA: {
                "required_columns": ["post_id", "platform", "engagement_type", "count"],
                "recommended_indexes": ["post_id", "platform", "created_at"],
                "sensitive_columns": ["user_data", "demographics"],
                "performance_columns": ["count", "engagement_rate"]
            },
            CreatorDataType.COMEDIAN_PERFORMANCE_DATA: {
                "required_columns": ["performance_id", "venue", "audience_size", "duration"],
                "recommended_indexes": ["venue", "performance_date"],
                "sensitive_columns": ["audience_demographics", "venue_details"],
                "performance_columns": ["audience_size", "duration", "satisfaction_score"]
            }
        }
        
        # Callbacks
        self.validation_callbacks: List[Callable] = []
        self.change_callbacks: List[Callable] = []
        
        self._setup_database()
        self._load_predefined_schemas()
        logger.info("🗃️ SchemaValidator initialized for enterprise data governance")
    
    def _setup_database(self) -> None:
        """Initialisation de la base de données"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des schémas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS table_schemas (
                        table_name TEXT PRIMARY KEY,
                        schema_definition TEXT NOT NULL,
                        creator_type TEXT,
                        version TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        description TEXT
                    )
                """)
                
                # Table des versions de schéma
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_versions (
                        version_id TEXT PRIMARY KEY,
                        version_number TEXT NOT NULL,
                        schemas_snapshot TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        created_by TEXT NOT NULL,
                        description TEXT NOT NULL,
                        compatibility_level TEXT NOT NULL,
                        migration_script TEXT,
                        rollback_script TEXT
                    )
                """)
                
                # Table des changements
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_changes (
                        change_id TEXT PRIMARY KEY,
                        change_type TEXT NOT NULL,
                        table_name TEXT NOT NULL,
                        column_name TEXT,
                        old_definition TEXT,
                        new_definition TEXT,
                        compatibility_impact TEXT NOT NULL,
                        migration_required BOOLEAN NOT NULL,
                        rollback_possible BOOLEAN NOT NULL,
                        description TEXT,
                        timestamp TEXT NOT NULL
                    )
                """)
                
                # Table des validations
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS validation_results (
                        validation_id TEXT PRIMARY KEY,
                        table_name TEXT NOT NULL,
                        is_valid BOOLEAN NOT NULL,
                        errors TEXT,
                        warnings TEXT,
                        compatibility_level TEXT NOT NULL,
                        validation_time_ms REAL NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Database setup error: {e}")
            raise
    
    def _load_predefined_schemas(self) -> None:
        """Chargement des schémas prédéfinis pour les créateurs"""
        try:
            # Schéma pour métadonnées audio des musiciens
            musician_audio_schema = TableSchema(
                table_name="musician_audio_metadata",
                columns={
                    "id": ColumnDefinition("id", "UUID", nullable=False),
                    "file_path": ColumnDefinition("file_path", "VARCHAR(500)", nullable=False, sensitive_data=True),
                    "title": ColumnDefinition("title", "VARCHAR(200)", nullable=False),
                    "artist_id": ColumnDefinition("artist_id", "UUID", nullable=False),
                    "duration": ColumnDefinition("duration", "INTEGER", nullable=False, description="Duration in seconds"),
                    "sample_rate": ColumnDefinition("sample_rate", "INTEGER", nullable=False),
                    "bit_rate": ColumnDefinition("bit_rate", "INTEGER", nullable=True),
                    "format": ColumnDefinition("format", "VARCHAR(10)", nullable=False),
                    "genre": ColumnDefinition("genre", "VARCHAR(50)", nullable=True),
                    "bpm": ColumnDefinition("bpm", "INTEGER", nullable=True),
                    "key_signature": ColumnDefinition("key_signature", "VARCHAR(10)", nullable=True),
                    "created_at": ColumnDefinition("created_at", "TIMESTAMP", nullable=False),
                    "updated_at": ColumnDefinition("updated_at", "TIMESTAMP", nullable=False)
                },
                primary_key=["id"],
                foreign_keys={"artist_id": "users.id"},
                indexes=["file_path", "artist_id", "created_at", "genre"],
                creator_type=CreatorDataType.MUSICIAN_AUDIO_METADATA,
                description="Métadonnées des fichiers audio pour musiciens"
            )
            
            # Schéma pour données de contenu des blogueurs
            blogger_content_schema = TableSchema(
                table_name="blogger_content_data",
                columns={
                    "id": ColumnDefinition("id", "UUID", nullable=False),
                    "title": ColumnDefinition("title", "VARCHAR(300)", nullable=False),
                    "content": ColumnDefinition("content", "TEXT", nullable=False),
                    "author_id": ColumnDefinition("author_id", "UUID", nullable=False),
                    "status": ColumnDefinition("status", "VARCHAR(20)", nullable=False, default_value="draft"),
                    "word_count": ColumnDefinition("word_count", "INTEGER", nullable=True),
                    "read_time": ColumnDefinition("read_time", "INTEGER", nullable=True, description="Estimated read time in minutes"),
                    "seo_score": ColumnDefinition("seo_score", "DECIMAL(5,2)", nullable=True),
                    "keywords": ColumnDefinition("keywords", "JSON", nullable=True),
                    "meta_description": ColumnDefinition("meta_description", "VARCHAR(160)", nullable=True),
                    "published_at": ColumnDefinition("published_at", "TIMESTAMP", nullable=True),
                    "created_at": ColumnDefinition("created_at", "TIMESTAMP", nullable=False),
                    "updated_at": ColumnDefinition("updated_at", "TIMESTAMP", nullable=False)
                },
                primary_key=["id"],
                foreign_keys={"author_id": "users.id"},
                indexes=["author_id", "status", "published_at", "created_at"],
                creator_type=CreatorDataType.BLOGGER_CONTENT_DATA,
                description="Données de contenu pour blogueurs"
            )
            
            # Schéma pour métadonnées d'images des photographes
            photographer_schema = TableSchema(
                table_name="photographer_image_metadata",
                columns={
                    "id": ColumnDefinition("id", "UUID", nullable=False),
                    "image_path": ColumnDefinition("image_path", "VARCHAR(500)", nullable=False, sensitive_data=True),
                    "photographer_id": ColumnDefinition("photographer_id", "UUID", nullable=False),
                    "title": ColumnDefinition("title", "VARCHAR(200)", nullable=True),
                    "camera_model": ColumnDefinition("camera_model", "VARCHAR(100)", nullable=True),
                    "lens": ColumnDefinition("lens", "VARCHAR(100)", nullable=True),
                    "exposure": ColumnDefinition("exposure", "VARCHAR(20)", nullable=True),
                    "aperture": ColumnDefinition("aperture", "VARCHAR(10)", nullable=True),
                    "iso": ColumnDefinition("iso", "INTEGER", nullable=True),
                    "focal_length": ColumnDefinition("focal_length", "INTEGER", nullable=True),
                    "resolution": ColumnDefinition("resolution", "VARCHAR(20)", nullable=True),
                    "file_size": ColumnDefinition("file_size", "BIGINT", nullable=True, description="File size in bytes"),
                    "location_data": ColumnDefinition("location_data", "JSON", nullable=True, sensitive_data=True),
                    "tags": ColumnDefinition("tags", "JSON", nullable=True),
                    "created_at": ColumnDefinition("created_at", "TIMESTAMP", nullable=False),
                    "updated_at": ColumnDefinition("updated_at", "TIMESTAMP", nullable=False)
                },
                primary_key=["id"],
                foreign_keys={"photographer_id": "users.id"},
                indexes=["image_path", "photographer_id", "camera_model", "created_at"],
                creator_type=CreatorDataType.PHOTOGRAPHER_IMAGE_METADATA,
                description="Métadonnées d'images pour photographes"
            )
            
            # Schéma pour données d'engagement des influenceurs
            influencer_schema = TableSchema(
                table_name="influencer_engagement_data",
                columns={
                    "id": ColumnDefinition("id", "UUID", nullable=False),
                    "post_id": ColumnDefinition("post_id", "VARCHAR(100)", nullable=False),
                    "influencer_id": ColumnDefinition("influencer_id", "UUID", nullable=False),
                    "platform": ColumnDefinition("platform", "VARCHAR(50)", nullable=False),
                    "engagement_type": ColumnDefinition("engagement_type", "VARCHAR(20)", nullable=False),
                    "count": ColumnDefinition("count", "INTEGER", nullable=False),
                    "engagement_rate": ColumnDefinition("engagement_rate", "DECIMAL(5,4)", nullable=True),
                    "reach": ColumnDefinition("reach", "INTEGER", nullable=True),
                    "impressions": ColumnDefinition("impressions", "INTEGER", nullable=True),
                    "demographics": ColumnDefinition("demographics", "JSON", nullable=True, sensitive_data=True),
                    "content_type": ColumnDefinition("content_type", "VARCHAR(30)", nullable=True),
                    "hashtags": ColumnDefinition("hashtags", "JSON", nullable=True),
                    "timestamp": ColumnDefinition("timestamp", "TIMESTAMP", nullable=False),
                    "created_at": ColumnDefinition("created_at", "TIMESTAMP", nullable=False)
                },
                primary_key=["id"],
                foreign_keys={"influencer_id": "users.id"},
                indexes=["post_id", "influencer_id", "platform", "timestamp"],
                creator_type=CreatorDataType.INFLUENCER_ENGAGEMENT_DATA,
                description="Données d'engagement pour influenceurs"
            )
            
            # Schéma pour données de performance des comédiens
            comedian_schema = TableSchema(
                table_name="comedian_performance_data",
                columns={
                    "id": ColumnDefinition("id", "UUID", nullable=False),
                    "performance_id": ColumnDefinition("performance_id", "VARCHAR(100)", nullable=False),
                    "comedian_id": ColumnDefinition("comedian_id", "UUID", nullable=False),
                    "venue": ColumnDefinition("venue", "VARCHAR(200)", nullable=False),
                    "venue_type": ColumnDefinition("venue_type", "VARCHAR(50)", nullable=True),
                    "audience_size": ColumnDefinition("audience_size", "INTEGER", nullable=False),
                    "duration": ColumnDefinition("duration", "INTEGER", nullable=False, description="Performance duration in minutes"),
                    "material_type": ColumnDefinition("material_type", "VARCHAR(30)", nullable=True),
                    "satisfaction_score": ColumnDefinition("satisfaction_score", "DECIMAL(3,2)", nullable=True),
                    "laugh_frequency": ColumnDefinition("laugh_frequency", "DECIMAL(5,2)", nullable=True),
                    "audience_demographics": ColumnDefinition("audience_demographics", "JSON", nullable=True, sensitive_data=True),
                    "performance_notes": ColumnDefinition("performance_notes", "TEXT", nullable=True),
                    "performance_date": ColumnDefinition("performance_date", "DATE", nullable=False),
                    "created_at": ColumnDefinition("created_at", "TIMESTAMP", nullable=False)
                },
                primary_key=["id"],
                foreign_keys={"comedian_id": "users.id"},
                indexes=["performance_id", "comedian_id", "venue", "performance_date"],
                creator_type=CreatorDataType.COMEDIAN_PERFORMANCE_DATA,
                description="Données de performance pour comédiens"
            )
            
            # Enregistrement des schémas
            schemas = [
                musician_audio_schema,
                blogger_content_schema,
                photographer_schema,
                influencer_schema,
                comedian_schema
            ]
            
            for schema in schemas:
                self.current_schemas[schema.table_name] = schema
                asyncio.create_task(self._save_schema_to_db(schema))
            
            logger.info(f"📋 Loaded {len(schemas)} predefined creator schemas")
            
        except Exception as e:
            logger.error(f"❌ Error loading predefined schemas: {e}")
    
    async def validate_schema(self, table_schema: TableSchema) -> ValidationResult:
        """Validation complète d'un schéma"""
        start_time = datetime.now()
        
        try:
            # Génération de la clé de cache
            cache_key = self._generate_schema_cache_key(table_schema)
            
            # Vérification du cache
            if cache_key in self.validation_cache:
                cached_result = self.validation_cache[cache_key]
                logger.debug(f"📦 Using cached validation for {table_schema.table_name}")
                return cached_result
            
            result = ValidationResult(is_valid=True)
            
            # Validation de base
            await self._validate_basic_structure(table_schema, result)
            
            # Validation spécifique au créateur
            if table_schema.creator_type:
                await self._validate_creator_specific(table_schema, result)
            
            # Validation des contraintes
            await self._validate_constraints(table_schema, result)
            
            # Validation des performances
            await self._validate_performance_implications(table_schema, result)
            
            # Validation de sécurité
            await self._validate_security_requirements(table_schema, result)
            
            # Validation de compatibilité
            if table_schema.table_name in self.current_schemas:
                await self._validate_compatibility(table_schema, result)
            
            # Calcul du temps de validation
            validation_time = (datetime.now() - start_time).total_seconds() * 1000
            result.validation_time_ms = validation_time
            
            # Détermination du statut final
            result.is_valid = len(result.errors) == 0
            
            # Mise en cache
            self.validation_cache[cache_key] = result
            
            # Sauvegarde du résultat
            await self._save_validation_result(table_schema, result)
            
            # Callbacks
            for callback in self.validation_callbacks:
                try:
                    await callback(table_schema, result)
                except Exception as e:
                    logger.error(f"❌ Validation callback error: {e}")
            
            logger.info(f"✅ Schema validation completed for {table_schema.table_name}: {'VALID' if result.is_valid else 'INVALID'}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Schema validation error for {table_schema.table_name}: {e}")
            result = ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                validation_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
            return result
    
    async def _validate_basic_structure(self, schema -> None: TableSchema, result -> None: ValidationResult) -> None:
        """Validation de la structure de base"""
        try:
            # Vérification du nom de table
            if not schema.table_name or not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', schema.table_name):
                result.errors.append("Invalid table name format")
            
            # Vérification des colonnes
            if not schema.columns:
                result.errors.append("Table must have at least one column")
                return
            
            # Vérification de la clé primaire
            if not schema.primary_key:
                result.warnings.append("Table has no primary key defined")
            else:
                for pk_col in schema.primary_key:
                    if pk_col not in schema.columns:
                        result.errors.append(f"Primary key column '{pk_col}' not found in table")
            
            # Validation des colonnes
            for col_name, col_def in schema.columns.items():
                await self._validate_column_definition(col_name, col_def, result)
            
            # Vérification des clés étrangères
            for fk_col, referenced in schema.foreign_keys.items():
                if fk_col not in schema.columns:
                    result.errors.append(f"Foreign key column '{fk_col}' not found in table")
                
                if '.' not in referenced:
                    result.errors.append(f"Invalid foreign key reference format: '{referenced}'")
            
        except Exception as e:
            result.errors.append(f"Basic structure validation error: {str(e)}")
    
    async def _validate_column_definition(self, col_name -> None: str, col_def -> None: ColumnDefinition, result -> None: ValidationResult) -> None:
        """Validation d'une définition de colonne"""
        try:
            # Vérification du nom de colonne
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', col_name):
                result.errors.append(f"Invalid column name format: '{col_name}'")
            
            # Vérification du type de données
            valid_types = [
                'INTEGER', 'BIGINT', 'DECIMAL', 'FLOAT', 'DOUBLE',
                'VARCHAR', 'TEXT', 'CHAR', 'BOOLEAN', 'DATE', 
                'TIMESTAMP', 'TIME', 'UUID', 'JSON', 'BLOB'
            ]
            
            base_type = col_def.data_type.split('(')[0].upper()
            if base_type not in valid_types:
                result.warnings.append(f"Non-standard data type: '{col_def.data_type}' for column '{col_name}'")
            
            # Vérification des contraintes
            if col_def.constraints:
                for constraint in col_def.constraints:
                    if not self._is_valid_constraint(constraint):
                        result.warnings.append(f"Potentially invalid constraint '{constraint}' on column '{col_name}'")
            
            # Vérification des données sensibles
            if col_def.sensitive_data and not any(c.upper() in col_def.constraints for c in ['ENCRYPTED', 'HASHED']):
                result.warnings.append(f"Sensitive column '{col_name}' should have encryption/hashing constraints")
            
        except Exception as e:
            result.errors.append(f"Column validation error for '{col_name}': {str(e)}")
    
    def _is_valid_constraint(self, constraint: str) -> bool:
        """Vérification si une contrainte est valide"""
        valid_constraints = [
            'NOT NULL', 'UNIQUE', 'CHECK', 'DEFAULT', 'AUTO_INCREMENT',
            'ENCRYPTED', 'HASHED', 'INDEXED'
        ]
        
        constraint_upper = constraint.upper()
        return any(vc in constraint_upper for vc in valid_constraints)
    
    async def _validate_creator_specific(self, schema -> None: TableSchema, result -> None: ValidationResult) -> None:
        """Validation spécifique au type de créateur"""
        try:
            if not schema.creator_type or schema.creator_type not in self.creator_validation_rules:
                return
            
            rules = self.creator_validation_rules[schema.creator_type]
            
            # Vérification des colonnes requises
            required_columns = rules.get("required_columns", [])
            for req_col in required_columns:
                if req_col not in schema.columns:
                    result.errors.append(f"Missing required column '{req_col}' for {schema.creator_type.value}")
            
            # Vérification des index recommandés
            recommended_indexes = rules.get("recommended_indexes", [])
            for rec_idx in recommended_indexes:
                if rec_idx not in schema.indexes:
                    result.warnings.append(f"Recommended index missing: '{rec_idx}' for {schema.creator_type.value}")
            
            # Vérification des colonnes sensibles
            sensitive_columns = rules.get("sensitive_columns", [])
            for sens_col in sensitive_columns:
                if sens_col in schema.columns:
                    col_def = schema.columns[sens_col]
                    if not col_def.sensitive_data:
                        result.warnings.append(f"Column '{sens_col}' should be marked as sensitive")
            
            # Vérification des colonnes de performance
            performance_columns = rules.get("performance_columns", [])
            for perf_col in performance_columns:
                if perf_col in schema.columns:
                    if perf_col not in schema.indexes:
                        result.warnings.append(f"Performance column '{perf_col}' should be indexed")
            
        except Exception as e:
            result.errors.append(f"Creator-specific validation error: {str(e)}")
    
    async def _validate_constraints(self, schema -> None: TableSchema, result -> None: ValidationResult) -> None:
        """Validation des contraintes"""
        try:
            # Vérification des contraintes de table
            for constraint in schema.constraints:
                if not self._is_valid_table_constraint(constraint):
                    result.warnings.append(f"Potentially invalid table constraint: '{constraint}'")
            
            # Vérification de la cohérence des clés étrangères
            for fk_col, referenced in schema.foreign_keys.items():
                col_def = schema.columns.get(fk_col)
                if col_def and col_def.nullable:
                    result.warnings.append(f"Foreign key column '{fk_col}' is nullable - consider NOT NULL constraint")
            
            # Vérification des colonnes timestamp
            timestamp_columns = ['created_at', 'updated_at']
            for ts_col in timestamp_columns:
                if ts_col in schema.columns:
                    col_def = schema.columns[ts_col]
                    if col_def.nullable:
                        result.warnings.append(f"Timestamp column '{ts_col}' should not be nullable")
                    if col_def.default_value is None and ts_col == 'created_at':
                        result.warnings.append(f"Column '{ts_col}' should have a default value")
            
        except Exception as e:
            result.errors.append(f"Constraints validation error: {str(e)}")
    
    def _is_valid_table_constraint(self, constraint: str) -> bool:
        """Vérification si une contrainte de table est valide"""
        valid_table_constraints = [
            'PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK'
        ]
        
        constraint_upper = constraint.upper()
        return any(vtc in constraint_upper for vtc in valid_table_constraints)
    
    async def _validate_performance_implications(self, schema -> None: TableSchema, result -> None: ValidationResult) -> None:
        """Validation des implications de performance"""
        try:
            # Vérification du nombre d'index
            if len(schema.indexes) == 0:
                result.warnings.append("No indexes defined - may impact query performance")
            elif len(schema.indexes) > 10:
                result.warnings.append("Many indexes defined - may impact write performance")
            
            # Vérification des types de données pour les grandes tables
            large_data_types = ['TEXT', 'BLOB', 'JSON']
            for col_name, col_def in schema.columns.items():
                if any(ldt in col_def.data_type.upper() for ldt in large_data_types):
                    if col_name in schema.indexes:
                        result.warnings.append(f"Indexing large data type column '{col_name}' may impact performance")
            
            # Vérification des clés primaires composites
            if len(schema.primary_key) > 3:
                result.warnings.append("Composite primary key with many columns may impact performance")
            
            # Estimation de la taille de ligne
            estimated_row_size = self._estimate_row_size(schema)
            if estimated_row_size > 8000:  # 8KB typical page size
                result.warnings.append(f"Large estimated row size ({estimated_row_size} bytes) may cause page splits")
            
        except Exception as e:
            result.errors.append(f"Performance validation error: {str(e)}")
    
    def _estimate_row_size(self, schema: TableSchema) -> int:
        """Estimation de la taille d'une ligne"""
        size_estimates = {
            'INTEGER': 4, 'BIGINT': 8, 'DECIMAL': 8, 'FLOAT': 4, 'DOUBLE': 8,
            'BOOLEAN': 1, 'DATE': 3, 'TIMESTAMP': 8, 'TIME': 3, 'UUID': 16
        }
        
        total_size = 0
        
        for col_name, col_def in schema.columns.items():
            data_type = col_def.data_type.upper()
            
            if data_type in size_estimates:
                total_size += size_estimates[data_type]
            elif data_type.startswith('VARCHAR'):
                # Extract length from VARCHAR(n)
                match = re.search(r'VARCHAR\((\d+)\)', data_type)
                if match:
                    total_size += int(match.group(1))
                else:
                    total_size += 255  # Default VARCHAR size
            elif data_type.startswith('CHAR'):
                # Extract length from CHAR(n)
                match = re.search(r'CHAR\((\d+)\)', data_type)
                if match:
                    total_size += int(match.group(1))
                else:
                    total_size += 1
            elif data_type in ['TEXT', 'BLOB', 'JSON']:
                total_size += 1000  # Estimate for variable length
            else:
                total_size += 100  # Default estimate
        
        return total_size
    
    async def _validate_security_requirements(self, schema -> None: TableSchema, result -> None: ValidationResult) -> None:
        """Validation des exigences de sécurité"""
        try:
            # Vérification des colonnes sensibles
            sensitive_columns = [col_name for col_name, col_def in schema.columns.items() if col_def.sensitive_data]
            
            if sensitive_columns:
                result.details["sensitive_columns"] = sensitive_columns
                
                # Vérification des mesures de protection
                for sens_col in sensitive_columns:
                    col_def = schema.columns[sens_col]
                    if not any(keyword in ' '.join(col_def.constraints).upper() 
                             for keyword in ['ENCRYPTED', 'HASHED', 'MASKED']):
                        result.warnings.append(f"Sensitive column '{sens_col}' lacks protection constraints")
            
            # Vérification des colonnes d'audit
            audit_columns = ['created_at', 'updated_at', 'created_by', 'updated_by']
            missing_audit = [col for col in audit_columns if col not in schema.columns]
            
            if missing_audit:
                result.warnings.append(f"Missing audit columns: {', '.join(missing_audit)}")
            
            # Vérification des colonnes de versioning pour la conformité
            if schema.creator_type and 'version' not in schema.columns:
                result.warnings.append("Consider adding version column for data versioning and compliance")
            
        except Exception as e:
            result.errors.append(f"Security validation error: {str(e)}")
    
    async def _validate_compatibility(self, schema -> None: TableSchema, result -> None: ValidationResult) -> None:
        """Validation de la compatibilité avec le schéma existant"""
        try:
            existing_schema = self.current_schemas[schema.table_name]
            changes = await self._detect_schema_changes(existing_schema, schema)
            
            if not changes:
                result.compatibility_level = CompatibilityLevel.FULLY_COMPATIBLE
                return
            
            # Analyse de l'impact des changements
            breaking_changes = []
            compatible_changes = []
            
            for change in changes:
                if self._is_breaking_change(change):
                    breaking_changes.append(change)
                else:
                    compatible_changes.append(change)
            
            if breaking_changes:
                result.compatibility_level = CompatibilityLevel.BREAKING_CHANGE
                result.errors.extend([f"Breaking change: {change.description}" for change in breaking_changes])
            elif compatible_changes:
                result.compatibility_level = CompatibilityLevel.BACKWARD_COMPATIBLE
                result.warnings.extend([f"Compatible change: {change.description}" for change in compatible_changes])
            else:
                result.compatibility_level = CompatibilityLevel.FULLY_COMPATIBLE
            
            # Génération des scripts de migration si nécessaire
            if changes:
                migration_script = await self._generate_migration_script(changes)
                result.required_migrations.append(migration_script)
            
            result.details["schema_changes"] = [
                {
                    "change_type": change.change_type.value,
                    "table_name": change.table_name,
                    "column_name": change.column_name,
                    "description": change.description,
                    "breaking": self._is_breaking_change(change)
                }
                for change in changes
            ]
            
        except Exception as e:
            result.errors.append(f"Compatibility validation error: {str(e)}")
            result.compatibility_level = CompatibilityLevel.UNKNOWN
    
    async def _detect_schema_changes(self, old_schema: TableSchema, new_schema: TableSchema) -> List[SchemaChange]:
        """Détection des changements entre deux schémas"""
        changes = []
        
        try:
            # Changements de colonnes
            old_columns = set(old_schema.columns.keys())
            new_columns = set(new_schema.columns.keys())
            
            # Colonnes ajoutées
            for added_col in new_columns - old_columns:
                change = SchemaChange(
                    change_id=f"add_col_{new_schema.table_name}_{added_col}",
                    change_type=SchemaChangeType.ADD_COLUMN,
                    table_name=new_schema.table_name,
                    column_name=added_col,
                    new_definition=new_schema.columns[added_col],
                    description=f"Added column '{added_col}'"
                )
                changes.append(change)
            
            # Colonnes supprimées
            for dropped_col in old_columns - new_columns:
                change = SchemaChange(
                    change_id=f"drop_col_{new_schema.table_name}_{dropped_col}",
                    change_type=SchemaChangeType.DROP_COLUMN,
                    table_name=new_schema.table_name,
                    column_name=dropped_col,
                    old_definition=old_schema.columns[dropped_col],
                    description=f"Dropped column '{dropped_col}'"
                )
                changes.append(change)
            
            # Colonnes modifiées
            for common_col in old_columns & new_columns:
                old_col_def = old_schema.columns[common_col]
                new_col_def = new_schema.columns[common_col]
                
                if old_col_def.data_type != new_col_def.data_type or old_col_def.nullable != new_col_def.nullable:
                    change = SchemaChange(
                        change_id=f"mod_col_{new_schema.table_name}_{common_col}",
                        change_type=SchemaChangeType.MODIFY_COLUMN,
                        table_name=new_schema.table_name,
                        column_name=common_col,
                        old_definition=old_col_def,
                        new_definition=new_col_def,
                        description=f"Modified column '{common_col}'"
                    )
                    changes.append(change)
            
            # Changements d'index
            old_indexes = set(old_schema.indexes)
            new_indexes = set(new_schema.indexes)
            
            for added_idx in new_indexes - old_indexes:
                change = SchemaChange(
                    change_id=f"add_idx_{new_schema.table_name}_{added_idx}",
                    change_type=SchemaChangeType.ADD_INDEX,
                    table_name=new_schema.table_name,
                    column_name=added_idx,
                    description=f"Added index on '{added_idx}'"
                )
                changes.append(change)
            
            for dropped_idx in old_indexes - new_indexes:
                change = SchemaChange(
                    change_id=f"drop_idx_{new_schema.table_name}_{dropped_idx}",
                    change_type=SchemaChangeType.DROP_INDEX,
                    table_name=new_schema.table_name,
                    column_name=dropped_idx,
                    description=f"Dropped index on '{dropped_idx}'"
                )
                changes.append(change)
            
        except Exception as e:
            logger.error(f"❌ Error detecting schema changes: {e}")
        
        return changes
    
    def _is_breaking_change(self, change: SchemaChange) -> bool:
        """Détermine si un changement est breaking"""
        breaking_change_types = [
            SchemaChangeType.DROP_COLUMN,
            SchemaChangeType.DROP_TABLE,
            SchemaChangeType.DROP_CONSTRAINT
        ]
        
        if change.change_type in breaking_change_types:
            return True
        
        # Modification de colonne qui change le type de manière incompatible
        if change.change_type == SchemaChangeType.MODIFY_COLUMN:
            if hasattr(change.old_definition, 'data_type') and hasattr(change.new_definition, 'data_type'):
                old_type = change.old_definition.data_type.upper()
                new_type = change.new_definition.data_type.upper()
                
                # Changements de type incompatibles
                incompatible_changes = [
                    ('VARCHAR', 'INTEGER'),
                    ('TEXT', 'INTEGER'),
                    ('INTEGER', 'VARCHAR'),
                    ('BIGINT', 'INTEGER')  # Peut causer des overflows
                ]
                
                for old, new in incompatible_changes:
                    if old in old_type and new in new_type:
                        return True
            
            # Changement de nullable vers non-nullable
            if (hasattr(change.old_definition, 'nullable') and 
                hasattr(change.new_definition, 'nullable')):
                if change.old_definition.nullable and not change.new_definition.nullable:
                    return True
        
        return False
    
    async def _generate_migration_script(self, changes: List[SchemaChange]) -> str:
        """Génération d'un script de migration"""
        try:
            script_lines = ["-- Auto-generated migration script", "BEGIN TRANSACTION;"]
            
            for change in changes:
                if change.change_type == SchemaChangeType.ADD_COLUMN:
                    col_def = change.new_definition
                    nullable = "NULL" if col_def.nullable else "NOT NULL"
                    default = f" DEFAULT {col_def.default_value}" if col_def.default_value else ""
                    
                    script_lines.append(
                        f"ALTER TABLE {change.table_name} ADD COLUMN {change.column_name} "
                        f"{col_def.data_type} {nullable}{default};"
                    )
                
                elif change.change_type == SchemaChangeType.DROP_COLUMN:
                    script_lines.append(
                        f"ALTER TABLE {change.table_name} DROP COLUMN {change.column_name};"
                    )
                
                elif change.change_type == SchemaChangeType.MODIFY_COLUMN:
                    col_def = change.new_definition
                    nullable = "NULL" if col_def.nullable else "NOT NULL"
                    
                    script_lines.append(
                        f"ALTER TABLE {change.table_name} ALTER COLUMN {change.column_name} "
                        f"TYPE {col_def.data_type} {nullable};"
                    )
                
                elif change.change_type == SchemaChangeType.ADD_INDEX:
                    script_lines.append(
                        f"CREATE INDEX idx_{change.table_name}_{change.column_name} "
                        f"ON {change.table_name} ({change.column_name});"
                    )
                
                elif change.change_type == SchemaChangeType.DROP_INDEX:
                    script_lines.append(
                        f"DROP INDEX IF EXISTS idx_{change.table_name}_{change.column_name};"
                    )
            
            script_lines.append("COMMIT;")
            return "\n".join(script_lines)
            
        except Exception as e:
            logger.error(f"❌ Error generating migration script: {e}")
            return f"-- Error generating migration script: {str(e)}"
    
    def _generate_schema_cache_key(self, schema: TableSchema) -> str:
        """Génération d'une clé de cache pour un schéma"""
        try:
            schema_str = f"{schema.table_name}_{schema.version}_{len(schema.columns)}"
            for col_name, col_def in schema.columns.items():
                schema_str += f"_{col_name}_{col_def.data_type}_{col_def.nullable}"
            
            return hashlib.md5(schema_str.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"❌ Error generating cache key: {e}")
            return f"error_{schema.table_name}_{datetime.now().timestamp()}"
    
    async def _save_schema_to_db(self, schema -> None: TableSchema) -> None:
        """Sauvegarde d'un schéma en base"""
        try:
            schema_json = {
                "columns": {
                    name: {
                        "name": col.name,
                        "data_type": col.data_type,
                        "nullable": col.nullable,
                        "default_value": col.default_value,
                        "constraints": col.constraints,
                        "description": col.description,
                        "creator_specific": col.creator_specific,
                        "sensitive_data": col.sensitive_data
                    }
                    for name, col in schema.columns.items()
                },
                "primary_key": schema.primary_key,
                "foreign_keys": schema.foreign_keys,
                "indexes": schema.indexes,
                "constraints": schema.constraints
            }
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO table_schemas 
                    (table_name, schema_definition, creator_type, version, created_at, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    schema.table_name,
                    json.dumps(schema_json),
                    schema.creator_type.value if schema.creator_type else None,
                    schema.version,
                    schema.created_at.isoformat(),
                    schema.description
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error saving schema to DB: {e}")
    
    async def _save_validation_result(self, schema -> None: TableSchema, result -> None: ValidationResult) -> None:
        """Sauvegarde d'un résultat de validation"""
        try:
            validation_id = f"val_{schema.table_name}_{int(datetime.now().timestamp())}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO validation_results 
                    (validation_id, table_name, is_valid, errors, warnings, 
                     compatibility_level, validation_time_ms, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    validation_id,
                    schema.table_name,
                    result.is_valid,
                    json.dumps(result.errors),
                    json.dumps(result.warnings),
                    result.compatibility_level.value,
                    result.validation_time_ms,
                    datetime.now().isoformat()
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error saving validation result: {e}")
    
    async def get_schema_validation_report(self, table_name: str) -> Dict[str, Any]:
        """Génération d'un rapport de validation pour un schéma"""
        try:
            if table_name not in self.current_schemas:
                return {"error": "Schema not found"}
            
            schema = self.current_schemas[table_name]
            validation_result = await self.validate_schema(schema)
            
            report = {
                "table_name": table_name,
                "schema_version": schema.version,
                "creator_type": schema.creator_type.value if schema.creator_type else None,
                "validation_status": "VALID" if validation_result.is_valid else "INVALID",
                "validation_time_ms": validation_result.validation_time_ms,
                "compatibility_level": validation_result.compatibility_level.value,
                "column_count": len(schema.columns),
                "index_count": len(schema.indexes),
                "constraint_count": len(schema.constraints),
                "sensitive_columns": [
                    name for name, col in schema.columns.items() if col.sensitive_data
                ],
                "errors": validation_result.errors,
                "warnings": validation_result.warnings,
                "required_migrations": validation_result.required_migrations,
                "details": validation_result.details,
                "timestamp": datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating validation report: {e}")
            return {"error": str(e)}
    
    def add_validation_callback(self, callback -> None: Callable) -> None:
        """Ajouter un callback de validation"""
        self.validation_callbacks.append(callback)
        logger.info(f"📋 Validation callback added. Total: {len(self.validation_callbacks)}")
    
    def add_change_callback(self, callback -> None: Callable) -> None:
        """Ajouter un callback de changement"""
        self.change_callbacks.append(callback)
        logger.info(f"🔄 Change callback added. Total: {len(self.change_callbacks)}")


# Exemple d'utilisation pour démonstration
async def main() -> None:
    """Démonstration des capacités du SchemaValidator"""
    
    validator = SchemaValidator()
    
    # Callbacks de démonstration
    async def validation_callback(schema -> None: TableSchema, result -> None: ValidationResult) -> None:
        status = "✅ VALID" if result.is_valid else "❌ INVALID"
        print(f"📋 VALIDATION: {schema.table_name} - {status}")
        if result.errors:
            print(f"   Errors: {len(result.errors)}")
        if result.warnings:
            print(f"   Warnings: {len(result.warnings)}")
    
    validator.add_validation_callback(validation_callback)
    
    # Test des schémas prédéfinis
    print(f"🔍 Validating predefined schemas...")
    
    for table_name, schema in validator.current_schemas.items():
        print(f"\n📊 Validating {table_name}...")
        result = await validator.validate_schema(schema)
        
        # Génération du rapport
        report = await validator.get_schema_validation_report(table_name)
        print(f"   Status: {report['validation_status']}")
        print(f"   Creator type: {report['creator_type']}")
        print(f"   Columns: {report['column_count']}")
        print(f"   Indexes: {report['index_count']}")
        print(f"   Sensitive columns: {len(report['sensitive_columns'])}")
        
        if report['errors']:
            print(f"   ❌ Errors: {report['errors']}")
        if report['warnings']:
            print(f"   ⚠️ Warnings: {report['warnings'][:2]}...")  # First 2 warnings
    
    # Test d'un schéma modifié (simulation d'évolution)
    print(f"\n🔄 Testing schema evolution...")
    
    # Modification du schéma des musiciens
    original_musician_schema = validator.current_schemas['musician_audio_metadata']
    modified_musician_schema = TableSchema(
        table_name="musician_audio_metadata",
        columns={
            **original_musician_schema.columns,
            # Ajout d'une nouvelle colonne
            "album_id": ColumnDefinition("album_id", "UUID", nullable=True),
            # Modification d'une colonne existante
            "duration": ColumnDefinition("duration", "BIGINT", nullable=False, description="Duration in milliseconds")
        },
        primary_key=original_musician_schema.primary_key,
        foreign_keys={
            **original_musician_schema.foreign_keys,
            "album_id": "albums.id"
        },
        indexes=original_musician_schema.indexes + ["album_id"],
        creator_type=original_musician_schema.creator_type,
        version="2.0.0",
        description="Enhanced musician audio metadata with album support"
    )
    
    print(f"🧪 Validating modified schema...")
    modified_result = await validator.validate_schema(modified_musician_schema)
    
    print(f"   Compatibility: {modified_result.compatibility_level.value}")
    if modified_result.required_migrations:
        print(f"   Migration required: Yes")
        print(f"   Migration script preview:")
        print(f"   {modified_result.required_migrations[0][:200]}...")
    
    # Test d'un schéma avec erreurs
    print(f"\n❌ Testing invalid schema...")
    
    invalid_schema = TableSchema(
        table_name="invalid_test_table",
        columns={
            "123invalid": ColumnDefinition("123invalid", "INVALID_TYPE", nullable=False),
            "missing_pk": ColumnDefinition("missing_pk", "VARCHAR(50)", nullable=True)
        },
        primary_key=[],  # Pas de clé primaire
        creator_type=CreatorDataType.BLOGGER_CONTENT_DATA
    )
    
    invalid_result = await validator.validate_schema(invalid_schema)
    print(f"   Valid: {invalid_result.is_valid}")
    print(f"   Errors: {invalid_result.errors}")
    print(f"   Warnings: {invalid_result.warnings}")
    
    print(f"\n✅ SchemaValidator demonstration completed")


if __name__ == "__main__":
    asyncio.run(main())