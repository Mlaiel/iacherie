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

Backup Service Template for Ainflue Creator Economy Platform
Enterprise backup service with multi-destination, compression, encryption and automated recovery
"""

import asyncio
import gzip
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import secrets
import pickle

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, validator
from cryptography.fernet import Fernet
import boto3
import redis.asyncio as redis
import logging
from prometheus_client import Counter, Histogram, Gauge


class BackupType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupDestination(str, Enum):
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    LOCAL = "local"
    REMOTE_SERVER = "remote_server"
    TAPE = "tape"


class BackupStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    VERIFYING = "verifying"
    VERIFIED = "verified"


class RestoreStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BackupSchedule(str, Enum):
    CONTINUOUS = "continuous"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class BackupConfig:
    """Configuration du service de sauvegarde"""
    # Destinations
    primary_destination: BackupDestination = BackupDestination.AWS_S3
    secondary_destinations: List[BackupDestination] = field(default_factory=list)
    
    # Backup settings
    default_backup_type: BackupType = BackupType.INCREMENTAL
    compression_enabled: bool = True
    encryption_enabled: bool = True
    encryption_key: Optional[str] = None
    
    # Retention policies
    full_backup_retention_days: int = 90
    incremental_backup_retention_days: int = 30
    snapshot_retention_count: int = 10
    
    # Performance
    compression_level: int = 6
    chunk_size_mb: int = 100
    parallel_transfers: int = 4
    bandwidth_limit_mbps: Optional[int] = None
    
    # Scheduling
    default_schedule: BackupSchedule = BackupSchedule.DAILY
    backup_window_start: str = "02:00"
    backup_window_duration_hours: int = 4
    
    # Verification
    enable_backup_verification: bool = True
    verification_sample_percentage: float = 10.0
    
    # Monitoring
    enable_alerts: bool = True
    alert_on_failure: bool = True
    alert_on_long_duration: bool = True
    max_backup_duration_hours: int = 12
    
    # AWS S3 configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_bucket_name: str = "ainflue-backups"
    
    # Database backup settings
    enable_database_backup: bool = True
    database_backup_format: str = "dump"  # dump, export, snapshot
    
    # File system backup settings
    enable_filesystem_backup: bool = True
    excluded_paths: List[str] = field(default_factory=lambda: ["/tmp", "/var/cache"])


class BackupJob(BaseModel):
    """Job de sauvegarde"""
    job_id: str
    name: str
    backup_type: BackupType
    source_paths: List[str]
    destination: BackupDestination
    schedule: BackupSchedule
    
    # Configuration
    compression_enabled: bool = True
    encryption_enabled: bool = True
    verify_backup: bool = True
    
    # Status
    status: BackupStatus = BackupStatus.PENDING
    created_at: datetime
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    
    # Statistics
    success_count: int = 0
    failure_count: int = 0
    total_size_bytes: int = 0
    compressed_size_bytes: int = 0
    
    # Metadata
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class BackupRecord(BaseModel):
    """Enregistrement de sauvegarde"""
    backup_id: str
    job_id: str
    backup_type: BackupType
    destination: BackupDestination
    
    # Timing
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Status and progress
    status: BackupStatus
    progress_percentage: float = 0.0
    current_operation: str = "initializing"
    
    # Data metrics
    total_files: int = 0
    processed_files: int = 0
    total_size_bytes: int = 0
    processed_size_bytes: int = 0
    compressed_size_bytes: int = 0
    
    # Storage info
    storage_path: str
    encryption_used: bool = False
    compression_used: bool = False
    checksum: str
    
    # Verification
    verification_status: str = "pending"
    verification_errors: List[str] = []
    
    # Metadata
    source_paths: List[str]
    metadata: Dict[str, Any] = {}


class RestoreJob(BaseModel):
    """Job de restauration"""
    restore_id: str
    backup_id: str
    destination_path: str
    
    # Options
    restore_type: str = "full"  # full, selective, point_in_time
    overwrite_existing: bool = False
    restore_permissions: bool = True
    
    # Status
    status: RestoreStatus = RestoreStatus.PENDING
    progress_percentage: float = 0.0
    
    # Timing
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    # Statistics
    restored_files: int = 0
    restored_size_bytes: int = 0
    errors: List[str] = []


class BackupServiceTemplate:
    """
    Template de service de sauvegarde enterprise pour Ainflue
    
    Fonctionnalités:
    - Multiple backup types (full, incremental, differential)
    - Multi-destination backup avec réplication
    - Compression et chiffrement avancés
    - Scheduling automatique flexible
    - Backup verification et integrity checking
    - Point-in-time recovery
    - Performance optimization
    - Monitoring et alerting complets
    - Disaster recovery planning
    """
    
    def __init__(self, config: BackupConfig = None):
        self.config = config or BackupConfig()
        self.app = FastAPI(
            title="Ainflue Backup Service",
            description="Enterprise backup service with multi-destination support",
            version="1.0.0"
        )
        
        # Storage clients
        self.s3_client = None
        
        # Redis pour état et coordination
        self.redis = redis.Redis(host='localhost', port=6379, db=11, decode_responses=True)
        
        # Active jobs tracking
        self.active_backup_jobs: Dict[str, BackupRecord] = {}
        self.active_restore_jobs: Dict[str, RestoreJob] = {}
        self.scheduled_jobs: Dict[str, BackupJob] = {}
        
        # Encryption
        self.encryption_key = self.config.encryption_key or Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)
        
        # Métriques Prometheus
        self.backup_operations = Counter('backup_operations_total', ['destination', 'backup_type', 'status'])
        self.restore_operations = Counter('restore_operations_total', ['status'])
        self.backup_duration = Histogram('backup_duration_seconds', ['backup_type', 'destination'])
        self.backup_size = Histogram('backup_size_bytes', ['backup_type'])
        self.active_backups = Gauge('backup_active_jobs_total')
        self.backup_success_rate = Gauge('backup_success_rate_percentage', ['destination'])
        
        # Setup
        asyncio.create_task(self._initialize_storage_clients())
        self._setup_routes()
        self._start_scheduler()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def _initialize_storage_clients(self):
        """Initialisation des clients de stockage"""
        try:
            # AWS S3 pour backups
            if (self.config.primary_destination == BackupDestination.AWS_S3 or 
                BackupDestination.AWS_S3 in self.config.secondary_destinations):
                
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.config.aws_access_key_id,
                    aws_secret_access_key=self.config.aws_secret_access_key,
                    region_name=self.config.aws_region
                )
                
                # Test et création du bucket
                try:
                    self.s3_client.head_bucket(Bucket=self.config.aws_bucket_name)
                except:
                    self.s3_client.create_bucket(Bucket=self.config.aws_bucket_name)
                    self.logger.info(f"Created backup bucket: {self.config.aws_bucket_name}")
            
            self.logger.info("Backup storage clients initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize storage clients: {str(e)}")
            raise

    def _start_scheduler(self):
        """Démarrer le scheduler de sauvegardes"""
        asyncio.create_task(self._backup_scheduler_loop())

    def _setup_routes(self):
        """Configuration des routes du service"""
        
        @self.app.post("/backup/jobs", response_model=BackupJob)
        async def create_backup_job(job_data: Dict[str, Any]):
            """Créer un job de sauvegarde"""
            try:
                job_id = f"job_{int(time.time())}_{secrets.token_hex(4)}"
                
                backup_job = BackupJob(
                    job_id=job_id,
                    name=job_data["name"],
                    backup_type=BackupType(job_data.get("backup_type", self.config.default_backup_type.value)),
                    source_paths=job_data["source_paths"],
                    destination=BackupDestination(job_data.get("destination", self.config.primary_destination.value)),
                    schedule=BackupSchedule(job_data.get("schedule", self.config.default_schedule.value)),
                    compression_enabled=job_data.get("compression_enabled", self.config.compression_enabled),
                    encryption_enabled=job_data.get("encryption_enabled", self.config.encryption_enabled),
                    verify_backup=job_data.get("verify_backup", self.config.enable_backup_verification),
                    created_at=datetime.utcnow(),
                    tags=job_data.get("tags", []),
                    metadata=job_data.get("metadata", {})
                )
                
                # Calculer prochaine exécution
                backup_job.next_run = await self._calculate_next_run(backup_job.schedule)
                
                # Stocker le job
                self.scheduled_jobs[job_id] = backup_job
                await self._persist_backup_job(backup_job)
                
                self.logger.info(f"Created backup job: {job_id}")
                return backup_job
                
            except Exception as e:
                self.logger.error(f"Failed to create backup job: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Job creation failed: {str(e)}")

        @self.app.post("/backup/run/{job_id}")
        async def run_backup_job(job_id: str, background_tasks: BackgroundTasks):
            """Exécuter un job de sauvegarde"""
            try:
                if job_id not in self.scheduled_jobs:
                    raise HTTPException(status_code=404, detail="Backup job not found")
                
                job = self.scheduled_jobs[job_id]
                
                # Créer enregistrement de backup
                backup_id = f"backup_{int(time.time())}_{secrets.token_hex(4)}"
                backup_record = BackupRecord(
                    backup_id=backup_id,
                    job_id=job_id,
                    backup_type=job.backup_type,
                    destination=job.destination,
                    started_at=datetime.utcnow(),
                    status=BackupStatus.PENDING,
                    storage_path=await self._generate_backup_path(backup_id, job),
                    encryption_used=job.encryption_enabled,
                    compression_used=job.compression_enabled,
                    checksum="",
                    source_paths=job.source_paths
                )
                
                # Ajouter aux jobs actifs
                self.active_backup_jobs[backup_id] = backup_record
                
                # Exécuter en arrière-plan
                background_tasks.add_task(self._execute_backup, backup_record)
                
                return {
                    "backup_id": backup_id,
                    "status": "started",
                    "job_id": job_id
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to run backup job: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Backup execution failed: {str(e)}")

        @self.app.get("/backup/status/{backup_id}", response_model=BackupRecord)
        async def get_backup_status(backup_id: str):
            """Récupérer le statut d'une sauvegarde"""
            try:
                # Vérifier jobs actifs
                if backup_id in self.active_backup_jobs:
                    return self.active_backup_jobs[backup_id]
                
                # Chercher dans l'historique
                backup_record = await self._get_backup_record(backup_id)
                if not backup_record:
                    raise HTTPException(status_code=404, detail="Backup not found")
                
                return backup_record
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get backup status: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve backup status")

        @self.app.post("/backup/restore", response_model=RestoreJob)
        async def start_restore(restore_data: Dict[str, Any], background_tasks: BackgroundTasks):
            """Démarrer une restauration"""
            try:
                restore_id = f"restore_{int(time.time())}_{secrets.token_hex(4)}"
                
                restore_job = RestoreJob(
                    restore_id=restore_id,
                    backup_id=restore_data["backup_id"],
                    destination_path=restore_data["destination_path"],
                    restore_type=restore_data.get("restore_type", "full"),
                    overwrite_existing=restore_data.get("overwrite_existing", False),
                    restore_permissions=restore_data.get("restore_permissions", True),
                    started_at=datetime.utcnow()
                )
                
                # Vérifier que le backup existe
                backup_record = await self._get_backup_record(restore_data["backup_id"])
                if not backup_record:
                    raise HTTPException(status_code=404, detail="Backup not found")
                
                # Ajouter aux jobs actifs
                self.active_restore_jobs[restore_id] = restore_job
                
                # Exécuter en arrière-plan
                background_tasks.add_task(self._execute_restore, restore_job, backup_record)
                
                return restore_job
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to start restore: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")

        @self.app.get("/backup/jobs")
        async def list_backup_jobs():
            """Lister tous les jobs de sauvegarde"""
            try:
                jobs = list(self.scheduled_jobs.values())
                return {"jobs": [job.dict() for job in jobs]}
                
            except Exception as e:
                self.logger.error(f"Failed to list backup jobs: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to list jobs")

        @self.app.get("/backup/history")
        async def get_backup_history(
            limit: int = 50,
            job_id: Optional[str] = None,
            days_back: int = 30
        ):
            """Récupérer l'historique des sauvegardes"""
            try:
                history = await self._get_backup_history(limit, job_id, days_back)
                return {"backups": history}
                
            except Exception as e:
                self.logger.error(f"Failed to get backup history: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve history")

        @self.app.delete("/backup/jobs/{job_id}")
        async def delete_backup_job(job_id: str):
            """Supprimer un job de sauvegarde"""
            try:
                if job_id not in self.scheduled_jobs:
                    raise HTTPException(status_code=404, detail="Backup job not found")
                
                # Supprimer du planning
                del self.scheduled_jobs[job_id]
                await self._remove_backup_job(job_id)
                
                return {"success": True, "job_id": job_id}
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to delete backup job: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to delete job")

        @self.app.post("/backup/verify/{backup_id}")
        async def verify_backup(backup_id: str, background_tasks: BackgroundTasks):
            """Vérifier l'intégrité d'une sauvegarde"""
            try:
                backup_record = await self._get_backup_record(backup_id)
                if not backup_record:
                    raise HTTPException(status_code=404, detail="Backup not found")
                
                # Lancer vérification en arrière-plan
                background_tasks.add_task(self._verify_backup_integrity, backup_record)
                
                return {
                    "backup_id": backup_id,
                    "verification_started": True
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to verify backup: {str(e)}")
                raise HTTPException(status_code=500, detail="Verification failed")

        @self.app.get("/backup/health")
        async def get_backup_health():
            """Health check du service de sauvegarde"""
            try:
                # Test storage connections
                storage_health = {}
                
                if self.s3_client:
                    try:
                        self.s3_client.head_bucket(Bucket=self.config.aws_bucket_name)
                        storage_health["s3"] = "healthy"
                    except Exception as e:
                        storage_health["s3"] = f"unhealthy: {str(e)}"
                
                # Redis health
                redis_health = "healthy"
                try:
                    await self.redis.ping()
                except Exception as e:
                    redis_health = f"unhealthy: {str(e)}"
                
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "storage": storage_health,
                    "redis": redis_health,
                    "active_backups": len(self.active_backup_jobs),
                    "active_restores": len(self.active_restore_jobs),
                    "scheduled_jobs": len(self.scheduled_jobs)
                }
                
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def _execute_backup(self, backup_record: BackupRecord):
        """Exécuter une sauvegarde"""
        try:
            # Mettre à jour statut
            backup_record.status = BackupStatus.IN_PROGRESS
            backup_record.current_operation = "scanning_files"
            
            start_time = time.time()
            
            # Scanner les fichiers source
            files_to_backup = await self._scan_source_files(backup_record.source_paths)
            backup_record.total_files = len(files_to_backup)
            backup_record.total_size_bytes = sum(f["size"] for f in files_to_backup)
            
            self.logger.info(f"Backup {backup_record.backup_id}: Found {backup_record.total_files} files ({backup_record.total_size_bytes} bytes)")
            
            # Créer archive
            backup_record.current_operation = "creating_archive"
            archive_path = await self._create_backup_archive(backup_record, files_to_backup)
            
            # Upload vers destination
            backup_record.current_operation = "uploading"
            upload_success = await self._upload_backup(backup_record, archive_path)
            
            if upload_success:
                # Calculer checksum final
                backup_record.checksum = await self._calculate_file_checksum(archive_path)
                
                # Vérification si activée
                if backup_record.job_id in self.scheduled_jobs:
                    job = self.scheduled_jobs[backup_record.job_id]
                    if job.verify_backup:
                        backup_record.status = BackupStatus.VERIFYING
                        await self._verify_backup_integrity(backup_record)
                
                # Finaliser
                backup_record.status = BackupStatus.COMPLETED
                backup_record.completed_at = datetime.utcnow()
                backup_record.duration_seconds = time.time() - start_time
                backup_record.progress_percentage = 100.0
                
                # Métriques
                self.backup_operations.labels(
                    destination=backup_record.destination.value,
                    backup_type=backup_record.backup_type.value,
                    status="success"
                ).inc()
                
                self.backup_duration.labels(
                    backup_type=backup_record.backup_type.value,
                    destination=backup_record.destination.value
                ).observe(backup_record.duration_seconds)
                
                self.backup_size.labels(
                    backup_type=backup_record.backup_type.value
                ).observe(backup_record.total_size_bytes)
                
                self.logger.info(f"Backup {backup_record.backup_id} completed successfully in {backup_record.duration_seconds:.2f}s")
                
            else:
                backup_record.status = BackupStatus.FAILED
                backup_record.completed_at = datetime.utcnow()
                
                self.backup_operations.labels(
                    destination=backup_record.destination.value,
                    backup_type=backup_record.backup_type.value,
                    status="failed"
                ).inc()
                
                self.logger.error(f"Backup {backup_record.backup_id} failed during upload")
            
            # Persister l'enregistrement
            await self._persist_backup_record(backup_record)
            
            # Supprimer des jobs actifs
            if backup_record.backup_id in self.active_backup_jobs:
                del self.active_backup_jobs[backup_record.backup_id]
            
            # Cleanup fichiers temporaires
            await self._cleanup_temporary_files(archive_path)
            
        except Exception as e:
            backup_record.status = BackupStatus.FAILED
            backup_record.completed_at = datetime.utcnow()
            
            self.backup_operations.labels(
                destination=backup_record.destination.value,
                backup_type=backup_record.backup_type.value,
                status="error"
            ).inc()
            
            self.logger.error(f"Backup {backup_record.backup_id} failed: {str(e)}")
            
            # Persister même en cas d'erreur
            await self._persist_backup_record(backup_record)
            
            if backup_record.backup_id in self.active_backup_jobs:
                del self.active_backup_jobs[backup_record.backup_id]

    async def _backup_scheduler_loop(self):
        """Boucle du scheduler de sauvegardes"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                # Vérifier chaque job programmé
                for job_id, job in self.scheduled_jobs.items():
                    if job.next_run and current_time >= job.next_run:
                        # Vérifier si pas déjà en cours
                        if not any(backup.job_id == job_id and backup.status == BackupStatus.IN_PROGRESS 
                                 for backup in self.active_backup_jobs.values()):
                            
                            self.logger.info(f"Starting scheduled backup job: {job_id}")
                            
                            # Créer et démarrer backup
                            backup_id = f"backup_{int(time.time())}_{secrets.token_hex(4)}"
                            backup_record = BackupRecord(
                                backup_id=backup_id,
                                job_id=job_id,
                                backup_type=job.backup_type,
                                destination=job.destination,
                                started_at=datetime.utcnow(),
                                status=BackupStatus.PENDING,
                                storage_path=await self._generate_backup_path(backup_id, job),
                                encryption_used=job.encryption_enabled,
                                compression_used=job.compression_enabled,
                                checksum="",
                                source_paths=job.source_paths
                            )
                            
                            self.active_backup_jobs[backup_id] = backup_record
                            asyncio.create_task(self._execute_backup(backup_record))
                            
                            # Calculer prochaine exécution
                            job.next_run = await self._calculate_next_run(job.schedule)
                            job.last_run = current_time
                            await self._persist_backup_job(job)
                
                # Attendre 60 secondes avant la prochaine vérification
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {str(e)}")
                await asyncio.sleep(60)

    async def _calculate_next_run(self, schedule: BackupSchedule) -> datetime:
        """Calculer la prochaine exécution selon le planning"""
        now = datetime.utcnow()
        
        if schedule == BackupSchedule.CONTINUOUS:
            return now + timedelta(minutes=15)  # Toutes les 15 minutes
        elif schedule == BackupSchedule.HOURLY:
            return now + timedelta(hours=1)
        elif schedule == BackupSchedule.DAILY:
            # Prochaine occurrence à backup_window_start
            next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)  # 02:00 par défaut
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
        elif schedule == BackupSchedule.WEEKLY:
            # Dimanche à backup_window_start
            days_ahead = 6 - now.weekday()  # Dimanche = 6
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            return next_run.replace(hour=2, minute=0, second=0, microsecond=0)
        elif schedule == BackupSchedule.MONTHLY:
            # Premier du mois suivant
            if now.month == 12:
                next_run = now.replace(year=now.year + 1, month=1, day=1, hour=2, minute=0, second=0, microsecond=0)
            else:
                next_run = now.replace(month=now.month + 1, day=1, hour=2, minute=0, second=0, microsecond=0)
            return next_run
        else:
            # Custom - par défaut quotidien
            return now + timedelta(days=1)

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


def create_backup_service(config: BackupConfig = None) -> FastAPI:
    """
    Factory pour créer service de sauvegarde
    
    Args:
        config: Configuration personnalisée
        
    Returns:
        FastAPI: Instance du service configuré
    """
    backup_service = BackupServiceTemplate(config)
    return backup_service.get_app()


if __name__ == "__main__":
    import uvicorn
    
    config = BackupConfig(
        primary_destination=BackupDestination.AWS_S3,
        compression_enabled=True,
        encryption_enabled=True,
        enable_backup_verification=True
    )
    
    app = create_backup_service(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )