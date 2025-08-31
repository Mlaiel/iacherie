"""Sync Configurations Management Module

Gestion des configurations de synchronisation pour les intégrations plateformes
dans la plateforme IA Influencer Agent.

Ce module fournit:
- Configuration avancée des synchronisations bidirectionnelles
- Mapping des champs entre plateformes
- Règles de transformation des données
- Stratégies de synchronisation (temps réel, batch, incrémentale)
- Monitoring et benchmarks des performances

Auteur: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Équipe: Lead AI Developer, Backend Senior, Data Engineer, Platform Integration Specialist

⚠️  AVERTISSEMENT LEGAL ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon le droit allemand et international.

Contact pour autorisation: mlaiel@live.de
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Dict, List, Any, Optional, Union
import uuid
import logging
from datetime import datetime, timedelta
from enum import Enum
import json

from backend.database.models.base import BaseModel

logger = logging.getLogger(__name__)


class SyncDirection(Enum):
    """Directions de synchronisation."""    INBOUND = "inbound"  # De la plateforme vers notre système
    OUTBOUND = "outbound"  # De notre système vers la plateforme
    BIDIRECTIONAL = "bidirectional"  # Dans les deux sens
    MIRROR = "mirror"  # Miroir exact (synchronisation complète)


class SyncStrategy(Enum):
    """Stratégies de synchronisation."""    FULL = "full"  # Synchronisation complète
    INCREMENTAL = "incremental"  # Synchronisation incrémentale
    DELTA = "delta"  # Synchronisation des changements uniquement
    REAL_TIME = "real_time"  # Synchronisation temps réel (webhooks)
    BATCH = "batch"  # Synchronisation par lots
    SCHEDULED = "scheduled"  # Synchronisation planifiée
    ON_DEMAND = "on_demand"  # Synchronisation à la demande


class SyncStatus(Enum):
    """Statuts de synchronisation."""    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"
    QUEUED = "queued"


class DataType(Enum):
    """Types de données synchronisées."""    CONTENT = "content"
    METADATA = "metadata"
    ANALYTICS = "analytics"
    USER_PROFILE = "user_profile"
    MEDIA_FILES = "media_files"
    INTERACTIONS = "interactions"
    PLAYLISTS = "playlists"
    FOLLOWERS = "followers"
    COMMENTS = "comments"
    TAGS = "tags"
    LOCATION = "location"
    ENGAGEMENT = "engagement"


class ConflictResolution(Enum):
    """Stratégies de résolution de conflits."""    SOURCE_WINS = "source_wins"  # La source a toujours raison
    TARGET_WINS = "target_wins"  # La cible a toujours raison
    LATEST_WINS = "latest_wins"  # La dernière modification gagne
    MERGE = "merge"  # Fusion des données
    MANUAL = "manual"  # Résolution manuelle requise
    SKIP = "skip"  # Ignore le conflit
    VERSION_BOTH = "version_both"  # Garde les deux versions


class SyncConfiguration(BaseModel):
    """    Configuration principale des synchronisations entre plateformes.
    
    Définit comment, quand et quelles données synchroniser
    entre notre système et les plateformes externes.
    """    
    __tablename__ = "sync_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Configuration de base
    configuration_name = Column(String(100), nullable=False)
    description = Column(Text)
    sync_direction = Column(SQLEnum(SyncDirection), nullable=False)
    sync_strategy = Column(SQLEnum(SyncStrategy), nullable=False)
    
    # Types de données à synchroniser
    data_types = Column(JSONB, default=list)  # Liste des DataType
    include_patterns = Column(JSONB, default=list)  # Patterns d'inclusion
    exclude_patterns = Column(JSONB, default=list)  # Patterns d'exclusion
    
    # Planification
    is_enabled = Column(Boolean, default=True, index=True)
    schedule_expression = Column(String(100))  # Cron expression
    sync_frequency = Column(String(20), default="daily")  # realtime, hourly, daily, weekly
    max_execution_time = Column(Integer, default=3600)  # en secondes
    
    # Limitations et quotas
    batch_size = Column(Integer, default=100)
    max_records_per_sync = Column(Integer, default=1000)
    rate_limit_per_minute = Column(Integer, default=60)
    retry_count = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=60)
    
    # Gestion des conflits
    conflict_resolution = Column(SQLEnum(ConflictResolution), default=ConflictResolution.LATEST_WINS)
    backup_on_conflict = Column(Boolean, default=True)
    
    # Filtres avancés
    date_range_start = Column(DateTime(timezone=True))
    date_range_end = Column(DateTime(timezone=True))
    content_filters = Column(JSONB, default=dict)  # Filtres spécifiques au contenu
    quality_filters = Column(JSONB, default=dict)  # Filtres de qualité
    
    # Monitoring et alertes
    enable_notifications = Column(Boolean, default=True)
    notification_threshold = Column(Float, default=0.95)  # Seuil d'alerte (95% de succès)
    alert_on_failure = Column(Boolean, default=True)
    
    # Métadonnées
    last_sync_at = Column(DateTime(timezone=True))
    last_success_at = Column(DateTime(timezone=True))
    last_failure_at = Column(DateTime(timezone=True))
    consecutive_failures = Column(Integer, default=0)
    
    # Performance
    average_sync_duration = Column(Integer, default=0)  # en secondes
    average_records_per_sync = Column(Integer, default=0)
    total_syncs_executed = Column(Integer, default=0)
    total_records_synced = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SyncConfiguration(platform={self.platform_name}, strategy={self.sync_strategy.value})>"
    
    @property
    def is_due_for_sync(self) -> bool:
        """Vérifie si une synchronisation est due."""        if not self.is_enabled:
            return False
        
        if self.sync_strategy == SyncStrategy.REAL_TIME:
            return False  # Géré par les webhooks
        
        if not self.last_sync_at:
            return True
        
        now = datetime.utcnow()
        time_since_last = now - self.last_sync_at
        
        if self.sync_frequency == "realtime":
            return False
        elif self.sync_frequency == "hourly":
            return time_since_last >= timedelta(hours=1)
        elif self.sync_frequency == "daily":
            return time_since_last >= timedelta(days=1)
        elif self.sync_frequency == "weekly":
            return time_since_last >= timedelta(weeks=1)
        
        return False
    
    @property
    def health_score(self) -> float:
        """Calcule un score de santé de la synchronisation (0-100)."""        if self.total_syncs_executed == 0:
            return 100.0
        
        # Facteurs de calcul du score
        success_rate = 100.0
        if self.total_syncs_executed > 0:
            failures = self.consecutive_failures
            success_rate = max(0, 100 - (failures * 10))
        
        # Pénalité pour les échecs consécutifs
        consecutive_penalty = min(50, self.consecutive_failures * 5)
        
        # Bonus pour la régularité
        regularity_bonus = 0
        if self.last_success_at:
            time_since_success = datetime.utcnow() - self.last_success_at
            if time_since_success < timedelta(days=1):
                regularity_bonus = 10
        
        health_score = success_rate - consecutive_penalty + regularity_bonus
        return max(0.0, min(100.0, health_score))
    
    def update_performance_metrics(self, duration_seconds: int, records_count: int, success: bool):
        """Met à jour les métriques de performance."""        self.total_syncs_executed += 1
        
        if success:
            self.last_success_at = datetime.utcnow()
            self.consecutive_failures = 0
            self.total_records_synced += records_count
            
            # Mise à jour des moyennes
            total_duration = self.average_sync_duration * (self.total_syncs_executed - 1) + duration_seconds
            self.average_sync_duration = total_duration // self.total_syncs_executed
            
            total_records = self.average_records_per_sync * (self.total_syncs_executed - 1) + records_count
            self.average_records_per_sync = total_records // self.total_syncs_executed
        else:
            self.last_failure_at = datetime.utcnow()
            self.consecutive_failures += 1
        
        self.last_sync_at = datetime.utcnow()


class SyncExecution(BaseModel):
    """    Historique des exécutions de synchronisation.
    
    Enregistre les détails de chaque exécution pour audit,
    debugging et optimisation des performances.
    """    
    __tablename__ = "sync_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sync_configuration_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Informations d'exécution
    execution_id = Column(String(100), unique=True, index=True)  # ID unique pour tracking
    sync_direction = Column(SQLEnum(SyncDirection), nullable=False)
    sync_strategy = Column(SQLEnum(SyncStrategy), nullable=False)
    sync_status = Column(SQLEnum(SyncStatus), nullable=False, index=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    estimated_completion = Column(DateTime(timezone=True))
    
    # Résultats
    records_processed = Column(Integer, default=0)
    records_successful = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    
    # Détails techniques
    batch_count = Column(Integer, default=0)
    current_batch = Column(Integer, default=0)
    api_calls_made = Column(Integer, default=0)
    data_transferred_bytes = Column(Integer, default=0)
    
    # Erreurs et warnings
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    error_details = Column(JSONB, default=list)
    warning_details = Column(JSONB, default=list)
    
    # Résumé et métadonnées
    execution_summary = Column(JSONB, default=dict)
    performance_metrics = Column(JSONB, default=dict)
    debug_information = Column(JSONB, default=dict)
    
    # Contexte d'exécution
    triggered_by = Column(String(50))  # system, user, webhook, schedule
    trigger_context = Column(JSONB, default=dict)
    execution_environment = Column(String(50), default="production")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SyncExecution(platform={self.platform_name}, status={self.sync_status.value})>"
    
    @property
    def duration_seconds(self) -> int:
        """Calcule la durée d'exécution en secondes."""        if not self.completed_at or not self.started_at:
            return 0
        
        duration = self.completed_at - self.started_at
        return int(duration.total_seconds())
    
    @property
    def success_rate(self) -> float:
        """Calcule le taux de succès de cette exécution."""        if self.records_processed == 0:
            return 100.0
        
        return (self.records_successful / self.records_processed) * 100
    
    @property
    def throughput_per_second(self) -> float:
        """Calcule le débit en enregistrements par seconde."""        duration = self.duration_seconds
        if duration == 0:
            return 0.0
        
        return self.records_processed / duration


class SyncFieldMapping(BaseModel):
    """    Mapping des champs entre plateformes.
    
    Définit comment mapper les champs de données
    entre notre système et les plateformes externes.
    """    
    __tablename__ = "sync_field_mappings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sync_configuration_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Définition du mapping
    source_field = Column(String(100), nullable=False)
    target_field = Column(String(100), nullable=False)
    field_type = Column(String(30), nullable=False)  # string, number, boolean, date, object, array
    
    # Transformation et validation
    is_required = Column(Boolean, default=False)
    is_readonly = Column(Boolean, default=False)
    default_value = Column(JSONB)
    transformation_rules = Column(JSONB, default=list)
    validation_rules = Column(JSONB, default=dict)
    
    # Direction du mapping
    sync_direction = Column(SQLEnum(SyncDirection), nullable=False)
    priority = Column(Integer, default=0)  # Priorité pour l'ordre de traitement
    
    # Métadonnées
    description = Column(Text)
    examples = Column(JSONB, default=list)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SyncFieldMapping(platform={self.platform_name}, {self.source_field}->{self.target_field})>"
    
    def apply_transformation(self, value: Any) -> Any:
        """Applique les règles de transformation à une valeur."""        if not self.transformation_rules:
            return value
        
        transformed_value = value
        
        for rule in self.transformation_rules:
            rule_type = rule.get("type")
            
            if rule_type == "format_string":
                if isinstance(transformed_value, str):
                    format_template = rule.get("template", "{}")
                    transformed_value = format_template.format(transformed_value)
            
            elif rule_type == "convert_type":
                target_type = rule.get("target_type")
                if target_type == "string":
                    transformed_value = str(transformed_value)
                elif target_type == "int":
                    transformed_value = int(float(transformed_value))
                elif target_type == "float":
                    transformed_value = float(transformed_value)
                elif target_type == "bool":
                    transformed_value = bool(transformed_value)
            
            elif rule_type == "replace":
                if isinstance(transformed_value, str):
                    old_value = rule.get("old", "")
                    new_value = rule.get("new", "")
                    transformed_value = transformed_value.replace(old_value, new_value)
            
            elif rule_type == "truncate":
                if isinstance(transformed_value, str):
                    max_length = rule.get("max_length", 255)
                    transformed_value = transformed_value[:max_length]
            
            elif rule_type == "default_if_empty":
                if not transformed_value:
                    transformed_value = rule.get("default", "")
        
        return transformed_value


class DataTransformationRule(BaseModel):
    """    Règles de transformation avancées pour les données.
    
    Permet de définir des transformations complexes
    appliquées lors de la synchronisation.
    """    
    __tablename__ = "data_transformation_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sync_configuration_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Identification de la règle
    rule_name = Column(String(100), nullable=False)
    rule_description = Column(Text)
    rule_type = Column(String(50), nullable=False)  # filter, transform, validate, enrich
    
    # Conditions d'application
    conditions = Column(JSONB, default=dict)  # Conditions pour appliquer la règle
    field_patterns = Column(JSONB, default=list)  # Patterns de champs concernés
    data_type_filter = Column(SQLEnum(DataType))
    
    # Configuration de la transformation
    transformation_config = Column(JSONB, default=dict)
    execution_order = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=True)
    
    # Actions en cas d'erreur
    on_error_action = Column(String(20), default="skip")  # skip, stop, retry, use_default
    fallback_value = Column(JSONB)
    
    # Métriques d'utilisation
    times_applied = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_applied = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<DataTransformationRule(platform={self.platform_name}, rule={self.rule_name})>"


class SyncBenchmark(BaseModel):
    """    Benchmarks de performance des synchronisations.
    
    Enregistre les métriques de performance pour
    optimiser et surveiller les synchronisations.
    """    
    __tablename__ = "sync_benchmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, index=True)
    sync_strategy = Column(SQLEnum(SyncStrategy), nullable=False, index=True)
    data_type = Column(SQLEnum(DataType), nullable=False)
    
    # Métriques de performance
    benchmark_date = Column(DateTime(timezone=True), nullable=False, index=True)
    records_count = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    throughput_per_second = Column(Float, nullable=False)
    
    # Métriques détaillées
    api_response_time_avg = Column(Integer, default=0)  # ms
    api_response_time_max = Column(Integer, default=0)  # ms
    memory_usage_mb = Column(Float, default=0.0)
    cpu_usage_percent = Column(Float, default=0.0)
    network_io_mb = Column(Float, default=0.0)
    
    # Conditions du test
    batch_size = Column(Integer, nullable=False)
    concurrent_workers = Column(Integer, default=1)
    rate_limit_applied = Column(Integer, default=0)
    
    # Résultats de qualité
    success_rate = Column(Float, nullable=False)
    error_rate = Column(Float, default=0.0)
    data_accuracy_score = Column(Float, default=100.0)
    
    # Métadonnées
    environment = Column(String(50), default="production")
    test_configuration = Column(JSONB, default=dict)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SyncBenchmark(platform={self.platform_name}, throughput={self.throughput_per_second:.2f}/s)>"


# Configurations par défaut pour les plateformes principales
DEFAULT_SYNC_CONFIGURATIONS = {
    "spotify": {
        "user_profile": {
            "sync_direction": SyncDirection.BIDIRECTIONAL,
            "sync_strategy": SyncStrategy.INCREMENTAL,
            "sync_frequency": "daily",
            "batch_size": 50,
            "conflict_resolution": ConflictResolution.SOURCE_WINS
        },
        "playlists": {
            "sync_direction": SyncDirection.INBOUND,
            "sync_strategy": SyncStrategy.DELTA,
            "sync_frequency": "hourly",
            "batch_size": 100,
            "conflict_resolution": ConflictResolution.LATEST_WINS
        },
        "listening_history": {
            "sync_direction": SyncDirection.INBOUND,
            "sync_strategy": SyncStrategy.INCREMENTAL,
            "sync_frequency": "hourly",
            "batch_size": 200,
            "conflict_resolution": ConflictResolution.SOURCE_WINS
        }
    },
    "youtube": {
        "channel_data": {
            "sync_direction": SyncDirection.BIDIRECTIONAL,
            "sync_strategy": SyncStrategy.INCREMENTAL,
            "sync_frequency": "daily",
            "batch_size": 25,
            "conflict_resolution": ConflictResolution.SOURCE_WINS
        },
        "videos": {
            "sync_direction": SyncDirection.INBOUND,
            "sync_strategy": SyncStrategy.DELTA,
            "sync_frequency": "hourly",
            "batch_size": 50,
            "conflict_resolution": ConflictResolution.LATEST_WINS
        },
        "analytics": {
            "sync_direction": SyncDirection.INBOUND,
            "sync_strategy": SyncStrategy.INCREMENTAL,
            "sync_frequency": "daily",
            "batch_size": 100,
            "conflict_resolution": ConflictResolution.SOURCE_WINS
        }
    },
    "instagram": {
        "posts": {
            "sync_direction": SyncDirection.BIDIRECTIONAL,
            "sync_strategy": SyncStrategy.REAL_TIME,
            "sync_frequency": "realtime",
            "batch_size": 20,
            "conflict_resolution": ConflictResolution.LATEST_WINS
        },
        "stories": {
            "sync_direction": SyncDirection.INBOUND,
            "sync_strategy": SyncStrategy.REAL_TIME,
            "sync_frequency": "realtime",
            "batch_size": 10,
            "conflict_resolution": ConflictResolution.SOURCE_WINS
        },
        "engagement": {
            "sync_direction": SyncDirection.INBOUND,
            "sync_strategy": SyncStrategy.INCREMENTAL,
            "sync_frequency": "hourly",
            "batch_size": 500,
            "conflict_resolution": ConflictResolution.SOURCE_WINS
        }
    }
}


def create_default_sync_configurations(
    user_id: str,
    platform_connection_id: str,
    platform_name: str
) -> List[SyncConfiguration]:
    """    Crée les configurations de synchronisation par défaut pour une plateforme.
    
    Args:
        user_id: ID de l'utilisateur
        platform_connection_id: ID de la connexion plateforme
        platform_name: Nom de la plateforme
        
    Returns:
        Liste des configurations créées
    """    if platform_name not in DEFAULT_SYNC_CONFIGURATIONS:
        raise ValueError(f"No default sync configurations defined for platform: {platform_name}")
    
    platform_configs = DEFAULT_SYNC_CONFIGURATIONS[platform_name]
    configurations = []
    
    for config_name, config_data in platform_configs.items():
        sync_config = SyncConfiguration(
            user_id=user_id,
            platform_connection_id=platform_connection_id,
            platform_name=platform_name,
            configuration_name=f"{platform_name}_{config_name}",
            description=f"Default sync configuration for {platform_name} {config_name}",
            sync_direction=config_data["sync_direction"],
            sync_strategy=config_data["sync_strategy"],
            sync_frequency=config_data["sync_frequency"],
            batch_size=config_data["batch_size"],
            conflict_resolution=config_data["conflict_resolution"],
            data_types=[config_name]  # Le nom de la config correspond au type de données
        )
        
        configurations.append(sync_config)
    
    return configurations

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from typing import Dict, List, Any, Optional, Union
import uuid
import logging
from datetime import datetime, timedelta
from enum import Enum

from backend.database.models.base import BaseModel

logger = logging.getLogger(__name__)


class SyncDirection(str, Enum):
    """Directions de synchronisation."""    IMPORT = "import"  # Depuis la plateforme vers notre système
    EXPORT = "export"  # Depuis notre système vers la plateforme
    BIDIRECTIONAL = "bidirectional"  # Dans les deux sens


class SyncStrategy(str, Enum):
    """Stratégies de synchronisation."""    FULL = "full"  # Synchronisation complète
    INCREMENTAL = "incremental"  # Synchronisation incrémentale
    DELTA = "delta"  # Synchronisation des changements uniquement
    REAL_TIME = "real_time"  # Synchronisation en temps réel


class SyncStatus(str, Enum):
    """Statuts de synchronisation."""    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class SyncConfiguration(BaseModel):
    """    Modèle pour les configurations de synchronisation.
    
    Définit comment et quand synchroniser les données
    entre notre système et les plateformes externes.
    """    
    __tablename__ = "sync_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Identification de la configuration
    config_name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Type de données à synchroniser
    data_type = Column(String(50), nullable=False)  # content, analytics, user_profile, playlist
    content_types = Column(ARRAY(String), default=list)  # audio, video, image, text
    
    # Direction et stratégie
    direction = Column(String(20), nullable=False)
    strategy = Column(String(20), nullable=False)
    
    # Planification
    schedule_type = Column(String(20), nullable=False)  # manual, cron, interval, event
    cron_expression = Column(String(100))  # Pour schedule_type = cron
    interval_minutes = Column(Integer)  # Pour schedule_type = interval
    trigger_events = Column(JSONB, default=list)  # Pour schedule_type = event
    
    # Fenêtre de synchronisation
    sync_window_start = Column(String(5))  # Format HH:MM
    sync_window_end = Column(String(5))  # Format HH:MM
    timezone = Column(String(50), default="UTC")
    
    # Filtres et sélection des données
    data_filters = Column(JSONB, default=dict)
    field_mapping = Column(JSONB, default=dict)
    transformation_rules = Column(JSONB, default=dict)
    
    # Gestion des conflits
    conflict_resolution = Column(String(20), default="latest")  # latest, merge, manual
    duplicate_handling = Column(String(20), default="skip")  # skip, update, create_new
    
    # Limites et performance
    batch_size = Column(Integer, default=100)
    max_retries = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=60)
    rate_limit_per_minute = Column(Integer, default=60)
    
    # Validation et qualité des données
    validation_rules = Column(JSONB, default=dict)
    quality_checks = Column(JSONB, default=dict)
    
    # Statut et monitoring
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime(timezone=True))
    next_sync = Column(DateTime(timezone=True))
    
    # Métriques
    total_syncs = Column(Integer, default=0)
    successful_syncs = Column(Integer, default=0)
    failed_syncs = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SyncConfiguration(name={self.config_name}, platform={self.platform_name})>"
    
    @property
    def success_rate(self) -> float:
        """Calcule le taux de succès des synchronisations."""        if self.total_syncs == 0:
            return 0.0
        return (self.successful_syncs / self.total_syncs) * 100
    
    def should_run_now(self) -> bool:
        """Vérifie si la synchronisation doit être exécutée maintenant."""        if not self.is_active:
            return False
        
        now = datetime.utcnow()
        
        # Vérification de la fenêtre de synchronisation
        if self.sync_window_start and self.sync_window_end:
            current_time = now.strftime("%H:%M")
            if not (self.sync_window_start <= current_time <= self.sync_window_end):
                return False
        
        # Vérification du planning
        if self.schedule_type == "manual":
            return False
        elif self.schedule_type == "interval":
            if not self.last_sync:
                return True
            next_run = self.last_sync + timedelta(minutes=self.interval_minutes)
            return now >= next_run
        elif self.schedule_type == "cron":
            # Logique cron à implémenter avec croniter
            pass
        
        return False
    
    def calculate_next_sync(self) -> Optional[datetime]:
        """Calcule la prochaine date de synchronisation."""        if not self.is_active or self.schedule_type == "manual":
            return None
        
        now = datetime.utcnow()
        
        if self.schedule_type == "interval":
            base_time = self.last_sync or now
            return base_time + timedelta(minutes=self.interval_minutes)
        elif self.schedule_type == "cron" and self.cron_expression:
            # Logique cron à implémenter
            pass
        
        return None


class SyncExecution(BaseModel):
    """    Modèle pour les exécutions de synchronisation.
    
    Stocke les détails et résultats de chaque exécution
    de synchronisation.
    """    
    __tablename__ = "sync_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sync_config_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Identification de l'exécution
    execution_name = Column(String(100))
    trigger_type = Column(String(20), nullable=False)  # scheduled, manual, event
    triggered_by = Column(String(255))  # User ID ou system
    
    # Statut et timing
    status = Column(String(20), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Données synchronisées
    records_processed = Column(Integer, default=0)
    records_successful = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    
    # Données transférées
    data_size_bytes = Column(Integer, default=0)
    
    # Erreurs et warnings
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    error_details = Column(JSONB, default=list)
    
    # Métadonnées de l'exécution
    execution_metadata = Column(JSONB, default=dict)
    sync_checkpoint = Column(String(255))  # Pour reprendre en cas d'échec
    
    # Logs et traces
    log_file_path = Column(String(500))
    trace_id = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SyncExecution(config={self.sync_config_id}, status={self.status})>"
    
    @property
    def success_rate(self) -> float:
        """Calcule le taux de succès de cette exécution."""        if self.records_processed == 0:
            return 0.0
        return (self.records_successful / self.records_processed) * 100
    
    def add_error(self, error_type: str, error_message: str, record_id: str = None):
        """Ajoute une erreur à l'exécution."""        if not self.error_details:
            self.error_details = []
        
        error_entry = {
            "type": error_type,
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            "record_id": record_id
        }
        
        self.error_details.append(error_entry)
        self.error_count = len(self.error_details)
    
    def update_progress(self, processed: int = 0, successful: int = 0, 
                       failed: int = 0, skipped: int = 0):
        """Met à jour les métriques de progression."""        self.records_processed += processed
        self.records_successful += successful
        self.records_failed += failed
        self.records_skipped += skipped


class SyncFieldMapping(BaseModel):
    """    Modèle pour le mapping des champs entre systèmes.
    
    Définit la correspondance entre les champs de notre système
    et ceux des plateformes externes.
    """    
    __tablename__ = "sync_field_mappings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, index=True)
    data_type = Column(String(50), nullable=False)
    
    # Mapping des champs
    internal_field = Column(String(100), nullable=False)
    external_field = Column(String(100), nullable=False)
    
    # Type de données
    field_type = Column(String(20), nullable=False)  # string, integer, boolean, date, array
    
    # Direction du mapping
    direction = Column(String(20), nullable=False)  # import, export, bidirectional
    
    # Transformation
    transformation_function = Column(String(255))
    transformation_parameters = Column(JSONB, default=dict)
    
    # Validation
    is_required = Column(Boolean, default=False)
    validation_rules = Column(JSONB, default=dict)
    default_value = Column(Text)
    
    # Statut
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SyncFieldMapping(platform={self.platform_name}, {self.internal_field}↔{self.external_field})>"


class DataTransformationRule(BaseModel):
    """    Modèle pour les règles de transformation des données.
    
    Définit comment transformer les données lors de la synchronisation
    entre notre système et les plateformes externes.
    """    
    __tablename__ = "data_transformation_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Identification de la règle
    rule_name = Column(String(100), nullable=False)
    rule_category = Column(String(50), nullable=False)  # format, validation, enrichment
    
    # Conditions d'application
    condition_expression = Column(Text)  # Expression pour déterminer quand appliquer
    applies_to_fields = Column(ARRAY(String), default=list)
    
    # Transformation
    transformation_type = Column(String(30), nullable=False)  # function, expression, lookup
    transformation_code = Column(Text, nullable=False)
    
    # Paramètres
    parameters = Column(JSONB, default=dict)
    
    # Ordre d'exécution
    execution_order = Column(Integer, default=0)
    
    # Statut
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<DataTransformationRule(name={self.rule_name}, platform={self.platform_name})>"


class SyncBenchmark(BaseModel):
    """    Modèle pour les benchmarks de synchronisation.
    
    Stocke les métriques de performance pour optimiser
    les configurations de synchronisation.
    """    
    __tablename__ = "sync_benchmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sync_config_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Métriques de performance
    average_throughput_per_minute = Column(Float)
    peak_throughput_per_minute = Column(Float)
    average_response_time_ms = Column(Float)
    
    # Métriques de ressources
    cpu_usage_percent = Column(Float)
    memory_usage_mb = Column(Float)
    network_bandwidth_mbps = Column(Float)
    
    # Métriques de qualité
    error_rate_percent = Column(Float)
    data_quality_score = Column(Float)  # 0-100
    
    # Période de mesure
    measurement_start = Column(DateTime(timezone=True), nullable=False)
    measurement_end = Column(DateTime(timezone=True), nullable=False)
    sample_size = Column(Integer, nullable=False)
    
    # Métadonnées
    benchmark_metadata = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SyncBenchmark(config={self.sync_config_id}, throughput={self.average_throughput_per_minute})>"
    
    @property
    def duration_hours(self) -> float:
        """Calcule la durée de la période de mesure en heures."""        if not self.measurement_end or not self.measurement_start:
            return 0.0
        
        delta = self.measurement_end - self.measurement_start
        return delta.total_seconds() / 3600


# Configuration par défaut des synchronisations par plateforme
DEFAULT_SYNC_CONFIGURATIONS = {
    "spotify": [
        {
            "name": "User Profile Sync",
            "data_type": "user_profile",
            "direction": SyncDirection.IMPORT,
            "strategy": SyncStrategy.INCREMENTAL,
            "schedule_type": "interval",
            "interval_minutes": 60,
            "batch_size": 1
        },
        {
            "name": "Playlist Sync",
            "data_type": "playlist",
            "direction": SyncDirection.BIDIRECTIONAL,
            "strategy": SyncStrategy.INCREMENTAL,
            "schedule_type": "interval",
            "interval_minutes": 30,
            "batch_size": 50
        },
        {
            "name": "Analytics Import",
            "data_type": "analytics",
            "direction": SyncDirection.IMPORT,
            "strategy": SyncStrategy.INCREMENTAL,
            "schedule_type": "cron",
            "cron_expression": "0 2 * * *",  # Tous les jours à 2h du matin
            "batch_size": 1000
        }
    ],
    "youtube": [
        {
            "name": "Video Upload Sync",
            "data_type": "content",
            "content_types": ["video"],
            "direction": SyncDirection.EXPORT,
            "strategy": SyncStrategy.REAL_TIME,
            "schedule_type": "event",
            "trigger_events": ["content.created", "content.updated"],
            "batch_size": 1
        },
        {
            "name": "Channel Analytics",
            "data_type": "analytics",
            "direction": SyncDirection.IMPORT,
            "strategy": SyncStrategy.INCREMENTAL,
            "schedule_type": "cron",
            "cron_expression": "0 3 * * *",
            "batch_size": 100
        }
    ],
    "instagram": [
        {
            "name": "Content Sync",
            "data_type": "content",
            "content_types": ["image", "video"],
            "direction": SyncDirection.BIDIRECTIONAL,
            "strategy": SyncStrategy.INCREMENTAL,
            "schedule_type": "interval",
            "interval_minutes": 15,
            "batch_size": 20
        }
    ]
}


def create_default_sync_configurations(platform_name: str, user_id: str) -> List[SyncConfiguration]:
    """    Crée les configurations de synchronisation par défaut pour une plateforme.
    
    Args:
        platform_name: Nom de la plateforme
        user_id: ID de l'utilisateur
    
    Returns:
        List[SyncConfiguration]: Liste des configurations créées
    """    if platform_name not in DEFAULT_SYNC_CONFIGURATIONS:
        return []
    
    configurations = []
    platform_configs = DEFAULT_SYNC_CONFIGURATIONS[platform_name]
    
    for config_data in platform_configs:
        config = SyncConfiguration(
            user_id=user_id,
            platform_name=platform_name,
            config_name=config_data["name"],
            data_type=config_data["data_type"],
            content_types=config_data.get("content_types", []),
            direction=config_data["direction"],
            strategy=config_data["strategy"],
            schedule_type=config_data["schedule_type"],
            cron_expression=config_data.get("cron_expression"),
            interval_minutes=config_data.get("interval_minutes"),
            trigger_events=config_data.get("trigger_events", []),
            batch_size=config_data["batch_size"]
        )
        
        configurations.append(config)
    
    return configurations


# Index pour optimisation des performances
from sqlalchemy import Index

sync_configuration_user_platform_idx = Index(
    'idx_sync_configurations_user_platform',
    SyncConfiguration.user_id,
    SyncConfiguration.platform_name
)

sync_execution_config_status_idx = Index(
    'idx_sync_executions_config_status',
    SyncExecution.sync_config_id,
    SyncExecution.status
)

sync_field_mapping_platform_type_idx = Index(
    'idx_sync_field_mappings_platform_type',
    SyncFieldMapping.platform_name,
    SyncFieldMapping.data_type
)
