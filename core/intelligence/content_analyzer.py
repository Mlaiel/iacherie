"""Content Analyzer - Advanced Multi-Format Content Analysis Engine

Provides comprehensive content analysis capabilities for audio, video, image,
and text content. Integrates multiple AI models and feature extraction techniques
to understand content characteristics, quality, and potential for monetization.

Features:
- Multi-modal content analysis
- Quality assessment and scoring
- Monetization potential evaluation
- Content classification and tagging
- Similarity detection and matching
- Performance prediction analytics

Author: Fahed Mlaiel <mlaiel@live.de>
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime
import json

# ML/AI Libraries
import torch
import tensorflow as tf
from transformers import AutoModel, AutoTokenizer
import cv2
import librosa
from PIL import Image
import spacy

# Core Dependencies
from ..adapters.content_adapter import ContentAdapter
from ..processors.media_processor import MediaProcessor
from ..engines.ai_engine import AIEngine
from ..storage.vector_storage import VectorStorage


class ContentType(Enum):
    """Content type enumeration"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"


class QualityScore(Enum):
    """Quality scoring levels"""
    EXCELLENT = 90
    GOOD = 75
    AVERAGE = 60
    POOR = 40
    UNACCEPTABLE = 20


@dataclass
class ContentMetrics:
    """Content analysis metrics"""
    quality_score: float
    engagement_potential: float
    monetization_score: float
    virality_prediction: float
    content_type: ContentType
    tags: List[str]
    features: Dict[str, Any]
    analysis_timestamp: datetime


@dataclass
class AnalysisResult:
    """Comprehensive analysis result"""
    content_id: str
    metrics: ContentMetrics
    recommendations: List[str]
    optimization_suggestions: List[str]
    risk_assessment: Dict[str, float]
    revenue_prediction: float
    similar_content: List[str]
    processing_time: float


class ContentAnalyzer:
    """
    Advanced content analyzer for multi-format content processing
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the content analyzer
        
        Args:
            config: Configuration dictionary containing model paths and settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize models and processors
        self._initialize_models()
        self._initialize_processors()
        self._initialize_storage()
        
        # Performance tracking
        self.analysis_cache = {}
        self.performance_metrics = {
            "total_analyses": 0,
            "average_processing_time": 0.0,
            "cache_hit_rate": 0.0
        }
    
    def _initialize_models(self) -> None:
        """Initialize AI models for content analysis"""
        try:
            # Text analysis models
            self.text_model = AutoModel.from_pretrained(
                self.config.get("text_model", "sentence-transformers/all-MiniLM-L6-v2")
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.get("text_model", "sentence-transformers/all-MiniLM-L6-v2")
            )
            
            # NLP processor
            self.nlp = spacy.load("en_core_web_sm")
            
            # Vision models for image/video analysis
            self.vision_model = torch.hub.load(
                'pytorch/vision:v0.10.0', 
                'resnet50', 
                pretrained=True
            )
            self.vision_model.eval()
            
            # Audio analysis setup
            self.audio_sample_rate = self.config.get("audio_sample_rate", 22050)
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {e}")
            raise
    
    def _initialize_processors(self) -> None:
        """Initialize content processors"""
        self.content_adapter = ContentAdapter(self.config)
        self.media_processor = MediaProcessor(self.config)
        self.ai_engine = AIEngine(self.config)
    
    def _initialize_storage(self) -> None:
        """Initialize vector storage for similarity matching"""
        self.vector_storage = VectorStorage(self.config)
    
    async def analyze_content(
        self, 
        content_data: Union[str, bytes, np.ndarray],
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        Perform comprehensive content analysis
        
        Args:
            content_data: Raw content data (file path, bytes, or array)
            content_type: Type of content to analyze
            metadata: Additional metadata for analysis
            
        Returns:
            AnalysisResult: Comprehensive analysis results
        """
        start_time = datetime.now()
        content_id = self._generate_content_id(content_data, content_type)
        
        try:
            # Check cache first
            if content_id in self.analysis_cache:
                self.logger.info(f"Cache hit for content: {content_id}")
                return self.analysis_cache[content_id]
            
            # Route to appropriate analyzer
            if content_type == ContentType.AUDIO:
                result = await self._analyze_audio(content_data, metadata)
            elif content_type == ContentType.VIDEO:
                result = await self._analyze_video(content_data, metadata)
            elif content_type == ContentType.IMAGE:
                result = await self._analyze_image(content_data, metadata)
            elif content_type == ContentType.TEXT:
                result = await self._analyze_text(content_data, metadata)
            else:
                result = await self._analyze_mixed_content(content_data, metadata)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            result.content_id = content_id
            
            # Cache result
            self.analysis_cache[content_id] = result
            
            # Update performance metrics
            self._update_performance_metrics(processing_time)
            
            self.logger.info(f"Content analysis completed for {content_id} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Content analysis failed for {content_id}: {e}")
            raise
    
    async def _analyze_audio(
        self, 
        audio_data: Union[str, np.ndarray], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """Analyze audio content"""
        
        # Load audio if path provided
        if isinstance(audio_data, str):
            y, sr = librosa.load(audio_data, sr=self.audio_sample_rate)
        else:
            y, sr = audio_data, self.audio_sample_rate
        
        # Extract audio features
        features = self._extract_audio_features(y, sr)
        
        # Quality assessment
        quality_score = self._assess_audio_quality(y, sr, features)
        
        # Engagement prediction
        engagement_potential = self._predict_audio_engagement(features)
        
        # Monetization scoring
        monetization_score = self._calculate_monetization_potential(
            features, ContentType.AUDIO
        )
        
        # Virality prediction
        virality_prediction = self._predict_virality(features, ContentType.AUDIO)
        
        # Generate tags
        tags = self._generate_audio_tags(features)
        
        # Create metrics
        metrics = ContentMetrics(
            quality_score=quality_score,
            engagement_potential=engagement_potential,
            monetization_score=monetization_score,
            virality_prediction=virality_prediction,
            content_type=ContentType.AUDIO,
            tags=tags,
            features=features,
            analysis_timestamp=datetime.now()
        )
        
        # Generate recommendations
        recommendations = self._generate_audio_recommendations(metrics)
        optimization_suggestions = self._generate_optimization_suggestions(metrics)
        risk_assessment = self._assess_content_risks(metrics)
        revenue_prediction = self._predict_revenue(metrics)
        similar_content = await self._find_similar_content(features, ContentType.AUDIO)
        
        return AnalysisResult(
            content_id="",  # Will be set by caller
            metrics=metrics,
            recommendations=recommendations,
            optimization_suggestions=optimization_suggestions,
            risk_assessment=risk_assessment,
            revenue_prediction=revenue_prediction,
            similar_content=similar_content,
            processing_time=0.0  # Will be set by caller
        )
    
    async def _analyze_video(
        self, 
        video_data: Union[str, np.ndarray], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """Analyze video content"""
        
        # Extract video features
        features = await self._extract_video_features(video_data)
        
        # Quality assessment
        quality_score = self._assess_video_quality(features)
        
        # Engagement prediction
        engagement_potential = self._predict_video_engagement(features)
        
        # Monetization scoring
        monetization_score = self._calculate_monetization_potential(
            features, ContentType.VIDEO
        )
        
        # Virality prediction
        virality_prediction = self._predict_virality(features, ContentType.VIDEO)
        
        # Generate tags
        tags = self._generate_video_tags(features)
        
        # Create metrics
        metrics = ContentMetrics(
            quality_score=quality_score,
            engagement_potential=engagement_potential,
            monetization_score=monetization_score,
            virality_prediction=virality_prediction,
            content_type=ContentType.VIDEO,
            tags=tags,
            features=features,
            analysis_timestamp=datetime.now()
        )
        
        # Generate recommendations and assessments
        recommendations = self._generate_video_recommendations(metrics)
        optimization_suggestions = self._generate_optimization_suggestions(metrics)
        risk_assessment = self._assess_content_risks(metrics)
        revenue_prediction = self._predict_revenue(metrics)
        similar_content = await self._find_similar_content(features, ContentType.VIDEO)
        
        return AnalysisResult(
            content_id="",
            metrics=metrics,
            recommendations=recommendations,
            optimization_suggestions=optimization_suggestions,
            risk_assessment=risk_assessment,
            revenue_prediction=revenue_prediction,
            similar_content=similar_content,
            processing_time=0.0
        )
    
    async def _analyze_image(
        self, 
        image_data: Union[str, np.ndarray, Image.Image], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """Analyze image content"""
        
        # Load and preprocess image
        image = self._preprocess_image(image_data)
        
        # Extract image features
        features = self._extract_image_features(image)
        
        # Quality assessment
        quality_score = self._assess_image_quality(image, features)
        
        # Engagement prediction
        engagement_potential = self._predict_image_engagement(features)
        
        # Monetization scoring
        monetization_score = self._calculate_monetization_potential(
            features, ContentType.IMAGE
        )
        
        # Virality prediction
        virality_prediction = self._predict_virality(features, ContentType.IMAGE)
        
        # Generate tags
        tags = self._generate_image_tags(features)
        
        # Create metrics
        metrics = ContentMetrics(
            quality_score=quality_score,
            engagement_potential=engagement_potential,
            monetization_score=monetization_score,
            virality_prediction=virality_prediction,
            content_type=ContentType.IMAGE,
            tags=tags,
            features=features,
            analysis_timestamp=datetime.now()
        )
        
        # Generate recommendations and assessments
        recommendations = self._generate_image_recommendations(metrics)
        optimization_suggestions = self._generate_optimization_suggestions(metrics)
        risk_assessment = self._assess_content_risks(metrics)
        revenue_prediction = self._predict_revenue(metrics)
        similar_content = await self._find_similar_content(features, ContentType.IMAGE)
        
        return AnalysisResult(
            content_id="",
            metrics=metrics,
            recommendations=recommendations,
            optimization_suggestions=optimization_suggestions,
            risk_assessment=risk_assessment,
            revenue_prediction=revenue_prediction,
            similar_content=similar_content,
            processing_time=0.0
        )
    
    async def _analyze_text(
        self, 
        text_data: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """Analyze text content"""
        
        # Extract text features
        features = self._extract_text_features(text_data)
        
        # Quality assessment
        quality_score = self._assess_text_quality(text_data, features)
        
        # Engagement prediction
        engagement_potential = self._predict_text_engagement(features)
        
        # Monetization scoring
        monetization_score = self._calculate_monetization_potential(
            features, ContentType.TEXT
        )
        
        # Virality prediction
        virality_prediction = self._predict_virality(features, ContentType.TEXT)
        
        # Generate tags
        tags = self._generate_text_tags(features)
        
        # Create metrics
        metrics = ContentMetrics(
            quality_score=quality_score,
            engagement_potential=engagement_potential,
            monetization_score=monetization_score,
            virality_prediction=virality_prediction,
            content_type=ContentType.TEXT,
            tags=tags,
            features=features,
            analysis_timestamp=datetime.now()
        )
        
        # Generate recommendations and assessments
        recommendations = self._generate_text_recommendations(metrics)
        optimization_suggestions = self._generate_optimization_suggestions(metrics)
        risk_assessment = self._assess_content_risks(metrics)
        revenue_prediction = self._predict_revenue(metrics)
        similar_content = await self._find_similar_content(features, ContentType.TEXT)
        
        return AnalysisResult(
            content_id="",
            metrics=metrics,
            recommendations=recommendations,
            optimization_suggestions=optimization_suggestions,
            risk_assessment=risk_assessment,
            revenue_prediction=revenue_prediction,
            similar_content=similar_content,
            processing_time=0.0
        )
    
    async def _analyze_mixed_content(
        self, 
        content_data: Any, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """Analyze mixed/multi-modal content"""
        
        # This would handle complex multi-modal content analysis
        # For now, return a placeholder implementation
        features = {"mixed_content": True}
        
        metrics = ContentMetrics(
            quality_score=75.0,
            engagement_potential=70.0,
            monetization_score=65.0,
            virality_prediction=60.0,
            content_type=ContentType.MIXED,
            tags=["mixed", "multimodal"],
            features=features,
            analysis_timestamp=datetime.now()
        )
        
        return AnalysisResult(
            content_id="",
            metrics=metrics,
            recommendations=["Optimize mixed content for platform-specific formats"],
            optimization_suggestions=["Consider splitting into single-format content"],
            risk_assessment={"complexity": 0.3},
            revenue_prediction=5000.0,
            similar_content=[],
            processing_time=0.0
        )
    
    def _extract_audio_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract comprehensive audio features"""
        features = {}
        
        # Basic features
        features["duration"] = len(y) / sr
        features["sample_rate"] = sr
        
        # Spectral features
        features["mfcc"] = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).mean(axis=1).tolist()
        features["spectral_centroid"] = librosa.feature.spectral_centroid(y=y, sr=sr).mean()
        features["spectral_rolloff"] = librosa.feature.spectral_rolloff(y=y, sr=sr).mean()
        features["zero_crossing_rate"] = librosa.feature.zero_crossing_rate(y).mean()
        
        # Rhythm features
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        features["tempo"] = float(tempo)
        features["beat_count"] = len(beats)
        
        # Energy features
        features["rms_energy"] = librosa.feature.rms(y=y).mean()
        
        return features
    
    async def _extract_video_features(self, video_data: Union[str, np.ndarray]) -> Dict[str, Any]:
        """Extract comprehensive video features"""
        features = {}
        
        if isinstance(video_data, str):
            # Load video file
            cap = cv2.VideoCapture(video_data)
            features["fps"] = cap.get(cv2.CAP_PROP_FPS)
            features["frame_count"] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            features["duration"] = features["frame_count"] / features["fps"]
            
            # Extract sample frames for analysis
            frames = []
            frame_step = max(1, features["frame_count"] // 10)  # Sample 10 frames
            
            for i in range(0, features["frame_count"], frame_step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
            
            cap.release()
            
            # Analyze frames
            if frames:
                features["resolution"] = f"{frames[0].shape[1]}x{frames[0].shape[0]}"
                features["motion_intensity"] = self._calculate_motion_intensity(frames)
                features["color_diversity"] = self._calculate_color_diversity(frames)
                features["face_detection"] = self._detect_faces_in_frames(frames)
        
        return features
    
    def _extract_image_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extract comprehensive image features"""
        features = {}
        
        # Basic properties
        features["width"], features["height"] = image.size
        features["aspect_ratio"] = features["width"] / features["height"]
        features["resolution"] = features["width"] * features["height"]
        
        # Convert to numpy for analysis
        img_array = np.array(image)
        
        # Color analysis
        features["color_channels"] = img_array.shape[2] if len(img_array.shape) == 3 else 1
        features["brightness"] = np.mean(img_array)
        features["contrast"] = np.std(img_array)
        
        # Feature extraction with CNN
        img_tensor = torch.tensor(img_array).permute(2, 0, 1).unsqueeze(0).float() / 255.0
        with torch.no_grad():
            cnn_features = self.vision_model(img_tensor)
            features["cnn_features"] = cnn_features.flatten().numpy()[:100].tolist()  # First 100 features
        
        return features
    
    def _extract_text_features(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive text features"""
        features = {}
        
        # Basic features
        features["length"] = len(text)
        features["word_count"] = len(text.split())
        features["sentence_count"] = len([s for s in text.split('.') if s.strip()])
        
        # NLP features
        doc = self.nlp(text)
        features["entities"] = [(ent.text, ent.label_) for ent in doc.ents]
        features["sentiment"] = doc.sentiment if hasattr(doc, 'sentiment') else 0.0
        
        # Advanced features with transformers
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.text_model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
            features["text_embeddings"] = embeddings.flatten().numpy()[:100].tolist()  # First 100 dims
        
        return features
    
    def _assess_audio_quality(self, y: np.ndarray, sr: int, features: Dict[str, Any]) -> float:
        """Assess audio quality score"""
        score = 50.0  # Base score
        
        # Duration check
        if 30 <= features["duration"] <= 300:  # 30s to 5min optimal
            score += 20
        elif features["duration"] < 10:  # Too short
            score -= 30
        
        # Audio clarity (based on spectral features)
        if features["spectral_centroid"] > 1000:  # Clear audio
            score += 15
        
        # Energy check
        if features["rms_energy"] > 0.01:  # Good energy
            score += 15
        
        return min(100.0, max(0.0, score))
    
    def _assess_video_quality(self, features: Dict[str, Any]) -> float:
        """Assess video quality score"""
        score = 50.0  # Base score
        
        # Resolution check
        if features.get("resolution"):
            width, height = map(int, features["resolution"].split('x'))
            if width >= 1920 and height >= 1080:  # HD+
                score += 25
            elif width >= 1280 and height >= 720:  # HD
                score += 15
        
        # Duration check
        if 15 <= features.get("duration", 0) <= 600:  # 15s to 10min
            score += 20
        
        # Motion and color diversity
        if features.get("motion_intensity", 0) > 0.3:
            score += 10
        if features.get("color_diversity", 0) > 0.5:
            score += 10
        
        return min(100.0, max(0.0, score))
    
    def _assess_image_quality(self, image: Image.Image, features: Dict[str, Any]) -> float:
        """Assess image quality score"""
        score = 50.0  # Base score
        
        # Resolution check
        if features["resolution"] >= 1920 * 1080:  # HD+
            score += 25
        elif features["resolution"] >= 1280 * 720:  # HD
            score += 15
        
        # Aspect ratio check (common ratios)
        aspect_ratio = features["aspect_ratio"]
        if 0.5 <= aspect_ratio <= 2.0:  # Reasonable aspect ratio
            score += 15
        
        # Contrast and brightness
        if 50 <= features["brightness"] <= 200:  # Good brightness
            score += 10
        if features["contrast"] > 30:  # Good contrast
            score += 10
        
        return min(100.0, max(0.0, score))
    
    def _assess_text_quality(self, text: str, features: Dict[str, Any]) -> float:
        """Assess text quality score"""
        score = 50.0  # Base score
        
        # Length check
        if 100 <= features["word_count"] <= 1000:  # Optimal length
            score += 25
        elif features["word_count"] < 20:  # Too short
            score -= 30
        
        # Sentence structure
        avg_sentence_length = features["word_count"] / max(1, features["sentence_count"])
        if 10 <= avg_sentence_length <= 25:  # Good sentence length
            score += 15
        
        # Entity richness
        if len(features["entities"]) > 2:  # Rich content
            score += 10
        
        return min(100.0, max(0.0, score))
    
    def _predict_audio_engagement(self, features: Dict[str, Any]) -> float:
        """Predict audio engagement potential"""
        engagement = 50.0  # Base engagement
        
        # Tempo impact
        tempo = features.get("tempo", 120)
        if 100 <= tempo <= 140:  # Dance/pop tempo
            engagement += 20
        
        # Duration impact
        duration = features.get("duration", 0)
        if 30 <= duration <= 180:  # Sweet spot for social media
            engagement += 15
        
        # Energy impact
        if features.get("rms_energy", 0) > 0.02:
            engagement += 15
        
        return min(100.0, max(0.0, engagement))
    
    def _predict_video_engagement(self, features: Dict[str, Any]) -> float:
        """Predict video engagement potential"""
        engagement = 50.0  # Base engagement
        
        # Duration impact
        duration = features.get("duration", 0)
        if 15 <= duration <= 60:  # Optimal for social media
            engagement += 25
        elif 60 <= duration <= 300:  # Good for YouTube
            engagement += 15
        
        # Motion impact
        if features.get("motion_intensity", 0) > 0.4:
            engagement += 20
        
        # Face detection impact
        if features.get("face_detection", 0) > 0:
            engagement += 10
        
        return min(100.0, max(0.0, engagement))
    
    def _predict_image_engagement(self, features: Dict[str, Any]) -> float:
        """Predict image engagement potential"""
        engagement = 50.0  # Base engagement
        
        # Resolution impact
        if features["resolution"] >= 1920 * 1080:
            engagement += 20
        
        # Contrast and visual appeal
        if features["contrast"] > 40:
            engagement += 15
        
        # Aspect ratio (Instagram/social media friendly)
        aspect_ratio = features["aspect_ratio"]
        if 0.8 <= aspect_ratio <= 1.25:  # Square-ish
            engagement += 15
        
        return min(100.0, max(0.0, engagement))
    
    def _predict_text_engagement(self, features: Dict[str, Any]) -> float:
        """Predict text engagement potential"""
        engagement = 50.0  # Base engagement
        
        # Word count impact
        word_count = features["word_count"]
        if 50 <= word_count <= 300:  # Social media optimal
            engagement += 25
        
        # Entity richness
        entity_count = len(features["entities"])
        if entity_count > 3:
            engagement += 15
        
        # Sentiment impact (if available)
        sentiment = features.get("sentiment", 0)
        if abs(sentiment) > 0.3:  # Strong sentiment
            engagement += 10
        
        return min(100.0, max(0.0, engagement))
    
    def _calculate_monetization_potential(
        self, 
        features: Dict[str, Any], 
        content_type: ContentType
    ) -> float:
        """Calculate monetization potential score"""
        monetization = 50.0  # Base score
        
        if content_type == ContentType.AUDIO:
            # Music industry standards
            if features.get("duration", 0) >= 30:  # Minimum for streaming royalties
                monetization += 20
            if 100 <= features.get("tempo", 120) <= 140:  # Commercial appeal
                monetization += 15
        
        elif content_type == ContentType.VIDEO:
            # Video monetization factors
            if features.get("duration", 0) >= 30:  # YouTube monetization minimum
                monetization += 25
            if features.get("face_detection", 0) > 0:  # Personal content
                monetization += 10
        
        elif content_type == ContentType.IMAGE:
            # Image monetization factors
            if features["resolution"] >= 1920 * 1080:  # High quality for licensing
                monetization += 20
            if features["contrast"] > 35:  # Professional quality
                monetization += 15
        
        elif content_type == ContentType.TEXT:
            # Text monetization factors
            if features["word_count"] >= 500:  # Long-form content
                monetization += 20
            if len(features["entities"]) > 5:  # Rich, informative content
                monetization += 15
        
        return min(100.0, max(0.0, monetization))
    
    def _predict_virality(self, features: Dict[str, Any], content_type: ContentType) -> float:
        """Predict content virality potential"""
        virality = 30.0  # Base score (virality is rare)
        
        # Common virality factors across content types
        if content_type == ContentType.AUDIO:
            # Catchy tempo and energy
            if 120 <= features.get("tempo", 120) <= 130:
                virality += 25
            if features.get("rms_energy", 0) > 0.025:
                virality += 20
        
        elif content_type == ContentType.VIDEO:
            # Short, engaging videos
            duration = features.get("duration", 0)
            if 15 <= duration <= 30:  # TikTok/Instagram Reels sweet spot
                virality += 30
            if features.get("motion_intensity", 0) > 0.5:
                virality += 15
        
        elif content_type == ContentType.IMAGE:
            # Visual appeal and shareability
            if 0.9 <= features["aspect_ratio"] <= 1.1:  # Square format
                virality += 20
            if features["contrast"] > 50:  # Eye-catching
                virality += 15
        
        elif content_type == ContentType.TEXT:
            # Shareable text content
            if 20 <= features["word_count"] <= 100:  # Tweet-length
                virality += 25
            sentiment = features.get("sentiment", 0)
            if abs(sentiment) > 0.5:  # Strong emotional content
                virality += 20
        
        return min(100.0, max(0.0, virality))
    
    def _generate_audio_tags(self, features: Dict[str, Any]) -> List[str]:
        """Generate tags for audio content"""
        tags = ["audio", "music"]
        
        # Tempo-based tags
        tempo = features.get("tempo", 120)
        if tempo < 80:
            tags.append("slow")
        elif tempo > 140:
            tags.append("fast")
        else:
            tags.append("moderate")
        
        # Energy-based tags
        if features.get("rms_energy", 0) > 0.02:
            tags.append("energetic")
        else:
            tags.append("calm")
        
        # Duration-based tags
        duration = features.get("duration", 0)
        if duration < 60:
            tags.append("short")
        elif duration > 300:
            tags.append("long")
        
        return tags
    
    def _generate_video_tags(self, features: Dict[str, Any]) -> List[str]:
        """Generate tags for video content"""
        tags = ["video"]
        
        # Duration-based tags
        duration = features.get("duration", 0)
        if duration < 30:
            tags.append("short-form")
        elif duration < 300:
            tags.append("medium-form")
        else:
            tags.append("long-form")
        
        # Quality-based tags
        if features.get("resolution"):
            width, height = map(int, features["resolution"].split('x'))
            if width >= 1920:
                tags.append("hd")
            if width >= 3840:
                tags.append("4k")
        
        # Content-based tags
        if features.get("face_detection", 0) > 0:
            tags.append("people")
        if features.get("motion_intensity", 0) > 0.4:
            tags.append("dynamic")
        
        return tags
    
    def _generate_image_tags(self, features: Dict[str, Any]) -> List[str]:
        """Generate tags for image content"""
        tags = ["image"]
        
        # Resolution-based tags
        if features["resolution"] >= 1920 * 1080:
            tags.append("high-resolution")
        
        # Format-based tags
        aspect_ratio = features["aspect_ratio"]
        if 0.9 <= aspect_ratio <= 1.1:
            tags.append("square")
        elif aspect_ratio > 1.5:
            tags.append("landscape")
        elif aspect_ratio < 0.7:
            tags.append("portrait")
        
        # Visual quality tags
        if features["contrast"] > 40:
            tags.append("high-contrast")
        if features["brightness"] > 150:
            tags.append("bright")
        elif features["brightness"] < 100:
            tags.append("dark")
        
        return tags
    
    def _generate_text_tags(self, features: Dict[str, Any]) -> List[str]:
        """Generate tags for text content"""
        tags = ["text"]
        
        # Length-based tags
        word_count = features["word_count"]
        if word_count < 50:
            tags.append("short")
        elif word_count > 500:
            tags.append("long-form")
        
        # Entity-based tags
        entities = features["entities"]
        entity_types = set([entity[1] for entity in entities])
        
        if "PERSON" in entity_types:
            tags.append("people")
        if "ORG" in entity_types:
            tags.append("organizations")
        if "GPE" in entity_types:
            tags.append("locations")
        
        # Sentiment-based tags
        sentiment = features.get("sentiment", 0)
        if sentiment > 0.3:
            tags.append("positive")
        elif sentiment < -0.3:
            tags.append("negative")
        else:
            tags.append("neutral")
        
        return tags
    
    def _generate_audio_recommendations(self, metrics: ContentMetrics) -> List[str]:
        """Generate audio-specific recommendations"""
        recommendations = []
        
        if metrics.quality_score < 70:
            recommendations.append("Consider improving audio quality through better recording equipment")
        
        if metrics.engagement_potential < 60:
            recommendations.append("Optimize tempo and energy for better audience engagement")
        
        if metrics.monetization_score < 50:
            recommendations.append("Extend duration to meet minimum monetization requirements")
        
        return recommendations
    
    def _generate_video_recommendations(self, metrics: ContentMetrics) -> List[str]:
        """Generate video-specific recommendations"""
        recommendations = []
        
        if metrics.quality_score < 70:
            recommendations.append("Improve video resolution and visual quality")
        
        if metrics.engagement_potential < 60:
            recommendations.append("Add more visual interest and motion to increase engagement")
        
        if metrics.virality_prediction > 70:
            recommendations.append("Consider cross-platform promotion for viral potential")
        
        return recommendations
    
    def _generate_image_recommendations(self, metrics: ContentMetrics) -> List[str]:
        """Generate image-specific recommendations"""
        recommendations = []
        
        if metrics.quality_score < 70:
            recommendations.append("Enhance image resolution and visual appeal")
        
        if metrics.engagement_potential < 60:
            recommendations.append("Optimize aspect ratio for social media platforms")
        
        if metrics.monetization_score > 70:
            recommendations.append("Consider stock photography licensing")
        
        return recommendations
    
    def _generate_text_recommendations(self, metrics: ContentMetrics) -> List[str]:
        """Generate text-specific recommendations"""
        recommendations = []
        
        if metrics.quality_score < 70:
            recommendations.append("Improve text structure and readability")
        
        if metrics.engagement_potential < 60:
            recommendations.append("Add more engaging elements and emotional content")
        
        if len(metrics.tags) > 5:
            recommendations.append("Rich content - consider developing into longer-form content")
        
        return recommendations
    
    def _generate_optimization_suggestions(self, metrics: ContentMetrics) -> List[str]:
        """Generate general optimization suggestions"""
        suggestions = []
        
        if metrics.quality_score < 80:
            suggestions.append("Focus on improving overall content quality")
        
        if metrics.engagement_potential > 75:
            suggestions.append("Leverage high engagement potential with strategic posting times")
        
        if metrics.monetization_score > 70:
            suggestions.append("Implement monetization strategies for this high-potential content")
        
        if metrics.virality_prediction > 60:
            suggestions.append("Prepare for viral marketing campaign")
        
        return suggestions
    
    def _assess_content_risks(self, metrics: ContentMetrics) -> Dict[str, float]:
        """Assess various content risks"""
        risks = {}
        
        # Quality risk
        if metrics.quality_score < 50:
            risks["quality_risk"] = 0.8
        elif metrics.quality_score < 70:
            risks["quality_risk"] = 0.4
        else:
            risks["quality_risk"] = 0.1
        
        # Engagement risk
        if metrics.engagement_potential < 40:
            risks["low_engagement_risk"] = 0.7
        else:
            risks["low_engagement_risk"] = 0.2
        
        # Monetization risk
        if metrics.monetization_score < 30:
            risks["monetization_risk"] = 0.9
        else:
            risks["monetization_risk"] = 0.3
        
        return risks
    
    def _predict_revenue(self, metrics: ContentMetrics) -> float:
        """Predict potential revenue from content"""
        base_revenue = 100.0  # Base revenue in euros
        
        # Scale by quality and monetization scores
        revenue_multiplier = (
            (metrics.quality_score / 100) * 
            (metrics.monetization_score / 100) * 
            (metrics.engagement_potential / 100)
        )
        
        # Content type multipliers
        type_multipliers = {
            ContentType.AUDIO: 1.5,  # Music streaming royalties
            ContentType.VIDEO: 2.0,  # Video monetization potential
            ContentType.IMAGE: 1.0,  # Stock photography
            ContentType.TEXT: 0.8,   # Text monetization
            ContentType.MIXED: 1.8   # Multi-modal content
        }
        
        predicted_revenue = (
            base_revenue * 
            revenue_multiplier * 
            type_multipliers.get(metrics.content_type, 1.0)
        )
        
        # Virality bonus
        if metrics.virality_prediction > 70:
            predicted_revenue *= 5.0
        elif metrics.virality_prediction > 50:
            predicted_revenue *= 2.0
        
        return round(predicted_revenue, 2)
    
    async def _find_similar_content(
        self, 
        features: Dict[str, Any], 
        content_type: ContentType
    ) -> List[str]:
        """Find similar content using vector similarity"""
        try:
            # Extract feature vector for similarity search
            if content_type == ContentType.AUDIO:
                feature_vector = features.get("mfcc", [])
            elif content_type == ContentType.VIDEO:
                feature_vector = features.get("motion_features", [])
            elif content_type == ContentType.IMAGE:
                feature_vector = features.get("cnn_features", [])
            elif content_type == ContentType.TEXT:
                feature_vector = features.get("text_embeddings", [])
            else:
                return []
            
            if not feature_vector:
                return []
            
            # Search for similar content
            similar_ids = await self.vector_storage.search_similar(
                feature_vector, 
                content_type.value,
                limit=5
            )
            
            return similar_ids
            
        except Exception as e:
            self.logger.error(f"Similar content search failed: {e}")
            return []
    
    def _preprocess_image(self, image_data: Union[str, np.ndarray, Image.Image]) -> Image.Image:
        """Preprocess image for analysis"""
        if isinstance(image_data, str):
            return Image.open(image_data)
        elif isinstance(image_data, np.ndarray):
            return Image.fromarray(image_data)
        else:
            return image_data
    
    def _calculate_motion_intensity(self, frames: List[np.ndarray]) -> float:
        """Calculate motion intensity in video frames"""
        if len(frames) < 2:
            return 0.0
        
        motion_scores = []
        for i in range(1, len(frames)):
            # Calculate optical flow or frame difference
            diff = cv2.absdiff(frames[i-1], frames[i])
            motion_score = np.mean(diff) / 255.0
            motion_scores.append(motion_score)
        
        return np.mean(motion_scores)
    
    def _calculate_color_diversity(self, frames: List[np.ndarray]) -> float:
        """Calculate color diversity in video frames"""
        color_scores = []
        
        for frame in frames:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            # Normalize and calculate diversity
            hist_norm = hist / hist.sum()
            diversity = -np.sum(hist_norm * np.log(hist_norm + 1e-10))
            color_scores.append(diversity)
        
        return np.mean(color_scores) / 5.0  # Normalize to 0-1 range
    
    def _detect_faces_in_frames(self, frames: List[np.ndarray]) -> int:
        """Detect faces in video frames"""
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            total_faces = 0
            
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                total_faces += len(faces)
            
            return total_faces
        except Exception:
            return 0
    
    def _generate_content_id(self, content_data: Any, content_type: ContentType) -> str:
        """Generate unique content ID"""
        import hashlib
        
        # Create hash from content data and timestamp
        content_str = str(content_data) + str(datetime.now().timestamp())
        content_hash = hashlib.md5(content_str.encode()).hexdigest()
        
        return f"{content_type.value}_{content_hash[:12]}"
    
    def _update_performance_metrics(self, processing_time: float) -> None:
        """Update performance tracking metrics"""
        self.performance_metrics["total_analyses"] += 1
        total = self.performance_metrics["total_analyses"]
        current_avg = self.performance_metrics["average_processing_time"]
        
        # Update running average
        self.performance_metrics["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # Update cache hit rate
        cache_hits = len(self.analysis_cache)
        self.performance_metrics["cache_hit_rate"] = cache_hits / total
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.performance_metrics.copy()
    
    async def clear_cache(self) -> None:
        """Clear analysis cache"""
        self.analysis_cache.clear()
        self.logger.info("Analysis cache cleared")
    
    async def batch_analyze(
        self, 
        content_items: List[Tuple[Any, ContentType, Optional[Dict[str, Any]]]]
    ) -> List[AnalysisResult]:
        """Analyze multiple content items in batch"""
        results = []
        
        for content_data, content_type, metadata in content_items:
            try:
                result = await self.analyze_content(content_data, content_type, metadata)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Batch analysis failed for item: {e}")
                # Continue with other items
                continue
        
        return results
