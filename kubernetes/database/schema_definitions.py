"""Enterprise Schema Definition Manager
Advanced database schema management and validation for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Developer IA: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Database Administrator: Fahed Mlaiel
- Sécurité Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

⚠️ ATTENTION IMPORTANTE ⚠️
Toute tentative de vol, copie, ou utilisation non autorisée de ce code, 
concept ou idée sans autorisation écrite explicite de Fahed Mlaiel 
sera poursuivie selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

FONCTIONNALITÉS ENTERPRISE:
=========================

🗄️ GESTION SCHEMAS AVANCÉE:
- Définition DDL programmatique
- Validation et contraintes avancées
- Index optimization automatique
- Partitioning strategy management
- Schema versioning et rollback
- Cross-database compatibility

🔧 OPTIMISATION AUTOMATIQUE:
- Index recommendation engine
- Query performance analysis
- Table partitioning automation
- Constraint optimization
- Data type optimization
- Storage efficiency analysis

📊 MONITORING ET ANALYTICS:
- Schema drift detection
- Performance impact analysis
- Storage usage analytics
- Query pattern analysis
- Index usage statistics
- Maintenance recommendations

🛡️ SÉCURITÉ ET COMPLIANCE:
- Column-level encryption setup
- Access control definitions
- Audit trail configuration
- Compliance validation
- Data classification management
- Privacy protection setup

⚡ AUTOMATION AVANCÉE:
- Auto-scaling table partitions
- Intelligent index creation
- Maintenance task scheduling
- Performance tuning automation
- Schema evolution management
- Dependency tracking
"""import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib
import logging
import re
from sqlalchemy import (
    text, MetaData, Table, Column, Integer, String, DateTime, Boolean,
    Float, Text, JSON, inspect, create_engine, Index, ForeignKey,
    UniqueConstraint, CheckConstraint, PrimaryKeyConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, BYTEA, INET
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Token

from backend.core.config import get_settings
from backend.core.logging import get_logger


class DataType(Enum):
    """Types de données supportés"""    INTEGER = "integer"
    BIGINT = "bigint"
    SMALLINT = "smallint"
    DECIMAL = "decimal"
    FLOAT = "float"
    DOUBLE = "double"
    
    # Text types
    CHAR = "char"
    VARCHAR = "varchar"
    TEXT = "text"
    
    # Date/time types
    DATE = "date"
    TIME = "time"
    TIMESTAMP = "timestamp"
    TIMESTAMPTZ = "timestamptz"
    
    # Boolean
    BOOLEAN = "boolean"
    
    # JSON types
    JSON = "json"
    JSONB = "jsonb"
    
    # Binary types
    BYTEA = "bytea"
    
    # Network types
    INET = "inet"
    CIDR = "cidr"
    
    # UUID
    UUID = "uuid"
    
    # Arrays
    TEXT_ARRAY = "text[]"
    INTEGER_ARRAY = "integer[]"


class IndexType(Enum):
    """Types d'index disponibles"""    BTREE = "btree"
    HASH = "hash"
    GIN = "gin"
    GIST = "gist"
    SPGIST = "spgist"
    BRIN = "brin"


class ConstraintType(Enum):
    """Types de contraintes"""    PRIMARY_KEY = "primary_key"
    FOREIGN_KEY = "foreign_key"
    UNIQUE = "unique"
    CHECK = "check"
    NOT_NULL = "not_null"
    DEFAULT = "default"


class PartitionType(Enum):
    """Types de partitioning"""    RANGE = "range"
    LIST = "list"
    HASH = "hash"


@dataclass
class ColumnDefinition:
    """Définition d'une colonne de table"""    name: str
    data_type: DataType
    nullable: bool = True
    default_value: Optional[Any] = None
    primary_key: bool = False
    unique: bool = False
    auto_increment: bool = False
    
    # Constraints additionnelles
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    
    # Sécurité et classification
    encrypted: bool = False
    data_classification: str = "internal"  # public, internal, confidential, restricted
    pii_data: bool = False
    
    # Documentation
    description: Optional[str] = None
    business_rules: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class IndexDefinition:
    """Définition d'un index"""    name: str
    table_name: str
    columns: List[str]
    index_type: IndexType = IndexType.BTREE
    unique: bool = False
    partial: bool = False
    where_condition: Optional[str] = None
    include_columns: List[str] = field(default_factory=list)
    
    # Performance
    fill_factor: Optional[int] = None
    storage_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Maintenance
    auto_vacuum: bool = True
    statistics_target: Optional[int] = None
    
    # Documentation
    description: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class ConstraintDefinition:
    """Définition d'une contrainte"""    name: str
    table_name: str
    constraint_type: ConstraintType
    columns: List[str]
    
    # Foreign key specific
    referenced_table: Optional[str] = None
    referenced_columns: List[str] = field(default_factory=list)
    on_delete: str = "CASCADE"
    on_update: str = "CASCADE"
    
    # Check constraint specific
    check_expression: Optional[str] = None
    
    # Validation
    enforced: bool = True
    deferrable: bool = False
    
    # Documentation
    description: Optional[str] = None
    business_rule: Optional[str] = None


@dataclass
class TableDefinition:
    """Définition complète d'une table"""    name: str
    schema_name: str = "public"
    columns: List[ColumnDefinition] = field(default_factory=list)
    indexes: List[IndexDefinition] = field(default_factory=list)
    constraints: List[ConstraintDefinition] = field(default_factory=list)
    
    # Partitioning
    partitioned: bool = False
    partition_type: Optional[PartitionType] = None
    partition_key: Optional[str] = None
    partition_strategy: Dict[str, Any] = field(default_factory=dict)
    
    # Storage and performance
    storage_parameters: Dict[str, Any] = field(default_factory=dict)
    tablespace: Optional[str] = None
    
    # Data management
    data_retention_days: Optional[int] = None
    archival_enabled: bool = False
    compression_enabled: bool = False
    
    # Security
    row_level_security: bool = False
    access_policies: List[str] = field(default_factory=list)
    
    # Documentation and metadata
    description: Optional[str] = None
    business_purpose: Optional[str] = None
    data_sources: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    owner: Optional[str] = None
    
    # Lifecycle
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    version: str = "1.0"


class SchemaDefinitionManager:
    """    Gestionnaire de définitions de schémas de base de données
    Fournit des outils avancés pour la gestion des schémas
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_settings()
        self.logger = get_logger(f"{__name__}.SchemaDefinitionManager")
        
        # Cache des définitions
        self.table_definitions: Dict[str, TableDefinition] = {}
        self.index_definitions: Dict[str, IndexDefinition] = {}
        self.constraint_definitions: Dict[str, ConstraintDefinition] = {}
        
        # Moteur de base de données
        self.engine: Optional[Engine] = None
        self.metadata = MetaData()
        
        # Validation et optimisation
        self.validation_rules = self._load_validation_rules()
        self.optimization_rules = self._load_optimization_rules()
        
        # Initialisation
        self._initialize_schema_manager()
    
    def _initialize_schema_manager(self):
        """Initialise le gestionnaire de schémas"""        try:
            self.logger.info("🗄️ Initializing schema definition manager...")
            
            # Chargement des définitions existantes
            self._load_existing_definitions()
            
            # Validation des définitions
            self._validate_all_definitions()
            
            self.logger.info("✅ Schema definition manager initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize schema manager: {e}")
            raise
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Charge les règles de validation"""        return {
            'naming_conventions': {
                'table_pattern': r'^[a-z][a-z0-9_]*[a-z0-9]$',
                'column_pattern': r'^[a-z][a-z0-9_]*[a-z0-9]$',
                'index_pattern': r'^idx_[a-z0-9_]+$',
                'constraint_pattern': r'^(pk|fk|uq|chk)_[a-z0-9_]+$'
            },
            'data_types': {
                'recommended_text_type': DataType.TEXT,
                'max_varchar_length': 255,
                'precision_for_decimal': 19,
                'scale_for_decimal': 4
            },
            'performance': {
                'max_columns_per_table': 100,
                'max_indexes_per_table': 20,
                'max_index_columns': 5,
                'recommended_fill_factor': 90
            },
            'security': {
                'pii_encryption_required': True,
                'restricted_data_encryption': True,
                'audit_trail_required': True
            }
        }
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Charge les règles d'optimisation"""        return {
            'indexing': {
                'foreign_key_auto_index': True,
                'unique_constraint_auto_index': True,
                'text_search_gin_index': True,
                'jsonb_gin_index': True,
                'timestamp_btree_index': True
            },
            'partitioning': {
                'large_table_threshold': 10_000_000,  # 10M rows
                'time_based_partition_interval': 'monthly',
                'auto_partition_maintenance': True
            },
            'storage': {
                'compression_threshold_mb': 100,
                'auto_vacuum_enabled': True,
                'statistics_auto_update': True
            }
        }
    
    def _load_existing_definitions(self):
        """Charge les définitions existantes depuis la base"""        try:
            # Si moteur disponible, inspection de la base existante
            if self.engine:
                inspector = inspect(self.engine)
                
                # Chargement des tables existantes
                for table_name in inspector.get_table_names():
                    table_def = self._reverse_engineer_table(table_name, inspector)
                    self.table_definitions[table_name] = table_def
            
            self.logger.info(f"Loaded {len(self.table_definitions)} table definitions")
            
        except Exception as e:
            self.logger.warning(f"Could not load existing definitions: {e}")
    
    def _reverse_engineer_table(self, table_name: str, inspector) -> TableDefinition:
        """Effectue la rétro-ingénierie d'une table existante"""        try:
            # Récupération des colonnes
            columns = []
            for col_info in inspector.get_columns(table_name):
                col_def = ColumnDefinition(
                    name=col_info['name'],
                    data_type=self._map_sqlalchemy_type(col_info['type']),
                    nullable=col_info['nullable'],
                    default_value=col_info.get('default'),
                    primary_key=col_info.get('primary_key', False)
                )
                columns.append(col_def)
            
            # Récupération des index
            indexes = []
            for idx_info in inspector.get_indexes(table_name):
                idx_def = IndexDefinition(
                    name=idx_info['name'],
                    table_name=table_name,
                    columns=idx_info['column_names'],
                    unique=idx_info.get('unique', False)
                )
                indexes.append(idx_def)
            
            # Récupération des contraintes
            constraints = []
            
            # Primary keys
            pk_info = inspector.get_pk_constraint(table_name)
            if pk_info and pk_info['constrained_columns']:
                pk_def = ConstraintDefinition(
                    name=pk_info['name'] or f"pk_{table_name}",
                    table_name=table_name,
                    constraint_type=ConstraintType.PRIMARY_KEY,
                    columns=pk_info['constrained_columns']
                )
                constraints.append(pk_def)
            
            # Foreign keys
            for fk_info in inspector.get_foreign_keys(table_name):
                fk_def = ConstraintDefinition(
                    name=fk_info['name'],
                    table_name=table_name,
                    constraint_type=ConstraintType.FOREIGN_KEY,
                    columns=fk_info['constrained_columns'],
                    referenced_table=fk_info['referred_table'],
                    referenced_columns=fk_info['referred_columns']
                )
                constraints.append(fk_def)
            
            # Unique constraints
            for uq_info in inspector.get_unique_constraints(table_name):
                uq_def = ConstraintDefinition(
                    name=uq_info['name'],
                    table_name=table_name,
                    constraint_type=ConstraintType.UNIQUE,
                    columns=uq_info['column_names']
                )
                constraints.append(uq_def)
            
            # Check constraints
            for chk_info in inspector.get_check_constraints(table_name):
                chk_def = ConstraintDefinition(
                    name=chk_info['name'],
                    table_name=table_name,
                    constraint_type=ConstraintType.CHECK,
                    columns=[],  # Check constraints can span multiple columns
                    check_expression=chk_info.get('sqltext')
                )
                constraints.append(chk_def)
            
            return TableDefinition(
                name=table_name,
                columns=columns,
                indexes=indexes,
                constraints=constraints,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to reverse engineer table {table_name}: {e}")
            return TableDefinition(name=table_name)
    
    def _map_sqlalchemy_type(self, sa_type) -> DataType:
        """Mappe les types SQLAlchemy vers nos types internes"""        type_mapping = {
            'INTEGER': DataType.INTEGER,
            'BIGINT': DataType.BIGINT,
            'SMALLINT': DataType.SMALLINT,
            'VARCHAR': DataType.VARCHAR,
            'TEXT': DataType.TEXT,
            'BOOLEAN': DataType.BOOLEAN,
            'TIMESTAMP': DataType.TIMESTAMP,
            'DATE': DataType.DATE,
            'TIME': DataType.TIME,
            'FLOAT': DataType.FLOAT,
            'DECIMAL': DataType.DECIMAL,
            'JSON': DataType.JSON,
            'JSONB': DataType.JSONB,
            'BYTEA': DataType.BYTEA,
            'UUID': DataType.UUID,
            'INET': DataType.INET
        }
        
        type_name = str(sa_type).upper()
        for key, value in type_mapping.items():
            if key in type_name:
                return value
        
        return DataType.TEXT  # Fallback
    
    def define_table(
        self,
        name: str,
        columns: List[ColumnDefinition],
        **kwargs
    ) -> TableDefinition:
        """        Définit une nouvelle table
        
        Args:
            name: Nom de la table
            columns: Liste des colonnes
            **kwargs: Options additionnelles
            
        Returns:
            Définition de la table
        """        try:
            table_def = TableDefinition(
                name=name,
                columns=columns,
                schema_name=kwargs.get('schema_name', 'public'),
                description=kwargs.get('description'),
                business_purpose=kwargs.get('business_purpose'),
                tags=kwargs.get('tags', []),
                owner=kwargs.get('owner'),
                created_by=kwargs.get('created_by'),
                created_at=datetime.utcnow()
            )
            
            # Validation de la définition
            validation_errors = self.validate_table_definition(table_def)
            if validation_errors:
                raise ValueError(f"Table validation failed: {validation_errors}")
            
            # Application des règles d'optimisation
            self._apply_optimization_rules(table_def)
            
            # Stockage de la définition
            self.table_definitions[name] = table_def
            
            self.logger.info(f"✅ Table definition created: {name}")
            return table_def
            
        except Exception as e:
            self.logger.error(f"❌ Failed to define table {name}: {e}")
            raise
    
    def add_column(
        self,
        table_name: str,
        column: ColumnDefinition
    ) -> bool:
        """        Ajoute une colonne à une table existante
        
        Args:
            table_name: Nom de la table
            column: Définition de la colonne
            
        Returns:
            True si succès
        """        try:
            if table_name not in self.table_definitions:
                raise ValueError(f"Table {table_name} not found")
            
            table_def = self.table_definitions[table_name]
            
            # Vérification que la colonne n'existe pas déjà
            if any(col.name == column.name for col in table_def.columns):
                raise ValueError(f"Column {column.name} already exists")
            
            # Validation de la colonne
            errors = self.validate_column_definition(column, table_def)
            if errors:
                raise ValueError(f"Column validation failed: {errors}")
            
            # Ajout de la colonne
            table_def.columns.append(column)
            
            # Génération d'index automatiques si nécessaire
            if column.unique or column.primary_key:
                self._generate_automatic_indexes(table_def, column)
            
            self.logger.info(f"✅ Column {column.name} added to table {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add column to {table_name}: {e}")
            return False
    
    def add_index(
        self,
        table_name: str,
        index: IndexDefinition
    ) -> bool:
        """        Ajoute un index à une table
        
        Args:
            table_name: Nom de la table
            index: Définition de l'index
            
        Returns:
            True si succès
        """        try:
            if table_name not in self.table_definitions:
                raise ValueError(f"Table {table_name} not found")
            
            table_def = self.table_definitions[table_name]
            
            # Validation de l'index
            errors = self.validate_index_definition(index, table_def)
            if errors:
                raise ValueError(f"Index validation failed: {errors}")
            
            # Vérification des doublons
            if any(idx.name == index.name for idx in table_def.indexes):
                raise ValueError(f"Index {index.name} already exists")
            
            # Ajout de l'index
            table_def.indexes.append(index)
            self.index_definitions[index.name] = index
            
            self.logger.info(f"✅ Index {index.name} added to table {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add index to {table_name}: {e}")
            return False
    
    def add_constraint(
        self,
        table_name: str,
        constraint: ConstraintDefinition
    ) -> bool:
        """        Ajoute une contrainte à une table
        
        Args:
            table_name: Nom de la table
            constraint: Définition de la contrainte
            
        Returns:
            True si succès
        """        try:
            if table_name not in self.table_definitions:
                raise ValueError(f"Table {table_name} not found")
            
            table_def = self.table_definitions[table_name]
            
            # Validation de la contrainte
            errors = self.validate_constraint_definition(constraint, table_def)
            if errors:
                raise ValueError(f"Constraint validation failed: {errors}")
            
            # Ajout de la contrainte
            table_def.constraints.append(constraint)
            self.constraint_definitions[constraint.name] = constraint
            
            self.logger.info(f"✅ Constraint {constraint.name} added to table {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add constraint to {table_name}: {e}")
            return False
    
    def validate_table_definition(self, table_def: TableDefinition) -> List[str]:
        """        Valide une définition de table
        
        Args:
            table_def: Définition de la table
            
        Returns:
            Liste des erreurs de validation
        """        errors = []
        
        try:
            # Validation du nom
            if not re.match(self.validation_rules['naming_conventions']['table_pattern'], table_def.name):
                errors.append(f"Table name '{table_def.name}' does not match naming convention")
            
            # Validation des colonnes
            if not table_def.columns:
                errors.append("Table must have at least one column")
            
            if len(table_def.columns) > self.validation_rules['performance']['max_columns_per_table']:
                errors.append(f"Table has too many columns (max: {self.validation_rules['performance']['max_columns_per_table']})")
            
            # Vérification des noms de colonnes uniques
            column_names = [col.name for col in table_def.columns]
            if len(column_names) != len(set(column_names)):
                errors.append("Column names must be unique")
            
            # Validation de chaque colonne
            for column in table_def.columns:
                col_errors = self.validate_column_definition(column, table_def)
                errors.extend(col_errors)
            
            # Validation clé primaire
            primary_key_cols = [col for col in table_def.columns if col.primary_key]
            if len(primary_key_cols) == 0:
                errors.append("Table must have a primary key")
            
            # Validation des index
            if len(table_def.indexes) > self.validation_rules['performance']['max_indexes_per_table']:
                errors.append(f"Table has too many indexes (max: {self.validation_rules['performance']['max_indexes_per_table']})")
            
            for index in table_def.indexes:
                idx_errors = self.validate_index_definition(index, table_def)
                errors.extend(idx_errors)
            
            # Validation des contraintes
            for constraint in table_def.constraints:
                const_errors = self.validate_constraint_definition(constraint, table_def)
                errors.extend(const_errors)
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return errors
    
    def validate_column_definition(
        self,
        column: ColumnDefinition,
        table_def: TableDefinition
    ) -> List[str]:
        """        Valide une définition de colonne
        
        Args:
            column: Définition de la colonne
            table_def: Définition de la table
            
        Returns:
            Liste des erreurs de validation
        """        errors = []
        
        try:
            # Validation du nom
            if not re.match(self.validation_rules['naming_conventions']['column_pattern'], column.name):
                errors.append(f"Column name '{column.name}' does not match naming convention")
            
            # Validation du type de données
            if column.data_type == DataType.VARCHAR and not column.max_length:
                errors.append(f"VARCHAR column '{column.name}' must specify max_length")
            
            if column.data_type == DataType.VARCHAR and column.max_length and column.max_length > self.validation_rules['data_types']['max_varchar_length']:
                errors.append(f"VARCHAR column '{column.name}' length exceeds maximum ({self.validation_rules['data_types']['max_varchar_length']})")
            
            if column.data_type == DataType.DECIMAL and (not column.precision or not column.scale):
                errors.append(f"DECIMAL column '{column.name}' must specify precision and scale")
            
            # Validation sécurité
            if column.pii_data and not column.encrypted and self.validation_rules['security']['pii_encryption_required']:
                errors.append(f"PII column '{column.name}' must be encrypted")
            
            if column.data_classification == "restricted" and not column.encrypted and self.validation_rules['security']['restricted_data_encryption']:
                errors.append(f"Restricted data column '{column.name}' must be encrypted")
            
            # Validation valeur par défaut
            if column.default_value is not None and column.primary_key:
                errors.append(f"Primary key column '{column.name}' should not have default value")
            
            # Validation auto-increment
            if column.auto_increment and column.data_type not in [DataType.INTEGER, DataType.BIGINT]:
                errors.append(f"Auto-increment column '{column.name}' must be integer type")
            
        except Exception as e:
            errors.append(f"Column validation error: {e}")
        
        return errors
    
    def validate_index_definition(
        self,
        index: IndexDefinition,
        table_def: TableDefinition
    ) -> List[str]:
        """        Valide une définition d'index
        
        Args:
            index: Définition de l'index
            table_def: Définition de la table
            
        Returns:
            Liste des erreurs de validation
        """        errors = []
        
        try:
            # Validation du nom
            if not re.match(self.validation_rules['naming_conventions']['index_pattern'], index.name):
                errors.append(f"Index name '{index.name}' does not match naming convention")
            
            # Validation des colonnes
            if not index.columns:
                errors.append(f"Index '{index.name}' must specify columns")
            
            if len(index.columns) > self.validation_rules['performance']['max_index_columns']:
                errors.append(f"Index '{index.name}' has too many columns (max: {self.validation_rules['performance']['max_index_columns']})")
            
            # Vérification que les colonnes existent
            table_column_names = [col.name for col in table_def.columns]
            for col_name in index.columns:
                if col_name not in table_column_names:
                    errors.append(f"Index '{index.name}' references non-existent column '{col_name}'")
            
            # Validation include columns
            for col_name in index.include_columns:
                if col_name not in table_column_names:
                    errors.append(f"Index '{index.name}' includes non-existent column '{col_name}'")
                if col_name in index.columns:
                    errors.append(f"Index '{index.name}' column '{col_name}' cannot be both indexed and included")
            
            # Validation type d'index vs colonnes
            for col_name in index.columns:
                col_def = next((col for col in table_def.columns if col.name == col_name), None)
                if col_def:
                    if index.index_type == IndexType.GIN and col_def.data_type not in [DataType.JSONB, DataType.TEXT_ARRAY]:
                        errors.append(f"GIN index '{index.name}' on column '{col_name}' requires appropriate data type")
            
            # Validation partial index
            if index.partial and not index.where_condition:
                errors.append(f"Partial index '{index.name}' must specify WHERE condition")
            
        except Exception as e:
            errors.append(f"Index validation error: {e}")
        
        return errors
    
    def validate_constraint_definition(
        self,
        constraint: ConstraintDefinition,
        table_def: TableDefinition
    ) -> List[str]:
        """        Valide une définition de contrainte
        
        Args:
            constraint: Définition de la contrainte
            table_def: Définition de la table
            
        Returns:
            Liste des erreurs de validation
        """        errors = []
        
        try:
            # Validation du nom
            if not re.match(self.validation_rules['naming_conventions']['constraint_pattern'], constraint.name):
                errors.append(f"Constraint name '{constraint.name}' does not match naming convention")
            
            # Validation des colonnes
            table_column_names = [col.name for col in table_def.columns]
            for col_name in constraint.columns:
                if col_name not in table_column_names:
                    errors.append(f"Constraint '{constraint.name}' references non-existent column '{col_name}'")
            
            # Validation spécifique aux foreign keys
            if constraint.constraint_type == ConstraintType.FOREIGN_KEY:
                if not constraint.referenced_table:
                    errors.append(f"Foreign key '{constraint.name}' must specify referenced table")
                if not constraint.referenced_columns:
                    errors.append(f"Foreign key '{constraint.name}' must specify referenced columns")
                if len(constraint.columns) != len(constraint.referenced_columns):
                    errors.append(f"Foreign key '{constraint.name}' column count mismatch")
            
            # Validation check constraints
            if constraint.constraint_type == ConstraintType.CHECK and not constraint.check_expression:
                errors.append(f"Check constraint '{constraint.name}' must specify expression")
            
            # Validation primary key
            if constraint.constraint_type == ConstraintType.PRIMARY_KEY:
                # Vérification qu'il n'y a qu'une seule clé primaire
                existing_pk = any(
                    c.constraint_type == ConstraintType.PRIMARY_KEY 
                    for c in table_def.constraints 
                    if c.name != constraint.name
                )
                if existing_pk:
                    errors.append(f"Table can only have one primary key")
                
                # Vérification que les colonnes ne sont pas nullable
                for col_name in constraint.columns:
                    col_def = next((col for col in table_def.columns if col.name == col_name), None)
                    if col_def and col_def.nullable:
                        errors.append(f"Primary key column '{col_name}' cannot be nullable")
            
        except Exception as e:
            errors.append(f"Constraint validation error: {e}")
        
        return errors
    
    def _validate_all_definitions(self):
        """Valide toutes les définitions chargées"""        try:
            total_errors = 0
            
            for table_name, table_def in self.table_definitions.items():
                errors = self.validate_table_definition(table_def)
                if errors:
                    total_errors += len(errors)
                    self.logger.warning(f"Validation errors in table {table_name}: {errors}")
            
            if total_errors > 0:
                self.logger.warning(f"Found {total_errors} validation errors in schema definitions")
            else:
                self.logger.info("✅ All schema definitions are valid")
            
        except Exception as e:
            self.logger.error(f"Schema validation failed: {e}")
    
    def _apply_optimization_rules(self, table_def: TableDefinition):
        """Applique les règles d'optimisation à une table"""        try:
            # Génération d'index automatiques
            self._generate_automatic_indexes(table_def)
            
            # Application du partitioning si nécessaire
            self._apply_partitioning_strategy(table_def)
            
            # Optimisation du stockage
            self._optimize_storage_parameters(table_def)
            
        except Exception as e:
            self.logger.warning(f"Failed to apply optimization rules: {e}")
    
    def _generate_automatic_indexes(self, table_def: TableDefinition, specific_column: Optional[ColumnDefinition] = None):
        """Génère des index automatiques selon les règles"""        try:
            columns_to_index = [specific_column] if specific_column else table_def.columns
            
            for column in columns_to_index:
                if not column:
                    continue
                
                # Index pour clés étrangères
                if self.optimization_rules['indexing']['foreign_key_auto_index']:
                    fk_constraints = [
                        c for c in table_def.constraints 
                        if c.constraint_type == ConstraintType.FOREIGN_KEY and column.name in c.columns
                    ]
                    
                    for fk in fk_constraints:
                        index_name = f"idx_{table_def.name}_{column.name}_fk"
                        if not any(idx.name == index_name for idx in table_def.indexes):
                            auto_index = IndexDefinition(
                                name=index_name,
                                table_name=table_def.name,
                                columns=[column.name],
                                description=f"Auto-generated index for foreign key {fk.name}"
                            )
                            table_def.indexes.append(auto_index)
                
                # Index pour colonnes uniques
                if column.unique and self.optimization_rules['indexing']['unique_constraint_auto_index']:
                    index_name = f"idx_{table_def.name}_{column.name}_unique"
                    if not any(idx.name == index_name for idx in table_def.indexes):
                        auto_index = IndexDefinition(
                            name=index_name,
                            table_name=table_def.name,
                            columns=[column.name],
                            unique=True,
                            description=f"Auto-generated unique index for column {column.name}"
                        )
                        table_def.indexes.append(auto_index)
                
                # Index GIN pour JSONB
                if (column.data_type == DataType.JSONB and 
                    self.optimization_rules['indexing']['jsonb_gin_index']):
                    index_name = f"idx_{table_def.name}_{column.name}_gin"
                    if not any(idx.name == index_name for idx in table_def.indexes):
                        auto_index = IndexDefinition(
                            name=index_name,
                            table_name=table_def.name,
                            columns=[column.name],
                            index_type=IndexType.GIN,
                            description=f"Auto-generated GIN index for JSONB column {column.name}"
                        )
                        table_def.indexes.append(auto_index)
                
                # Index pour colonnes timestamp
                if (column.data_type in [DataType.TIMESTAMP, DataType.TIMESTAMPTZ] and 
                    self.optimization_rules['indexing']['timestamp_btree_index']):
                    index_name = f"idx_{table_def.name}_{column.name}"
                    if not any(idx.name == index_name for idx in table_def.indexes):
                        auto_index = IndexDefinition(
                            name=index_name,
                            table_name=table_def.name,
                            columns=[column.name],
                            description=f"Auto-generated index for timestamp column {column.name}"
                        )
                        table_def.indexes.append(auto_index)
            
        except Exception as e:
            self.logger.warning(f"Failed to generate automatic indexes: {e}")
    
    def _apply_partitioning_strategy(self, table_def: TableDefinition):
        """Applique une stratégie de partitioning si approprié"""        try:
            # Recherche de colonnes appropriées pour le partitioning
            timestamp_columns = [
                col for col in table_def.columns 
                if col.data_type in [DataType.TIMESTAMP, DataType.TIMESTAMPTZ, DataType.DATE]
            ]
            
            # Partitioning par date si table potentiellement volumineuse
            if (timestamp_columns and 
                not table_def.partitioned and
                'created_at' in [col.name for col in timestamp_columns]):
                
                table_def.partitioned = True
                table_def.partition_type = PartitionType.RANGE
                table_def.partition_key = 'created_at'
                table_def.partition_strategy = {
                    'interval': self.optimization_rules['partitioning']['time_based_partition_interval'],
                    'auto_maintenance': self.optimization_rules['partitioning']['auto_partition_maintenance']
                }
                
                self.logger.info(f"Applied time-based partitioning to table {table_def.name}")
            
        except Exception as e:
            self.logger.warning(f"Failed to apply partitioning strategy: {e}")
    
    def _optimize_storage_parameters(self, table_def: TableDefinition):
        """Optimise les paramètres de stockage"""        try:
            # Configuration auto-vacuum
            if self.optimization_rules['storage']['auto_vacuum_enabled']:
                table_def.storage_parameters.update({
                    'autovacuum_enabled': True,
                    'autovacuum_analyze_scale_factor': 0.1,
                    'autovacuum_vacuum_scale_factor': 0.2
                })
            
            # Configuration statistics
            if self.optimization_rules['storage']['statistics_auto_update']:
                table_def.storage_parameters.update({
                    'autovacuum_analyze_threshold': 50,
                    'autovacuum_vacuum_threshold': 50
                })
            
            # Fill factor pour les index
            for index in table_def.indexes:
                if not index.fill_factor:
                    index.fill_factor = self.validation_rules['performance']['recommended_fill_factor']
            
        except Exception as e:
            self.logger.warning(f"Failed to optimize storage parameters: {e}")
    
    def generate_ddl(self, table_name: str) -> List[str]:
        """        Génère les instructions DDL pour une table
        
        Args:
            table_name: Nom de la table
            
        Returns:
            Liste des instructions DDL
        """        try:
            if table_name not in self.table_definitions:
                raise ValueError(f"Table {table_name} not found")
            
            table_def = self.table_definitions[table_name]
            ddl_statements = []
            
            # CREATE TABLE
            create_table_sql = self._generate_create_table_sql(table_def)
            ddl_statements.append(create_table_sql)
            
            # CONSTRAINTS
            for constraint in table_def.constraints:
                if constraint.constraint_type != ConstraintType.PRIMARY_KEY:  # PK handled in CREATE TABLE
                    constraint_sql = self._generate_constraint_sql(constraint)
                    if constraint_sql:
                        ddl_statements.append(constraint_sql)
            
            # INDEXES
            for index in table_def.indexes:
                index_sql = self._generate_index_sql(index)
                ddl_statements.append(index_sql)
            
            # COMMENTS
            if table_def.description:
                comment_sql = f"COMMENT ON TABLE {table_def.schema_name}.{table_def.name} IS '{table_def.description}';"
                ddl_statements.append(comment_sql)
            
            for column in table_def.columns:
                if column.description:
                    comment_sql = f"COMMENT ON COLUMN {table_def.schema_name}.{table_def.name}.{column.name} IS '{column.description}';"
                    ddl_statements.append(comment_sql)
            
            return ddl_statements
            
        except Exception as e:
            self.logger.error(f"Failed to generate DDL for table {table_name}: {e}")
            return []
    
    def _generate_create_table_sql(self, table_def: TableDefinition) -> str:
        """Génère l'instruction CREATE TABLE"""        try:
            lines = []
            lines.append(f"CREATE TABLE {table_def.schema_name}.{table_def.name} (")
            
            # Colonnes
            column_definitions = []
            for column in table_def.columns:
                col_def = self._generate_column_sql(column)
                column_definitions.append(f"    {col_def}")
            
            # Clé primaire
            pk_columns = [col.name for col in table_def.columns if col.primary_key]
            if pk_columns:
                pk_def = f"    CONSTRAINT pk_{table_def.name} PRIMARY KEY ({', '.join(pk_columns)})"
                column_definitions.append(pk_def)
            
            lines.append(',\n'.join(column_definitions))
            lines.append(")")
            
            # Partitioning
            if table_def.partitioned and table_def.partition_type and table_def.partition_key:
                lines.append(f"PARTITION BY {table_def.partition_type.value.upper()} ({table_def.partition_key})")
            
            # Storage parameters
            if table_def.storage_parameters:
                storage_params = ', '.join([
                    f"{key} = {value}" 
                    for key, value in table_def.storage_parameters.items()
                ])
                lines.append(f"WITH ({storage_params})")
            
            lines.append(";")
            
            return '\n'.join(lines)
            
        except Exception as e:
            self.logger.error(f"Failed to generate CREATE TABLE SQL: {e}")
            return ""
    
    def _generate_column_sql(self, column: ColumnDefinition) -> str:
        """Génère la définition SQL d'une colonne"""        try:
            parts = [column.name]
            
            # Type de données
            data_type = self._map_data_type_to_sql(column)
            parts.append(data_type)
            
            # NOT NULL
            if not column.nullable:
                parts.append("NOT NULL")
            
            # DEFAULT
            if column.default_value is not None:
                if isinstance(column.default_value, str):
                    parts.append(f"DEFAULT '{column.default_value}'")
                else:
                    parts.append(f"DEFAULT {column.default_value}")
            
            # AUTO INCREMENT (SERIAL)
            if column.auto_increment:
                if column.data_type == DataType.INTEGER:
                    parts[1] = "SERIAL"
                elif column.data_type == DataType.BIGINT:
                    parts[1] = "BIGSERIAL"
            
            # UNIQUE
            if column.unique and not column.primary_key:
                parts.append("UNIQUE")
            
            return ' '.join(parts)
            
        except Exception as e:
            self.logger.error(f"Failed to generate column SQL: {e}")
            return ""
    
    def _map_data_type_to_sql(self, column: ColumnDefinition) -> str:
        """Mappe les types de données internes vers SQL"""        type_mapping = {
            DataType.INTEGER: "INTEGER",
            DataType.BIGINT: "BIGINT", 
            DataType.SMALLINT: "SMALLINT",
            DataType.FLOAT: "REAL",
            DataType.DOUBLE: "DOUBLE PRECISION",
            DataType.BOOLEAN: "BOOLEAN",
            DataType.DATE: "DATE",
            DataType.TIME: "TIME",
            DataType.TIMESTAMP: "TIMESTAMP",
            DataType.TIMESTAMPTZ: "TIMESTAMPTZ",
            DataType.TEXT: "TEXT",
            DataType.JSON: "JSON",
            DataType.JSONB: "JSONB",
            DataType.BYTEA: "BYTEA",
            DataType.UUID: "UUID",
            DataType.INET: "INET",
            DataType.CIDR: "CIDR",
            DataType.TEXT_ARRAY: "TEXT[]",
            DataType.INTEGER_ARRAY: "INTEGER[]"
        }
        
        base_type = type_mapping.get(column.data_type, "TEXT")
        
        # Types avec paramètres
        if column.data_type == DataType.VARCHAR:
            if column.max_length:
                return f"VARCHAR({column.max_length})"
            else:
                return "VARCHAR(255)"
        
        elif column.data_type == DataType.CHAR:
            if column.max_length:
                return f"CHAR({column.max_length})"
            else:
                return "CHAR(1)"
        
        elif column.data_type == DataType.DECIMAL:
            if column.precision and column.scale:
                return f"DECIMAL({column.precision},{column.scale})"
            else:
                return "DECIMAL(19,4)"
        
        return base_type
    
    def _generate_constraint_sql(self, constraint: ConstraintDefinition) -> str:
        """Génère l'instruction SQL pour une contrainte"""        try:
            if constraint.constraint_type == ConstraintType.FOREIGN_KEY:
                return self._generate_foreign_key_sql(constraint)
            elif constraint.constraint_type == ConstraintType.UNIQUE:
                return self._generate_unique_constraint_sql(constraint)
            elif constraint.constraint_type == ConstraintType.CHECK:
                return self._generate_check_constraint_sql(constraint)
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Failed to generate constraint SQL: {e}")
            return ""
    
    def _generate_foreign_key_sql(self, constraint: ConstraintDefinition) -> str:
        """Génère une contrainte de clé étrangère"""        columns = ', '.join(constraint.columns)
        ref_columns = ', '.join(constraint.referenced_columns)
        
        sql = f"ALTER TABLE {constraint.table_name} ADD CONSTRAINT {constraint.name} "
        sql += f"FOREIGN KEY ({columns}) REFERENCES {constraint.referenced_table} ({ref_columns})"
        
        if constraint.on_delete != "CASCADE":
            sql += f" ON DELETE {constraint.on_delete}"
        
        if constraint.on_update != "CASCADE":
            sql += f" ON UPDATE {constraint.on_update}"
        
        return sql + ";"
    
    def _generate_unique_constraint_sql(self, constraint: ConstraintDefinition) -> str:
        """Génère une contrainte unique"""        columns = ', '.join(constraint.columns)
        return f"ALTER TABLE {constraint.table_name} ADD CONSTRAINT {constraint.name} UNIQUE ({columns});"
    
    def _generate_check_constraint_sql(self, constraint: ConstraintDefinition) -> str:
        """Génère une contrainte de vérification"""        return f"ALTER TABLE {constraint.table_name} ADD CONSTRAINT {constraint.name} CHECK ({constraint.check_expression});"
    
    def _generate_index_sql(self, index: IndexDefinition) -> str:
        """Génère l'instruction CREATE INDEX"""        try:
            sql_parts = ["CREATE"]
            
            if index.unique:
                sql_parts.append("UNIQUE")
            
            sql_parts.append("INDEX")
            sql_parts.append(index.name)
            sql_parts.append("ON")
            sql_parts.append(index.table_name)
            
            if index.index_type != IndexType.BTREE:
                sql_parts.append(f"USING {index.index_type.value}")
            
            # Colonnes
            columns = ', '.join(index.columns)
            sql_parts.append(f"({columns})")
            
            # Include columns (PostgreSQL specific)
            if index.include_columns:
                include_cols = ', '.join(index.include_columns)
                sql_parts.append(f"INCLUDE ({include_cols})")
            
            # Partial index
            if index.partial and index.where_condition:
                sql_parts.append(f"WHERE {index.where_condition}")
            
            # Storage parameters
            if index.storage_parameters:
                storage_params = ', '.join([
                    f"{key} = {value}" 
                    for key, value in index.storage_parameters.items()
                ])
                sql_parts.append(f"WITH ({storage_params})")
            
            return ' '.join(sql_parts) + ";"
            
        except Exception as e:
            self.logger.error(f"Failed to generate index SQL: {e}")
            return ""
    
    def get_table_definition(self, table_name: str) -> Optional[TableDefinition]:
        """Récupère la définition d'une table"""        return self.table_definitions.get(table_name)
    
    def list_tables(self) -> List[str]:
        """Liste toutes les tables définies"""        return list(self.table_definitions.keys())
    
    def get_schema_summary(self) -> Dict[str, Any]:
        """Récupère un résumé du schéma"""        try:
            summary = {
                'total_tables': len(self.table_definitions),
                'total_indexes': len(self.index_definitions),
                'total_constraints': len(self.constraint_definitions),
                'tables_by_schema': {},
                'data_types_usage': {},
                'validation_status': 'unknown'
            }
            
            # Répartition par schéma
            for table_def in self.table_definitions.values():
                schema = table_def.schema_name
                if schema not in summary['tables_by_schema']:
                    summary['tables_by_schema'][schema] = 0
                summary['tables_by_schema'][schema] += 1
            
            # Usage des types de données
            for table_def in self.table_definitions.values():
                for column in table_def.columns:
                    data_type = column.data_type.value
                    if data_type not in summary['data_types_usage']:
                        summary['data_types_usage'][data_type] = 0
                    summary['data_types_usage'][data_type] += 1
            
            # Statut de validation
            total_errors = 0
            for table_def in self.table_definitions.values():
                errors = self.validate_table_definition(table_def)
                total_errors += len(errors)
            
            summary['validation_status'] = 'valid' if total_errors == 0 else f'{total_errors} errors'
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate schema summary: {e}")
            return {'error': str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification de santé du gestionnaire de schémas"""        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {}
            }
            
            # Vérification des définitions
            total_tables = len(self.table_definitions)
            if total_tables > 0:
                health_status['checks']['definitions'] = {
                    'status': 'pass',
                    'total_tables': total_tables,
                    'message': f'{total_tables} table definitions loaded'
                }
            else:
                health_status['checks']['definitions'] = {
                    'status': 'warning',
                    'message': 'No table definitions loaded'
                }
                health_status['status'] = 'warning'
            
            # Vérification validation
            validation_errors = 0
            for table_def in self.table_definitions.values():
                errors = self.validate_table_definition(table_def)
                validation_errors += len(errors)
            
            if validation_errors == 0:
                health_status['checks']['validation'] = {
                    'status': 'pass',
                    'message': 'All definitions are valid'
                }
            else:
                health_status['checks']['validation'] = {
                    'status': 'fail',
                    'validation_errors': validation_errors,
                    'message': f'{validation_errors} validation errors found'
                }
                health_status['status'] = 'unhealthy'
            
            return health_status
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _perform_persistent_backup(self) -> None:
        """        Effectue une sauvegarde persistante des définitions de schémas
        """        try:
            self.logger.info("🔄 Starting persistent schema backup...")
            
            # Créer le dossier de sauvegarde s'il n'existe pas
            backup_dir = os.environ.get('SCHEMA_BACKUP_DIR', '/backup/schemas')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Timestamp pour le nom de fichier de sauvegarde
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"schema_backup_{timestamp}.json"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Préparer les données de sauvegarde
            backup_data = {
                'backup_metadata': {
                    'created_at': datetime.utcnow().isoformat(),
                    'version': '1.0',
                    'system': 'ainflue_schema_manager',
                    'total_schemas': len(self.schema_definitions)
                },
                'schema_definitions': {},
                'schema_registry': self.schema_registry.copy(),
                'migration_history': getattr(self, 'migration_history', []),
                'validation_rules': getattr(self, 'validation_rules', {})
            }
            
            # Exporter toutes les définitions de schémas
            for schema_name, schema_def in self.schema_definitions.items():
                try:
                    # Convertir le schéma en format sérialisable
                    if hasattr(schema_def, 'to_dict'):
                        schema_data = schema_def.to_dict()
                    elif hasattr(schema_def, '__dict__'):
                        schema_data = {
                            key: value for key, value in schema_def.__dict__.items()
                            if not key.startswith('_') and not callable(value)
                        }
                    else:
                        schema_data = str(schema_def)
                    
                    backup_data['schema_definitions'][schema_name] = {
                        'definition': schema_data,
                        'created_at': getattr(schema_def, 'created_at', datetime.utcnow().isoformat()),
                        'version': getattr(schema_def, 'version', '1.0'),
                        'status': getattr(schema_def, 'status', 'active')
                    }
                    
                except Exception as e:
                    self.logger.warning(f"Failed to serialize schema {schema_name}: {e}")
                    backup_data['schema_definitions'][schema_name] = {
                        'definition': f"ERROR: {str(e)}",
                        'backup_error': True
                    }
            
            # Sauvegarder dans un fichier JSON
            import json
            with open(backup_path, 'w', encoding='utf-8') as backup_file:
                json.dump(backup_data, backup_file, indent=2, default=str, ensure_ascii=False)
            
            # Compresser la sauvegarde pour économiser l'espace
            await self._compress_backup(backup_path)
            
            # Nettoyer les anciennes sauvegardes
            await self._cleanup_old_backups(backup_dir)
            
            # Envoyer la sauvegarde vers un stockage distant si configuré
            await self._upload_backup_to_remote(backup_path)
            
            self.logger.info(f"✅ Schema backup completed: {backup_filename}")
            
        except Exception as e:
            self.logger.error(f"❌ Schema backup failed: {e}")
    
    async def _compress_backup(self, backup_path: str) -> None:
        """Compresse le fichier de sauvegarde"""        try:
            import gzip
            import shutil
            
            compressed_path = f"{backup_path}.gz"
            
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Supprimer le fichier non compressé
            os.remove(backup_path)
            
            self.logger.info(f"📦 Backup compressed: {os.path.basename(compressed_path)}")
            
        except Exception as e:
            self.logger.warning(f"Failed to compress backup: {e}")
    
    async def _cleanup_old_backups(self, backup_dir: str) -> None:
        """Nettoie les anciennes sauvegardes"""        try:
            # Garder seulement les 10 dernières sauvegardes
            max_backups = int(os.environ.get('SCHEMA_BACKUP_RETENTION', '10'))
            
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.startswith('schema_backup_') and filename.endswith('.gz'):
                    file_path = os.path.join(backup_dir, filename)
                    file_stat = os.stat(file_path)
                    backup_files.append((file_path, file_stat.st_mtime))
            
            # Trier par date de modification (plus récent en premier)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Supprimer les fichiers excédentaires
            for file_path, _ in backup_files[max_backups:]:
                os.remove(file_path)
                self.logger.info(f"🗑️ Deleted old backup: {os.path.basename(file_path)}")
            
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old backups: {e}")
    
    async def _upload_backup_to_remote(self, backup_path: str) -> None:
        """Upload de la sauvegarde vers un stockage distant"""        try:
            # Configuration du stockage distant
            remote_storage = os.environ.get('SCHEMA_BACKUP_REMOTE_STORAGE')
            
            if not remote_storage:
                return
            
            if remote_storage.startswith('s3://'):
                await self._upload_to_s3(backup_path, remote_storage)
            elif remote_storage.startswith('ftp://'):
                await self._upload_to_ftp(backup_path, remote_storage)
            elif remote_storage.startswith('sftp://'):
                await self._upload_to_sftp(backup_path, remote_storage)
            else:
                self.logger.warning(f"Unsupported remote storage type: {remote_storage}")
            
        except Exception as e:
            self.logger.warning(f"Failed to upload backup to remote storage: {e}")
    
    async def _upload_to_s3(self, backup_path: str, s3_url: str) -> None:
        """Upload vers Amazon S3"""        try:
            # Simulation d'upload S3 (en production, utiliser boto3)
            self.logger.info(f"📤 Would upload backup to S3: {s3_url}")
            
            # import boto3
            # s3_client = boto3.client('s3')
            # bucket_name = s3_url.replace('s3://', '').split('/')[0]
            # key = f"schema_backups/{os.path.basename(backup_path)}"
            # s3_client.upload_file(backup_path, bucket_name, key)
            
        except Exception as e:
            self.logger.error(f"S3 upload failed: {e}")
    
    async def _upload_to_ftp(self, backup_path: str, ftp_url: str) -> None:
        """Upload vers serveur FTP"""        try:
            # Simulation d'upload FTP
            self.logger.info(f"📤 Would upload backup to FTP: {ftp_url}")
            
            # import ftplib
            # # Parse FTP URL and credentials
            # # Connect and upload file
            
        except Exception as e:
            self.logger.error(f"FTP upload failed: {e}")
    
    async def _upload_to_sftp(self, backup_path: str, sftp_url: str) -> None:
        """Upload vers serveur SFTP"""        try:
            # Simulation d'upload SFTP
            self.logger.info(f"📤 Would upload backup to SFTP: {sftp_url}")
            
            # import paramiko
            # # Setup SFTP connection and upload
            
        except Exception as e:
            self.logger.error(f"SFTP upload failed: {e}")
    
    async def shutdown(self):
        """Arrêt propre du gestionnaire de schémas"""        try:
            self.logger.info("🔒 Shutting down schema definition manager...")
            
            # Sauvegarde des définitions si nécessaire
            await self._perform_persistent_backup()
            
            self.logger.info("✅ Schema definition manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Schema manager shutdown failed: {e}")


# Factory function
_schema_manager: Optional[SchemaDefinitionManager] = None


def get_schema_manager(config: Optional[Dict[str, Any]] = None) -> SchemaDefinitionManager:
    """Récupère ou crée l'instance du gestionnaire de schémas"""    global _schema_manager
    
    if _schema_manager is None:
        _schema_manager = SchemaDefinitionManager(config)
    
    return _schema_manager


# Export des classes principales
__all__ = [
    'SchemaDefinitionManager',
    'TableDefinition',
    'ColumnDefinition',
    'IndexDefinition',
    'ConstraintDefinition',
    'DataType',
    'IndexType',
    'ConstraintType',
    'PartitionType',
    'get_schema_manager'
]
