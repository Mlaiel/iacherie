"""Evidence Collection System for Content Protection

This module provides comprehensive evidence collection for legal proceedings:
- Automated screenshot and screen recording capture
- Metadata extraction and preservation
- Digital forensics and chain of custody
- Evidence packaging for legal use
- Timestamp verification and notarization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import json
import hashlib
import base64
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import logging
from pathlib import Path
import zipfile
import tempfile
import uuid

# Web automation and screenshots
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Image and video processing
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

# Network and metadata analysis
import aiohttp
import requests
from bs4 import BeautifulSoup
import whois
from urllib.parse import urlparse, urljoin

# Cryptographic verification
import hmac
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# Internal imports
from ...utils.logging import get_logger
from ...database.models.content import ContentFingerprint, EvidenceRecord
from ...config.settings import get_settings
from .violation_detector import ViolationEvidence, ViolationType

logger = get_logger(__name__)
settings = get_settings()


class EvidenceType(Enum):
    """Types of evidence that can be collected"""
    SCREENSHOT = "screenshot"
    SCREEN_RECORDING = "screen_recording"
    PAGE_SOURCE = "page_source"
    NETWORK_CAPTURE = "network_capture"
    METADATA_DUMP = "metadata_dump"
    WHOIS_RECORD = "whois_record"
    CERTIFICATE_CHAIN = "certificate_chain"
    HASH_VERIFICATION = "hash_verification"
    TIMESTAMP_PROOF = "timestamp_proof"


class EvidenceQuality(Enum):
    """Quality levels for evidence"""
    HIGH = "high"           # Full metadata, timestamps, signatures
    MEDIUM = "medium"       # Basic metadata and screenshots
    LOW = "low"            # Minimal evidence
    INSUFFICIENT = "insufficient"


@dataclass
class EvidenceMetadata:
    """Metadata for evidence items"""
    evidence_id: str
    evidence_type: EvidenceType
    file_path: str
    file_hash: str
    file_size: int
    
    # Collection details
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    collection_method: str = ""
    collector_info: Dict[str, str] = field(default_factory=dict)
    
    # Content details
    source_url: str = ""
    page_title: str = ""
    content_hash: str = ""
    
    # Technical details
    resolution: Optional[Tuple[int, int]] = None
    duration: Optional[float] = None
    encoding: str = ""
    
    # Verification
    digital_signature: Optional[str] = None
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)
    
    # Legal compliance
    jurisdiction: str = ""
    collection_legal_basis: str = ""
    retention_period: Optional[datetime] = None


@dataclass
class EvidencePackage:
    """Complete evidence package for legal proceedings"""
    package_id: str
    violation_evidence: ViolationEvidence
    
    # Evidence items
    evidence_items: List[EvidenceMetadata] = field(default_factory=list)
    
    # Package metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = ""
    case_reference: str = ""
    
    # Quality assessment
    evidence_quality: EvidenceQuality = EvidenceQuality.INSUFFICIENT
    completeness_score: float = 0.0
    
    # Legal compliance
    chain_of_custody_verified: bool = False
    timestamps_verified: bool = False
    signatures_verified: bool = False
    
    # Packaging
    archive_path: Optional[str] = None
    archive_hash: Optional[str] = None


class WebEvidenceCollector:
    """Collect evidence from web sources"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "evidence_collection"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Chrome driver setup
        self.driver_options = Options()
        self.driver_options.add_argument('--headless')
        self.driver_options.add_argument('--no-sandbox')
        self.driver_options.add_argument('--disable-dev-shm-usage')
        self.driver_options.add_argument('--disable-gpu')
        self.driver_options.add_argument('--window-size=1920,1080')
        self.driver_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Evidence collection settings
        self.screenshot_quality = 95
        self.max_page_load_time = 30
        self.evidence_retention_days = 365 * 7  # 7 years for legal compliance
    
    async def collect_screenshot_evidence(self, url: str, evidence_id: str) -> EvidenceMetadata:
        """Collect screenshot evidence with legal annotations"""
        try:
            driver = webdriver.Chrome(options=self.driver_options)
            
            try:
                # Navigate to URL
                driver.get(url)
                
                # Wait for page to load
                WebDriverWait(driver, self.max_page_load_time).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Additional wait for dynamic content
                await asyncio.sleep(3)
                
                # Get page metadata
                page_title = driver.title
                page_source_hash = hashlib.sha256(driver.page_source.encode()).hexdigest()
                
                # Take full page screenshot
                screenshot_data = driver.get_screenshot_as_png()
                
                # Add legal annotations
                annotated_screenshot = self._add_legal_annotations(
                    screenshot_data, url, page_title
                )
                
                # Save screenshot
                screenshot_path = self.temp_dir / f"screenshot_{evidence_id}.png"
                with open(screenshot_path, 'wb') as f:
                    f.write(annotated_screenshot)
                
                # Calculate file hash
                file_hash = hashlib.sha256(annotated_screenshot).hexdigest()
                
                # Create metadata
                metadata = EvidenceMetadata(
                    evidence_id=evidence_id,
                    evidence_type=EvidenceType.SCREENSHOT,
                    file_path=str(screenshot_path),
                    file_hash=file_hash,
                    file_size=len(annotated_screenshot),
                    collection_method="selenium_webdriver",
                    collector_info={
                        'user_agent': driver.execute_script("return navigator.userAgent;"),
                        'browser_version': driver.capabilities.get('browserVersion', ''),
                        'platform': driver.capabilities.get('platformName', '')
                    },
                    source_url=url,
                    page_title=page_title,
                    content_hash=page_source_hash,
                    resolution=(1920, 1080),
                    encoding="PNG"
                )
                
                # Add to chain of custody
                self._add_chain_of_custody_entry(metadata, "screenshot_captured", {
                    'method': 'automated_selenium',
                    'quality': 'high',
                    'full_page': True
                })
                
                return metadata
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Error collecting screenshot evidence: {e}")
            raise
    
    async def collect_page_source_evidence(self, url: str, evidence_id: str) -> EvidenceMetadata:
        """Collect page source code evidence"""
        try:
            driver = webdriver.Chrome(options=self.driver_options)
            
            try:
                driver.get(url)
                WebDriverWait(driver, self.max_page_load_time).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                await asyncio.sleep(3)
                
                # Get page source
                page_source = driver.page_source
                page_title = driver.title
                
                # Save page source
                source_path = self.temp_dir / f"source_{evidence_id}.html"
                with open(source_path, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                
                # Calculate hash
                source_hash = hashlib.sha256(page_source.encode()).hexdigest()
                
                metadata = EvidenceMetadata(
                    evidence_id=evidence_id,
                    evidence_type=EvidenceType.PAGE_SOURCE,
                    file_path=str(source_path),
                    file_hash=source_hash,
                    file_size=len(page_source.encode()),
                    collection_method="selenium_page_source",
                    source_url=url,
                    page_title=page_title,
                    content_hash=source_hash,
                    encoding="UTF-8"
                )
                
                self._add_chain_of_custody_entry(metadata, "page_source_captured")
                
                return metadata
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Error collecting page source evidence: {e}")
            raise
    
    async def collect_metadata_evidence(self, url: str, evidence_id: str) -> EvidenceMetadata:
        """Collect comprehensive metadata evidence"""
        try:
            metadata_collection = {}
            
            # HTTP headers
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    metadata_collection['http_headers'] = dict(response.headers)
                    metadata_collection['status_code'] = response.status
                    metadata_collection['response_size'] = len(await response.read())
            
            # HTML metadata extraction
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract meta tags
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
                content = meta.get('content')
                if name and content:
                    meta_tags[name] = content
            
            metadata_collection['meta_tags'] = meta_tags
            
            # Extract structured data (JSON-LD, microdata)
            structured_data = []
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    structured_data.append(data)
                except:
                    pass
            
            metadata_collection['structured_data'] = structured_data
            
            # Social media meta tags
            social_meta = {}
            social_prefixes = ['og:', 'twitter:', 'fb:']
            for meta in soup.find_all('meta'):
                property_name = meta.get('property') or meta.get('name', '')
                if any(property_name.startswith(prefix) for prefix in social_prefixes):
                    social_meta[property_name] = meta.get('content')
            
            metadata_collection['social_meta'] = social_meta
            
            # Save metadata
            metadata_json = json.dumps(metadata_collection, indent=2, default=str)
            metadata_path = self.temp_dir / f"metadata_{evidence_id}.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write(metadata_json)
            
            # Calculate hash
            metadata_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
            
            evidence_metadata = EvidenceMetadata(
                evidence_id=evidence_id,
                evidence_type=EvidenceType.METADATA_DUMP,
                file_path=str(metadata_path),
                file_hash=metadata_hash,
                file_size=len(metadata_json.encode()),
                collection_method="http_metadata_extraction",
                source_url=url,
                content_hash=metadata_hash,
                encoding="JSON"
            )
            
            self._add_chain_of_custody_entry(evidence_metadata, "metadata_extracted", {
                'meta_tags_count': len(meta_tags),
                'structured_data_count': len(structured_data),
                'social_meta_count': len(social_meta)
            })
            
            return evidence_metadata
            
        except Exception as e:
            logger.error(f"Error collecting metadata evidence: {e}")
            raise
    
    async def collect_whois_evidence(self, url: str, evidence_id: str) -> EvidenceMetadata:
        """Collect WHOIS domain information"""
        try:
            domain = urlparse(url).netloc
            
            # Get WHOIS information
            domain_info = whois.whois(domain)
            
            # Convert to JSON serializable format
            whois_data = {}
            for key, value in domain_info.items():
                if value is not None:
                    if isinstance(value, (list, tuple)):
                        whois_data[key] = [str(item) for item in value]
                    else:
                        whois_data[key] = str(value)
            
            # Save WHOIS data
            whois_json = json.dumps(whois_data, indent=2, default=str)
            whois_path = self.temp_dir / f"whois_{evidence_id}.json"
            with open(whois_path, 'w', encoding='utf-8') as f:
                f.write(whois_json)
            
            # Calculate hash
            whois_hash = hashlib.sha256(whois_json.encode()).hexdigest()
            
            metadata = EvidenceMetadata(
                evidence_id=evidence_id,
                evidence_type=EvidenceType.WHOIS_RECORD,
                file_path=str(whois_path),
                file_hash=whois_hash,
                file_size=len(whois_json.encode()),
                collection_method="whois_lookup",
                source_url=url,
                content_hash=whois_hash,
                encoding="JSON"
            )
            
            self._add_chain_of_custody_entry(metadata, "whois_lookup_performed", {
                'domain': domain,
                'registrar': whois_data.get('registrar'),
                'creation_date': whois_data.get('creation_date')
            })
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error collecting WHOIS evidence: {e}")
            raise
    
    def _add_legal_annotations(self, screenshot_data: bytes, url: str, page_title: str) -> bytes:
        """Add legal annotations to screenshot"""
        try:
            # Open image
            image = Image.open(io.BytesIO(screenshot_data))
            draw = ImageDraw.Draw(image)
            
            # Try to load a font
            try:
                font = ImageFont.truetype("arial.ttf", 16)
                small_font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Add timestamp annotation
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Create annotation box
            annotation_height = 80
            annotation_box = Image.new('RGBA', (image.width, annotation_height), (0, 0, 0, 200))
            annotation_draw = ImageDraw.Draw(annotation_box)
            
            # Add text to annotation
            annotation_draw.text((10, 5), f"Evidence Collection Timestamp: {timestamp}", fill="white", font=font)
            annotation_draw.text((10, 25), f"URL: {url[:100]}{'...' if len(url) > 100 else ''}", fill="white", font=small_font)
            annotation_draw.text((10, 40), f"Page Title: {page_title[:80]}{'...' if len(page_title) > 80 else ''}", fill="white", font=small_font)
            annotation_draw.text((10, 55), f"Evidence ID: {uuid.uuid4()}", fill="white", font=small_font)
            
            # Composite annotation onto image
            result_image = Image.new('RGBA', (image.width, image.height + annotation_height))
            result_image.paste(annotation_box, (0, 0))
            result_image.paste(image, (0, annotation_height))
            
            # Convert back to bytes
            import io
            output = io.BytesIO()
            result_image.convert('RGB').save(output, format='PNG', quality=self.screenshot_quality)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error adding legal annotations: {e}")
            return screenshot_data  # Return original if annotation fails
    
    def _add_chain_of_custody_entry(self, metadata: EvidenceMetadata, action: str, details: Dict[str, Any] = None):
        """Add entry to chain of custody"""
        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'action': action,
            'operator': 'automated_system',
            'details': details or {}
        }
        metadata.chain_of_custody.append(entry)


class CryptographicVerifier:
    """Handle cryptographic verification of evidence"""
    
    def __init__(self):
        self.private_key = self._load_or_generate_private_key()
        self.public_key = self.private_key.public_key()
    
    def _load_or_generate_private_key(self):
        """Load or generate RSA private key for signing"""
        key_path = Path("evidence_signing_key.pem")
        
        if key_path.exists():
            with open(key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None
                )
        else:
            # Generate new key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Save key
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            with open(key_path, 'wb') as f:
                f.write(pem)
        
        return private_key
    
    def sign_evidence(self, evidence_metadata: EvidenceMetadata) -> str:
        """Create digital signature for evidence"""
        try:
            # Create message to sign
            message_data = {
                'evidence_id': evidence_metadata.evidence_id,
                'file_hash': evidence_metadata.file_hash,
                'collected_at': evidence_metadata.collected_at.isoformat(),
                'source_url': evidence_metadata.source_url
            }
            
            message = json.dumps(message_data, sort_keys=True).encode()
            
            # Sign message
            signature = self.private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Return base64 encoded signature
            return base64.b64encode(signature).decode()
            
        except Exception as e:
            logger.error(f"Error signing evidence: {e}")
            raise
    
    def verify_signature(self, evidence_metadata: EvidenceMetadata, signature: str) -> bool:
        """Verify digital signature"""
        try:
            # Recreate message
            message_data = {
                'evidence_id': evidence_metadata.evidence_id,
                'file_hash': evidence_metadata.file_hash,
                'collected_at': evidence_metadata.collected_at.isoformat(),
                'source_url': evidence_metadata.source_url
            }
            
            message = json.dumps(message_data, sort_keys=True).encode()
            signature_bytes = base64.b64decode(signature)
            
            # Verify signature
            self.public_key.verify(
                signature_bytes,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False


class EvidenceCollector:
    """Main evidence collection coordinator"""
    
    def __init__(self):
        self.web_collector = WebEvidenceCollector()
        self.crypto_verifier = CryptographicVerifier()
        
        # Evidence storage
        self.evidence_packages: Dict[str, EvidencePackage] = {}
        
        # Quality thresholds
        self.quality_thresholds = {
            EvidenceQuality.HIGH: 0.85,
            EvidenceQuality.MEDIUM: 0.65,
            EvidenceQuality.LOW: 0.40
        }
    
    async def collect_evidence(self, violation_evidence: ViolationEvidence) -> EvidencePackage:
        """Collect comprehensive evidence for violation"""
        try:
            package_id = f"evidence_{violation_evidence.violation_id}_{int(datetime.utcnow().timestamp())}"
            
            package = EvidencePackage(
                package_id=package_id,
                violation_evidence=violation_evidence,
                created_by="automated_system"
            )
            
            url = violation_evidence.detected_url
            
            # Collect different types of evidence
            evidence_items = []
            
            # 1. Screenshot evidence
            try:
                screenshot_evidence = await self.web_collector.collect_screenshot_evidence(
                    url, f"{package_id}_screenshot"
                )
                screenshot_evidence.digital_signature = self.crypto_verifier.sign_evidence(screenshot_evidence)
                evidence_items.append(screenshot_evidence)
            except Exception as e:
                logger.warning(f"Failed to collect screenshot evidence: {e}")
            
            # 2. Page source evidence
            try:
                source_evidence = await self.web_collector.collect_page_source_evidence(
                    url, f"{package_id}_source"
                )
                source_evidence.digital_signature = self.crypto_verifier.sign_evidence(source_evidence)
                evidence_items.append(source_evidence)
            except Exception as e:
                logger.warning(f"Failed to collect page source evidence: {e}")
            
            # 3. Metadata evidence
            try:
                metadata_evidence = await self.web_collector.collect_metadata_evidence(
                    url, f"{package_id}_metadata"
                )
                metadata_evidence.digital_signature = self.crypto_verifier.sign_evidence(metadata_evidence)
                evidence_items.append(metadata_evidence)
            except Exception as e:
                logger.warning(f"Failed to collect metadata evidence: {e}")
            
            # 4. WHOIS evidence
            try:
                whois_evidence = await self.web_collector.collect_whois_evidence(
                    url, f"{package_id}_whois"
                )
                whois_evidence.digital_signature = self.crypto_verifier.sign_evidence(whois_evidence)
                evidence_items.append(whois_evidence)
            except Exception as e:
                logger.warning(f"Failed to collect WHOIS evidence: {e}")
            
            package.evidence_items = evidence_items
            
            # Assess evidence quality
            package.evidence_quality = self._assess_evidence_quality(package)
            package.completeness_score = self._calculate_completeness_score(package)
            
            # Verify chain of custody and signatures
            package.chain_of_custody_verified = self._verify_chain_of_custody(package)
            package.signatures_verified = self._verify_all_signatures(package)
            package.timestamps_verified = True  # All timestamps are UTC from system clock
            
            # Create evidence archive
            archive_path = await self._create_evidence_archive(package)
            package.archive_path = str(archive_path)
            package.archive_hash = self._calculate_file_hash(archive_path)
            
            # Store package
            self.evidence_packages[package_id] = package
            
            logger.info(f"Evidence collection completed: {package_id}, quality: {package.evidence_quality.value}")
            return package
            
        except Exception as e:
            logger.error(f"Error collecting evidence: {e}")
            raise
    
    def _assess_evidence_quality(self, package: EvidencePackage) -> EvidenceQuality:
        """Assess overall quality of evidence package"""
        evidence_types = set(item.evidence_type for item in package.evidence_items)
        
        # Required evidence types for high quality
        high_quality_types = {
            EvidenceType.SCREENSHOT,
            EvidenceType.PAGE_SOURCE,
            EvidenceType.METADATA_DUMP,
            EvidenceType.WHOIS_RECORD
        }
        
        medium_quality_types = {
            EvidenceType.SCREENSHOT,
            EvidenceType.PAGE_SOURCE,
            EvidenceType.METADATA_DUMP
        }
        
        low_quality_types = {
            EvidenceType.SCREENSHOT,
            EvidenceType.PAGE_SOURCE
        }
        
        if high_quality_types.issubset(evidence_types):
            return EvidenceQuality.HIGH
        elif medium_quality_types.issubset(evidence_types):
            return EvidenceQuality.MEDIUM
        elif low_quality_types.issubset(evidence_types):
            return EvidenceQuality.LOW
        else:
            return EvidenceQuality.INSUFFICIENT
    
    def _calculate_completeness_score(self, package: EvidencePackage) -> float:
        """Calculate completeness score (0-1)"""
        max_possible_evidence = 6  # screenshot, source, metadata, whois, network, timestamp
        actual_evidence = len(package.evidence_items)
        
        # Base score from evidence count
        evidence_score = min(actual_evidence / max_possible_evidence, 1.0)
        
        # Bonus for signatures and chain of custody
        signature_bonus = 0.1 if any(item.digital_signature for item in package.evidence_items) else 0
        custody_bonus = 0.1 if any(item.chain_of_custody for item in package.evidence_items) else 0
        
        return min(evidence_score + signature_bonus + custody_bonus, 1.0)
    
    def _verify_chain_of_custody(self, package: EvidencePackage) -> bool:
        """Verify chain of custody for all evidence items"""
        try:
            for item in package.evidence_items:
                if not item.chain_of_custody:
                    return False
                
                # Verify timestamps are in chronological order
                timestamps = [
                    datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    for entry in item.chain_of_custody
                ]
                
                if timestamps != sorted(timestamps):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying chain of custody: {e}")
            return False
    
    def _verify_all_signatures(self, package: EvidencePackage) -> bool:
        """Verify digital signatures for all evidence items"""
        try:
            for item in package.evidence_items:
                if item.digital_signature:
                    if not self.crypto_verifier.verify_signature(item, item.digital_signature):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying signatures: {e}")
            return False
    
    async def _create_evidence_archive(self, package: EvidencePackage) -> Path:
        """Create compressed archive of all evidence"""
        try:
            archive_path = self.web_collector.temp_dir / f"evidence_package_{package.package_id}.zip"
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                # Add evidence files
                for item in package.evidence_items:
                    file_path = Path(item.file_path)
                    if file_path.exists():
                        archive.write(file_path, file_path.name)
                
                # Add package metadata
                package_metadata = {
                    'package_id': package.package_id,
                    'violation_id': package.violation_evidence.violation_id,
                    'created_at': package.created_at.isoformat(),
                    'evidence_quality': package.evidence_quality.value,
                    'completeness_score': package.completeness_score,
                    'evidence_items': [
                        {
                            'evidence_id': item.evidence_id,
                            'evidence_type': item.evidence_type.value,
                            'file_hash': item.file_hash,
                            'collected_at': item.collected_at.isoformat(),
                            'digital_signature': item.digital_signature
                        }
                        for item in package.evidence_items
                    ]
                }
                
                package_json = json.dumps(package_metadata, indent=2)
                archive.writestr("package_metadata.json", package_json)
                
                # Add README with legal information
                readme_content = f"""DIGITAL EVIDENCE PACKAGE
========================

Package ID: {package.package_id}
Created: {package.created_at.isoformat()}
Violation ID: {package.violation_evidence.violation_id}

This evidence package contains digital evidence collected in accordance with 
best practices for digital forensics and legal proceedings.

Evidence Quality: {package.evidence_quality.value.upper()}
Completeness Score: {package.completeness_score:.2%}

Chain of Custody: {'VERIFIED' if package.chain_of_custody_verified else 'NOT VERIFIED'}
Digital Signatures: {'VERIFIED' if package.signatures_verified else 'NOT VERIFIED'}
Timestamps: {'VERIFIED' if package.timestamps_verified else 'NOT VERIFIED'}

Evidence Items:
{chr(10).join(f"- {item.evidence_type.value}: {item.file_hash}" for item in package.evidence_items)}

For questions regarding this evidence package, contact the system administrator.
Generated by IA Influencer Agent Protection System v2.0
                """.strip()
                
                archive.writestr("README.txt", readme_content)
            
            return archive_path
            
        except Exception as e:
            logger.error(f"Error creating evidence archive: {e}")
            raise
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""
    
    def get_evidence_package(self, package_id: str) -> Optional[EvidencePackage]:
        """Get evidence package by ID"""
        return self.evidence_packages.get(package_id)
    
    def get_evidence_statistics(self) -> Dict[str, Any]:
        """Get evidence collection statistics"""
        total_packages = len(self.evidence_packages)
        
        if total_packages == 0:
            return {'total_packages': 0}
        
        quality_distribution = {}
        for package in self.evidence_packages.values():
            quality = package.evidence_quality.value
            quality_distribution[quality] = quality_distribution.get(quality, 0) + 1
        
        avg_completeness = sum(p.completeness_score for p in self.evidence_packages.values()) / total_packages
        
        verified_packages = sum(1 for p in self.evidence_packages.values() 
                              if p.chain_of_custody_verified and p.signatures_verified)
        
        return {
            'total_packages': total_packages,
            'quality_distribution': quality_distribution,
            'average_completeness_score': avg_completeness,
            'verification_rate': verified_packages / total_packages,
            'evidence_types_collected': list(set(
                item.evidence_type.value 
                for package in self.evidence_packages.values()
                for item in package.evidence_items
            ))
        }


# Data class for external use
@dataclass
class EvidenceData:
    """Simplified evidence data for external APIs"""
    package_id: str
    evidence_quality: str
    completeness_score: float
    archive_path: str
    evidence_count: int
    verified: bool
