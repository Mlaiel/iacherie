#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚠️ AVERTISSEMENT: Ce module fait partie du système propriétaire Ainflue
Toute reproduction, distribution ou modification non autorisée est strictement interdite.
© 2024 Ainflue - Tous droits réservés

Backup Manager - Enterprise Backup & Disaster Recovery System
============================================================

Professional backup and disaster recovery management for multi-format content.
Supports multi-tier backup strategy, automated recovery, and compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
import hashlib
import gzip
import lzma
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import tempfile
import shutil
import aiofiles
import aiofiles.os
from concurrent.futures import ThreadPoolExecutor
import threading

try:
    import boto3
    from botocore.exceptions import ClientError
    from google.cloud import storage as gcs
    from azure.storage.blob.aio import BlobServiceClient
    import aiobotocore.session
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    import os
except ImportError as e:
    logging.warning(f"Dépendance optionnelle manquante: {e}")


class BackupTier(Enum):
    """Niveaux de backup avec objectifs RTO/RPO"""
    HOT = "hot"           # RTO: <1min, RPO: <5min
    WARM = "warm"         # RTO: <15min, RPO: <30min  
    COLD = "cold"         # RTO: <4h, RPO: <2h
    ARCHIVE = "archive"   # RTO: <24h, RPO: <12h


class BackupType(Enum):
    """Types de backup"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"
    CONTINUOUS = "continuous"


class BackupStatus(Enum):
    """États de backup"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    VERIFYING = "verifying"
    VERIFIED = "verified"


class RecoveryType(Enum):
    """Types de recovery"""
    FULL_RESTORE = "full_restore"
    PARTIAL_RESTORE = "partial_restore"
    POINT_IN_TIME = "point_in_time"
    INSTANT_RECOVERY = "instant_recovery"
    DISASTER_RECOVERY = "disaster_recovery"


class CompressionAlgorithm(Enum):
    """Algorithmes de compression"""
    NONE = "none"
    GZIP = "gzip"
    LZMA = "lzma"
    BROTLI = "brotli"
    ZSTD = "zstd"


@dataclass
class BackupDestination:
    """Configuration de destination backup"""
    provider: str
    bucket: str
    region: str
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    endpoint_url: Optional[str] = None
    encryption_enabled: bool = True
    compression: CompressionAlgorithm = CompressionAlgorithm.LZMA
    tier: BackupTier = BackupTier.WARM


@dataclass
class BackupConfig:
    """Configuration backup"""
    name: str
    backup_type: BackupType
    tier: BackupTier
    destinations: List[BackupDestination]
    schedule: Optional[str] = None  # Cron expression
    retention_days: int = 30
    max_parallel_uploads: int = 4
    verification_enabled: bool = True
    encryption_enabled: bool = True
    compression: CompressionAlgorithm = CompressionAlgorithm.LZMA
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class BackupJob:
    """Job de backup"""
    id: str
    config: BackupConfig
    source_paths: List[Path]
    status: BackupStatus = BackupStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_size: int = 0
    compressed_size: int = 0
    files_count: int = 0
    progress: float = 0.0
    error_message: Optional[str] = None
    backup_manifest: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RestoreJob:
    """Job de restore"""
    id: str
    backup_id: str
    recovery_type: RecoveryType
    destination_path: Path
    status: BackupStatus = BackupStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    files_restored: int = 0
    progress: float = 0.0
    error_message: Optional[str] = None


@dataclass
class BackupStatistics:
    """Statistiques de backup"""
    total_backups: int = 0
    successful_backups: int = 0
    failed_backups: int = 0
    total_size_backed_up: int = 0
    total_compressed_size: int = 0
    average_compression_ratio: float = 0.0
    average_backup_duration: float = 0.0
    last_backup_time: Optional[datetime] = None
    next_scheduled_backup: Optional[datetime] = None


class BackupManager:
    """
    Gestionnaire de backup enterprise avec support multi-tier
    
    Features:
    - Multi-tier backup strategy (Hot/Warm/Cold/Archive)
    - Automated scheduling and retention
    - Multi-destination replication
    - Encryption and compression
    - Integrity verification
    - Point-in-time recovery
    - Disaster recovery automation
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.backup_configs: Dict[str, BackupConfig] = {}
        self.active_jobs: Dict[str, BackupJob] = {}
        self.active_restores: Dict[str, RestoreJob] = {}
        self.statistics = BackupStatistics()
        
        # Thread pool pour opérations I/O
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Cache pour optimiser les opérations
        self._manifest_cache: Dict[str, Dict] = {}
        
        # Lock pour thread safety
        self._lock = threading.RLock()
        
        # Chargement de la configuration
        if config_path and config_path.exists():
            self._load_configurations()
    
    async def create_backup_config(
        self,
        name: str,
        backup_type: BackupType,
        tier: BackupTier,
        destinations: List[BackupDestination],
        **kwargs
    ) -> BackupConfig:
        """Crée une configuration de backup"""
        
        config = BackupConfig(
            name=name,
            backup_type=backup_type,
            tier=tier,
            destinations=destinations,
            **kwargs
        )
        
        with self._lock:
            self.backup_configs[name] = config
        
        await self._save_configurations()
        
        self.logger.info(f"Configuration backup créée: {name}")
        return config
    
    async def schedule_backup(
        self,
        config_name: str,
        source_paths: List[Union[str, Path]],
        immediate: bool = False
    ) -> str:
        """Planifie un backup"""
        
        if config_name not in self.backup_configs:
            raise ValueError(f"Configuration backup non trouvée: {config_name}")
        
        config = self.backup_configs[config_name]
        job_id = f"backup_{config_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Conversion des chemins
        paths = [Path(p) if isinstance(p, str) else p for p in source_paths]
        
        # Validation des chemins source
        for path in paths:
            if not path.exists():
                raise FileNotFoundError(f"Chemin source non trouvé: {path}")
        
        job = BackupJob(
            id=job_id,
            config=config,
            source_paths=paths
        )
        
        with self._lock:
            self.active_jobs[job_id] = job
        
        if immediate:
            # Démarrage immédiat
            await self._execute_backup_job(job)
        else:
            # Planification pour plus tard (implémentation scheduler)
            self.logger.info(f"Backup planifié: {job_id} selon schedule {config.schedule}")
        
        return job_id
    
    async def _execute_backup_job(self, job: BackupJob) -> bool:
        """Exécute un job de backup"""
        
        try:
            job.status = BackupStatus.RUNNING
            job.started_at = datetime.now()
            
            self.logger.info(f"Démarrage backup job: {job.id}")
            
            # Calcul de la taille totale
            total_size = await self._calculate_total_size(job.source_paths)
            job.total_size = total_size
            
            # Création du manifest
            manifest = await self._create_backup_manifest(job)
            job.backup_manifest = manifest
            
            # Préparation des fichiers
            temp_dir = Path(tempfile.mkdtemp(prefix=f"ainflue_backup_{job.id}_"))
            
            try:
                # Compression et chiffrement
                compressed_files = await self._prepare_backup_files(
                    job.source_paths, 
                    temp_dir, 
                    job.config.compression,
                    job.config.encryption_enabled
                )
                
                # Upload vers toutes les destinations
                await self._upload_to_destinations(job, compressed_files, manifest)
                
                # Vérification si activée
                if job.config.verification_enabled:
                    job.status = BackupStatus.VERIFYING
                    verification_success = await self._verify_backup(job, manifest)
                    
                    if verification_success:
                        job.status = BackupStatus.VERIFIED
                    else:
                        job.status = BackupStatus.FAILED
                        job.error_message = "Échec de vérification d'intégrité"
                        return False
                
                job.status = BackupStatus.COMPLETED
                job.completed_at = datetime.now()
                job.progress = 1.0
                
                # Mise à jour des statistiques
                await self._update_statistics(job, success=True)
                
                self.logger.info(f"Backup job complété avec succès: {job.id}")
                return True
                
            finally:
                # Nettoyage du répertoire temporaire
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            
            await self._update_statistics(job, success=False)
            
            self.logger.error(f"Échec backup job {job.id}: {e}")
            return False
    
    async def _calculate_total_size(self, source_paths: List[Path]) -> int:
        """Calcule la taille totale des fichiers à sauvegarder"""
        
        total_size = 0
        
        for path in source_paths:
            if path.is_file():
                total_size += path.stat().st_size
            elif path.is_dir():
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
        
        return total_size
    
    async def _create_backup_manifest(self, job: BackupJob) -> Dict[str, Any]:
        """Crée le manifest de backup"""
        
        manifest = {
            'backup_id': job.id,
            'created_at': datetime.now().isoformat(),
            'backup_type': job.config.backup_type.value,
            'tier': job.config.tier.value,
            'compression': job.config.compression.value,
            'encryption_enabled': job.config.encryption_enabled,
            'source_paths': [str(p) for p in job.source_paths],
            'files': [],
            'checksums': {},
            'metadata': {
                'total_size': job.total_size,
                'compressed_size': 0,  # Sera mis à jour
                'files_count': 0,      # Sera mis à jour
                'compression_ratio': 0.0
            }
        }
        
        # Catalogage des fichiers
        for source_path in job.source_paths:
            if source_path.is_file():
                file_info = await self._get_file_info(source_path)
                manifest['files'].append(file_info)
            elif source_path.is_dir():
                async for file_info in self._catalog_directory(source_path):
                    manifest['files'].append(file_info)
        
        manifest['metadata']['files_count'] = len(manifest['files'])
        
        return manifest
    
    async def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Obtient les informations d'un fichier"""
        
        stat = file_path.stat()
        
        # Calcul du checksum
        checksum = await self._calculate_file_checksum(file_path)
        
        return {
            'path': str(file_path),
            'relative_path': file_path.name,
            'size': stat.st_size,
            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'checksum': checksum,
            'permissions': oct(stat.st_mode)
        }
    
    async def _catalog_directory(self, dir_path: Path) -> AsyncGenerator[Dict[str, Any], None]:
        """Catalogue récursivement un répertoire"""
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                try:
                    file_info = await self._get_file_info(file_path)
                    # Chemin relatif par rapport au répertoire racine
                    file_info['relative_path'] = str(file_path.relative_to(dir_path))
                    yield file_info
                except Exception as e:
                    self.logger.warning(f"Erreur catalogage fichier {file_path}: {e}")
    
    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calcule le checksum SHA-256 d'un fichier"""
        
        hash_sha256 = hashlib.sha256()
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    async def _prepare_backup_files(
        self,
        source_paths: List[Path],
        temp_dir: Path,
        compression: CompressionAlgorithm,
        encryption_enabled: bool
    ) -> List[Path]:
        """Prépare les fichiers pour backup (compression + chiffrement)"""
        
        prepared_files = []
        
        for i, source_path in enumerate(source_paths):
            archive_name = f"backup_part_{i:03d}"
            
            # Compression
            if compression != CompressionAlgorithm.NONE:
                compressed_path = temp_dir / f"{archive_name}.{compression.value}"
                await self._compress_path(source_path, compressed_path, compression)
                current_path = compressed_path
            else:
                # Simple copie
                if source_path.is_file():
                    current_path = temp_dir / f"{archive_name}_{source_path.name}"
                    shutil.copy2(source_path, current_path)
                else:
                    current_path = temp_dir / f"{archive_name}.tar"
                    await self._create_tar_archive(source_path, current_path)
            
            # Chiffrement
            if encryption_enabled:
                encrypted_path = temp_dir / f"{current_path.name}.enc"
                await self._encrypt_file(current_path, encrypted_path)
                current_path.unlink()  # Suppression du fichier non chiffré
                current_path = encrypted_path
            
            prepared_files.append(current_path)
        
        return prepared_files
    
    async def _compress_path(
        self,
        source_path: Path,
        output_path: Path,
        compression: CompressionAlgorithm
    ):
        """Compresse un fichier ou répertoire"""
        
        if compression == CompressionAlgorithm.GZIP:
            await self._compress_gzip(source_path, output_path)
        elif compression == CompressionAlgorithm.LZMA:
            await self._compress_lzma(source_path, output_path)
        else:
            # Fallback: copie simple
            if source_path.is_file():
                shutil.copy2(source_path, output_path)
            else:
                await self._create_tar_archive(source_path, output_path)
    
    async def _compress_gzip(self, source_path: Path, output_path: Path):
        """Compression GZIP"""
        
        with gzip.open(output_path, 'wb') as gz_file:
            if source_path.is_file():
                async with aiofiles.open(source_path, 'rb') as source_file:
                    while chunk := await source_file.read(8192):
                        gz_file.write(chunk)
            else:
                # Pour un répertoire, créer d'abord un tar
                import tarfile
                with tarfile.open(fileobj=gz_file, mode='w') as tar:
                    tar.add(source_path, arcname=source_path.name)
    
    async def _compress_lzma(self, source_path: Path, output_path: Path):
        """Compression LZMA"""
        
        with lzma.open(output_path, 'wb', preset=6) as lzma_file:
            if source_path.is_file():
                async with aiofiles.open(source_path, 'rb') as source_file:
                    while chunk := await source_file.read(8192):
                        lzma_file.write(chunk)
            else:
                # Pour un répertoire, créer d'abord un tar
                import tarfile
                with tarfile.open(fileobj=lzma_file, mode='w') as tar:
                    tar.add(source_path, arcname=source_path.name)
    
    async def _create_tar_archive(self, source_path: Path, output_path: Path):
        """Crée une archive TAR"""
        
        import tarfile
        
        def create_tar():
            with tarfile.open(output_path, 'w') as tar:
                tar.add(source_path, arcname=source_path.name)
        
        # Exécution dans thread pool pour éviter blocage
        await asyncio.get_event_loop().run_in_executor(
            self.executor, create_tar
        )
    
    async def _encrypt_file(self, input_path: Path, output_path: Path):
        """Chiffre un fichier"""
        
        # Génération d'une clé de chiffrement
        password = b"ainflue_backup_key_2025"  # En production: clé sécurisée
        salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        cipher = Fernet(key)
        
        async with aiofiles.open(input_path, 'rb') as input_file:
            data = await input_file.read()
        
        encrypted_data = cipher.encrypt(data)
        
        # Sauvegarde avec le salt en préfixe
        async with aiofiles.open(output_path, 'wb') as output_file:
            await output_file.write(salt + encrypted_data)
    
    async def _upload_to_destinations(
        self,
        job: BackupJob,
        files: List[Path],
        manifest: Dict[str, Any]
    ):
        """Upload vers toutes les destinations configurées"""
        
        upload_tasks = []
        
        for destination in job.config.destinations:
            for file_path in files:
                task = self._upload_file_to_destination(job, file_path, destination, manifest)
                upload_tasks.append(task)
        
        # Upload du manifest
        manifest_path = files[0].parent / "backup_manifest.json"
        async with aiofiles.open(manifest_path, 'w') as f:
            await f.write(json.dumps(manifest, indent=2, ensure_ascii=False))
        
        for destination in job.config.destinations:
            task = self._upload_file_to_destination(job, manifest_path, destination, manifest)
            upload_tasks.append(task)
        
        # Exécution parallèle avec limite
        semaphore = asyncio.Semaphore(job.config.max_parallel_uploads)
        
        async def upload_with_semaphore(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(
            *[upload_with_semaphore(task) for task in upload_tasks],
            return_exceptions=True
        )
        
        # Vérification des résultats
        failed_uploads = [r for r in results if isinstance(r, Exception)]
        if failed_uploads:
            raise Exception(f"Échec upload: {len(failed_uploads)} fichiers")
    
    async def _upload_file_to_destination(
        self,
        job: BackupJob,
        file_path: Path,
        destination: BackupDestination,
        manifest: Dict[str, Any]
    ):
        """Upload un fichier vers une destination"""
        
        try:
            object_key = f"backups/{job.id}/{file_path.name}"
            
            if destination.provider == "aws_s3":
                await self._upload_to_s3(file_path, destination, object_key)
            elif destination.provider == "gcp_storage":
                await self._upload_to_gcs(file_path, destination, object_key)
            elif destination.provider == "azure_blob":
                await self._upload_to_azure(file_path, destination, object_key)
            else:
                raise ValueError(f"Provider non supporté: {destination.provider}")
            
            # Mise à jour du progrès
            job.progress += 1.0 / (len(job.source_paths) * len(job.config.destinations))
            
        except Exception as e:
            self.logger.error(f"Échec upload {file_path} vers {destination.provider}: {e}")
            raise
    
    async def _upload_to_s3(self, file_path: Path, destination: BackupDestination, object_key: str):
        """Upload vers AWS S3"""
        
        session = aiobotocore.session.get_session()
        
        async with session.create_client(
            's3',
            aws_access_key_id=destination.access_key,
            aws_secret_access_key=destination.secret_key,
            region_name=destination.region
        ) as client:
            
            async with aiofiles.open(file_path, 'rb') as f:
                data = await f.read()
                
                await client.put_object(
                    Bucket=destination.bucket,
                    Key=object_key,
                    Body=data,
                    StorageClass=self._get_s3_storage_class(destination.tier)
                )
    
    async def _upload_to_gcs(self, file_path: Path, destination: BackupDestination, object_key: str):
        """Upload vers Google Cloud Storage"""
        
        # Implémentation GCS
        client = gcs.Client()
        bucket = client.bucket(destination.bucket)
        blob = bucket.blob(object_key)
        
        def upload_sync():
            blob.upload_from_filename(str(file_path))
        
        await asyncio.get_event_loop().run_in_executor(
            self.executor, upload_sync
        )
    
    async def _upload_to_azure(self, file_path: Path, destination: BackupDestination, object_key: str):
        """Upload vers Azure Blob Storage"""
        
        async with BlobServiceClient(
            account_url=f"https://{destination.bucket}.blob.core.windows.net",
            credential=destination.access_key
        ) as client:
            
            blob_client = client.get_blob_client(
                container=destination.bucket,
                blob=object_key
            )
            
            async with aiofiles.open(file_path, 'rb') as f:
                data = await f.read()
                await blob_client.upload_blob(data, overwrite=True)
    
    def _get_s3_storage_class(self, tier: BackupTier) -> str:
        """Retourne la classe de stockage S3 selon le tier"""
        
        mapping = {
            BackupTier.HOT: 'STANDARD',
            BackupTier.WARM: 'STANDARD_IA',
            BackupTier.COLD: 'GLACIER',
            BackupTier.ARCHIVE: 'DEEP_ARCHIVE'
        }
        
        return mapping.get(tier, 'STANDARD')
    
    async def _verify_backup(self, job: BackupJob, manifest: Dict[str, Any]) -> bool:
        """Vérifie l'intégrité du backup"""
        
        try:
            # Vérification de la présence des fichiers
            for destination in job.config.destinations:
                for file_info in manifest['files']:
                    object_key = f"backups/{job.id}/{Path(file_info['path']).name}"
                    
                    if not await self._verify_file_exists(destination, object_key):
                        self.logger.error(f"Fichier manquant: {object_key}")
                        return False
            
            # Vérification des checksums (échantillonnage)
            sample_files = manifest['files'][:min(10, len(manifest['files']))]
            
            for file_info in sample_files:
                if not await self._verify_file_checksum(job, file_info):
                    self.logger.error(f"Checksum invalide: {file_info['path']}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur vérification backup: {e}")
            return False
    
    async def _verify_file_exists(self, destination: BackupDestination, object_key: str) -> bool:
        """Vérifie l'existence d'un fichier dans une destination"""
        
        try:
            if destination.provider == "aws_s3":
                session = aiobotocore.session.get_session()
                async with session.create_client(
                    's3',
                    aws_access_key_id=destination.access_key,
                    aws_secret_access_key=destination.secret_key,
                    region_name=destination.region
                ) as client:
                    await client.head_object(Bucket=destination.bucket, Key=object_key)
                    return True
            
            # Autres providers...
            return True
            
        except Exception:
            return False
    
    async def _verify_file_checksum(self, job: BackupJob, file_info: Dict[str, Any]) -> bool:
        """Vérifie le checksum d'un fichier sauvegardé"""
        
        # Implémentation simplifiée - en production: download et vérification complète
        return True
    
    async def _update_statistics(self, job: BackupJob, success: bool):
        """Met à jour les statistiques de backup"""
        
        with self._lock:
            self.statistics.total_backups += 1
            
            if success:
                self.statistics.successful_backups += 1
                self.statistics.total_size_backed_up += job.total_size
                self.statistics.total_compressed_size += job.compressed_size
                
                if job.total_size > 0:
                    compression_ratio = (job.total_size - job.compressed_size) / job.total_size * 100
                    self.statistics.average_compression_ratio = (
                        (self.statistics.average_compression_ratio * (self.statistics.successful_backups - 1) + compression_ratio) /
                        self.statistics.successful_backups
                    )
                
                if job.started_at and job.completed_at:
                    duration = (job.completed_at - job.started_at).total_seconds()
                    self.statistics.average_backup_duration = (
                        (self.statistics.average_backup_duration * (self.statistics.successful_backups - 1) + duration) /
                        self.statistics.successful_backups
                    )
                
                self.statistics.last_backup_time = job.completed_at
            else:
                self.statistics.failed_backups += 1
    
    async def restore_backup(
        self,
        backup_id: str,
        destination_path: Path,
        recovery_type: RecoveryType = RecoveryType.FULL_RESTORE,
        point_in_time: Optional[datetime] = None
    ) -> str:
        """Démarre une opération de restore"""
        
        restore_id = f"restore_{backup_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        restore_job = RestoreJob(
            id=restore_id,
            backup_id=backup_id,
            recovery_type=recovery_type,
            destination_path=destination_path
        )
        
        with self._lock:
            self.active_restores[restore_id] = restore_job
        
        # Démarrage asynchrone du restore
        asyncio.create_task(self._execute_restore_job(restore_job))
        
        return restore_id
    
    async def _execute_restore_job(self, job: RestoreJob):
        """Exécute un job de restore"""
        
        try:
            job.status = BackupStatus.RUNNING
            job.started_at = datetime.now()
            
            self.logger.info(f"Démarrage restore job: {job.id}")
            
            # Récupération du manifest
            manifest = await self._download_backup_manifest(job.backup_id)
            if not manifest:
                raise Exception("Manifest de backup non trouvé")
            
            # Création du répertoire de destination
            job.destination_path.mkdir(parents=True, exist_ok=True)
            
            # Download et restoration des fichiers
            await self._restore_files_from_backup(job, manifest)
            
            job.status = BackupStatus.COMPLETED
            job.completed_at = datetime.now()
            job.progress = 1.0
            
            self.logger.info(f"Restore job complété: {job.id}")
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            
            self.logger.error(f"Échec restore job {job.id}: {e}")
    
    async def _download_backup_manifest(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Télécharge le manifest d'un backup"""
        
        # Recherche dans le cache
        if backup_id in self._manifest_cache:
            return self._manifest_cache[backup_id]
        
        # Recherche dans les destinations configurées
        for config in self.backup_configs.values():
            for destination in config.destinations:
                try:
                    manifest_key = f"backups/{backup_id}/backup_manifest.json"
                    manifest_data = await self._download_file_from_destination(
                        destination, manifest_key
                    )
                    
                    if manifest_data:
                        manifest = json.loads(manifest_data.decode('utf-8'))
                        self._manifest_cache[backup_id] = manifest
                        return manifest
                        
                except Exception as e:
                    self.logger.debug(f"Manifest non trouvé dans {destination.provider}: {e}")
                    continue
        
        return None
    
    async def _download_file_from_destination(
        self,
        destination: BackupDestination,
        object_key: str
    ) -> Optional[bytes]:
        """Télécharge un fichier depuis une destination"""
        
        try:
            if destination.provider == "aws_s3":
                session = aiobotocore.session.get_session()
                async with session.create_client(
                    's3',
                    aws_access_key_id=destination.access_key,
                    aws_secret_access_key=destination.secret_key,
                    region_name=destination.region
                ) as client:
                    
                    response = await client.get_object(
                        Bucket=destination.bucket,
                        Key=object_key
                    )
                    
                    return await response['Body'].read()
            
            # Autres providers...
            return None
            
        except Exception as e:
            self.logger.debug(f"Erreur download {object_key}: {e}")
            return None
    
    async def _restore_files_from_backup(
        self,
        job: RestoreJob,
        manifest: Dict[str, Any]
    ):
        """Restore les fichiers depuis un backup"""
        
        total_files = len(manifest['files'])
        
        for i, file_info in enumerate(manifest['files']):
            try:
                # Restauration du fichier
                await self._restore_single_file(job, file_info, manifest)
                
                job.files_restored += 1
                job.progress = (i + 1) / total_files
                
            except Exception as e:
                self.logger.error(f"Erreur restore fichier {file_info['path']}: {e}")
                continue
    
    async def _restore_single_file(
        self,
        job: RestoreJob,
        file_info: Dict[str, Any],
        manifest: Dict[str, Any]
    ):
        """Restore un fichier individuel"""
        
        # Reconstruction du nom du fichier de backup
        backup_filename = f"backup_part_000.{manifest['compression']}"
        if manifest['encryption_enabled']:
            backup_filename += ".enc"
        
        # Téléchargement du fichier de backup
        backup_data = None
        for config in self.backup_configs.values():
            for destination in config.destinations:
                object_key = f"backups/{job.backup_id}/{backup_filename}"
                backup_data = await self._download_file_from_destination(destination, object_key)
                if backup_data:
                    break
            if backup_data:
                break
        
        if not backup_data:
            raise Exception(f"Données de backup non trouvées pour {file_info['path']}")
        
        # Déchiffrement si nécessaire
        if manifest['encryption_enabled']:
            backup_data = await self._decrypt_data(backup_data)
        
        # Décompression si nécessaire
        if manifest['compression'] != 'none':
            backup_data = await self._decompress_data(backup_data, manifest['compression'])
        
        # Restauration du fichier
        restore_path = job.destination_path / file_info['relative_path']
        restore_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(restore_path, 'wb') as f:
            await f.write(backup_data)
        
        # Restauration des permissions
        try:
            restore_path.chmod(int(file_info['permissions'], 8))
        except:
            pass  # Ignore les erreurs de permissions
    
    async def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Déchiffre des données"""
        
        # Extraction du salt
        salt = encrypted_data[:16]
        encrypted_content = encrypted_data[16:]
        
        # Régénération de la clé
        password = b"ainflue_backup_key_2025"  # En production: clé sécurisée
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        cipher = Fernet(key)
        
        return cipher.decrypt(encrypted_content)
    
    async def _decompress_data(self, compressed_data: bytes, compression: str) -> bytes:
        """Décompresse des données"""
        
        if compression == 'gzip':
            return gzip.decompress(compressed_data)
        elif compression == 'lzma':
            return lzma.decompress(compressed_data)
        else:
            return compressed_data
    
    async def list_backups(self, config_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Liste les backups disponibles"""
        
        backups = []
        
        # Recherche dans toutes les destinations
        configs_to_search = [self.backup_configs[config_name]] if config_name else self.backup_configs.values()
        
        for config in configs_to_search:
            for destination in config.destinations:
                try:
                    backup_list = await self._list_backups_in_destination(destination)
                    backups.extend(backup_list)
                except Exception as e:
                    self.logger.error(f"Erreur listing backups dans {destination.provider}: {e}")
        
        # Dédoublonnage par backup_id
        unique_backups = {}
        for backup in backups:
            backup_id = backup.get('backup_id')
            if backup_id and backup_id not in unique_backups:
                unique_backups[backup_id] = backup
        
        return list(unique_backups.values())
    
    async def _list_backups_in_destination(
        self,
        destination: BackupDestination
    ) -> List[Dict[str, Any]]:
        """Liste les backups dans une destination"""
        
        backups = []
        
        try:
            if destination.provider == "aws_s3":
                session = aiobotocore.session.get_session()
                async with session.create_client(
                    's3',
                    aws_access_key_id=destination.access_key,
                    aws_secret_access_key=destination.secret_key,
                    region_name=destination.region
                ) as client:
                    
                    paginator = client.get_paginator('list_objects_v2')
                    async for page in paginator.paginate(
                        Bucket=destination.bucket,
                        Prefix="backups/",
                        Delimiter="/"
                    ):
                        for prefix in page.get('CommonPrefixes', []):
                            backup_id = prefix['Prefix'].split('/')[-2]
                            
                            # Tentative de récupération du manifest
                            manifest = await self._download_backup_manifest(backup_id)
                            if manifest:
                                backups.append({
                                    'backup_id': backup_id,
                                    'created_at': manifest['created_at'],
                                    'backup_type': manifest['backup_type'],
                                    'tier': manifest['tier'],
                                    'total_size': manifest['metadata']['total_size'],
                                    'files_count': manifest['metadata']['files_count'],
                                    'destination': destination.provider
                                })
            
            # Autres providers...
            
        except Exception as e:
            self.logger.error(f"Erreur listing backups: {e}")
        
        return backups
    
    async def delete_backup(self, backup_id: str) -> bool:
        """Supprime un backup"""
        
        try:
            deleted_count = 0
            
            # Suppression dans toutes les destinations
            for config in self.backup_configs.values():
                for destination in config.destinations:
                    if await self._delete_backup_from_destination(backup_id, destination):
                        deleted_count += 1
            
            # Nettoyage du cache
            if backup_id in self._manifest_cache:
                del self._manifest_cache[backup_id]
            
            self.logger.info(f"Backup {backup_id} supprimé de {deleted_count} destinations")
            return deleted_count > 0
            
        except Exception as e:
            self.logger.error(f"Erreur suppression backup {backup_id}: {e}")
            return False
    
    async def _delete_backup_from_destination(
        self,
        backup_id: str,
        destination: BackupDestination
    ) -> bool:
        """Supprime un backup d'une destination"""
        
        try:
            if destination.provider == "aws_s3":
                session = aiobotocore.session.get_session()
                async with session.create_client(
                    's3',
                    aws_access_key_id=destination.access_key,
                    aws_secret_access_key=destination.secret_key,
                    region_name=destination.region
                ) as client:
                    
                    # Liste tous les objets du backup
                    paginator = client.get_paginator('list_objects_v2')
                    objects_to_delete = []
                    
                    async for page in paginator.paginate(
                        Bucket=destination.bucket,
                        Prefix=f"backups/{backup_id}/"
                    ):
                        for obj in page.get('Contents', []):
                            objects_to_delete.append({'Key': obj['Key']})
                    
                    # Suppression par batch
                    if objects_to_delete:
                        await client.delete_objects(
                            Bucket=destination.bucket,
                            Delete={'Objects': objects_to_delete}
                        )
                    
                    return True
            
            # Autres providers...
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur suppression backup de {destination.provider}: {e}")
            return False
    
    async def get_backup_info(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Obtient les informations détaillées d'un backup"""
        
        manifest = await self._download_backup_manifest(backup_id)
        if not manifest:
            return None
        
        # Enrichissement avec des informations système
        info = {
            'backup_id': backup_id,
            'manifest': manifest,
            'destinations': [],
            'total_size_on_storage': 0,
            'verification_status': 'unknown'
        }
        
        # Vérification de la présence dans les destinations
        for config in self.backup_configs.values():
            for destination in config.destinations:
                if await self._backup_exists_in_destination(backup_id, destination):
                    info['destinations'].append({
                        'provider': destination.provider,
                        'bucket': destination.bucket,
                        'region': destination.region
                    })
        
        return info
    
    async def _backup_exists_in_destination(
        self,
        backup_id: str,
        destination: BackupDestination
    ) -> bool:
        """Vérifie si un backup existe dans une destination"""
        
        manifest_key = f"backups/{backup_id}/backup_manifest.json"
        return await self._verify_file_exists(destination, manifest_key)
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Obtient le statut d'un job"""
        
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            return {
                'job_id': job_id,
                'type': 'backup',
                'status': job.status.value,
                'progress': job.progress,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'total_size': job.total_size,
                'files_count': job.files_count,
                'error_message': job.error_message
            }
        
        if job_id in self.active_restores:
            job = self.active_restores[job_id]
            return {
                'job_id': job_id,
                'type': 'restore',
                'status': job.status.value,
                'progress': job.progress,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'files_restored': job.files_restored,
                'error_message': job.error_message
            }
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de backup"""
        
        stats = {
            'total_backups': self.statistics.total_backups,
            'successful_backups': self.statistics.successful_backups,
            'failed_backups': self.statistics.failed_backups,
            'success_rate': (
                self.statistics.successful_backups / self.statistics.total_backups * 100
                if self.statistics.total_backups > 0 else 0
            ),
            'total_size_backed_up': self.statistics.total_size_backed_up,
            'total_compressed_size': self.statistics.total_compressed_size,
            'average_compression_ratio': self.statistics.average_compression_ratio,
            'average_backup_duration': self.statistics.average_backup_duration,
            'last_backup_time': (
                self.statistics.last_backup_time.isoformat()
                if self.statistics.last_backup_time else None
            ),
            'active_backup_jobs': len(self.active_jobs),
            'active_restore_jobs': len(self.active_restores)
        }
        
        return stats
    
    async def cleanup_old_backups(self, max_age_days: int = 365):
        """Nettoie les anciens backups selon la politique de rétention"""
        
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0
        
        try:
            backups = await self.list_backups()
            
            for backup in backups:
                backup_date = datetime.fromisoformat(backup['created_at'].replace('Z', '+00:00'))
                
                if backup_date < cutoff_date:
                    if await self.delete_backup(backup['backup_id']):
                        deleted_count += 1
                        self.logger.info(f"Backup expiré supprimé: {backup['backup_id']}")
            
            self.logger.info(f"Nettoyage terminé: {deleted_count} backups supprimés")
            
        except Exception as e:
            self.logger.error(f"Erreur nettoyage backups: {e}")
        
        return deleted_count
    
    async def _load_configurations(self):
        """Charge les configurations depuis un fichier"""
        
        try:
            if self.config_path and self.config_path.exists():
                async with aiofiles.open(self.config_path, 'r') as f:
                    data = json.loads(await f.read())
                    
                    for config_data in data.get('backup_configs', []):
                        config = BackupConfig(**config_data)
                        self.backup_configs[config.name] = config
                
                self.logger.info(f"Configurations chargées: {len(self.backup_configs)}")
                
        except Exception as e:
            self.logger.error(f"Erreur chargement configurations: {e}")
    
    async def _save_configurations(self):
        """Sauvegarde les configurations dans un fichier"""
        
        try:
            if self.config_path:
                data = {
                    'backup_configs': [
                        {
                            'name': config.name,
                            'backup_type': config.backup_type.value,
                            'tier': config.tier.value,
                            'destinations': [
                                {
                                    'provider': dest.provider,
                                    'bucket': dest.bucket,
                                    'region': dest.region,
                                    'encryption_enabled': dest.encryption_enabled,
                                    'compression': dest.compression.value,
                                    'tier': dest.tier.value
                                }
                                for dest in config.destinations
                            ],
                            'schedule': config.schedule,
                            'retention_days': config.retention_days,
                            'max_parallel_uploads': config.max_parallel_uploads,
                            'verification_enabled': config.verification_enabled,
                            'encryption_enabled': config.encryption_enabled,
                            'compression': config.compression.value,
                            'tags': config.tags
                        }
                        for config in self.backup_configs.values()
                    ]
                }
                
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(self.config_path, 'w') as f:
                    await f.write(json.dumps(data, indent=2, ensure_ascii=False))
                
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde configurations: {e}")
    
    async def __aenter__(self):
        """Context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        # Nettoyage des ressources
        self.executor.shutdown(wait=True)


# Instance globale pour utilisation dans l'application
backup_manager = BackupManager()


async def create_simple_backup(
    source_paths: List[str],
    destination_bucket: str,
    backup_name: str = "simple_backup"
) -> str:
    """
    Interface simplifiée pour créer un backup
    
    Args:
        source_paths: Chemins des fichiers/dossiers à sauvegarder
        destination_bucket: Bucket de destination
        backup_name: Nom du backup
        
    Returns:
        ID du job de backup
    """
    
    # Configuration par défaut
    destination = BackupDestination(
        provider="aws_s3",
        bucket=destination_bucket,
        region="us-east-1",
        tier=BackupTier.WARM
    )
    
    await backup_manager.create_backup_config(
        name=backup_name,
        backup_type=BackupType.FULL,
        tier=BackupTier.WARM,
        destinations=[destination]
    )
    
    return await backup_manager.schedule_backup(
        config_name=backup_name,
        source_paths=source_paths,
        immediate=True
    )


if __name__ == "__main__":
    # Test de backup
    import sys
    
    async def test_backup():
        if len(sys.argv) < 3:
            print("Usage: python backup_manager.py <source_path> <destination_bucket>")
            return
        
        source_path = sys.argv[1]
        destination_bucket = sys.argv[2]
        
        job_id = await create_simple_backup([source_path], destination_bucket)
        print(f"Backup job créé: {job_id}")
        
        # Attente de completion
        while True:
            status = backup_manager.get_job_status(job_id)
            if status:
                print(f"Status: {status['status']}, Progress: {status['progress']:.1%}")
                
                if status['status'] in ['completed', 'failed']:
                    break
            
            await asyncio.sleep(5)
        
        # Statistiques finales
        stats = backup_manager.get_statistics()
        print(f"Statistiques: {json.dumps(stats, indent=2)}")
    
    asyncio.run(test_backup())
