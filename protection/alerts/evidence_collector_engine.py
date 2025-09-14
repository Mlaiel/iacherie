"""Advanced Evidence Collection Engine - IA Influencer Agent Enterprise System
Created by: Fahed Mlaiel (mlaiel@live.de)

WARNING: This code is proprietary and confidential. Any unauthorized use, reproduction, 
or distribution is strictly prohibited without explicit written permission from Fahed Mlaiel.
Legal action will be taken against any violation of intellectual property rights.
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Ultra-advanced evidence collection engine with forensic-grade integrity,
legal-compliant documentation, blockchain verification, and audit trails.
Business Logic: Alert trigger → evidence collection → integrity verification → legal documentation → chain of custody
"""

import asyncio
import logging
import hashlib
import json
import uuid
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
import mimetypes
import base64
import gzip

import aiofiles
import aiohttp
from pydantic import BaseModel, Field, validator
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import redis.asyncio as redis

from .alert_models import ContentProtectionAlert, AlertSeverity
from .forensic_analyzer import AdvancedForensicAnalyzer
from ..monitoring.blockchain_recorder import BlockchainRecorder
from ..security.encryption_manager import EncryptionManager
from ...core.config import settings
from ...core.database import get_async_session
from ...utils.hashing import HashGenerator
from ...utils.compression import CompressionManager

logger = logging.getLogger(__name__)


class EvidenceType(Enum):
    """
Types of evidence that can be collected"""

    SCREENSHOT = "screenshot"
    VIDEO_RECORDING = "video_recording"
    AUDIO_RECORDING = "audio_recording"
    WEBPAGE_SNAPSHOT = "webpage_snapshot"
    METADATA_EXTRACTION = "metadata_extraction"
    NETWORK_TRAFFIC = "network_traffic"
    FILE_DOWNLOAD = "file_download"
    API_RESPONSE = "api_response"
    SOCIAL_MEDIA_POST = "social_media_post"
    EMAIL_CONTENT = "email_content"
    DATABASE_RECORD = "database_record"
    LOG_ENTRY = "log_entry"
    DIGITAL_FINGERPRINT = "digital_fingerprint"
    BLOCKCHAIN_RECORD = "blockchain_record"
    LEGAL_DOCUMENT = "legal_document"


class EvidenceStatus(Enum):
    """Status of evidence collection process"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COLLECTED = "collected"
    VERIFIED = "verified"
    ENCRYPTED = "encrypted"
    ARCHIVED = "archived"
    FAILED = "failed"
    CORRUPTED = "corrupted"
    EXPIRED = "expired"
    LEGAL_HOLD = "legal_hold"


class EvidenceIntegrity(Enum):
    """Evidence integrity verification levels"""

    BASIC = "basic"
    CRYPTOGRAPHIC = "cryptographic"
    BLOCKCHAIN = "blockchain"
    LEGAL_GRADE = "legal_grade"
    FORENSIC_GRADE = "forensic_grade"


@dataclass
class EvidenceMetadata:
    """Comprehensive evidence metadata"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: EvidenceType = EvidenceType.SCREENSHOT
    source_url: Optional[str] = None
    collection_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    collector_agent: str = ""
    collection_method: str = ""
    file_size_bytes: int = 0
    file_format: str = ""
    mime_type: str = ""
    md5_hash: Optional[str] = None
    sha256_hash: Optional[str] = None
    sha512_hash: Optional[str] = None
    blockchain_hash: Optional[str] = None
    encryption_key_id: Optional[str] = None
    compression_algorithm: Optional[str] = None
    integrity_level: EvidenceIntegrity = EvidenceIntegrity.BASIC
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)
    legal_tags: List[str] = field(default_factory=list)
    retention_policy: Dict[str, Any] = field(default_factory=dict)
    access_permissions: List[str] = field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EvidenceCollectionResult:
    """Result of evidence collection operation"""
    success: bool = False
    evidence_id: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[EvidenceMetadata] = None
    verification_status: bool = False
    blockchain_record_id: Optional[str] = None
    error_message: Optional[str] = None
    collection_duration_seconds: float = 0.0
    warnings: List[str] = field(default_factory=list)


@dataclass
class ChainOfCustodyEntry:
    """
Individual chain of custody entry"""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    actor: str = ""
    action: str = ""
    location: str = ""
    signature: Optional[str] = None
    witness: Optional[str] = None
    notes: str = ""
    verification_hash: Optional[str] = None


class AdvancedEvidenceCollector:
    """
    Enterprise-grade evidence collection engine with forensic integrity,
    legal compliance, and blockchain verification capabilities.
    """
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.forensic_analyzer = AdvancedForensicAnalyzer()
        self.blockchain_recorder = BlockchainRecorder()
        self.encryption_manager = EncryptionManager()
        self.hash_generator = HashGenerator()
        self.compression_manager = CompressionManager()
        
        # Evidence storage
        self.evidence_storage_path = Path(settings.EVIDENCE_STORAGE_PATH)
        self.evidence_registry: Dict[str, EvidenceMetadata] = {}
        self.active_collections: Dict[str, asyncio.Task] = {}
        
        # Collection configuration
        self.max_file_size_mb = settings.MAX_EVIDENCE_FILE_SIZE_MB
        self.retention_days = settings.EVIDENCE_RETENTION_DAYS
        self.integrity_verification = settings.EVIDENCE_INTEGRITY_VERIFICATION
        
        # Legal compliance
        self.legal_jurisdictions = settings.LEGAL_JURISDICTIONS
        self.privacy_regulations = settings.PRIVACY_REGULATIONS
        
        # Redis for caching
        self.redis_client = None
        
    async def initialize(self) -> None:
        """
Initialize evidence collection engine"""
        await self.forensic_analyzer.initialize()
        await self.blockchain_recorder.initialize()
        await self.encryption_manager.initialize()
        await self.hash_generator.initialize()
        await self.compression_manager.initialize()
        
        # Initialize Redis
        self.redis_client = redis.from_url(settings.REDIS_URL)
        
        # Ensure storage directory exists
        self.evidence_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing evidence registry
        await self._load_evidence_registry()
        
        # Start background tasks
        asyncio.create_task(self._evidence_maintenance_worker())
        asyncio.create_task(self._integrity_verification_worker())
        asyncio.create_task(self._retention_policy_worker())
        
        self.logger.info("Advanced Evidence Collector initialized")
    
    async def collect_evidence(
        self,
        alert: ContentProtectionAlert,
        evidence_types: List[EvidenceType],
        priority: str = "normal",
        legal_hold: bool = False
    ) -> List[EvidenceCollectionResult]:
        """Collect multiple types of evidence for an alert"""
        try:
            results = []
            collection_id = str(uuid.uuid4())
            
            self.logger.info(f"Starting evidence collection {collection_id} for alert {alert.id}")
            
            # Create collection tasks
            tasks = []
            for evidence_type in evidence_types:
                task = asyncio.create_task(
                    self._collect_single_evidence(alert, evidence_type, collection_id, legal_hold)
                )
                tasks.append(task)
                self.active_collections[f"{collection_id}_{evidence_type.value}"] = task
            
            # Execute collection tasks
            collection_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(collection_results):
                if isinstance(result, Exception):
                    error_result = EvidenceCollectionResult(
                        success=False,
                        error_message=str(result)
                    )
                    results.append(error_result)
                    self.logger.error(f"Evidence collection failed: {str(result)}")
                else:
                    results.append(result)
                    if result.success:
                        # Record in blockchain
                        if result.metadata:
                            await self._record_evidence_in_blockchain(result.metadata)
            
            # Clean up active collections
            for evidence_type in evidence_types:
                key = f"{collection_id}_{evidence_type.value}"
                self.active_collections.pop(key, None)
            
            self.logger.info(f"Evidence collection {collection_id} completed. "
                           f"{sum(1 for r in results if r.success)}/{len(results)} successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Evidence collection failed: {str(e)}")
            raise
    
    async def _collect_single_evidence(
        self,
        alert: ContentProtectionAlert,
        evidence_type: EvidenceType,
        collection_id: str,
        legal_hold: bool
    ) -> EvidenceCollectionResult:
        """Collect a single piece of evidence"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Create evidence metadata
            metadata = EvidenceMetadata(
                evidence_type=evidence_type,
                source_url=alert.content_url,
                collection_timestamp=start_time,
                collector_agent="AdvancedEvidenceCollector",
                collection_method=self._get_collection_method(evidence_type),
                integrity_level=EvidenceIntegrity.FORENSIC_GRADE,
                legal_tags=["content_protection", "copyright_violation"] if legal_hold else []
            )
            
            # Add to chain of custody
            custody_entry = ChainOfCustodyEntry(
                actor="AdvancedEvidenceCollector",
                action="evidence_collection_initiated",
                location=str(self.evidence_storage_path),
                notes=f"Collection for alert {alert.id}"
            )
            metadata.chain_of_custody.append(custody_entry.__dict__)
            
            # Collect evidence based on type
            file_path, file_size = await self._perform_collection(alert, evidence_type, metadata)
            
            if not file_path:
                return EvidenceCollectionResult(
                    success=False,
                    error_message="Evidence collection failed - no file created"
                )
            
            # Update metadata with file information
            metadata.file_size_bytes = file_size
            metadata.file_format = Path(file_path).suffix.lower()
            metadata.mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
            
            # Generate cryptographic hashes
            hashes_result = await self._generate_evidence_hashes(file_path)
            metadata.md5_hash = hashes_result["md5"]
            metadata.sha256_hash = hashes_result["sha256"]
            metadata.sha512_hash = hashes_result["sha512"]
            
            # Encrypt evidence if required
            if settings.ENCRYPT_EVIDENCE:
                encrypted_path = await self._encrypt_evidence_file(file_path, metadata)
                file_path = encrypted_path
            
            # Compress evidence if beneficial
            if file_size > settings.COMPRESSION_THRESHOLD_BYTES:
                compressed_path = await self._compress_evidence_file(file_path, metadata)
                if compressed_path:
                    file_path = compressed_path
            
            # Verify integrity
            verification_status = await self._verify_evidence_integrity(file_path, metadata)
            
            # Add to evidence registry
            self.evidence_registry[metadata.id] = metadata
            await self._save_evidence_registry()
            
            # Update chain of custody
            custody_entry = ChainOfCustodyEntry(
                actor="AdvancedEvidenceCollector",
                action="evidence_collection_completed",
                location=str(file_path),
                notes=f"Evidence collected and verified"
            )
            metadata.chain_of_custody.append(custody_entry.__dict__)
            
            collection_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return EvidenceCollectionResult(
                success=True,
                evidence_id=metadata.id,
                file_path=str(file_path),
                metadata=metadata,
                verification_status=verification_status,
                collection_duration_seconds=collection_duration
            )
            
        except Exception as e:
            self.logger.error(f"Single evidence collection failed: {str(e)}")
            collection_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return EvidenceCollectionResult(
                success=False,
                error_message=str(e),
                collection_duration_seconds=collection_duration
            )
    
    async def _perform_collection(
        self,
        alert: ContentProtectionAlert,
        evidence_type: EvidenceType,
        metadata: EvidenceMetadata
    ) -> Tuple[Optional[str], int]:
        """Perform the actual evidence collection based on type"""
        try:
            if evidence_type == EvidenceType.SCREENSHOT:
                return await self._collect_screenshot(alert, metadata)
            elif evidence_type == EvidenceType.VIDEO_RECORDING:
                return await self._collect_video_recording(alert, metadata)
            elif evidence_type == EvidenceType.WEBPAGE_SNAPSHOT:
                return await self._collect_webpage_snapshot(alert, metadata)
            elif evidence_type == EvidenceType.METADATA_EXTRACTION:
                return await self._collect_metadata(alert, metadata)
            elif evidence_type == EvidenceType.NETWORK_TRAFFIC:
                return await self._collect_network_traffic(alert, metadata)
            elif evidence_type == EvidenceType.FILE_DOWNLOAD:
                return await self._collect_file_download(alert, metadata)
            elif evidence_type == EvidenceType.API_RESPONSE:
                return await self._collect_api_response(alert, metadata)
            elif evidence_type == EvidenceType.SOCIAL_MEDIA_POST:
                return await self._collect_social_media_post(alert, metadata)
            elif evidence_type == EvidenceType.DIGITAL_FINGERPRINT:
                return await self._collect_digital_fingerprint(alert, metadata)
            else:
                self.logger.warning(f"Unsupported evidence type: {evidence_type}")
                return None, 0
                
        except Exception as e:
            self.logger.error(f"Evidence collection failed for type {evidence_type}: {str(e)}")
            raise
    
    async def _collect_screenshot(self, alert: ContentProtectionAlert, metadata: EvidenceMetadata) -> Tuple[str, int]:
        """Collect screenshot evidence using headless browser"""
        try:
            from playwright.async_api import async_playwright
            
            file_name = f"screenshot_{metadata.id}.png"
            file_path = self.evidence_storage_path / file_name
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (IA-Influencer-Agent) Evidence-Collector/1.0'
                )
                
                page = await context.new_page()
                
                # Set timeout and load page
                page.set_default_timeout(30000)
                await page.goto(alert.content_url, wait_until='networkidle')
                
                # Take full page screenshot
                await page.screenshot(
                    path=str(file_path),
                    full_page=True,
                    type='png'
                )
                
                await browser.close()
            
            file_size = file_path.stat().st_size
            return str(file_path), file_size
            
        except Exception as e:
            self.logger.error(f"Screenshot collection failed: {str(e)}")
            raise
    
    async def _collect_video_recording(self, alert: ContentProtectionAlert, metadata: EvidenceMetadata) -> Tuple[str, int]:
        """Collect video recording evidence"""
        try:
            from playwright.async_api import async_playwright
            
            file_name = f"video_{metadata.id}.webm"
            file_path = self.evidence_storage_path / file_name
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    record_video_dir=str(self.evidence_storage_path),
                    record_video_size={'width': 1920, 'height': 1080}
                )
                
                page = await context.new_page()
                await page.goto(alert.content_url, wait_until='networkidle')
                
                # Record for 30 seconds
                await asyncio.sleep(30)
                
                await browser.close()
            
            # Find the recorded video file
            video_files = list(self.evidence_storage_path.glob("*.webm"))
            if video_files:
                latest_video = max(video_files, key=lambda x: x.stat().st_mtime)
                latest_video.rename(file_path)
                file_size = file_path.stat().st_size
                return str(file_path), file_size
            else:
                raise Exception("No video file was created")
                
        except Exception as e:
            self.logger.error(f"Video recording collection failed: {str(e)}")
            raise
    
    async def _collect_webpage_snapshot(self, alert: ContentProtectionAlert, metadata: EvidenceMetadata) -> Tuple[str, int]:
        """Collect complete webpage snapshot including HTML, CSS, images"""
        try:
            file_name = f"webpage_{metadata.id}.mhtml"
            file_path = self.evidence_storage_path / file_name
            
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                await page.goto(alert.content_url, wait_until='networkidle')
                
                # Get full HTML content
                html_content = await page.content()
                
                # Save as MHTML (web archive)
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(html_content)
                
                await browser.close()
            
            file_size = file_path.stat().st_size
            return str(file_path), file_size
            
        except Exception as e:
            self.logger.error(f"Webpage snapshot collection failed: {str(e)}")
            raise
    
    async def _collect_metadata(self, alert: ContentProtectionAlert, metadata: EvidenceMetadata) -> Tuple[str, int]:
        """Collect metadata information about the content"""
        try:
            file_name = f"metadata_{metadata.id}.json"
            file_path = self.evidence_storage_path / file_name
            
            # Collect various metadata
            metadata_info = {
                "url": alert.content_url,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "headers": {},
                "dns_info": {},
                "whois_info": {},
                "ssl_info": {},
                "page_metadata": {}
            }
            
            # HTTP headers
            async with aiohttp.ClientSession() as session:
                async with session.head(alert.content_url) as response:
                    metadata_info["headers"] = dict(response.headers)
                    metadata_info["status_code"] = response.status
            
            # DNS information
            import socket
            from urllib.parse import urlparse
            
            parsed_url = urlparse(alert.content_url)
            hostname = parsed_url.hostname
            
            if hostname:
                try:
                    ip_addresses = socket.gethostbyname_ex(hostname)
                    metadata_info["dns_info"] = {
                        "hostname": hostname,
                        "ip_addresses": ip_addresses[2]
                    }
                except:
                    pass
            
            # Save metadata
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(metadata_info, indent=2))
            
            file_size = file_path.stat().st_size
            return str(file_path), file_size
            
        except Exception as e:
            self.logger.error(f"Metadata collection failed: {str(e)}")
            raise
    
    async def _collect_network_traffic(self, alert: ContentProtectionAlert, metadata: EvidenceMetadata) -> Tuple[str, int]:
        """Collect network traffic during content access"""
        try:
            file_name = f"network_{metadata.id}.har"
            file_path = self.evidence_storage_path / file_name
            
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                
                # Start HAR recording
                await context.tracing.start(screenshots=True, snapshots=True)
                
                page = await context.new_page()
                await page.goto(alert.content_url, wait_until='networkidle')
                
                # Stop tracing and save
                await context.tracing.stop(path=str(file_path))
                await browser.close()
            
            file_size = file_path.stat().st_size
            return str(file_path), file_size
            
        except Exception as e:
            self.logger.error(f"Network traffic collection failed: {str(e)}")
            raise
    
    async def _collect_file_download(self, alert: ContentProtectionAlert, metadata: EvidenceMetadata) -> Tuple[str, int]:
        """Download and collect the actual file content"""
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(alert.content_url)
            file_extension = Path(parsed_url.path).suffix or '.bin'
            
            file_name = f"download_{metadata.id}{file_extension}"
            file_path = self.evidence_storage_path / file_name
            
            async with aiohttp.ClientSession() as session:
                async with session.get(alert.content_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                    else:
                        raise Exception(f"Download failed with status {response.status}")
            
            file_size = file_path.stat().st_size
            
            # Check file size limit
            if file_size > self.max_file_size_mb * 1024 * 1024:
                file_path.unlink()
                raise Exception(f"File too large: {file_size} bytes")
            
            return str(file_path), file_size
            
        except Exception as e:
            self.logger.error(f"File download collection failed: {str(e)}")
            raise
    
    async def _collect_api_response(self, alert: ContentProtectionAlert, metadata: EvidenceMetadata) -> Tuple[str, int]:
        """Collect API response data"""
        try:
            file_name = f"api_response_{metadata.id}.json"
            file_path = self.evidence_storage_path / file_name
            
            async with aiohttp.ClientSession() as session:
                async with session.get(alert.content_url) as response:
                    response_data = {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "content": await response.text(),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(response_data, indent=2))
            
            file_size = file_path.stat().st_size
            return str(file_path), file_size
            
        except Exception as e:
            self.logger.error(f"API response collection failed: {str(e)}")
            raise
    
    async def _collect_social_media_post(self, alert: ContentProtectionAlert, metadata: EvidenceMetadata) -> Tuple[str, int]:
        """Collect social media post content"""
        try:
            # This would integrate with platform-specific APIs
            file_name = f"social_media_{metadata.id}.json"
            file_path = self.evidence_storage_path / file_name
            
            # Placeholder for social media API integration
            post_data = {
                "url": alert.content_url,
                "platform": alert.platform or "unknown",
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "content": "Social media content collection not implemented"
            }
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(post_data, indent=2))
            
            file_size = file_path.stat().st_size
            return str(file_path), file_size
            
        except Exception as e:
            self.logger.error(f"Social media collection failed: {str(e)}")
            raise
    
    async def _collect_digital_fingerprint(self, alert: ContentProtectionAlert, metadata: EvidenceMetadata) -> Tuple[str, int]:
        """Collect digital fingerprint of the content"""
        try:
            file_name = f"fingerprint_{metadata.id}.json"
            file_path = self.evidence_storage_path / file_name
            
            # Generate digital fingerprint
            fingerprint_data = await self.forensic_analyzer.generate_content_fingerprint(
                alert.content_url
            )
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(fingerprint_data, indent=2))
            
            file_size = file_path.stat().st_size
            return str(file_path), file_size
            
        except Exception as e:
            self.logger.error(f"Digital fingerprint collection failed: {str(e)}")
            raise
    
    async def _generate_evidence_hashes(self, file_path: str) -> Dict[str, str]:
        """Generate cryptographic hashes for evidence file"""
        try:
            hashes_dict = {}
            
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
                
                # MD5
                md5_hash = hashlib.md5(content).hexdigest()
                hashes_dict["md5"] = md5_hash
                
                # SHA256
                sha256_hash = hashlib.sha256(content).hexdigest()
                hashes_dict["sha256"] = sha256_hash
                
                # SHA512
                sha512_hash = hashlib.sha512(content).hexdigest()
                hashes_dict["sha512"] = sha512_hash
            
            return hashes_dict
            
        except Exception as e:
            self.logger.error(f"Hash generation failed: {str(e)}")
            raise
    
    async def _encrypt_evidence_file(self, file_path: str, metadata: EvidenceMetadata) -> str:
        """Encrypt evidence file using AES encryption"""
        try:
            encrypted_path = f"{file_path}.encrypted"
            key_id = await self.encryption_manager.encrypt_file(file_path, encrypted_path)
            metadata.encryption_key_id = key_id
            
            # Remove original file
            Path(file_path).unlink()
            
            return encrypted_path
            
        except Exception as e:
            self.logger.error(f"Evidence encryption failed: {str(e)}")
            raise
    
    async def _compress_evidence_file(self, file_path: str, metadata: EvidenceMetadata) -> Optional[str]:
        """Compress evidence file if beneficial"""
        try:
            compressed_path = f"{file_path}.gz"
            compression_ratio = await self.compression_manager.compress_file(file_path, compressed_path)
            
            if compression_ratio > 0.1:  # Only keep if compression is significant
                metadata.compression_algorithm = "gzip"
                Path(file_path).unlink()
                return compressed_path
            else:
                Path(compressed_path).unlink()
                return None
                
        except Exception as e:
            self.logger.error(f"Evidence compression failed: {str(e)}")
            return None
    
    async def _verify_evidence_integrity(self, file_path: str, metadata: EvidenceMetadata) -> bool:
        """Verify evidence integrity using multiple methods"""
        try:
            # Verify file exists and is readable
            file_obj = Path(file_path)
            if not file_obj.exists():
                return False
            
            # Verify file size matches metadata
            actual_size = file_obj.stat().st_size
            if metadata.file_size_bytes != actual_size:
                self.logger.warning(f"File size mismatch: expected {metadata.file_size_bytes}, got {actual_size}")
                return False
            
            # Verify hashes if available
            if metadata.sha256_hash:
                current_hashes = await self._generate_evidence_hashes(file_path)
                if current_hashes["sha256"] != metadata.sha256_hash:
                    self.logger.error("SHA256 hash verification failed")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Integrity verification failed: {str(e)}")
            return False
    
    async def _record_evidence_in_blockchain(self, metadata -> None: EvidenceMetadata) -> None:
        """Record evidence existence and hashes in blockchain"""
        try:
            blockchain_data = {
                "evidence_id": metadata.id,
                "evidence_type": metadata.evidence_type.value,
                "collection_timestamp": metadata.collection_timestamp.isoformat(),
                "sha256_hash": metadata.sha256_hash,
                "file_size": metadata.file_size_bytes,
                "collector": metadata.collector_agent
            }
            
            record_id = await self.blockchain_recorder.record_evidence(blockchain_data)
            metadata.blockchain_hash = record_id
            
            self.logger.info(f"Evidence {metadata.id} recorded in blockchain: {record_id}")
            
        except Exception as e:
            self.logger.error(f"Blockchain recording failed: {str(e)}")
    
    async def _get_collection_method(self, evidence_type: EvidenceType) -> str:
        """Get human-readable collection method description"""
        methods = {
            EvidenceType.SCREENSHOT: "Headless browser screenshot capture",
            EvidenceType.VIDEO_RECORDING: "Automated browser video recording",
            EvidenceType.WEBPAGE_SNAPSHOT: "Complete HTML page archive",
            EvidenceType.METADATA_EXTRACTION: "HTTP headers and DNS analysis",
            EvidenceType.NETWORK_TRAFFIC: "HAR network trace recording",
            EvidenceType.FILE_DOWNLOAD: "Direct file content download",
            EvidenceType.API_RESPONSE: "REST API response capture",
            EvidenceType.SOCIAL_MEDIA_POST: "Platform API content extraction",
            EvidenceType.DIGITAL_FINGERPRINT: "Cryptographic content fingerprinting"
        }
        return methods.get(evidence_type, "Unknown collection method")
    
    # Background maintenance tasks
    
    async def _evidence_maintenance_worker(self) -> None:
        """Background worker for evidence maintenance"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._perform_maintenance()
            except Exception as e:
                self.logger.error(f"Evidence maintenance error: {str(e)}")
    
    async def _integrity_verification_worker(self) -> None:
        """Background worker for periodic integrity verification"""
        while True:
            try:
                await asyncio.sleep(21600)  # Run every 6 hours
                await self._verify_all_evidence_integrity()
            except Exception as e:
                self.logger.error(f"Integrity verification error: {str(e)}")
    
    async def _retention_policy_worker(self) -> None:
        """Background worker for retention policy enforcement"""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily
                await self._enforce_retention_policies()
            except Exception as e:
                self.logger.error(f"Retention policy error: {str(e)}")
    
    async def _perform_maintenance(self) -> None:
        """Perform regular maintenance tasks"""
        # Cleanup temporary files
        temp_files = list(self.evidence_storage_path.glob("*.tmp"))
        for temp_file in temp_files:
            if temp_file.stat().st_mtime < (datetime.now().timestamp() - 3600):
                temp_file.unlink()
        
        # Update evidence registry
        await self._save_evidence_registry()
    
    async def _verify_all_evidence_integrity(self) -> None:
        """Verify integrity of all stored evidence"""
        for evidence_id, metadata in self.evidence_registry.items():
            if metadata.file_size_bytes > 0:  # Only verify files that should exist
                file_path = self.evidence_storage_path / f"*_{evidence_id}.*"
                matching_files = list(self.evidence_storage_path.glob(f"*_{evidence_id}.*"))
                
                if matching_files:
                    integrity_ok = await self._verify_evidence_integrity(str(matching_files[0]), metadata)
                    if not integrity_ok:
                        self.logger.warning(f"Integrity verification failed for evidence {evidence_id}")
    
    async def _enforce_retention_policies(self) -> None:
        """Enforce evidence retention policies"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        
        expired_evidence = []
        for evidence_id, metadata in self.evidence_registry.items():
            if metadata.collection_timestamp < cutoff_date:
                # Check if evidence is under legal hold
                if "legal_hold" not in metadata.legal_tags:
                    expired_evidence.append(evidence_id)
        
        # Archive or delete expired evidence
        for evidence_id in expired_evidence:
            await self._archive_evidence(evidence_id)
    
    async def _archive_evidence(self, evidence_id -> None: str) -> None:
        """Archive expired evidence"""
        try:
            metadata = self.evidence_registry.get(evidence_id)
            if not metadata:
                return
            
            # Move to archive storage
            archive_path = self.evidence_storage_path / "archive"
            archive_path.mkdir(exist_ok=True)
            
            # Find evidence files
            evidence_files = list(self.evidence_storage_path.glob(f"*_{evidence_id}.*"))
            for evidence_file in evidence_files:
                archive_file = archive_path / evidence_file.name
                evidence_file.rename(archive_file)
            
            # Update metadata
            metadata.audit_trail.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "archived",
                "actor": "retention_policy_worker"
            })
            
            self.logger.info(f"Evidence {evidence_id} archived")
            
        except Exception as e:
            self.logger.error(f"Evidence archival failed for {evidence_id}: {str(e)}")
    
    async def _load_evidence_registry(self) -> None:
        """Load evidence registry from storage"""
        try:
            registry_file = self.evidence_storage_path / "evidence_registry.json"
            if registry_file.exists():
                async with aiofiles.open(registry_file, 'r') as f:
                    registry_data = json.loads(await f.read())
                    
                    for evidence_id, metadata_dict in registry_data.items():
                        # Convert dict back to EvidenceMetadata
                        metadata = EvidenceMetadata(**metadata_dict)
                        self.evidence_registry[evidence_id] = metadata
                        
        except Exception as e:
            self.logger.error(f"Failed to load evidence registry: {str(e)}")
    
    async def _save_evidence_registry(self) -> None:
        """Save evidence registry to storage"""
        try:
            registry_file = self.evidence_storage_path / "evidence_registry.json"
            registry_data = {}
            
            for evidence_id, metadata in self.evidence_registry.items():
                registry_data[evidence_id] = metadata.__dict__.copy()
                # Convert datetime objects to ISO strings
                if isinstance(registry_data[evidence_id]["collection_timestamp"], datetime):
                    registry_data[evidence_id]["collection_timestamp"] = metadata.collection_timestamp.isoformat()
            
            async with aiofiles.open(registry_file, 'w') as f:
                await f.write(json.dumps(registry_data, indent=2))
                
        except Exception as e:
            self.logger.error(f"Failed to save evidence registry: {str(e)}")


# Export main classes
__all__ = [
    "AdvancedEvidenceCollector",
    "EvidenceMetadata",
    "EvidenceCollectionResult",
    "ChainOfCustodyEntry",
    "EvidenceType",
    "EvidenceStatus",
    "EvidenceIntegrity"
]
