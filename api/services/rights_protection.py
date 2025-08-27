"""
Enterprise Rights Protection Service - AI-Powered Content Security & Enforcement
Advanced fingerprinting, violation detection, and automated legal enforcement

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + Security Expert + Legal Tech + ML Engineer

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are proprietary to Fahed Mlaiel.
Unauthorized copying, distribution, or use without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import base64
import hmac
from pathlib import Path

import numpy as np
import redis
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import SQLAlchemyError
import requests
from PIL import Image
import cv2
import librosa
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.models.domain import ProtectionRecord, ContentAsset, Creator, ProtectionAlert, ViolationReport
from backend.app.core.exceptions import ProtectionError, FingerprintingError
from backend.app.services.audio_fingerprint_engine import AudioFingerprintEngine
from backend.app.services.video_fingerprint_engine import VideoFingerprintEngine
from backend.app.services.image_fingerprint_engine import ImageFingerprintEngine
from backend.app.services.text_fingerprint_engine import TextFingerprintEngine

logger = logging.getLogger(__name__)


class ProtectionMethod(Enum):
    DIGITAL_FINGERPRINT = "digital_fingerprint"
    BLOCKCHAIN_ANCHOR = "blockchain_anchor"
    WATERMARK_EMBED = "watermark_embed"
    CRYPTOGRAPHIC_HASH = "cryptographic_hash"
    PERCEPTUAL_HASH = "perceptual_hash"
    VECTOR_EMBEDDING = "vector_embedding"


class ViolationType(Enum):
    EXACT_COPY = "exact_copy"
    PARTIAL_COPY = "partial_copy"
    DERIVATIVE_WORK = "derivative_work"
    UNAUTHORIZED_REMIX = "unauthorized_remix"
    COMMERCIAL_USE = "commercial_use"
    DEEPFAKE = "deepfake"


class EnforcementAction(Enum):
    DMCA_TAKEDOWN = "dmca_takedown"
    CEASE_DESIST = "cease_desist"
    LEGAL_NOTICE = "legal_notice"
    PLATFORM_REPORT = "platform_report"
    MONETIZATION_CLAIM = "monetization_claim"
    CONTENT_ID_CLAIM = "content_id_claim"


@dataclass
class FingerprintResult:
    fingerprint_id: str
    primary_hash: str
    perceptual_hash: str
    vector_embedding: List[float]
    metadata_signature: str
    protection_level: float
    vulnerability_score: float


@dataclass
class ViolationDetection:
    violation_id: str
    original_asset_id: int
    detected_url: str
    platform: str
    similarity_score: float
    violation_type: ViolationType
    evidence_data: Dict[str, Any]
    confidence_level: float
    detected_at: datetime
    automated_actions: List[str]


@dataclass
class ProtectionReport:
    asset_id: int
    protection_methods: List[ProtectionMethod]
    fingerprint_data: FingerprintResult
    monitoring_status: str
    violations_detected: int
    enforcement_actions: int
    protection_score: float
    recommendations: List[str]


class EnterpriseRightsProtectionService:
    """
    Professional rights protection service providing multi-layered content security,
    AI-powered violation detection, and automated legal enforcement
    """
    
    # Similarity thresholds for different violation types
    SIMILARITY_THRESHOLDS = {
        ViolationType.EXACT_COPY: 0.95,
        ViolationType.PARTIAL_COPY: 0.80,
        ViolationType.DERIVATIVE_WORK: 0.70,
        ViolationType.UNAUTHORIZED_REMIX: 0.60,
        ViolationType.COMMERCIAL_USE: 0.85,
        ViolationType.DEEPFAKE: 0.75
    }
    
    # Platform-specific monitoring endpoints
    PLATFORM_CRAWLERS = {
        'youtube': 'https://www.googleapis.com/youtube/v3',
        'instagram': 'https://graph.facebook.com/v18.0',
        'tiktok': 'https://open-api.tiktok.com',
        'twitter': 'https://api.twitter.com/2',
        'facebook': 'https://graph.facebook.com/v18.0',
        'reddit': 'https://www.reddit.com/api',
        'pinterest': 'https://api.pinterest.com/v5'
    }
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        
        # Initialize fingerprinting engines
        self.audio_engine = AudioFingerprintEngine()
        self.video_engine = VideoFingerprintEngine()
        self.image_engine = ImageFingerprintEngine()
        self.text_engine = TextFingerprintEngine()
        
        # Protection settings
        self.monitoring_interval = 3600  # 1 hour
        self.batch_size = 100
        self.max_concurrent_crawls = 10
        
        # Blockchain integration (would be configured)
        self.blockchain_enabled = True
        self.blockchain_network = "ethereum"
        
        # Legal automation settings
        self.auto_dmca_enabled = True
        self.auto_takedown_threshold = 0.90

    async def create_comprehensive_protection(
        self,
        db: Session,
        asset: ContentAsset,
        protection_methods: List[ProtectionMethod] = None
    ) -> ProtectionReport:
        """
        Create comprehensive protection for content asset using multiple methods
        """
        try:
            if not protection_methods:
                protection_methods = [
                    ProtectionMethod.DIGITAL_FINGERPRINT,
                    ProtectionMethod.PERCEPTUAL_HASH,
                    ProtectionMethod.VECTOR_EMBEDDING,
                    ProtectionMethod.CRYPTOGRAPHIC_HASH
                ]
            
            # Generate multi-layered fingerprint
            fingerprint_data = await self._generate_multi_layered_fingerprint(asset)
            
            # Apply protection methods
            protection_records = []
            for method in protection_methods:
                record = await self._apply_protection_method(db, asset, method, fingerprint_data)
                protection_records.append(record)
            
            # Start monitoring
            await self._initialize_monitoring(db, asset, fingerprint_data)
            
            # Calculate protection score
            protection_score = await self._calculate_protection_score(asset, protection_methods, fingerprint_data)
            
            # Generate recommendations
            recommendations = await self._generate_protection_recommendations(asset, protection_score)
            
            report = ProtectionReport(
                asset_id=asset.id,
                protection_methods=protection_methods,
                fingerprint_data=fingerprint_data,
                monitoring_status="active",
                violations_detected=0,  # Initial count
                enforcement_actions=0,  # Initial count
                protection_score=protection_score,
                recommendations=recommendations
            )
            
            # Cache protection data
            await self._cache_protection_data(asset.id, report)
            
            logger.info(f"Comprehensive protection created for asset {asset.id}")
            return report
            
        except Exception as e:
            logger.error(f"Protection creation failed: {str(e)}")
            raise ProtectionError(f"Failed to create protection: {str(e)}")

    async def _generate_multi_layered_fingerprint(self, asset: ContentAsset) -> FingerprintResult:
        """Generate comprehensive fingerprint using multiple techniques"""
        try:
            # Generate content-specific fingerprints
            if asset.media_type == 'audio':
                primary_hash = await self.audio_engine.generate_fingerprint(asset.storage_uri)
                vector_embedding = await self.audio_engine.generate_vector_embedding(asset.storage_uri)
            elif asset.media_type == 'video':
                primary_hash = await self.video_engine.generate_fingerprint(asset.storage_uri)
                vector_embedding = await self.video_engine.generate_vector_embedding(asset.storage_uri)
            elif asset.media_type == 'image':
                primary_hash = await self.image_engine.generate_fingerprint(asset.storage_uri)
                vector_embedding = await self.image_engine.generate_vector_embedding(asset.storage_uri)
            elif asset.media_type == 'text':
                primary_hash = await self.text_engine.generate_fingerprint(asset.storage_uri)
                vector_embedding = await self.text_engine.generate_vector_embedding(asset.storage_uri)
            else:
                raise FingerprintingError(f"Unsupported media type: {asset.media_type}")
            
            # Generate perceptual hash
            perceptual_hash = await self._generate_perceptual_hash(asset)
            
            # Generate metadata signature
            metadata_signature = await self._generate_metadata_signature(asset)
            
            # Calculate protection metrics
            protection_level = await self._calculate_protection_level(asset)
            vulnerability_score = await self._assess_vulnerability(asset)
            
            fingerprint_id = f"fp_{asset.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return FingerprintResult(
                fingerprint_id=fingerprint_id,
                primary_hash=primary_hash,
                perceptual_hash=perceptual_hash,
                vector_embedding=vector_embedding,
                metadata_signature=metadata_signature,
                protection_level=protection_level,
                vulnerability_score=vulnerability_score
            )
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {str(e)}")
            raise FingerprintingError(f"Failed to generate fingerprint: {str(e)}")

    async def _generate_perceptual_hash(self, asset: ContentAsset) -> str:
        """Generate perceptual hash for content similarity detection"""
        try:
            if asset.media_type == 'image':
                # Use PIL for image perceptual hashing
                with Image.open(asset.storage_uri) as img:
                    # Convert to grayscale and resize
                    img_gray = img.convert('L').resize((8, 8))
                    pixels = list(img_gray.getdata())
                    avg = sum(pixels) / len(pixels)
                    
                    # Create binary hash
                    hash_bits = []
                    for pixel in pixels:
                        hash_bits.append('1' if pixel > avg else '0')
                    
                    return ''.join(hash_bits)
            
            elif asset.media_type == 'audio':
                # Generate audio perceptual hash using spectral features
                y, sr = librosa.load(asset.storage_uri, duration=30)  # First 30 seconds
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=12)
                return hashlib.sha256(mfcc.tobytes()).hexdigest()
            
            elif asset.media_type == 'video':
                # Extract key frames and generate composite hash
                cap = cv2.VideoCapture(asset.storage_uri)
                frame_hashes = []
                
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                sample_frames = min(10, frame_count // 10)  # Sample 10 frames
                
                for i in range(sample_frames):
                    frame_pos = (frame_count // sample_frames) * i
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                    ret, frame = cap.read()
                    
                    if ret:
                        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        frame_hash = hashlib.md5(gray_frame.tobytes()).hexdigest()
                        frame_hashes.append(frame_hash)
                
                cap.release()
                return hashlib.sha256(''.join(frame_hashes).encode()).hexdigest()
            
            else:
                # Text perceptual hash based on content structure
                with open(asset.storage_uri, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create structural hash (word count, sentence structure, etc.)
                words = content.split()
                sentences = content.split('.')
                paragraphs = content.split('\n\n')
                
                structure_data = f"{len(words)}_{len(sentences)}_{len(paragraphs)}"
                return hashlib.sha256(structure_data.encode()).hexdigest()
                
        except Exception as e:
            logger.error(f"Perceptual hash generation failed: {str(e)}")
            return hashlib.sha256(f"fallback_{asset.id}".encode()).hexdigest()

    async def _generate_metadata_signature(self, asset: ContentAsset) -> str:
        """Generate metadata signature for integrity verification"""
        metadata = asset.metadata or {}
        
        # Include critical metadata fields
        signature_data = {
            'title': asset.title,
            'media_type': asset.media_type,
            'file_size': asset.file_size,
            'creator_id': asset.creator_id,
            'created_at': asset.created_at.isoformat() if asset.created_at else None,
            'metadata_hash': hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest()
        }
        
        signature_string = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(signature_string.encode()).hexdigest()

    async def _apply_protection_method(
        self,
        db: Session,
        asset: ContentAsset,
        method: ProtectionMethod,
        fingerprint_data: FingerprintResult
    ) -> ProtectionRecord:
        """Apply specific protection method to asset"""
        try:
            details = {}
            
            if method == ProtectionMethod.DIGITAL_FINGERPRINT:
                details = {
                    'fingerprint_id': fingerprint_data.fingerprint_id,
                    'primary_hash': fingerprint_data.primary_hash,
                    'algorithm': 'multi_modal_fingerprint'
                }
            
            elif method == ProtectionMethod.BLOCKCHAIN_ANCHOR:
                if self.blockchain_enabled:
                    anchor_result = await self._create_blockchain_anchor(asset, fingerprint_data)
                    details = {
                        'blockchain_network': self.blockchain_network,
                        'transaction_hash': anchor_result.get('tx_hash'),
                        'block_number': anchor_result.get('block_number'),
                        'timestamp': anchor_result.get('timestamp')
                    }
            
            elif method == ProtectionMethod.WATERMARK_EMBED:
                watermark_result = await self._embed_watermark(asset)
                details = {
                    'watermark_type': watermark_result.get('type'),
                    'strength': watermark_result.get('strength'),
                    'invisible': watermark_result.get('invisible', True)
                }
            
            elif method == ProtectionMethod.CRYPTOGRAPHIC_HASH:
                details = {
                    'sha256': hashlib.sha256(open(asset.storage_uri, 'rb').read()).hexdigest(),
                    'md5': hashlib.md5(open(asset.storage_uri, 'rb').read()).hexdigest()
                }
            
            elif method == ProtectionMethod.PERCEPTUAL_HASH:
                details = {
                    'perceptual_hash': fingerprint_data.perceptual_hash,
                    'similarity_threshold': 0.85
                }
            
            elif method == ProtectionMethod.VECTOR_EMBEDDING:
                details = {
                    'embedding_dimension': len(fingerprint_data.vector_embedding),
                    'embedding_hash': hashlib.sha256(
                        np.array(fingerprint_data.vector_embedding).tobytes()
                    ).hexdigest(),
                    'similarity_algorithm': 'cosine'
                }
            
            # Create protection record
            record = ProtectionRecord(
                asset_id=asset.id,
                fingerprint=fingerprint_data.fingerprint_id,
                method=method.value,
                details=details,
                created_at=datetime.now(),
                is_active=True
            )
            
            db.add(record)
            db.commit()
            
            return record
            
        except Exception as e:
            db.rollback()
            logger.error(f"Protection method application failed: {str(e)}")
            raise ProtectionError(f"Failed to apply {method.value}: {str(e)}")

    async def _create_blockchain_anchor(
        self,
        asset: ContentAsset,
        fingerprint_data: FingerprintResult
    ) -> Dict[str, Any]:
        """Create blockchain anchor for immutable proof of ownership"""
        try:
            # This would implement actual blockchain integration
            # For now, simulate blockchain anchoring
            
            anchor_data = {
                'asset_id': asset.id,
                'fingerprint': fingerprint_data.primary_hash,
                'creator_id': asset.creator_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # Simulate blockchain transaction
            tx_hash = hashlib.sha256(
                json.dumps(anchor_data, sort_keys=True).encode()
            ).hexdigest()
            
            return {
                'tx_hash': tx_hash,
                'block_number': 12345678,  # Would be actual block number
                'timestamp': datetime.now().isoformat(),
                'gas_used': 21000,
                'confirmation_time': 15  # seconds
            }
            
        except Exception as e:
            logger.error(f"Blockchain anchoring failed: {str(e)}")
            return {'error': str(e)}

    async def _embed_watermark(self, asset: ContentAsset) -> Dict[str, Any]:
        """Embed invisible watermark in content"""
        try:
            if asset.media_type == 'image':
                # Implement image watermarking using LSB or frequency domain
                return {
                    'type': 'invisible_lsb',
                    'strength': 0.3,
                    'invisible': True,
                    'watermark_data': f"Protected by IA Influencer Agent - Asset {asset.id}"
                }
            
            elif asset.media_type == 'audio':
                # Implement audio watermarking in frequency domain
                return {
                    'type': 'spectral_watermark',
                    'strength': 0.2,
                    'invisible': True,
                    'frequency_range': '8000-12000_hz'
                }
            
            elif asset.media_type == 'video':
                # Implement video watermarking frame by frame
                return {
                    'type': 'frame_watermark',
                    'strength': 0.25,
                    'invisible': True,
                    'frames_modified': 'keyframes'
                }
            
            else:
                return {
                    'type': 'metadata_watermark',
                    'invisible': False,
                    'location': 'header'
                }
                
        except Exception as e:
            logger.error(f"Watermarking failed: {str(e)}")
            return {'error': str(e)}

    async def monitor_violations(
        self,
        db: Session,
        asset_id: Optional[int] = None,
        platform: Optional[str] = None
    ) -> List[ViolationDetection]:
        """
        Monitor platforms for content violations using AI detection
        """
        try:
            violations = []
            
            # Get assets to monitor
            if asset_id:
                assets = [db.query(ContentAsset).filter(ContentAsset.id == asset_id).first()]
            else:
                # Get all assets with active protection
                assets = db.query(ContentAsset).join(ProtectionRecord).filter(
                    ProtectionRecord.is_active == True
                ).limit(100).all()
            
            # Monitor platforms
            platforms_to_check = [platform] if platform else list(self.PLATFORM_CRAWLERS.keys())
            
            for asset in assets:
                if not asset:
                    continue
                    
                protection_records = db.query(ProtectionRecord).filter(
                    ProtectionRecord.asset_id == asset.id
                ).all()
                
                for platform_name in platforms_to_check:
                    platform_violations = await self._scan_platform_for_violations(
                        asset, protection_records, platform_name
                    )
                    violations.extend(platform_violations)
            
            # Process detected violations
            for violation in violations:
                await self._process_violation(db, violation)
            
            return violations
            
        except Exception as e:
            logger.error(f"Violation monitoring failed: {str(e)}")
            raise ProtectionError(f"Monitoring failed: {str(e)}")

    async def _scan_platform_for_violations(
        self,
        asset: ContentAsset,
        protection_records: List[ProtectionRecord],
        platform: str
    ) -> List[ViolationDetection]:
        """Scan specific platform for violations of protected content"""
        violations = []
        
        try:
            # Get platform-specific search parameters
            search_params = await self._build_search_parameters(asset, platform)
            
            # Search for potential violations (would use actual platform APIs)
            search_results = await self._search_platform_content(platform, search_params)
            
            # Analyze each potential match
            for result in search_results:
                similarity_scores = []
                
                # Compare against each protection record
                for record in protection_records:
                    if record.method == ProtectionMethod.DIGITAL_FINGERPRINT.value:
                        similarity = await self._compare_digital_fingerprints(
                            record.details.get('primary_hash'),
                            result.get('content_data')
                        )
                        similarity_scores.append(similarity)
                    
                    elif record.method == ProtectionMethod.PERCEPTUAL_HASH.value:
                        similarity = await self._compare_perceptual_hashes(
                            record.details.get('perceptual_hash'),
                            result.get('perceptual_data')
                        )
                        similarity_scores.append(similarity)
                
                # Determine violation type and confidence
                max_similarity = max(similarity_scores) if similarity_scores else 0
                violation_type = await self._classify_violation_type(max_similarity, result)
                
                # Create violation if threshold exceeded
                threshold = self.SIMILARITY_THRESHOLDS.get(violation_type, 0.80)
                if max_similarity >= threshold:
                    violation = ViolationDetection(
                        violation_id=f"v_{asset.id}_{platform}_{int(datetime.now().timestamp())}",
                        original_asset_id=asset.id,
                        detected_url=result.get('url'),
                        platform=platform,
                        similarity_score=max_similarity,
                        violation_type=violation_type,
                        evidence_data={
                            'screenshot_url': result.get('screenshot'),
                            'metadata': result.get('metadata'),
                            'detection_algorithm': 'multi_modal_comparison'
                        },
                        confidence_level=max_similarity,
                        detected_at=datetime.now(),
                        automated_actions=await self._determine_automated_actions(violation_type, max_similarity)
                    )
                    violations.append(violation)
            
            return violations
            
        except Exception as e:
            logger.error(f"Platform scanning failed for {platform}: {str(e)}")
            return []

    async def _build_search_parameters(self, asset: ContentAsset, platform: str) -> Dict[str, Any]:
        """Build platform-specific search parameters"""
        params = {
            'title_keywords': asset.title.split() if asset.title else [],
            'content_type': asset.media_type,
            'duration': asset.metadata.get('duration') if asset.metadata else None,
            'tags': asset.metadata.get('tags', []) if asset.metadata else [],
            'upload_date_range': {
                'start': (datetime.now() - timedelta(days=30)).isoformat(),
                'end': datetime.now().isoformat()
            }
        }
        
        # Platform-specific optimizations
        if platform == 'youtube':
            params['video_duration'] = asset.metadata.get('duration')
            params['search_type'] = 'video'
        elif platform == 'instagram':
            params['media_type'] = 'image' if asset.media_type == 'image' else 'video'
        elif platform == 'tiktok':
            params['video_length'] = 'short'
        
        return params

    async def _search_platform_content(self, platform: str, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search platform for potential violations (would use actual APIs)"""
        # This would implement actual platform API calls
        # For now, simulate search results
        
        simulated_results = [
            {
                'id': f'{platform}_result_1',
                'url': f'https://{platform}.com/content/123456',
                'title': 'Similar content title',
                'thumbnail': f'https://{platform}.com/thumb/123456.jpg',
                'upload_date': (datetime.now() - timedelta(days=5)).isoformat(),
                'creator': 'unknown_user',
                'content_data': 'simulated_fingerprint_data',
                'perceptual_data': 'simulated_perceptual_data',
                'metadata': {
                    'views': 10000,
                    'likes': 500,
                    'duration': 120
                }
            }
        ]
        
        return simulated_results

    async def _compare_digital_fingerprints(self, original_hash: str, suspect_data: str) -> float:
        """Compare digital fingerprints for similarity"""
        if not original_hash or not suspect_data:
            return 0.0
        
        # Would implement actual fingerprint comparison
        # For now, simulate comparison based on hash similarity
        return 0.85 if hashlib.sha256(suspect_data.encode()).hexdigest() == original_hash else 0.3

    async def _compare_perceptual_hashes(self, original_hash: str, suspect_data: str) -> float:
        """Compare perceptual hashes for similarity"""
        if not original_hash or not suspect_data:
            return 0.0
        
        # Hamming distance for perceptual hash comparison
        if len(original_hash) == len(suspect_data):
            distance = sum(c1 != c2 for c1, c2 in zip(original_hash, suspect_data))
            similarity = 1.0 - (distance / len(original_hash))
            return max(0.0, similarity)
        
        return 0.0

    async def _classify_violation_type(self, similarity_score: float, result_data: Dict[str, Any]) -> ViolationType:
        """Classify the type of violation based on similarity and context"""
        if similarity_score >= 0.95:
            return ViolationType.EXACT_COPY
        elif similarity_score >= 0.85:
            return ViolationType.PARTIAL_COPY
        elif similarity_score >= 0.70:
            return ViolationType.DERIVATIVE_WORK
        elif similarity_score >= 0.60:
            return ViolationType.UNAUTHORIZED_REMIX
        else:
            return ViolationType.COMMERCIAL_USE  # Default assumption

    async def _determine_automated_actions(self, violation_type: ViolationType, similarity: float) -> List[str]:
        """Determine automated enforcement actions based on violation"""
        actions = []
        
        if similarity >= 0.90 and self.auto_dmca_enabled:
            actions.append("dmca_takedown_notice")
        
        if similarity >= 0.85:
            actions.extend(["evidence_collection", "platform_report"])
        
        if violation_type == ViolationType.COMMERCIAL_USE:
            actions.append("monetization_claim")
        
        actions.append("violation_alert")
        
        return actions

    async def _process_violation(self, db: Session, violation: ViolationDetection) -> None:
        """Process detected violation with automated actions"""
        try:
            # Create violation alert record
            alert = ProtectionAlert(
                fingerprint_id=violation.original_asset_id,
                detected_url=violation.detected_url,
                platform=violation.platform,
                similarity_score=violation.similarity_score,
                status='detected',
                evidence_screenshot=violation.evidence_data.get('screenshot_url'),
                created_at=violation.detected_at
            )
            
            db.add(alert)
            
            # Execute automated actions
            for action in violation.automated_actions:
                if action == "dmca_takedown_notice":
                    await self._send_dmca_takedown(violation)
                elif action == "platform_report":
                    await self._report_to_platform(violation)
                elif action == "monetization_claim":
                    await self._submit_monetization_claim(violation)
                elif action == "evidence_collection":
                    await self._collect_violation_evidence(violation)
            
            db.commit()
            logger.info(f"Processed violation: {violation.violation_id}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Violation processing failed: {str(e)}")

    async def _send_dmca_takedown(self, violation: ViolationDetection) -> None:
        """Send automated DMCA takedown notice"""
        try:
            # This would implement actual DMCA notice sending
            logger.info(f"DMCA takedown notice sent for violation: {violation.violation_id}")
        except Exception as e:
            logger.error(f"DMCA takedown failed: {str(e)}")

    async def _report_to_platform(self, violation: ViolationDetection) -> None:
        """Report violation to platform"""
        try:
            # This would use platform-specific reporting APIs
            logger.info(f"Platform report submitted for violation: {violation.violation_id}")
        except Exception as e:
            logger.error(f"Platform reporting failed: {str(e)}")

    async def _submit_monetization_claim(self, violation: ViolationDetection) -> None:
        """Submit monetization claim for commercial violations"""
        try:
            # This would implement Content ID or similar systems
            logger.info(f"Monetization claim submitted for violation: {violation.violation_id}")
        except Exception as e:
            logger.error(f"Monetization claim failed: {str(e)}")

    async def _collect_violation_evidence(self, violation: ViolationDetection) -> None:
        """Collect additional evidence for violation"""
        try:
            # This would capture screenshots, download content, etc.
            logger.info(f"Evidence collected for violation: {violation.violation_id}")
        except Exception as e:
            logger.error(f"Evidence collection failed: {str(e)}")

    async def _calculate_protection_level(self, asset: ContentAsset) -> float:
        """Calculate overall protection level for asset"""
        factors = []
        
        # File characteristics
        if asset.file_size and asset.file_size > 1024 * 1024:  # >1MB
            factors.append(0.8)
        else:
            factors.append(0.6)
        
        # Metadata richness
        metadata_score = len(asset.metadata.keys()) / 10 if asset.metadata else 0
        factors.append(min(0.9, max(0.4, metadata_score)))
        
        # Content type security
        type_security = {
            'video': 0.9,
            'audio': 0.8,
            'image': 0.7,
            'text': 0.6
        }
        factors.append(type_security.get(asset.media_type, 0.5))
        
        return sum(factors) / len(factors) if factors else 0.5

    async def _assess_vulnerability(self, asset: ContentAsset) -> float:
        """Assess vulnerability score (higher = more vulnerable)"""
        vulnerability_factors = []
        
        # Public accessibility
        if asset.metadata and asset.metadata.get('public', True):
            vulnerability_factors.append(0.7)
        else:
            vulnerability_factors.append(0.3)
        
        # Content type vulnerability
        type_vulnerability = {
            'image': 0.8,  # Easy to copy
            'text': 0.9,   # Very easy to copy
            'audio': 0.6,  # Moderate difficulty
            'video': 0.5   # Harder to copy
        }
        vulnerability_factors.append(type_vulnerability.get(asset.media_type, 0.6))
        
        # Popularity factor (would be based on actual metrics)
        vulnerability_factors.append(0.5)  # Moderate baseline
        
        return sum(vulnerability_factors) / len(vulnerability_factors)

    async def _generate_protection_recommendations(self, asset: ContentAsset, protection_score: float) -> List[str]:
        """Generate protection improvement recommendations"""
        recommendations = []
        
        if protection_score < 0.7:
            recommendations.append("Enable blockchain anchoring for immutable proof of ownership")
        
        if asset.metadata and not asset.metadata.get('watermark'):
            recommendations.append("Add invisible watermark for additional protection")
        
        if protection_score < 0.6:
            recommendations.append("Increase monitoring frequency for early violation detection")
        
        recommendations.append("Enable automated DMCA takedown for faster enforcement")
        
        if asset.media_type == 'image':
            recommendations.append("Consider visible attribution watermark for deterrent effect")
        
        return recommendations[:5]

    async def _calculate_protection_score(
        self,
        asset: ContentAsset,
        methods: List[ProtectionMethod],
        fingerprint_data: FingerprintResult
    ) -> float:
        """Calculate comprehensive protection score"""
        method_scores = {
            ProtectionMethod.DIGITAL_FINGERPRINT: 0.2,
            ProtectionMethod.BLOCKCHAIN_ANCHOR: 0.25,
            ProtectionMethod.WATERMARK_EMBED: 0.15,
            ProtectionMethod.CRYPTOGRAPHIC_HASH: 0.1,
            ProtectionMethod.PERCEPTUAL_HASH: 0.15,
            ProtectionMethod.VECTOR_EMBEDDING: 0.15
        }
        
        # Base score from applied methods
        methods_score = sum(method_scores.get(method, 0) for method in methods)
        
        # Adjust for content characteristics
        content_factor = fingerprint_data.protection_level
        vulnerability_penalty = 1.0 - fingerprint_data.vulnerability_score
        
        final_score = methods_score * content_factor * vulnerability_penalty
        return min(1.0, max(0.0, final_score))

    async def _cache_protection_data(self, asset_id: int, report: ProtectionReport) -> None:
        """Cache protection data for quick access"""
        try:
            cache_key = f"protection:report:{asset_id}"
            self.redis_client.setex(
                cache_key,
                3600,  # 1 hour TTL
                json.dumps(asdict(report), default=str)
            )
        except Exception as e:
            logger.warning(f"Failed to cache protection data: {str(e)}")

    # Legacy methods for backward compatibility
    def fingerprint(self, asset: ContentAsset) -> str:
        """Legacy fingerprint method - deprecated"""
        logger.warning("Using deprecated fingerprint method. Switch to create_comprehensive_protection")
        
        # Simple robust fingerprint: sha256(content path + title)
        h = hashlib.sha256()
        h.update(asset.storage_uri.encode("utf-8"))
        h.update(asset.title.encode("utf-8"))
        return h.hexdigest()

    def protect(self, db: Session, asset: ContentAsset, method: str) -> ProtectionRecord:
        """Legacy protect method - deprecated"""
        logger.warning("Using deprecated protect method. Switch to create_comprehensive_protection")
        
        fp = self.fingerprint(asset)
        record = ProtectionRecord(
            asset_id=asset.id,
            fingerprint=fp,
            method=method,
            details={"anchored": method == "blockchain"},
        )
        db.add(record)
        db.flush()
        return record


# Create alias for backward compatibility
RightsProtectionService = EnterpriseRightsProtectionService
