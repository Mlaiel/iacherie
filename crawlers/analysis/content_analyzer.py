"""Advanced Content Analyzer
==========================

Professional multi-modal content analysis system with AI-powered detection.
Implements comprehensive content analysis, fingerprinting, and violation detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""
import asyncio
import logging
import hashlib
import re
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from pathlib import Path
import aiofiles
import cv2
import librosa
import torch
from transformers import CLIPProcessor, CLIPModel, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import imagehash
from PIL import Image
import chromaprint
import soundfile as sf

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content type enumeration."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    SOCIAL_POST = "social_post"
    PODCAST = "podcast"
    STREAM = "stream"

class AnalysisStatus(Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class ThreatLevel(Enum):
    """Threat level enumeration."""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ContentFeatures:
    """Content feature extraction result."""
    content_id: str
    content_type: ContentType
    text_features: Optional[Dict[str, Any]] = None
    audio_features: Optional[Dict[str, Any]] = None
    video_features: Optional[Dict[str, Any]] = None
    image_features: Optional[Dict[str, Any]] = None
    metadata_features: Optional[Dict[str, Any]] = None
    extracted_at: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0

@dataclass
class AnalysisResult:
    """Comprehensive analysis result."""
    content_id: str
    analysis_id: str
    content_type: ContentType
    status: AnalysisStatus
    features: ContentFeatures
    threat_level: ThreatLevel
    confidence_score: float
    similarity_matches: List[Dict[str, Any]] = field(default_factory=list)
    violations: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0

class ContentAnalyzer:
    """
    Advanced content analyzer with AI-powered multi-modal detection.
    
    Features:
    - Multi-modal content analysis (audio, video, image, text)
    - AI-powered feature extraction using state-of-the-art models
    - Real-time similarity detection and violation assessment
    - Scalable architecture with async processing
    - Enterprise-grade security and performance optimization
    """
    
    def __init__(
        self,
        model_cache_dir: str = "/tmp/models",
        similarity_threshold: float = 0.85,
        enable_gpu: bool = True,
        max_concurrent_analyses: int = 10
    ):
        """
        Initialize content analyzer.
        
        Args:
            model_cache_dir: Directory for caching AI models
            similarity_threshold: Minimum similarity for violation detection
            enable_gpu: Enable GPU acceleration if available
            max_concurrent_analyses: Maximum concurrent analysis tasks
        """
        self.model_cache_dir = Path(model_cache_dir)
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.similarity_threshold = similarity_threshold
        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.max_concurrent_analyses = max_concurrent_analyses
        
        # Analysis tracking
        self.analysis_count = 0
        self.violation_count = 0
        self.processing_times = []
        
        # Feature databases
        self.feature_database = {}
        self.similarity_index = {}
        
        # Processing semaphore
        self.semaphore = asyncio.Semaphore(max_concurrent_analyses)
        
        # Initialize AI models
        self._initialize_models()
        
        logger.info(f"ContentAnalyzer initialized with GPU: {self.enable_gpu}")
    
    def _initialize_models(self) -> None:
        """Initialize AI models for content analysis."""
        try:
            # Text analysis models
            self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
            
            # Image analysis models
            self.clip_model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
            self.clip_processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
            
            # Move models to GPU if available
            if self.enable_gpu:
                self.clip_model = self.clip_model.cuda()
                
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
            raise
    
    async def analyze_content(
        self,
        content_id: str,
        content_data: Union[str, bytes, Path],
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        Analyze content for features, similarity, and violations.
        
        Args:
            content_id: Unique content identifier
            content_data: Content data (file path, URL, or raw data)
            content_type: Type of content being analyzed
            metadata: Additional metadata for analysis
            
        Returns:
            AnalysisResult: Comprehensive analysis result
        """
        async with self.semaphore:
            start_time = datetime.now()
            analysis_id = hashlib.sha256(f"{content_id}_{start_time}".encode()).hexdigest()[:16]
            
            try:
                # Extract features based on content type
                features = await self._extract_features(content_id, content_data, content_type)
                
                # Detect similarity matches
                similarity_matches = await self._detect_similarity(features)
                
                # Assess threat level and violations
                threat_level, violations = await self._assess_threats(features, similarity_matches)
                
                # Generate recommendations
                recommendations = self._generate_recommendations(features, threat_level, violations)
                
                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds()
                self.processing_times.append(processing_time)
                
                # Create analysis result
                result = AnalysisResult(
                    content_id=content_id,
                    analysis_id=analysis_id,
                    content_type=content_type,
                    status=AnalysisStatus.COMPLETED,
                    features=features,
                    threat_level=threat_level,
                    confidence_score=self._calculate_confidence(features, similarity_matches),
                    similarity_matches=similarity_matches,
                    violations=violations,
                    recommendations=recommendations,
                    metadata=metadata or {},
                    processing_time=processing_time
                )
                
                # Update statistics
                self.analysis_count += 1
                if threat_level != ThreatLevel.NONE:
                    self.violation_count += 1
                
                # Store features for future comparisons
                self.feature_database[content_id] = features
                await self._update_similarity_index(content_id, features)
                
                logger.info(f"Analysis completed for {content_id}: {threat_level.name}")
                return result
                
            except Exception as e:
                logger.error(f"Analysis failed for {content_id}: {e}")
                return AnalysisResult(
                    content_id=content_id,
                    analysis_id=analysis_id,
                    content_type=content_type,
                    status=AnalysisStatus.FAILED,
                    features=ContentFeatures(content_id, content_type),
                    threat_level=ThreatLevel.NONE,
                    confidence_score=0.0,
                    metadata={"error": str(e)},
                    processing_time=(datetime.now() - start_time).total_seconds()
                )
    
    async def _extract_features(
        self,
        content_id: str,
        content_data: Union[str, bytes, Path],
        content_type: ContentType
    ) -> ContentFeatures:
        """Extract features from content based on type."""
        start_time = datetime.now()
        features = ContentFeatures(content_id, content_type)
        
        try:
            if content_type == ContentType.TEXT or content_type == ContentType.SOCIAL_POST:
                features.text_features = await self._extract_text_features(content_data)
                
            elif content_type == ContentType.IMAGE:
                features.image_features = await self._extract_image_features(content_data)
                
            elif content_type == ContentType.AUDIO or content_type == ContentType.PODCAST:
                features.audio_features = await self._extract_audio_features(content_data)
                
            elif content_type == ContentType.VIDEO or content_type == ContentType.STREAM:
                features.video_features = await self._extract_video_features(content_data)
                features.audio_features = await self._extract_video_audio_features(content_data)
                
            # Always extract metadata features
            features.metadata_features = await self._extract_metadata_features(content_data, content_type)
            
            features.processing_time = (datetime.now() - start_time).total_seconds()
            
        except Exception as e:
            logger.error(f"Feature extraction failed for {content_id}: {e}")
            
        return features
    
    async def _extract_text_features(self, text_data: Union[str, bytes]) -> Dict[str, Any]:
        """Extract features from text content."""
        if isinstance(text_data, bytes):
            text_data = text_data.decode('utf-8', errors='ignore')
        
        # Generate text embeddings
        embeddings = self.text_model.encode([text_data])[0]
        
        # Extract linguistic features
        word_count = len(text_data.split())
        char_count = len(text_data)
        
        # Extract n-grams
        words = text_data.lower().split()
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
        
        # Content hash
        content_hash = hashlib.sha256(text_data.encode()).hexdigest()
        
        return {
            "embeddings": embeddings.tolist(),
            "content_hash": content_hash,
            "word_count": word_count,
            "char_count": char_count,
            "bigrams": bigrams[:50],  # Limit to top 50
            "trigrams": trigrams[:30],  # Limit to top 30
            "language_detected": self._detect_language(text_data),
            "sentiment_score": self._calculate_sentiment(text_data),
            "readability_score": self._calculate_readability(text_data)
        }
    
    async def _extract_image_features(self, image_data: Union[str, bytes, Path]) -> Dict[str, Any]:
        """Extract features from image content."""
        try:
            # Load image
            if isinstance(image_data, (str, Path)):
                image = Image.open(image_data)
            else:
                from io import BytesIO
                image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract CLIP features
            inputs = self.clip_processor(images=image, return_tensors="pt")
            if self.enable_gpu:
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                clip_embeddings = image_features.cpu().numpy().flatten()
            
            # Extract perceptual hashes
            phash = str(imagehash.phash(image))
            dhash = str(imagehash.dhash(image))
            whash = str(imagehash.whash(image))
            
            # Extract basic image properties
            width, height = image.size
            aspect_ratio = width / height
            
            # Color analysis
            colors = image.getcolors(maxcolors=256*256*256)
            dominant_colors = sorted(colors, key=lambda x: x[0], reverse=True)[:5] if colors else []
            
            return {
                "clip_embeddings": clip_embeddings.tolist(),
                "perceptual_hash": phash,
                "difference_hash": dhash,
                "wavelet_hash": whash,
                "width": width,
                "height": height,
                "aspect_ratio": aspect_ratio,
                "dominant_colors": [color[1] for color in dominant_colors],
                "file_size": len(image_data) if isinstance(image_data, bytes) else None,
                "format": image.format
            }
            
        except Exception as e:
            logger.error(f"Image feature extraction failed: {e}")
            return {}
    
    async def _extract_audio_features(self, audio_data: Union[str, bytes, Path]) -> Dict[str, Any]:
        """Extract features from audio content."""
        try:
            # Load audio
            if isinstance(audio_data, (str, Path)):
                y, sr = librosa.load(audio_data)
            else:
                # Handle bytes data
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                    tmp.write(audio_data)
                    tmp.flush()
                    y, sr = librosa.load(tmp.name)
            
            # Extract chromaprint fingerprint
            try:
                fingerprint = chromaprint.encode(y, sr)
            except:
                fingerprint = None
            
            # Extract spectral features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
            
            # Tempo and beat detection
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Audio properties
            duration = len(y) / sr
            rms_energy = np.sqrt(np.mean(y**2))
            
            return {
                "chromaprint": fingerprint,
                "mfccs": mfccs.mean(axis=1).tolist(),
                "spectral_centroid": float(spectral_centroids.mean()),
                "spectral_rolloff": float(spectral_rolloff.mean()),
                "zero_crossing_rate": float(zero_crossing_rate.mean()),
                "tempo": float(tempo),
                "duration": duration,
                "sample_rate": sr,
                "rms_energy": float(rms_energy),
                "beat_count": len(beats)
            }
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            return {}
    
    async def _extract_video_features(self, video_data: Union[str, Path]) -> Dict[str, Any]:
        """Extract features from video content."""
        try:
            # Open video
            cap = cv2.VideoCapture(str(video_data))
            
            if not cap.isOpened():
                return {}
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Sample frames for analysis
            sample_frames = []
            frame_interval = max(1, frame_count // 10)  # Sample 10 frames
            
            for i in range(0, frame_count, frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    # Convert to RGB and resize for efficiency
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_resized = cv2.resize(frame_rgb, (224, 224))
                    sample_frames.append(frame_resized)
            
            cap.release()
            
            # Extract CLIP features from sample frames
            frame_features = []
            for frame in sample_frames[:5]:  # Limit to 5 frames
                frame_pil = Image.fromarray(frame)
                inputs = self.clip_processor(images=frame_pil, return_tensors="pt")
                if self.enable_gpu:
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                
                with torch.no_grad():
                    features = self.clip_model.get_image_features(**inputs)
                    frame_features.append(features.cpu().numpy().flatten())
            
            # Average frame features
            avg_features = np.mean(frame_features, axis=0) if frame_features else np.array([])
            
            return {
                "clip_embeddings": avg_features.tolist(),
                "duration": duration,
                "fps": fps,
                "frame_count": frame_count,
                "width": width,
                "height": height,
                "aspect_ratio": width / height if height > 0 else 0,
                "sample_frame_count": len(sample_frames),
                "estimated_size": width * height * frame_count
            }
            
        except Exception as e:
            logger.error(f"Video feature extraction failed: {e}")
            return {}
    
    async def _extract_video_audio_features(self, video_data: Union[str, Path]) -> Dict[str, Any]:
        """Extract audio features from video content."""
        try:
            # Extract audio from video using librosa
            y, sr = librosa.load(str(video_data))
            
            # Use existing audio feature extraction
            return await self._extract_audio_features(y)
            
        except Exception as e:
            logger.warning(f"Video audio extraction failed: {e}")
            return {}
    
    async def _extract_metadata_features(
        self,
        content_data: Union[str, bytes, Path],
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Extract metadata features from content."""
        metadata = {
            "content_type": content_type.value,
            "extracted_at": datetime.now().isoformat(),
            "data_type": type(content_data).__name__
        }
        
        if isinstance(content_data, (str, Path)):
            path = Path(content_data)
            if path.exists():
                stat = path.stat()
                metadata.update({
                    "file_size": stat.st_size,
                    "file_extension": path.suffix.lower(),
                    "file_name": path.name,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        elif isinstance(content_data, bytes):
            metadata["data_size"] = len(content_data)
        
        return metadata
    
    async def _detect_similarity(self, features: ContentFeatures) -> List[Dict[str, Any]]:
        """Detect similarity with existing content."""
        matches = []
        
        for existing_id, existing_features in self.feature_database.items():
            if existing_features.content_type == features.content_type:
                similarity_score = self._calculate_similarity(features, existing_features)
                
                if similarity_score >= self.similarity_threshold:
                    matches.append({
                        "match_id": existing_id,
                        "similarity_score": similarity_score,
                        "match_type": "exact" if similarity_score > 0.95 else "similar",
                        "features_compared": self._get_compared_features(features, existing_features)
                    })
        
        return sorted(matches, key=lambda x: x["similarity_score"], reverse=True)
    
    def _calculate_similarity(self, features1: ContentFeatures, features2: ContentFeatures) -> float:
        """Calculate similarity between two content features."""
        if features1.content_type != features2.content_type:
            return 0.0
        
        similarities = []
        
        # Text similarity
        if features1.text_features and features2.text_features:
            emb1 = np.array(features1.text_features.get("embeddings", []))
            emb2 = np.array(features2.text_features.get("embeddings", []))
            if len(emb1) > 0 and len(emb2) > 0:
                text_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                similarities.append(text_sim)
        
        # Image similarity
        if features1.image_features and features2.image_features:
            emb1 = np.array(features1.image_features.get("clip_embeddings", []))
            emb2 = np.array(features2.image_features.get("clip_embeddings", []))
            if len(emb1) > 0 and len(emb2) > 0:
                img_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                similarities.append(img_sim)
        
        # Audio similarity
        if features1.audio_features and features2.audio_features:
            mfcc1 = np.array(features1.audio_features.get("mfccs", []))
            mfcc2 = np.array(features2.audio_features.get("mfccs", []))
            if len(mfcc1) > 0 and len(mfcc2) > 0:
                audio_sim = np.dot(mfcc1, mfcc2) / (np.linalg.norm(mfcc1) * np.linalg.norm(mfcc2))
                similarities.append(audio_sim)
        
        return float(np.mean(similarities)) if similarities else 0.0
    
    def _get_compared_features(self, features1: ContentFeatures, features2: ContentFeatures) -> List[str]:
        """Get list of features that were compared."""
        compared = []
        
        if features1.text_features and features2.text_features:
            compared.append("text_embeddings")
        if features1.image_features and features2.image_features:
            compared.append("image_embeddings")
        if features1.audio_features and features2.audio_features:
            compared.append("audio_features")
        if features1.video_features and features2.video_features:
            compared.append("video_features")
        
        return compared
    
    async def _assess_threats(
        self,
        features: ContentFeatures,
        similarity_matches: List[Dict[str, Any]]
    ) -> Tuple[ThreatLevel, List[Dict[str, Any]]]:
        """Assess threat level and identify violations."""
        violations = []
        
        # Check for exact matches (potential copyright violation)
        exact_matches = [m for m in similarity_matches if m["similarity_score"] > 0.95]
        if exact_matches:
            violations.extend([{
                "type": "copyright_infringement",
                "severity": "high",
                "evidence": match,
                "description": f"Exact match detected with similarity {match['similarity_score']:.2%}"
            } for match in exact_matches])
        
        # Check for high similarity (potential derivative work)
        high_similarity = [m for m in similarity_matches if 0.85 <= m["similarity_score"] <= 0.95]
        if high_similarity:
            violations.extend([{
                "type": "derivative_work",
                "severity": "medium",
                "evidence": match,
                "description": f"High similarity detected: {match['similarity_score']:.2%}"
            } for match in high_similarity])
        
        # Determine threat level
        if exact_matches:
            threat_level = ThreatLevel.CRITICAL
        elif len(high_similarity) > 3:
            threat_level = ThreatLevel.HIGH
        elif len(high_similarity) > 0:
            threat_level = ThreatLevel.MEDIUM
        elif len(similarity_matches) > 0:
            threat_level = ThreatLevel.LOW
        else:
            threat_level = ThreatLevel.NONE
        
        return threat_level, violations
    
    def _generate_recommendations(
        self,
        features: ContentFeatures,
        threat_level: ThreatLevel,
        violations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        if threat_level == ThreatLevel.CRITICAL:
            recommendations.extend([
                "Immediate action required: Potential copyright infringement detected",
                "Contact legal team for DMCA takedown request",
                "Document all evidence for potential legal proceedings",
                "Monitor for additional violations across platforms"
            ])
        
        elif threat_level == ThreatLevel.HIGH:
            recommendations.extend([
                "High risk content detected - investigate immediately",
                "Review content licensing and usage rights",
                "Consider watermarking or additional protection measures",
                "Increase monitoring frequency for this content"
            ])
        
        elif threat_level == ThreatLevel.MEDIUM:
            recommendations.extend([
                "Moderate similarity detected - review content usage",
                "Verify licensing agreements and permissions",
                "Consider additional content protection measures"
            ])
        
        elif threat_level == ThreatLevel.LOW:
            recommendations.append("Low risk detected - continue standard monitoring")
        
        return recommendations
    
    def _calculate_confidence(
        self,
        features: ContentFeatures,
        similarity_matches: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for the analysis."""
        confidence_factors = []
        
        # Feature completeness
        feature_count = sum([
            1 for f in [features.text_features, features.image_features, 
                       features.audio_features, features.video_features] if f
        ])
        feature_completeness = feature_count / 4
        confidence_factors.append(feature_completeness)
        
        # Match consistency
        if similarity_matches:
            scores = [m["similarity_score"] for m in similarity_matches]
            match_consistency = 1.0 - np.std(scores)
            confidence_factors.append(match_consistency)
        else:
            confidence_factors.append(1.0)  # High confidence when no matches
        
        # Model reliability (static factor for now)
        confidence_factors.append(0.9)
        
        return float(np.mean(confidence_factors))
    
    async def _update_similarity_index(self, content_id: str, features: ContentFeatures) -> None:
        """Update similarity index for faster future searches."""
        # This would integrate with a vector database like FAISS in production
        # For now, we'll just track in memory
        if features.text_features and "embeddings" in features.text_features:
            if "text" not in self.similarity_index:
                self.similarity_index["text"] = {}
            self.similarity_index["text"][content_id] = features.text_features["embeddings"]
        
        if features.image_features and "clip_embeddings" in features.image_features:
            if "image" not in self.similarity_index:
                self.similarity_index["image"] = {}
            self.similarity_index["image"][content_id] = features.image_features["clip_embeddings"]
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text content."""
        # Simplified language detection - in production use langdetect
        english_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from'}
        french_words = {'le', 'la', 'les', 'et', 'ou', 'mais', 'dans', 'sur', 'à', 'pour', 'de', 'avec', 'par'}
        german_words = {'der', 'die', 'das', 'und', 'oder', 'aber', 'in', 'auf', 'zu', 'für', 'von', 'mit', 'durch'}
        
        words = set(text.lower().split())
        
        en_score = len(words & english_words)
        fr_score = len(words & french_words)
        de_score = len(words & german_words)
        
        if en_score >= fr_score and en_score >= de_score:
            return "en"
        elif fr_score >= de_score:
            return "fr"
        else:
            return "de"
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score for text."""
        # Simplified sentiment analysis - in production use VADER or transformers
        positive_words = {'good', 'great', 'excellent', 'amazing', 'love', 'like', 'best', 'awesome'}
        negative_words = {'bad', 'terrible', 'awful', 'hate', 'dislike', 'worst', 'horrible'}
        
        words = set(text.lower().split())
        positive_count = len(words & positive_words)
        negative_count = len(words & negative_words)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score for text."""
        # Simplified Flesch Reading Ease score
        sentences = len([s for s in text.split('.') if s.strip()])
        words = len(text.split())
        syllables = sum([self._count_syllables(word) for word in text.split()])
        
        if sentences == 0 or words == 0:
            return 0.0
        
        score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        return max(0.0, min(100.0, score)) / 100.0  # Normalize to 0-1
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word."""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_char_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not previous_char_was_vowel:
                    syllable_count += 1
                previous_char_was_vowel = True
            else:
                previous_char_was_vowel = False
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    async def batch_analyze(
        self,
        content_batch: List[Tuple[str, Union[str, bytes, Path], ContentType, Optional[Dict[str, Any]]]]
    ) -> List[AnalysisResult]:
        """Analyze multiple content items in batch."""
        tasks = []
        
        for content_id, content_data, content_type, metadata in content_batch:
            task = asyncio.create_task(
                self.analyze_content(content_id, content_data, content_type, metadata)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        valid_results = [r for r in results if isinstance(r, AnalysisResult)]
        
        logger.info(f"Batch analyzed {len(valid_results)} out of {len(content_batch)} items")
        return valid_results
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics about the analyzer performance."""
        avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0
        
        return {
            "total_analyses": self.analysis_count,
            "violations_detected": self.violation_count,
            "violation_rate": self.violation_count / max(1, self.analysis_count),
            "average_processing_time": avg_processing_time,
            "feature_database_size": len(self.feature_database),
            "similarity_index_size": sum(len(idx) for idx in self.similarity_index.values()),
            "gpu_enabled": self.enable_gpu,
            "max_concurrent_analyses": self.max_concurrent_analyses,
            "processing_time_percentiles": {
                "p50": np.percentile(self.processing_times, 50) if self.processing_times else 0,
                "p90": np.percentile(self.processing_times, 90) if self.processing_times else 0,
                "p99": np.percentile(self.processing_times, 99) if self.processing_times else 0
            }
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources and models."""
        # Clear caches
        self.feature_database.clear()
        self.similarity_index.clear()
        self.processing_times.clear()
        
        # Clear GPU memory if using CUDA
        if self.enable_gpu and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("ContentAnalyzer cleanup completed")
