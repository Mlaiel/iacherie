"""
⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Data Sync Template for iacherie Creator Economy Platform
Enterprise data synchronization service with real-time CDC, conflict resolution and multi-source support
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, validator
import redis.asyncio as redis
import logging
from prometheus_client import Counter, Histogram, Gauge


class SyncDirection(str, Enum):
    BIDIRECTIONAL = "bidirectional"
    SOURCE_TO_TARGET = "source_to_target"
    TARGET_TO_SOURCE = "target_to_source"


class ConflictResolution(str, Enum):
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL = "manual"
    MERGE = "merge"
    CUSTOM = "custom"


class SyncStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"
    INITIALIZING = "initializing"


class ChangeType(str, Enum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    SCHEMA_CHANGE = "schema_change"


@dataclass
class DataSyncConfig:
    """Configuration du service de synchronisation"""
    # Performance settings
    batch_size: int = 1000
    max_concurrent_syncs: int = 10
    sync_interval_seconds: int = 30
    initial_sync_chunk_size: int = 10000
    
    # Change tracking
    enable_cdc: bool = True  # Change Data Capture
    change_retention_hours: int = 72
    track_schema_changes: bool = True
    
    # Conflict resolution
    default_conflict_resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS
    enable_conflict_logging: bool = True
    
    # Data validation
    enable_data_validation: bool = True
    validate_schema_compatibility: bool = True
    enable_checksum_validation: bool = True
    
    # Performance optimization
    enable_compression: bool = True
    enable_parallel_processing: bool = True
    connection_pool_size: int = 20
    
    # Monitoring
    enable_metrics: bool = True
    alert_on_lag: bool = True
    max_lag_minutes: int = 30
    
    # Security
    encrypt_data_in_transit: bool = True
    mask_sensitive_fields: bool = True
    sensitive_field_patterns: List[str] = field(default_factory=lambda: [
        "password", "ssn", "credit_card", "email"
    ])


class DataSource(BaseModel):
    """Source de données"""
    source_id: str
    name: str
    type: str  # postgresql, mysql, mongodb, api, etc.
    connection_string: str
    connection_params: Dict[str, Any] = {}
    
    # Sync configuration
    tables_to_sync: List[str] = []
    excluded_tables: List[str] = []
    sync_filters: Dict[str, str] = {}  # table -> WHERE clause
    
    # Change tracking
    last_sync_timestamp: Optional[datetime] = None
    change_log_table: Optional[str] = None
    
    # Status
    is_active: bool = True
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"


class SyncRule(BaseModel):
    """Règle de synchronisation"""
    rule_id: str
    name: str
    source_id: str
    target_id: str
    
    # Configuration
    direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    conflict_resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS
    
    # Mapping
    table_mappings: Dict[str, str] = {}  # source_table -> target_table
    field_mappings: Dict[str, Dict[str, str]] = {}  # table -> {source_field -> target_field}
    
    # Filtering and transformation
    sync_filters: Dict[str, str] = {}
    field_transformations: Dict[str, str] = {}  # field -> transformation_function
    
    # Scheduling
    sync_schedule: str = "continuous"  # continuous, hourly, daily, etc.
    is_active: bool = True
    
    # Status
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    sync_status: SyncStatus = SyncStatus.INITIALIZING
    
    # Statistics
    records_synced: int = 0
    errors_count: int = 0
    last_error: Optional[str] = None


class ChangeRecord(BaseModel):
    """Enregistrement de changement"""
    change_id: str
    source_id: str
    table_name: str
    change_type: ChangeType
    primary_key: Dict[str, Any]
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    timestamp: datetime
    transaction_id: Optional[str] = None
    
    # Sync tracking
    sync_status: str = "pending"
    synced_to: List[str] = []
    conflicts: List[Dict[str, Any]] = []


class SyncConflict(BaseModel):
    """Conflit de synchronisation"""
    conflict_id: str
    rule_id: str
    table_name: str
    primary_key: Dict[str, Any]
    
    # Conflict details
    source_values: Dict[str, Any]
    target_values: Dict[str, Any]
    conflict_fields: List[str]
    
    # Timestamps
    source_timestamp: datetime
    target_timestamp: datetime
    detected_at: datetime
    
    # Resolution
    resolution_strategy: ConflictResolution
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_values: Optional[Dict[str, Any]] = None


class DataSyncTemplate:
    """
    Template de service de synchronisation de données pour iacherie
    
    Fonctionnalités:
    - Change Data Capture (CDC) en temps réel
    - Synchronisation multi-directionnelle
    - Résolution automatique de conflits
    - Transformation de données à la volée
    - Monitoring et alerting avancés
    - Support multi-sources (SQL, NoSQL, API)
    - Performance optimization
    - Data validation et integrity checking
    """
    
    def __init__(self, config: DataSyncConfig = None):
        self.config = config or DataSyncConfig()
        self.app = FastAPI(
            title="iacherie Data Sync Service",
            description="Enterprise data synchronization with real-time CDC",
            version="1.0.0"
        )
        
        # Redis pour coordination et cache
        self.redis = redis.Redis(host='localhost', port=6379, db=12, decode_responses=True)
        
        # Configuration storage
        self.data_sources: Dict[str, DataSource] = {}
        self.sync_rules: Dict[str, SyncRule] = {}
        self.active_syncs: Dict[str, Dict[str, Any]] = {}
        
        # Change tracking
        self.pending_changes: Dict[str, List[ChangeRecord]] = {}
        self.conflicts: Dict[str, SyncConflict] = {}
        
        # Connection pools
        self.connection_pools: Dict[str, Any] = {}
        
        # Métriques Prometheus
        self.sync_operations = Counter('data_sync_operations_total', ['source', 'target', 'status'])
        self.records_processed = Counter('data_sync_records_total', ['rule_id', 'change_type'])
        self.sync_lag = Histogram('data_sync_lag_seconds', ['rule_id'])
        self.active_sync_rules = Gauge('data_sync_active_rules_total')
        self.conflicts_total = Gauge('data_sync_conflicts_total', ['rule_id'])
        self.sync_duration = Histogram('data_sync_duration_seconds', ['rule_id'])
        
        # Setup
        self._setup_routes()
        self._start_sync_engine()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _start_sync_engine(self):
        """Démarrer le moteur de synchronisation"""
        # CDC monitoring
        asyncio.create_task(self._cdc_monitor_loop())
        
        # Sync execution
        asyncio.create_task(self._sync_execution_loop())
        
        # Conflict resolution
        asyncio.create_task(self._conflict_resolution_loop())
        
        # Health monitoring
        asyncio.create_task(self._health_monitor_loop())

    def _setup_routes(self):
        """Configuration des routes du service"""
        
        @self.app.post("/sync/sources")
        async def create_data_source(source_data: Dict[str, Any]):
            """Créer une source de données"""
            try:
                source = DataSource(**source_data)
                
                # Test de connexion
                await self._test_source_connection(source)
                
                # Stocker la source
                self.data_sources[source.source_id] = source
                await self._persist_data_source(source)
                
                # Initialiser pool de connexions
                await self._initialize_connection_pool(source)
                
                self.logger.info(f"Created data source: {source.source_id}")
                return {"success": True, "source_id": source.source_id}
                
            except Exception as e:
                self.logger.error(f"Failed to create data source: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Source creation failed: {str(e)}")

        @self.app.post("/sync/rules")
        async def create_sync_rule(rule_data: Dict[str, Any]):
            """Créer une règle de synchronisation"""
            try:
                rule = SyncRule(**rule_data)
                
                # Valider que les sources existent
                if rule.source_id not in self.data_sources:
                    raise HTTPException(status_code=400, detail="Source not found")
                if rule.target_id not in self.data_sources:
                    raise HTTPException(status_code=400, detail="Target not found")
                
                # Stocker la règle
                self.sync_rules[rule.rule_id] = rule
                await self._persist_sync_rule(rule)
                
                # Planifier prochaine sync
                if rule.is_active:
                    await self._schedule_next_sync(rule)
                
                self.active_sync_rules.inc()
                self.logger.info(f"Created sync rule: {rule.rule_id}")
                
                return {"success": True, "rule_id": rule.rule_id}
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to create sync rule: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Rule creation failed: {str(e)}")

        @self.app.post("/sync/execute/{rule_id}")
        async def execute_sync_rule(rule_id: str, background_tasks: BackgroundTasks):
            """Exécuter une règle de synchronisation"""
            try:
                if rule_id not in self.sync_rules:
                    raise HTTPException(status_code=404, detail="Sync rule not found")
                
                rule = self.sync_rules[rule_id]
                
                # Vérifier si déjà en cours
                if rule_id in self.active_syncs:
                    return {"message": "Sync already in progress", "rule_id": rule_id}
                
                # Marquer comme actif
                self.active_syncs[rule_id] = {
                    "started_at": datetime.utcnow(),
                    "status": "running"
                }
                
                # Exécuter en arrière-plan
                background_tasks.add_task(self._execute_sync_rule, rule)
                
                return {"message": "Sync started", "rule_id": rule_id}
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to execute sync rule: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Sync execution failed: {str(e)}")

        @self.app.get("/sync/status/{rule_id}")
        async def get_sync_status(rule_id: str):
            """Récupérer le statut d'une règle de synchronisation"""
            try:
                if rule_id not in self.sync_rules:
                    raise HTTPException(status_code=404, detail="Sync rule not found")
                
                rule = self.sync_rules[rule_id]
                
                # Statut actuel
                current_sync = self.active_syncs.get(rule_id)
                
                # Statistiques récentes
                recent_stats = await self._get_sync_statistics(rule_id)
                
                return {
                    "rule_id": rule_id,
                    "status": rule.sync_status.value,
                    "last_sync": rule.last_sync.isoformat() if rule.last_sync else None,
                    "next_sync": rule.next_sync.isoformat() if rule.next_sync else None,
                    "current_sync": current_sync,
                    "statistics": recent_stats,
                    "conflicts": len([c for c in self.conflicts.values() if c.rule_id == rule_id and not c.resolved])
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get sync status: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve status")

        @self.app.get("/sync/conflicts")
        async def get_conflicts(rule_id: Optional[str] = None, resolved: bool = False):
            """Récupérer les conflits de synchronisation"""
            try:
                conflicts = []
                
                for conflict in self.conflicts.values():
                    if rule_id and conflict.rule_id != rule_id:
                        continue
                    if conflict.resolved != resolved:
                        continue
                    
                    conflicts.append(conflict.dict())
                
                return {"conflicts": conflicts}
                
            except Exception as e:
                self.logger.error(f"Failed to get conflicts: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve conflicts")

        @self.app.post("/sync/conflicts/{conflict_id}/resolve")
        async def resolve_conflict(conflict_id: str, resolution_data: Dict[str, Any]):
            """Résoudre un conflit manuellement"""
            try:
                if conflict_id not in self.conflicts:
                    raise HTTPException(status_code=404, detail="Conflict not found")
                
                conflict = self.conflicts[conflict_id]
                
                # Appliquer la résolution
                success = await self._resolve_conflict_manually(conflict, resolution_data)
                
                if success:
                    conflict.resolved = True
                    conflict.resolved_at = datetime.utcnow()
                    conflict.resolved_values = resolution_data.get("resolved_values")
                    
                    await self._persist_conflict_resolution(conflict)
                
                return {"success": success, "conflict_id": conflict_id}
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to resolve conflict: {str(e)}")
                raise HTTPException(status_code=500, detail="Conflict resolution failed")

        @self.app.get("/sync/rules")
        async def list_sync_rules():
            """Lister toutes les règles de synchronisation"""
            try:
                rules = []
                for rule in self.sync_rules.values():
                    rule_info = rule.dict()
                    rule_info["active_sync"] = rule.rule_id in self.active_syncs
                    rules.append(rule_info)
                
                return {"rules": rules}
                
            except Exception as e:
                self.logger.error(f"Failed to list sync rules: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to list rules")

        @self.app.put("/sync/rules/{rule_id}/toggle")
        async def toggle_sync_rule(rule_id: str):
            """Activer/désactiver une règle de synchronisation"""
            try:
                if rule_id not in self.sync_rules:
                    raise HTTPException(status_code=404, detail="Sync rule not found")
                
                rule = self.sync_rules[rule_id]
                rule.is_active = not rule.is_active
                
                if rule.is_active:
                    rule.sync_status = SyncStatus.ACTIVE
                    await self._schedule_next_sync(rule)
                    self.active_sync_rules.inc()
                else:
                    rule.sync_status = SyncStatus.STOPPED
                    # Arrêter sync en cours si applicable
                    if rule_id in self.active_syncs:
                        del self.active_syncs[rule_id]
                    self.active_sync_rules.dec()
                
                await self._persist_sync_rule(rule)
                
                return {
                    "rule_id": rule_id,
                    "is_active": rule.is_active,
                    "status": rule.sync_status.value
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to toggle sync rule: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to toggle rule")

        @self.app.get("/sync/health")
        async def get_sync_health():
            """Health check du service de synchronisation"""
            try:
                # Test Redis
                redis_health = "healthy"
                try:
                    await self.redis.ping()
                except Exception as e:
                    redis_health = f"unhealthy: {str(e)}"
                
                # Test sources
                source_health = {}
                for source_id, source in self.data_sources.items():
                    try:
                        await self._test_source_connection(source)
                        source_health[source_id] = "healthy"
                    except Exception as e:
                        source_health[source_id] = f"unhealthy: {str(e)}"
                
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "redis": redis_health,
                    "sources": source_health,
                    "active_rules": len([r for r in self.sync_rules.values() if r.is_active]),
                    "active_syncs": len(self.active_syncs),
                    "unresolved_conflicts": len([c for c in self.conflicts.values() if not c.resolved])
                }
                
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def _cdc_monitor_loop(self):
        """Boucle de monitoring CDC"""
        while True:
            try:
                if self.config.enable_cdc:
                    # Surveiller les changements sur chaque source
                    for source_id, source in self.data_sources.items():
                        if source.is_active:
                            await self._capture_changes(source)
                
                await asyncio.sleep(self.config.sync_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"CDC monitor error: {str(e)}")
                await asyncio.sleep(60)

    async def _sync_execution_loop(self):
        """Boucle d'exécution des synchronisations"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                # Vérifier les règles qui doivent être exécutées
                for rule_id, rule in self.sync_rules.items():
                    if (rule.is_active and 
                        rule.next_sync and 
                        current_time >= rule.next_sync and
                        rule_id not in self.active_syncs):
                        
                        # Limiter le nombre de syncs simultanées
                        if len(self.active_syncs) >= self.config.max_concurrent_syncs:
                            continue
                        
                        self.logger.info(f"Starting scheduled sync: {rule_id}")
                        
                        # Marquer comme actif
                        self.active_syncs[rule_id] = {
                            "started_at": current_time,
                            "status": "running"
                        }
                        
                        # Exécuter en arrière-plan
                        asyncio.create_task(self._execute_sync_rule(rule))
                
                await asyncio.sleep(30)  # Vérifier toutes les 30 secondes
                
            except Exception as e:
                self.logger.error(f"Sync execution loop error: {str(e)}")
                await asyncio.sleep(60)

    async def _execute_sync_rule(self, rule: SyncRule):
        """Exécuter une règle de synchronisation"""
        start_time = time.time()
        
        try:
            rule.sync_status = SyncStatus.ACTIVE
            
            # Récupérer les sources
            source = self.data_sources[rule.source_id]
            target = self.data_sources[rule.target_id]
            
            # Récupérer les changements pending
            changes = await self._get_pending_changes(rule)
            
            if changes:
                self.logger.info(f"Syncing {len(changes)} changes for rule {rule.rule_id}")
                
                # Traiter par batch
                for i in range(0, len(changes), self.config.batch_size):
                    batch = changes[i:i + self.config.batch_size]
                    await self._process_change_batch(rule, batch)
                
                # Mettre à jour statistiques
                rule.records_synced += len(changes)
                rule.last_sync = datetime.utcnow()
            
            # Planifier prochaine sync
            await self._schedule_next_sync(rule)
            
            # Métriques
            duration = time.time() - start_time
            self.sync_duration.labels(rule_id=rule.rule_id).observe(duration)
            
            self.sync_operations.labels(
                source=rule.source_id,
                target=rule.target_id,
                status="success"
            ).inc()
            
            self.logger.info(f"Sync rule {rule.rule_id} completed successfully in {duration:.2f}s")
            
        except Exception as e:
            rule.sync_status = SyncStatus.ERROR
            rule.last_error = str(e)
            rule.errors_count += 1
            
            self.sync_operations.labels(
                source=rule.source_id,
                target=rule.target_id,
                status="error"
            ).inc()
            
            self.logger.error(f"Sync rule {rule.rule_id} failed: {str(e)}")
            
        finally:
            # Supprimer des syncs actifs
            if rule.rule_id in self.active_syncs:
                del self.active_syncs[rule.rule_id]
            
            # Persister la règle mise à jour
            await self._persist_sync_rule(rule)

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


def create_data_sync_service(config: DataSyncConfig = None) -> FastAPI:
    """
    Factory pour créer service de synchronisation de données
    
    Args:
        config: Configuration personnalisée
        
    Returns:
        FastAPI: Instance du service configuré
    """
    sync_service = DataSyncTemplate(config)
    return sync_service.get_app()


if __name__ == "__main__":
    import uvicorn
    
    config = DataSyncConfig(
        enable_cdc=True,
        batch_size=1000,
        enable_conflict_logging=True,
        default_conflict_resolution=ConflictResolution.LAST_WRITE_WINS
    )
    
    app = create_data_sync_service(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )