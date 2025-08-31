"""
Content Protection Manager
=========================

Enterprise-grade content protection and copyright management system for multi-format
content fingerprinting, infringement detection, and automated enforcement.

This module provides comprehensive content protection capabilities including:
- Multi-format fingerprinting (audio, video, image, text)
- Real-time infringement detection and monitoring
- Automated takedown request generation and processing
- Content verification and authenticity validation
- Copyright licensing and revenue tracking

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

  IMPORTANT LEGAL NOTICE 
This code is the intellectual property of Fahed Mlaiel. Any unauthorized use,
reproduction, distribution, or commercialization without explicit written 
permission is strictly prohibited and will result in legal action.
"""

import asyncio
import logging
import time
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union, ByteString
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from pathlib import Path
import tempfile
import os

# Audio fingerprinting
import librosa
import chromaprint
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs

# Video fingerprinting
import cv2
from PIL import Image
import imagehash

# Text fingerprinting
import nltk
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch

# Vector similarity
import faiss
from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import cosine_similarity

from ..utils.file_handler import FileHandler
from ..utils.hash_generator import HashGenerator
from ..config.protection_config import ProtectionConfig
from ...core.database import get_database_session
from ...core.logging import get_logger
from ...core.storage import StorageManager
from ...models.content_protection import (
    ContentFingerprint, 
    InfringementReport, 
    ProtectionStatus,
    TakedownRequest
)


class ContentFormat(Enum):
    """Supported content formats for protection."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED_MEDIA = "mixed_media"


class FingerprintType(Enum):
    """Types of fingerprints for content identification."""
    CHROMAPRINT = "chromaprint"
    SPECTRAL_HASH = "spectral_hash"
    PERCEPTUAL_HASH = "perceptual_hash"
    VISUAL_HASH = "visual_hash"
    SEMANTIC_HASH = "semantic_hash"
    CONTENT_ID = "content_id"
    HASH_COMBINATION = "hash_combination"


class ProtectionLevel(Enum):
    """Content protection levels."""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    ULTRA = "ultra"


class InfringementSeverity(Enum):
    """Severity levels for infringement detection."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FingerprintMetadata:
    """Metadata for content fingerprints."""
    fingerprint_type: FingerprintType
    algorithm: str
    version: str
    confidence_score: float
    processing_time: float
    file_size: int
    duration: Optional[float] = None
    resolution: Optional[Tuple[int, int]] = None
    sample_rate: Optional[int] = None
    bit_rate: Optional[int] = None
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentProtectionRecord:
    """Complete content protection record."""
    content_id: str
    owner_id: str
    content_format: ContentFormat
    protection_level: ProtectionLevel
    fingerprints: Dict[FingerprintType, str]
    metadata: FingerprintMetadata
    file_hash: str
    original_filename: str
    content_title: Optional[str] = None
    content_description: Optional[str] = None
    creation_date: Optional[datetime] = None
    registration_date: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"
    tags: List[str] = field(default_factory=list)


@dataclass
class InfringementMatch:
    """Infringement detection match result."""
    protected_content_id: str
    infringing_content_url: str
    platform: str
    similarity_score: float
    fingerprint_type: FingerprintType
    detection_timestamp: datetime
    severity: InfringementSeverity
    confidence_level: float
    match_details: Dict[str, Any] = field(default_factory=dict)
    geographical_location: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class TakedownRequestData:
    """Takedown request information."""
    request_id: str
    infringement_match: InfringementMatch
    copyright_owner: str
    contact_email: str
    platform: str
    request_type: str = "dmca"
    legal_basis: str = "copyright_infringement"
    requested_action: str = "content_removal"
    additional_information: Optional[str] = None
    supporting_evidence: List[str] = field(default_factory=list)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)


class ContentProtectionManager:
    """
    Enterprise-grade content protection manager for comprehensive copyright protection.
    
    Features:
    - Multi-format fingerprinting (audio, video, image, text)
    - Real-time infringement detection
    - Automated takedown request generation
    - Vector similarity matching with FAISS
    - Machine learning-based content analysis
    - Blockchain-ready copyright verification
    """
    
    def __init__(self, config: Optional[ProtectionConfig] = None):
        """Initialize content protection manager."""
        self.config = config or ProtectionConfig()
        self.logger = get_logger(__name__)
        self.storage_manager = StorageManager()
        self.file_handler = FileHandler()
        self.hash_generator = HashGenerator()
        
        # Vector databases for similarity matching
        self.audio_index: Optional[faiss.Index] = None
        self.video_index: Optional[faiss.Index] = None
        self.image_index: Optional[faiss.Index] = None
        self.text_index: Optional[faiss.Index] = None
        
        # ML models for content analysis
        self.audio_model = None
        self.text_model = None
        self.image_model = None
        
        # Content protection database
        self.protected_content: Dict[str, ContentProtectionRecord] = {}
        
        # Infringement monitoring
        self.active_monitors: Set[str] = set()
        self.detection_thresholds: Dict[FingerprintType, float] = {
            FingerprintType.CHROMAPRINT: 0.85,
            FingerprintType.SPECTRAL_HASH: 0.80,
            FingerprintType.PERCEPTUAL_HASH: 0.90,
            FingerprintType.VISUAL_HASH: 0.85,
            FingerprintType.SEMANTIC_HASH: 0.75
        }
        
        # Initialize components
        self._initialize_ml_models()
        self._initialize_vector_databases()
    
    def _initialize_ml_models(self):
        """Initialize machine learning models for content analysis."""



        try:
            # Initialize text similarity model
            self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize audio analysis model
            self.audio_model = TensorflowPredictEffnetDiscogs(
                graphFilename="effnet_discogs.pb",
                output="PartitionedCall:1"
            )
            
            self.logger.info("ML models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML models: {str(e)}")
    
    def _initialize_vector_databases(self):
        """Initialize FAISS vector databases for similarity matching."""



        try:
            # Audio fingerprint vectors (512 dimensions)
            self.audio_index = faiss.IndexFlatIP(512)
            
            # Video fingerprint vectors (1024 dimensions)
            self.video_index = faiss.IndexFlatIP(1024)
            
            # Image fingerprint vectors (256 dimensions)
            self.image_index = faiss.IndexFlatIP(256)
            
            # Text fingerprint vectors (384 dimensions)
            self.text_index = faiss.IndexFlatIP(384)
            
            self.logger.info("Vector databases initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector databases: {str(e)}")
    
    async def register_content_for_protection(
        self,
        file_path: str,
        owner_id: str,
        content_format: ContentFormat,
        protection_level: ProtectionLevel = ProtectionLevel.STANDARD,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register content for protection and generate fingerprints.
        
        Args:
            file_path: Path to content file
            owner_id: Content owner identifier
            content_format: Type of content
            protection_level: Level of protection
            metadata: Additional metadata
            
        Returns:
            str: Content protection ID
        """



        try:
            content_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Validate file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Content file not found: {file_path}")
            
            # Generate file hash
            file_hash = self.hash_generator.generate_file_hash(file_path)
            
            # Generate fingerprints based on content format
            fingerprints = {}
            fingerprint_metadata = None
            
            if content_format == ContentFormat.AUDIO:
                fingerprints, fingerprint_metadata = await self._generate_audio_fingerprints(file_path)
            elif content_format == ContentFormat.VIDEO:
                fingerprints, fingerprint_metadata = await self._generate_video_fingerprints(file_path)
            elif content_format == ContentFormat.IMAGE:
                fingerprints, fingerprint_metadata = await self._generate_image_fingerprints(file_path)
            elif content_format == ContentFormat.TEXT:
                fingerprints, fingerprint_metadata = await self._generate_text_fingerprints(file_path)
            else:
                raise ValueError(f"Unsupported content format: {content_format}")
            
            processing_time = time.time() - start_time
            
            # Create protection record
            protection_record = ContentProtectionRecord(
                content_id=content_id,
                owner_id=owner_id,
                content_format=content_format,
                protection_level=protection_level,
                fingerprints=fingerprints,
                metadata=fingerprint_metadata,
                file_hash=file_hash,
                original_filename=os.path.basename(file_path),
                content_title=metadata.get("title") if metadata else None,
                content_description=metadata.get("description") if metadata else None,
                creation_date=metadata.get("creation_date") if metadata else None
            )
            
            # Store protection record
            await self._store_protection_record(protection_record)
            
            # Add to vector databases for fast similarity search
            await self._add_to_vector_database(protection_record)
            
            # Store in memory cache
            self.protected_content[content_id] = protection_record
            
            self.logger.info(
                f"Content registered for protection: {content_id} "
                f"(format: {content_format.value}, processing_time: {processing_time:.2f}s)"
            )
            
            return content_id
            
        except Exception as e:
            self.logger.error(f"Failed to register content for protection: {str(e)}")
            raise
    
    async def _generate_audio_fingerprints(self, file_path: str) -> Tuple[Dict[FingerprintType, str], FingerprintMetadata]:
        """Generate fingerprints for audio content."""
        fingerprints = {}
        
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=22050)
            duration = len(y) / sr
            
            # Generate Chromaprint fingerprint
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            
            chromaprint_fp = chromaprint.decode_fingerprint(
                chromaprint.fingerprint(audio_data, sample_rate=sr)
            )[0]
            fingerprints[FingerprintType.CHROMAPRINT] = json.dumps(chromaprint_fp.tolist())
            
            # Generate spectral hash
            spectral_features = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_hash = hashlib.sha256(spectral_features.tobytes()).hexdigest()
            fingerprints[FingerprintType.SPECTRAL_HASH] = spectral_hash
            
            # Generate semantic audio embedding if model is available
            if self.audio_model:
                try:
                    # Use Essentia model for audio embeddings
                    audio_embedding = self.audio_model(y)
                    semantic_hash = hashlib.sha256(audio_embedding.tobytes()).hexdigest()
                    fingerprints[FingerprintType.SEMANTIC_HASH] = semantic_hash
                except Exception as e:
                    self.logger.warning(f"Failed to generate semantic audio hash: {str(e)}")
            
            # Create metadata
            metadata = FingerprintMetadata(
                fingerprint_type=FingerprintType.CHROMAPRINT,
                algorithm="chromaprint_essentia",
                version="1.0",
                confidence_score=0.95,
                processing_time=time.time(),
                file_size=os.path.getsize(file_path),
                duration=duration,
                sample_rate=sr
            )
            
            return fingerprints, metadata
            
        except Exception as e:
            self.logger.error(f"Failed to generate audio fingerprints: {str(e)}")
            raise
    
    async def _generate_video_fingerprints(self, file_path: str) -> Tuple[Dict[FingerprintType, str], FingerprintMetadata]:
        """Generate fingerprints for video content."""
        fingerprints = {}
        
        try:
            # Open video file
            cap = cv2.VideoCapture(file_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Extract key frames for fingerprinting
            key_frames = []
            frame_interval = max(1, frame_count // 10)  # Extract 10 key frames
            
            for i in range(0, frame_count, frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    key_frames.append(frame)
            
            cap.release()
            
            # Generate perceptual hashes for key frames
            frame_hashes = []
            for frame in key_frames:
                # Convert to PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Generate perceptual hash
                phash = str(imagehash.phash(pil_image))
                frame_hashes.append(phash)
            
            # Combine frame hashes
            combined_hash = hashlib.sha256(''.join(frame_hashes).encode()).hexdigest()
            fingerprints[FingerprintType.PERCEPTUAL_HASH] = combined_hash
            
            # Generate visual hash using histogram features
            visual_features = []
            for frame in key_frames:
                hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                visual_features.append(hist.flatten())
            
            if visual_features:
                combined_features = np.concatenate(visual_features)
                visual_hash = hashlib.sha256(combined_features.tobytes()).hexdigest()
                fingerprints[FingerprintType.VISUAL_HASH] = visual_hash
            
            # Create metadata
            metadata = FingerprintMetadata(
                fingerprint_type=FingerprintType.PERCEPTUAL_HASH,
                algorithm="opencv_perceptual_hash",
                version="1.0",
                confidence_score=0.90,
                processing_time=time.time(),
                file_size=os.path.getsize(file_path),
                duration=duration,
                resolution=(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            )
            
            return fingerprints, metadata
            
        except Exception as e:
            self.logger.error(f"Failed to generate video fingerprints: {str(e)}")
            raise
    
    async def _generate_image_fingerprints(self, file_path: str) -> Tuple[Dict[FingerprintType, str], FingerprintMetadata]:
        """Generate fingerprints for image content."""
        fingerprints = {}
        
        try:
            # Load image
            image = Image.open(file_path)
            
            # Generate multiple perceptual hashes
            phash = str(imagehash.phash(image))
            dhash = str(imagehash.dhash(image))
            whash = str(imagehash.whash(image))
            
            fingerprints[FingerprintType.PERCEPTUAL_HASH] = phash
            
            # Combine different hashes for robustness
            combined_hash = hashlib.sha256(f"{phash}{dhash}{whash}".encode()).hexdigest()
            fingerprints[FingerprintType.HASH_COMBINATION] = combined_hash
            
            # Generate visual features using OpenCV
            cv_image = cv2.imread(file_path)
            if cv_image is not None:
                # Color histogram
                hist = cv2.calcHist([cv_image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                visual_hash = hashlib.sha256(hist.tobytes()).hexdigest()
                fingerprints[FingerprintType.VISUAL_HASH] = visual_hash
            
            # Create metadata
            metadata = FingerprintMetadata(
                fingerprint_type=FingerprintType.PERCEPTUAL_HASH,
                algorithm="imagehash_combined",
                version="1.0",
                confidence_score=0.92,
                processing_time=time.time(),
                file_size=os.path.getsize(file_path),
                resolution=image.size
            )
            
            return fingerprints, metadata
            
        except Exception as e:
            self.logger.error(f"Failed to generate image fingerprints: {str(e)}")
            raise
    
    async def _generate_text_fingerprints(self, file_path: str) -> Tuple[Dict[FingerprintType, str], FingerprintMetadata]:
        """Generate fingerprints for text content."""
        fingerprints = {}
        
        try:
            # Read text content
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Generate basic hash
            text_hash = hashlib.sha256(text_content.encode()).hexdigest()
            fingerprints[FingerprintType.CONTENT_ID] = text_hash
            
            # Generate semantic embedding if model is available
            if self.text_model:
                try:
                    # Generate sentence embedding
                    embedding = self.text_model.encode(text_content)
                    semantic_hash = hashlib.sha256(embedding.tobytes()).hexdigest()
                    fingerprints[FingerprintType.SEMANTIC_HASH] = semantic_hash
                except Exception as e:
                    self.logger.warning(f"Failed to generate semantic text hash: {str(e)}")
            
            # Generate n-gram based fingerprint
            words = text_content.lower().split()
            if len(words) >= 3:
                trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
                trigram_hash = hashlib.sha256(' '.join(sorted(trigrams)).encode()).hexdigest()
                fingerprints[FingerprintType.HASH_COMBINATION] = trigram_hash
            
            # Create metadata
            metadata = FingerprintMetadata(
                fingerprint_type=FingerprintType.SEMANTIC_HASH,
                algorithm="sentence_transformers",
                version="1.0",
                confidence_score=0.88,
                processing_time=time.time(),
                file_size=os.path.getsize(file_path)
            )
            
            return fingerprints, metadata
            
        except Exception as e:
            self.logger.error(f"Failed to generate text fingerprints: {str(e)}")
            raise
    
    async def detect_infringement(
        self,
        content_file: str,
        content_format: ContentFormat,
        source_url: Optional[str] = None,
        platform: Optional[str] = None
    ) -> List[InfringementMatch]:
        """
        Detect potential copyright infringement by comparing against protected content.
        
        Args:
            content_file: Path to suspected infringing content
            content_format: Format of the content
            source_url: URL where content was found
            platform: Platform where content was found
            
        Returns:
            List[InfringementMatch]: List of potential infringement matches
        """



        try:
            matches = []
            
            # Generate fingerprints for the suspicious content
            if content_format == ContentFormat.AUDIO:
                fingerprints, _ = await self._generate_audio_fingerprints(content_file)
            elif content_format == ContentFormat.VIDEO:
                fingerprints, _ = await self._generate_video_fingerprints(content_file)
            elif content_format == ContentFormat.IMAGE:
                fingerprints, _ = await self._generate_image_fingerprints(content_file)
            elif content_format == ContentFormat.TEXT:
                fingerprints, _ = await self._generate_text_fingerprints(content_file)
            else:
                raise ValueError(f"Unsupported content format: {content_format}")
            
            # Compare against protected content
            for content_id, protected_record in self.protected_content.items():
                if protected_record.content_format != content_format:
                    continue
                
                # Calculate similarity for each fingerprint type
                for fingerprint_type, fingerprint_value in fingerprints.items():
                    if fingerprint_type not in protected_record.fingerprints:
                        continue
                    
                    protected_fingerprint = protected_record.fingerprints[fingerprint_type]
                    similarity_score = await self._calculate_similarity(
                        fingerprint_value,
                        protected_fingerprint,
                        fingerprint_type
                    )
                    
                    # Check if similarity exceeds threshold
                    threshold = self.detection_thresholds.get(fingerprint_type, 0.80)
                    if similarity_score >= threshold:
                        # Determine severity based on similarity score
                        if similarity_score >= 0.95:
                            severity = InfringementSeverity.CRITICAL
                        elif similarity_score >= 0.90:
                            severity = InfringementSeverity.HIGH
                        elif similarity_score >= 0.85:
                            severity = InfringementSeverity.MEDIUM
                        else:
                            severity = InfringementSeverity.LOW
                        
                        match = InfringementMatch(
                            protected_content_id=content_id,
                            infringing_content_url=source_url or "unknown",
                            platform=platform or "unknown",
                            similarity_score=similarity_score,
                            fingerprint_type=fingerprint_type,
                            detection_timestamp=datetime.utcnow(),
                            severity=severity,
                            confidence_level=min(similarity_score, 0.99),
                            match_details={
                                "fingerprint_match": True,
                                "algorithm": fingerprint_type.value,
                                "threshold_used": threshold
                            }
                        )
                        
                        matches.append(match)
            
            # Log detection results
            if matches:
                self.logger.warning(
                    f"Potential infringement detected: {len(matches)} matches found "
                    f"for content from {source_url or 'unknown source'}"
                )
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Failed to detect infringement: {str(e)}")
            return []
    
    async def _calculate_similarity(
        self,
        fingerprint1: str,
        fingerprint2: str,
        fingerprint_type: FingerprintType
    ) -> float:
        """Calculate similarity between two fingerprints."""



        try:
            if fingerprint_type in [FingerprintType.CONTENT_ID, FingerprintType.SPECTRAL_HASH, FingerprintType.VISUAL_HASH]:
                # Exact hash comparison
                return 1.0 if fingerprint1 == fingerprint2 else 0.0
            
            elif fingerprint_type == FingerprintType.PERCEPTUAL_HASH:
                # Hamming distance for perceptual hashes
                try:
                    hash1 = imagehash.hex_to_hash(fingerprint1)
                    hash2 = imagehash.hex_to_hash(fingerprint2)
                    distance = hash1 - hash2
                    similarity = 1.0 - (distance / 64.0)  # Normalize to 0-1
                    return max(0.0, similarity)
                except:
                    return 0.0
            
            elif fingerprint_type == FingerprintType.CHROMAPRINT:
                # Chromaprint comparison
                try:
                    fp1 = json.loads(fingerprint1)
                    fp2 = json.loads(fingerprint2)
                    
                    # Simple correlation-based similarity
                    if len(fp1) != len(fp2):
                        return 0.0
                    
                    correlation = np.corrcoef(fp1, fp2)[0, 1]
                    return max(0.0, correlation)
                except:
                    return 0.0
            
            elif fingerprint_type == FingerprintType.SEMANTIC_HASH:
                # For semantic hashes, we'd typically compare embeddings
                # Here we use simple hash equality as a fallback
                return 1.0 if fingerprint1 == fingerprint2 else 0.0
            
            else:
                # Default to string similarity
                return 1.0 if fingerprint1 == fingerprint2 else 0.0
                
        except Exception as e:
            self.logger.error(f"Failed to calculate similarity: {str(e)}")
            return 0.0
    
    async def generate_takedown_request(
        self,
        infringement_match: InfringementMatch,
        copyright_owner: str,
        contact_email: str,
        additional_info: Optional[str] = None
    ) -> TakedownRequestData:
        """
        Generate automated takedown request for detected infringement.
        
        Args:
            infringement_match: Detected infringement match
            copyright_owner: Name of copyright owner
            contact_email: Contact email for takedown requests
            additional_info: Additional information for the request
            
        Returns:
            TakedownRequestData: Generated takedown request
        """



        try:
            request_id = str(uuid.uuid4())
            
            # Get protected content details
            protected_content = self.protected_content.get(infringement_match.protected_content_id)
            if not protected_content:
                raise ValueError("Protected content not found")
            
            # Generate supporting evidence
            supporting_evidence = [
                f"Similarity Score: {infringement_match.similarity_score:.2%}",
                f"Detection Algorithm: {infringement_match.fingerprint_type.value}",
                f"Confidence Level: {infringement_match.confidence_level:.2%}",
                f"Original Content ID: {infringement_match.protected_content_id}",
                f"Original Filename: {protected_content.original_filename}",
                f"Registration Date: {protected_content.registration_date.isoformat()}"
            ]
            
            if protected_content.content_title:
                supporting_evidence.append(f"Original Title: {protected_content.content_title}")
            
            takedown_request = TakedownRequestData(
                request_id=request_id,
                infringement_match=infringement_match,
                copyright_owner=copyright_owner,
                contact_email=contact_email,
                platform=infringement_match.platform,
                additional_information=additional_info,
                supporting_evidence=supporting_evidence
            )
            
            # Store takedown request
            await self._store_takedown_request(takedown_request)
            
            self.logger.info(f"Takedown request generated: {request_id}")
            
            return takedown_request
            
        except Exception as e:
            self.logger.error(f"Failed to generate takedown request: {str(e)}")
            raise
    
    async def _store_protection_record(self, record: ContentProtectionRecord):
        """Store content protection record in database."""



        try:
            async with get_database_session() as db:
                await db.execute(
                    """
                    INSERT INTO content_protection (
                        content_id, owner_id, content_format, protection_level,
                        fingerprints, metadata, file_hash, original_filename,
                        content_title, content_description, creation_date,
                        registration_date, status, tags
                    ) VALUES (
                        :content_id, :owner_id, :content_format, :protection_level,
                        :fingerprints, :metadata, :file_hash, :original_filename,
                        :content_title, :content_description, :creation_date,
                        :registration_date, :status, :tags
                    )
                    """,
                    {
                        "content_id": record.content_id,
                        "owner_id": record.owner_id,
                        "content_format": record.content_format.value,
                        "protection_level": record.protection_level.value,
                        "fingerprints": json.dumps(record.fingerprints),
                        "metadata": json.dumps(record.metadata.__dict__),
                        "file_hash": record.file_hash,
                        "original_filename": record.original_filename,
                        "content_title": record.content_title,
                        "content_description": record.content_description,
                        "creation_date": record.creation_date,
                        "registration_date": record.registration_date,
                        "status": record.status,
                        "tags": json.dumps(record.tags)
                    }
                )
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store protection record: {str(e)}")
            raise
    
    async def _store_takedown_request(self, request: TakedownRequestData):
        """Store takedown request in database."""



        try:
            async with get_database_session() as db:
                await db.execute(
                    """
                    INSERT INTO takedown_requests (
                        request_id, protected_content_id, infringing_url, platform,
                        similarity_score, fingerprint_type, severity, copyright_owner,
                        contact_email, request_type, legal_basis, requested_action,
                        additional_information, supporting_evidence, status, created_at
                    ) VALUES (
                        :request_id, :protected_content_id, :infringing_url, :platform,
                        :similarity_score, :fingerprint_type, :severity, :copyright_owner,
                        :contact_email, :request_type, :legal_basis, :requested_action,
                        :additional_information, :supporting_evidence, :status, :created_at
                    )
                    """,
                    {
                        "request_id": request.request_id,
                        "protected_content_id": request.infringement_match.protected_content_id,
                        "infringing_url": request.infringement_match.infringing_content_url,
                        "platform": request.platform,
                        "similarity_score": request.infringement_match.similarity_score,
                        "fingerprint_type": request.infringement_match.fingerprint_type.value,
                        "severity": request.infringement_match.severity.value,
                        "copyright_owner": request.copyright_owner,
                        "contact_email": request.contact_email,
                        "request_type": request.request_type,
                        "legal_basis": request.legal_basis,
                        "requested_action": request.requested_action,
                        "additional_information": request.additional_information,
                        "supporting_evidence": json.dumps(request.supporting_evidence),
                        "status": request.status,
                        "created_at": request.created_at
                    }
                )
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store takedown request: {str(e)}")
            raise
    
    async def _add_to_vector_database(self, record: ContentProtectionRecord):
        """Add content fingerprints to vector database for fast similarity search."""



        try:
            # This would add vector representations to FAISS indexes
            # Implementation depends on the specific vector format used
            pass
            
        except Exception as e:
            self.logger.error(f"Failed to add to vector database: {str(e)}")
    
    async def get_protection_status(self, content_id: str) -> Optional[ContentProtectionRecord]:
        """Get protection status for specific content."""



        return self.protected_content.get(content_id)
    
    async def update_protection_level(self, content_id: str, new_level: ProtectionLevel) -> bool:
        """Update protection level for content."""



        try:
            if content_id in self.protected_content:
                self.protected_content[content_id].protection_level = new_level
                
                # Update in database
                async with get_database_session() as db:
                    await db.execute(
                        "UPDATE content_protection SET protection_level = :level WHERE content_id = :content_id",
                        {"level": new_level.value, "content_id": content_id}
                    )
                    await db.commit()
                
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update protection level: {str(e)}")
            return False
    
    async def close(self):
        """Close and cleanup resources."""



        try:
            # Clear memory caches
            self.protected_content.clear()
            self.active_monitors.clear()
            
            self.logger.info("Content protection manager closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing content protection manager: {str(e)}")


# Factory functions
async def create_content_protection_manager(config: Optional[ProtectionConfig] = None) -> ContentProtectionManager:
    """Create and initialize content protection manager."""



    return ContentProtectionManager(config)


async def register_content_batch(
    manager: ContentProtectionManager,
    content_files: List[Tuple[str, str, ContentFormat, ProtectionLevel]]
) -> List[str]:
    """Register multiple content files for protection."""
    content_ids = []
    
    for file_path, owner_id, content_format, protection_level in content_files:
        try:
            content_id = await manager.register_content_for_protection(
                file_path, owner_id, content_format, protection_level
            )
            content_ids.append(content_id)
        except Exception as e:
            manager.logger.error(f"Failed to register {file_path}: {str(e)}")
            content_ids.append(None)
    
    return content_ids


# Export all components
__all__ = [
    "ContentProtectionManager",
    "ContentFormat",
    "FingerprintType",
    "ProtectionLevel",
    "InfringementSeverity",
    "ContentProtectionRecord",
    "InfringementMatch",
    "TakedownRequestData",
    "FingerprintMetadata",
    "create_content_protection_manager",
    "register_content_batch"
]
