"""📋 Models - Backup System Data Models
====================================
Module: backend/data_management/backups/models.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Data Models - Enterprise Production-Ready
Responsibility: Modèles de données centralisés pour système de sauvegarde
======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class BackupType(Enum):
    """Types de sauvegarde"""    FULL = "full"                    # Sauvegarde complète
    INCREMENTAL = "incremental"      # Sauvegarde incrémentale
    DIFFERENTIAL = "differential"    # Sauvegarde différentielle
    SNAPSHOT = "snapshot"            # Instantané
    MIRROR = "mirror"               # Miroir synchronisé
    ARCHIVE = "archive"             # Archive
    CLONE = "clone"                 # Clone complet


class BackupStatus(Enum):
    """États de sauvegarde"""    PENDING = "pending"             # En attente
    RUNNING = "running"             # En cours
    PAUSED = "paused"              # En pause
    COMPLETED = "completed"         # Terminée avec succès
    FAILED = "failed"              # Échouée
    CANCELLED = "cancelled"         # Annulée
    CORRUPTED = "corrupted"        # Corrompue
    VERIFYING = "verifying"        # En cours de vérification
    ARCHIVED = "archived"          # Archivée


class BackupPriority(Enum):
    """Priorités de sauvegarde"""    CRITICAL = "critical"          # Critique (immédiat)
    HIGH = "high"                  # Haute priorité
    NORMAL = "normal"              # Priorité normale
    LOW = "low"                    # Basse priorité
    BACKGROUND = "background"      # Arrière-plan


class StorageClass(Enum):
    """Classes de stockage"""    HOT = "hot"                    # Accès immédiat (SSD)
    WARM = "warm"                  # Accès rapide (HDD)
    COLD = "cold"                  # Accès lent (tape/cloud)
    FROZEN = "frozen"              # Archivage long terme
    GLACIER = "glacier"            # Archivage très long terme


class CompressionAlgorithm(Enum):
    """Algorithmes de compression"""    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"
    ZSTD = "zstd"
    LZ4 = "lz4"


class EncryptionAlgorithm(Enum):
    """Algorithmes de chiffrement"""    NONE = "none"
    AES_128 = "aes-128"
    AES_256 = "aes-256"
    RSA_2048 = "rsa-2048"
    RSA_4096 = "rsa-4096"


@dataclass
class FileMetadata:
    """Métadonnées d'un fichier"""    path: str
    size: int
    checksum: str
    checksum_algorithm: str = "sha256"
    mime_type: Optional[str] = None
    permissions: Optional[str] = None
    owner: Optional[str] = None
    group: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    accessed_at: Optional[datetime] = None
    is_directory: bool = False
    is_symlink: bool = False
    symlink_target: Optional[str] = None
    compression_algorithm: CompressionAlgorithm = CompressionAlgorithm.NONE
    compression_ratio: Optional[float] = None
    encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.NONE
    encryption_key_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "path": self.path,
            "size": self.size,
            "checksum": self.checksum,
            "checksum_algorithm": self.checksum_algorithm,
            "mime_type": self.mime_type,
            "permissions": self.permissions,
            "owner": self.owner,
            "group": self.group,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "accessed_at": self.accessed_at.isoformat() if self.accessed_at else None,
            "is_directory": self.is_directory,
            "is_symlink": self.is_symlink,
            "symlink_target": self.symlink_target,
            "compression_algorithm": self.compression_algorithm.value,
            "compression_ratio": self.compression_ratio,
            "encryption_algorithm": self.encryption_algorithm.value,
            "encryption_key_id": self.encryption_key_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileMetadata':
        """Crée depuis un dictionnaire"""        return cls(
            path=data["path"],
            size=data["size"],
            checksum=data["checksum"],
            checksum_algorithm=data.get("checksum_algorithm", "sha256"),
            mime_type=data.get("mime_type"),
            permissions=data.get("permissions"),
            owner=data.get("owner"),
            group=data.get("group"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            modified_at=datetime.fromisoformat(data["modified_at"]) if data.get("modified_at") else None,
            accessed_at=datetime.fromisoformat(data["accessed_at"]) if data.get("accessed_at") else None,
            is_directory=data.get("is_directory", False),
            is_symlink=data.get("is_symlink", False),
            symlink_target=data.get("symlink_target"),
            compression_algorithm=CompressionAlgorithm(data.get("compression_algorithm", "none")),
            compression_ratio=data.get("compression_ratio"),
            encryption_algorithm=EncryptionAlgorithm(data.get("encryption_algorithm", "none")),
            encryption_key_id=data.get("encryption_key_id"),
            metadata=data.get("metadata", {})
        )


@dataclass
class BackupJob:
    """Tâche de sauvegarde"""    job_id: str
    user_id: str
    backup_type: BackupType
    priority: BackupPriority = BackupPriority.NORMAL
    source_paths: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    include_patterns: List[str] = field(default_factory=list)
    destination: Optional[str] = None
    storage_class: StorageClass = StorageClass.WARM
    compression_algorithm: CompressionAlgorithm = CompressionAlgorithm.ZSTD
    encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256
    encryption_key_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    bandwidth_limit: Optional[int] = None  # bytes/sec
    verify_integrity: bool = True
    send_notifications: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "job_id": self.job_id,
            "user_id": self.user_id,
            "backup_type": self.backup_type.value,
            "priority": self.priority.value,
            "source_paths": self.source_paths,
            "exclude_patterns": self.exclude_patterns,
            "include_patterns": self.include_patterns,
            "destination": self.destination,
            "storage_class": self.storage_class.value,
            "compression_algorithm": self.compression_algorithm.value,
            "encryption_algorithm": self.encryption_algorithm.value,
            "encryption_key_id": self.encryption_key_id,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "bandwidth_limit": self.bandwidth_limit,
            "verify_integrity": self.verify_integrity,
            "send_notifications": self.send_notifications,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class BackupProgress:
    """Progression d'une sauvegarde"""    backup_id: str
    job_id: str
    status: BackupStatus
    files_total: int = 0
    files_processed: int = 0
    files_skipped: int = 0
    files_failed: int = 0
    bytes_total: int = 0
    bytes_processed: int = 0
    bytes_compressed: int = 0
    compression_ratio: float = 0.0
    transfer_speed: float = 0.0  # bytes/sec
    eta_seconds: Optional[int] = None
    current_file: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def progress_percentage(self) -> float:
        """Pourcentage de progression"""        if self.files_total == 0:
            return 0.0
        return (self.files_processed / self.files_total) * 100
    
    @property
    def bytes_percentage(self) -> float:
        """Pourcentage de bytes traités"""        if self.bytes_total == 0:
            return 0.0
        return (self.bytes_processed / self.bytes_total) * 100
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Durée d'exécution"""        if not self.started_at:
            return None
        end_time = self.completed_at or datetime.now()
        return end_time - self.started_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "backup_id": self.backup_id,
            "job_id": self.job_id,
            "status": self.status.value,
            "files_total": self.files_total,
            "files_processed": self.files_processed,
            "files_skipped": self.files_skipped,
            "files_failed": self.files_failed,
            "bytes_total": self.bytes_total,
            "bytes_processed": self.bytes_processed,
            "bytes_compressed": self.bytes_compressed,
            "compression_ratio": self.compression_ratio,
            "transfer_speed": self.transfer_speed,
            "eta_seconds": self.eta_seconds,
            "current_file": self.current_file,
            "progress_percentage": self.progress_percentage,
            "bytes_percentage": self.bytes_percentage,
            "errors": self.errors,
            "warnings": self.warnings,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration.total_seconds() if self.duration else None
        }


@dataclass
class BackupMetadata:
    """Métadonnées complètes d'une sauvegarde"""    backup_id: str
    user_id: str
    job_id: Optional[str] = None
    backup_type: BackupType = BackupType.FULL
    status: BackupStatus = BackupStatus.PENDING
    priority: BackupPriority = BackupPriority.NORMAL
    
    # Informations de contenu
    source_paths: List[str] = field(default_factory=list)
    files: List[FileMetadata] = field(default_factory=list)
    total_files: int = 0
    total_size: int = 0  # bytes
    compressed_size: int = 0  # bytes
    
    # Algorithmes et sécurité
    compression_algorithm: CompressionAlgorithm = CompressionAlgorithm.ZSTD
    compression_ratio: float = 0.0
    encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256
    encryption_key_id: Optional[str] = None
    
    # Stockage
    storage_provider: Optional[str] = None
    storage_class: StorageClass = StorageClass.WARM
    storage_path: Optional[str] = None
    storage_cost: Optional[float] = None  # coût en devise
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Intégrité et vérification
    checksum: Optional[str] = None
    checksum_algorithm: str = "sha256"
    verified_at: Optional[datetime] = None
    verification_status: Optional[str] = None
    
    # Parent/child relationships
    parent_backup_id: Optional[str] = None  # Pour incrémentales
    child_backup_ids: List[str] = field(default_factory=list)
    
    # Statistiques et performance
    transfer_speed: float = 0.0  # bytes/sec
    cpu_time: float = 0.0  # seconds
    memory_peak: int = 0  # bytes
    
    # Erreurs et logs
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    log_path: Optional[str] = None
    
    # Métadonnées étendues
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_completed(self) -> bool:
        """Vérifie si la sauvegarde est terminée"""        return self.status == BackupStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Vérifie si la sauvegarde a échoué"""        return self.status in [BackupStatus.FAILED, BackupStatus.CORRUPTED]
    
    @property
    def is_running(self) -> bool:
        """Vérifie si la sauvegarde est en cours"""        return self.status in [BackupStatus.RUNNING, BackupStatus.VERIFYING]
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Durée d'exécution"""        if not self.started_at:
            return None
        end_time = self.completed_at or datetime.now()
        return end_time - self.started_at
    
    @property
    def size_gb(self) -> float:
        """Taille en GB"""        return self.total_size / (1024**3)
    
    @property
    def compressed_size_gb(self) -> float:
        """Taille compressée en GB"""        return self.compressed_size / (1024**3)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "backup_id": self.backup_id,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "backup_type": self.backup_type.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "source_paths": self.source_paths,
            "files": [f.to_dict() for f in self.files],
            "total_files": self.total_files,
            "total_size": self.total_size,
            "compressed_size": self.compressed_size,
            "compression_algorithm": self.compression_algorithm.value,
            "compression_ratio": self.compression_ratio,
            "encryption_algorithm": self.encryption_algorithm.value,
            "encryption_key_id": self.encryption_key_id,
            "storage_provider": self.storage_provider,
            "storage_class": self.storage_class.value,
            "storage_path": self.storage_path,
            "storage_cost": self.storage_cost,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "checksum": self.checksum,
            "checksum_algorithm": self.checksum_algorithm,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "verification_status": self.verification_status,
            "parent_backup_id": self.parent_backup_id,
            "child_backup_ids": self.child_backup_ids,
            "transfer_speed": self.transfer_speed,
            "cpu_time": self.cpu_time,
            "memory_peak": self.memory_peak,
            "errors": self.errors,
            "warnings": self.warnings,
            "log_path": self.log_path,
            "tags": self.tags,
            "description": self.description,
            "metadata": self.metadata,
            "duration_seconds": self.duration.total_seconds() if self.duration else None,
            "size_gb": self.size_gb,
            "compressed_size_gb": self.compressed_size_gb
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupMetadata':
        """Crée depuis un dictionnaire"""        return cls(
            backup_id=data["backup_id"],
            user_id=data["user_id"],
            job_id=data.get("job_id"),
            backup_type=BackupType(data.get("backup_type", "full")),
            status=BackupStatus(data.get("status", "pending")),
            priority=BackupPriority(data.get("priority", "normal")),
            source_paths=data.get("source_paths", []),
            files=[FileMetadata.from_dict(f) for f in data.get("files", [])],
            total_files=data.get("total_files", 0),
            total_size=data.get("total_size", 0),
            compressed_size=data.get("compressed_size", 0),
            compression_algorithm=CompressionAlgorithm(data.get("compression_algorithm", "zstd")),
            compression_ratio=data.get("compression_ratio", 0.0),
            encryption_algorithm=EncryptionAlgorithm(data.get("encryption_algorithm", "aes-256")),
            encryption_key_id=data.get("encryption_key_id"),
            storage_provider=data.get("storage_provider"),
            storage_class=StorageClass(data.get("storage_class", "warm")),
            storage_path=data.get("storage_path"),
            storage_cost=data.get("storage_cost"),
            created_at=datetime.fromisoformat(data["created_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            checksum=data.get("checksum"),
            checksum_algorithm=data.get("checksum_algorithm", "sha256"),
            verified_at=datetime.fromisoformat(data["verified_at"]) if data.get("verified_at") else None,
            verification_status=data.get("verification_status"),
            parent_backup_id=data.get("parent_backup_id"),
            child_backup_ids=data.get("child_backup_ids", []),
            transfer_speed=data.get("transfer_speed", 0.0),
            cpu_time=data.get("cpu_time", 0.0),
            memory_peak=data.get("memory_peak", 0),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            log_path=data.get("log_path"),
            tags=data.get("tags", []),
            description=data.get("description"),
            metadata=data.get("metadata", {})
        )


@dataclass
class BackupSchedule:
    """Planning de sauvegarde"""    schedule_id: str
    user_id: str
    name: str
    enabled: bool = True
    
    # Configuration de sauvegarde
    backup_type: BackupType = BackupType.INCREMENTAL
    priority: BackupPriority = BackupPriority.NORMAL
    source_paths: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    storage_class: StorageClass = StorageClass.WARM
    compression_algorithm: CompressionAlgorithm = CompressionAlgorithm.ZSTD
    encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256
    
    # Planning
    cron_expression: Optional[str] = None
    frequency: Optional[str] = None  # daily, weekly, monthly
    time_of_day: Optional[str] = None  # HH:MM format
    days_of_week: List[int] = field(default_factory=list)  # 0-6 (Monday-Sunday)
    days_of_month: List[int] = field(default_factory=list)  # 1-31
    
    # Fenêtres de maintenance
    maintenance_window_start: Optional[str] = None  # HH:MM
    maintenance_window_end: Optional[str] = None    # HH:MM
    
    # Rétention
    retention_days: int = 30
    max_backups: Optional[int] = None
    
    # Statut
    last_backup_id: Optional[str] = None
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    consecutive_failures: int = 0
    
    # Métadonnées
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "schedule_id": self.schedule_id,
            "user_id": self.user_id,
            "name": self.name,
            "enabled": self.enabled,
            "backup_type": self.backup_type.value,
            "priority": self.priority.value,
            "source_paths": self.source_paths,
            "exclude_patterns": self.exclude_patterns,
            "storage_class": self.storage_class.value,
            "compression_algorithm": self.compression_algorithm.value,
            "encryption_algorithm": self.encryption_algorithm.value,
            "cron_expression": self.cron_expression,
            "frequency": self.frequency,
            "time_of_day": self.time_of_day,
            "days_of_week": self.days_of_week,
            "days_of_month": self.days_of_month,
            "maintenance_window_start": self.maintenance_window_start,
            "maintenance_window_end": self.maintenance_window_end,
            "retention_days": self.retention_days,
            "max_backups": self.max_backups,
            "last_backup_id": self.last_backup_id,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "next_execution": self.next_execution.isoformat() if self.next_execution else None,
            "consecutive_failures": self.consecutive_failures,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class BackupStats:
    """Statistiques globales des sauvegardes"""    total_backups: int = 0
    successful_backups: int = 0
    failed_backups: int = 0
    pending_backups: int = 0
    running_backups: int = 0
    
    total_size_bytes: int = 0
    compressed_size_bytes: int = 0
    
    total_files: int = 0
    
    average_compression_ratio: float = 0.0
    average_backup_duration: float = 0.0  # seconds
    average_transfer_speed: float = 0.0   # bytes/sec
    
    oldest_backup: Optional[datetime] = None
    newest_backup: Optional[datetime] = None
    
    storage_usage_by_class: Dict[str, int] = field(default_factory=dict)
    backup_count_by_type: Dict[str, int] = field(default_factory=dict)
    
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        """Taux de réussite en pourcentage"""        total = self.total_backups
        if total == 0:
            return 0.0
        return (self.successful_backups / total) * 100
    
    @property
    def total_size_gb(self) -> float:
        """Taille totale en GB"""        return self.total_size_bytes / (1024**3)
    
    @property
    def compressed_size_gb(self) -> float:
        """Taille compressée en GB"""        return self.compressed_size_bytes / (1024**3)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "total_backups": self.total_backups,
            "successful_backups": self.successful_backups,
            "failed_backups": self.failed_backups,
            "pending_backups": self.pending_backups,
            "running_backups": self.running_backups,
            "total_size_bytes": self.total_size_bytes,
            "compressed_size_bytes": self.compressed_size_bytes,
            "total_files": self.total_files,
            "average_compression_ratio": self.average_compression_ratio,
            "average_backup_duration": self.average_backup_duration,
            "average_transfer_speed": self.average_transfer_speed,
            "oldest_backup": self.oldest_backup.isoformat() if self.oldest_backup else None,
            "newest_backup": self.newest_backup.isoformat() if self.newest_backup else None,
            "storage_usage_by_class": self.storage_usage_by_class,
            "backup_count_by_type": self.backup_count_by_type,
            "success_rate": self.success_rate,
            "total_size_gb": self.total_size_gb,
            "compressed_size_gb": self.compressed_size_gb,
            "last_updated": self.last_updated.isoformat()
        }


# Fonctions utilitaires pour les modèles

def create_backup_job(
    user_id: str,
    source_paths: List[str],
    backup_type: BackupType = BackupType.INCREMENTAL,
    **kwargs
) -> BackupJob:
    """    Crée une nouvelle tâche de sauvegarde
    
    Args:
        user_id: ID de l'utilisateur
        source_paths: Chemins à sauvegarder
        backup_type: Type de sauvegarde
        **kwargs: Options supplémentaires
        
    Returns:
        BackupJob: Nouvelle tâche
    """    import secrets
    
    job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(8)}"
    
    return BackupJob(
        job_id=job_id,
        user_id=user_id,
        backup_type=backup_type,
        source_paths=source_paths,
        **kwargs
    )


def create_backup_metadata(
    user_id: str,
    backup_type: BackupType = BackupType.FULL,
    **kwargs
) -> BackupMetadata:
    """    Crée de nouvelles métadonnées de sauvegarde
    
    Args:
        user_id: ID de l'utilisateur
        backup_type: Type de sauvegarde
        **kwargs: Options supplémentaires
        
    Returns:
        BackupMetadata: Nouvelles métadonnées
    """    import secrets
    
    backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(8)}"
    
    return BackupMetadata(
        backup_id=backup_id,
        user_id=user_id,
        backup_type=backup_type,
        **kwargs
    )


def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """    Calcule le ratio de compression
    
    Args:
        original_size: Taille originale en bytes
        compressed_size: Taille compressée en bytes
        
    Returns:
        float: Ratio de compression (0.0 à 1.0)
    """    if original_size == 0:
        return 0.0
    
    return 1.0 - (compressed_size / original_size)


def estimate_backup_duration(
    total_size: int,
    transfer_speed: float,
    compression_factor: float = 0.5
) -> int:
    """    Estime la durée d'une sauvegarde
    
    Args:
        total_size: Taille totale en bytes
        transfer_speed: Vitesse de transfert en bytes/sec
        compression_factor: Facteur de compression (0.0 à 1.0)
        
    Returns:
        int: Durée estimée en secondes
    """    if transfer_speed <= 0:
        return 0
    
    effective_size = total_size * compression_factor
    return int(effective_size / transfer_speed)


# Export des classes et enums principaux
__all__ = [
    # Enums
    'BackupType',
    'BackupStatus', 
    'BackupPriority',
    'StorageClass',
    'CompressionAlgorithm',
    'EncryptionAlgorithm',
    
    # Modèles de données
    'FileMetadata',
    'BackupJob',
    'BackupProgress',
    'BackupMetadata',
    'BackupSchedule',
    'BackupStats',
    
    # Fonctions utilitaires
    'create_backup_job',
    'create_backup_metadata',
    'calculate_compression_ratio',
    'estimate_backup_duration'
]
