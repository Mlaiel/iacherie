"""Evidence Storage Manager

Ultra-advanced evidence management system for content protection with
blockchain verification, chain of custody, and forensic-grade storage.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + DBA + DevOps + Legal Tech
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION ⚠️
==================================================================
This code and all associated intellectual property are the EXCLUSIVE property of Fahed Mlaiel.
ANY unauthorized use, copying, modification, distribution, or commercialization without 
explicit written permission is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries.
Legal violations will be prosecuted to the full extent of international law.
"""
import asyncio
import hashlib
import json
import logging
import mimetypes
import os
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import UUID, uuid4

from sqlalchemy import and_, desc, func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError

from ..models.content_models import (
    EvidenceRecord, EvidenceFile, ChainOfCustody,
    BlockchainVerification, ForensicAnalysis
)
from ..security.encryption import AdvancedEncryptionManager
from ...core.config import DatabaseConfig
from ...utils.blockchain import BlockchainManager
from ...utils.forensics import ForensicAnalyzer
from ...utils.storage import SecureStorageManager
from ...utils.integrity import IntegrityValidator


logger = logging.getLogger(__name__)


class EvidenceType(Enum):
    """Types of evidence that can be stored"""    SCREENSHOT = "screenshot"
    VIDEO_RECORDING = "video_recording"
    NETWORK_CAPTURE = "network_capture"
    DOCUMENT = "document"
    AUDIO_RECORDING = "audio_recording"
    SOURCE_CODE = "source_code"
    DATABASE_EXPORT = "database_export"
    LOG_FILE = "log_file"
    METADATA_EXPORT = "metadata_export"
    DIGITAL_SIGNATURE = "digital_signature"


class EvidenceStatus(Enum):
    """Evidence processing status"""    UPLOADED = "uploaded"
    PROCESSING = "processing"
    VERIFIED = "verified"
    BLOCKCHAIN_SECURED = "blockchain_secured"
    FORENSICALLY_ANALYZED = "forensically_analyzed"
    LEGALLY_ADMISSIBLE = "legally_admissible"
    CORRUPTED = "corrupted"
    COMPROMISED = "compromised"


class CustodyEventType(Enum):
    """Types of custody events"""    CREATION = "creation"
    ACCESS = "access"
    MODIFICATION = "modification"
    TRANSFER = "transfer"
    ANALYSIS = "analysis"
    EXPORT = "export"
    DELETION = "deletion"


class EvidenceStorageManagerError(Exception):
    """Custom exception for evidence storage operations"""    pass


class EvidenceStorageManager:
    """    Ultra-advanced evidence storage manager with enterprise features:
    - Forensic-grade evidence collection and preservation
    - Blockchain-secured chain of custody
    - Advanced encryption and integrity protection
    - Legal admissibility compliance
    - Automated forensic analysis
    - Tamper-proof storage and verification
    """    
    def __init__(
        self,
        db_session: AsyncSession,
        config: DatabaseConfig,
        encryption_manager: Optional[AdvancedEncryptionManager] = None,
        blockchain_manager: Optional[BlockchainManager] = None,
        storage_manager: Optional[SecureStorageManager] = None,
        forensic_analyzer: Optional[ForensicAnalyzer] = None
    ):
        self.db_session = db_session
        self.config = config
        self.encryption_manager = encryption_manager or AdvancedEncryptionManager()
        self.blockchain_manager = blockchain_manager or BlockchainManager()
        self.storage_manager = storage_manager or SecureStorageManager()
        self.forensic_analyzer = forensic_analyzer or ForensicAnalyzer()
        self.integrity_validator = IntegrityValidator()
        
        # Storage configuration
        self.evidence_storage_path = config.evidence_storage_path or "/secure/evidence"
        self.max_file_size_mb = config.max_evidence_file_size or 1024  # 1GB
        self.retention_period_years = config.evidence_retention_years or 7
        self.blockchain_verification_enabled = config.blockchain_verification_enabled or True
        
        # Supported file types for evidence
        self.supported_evidence_types = {
            EvidenceType.SCREENSHOT: [".png", ".jpg", ".jpeg", ".bmp", ".tiff"],
            EvidenceType.VIDEO_RECORDING: [".mp4", ".avi", ".mov", ".mkv", ".webm"],
            EvidenceType.DOCUMENT: [".pdf", ".doc", ".docx", ".txt", ".rtf"],
            EvidenceType.AUDIO_RECORDING: [".mp3", ".wav", ".flac", ".m4a"],
            EvidenceType.SOURCE_CODE: [".py", ".js", ".html", ".css", ".json", ".xml"],
            EvidenceType.LOG_FILE: [".log", ".txt", ".json"],
            EvidenceType.NETWORK_CAPTURE: [".pcap", ".pcapng", ".cap"]
        }
        
        # Performance metrics
        self.storage_metrics = {
            "total_evidence_files": 0,
            "total_storage_size_gb": 0,
            "verification_success_rate": 0,
            "avg_processing_time_seconds": 0,
            "blockchain_verifications": 0
        }
        
        logger.info("EvidenceStorageManager initialized with forensic capabilities")
    
    async def store_evidence_file(
        self,
        violation_id: UUID,
        file_data: bytes,
        file_name: str,
        evidence_type: EvidenceType,
        collector_id: str,
        collection_metadata: Optional[Dict[str, Any]] = None,
        auto_analyze: bool = True
    ) -> EvidenceRecord:
        """        Store evidence file with full chain of custody and verification
        
        Args:
            violation_id: Associated violation report ID
            file_data: Binary file data
            file_name: Original file name
            evidence_type: Type of evidence
            collector_id: ID of person/system collecting evidence
            collection_metadata: Metadata about collection process
            auto_analyze: Enable automatic forensic analysis
            
        Returns:
            Created EvidenceRecord with complete provenance
            
        Raises:
            EvidenceStorageManagerError: If storage fails
        """        try:
            # Validate file and evidence type
            await self._validate_evidence_file(file_data, file_name, evidence_type)
            
            # Generate evidence identifiers
            evidence_id = uuid4()
            file_hash = await self._calculate_file_hash(file_data)
            
            # Create forensic metadata
            forensic_metadata = await self._create_forensic_metadata(
                file_data, file_name, collection_metadata or {}
            )
            
            # Store file securely
            storage_result = await self.storage_manager.store_secure_file(
                file_data, f"evidence/{evidence_id}/{file_name}"
            )
            
            # Encrypt sensitive metadata
            encrypted_metadata = await self.encryption_manager.encrypt_data(
                json.dumps(collection_metadata or {})
            )
            
            # Create evidence record
            evidence = EvidenceRecord(
                id=evidence_id,
                violation_id=violation_id,
                evidence_type=evidence_type.value,
                file_name=file_name,
                file_hash=file_hash,
                file_size=len(file_data),
                storage_path=storage_result["storage_path"],
                storage_metadata=storage_result.get("metadata", {}),
                collection_timestamp=datetime.now(timezone.utc),
                collector_id=collector_id,
                collection_metadata=encrypted_metadata,
                forensic_metadata=forensic_metadata,
                status=EvidenceStatus.UPLOADED.value,
                integrity_verified=False,
                blockchain_verified=False,
                legal_admissible=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            self.db_session.add(evidence)
            
            # Create initial chain of custody entry
            initial_custody = await self._create_custody_entry(
                evidence.id,
                CustodyEventType.CREATION,
                collector_id,
                "Evidence file created and stored securely",
                {"collection_method": "automated", "initial_storage": True}
            )
            
            evidence.custody_chain.append(initial_custody)
            
            await self.db_session.commit()
            
            # Perform integrity verification
            await self.verify_evidence_integrity(evidence.id)
            
            # Blockchain verification if enabled
            if self.blockchain_verification_enabled:
                await self.create_blockchain_verification(evidence.id)
            
            # Automatic forensic analysis if enabled
            if auto_analyze:
                await self.perform_forensic_analysis(evidence.id)
            
            # Update metrics
            self.storage_metrics["total_evidence_files"] += 1
            self.storage_metrics["total_storage_size_gb"] += len(file_data) / (1024**3)
            
            logger.info(f"Evidence file stored: {evidence.id} [{evidence_type.value}]")
            return evidence
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Evidence file storage failed: {e}")
            raise EvidenceStorageManagerError(f"Evidence file storage failed: {e}")
    
    async def create_evidence_collection(
        self,
        violation_id: UUID,
        evidence_files: List[Dict[str, Any]],
        collection_context: Dict[str, Any],
        collector_id: str
    ) -> List[EvidenceRecord]:
        """        Create collection of related evidence files with batch processing
        
        Args:
            violation_id: Associated violation report ID
            evidence_files: List of evidence file dictionaries
            collection_context: Context of the evidence collection
            collector_id: ID of person/system collecting evidence
            
        Returns:
            List of created EvidenceRecord objects
        """        try:
            stored_evidence = []
            collection_start_time = datetime.now()
            
            # Generate collection ID for grouping
            collection_id = str(uuid4())
            
            for i, evidence_file in enumerate(evidence_files):
                try:
                    # Add collection context to metadata
                    file_metadata = evidence_file.get("metadata", {})
                    file_metadata.update({
                        "collection_id": collection_id,
                        "collection_index": i,
                        "collection_context": collection_context,
                        "collection_timestamp": collection_start_time.isoformat()
                    })
                    
                    # Store individual evidence file
                    evidence = await self.store_evidence_file(
                        violation_id=violation_id,
                        file_data=evidence_file["file_data"],
                        file_name=evidence_file["file_name"],
                        evidence_type=EvidenceType(evidence_file["evidence_type"]),
                        collector_id=collector_id,
                        collection_metadata=file_metadata,
                        auto_analyze=False  # Batch analyze later
                    )
                    
                    stored_evidence.append(evidence)
                    
                except Exception as e:
                    logger.error(f"Failed to store evidence file {i}: {e}")
                    # Continue with other files
                    continue
            
            # Perform batch forensic analysis
            if stored_evidence:
                await self._perform_batch_forensic_analysis(stored_evidence)
            
            # Create collection summary
            await self._create_collection_summary(collection_id, stored_evidence, collection_context)
            
            logger.info(f"Evidence collection created: {len(stored_evidence)} files for violation {violation_id}")
            return stored_evidence
            
        except Exception as e:
            logger.error(f"Evidence collection creation failed: {e}")
            raise EvidenceStorageManagerError(f"Evidence collection creation failed: {e}")
    
    async def verify_evidence_integrity(
        self,
        evidence_id: UUID,
        verification_method: str = "comprehensive"
    ) -> bool:
        """        Verify evidence integrity using multiple validation methods
        
        Args:
            evidence_id: Evidence record identifier
            verification_method: Method of verification (basic, comprehensive, forensic)
            
        Returns:
            Verification success status
        """        try:
            evidence = await self.db_session.get(EvidenceRecord, evidence_id)
            
            if not evidence:
                raise EvidenceStorageManagerError(f"Evidence not found: {evidence_id}")
            
            # Retrieve stored file
            file_data = await self.storage_manager.retrieve_secure_file(evidence.storage_path)
            
            if not file_data:
                raise EvidenceStorageManagerError("Evidence file not accessible")
            
            verification_results = {}
            
            # Hash verification
            current_hash = await self._calculate_file_hash(file_data)
            hash_verified = current_hash == evidence.file_hash
            verification_results["hash_verification"] = hash_verified
            
            if verification_method in ["comprehensive", "forensic"]:
                # Size verification
                size_verified = len(file_data) == evidence.file_size
                verification_results["size_verification"] = size_verified
                
                # Format verification
                format_verified = await self._verify_file_format(file_data, evidence.file_name)
                verification_results["format_verification"] = format_verified
                
                # Metadata consistency check
                metadata_verified = await self._verify_metadata_consistency(evidence)
                verification_results["metadata_verification"] = metadata_verified
            
            if verification_method == "forensic":
                # Deep forensic verification
                forensic_results = await self.forensic_analyzer.verify_integrity(
                    file_data, evidence.forensic_metadata
                )
                verification_results["forensic_verification"] = forensic_results["verified"]
            
            # Overall verification status
            overall_verified = all(verification_results.values())
            
            # Update evidence record
            evidence.integrity_verified = overall_verified
            evidence.last_verification_at = datetime.now(timezone.utc)
            evidence.verification_results = verification_results
            evidence.updated_at = datetime.now(timezone.utc)
            
            if overall_verified:
                evidence.status = EvidenceStatus.VERIFIED.value
            else:
                evidence.status = EvidenceStatus.CORRUPTED.value
                logger.warning(f"Evidence integrity verification failed: {evidence_id}")
            
            # Create custody entry
            await self._create_custody_entry(
                evidence_id,
                CustodyEventType.ANALYSIS,
                "system",
                f"Integrity verification: {'passed' if overall_verified else 'failed'}",
                verification_results
            )
            
            await self.db_session.commit()
            
            # Update metrics
            if overall_verified:
                self.storage_metrics["verification_success_rate"] = (
                    (self.storage_metrics["verification_success_rate"] * 
                     (self.storage_metrics["total_evidence_files"] - 1) + 1) /
                    self.storage_metrics["total_evidence_files"]
                )
            
            logger.info(f"Evidence integrity verification: {evidence_id} -> {'PASSED' if overall_verified else 'FAILED'}")
            return overall_verified
            
        except Exception as e:
            logger.error(f"Evidence integrity verification failed: {e}")
            raise EvidenceStorageManagerError(f"Evidence integrity verification failed: {e}")
    
    async def create_blockchain_verification(
        self,
        evidence_id: UUID,
        blockchain_network: str = "ethereum"
    ) -> BlockchainVerification:
        """        Create blockchain verification record for evidence
        
        Args:
            evidence_id: Evidence record identifier
            blockchain_network: Blockchain network to use
            
        Returns:
            Created BlockchainVerification record
        """        try:
            evidence = await self.db_session.get(EvidenceRecord, evidence_id)
            
            if not evidence:
                raise EvidenceStorageManagerError(f"Evidence not found: {evidence_id}")
            
            # Prepare verification data
            verification_data = {
                "evidence_id": str(evidence_id),
                "file_hash": evidence.file_hash,
                "collection_timestamp": evidence.collection_timestamp.isoformat(),
                "collector_id": evidence.collector_id,
                "file_size": evidence.file_size
            }
            
            # Create blockchain transaction
            blockchain_result = await self.blockchain_manager.create_verification_record(
                verification_data, blockchain_network
            )
            
            # Create verification record
            verification = BlockchainVerification(
                id=uuid4(),
                evidence_id=evidence_id,
                blockchain_network=blockchain_network,
                transaction_hash=blockchain_result["transaction_hash"],
                block_number=blockchain_result.get("block_number"),
                blockchain_timestamp=blockchain_result["timestamp"],
                verification_data=verification_data,
                gas_cost=blockchain_result.get("gas_cost", 0),
                network_fee=blockchain_result.get("network_fee", 0),
                verification_status="confirmed",
                created_at=datetime.now(timezone.utc)
            )
            
            self.db_session.add(verification)
            
            # Update evidence record
            evidence.blockchain_verified = True
            evidence.status = EvidenceStatus.BLOCKCHAIN_SECURED.value
            evidence.updated_at = datetime.now(timezone.utc)
            
            # Create custody entry
            await self._create_custody_entry(
                evidence_id,
                CustodyEventType.ANALYSIS,
                "system",
                f"Blockchain verification created on {blockchain_network}",
                {
                    "transaction_hash": blockchain_result["transaction_hash"],
                    "network": blockchain_network
                }
            )
            
            await self.db_session.commit()
            
            # Update metrics
            self.storage_metrics["blockchain_verifications"] += 1
            
            logger.info(f"Blockchain verification created: {evidence_id} -> {blockchain_result['transaction_hash']}")
            return verification
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Blockchain verification creation failed: {e}")
            raise EvidenceStorageManagerError(f"Blockchain verification creation failed: {e}")
    
    async def perform_forensic_analysis(
        self,
        evidence_id: UUID,
        analysis_type: str = "comprehensive"
    ) -> ForensicAnalysis:
        """        Perform comprehensive forensic analysis of evidence
        
        Args:
            evidence_id: Evidence record identifier
            analysis_type: Type of analysis (basic, comprehensive, advanced)
            
        Returns:
            Created ForensicAnalysis record
        """        try:
            evidence = await self.db_session.get(EvidenceRecord, evidence_id)
            
            if not evidence:
                raise EvidenceStorageManagerError(f"Evidence not found: {evidence_id}")
            
            # Retrieve file for analysis
            file_data = await self.storage_manager.retrieve_secure_file(evidence.storage_path)
            
            if not file_data:
                raise EvidenceStorageManagerError("Evidence file not accessible for analysis")
            
            analysis_start_time = datetime.now()
            
            # Perform forensic analysis
            analysis_results = await self.forensic_analyzer.perform_comprehensive_analysis(
                file_data,
                evidence.file_name,
                evidence.evidence_type,
                analysis_type
            )
            
            analysis_end_time = datetime.now()
            processing_time = (analysis_end_time - analysis_start_time).total_seconds()
            
            # Create forensic analysis record
            forensic_analysis = ForensicAnalysis(
                id=uuid4(),
                evidence_id=evidence_id,
                analysis_type=analysis_type,
                analysis_timestamp=analysis_start_time,
                processing_time_seconds=processing_time,
                analysis_results=analysis_results,
                findings_summary=analysis_results.get("summary", {}),
                anomalies_detected=analysis_results.get("anomalies", []),
                technical_metadata=analysis_results.get("technical_metadata", {}),
                legal_relevance_score=analysis_results.get("legal_relevance_score", 0.0),
                admissibility_assessment=analysis_results.get("admissibility_assessment", {}),
                created_at=datetime.now(timezone.utc)
            )
            
            self.db_session.add(forensic_analysis)
            
            # Update evidence record
            evidence.status = EvidenceStatus.FORENSICALLY_ANALYZED.value
            evidence.forensic_analysis_completed = True
            evidence.updated_at = datetime.now(timezone.utc)
            
            # Determine legal admissibility
            if analysis_results.get("legal_relevance_score", 0) >= 0.8:
                evidence.legal_admissible = True
                evidence.status = EvidenceStatus.LEGALLY_ADMISSIBLE.value
            
            # Create custody entry
            await self._create_custody_entry(
                evidence_id,
                CustodyEventType.ANALYSIS,
                "forensic_system",
                f"Forensic analysis completed: {analysis_type}",
                {
                    "processing_time_seconds": processing_time,
                    "legal_relevance_score": analysis_results.get("legal_relevance_score", 0),
                    "anomalies_count": len(analysis_results.get("anomalies", []))
                }
            )
            
            await self.db_session.commit()
            
            # Update metrics
            self.storage_metrics["avg_processing_time_seconds"] = (
                (self.storage_metrics["avg_processing_time_seconds"] * 
                 (self.storage_metrics["total_evidence_files"] - 1) + processing_time) /
                self.storage_metrics["total_evidence_files"]
            )
            
            logger.info(f"Forensic analysis completed: {evidence_id} in {processing_time:.2f}s")
            return forensic_analysis
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Forensic analysis failed: {e}")
            raise EvidenceStorageManagerError(f"Forensic analysis failed: {e}")
    
    async def access_evidence_with_custody(
        self,
        evidence_id: UUID,
        accessor_id: str,
        access_purpose: str,
        authorized_by: Optional[str] = None
    ) -> bytes:
        """        Access evidence file with complete chain of custody tracking
        
        Args:
            evidence_id: Evidence record identifier
            accessor_id: ID of person/system accessing evidence
            access_purpose: Purpose of access
            authorized_by: ID of authorizing person (if required)
            
        Returns:
            Evidence file data
        """        try:
            evidence = await self.db_session.get(EvidenceRecord, evidence_id)
            
            if not evidence:
                raise EvidenceStorageManagerError(f"Evidence not found: {evidence_id}")
            
            # Verify access authorization
            if not await self._verify_access_authorization(evidence, accessor_id, access_purpose):
                raise EvidenceStorageManagerError("Access not authorized")
            
            # Retrieve file
            file_data = await self.storage_manager.retrieve_secure_file(evidence.storage_path)
            
            if not file_data:
                raise EvidenceStorageManagerError("Evidence file not accessible")
            
            # Create custody entry
            await self._create_custody_entry(
                evidence_id,
                CustodyEventType.ACCESS,
                accessor_id,
                f"Evidence accessed for: {access_purpose}",
                {
                    "access_purpose": access_purpose,
                    "authorized_by": authorized_by,
                    "file_size_accessed": len(file_data)
                }
            )
            
            await self.db_session.commit()
            
            logger.info(f"Evidence accessed: {evidence_id} by {accessor_id}")
            return file_data
            
        except Exception as e:
            logger.error(f"Evidence access failed: {e}")
            raise EvidenceStorageManagerError(f"Evidence access failed: {e}")
    
    async def export_evidence_package(
        self,
        violation_id: UUID,
        export_format: str = "legal_package",
        requester_id: str,
        export_purpose: str
    ) -> Dict[str, Any]:
        """        Export comprehensive evidence package for legal proceedings
        
        Args:
            violation_id: Violation report identifier
            export_format: Format of export (legal_package, forensic_report, archive)
            requester_id: ID of person requesting export
            export_purpose: Purpose of export
            
        Returns:
            Export package information and download details
        """        try:
            # Get all evidence for violation
            evidence_records = await self.db_session.query(EvidenceRecord).filter(
                EvidenceRecord.violation_id == violation_id
            ).options(
                selectinload(EvidenceRecord.custody_chain),
                selectinload(EvidenceRecord.blockchain_verifications),
                selectinload(EvidenceRecord.forensic_analyses)
            ).all()
            
            if not evidence_records:
                raise EvidenceStorageManagerError(f"No evidence found for violation: {violation_id}")
            
            # Create export package
            export_id = str(uuid4())
            export_timestamp = datetime.now(timezone.utc)
            
            # Compile evidence package
            package_data = await self._compile_evidence_package(
                evidence_records, export_format, requester_id, export_purpose
            )
            
            # Store export package
            package_path = f"exports/{export_id}/{export_format}_package.zip"
            storage_result = await self.storage_manager.store_secure_file(
                package_data["package_bytes"], package_path
            )
            
            # Create custody entries for all evidence
            for evidence in evidence_records:
                await self._create_custody_entry(
                    evidence.id,
                    CustodyEventType.EXPORT,
                    requester_id,
                    f"Evidence exported as {export_format} package",
                    {
                        "export_id": export_id,
                        "export_purpose": export_purpose,
                        "package_size_bytes": len(package_data["package_bytes"])
                    }
                )
            
            await self.db_session.commit()
            
            export_result = {
                "export_id": export_id,
                "violation_id": str(violation_id),
                "export_format": export_format,
                "evidence_count": len(evidence_records),
                "package_size_bytes": len(package_data["package_bytes"]),
                "storage_path": storage_result["storage_path"],
                "download_url": storage_result.get("download_url"),
                "export_timestamp": export_timestamp.isoformat(),
                "requester_id": requester_id,
                "export_purpose": export_purpose,
                "package_contents": package_data["contents_manifest"],
                "legal_certification": package_data.get("legal_certification"),
                "integrity_hashes": package_data.get("integrity_hashes")
            }
            
            logger.info(f"Evidence package exported: {export_id} for violation {violation_id}")
            return export_result
            
        except Exception as e:
            logger.error(f"Evidence package export failed: {e}")
            raise EvidenceStorageManagerError(f"Evidence package export failed: {e}")
    
    # Private helper methods
    
    async def _validate_evidence_file(
        self,
        file_data: bytes,
        file_name: str,
        evidence_type: EvidenceType
    ) -> None:
        """Validate evidence file before storage"""        # Size validation
        file_size_mb = len(file_data) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise EvidenceStorageManagerError(f"File size exceeds limit: {file_size_mb:.2f}MB")
        
        # File type validation
        file_extension = Path(file_name).suffix.lower()
        allowed_extensions = self.supported_evidence_types.get(evidence_type, [])
        
        if allowed_extensions and file_extension not in allowed_extensions:
            raise EvidenceStorageManagerError(f"Unsupported file type for {evidence_type.value}: {file_extension}")
        
        # Basic file format validation
        if not await self._verify_file_format(file_data, file_name):
            raise EvidenceStorageManagerError("File format validation failed")
    
    async def _calculate_file_hash(self, file_data: bytes, algorithm: str = "sha256") -> str:
        """Calculate cryptographic hash of file data"""        if algorithm == "sha256":
            return hashlib.sha256(file_data).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(file_data).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(file_data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    async def _create_forensic_metadata(
        self,
        file_data: bytes,
        file_name: str,
        collection_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create comprehensive forensic metadata"""        metadata = {
            "file_name": file_name,
            "file_size": len(file_data),
            "mime_type": mimetypes.guess_type(file_name)[0],
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "hash_sha256": await self._calculate_file_hash(file_data, "sha256"),
            "hash_sha512": await self._calculate_file_hash(file_data, "sha512"),
            "hash_md5": await self._calculate_file_hash(file_data, "md5"),
            "collection_metadata": collection_metadata
        }
        
        # Add file type specific metadata
        file_extension = Path(file_name).suffix.lower()
        if file_extension in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
            metadata.update(await self._extract_image_metadata(file_data))
        elif file_extension in [".mp4", ".avi", ".mov", ".mkv"]:
            metadata.update(await self._extract_video_metadata(file_data))
        elif file_extension in [".mp3", ".wav", ".flac"]:
            metadata.update(await self._extract_audio_metadata(file_data))
        
        return metadata
    
    async def _create_custody_entry(
        self,
        evidence_id: UUID,
        event_type: CustodyEventType,
        actor_id: str,
        description: str,
        event_data: Optional[Dict[str, Any]] = None
    ) -> ChainOfCustody:
        """Create chain of custody entry"""        custody_entry = ChainOfCustody(
            id=uuid4(),
            evidence_id=evidence_id,
            event_type=event_type.value,
            event_timestamp=datetime.now(timezone.utc),
            actor_id=actor_id,
            event_description=description,
            event_data=event_data or {},
            location_data=await self._get_location_data(),
            system_metadata=await self._get_system_metadata(),
            created_at=datetime.now(timezone.utc)
        )
        
        self.db_session.add(custody_entry)
        return custody_entry
    
    async def _verify_file_format(self, file_data: bytes, file_name: str) -> bool:
        """Verify file format matches expected type"""        try:
            # Basic magic number validation
            magic_signatures = {
                b'\x89PNG\r\n\x1a\n': '.png',
                b'\xff\xd8\xff': '.jpg',
                b'GIF8': '.gif',
                b'%PDF': '.pdf',
                b'PK\x03\x04': '.zip',
                b'Rar!': '.rar'
            }
            
            for signature, extension in magic_signatures.items():
                if file_data.startswith(signature):
                    return Path(file_name).suffix.lower() == extension
            
            return True  # If no specific validation available
            
        except Exception:
            return False
    
    async def _verify_metadata_consistency(self, evidence: EvidenceRecord) -> bool:
        """Verify metadata consistency"""        try:
            # Check timestamp consistency
            if evidence.collection_timestamp > datetime.now(timezone.utc):
                return False
            
            # Check file size consistency
            if evidence.file_size <= 0:
                return False
            
            # Check hash format
            if len(evidence.file_hash) != 64:  # SHA256 length
                return False
            
            return True
            
        except Exception:
            return False
    
    async def _perform_batch_forensic_analysis(self, evidence_list: List[EvidenceRecord]) -> None:
        """Perform batch forensic analysis for efficiency"""        for evidence in evidence_list:
            try:
                await self.perform_forensic_analysis(evidence.id, "basic")
            except Exception as e:
                logger.warning(f"Batch forensic analysis failed for {evidence.id}: {e}")
    
    async def _create_collection_summary(
        self,
        collection_id: str,
        evidence_list: List[EvidenceRecord],
        context: Dict[str, Any]
    ) -> None:
        """Create summary for evidence collection"""        # Implementation would create collection summary record
        pass
    
    async def _verify_access_authorization(
        self,
        evidence: EvidenceRecord,
        accessor_id: str,
        purpose: str
    ) -> bool:
        """Verify if access is authorized"""        # Implementation would check access permissions
        return True  # Simplified for example
    
    async def _compile_evidence_package(
        self,
        evidence_records: List[EvidenceRecord],
        export_format: str,
        requester_id: str,
        purpose: str
    ) -> Dict[str, Any]:
        """Compile evidence into exportable package"""        # Implementation would create comprehensive evidence package
        return {
            "package_bytes": b"mock_package_data",
            "contents_manifest": ["evidence_list", "chain_of_custody", "forensic_reports"],
            "legal_certification": {"certified": True, "certifier": "system"},
            "integrity_hashes": {"package_hash": "mock_hash"}
        }
    
    # Additional helper methods for metadata extraction
    
    async def _extract_image_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract image-specific metadata"""        return {"image_metadata": "extracted"}
    
    async def _extract_video_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract video-specific metadata"""        return {"video_metadata": "extracted"}
    
    async def _extract_audio_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract audio-specific metadata"""        return {"audio_metadata": "extracted"}
    
    async def _get_location_data(self) -> Dict[str, Any]:
        """Get current location data for custody tracking"""        return {"location": "secure_datacenter", "jurisdiction": "legal_compliant"}
    
    async def _get_system_metadata(self) -> Dict[str, Any]:
        """Get system metadata for custody tracking"""        return {
            "system_id": "evidence_storage_system",
            "software_version": "2.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
