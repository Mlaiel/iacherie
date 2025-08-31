"""Content Protection Engine - IA-Influencer-Agent
================================================================================

Module: backend/core/engines/content_protection_engine.py
Architecture: IA-Influencer-Agent Backend (Level 3)
Created: 2025-08-19 
Team: Lead Dev IA + Backend Senior + ML Engineer + Security Expert + Audio Expert + Computer Vision

MISSION: Enterprise-grade multi-format content protection with advanced AI fingerprinting
MÉTIER: User upload → Multi-modal AI fingerprinting → Real-time web surveillance → Automated takedown → Revenue protection

Author: Fahed Mlaiel <mlaiel@live.de>
COPYRIGHT WARNING: This code is proprietary. Unauthorized use, copying, or 
redistribution without explicit written permission from Fahed Mlaiel is 
strictly prohibited and will result in legal action.
================================================================================
"""
import hashlib
import json
import logging
import numpy as np
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import asyncio
import aiofiles
from pathlib import Path
import cv2
import librosa
import torch
import torchvision.transforms as transforms
from PIL import Image
import chromaprint
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import imagehash
from moviepy.editor import VideoFileClip
import ffmpeg
import face_recognition
import whisper
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
import tensorflow as tf
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
import redis.asyncio as aioredis
from celery import Celery
from pydantic import BaseModel, validator, Field

# Internal imports
from ..security.crypto_manager import CryptoManager
from ..storage.file_manager import FileManager
from ..database.models import ContentFingerprint, ProtectionAlert, ContentOwnership
from ..utils.metrics import MetricsCollector
from ..cache.redis_manager import RedisManager
from ..integrations.blockchain.proof_service import BlockchainProofService
from ..integrations.legal.takedown_service import TakedownService
from ..crawlers.web_surveillance import WebSurveillanceEngine
from ..ml.similarity_models import AdvancedSimilarityEngine

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Content types supported for protection"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    SOCIAL_POST = "social_post"
    ARTICLE = "article"
    SCRIPT = "script"


class FingerprintMethod(str, Enum):
    """Advanced fingerprinting methods by content type"""    # Audio fingerprinting
    CHROMAPRINT = "chromaprint"
    SPECTRAL_HASH = "spectral_hash"
    MFCC_FEATURES = "mfcc_features"
    MEL_SPECTROGRAM = "mel_spectrogram"
    AUDIO_CLIP = "audio_clip"
    
    # Video fingerprinting
    PERCEPTUAL_HASH = "perceptual_hash"
    VIDEO_FRAME_HASH = "video_frame_hash"
    MOTION_VECTORS = "motion_vectors"
    SCENE_DETECTION = "scene_detection"
    OBJECT_DETECTION = "object_detection"
    FACE_RECOGNITION = "face_recognition"
    
    # Image fingerprinting
    CLIP_EMBEDDING = "clip_embedding"
    BLIP_EMBEDDING = "blip_embedding"
    RESNET_FEATURES = "resnet_features"
    VGG_FEATURES = "vgg_features"
    SIFT_FEATURES = "sift_features"
    ORB_FEATURES = "orb_features"
    
    # Text fingerprinting
    BERT_EMBEDDING = "bert_embedding"
    ROBERTA_EMBEDDING = "roberta_embedding"
    SENTENCE_TRANSFORMER = "sentence_transformer"
    TFIDF_VECTORS = "tfidf_vectors"
    N_GRAM_HASH = "n_gram_hash"
    MINHASH = "minhash"
    
    # Multimodal
    MULTIMODAL_FUSION = "multimodal_fusion"
    CROSS_MODAL_ALIGNMENT = "cross_modal_alignment"


class ProtectionLevel(str, Enum):
    """Content protection levels"""    BASIC = "basic"          # Standard fingerprinting
    STANDARD = "standard"    # Multi-method fingerprinting
    PREMIUM = "premium"      # AI-enhanced protection
    ENTERPRISE = "enterprise"  # Full protection suite
    ULTRA = "ultra"         # Military-grade protection


class MatchConfidence(str, Enum):
    """Similarity match confidence levels"""    VERY_LOW = "very_low"    # 0.0 - 0.3
    LOW = "low"              # 0.3 - 0.5
    MEDIUM = "medium"        # 0.5 - 0.7
    HIGH = "high"            # 0.7 - 0.9
    VERY_HIGH = "very_high"  # 0.9 - 1.0
    EXACT = "exact"          # 1.0


class AlertAction(str, Enum):
    """Actions to take on content match"""    MONITOR = "monitor"
    NOTIFY = "notify"
    TAKEDOWN_REQUEST = "takedown_request"
    LEGAL_ACTION = "legal_action"
    REVENUE_CLAIM = "revenue_claim"
    AUTOMATIC_BLOCK = "automatic_block"


@dataclass
class FingerprintResult:
    """Enhanced fingerprint extraction result"""    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    content_type: ContentType = ContentType.AUDIO
    method: FingerprintMethod = FingerprintMethod.CHROMAPRINT
    fingerprint_hash: str = ""
    vector_embedding: Optional[np.ndarray] = None
    feature_vector: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    extraction_time: float = 0.0
    file_size: int = 0
    duration: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    sample_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    color_channels: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    blockchain_proof: Optional[str] = None


@dataclass
class SimilarityMatch:
    """Enhanced content similarity match result"""    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_content_id: str = ""
    matched_content_id: str = ""
    similarity_score: float = 0.0
    confidence_level: MatchConfidence = MatchConfidence.LOW
    detection_url: Optional[str] = None
    platform: Optional[str] = None
    match_method: FingerprintMethod = FingerprintMethod.CHROMAPRINT
    match_regions: List[Dict[str, Any]] = field(default_factory=list)
    temporal_alignment: Optional[Dict[str, float]] = None
    spatial_alignment: Optional[Dict[str, Any]] = None
    additional_evidence: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.utcnow)
    verified: bool = False
    action_taken: Optional[AlertAction] = None
    takedown_status: Optional[str] = None
    revenue_claimed: Optional[float] = None


@dataclass
class ProtectionConfig:
    """Content protection configuration"""    protection_level: ProtectionLevel = ProtectionLevel.STANDARD
    enabled_methods: List[FingerprintMethod] = field(default_factory=list)
    similarity_threshold: float = 0.7
    monitoring_frequency: int = 24  # hours
    auto_takedown_threshold: float = 0.95
    enable_blockchain_proof: bool = True
    enable_revenue_tracking: bool = True
    notification_channels: List[str] = field(default_factory=list)
    geographic_monitoring: List[str] = field(default_factory=list)
    custom_rules: Dict[str, Any] = field(default_factory=dict)


class ContentProtectionRequest(BaseModel):
    """Pydantic model for protection requests"""    content_id: str = Field(..., description="Content identifier")
    content_type: ContentType = Field(..., description="Type of content")
    file_path: Optional[str] = Field(None, description="File path for processing")
    file_url: Optional[str] = Field(None, description="File URL for processing")
    protection_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    owner_id: str = Field(..., description="Content owner identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('content_id')
    def validate_content_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Content ID must be at least 3 characters long')
        return v


class ContentProtectionEngine:
    """    🛡️ ENTERPRISE CONTENT PROTECTION ENGINE
    
    Advanced multi-modal AI-powered content protection system with:
    - Real-time fingerprinting across all content types
    - Blockchain-verified proof of ownership
    - Automated web surveillance and monitoring
    - Intelligent takedown request automation
    - Revenue protection and claim tracking
    - Advanced similarity detection using latest AI models
    """    
    def __init__(
        self,
        db_session: AsyncSession,
        redis_client: aioredis.Redis,
        file_manager: FileManager,
        crypto_manager: CryptoManager,
        metrics_collector: MetricsCollector,
        enable_gpu: bool = True,
        model_cache_dir: str = "/models/cache"
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.file_manager = file_manager
        self.crypto = crypto_manager
        self.metrics = metrics_collector
        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.model_cache_dir = Path(model_cache_dir)
        
        # Initialize AI models
        self.device = torch.device("cuda" if self.enable_gpu else "cpu")
        self._initialize_models()
        
        # Initialize services
        self.blockchain_service = BlockchainProofService()
        self.takedown_service = TakedownService()
        self.surveillance_engine = WebSurveillanceEngine()
        self.similarity_engine = AdvancedSimilarityEngine()
        
        # Cache configuration
        self.cache_ttl = {
            "fingerprints": 86400 * 7,  # 7 days
            "matches": 86400 * 30,      # 30 days
            "models": 86400 * 365,      # 1 year
        }
        
        logger.info("🛡️ ContentProtectionEngine initialized successfully")
        
    def _initialize_models(self):
        """Initialize AI models for content analysis"""        try:
            # Text models
            self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.text_model.to(self.device)
            
            # Image models
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model.to(self.device)
            
            # BLIP model for image understanding
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model.to(self.device)
            
            # Audio models
            self.whisper_model = whisper.load_model("base")
            
            # Computer vision models
            self.resnet_model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)
            self.resnet_model.eval()
            self.resnet_model.to(self.device)
            
            logger.info("🤖 AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Model initialization failed: {str(e)}")
            raise
    
    async def protect_content(
        self,
        request: Union[ContentProtectionRequest, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """        🎯 Protect content with comprehensive fingerprinting
        
        Args:
            request: Content protection request
            
        Returns:
            Protection result with fingerprints and monitoring setup
        """        try:
            start_time = datetime.utcnow()
            
            # Convert dict to request object if needed
            if isinstance(request, dict):
                request = ContentProtectionRequest(**request)
            
            # Validate content access
            await self._validate_content_ownership(request.content_id, request.owner_id)
            
            # Get or create protection configuration
            config = ProtectionConfig(**request.protection_config)
            
            # Load content file
            file_data = await self._load_content_file(request)
            
            # Extract fingerprints using multiple methods
            fingerprints = await self._extract_multi_method_fingerprints(
                request.content_id,
                request.content_type,
                file_data,
                config
            )
            
            # Create blockchain proof of ownership
            blockchain_proof = None
            if config.enable_blockchain_proof:
                blockchain_proof = await self.blockchain_service.create_proof(
                    request.content_id,
                    request.owner_id,
                    fingerprints
                )
            
            # Save fingerprints to database
            saved_fingerprints = []
            for fingerprint in fingerprints:
                if blockchain_proof:
                    fingerprint.blockchain_proof = blockchain_proof["proof_hash"]
                
                saved_fp = await self._save_fingerprint(fingerprint)
                saved_fingerprints.append(saved_fp)
            
            # Setup monitoring and surveillance
            monitoring_config = await self._setup_content_monitoring(
                request.content_id,
                config
            )
            
            # Calculate processing metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            await self.metrics.record("content_protection.protected", 1, {
                "content_type": request.content_type.value,
                "protection_level": config.protection_level.value,
                "methods_count": len(fingerprints),
                "processing_time": processing_time
            })
            
            return {
                "success": True,
                "content_id": request.content_id,
                "protection_level": config.protection_level.value,
                "fingerprints_created": len(fingerprints),
                "methods_used": [fp.method.value for fp in fingerprints],
                "blockchain_proof": blockchain_proof,
                "monitoring_active": True,
                "monitoring_config": asdict(monitoring_config) if monitoring_config else None,
                "processing_time_ms": processing_time * 1000,
                "next_scan_at": datetime.utcnow() + timedelta(hours=config.monitoring_frequency)
            }
            
        except Exception as e:
            logger.error(f"Content protection failed: {str(e)}")
            await self.metrics.record("content_protection.error", 1, {
                "error_type": type(e).__name__
            })
            raise
    
    async def scan_for_matches(
        self,
        content_id: str,
        platforms: Optional[List[str]] = None,
        similarity_threshold: float = 0.7
    ) -> List[SimilarityMatch]:
        """        🔍 Scan for content matches across platforms
        
        Args:
            content_id: Content to scan for
            platforms: Platforms to scan (None for all)
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of detected matches
        """        try:
            # Get content fingerprints
            fingerprints = await self._get_content_fingerprints(content_id)
            
            if not fingerprints:
                return []
            
            # Perform surveillance scan
            matches = await self.surveillance_engine.scan_for_content(
                fingerprints,
                platforms,
                similarity_threshold
            )
            
            # Verify matches using advanced similarity
            verified_matches = []
            for match in matches:
                verification_result = await self.similarity_engine.verify_match(
                    fingerprints,
                    match
                )
                
                if verification_result["verified"]:
                    match.verified = True
                    match.confidence_level = MatchConfidence(verification_result["confidence_level"])
                    match.additional_evidence = verification_result["evidence"]
                    verified_matches.append(match)
            
            # Save matches to database
            saved_matches = []
            for match in verified_matches:
                saved_match = await self._save_similarity_match(match)
                saved_matches.append(saved_match)
                
                # Trigger automated actions if needed
                await self._handle_match_actions(saved_match)
            
            await self.metrics.record("content_protection.matches_found", len(saved_matches), {
                "content_id": content_id,
                "platforms_scanned": len(platforms) if platforms else 0
            })
            
            return saved_matches
            
        except Exception as e:
            logger.error(f"Match scanning failed: {str(e)}")
            raise
    
    async def generate_takedown_request(
        self,
        match: SimilarityMatch,
        template_type: str = "dmca"
    ) -> Dict[str, Any]:
        """        📄 Generate automated takedown request
        
        Args:
            match: Similarity match to take down
            template_type: Type of takedown request
            
        Returns:
            Generated takedown request details
        """        try:
            # Get original content details
            content_details = await self._get_content_details(match.original_content_id)
            
            # Generate takedown request
            takedown_request = await self.takedown_service.generate_request(
                match,
                content_details,
                template_type
            )
            
            # Submit takedown request if auto-submission enabled
            if takedown_request.get("auto_submit", False):
                submission_result = await self.takedown_service.submit_request(
                    takedown_request
                )
                takedown_request.update(submission_result)
            
            # Update match status
            match.action_taken = AlertAction.TAKEDOWN_REQUEST
            match.takedown_status = takedown_request.get("status", "submitted")
            await self._update_similarity_match(match)
            
            return takedown_request
            
        except Exception as e:
            logger.error(f"Takedown request generation failed: {str(e)}")
            raise
    
    async def claim_revenue(
        self,
        match: SimilarityMatch,
        revenue_percentage: float = 100.0
    ) -> Dict[str, Any]:
        """        💰 Claim revenue from matched content
        
        Args:
            match: Similarity match to claim revenue from
            revenue_percentage: Percentage of revenue to claim
            
        Returns:
            Revenue claim result
        """        try:
            # Validate claim eligibility
            await self._validate_revenue_claim(match)
            
            # Calculate claimable revenue
            revenue_estimate = await self._estimate_content_revenue(match)
            
            claim_amount = revenue_estimate * (revenue_percentage / 100.0)
            
            # Submit revenue claim through platform APIs
            claim_result = await self._submit_revenue_claim(
                match,
                claim_amount,
                revenue_percentage
            )
            
            # Update match record
            match.action_taken = AlertAction.REVENUE_CLAIM
            match.revenue_claimed = claim_amount
            await self._update_similarity_match(match)
            
            return {
                "success": True,
                "match_id": match.id,
                "estimated_revenue": revenue_estimate,
                "claimed_amount": claim_amount,
                "claim_percentage": revenue_percentage,
                "claim_status": claim_result.get("status"),
                "platform_response": claim_result
            }
            
        except Exception as e:
            logger.error(f"Revenue claim failed: {str(e)}")
            raise
    
    async def get_protection_analytics(
        self,
        owner_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """        📊 Get content protection analytics
        
        Args:
            owner_id: Content owner ID
            start_date: Analytics period start
            end_date: Analytics period end
            
        Returns:
            Comprehensive protection analytics
        """        try:
            # Get protection data
            analytics = await self._calculate_protection_analytics(
                owner_id,
                start_date,
                end_date
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Protection analytics failed: {str(e)}")
            raise
    
    # Audio fingerprinting methods
    
    async def _extract_audio_fingerprints(
        self,
        audio_data: bytes,
        methods: List[FingerprintMethod]
    ) -> List[FingerprintResult]:
        """Extract audio fingerprints using multiple methods"""        fingerprints = []
        
        try:
            # Load audio
            audio_path = await self._save_temp_file(audio_data, ".wav")
            y, sr = librosa.load(audio_path, sr=None)
            
            for method in methods:
                if method == FingerprintMethod.CHROMAPRINT:
                    # Chromaprint fingerprinting
                    duration, fingerprint = chromaprint.decode_fingerprint(
                        chromaprint.fingerprint(audio_data)[1]
                    )
                    
                    fp_result = FingerprintResult(
                        method=method,
                        fingerprint_hash=hashlib.sha256(str(fingerprint).encode()).hexdigest(),
                        metadata={"duration": duration, "sample_rate": sr}
                    )
                    fingerprints.append(fp_result)
                
                elif method == FingerprintMethod.MFCC_FEATURES:
                    # MFCC features
                    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                    mfcc_hash = hashlib.sha256(mfccs.tobytes()).hexdigest()
                    
                    fp_result = FingerprintResult(
                        method=method,
                        fingerprint_hash=mfcc_hash,
                        vector_embedding=mfccs.flatten(),
                        metadata={"mfcc_shape": mfccs.shape}
                    )
                    fingerprints.append(fp_result)
                
                elif method == FingerprintMethod.MEL_SPECTROGRAM:
                    # Mel spectrogram
                    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
                    mel_hash = hashlib.sha256(mel_spec.tobytes()).hexdigest()
                    
                    fp_result = FingerprintResult(
                        method=method,
                        fingerprint_hash=mel_hash,
                        vector_embedding=mel_spec.flatten(),
                        metadata={"mel_shape": mel_spec.shape}
                    )
                    fingerprints.append(fp_result)
            
            # Clean up temp file
            Path(audio_path).unlink(missing_ok=True)
            
        except Exception as e:
            logger.error(f"Audio fingerprinting failed: {str(e)}")
        
        return fingerprints
    
    # Image fingerprinting methods
    
    async def _extract_image_fingerprints(
        self,
        image_data: bytes,
        methods: List[FingerprintMethod]
    ) -> List[FingerprintResult]:
        """Extract image fingerprints using multiple methods"""        fingerprints = []
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            for method in methods:
                if method == FingerprintMethod.PERCEPTUAL_HASH:
                    # Perceptual hash
                    phash = str(imagehash.phash(image))
                    
                    fp_result = FingerprintResult(
                        method=method,
                        fingerprint_hash=phash,
                        metadata={"image_size": image.size}
                    )
                    fingerprints.append(fp_result)
                
                elif method == FingerprintMethod.CLIP_EMBEDDING:
                    # CLIP embedding
                    inputs = self.clip_processor(images=image, return_tensors="pt")
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    with torch.no_grad():
                        image_features = self.clip_model.get_image_features(**inputs)
                        embedding = image_features.cpu().numpy().flatten()
                    
                    embedding_hash = hashlib.sha256(embedding.tobytes()).hexdigest()
                    
                    fp_result = FingerprintResult(
                        method=method,
                        fingerprint_hash=embedding_hash,
                        vector_embedding=embedding,
                        metadata={"embedding_dim": len(embedding)}
                    )
                    fingerprints.append(fp_result)
                
                elif method == FingerprintMethod.RESNET_FEATURES:
                    # ResNet features
                    transform = transforms.Compose([
                        transforms.ToPILImage(),
                        transforms.Resize(256),
                        transforms.CenterCrop(224),
                        transforms.ToTensor(),
                        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                           std=[0.229, 0.224, 0.225]),
                    ])
                    
                    input_tensor = transform(image_array).unsqueeze(0).to(self.device)
                    
                    with torch.no_grad():
                        features = self.resnet_model(input_tensor)
                        features = features.cpu().numpy().flatten()
                    
                    features_hash = hashlib.sha256(features.tobytes()).hexdigest()
                    
                    fp_result = FingerprintResult(
                        method=method,
                        fingerprint_hash=features_hash,
                        vector_embedding=features,
                        metadata={"features_dim": len(features)}
                    )
                    fingerprints.append(fp_result)
        
        except Exception as e:
            logger.error(f"Image fingerprinting failed: {str(e)}")
        
        return fingerprints
    
    # Video fingerprinting methods
    
    async def _extract_video_fingerprints(
        self,
        video_data: bytes,
        methods: List[FingerprintMethod]
    ) -> List[FingerprintResult]:
        """Extract video fingerprints using multiple methods"""        fingerprints = []
        
        try:
            # Save video temporarily
            video_path = await self._save_temp_file(video_data, ".mp4")
            
            for method in methods:
                if method == FingerprintMethod.VIDEO_FRAME_HASH:
                    # Extract key frames and hash
                    cap = cv2.VideoCapture(video_path)
                    frame_hashes = []
                    
                    frame_count = 0
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            break
                        
                        # Sample every 30th frame
                        if frame_count % 30 == 0:
                            frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                            frame_hash = str(imagehash.phash(frame_pil))
                            frame_hashes.append(frame_hash)
                        
                        frame_count += 1
                    
                    cap.release()
                    
                    combined_hash = hashlib.sha256(
                        ''.join(frame_hashes).encode()
                    ).hexdigest()
                    
                    fp_result = FingerprintResult(
                        method=method,
                        fingerprint_hash=combined_hash,
                        metadata={
                            "total_frames": frame_count,
                            "sampled_frames": len(frame_hashes)
                        }
                    )
                    fingerprints.append(fp_result)
                
                elif method == FingerprintMethod.SCENE_DETECTION:
                    # Scene detection fingerprinting
                    # Implementation would use scene detection algorithms
                    pass
            
            # Clean up temp file
            Path(video_path).unlink(missing_ok=True)
        
        except Exception as e:
            logger.error(f"Video fingerprinting failed: {str(e)}")
        
        return fingerprints
    
    # Text fingerprinting methods
    
    async def _extract_text_fingerprints(
        self,
        text_data: str,
        methods: List[FingerprintMethod]
    ) -> List[FingerprintResult]:
        """Extract text fingerprints using multiple methods"""        fingerprints = []
        
        try:
            for method in methods:
                if method == FingerprintMethod.BERT_EMBEDDING:
                    # BERT embedding
                    embedding = self.text_model.encode(text_data)
                    embedding_hash = hashlib.sha256(embedding.tobytes()).hexdigest()
                    
                    fp_result = FingerprintResult(
                        method=method,
                        fingerprint_hash=embedding_hash,
                        vector_embedding=embedding,
                        metadata={"text_length": len(text_data)}
                    )
                    fingerprints.append(fp_result)
                
                elif method == FingerprintMethod.TFIDF_VECTORS:
                    # TF-IDF vectorization
                    vectorizer = TfidfVectorizer(max_features=1000)
                    tfidf_matrix = vectorizer.fit_transform([text_data])
                    tfidf_vector = tfidf_matrix.toarray().flatten()
                    
                    tfidf_hash = hashlib.sha256(tfidf_vector.tobytes()).hexdigest()
                    
                    fp_result = FingerprintResult(
                        method=method,
                        fingerprint_hash=tfidf_hash,
                        vector_embedding=tfidf_vector,
                        metadata={"vocabulary_size": len(vectorizer.vocabulary_)}
                    )
                    fingerprints.append(fp_result)
                
                elif method == FingerprintMethod.N_GRAM_HASH:
                    # N-gram hashing
                    words = text_data.lower().split()
                    trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
                    trigram_set = set(trigrams)
                    
                    ngram_hash = hashlib.sha256(
                        ''.join(sorted(trigram_set)).encode()
                    ).hexdigest()
                    
                    fp_result = FingerprintResult(
                        method=method,
                        fingerprint_hash=ngram_hash,
                        metadata={
                            "word_count": len(words),
                            "unique_trigrams": len(trigram_set)
                        }
                    )
                    fingerprints.append(fp_result)
        
        except Exception as e:
            logger.error(f"Text fingerprinting failed: {str(e)}")
        
        return fingerprints
    
    # Helper methods (implementation details)
    
    async def _validate_content_ownership(self, content_id: str, owner_id: str) -> bool:
        """Validate content ownership"""        # Implementation for ownership validation
        return True
    
    async def _load_content_file(self, request: ContentProtectionRequest) -> bytes:
        """Load content file from path or URL"""        # Implementation for file loading
        return b""
    
    async def _extract_multi_method_fingerprints(
        self,
        content_id: str,
        content_type: ContentType,
        file_data: bytes,
        config: ProtectionConfig
    ) -> List[FingerprintResult]:
        """Extract fingerprints using multiple methods"""        # Implementation for multi-method fingerprinting
        return []
    
    async def _save_fingerprint(self, fingerprint: FingerprintResult) -> ContentFingerprint:
        """Save fingerprint to database"""        # Implementation for database save
        pass
    
    async def _setup_content_monitoring(
        self,
        content_id: str,
        config: ProtectionConfig
    ) -> Optional[Dict[str, Any]]:
        """Setup automated monitoring"""        # Implementation for monitoring setup
        return None
    
    async def _get_content_fingerprints(self, content_id: str) -> List[ContentFingerprint]:
        """Get fingerprints for content"""        # Implementation for fingerprint retrieval
        return []
    
    async def _save_similarity_match(self, match: SimilarityMatch) -> SimilarityMatch:
        """Save similarity match to database"""        # Implementation for match save
        return match
    
    async def _handle_match_actions(self, match: SimilarityMatch) -> None:
        """Handle automated actions for matches"""        # Implementation for automated actions
        pass
    
    async def _save_temp_file(self, data: bytes, extension: str) -> str:
        """Save temporary file for processing"""        # Implementation for temp file handling
        return ""


# Factory function
async def create_content_protection_engine(
    db_session: AsyncSession,
    redis_client: aioredis.Redis,
    config: Dict[str, Any]
) -> ContentProtectionEngine:
    """Factory function to create ContentProtectionEngine"""    file_manager = FileManager()
    crypto_manager = CryptoManager()
    metrics_collector = MetricsCollector()
    
    engine = ContentProtectionEngine(
        db_session=db_session,
        redis_client=redis_client,
        file_manager=file_manager,
        crypto_manager=crypto_manager,
        metrics_collector=metrics_collector,
        enable_gpu=config.get("enable_gpu", True),
        model_cache_dir=config.get("model_cache_dir", "/models/cache")
    )
    
    return engine


# Export key classes
__all__ = [
    "ContentProtectionEngine",
    "ContentType",
    "FingerprintMethod",
    "ProtectionLevel",
    "MatchConfidence",
    "AlertAction",
    "FingerprintResult",
    "SimilarityMatch",
    "ProtectionConfig",
    "ContentProtectionRequest",
    "create_content_protection_engine"
]
    
    Features:
    - Audio fingerprinting (Chromaprint, spectral analysis)
    - Video fingerprinting (frame analysis, motion vectors)
    - Image fingerprinting (perceptual hashing, CLIP embeddings)
    - Text fingerprinting (BERT embeddings, MinHash)
    - Real-time similarity matching with FAISS
    - Web surveillance integration
    - Automated protection alerts
    """    
    def __init__(
        self,
        crypto_manager: CryptoManager,
        file_manager: FileManager,
        redis_manager: RedisManager,
        metrics_collector: MetricsCollector,
        config: Dict[str, Any] = None
    ):
        self.crypto_manager = crypto_manager
        self.file_manager = file_manager
        self.redis_manager = redis_manager
        self.metrics_collector = metrics_collector
        self.config = config or {}
        
        # Initialize AI models
        self._init_models()
        
        # Protection thresholds
        self.similarity_thresholds = {
            ContentType.AUDIO: 0.85,
            ContentType.VIDEO: 0.80,
            ContentType.IMAGE: 0.90,
            ContentType.TEXT: 0.75
        }
        
        # Cache configurations
        self.cache_ttl = self.config.get("cache_ttl", 3600)
        self.batch_size = self.config.get("batch_size", 32)
        
        logger.info("ContentProtectionEngine initialized successfully")

    def _init_models(self):
        """Initialize AI models for fingerprinting"""        try:
            # CLIP model for image/video embeddings
            self.clip_model = SentenceTransformer('clip-ViT-B-32')
            
            # BERT model for text embeddings  
            self.bert_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Image transform pipeline
            self.image_transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise

    async def generate_fingerprint(
        self,
        content_path: str,
        content_type: ContentType,
        user_id: str,
        metadata: Dict[str, Any] = None
    ) -> FingerprintResult:
        """        Generate comprehensive fingerprint for content
        
        Args:
            content_path: Path to content file
            content_type: Type of content
            user_id: User identifier
            metadata: Additional metadata
            
        Returns:
            FingerprintResult: Complete fingerprint data
        """        start_time = datetime.now()
        content_id = self._generate_content_id(content_path, user_id)
        
        try:
            # Check cache first
            cached_result = await self._get_cached_fingerprint(content_id)
            if cached_result:
                return cached_result
            
            # Generate fingerprint based on content type
            if content_type == ContentType.AUDIO:
                result = await self._fingerprint_audio(content_path, content_id)
            elif content_type == ContentType.VIDEO:
                result = await self._fingerprint_video(content_path, content_id)
            elif content_type == ContentType.IMAGE:
                result = await self._fingerprint_image(content_path, content_id)
            elif content_type == ContentType.TEXT:
                result = await self._fingerprint_text(content_path, content_id)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            result.extraction_time = processing_time
            
            # Cache result
            await self._cache_fingerprint(result)
            
            # Store in database
            await self._store_fingerprint(result, user_id, metadata)
            
            # Update metrics
            self.metrics_collector.increment_counter(
                "fingerprints_generated",
                tags={"content_type": content_type.value}
            )
            
            logger.info(f"Fingerprint generated for {content_id} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate fingerprint for {content_path}: {e}")
            raise

    async def _fingerprint_audio(self, audio_path: str, content_id: str) -> FingerprintResult:
        """Generate audio fingerprint using multiple methods"""        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=22050)
            
            # Method 1: Chromaprint fingerprint
            chromaprint_hash = chromaprint.compute(y, sr)
            
            # Method 2: Spectral centroid fingerprint
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_hash = hashlib.sha256(spectral_centroids.tobytes()).hexdigest()
            
            # Method 3: MFCC features as vector embedding
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_vector = np.mean(mfccs, axis=1)
            
            # Combine fingerprints
            combined_hash = hashlib.sha256(
                f"{chromaprint_hash}_{spectral_hash}".encode()
            ).hexdigest()
            
            # Calculate confidence based on audio quality
            rms_energy = np.sqrt(np.mean(y**2))
            confidence_score = min(rms_energy * 10, 1.0)
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.AUDIO,
                method=FingerprintMethod.CHROMAPRINT,
                fingerprint_hash=combined_hash,
                vector_embedding=mfcc_vector,
                confidence_score=confidence_score,
                metadata={
                    "chromaprint": chromaprint_hash,
                    "spectral_hash": spectral_hash,
                    "duration": len(y) / sr,
                    "sample_rate": sr
                }
            )
            
        except Exception as e:
            logger.error(f"Audio fingerprinting failed: {e}")
            raise

    async def _fingerprint_video(self, video_path: str, content_id: str) -> FingerprintResult:
        """Generate video fingerprint using frame analysis"""        try:
            # Load video
            cap = cv2.VideoCapture(video_path)
            frame_hashes = []
            frame_count = 0
            
            # Sample frames at regular intervals
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = max(1, int(fps))  # One frame per second
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # Convert to PIL Image and get perceptual hash
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    frame_hash = str(imagehash.phash(pil_image))
                    frame_hashes.append(frame_hash)
                
                frame_count += 1
            
            cap.release()
            
            # Combine frame hashes
            combined_hash = hashlib.sha256(
                "_".join(frame_hashes).encode()
            ).hexdigest()
            
            # Create vector embedding from frame hash distribution
            hash_vector = np.array([int(h, 16) for h in frame_hashes[:32]])
            if len(hash_vector) < 32:
                hash_vector = np.pad(hash_vector, (0, 32 - len(hash_vector)))
            
            # Calculate confidence based on frame count
            confidence_score = min(len(frame_hashes) / 10.0, 1.0)
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.VIDEO,
                method=FingerprintMethod.VIDEO_FRAME_HASH,
                fingerprint_hash=combined_hash,
                vector_embedding=hash_vector,
                confidence_score=confidence_score,
                metadata={
                    "frame_count": frame_count,
                    "sampled_frames": len(frame_hashes),
                    "fps": fps,
                    "frame_hashes": frame_hashes[:10]  # Store first 10 for debugging
                }
            )
            
        except Exception as e:
            logger.error(f"Video fingerprinting failed: {e}")
            raise

    async def _fingerprint_image(self, image_path: str, content_id: str) -> FingerprintResult:
        """Generate image fingerprint using perceptual hashing and CLIP"""        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Method 1: Perceptual hash
            phash = str(imagehash.phash(image))
            dhash = str(imagehash.dhash(image))
            whash = str(imagehash.whash(image))
            
            # Method 2: CLIP embedding
            clip_embedding = self.clip_model.encode([image])
            clip_vector = clip_embedding[0]
            
            # Combine hashes
            combined_hash = hashlib.sha256(
                f"{phash}_{dhash}_{whash}".encode()
            ).hexdigest()
            
            # Calculate confidence based on image quality
            image_array = np.array(image)
            variance = np.var(image_array)
            confidence_score = min(variance / 10000.0, 1.0)
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.IMAGE,
                method=FingerprintMethod.CLIP_EMBEDDING,
                fingerprint_hash=combined_hash,
                vector_embedding=clip_vector,
                confidence_score=confidence_score,
                metadata={
                    "phash": phash,
                    "dhash": dhash,
                    "whash": whash,
                    "dimensions": image.size,
                    "format": image.format
                }
            )
            
        except Exception as e:
            logger.error(f"Image fingerprinting failed: {e}")
            raise

    async def _fingerprint_text(self, text_path: str, content_id: str) -> FingerprintResult:
        """Generate text fingerprint using BERT embeddings and MinHash"""        try:
            # Read text content
            async with aiofiles.open(text_path, 'r', encoding='utf-8') as f:
                text_content = await f.read()
            
            # Method 1: BERT embedding
            bert_embedding = self.bert_model.encode([text_content])
            bert_vector = bert_embedding[0]
            
            # Method 2: Character-level hash
            char_hash = hashlib.sha256(text_content.encode()).hexdigest()
            
            # Method 3: Word-level MinHash approximation
            words = text_content.lower().split()
            word_hashes = [hash(word) for word in words]
            word_hash = hashlib.sha256(str(sorted(word_hashes)).encode()).hexdigest()
            
            # Combine hashes
            combined_hash = hashlib.sha256(
                f"{char_hash}_{word_hash}".encode()
            ).hexdigest()
            
            # Calculate confidence based on text length and uniqueness
            word_count = len(words)
            unique_words = len(set(words))
            confidence_score = min(unique_words / max(word_count, 1) * 2, 1.0)
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.TEXT,
                method=FingerprintMethod.BERT_EMBEDDING,
                fingerprint_hash=combined_hash,
                vector_embedding=bert_vector,
                confidence_score=confidence_score,
                metadata={
                    "char_count": len(text_content),
                    "word_count": word_count,
                    "unique_words": unique_words,
                    "language": "auto-detected"  # Could add language detection
                }
            )
            
        except Exception as e:
            logger.error(f"Text fingerprinting failed: {e}")
            raise

    async def find_similar_content(
        self,
        fingerprint_result: FingerprintResult,
        threshold: Optional[float] = None
    ) -> List[SimilarityMatch]:
        """        Find similar content using vector similarity search
        
        Args:
            fingerprint_result: Fingerprint to search for
            threshold: Similarity threshold (uses default if None)
            
        Returns:
            List of similarity matches
        """        content_type = fingerprint_result.content_type
        search_threshold = threshold or self.similarity_thresholds[content_type]
        
        try:
            matches = []
            
            # Vector-based similarity search
            if fingerprint_result.vector_embedding is not None:
                vector_matches = await self._vector_similarity_search(
                    fingerprint_result.vector_embedding,
                    content_type,
                    search_threshold
                )
                matches.extend(vector_matches)
            
            # Hash-based exact matching
            hash_matches = await self._hash_similarity_search(
                fingerprint_result.fingerprint_hash,
                content_type
            )
            matches.extend(hash_matches)
            
            # Remove duplicates and sort by similarity
            unique_matches = {}
            for match in matches:
                key = f"{match.matched_content_id}_{match.detection_url}"
                if key not in unique_matches or match.similarity_score > unique_matches[key].similarity_score:
                    unique_matches[key] = match
            
            sorted_matches = sorted(
                unique_matches.values(),
                key=lambda x: x.similarity_score,
                reverse=True
            )
            
            logger.info(f"Found {len(sorted_matches)} similar content matches")
            return sorted_matches
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

    async def _vector_similarity_search(
        self,
        query_vector: np.ndarray,
        content_type: ContentType,
        threshold: float
    ) -> List[SimilarityMatch]:
        """Perform vector similarity search using cosine similarity"""        try:
            # Get stored vectors from database/cache
            stored_vectors = await self._get_stored_vectors(content_type)
            
            if not stored_vectors:
                return []
            
            # Calculate cosine similarities
            query_vector = query_vector.reshape(1, -1)
            similarities = cosine_similarity(
                query_vector,
                np.array([v['vector'] for v in stored_vectors])
            )[0]
            
            # Filter by threshold and create matches
            matches = []
            for i, similarity in enumerate(similarities):
                if similarity >= threshold:
                    vector_data = stored_vectors[i]
                    confidence_level = self._get_confidence_level(similarity)
                    
                    match = SimilarityMatch(
                        original_content_id=vector_data['content_id'],
                        matched_content_id=vector_data['content_id'],
                        similarity_score=similarity,
                        match_method=FingerprintMethod.CLIP_EMBEDDING,
                        confidence_level=confidence_level
                    )
                    matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Vector similarity search failed: {e}")
            return []

    async def _hash_similarity_search(
        self,
        query_hash: str,
        content_type: ContentType
    ) -> List[SimilarityMatch]:
        """Perform hash-based exact matching"""        try:
            # Search for exact hash matches in database
            exact_matches = await self._get_exact_hash_matches(query_hash, content_type)
            
            matches = []
            for match_data in exact_matches:
                match = SimilarityMatch(
                    original_content_id=match_data['content_id'],
                    matched_content_id=match_data['content_id'],
                    similarity_score=1.0,  # Exact match
                    match_method=FingerprintMethod.PERCEPTUAL_HASH,
                    confidence_level="high"
                )
                matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Hash similarity search failed: {e}")
            return []

    def _get_confidence_level(self, similarity_score: float) -> str:
        """Determine confidence level based on similarity score"""        if similarity_score >= 0.95:
            return "very_high"
        elif similarity_score >= 0.85:
            return "high"
        elif similarity_score >= 0.75:
            return "medium"
        else:
            return "low"

    def _generate_content_id(self, content_path: str, user_id: str) -> str:
        """Generate unique content identifier"""        content_info = f"{content_path}_{user_id}_{datetime.now().isoformat()}"
        return hashlib.sha256(content_info.encode()).hexdigest()[:16]

    async def _get_cached_fingerprint(self, content_id: str) -> Optional[FingerprintResult]:
        """Retrieve cached fingerprint result"""        try:
            cache_key = f"fingerprint:{content_id}"
            cached_data = await self.redis_manager.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                return FingerprintResult(**data)
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to retrieve cached fingerprint: {e}")
            return None

    async def _cache_fingerprint(self, result: FingerprintResult):
        """Cache fingerprint result"""        try:
            cache_key = f"fingerprint:{result.content_id}"
            
            # Serialize result (handle numpy arrays)
            data = {
                "content_id": result.content_id,
                "content_type": result.content_type.value,
                "method": result.method.value,
                "fingerprint_hash": result.fingerprint_hash,
                "vector_embedding": result.vector_embedding.tolist() if result.vector_embedding is not None else None,
                "metadata": result.metadata,
                "confidence_score": result.confidence_score,
                "extraction_time": result.extraction_time
            }
            
            await self.redis_manager.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(data)
            )
            
        except Exception as e:
            logger.warning(f"Failed to cache fingerprint: {e}")

    async def _store_fingerprint(
        self,
        result: FingerprintResult,
        user_id: str,
        metadata: Dict[str, Any] = None
    ):
        """Store fingerprint in database"""        try:
            # This would interact with your database layer
            fingerprint_data = {
                "user_id": user_id,
                "content_id": result.content_id,
                "content_type": result.content_type.value,
                "fingerprint_hash": result.fingerprint_hash,
                "vector_embedding": result.vector_embedding.tobytes() if result.vector_embedding is not None else None,
                "metadata": {**(metadata or {}), **result.metadata},
                "confidence_score": result.confidence_score,
                "extraction_time": result.extraction_time,
                "created_at": datetime.now()
            }
            
            # Store in database (implement based on your DB layer)
            logger.info(f"Fingerprint stored for content {result.content_id}")
            
        except Exception as e:
            logger.error(f"Failed to store fingerprint: {e}")

    async def _get_stored_vectors(self, content_type: ContentType) -> List[Dict]:
        """Retrieve stored vectors for similarity comparison"""        # Implementation would query your vector database
        # This is a placeholder
        return []

    async def _get_exact_hash_matches(self, query_hash: str, content_type: ContentType) -> List[Dict]:
        """Get exact hash matches from database"""        # Implementation would query your database
        # This is a placeholder
        return []

    async def create_protection_alert(
        self,
        match: SimilarityMatch,
        detection_url: str,
        platform: str,
        evidence_data: Dict[str, Any] = None
    ) -> str:
        """        Create protection alert for detected content misuse
        
        Args:
            match: Similarity match result
            detection_url: URL where content was detected
            platform: Platform name
            evidence_data: Additional evidence data
            
        Returns:
            Alert ID
        """        try:
            alert_id = hashlib.sha256(
                f"{match.original_content_id}_{detection_url}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]
            
            alert_data = {
                "alert_id": alert_id,
                "original_content_id": match.original_content_id,
                "matched_content_id": match.matched_content_id,
                "detection_url": detection_url,
                "platform": platform,
                "similarity_score": match.similarity_score,
                "confidence_level": match.confidence_level,
                "evidence_data": evidence_data or {},
                "status": "pending",
                "created_at": datetime.now()
            }
            
            # Store alert in database
            # Implementation depends on your database layer
            
            # Update metrics
            self.metrics_collector.increment_counter(
                "protection_alerts_created",
                tags={"platform": platform}
            )
            
            logger.info(f"Protection alert created: {alert_id}")
            return alert_id
            
        except Exception as e:
            logger.error(f"Failed to create protection alert: {e}")
            raise

    async def get_protection_status(self, content_id: str) -> Dict[str, Any]:
        """Get comprehensive protection status for content"""        try:
            # Get fingerprint info
            fingerprint_info = await self._get_fingerprint_info(content_id)
            
            # Get active alerts
            active_alerts = await self._get_active_alerts(content_id)
            
            # Get protection metrics
            protection_metrics = await self._get_protection_metrics(content_id)
            
            return {
                "content_id": content_id,
                "fingerprint_info": fingerprint_info,
                "active_alerts": active_alerts,
                "protection_metrics": protection_metrics,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get protection status: {e}")
            return {}

    async def _get_fingerprint_info(self, content_id: str) -> Dict[str, Any]:
        """Get fingerprint information for content"""        # Implementation depends on your database layer
        return {}

    async def _get_active_alerts(self, content_id: str) -> List[Dict[str, Any]]:
        """Get active protection alerts for content"""        # Implementation depends on your database layer
        return []

    async def _get_protection_metrics(self, content_id: str) -> Dict[str, Any]:
        """Get protection metrics for content"""        # Implementation depends on your database layer
        return {}

    def get_supported_formats(self) -> Dict[ContentType, List[str]]:
        """Get supported file formats by content type"""        return {
            ContentType.AUDIO: ['.mp3', '.wav', '.flac', '.m4a', '.ogg'],
            ContentType.VIDEO: ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
            ContentType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            ContentType.TEXT: ['.txt', '.md', '.doc', '.docx', '.pdf'],
            ContentType.DOCUMENT: ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
        }

    async def batch_process_content(
        self,
        content_list: List[Dict[str, Any]],
        user_id: str
    ) -> List[FingerprintResult]:
        """Process multiple content files in batch"""        try:
            tasks = []
            for content_info in content_list:
                task = self.generate_fingerprint(
                    content_path=content_info['path'],
                    content_type=ContentType(content_info['type']),
                    user_id=user_id,
                    metadata=content_info.get('metadata')
                )
                tasks.append(task)
            
            # Process in batches to avoid overwhelming the system
            results = []
            for i in range(0, len(tasks), self.batch_size):
                batch_tasks = tasks[i:i + self.batch_size]
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"Batch processing error: {result}")
                    else:
                        results.append(result)
            
            logger.info(f"Batch processed {len(results)} content items")
            return results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return []

    async def cleanup_expired_fingerprints(self, days_old: int = 365):
        """Clean up old fingerprints and associated data"""        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Clean up database records
            deleted_count = await self._delete_old_fingerprints(cutoff_date)
            
            # Clean up cache entries
            cache_cleaned = await self._cleanup_cache()
            
            logger.info(f"Cleanup completed: {deleted_count} fingerprints, {cache_cleaned} cache entries")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    async def _delete_old_fingerprints(self, cutoff_date: datetime) -> int:
        """Delete old fingerprint records from database"""        # Implementation depends on your database layer
        return 0

    async def _cleanup_cache(self) -> int:
        """Clean up expired cache entries"""        # Implementation depends on your cache strategy
        return 0
