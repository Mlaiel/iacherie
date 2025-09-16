#!/usr/bin/env python3
"""
💾 BACKUP & DISASTER RECOVERY SERVICE
====================================

Unified service combining backup operations and disaster recovery capabilities.
Handles automated backups, data integrity, disaster detection, and automated recovery.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import os
import shutil
import gzip
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import tarfile
import tempfile
import threading
import aiofiles
import psutil
from cryptography.fernet import Fernet
import boto3
from botocore.exceptions import ClientError
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== BACKUP ENUMS =====
class BackupType(Enum):
    """Backup type enumeration"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"

class BackupStatus(Enum):
    """Backup status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CORRUPTED = "corrupted"

class StorageType(Enum):
    """Storage type enumeration"""
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCP = "gcp"

# ===== DISASTER RECOVERY ENUMS =====
class DisasterType(Enum):
    """Types of disasters that can be handled."""
    HARDWARE_FAILURE = "hardware_failure"
    NETWORK_OUTAGE = "network_outage"
    DATA_CORRUPTION = "data_corruption"
    CYBER_ATTACK = "cyber_attack"
    NATURAL_DISASTER = "natural_disaster"
    HUMAN_ERROR = "human_error"
    SOFTWARE_FAILURE = "software_failure"
    POWER_OUTAGE = "power_outage"

class RecoveryState(Enum):
    """Recovery operation states."""
    IDLE = "idle"
    DETECTING = "detecting"
    PREPARING = "preparing"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"

class RecoveryPriority(Enum):
    """Recovery priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# ===== DATA CLASSES =====
@dataclass
class BackupConfiguration:
    """Backup configuration data class"""
    backup_type: BackupType
    storage_type: StorageType
    encryption_enabled: bool = True
    compression_enabled: bool = True
    retention_days: int = 30
    schedule_cron: Optional[str] = None
    storage_path: str = "/backup"
    max_backup_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    verification_enabled: bool = True

@dataclass
class BackupMetadata:
    """Backup metadata information"""
    backup_id: str
    timestamp: datetime
    backup_type: BackupType
    size: int
    checksum: str
    status: BackupStatus
    source_paths: List[str]
    storage_location: str
    encryption_key_id: Optional[str] = None
    compression_ratio: Optional[float] = None
    verification_status: bool = False

@dataclass
class DisasterEvent:
    """Disaster event information."""
    event_id: str
    disaster_type: DisasterType
    severity: int
    detected_at: datetime
    affected_services: List[str]
    description: str
    recovery_priority: RecoveryPriority = RecoveryPriority.MEDIUM

@dataclass
class RecoveryPlan:
    """Recovery plan definition."""
    plan_id: str
    disaster_types: List[DisasterType]
    recovery_steps: List[Dict[str, Any]]
    estimated_rto: int  # Recovery Time Objective in minutes
    estimated_rpo: int  # Recovery Point Objective in minutes
    dependencies: List[str] = field(default_factory=list)
    rollback_steps: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class RecoveryOperation:
    """Recovery operation tracking."""
    operation_id: str
    disaster_event: DisasterEvent
    recovery_plan: RecoveryPlan
    state: RecoveryState
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percentage: int = 0
    current_step: int = 0
    error_message: Optional[str] = None

class BackupRecoveryService:
    """Unified Backup and Disaster Recovery Service"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the backup and recovery service"""
        self.config = config
        self.backup_configs: Dict[str, BackupConfiguration] = {}
        self.active_backups: Dict[str, BackupMetadata] = {}
        self.backup_history: List[BackupMetadata] = []
        
        # Disaster Recovery
        self.recovery_plans: Dict[str, RecoveryPlan] = {}
        self.active_operations: Dict[str, RecoveryOperation] = {}
        self.disaster_history: List[DisasterEvent] = []
        self.monitoring_active = False
        self.monitoring_interval = config.get('monitoring_interval', 30)
        
        # Initialize components
        self._init_encryption()
        self._init_storage()
        self._init_monitoring()
        
        logger.info("Backup & Recovery Service initialized")

    def _init_encryption(self):
        """Initialize encryption components"""
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    def _init_storage(self):
        """Initialize storage clients"""
        try:
            # AWS S3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.config.get('aws_access_key'),
                aws_secret_access_key=self.config.get('aws_secret_key'),
                region_name=self.config.get('aws_region', 'us-east-1')
            )
            
            # Redis for metadata
            self.redis_client = redis.Redis(
                host=self.config.get('redis_host', 'localhost'),
                port=self.config.get('redis_port', 6379),
                db=self.config.get('redis_db', 2)
            )
            
        except Exception as e:
            logger.error(f"Storage initialization error: {e}")

    def _init_monitoring(self):
        """Initialize disaster monitoring"""
        self.monitoring_metrics = {
            'cpu_threshold': 90.0,
            'memory_threshold': 90.0,
            'disk_threshold': 95.0,
            'network_timeout': 10.0
        }

    # ===== BACKUP OPERATIONS =====
    async def create_backup(self, backup_name: str, source_paths: List[str], 
                          config: Optional[BackupConfiguration] = None) -> str:
        """Create a new backup"""
        try:
            backup_id = f"backup_{int(time.time())}"
            
            if not config:
                config = BackupConfiguration(
                    backup_type=BackupType.FULL,
                    storage_type=StorageType.LOCAL
                )
            
            # Create backup metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.now(),
                backup_type=config.backup_type,
                size=0,
                checksum="",
                status=BackupStatus.PENDING,
                source_paths=source_paths,
                storage_location=""
            )
            
            self.active_backups[backup_id] = metadata
            
            # Start backup process
            await self._execute_backup(backup_id, source_paths, config)
            
            return backup_id
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            raise

    async def _execute_backup(self, backup_id: str, source_paths: List[str], 
                            config: BackupConfiguration):
        """Execute the backup process"""
        try:
            metadata = self.active_backups[backup_id]
            metadata.status = BackupStatus.IN_PROGRESS
            
            # Create temporary backup file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as temp_file:
                temp_path = temp_file.name
                
                # Create compressed archive
                with tarfile.open(temp_path, 'w:gz') as tar:
                    for source_path in source_paths:
                        if os.path.exists(source_path):
                            tar.add(source_path, arcname=os.path.basename(source_path))
                
                # Get file size and checksum
                file_size = os.path.getsize(temp_path)
                checksum = await self._calculate_checksum(temp_path)
                
                # Encrypt if enabled
                if config.encryption_enabled:
                    encrypted_path = await self._encrypt_file(temp_path)
                    os.remove(temp_path)
                    temp_path = encrypted_path
                
                # Upload to storage
                storage_location = await self._upload_backup(backup_id, temp_path, config)
                
                # Update metadata
                metadata.size = file_size
                metadata.checksum = checksum
                metadata.storage_location = storage_location
                metadata.status = BackupStatus.COMPLETED
                
                # Verify backup if enabled
                if config.verification_enabled:
                    metadata.verification_status = await self._verify_backup(backup_id)
                
                # Clean up temporary file
                os.remove(temp_path)
                
                # Store metadata
                await self._store_backup_metadata(metadata)
                
                logger.info(f"Backup {backup_id} completed successfully")
                
        except Exception as e:
            if backup_id in self.active_backups:
                self.active_backups[backup_id].status = BackupStatus.FAILED
            logger.error(f"Backup execution failed: {e}")
            raise

    async def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        hash_md5 = hashlib.md5()
        async with aiofiles.open(file_path, "rb") as f:
            async for chunk in self._read_chunks(f):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    async def _read_chunks(self, file_obj, chunk_size: int = 8192):
        """Read file in chunks"""
        while True:
            chunk = await file_obj.read(chunk_size)
            if not chunk:
                break
            yield chunk

    async def _encrypt_file(self, file_path: str) -> str:
        """Encrypt backup file"""
        encrypted_path = f"{file_path}.encrypted"
        
        async with aiofiles.open(file_path, "rb") as source:
            async with aiofiles.open(encrypted_path, "wb") as target:
                async for chunk in self._read_chunks(source):
                    encrypted_chunk = self.cipher_suite.encrypt(chunk)
                    await target.write(encrypted_chunk)
        
        return encrypted_path

    async def _upload_backup(self, backup_id: str, file_path: str, 
                           config: BackupConfiguration) -> str:
        """Upload backup to storage"""
        if config.storage_type == StorageType.S3:
            return await self._upload_to_s3(backup_id, file_path)
        elif config.storage_type == StorageType.LOCAL:
            return await self._upload_to_local(backup_id, file_path, config.storage_path)
        else:
            raise ValueError(f"Unsupported storage type: {config.storage_type}")

    async def _upload_to_s3(self, backup_id: str, file_path: str) -> str:
        """Upload backup to S3"""
        bucket_name = self.config.get('s3_bucket_name', 'ainflue-backups')
        key = f"backups/{backup_id}.tar.gz"
        
        try:
            self.s3_client.upload_file(file_path, bucket_name, key)
            return f"s3://{bucket_name}/{key}"
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise

    async def _upload_to_local(self, backup_id: str, file_path: str, 
                             storage_path: str) -> str:
        """Upload backup to local storage"""
        os.makedirs(storage_path, exist_ok=True)
        destination = os.path.join(storage_path, f"{backup_id}.tar.gz")
        shutil.move(file_path, destination)
        return destination

    async def _verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity"""
        try:
            metadata = self.active_backups[backup_id]
            
            # Download and verify checksum
            temp_file = await self._download_backup(backup_id)
            calculated_checksum = await self._calculate_checksum(temp_file)
            
            is_valid = calculated_checksum == metadata.checksum
            os.remove(temp_file)
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return False

    # ===== DISASTER RECOVERY OPERATIONS =====
    async def start_monitoring(self):
        """Start disaster monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        asyncio.create_task(self._monitoring_loop())
        logger.info("Disaster monitoring started")

    async def stop_monitoring(self):
        """Stop disaster monitoring"""
        self.monitoring_active = False
        logger.info("Disaster monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await self._check_system_health()
                await self._check_service_health()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(5)

    async def _check_system_health(self):
        """Check system health metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.monitoring_metrics['cpu_threshold']:
                await self._trigger_disaster_event(
                    DisasterType.HARDWARE_FAILURE,
                    f"High CPU usage: {cpu_percent}%",
                    ['cpu_service']
                )
            
            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.monitoring_metrics['memory_threshold']:
                await self._trigger_disaster_event(
                    DisasterType.HARDWARE_FAILURE,
                    f"High memory usage: {memory.percent}%",
                    ['memory_service']
                )
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > self.monitoring_metrics['disk_threshold']:
                await self._trigger_disaster_event(
                    DisasterType.HARDWARE_FAILURE,
                    f"High disk usage: {disk_percent:.1f}%",
                    ['storage_service']
                )
                
        except Exception as e:
            logger.error(f"System health check failed: {e}")

    async def _check_service_health(self):
        """Check service health"""
        critical_services = ['redis', 'database', 'api_gateway']
        
        for service in critical_services:
            try:
                # Service-specific health checks
                if service == 'redis':
                    await self.redis_client.ping()
                # Add other service checks as needed
                    
            except Exception as e:
                await self._trigger_disaster_event(
                    DisasterType.SOFTWARE_FAILURE,
                    f"Service {service} health check failed: {e}",
                    [service]
                )

    async def _trigger_disaster_event(self, disaster_type: DisasterType, 
                                    description: str, affected_services: List[str]):
        """Trigger a disaster event"""
        event_id = f"disaster_{int(time.time())}"
        
        disaster_event = DisasterEvent(
            event_id=event_id,
            disaster_type=disaster_type,
            severity=self._calculate_severity(disaster_type, affected_services),
            detected_at=datetime.now(),
            affected_services=affected_services,
            description=description
        )
        
        self.disaster_history.append(disaster_event)
        logger.warning(f"Disaster event triggered: {event_id} - {description}")
        
        # Start recovery if auto-recovery is enabled
        if self.config.get('auto_recovery_enabled', True):
            await self.start_recovery(disaster_event)

    def _calculate_severity(self, disaster_type: DisasterType, 
                          affected_services: List[str]) -> int:
        """Calculate disaster severity (1-10)"""
        base_severity = {
            DisasterType.HARDWARE_FAILURE: 7,
            DisasterType.NETWORK_OUTAGE: 8,
            DisasterType.DATA_CORRUPTION: 9,
            DisasterType.CYBER_ATTACK: 10,
            DisasterType.SOFTWARE_FAILURE: 5,
            DisasterType.POWER_OUTAGE: 6
        }.get(disaster_type, 5)
        
        # Adjust based on number of affected services
        severity_modifier = min(len(affected_services), 3)
        return min(base_severity + severity_modifier, 10)

    async def start_recovery(self, disaster_event: DisasterEvent) -> str:
        """Start disaster recovery process"""
        try:
            # Find appropriate recovery plan
            recovery_plan = self._find_recovery_plan(disaster_event.disaster_type)
            if not recovery_plan:
                logger.error(f"No recovery plan found for {disaster_event.disaster_type}")
                return ""
            
            operation_id = f"recovery_{int(time.time())}"
            
            recovery_operation = RecoveryOperation(
                operation_id=operation_id,
                disaster_event=disaster_event,
                recovery_plan=recovery_plan,
                state=RecoveryState.PREPARING,
                started_at=datetime.now()
            )
            
            self.active_operations[operation_id] = recovery_operation
            
            # Execute recovery
            asyncio.create_task(self._execute_recovery(operation_id))
            
            return operation_id
            
        except Exception as e:
            logger.error(f"Recovery start failed: {e}")
            raise

    def _find_recovery_plan(self, disaster_type: DisasterType) -> Optional[RecoveryPlan]:
        """Find appropriate recovery plan"""
        for plan in self.recovery_plans.values():
            if disaster_type in plan.disaster_types:
                return plan
        return None

    async def _execute_recovery(self, operation_id: str):
        """Execute recovery operation"""
        try:
            operation = self.active_operations[operation_id]
            operation.state = RecoveryState.EXECUTING
            
            total_steps = len(operation.recovery_plan.recovery_steps)
            
            for i, step in enumerate(operation.recovery_plan.recovery_steps):
                operation.current_step = i + 1
                operation.progress_percentage = int((i + 1) / total_steps * 100)
                
                await self._execute_recovery_step(step)
                
                logger.info(f"Recovery step {i+1}/{total_steps} completed")
            
            operation.state = RecoveryState.VALIDATING
            
            # Validate recovery
            if await self._validate_recovery(operation):
                operation.state = RecoveryState.COMPLETED
                operation.completed_at = datetime.now()
                logger.info(f"Recovery {operation_id} completed successfully")
            else:
                operation.state = RecoveryState.FAILED
                operation.error_message = "Recovery validation failed"
                logger.error(f"Recovery {operation_id} validation failed")
                
        except Exception as e:
            operation.state = RecoveryState.FAILED
            operation.error_message = str(e)
            logger.error(f"Recovery execution failed: {e}")

    async def _execute_recovery_step(self, step: Dict[str, Any]):
        """Execute individual recovery step"""
        step_type = step.get('type')
        
        if step_type == 'service_restart':
            await self._restart_service(step.get('service_name'))
        elif step_type == 'backup_restore':
            await self._restore_from_backup(step.get('backup_id'))
        elif step_type == 'failover':
            await self._execute_failover(step.get('target_instance'))
        elif step_type == 'command':
            await self._execute_command(step.get('command'))
        else:
            logger.warning(f"Unknown recovery step type: {step_type}")

    async def _restart_service(self, service_name: str):
        """Restart a service"""
        # Implementation for service restart
        logger.info(f"Restarting service: {service_name}")
        # Add actual service restart logic here

    async def _restore_from_backup(self, backup_id: str):
        """Restore from backup"""
        logger.info(f"Restoring from backup: {backup_id}")
        # Add backup restoration logic here

    async def _execute_failover(self, target_instance: str):
        """Execute failover to target instance"""
        logger.info(f"Executing failover to: {target_instance}")
        # Add failover logic here

    async def _execute_command(self, command: str):
        """Execute recovery command"""
        logger.info(f"Executing command: {command}")
        # Add command execution logic here

    async def _validate_recovery(self, operation: RecoveryOperation) -> bool:
        """Validate recovery operation"""
        try:
            # Check if affected services are healthy
            for service in operation.disaster_event.affected_services:
                if not await self._check_service_status(service):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Recovery validation error: {e}")
            return False

    async def _check_service_status(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        # Implementation for service health check
        return True

    # ===== UTILITY METHODS =====
    async def _store_backup_metadata(self, metadata: BackupMetadata):
        """Store backup metadata in Redis"""
        try:
            await self.redis_client.hset(
                f"backup:{metadata.backup_id}",
                mapping={
                    "metadata": json.dumps(asdict(metadata), default=str)
                }
            )
            
            # Add to history
            self.backup_history.append(metadata)
            
            # Move from active to history
            if metadata.backup_id in self.active_backups:
                del self.active_backups[metadata.backup_id]
                
        except Exception as e:
            logger.error(f"Metadata storage failed: {e}")

    async def _download_backup(self, backup_id: str) -> str:
        """Download backup for verification"""
        # Implementation for backup download
        temp_file = f"/tmp/{backup_id}_verify.tar.gz"
        # Add download logic here
        return temp_file

    async def get_backup_status(self, backup_id: str) -> Optional[BackupMetadata]:
        """Get backup status"""
        if backup_id in self.active_backups:
            return self.active_backups[backup_id]
        
        # Check Redis for completed backups
        try:
            metadata_json = await self.redis_client.hget(f"backup:{backup_id}", "metadata")
            if metadata_json:
                return BackupMetadata(**json.loads(metadata_json))
        except Exception as e:
            logger.error(f"Backup status retrieval failed: {e}")
        
        return None

    async def list_backups(self) -> List[BackupMetadata]:
        """List all backups"""
        return self.backup_history + list(self.active_backups.values())

    async def get_recovery_status(self, operation_id: str) -> Optional[RecoveryOperation]:
        """Get recovery operation status"""
        return self.active_operations.get(operation_id)

    async def list_disaster_events(self) -> List[DisasterEvent]:
        """List all disaster events"""
        return self.disaster_history

    def register_recovery_plan(self, plan: RecoveryPlan):
        """Register a recovery plan"""
        self.recovery_plans[plan.plan_id] = plan
        logger.info(f"Recovery plan registered: {plan.plan_id}")

    async def test_recovery_plan(self, plan_id: str) -> bool:
        """Test a recovery plan"""
        plan = self.recovery_plans.get(plan_id)
        if not plan:
            return False
        
        # Simulate disaster event for testing
        test_event = DisasterEvent(
            event_id="test_event",
            disaster_type=plan.disaster_types[0],
            severity=1,
            detected_at=datetime.now(),
            affected_services=["test_service"],
            description="Recovery plan test"
        )
        
        # Execute recovery in test mode
        try:
            operation_id = await self.start_recovery(test_event)
            return operation_id is not None
        except Exception as e:
            logger.error(f"Recovery plan test failed: {e}")
            return False

    async def cleanup_old_backups(self, retention_days: int = 30):
        """Clean up old backups"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Clean up from history
            self.backup_history = [
                backup for backup in self.backup_history
                if backup.timestamp > cutoff_date
            ]
            
            logger.info(f"Cleaned up backups older than {retention_days} days")
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")

    async def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "active_backups": len(self.active_backups),
            "total_backups": len(self.backup_history),
            "active_recoveries": len(self.active_operations),
            "disaster_events": len(self.disaster_history),
            "recovery_plans": len(self.recovery_plans),
            "monitoring_active": self.monitoring_active
        }

# ===== SERVICE FACTORY =====
def create_backup_recovery_service(config: Dict[str, Any]) -> BackupRecoveryService:
    """Factory function to create backup recovery service"""
    return BackupRecoveryService(config)

# Example usage and testing
if __name__ == "__main__":
    async def main():
        config = {
            'redis_host': 'localhost',
            'redis_port': 6379,
            'redis_db': 2,
            'aws_access_key': 'your_access_key',
            'aws_secret_key': 'your_secret_key',
            'aws_region': 'us-east-1',
            's3_bucket_name': 'ainflue-backups',
            'monitoring_interval': 30,
            'auto_recovery_enabled': True
        }
        
        service = create_backup_recovery_service(config)
        
        # Start monitoring
        await service.start_monitoring()
        
        # Create a backup
        backup_id = await service.create_backup(
            "test_backup",
            ["/path/to/important/data"]
        )
        
        print(f"Backup created: {backup_id}")
        
        # Get service stats
        stats = await service.get_service_stats()
        print(f"Service stats: {stats}")
        
        # Keep running for monitoring
        await asyncio.sleep(60)
        
        await service.stop_monitoring()
    
    asyncio.run(main())