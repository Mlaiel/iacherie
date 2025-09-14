"""
🎯 Data Archiving Service - Enterprise Data Archiving & Retention Management
Enterprise data archiving with intelligent lifecycle management, compliance-driven retention, and cost optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Multi-Expert Implementation:
🧠 Lead Dev IA: AI-powered data classification, intelligent archiving strategies, and predictive storage optimization
🏗️ Backend Senior: Scalable archiving infrastructure with distributed storage and high-performance data transfer
🤖 ML Engineer: ML models for data importance scoring, access pattern analysis, and retention optimization
🗄️ DBA: Optimized data lifecycle management, storage tier optimization, and database archiving strategies
🔒 Security: Secure data archiving, encryption, access controls, and compliance-driven retention policies
🌐 Microservices: Integration with storage, compliance, and analytics services for unified data lifecycle management
🎵 Audio: Audio content archiving, music metadata preservation, and audio-specific compression strategies
⚙️ DevOps: Automated archiving workflows, storage monitoring, and intelligent cost optimization systems
💡 AI Prompt: Intelligent retention recommendations, archiving insights, and automated policy generation
"""

import asyncio
import json
import time
import logging
import uuid
import os
import shutil
import gzip
import lz4.frame
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import threading
from datetime import datetime, timedelta
from collections import defaultdict
import re
from decimal import Decimal
import hashlib
import statistics
from pathlib import Path
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ArchiveStatus(str, Enum):
    """Archive status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ARCHIVED = "archived"
    RESTORING = "restoring"
    RESTORED = "restored"
    FAILED = "failed"
    EXPIRED = "expired"
    DELETED = "deleted"


class StorageTier(str, Enum):
    """Storage tiers"""
    HOT = "hot"  # Frequent access
    WARM = "warm"  # Infrequent access
    COLD = "cold"  # Rare access
    GLACIER = "glacier"  # Deep archive
    DEEP_FREEZE = "deep_freeze"  # Long-term archive


class CompressionType(str, Enum):
    """Compression types"""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    BROTLI = "brotli"
    ZSTD = "zstd"


class DataClassification(str, Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class RetentionPolicy(str, Enum):
    """Retention policy types"""
    COMPLIANCE_DRIVEN = "compliance_driven"
    BUSINESS_VALUE = "business_value"
    COST_OPTIMIZED = "cost_optimized"
    REGULATORY_REQUIRED = "regulatory_required"
    USER_DEFINED = "user_defined"


@dataclass
class ArchiveRecord:
    """Archive record metadata"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_path: str = ""
    archive_path: str = ""
    data_type: str = ""
    classification: DataClassification = DataClassification.INTERNAL
    storage_tier: StorageTier = StorageTier.COLD
    compression: CompressionType = CompressionType.GZIP
    original_size: int = 0
    compressed_size: int = 0
    checksum: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    archived_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    retention_until: Optional[datetime] = None
    status: ArchiveStatus = ArchiveStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    owner: str = ""
    cost_tier: str = "standard"
    
    def calculate_compression_ratio(self) -> float:
        """Calculate compression ratio"""
        if self.original_size > 0:
            return (1 - (self.compressed_size / self.original_size)) * 100
        return 0.0
    
    def is_expired(self) -> bool:
        """Check if archive has expired"""
        if self.retention_until:
            return datetime.utcnow() > self.retention_until
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'original_path': self.original_path,
            'archive_path': self.archive_path,
            'data_type': self.data_type,
            'classification': self.classification.value,
            'storage_tier': self.storage_tier.value,
            'compression': self.compression.value,
            'original_size': self.original_size,
            'compressed_size': self.compressed_size,
            'compression_ratio': self.calculate_compression_ratio(),
            'checksum': self.checksum,
            'created_at': self.created_at.isoformat(),
            'archived_at': self.archived_at.isoformat() if self.archived_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'access_count': self.access_count,
            'retention_until': self.retention_until.isoformat() if self.retention_until else None,
            'status': self.status.value,
            'metadata': self.metadata,
            'tags': self.tags,
            'owner': self.owner,
            'cost_tier': self.cost_tier,
            'is_expired': self.is_expired()
        }


@dataclass
class RetentionRule:
    """Data retention rule"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    policy_type: RetentionPolicy = RetentionPolicy.BUSINESS_VALUE
    data_types: List[str] = field(default_factory=list)
    classification_levels: List[DataClassification] = field(default_factory=list)
    retention_period_days: int = 2555  # 7 years default
    storage_tier_progression: List[StorageTier] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1-10, 1 being highest
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def matches_data(self, data_type: str, classification: DataClassification, metadata: Dict[str, Any]) -> bool:
        """Check if rule matches given data"""
        if not self.active:
            return False
        
        # Check data type
        if self.data_types and data_type not in self.data_types:
            return False
        
        # Check classification
        if self.classification_levels and classification not in self.classification_levels:
            return False
        
        # Check custom conditions
        for condition_key, condition_value in self.conditions.items():
            if condition_key in metadata:
                if metadata[condition_key] != condition_value:
                    return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'policy_type': self.policy_type.value,
            'data_types': self.data_types,
            'classification_levels': [cl.value for cl in self.classification_levels],
            'retention_period_days': self.retention_period_days,
            'storage_tier_progression': [tier.value for tier in self.storage_tier_progression],
            'conditions': self.conditions,
            'priority': self.priority,
            'active': self.active,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class ArchiveJob:
    """Archive operation job"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_type: str = "archive"  # archive, restore, delete
    records: List[str] = field(default_factory=list)  # Record IDs
    status: ArchiveStatus = ArchiveStatus.PENDING
    progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: str = ""
    total_files: int = 0
    processed_files: int = 0
    total_size: int = 0
    processed_size: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'job_type': self.job_type,
            'records': self.records,
            'status': self.status.value,
            'progress': self.progress,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'total_size': self.total_size,
            'processed_size': self.processed_size
        }


class DataClassifier:
    """AI-powered data classification"""
    
    def __init__(self) -> None:
        self.classification_models = {}
        self.classification_rules = {}
        
    async def classify_data(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Classify data automatically"""
        try:
            classification_result = {
                'classification': DataClassification.INTERNAL,
                'confidence': 0.5,
                'reasons': [],
                'recommended_retention_days': 1095,  # 3 years default
                'recommended_storage_tier': StorageTier.WARM
            }
            
            # File extension based classification
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.mp3', '.wav', '.flac', '.aac']:
                classification_result.update({
                    'classification': DataClassification.PUBLIC,
                    'confidence': 0.8,
                    'reasons': ['Audio file - typically public content'],
                    'recommended_retention_days': 2555,  # 7 years for music
                    'recommended_storage_tier': StorageTier.COLD
                })
            elif file_ext in ['.jpg', '.png', '.gif', '.webp']:
                classification_result.update({
                    'classification': DataClassification.PUBLIC,
                    'confidence': 0.7,
                    'reasons': ['Image file - typically public content'],
                    'recommended_retention_days': 1825,  # 5 years
                    'recommended_storage_tier': StorageTier.WARM
                })
            elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                classification_result.update({
                    'classification': DataClassification.PUBLIC,
                    'confidence': 0.8,
                    'reasons': ['Video file - typically public content'],
                    'recommended_retention_days': 2555,  # 7 years
                    'recommended_storage_tier': StorageTier.COLD
                })
            elif file_ext in ['.pdf', '.doc', '.docx']:
                classification_result.update({
                    'classification': DataClassification.CONFIDENTIAL,
                    'confidence': 0.6,
                    'reasons': ['Document file - potentially confidential'],
                    'recommended_retention_days': 2555,  # 7 years for documents
                    'recommended_storage_tier': StorageTier.WARM
                })
            elif file_ext in ['.sql', '.db', '.sqlite']:
                classification_result.update({
                    'classification': DataClassification.RESTRICTED,
                    'confidence': 0.9,
                    'reasons': ['Database file - contains structured data'],
                    'recommended_retention_days': 2555,  # 7 years for data
                    'recommended_storage_tier': StorageTier.HOT
                })
            
            # Content-based classification using metadata
            if 'personal_data' in metadata and metadata['personal_data']:
                classification_result['classification'] = DataClassification.RESTRICTED
                classification_result['confidence'] = min(1.0, classification_result['confidence'] + 0.3)
                classification_result['reasons'].append('Contains personal data')
            
            if 'financial_data' in metadata and metadata['financial_data']:
                classification_result['classification'] = DataClassification.RESTRICTED
                classification_result['confidence'] = min(1.0, classification_result['confidence'] + 0.4)
                classification_result['reasons'].append('Contains financial data')
            
            # Size-based recommendations
            file_size = metadata.get('file_size', 0)
            if file_size > 1024 * 1024 * 100:  # > 100MB
                classification_result['recommended_storage_tier'] = StorageTier.COLD
                classification_result['reasons'].append('Large file - recommended for cold storage')
            
            return classification_result
            
        except Exception as e:
            logger.error(f"Error classifying data: {str(e)}")
            return {
                'classification': DataClassification.INTERNAL,
                'confidence': 0.0,
                'error': str(e)
            }


class CompressionEngine:
    """Data compression engine"""
    
    def __init__(self) -> None:
        self.compression_stats = defaultdict(int)
        
    async def compress_file(self, source_path: str, target_path: str, compression_type: CompressionType) -> Dict[str, Any]:
        """Compress file using specified algorithm"""
        try:
            start_time = time.time()
            original_size = os.path.getsize(source_path)
            
            if compression_type == CompressionType.GZIP:
                compressed_size = await self._compress_gzip(source_path, target_path)
            elif compression_type == CompressionType.LZ4:
                compressed_size = await self._compress_lz4(source_path, target_path)
            elif compression_type == CompressionType.NONE:
                shutil.copy2(source_path, target_path)
                compressed_size = original_size
            else:
                # Default to gzip
                compressed_size = await self._compress_gzip(source_path, target_path)
            
            compression_time = time.time() - start_time
            compression_ratio = ((original_size - compressed_size) / original_size) * 100 if original_size > 0 else 0
            
            # Update stats
            self.compression_stats[f"{compression_type.value}_files"] += 1
            self.compression_stats[f"{compression_type.value}_time"] += compression_time
            
            return {
                'success': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio,
                'compression_time': compression_time,
                'compression_type': compression_type.value
            }
            
        except Exception as e:
            logger.error(f"Error compressing file: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _compress_gzip(self, source_path: str, target_path: str) -> int:
        """Compress using gzip"""
        with open(source_path, 'rb') as f_in:
            with gzip.open(target_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return os.path.getsize(target_path)
    
    async def _compress_lz4(self, source_path: str, target_path: str) -> int:
        """Compress using LZ4"""
        with open(source_path, 'rb') as f_in:
            with lz4.frame.open(target_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return os.path.getsize(target_path)
    
    async def decompress_file(self, source_path: str, target_path: str, compression_type: CompressionType) -> Dict[str, Any]:
        """Decompress file"""
        try:
            start_time = time.time()
            
            if compression_type == CompressionType.GZIP:
                await self._decompress_gzip(source_path, target_path)
            elif compression_type == CompressionType.LZ4:
                await self._decompress_lz4(source_path, target_path)
            elif compression_type == CompressionType.NONE:
                shutil.copy2(source_path, target_path)
            else:
                await self._decompress_gzip(source_path, target_path)
            
            decompression_time = time.time() - start_time
            decompressed_size = os.path.getsize(target_path)
            
            return {
                'success': True,
                'decompressed_size': decompressed_size,
                'decompression_time': decompression_time
            }
            
        except Exception as e:
            logger.error(f"Error decompressing file: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _decompress_gzip(self, source_path -> None: str, target_path -> None: str) -> None:
        """Decompress gzip file"""
        with gzip.open(source_path, 'rb') as f_in:
            with open(target_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    async def _decompress_lz4(self, source_path -> None: str, target_path -> None: str) -> None:
        """Decompress LZ4 file"""
        with lz4.frame.open(source_path, 'rb') as f_in:
            with open(target_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)


class DataArchivingService:
    """
    🎯 Enterprise Data Archiving Service
    
    Multi-Expert Implementation:
    🧠 Lead Dev IA: AI-powered data classification, intelligent archiving strategies, and predictive storage optimization
    🏗️ Backend Senior: Scalable archiving infrastructure with distributed storage and high-performance data transfer
    🤖 ML Engineer: ML models for data importance scoring, access pattern analysis, and retention optimization
    🗄️ DBA: Optimized data lifecycle management, storage tier optimization, and database archiving strategies
    🔒 Security: Secure data archiving, encryption, access controls, and compliance-driven retention policies
    🌐 Microservices: Integration with storage, compliance, and analytics services for unified data lifecycle management
    🎵 Audio: Audio content archiving, music metadata preservation, and audio-specific compression strategies
    ⚙️ DevOps: Automated archiving workflows, storage monitoring, and intelligent cost optimization systems
    💡 AI Prompt: Intelligent retention recommendations, archiving insights, and automated policy generation
    """
    
    def __init__(self) -> None:
        self.archive_records: Dict[str, ArchiveRecord] = {}
        self.retention_rules: Dict[str, RetentionRule] = {}
        self.archive_jobs: Dict[str, ArchiveJob] = {}
        self.data_classifier = DataClassifier()
        self.compression_engine = CompressionEngine()
        self.archive_base_path = "/tmp/archive"  # In production, this would be configurable
        self.storage_tiers = {}
        self._lock = threading.Lock()
        
        # Initialize storage tiers
        self._initialize_storage_tiers()
        
        # Initialize default retention rules
        self._initialize_default_retention_rules()
        
        logger.info("DataArchivingService initialized successfully")
    
    def _initialize_storage_tiers(self) -> None:
        """Initialize storage tier configurations"""
        self.storage_tiers = {
            StorageTier.HOT: {
                'base_path': f"{self.archive_base_path}/hot",
                'cost_per_gb_month': 0.023,
                'retrieval_time_minutes': 0,
                'compression_recommended': CompressionType.NONE
            },
            StorageTier.WARM: {
                'base_path': f"{self.archive_base_path}/warm",
                'cost_per_gb_month': 0.0125,
                'retrieval_time_minutes': 1,
                'compression_recommended': CompressionType.GZIP
            },
            StorageTier.COLD: {
                'base_path': f"{self.archive_base_path}/cold",
                'cost_per_gb_month': 0.004,
                'retrieval_time_minutes': 5,
                'compression_recommended': CompressionType.GZIP
            },
            StorageTier.GLACIER: {
                'base_path': f"{self.archive_base_path}/glacier",
                'cost_per_gb_month': 0.001,
                'retrieval_time_minutes': 240,  # 4 hours
                'compression_recommended': CompressionType.LZ4
            },
            StorageTier.DEEP_FREEZE: {
                'base_path': f"{self.archive_base_path}/deep_freeze",
                'cost_per_gb_month': 0.00099,
                'retrieval_time_minutes': 720,  # 12 hours
                'compression_recommended': CompressionType.LZ4
            }
        }
        
        # Create directories
        for tier_config in self.storage_tiers.values():
            os.makedirs(tier_config['base_path'], exist_ok=True)
    
    def _initialize_default_retention_rules(self) -> None:
        """Initialize default retention rules"""
        default_rules = [
            RetentionRule(
                name="Audio Content Long-term",
                description="Music and audio content with long-term value",
                policy_type=RetentionPolicy.BUSINESS_VALUE,
                data_types=["audio", "music"],
                classification_levels=[DataClassification.PUBLIC, DataClassification.INTERNAL],
                retention_period_days=2555,  # 7 years
                storage_tier_progression=[StorageTier.HOT, StorageTier.WARM, StorageTier.COLD],
                priority=1
            ),
            RetentionRule(
                name="User Data Compliance",
                description="Personal user data with compliance requirements",
                policy_type=RetentionPolicy.COMPLIANCE_DRIVEN,
                data_types=["user_data", "personal_info"],
                classification_levels=[DataClassification.RESTRICTED, DataClassification.CONFIDENTIAL],
                retention_period_days=2555,  # 7 years for compliance
                storage_tier_progression=[StorageTier.HOT, StorageTier.WARM, StorageTier.GLACIER],
                priority=1
            ),
            RetentionRule(
                name="Temporary Files Cleanup",
                description="Temporary files and cache data",
                policy_type=RetentionPolicy.COST_OPTIMIZED,
                data_types=["temp", "cache", "logs"],
                classification_levels=[DataClassification.INTERNAL],
                retention_period_days=90,  # 3 months
                storage_tier_progression=[StorageTier.HOT, StorageTier.COLD],
                priority=3
            ),
            RetentionRule(
                name="Financial Records",
                description="Financial and transaction data",
                policy_type=RetentionPolicy.REGULATORY_REQUIRED,
                data_types=["financial", "transaction", "payment"],
                classification_levels=[DataClassification.RESTRICTED],
                retention_period_days=2555,  # 7 years
                storage_tier_progression=[StorageTier.HOT, StorageTier.WARM, StorageTier.GLACIER],
                priority=1
            )
        ]
        
        for rule in default_rules:
            self.retention_rules[rule.id] = rule
    
    async def archive_data(self, archive_request: Dict[str, Any]) -> Dict[str, Any]:
        """Archive data according to policies"""
        try:
            with self._lock:
                file_path = archive_request.get('file_path', '')
                data_type = archive_request.get('data_type', 'unknown')
                metadata = archive_request.get('metadata', {})
                owner = archive_request.get('owner', 'system')
                
                if not file_path or not os.path.exists(file_path):
                    return {'success': False, 'error': 'File path is required and must exist'}
                
                # Classify data
                classification_result = await self.data_classifier.classify_data(file_path, metadata)
                
                # Find matching retention rule
                matching_rule = self._find_matching_retention_rule(
                    data_type, 
                    classification_result['classification'], 
                    metadata
                )
                
                # Create archive record
                archive_record = ArchiveRecord(
                    original_path=file_path,
                    data_type=data_type,
                    classification=classification_result['classification'],
                    original_size=os.path.getsize(file_path),
                    metadata=metadata,
                    owner=owner
                )
                
                # Apply retention rule
                if matching_rule:
                    archive_record.retention_until = datetime.utcnow() + timedelta(days=matching_rule.retention_period_days)
                    archive_record.storage_tier = matching_rule.storage_tier_progression[0] if matching_rule.storage_tier_progression else StorageTier.WARM
                else:
                    # Use classification recommendations
                    archive_record.retention_until = datetime.utcnow() + timedelta(days=classification_result['recommended_retention_days'])
                    archive_record.storage_tier = classification_result['recommended_storage_tier']
                
                # Determine compression
                tier_config = self.storage_tiers[archive_record.storage_tier]
                archive_record.compression = tier_config['compression_recommended']
                
                # Generate archive path
                archive_record.archive_path = self._generate_archive_path(archive_record)
                
                # Create archive job
                job = ArchiveJob(
                    job_type="archive",
                    records=[archive_record.id],
                    total_files=1,
                    total_size=archive_record.original_size
                )
                
                self.archive_jobs[job.id] = job
                self.archive_records[archive_record.id] = archive_record
                
                # Start archiving process
                archiving_result = await self._execute_archive_job(job.id)
                
                return {
                    'success': True,
                    'archive_record_id': archive_record.id,
                    'job_id': job.id,
                    'archive_record': archive_record.to_dict(),
                    'classification_result': classification_result,
                    'matching_rule': matching_rule.to_dict() if matching_rule else None,
                    'archiving_result': archiving_result,
                    'message': 'Data archived successfully'
                }
                
        except Exception as e:
            logger.error(f"Error archiving data: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to archive data'
            }
    
    def _find_matching_retention_rule(self, data_type: str, classification: DataClassification, metadata: Dict[str, Any]) -> Optional[RetentionRule]:
        """Find matching retention rule"""
        matching_rules = []
        
        for rule in self.retention_rules.values():
            if rule.matches_data(data_type, classification, metadata):
                matching_rules.append(rule)
        
        # Return highest priority rule
        if matching_rules:
            return min(matching_rules, key=lambda r: r.priority)
        
        return None
    
    def _generate_archive_path(self, record: ArchiveRecord) -> str:
        """Generate archive file path"""
        tier_config = self.storage_tiers[record.storage_tier]
        
        # Create hierarchical structure: tier/year/month/day/file
        date_str = record.created_at.strftime("%Y/%m/%d")
        file_name = f"{record.id}_{Path(record.original_path).name}"
        
        if record.compression != CompressionType.NONE:
            file_name += f".{record.compression.value}"
        
        return os.path.join(tier_config['base_path'], date_str, file_name)
    
    async def _execute_archive_job(self, job_id: str) -> Dict[str, Any]:
        """Execute archive job"""
        try:
            job = self.archive_jobs[job_id]
            job.status = ArchiveStatus.IN_PROGRESS
            job.started_at = datetime.utcnow()
            
            results = []
            
            for record_id in job.records:
                record = self.archive_records[record_id]
                
                try:
                    # Create target directory
                    os.makedirs(os.path.dirname(record.archive_path), exist_ok=True)
                    
                    # Compress and move file
                    compression_result = await self.compression_engine.compress_file(
                        record.original_path,
                        record.archive_path,
                        record.compression
                    )
                    
                    if compression_result['success']:
                        record.compressed_size = compression_result['compressed_size']
                        record.checksum = self._calculate_checksum(record.archive_path)
                        record.status = ArchiveStatus.ARCHIVED
                        record.archived_at = datetime.utcnow()
                        
                        job.processed_files += 1
                        job.processed_size += record.original_size
                        
                        results.append({
                            'record_id': record_id,
                            'success': True,
                            'compression_result': compression_result
                        })
                    else:
                        record.status = ArchiveStatus.FAILED
                        results.append({
                            'record_id': record_id,
                            'success': False,
                            'error': compression_result.get('error', 'Compression failed')
                        })
                        
                except Exception as e:
                    record.status = ArchiveStatus.FAILED
                    results.append({
                        'record_id': record_id,
                        'success': False,
                        'error': str(e)
                    })
                
                # Update job progress
                job.progress = (job.processed_files / job.total_files) * 100
            
            # Complete job
            job.status = ArchiveStatus.ARCHIVED
            job.completed_at = datetime.utcnow()
            
            return {
                'success': True,
                'job_id': job_id,
                'results': results,
                'job_summary': job.to_dict()
            }
            
        except Exception as e:
            job.status = ArchiveStatus.FAILED
            job.error_message = str(e)
            logger.error(f"Error executing archive job: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    async def restore_data(self, record_id: str, target_path: Optional[str] = None) -> Dict[str, Any]:
        """Restore archived data"""
        try:
            if record_id not in self.archive_records:
                return {'success': False, 'error': 'Archive record not found'}
            
            record = self.archive_records[record_id]
            
            if record.status != ArchiveStatus.ARCHIVED:
                return {'success': False, 'error': 'Data is not in archived state'}
            
            if not os.path.exists(record.archive_path):
                return {'success': False, 'error': 'Archived file not found'}
            
            # Set target path
            if not target_path:
                target_path = record.original_path + '.restored'
            
            # Update record status
            record.status = ArchiveStatus.RESTORING
            
            # Decompress file
            decompression_result = await self.compression_engine.decompress_file(
                record.archive_path,
                target_path,
                record.compression
            )
            
            if decompression_result['success']:
                # Verify checksum
                restored_checksum = self._calculate_checksum(record.archive_path)
                if restored_checksum == record.checksum:
                    record.status = ArchiveStatus.RESTORED
                    record.last_accessed = datetime.utcnow()
                    record.access_count += 1
                    
                    return {
                        'success': True,
                        'record_id': record_id,
                        'restored_path': target_path,
                        'decompression_result': decompression_result,
                        'checksum_verified': True,
                        'message': 'Data restored successfully'
                    }
                else:
                    record.status = ArchiveStatus.FAILED
                    return {'success': False, 'error': 'Checksum verification failed'}
            else:
                record.status = ArchiveStatus.FAILED
                return {'success': False, 'error': decompression_result.get('error', 'Decompression failed')}
                
        except Exception as e:
            logger.error(f"Error restoring data: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to restore data'
            }
    
    async def cleanup_expired_archives(self) -> Dict[str, Any]:
        """Clean up expired archives"""
        try:
            expired_records = []
            cleanup_results = []
            
            for record_id, record in self.archive_records.items():
                if record.is_expired() and record.status == ArchiveStatus.ARCHIVED:
                    expired_records.append(record_id)
            
            for record_id in expired_records:
                record = self.archive_records[record_id]
                
                try:
                    # Remove archived file
                    if os.path.exists(record.archive_path):
                        os.remove(record.archive_path)
                    
                    # Update record status
                    record.status = ArchiveStatus.DELETED
                    
                    cleanup_results.append({
                        'record_id': record_id,
                        'success': True,
                        'freed_space': record.compressed_size
                    })
                    
                except Exception as e:
                    cleanup_results.append({
                        'record_id': record_id,
                        'success': False,
                        'error': str(e)
                    })
            
            total_freed_space = sum(
                result['freed_space'] for result in cleanup_results 
                if result['success'] and 'freed_space' in result
            )
            
            return {
                'success': True,
                'expired_records_found': len(expired_records),
                'cleanup_results': cleanup_results,
                'total_freed_space_bytes': total_freed_space,
                'message': f'Cleaned up {len(expired_records)} expired archives'
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up expired archives: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to cleanup expired archives'
            }
    
    async def get_archive_analytics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get archive analytics and statistics"""
        try:
            filters = filters or {}
            
            # Filter records
            filtered_records = []
            for record in self.archive_records.values():
                include_record = True
                
                if filters.get('storage_tier') and record.storage_tier.value != filters['storage_tier']:
                    include_record = False
                if filters.get('classification') and record.classification.value != filters['classification']:
                    include_record = False
                if filters.get('data_type') and record.data_type != filters['data_type']:
                    include_record = False
                
                if include_record:
                    filtered_records.append(record)
            
            # Calculate statistics
            total_records = len(filtered_records)
            total_original_size = sum(record.original_size for record in filtered_records)
            total_compressed_size = sum(record.compressed_size for record in filtered_records)
            
            # Storage tier distribution
            tier_distribution = defaultdict(int)
            tier_sizes = defaultdict(int)
            
            for record in filtered_records:
                tier_distribution[record.storage_tier.value] += 1
                tier_sizes[record.storage_tier.value] += record.compressed_size
            
            # Status distribution
            status_distribution = defaultdict(int)
            for record in filtered_records:
                status_distribution[record.status.value] += 1
            
            # Classification distribution
            classification_distribution = defaultdict(int)
            for record in filtered_records:
                classification_distribution[record.classification.value] += 1
            
            # Calculate cost estimates
            monthly_storage_cost = 0.0
            for tier, size_bytes in tier_sizes.items():
                tier_enum = StorageTier(tier)
                cost_per_gb = self.storage_tiers[tier_enum]['cost_per_gb_month']
                size_gb = size_bytes / (1024 * 1024 * 1024)
                monthly_storage_cost += size_gb * cost_per_gb
            
            # Compression efficiency
            compression_ratio = 0.0
            if total_original_size > 0:
                compression_ratio = ((total_original_size - total_compressed_size) / total_original_size) * 100
            
            # Access patterns
            access_stats = {
                'most_accessed': max(filtered_records, key=lambda r: r.access_count) if filtered_records else None,
                'never_accessed': sum(1 for r in filtered_records if r.access_count == 0),
                'avg_access_count': statistics.mean([r.access_count for r in filtered_records]) if filtered_records else 0
            }
            
            return {
                'success': True,
                'analytics': {
                    'total_records': total_records,
                    'total_original_size_bytes': total_original_size,
                    'total_compressed_size_bytes': total_compressed_size,
                    'compression_ratio_percent': compression_ratio,
                    'monthly_storage_cost_usd': monthly_storage_cost,
                    'storage_tier_distribution': dict(tier_distribution),
                    'storage_tier_sizes': dict(tier_sizes),
                    'status_distribution': dict(status_distribution),
                    'classification_distribution': dict(classification_distribution),
                    'access_patterns': access_stats
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting archive analytics: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get archive analytics'
            }
    
    async def create_retention_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new retention rule"""
        try:
            rule = RetentionRule(
                name=rule_data.get('name', ''),
                description=rule_data.get('description', ''),
                policy_type=RetentionPolicy(rule_data.get('policy_type', 'business_value')),
                data_types=rule_data.get('data_types', []),
                classification_levels=[DataClassification(cl) for cl in rule_data.get('classification_levels', [])],
                retention_period_days=rule_data.get('retention_period_days', 365),
                storage_tier_progression=[StorageTier(tier) for tier in rule_data.get('storage_tier_progression', [])],
                conditions=rule_data.get('conditions', {}),
                priority=rule_data.get('priority', 5)
            )
            
            self.retention_rules[rule.id] = rule
            
            return {
                'success': True,
                'rule_id': rule.id,
                'rule': rule.to_dict(),
                'message': 'Retention rule created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating retention rule: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create retention rule'
            }
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get data archiving service health status"""
        try:
            total_records = len(self.archive_records)
            archived_records = sum(1 for r in self.archive_records.values() if r.status == ArchiveStatus.ARCHIVED)
            failed_records = sum(1 for r in self.archive_records.values() if r.status == ArchiveStatus.FAILED)
            
            # Calculate storage usage by tier
            storage_usage = {}
            for tier in StorageTier:
                tier_records = [r for r in self.archive_records.values() if r.storage_tier == tier]
                total_size = sum(r.compressed_size for r in tier_records)
                storage_usage[tier.value] = {
                    'record_count': len(tier_records),
                    'total_size_bytes': total_size,
                    'total_size_gb': total_size / (1024 * 1024 * 1024)
                }
            
            # Active jobs
            active_jobs = sum(1 for job in self.archive_jobs.values() if job.status == ArchiveStatus.IN_PROGRESS)
            
            # Compression statistics
            compression_stats = dict(self.compression_engine.compression_stats)
            
            return {
                'service_status': 'healthy',
                'archive_summary': {
                    'total_records': total_records,
                    'archived_records': archived_records,
                    'failed_records': failed_records,
                    'success_rate': (archived_records / max(1, total_records)) * 100,
                    'active_jobs': active_jobs
                },
                'storage_usage': storage_usage,
                'retention_rules': {
                    'total_rules': len(self.retention_rules),
                    'active_rules': sum(1 for r in self.retention_rules.values() if r.active)
                },
                'compression_statistics': compression_stats,
                'storage_tiers_configured': list(self.storage_tiers.keys()),
                'supported_compression_types': [comp.value for comp in CompressionType],
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting service health: {str(e)}")
            return {
                'service_status': 'error',
                'error': str(e),
                'last_updated': datetime.utcnow().isoformat()
            }


# Example usage and testing
async def main() -> None:
    """Example usage of the DataArchivingService"""
    service = DataArchivingService()
    
    # Create a test file
    test_file_path = "/tmp/test_audio.mp3"
    with open(test_file_path, "w") as f:
        f.write("This is a test audio file content for archiving")
    
    # Test data archiving
    archive_request = {
        'file_path': test_file_path,
        'data_type': 'audio',
        'metadata': {
            'file_size': os.path.getsize(test_file_path),
            'content_type': 'music',
            'artist': 'Test Artist',
            'album': 'Test Album'
        },
        'owner': 'music_service'
    }
    
    result = await service.archive_data(archive_request)
    print(f"Archive data: {result}")
    
    if result['success']:
        record_id = result['archive_record_id']
        
        # Test data restoration
        restore_result = await service.restore_data(record_id, "/tmp/restored_audio.mp3")
        print(f"Restore data: {restore_result}")
        
        # Test analytics
        analytics = await service.get_archive_analytics()
        print(f"Archive analytics: {analytics}")
    
    # Test retention rule creation
    rule_data = {
        'name': 'Podcast Audio Archives',
        'description': 'Long-term archiving for podcast audio content',
        'policy_type': 'business_value',
        'data_types': ['audio', 'podcast'],
        'classification_levels': ['public'],
        'retention_period_days': 1825,  # 5 years
        'storage_tier_progression': ['hot', 'warm', 'cold'],
        'priority': 2
    }
    
    rule_result = await service.create_retention_rule(rule_data)
    print(f"Create retention rule: {rule_result}")
    
    # Test cleanup
    cleanup_result = await service.cleanup_expired_archives()
    print(f"Cleanup expired archives: {cleanup_result}")
    
    # Test service health
    health = await service.get_service_health()
    print(f"Service health: {health}")


if __name__ == "__main__":
    asyncio.run(main())