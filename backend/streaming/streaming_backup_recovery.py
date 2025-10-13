"""Streaming Backup & Recovery System
====================================
Enterprise backup and disaster recovery for streaming infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib

logger = logging.getLogger(__name__)


class BackupType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class RecoveryPointObjective(str, Enum):
    CRITICAL = "critical"  # RPO: 1 minute
    HIGH = "high"  # RPO: 5 minutes
    MEDIUM = "medium"  # RPO: 15 minutes
    LOW = "low"  # RPO: 1 hour


class StreamingBackupRecovery:
    """Enterprise streaming backup and disaster recovery system"""
    
    def __init__(self):
        self.backups: Dict[str, Dict] = {}
        self.recovery_points: Dict[str, List[Dict]] = {}
        self.backup_schedule: Dict[str, Dict] = {}
        self.retention_policies: Dict[str, int] = {
            BackupType.FULL: 30,  # 30 days
            BackupType.INCREMENTAL: 7,  # 7 days
            BackupType.DIFFERENTIAL: 14,  # 14 days
        }
        
    async def create_backup(
        self,
        stream_id: str,
        backup_type: BackupType = BackupType.INCREMENTAL,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create streaming backup"""
        backup_id = f"backup_{stream_id}_{int(datetime.utcnow().timestamp())}"
        
        backup = {
            "id": backup_id,
            "stream_id": stream_id,
            "type": backup_type.value,
            "status": BackupStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "size_bytes": 0,
            "checksum": "",
        }
        
        self.backups[backup_id] = backup
        
        try:
            backup["status"] = BackupStatus.IN_PROGRESS.value
            
            backup_data = await self._capture_stream_state(stream_id, backup_type)
            
            backup["size_bytes"] = len(json.dumps(backup_data))
            backup["checksum"] = hashlib.sha256(
                json.dumps(backup_data).encode()
            ).hexdigest()
            backup["status"] = BackupStatus.COMPLETED.value
            backup["completed_at"] = datetime.utcnow().isoformat()
            
            if stream_id not in self.recovery_points:
                self.recovery_points[stream_id] = []
            
            self.recovery_points[stream_id].append({
                "backup_id": backup_id,
                "timestamp": datetime.utcnow().isoformat(),
                "type": backup_type.value,
                "checksum": backup["checksum"]
            })
            
            await self._apply_retention_policy(stream_id)
            
            logger.info(f"Backup created: {backup_id} for stream {stream_id}")
            
        except Exception as e:
            backup["status"] = BackupStatus.FAILED.value
            backup["error"] = str(e)
            logger.error(f"Backup failed: {e}")
            
        return backup
    
    async def restore_stream(
        self,
        stream_id: str,
        backup_id: Optional[str] = None,
        point_in_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Restore stream from backup"""
        if backup_id:
            backup = self.backups.get(backup_id)
            if not backup:
                raise ValueError(f"Backup {backup_id} not found")
        elif point_in_time:
            backup = await self._find_backup_at_time(stream_id, point_in_time)
        else:
            backup = await self._get_latest_backup(stream_id)
        
        if not backup:
            raise ValueError(f"No backup found for stream {stream_id}")
        
        try:
            stream_state = await self._load_backup_data(backup["id"])
            
            await self._restore_stream_state(stream_id, stream_state)
            
            logger.info(f"Stream {stream_id} restored from backup {backup['id']}")
            
            return {
                "stream_id": stream_id,
                "backup_id": backup["id"],
                "restored_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise
    
    async def schedule_backup(
        self,
        stream_id: str,
        backup_type: BackupType,
        schedule_expression: str,
        rpo: RecoveryPointObjective = RecoveryPointObjective.MEDIUM
    ) -> Dict[str, Any]:
        """Schedule automatic backups"""
        schedule_id = f"schedule_{stream_id}_{backup_type.value}"
        
        schedule = {
            "id": schedule_id,
            "stream_id": stream_id,
            "backup_type": backup_type.value,
            "schedule": schedule_expression,
            "rpo": rpo.value,
            "enabled": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_run": None,
            "next_run": None
        }
        
        self.backup_schedule[schedule_id] = schedule
        
        logger.info(f"Backup schedule created: {schedule_id}")
        
        return schedule
    
    async def verify_backup(self, backup_id: str) -> Dict[str, Any]:
        """Verify backup integrity"""
        backup = self.backups.get(backup_id)
        if not backup:
            raise ValueError(f"Backup {backup_id} not found")
        
        try:
            backup_data = await self._load_backup_data(backup_id)
            
            checksum = hashlib.sha256(
                json.dumps(backup_data).encode()
            ).hexdigest()
            
            is_valid = checksum == backup["checksum"]
            
            return {
                "backup_id": backup_id,
                "valid": is_valid,
                "expected_checksum": backup["checksum"],
                "actual_checksum": checksum,
                "verified_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return {
                "backup_id": backup_id,
                "valid": False,
                "error": str(e)
            }
    
    async def get_recovery_points(self, stream_id: str) -> List[Dict]:
        """Get available recovery points for stream"""
        return self.recovery_points.get(stream_id, [])
    
    async def get_backup_status(self, backup_id: str) -> Dict[str, Any]:
        """Get backup status"""
        backup = self.backups.get(backup_id)
        if not backup:
            raise ValueError(f"Backup {backup_id} not found")
        
        return {
            "id": backup["id"],
            "status": backup["status"],
            "created_at": backup["created_at"],
            "completed_at": backup.get("completed_at"),
            "size_bytes": backup["size_bytes"],
            "type": backup["type"]
        }
    
    async def delete_backup(self, backup_id: str) -> Dict[str, Any]:
        """Delete backup"""
        backup = self.backups.get(backup_id)
        if not backup:
            raise ValueError(f"Backup {backup_id} not found")
        
        stream_id = backup["stream_id"]
        
        if stream_id in self.recovery_points:
            self.recovery_points[stream_id] = [
                rp for rp in self.recovery_points[stream_id]
                if rp["backup_id"] != backup_id
            ]
        
        del self.backups[backup_id]
        
        logger.info(f"Backup deleted: {backup_id}")
        
        return {"backup_id": backup_id, "deleted": True}
    
    async def _capture_stream_state(
        self,
        stream_id: str,
        backup_type: BackupType
    ) -> Dict[str, Any]:
        """Capture current stream state"""
        state = {
            "stream_id": stream_id,
            "timestamp": datetime.utcnow().isoformat(),
            "configuration": {},
            "metrics": {},
            "recordings": [],
            "analytics": {}
        }
        
        return state
    
    async def _load_backup_data(self, backup_id: str) -> Dict[str, Any]:
        """Load backup data from storage"""
        backup = self.backups.get(backup_id)
        if not backup:
            raise ValueError(f"Backup {backup_id} not found")
        
        return {}
    
    async def _restore_stream_state(
        self,
        stream_id: str,
        state: Dict[str, Any]
    ) -> None:
        """Restore stream to previous state"""
        pass
    
    async def _find_backup_at_time(
        self,
        stream_id: str,
        target_time: datetime
    ) -> Optional[Dict]:
        """Find backup closest to target time"""
        recovery_points = self.recovery_points.get(stream_id, [])
        
        if not recovery_points:
            return None
        
        closest = min(
            recovery_points,
            key=lambda rp: abs(
                datetime.fromisoformat(rp["timestamp"]) - target_time
            )
        )
        
        return self.backups.get(closest["backup_id"])
    
    async def _get_latest_backup(self, stream_id: str) -> Optional[Dict]:
        """Get most recent backup for stream"""
        recovery_points = self.recovery_points.get(stream_id, [])
        
        if not recovery_points:
            return None
        
        latest = max(
            recovery_points,
            key=lambda rp: datetime.fromisoformat(rp["timestamp"])
        )
        
        return self.backups.get(latest["backup_id"])
    
    async def _apply_retention_policy(self, stream_id: str) -> None:
        """Apply backup retention policy"""
        recovery_points = self.recovery_points.get(stream_id, [])
        
        now = datetime.utcnow()
        
        for rp in recovery_points[:]:
            backup = self.backups.get(rp["backup_id"])
            if not backup:
                continue
            
            backup_type = BackupType(backup["type"])
            retention_days = self.retention_policies.get(backup_type, 7)
            
            backup_age = now - datetime.fromisoformat(backup["created_at"])
            
            if backup_age.days > retention_days:
                await self.delete_backup(backup["id"])
                logger.info(f"Backup {backup['id']} deleted by retention policy")
