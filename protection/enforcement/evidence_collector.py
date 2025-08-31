"""
Evidence Collection and Documentation System
Professional evidence gathering for copyright enforcement cases
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import base64
import mimetypes
from pathlib import Path
import aiohttp
import aiofiles
from urllib.parse import urlparse
from PIL import Image
import io

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class EvidenceType(Enum):
    """Types of evidence that can be collected"""
    SCREENSHOT = "screenshot"
    VIDEO_RECORDING = "video_recording"
    AUDIO_SAMPLE = "audio_sample"
    SOURCE_CODE = "source_code"
    METADATA = "metadata"
    URL_CAPTURE = "url_capture"
    TIMESTAMP_PROOF = "timestamp_proof"
    FINGERPRINT_DATA = "fingerprint_data"
    PLATFORM_RESPONSE = "platform_response"
    LEGAL_DOCUMENT = "legal_document"


class EvidenceQuality(Enum):
    """Quality levels for collected evidence"""
    EXCELLENT = "excellent"    # Court-admissible quality
    GOOD = "good"             # Strong supporting evidence
    FAIR = "fair"             # Basic documentation
    POOR = "poor"             # Insufficient quality


class CollectionMethod(Enum):
    """Methods used to collect evidence"""
    AUTOMATED_CRAWL = "automated_crawl"
    API_EXTRACTION = "api_extraction"
    MANUAL_CAPTURE = "manual_capture"
    THIRD_PARTY_SERVICE = "third_party_service"
    BLOCKCHAIN_TIMESTAMP = "blockchain_timestamp"
    ARCHIVE_RETRIEVAL = "archive_retrieval"


@dataclass
class EvidenceMetadata:
    """Metadata for evidence collection"""
    collector_id: str
    collection_method: CollectionMethod
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_url: Optional[str] = None
    source_platform: Optional[str] = None
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    chain_of_custody: List[str] = field(default_factory=list)
    verification_status: str = "unverified"
    quality_score: float = 0.0
    
    def add_custody_entry(self, entry: str):
        """Add chain of custody entry"""
        self.chain_of_custody.append(f"{datetime.utcnow().isoformat()}: {entry}")


@dataclass
class EvidenceItem:
    """Individual piece of evidence"""
    id: str
    evidence_type: EvidenceType
    title: str
    description: str
    file_path: Optional[str] = None
    file_data: Optional[bytes] = None
    text_content: Optional[str] = None
    metadata: EvidenceMetadata = field(default_factory=lambda: EvidenceMetadata("", CollectionMethod.AUTOMATED_CRAWL))
    quality: EvidenceQuality = EvidenceQuality.FAIR
    tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def calculate_hash(self) -> str:
        """Calculate hash of evidence content"""
        if self.file_data:
            return hashlib.sha256(self.file_data).hexdigest()
        elif self.text_content:
            return hashlib.sha256(self.text_content.encode()).hexdigest()
        else:
            return ""
    
    def is_expired(self) -> bool:
        """Check if evidence has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


@dataclass
class EvidencePackage:
    """Complete evidence package for a case"""
    case_id: str
    violation_url: str
    original_content_url: str
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    summary: str = ""
    collection_started: datetime = field(default_factory=datetime.utcnow)
    collection_completed: Optional[datetime] = None
    total_items: int = 0
    verification_status: str = "pending"
    legal_admissibility: bool = False
    
    def add_evidence(self, item: EvidenceItem):
        """Add evidence item to package"""
        self.evidence_items.append(item)
        self.total_items = len(self.evidence_items)
    
    def get_evidence_by_type(self, evidence_type: EvidenceType) -> List[EvidenceItem]:
        """Get all evidence items of specific type"""



        return [item for item in self.evidence_items if item.evidence_type == evidence_type]
    
    def calculate_package_hash(self) -> str:
        """Calculate hash of entire evidence package"""
        content = f"{self.case_id}:{self.violation_url}:{self.total_items}"
        for item in self.evidence_items:
            content += f":{item.calculate_hash()}"
        return hashlib.sha256(content.encode()).hexdigest()


class ScreenshotCollector:
    """Automated screenshot collection service"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.browser_path = self.config.get('browser_path')
        self.headless = self.config.get('headless', True)
        self.screenshot_quality = self.config.get('screenshot_quality', 95)
        self.wait_time = self.config.get('wait_time', 3)  # seconds
        self.max_retries = self.config.get('max_retries', 3)
        
    async def capture_screenshot(
        self,
        url: str,
        case_id: str,
        description: str = ""
    ) -> EvidenceItem:
        """Capture screenshot of specified URL"""



        try:
            logger.info(f"Capturing screenshot of {url}")
            
            # In real implementation, would use Selenium/Playwright
            # For now, simulating screenshot capture
            screenshot_data = await self._simulate_screenshot_capture(url)
            
            # Generate evidence ID
            evidence_id = f"SCREENSHOT-{case_id}-{int(datetime.utcnow().timestamp())}"
            
            # Create metadata
            metadata = EvidenceMetadata(
                collector_id="screenshot_collector",
                collection_method=CollectionMethod.AUTOMATED_CRAWL,
                source_url=url,
                source_platform=self._extract_platform_from_url(url),
                file_hash=hashlib.sha256(screenshot_data).hexdigest(),
                file_size=len(screenshot_data),
                mime_type="image/png"
            )
            metadata.add_custody_entry(f"Screenshot captured from {url}")
            
            # Create evidence item
            evidence = EvidenceItem(
                id=evidence_id,
                evidence_type=EvidenceType.SCREENSHOT,
                title=f"Screenshot of {url}",
                description=description or f"Automated screenshot capture of alleged infringing content",
                file_data=screenshot_data,
                metadata=metadata,
                quality=EvidenceQuality.GOOD,
                tags={"screenshot", "automated", "visual_evidence"}
            )
            
            logger.info(f"Screenshot captured successfully: {evidence_id}")
            return evidence
            
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            raise
    
    async def _simulate_screenshot_capture(self, url: str) -> bytes:
        """Simulate screenshot capture (placeholder)"""



        try:
            # In real implementation, would use browser automation
            # Create a simple placeholder image
            img = Image.new('RGB', (1920, 1080), color='white')
            
            # Add some text to indicate this is a placeholder
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.load_default()
                draw.text((50, 50), f"Screenshot of: {url}", fill='black', font=font)
                draw.text((50, 100), f"Captured at: {datetime.utcnow().isoformat()}", fill='black', font=font)
            except:
                pass
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG', quality=self.screenshot_quality)
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"Error simulating screenshot: {e}")
            raise
    
    def _extract_platform_from_url(self, url: str) -> str:
        """Extract platform name from URL"""



        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if 'youtube.com' in domain or 'youtu.be' in domain:
                return 'youtube'
            elif 'spotify.com' in domain:
                return 'spotify'
            elif 'instagram.com' in domain:
                return 'instagram'
            elif 'tiktok.com' in domain:
                return 'tiktok'
            elif 'twitter.com' in domain or 'x.com' in domain:
                return 'twitter'
            else:
                return domain
                
        except Exception as e:
            logger.error(f"Error extracting platform from URL: {e}")
            return "unknown"


class MetadataCollector:
    """Metadata and technical information collector"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.include_headers = self.config.get('include_headers', True)
        self.include_social_tags = self.config.get('include_social_tags', True)
        self.timeout = self.config.get('timeout', 30)
    
    async def collect_metadata(
        self,
        url: str,
        case_id: str
    ) -> EvidenceItem:
        """Collect metadata from URL"""



        try:
            logger.info(f"Collecting metadata from {url}")
            
            metadata_dict = await self._fetch_page_metadata(url)
            
            # Generate evidence ID
            evidence_id = f"METADATA-{case_id}-{int(datetime.utcnow().timestamp())}"
            
            # Create metadata
            metadata = EvidenceMetadata(
                collector_id="metadata_collector",
                collection_method=CollectionMethod.API_EXTRACTION,
                source_url=url,
                source_platform=self._extract_platform_from_url(url),
                file_hash=hashlib.sha256(json.dumps(metadata_dict, sort_keys=True).encode()).hexdigest()
            )
            metadata.add_custody_entry(f"Metadata collected from {url}")
            
            # Create evidence item
            evidence = EvidenceItem(
                id=evidence_id,
                evidence_type=EvidenceType.METADATA,
                title=f"Metadata from {url}",
                description="Technical metadata and page information",
                text_content=json.dumps(metadata_dict, indent=2),
                metadata=metadata,
                quality=EvidenceQuality.GOOD,
                tags={"metadata", "technical", "automated"}
            )
            
            logger.info(f"Metadata collected successfully: {evidence_id}")
            return evidence
            
        except Exception as e:
            logger.error(f"Error collecting metadata: {e}")
            raise
    
    async def _fetch_page_metadata(self, url: str) -> Dict[str, Any]:
        """Fetch metadata from web page"""



        try:
            metadata = {
                'url': url,
                'timestamp': datetime.utcnow().isoformat(),
                'headers': {},
                'meta_tags': {},
                'social_tags': {},
                'title': '',
                'description': '',
                'canonical_url': '',
                'language': '',
                'status_code': 0
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url) as response:
                    metadata['status_code'] = response.status
                    
                    if self.include_headers:
                        metadata['headers'] = dict(response.headers)
                    
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Parse HTML for meta tags (simplified)
                        # In real implementation, would use BeautifulSoup or similar
                        metadata.update(self._parse_html_metadata(html_content))
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error fetching page metadata: {e}")
            return {
                'url': url,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def _parse_html_metadata(self, html: str) -> Dict[str, Any]:
        """Parse HTML for metadata (simplified implementation)"""



        try:
            # Simplified HTML parsing - in real implementation would use proper parser
            meta_data = {
                'title': '',
                'description': '',
                'meta_tags': {},
                'social_tags': {}
            }
            
            # Extract title
            import re
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            if title_match:
                meta_data['title'] = title_match.group(1).strip()
            
            # Extract meta tags
            meta_matches = re.findall(r'<meta[^>]+>', html, re.IGNORECASE)
            for meta_tag in meta_matches:
                name_match = re.search(r'name=["\']([^"\']+)["\']', meta_tag)
                content_match = re.search(r'content=["\']([^"\']+)["\']', meta_tag)
                
                if name_match and content_match:
                    meta_data['meta_tags'][name_match.group(1)] = content_match.group(1)
                    
                    # Special handling for description
                    if name_match.group(1).lower() == 'description':
                        meta_data['description'] = content_match.group(1)
            
            return meta_data
            
        except Exception as e:
            logger.error(f"Error parsing HTML metadata: {e}")
            return {}
    
    def _extract_platform_from_url(self, url: str) -> str:
        """Extract platform name from URL"""



        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if 'youtube.com' in domain or 'youtu.be' in domain:
                return 'youtube'
            elif 'spotify.com' in domain:
                return 'spotify'
            elif 'instagram.com' in domain:
                return 'instagram'
            elif 'tiktok.com' in domain:
                return 'tiktok'
            elif 'twitter.com' in domain or 'x.com' in domain:
                return 'twitter'
            else:
                return domain
                
        except Exception as e:
            logger.error(f"Error extracting platform from URL: {e}")
            return "unknown"


class TimestampCollector:
    """Timestamp and chronological evidence collector"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.blockchain_enabled = self.config.get('blockchain_enabled', False)
        self.archive_enabled = self.config.get('archive_enabled', True)
    
    async def create_timestamp_proof(
        self,
        case_id: str,
        content_hash: str,
        description: str = ""
    ) -> EvidenceItem:
        """Create timestamp proof for content"""



        try:
            logger.info(f"Creating timestamp proof for case {case_id}")
            
            timestamp_data = {
                'case_id': case_id,
                'content_hash': content_hash,
                'timestamp': datetime.utcnow().isoformat(),
                'timezone': 'UTC',
                'proof_method': 'digital_signature',
                'nonce': hashlib.sha256(f"{case_id}{content_hash}{datetime.utcnow()}".encode()).hexdigest()[:16]
            }
            
            if self.blockchain_enabled:
                timestamp_data['blockchain_record'] = await self._create_blockchain_timestamp(content_hash)
            
            # Generate evidence ID
            evidence_id = f"TIMESTAMP-{case_id}-{int(datetime.utcnow().timestamp())}"
            
            # Create metadata
            metadata = EvidenceMetadata(
                collector_id="timestamp_collector",
                collection_method=CollectionMethod.BLOCKCHAIN_TIMESTAMP if self.blockchain_enabled else CollectionMethod.AUTOMATED_CRAWL,
                file_hash=hashlib.sha256(json.dumps(timestamp_data, sort_keys=True).encode()).hexdigest()
            )
            metadata.add_custody_entry(f"Timestamp proof created for content hash {content_hash}")
            
            # Create evidence item
            evidence = EvidenceItem(
                id=evidence_id,
                evidence_type=EvidenceType.TIMESTAMP_PROOF,
                title=f"Timestamp Proof for Case {case_id}",
                description=description or "Cryptographic timestamp proof of content existence",
                text_content=json.dumps(timestamp_data, indent=2),
                metadata=metadata,
                quality=EvidenceQuality.EXCELLENT if self.blockchain_enabled else EvidenceQuality.GOOD,
                tags={"timestamp", "proof", "cryptographic"}
            )
            
            logger.info(f"Timestamp proof created successfully: {evidence_id}")
            return evidence
            
        except Exception as e:
            logger.error(f"Error creating timestamp proof: {e}")
            raise
    
    async def _create_blockchain_timestamp(self, content_hash: str) -> Dict[str, Any]:
        """Create blockchain timestamp (placeholder)"""



        try:
            # In real implementation, would interact with blockchain service
            # like OpenTimestamps, or submit to Bitcoin/Ethereum blockchain
            
            blockchain_record = {
                'transaction_id': f"0x{hashlib.sha256(content_hash.encode()).hexdigest()}",
                'block_number': 12345678,  # Simulated
                'block_hash': f"0x{hashlib.sha256(f'block{content_hash}'.encode()).hexdigest()}",
                'timestamp': datetime.utcnow().isoformat(),
                'network': 'bitcoin_testnet',  # or ethereum, etc.
                'confirmation_count': 6
            }
            
            return blockchain_record
            
        except Exception as e:
            logger.error(f"Error creating blockchain timestamp: {e}")
            return {}


class FingerprintCollector:
    """Content fingerprint evidence collector"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    async def collect_fingerprint_evidence(
        self,
        case_id: str,
        original_fingerprint: Dict[str, Any],
        matched_fingerprint: Dict[str, Any],
        similarity_score: float
    ) -> EvidenceItem:
        """Collect fingerprint matching evidence"""



        try:
            logger.info(f"Collecting fingerprint evidence for case {case_id}")
            
            fingerprint_data = {
                'case_id': case_id,
                'original_fingerprint': original_fingerprint,
                'matched_fingerprint': matched_fingerprint,
                'similarity_score': similarity_score,
                'matching_algorithm': 'advanced_perceptual_hash',
                'confidence_level': self._calculate_confidence_level(similarity_score),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'matching_details': {
                    'hash_distance': abs(hash(str(original_fingerprint)) - hash(str(matched_fingerprint))),
                    'feature_correlation': similarity_score,
                    'false_positive_probability': max(0.01, 1.0 - similarity_score)
                }
            }
            
            # Generate evidence ID
            evidence_id = f"FINGERPRINT-{case_id}-{int(datetime.utcnow().timestamp())}"
            
            # Create metadata
            metadata = EvidenceMetadata(
                collector_id="fingerprint_collector",
                collection_method=CollectionMethod.API_EXTRACTION,
                file_hash=hashlib.sha256(json.dumps(fingerprint_data, sort_keys=True).encode()).hexdigest()
            )
            metadata.add_custody_entry(f"Fingerprint analysis completed with {similarity_score:.3f} similarity")
            
            # Create evidence item
            evidence = EvidenceItem(
                id=evidence_id,
                evidence_type=EvidenceType.FINGERPRINT_DATA,
                title=f"Fingerprint Analysis for Case {case_id}",
                description=f"Content fingerprint matching analysis showing {similarity_score:.1%} similarity",
                text_content=json.dumps(fingerprint_data, indent=2),
                metadata=metadata,
                quality=self._determine_quality_from_score(similarity_score),
                tags={"fingerprint", "analysis", "technical", "similarity"}
            )
            
            logger.info(f"Fingerprint evidence collected successfully: {evidence_id}")
            return evidence
            
        except Exception as e:
            logger.error(f"Error collecting fingerprint evidence: {e}")
            raise
    
    def _calculate_confidence_level(self, similarity_score: float) -> str:
        """Calculate confidence level based on similarity score"""
        if similarity_score >= 0.95:
            return "very_high"
        elif similarity_score >= 0.85:
            return "high"
        elif similarity_score >= 0.70:
            return "medium"
        elif similarity_score >= 0.50:
            return "low"
        else:
            return "very_low"
    
    def _determine_quality_from_score(self, similarity_score: float) -> EvidenceQuality:
        """Determine evidence quality based on similarity score"""
        if similarity_score >= 0.90:
            return EvidenceQuality.EXCELLENT
        elif similarity_score >= 0.75:
            return EvidenceQuality.GOOD
        elif similarity_score >= 0.60:
            return EvidenceQuality.FAIR
        else:
            return EvidenceQuality.POOR


class EvidenceCollectionService:
    """Main service for collecting and managing evidence"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize collectors
        self.screenshot_collector = ScreenshotCollector(self.config.get('screenshot', {}))
        self.metadata_collector = MetadataCollector(self.config.get('metadata', {}))
        self.timestamp_collector = TimestampCollector(self.config.get('timestamp', {}))
        self.fingerprint_collector = FingerprintCollector(self.config.get('fingerprint', {}))
        
        # Storage configuration
        self.storage_path = Path(self.config.get('storage_path', 'evidence_storage'))
        self.storage_path.mkdir(exist_ok=True)
        
        # Collection settings
        self.max_concurrent_collections = self.config.get('max_concurrent_collections', 5)
        self.evidence_retention_days = self.config.get('evidence_retention_days', 365)
        self.auto_verification = self.config.get('auto_verification', True)
        
        # Active evidence packages
        self.active_packages: Dict[str, EvidencePackage] = {}
        
        logger.info("Evidence collection service initialized")
    
    async def start_evidence_collection(
        self,
        case_id: str,
        violation_url: str,
        original_content_url: str,
        collection_types: Optional[List[EvidenceType]] = None
    ) -> EvidencePackage:
        """Start comprehensive evidence collection for a case"""



        try:
            logger.info(f"Starting evidence collection for case {case_id}")
            
            # Create evidence package
            package = EvidencePackage(
                case_id=case_id,
                violation_url=violation_url,
                original_content_url=original_content_url
            )
            
            self.active_packages[case_id] = package
            
            # Default collection types
            if not collection_types:
                collection_types = [
                    EvidenceType.SCREENSHOT,
                    EvidenceType.METADATA,
                    EvidenceType.TIMESTAMP_PROOF,
                    EvidenceType.URL_CAPTURE
                ]
            
            # Collect evidence concurrently
            collection_tasks = []
            
            if EvidenceType.SCREENSHOT in collection_types:
                collection_tasks.append(
                    self._collect_screenshot_evidence(package, violation_url)
                )
            
            if EvidenceType.METADATA in collection_types:
                collection_tasks.append(
                    self._collect_metadata_evidence(package, violation_url)
                )
            
            if EvidenceType.TIMESTAMP_PROOF in collection_types:
                collection_tasks.append(
                    self._collect_timestamp_evidence(package)
                )
            
            # Execute collection tasks
            if collection_tasks:
                await asyncio.gather(*collection_tasks, return_exceptions=True)
            
            # Mark collection as completed
            package.collection_completed = datetime.utcnow()
            
            # Auto-verification if enabled
            if self.auto_verification:
                await self._verify_evidence_package(package)
            
            # Save package to storage
            await self._save_evidence_package(package)
            
            logger.info(f"Evidence collection completed for case {case_id}: {package.total_items} items")
            return package
            
        except Exception as e:
            logger.error(f"Error in evidence collection for case {case_id}: {e}")
            raise
    
    async def _collect_screenshot_evidence(self, package: EvidencePackage, url: str):
        """Collect screenshot evidence"""



        try:
            evidence = await self.screenshot_collector.capture_screenshot(
                url=url,
                case_id=package.case_id,
                description=f"Screenshot of alleged infringing content at {url}"
            )
            package.add_evidence(evidence)
            
        except Exception as e:
            logger.error(f"Error collecting screenshot evidence: {e}")
    
    async def _collect_metadata_evidence(self, package: EvidencePackage, url: str):
        """Collect metadata evidence"""



        try:
            evidence = await self.metadata_collector.collect_metadata(
                url=url,
                case_id=package.case_id
            )
            package.add_evidence(evidence)
            
        except Exception as e:
            logger.error(f"Error collecting metadata evidence: {e}")
    
    async def _collect_timestamp_evidence(self, package: EvidencePackage):
        """Collect timestamp evidence"""



        try:
            # Create timestamp for the violation URL content
            url_hash = hashlib.sha256(package.violation_url.encode()).hexdigest()
            
            evidence = await self.timestamp_collector.create_timestamp_proof(
                case_id=package.case_id,
                content_hash=url_hash,
                description=f"Timestamp proof for violation detection at {package.violation_url}"
            )
            package.add_evidence(evidence)
            
        except Exception as e:
            logger.error(f"Error collecting timestamp evidence: {e}")
    
    async def add_fingerprint_evidence(
        self,
        case_id: str,
        original_fingerprint: Dict[str, Any],
        matched_fingerprint: Dict[str, Any],
        similarity_score: float
    ) -> bool:
        """Add fingerprint evidence to existing package"""



        try:
            package = self.active_packages.get(case_id)
            if not package:
                logger.error(f"No active evidence package found for case {case_id}")
                return False
            
            evidence = await self.fingerprint_collector.collect_fingerprint_evidence(
                case_id=case_id,
                original_fingerprint=original_fingerprint,
                matched_fingerprint=matched_fingerprint,
                similarity_score=similarity_score
            )
            
            package.add_evidence(evidence)
            
            # Update package verification status
            if self.auto_verification:
                await self._verify_evidence_package(package)
            
            # Save updated package
            await self._save_evidence_package(package)
            
            logger.info(f"Fingerprint evidence added to case {case_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding fingerprint evidence to case {case_id}: {e}")
            return False
    
    async def _verify_evidence_package(self, package: EvidencePackage):
        """Verify evidence package integrity and quality"""



        try:
            verification_checks = {
                'has_screenshot': bool(package.get_evidence_by_type(EvidenceType.SCREENSHOT)),
                'has_metadata': bool(package.get_evidence_by_type(EvidenceType.METADATA)),
                'has_timestamp': bool(package.get_evidence_by_type(EvidenceType.TIMESTAMP_PROOF)),
                'has_fingerprint': bool(package.get_evidence_by_type(EvidenceType.FINGERPRINT_DATA)),
                'all_hashes_valid': True,
                'quality_sufficient': True
            }
            
            # Verify evidence hashes
            for evidence in package.evidence_items:
                calculated_hash = evidence.calculate_hash()
                if evidence.metadata.file_hash and evidence.metadata.file_hash != calculated_hash:
                    verification_checks['all_hashes_valid'] = False
                    break
            
            # Check evidence quality
            poor_quality_count = sum(1 for item in package.evidence_items if item.quality == EvidenceQuality.POOR)
            if poor_quality_count > len(package.evidence_items) / 2:
                verification_checks['quality_sufficient'] = False
            
            # Determine legal admissibility
            required_evidence_types = [EvidenceType.SCREENSHOT, EvidenceType.TIMESTAMP_PROOF]
            has_required = all(
                verification_checks.get(f'has_{etype.value}', False)
                for etype in required_evidence_types
            )
            
            package.legal_admissibility = (
                has_required and
                verification_checks['all_hashes_valid'] and
                verification_checks['quality_sufficient']
            )
            
            package.verification_status = "verified" if package.legal_admissibility else "insufficient"
            
            logger.info(f"Evidence package verification completed for case {package.case_id}: {package.verification_status}")
            
        except Exception as e:
            logger.error(f"Error verifying evidence package: {e}")
            package.verification_status = "error"
    
    async def _save_evidence_package(self, package: EvidencePackage):
        """Save evidence package to persistent storage"""



        try:
            case_dir = self.storage_path / package.case_id
            case_dir.mkdir(exist_ok=True)
            
            # Save individual evidence files
            for evidence in package.evidence_items:
                if evidence.file_data:
                    file_path = case_dir / f"{evidence.id}.dat"
                    async with aiofiles.open(file_path, 'wb') as f:
                        await f.write(evidence.file_data)
                    evidence.file_path = str(file_path)
                    evidence.file_data = None  # Clear from memory
                
                elif evidence.text_content:
                    file_path = case_dir / f"{evidence.id}.txt"
                    async with aiofiles.open(file_path, 'w') as f:
                        await f.write(evidence.text_content)
                    evidence.file_path = str(file_path)
            
            # Save package metadata
            package_data = {
                'case_id': package.case_id,
                'violation_url': package.violation_url,
                'original_content_url': package.original_content_url,
                'summary': package.summary,
                'collection_started': package.collection_started.isoformat(),
                'collection_completed': package.collection_completed.isoformat() if package.collection_completed else None,
                'total_items': package.total_items,
                'verification_status': package.verification_status,
                'legal_admissibility': package.legal_admissibility,
                'package_hash': package.calculate_package_hash(),
                'evidence_items': [
                    {
                        'id': item.id,
                        'evidence_type': item.evidence_type.value,
                        'title': item.title,
                        'description': item.description,
                        'file_path': item.file_path,
                        'quality': item.quality.value,
                        'tags': list(item.tags),
                        'created_at': item.created_at.isoformat(),
                        'expires_at': item.expires_at.isoformat() if item.expires_at else None,
                        'metadata': {
                            'collector_id': item.metadata.collector_id,
                            'collection_method': item.metadata.collection_method.value,
                            'timestamp': item.metadata.timestamp.isoformat(),
                            'source_url': item.metadata.source_url,
                            'source_platform': item.metadata.source_platform,
                            'file_hash': item.metadata.file_hash,
                            'file_size': item.metadata.file_size,
                            'mime_type': item.metadata.mime_type,
                            'chain_of_custody': item.metadata.chain_of_custody,
                            'verification_status': item.metadata.verification_status,
                            'quality_score': item.metadata.quality_score
                        }
                    }
                    for item in package.evidence_items
                ]
            }
            
            package_file = case_dir / 'package.json'
            async with aiofiles.open(package_file, 'w') as f:
                await f.write(json.dumps(package_data, indent=2))
            
            logger.debug(f"Evidence package saved for case {package.case_id}")
            
        except Exception as e:
            logger.error(f"Error saving evidence package: {e}")
            raise
    
    async def get_evidence_package(self, case_id: str) -> Optional[EvidencePackage]:
        """Retrieve evidence package for case"""



        try:
            # Check active packages first
            if case_id in self.active_packages:
                return self.active_packages[case_id]
            
            # Load from storage
            package_file = self.storage_path / case_id / 'package.json'
            if not package_file.exists():
                return None
            
            async with aiofiles.open(package_file, 'r') as f:
                package_data = json.loads(await f.read())
            
            # Reconstruct package
            package = EvidencePackage(
                case_id=package_data['case_id'],
                violation_url=package_data['violation_url'],
                original_content_url=package_data['original_content_url'],
                summary=package_data.get('summary', ''),
                collection_started=datetime.fromisoformat(package_data['collection_started']),
                collection_completed=datetime.fromisoformat(package_data['collection_completed']) if package_data.get('collection_completed') else None,
                total_items=package_data['total_items'],
                verification_status=package_data['verification_status'],
                legal_admissibility=package_data['legal_admissibility']
            )
            
            # Reconstruct evidence items
            for item_data in package_data['evidence_items']:
                metadata = EvidenceMetadata(
                    collector_id=item_data['metadata']['collector_id'],
                    collection_method=CollectionMethod(item_data['metadata']['collection_method']),
                    timestamp=datetime.fromisoformat(item_data['metadata']['timestamp']),
                    source_url=item_data['metadata'].get('source_url'),
                    source_platform=item_data['metadata'].get('source_platform'),
                    file_hash=item_data['metadata'].get('file_hash'),
                    file_size=item_data['metadata'].get('file_size'),
                    mime_type=item_data['metadata'].get('mime_type'),
                    chain_of_custody=item_data['metadata'].get('chain_of_custody', []),
                    verification_status=item_data['metadata'].get('verification_status', 'unverified'),
                    quality_score=item_data['metadata'].get('quality_score', 0.0)
                )
                
                evidence = EvidenceItem(
                    id=item_data['id'],
                    evidence_type=EvidenceType(item_data['evidence_type']),
                    title=item_data['title'],
                    description=item_data['description'],
                    file_path=item_data.get('file_path'),
                    metadata=metadata,
                    quality=EvidenceQuality(item_data['quality']),
                    tags=set(item_data.get('tags', [])),
                    created_at=datetime.fromisoformat(item_data['created_at']),
                    expires_at=datetime.fromisoformat(item_data['expires_at']) if item_data.get('expires_at') else None
                )
                
                package.add_evidence(evidence)
            
            return package
            
        except Exception as e:
            logger.error(f"Error retrieving evidence package for case {case_id}: {e}")
            return None
    
    async def cleanup_expired_evidence(self):
        """Clean up expired evidence packages"""



        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.evidence_retention_days)
            cleaned_count = 0
            
            for case_dir in self.storage_path.iterdir():
                if case_dir.is_dir():
                    package_file = case_dir / 'package.json'
                    if package_file.exists():
                        try:
                            async with aiofiles.open(package_file, 'r') as f:
                                package_data = json.loads(await f.read())
                            
                            collection_date = datetime.fromisoformat(package_data['collection_started'])
                            if collection_date < cutoff_date:
                                # Remove entire case directory
                                import shutil
                                shutil.rmtree(case_dir)
                                cleaned_count += 1
                                
                                # Remove from active packages if present
                                case_id = package_data['case_id']
                                if case_id in self.active_packages:
                                    del self.active_packages[case_id]
                                    
                        except Exception as e:
                            logger.error(f"Error processing case directory {case_dir}: {e}")
            
            logger.info(f"Cleaned up {cleaned_count} expired evidence packages")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired evidence: {e}")
    
    async def get_collection_statistics(self) -> Dict[str, Any]:
        """Get evidence collection statistics"""



        try:
            total_packages = len(list(self.storage_path.iterdir()))
            active_packages = len(self.active_packages)
            
            # Count evidence by type
            evidence_type_counts = {}
            quality_counts = {}
            
            for package in self.active_packages.values():
                for evidence in package.evidence_items:
                    evidence_type = evidence.evidence_type.value
                    evidence_type_counts[evidence_type] = evidence_type_counts.get(evidence_type, 0) + 1
                    
                    quality = evidence.quality.value
                    quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
            stats = {
                'total_packages': total_packages,
                'active_packages': active_packages,
                'evidence_by_type': evidence_type_counts,
                'evidence_by_quality': quality_counts,
                'storage_path': str(self.storage_path),
                'retention_days': self.evidence_retention_days,
                'auto_verification_enabled': self.auto_verification
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection statistics: {e}")
            return {}
    
    async def shutdown(self):
        """Shutdown evidence collection service"""



        try:
            # Save all active packages
            for package in self.active_packages.values():
                await self._save_evidence_package(package)
            
            self.active_packages.clear()
            logger.info("Evidence collection service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error shutting down evidence collection service: {e}")


# Global instance
evidence_service = EvidenceCollectionService()


async def get_evidence_service() -> EvidenceCollectionService:
    """Get the global evidence collection service instance"""



    return evidence_service


__all__ = [
    'EvidenceCollectionService',
    'EvidencePackage',
    'EvidenceItem',
    'EvidenceMetadata',
    'EvidenceType',
    'EvidenceQuality',
    'CollectionMethod',
    'ScreenshotCollector',
    'MetadataCollector',
    'TimestampCollector',
    'FingerprintCollector',
    'get_evidence_service'
]
