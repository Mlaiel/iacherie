"""
Content Protection & Rights Management System for IA Influencer Agent Platform

Advanced content protection, copyright management, plagiarism detection,
and intellectual property rights enforcement for creator content.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING - Unauthorized use prohibited 
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import hashlib
import hmac
import base64
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
import re
from collections import defaultdict, Counter
import cv2
import imagehash
from PIL import Image
import librosa

logger = logging.getLogger(__name__)


class ContentSecurityLevel(Enum):
    """Security levels for content protection."""
    PUBLIC = "public"
    WATERMARKED = "watermarked"
    ENCRYPTED = "encrypted"
    PREMIUM_PROTECTED = "premium_protected"
    EXCLUSIVE_ACCESS = "exclusive_access"


class ProtectionType(Enum):
    """Types of content protection."""
    TEXT_FINGERPRINTING = "text_fingerprinting"
    IMAGE_WATERMARKING = "image_watermarking"
    AUDIO_FINGERPRINTING = "audio_fingerprinting"
    VIDEO_WATERMARKING = "video_watermarking"
    BLOCKCHAIN_REGISTRY = "blockchain_registry"
    DMCA_PROTECTION = "dmca_protection"
    COPYRIGHT_REGISTRATION = "copyright_registration"


class ThreatLevel(Enum):
    """Threat levels for security assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class ContentFingerprint:
    """Digital fingerprint for content identification."""
    content_id: str
    fingerprint_hash: str
    fingerprint_type: ProtectionType
    content_type: str
    creator_id: str
    metadata: Dict[str, Any]
    creation_timestamp: datetime
    protection_level: ContentSecurityLevel
    verification_signature: str
    blockchain_hash: Optional[str] = None


@dataclass
class SecurityThreat:
    """Security threat detection result."""
    threat_id: str
    threat_type: str
    threat_level: ThreatLevel
    detected_at: datetime
    content_id: str
    source_location: str
    similarity_score: float
    evidence: Dict[str, Any]
    mitigation_actions: List[str]
    status: str = "detected"


@dataclass
class ProtectionReport:
    """Comprehensive content protection report."""
    report_id: str
    content_id: str
    creator_id: str
    protection_status: str
    security_score: float
    active_protections: List[ProtectionType]
    detected_threats: List[SecurityThreat]
    recommendations: List[str]
    compliance_status: Dict[str, str]
    generated_at: datetime = field(default_factory=datetime.now)


class ContentProtectionEngine:
    """
    Advanced content protection and rights management engine.
    
    Provides comprehensive protection for creator content including fingerprinting,
    watermarking, plagiarism detection, and copyright enforcement.
    """
    
    def __init__(self):
        """Initialize the content protection engine."""
        self.fingerprint_database: Dict[str, ContentFingerprint] = {}
        self.threat_database: Dict[str, SecurityThreat] = {}
        self.protection_policies: Dict[str, Dict[str, Any]] = {}
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.content_vectors: Dict[str, np.ndarray] = {}
        
        # Initialize protection algorithms
        self._initialize_protection_algorithms()
        
        # Load protection policies
        self._load_protection_policies()
    
    def _initialize_protection_algorithms(self):
        """Initialize various protection algorithms."""



        try:
            # Text similarity threshold
            self.text_similarity_threshold = 0.85
            
            # Image hashing algorithms
            self.image_hash_algorithms = [
                imagehash.average_hash,
                imagehash.phash,
                imagehash.dhash,
                imagehash.whash
            ]
            
            # Audio fingerprinting parameters
            self.audio_fingerprint_params = {
                'sr': 22050,
                'hop_length': 512,
                'n_mfcc': 13
            }
            
            logger.info("Protection algorithms initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize protection algorithms: {e}")
            raise
    
    def _load_protection_policies(self):
        """Load content protection policies."""



        try:
            self.protection_policies = {
                'text_content': {
                    'min_similarity_for_alert': 0.7,
                    'max_allowed_copies': 3,
                    'dmca_auto_filing': True,
                    'watermark_required': False
                },
                'image_content': {
                    'watermark_required': True,
                    'watermark_opacity': 0.3,
                    'max_allowed_copies': 5,
                    'hash_verification': True
                },
                'audio_content': {
                    'fingerprint_required': True,
                    'streaming_protection': True,
                    'download_protection': True,
                    'max_allowed_clips': 2
                },
                'video_content': {
                    'watermark_required': True,
                    'fingerprint_required': True,
                    'content_id_embedding': True,
                    'platform_protection': True
                }
            }
            
            logger.info("Protection policies loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load protection policies: {e}")
            raise
    
    async def protect_content(
        self, 
        content: Any,
        content_type: str,
        creator_id: str,
        protection_level: ContentSecurityLevel = ContentSecurityLevel.WATERMARKED,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContentFingerprint:
        """
        Apply comprehensive protection to content.
        
        Args:
            content: Content to protect (text, image, audio, video)
            content_type: Type of content
            creator_id: Creator identifier
            protection_level: Level of protection to apply
            metadata: Additional content metadata
            
        Returns:
            ContentFingerprint: Generated content fingerprint
        """



        try:
            content_id = self._generate_content_id(content, creator_id)
            
            # Apply appropriate protection based on content type
            if content_type == 'text':
                fingerprint = await self._protect_text_content(
                    content, content_id, creator_id, protection_level, metadata
                )
            elif content_type == 'image':
                fingerprint = await self._protect_image_content(
                    content, content_id, creator_id, protection_level, metadata
                )
            elif content_type == 'audio':
                fingerprint = await self._protect_audio_content(
                    content, content_id, creator_id, protection_level, metadata
                )
            elif content_type == 'video':
                fingerprint = await self._protect_video_content(
                    content, content_id, creator_id, protection_level, metadata
                )
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Store fingerprint in database
            self.fingerprint_database[content_id] = fingerprint
            
            # Register on blockchain if required
            if protection_level in [ContentSecurityLevel.PREMIUM_PROTECTED, ContentSecurityLevel.EXCLUSIVE_ACCESS]:
                fingerprint.blockchain_hash = await self._register_on_blockchain(fingerprint)
            
            logger.info(f"Content protection applied successfully for {content_id}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Content protection failed: {e}")
            raise
    
    async def _protect_text_content(
        self,
        content: str,
        content_id: str,
        creator_id: str,
        protection_level: ContentSecurityLevel,
        metadata: Optional[Dict[str, Any]]
    ) -> ContentFingerprint:
        """Protect text content with fingerprinting."""



        try:
            # Generate text fingerprint
            fingerprint_hash = self._generate_text_fingerprint(content)
            
            # Create content vector for similarity detection
            content_vector = self.vectorizer.fit_transform([content]).toarray()[0]
            self.content_vectors[content_id] = content_vector
            
            # Generate verification signature
            verification_signature = self._generate_verification_signature(
                content_id, creator_id, fingerprint_hash
            )
            
            # Apply watermarking if required
            if protection_level != ContentSecurityLevel.PUBLIC:
                content = self._add_invisible_text_watermark(content, creator_id)
            
            return ContentFingerprint(
                content_id=content_id,
                fingerprint_hash=fingerprint_hash,
                fingerprint_type=ProtectionType.TEXT_FINGERPRINTING,
                content_type='text',
                creator_id=creator_id,
                metadata=metadata or {},
                creation_timestamp=datetime.now(),
                protection_level=protection_level,
                verification_signature=verification_signature
            )
            
        except Exception as e:
            logger.error(f"Text content protection failed: {e}")
            raise
    
    async def _protect_image_content(
        self,
        content: Any,  # PIL Image or file path
        content_id: str,
        creator_id: str,
        protection_level: ContentSecurityLevel,
        metadata: Optional[Dict[str, Any]]
    ) -> ContentFingerprint:
        """Protect image content with hashing and watermarking."""



        try:
            # Load image if path provided
            if isinstance(content, str):
                image = Image.open(content)
            else:
                image = content
            
            # Generate image fingerprints using multiple algorithms
            fingerprint_hashes = []
            for hash_func in self.image_hash_algorithms:
                img_hash = str(hash_func(image))
                fingerprint_hashes.append(img_hash)
            
            # Combined fingerprint
            combined_hash = hashlib.sha256(''.join(fingerprint_hashes).encode()).hexdigest()
            
            # Apply watermarking if required
            if protection_level != ContentSecurityLevel.PUBLIC:
                watermarked_image = self._add_image_watermark(image, creator_id, protection_level)
                # Save watermarked image back
                if isinstance(content, str):
                    watermarked_image.save(content)
            
            # Generate verification signature
            verification_signature = self._generate_verification_signature(
                content_id, creator_id, combined_hash
            )
            
            return ContentFingerprint(
                content_id=content_id,
                fingerprint_hash=combined_hash,
                fingerprint_type=ProtectionType.IMAGE_WATERMARKING,
                content_type='image',
                creator_id=creator_id,
                metadata=metadata or {},
                creation_timestamp=datetime.now(),
                protection_level=protection_level,
                verification_signature=verification_signature
            )
            
        except Exception as e:
            logger.error(f"Image content protection failed: {e}")
            raise
    
    async def _protect_audio_content(
        self,
        content: Any,  # Audio file path or audio data
        content_id: str,
        creator_id: str,
        protection_level: ContentSecurityLevel,
        metadata: Optional[Dict[str, Any]]
    ) -> ContentFingerprint:
        """Protect audio content with fingerprinting."""



        try:
            # Load audio data
            if isinstance(content, str):
                y, sr = librosa.load(content, sr=self.audio_fingerprint_params['sr'])
            else:
                y, sr = content, self.audio_fingerprint_params['sr']
            
            # Generate audio fingerprint using MFCC features
            mfccs = librosa.feature.mfcc(
                y=y, 
                sr=sr, 
                n_mfcc=self.audio_fingerprint_params['n_mfcc'],
                hop_length=self.audio_fingerprint_params['hop_length']
            )
            
            # Create fingerprint hash from MFCC features
            mfcc_hash = hashlib.sha256(mfccs.tobytes()).hexdigest()
            
            # Generate spectral centroid for additional fingerprinting
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_hash = hashlib.sha256(spectral_centroids.tobytes()).hexdigest()
            
            # Combined fingerprint
            combined_hash = hashlib.sha256((mfcc_hash + spectral_hash).encode()).hexdigest()
            
            # Add inaudible watermark if required
            if protection_level != ContentSecurityLevel.PUBLIC:
                watermarked_audio = self._add_audio_watermark(y, creator_id, sr)
                # Save watermarked audio if file path provided
                if isinstance(content, str):
                    import soundfile as sf
                    sf.write(content, watermarked_audio, sr)
            
            # Generate verification signature
            verification_signature = self._generate_verification_signature(
                content_id, creator_id, combined_hash
            )
            
            return ContentFingerprint(
                content_id=content_id,
                fingerprint_hash=combined_hash,
                fingerprint_type=ProtectionType.AUDIO_FINGERPRINTING,
                content_type='audio',
                creator_id=creator_id,
                metadata=metadata or {},
                creation_timestamp=datetime.now(),
                protection_level=protection_level,
                verification_signature=verification_signature
            )
            
        except Exception as e:
            logger.error(f"Audio content protection failed: {e}")
            raise
    
    async def _protect_video_content(
        self,
        content: Any,  # Video file path or video data
        content_id: str,
        creator_id: str,
        protection_level: ContentSecurityLevel,
        metadata: Optional[Dict[str, Any]]
    ) -> ContentFingerprint:
        """Protect video content with fingerprinting and watermarking."""



        try:
            # Load video
            if isinstance(content, str):
                cap = cv2.VideoCapture(content)
            else:
                cap = content
            
            # Extract key frames for fingerprinting
            frame_hashes = []
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames at regular intervals
            sample_interval = max(1, frame_count // 10)  # Sample 10 frames max
            
            for i in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    # Convert frame to PIL Image for hashing
                    pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    frame_hash = str(imagehash.phash(pil_frame))
                    frame_hashes.append(frame_hash)
            
            cap.release()
            
            # Combined video fingerprint
            combined_hash = hashlib.sha256(''.join(frame_hashes).encode()).hexdigest()
            
            # Add watermark if required
            if protection_level != ContentSecurityLevel.PUBLIC:
                watermarked_video_path = self._add_video_watermark(content, creator_id, protection_level)
            
            # Generate verification signature
            verification_signature = self._generate_verification_signature(
                content_id, creator_id, combined_hash
            )
            
            return ContentFingerprint(
                content_id=content_id,
                fingerprint_hash=combined_hash,
                fingerprint_type=ProtectionType.VIDEO_WATERMARKING,
                content_type='video',
                creator_id=creator_id,
                metadata=metadata or {},
                creation_timestamp=datetime.now(),
                protection_level=protection_level,
                verification_signature=verification_signature
            )
            
        except Exception as e:
            logger.error(f"Video content protection failed: {e}")
            raise
    
    async def detect_content_theft(
        self, 
        suspicious_content: Any,
        content_type: str,
        threshold: Optional[float] = None
    ) -> List[SecurityThreat]:
        """
        Detect potential content theft or unauthorized usage.
        
        Args:
            suspicious_content: Content to analyze for theft
            content_type: Type of content
            threshold: Similarity threshold for detection
            
        Returns:
            List[SecurityThreat]: Detected security threats
        """



        try:
            threats = []
            
            if content_type == 'text':
                threats = await self._detect_text_plagiarism(suspicious_content, threshold)
            elif content_type == 'image':
                threats = await self._detect_image_theft(suspicious_content, threshold)
            elif content_type == 'audio':
                threats = await self._detect_audio_piracy(suspicious_content, threshold)
            elif content_type == 'video':
                threats = await self._detect_video_theft(suspicious_content, threshold)
            
            # Store detected threats
            for threat in threats:
                self.threat_database[threat.threat_id] = threat
            
            return threats
            
        except Exception as e:
            logger.error(f"Content theft detection failed: {e}")
            raise
    
    async def _detect_text_plagiarism(
        self, 
        suspicious_text: str, 
        threshold: Optional[float]
    ) -> List[SecurityThreat]:
        """Detect text plagiarism using similarity analysis."""



        try:
            threats = []
            threshold = threshold or self.text_similarity_threshold
            
            # Create vector for suspicious text
            suspicious_vector = self.vectorizer.transform([suspicious_text]).toarray()[0]
            
            # Compare with all protected content
            for content_id, protected_vector in self.content_vectors.items():
                similarity = cosine_similarity([suspicious_vector], [protected_vector])[0][0]
                
                if similarity >= threshold:
                    fingerprint = self.fingerprint_database.get(content_id)
                    if fingerprint:
                        threat = SecurityThreat(
                            threat_id=f"text_threat_{content_id}_{int(datetime.now().timestamp())}",
                            threat_type="text_plagiarism",
                            threat_level=self._assess_threat_level(similarity),
                            detected_at=datetime.now(),
                            content_id=content_id,
                            source_location="unknown",
                            similarity_score=similarity,
                            evidence={
                                'original_content': content_id,
                                'similarity_score': similarity,
                                'detection_method': 'cosine_similarity'
                            },
                            mitigation_actions=[
                                "File DMCA takedown notice",
                                "Contact platform administrators",
                                "Document evidence for legal action",
                                "Notify content creator"
                            ]
                        )
                        threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Text plagiarism detection failed: {e}")
            return []
    
    async def _detect_image_theft(
        self, 
        suspicious_image: Any, 
        threshold: Optional[float]
    ) -> List[SecurityThreat]:
        """Detect image theft using perceptual hashing."""



        try:
            threats = []
            threshold = threshold or 10  # Hamming distance threshold
            
            # Load suspicious image
            if isinstance(suspicious_image, str):
                image = Image.open(suspicious_image)
            else:
                image = suspicious_image
            
            # Generate hashes for suspicious image
            suspicious_hashes = []
            for hash_func in self.image_hash_algorithms:
                img_hash = hash_func(image)
                suspicious_hashes.append(img_hash)
            
            # Compare with protected images
            for content_id, fingerprint in self.fingerprint_database.items():
                if fingerprint.fingerprint_type == ProtectionType.IMAGE_WATERMARKING:
                    # Compare hashes (simplified - in reality, we'd need stored hash components)
                    similarity_score = self._calculate_image_similarity(suspicious_hashes, fingerprint)
                    
                    if similarity_score >= threshold:
                        threat = SecurityThreat(
                            threat_id=f"image_theft_{content_id}_{int(datetime.now().timestamp())}",
                            threat_type="image_theft",
                            threat_level=self._assess_threat_level(similarity_score / 100),
                            detected_at=datetime.now(),
                            content_id=content_id,
                            source_location="unknown",
                            similarity_score=similarity_score / 100,
                            evidence={
                                'hash_similarity': similarity_score,
                                'detection_method': 'perceptual_hashing'
                            },
                            mitigation_actions=[
                                "File copyright infringement claim",
                                "Request image takedown",
                                "Contact hosting provider",
                                "Document evidence"
                            ]
                        )
                        threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Image theft detection failed: {e}")
            return []
    
    async def _detect_audio_piracy(
        self, 
        suspicious_audio: Any, 
        threshold: Optional[float]
    ) -> List[SecurityThreat]:
        """Detect audio piracy using acoustic fingerprinting."""



        try:
            threats = []
            threshold = threshold or 0.8
            
            # Load suspicious audio
            if isinstance(suspicious_audio, str):
                y, sr = librosa.load(suspicious_audio, sr=self.audio_fingerprint_params['sr'])
            else:
                y, sr = suspicious_audio, self.audio_fingerprint_params['sr']
            
            # Generate fingerprint for suspicious audio
            mfccs = librosa.feature.mfcc(
                y=y, 
                sr=sr, 
                n_mfcc=self.audio_fingerprint_params['n_mfcc']
            )
            
            # Compare with protected audio fingerprints
            for content_id, fingerprint in self.fingerprint_database.items():
                if fingerprint.fingerprint_type == ProtectionType.AUDIO_FINGERPRINTING:
                    # In a real implementation, we'd compare MFCC features
                    similarity_score = self._calculate_audio_similarity(mfccs, fingerprint)
                    
                    if similarity_score >= threshold:
                        threat = SecurityThreat(
                            threat_id=f"audio_piracy_{content_id}_{int(datetime.now().timestamp())}",
                            threat_type="audio_piracy",
                            threat_level=self._assess_threat_level(similarity_score),
                            detected_at=datetime.now(),
                            content_id=content_id,
                            source_location="unknown",
                            similarity_score=similarity_score,
                            evidence={
                                'acoustic_similarity': similarity_score,
                                'detection_method': 'mfcc_comparison'
                            },
                            mitigation_actions=[
                                "File copyright strike",
                                "Contact streaming platforms",
                                "Report to collection societies",
                                "Legal action if commercial use"
                            ]
                        )
                        threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Audio piracy detection failed: {e}")
            return []
    
    async def _detect_video_theft(
        self, 
        suspicious_video: Any, 
        threshold: Optional[float]
    ) -> List[SecurityThreat]:
        """Detect video theft using frame-based comparison."""



        try:
            threats = []
            threshold = threshold or 0.85
            
            # Extract frames from suspicious video
            if isinstance(suspicious_video, str):
                cap = cv2.VideoCapture(suspicious_video)
            else:
                cap = suspicious_video
            
            suspicious_frame_hashes = []
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, frame_count // 10)
            
            for i in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    frame_hash = str(imagehash.phash(pil_frame))
                    suspicious_frame_hashes.append(frame_hash)
            
            cap.release()
            
            # Compare with protected videos
            for content_id, fingerprint in self.fingerprint_database.items():
                if fingerprint.fingerprint_type == ProtectionType.VIDEO_WATERMARKING:
                    similarity_score = self._calculate_video_similarity(suspicious_frame_hashes, fingerprint)
                    
                    if similarity_score >= threshold:
                        threat = SecurityThreat(
                            threat_id=f"video_theft_{content_id}_{int(datetime.now().timestamp())}",
                            threat_type="video_theft",
                            threat_level=self._assess_threat_level(similarity_score),
                            detected_at=datetime.now(),
                            content_id=content_id,
                            source_location="unknown",
                            similarity_score=similarity_score,
                            evidence={
                                'frame_similarity': similarity_score,
                                'detection_method': 'frame_hashing'
                            },
                            mitigation_actions=[
                                "File video copyright claim",
                                "Contact video platforms",
                                "Request immediate takedown",
                                "Gather evidence for legal action"
                            ]
                        )
                        threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Video theft detection failed: {e}")
            return []
    
    async def generate_protection_report(
        self, 
        content_id: str, 
        creator_id: str
    ) -> ProtectionReport:
        """Generate comprehensive protection report for content."""



        try:
            # Get content fingerprint
            fingerprint = self.fingerprint_database.get(content_id)
            if not fingerprint:
                raise ValueError(f"No protection data found for content {content_id}")
            
            # Get related threats
            content_threats = [
                threat for threat in self.threat_database.values()
                if threat.content_id == content_id
            ]
            
            # Calculate security score
            security_score = self._calculate_security_score(fingerprint, content_threats)
            
            # Determine protection status
            protection_status = self._determine_protection_status(fingerprint, content_threats)
            
            # Generate recommendations
            recommendations = self._generate_protection_recommendations(fingerprint, content_threats)
            
            # Check compliance status
            compliance_status = self._check_compliance_status(fingerprint)
            
            report_id = f"protection_report_{content_id}_{int(datetime.now().timestamp())}"
            
            return ProtectionReport(
                report_id=report_id,
                content_id=content_id,
                creator_id=creator_id,
                protection_status=protection_status,
                security_score=security_score,
                active_protections=[fingerprint.fingerprint_type],
                detected_threats=content_threats,
                recommendations=recommendations,
                compliance_status=compliance_status
            )
            
        except Exception as e:
            logger.error(f"Protection report generation failed: {e}")
            raise
    
    def _generate_content_id(self, content: Any, creator_id: str) -> str:
        """Generate unique content identifier."""



        try:
            content_str = str(content)[:1000]  # Limit for hashing
            timestamp = str(int(datetime.now().timestamp()))
            combined = f"{creator_id}_{content_str}_{timestamp}"
            return hashlib.sha256(combined.encode()).hexdigest()[:16]
            
        except Exception as e:
            logger.error(f"Content ID generation failed: {e}")
            return f"content_{int(datetime.now().timestamp())}"
    
    def _generate_text_fingerprint(self, content: str) -> str:
        """Generate fingerprint for text content."""



        try:
            # Normalize text
            normalized = re.sub(r'\s+', ' ', content.lower().strip())
            
            # Create fingerprint using multiple methods
            sha256_hash = hashlib.sha256(normalized.encode()).hexdigest()
            
            # Add shingling for n-gram based fingerprinting
            shingles = [normalized[i:i+5] for i in range(len(normalized)-4)]
            shingle_hash = hashlib.md5(''.join(shingles).encode()).hexdigest()
            
            return f"{sha256_hash[:16]}_{shingle_hash[:16]}"
            
        except Exception as e:
            logger.error(f"Text fingerprint generation failed: {e}")
            return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    def _generate_verification_signature(self, content_id: str, creator_id: str, fingerprint_hash: str) -> str:
        """Generate verification signature for content authenticity."""



        try:
            # Create signature using HMAC
            secret_key = f"ia_influencer_agent_{creator_id}".encode()
            message = f"{content_id}_{fingerprint_hash}_{datetime.now().isoformat()}".encode()
            signature = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
            return signature
            
        except Exception as e:
            logger.error(f"Verification signature generation failed: {e}")
            return hashlib.sha256(f"{content_id}_{creator_id}".encode()).hexdigest()
    
    def _add_invisible_text_watermark(self, content: str, creator_id: str) -> str:
        """Add invisible watermark to text content."""



        try:
            # Use zero-width characters as invisible watermark
            watermark_chars = ['\u200B', '\u200C', '\u200D', '\uFEFF']  # Zero-width characters
            
            # Encode creator_id into binary
            creator_binary = ''.join(format(ord(char), '08b') for char in creator_id[:8])
            
            # Add watermark characters based on binary
            watermarked_content = ""
            binary_index = 0
            
            for i, char in enumerate(content):
                watermarked_content += char
                
                # Add watermark character based on binary bit
                if binary_index < len(creator_binary) and i % 10 == 0:
                    bit = creator_binary[binary_index]
                    watermark_char = watermark_chars[int(bit) * 2]
                    watermarked_content += watermark_char
                    binary_index += 1
            
            return watermarked_content
            
        except Exception as e:
            logger.error(f"Text watermark addition failed: {e}")
            return content
    
    def _add_image_watermark(self, image: Image.Image, creator_id: str, protection_level: ContentSecurityLevel) -> Image.Image:
        """Add watermark to image content."""



        try:
            from PIL import ImageDraw, ImageFont
            
            # Create a copy of the original image
            watermarked = image.copy()
            
            # Create drawing context
            draw = ImageDraw.Draw(watermarked)
            
            # Watermark text
            watermark_text = f"© {creator_id} - IA Influencer Agent"
            
            # Get image dimensions
            width, height = watermarked.size
            
            # Try to load a font, fallback to default if not available
            try:
                font_size = max(width, height) // 40
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Get text dimensions
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Position watermark
            if protection_level == ContentSecurityLevel.WATERMARKED:
                # Bottom right corner
                x = width - text_width - 10
                y = height - text_height - 10
                opacity = 128
            elif protection_level == ContentSecurityLevel.PREMIUM_PROTECTED:
                # Center of image
                x = (width - text_width) // 2
                y = (height - text_height) // 2
                opacity = 100
            else:
                # Multiple watermarks for exclusive access
                positions = [
                    (10, 10),  # Top left
                    (width - text_width - 10, 10),  # Top right
                    (10, height - text_height - 10),  # Bottom left
                    (width - text_width - 10, height - text_height - 10)  # Bottom right
                ]
                opacity = 150
                
                for pos_x, pos_y in positions:
                    draw.text((pos_x, pos_y), watermark_text, fill=(255, 255, 255, opacity), font=font)
                
                return watermarked
            
            # Add single watermark
            draw.text((x, y), watermark_text, fill=(255, 255, 255, opacity), font=font)
            
            return watermarked
            
        except Exception as e:
            logger.error(f"Image watermark addition failed: {e}")
            return image
    
    def _add_audio_watermark(self, audio_data: np.ndarray, creator_id: str, sample_rate: int) -> np.ndarray:
        """Add inaudible watermark to audio content."""



        try:
            # Create a copy of audio data
            watermarked = audio_data.copy()
            
            # Generate watermark signal (high frequency, low amplitude)
            watermark_freq = 15000  # 15kHz - mostly inaudible
            watermark_amplitude = 0.001  # Very low amplitude
            
            # Create watermark signal
            duration = len(audio_data) / sample_rate
            t = np.linspace(0, duration, len(audio_data))
            
            # Encode creator_id as frequency modulation
            creator_hash = hashlib.md5(creator_id.encode()).hexdigest()[:8]
            freq_offset = int(creator_hash, 16) % 1000  # Frequency offset
            
            watermark_signal = watermark_amplitude * np.sin(2 * np.pi * (watermark_freq + freq_offset) * t)
            
            # Add watermark to audio
            watermarked += watermark_signal
            
            # Ensure audio doesn't clip
            max_val = np.max(np.abs(watermarked))
            if max_val > 1.0:
                watermarked = watermarked / max_val
            
            return watermarked
            
        except Exception as e:
            logger.error(f"Audio watermark addition failed: {e}")
            return audio_data
    
    def _add_video_watermark(self, video_path: str, creator_id: str, protection_level: ContentSecurityLevel) -> str:
        """Add watermark to video content."""



        try:
            # This would use ffmpeg or similar for video processing
            # Simplified implementation - in reality would use video processing library
            
            output_path = f"watermarked_{video_path}"
            watermark_text = f"© {creator_id} - IA Influencer Agent"
            
            # ffmpeg command for watermarking (pseudo-code)
            # ffmpeg -i input.mp4 -vf "drawtext=text='watermark':x=10:y=10:fontcolor=white@0.8" output.mp4
            
            logger.info(f"Video watermarking would be applied to {video_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Video watermark addition failed: {e}")
            return video_path
    
    async def _register_on_blockchain(self, fingerprint: ContentFingerprint) -> str:
        """Register content fingerprint on blockchain for immutable proof."""



        try:
            # Blockchain registration implementation
            # This would integrate with blockchain networks like Ethereum, Hyperledger, etc.
            
            blockchain_data = {
                'content_id': fingerprint.content_id,
                'fingerprint_hash': fingerprint.fingerprint_hash,
                'creator_id': fingerprint.creator_id,
                'timestamp': fingerprint.creation_timestamp.isoformat(),
                'protection_level': fingerprint.protection_level.value
            }
            
            # Create blockchain transaction hash (simplified)
            blockchain_hash = hashlib.sha256(json.dumps(blockchain_data, sort_keys=True).encode()).hexdigest()
            
            logger.info(f"Content registered on blockchain: {blockchain_hash}")
            return blockchain_hash
            
        except Exception as e:
            logger.error(f"Blockchain registration failed: {e}")
            return ""
    
    def _assess_threat_level(self, similarity_score: float) -> ThreatLevel:
        """Assess threat level based on similarity score."""



        try:
            if similarity_score >= 0.95:
                return ThreatLevel.CRITICAL
            elif similarity_score >= 0.85:
                return ThreatLevel.HIGH
            elif similarity_score >= 0.7:
                return ThreatLevel.MEDIUM
            else:
                return ThreatLevel.LOW
                
        except Exception:
            return ThreatLevel.LOW
    
    def _calculate_image_similarity(self, suspicious_hashes: List, fingerprint: ContentFingerprint) -> float:
        """Calculate image similarity score."""



        try:
            # Simplified similarity calculation
            # In reality, would compare actual hash values
            return 85.0  # Placeholder
            
        except Exception:
            return 0.0
    
    def _calculate_audio_similarity(self, suspicious_mfccs: np.ndarray, fingerprint: ContentFingerprint) -> float:
        """Calculate audio similarity score."""



        try:
            # Simplified similarity calculation
            # In reality, would compare MFCC features
            return 0.8  # Placeholder
            
        except Exception:
            return 0.0
    
    def _calculate_video_similarity(self, suspicious_frames: List[str], fingerprint: ContentFingerprint) -> float:
        """Calculate video similarity score."""



        try:
            # Simplified similarity calculation
            # In reality, would compare frame hashes
            return 0.85  # Placeholder
            
        except Exception:
            return 0.0
    
    def _calculate_security_score(self, fingerprint: ContentFingerprint, threats: List[SecurityThreat]) -> float:
        """Calculate overall security score for content."""



        try:
            base_score = 0.8  # Base security score
            
            # Reduce score based on protection level
            protection_multipliers = {
                ContentSecurityLevel.PUBLIC: 0.5,
                ContentSecurityLevel.WATERMARKED: 0.7,
                ContentSecurityLevel.ENCRYPTED: 0.85,
                ContentSecurityLevel.PREMIUM_PROTECTED: 0.9,
                ContentSecurityLevel.EXCLUSIVE_ACCESS: 1.0
            }
            
            score = base_score * protection_multipliers.get(fingerprint.protection_level, 0.5)
            
            # Reduce score based on detected threats
            threat_penalty = len(threats) * 0.1
            score = max(score - threat_penalty, 0.0)
            
            return min(score, 1.0)
            
        except Exception:
            return 0.5
    
    def _determine_protection_status(self, fingerprint: ContentFingerprint, threats: List[SecurityThreat]) -> str:
        """Determine overall protection status."""



        try:
            if len(threats) == 0:
                return "protected"
            elif any(threat.threat_level == ThreatLevel.CRITICAL for threat in threats):
                return "critical_threats_detected"
            elif any(threat.threat_level == ThreatLevel.HIGH for threat in threats):
                return "high_threats_detected"
            else:
                return "low_threats_detected"
                
        except Exception:
            return "unknown"
    
    def _generate_protection_recommendations(
        self, 
        fingerprint: ContentFingerprint, 
        threats: List[SecurityThreat]
    ) -> List[str]:
        """Generate protection improvement recommendations."""



        try:
            recommendations = []
            
            # Base recommendations based on protection level
            if fingerprint.protection_level == ContentSecurityLevel.PUBLIC:
                recommendations.append("Consider upgrading to watermarked protection")
                
            if fingerprint.protection_level in [ContentSecurityLevel.PUBLIC, ContentSecurityLevel.WATERMARKED]:
                recommendations.append("Enable blockchain registration for immutable proof")
            
            # Threat-based recommendations
            if threats:
                recommendations.append("Implement automated monitoring for unauthorized usage")
                recommendations.append("Set up DMCA takedown automation")
                
                if any(threat.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL] for threat in threats):
                    recommendations.append("Consider legal action for high-severity threats")
                    recommendations.append("Upgrade to premium protection level")
            
            # Content-type specific recommendations
            if fingerprint.content_type == 'image':
                recommendations.append("Use multiple watermark positions for better protection")
            elif fingerprint.content_type == 'audio':
                recommendations.append("Register with music collection societies")
            elif fingerprint.content_type == 'video':
                recommendations.append("Enable Content ID on video platforms")
            
            return recommendations[:8]  # Limit to top 8 recommendations
            
        except Exception:
            return ["Review content protection settings", "Monitor for unauthorized usage"]
    
    def _check_compliance_status(self, fingerprint: ContentFingerprint) -> Dict[str, str]:
        """Check compliance with various standards and regulations."""



        try:
            compliance = {
                'dmca_compliant': 'yes' if fingerprint.protection_level != ContentSecurityLevel.PUBLIC else 'partial',
                'copyright_registered': 'yes' if fingerprint.blockchain_hash else 'no',
                'watermark_applied': 'yes' if fingerprint.protection_level != ContentSecurityLevel.PUBLIC else 'no',
                'fingerprint_recorded': 'yes',
                'verification_available': 'yes' if fingerprint.verification_signature else 'no'
            }
            
            return compliance
            
        except Exception:
            return {'status': 'unknown'}


class ContentRightsManager:
    """Manage content rights, licensing, and usage permissions."""
    
    def __init__(self, protection_engine: ContentProtectionEngine):
        """Initialize rights manager."""
        self.protection_engine = protection_engine
        self.licensing_database: Dict[str, Dict[str, Any]] = {}
        self.usage_permissions: Dict[str, List[str]] = defaultdict(list)
    
    async def create_license(
        self, 
        content_id: str, 
        license_type: str,
        terms: Dict[str, Any],
        creator_id: str
    ) -> str:
        """Create content license with specific terms."""



        try:
            license_id = f"license_{content_id}_{int(datetime.now().timestamp())}"
            
            license_data = {
                'license_id': license_id,
                'content_id': content_id,
                'creator_id': creator_id,
                'license_type': license_type,  # exclusive, non-exclusive, royalty-free, etc.
                'terms': terms,
                'created_at': datetime.now(),
                'status': 'active'
            }
            
            self.licensing_database[license_id] = license_data
            
            logger.info(f"License created: {license_id}")
            return license_id
            
        except Exception as e:
            logger.error(f"License creation failed: {e}")
            raise
    
    async def grant_usage_permission(
        self, 
        content_id: str, 
        grantee_id: str,
        permission_type: str,
        duration: Optional[timedelta] = None
    ):
        """Grant usage permission to specific user."""



        try:
            permission = {
                'grantee_id': grantee_id,
                'permission_type': permission_type,
                'granted_at': datetime.now(),
                'expires_at': datetime.now() + duration if duration else None,
                'status': 'active'
            }
            
            self.usage_permissions[content_id].append(permission)
            
            logger.info(f"Usage permission granted for {content_id} to {grantee_id}")
            
        except Exception as e:
            logger.error(f"Permission granting failed: {e}")
            raise
    
    def check_usage_permission(self, content_id: str, user_id: str) -> bool:
        """Check if user has permission to use content."""



        try:
            permissions = self.usage_permissions.get(content_id, [])
            
            for permission in permissions:
                if (permission['grantee_id'] == user_id and 
                    permission['status'] == 'active'):
                    
                    # Check expiration
                    if permission['expires_at'] and permission['expires_at'] < datetime.now():
                        permission['status'] = 'expired'
                        continue
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False


# Export classes
__all__ = [
    'ContentSecurityLevel',
    'ProtectionType',
    'ThreatLevel',
    'ContentFingerprint',
    'SecurityThreat',
    'ProtectionReport',
    'ContentProtectionEngine',
    'ContentRightsManager'
]
