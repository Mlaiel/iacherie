"""
 Integrity Checker - IA Influencer Agent Platform Enterprise
=============================================================
Module: backend/data_management/storage/integrity_checker.py
Author: Fahed Mlaiel (mlaiel@live.de)
=============================================================

Enterprise data integrity checker with corruption detection,
verification, and automatic repair capabilities.

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

ÉQUIPE PROJET - SPÉCIALITÉS:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- DBA: Fahed Mlaiel
- DevOps: Fahed Mlaiel
"""

from typing import Dict, List, Optional, Any, Union, Set, Tuple, Callable
import logging
import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import aiofiles
import aiofiles.os
import struct
import zlib
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class IntegrityLevel(Enum):
    """Data integrity levels"""
    BASIC = "basic"  # Basic checksum verification
    STANDARD = "standard"  # Multi-algorithm verification
    ADVANCED = "advanced"  # Deep structure analysis
    PARANOID = "paranoid"  # Comprehensive multi-layer verification

class CorruptionSeverity(Enum):
    """Corruption severity levels"""
    MINOR = "minor"  # Recoverable corruption
    MAJOR = "major"  # Significant data loss
    CRITICAL = "critical"  # Complete file corruption
    CATASTROPHIC = "catastrophic"  # System-wide corruption

class VerificationStatus(Enum):
    """Verification status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CORRUPTED = "corrupted"
    REPAIRED = "repaired"

class RepairStrategy(Enum):
    """Corruption repair strategies"""
    AUTO_REPAIR = "auto_repair"
    BACKUP_RESTORE = "backup_restore"
    REDUNDANT_COPY = "redundant_copy"
    MANUAL_INTERVENTION = "manual_intervention"
    QUARANTINE = "quarantine"

@dataclass
class IntegrityCheckpoint:
    """Represents an integrity checkpoint"""
    checkpoint_id: str
    file_path: str
    file_size: int
    
    # Checksums
    md5_hash: str
    sha256_hash: str
    crc32_checksum: str
    
    # Metadata
    created_at: datetime
    file_permissions: str
    file_owner: str
    
    # Verification history
    last_verified: Optional[datetime] = None
    verification_count: int = 0
    corruption_detected: bool = False
    
    # Extended attributes
    extended_attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Repair information
    repair_attempts: int = 0
    last_repair: Optional[datetime] = None
    repair_strategy: Optional[RepairStrategy] = None

@dataclass
class CorruptionReport:
    """Corruption detection report"""
    report_id: str
    checkpoint_id: str
    file_path: str
    
    # Corruption details
    corruption_type: str
    severity: CorruptionSeverity
    detected_at: datetime
    
    # Verification results
    expected_checksums: Dict[str, str]
    actual_checksums: Dict[str, str]
    differences: List[str]
    
    # File analysis
    file_analysis: Dict[str, Any] = field(default_factory=dict)
    corruption_patterns: List[str] = field(default_factory=list)
    
    # Repair information
    is_repairable: bool = False
    repair_confidence: float = 0.0
    recommended_strategy: Optional[RepairStrategy] = None
    
    # Resolution
    resolved: bool = False
    resolution_method: str = ""
    resolved_at: Optional[datetime] = None

@dataclass
class IntegrityConfig:
    """Configuration for integrity checker"""
    storage_root_path: str
    checkpoints_directory: str
    reports_directory: str
    
    # Verification settings
    default_integrity_level: IntegrityLevel = IntegrityLevel.STANDARD
    verification_interval_hours: int = 24
    deep_scan_interval_days: int = 7
    
    # Performance settings
    max_concurrent_verifications: int = 10
    verification_chunk_size: int = 1024 * 1024  # 1MB
    max_memory_usage: int = 512 * 1024 * 1024  # 512MB
    
    # Repair settings
    auto_repair_enabled: bool = True
    max_repair_attempts: int = 3
    quarantine_corrupted_files: bool = True
    
    # Monitoring settings
    real_time_monitoring: bool = True
    corruption_alerting: bool = True
    detailed_logging: bool = True
    
    # Retention settings
    checkpoint_retention_days: int = 90
    report_retention_days: int = 365

class IntegrityChecker:
    """
    Enterprise data integrity checker and corruption detector.
    
    Features:
    - Multi-algorithm checksum verification
    - Real-time corruption detection
    - Automatic repair capabilities
    - Comprehensive reporting
    - Performance optimization
    - Scheduled verification
    """
    
    def __init__(self, config: IntegrityConfig):
        """Initialize integrity checker"""
        self.config = config
        self.checkpoints: Dict[str, IntegrityCheckpoint] = {}
        self.corruption_reports: Dict[str, CorruptionReport] = {}
        self.active_verifications: Set[str] = set()
        
        # Managers
        self.verification_engine = VerificationEngine(self)
        self.corruption_detector = CorruptionDetector(self)
        self.repair_engine = RepairEngine(self)
        self.scheduler = IntegrityScheduler(self)
        
        # Performance tracking
        self.metrics = {
            'total_verifications': 0,
            'successful_verifications': 0,
            'corruptions_detected': 0,
            'corruptions_repaired': 0,
            'false_positives': 0,
            'average_verification_time': 0.0,
            'data_integrity_score': 100.0,
            'last_full_scan': None
        }
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_verifications)
        self.shutdown_event = threading.Event()
        
        # Initialize directories
        self._initialize_integrity_directories()
        
        # Start background monitoring
        asyncio.create_task(self._start_monitoring())
        
        logger.info("IntegrityChecker initialized successfully")
    
    def _initialize_integrity_directories(self) -> None:
        """Initialize integrity checking directories"""



        try:
            directories = [
                self.config.storage_root_path,
                self.config.checkpoints_directory,
                self.config.reports_directory
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            checkpoints_dir = Path(self.config.checkpoints_directory)
            (checkpoints_dir / "active").mkdir(exist_ok=True)
            (checkpoints_dir / "archived").mkdir(exist_ok=True)
            
            reports_dir = Path(self.config.reports_directory)
            (reports_dir / "corruption").mkdir(exist_ok=True)
            (reports_dir / "verification").mkdir(exist_ok=True)
            (reports_dir / "repair").mkdir(exist_ok=True)
            
            logger.info("Integrity directories initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize integrity directories: {str(e)}")
            raise
    
    async def create_checkpoint(
        self,
        file_path: str,
        integrity_level: Optional[IntegrityLevel] = None
    ) -> Dict[str, Any]:
        """Create integrity checkpoint for file"""



        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }
            
            if not file_path_obj.is_file():
                return {
                    'success': False,
                    'error': f'Path is not a file: {file_path}'
                }
            
            # Generate checkpoint ID
            checkpoint_id = f"checkpoint_{int(time.time())}_{hash(file_path) & 0xFFFF:04x}"
            
            # Calculate checksums
            integrity_level = integrity_level or self.config.default_integrity_level
            checksums = await self._calculate_checksums(file_path_obj, integrity_level)
            
            if not checksums['success']:
                return checksums
            
            # Get file metadata
            file_stat = file_path_obj.stat()
            
            # Create checkpoint
            checkpoint = IntegrityCheckpoint(
                checkpoint_id=checkpoint_id,
                file_path=file_path,
                file_size=file_stat.st_size,
                md5_hash=checksums['md5'],
                sha256_hash=checksums['sha256'],
                crc32_checksum=checksums['crc32'],
                created_at=datetime.now(),
                file_permissions=oct(file_stat.st_mode)[-3:],
                file_owner=str(file_stat.st_uid)
            )
            
            # Add extended attributes if available
            checkpoint.extended_attributes = await self._get_extended_attributes(file_path_obj)
            
            # Store checkpoint
            self.checkpoints[checkpoint_id] = checkpoint
            
            # Save checkpoint to disk
            await self._save_checkpoint(checkpoint)
            
            logger.info(f"Integrity checkpoint created: {checkpoint_id} for {file_path}")
            
            return {
                'success': True,
                'checkpoint_id': checkpoint_id,
                'file_path': file_path,
                'file_size': checkpoint.file_size,
                'checksums': {
                    'md5': checkpoint.md5_hash,
                    'sha256': checkpoint.sha256_hash,
                    'crc32': checkpoint.crc32_checksum
                },
                'created_at': checkpoint.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint for {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def verify_file(
        self,
        file_path: str,
        checkpoint_id: Optional[str] = None,
        create_if_missing: bool = True
    ) -> Dict[str, Any]:
        """Verify file integrity"""



        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                return {
                    'success': False,
                    'error': f'File not found: {file_path}',
                    'status': VerificationStatus.FAILED.value
                }
            
            # Find or create checkpoint
            if checkpoint_id:
                if checkpoint_id not in self.checkpoints:
                    return {
                        'success': False,
                        'error': f'Checkpoint not found: {checkpoint_id}',
                        'status': VerificationStatus.FAILED.value
                    }
                checkpoint = self.checkpoints[checkpoint_id]
            else:
                # Find checkpoint by file path
                checkpoint = None
                for cp in self.checkpoints.values():
                    if cp.file_path == file_path:
                        checkpoint = cp
                        break
                
                if not checkpoint and create_if_missing:
                    # Create new checkpoint
                    result = await self.create_checkpoint(file_path)
                    if result['success']:
                        checkpoint = self.checkpoints[result['checkpoint_id']]
                    else:
                        return result
                elif not checkpoint:
                    return {
                        'success': False,
                        'error': f'No checkpoint found for file: {file_path}',
                        'status': VerificationStatus.FAILED.value
                    }
            
            # Add to active verifications
            self.active_verifications.add(checkpoint.checkpoint_id)
            
            try:
                # Perform verification
                verification_result = await self.verification_engine.verify_checkpoint(checkpoint)
                
                # Update checkpoint
                checkpoint.last_verified = datetime.now()
                checkpoint.verification_count += 1
                
                if verification_result['success']:
                    if verification_result['integrity_verified']:
                        checkpoint.corruption_detected = False
                        
                        # Update metrics
                        self.metrics['total_verifications'] += 1
                        self.metrics['successful_verifications'] += 1
                        
                        return {
                            'success': True,
                            'checkpoint_id': checkpoint.checkpoint_id,
                            'file_path': file_path,
                            'status': VerificationStatus.COMPLETED.value,
                            'integrity_verified': True,
                            'verification_time': verification_result.get('verification_time', 0)
                        }
                    else:
                        # Corruption detected
                        checkpoint.corruption_detected = True
                        
                        # Create corruption report
                        corruption_report = await self._create_corruption_report(
                            checkpoint, verification_result
                        )
                        
                        # Update metrics
                        self.metrics['corruptions_detected'] += 1
                        
                        # Attempt automatic repair if enabled
                        repair_result = None
                        if self.config.auto_repair_enabled:
                            repair_result = await self.repair_engine.attempt_repair(
                                checkpoint, corruption_report
                            )
                        
                        return {
                            'success': True,
                            'checkpoint_id': checkpoint.checkpoint_id,
                            'file_path': file_path,
                            'status': VerificationStatus.CORRUPTED.value,
                            'integrity_verified': False,
                            'corruption_report_id': corruption_report.report_id,
                            'corruption_severity': corruption_report.severity.value,
                            'repair_attempted': repair_result is not None,
                            'repair_successful': repair_result['success'] if repair_result else False
                        }
                else:
                    return {
                        'success': False,
                        'error': verification_result.get('error', 'Verification failed'),
                        'status': VerificationStatus.FAILED.value
                    }
                
            finally:
                self.active_verifications.discard(checkpoint.checkpoint_id)
                
                # Save updated checkpoint
                await self._save_checkpoint(checkpoint)
            
        except Exception as e:
            logger.error(f"File verification failed for {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status': VerificationStatus.FAILED.value
            }
    
    async def scan_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        integrity_level: Optional[IntegrityLevel] = None
    ) -> Dict[str, Any]:
        """Scan directory for integrity verification"""



        try:
            directory_path_obj = Path(directory_path)
            
            if not directory_path_obj.exists():
                return {
                    'success': False,
                    'error': f'Directory not found: {directory_path}'
                }
            
            if not directory_path_obj.is_dir():
                return {
                    'success': False,
                    'error': f'Path is not a directory: {directory_path}'
                }
            
            scan_results = {
                'total_files': 0,
                'verified_files': 0,
                'corrupted_files': 0,
                'failed_verifications': 0,
                'new_checkpoints': 0,
                'corruption_reports': [],
                'scan_duration': 0.0
            }
            
            start_time = datetime.now()
            
            # Get file list
            if recursive:
                files = [f for f in directory_path_obj.rglob("*") if f.is_file()]
            else:
                files = [f for f in directory_path_obj.iterdir() if f.is_file()]
            
            scan_results['total_files'] = len(files)
            
            # Process files in batches to avoid overwhelming the system
            batch_size = min(self.config.max_concurrent_verifications, 50)
            
            for i in range(0, len(files), batch_size):
                batch = files[i:i + batch_size]
                
                # Create verification tasks
                tasks = []
                for file_path in batch:
                    task = asyncio.create_task(
                        self.verify_file(str(file_path), create_if_missing=True)
                    )
                    tasks.append(task)
                
                # Wait for batch completion
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in batch_results:
                    if isinstance(result, Exception):
                        scan_results['failed_verifications'] += 1
                        logger.error(f"Verification error: {str(result)}")
                        continue
                    
                    if result['success']:
                        if result.get('integrity_verified', False):
                            scan_results['verified_files'] += 1
                        elif result.get('status') == VerificationStatus.CORRUPTED.value:
                            scan_results['corrupted_files'] += 1
                            scan_results['corruption_reports'].append({
                                'file_path': result['file_path'],
                                'corruption_report_id': result.get('corruption_report_id'),
                                'severity': result.get('corruption_severity')
                            })
                        
                        if 'checkpoint_id' in result:
                            scan_results['new_checkpoints'] += 1
                    else:
                        scan_results['failed_verifications'] += 1
            
            scan_results['scan_duration'] = (datetime.now() - start_time).total_seconds()
            
            # Update metrics
            if scan_results['total_files'] > 0:
                integrity_score = (scan_results['verified_files'] / scan_results['total_files']) * 100
                self.metrics['data_integrity_score'] = integrity_score
            
            self.metrics['last_full_scan'] = datetime.now().isoformat()
            
            logger.info(f"Directory scan completed: {directory_path} - {scan_results['total_files']} files")
            
            return {
                'success': True,
                'directory_path': directory_path,
                'scan_results': scan_results
            }
            
        except Exception as e:
            logger.error(f"Directory scan failed for {directory_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def repair_corruption(
        self,
        report_id: str,
        repair_strategy: Optional[RepairStrategy] = None
    ) -> Dict[str, Any]:
        """Repair detected corruption"""



        try:
            if report_id not in self.corruption_reports:
                return {
                    'success': False,
                    'error': f'Corruption report not found: {report_id}'
                }
            
            corruption_report = self.corruption_reports[report_id]
            
            if corruption_report.resolved:
                return {
                    'success': False,
                    'error': f'Corruption already resolved: {report_id}'
                }
            
            # Get associated checkpoint
            checkpoint = None
            for cp in self.checkpoints.values():
                if cp.checkpoint_id == corruption_report.checkpoint_id:
                    checkpoint = cp
                    break
            
            if not checkpoint:
                return {
                    'success': False,
                    'error': f'Associated checkpoint not found: {corruption_report.checkpoint_id}'
                }
            
            # Use provided strategy or recommended strategy
            strategy = repair_strategy or corruption_report.recommended_strategy
            
            if not strategy:
                strategy = RepairStrategy.AUTO_REPAIR
            
            # Attempt repair
            repair_result = await self.repair_engine.repair_with_strategy(
                checkpoint, corruption_report, strategy
            )
            
            if repair_result['success']:
                # Update corruption report
                corruption_report.resolved = True
                corruption_report.resolution_method = strategy.value
                corruption_report.resolved_at = datetime.now()
                
                # Update checkpoint
                checkpoint.repair_attempts += 1
                checkpoint.last_repair = datetime.now()
                checkpoint.repair_strategy = strategy
                
                # Re-verify after repair
                verification_result = await self.verify_file(checkpoint.file_path, checkpoint.checkpoint_id)
                
                if verification_result.get('integrity_verified', False):
                    checkpoint.corruption_detected = False
                    self.metrics['corruptions_repaired'] += 1
                
                # Save updates
                await self._save_checkpoint(checkpoint)
                await self._save_corruption_report(corruption_report)
                
                logger.info(f"Corruption repaired: {report_id} using {strategy.value}")
                
                return {
                    'success': True,
                    'report_id': report_id,
                    'repair_strategy': strategy.value,
                    'verification_result': verification_result,
                    'repair_details': repair_result.get('details', {})
                }
            else:
                return {
                    'success': False,
                    'error': repair_result.get('error', 'Repair failed'),
                    'report_id': report_id
                }
            
        except Exception as e:
            logger.error(f"Corruption repair failed for {report_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_integrity_report(self) -> Dict[str, Any]:
        """Get comprehensive integrity report"""



        try:
            # Calculate statistics
            total_checkpoints = len(self.checkpoints)
            corrupted_checkpoints = len([cp for cp in self.checkpoints.values() if cp.corruption_detected])
            
            # Corruption severity distribution
            severity_counts = {}
            for severity in CorruptionSeverity:
                severity_counts[severity.value] = len([
                    report for report in self.corruption_reports.values()
                    if report.severity == severity and not report.resolved
                ])
            
            # Recent activity
            last_24h = datetime.now() - timedelta(hours=24)
            recent_verifications = len([
                cp for cp in self.checkpoints.values()
                if cp.last_verified and cp.last_verified >= last_24h
            ])
            
            recent_corruptions = len([
                report for report in self.corruption_reports.values()
                if report.detected_at >= last_24h
            ])
            
            # Repair success rate
            total_repairs = len([
                report for report in self.corruption_reports.values()
                if report.resolved
            ])
            
            repair_success_rate = 0.0
            if self.metrics['corruptions_detected'] > 0:
                repair_success_rate = (self.metrics['corruptions_repaired'] / self.metrics['corruptions_detected']) * 100
            
            return {
                'success': True,
                'report_generated_at': datetime.now().isoformat(),
                'overall_status': {
                    'total_checkpoints': total_checkpoints,
                    'healthy_checkpoints': total_checkpoints - corrupted_checkpoints,
                    'corrupted_checkpoints': corrupted_checkpoints,
                    'data_integrity_score': self.metrics['data_integrity_score']
                },
                'corruption_analysis': {
                    'total_corruptions_detected': self.metrics['corruptions_detected'],
                    'corruptions_repaired': self.metrics['corruptions_repaired'],
                    'unresolved_corruptions': len([
                        report for report in self.corruption_reports.values()
                        if not report.resolved
                    ]),
                    'severity_distribution': severity_counts,
                    'repair_success_rate': repair_success_rate
                },
                'recent_activity': {
                    'verifications_last_24h': recent_verifications,
                    'corruptions_last_24h': recent_corruptions,
                    'active_verifications': len(self.active_verifications)
                },
                'performance_metrics': self.metrics,
                'system_health': {
                    'last_full_scan': self.metrics['last_full_scan'],
                    'average_verification_time': self.metrics['average_verification_time'],
                    'false_positive_rate': (self.metrics['false_positives'] / max(self.metrics['total_verifications'], 1)) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate integrity report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Private implementation methods
    
    async def _calculate_checksums(
        self,
        file_path: Path,
        integrity_level: IntegrityLevel
    ) -> Dict[str, Any]:
        """Calculate file checksums based on integrity level"""



        try:
            checksums = {}
            
            # Always calculate basic checksums
            md5_hash = hashlib.md5()
            sha256_hash = hashlib.sha256()
            crc32_checksum = 0
            
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(self.config.verification_chunk_size):
                    md5_hash.update(chunk)
                    sha256_hash.update(chunk)
                    crc32_checksum = zlib.crc32(chunk, crc32_checksum)
            
            checksums['md5'] = md5_hash.hexdigest()
            checksums['sha256'] = sha256_hash.hexdigest()
            checksums['crc32'] = format(crc32_checksum & 0xffffffff, '08x')
            
            # Additional checksums for higher integrity levels
            if integrity_level in [IntegrityLevel.ADVANCED, IntegrityLevel.PARANOID]:
                # Add more sophisticated integrity checks
                checksums['blake2b'] = await self._calculate_blake2b(file_path)
                
            if integrity_level == IntegrityLevel.PARANOID:
                # Add even more integrity checks
                checksums['sha3_256'] = await self._calculate_sha3_256(file_path)
                checksums['file_structure'] = await self._analyze_file_structure(file_path)
            
            return {
                'success': True,
                **checksums
            }
            
        except Exception as e:
            logger.error(f"Checksum calculation failed for {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _calculate_blake2b(self, file_path: Path) -> str:
        """Calculate BLAKE2b hash"""



        try:
            blake2b_hash = hashlib.blake2b()
            
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(self.config.verification_chunk_size):
                    blake2b_hash.update(chunk)
            
            return blake2b_hash.hexdigest()
            
        except Exception:
            return ""
    
    async def _calculate_sha3_256(self, file_path: Path) -> str:
        """Calculate SHA3-256 hash"""



        try:
            sha3_hash = hashlib.sha3_256()
            
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(self.config.verification_chunk_size):
                    sha3_hash.update(chunk)
            
            return sha3_hash.hexdigest()
            
        except Exception:
            return ""
    
    async def _analyze_file_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze file structure for corruption patterns"""



        try:
            structure_info = {
                'file_type': file_path.suffix.lower(),
                'size': file_path.stat().st_size,
                'null_bytes': 0,
                'entropy': 0.0
            }
            
            # Simple structure analysis
            async with aiofiles.open(file_path, 'rb') as f:
                chunk = await f.read(min(1024, file_path.stat().st_size))
                
                # Count null bytes
                structure_info['null_bytes'] = chunk.count(b'\x00')
                
                # Calculate basic entropy
                if len(chunk) > 0:
                    byte_counts = [0] * 256
                    for byte in chunk:
                        byte_counts[byte] += 1
                    
                    entropy = 0.0
                    for count in byte_counts:
                        if count > 0:
                            probability = count / len(chunk)
                            entropy -= probability * (probability.bit_length() - 1)
                    
                    structure_info['entropy'] = entropy
            
            return structure_info
            
        except Exception as e:
            logger.error(f"File structure analysis failed: {str(e)}")
            return {}
    
    async def _get_extended_attributes(self, file_path: Path) -> Dict[str, Any]:
        """Get extended file attributes"""



        try:
            attributes = {}
            
            # Get basic file attributes
            stat_info = file_path.stat()
            attributes['inode'] = stat_info.st_ino
            attributes['device'] = stat_info.st_dev
            attributes['links'] = stat_info.st_nlink
            attributes['access_time'] = stat_info.st_atime
            attributes['modify_time'] = stat_info.st_mtime
            attributes['change_time'] = stat_info.st_ctime
            
            return attributes
            
        except Exception as e:
            logger.error(f"Extended attributes collection failed: {str(e)}")
            return {}
    
    async def _create_corruption_report(
        self,
        checkpoint: IntegrityCheckpoint,
        verification_result: Dict[str, Any]
    ) -> CorruptionReport:
        """Create corruption report"""
        report_id = f"corruption_{int(time.time())}_{hash(checkpoint.file_path) & 0xFFFF:04x}"
        
        # Determine corruption severity
        severity = CorruptionSeverity.MINOR
        if verification_result.get('multiple_checksum_failures', False):
            severity = CorruptionSeverity.MAJOR
        if verification_result.get('file_unreadable', False):
            severity = CorruptionSeverity.CRITICAL
        
        # Create report
        corruption_report = CorruptionReport(
            report_id=report_id,
            checkpoint_id=checkpoint.checkpoint_id,
            file_path=checkpoint.file_path,
            corruption_type=verification_result.get('corruption_type', 'checksum_mismatch'),
            severity=severity,
            detected_at=datetime.now(),
            expected_checksums={
                'md5': checkpoint.md5_hash,
                'sha256': checkpoint.sha256_hash,
                'crc32': checkpoint.crc32_checksum
            },
            actual_checksums=verification_result.get('actual_checksums', {}),
            differences=verification_result.get('differences', [])
        )
        
        # Analyze repairability
        corruption_report.is_repairable = await self._assess_repairability(corruption_report)
        corruption_report.repair_confidence = verification_result.get('repair_confidence', 0.0)
        corruption_report.recommended_strategy = await self._recommend_repair_strategy(corruption_report)
        
        # Store report
        self.corruption_reports[report_id] = corruption_report
        
        # Save report to disk
        await self._save_corruption_report(corruption_report)
        
        return corruption_report
    
    async def _assess_repairability(self, corruption_report: CorruptionReport) -> bool:
        """Assess if corruption is repairable"""



        try:
            # Basic repairability heuristics
            if corruption_report.severity == CorruptionSeverity.CATASTROPHIC:
                return False
            
            if corruption_report.corruption_type == "file_missing":
                return False
            
            if corruption_report.corruption_type == "checksum_mismatch":
                return True
            
            return True
            
        except Exception:
            return False
    
    async def _recommend_repair_strategy(self, corruption_report: CorruptionReport) -> RepairStrategy:
        """Recommend repair strategy based on corruption analysis"""



        try:
            if corruption_report.severity == CorruptionSeverity.CRITICAL:
                return RepairStrategy.BACKUP_RESTORE
            
            if corruption_report.severity == CorruptionSeverity.MAJOR:
                return RepairStrategy.REDUNDANT_COPY
            
            if corruption_report.is_repairable:
                return RepairStrategy.AUTO_REPAIR
            
            return RepairStrategy.MANUAL_INTERVENTION
            
        except Exception:
            return RepairStrategy.QUARANTINE
    
    async def _start_monitoring(self) -> None:
        """Start background monitoring"""



        try:
            # Start scheduler
            await self.scheduler.start()
            
            # Real-time monitoring if enabled
            if self.config.real_time_monitoring:
                asyncio.create_task(self._real_time_monitor())
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
    
    async def _real_time_monitor(self) -> None:
        """Real-time file system monitoring"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Monitor active checkpoints for changes
                for checkpoint in list(self.checkpoints.values()):
                    file_path = Path(checkpoint.file_path)
                    
                    if file_path.exists():
                        current_stat = file_path.stat()
                        
                        # Check if file was modified
                        if current_stat.st_mtime > checkpoint.last_verified.timestamp():
                            # File was modified, schedule verification
                            asyncio.create_task(
                                self.verify_file(checkpoint.file_path, checkpoint.checkpoint_id)
                            )
                
            except Exception as e:
                logger.error(f"Real-time monitoring error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _save_checkpoint(self, checkpoint: IntegrityCheckpoint) -> None:
        """Save checkpoint to disk"""



        try:
            checkpoint_path = Path(self.config.checkpoints_directory) / "active" / f"{checkpoint.checkpoint_id}.json"
            
            checkpoint_data = {
                'checkpoint_id': checkpoint.checkpoint_id,
                'file_path': checkpoint.file_path,
                'file_size': checkpoint.file_size,
                'md5_hash': checkpoint.md5_hash,
                'sha256_hash': checkpoint.sha256_hash,
                'crc32_checksum': checkpoint.crc32_checksum,
                'created_at': checkpoint.created_at.isoformat(),
                'file_permissions': checkpoint.file_permissions,
                'file_owner': checkpoint.file_owner,
                'last_verified': checkpoint.last_verified.isoformat() if checkpoint.last_verified else None,
                'verification_count': checkpoint.verification_count,
                'corruption_detected': checkpoint.corruption_detected,
                'extended_attributes': checkpoint.extended_attributes,
                'repair_attempts': checkpoint.repair_attempts,
                'last_repair': checkpoint.last_repair.isoformat() if checkpoint.last_repair else None,
                'repair_strategy': checkpoint.repair_strategy.value if checkpoint.repair_strategy else None
            }
            
            async with aiofiles.open(checkpoint_path, 'w') as f:
                await f.write(json.dumps(checkpoint_data, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {str(e)}")
    
    async def _save_corruption_report(self, corruption_report: CorruptionReport) -> None:
        """Save corruption report to disk"""



        try:
            report_path = Path(self.config.reports_directory) / "corruption" / f"{corruption_report.report_id}.json"
            
            report_data = {
                'report_id': corruption_report.report_id,
                'checkpoint_id': corruption_report.checkpoint_id,
                'file_path': corruption_report.file_path,
                'corruption_type': corruption_report.corruption_type,
                'severity': corruption_report.severity.value,
                'detected_at': corruption_report.detected_at.isoformat(),
                'expected_checksums': corruption_report.expected_checksums,
                'actual_checksums': corruption_report.actual_checksums,
                'differences': corruption_report.differences,
                'file_analysis': corruption_report.file_analysis,
                'corruption_patterns': corruption_report.corruption_patterns,
                'is_repairable': corruption_report.is_repairable,
                'repair_confidence': corruption_report.repair_confidence,
                'recommended_strategy': corruption_report.recommended_strategy.value if corruption_report.recommended_strategy else None,
                'resolved': corruption_report.resolved,
                'resolution_method': corruption_report.resolution_method,
                'resolved_at': corruption_report.resolved_at.isoformat() if corruption_report.resolved_at else None
            }
            
            async with aiofiles.open(report_path, 'w') as f:
                await f.write(json.dumps(report_data, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to save corruption report: {str(e)}")


class VerificationEngine:
    """Handles file verification operations"""
    
    def __init__(self, integrity_checker: IntegrityChecker):
        """Initialize verification engine"""
        self.integrity_checker = integrity_checker
    
    async def verify_checkpoint(self, checkpoint: IntegrityCheckpoint) -> Dict[str, Any]:
        """Verify checkpoint integrity"""



        try:
            start_time = datetime.now()
            file_path = Path(checkpoint.file_path)
            
            if not file_path.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'integrity_verified': False
                }
            
            # Calculate current checksums
            current_checksums = await self.integrity_checker._calculate_checksums(
                file_path, IntegrityLevel.STANDARD
            )
            
            if not current_checksums['success']:
                return current_checksums
            
            # Compare checksums
            integrity_verified = True
            differences = []
            
            if current_checksums['md5'] != checkpoint.md5_hash:
                integrity_verified = False
                differences.append(f"MD5 mismatch: expected {checkpoint.md5_hash}, got {current_checksums['md5']}")
            
            if current_checksums['sha256'] != checkpoint.sha256_hash:
                integrity_verified = False
                differences.append(f"SHA256 mismatch: expected {checkpoint.sha256_hash}, got {current_checksums['sha256']}")
            
            if current_checksums['crc32'] != checkpoint.crc32_checksum:
                integrity_verified = False
                differences.append(f"CRC32 mismatch: expected {checkpoint.crc32_checksum}, got {current_checksums['crc32']}")
            
            verification_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'integrity_verified': integrity_verified,
                'verification_time': verification_time,
                'actual_checksums': current_checksums,
                'differences': differences,
                'corruption_type': 'checksum_mismatch' if not integrity_verified else None,
                'multiple_checksum_failures': len(differences) > 1
            }
            
        except Exception as e:
            logger.error(f"Checkpoint verification failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'integrity_verified': False
            }


class CorruptionDetector:
    """Detects various types of data corruption"""
    
    def __init__(self, integrity_checker: IntegrityChecker):
        """Initialize corruption detector"""
        self.integrity_checker = integrity_checker
    
    async def detect_corruption_patterns(self, file_path: Path) -> List[str]:
        """Detect corruption patterns in file"""
        patterns = []
        
        try:
            # Check for common corruption patterns
            async with aiofiles.open(file_path, 'rb') as f:
                chunk = await f.read(min(1024, file_path.stat().st_size))
                
                # Detect excessive null bytes
                null_ratio = chunk.count(b'\x00') / len(chunk) if len(chunk) > 0 else 0
                if null_ratio > 0.5:
                    patterns.append("excessive_null_bytes")
                
                # Detect repeated patterns
                if len(set(chunk)) < 10 and len(chunk) > 100:
                    patterns.append("repeated_pattern")
                
                # Detect truncation
                if len(chunk) < 1024 and file_path.stat().st_size > 1024:
                    patterns.append("file_truncation")
            
        except Exception as e:
            logger.error(f"Corruption pattern detection failed: {str(e)}")
        
        return patterns


class RepairEngine:
    """Handles corruption repair operations"""
    
    def __init__(self, integrity_checker: IntegrityChecker):
        """Initialize repair engine"""
        self.integrity_checker = integrity_checker
    
    async def attempt_repair(
        self,
        checkpoint: IntegrityCheckpoint,
        corruption_report: CorruptionReport
    ) -> Dict[str, Any]:
        """Attempt automatic repair"""



        try:
            if not corruption_report.is_repairable:
                return {
                    'success': False,
                    'error': 'Corruption is not repairable'
                }
            
            if checkpoint.repair_attempts >= self.integrity_checker.config.max_repair_attempts:
                return {
                    'success': False,
                    'error': 'Maximum repair attempts reached'
                }
            
            # Use recommended strategy
            strategy = corruption_report.recommended_strategy or RepairStrategy.AUTO_REPAIR
            
            return await self.repair_with_strategy(checkpoint, corruption_report, strategy)
            
        except Exception as e:
            logger.error(f"Automatic repair failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def repair_with_strategy(
        self,
        checkpoint: IntegrityCheckpoint,
        corruption_report: CorruptionReport,
        strategy: RepairStrategy
    ) -> Dict[str, Any]:
        """Repair using specific strategy"""



        try:
            if strategy == RepairStrategy.AUTO_REPAIR:
                return await self._auto_repair(checkpoint, corruption_report)
            elif strategy == RepairStrategy.BACKUP_RESTORE:
                return await self._backup_restore(checkpoint, corruption_report)
            elif strategy == RepairStrategy.REDUNDANT_COPY:
                return await self._redundant_copy_restore(checkpoint, corruption_report)
            elif strategy == RepairStrategy.QUARANTINE:
                return await self._quarantine_file(checkpoint, corruption_report)
            else:
                return {
                    'success': False,
                    'error': f'Repair strategy not implemented: {strategy}'
                }
            
        except Exception as e:
            logger.error(f"Repair with strategy {strategy} failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _auto_repair(self, checkpoint: IntegrityCheckpoint, corruption_report: CorruptionReport) -> Dict[str, Any]:
        """Attempt automatic repair"""
        # This is a simplified implementation
        # In a real system, this would implement sophisticated repair algorithms
        return {
            'success': False,
            'error': 'Auto-repair not implemented for this corruption type'
        }
    
    async def _backup_restore(self, checkpoint: IntegrityCheckpoint, corruption_report: CorruptionReport) -> Dict[str, Any]:
        """Restore from backup"""
        # Implement backup restoration logic
        return {
            'success': False,
            'error': 'Backup restore not implemented'
        }
    
    async def _redundant_copy_restore(self, checkpoint: IntegrityCheckpoint, corruption_report: CorruptionReport) -> Dict[str, Any]:
        """Restore from redundant copy"""
        # Implement redundant copy restoration logic
        return {
            'success': False,
            'error': 'Redundant copy restore not implemented'
        }
    
    async def _quarantine_file(self, checkpoint: IntegrityCheckpoint, corruption_report: CorruptionReport) -> Dict[str, Any]:
        """Quarantine corrupted file"""



        try:
            file_path = Path(checkpoint.file_path)
            quarantine_dir = Path(self.integrity_checker.config.storage_root_path) / "quarantine"
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            
            quarantine_path = quarantine_dir / f"{file_path.name}.quarantine.{int(time.time())}"
            
            # Move file to quarantine
            await aiofiles.os.rename(str(file_path), str(quarantine_path))
            
            return {
                'success': True,
                'details': {
                    'quarantine_path': str(quarantine_path),
                    'action': 'file_quarantined'
                }
            }
            
        except Exception as e:
            logger.error(f"File quarantine failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class IntegrityScheduler:
    """Manages scheduled integrity checks"""
    
    def __init__(self, integrity_checker: IntegrityChecker):
        """Initialize integrity scheduler"""
        self.integrity_checker = integrity_checker
        self.scheduler_task = None
    
    async def start(self) -> None:
        """Start the scheduler"""
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
    
    async def stop(self) -> None:
        """Stop the scheduler"""
        if self.scheduler_task:
            self.scheduler_task.cancel()
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while not self.integrity_checker.shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                current_time = datetime.now()
                
                # Check for scheduled verifications
                for checkpoint in self.integrity_checker.checkpoints.values():
                    if self._should_verify(checkpoint, current_time):
                        asyncio.create_task(
                            self.integrity_checker.verify_file(
                                checkpoint.file_path, 
                                checkpoint.checkpoint_id
                            )
                        )
                
                # Periodic cleanup
                if current_time.hour == 2:  # Run cleanup at 2 AM
                    await self._cleanup_old_records()
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {str(e)}")
    
    def _should_verify(self, checkpoint: IntegrityCheckpoint, current_time: datetime) -> bool:
        """Check if checkpoint should be verified"""
        if not checkpoint.last_verified:
            return True
        
        hours_since_verification = (current_time - checkpoint.last_verified).total_seconds() / 3600
        
        return hours_since_verification >= self.integrity_checker.config.verification_interval_hours
    
    async def _cleanup_old_records(self) -> None:
        """Clean up old checkpoints and reports"""



        try:
            current_time = datetime.now()
            
            # Clean up old checkpoints
            retention_date = current_time - timedelta(days=self.integrity_checker.config.checkpoint_retention_days)
            
            expired_checkpoints = [
                checkpoint_id for checkpoint_id, checkpoint in self.integrity_checker.checkpoints.items()
                if checkpoint.created_at < retention_date
            ]
            
            for checkpoint_id in expired_checkpoints:
                del self.integrity_checker.checkpoints[checkpoint_id]
                
                # Remove checkpoint file
                checkpoint_path = Path(self.integrity_checker.config.checkpoints_directory) / "active" / f"{checkpoint_id}.json"
                if checkpoint_path.exists():
                    await aiofiles.os.remove(str(checkpoint_path))
            
            # Clean up old reports
            report_retention_date = current_time - timedelta(days=self.integrity_checker.config.report_retention_days)
            
            expired_reports = [
                report_id for report_id, report in self.integrity_checker.corruption_reports.items()
                if report.detected_at < report_retention_date and report.resolved
            ]
            
            for report_id in expired_reports:
                del self.integrity_checker.corruption_reports[report_id]
                
                # Remove report file
                report_path = Path(self.integrity_checker.config.reports_directory) / "corruption" / f"{report_id}.json"
                if report_path.exists():
                    await aiofiles.os.remove(str(report_path))
            
            logger.info(f"Cleanup completed: {len(expired_checkpoints)} checkpoints, {len(expired_reports)} reports removed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")


# Export classes
__all__ = [
    'IntegrityChecker',
    'VerificationEngine',
    'CorruptionDetector',
    'RepairEngine',
    'IntegrityScheduler',
    'IntegrityCheckpoint',
    'CorruptionReport',
    'IntegrityConfig',
    'IntegrityLevel',
    'CorruptionSeverity',
    'VerificationStatus',
    'RepairStrategy'
]
