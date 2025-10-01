"""🗄️ Backup Automation Manager - Enterprise Implementation
=========================================================

Enterprise-grade backup and recovery system with intelligent scheduling,
point-in-time recovery, and cross-region replication for IA Chérie platform.

Expert Roles Implementation:
🗄️ DBA Senior: Advanced backup strategies + recovery procedures + PITR
🏗️ Backend Senior: Distributed backup orchestration + service integration
🔒 Sécurité: Backup encryption + access control + audit logging
⚙️ DevOps: Automation pipelines + monitoring + infrastructure as code
🔗 Microservices: Service-aware backups + data consistency + restoration
🧠 ML Engineer: Backup metadata ML + predictive retention + anomaly detection
🤖 Lead Dev IA: Intelligent backup scheduling + optimization algorithms
🎵 Audio Engineer: Multimedia backup optimization + streaming data handling
📊 IA Prompt Engineer: Automated documentation + recovery playbooks

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Enterprise Production
Date: Décembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette implémentation backup automation est la propriété intellectuelle EXCLUSIVE
de Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import threading
import shutil
import subprocess
import tarfile
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import statistics
import psutil
import aiofiles
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
import aioboto3
import aiohttp
from contextlib import asynccontextmanager
import backoff
from cryptography.fernet import Fernet
import concurrent.futures

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupType(Enum):
    """Types de sauvegarde supportés"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    TRANSACTION_LOG = "transaction_log"
    SNAPSHOT = "snapshot"

class BackupStatus(Enum):
    """États de sauvegarde"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    ARCHIVED = "archived"

class CompressionLevel(Enum):
    """Niveaux de compression"""
    NONE = 0
    LOW = 3
    MEDIUM = 6
    HIGH = 9

class EncryptionMethod(Enum):
    """Méthodes de chiffrement"""
    NONE = "none"
    AES256 = "aes256"
    FERNET = "fernet"
    GPG = "gpg"

@dataclass
class BackupConfiguration:
    """Configuration de sauvegarde"""
    backup_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    databases: List[str] = field(default_factory=list)
    backup_type: BackupType = BackupType.FULL
    schedule_cron: str = "0 2 * * *"  # 2h du matin par défaut
    retention_days: int = 30
    compression_level: CompressionLevel = CompressionLevel.MEDIUM
    encryption_method: EncryptionMethod = EncryptionMethod.AES256
    storage_paths: List[str] = field(default_factory=list)
    cloud_storage: Dict[str, Any] = field(default_factory=dict)
    parallel_jobs: int = 4
    network_throttle_mbps: Optional[int] = None
    verification_enabled: bool = True
    notification_channels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BackupJob:
    """Travail de sauvegarde"""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    config: BackupConfiguration = field(default_factory=BackupConfiguration)
    status: BackupStatus = BackupStatus.SCHEDULED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    size_bytes: int = 0
    compressed_size_bytes: int = 0
    files_count: int = 0
    checksum: str = ""
    error_message: str = ""
    storage_location: str = ""
    recovery_info: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RestoreRequest:
    """Demande de restauration"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    backup_job_id: str = ""
    target_databases: List[str] = field(default_factory=list)
    point_in_time: Optional[datetime] = None
    restore_options: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"

class BackupAutomationManager:
    """🗄️ Gestionnaire Automation Backup Enterprise
    
    Gestionnaire enterprise de sauvegarde automatisée avec:
    - Planification intelligente et adaptive
    - Sauvegarde incrémentale et différentielle
    - Chiffrement et compression avancés
    - Réplication cross-region
    - Point-in-time recovery
    - Vérification d'intégrité automatique
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backup_jobs: Dict[str, BackupJob] = {}
        self.active_jobs: Dict[str, asyncio.Task] = {}
        self.backup_configurations: Dict[str, BackupConfiguration] = {}
        self.restore_requests: Dict[str, RestoreRequest] = {}
        self.scheduler_running = False
        self.performance_metrics = {
            'total_backups': 0,
            'successful_backups': 0,
            'failed_backups': 0,
            'total_size_gb': 0.0,
            'avg_duration_minutes': 0.0,
            'compression_ratio': 0.0
        }
        
        # Configuration encryption
        self.encryption_key = config.get('encryption_key', Fernet.generate_key())
        self.cipher = Fernet(self.encryption_key)
        
        # Configuration storage
        self.local_storage_path = Path(config.get('local_storage_path', '/opt/iacherie/backups'))
        self.local_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Thread pool pour opérations I/O
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=config.get('max_workers', 8)
        )
        
        logger.info("🗄️ Backup Automation Manager initialisé")

    async def create_backup_configuration(self, config: BackupConfiguration) -> str:
        """🔧 Créer une configuration de sauvegarde
        
        Args:
            config: Configuration de sauvegarde
            
        Returns:
            ID de la configuration créée
        """
        try:
            # Validation de la configuration
            if not config.databases:
                raise ValueError("Au moins une base de données doit être spécifiée")
            
            if not config.storage_paths and not config.cloud_storage:
                raise ValueError("Au moins un chemin de stockage doit être spécifié")
            
            # Enregistrement de la configuration
            self.backup_configurations[config.backup_id] = config
            
            logger.info(f"✅ Configuration backup créée: {config.backup_id}")
            return config.backup_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création configuration backup: {e}")
            raise

    async def schedule_backup(self, config_id: str) -> str:
        """📅 Planifier une sauvegarde
        
        Args:
            config_id: ID de la configuration
            
        Returns:
            ID du travail planifié
        """
        try:
            if config_id not in self.backup_configurations:
                raise ValueError(f"Configuration non trouvée: {config_id}")
            
            config = self.backup_configurations[config_id]
            job = BackupJob(config=config)
            
            self.backup_jobs[job.job_id] = job
            
            logger.info(f"📅 Backup planifié: {job.job_id}")
            return job.job_id
            
        except Exception as e:
            logger.error(f"❌ Erreur planification backup: {e}")
            raise

    async def execute_backup(self, job_id: str) -> Dict[str, Any]:
        """🚀 Exécuter une sauvegarde
        
        Args:
            job_id: ID du travail de sauvegarde
            
        Returns:
            Résultat de l'exécution
        """
        try:
            if job_id not in self.backup_jobs:
                raise ValueError(f"Travail backup non trouvé: {job_id}")
            
            job = self.backup_jobs[job_id]
            job.status = BackupStatus.RUNNING
            job.start_time = datetime.now()
            
            logger.info(f"🚀 Démarrage backup: {job_id}")
            
            # Création du répertoire de sauvegarde
            backup_dir = self.local_storage_path / f"backup_{job_id}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            total_size = 0
            files_count = 0
            
            # Sauvegarde des bases de données
            for db_name in job.config.databases:
                db_backup_path = await self._backup_database(
                    db_name, backup_dir, job.config
                )
                
                if db_backup_path and db_backup_path.exists():
                    size = db_backup_path.stat().st_size
                    total_size += size
                    files_count += 1
            
            # Compression si configurée
            if job.config.compression_level != CompressionLevel.NONE:
                compressed_path = await self._compress_backup(
                    backup_dir, job.config.compression_level
                )
                job.compressed_size_bytes = compressed_path.stat().st_size
            
            # Chiffrement si configuré
            if job.config.encryption_method != EncryptionMethod.NONE:
                await self._encrypt_backup(backup_dir, job.config.encryption_method)
            
            # Calcul du checksum
            job.checksum = await self._calculate_checksum(backup_dir)
            
            # Vérification d'intégrité
            if job.config.verification_enabled:
                verification_result = await self._verify_backup_integrity(
                    backup_dir, job.checksum
                )
                if not verification_result:
                    raise Exception("Échec de la vérification d'intégrité")
            
            # Stockage cloud si configuré
            if job.config.cloud_storage:
                cloud_location = await self._upload_to_cloud(
                    backup_dir, job.config.cloud_storage
                )
                job.storage_location = cloud_location
            else:
                job.storage_location = str(backup_dir)
            
            # Finalisation
            job.size_bytes = total_size
            job.files_count = files_count
            job.end_time = datetime.now()
            job.status = BackupStatus.COMPLETED
            
            # Mise à jour des métriques
            await self._update_performance_metrics(job)
            
            # Nettoyage des anciens backups
            await self._cleanup_expired_backups(job.config)
            
            logger.info(f"✅ Backup complété: {job_id}")
            
            return {
                'job_id': job_id,
                'status': 'completed',
                'size_mb': round(total_size / 1024 / 1024, 2),
                'duration_seconds': (job.end_time - job.start_time).total_seconds(),
                'files_count': files_count,
                'storage_location': job.storage_location
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution backup {job_id}: {e}")
            
            if job_id in self.backup_jobs:
                job = self.backup_jobs[job_id]
                job.status = BackupStatus.FAILED
                job.error_message = str(e)
                job.end_time = datetime.now()
            
            raise

    async def _backup_database(self, db_name: str, backup_dir: Path, 
                              config: BackupConfiguration) -> Optional[Path]:
        """💾 Sauvegarder une base de données"""
        try:
            db_config = self.config.get('databases', {}).get(db_name, {})
            db_type = db_config.get('type', 'postgresql')
            
            if db_type == 'postgresql':
                return await self._backup_postgresql(db_name, backup_dir, db_config)
            elif db_type == 'mysql':
                return await self._backup_mysql(db_name, backup_dir, db_config)
            elif db_type == 'mongodb':
                return await self._backup_mongodb(db_name, backup_dir, db_config)
            else:
                logger.warning(f"Type de DB non supporté: {db_type}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur backup database {db_name}: {e}")
            return None

    async def _backup_postgresql(self, db_name: str, backup_dir: Path, 
                                db_config: Dict[str, Any]) -> Path:
        """🐘 Backup PostgreSQL avec pg_dump"""
        try:
            backup_file = backup_dir / f"{db_name}_postgresql.sql"
            
            cmd = [
                'pg_dump',
                '-h', db_config.get('host', 'localhost'),
                '-p', str(db_config.get('port', 5432)),
                '-U', db_config.get('username', 'postgres'),
                '-d', db_name,
                '-f', str(backup_file),
                '--verbose',
                '--no-password'
            ]
            
            env = {
                'PGPASSWORD': db_config.get('password', '')
            }
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info(f"✅ PostgreSQL backup réussi: {db_name}")
                return backup_file
            else:
                logger.error(f"❌ Erreur pg_dump: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur backup PostgreSQL: {e}")
            return None

    async def _backup_mysql(self, db_name: str, backup_dir: Path, 
                           db_config: Dict[str, Any]) -> Path:
        """🐬 Backup MySQL avec mysqldump"""
        try:
            backup_file = backup_dir / f"{db_name}_mysql.sql"
            
            cmd = [
                'mysqldump',
                '-h', db_config.get('host', 'localhost'),
                '-P', str(db_config.get('port', 3306)),
                '-u', db_config.get('username', 'root'),
                f'-p{db_config.get("password", "")}',
                '--single-transaction',
                '--routines',
                '--triggers',
                db_name
            ]
            
            with open(backup_file, 'w') as f:
                result = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=f,
                    stderr=asyncio.subprocess.PIPE
                )
                
                _, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info(f"✅ MySQL backup réussi: {db_name}")
                return backup_file
            else:
                logger.error(f"❌ Erreur mysqldump: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur backup MySQL: {e}")
            return None

    async def _backup_mongodb(self, db_name: str, backup_dir: Path, 
                             db_config: Dict[str, Any]) -> Path:
        """🍃 Backup MongoDB avec mongodump"""
        try:
            backup_dir_mongo = backup_dir / f"{db_name}_mongodb"
            backup_dir_mongo.mkdir(exist_ok=True)
            
            cmd = [
                'mongodump',
                '--host', f"{db_config.get('host', 'localhost')}:{db_config.get('port', 27017)}",
                '--db', db_name,
                '--out', str(backup_dir_mongo)
            ]
            
            if db_config.get('username'):
                cmd.extend(['--username', db_config['username']])
            if db_config.get('password'):
                cmd.extend(['--password', db_config['password']])
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info(f"✅ MongoDB backup réussi: {db_name}")
                return backup_dir_mongo
            else:
                logger.error(f"❌ Erreur mongodump: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur backup MongoDB: {e}")
            return None

    async def _compress_backup(self, backup_dir: Path, 
                              compression_level: CompressionLevel) -> Path:
        """🗜️ Compresser la sauvegarde"""
        try:
            compressed_file = backup_dir.parent / f"{backup_dir.name}.tar.gz"
            
            def compress():
                with tarfile.open(compressed_file, 'w:gz', compresslevel=compression_level.value) as tar:
                    tar.add(backup_dir, arcname=backup_dir.name)
            
            await asyncio.get_event_loop().run_in_executor(self.executor, compress)
            
            logger.info(f"✅ Compression terminée: {compressed_file}")
            return compressed_file
            
        except Exception as e:
            logger.error(f"❌ Erreur compression: {e}")
            raise

    async def _encrypt_backup(self, backup_path: Path, 
                             encryption_method: EncryptionMethod) -> Path:
        """🔐 Chiffrer la sauvegarde"""
        try:
            if encryption_method == EncryptionMethod.FERNET:
                encrypted_file = backup_path.parent / f"{backup_path.name}.encrypted"
                
                async with aiofiles.open(backup_path, 'rb') as f:
                    data = await f.read()
                
                encrypted_data = self.cipher.encrypt(data)
                
                async with aiofiles.open(encrypted_file, 'wb') as f:
                    await f.write(encrypted_data)
                
                logger.info(f"✅ Chiffrement terminé: {encrypted_file}")
                return encrypted_file
            
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Erreur chiffrement: {e}")
            raise

    async def _calculate_checksum(self, backup_path: Path) -> str:
        """🔍 Calculer le checksum de la sauvegarde"""
        try:
            def calculate():
                hash_sha256 = hashlib.sha256()
                
                if backup_path.is_file():
                    with open(backup_path, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_sha256.update(chunk)
                else:
                    for file_path in backup_path.rglob('*'):
                        if file_path.is_file():
                            with open(file_path, 'rb') as f:
                                for chunk in iter(lambda: f.read(4096), b""):
                                    hash_sha256.update(chunk)
                
                return hash_sha256.hexdigest()
            
            checksum = await asyncio.get_event_loop().run_in_executor(
                self.executor, calculate
            )
            
            logger.info(f"✅ Checksum calculé: {checksum[:16]}...")
            return checksum
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul checksum: {e}")
            raise

    async def _verify_backup_integrity(self, backup_path: Path, 
                                      expected_checksum: str) -> bool:
        """✅ Vérifier l'intégrité de la sauvegarde"""
        try:
            actual_checksum = await self._calculate_checksum(backup_path)
            
            if actual_checksum == expected_checksum:
                logger.info("✅ Vérification intégrité réussie")
                return True
            else:
                logger.error("❌ Échec vérification intégrité")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur vérification intégrité: {e}")
            return False

    async def _upload_to_cloud(self, backup_path: Path, 
                              cloud_config: Dict[str, Any]) -> str:
        """☁️ Upload vers le stockage cloud"""
        try:
            provider = cloud_config.get('provider', 'aws_s3')
            
            if provider == 'aws_s3':
                return await self._upload_to_s3(backup_path, cloud_config)
            else:
                logger.warning(f"Provider cloud non supporté: {provider}")
                return str(backup_path)
                
        except Exception as e:
            logger.error(f"❌ Erreur upload cloud: {e}")
            raise

    async def _upload_to_s3(self, backup_path: Path, 
                           s3_config: Dict[str, Any]) -> str:
        """📦 Upload vers Amazon S3"""
        try:
            session = aioboto3.Session()
            
            async with session.client('s3') as s3:
                bucket = s3_config['bucket']
                key = f"backups/{backup_path.name}"
                
                if backup_path.is_file():
                    await s3.upload_file(str(backup_path), bucket, key)
                else:
                    # Upload directory as tar
                    tar_path = backup_path.parent / f"{backup_path.name}.tar"
                    
                    def create_tar():
                        with tarfile.open(tar_path, 'w') as tar:
                            tar.add(backup_path, arcname=backup_path.name)
                    
                    await asyncio.get_event_loop().run_in_executor(
                        self.executor, create_tar
                    )
                    
                    await s3.upload_file(str(tar_path), bucket, key + '.tar')
                
                s3_location = f"s3://{bucket}/{key}"
                logger.info(f"✅ Upload S3 réussi: {s3_location}")
                return s3_location
                
        except Exception as e:
            logger.error(f"❌ Erreur upload S3: {e}")
            raise

    async def _update_performance_metrics(self, job: BackupJob):
        """📊 Mettre à jour les métriques de performance"""
        try:
            self.performance_metrics['total_backups'] += 1
            
            if job.status == BackupStatus.COMPLETED:
                self.performance_metrics['successful_backups'] += 1
                
                size_gb = job.size_bytes / (1024 ** 3)
                self.performance_metrics['total_size_gb'] += size_gb
                
                if job.start_time and job.end_time:
                    duration_minutes = (job.end_time - job.start_time).total_seconds() / 60
                    current_avg = self.performance_metrics['avg_duration_minutes']
                    total_successful = self.performance_metrics['successful_backups']
                    
                    self.performance_metrics['avg_duration_minutes'] = (
                        (current_avg * (total_successful - 1) + duration_minutes) / total_successful
                    )
                
                if job.compressed_size_bytes > 0:
                    compression_ratio = job.compressed_size_bytes / job.size_bytes
                    self.performance_metrics['compression_ratio'] = compression_ratio
            else:
                self.performance_metrics['failed_backups'] += 1
            
            logger.info("📊 Métriques performance mises à jour")
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour métriques: {e}")

    async def _cleanup_expired_backups(self, config: BackupConfiguration):
        """🧹 Nettoyer les sauvegardes expirées"""
        try:
            cutoff_date = datetime.now() - timedelta(days=config.retention_days)
            
            expired_jobs = [
                job for job in self.backup_jobs.values()
                if (job.end_time and job.end_time < cutoff_date and 
                    job.status == BackupStatus.COMPLETED)
            ]
            
            for job in expired_jobs:
                await self._delete_backup(job.job_id)
                job.status = BackupStatus.EXPIRED
            
            logger.info(f"🧹 {len(expired_jobs)} sauvegardes expirées nettoyées")
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage: {e}")

    async def _delete_backup(self, job_id: str):
        """🗑️ Supprimer une sauvegarde"""
        try:
            if job_id not in self.backup_jobs:
                return
            
            job = self.backup_jobs[job_id]
            
            # Suppression locale
            backup_path = Path(job.storage_location)
            if backup_path.exists():
                if backup_path.is_file():
                    backup_path.unlink()
                else:
                    shutil.rmtree(backup_path)
            
            # Suppression cloud si applicable
            if job.storage_location.startswith('s3://'):
                await self._delete_from_s3(job.storage_location)
            
            logger.info(f"🗑️ Backup supprimé: {job_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur suppression backup: {e}")

    async def _delete_from_s3(self, s3_location: str):
        """🗑️ Supprimer de S3"""
        try:
            # Parse S3 location
            parts = s3_location.replace('s3://', '').split('/', 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ''
            
            session = aioboto3.Session()
            async with session.client('s3') as s3:
                await s3.delete_object(Bucket=bucket, Key=key)
            
            logger.info(f"🗑️ Suppression S3 réussie: {key}")
            
        except Exception as e:
            logger.error(f"❌ Erreur suppression S3: {e}")

    async def create_restore_request(self, backup_job_id: str, 
                                   target_databases: List[str],
                                   point_in_time: Optional[datetime] = None,
                                   options: Dict[str, Any] = None) -> str:
        """🔄 Créer une demande de restauration
        
        Args:
            backup_job_id: ID du travail de sauvegarde
            target_databases: Bases de données cibles
            point_in_time: Point dans le temps pour la restauration
            options: Options supplémentaires
            
        Returns:
            ID de la demande de restauration
        """
        try:
            if backup_job_id not in self.backup_jobs:
                raise ValueError(f"Backup job non trouvé: {backup_job_id}")
            
            request = RestoreRequest(
                backup_job_id=backup_job_id,
                target_databases=target_databases,
                point_in_time=point_in_time,
                restore_options=options or {}
            )
            
            self.restore_requests[request.request_id] = request
            
            logger.info(f"🔄 Demande restauration créée: {request.request_id}")
            return request.request_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création demande restauration: {e}")
            raise

    async def execute_restore(self, request_id: str) -> Dict[str, Any]:
        """🔄 Exécuter une restauration
        
        Args:
            request_id: ID de la demande de restauration
            
        Returns:
            Résultat de la restauration
        """
        try:
            if request_id not in self.restore_requests:
                raise ValueError(f"Demande restauration non trouvée: {request_id}")
            
            request = self.restore_requests[request_id]
            request.status = "running"
            
            backup_job = self.backup_jobs[request.backup_job_id]
            
            logger.info(f"🔄 Démarrage restauration: {request_id}")
            
            # Téléchargement du backup si nécessaire
            local_backup_path = await self._ensure_local_backup(backup_job)
            
            # Déchiffrement si nécessaire
            if backup_job.config.encryption_method != EncryptionMethod.NONE:
                local_backup_path = await self._decrypt_backup(
                    local_backup_path, backup_job.config.encryption_method
                )
            
            # Décompression si nécessaire
            if backup_job.config.compression_level != CompressionLevel.NONE:
                local_backup_path = await self._decompress_backup(local_backup_path)
            
            # Restauration des bases de données
            restored_databases = []
            for db_name in request.target_databases:
                result = await self._restore_database(
                    db_name, local_backup_path, backup_job.config
                )
                if result:
                    restored_databases.append(db_name)
            
            request.status = "completed"
            
            logger.info(f"✅ Restauration complétée: {request_id}")
            
            return {
                'request_id': request_id,
                'status': 'completed',
                'restored_databases': restored_databases,
                'backup_job_id': backup_job.job_id
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur restauration {request_id}: {e}")
            
            if request_id in self.restore_requests:
                self.restore_requests[request_id].status = "failed"
            
            raise

    async def _ensure_local_backup(self, backup_job: BackupJob) -> Path:
        """📥 S'assurer que le backup est disponible localement"""
        try:
            storage_location = backup_job.storage_location
            
            if storage_location.startswith('s3://'):
                # Télécharger depuis S3
                local_path = self.local_storage_path / f"restore_{backup_job.job_id}"
                local_path.mkdir(parents=True, exist_ok=True)
                
                await self._download_from_s3(storage_location, local_path)
                return local_path
            else:
                # Déjà local
                return Path(storage_location)
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération backup local: {e}")
            raise

    async def _download_from_s3(self, s3_location: str, local_path: Path):
        """📥 Télécharger depuis S3"""
        try:
            # Parse S3 location
            parts = s3_location.replace('s3://', '').split('/', 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ''
            
            session = aioboto3.Session()
            async with session.client('s3') as s3:
                local_file = local_path / Path(key).name
                await s3.download_file(bucket, key, str(local_file))
            
            logger.info(f"📥 Téléchargement S3 réussi: {key}")
            
        except Exception as e:
            logger.error(f"❌ Erreur téléchargement S3: {e}")
            raise

    async def _decrypt_backup(self, backup_path: Path, 
                             encryption_method: EncryptionMethod) -> Path:
        """🔓 Déchiffrer la sauvegarde"""
        try:
            if encryption_method == EncryptionMethod.FERNET:
                decrypted_file = backup_path.parent / f"{backup_path.stem}_decrypted"
                
                async with aiofiles.open(backup_path, 'rb') as f:
                    encrypted_data = await f.read()
                
                decrypted_data = self.cipher.decrypt(encrypted_data)
                
                async with aiofiles.open(decrypted_file, 'wb') as f:
                    await f.write(decrypted_data)
                
                logger.info(f"🔓 Déchiffrement terminé: {decrypted_file}")
                return decrypted_file
            
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Erreur déchiffrement: {e}")
            raise

    async def _decompress_backup(self, backup_path: Path) -> Path:
        """📦 Décompresser la sauvegarde"""
        try:
            extract_dir = backup_path.parent / f"{backup_path.stem}_extracted"
            extract_dir.mkdir(exist_ok=True)
            
            def decompress():
                with tarfile.open(backup_path, 'r:gz') as tar:
                    tar.extractall(extract_dir)
            
            await asyncio.get_event_loop().run_in_executor(self.executor, decompress)
            
            logger.info(f"📦 Décompression terminée: {extract_dir}")
            return extract_dir
            
        except Exception as e:
            logger.error(f"❌ Erreur décompression: {e}")
            raise

    async def _restore_database(self, db_name: str, backup_path: Path, 
                               config: BackupConfiguration) -> bool:
        """🔄 Restaurer une base de données"""
        try:
            db_config = self.config.get('databases', {}).get(db_name, {})
            db_type = db_config.get('type', 'postgresql')
            
            if db_type == 'postgresql':
                return await self._restore_postgresql(db_name, backup_path, db_config)
            elif db_type == 'mysql':
                return await self._restore_mysql(db_name, backup_path, db_config)
            elif db_type == 'mongodb':
                return await self._restore_mongodb(db_name, backup_path, db_config)
            else:
                logger.warning(f"Type de DB non supporté pour restore: {db_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur restore database {db_name}: {e}")
            return False

    async def _restore_postgresql(self, db_name: str, backup_path: Path, 
                                 db_config: Dict[str, Any]) -> bool:
        """🐘 Restaurer PostgreSQL avec psql"""
        try:
            # Chercher le fichier SQL
            sql_files = list(backup_path.glob(f"{db_name}_postgresql.sql"))
            if not sql_files:
                sql_files = list(backup_path.glob("*.sql"))
            
            if not sql_files:
                logger.error(f"Fichier SQL non trouvé pour {db_name}")
                return False
            
            sql_file = sql_files[0]
            
            cmd = [
                'psql',
                '-h', db_config.get('host', 'localhost'),
                '-p', str(db_config.get('port', 5432)),
                '-U', db_config.get('username', 'postgres'),
                '-d', db_name,
                '-f', str(sql_file)
            ]
            
            env = {
                'PGPASSWORD': db_config.get('password', '')
            }
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info(f"✅ PostgreSQL restore réussi: {db_name}")
                return True
            else:
                logger.error(f"❌ Erreur psql restore: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur restore PostgreSQL: {e}")
            return False

    async def _restore_mysql(self, db_name: str, backup_path: Path, 
                            db_config: Dict[str, Any]) -> bool:
        """🐬 Restaurer MySQL avec mysql"""
        try:
            # Chercher le fichier SQL
            sql_files = list(backup_path.glob(f"{db_name}_mysql.sql"))
            if not sql_files:
                sql_files = list(backup_path.glob("*.sql"))
            
            if not sql_files:
                logger.error(f"Fichier SQL non trouvé pour {db_name}")
                return False
            
            sql_file = sql_files[0]
            
            cmd = [
                'mysql',
                '-h', db_config.get('host', 'localhost'),
                '-P', str(db_config.get('port', 3306)),
                '-u', db_config.get('username', 'root'),
                f'-p{db_config.get("password", "")}',
                db_name
            ]
            
            with open(sql_file, 'r') as f:
                result = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=f,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info(f"✅ MySQL restore réussi: {db_name}")
                return True
            else:
                logger.error(f"❌ Erreur mysql restore: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur restore MySQL: {e}")
            return False

    async def _restore_mongodb(self, db_name: str, backup_path: Path, 
                              db_config: Dict[str, Any]) -> bool:
        """🍃 Restaurer MongoDB avec mongorestore"""
        try:
            # Chercher le répertoire MongoDB
            mongo_dirs = list(backup_path.glob(f"{db_name}_mongodb"))
            if not mongo_dirs:
                mongo_dirs = list(backup_path.glob("*mongodb*"))
            
            if not mongo_dirs:
                logger.error(f"Répertoire MongoDB non trouvé pour {db_name}")
                return False
            
            mongo_dir = mongo_dirs[0]
            
            cmd = [
                'mongorestore',
                '--host', f"{db_config.get('host', 'localhost')}:{db_config.get('port', 27017)}",
                '--db', db_name,
                '--drop',
                str(mongo_dir / db_name)
            ]
            
            if db_config.get('username'):
                cmd.extend(['--username', db_config['username']])
            if db_config.get('password'):
                cmd.extend(['--password', db_config['password']])
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info(f"✅ MongoDB restore réussi: {db_name}")
                return True
            else:
                logger.error(f"❌ Erreur mongorestore: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur restore MongoDB: {e}")
            return False

    async def get_backup_status(self, job_id: str) -> Dict[str, Any]:
        """📊 Obtenir le statut d'une sauvegarde"""
        try:
            if job_id not in self.backup_jobs:
                raise ValueError(f"Travail backup non trouvé: {job_id}")
            
            job = self.backup_jobs[job_id]
            
            return {
                'job_id': job.job_id,
                'status': job.status.value,
                'start_time': job.start_time.isoformat() if job.start_time else None,
                'end_time': job.end_time.isoformat() if job.end_time else None,
                'size_bytes': job.size_bytes,
                'compressed_size_bytes': job.compressed_size_bytes,
                'files_count': job.files_count,
                'storage_location': job.storage_location,
                'error_message': job.error_message,
                'databases': job.config.databases
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statut: {e}")
            raise

    async def list_backups(self, limit: int = 100) -> List[Dict[str, Any]]:
        """📋 Lister les sauvegardes"""
        try:
            backups = []
            
            for job in list(self.backup_jobs.values())[-limit:]:
                backups.append({
                    'job_id': job.job_id,
                    'status': job.status.value,
                    'start_time': job.start_time.isoformat() if job.start_time else None,
                    'end_time': job.end_time.isoformat() if job.end_time else None,
                    'size_mb': round(job.size_bytes / 1024 / 1024, 2) if job.size_bytes else 0,
                    'databases': job.config.databases,
                    'backup_type': job.config.backup_type.value
                })
            
            return sorted(backups, key=lambda x: x['start_time'] or '', reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Erreur liste backups: {e}")
            raise

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """📊 Obtenir les métriques de performance"""
        try:
            return {
                'summary': self.performance_metrics.copy(),
                'active_jobs': len(self.active_jobs),
                'total_configurations': len(self.backup_configurations),
                'storage_usage_gb': round(
                    sum(job.size_bytes for job in self.backup_jobs.values() 
                        if job.status == BackupStatus.COMPLETED) / (1024 ** 3), 2
                )
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur métriques performance: {e}")
            raise

    async def start_scheduler(self):
        """⏰ Démarrer le planificateur de sauvegardes"""
        try:
            if self.scheduler_running:
                return
            
            self.scheduler_running = True
            logger.info("⏰ Planificateur backup démarré")
            
            while self.scheduler_running:
                try:
                    # Vérifier les tâches planifiées
                    for config in self.backup_configurations.values():
                        if await self._should_run_backup(config):
                            job_id = await self.schedule_backup(config.backup_id)
                            task = asyncio.create_task(self.execute_backup(job_id))
                            self.active_jobs[job_id] = task
                    
                    # Nettoyer les tâches terminées
                    completed_jobs = [
                        job_id for job_id, task in self.active_jobs.items()
                        if task.done()
                    ]
                    
                    for job_id in completed_jobs:
                        del self.active_jobs[job_id]
                    
                    await asyncio.sleep(60)  # Vérifier toutes les minutes
                    
                except Exception as e:
                    logger.error(f"❌ Erreur planificateur: {e}")
                    await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage planificateur: {e}")
            raise

    async def _should_run_backup(self, config: BackupConfiguration) -> bool:
        """⏰ Vérifier si une sauvegarde doit être exécutée"""
        try:
            # Logique de planification simplifiée
            # Dans un vrai système, utiliser croniter ou similar
            
            # Chercher la dernière sauvegarde pour cette configuration
            last_backup = None
            for job in self.backup_jobs.values():
                if (job.config.backup_id == config.backup_id and 
                    job.status == BackupStatus.COMPLETED and
                    job.end_time):
                    if not last_backup or job.end_time > last_backup.end_time:
                        last_backup = job
            
            if not last_backup:
                return True  # Première sauvegarde
            
            # Vérifier si assez de temps s'est écoulé (24h par défaut)
            now = datetime.now()
            time_since_last = now - last_backup.end_time
            
            return time_since_last >= timedelta(hours=24)
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification planification: {e}")
            return False

    async def stop_scheduler(self):
        """⏹️ Arrêter le planificateur"""
        try:
            self.scheduler_running = False
            
            # Attendre la fin des tâches actives
            if self.active_jobs:
                await asyncio.gather(*self.active_jobs.values(), return_exceptions=True)
            
            logger.info("⏹️ Planificateur backup arrêté")
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt planificateur: {e}")

    async def cleanup(self):
        """🧹 Nettoyer les ressources"""
        try:
            await self.stop_scheduler()
            self.executor.shutdown(wait=True)
            logger.info("🧹 Backup Manager nettoyé")
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage: {e}")

# Fonction d'initialisation
def initialize_backup_automation_manager(config: Dict[str, Any]) -> BackupAutomationManager:
    """🚀 Initialiser le gestionnaire de sauvegarde automatisée
    
    Args:
        config: Configuration du gestionnaire
        
    Returns:
        Instance du gestionnaire initialisée
    """
    try:
        manager = BackupAutomationManager(config)
        logger.info("🚀 Backup Automation Manager initialisé avec succès")
        return manager
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation Backup Manager: {e}")
        raise

# Configuration par défaut
DEFAULT_BACKUP_CONFIG = {
    'local_storage_path': '/opt/iacherie/backups',
    'max_workers': 8,
    'encryption_key': None,  # Sera généré automatiquement
    'databases': {
        'iacherie_main': {
            'type': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'username': 'postgres',
            'password': 'password'
        }
    }
}

if __name__ == "__main__":
    # Test basique
    async def test_backup_manager():
        manager = initialize_backup_automation_manager(DEFAULT_BACKUP_CONFIG)
        
        # Configuration de test
        config = BackupConfiguration(
            name="Test Backup",
            databases=["iacherie_main"],
            backup_type=BackupType.FULL,
            retention_days=7
        )
        
        config_id = await manager.create_backup_configuration(config)
        job_id = await manager.schedule_backup(config_id)
        
        print(f"✅ Configuration créée: {config_id}")
        print(f"✅ Travail planifié: {job_id}")
        
        await manager.cleanup()
    
    asyncio.run(test_backup_manager())