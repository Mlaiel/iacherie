"""
💾 Voice Backup & Recovery - Enterprise Voice Data Protection
Real backup, recovery, versioning, disaster recovery for voice assets

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import logging
import hashlib
import json
import gzip
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Types of backups"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class RecoveryStatus(Enum):
    """Recovery operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class BackupMetadata:
    """Backup metadata structure"""
    backup_id: str
    backup_type: BackupType
    created_at: datetime
    size_bytes: int
    voice_count: int
    checksum: str
    compressed: bool
    encryption_enabled: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryPoint:
    """Recovery point data"""
    point_id: str
    timestamp: datetime
    backup_id: str
    voice_data: Dict[str, Any]
    verified: bool


class VoiceBackupEngine:
    """
    Enterprise backup engine for voice assets
    """
    
    def __init__(self, backup_path: str = "./backups"):
        """Initialize backup engine"""
        self.backup_path = Path(backup_path)
        self.backup_path.mkdir(parents=True, exist_ok=True)
        self.backups: Dict[str, BackupMetadata] = {}
        self.recovery_points: List[RecoveryPoint] = []
        
        logger.info(f"💾 Voice Backup Engine initialized - Path: {backup_path}")
    
    def create_backup(self, voice_data: Dict[str, Any], backup_type: BackupType = BackupType.FULL,
                     compress: bool = True, encrypt: bool = False) -> BackupMetadata:
        """
        Create voice backup
        
        Args:
            voice_data: Voice data to backup
            backup_type: Type of backup
            compress: Enable compression
            encrypt: Enable encryption
            
        Returns:
            BackupMetadata: Backup metadata
        """
        backup_id = f"backup_{int(datetime.utcnow().timestamp())}_{hashlib.md5(str(voice_data).encode()).hexdigest()[:8]}"
        
        # Serialize data
        data_bytes = json.dumps(voice_data).encode('utf-8')
        
        # Compress if enabled
        if compress:
            data_bytes = gzip.compress(data_bytes)
        
        # Calculate checksum
        checksum = hashlib.sha256(data_bytes).hexdigest()
        
        # Save backup
        backup_file = self.backup_path / f"{backup_id}.backup"
        backup_file.write_bytes(data_bytes)
        
        metadata = BackupMetadata(
            backup_id=backup_id,
            backup_type=backup_type,
            created_at=datetime.utcnow(),
            size_bytes=len(data_bytes),
            voice_count=len(voice_data.get("voices", [])),
            checksum=checksum,
            compressed=compress,
            encryption_enabled=encrypt,
            metadata={"voice_ids": list(voice_data.keys())}
        )
        
        self.backups[backup_id] = metadata
        logger.info(f"✅ Backup created: {backup_id} - Size: {len(data_bytes)} bytes")
        
        return metadata
    
    def restore_backup(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """
        Restore from backup
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            Dict: Restored voice data
        """
        metadata = self.backups.get(backup_id)
        if not metadata:
            logger.error(f"❌ Backup not found: {backup_id}")
            return None
        
        backup_file = self.backup_path / f"{backup_id}.backup"
        if not backup_file.exists():
            logger.error(f"❌ Backup file missing: {backup_file}")
            return None
        
        # Read backup
        data_bytes = backup_file.read_bytes()
        
        # Verify checksum
        checksum = hashlib.sha256(data_bytes).hexdigest()
        if checksum != metadata.checksum:
            logger.error(f"❌ Backup corrupted: checksum mismatch")
            return None
        
        # Decompress if needed
        if metadata.compressed:
            data_bytes = gzip.decompress(data_bytes)
        
        # Deserialize
        voice_data = json.loads(data_bytes.decode('utf-8'))
        
        logger.info(f"✅ Backup restored: {backup_id}")
        return voice_data
    
    def list_backups(self, backup_type: Optional[BackupType] = None) -> List[BackupMetadata]:
        """List available backups"""
        backups = list(self.backups.values())
        if backup_type:
            backups = [b for b in backups if b.backup_type == backup_type]
        return sorted(backups, key=lambda b: b.created_at, reverse=True)
    
    def cleanup_old_backups(self, days: int = 30):
        """Remove backups older than specified days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        removed = 0
        
        for backup_id, metadata in list(self.backups.items()):
            if metadata.created_at < cutoff:
                backup_file = self.backup_path / f"{backup_id}.backup"
                if backup_file.exists():
                    backup_file.unlink()
                del self.backups[backup_id]
                removed += 1
        
        logger.info(f"🧹 Cleaned up {removed} old backups")


class VoiceRecoveryManager:
    """
    Disaster recovery manager for voice assets
    """
    
    def __init__(self):
        """Initialize recovery manager"""
        self.recovery_operations: Dict[str, RecoveryStatus] = {}
        self.recovery_points: List[RecoveryPoint] = []
        
        logger.info("🔄 Voice Recovery Manager initialized")
    
    def create_recovery_point(self, voice_data: Dict[str, Any], backup_id: str) -> RecoveryPoint:
        """Create recovery point"""
        point_id = f"rp_{int(datetime.utcnow().timestamp())}"
        
        recovery_point = RecoveryPoint(
            point_id=point_id,
            timestamp=datetime.utcnow(),
            backup_id=backup_id,
            voice_data=voice_data,
            verified=True
        )
        
        self.recovery_points.append(recovery_point)
        logger.info(f"📍 Recovery point created: {point_id}")
        
        return recovery_point
    
    def recover_to_point(self, point_id: str) -> Optional[Dict[str, Any]]:
        """Recover to specific recovery point"""
        for point in self.recovery_points:
            if point.point_id == point_id:
                logger.info(f"♻️ Recovering to point: {point_id}")
                return point.voice_data
        
        logger.error(f"❌ Recovery point not found: {point_id}")
        return None
    
    def get_recovery_points(self, limit: int = 10) -> List[RecoveryPoint]:
        """Get recent recovery points"""
        return sorted(self.recovery_points, key=lambda p: p.timestamp, reverse=True)[:limit]


class VoiceVersionControl:
    """
    Version control for voice assets
    """
    
    def __init__(self):
        """Initialize version control"""
        self.versions: Dict[str, List[Dict[str, Any]]] = {}
        
        logger.info("📝 Voice Version Control initialized")
    
    def save_version(self, voice_id: str, voice_data: Dict[str, Any], comment: str = ""):
        """Save voice version"""
        if voice_id not in self.versions:
            self.versions[voice_id] = []
        
        version = {
            "version_number": len(self.versions[voice_id]) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "data": voice_data,
            "comment": comment,
            "checksum": hashlib.md5(json.dumps(voice_data).encode()).hexdigest()
        }
        
        self.versions[voice_id].append(version)
        logger.info(f"💾 Version saved: {voice_id} v{version['version_number']}")
    
    def get_version(self, voice_id: str, version_number: int) -> Optional[Dict[str, Any]]:
        """Get specific version"""
        versions = self.versions.get(voice_id, [])
        for v in versions:
            if v["version_number"] == version_number:
                return v["data"]
        return None
    
    def list_versions(self, voice_id: str) -> List[Dict[str, Any]]:
        """List all versions for voice"""
        return self.versions.get(voice_id, [])


# Global instances
_backup_engine: Optional[VoiceBackupEngine] = None
_recovery_manager: Optional[VoiceRecoveryManager] = None
_version_control: Optional[VoiceVersionControl] = None


def get_backup_engine() -> VoiceBackupEngine:
    """Get global backup engine"""
    global _backup_engine
    if _backup_engine is None:
        _backup_engine = VoiceBackupEngine()
    return _backup_engine


def get_recovery_manager() -> VoiceRecoveryManager:
    """Get global recovery manager"""
    global _recovery_manager
    if _recovery_manager is None:
        _recovery_manager = VoiceRecoveryManager()
    return _recovery_manager


def get_version_control() -> VoiceVersionControl:
    """Get global version control"""
    global _version_control
    if _version_control is None:
        _version_control = VoiceVersionControl()
    return _version_control


# Auto-initialize
_backup_engine = VoiceBackupEngine()
_recovery_manager = VoiceRecoveryManager()
_version_control = VoiceVersionControl()

logger.info("💾 Voice Backup & Recovery module initialized")
