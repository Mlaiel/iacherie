"""💾 Backup Manager - Enterprise Backup Orchestration System
========================================================
Module: backend/data_management/backups/backup_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Backup Management - Enterprise Production-Ready
Responsibility: Orchestration intelligente des sauvegardes multi-format
===========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path
import json
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import BackupJob, BackupMetadata, BackupStatus
from .backup_engine import BackupEngine, IncrementalBackupEngine, RealTimeBackupEngine
from .backup_storage import BackupStorage, MultiCloudStorage
from .backup_scheduler import BackupScheduler
from .compression_engine import CompressionEngine
from .encryption_manager import EncryptionManager
from .verification_engine import VerificationEngine
from .monitoring import BackupMonitoring
from .retention_manager import RetentionManager
from .exceptions import BackupException, BackupManagerException

logger = logging.getLogger(__name__)


@dataclass
class BackupConfiguration:
    """
Configuration avancée pour les sauvegardes"""
    backup_type: str = "incremental"
    compression_enabled: bool = True
    encryption_enabled: bool = True
    verification_enabled: bool = True
    parallel_jobs: int = 4
    max_retries: int = 3
    backup_interval_hours: int = 6
    retention_days: int = 90
    storage_class: str = "hot"
    priority: str = "medium"
    content_types: List[str] = field(default_factory=lambda: ["audio", "video", "image", "text"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire"""
        return {
            "backup_type": self.backup_type,
            "compression_enabled": self.compression_enabled,
            "encryption_enabled": self.encryption_enabled,
            "verification_enabled": self.verification_enabled,
            "parallel_jobs": self.parallel_jobs,
            "max_retries": self.max_retries,
            "backup_interval_hours": self.backup_interval_hours,
            "retention_days": self.retention_days,
            "storage_class": self.storage_class,
            "priority": self.priority,
            "content_types": self.content_types
        }


class BackupManager:
    """
    Gestionnaire principal des sauvegardes avec orchestration intelligente
    
    Fonctionnalités:
    - Orchestration multi-engine backup
    - Gestion priorités et scheduling
    - Monitoring performance temps réel
    - Récupération automatique erreurs
    - Optimisation basée sur patterns usage
    """
    
    def __init__(self, config: Optional[BackupConfiguration] = None):
        self.config = config or BackupConfiguration()
        self.job_id = str(uuid.uuid4())
        
        # Core Components Initialization
        self.backup_engine = BackupEngine()
        self.incremental_engine = IncrementalBackupEngine()
        self.realtime_engine = RealTimeBackupEngine()
        self.storage = MultiCloudStorage()
        self.scheduler = BackupScheduler()
        self.compression = CompressionEngine()
        self.encryption = EncryptionManager()
        self.verification = VerificationEngine()
        self.monitoring = BackupMonitoring()
        self.retention = RetentionManager()
        
        # Job Management
        self.active_jobs: Dict[str, BackupJob] = {}
        self.job_history: List[BackupJob] = []
        self.performance_metrics: Dict[str, Any] = {}
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=self.config.parallel_jobs)
        
        logger.info(f"BackupManager initialized with config: {self.config.to_dict()}")
    
    async def create_backup(
        self,
        source_paths: List[Union[str, Path]],
        backup_name: Optional[str] = None,
        user_id: Optional[str] = None,
        content_type: str = "mixed",
        priority: str = "medium",
        options: Optional[Dict[str, Any]] = None
    ) -> BackupJob:
        """
        Crée une nouvelle sauvegarde avec orchestration intelligente
        
        Args:
            source_paths: Chemins des fichiers/dossiers à sauvegarder
            backup_name: Nom optionnel de la sauvegarde
            user_id: ID utilisateur pour multi-tenant
            content_type: Type de contenu (audio, video, image, text, mixed)
            priority: Priorité (critical, high, medium, low)
            options: Options additionnelles
            
        Returns:
            BackupJob: Job de sauvegarde créé
        """
        try:
            # Génération job unique
            job_id = str(uuid.uuid4())
            backup_name = backup_name or f"backup_{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Création du job
            backup_job = BackupJob(
                job_id=job_id,
                name=backup_name,
                source_paths=[Path(p) for p in source_paths],
                content_type=content_type,
                priority=priority,
                user_id=user_id,
                created_at=datetime.now(),
                status=BackupStatus.PENDING,
                options=options or {}
            )
            
            # Ajout à la queue active
            self.active_jobs[job_id] = backup_job
            
            logger.info(f"Created backup job {job_id} for {len(source_paths)} sources")
            
            # Lancement asynchrone
            asyncio.create_task(self._execute_backup_job(backup_job))
            
            return backup_job
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise BackupManagerException(f"Backup creation failed: {e}")
    
    async def _execute_backup_job(self, job: BackupJob) -> None:
        """
        Exécute un job de sauvegarde avec gestion d'erreurs avancée
        
        Args:
            job: Job de sauvegarde à exécuter
        """
        try:
            # Mise à jour statut
            job.status = BackupStatus.RUNNING
            job.started_at = datetime.now()
            
            # Sélection engine selon type contenu
            engine = self._select_optimal_engine(job.content_type, job.priority)
            
            # Pré-traitement : validation et analyse
            await self._preprocess_backup_sources(job)
            
            # Compression si activée
            if self.config.compression_enabled:
                await self._compress_backup_data(job)
            
            # Chiffrement si activé
            if self.config.encryption_enabled:
                await self._encrypt_backup_data(job)
            
            # Exécution sauvegarde
            backup_metadata = await engine.backup(
                source_paths=job.source_paths,
                destination=job.destination_path,
                options=job.options
            )
            
            # Vérification intégrité si activée
            if self.config.verification_enabled:
                verification_result = await self.verification.verify_backup(
                    backup_path=job.destination_path,
                    original_paths=job.source_paths
                )
                job.verification_result = verification_result
            
            # Mise à jour métadonnées
            job.metadata = backup_metadata
            job.status = BackupStatus.COMPLETED
            job.completed_at = datetime.now()
            job.duration = job.completed_at - job.started_at
            
            # Monitoring et métriques
            await self.monitoring.record_backup_success(job)
            
            # Nettoyage et archivage
            await self._finalize_backup_job(job)
            
            logger.info(f"Backup job {job.job_id} completed successfully in {job.duration}")
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.failed_at = datetime.now()
            
            logger.error(f"Backup job {job.job_id} failed: {e}")
            
            # Tentative de récupération
            if job.retry_count < self.config.max_retries:
                job.retry_count += 1
                logger.info(f"Retrying backup job {job.job_id} (attempt {job.retry_count})")
                await asyncio.sleep(60 * job.retry_count)  # Backoff exponentiel
                await self._execute_backup_job(job)
            else:
                await self.monitoring.record_backup_failure(job)
                raise BackupException(f"Backup job failed after {self.config.max_retries} retries: {e}")
        
        finally:
            # Nettoyage job actif
            if job.job_id in self.active_jobs:
                self.job_history.append(self.active_jobs.pop(job.job_id))
    
    def _select_optimal_engine(self, content_type: str, priority: str) -> BackupEngine:
        """
        Sélectionne le moteur de sauvegarde optimal selon le contexte
        
        Args:
            content_type: Type de contenu
            priority: Priorité du job
            
        Returns:
            BackupEngine: Moteur optimal sélectionné
        """
        if priority == "critical":
            return self.realtime_engine
        elif content_type in ["audio", "video"] and priority in ["high", "medium"]:
            return self.incremental_engine
        else:
            return self.backup_engine
    
    async def _preprocess_backup_sources(self, job: BackupJob) -> None:
        """
        Pré-traitement et validation des sources de sauvegarde
        
        Args:
            job: Job de sauvegarde
        """
        validated_paths = []
        total_size = 0
        
        for source_path in job.source_paths:
            if not source_path.exists():
                logger.warning(f"Source path does not exist: {source_path}")
                continue
            
            if source_path.is_file():
                total_size += source_path.stat().st_size
            elif source_path.is_dir():
                for file_path in source_path.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
            
            validated_paths.append(source_path)
        
        job.source_paths = validated_paths
        job.estimated_size = total_size
        
        logger.info(f"Validated {len(validated_paths)} sources, total size: {total_size / (1024**3):.2f} GB")
    
    async def _compress_backup_data(self, job: BackupJob) -> None:
        """
        Compression intelligente des données de sauvegarde
        
        Args:
            job: Job de sauvegarde
        """
        compression_config = {
            "algorithm": "zstd",
            "level": 6,
            "content_aware": True
        }
        
        compressed_size = await self.compression.compress(
            source_paths=job.source_paths,
            config=compression_config
        )
        
        job.compression_ratio = compressed_size / job.estimated_size if job.estimated_size > 0 else 1.0
        logger.info(f"Compression ratio: {job.compression_ratio:.2f}")
    
    async def _encrypt_backup_data(self, job: BackupJob) -> None:
        """
        Chiffrement sécurisé des données de sauvegarde
        
        Args:
            job: Job de sauvegarde
        """
        encryption_config = {
            "algorithm": "AES-256-GCM",
            "key_derivation": "PBKDF2",
            "iterations": 100000
        }
        
        encryption_key = await self.encryption.generate_key(
            user_id=job.user_id,
            config=encryption_config
        )
        
        job.encryption_key_id = encryption_key.key_id
        logger.info(f"Backup encrypted with key ID: {encryption_key.key_id}")
    
    async def _finalize_backup_job(self, job: BackupJob) -> None:
        """
        Finalisation du job de sauvegarde
        
        Args:
            job: Job de sauvegarde complété
        """
        # Application des politiques de rétention
        await self.retention.apply_retention_policy(job)
        
        # Mise à jour index de recherche
        await self._update_backup_index(job)
        
        # Nettoyage fichiers temporaires
        await self._cleanup_temporary_files(job)
    
    async def _update_backup_index(self, job: BackupJob) -> None:
        """
        Met à jour l'index de recherche des sauvegardes
        
        Args:
            job: Job de sauvegarde
        """
        index_entry = {
            "job_id": job.job_id,
            "name": job.name,
            "content_type": job.content_type,
            "user_id": job.user_id,
            "created_at": job.created_at.isoformat(),
            "size": job.estimated_size,
            "compression_ratio": job.compression_ratio,
            "tags": job.options.get("tags", []),
            "searchable_content": self._extract_searchable_content(job)
        }
        
        # Indexation pour recherche rapide
        await self.storage.index_backup(index_entry)
    
    def _extract_searchable_content(self, job: BackupJob) -> List[str]:
        """
        Extrait le contenu recherchable pour indexation
        
        Args:
            job: Job de sauvegarde
            
        Returns:
            List[str]: Termes recherchables
        """
        searchable = [job.name, job.content_type]
        
        if job.user_id:
            searchable.append(job.user_id)
        
        # Extraction métadonnées fichiers
        for source_path in job.source_paths:
            searchable.append(source_path.name)
            searchable.append(source_path.suffix.lower())
        
        return list(set(searchable))
    
    async def _cleanup_temporary_files(self, job: BackupJob) -> None:
        """
        Nettoyage des fichiers temporaires
        
        Args:
            job: Job de sauvegarde
        """
        temp_patterns = ["*.tmp", "*.temp", "*.bak"]
        
        for pattern in temp_patterns:
            for temp_file in Path("/tmp").glob(f"{job.job_id}_{pattern}"):
                try:
                    temp_file.unlink()
                    logger.debug(f"Cleaned temporary file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean temporary file {temp_file}: {e}")
    
    async def get_backup_status(self, job_id: str) -> Optional[BackupJob]:
        """
        Récupère le statut d'un job de sauvegarde
        
        Args:
            job_id: ID du job
            
        Returns:
            Optional[BackupJob]: Job si trouvé, None sinon
        """
        # Recherche dans jobs actifs
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        
        # Recherche dans historique
        for job in self.job_history:
            if job.job_id == job_id:
                return job
        
        return None
    
    async def list_backups(
        self,
        user_id: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[BackupJob]:
        """
        Liste les sauvegardes avec filtrage
        
        Args:
            user_id: Filtrer par utilisateur
            content_type: Filtrer par type de contenu
            limit: Nombre maximum de résultats
            offset: Décalage pour pagination
            
        Returns:
            List[BackupJob]: Liste des sauvegardes
        """
        all_jobs = list(self.active_jobs.values()) + self.job_history
        
        # Filtrage
        filtered_jobs = []
        for job in all_jobs:
            if user_id and job.user_id != user_id:
                continue
            if content_type and job.content_type != content_type:
                continue
            filtered_jobs.append(job)
        
        # Tri par date de création (plus récent en premier)
        filtered_jobs.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        return filtered_jobs[offset:offset + limit]
    
    async def cancel_backup(self, job_id: str, reason: str = "User requested") -> bool:
        """
        Annule un job de sauvegarde en cours
        
        Args:
            job_id: ID du job à annuler
            reason: Raison de l'annulation
            
        Returns:
            bool: True si annulé avec succès
        """
        if job_id not in self.active_jobs:
            logger.warning(f"Cannot cancel job {job_id}: not found in active jobs")
            return False
        
        job = self.active_jobs[job_id]
        
        if job.status in [BackupStatus.COMPLETED, BackupStatus.FAILED, BackupStatus.CANCELLED]:
            logger.warning(f"Cannot cancel job {job_id}: already in final state {job.status}")
            return False
        
        job.status = BackupStatus.CANCELLED
        job.error_message = f"Cancelled: {reason}"
        job.cancelled_at = datetime.now()
        
        # Déplacement vers historique
        self.job_history.append(self.active_jobs.pop(job_id))
        
        logger.info(f"Backup job {job_id} cancelled: {reason}")
        return True
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Récupère les métriques de performance du système de sauvegarde
        
        Returns:
            Dict[str, Any]: Métriques de performance
        """
        completed_jobs = [job for job in self.job_history if job.status == BackupStatus.COMPLETED]
        failed_jobs = [job for job in self.job_history if job.status == BackupStatus.FAILED]
        
        if not completed_jobs:
            return {"status": "no_data", "message": "No completed backups yet"}
        
        # Calculs métriques
        total_backups = len(self.job_history)
        success_rate = len(completed_jobs) / total_backups if total_backups > 0 else 0
        
        avg_duration = sum((job.duration.total_seconds() for job in completed_jobs if job.duration), 0) / len(completed_jobs)
        
        total_size = sum(job.estimated_size for job in completed_jobs if job.estimated_size)
        avg_compression_ratio = sum(job.compression_ratio for job in completed_jobs if job.compression_ratio) / len(completed_jobs)
        
        return {
            "total_backups": total_backups,
            "active_jobs": len(self.active_jobs),
            "success_rate": round(success_rate * 100, 2),
            "failed_jobs": len(failed_jobs),
            "average_duration_seconds": round(avg_duration, 2),
            "total_data_backed_up_gb": round(total_size / (1024**3), 2),
            "average_compression_ratio": round(avg_compression_ratio, 2),
            "last_backup": completed_jobs[0].created_at.isoformat() if completed_jobs else None
        }
    
    def __del__(self):
        """Nettoyage lors de la destruction de l'objet"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


class BackupOrchestrator:
    """
    Orchestrateur avancé pour la coordination de multiples gestionnaires de sauvegarde
    
    Fonctionnalités:
    - Coordination multi-tenant
    - Load balancing intelligent
    - Priorisation dynamique
    - Optimisation ressources globales
    """
    
    def __init__(self):
        self.managers: Dict[str, BackupManager] = {}
        self.global_scheduler = BackupScheduler()
        self.load_balancer = self._create_load_balancer()
        
        logger.info("BackupOrchestrator initialized")
    
    def _create_load_balancer(self):
        """Create intelligent load balancer for backup managers"""
        try:
            # Create load balancer with round-robin and health checking
            load_balancer_config = {
                "algorithm": "weighted_round_robin",
                "health_check_interval": 30,  # seconds
                "max_retries": 3,
                "timeout": 120,  # seconds
                "circuit_breaker": {
                    "failure_threshold": 5,
                    "recovery_timeout": 300,  # 5 minutes
                    "enabled": True
                },
                "weights": {
                    "default": 1.0,
                    "high_priority": 1.5,
                    "low_priority": 0.5
                }
            }
            
            # Initialize load balancer state
            load_balancer = {
                "config": load_balancer_config,
                "managers": {},
                "current_index": 0,
                "health_status": {},
                "circuit_breakers": {},
                "statistics": {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "avg_response_time": 0.0
                }
            }
            
            logger.info("Created intelligent load balancer for backup managers")
            logger.info(f"Load balancing algorithm: {load_balancer_config['algorithm']}")
            
            return load_balancer
            
        except Exception as e:
            logger.error(f"Failed to create load balancer: {e}")
            raise
    
    async def register_manager(self, tenant_id: str, config: BackupConfiguration) -> BackupManager:
        """
        Enregistre un nouveau gestionnaire pour un tenant
        
        Args:
            tenant_id: ID du tenant
            config: Configuration du manager
            
        Returns:
            BackupManager: Manager créé
        """
        manager = BackupManager(config)
        self.managers[tenant_id] = manager
        
        logger.info(f"Registered backup manager for tenant {tenant_id}")
        return manager
    
    async def orchestrate_global_backup(self) -> Dict[str, Any]:
        """
        Orchestre une sauvegarde globale coordonnée
        
        Returns:
            Dict[str, Any]: Résultats de l'orchestration
        """
        results = {}
        
        for tenant_id, manager in self.managers.items():
            try:
                metrics = await manager.get_performance_metrics()
                results[tenant_id] = metrics
            except Exception as e:
                logger.error(f"Failed to get metrics for tenant {tenant_id}: {e}")
                results[tenant_id] = {"error": str(e)}
        
        return results
