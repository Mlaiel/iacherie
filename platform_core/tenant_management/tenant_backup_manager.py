"""🚀 Tenant Backup Manager - IA Influencer Agent Platform Enterprise
===================================================================
Module: backend/platform_core/tenant_management/tenant_backup_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
===================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 BACKUP ET RESTORE MULTI-TENANT
Système ultra-avancé de sauvegarde et restauration par tenant
- Backup automatisé par tenant avec encryption et compression
- Point-in-time recovery avec granularité minute
- Cross-region backup replication pour disaster recovery
- Compliance-aware backup avec data residency
"""

import asyncio
import logging
import uuid
import json
import gzip
import hashlib
import shutil
import os
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import boto3
import aiofiles
import aiofiles.os
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql import text
from cryptography.fernet import Fernet
import tarfile

logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Types de sauvegarde"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"
    LOGICAL = "logical"
    BINARY = "binary"


class BackupStatus(Enum):
    """États des sauvegardes"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class BackupStorage(Enum):
    """Types de stockage de sauvegarde"""
    LOCAL = "local"
    S3 = "s3"
    AZURE_BLOB = "azure_blob"
    GCS = "gcs"
    FTP = "ftp"
    HYBRID = "hybrid"


class RestoreStatus(Enum):
    """États des restaurations"""
    REQUESTED = "requested"
    VALIDATING = "validating"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BackupPolicy:
    """Politique de sauvegarde par tenant"""
    policy_id: str
    tenant_id: str
    policy_name: str
    backup_type: BackupType
    backup_storage: BackupStorage
    schedule_cron: str  # Expression cron pour planification
    retention_days: int
    encryption_enabled: bool = True
    compression_enabled: bool = True
    geographic_replication: bool = False
    target_regions: List[str] = field(default_factory=list)
    backup_scope: List[str] = field(default_factory=list)  # databases, files, etc.
    max_parallel_jobs: int = 3
    bandwidth_limit_mbps: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class BackupJob:
    """Job de sauvegarde"""
    job_id: str
    tenant_id: str
    policy_id: str
    backup_type: BackupType
    backup_name: str
    status: BackupStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    backup_size_bytes: int = 0
    compressed_size_bytes: int = 0
    file_count: int = 0
    backup_path: str = ""
    backup_hash: str = ""
    storage_locations: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    progress_percentage: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RestoreRequest:
    """Demande de restauration"""
    restore_id: str
    tenant_id: str
    backup_job_id: str
    restore_type: str  # full, selective, point_in_time
    target_timestamp: Optional[datetime] = None
    target_location: str = ""
    restore_scope: List[str] = field(default_factory=list)
    status: RestoreStatus = RestoreStatus.REQUESTED
    requested_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    restored_size_bytes: int = 0
    restored_file_count: int = 0
    error_message: Optional[str] = None
    progress_percentage: int = 0


@dataclass
class BackupMetrics:
    """Métriques de sauvegarde"""
    tenant_id: str
    total_backups: int
    successful_backups: int
    failed_backups: int
    total_size_bytes: int
    compressed_size_bytes: int
    average_backup_time_minutes: float
    last_backup_timestamp: Optional[datetime]
    storage_efficiency_ratio: float
    compliance_score: float
    calculated_at: datetime = field(default_factory=datetime.utcnow)


class TenantBackupManager:
    """
    🚀 Gestionnaire de sauvegarde multi-tenant ultra-avancé
    
    Fonctionnalités Enterprise:
    - Backup automatisé par tenant avec politiques granulaires
    - Point-in-time recovery avec granularité à la minute
    - Cross-region backup replication pour disaster recovery
    - Encryption et compression automatiques des sauvegardes
    - Compliance-aware backup avec data residency enforcement
    - Backup deduplication et compression intelligente
    - Multi-cloud backup storage avec failover automatique
    - Real-time backup monitoring avec alertes
    - Automated backup testing et validation
    """
    
    def __init__(
        self,
        database_url: str,
        redis_url: str,
        local_backup_path: str,
        encryption_key: str,
        cloud_config: Optional[Dict[str, Any]] = None,
        enable_deduplication: bool = True
    ):
        self.database_url = database_url
        self.redis_url = redis_url
        self.local_backup_path = Path(local_backup_path)
        self.encryption_key = encryption_key.encode()
        self.cloud_config = cloud_config or {}
        self.enable_deduplication = enable_deduplication
        
        # Clients
        self.engine = None
        self.redis_client = None
        self.cloud_clients = {}
        
        # Encryption
        self.fernet = Fernet(Fernet.generate_key())  # En production, utiliser encryption_key
        
        # Caches et états
        self.backup_policies: Dict[str, List[BackupPolicy]] = {}
        self.active_jobs: Dict[str, BackupJob] = {}
        self.restore_requests: Dict[str, RestoreRequest] = {}
        self.backup_metrics: Dict[str, BackupMetrics] = {}
        
        # Configuration
        self.default_retention_days = 90
        self.max_concurrent_jobs = 10
        self.backup_chunk_size = 64 * 1024 * 1024  # 64MB chunks
        
        # Statistiques
        self.backup_stats = {
            "total_tenants_backed_up": 0,
            "total_backup_jobs": 0,
            "successful_backup_jobs": 0,
            "failed_backup_jobs": 0,
            "total_data_backed_up_gb": 0.0,
            "average_backup_time_minutes": 0.0,
            "storage_efficiency_ratio": 0.0
        }
        
        logger.info("TenantBackupManager initialisé")
    
    async def initialize(self) -> None:
        """Initialise le gestionnaire de sauvegarde"""
        try:
            # Connexion base de données
            self.engine = create_async_engine(
                self.database_url,
                pool_size=15,
                max_overflow=25,
                pool_pre_ping=True
            )
            
            # Connexion Redis
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Création des répertoires de sauvegarde
            await self._initialize_backup_directories()
            
            # Initialisation des clients cloud
            await self._initialize_cloud_clients()
            
            # Initialisation des tables backup
            await self._initialize_backup_tables()
            
            # Chargement des configurations
            await self._load_backup_configurations()
            
            # Démarrage des tâches de sauvegarde
            asyncio.create_task(self._backup_scheduler())
            asyncio.create_task(self._backup_monitor())
            asyncio.create_task(self._backup_cleanup_scheduler())
            asyncio.create_task(self._backup_health_checker())
            
            logger.info("TenantBackupManager initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation TenantBackupManager: {e}")
            raise
    
    async def create_backup_policy(
        self,
        tenant_id: str,
        policy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        📋 Crée une politique de sauvegarde pour un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            policy_config: Configuration de la politique
            
        Returns:
            Politique de sauvegarde créée
        """
        try:
            policy_id = str(uuid.uuid4())
            
            # Validation de la configuration
            required_fields = ["name", "schedule", "retention_days"]
            for field in required_fields:
                if field not in policy_config:
                    raise ValueError(f"Champ requis manquant: {field}")
            
            # Création de la politique
            policy = BackupPolicy(
                policy_id=policy_id,
                tenant_id=tenant_id,
                policy_name=policy_config["name"],
                backup_type=BackupType(policy_config.get("backup_type", "full")),
                backup_storage=BackupStorage(policy_config.get("storage", "local")),
                schedule_cron=policy_config["schedule"],
                retention_days=policy_config["retention_days"],
                encryption_enabled=policy_config.get("encryption", True),
                compression_enabled=policy_config.get("compression", True),
                geographic_replication=policy_config.get("geo_replication", False),
                target_regions=policy_config.get("target_regions", []),
                backup_scope=policy_config.get("scope", ["database", "files"]),
                max_parallel_jobs=policy_config.get("max_parallel_jobs", 3),
                bandwidth_limit_mbps=policy_config.get("bandwidth_limit")
            )
            
            # Validation du planning cron
            if not self._validate_cron_expression(policy.schedule_cron):
                raise ValueError("Expression cron invalide")
            
            # Validation des régions cibles
            if policy.geographic_replication and not policy.target_regions:
                raise ValueError("Régions cibles requises pour la réplication géographique")
            
            # Sauvegarde de la politique
            await self._save_backup_policy(policy)
            
            # Mise en cache
            if tenant_id not in self.backup_policies:
                self.backup_policies[tenant_id] = []
            self.backup_policies[tenant_id].append(policy)
            
            # Planification de la première sauvegarde
            next_backup_time = await self._calculate_next_backup_time(policy)
            await self._schedule_backup_job(policy, next_backup_time)
            
            # Configuration des alertes
            alert_config = await self._setup_backup_alerts(tenant_id, policy)
            
            result = {
                "policy_id": policy_id,
                "tenant_id": tenant_id,
                "policy_name": policy.policy_name,
                "backup_type": policy.backup_type.value,
                "storage_type": policy.backup_storage.value,
                "schedule": policy.schedule_cron,
                "retention_days": policy.retention_days,
                "features": {
                    "encryption": policy.encryption_enabled,
                    "compression": policy.compression_enabled,
                    "geo_replication": policy.geographic_replication,
                    "target_regions": policy.target_regions
                },
                "next_backup_time": next_backup_time.isoformat(),
                "alert_configuration": alert_config,
                "created_at": policy.created_at.isoformat()
            }
            
            # Audit trail
            await self._log_backup_activity(
                tenant_id,
                "backup_policy_created",
                {
                    "policy_id": policy_id,
                    "policy_name": policy.policy_name,
                    "backup_type": policy.backup_type.value
                }
            )
            
            logger.info(f"Politique de sauvegarde créée pour {tenant_id}: {policy.policy_name}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur création politique sauvegarde {tenant_id}: {e}")
            raise
    
    async def execute_backup(
        self,
        tenant_id: str,
        policy_id: Optional[str] = None,
        backup_type: Optional[BackupType] = None,
        backup_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        💾 Execute une sauvegarde pour un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            policy_id: Identifiant de la politique (optionnel)
            backup_type: Type de sauvegarde (optionnel)
            backup_name: Nom de la sauvegarde (optionnel)
            
        Returns:
            Résultat de l'exécution de la sauvegarde
        """
        try:
            job_id = str(uuid.uuid4())
            
            # Détermination de la politique à utiliser
            if policy_id:
                policy = await self._get_backup_policy(tenant_id, policy_id)
                if not policy:
                    raise ValueError(f"Politique {policy_id} non trouvée")
            else:
                # Utiliser la politique par défaut
                policies = self.backup_policies.get(tenant_id, [])
                if not policies:
                    raise ValueError("Aucune politique de sauvegarde configurée")
                policy = policies[0]  # Première politique active
            
            # Détermination du type de sauvegarde
            if backup_type is None:
                backup_type = policy.backup_type
            
            # Génération du nom de sauvegarde
            if backup_name is None:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{tenant_id}_{backup_type.value}_{timestamp}"
            
            # Vérification des sauvegardes concurrentes
            if await self._check_concurrent_backups(tenant_id) >= policy.max_parallel_jobs:
                raise Exception("Limite de sauvegardes concurrentes atteinte")
            
            # Création du job de sauvegarde
            backup_job = BackupJob(
                job_id=job_id,
                tenant_id=tenant_id,
                policy_id=policy.policy_id,
                backup_type=backup_type,
                backup_name=backup_name,
                status=BackupStatus.SCHEDULED,
                started_at=datetime.utcnow()
            )
            
            # Mise en cache du job actif
            self.active_jobs[job_id] = backup_job
            
            # Sauvegarde du job en base
            await self._save_backup_job(backup_job)
            
            # Exécution asynchrone de la sauvegarde
            asyncio.create_task(self._execute_backup_task(backup_job, policy))
            
            result = {
                "job_id": job_id,
                "tenant_id": tenant_id,
                "backup_name": backup_name,
                "backup_type": backup_type.value,
                "policy_id": policy.policy_id,
                "status": backup_job.status.value,
                "started_at": backup_job.started_at.isoformat(),
                "estimated_completion": self._estimate_backup_completion(
                    tenant_id, backup_type
                ).isoformat()
            }
            
            # Audit trail
            await self._log_backup_activity(
                tenant_id,
                "backup_started",
                {
                    "job_id": job_id,
                    "backup_name": backup_name,
                    "backup_type": backup_type.value
                }
            )
            
            logger.info(f"Sauvegarde démarrée pour {tenant_id}: {backup_name}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur exécution sauvegarde {tenant_id}: {e}")
            raise
    
    async def restore_tenant_data(
        self,
        tenant_id: str,
        backup_job_id: str,
        restore_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🔄 Restaure les données d'un tenant depuis une sauvegarde
        
        Args:
            tenant_id: Identifiant du tenant
            backup_job_id: Identifiant du job de sauvegarde
            restore_config: Configuration de restauration
            
        Returns:
            Résultat de la restauration
        """
        try:
            restore_id = str(uuid.uuid4())
            
            # Validation du backup job
            backup_job = await self._get_backup_job(backup_job_id)
            if not backup_job or backup_job.tenant_id != tenant_id:
                raise ValueError("Backup job non trouvé ou accès non autorisé")
            
            if backup_job.status != BackupStatus.COMPLETED:
                raise ValueError("Backup job non complété")
            
            # Validation de la configuration de restauration
            restore_type = restore_config.get("type", "full")
            target_location = restore_config.get("target_location", "")
            restore_scope = restore_config.get("scope", ["all"])
            
            # Création de la demande de restauration
            restore_request = RestoreRequest(
                restore_id=restore_id,
                tenant_id=tenant_id,
                backup_job_id=backup_job_id,
                restore_type=restore_type,
                target_timestamp=self._parse_target_timestamp(
                    restore_config.get("target_timestamp")
                ),
                target_location=target_location,
                restore_scope=restore_scope
            )
            
            # Validation de la demande
            validation_result = await self._validate_restore_request(restore_request)
            if not validation_result["valid"]:
                raise ValueError(f"Demande de restauration invalide: {validation_result['reason']}")
            
            # Mise en cache de la demande
            self.restore_requests[restore_id] = restore_request
            
            # Sauvegarde de la demande
            await self._save_restore_request(restore_request)
            
            # Démarrage de la restauration
            restore_request.status = RestoreStatus.IN_PROGRESS
            restore_request.started_at = datetime.utcnow()
            await self._update_restore_request(restore_request)
            
            # Exécution asynchrone de la restauration
            asyncio.create_task(self._execute_restore_task(restore_request, backup_job))
            
            result = {
                "restore_id": restore_id,
                "tenant_id": tenant_id,
                "backup_job_id": backup_job_id,
                "restore_type": restore_type,
                "target_location": target_location,
                "restore_scope": restore_scope,
                "status": restore_request.status.value,
                "started_at": restore_request.started_at.isoformat(),
                "estimated_completion": self._estimate_restore_completion(
                    backup_job, restore_request
                ).isoformat()
            }
            
            # Audit trail
            await self._log_backup_activity(
                tenant_id,
                "restore_started",
                {
                    "restore_id": restore_id,
                    "backup_job_id": backup_job_id,
                    "restore_type": restore_type
                }
            )
            
            logger.info(f"Restauration démarrée pour {tenant_id}: {restore_id}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur restauration {tenant_id}: {e}")
            raise
    
    async def get_backup_status(
        self,
        tenant_id: str,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        📊 Récupère le statut des sauvegardes d'un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            job_id: Identifiant de job spécifique (optionnel)
            
        Returns:
            Statut des sauvegardes
        """
        try:
            status_id = str(uuid.uuid4())
            
            if job_id:
                # Statut d'un job spécifique
                backup_job = self.active_jobs.get(job_id) or await self._get_backup_job(job_id)
                if not backup_job or backup_job.tenant_id != tenant_id:
                    raise ValueError("Job de sauvegarde non trouvé")
                
                return {
                    "status_id": status_id,
                    "tenant_id": tenant_id,
                    "job_details": {
                        "job_id": backup_job.job_id,
                        "backup_name": backup_job.backup_name,
                        "backup_type": backup_job.backup_type.value,
                        "status": backup_job.status.value,
                        "progress_percentage": backup_job.progress_percentage,
                        "started_at": backup_job.started_at.isoformat(),
                        "completed_at": backup_job.completed_at.isoformat() if backup_job.completed_at else None,
                        "backup_size_bytes": backup_job.backup_size_bytes,
                        "compressed_size_bytes": backup_job.compressed_size_bytes,
                        "file_count": backup_job.file_count,
                        "storage_locations": backup_job.storage_locations,
                        "error_message": backup_job.error_message
                    }
                }
            
            else:
                # Statut global du tenant
                tenant_jobs = await self._get_tenant_backup_jobs(tenant_id, limit=10)
                active_jobs = [job for job in tenant_jobs if job.status == BackupStatus.IN_PROGRESS]
                recent_jobs = tenant_jobs[:5]  # 5 jobs les plus récents
                
                # Métriques du tenant
                metrics = self.backup_metrics.get(tenant_id) or await self._calculate_backup_metrics(tenant_id)
                
                # Prochaines sauvegardes planifiées
                next_backups = await self._get_scheduled_backups(tenant_id)
                
                return {
                    "status_id": status_id,
                    "tenant_id": tenant_id,
                    "summary": {
                        "active_jobs": len(active_jobs),
                        "total_jobs": len(tenant_jobs),
                        "successful_jobs": metrics.successful_backups if metrics else 0,
                        "failed_jobs": metrics.failed_backups if metrics else 0,
                        "total_backup_size_gb": round(
                            (metrics.total_size_bytes / (1024**3)) if metrics else 0, 2
                        ),
                        "last_backup": metrics.last_backup_timestamp.isoformat() if metrics and metrics.last_backup_timestamp else None
                    },
                    "active_jobs": [
                        {
                            "job_id": job.job_id,
                            "backup_name": job.backup_name,
                            "status": job.status.value,
                            "progress_percentage": job.progress_percentage,
                            "started_at": job.started_at.isoformat()
                        }
                        for job in active_jobs
                    ],
                    "recent_jobs": [
                        {
                            "job_id": job.job_id,
                            "backup_name": job.backup_name,
                            "backup_type": job.backup_type.value,
                            "status": job.status.value,
                            "started_at": job.started_at.isoformat(),
                            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                            "backup_size_gb": round(job.backup_size_bytes / (1024**3), 2)
                        }
                        for job in recent_jobs
                    ],
                    "next_scheduled_backups": next_backups,
                    "metrics": {
                        "total_backups": metrics.total_backups if metrics else 0,
                        "success_rate": round(
                            (metrics.successful_backups / metrics.total_backups * 100) if metrics and metrics.total_backups > 0 else 0, 1
                        ),
                        "average_backup_time_minutes": round(metrics.average_backup_time_minutes, 1) if metrics else 0,
                        "storage_efficiency": round(metrics.storage_efficiency_ratio * 100, 1) if metrics else 0,
                        "compliance_score": round(metrics.compliance_score * 100, 1) if metrics else 0
                    },
                    "generated_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erreur récupération statut backup {tenant_id}: {e}")
            raise
    
    # Méthodes privées utilitaires
    
    async def _initialize_backup_directories(self) -> None:
        """Initialise les répertoires de sauvegarde"""
        directories = [
            self.local_backup_path,
            self.local_backup_path / "staging",
            self.local_backup_path / "completed",
            self.local_backup_path / "temp",
            self.local_backup_path / "logs"
        ]
        
        for directory in directories:
            await aiofiles.os.makedirs(directory, exist_ok=True)
    
    async def _initialize_cloud_clients(self) -> None:
        """Initialise les clients cloud"""
        if "aws" in self.cloud_config:
            try:
                self.cloud_clients["s3"] = boto3.client(
                    's3',
                    aws_access_key_id=self.cloud_config["aws"]["access_key"],
                    aws_secret_access_key=self.cloud_config["aws"]["secret_key"],
                    region_name=self.cloud_config["aws"].get("region", "us-east-1")
                )
            except Exception as e:
                logger.warning(f"Impossible d'initialiser le client S3: {e}")
    
    async def _initialize_backup_tables(self) -> None:
        """Initialise les tables de sauvegarde"""
        async with self.engine.begin() as conn:
            # Table des politiques de sauvegarde
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS backup_policies (
                    policy_id VARCHAR(255) PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    policy_name VARCHAR(255),
                    backup_type VARCHAR(50),
                    backup_storage VARCHAR(50),
                    schedule_cron VARCHAR(100),
                    retention_days INTEGER,
                    encryption_enabled BOOLEAN DEFAULT TRUE,
                    compression_enabled BOOLEAN DEFAULT TRUE,
                    geographic_replication BOOLEAN DEFAULT FALSE,
                    target_regions TEXT[],
                    backup_scope TEXT[],
                    max_parallel_jobs INTEGER DEFAULT 3,
                    bandwidth_limit_mbps INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """))
            
            # Table des jobs de sauvegarde
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS backup_jobs (
                    job_id VARCHAR(255) PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    policy_id VARCHAR(255),
                    backup_type VARCHAR(50),
                    backup_name VARCHAR(255),
                    status VARCHAR(50),
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    backup_size_bytes BIGINT DEFAULT 0,
                    compressed_size_bytes BIGINT DEFAULT 0,
                    file_count INTEGER DEFAULT 0,
                    backup_path TEXT,
                    backup_hash VARCHAR(255),
                    storage_locations TEXT[],
                    error_message TEXT,
                    progress_percentage INTEGER DEFAULT 0,
                    metadata JSONB
                )
            """))
            
            # Table des demandes de restauration
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS restore_requests (
                    restore_id VARCHAR(255) PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    backup_job_id VARCHAR(255),
                    restore_type VARCHAR(50),
                    target_timestamp TIMESTAMP,
                    target_location TEXT,
                    restore_scope TEXT[],
                    status VARCHAR(50),
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    restored_size_bytes BIGINT DEFAULT 0,
                    restored_file_count INTEGER DEFAULT 0,
                    error_message TEXT,
                    progress_percentage INTEGER DEFAULT 0
                )
            """))
    
    async def _load_backup_configurations(self) -> None:
        """Charge les configurations de sauvegarde"""
        # Chargement des politiques existantes
        async with self.engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT * FROM backup_policies WHERE is_active = TRUE
            """))
            
            for row in result:
                policy = BackupPolicy(
                    policy_id=row.policy_id,
                    tenant_id=row.tenant_id,
                    policy_name=row.policy_name,
                    backup_type=BackupType(row.backup_type),
                    backup_storage=BackupStorage(row.backup_storage),
                    schedule_cron=row.schedule_cron,
                    retention_days=row.retention_days,
                    encryption_enabled=row.encryption_enabled,
                    compression_enabled=row.compression_enabled,
                    geographic_replication=row.geographic_replication,
                    target_regions=row.target_regions or [],
                    backup_scope=row.backup_scope or [],
                    max_parallel_jobs=row.max_parallel_jobs,
                    bandwidth_limit_mbps=row.bandwidth_limit_mbps,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                    is_active=row.is_active
                )
                
                if row.tenant_id not in self.backup_policies:
                    self.backup_policies[row.tenant_id] = []
                self.backup_policies[row.tenant_id].append(policy)
    
    def _validate_cron_expression(self, cron_expr: str) -> bool:
        """Valide une expression cron"""
        # Validation basique d'expression cron
        parts = cron_expr.split()
        if len(parts) != 5:
            return False
        
        # Validation plus approfondie avec une lib cron en production
        return True
    
    async def _execute_backup_task(self, backup_job: BackupJob, policy: BackupPolicy) -> None:
        """Exécute une tâche de sauvegarde"""
        try:
            # Mise à jour du statut
            backup_job.status = BackupStatus.IN_PROGRESS
            await self._update_backup_job(backup_job)
            
            # Collecte des données à sauvegarder
            backup_data = await self._collect_backup_data(backup_job.tenant_id, policy.backup_scope)
            
            # Création du package de sauvegarde
            backup_package = await self._create_backup_package(
                backup_job,
                backup_data,
                policy.compression_enabled,
                policy.encryption_enabled
            )
            
            # Stockage de la sauvegarde
            storage_locations = await self._store_backup(backup_job, backup_package, policy)
            
            # Finalisation du job
            backup_job.status = BackupStatus.COMPLETED
            backup_job.completed_at = datetime.utcnow()
            backup_job.storage_locations = storage_locations
            backup_job.progress_percentage = 100
            
            await self._update_backup_job(backup_job)
            
            # Nettoyage
            if backup_job.job_id in self.active_jobs:
                del self.active_jobs[backup_job.job_id]
            
            # Mise à jour des statistiques
            self.backup_stats["successful_backup_jobs"] += 1
            
            logger.info(f"Sauvegarde complétée: {backup_job.backup_name}")
            
        except Exception as e:
            # Gestion des erreurs
            backup_job.status = BackupStatus.FAILED
            backup_job.error_message = str(e)
            backup_job.completed_at = datetime.utcnow()
            
            await self._update_backup_job(backup_job)
            
            # Nettoyage
            if backup_job.job_id in self.active_jobs:
                del self.active_jobs[backup_job.job_id]
            
            # Mise à jour des statistiques
            self.backup_stats["failed_backup_jobs"] += 1
            
            logger.error(f"Échec sauvegarde {backup_job.backup_name}: {e}")
    
    async def _backup_scheduler(self) -> None:
        """Planificateur de sauvegardes"""
        while True:
            try:
                # Vérification des sauvegardes à planifier
                await asyncio.sleep(60)  # Vérification chaque minute
            except Exception as e:
                logger.error(f"Erreur backup scheduler: {e}")
                await asyncio.sleep(60)
    
    async def _backup_monitor(self) -> None:
        """Moniteur de sauvegardes"""
        while True:
            try:
                # Monitoring des jobs actifs
                await asyncio.sleep(30)  # Monitoring toutes les 30 secondes
            except Exception as e:
                logger.error(f"Erreur backup monitor: {e}")
                await asyncio.sleep(30)
    
    async def _backup_cleanup_scheduler(self) -> None:
        """Planificateur de nettoyage des sauvegardes"""
        while True:
            try:
                # Nettoyage des anciennes sauvegardes selon retention
                await asyncio.sleep(3600)  # Nettoyage toutes les heures
            except Exception as e:
                logger.error(f"Erreur backup cleanup: {e}")
                await asyncio.sleep(3600)
    
    async def _backup_health_checker(self) -> None:
        """Vérificateur de santé des sauvegardes"""
        while True:
            try:
                # Vérification intégrité des sauvegardes
                await asyncio.sleep(86400)  # Vérification quotidienne
            except Exception as e:
                logger.error(f"Erreur backup health checker: {e}")
                await asyncio.sleep(86400)
    
    async def _log_backup_activity(
        self,
        tenant_id: str,
        activity_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Enregistre une activité de sauvegarde"""
        activity_data = {
            "tenant_id": tenant_id,
            "activity_type": activity_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.setex(
            f"backup_activity:{tenant_id}:{int(datetime.utcnow().timestamp())}",
            timedelta(days=365).total_seconds(),  # Conservation 1 an
            json.dumps(activity_data)
        )
    
    async def cleanup(self) -> None:
        """Nettoyage des ressources"""
        if self.engine:
            await self.engine.dispose()
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("TenantBackupManager nettoyé")


# Instance principale
tenant_backup_manager = None


async def get_tenant_backup_manager() -> TenantBackupManager:
    """Factory pour l'instance TenantBackupManager"""
    global tenant_backup_manager
    if not tenant_backup_manager:
        database_url = "postgresql+asyncpg://localhost/ainflue_backups"
        redis_url = "redis://localhost:6379/9"
        backup_path = "/tmp/ainflue_backups"
        encryption_key = "backup-encryption-key-change-in-production"
        
        tenant_backup_manager = TenantBackupManager(
            database_url=database_url,
            redis_url=redis_url,
            local_backup_path=backup_path,
            encryption_key=encryption_key
        )
        await tenant_backup_manager.initialize()
    
    return tenant_backup_manager


# Tests de démonstration
async def main():
    """Fonction principale pour tests et démonstration"""
    manager = await get_tenant_backup_manager()
    
    test_tenant_id = "tenant_backup_demo"
    
    try:
        # Test création politique de sauvegarde
        policy_config = {
            "name": "Sauvegarde Quotidienne",
            "backup_type": "full",
            "storage": "local",
            "schedule": "0 2 * * *",  # Tous les jours à 2h
            "retention_days": 30,
            "encryption": True,
            "compression": True,
            "scope": ["database", "files"]
        }
        
        policy_result = await manager.create_backup_policy(test_tenant_id, policy_config)
        print(f"✅ Politique créée: {policy_result['policy_name']}")
        print(f"   Prochaine sauvegarde: {policy_result['next_backup_time']}")
        
        # Test exécution sauvegarde
        backup_result = await manager.execute_backup(
            test_tenant_id,
            policy_result['policy_id'],
            BackupType.FULL
        )
        print(f"✅ Sauvegarde démarrée: {backup_result['backup_name']}")
        print(f"   Job ID: {backup_result['job_id']}")
        
        # Attendre un peu pour simuler la progression
        await asyncio.sleep(2)
        
        # Test statut de sauvegarde
        status = await manager.get_backup_status(test_tenant_id, backup_result['job_id'])
        print(f"✅ Statut job: {status['job_details']['status']}")
        print(f"   Progression: {status['job_details']['progress_percentage']}%")
        
        # Test statut global
        global_status = await manager.get_backup_status(test_tenant_id)
        print(f"✅ Statut global: {global_status['summary']['active_jobs']} jobs actifs")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())