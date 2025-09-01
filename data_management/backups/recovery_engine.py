"""🔄 Recovery Engine - Advanced Backup Recovery System
===================================================
Module: backend/data_management/backups/recovery_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Recovery System - Enterprise Production-Ready
Responsibility: Récupération intelligente et restauration sauvegardes
==================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import os
import shutil
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from .models import BackupMetadata, BackupStatus, BackupType
from .exceptions import RecoveryException, CorruptionException
from .verification_engine import VerificationEngine, VerificationLevel
from .encryption_manager import EncryptionManager
from .compression_engine import CompressionEngine

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """
Stratégies de récupération"""

    FULL_RESTORE = "full_restore"           # Restauration complète
    SELECTIVE_RESTORE = "selective_restore" # Restauration sélective
    INCREMENTAL_RESTORE = "incremental_restore" # Restauration incrémentale
    POINT_IN_TIME = "point_in_time"         # Restauration à un point dans le temps
    DISASTER_RECOVERY = "disaster_recovery" # Récupération après sinistre


class RecoveryPriority(Enum):
    """Priorités de récupération"""

    CRITICAL = "critical"     # Critique (immédiat)
    HIGH = "high"            # Haute priorité
    NORMAL = "normal"        # Priorité normale
    LOW = "low"              # Basse priorité
    BACKGROUND = "background" # Arrière-plan


class RecoveryStatus(Enum):
    """États de récupération"""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RecoveryPlan:
    """Plan de récupération détaillé"""
    recovery_id: str
    strategy: RecoveryStrategy
    priority: RecoveryPriority
    source_backup_id: str
    target_location: Path
    files_to_recover: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    recovery_point: Optional[datetime] = None
    verify_integrity: bool = True
    decrypt_files: bool = True
    decompress_files: bool = True
    preserve_permissions: bool = True
    overwrite_existing: bool = False
    progress_callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convertit en dictionnaire"""
        return {
            "recovery_id": self.recovery_id,
            "strategy": self.strategy.value,
            "priority": self.priority.value,
            "source_backup_id": self.source_backup_id,
            "target_location": str(self.target_location),
            "files_to_recover": self.files_to_recover,
            "exclude_patterns": self.exclude_patterns,
            "recovery_point": self.recovery_point.isoformat() if self.recovery_point else None,
            "verify_integrity": self.verify_integrity,
            "decrypt_files": self.decrypt_files,
            "decompress_files": self.decompress_files,
            "preserve_permissions": self.preserve_permissions,
            "overwrite_existing": self.overwrite_existing,
            "metadata": self.metadata
        }


@dataclass
class RecoveryProgress:
    """Progression de récupération"""
    recovery_id: str
    status: RecoveryStatus
    files_total: int = 0
    files_processed: int = 0
    bytes_total: int = 0
    bytes_processed: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    current_file: Optional[str] = None
    speed_bps: float = 0.0
    
    @property
    def progress_percentage(self) -> float:
        """
Pourcentage de progression"""
        if self.files_total == 0:
            return 0.0
        return (self.files_processed / self.files_total) * 100
    
    @property
    def bytes_percentage(self) -> float:
        """
Pourcentage de bytes traités"""
        if self.bytes_total == 0:
            return 0.0
        return (self.bytes_processed / self.bytes_total) * 100
    
    @property
    def duration(self) -> Optional[timedelta]:
        """
Durée d'exécution"""
        if not self.started_at:
            return None
        end_time = self.completed_at or datetime.now()
        return end_time - self.started_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convertit en dictionnaire"""
        return {
            "recovery_id": self.recovery_id,
            "status": self.status.value,
            "files_total": self.files_total,
            "files_processed": self.files_processed,
            "bytes_total": self.bytes_total,
            "bytes_processed": self.bytes_processed,
            "progress_percentage": self.progress_percentage,
            "bytes_percentage": self.bytes_percentage,
            "errors": self.errors,
            "warnings": self.warnings,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "current_file": self.current_file,
            "speed_bps": self.speed_bps,
            "duration_seconds": self.duration.total_seconds() if self.duration else None
        }


@dataclass
class RecoveryConfig:
    """Configuration de récupération"""
    parallel_workers: int = 4
    chunk_size: int = 64 * 1024  # 64KB
    verify_checksums: bool = True
    auto_resume: bool = True
    temp_directory: Optional[Path] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    progress_update_interval: float = 1.0  # secondes
    bandwidth_limit: Optional[int] = None  # bytes/sec
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convertit en dictionnaire"""
        return {
            "parallel_workers": self.parallel_workers,
            "chunk_size": self.chunk_size,
            "verify_checksums": self.verify_checksums,
            "auto_resume": self.auto_resume,
            "temp_directory": str(self.temp_directory) if self.temp_directory else None,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "progress_update_interval": self.progress_update_interval,
            "bandwidth_limit": self.bandwidth_limit
        }


class RecoveryEngine:
    """
    Moteur de récupération avancé pour sauvegardes
    
    Fonctionnalités:
    - Récupération multi-stratégies
    - Récupération point-in-time
    - Parallélisation et optimisation
    - Vérification intégrité
    - Déchiffrement et décompression
    - Gestion erreurs et reprise
    - Monitoring temps réel
    - Récupération sélective
    """
    
    def __init__(
        self,
        config: Optional[RecoveryConfig] = None,
        verification_engine: Optional[VerificationEngine] = None,
        encryption_manager: Optional[EncryptionManager] = None,
        compression_engine: Optional[CompressionEngine] = None
    ):
        self.config = config or RecoveryConfig()
        self.verification_engine = verification_engine or VerificationEngine()
        self.encryption_manager = encryption_manager
        self.compression_engine = compression_engine
        
        # Gestion des récupérations actives
        self.active_recoveries: Dict[str, RecoveryProgress] = {}
        self.recovery_tasks: Dict[str, asyncio.Task] = {}
        
        # Statistiques de récupération
        self.recovery_stats = {
            "total_recoveries": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "total_files_recovered": 0,
            "total_bytes_recovered": 0,
            "average_recovery_time": 0.0,
            "fastest_recovery": float('inf'),
            "slowest_recovery": 0.0
        }
        
        # Cache des métadonnées de sauvegarde
        self.backup_metadata_cache: Dict[str, BackupMetadata] = {}
        
        logger.info(f"RecoveryEngine initialized with {self.config.parallel_workers} workers")
    
    async def create_recovery_plan(
        self,
        backup_id: str,
        strategy: RecoveryStrategy,
        target_location: Path,
        **kwargs
    ) -> RecoveryPlan:
        """
        Crée un plan de récupération
        
        Args:
            backup_id: ID de la sauvegarde source
            strategy: Stratégie de récupération
            target_location: Emplacement de restauration
            **kwargs: Options supplémentaires
            
        Returns:
            RecoveryPlan: Plan de récupération détaillé
        """
        try:
            recovery_id = self._generate_recovery_id()
            
            # Récupération métadonnées de sauvegarde
            backup_metadata = await self._get_backup_metadata(backup_id)
            
            if not backup_metadata:
                raise RecoveryException(f"Backup metadata not found for {backup_id}")
            
            # Création du plan
            recovery_plan = RecoveryPlan(
                recovery_id=recovery_id,
                strategy=strategy,
                priority=kwargs.get("priority", RecoveryPriority.NORMAL),
                source_backup_id=backup_id,
                target_location=target_location,
                files_to_recover=kwargs.get("files_to_recover", []),
                exclude_patterns=kwargs.get("exclude_patterns", []),
                recovery_point=kwargs.get("recovery_point"),
                verify_integrity=kwargs.get("verify_integrity", True),
                decrypt_files=kwargs.get("decrypt_files", True),
                decompress_files=kwargs.get("decompress_files", True),
                preserve_permissions=kwargs.get("preserve_permissions", True),
                overwrite_existing=kwargs.get("overwrite_existing", False),
                progress_callback=kwargs.get("progress_callback"),
                metadata=kwargs.get("metadata", {})
            )
            
            # Validation du plan
            await self._validate_recovery_plan(recovery_plan, backup_metadata)
            
            # Optimisation du plan
            await self._optimize_recovery_plan(recovery_plan, backup_metadata)
            
            logger.info(f"Created recovery plan {recovery_id} for backup {backup_id}")
            return recovery_plan
            
        except Exception as e:
            logger.error(f"Recovery plan creation failed: {e}")
            raise RecoveryException(f"Recovery plan creation failed: {e}")
    
    def _generate_recovery_id(self) -> str:
        """Génère un ID unique pour une récupération"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        import secrets
        return f"recovery_{timestamp}_{secrets.token_hex(8)}"
    
    async def _get_backup_metadata(self, backup_id: str) -> Optional[BackupMetadata]:
        """Récupère les métadonnées d'une sauvegarde"""
        # Vérification cache
        if backup_id in self.backup_metadata_cache:
            return self.backup_metadata_cache[backup_id]
        
        # En production: récupération depuis base de données ou stockage
        # Ici: simulation
        try:
            metadata_path = Path(f"/tmp/backup_metadata_{backup_id}.json")
            
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    data = json.load(f)
                
                metadata = BackupMetadata(
                    backup_id=data["backup_id"],
                    user_id=data["user_id"],
                    backup_type=BackupType(data["backup_type"]),
                    status=BackupStatus(data["status"]),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    files=data["files"],
                    total_size=data["total_size"],
                    metadata=data.get("metadata", {})
                )
                
                # Mise en cache
                self.backup_metadata_cache[backup_id] = metadata
                return metadata
                
        except Exception as e:
            logger.error(f"Failed to load backup metadata for {backup_id}: {e}")
        
        return None
    
    async def _validate_recovery_plan(
        self,
        plan: RecoveryPlan,
        backup_metadata: BackupMetadata
    ):
        """Valide un plan de récupération"""
        # Vérification emplacement cible
        if not plan.target_location.parent.exists():
            raise RecoveryException(f"Target directory does not exist: {plan.target_location.parent}")
        
        # Vérification permissions
        if not os.access(plan.target_location.parent, os.W_OK):
            raise RecoveryException(f"No write permission to target directory: {plan.target_location.parent}")
        
        # Vérification espace disque
        available_space = shutil.disk_usage(plan.target_location.parent).free
        required_space = backup_metadata.total_size
        
        if available_space < required_space:
            raise RecoveryException(
                f"Insufficient disk space: {available_space} available, {required_space} required"
            )
        
        # Vérification fichiers spécifiques
        if plan.files_to_recover:
            backup_files = {f["path"] for f in backup_metadata.files}
            
            for file_path in plan.files_to_recover:
                if file_path not in backup_files:
                    logger.warning(f"File not found in backup: {file_path}")
        
        logger.debug(f"Recovery plan validation completed for {plan.recovery_id}")
    
    async def _optimize_recovery_plan(
        self,
        plan: RecoveryPlan,
        backup_metadata: BackupMetadata
    ):
        """Optimise un plan de récupération"""
        # Tri des fichiers par taille pour optimiser l'ordre
        files_to_process = backup_metadata.files.copy()
        
        if plan.files_to_recover:
            # Filtrage fichiers spécifiques
            files_to_process = [
                f for f in files_to_process
                if f["path"] in plan.files_to_recover
            ]
        
        # Application des patterns d'exclusion
        if plan.exclude_patterns:
            import fnmatch
            
            filtered_files = []
            for file_info in files_to_process:
                excluded = False
                
                for pattern in plan.exclude_patterns:
                    if fnmatch.fnmatch(file_info["path"], pattern):
                        excluded = True
                        break
                
                if not excluded:
                    filtered_files.append(file_info)
            
            files_to_process = filtered_files
        
        # Tri par priorité (gros fichiers à la fin pour parallélisation)
        files_to_process.sort(key=lambda x: x.get("size", 0))
        
        # Mise à jour du plan
        plan.files_to_recover = [f["path"] for f in files_to_process]
        plan.metadata["optimized_file_order"] = True
        plan.metadata["total_files"] = len(files_to_process)
        plan.metadata["total_size"] = sum(f.get("size", 0) for f in files_to_process)
        
        logger.debug(f"Recovery plan optimized: {len(files_to_process)} files to recover")
    
    async def execute_recovery(self, plan: RecoveryPlan) -> str:
        """
        Exécute un plan de récupération
        
        Args:
            plan: Plan de récupération à exécuter
            
        Returns:
            str: ID de la récupération lancée
        """
        try:
            recovery_id = plan.recovery_id
            
            # Vérification si récupération déjà active
            if recovery_id in self.active_recoveries:
                raise RecoveryException(f"Recovery {recovery_id} is already active")
            
            # Initialisation progression
            progress = RecoveryProgress(
                recovery_id=recovery_id,
                status=RecoveryStatus.PENDING,
                started_at=datetime.now()
            )
            
            self.active_recoveries[recovery_id] = progress
            
            # Lancement tâche asynchrone
            task = asyncio.create_task(self._execute_recovery_task(plan, progress))
            self.recovery_tasks[recovery_id] = task
            
            # Mise à jour statut
            progress.status = RecoveryStatus.RUNNING
            
            logger.info(f"Started recovery {recovery_id} with strategy {plan.strategy.value}")
            return recovery_id
            
        except Exception as e:
            logger.error(f"Recovery execution failed: {e}")
            raise RecoveryException(f"Recovery execution failed: {e}")
    
    async def _execute_recovery_task(
        self,
        plan: RecoveryPlan,
        progress: RecoveryProgress
    ):
        """
        Tâche d'exécution de récupération
        
        Args:
            plan: Plan de récupération
            progress: Objet de progression
        """
        try:
            # Récupération métadonnées
            backup_metadata = await self._get_backup_metadata(plan.source_backup_id)
            
            if not backup_metadata:
                raise RecoveryException(f"Backup metadata not found")
            
            # Préparation des fichiers à récupérer
            files_to_recover = self._prepare_file_list(plan, backup_metadata)
            
            # Initialisation progression
            progress.files_total = len(files_to_recover)
            progress.bytes_total = sum(f.get("size", 0) for f in files_to_recover)
            
            # Création répertoire cible
            plan.target_location.mkdir(parents=True, exist_ok=True)
            
            # Exécution selon stratégie
            if plan.strategy == RecoveryStrategy.FULL_RESTORE:
                await self._execute_full_restore(plan, files_to_recover, progress)
            elif plan.strategy == RecoveryStrategy.SELECTIVE_RESTORE:
                await self._execute_selective_restore(plan, files_to_recover, progress)
            elif plan.strategy == RecoveryStrategy.INCREMENTAL_RESTORE:
                await self._execute_incremental_restore(plan, files_to_recover, progress)
            elif plan.strategy == RecoveryStrategy.POINT_IN_TIME:
                await self._execute_point_in_time_restore(plan, files_to_recover, progress)
            elif plan.strategy == RecoveryStrategy.DISASTER_RECOVERY:
                await self._execute_disaster_recovery(plan, files_to_recover, progress)
            
            # Finalisation
            progress.status = RecoveryStatus.COMPLETED
            progress.completed_at = datetime.now()
            
            # Mise à jour statistiques
            self._update_recovery_stats(progress, True)
            
            # Callback de progression
            if plan.progress_callback:
                plan.progress_callback(progress)
            
            logger.info(f"Recovery {plan.recovery_id} completed successfully")
            
        except Exception as e:
            progress.status = RecoveryStatus.FAILED
            progress.errors.append(str(e))
            progress.completed_at = datetime.now()
            
            # Mise à jour statistiques
            self._update_recovery_stats(progress, False)
            
            logger.error(f"Recovery {plan.recovery_id} failed: {e}")
            
        finally:
            # Nettoyage
            if plan.recovery_id in self.recovery_tasks:
                del self.recovery_tasks[plan.recovery_id]
    
    def _prepare_file_list(
        self,
        plan: RecoveryPlan,
        backup_metadata: BackupMetadata
    ) -> List[Dict[str, Any]]:
        """Prépare la liste des fichiers à récupérer"""
        files = backup_metadata.files.copy()
        
        # Filtrage par fichiers spécifiques
        if plan.files_to_recover:
            files = [f for f in files if f["path"] in plan.files_to_recover]
        
        # Filtrage par point dans le temps
        if plan.recovery_point:
            files = [
                f for f in files
                if datetime.fromisoformat(f.get("timestamp", "1970-01-01T00:00:00")) <= plan.recovery_point
            ]
        
        return files
    
    async def _execute_full_restore(
        self,
        plan: RecoveryPlan,
        files_to_recover: List[Dict[str, Any]],
        progress: RecoveryProgress
    ):
        """Exécute une restauration complète"""
        semaphore = asyncio.Semaphore(self.config.parallel_workers)
        
        async def restore_single_file(file_info):
            async with semaphore:
                await self._restore_file(plan, file_info, progress)
        
        # Exécution parallèle
        tasks = [restore_single_file(file_info) for file_info in files_to_recover]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_selective_restore(
        self,
        plan: RecoveryPlan,
        files_to_recover: List[Dict[str, Any]],
        progress: RecoveryProgress
    ):
        """
Exécute une restauration sélective"""
        # Même logique que restauration complète mais avec fichiers filtrés
        await self._execute_full_restore(plan, files_to_recover, progress)
    
    async def _execute_incremental_restore(
        self,
        plan: RecoveryPlan,
        files_to_recover: List[Dict[str, Any]],
        progress: RecoveryProgress
    ):
        """
Exécute une restauration incrémentale"""
        # Tri par timestamp pour restauration chronologique
        files_sorted = sorted(
            files_to_recover,
            key=lambda x: datetime.fromisoformat(x.get("timestamp", "1970-01-01T00:00:00"))
        )
        
        # Restauration séquentielle pour préserver ordre
        for file_info in files_sorted:
            await self._restore_file(plan, file_info, progress)
    
    async def _execute_point_in_time_restore(
        self,
        plan: RecoveryPlan,
        files_to_recover: List[Dict[str, Any]],
        progress: RecoveryProgress
    ):
        """Exécute une restauration point-in-time"""
        if not plan.recovery_point:
            raise RecoveryException("Recovery point not specified for point-in-time restore")
        
        # Fichiers déjà filtrés par _prepare_file_list
        await self._execute_full_restore(plan, files_to_recover, progress)
    
    async def _execute_disaster_recovery(
        self,
        plan: RecoveryPlan,
        files_to_recover: List[Dict[str, Any]],
        progress: RecoveryProgress
    ):
        """Exécute une récupération après sinistre"""
        # Priorité aux fichiers critiques
        critical_patterns = ["*.db", "*.config", "*.key", "*.cert"]
        import fnmatch
        
        critical_files = []
        normal_files = []
        
        for file_info in files_to_recover:
            is_critical = any(
                fnmatch.fnmatch(file_info["path"], pattern)
                for pattern in critical_patterns
            )
            
            if is_critical:
                critical_files.append(file_info)
            else:
                normal_files.append(file_info)
        
        # Restauration critique en premier
        if critical_files:
            await self._execute_full_restore(plan, critical_files, progress)
        
        # Puis fichiers normaux
        if normal_files:
            await self._execute_full_restore(plan, normal_files, progress)
    
    async def _restore_file(
        self,
        plan: RecoveryPlan,
        file_info: Dict[str, Any],
        progress: RecoveryProgress
    ):
        """
        Restaure un fichier individuel
        
        Args:
            plan: Plan de récupération
            file_info: Informations du fichier
            progress: Objet de progression
        """
        try:
            source_path = Path(file_info["path"])
            target_path = plan.target_location / source_path.name
            
            # Mise à jour progression
            progress.current_file = str(source_path)
            
            # Vérification existence fichier cible
            if target_path.exists() and not plan.overwrite_existing:
                progress.warnings.append(f"File already exists, skipping: {target_path}")
                progress.files_processed += 1
                return
            
            # Récupération du fichier depuis stockage
            temp_file = await self._retrieve_file_from_backup(plan.source_backup_id, source_path)
            
            if not temp_file or not temp_file.exists():
                raise RecoveryException(f"Could not retrieve file from backup: {source_path}")
            
            try:
                # Déchiffrement si nécessaire
                if plan.decrypt_files and self.encryption_manager:
                    decrypted_file = await self._decrypt_file(temp_file, file_info)
                    if decrypted_file:
                        temp_file.unlink()  # Nettoyage fichier chiffré
                        temp_file = decrypted_file
                
                # Décompression si nécessaire
                if plan.decompress_files and self.compression_engine:
                    decompressed_file = await self._decompress_file(temp_file, file_info)
                    if decompressed_file:
                        temp_file.unlink()  # Nettoyage fichier compressé
                        temp_file = decompressed_file
                
                # Vérification intégrité
                if plan.verify_integrity:
                    await self._verify_restored_file(temp_file, file_info)
                
                # Copie vers emplacement final
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(temp_file, target_path)
                
                # Préservation permissions
                if plan.preserve_permissions:
                    await self._restore_file_permissions(target_path, file_info)
                
                # Mise à jour progression
                progress.files_processed += 1
                progress.bytes_processed += file_info.get("size", 0)
                
                # Limitation bande passante
                if self.config.bandwidth_limit:
                    await self._apply_bandwidth_limit(file_info.get("size", 0))
                
                logger.debug(f"File restored successfully: {source_path} -> {target_path}")
                
            finally:
                # Nettoyage fichier temporaire
                if temp_file.exists():
                    temp_file.unlink()
                    
        except Exception as e:
            error_msg = f"Failed to restore file {file_info['path']}: {e}"
            progress.errors.append(error_msg)
            logger.error(error_msg)
    
    async def _retrieve_file_from_backup(
        self,
        backup_id: str,
        file_path: Path
    ) -> Optional[Path]:
        """
        Récupère un fichier depuis le stockage de sauvegarde
        
        Args:
            backup_id: ID de la sauvegarde
            file_path: Chemin du fichier dans la sauvegarde
            
        Returns:
            Optional[Path]: Fichier temporaire récupéré
        """
        try:
            # En production: récupération depuis le storage provider
            # Ici: simulation avec fichier local
            
            temp_dir = self.config.temp_directory or Path("/tmp")
            temp_file = temp_dir / f"recovery_{backup_id}_{file_path.name}"
            
            # Simulation récupération
            backup_file_path = Path(f"/backups/{backup_id}/{file_path}")
            
            if backup_file_path.exists():
                shutil.copy2(backup_file_path, temp_file)
                return temp_file
            else:
                logger.warning(f"Backup file not found: {backup_file_path}")
                return None
                
        except Exception as e:
            logger.error(f"File retrieval failed: {e}")
            return None
    
    async def _decrypt_file(
        self,
        encrypted_file: Path,
        file_info: Dict[str, Any]
    ) -> Optional[Path]:
        """Déchiffre un fichier récupéré"""
        try:
            if not self.encryption_manager:
                return None
            
            decrypted_file = encrypted_file.parent / f"{encrypted_file.name}.decrypted"
            
            # Récupération clé de déchiffrement
            key_id = file_info.get("encryption_key_id")
            
            if key_id:
                success = await self.encryption_manager.decrypt_file(
                    encrypted_file,
                    decrypted_file,
                    key_id
                )
                
                if success:
                    return decrypted_file
            
            return None
            
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            return None
    
    async def _decompress_file(
        self,
        compressed_file: Path,
        file_info: Dict[str, Any]
    ) -> Optional[Path]:
        """Décompresse un fichier récupéré"""
        try:
            if not self.compression_engine:
                return None
            
            decompressed_file = compressed_file.parent / f"{compressed_file.name}.decompressed"
            
            # Détection algorithme de compression
            compression_algorithm = file_info.get("compression_algorithm")
            
            if compression_algorithm:
                success = await self.compression_engine.decompress_file(
                    compressed_file,
                    decompressed_file,
                    compression_algorithm
                )
                
                if success:
                    return decompressed_file
            
            return None
            
        except Exception as e:
            logger.error(f"File decompression failed: {e}")
            return None
    
    async def _verify_restored_file(
        self,
        restored_file: Path,
        file_info: Dict[str, Any]
    ):
        """Vérifie l'intégrité du fichier restauré"""
        try:
            # Vérification taille
            expected_size = file_info.get("original_size", file_info.get("size"))
            actual_size = restored_file.stat().st_size
            
            if expected_size and actual_size != expected_size:
                raise CorruptionException(
                    f"Size mismatch: expected {expected_size}, got {actual_size}"
                )
            
            # Vérification checksum si disponible
            expected_checksum = file_info.get("checksum")
            
            if expected_checksum:
                result = await self.verification_engine.verify_file(
                    restored_file,
                    level=VerificationLevel.BASIC
                )
                
                if not result.is_valid:
                    raise CorruptionException(f"Checksum verification failed: {result.errors}")
            
        except Exception as e:
            logger.error(f"File verification failed: {e}")
            raise
    
    async def _restore_file_permissions(
        self,
        file_path: Path,
        file_info: Dict[str, Any]
    ):
        """Restaure les permissions d'un fichier"""
        try:
            # Restauration permissions Unix
            if "permissions" in file_info:
                permissions = file_info["permissions"]
                
                if isinstance(permissions, int):
                    os.chmod(file_path, permissions)
                elif isinstance(permissions, str):
                    # Conversion permissions octales
                    os.chmod(file_path, int(permissions, 8))
            
            # Restauration timestamps
            if "mtime" in file_info:
                mtime = datetime.fromisoformat(file_info["mtime"]).timestamp()
                os.utime(file_path, (mtime, mtime))
                
        except Exception as e:
            logger.warning(f"Failed to restore file permissions: {e}")
    
    async def _apply_bandwidth_limit(self, bytes_transferred: int):
        """Applique la limitation de bande passante"""
        if not self.config.bandwidth_limit:
            return
        
        # Calcul délai nécessaire
        delay = bytes_transferred / self.config.bandwidth_limit
        
        if delay > 0:
            await asyncio.sleep(delay)
    
    def _update_recovery_stats(self, progress: RecoveryProgress, success: bool):
        """
Met à jour les statistiques de récupération"""
        self.recovery_stats["total_recoveries"] += 1
        
        if success:
            self.recovery_stats["successful_recoveries"] += 1
            self.recovery_stats["total_files_recovered"] += progress.files_processed
            self.recovery_stats["total_bytes_recovered"] += progress.bytes_processed
        else:
            self.recovery_stats["failed_recoveries"] += 1
        
        # Mise à jour temps de récupération
        if progress.duration:
            duration_seconds = progress.duration.total_seconds()
            
            # Temps moyen
            total_recoveries = self.recovery_stats["total_recoveries"]
            current_avg = self.recovery_stats["average_recovery_time"]
            new_avg = ((current_avg * (total_recoveries - 1)) + duration_seconds) / total_recoveries
            self.recovery_stats["average_recovery_time"] = new_avg
            
            # Min/Max
            self.recovery_stats["fastest_recovery"] = min(
                self.recovery_stats["fastest_recovery"],
                duration_seconds
            )
            self.recovery_stats["slowest_recovery"] = max(
                self.recovery_stats["slowest_recovery"],
                duration_seconds
            )
    
    async def pause_recovery(self, recovery_id: str) -> bool:
        """
        Met en pause une récupération
        
        Args:
            recovery_id: ID de la récupération
            
        Returns:
            bool: True si mise en pause réussie
        """
        try:
            if recovery_id not in self.active_recoveries:
                return False
            
            progress = self.active_recoveries[recovery_id]
            
            if progress.status == RecoveryStatus.RUNNING:
                progress.status = RecoveryStatus.PAUSED
                
                # Annulation de la tâche si possible
                if recovery_id in self.recovery_tasks:
                    task = self.recovery_tasks[recovery_id]
                    task.cancel()
                
                logger.info(f"Recovery {recovery_id} paused")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to pause recovery {recovery_id}: {e}")
            return False
    
    async def resume_recovery(self, recovery_id: str) -> bool:
        """
        Reprend une récupération en pause
        
        Args:
            recovery_id: ID de la récupération
            
        Returns:
            bool: True si reprise réussie
        """
        try:
            if recovery_id not in self.active_recoveries:
                return False
            
            progress = self.active_recoveries[recovery_id]
            
            if progress.status == RecoveryStatus.PAUSED:
                # En production: reprise depuis dernier point
                # Ici: relance complète simplifiée
                progress.status = RecoveryStatus.RUNNING
                
                logger.info(f"Recovery {recovery_id} resumed")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resume recovery {recovery_id}: {e}")
            return False
    
    async def cancel_recovery(self, recovery_id: str) -> bool:
        """
        Annule une récupération
        
        Args:
            recovery_id: ID de la récupération
            
        Returns:
            bool: True si annulation réussie
        """
        try:
            if recovery_id not in self.active_recoveries:
                return False
            
            progress = self.active_recoveries[recovery_id]
            progress.status = RecoveryStatus.CANCELLED
            progress.completed_at = datetime.now()
            
            # Annulation de la tâche
            if recovery_id in self.recovery_tasks:
                task = self.recovery_tasks[recovery_id]
                task.cancel()
                del self.recovery_tasks[recovery_id]
            
            logger.info(f"Recovery {recovery_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel recovery {recovery_id}: {e}")
            return False
    
    def get_recovery_progress(self, recovery_id: str) -> Optional[RecoveryProgress]:
        """
        Récupère la progression d'une récupération
        
        Args:
            recovery_id: ID de la récupération
            
        Returns:
            Optional[RecoveryProgress]: Progression actuelle
        """
        return self.active_recoveries.get(recovery_id)
    
    def list_active_recoveries(self) -> List[RecoveryProgress]:
        """
        Liste les récupérations actives
        
        Returns:
            List[RecoveryProgress]: Récupérations en cours
        """
        return list(self.active_recoveries.values())
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques de récupération
        
        Returns:
            Dict[str, Any]: Statistiques détaillées
        """
        stats = self.recovery_stats.copy()
        
        # Calculs additionnels
        total_recoveries = stats["total_recoveries"]
        
        if total_recoveries > 0:
            stats["success_rate"] = (
                stats["successful_recoveries"] / total_recoveries
            ) * 100
            
            stats["failure_rate"] = (
                stats["failed_recoveries"] / total_recoveries
            ) * 100
        
        stats["active_recoveries"] = len(self.active_recoveries)
        stats["total_gb_recovered"] = stats["total_bytes_recovered"] / (1024**3)
        
        # Correction valeur infinie
        if stats["fastest_recovery"] == float('inf'):
            stats["fastest_recovery"] = 0.0
        
        return stats


# Export des classes principales
__all__ = [
    'RecoveryEngine',
    'RecoveryPlan',
    'RecoveryProgress',
    'RecoveryConfig',
    'RecoveryStrategy',
    'RecoveryPriority',
    'RecoveryStatus'
]
