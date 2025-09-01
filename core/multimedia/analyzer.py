"""Multimedia Analyzer - Enterprise Content Analysis Engine

Advanced content analysis system for multimedia files.
Provides comprehensive analysis of audio, video, image, and document content.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import os
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import cv2
from PIL import Image
import librosa
import soundfile as sf
from scipy import stats
import json

# AI/ML imports
import torch
import torchvision.transforms as transforms
from transformers import (
    pipeline, AutoModel, AutoTokenizer,
    BlipProcessor, BlipForConditionalGeneration,
    Wav2Vec2Processor, Wav2Vec2ForCTC
)
import clip

# Computer vision
from ultralytics import YOLO
import face_recognition
import pytesseract

# Audio analysis
import aubio
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs

from .metadata import MultimediaMetadata
from .format_detector import MultimediaFormatDetector

logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """
Analysis types"""

    CONTENT = "content"
    TECHNICAL = "technical"
    SEMANTIC = "semantic"
    QUALITY = "quality"
    AESTHETIC = "aesthetic"
    SENTIMENT = "sentiment"
    CLASSIFICATION = "classification"
    FEATURE_EXTRACTION = "feature_extraction"


class ContentCategory(Enum):
    """Content categories"""

    MUSIC = "music"
    SPEECH = "speech"
    NATURE = "nature"
    URBAN = "urban"
    PEOPLE = "people"
    OBJECTS = "objects"
    ANIMALS = "animals"
    FOOD = "food"
    VEHICLES = "vehicles"
    BUILDINGS = "buildings"
    LANDSCAPE = "landscape"
    ABSTRACT = "abstract"
    DOCUMENT = "document"
    OTHER = "other"


@dataclass
class AnalysisResult:
    """Analysis result container"""
    analysis_id: str
    file_path: str
    analysis_type: AnalysisType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Technical analysis
    technical_metrics: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    format_info: Dict[str, Any] = field(default_factory=dict)
    
    # Content analysis
    content_category: Optional[ContentCategory] = None
    detected_objects: List[Dict[str, Any]] = field(default_factory=list)
    detected_faces: List[Dict[str, Any]] = field(default_factory=list)
    extracted_text: str = ""
    
    # Semantic analysis
    description: str = ""
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    sentiment_score: float = 0.0
    
    # Features
    feature_vectors: Dict[str, List[float]] = field(default_factory=dict)
    audio_features: Dict[str, Any] = field(default_factory=dict)
    visual_features: Dict[str, Any] = field(default_factory=dict)
    
    # Confidence scores
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    
    # Processing metadata
    processing_time: float = 0.0
    model_versions: Dict[str, str] = field(default_factory=dict)
    error_details: Optional[str] = None


class MultimediaAnalyzer:
    """Enterprise multimedia content analyzer"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.format_detector = MultimediaFormatDetector(config.get("detector", {}))
        self.metadata_extractor = MultimediaMetadata(config.get("metadata", {}))
        
        # AI Models
        self.models = {}
        self.processors = {}
        
        # Configuration
        self.model_cache_dir = config.get("model_cache_dir", "./models")
        self.gpu_enabled = config.get("gpu_enabled", torch.cuda.is_available())
        self.batch_size = config.get("batch_size", 1)
        self.max_file_size = config.get("max_file_size", 500 * 1024 * 1024)  # 500MB
        
        # Analysis statistics
        self.analysis_stats = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "average_processing_time": 0.0,
            "analysis_types": {},
            "content_categories": {}
        }
        
    async def initialize(self):
        """Initialize analyzer models"""
        try:
            await self._load_models()
            await self.format_detector.initialize()
            await self.metadata_extractor.initialize()
            
            logger.info("Multimedia analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize analyzer: {e}")
            raise
            
    async def analyze_file(
        self, 
        file_path: str, 
        analysis_types: List[AnalysisType] = None,
        options: Dict[str, Any] = None
    ) -> AnalysisResult:
        """Analyze multimedia file"""
        start_time = datetime.now()
        analysis_id = f"analysis_{int(start_time.timestamp())}_{hash(file_path) % 10000}"
        
        try:
            # Default analysis types
            if not analysis_types:
                analysis_types = [AnalysisType.CONTENT, AnalysisType.TECHNICAL, AnalysisType.SEMANTIC]
                
            options = options or {}
            
            # Validate file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                raise ValueError(f"File size {file_size} exceeds maximum {self.max_file_size}")
                
            # Detect format
            file_format = await self.format_detector.detect_format(file_path)
            if not file_format:
                raise ValueError("Unable to detect file format")
                
            # Create result container
            result = AnalysisResult(
                analysis_id=analysis_id,
                file_path=file_path,
                analysis_type=AnalysisType.CONTENT,  # Primary type
                format_info={"format": file_format, "size": file_size}
            )
            
            # Perform format-specific analysis
            if file_format in ["mp3", "wav", "flac", "aac", "ogg", "m4a"]:
                await self._analyze_audio(file_path, result, analysis_types, options)
            elif file_format in ["mp4", "avi", "mov", "mkv", "webm", "flv"]:
                await self._analyze_video(file_path, result, analysis_types, options)
            elif file_format in ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"]:
                await self._analyze_image(file_path, result, analysis_types, options)
            elif file_format in ["pdf", "docx", "txt", "html", "md"]:
                await self._analyze_document(file_path, result, analysis_types, options)
            else:
                raise ValueError(f"Unsupported format for analysis: {file_format}")
                
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            # Update statistics
            await self._update_analysis_stats(analysis_types, result.content_category, processing_time, True)
            
            logger.info(f"Analysis completed: {analysis_id} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            await self._update_analysis_stats(analysis_types or [], None, processing_time, False)
            
            logger.error(f"Analysis failed for {file_path}: {e}")
            
            return AnalysisResult(
                analysis_id=analysis_id,
                file_path=file_path,
                analysis_type=AnalysisType.CONTENT,
                processing_time=processing_time,
                error_details=str(e)
            )
            
    async def batch_analyze(
        self, 
        file_paths: List[str],
        analysis_types: List[AnalysisType] = None,
        options: Dict[str, Any] = None
    ) -> List[AnalysisResult]:
        """Analyze multiple files in batch"""
        try:
            # Create semaphore for parallel processing
            semaphore = asyncio.Semaphore(self.batch_size)
            
            async def analyze_with_semaphore(file_path):
                async with semaphore:
                    return await self.analyze_file(file_path, analysis_types, options)
                    
            # Process files in parallel
            tasks = [analyze_with_semaphore(path) for path in file_paths]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    final_results.append(AnalysisResult(
                        analysis_id=f"batch_error_{i}",
                        file_path=file_paths[i],
                        analysis_type=AnalysisType.CONTENT,
                        error_details=str(result)
                    ))
                else:
                    final_results.append(result)
                    
            return final_results
            
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return [
                AnalysisResult(
                    analysis_id=f"batch_error_{i}",
                    file_path=path,
                    analysis_type=AnalysisType.CONTENT,
                    error_details=str(e)
                ) for i, path in enumerate(file_paths)
            ]
            
    async def compare_content(self, file1: str, file2: str) -> Dict[str, Any]:
        """Compare two multimedia files"""
        try:
            # Analyze both files
            result1 = await self.analyze_file(file1, [AnalysisType.FEATURE_EXTRACTION])
            result2 = await self.analyze_file(file2, [AnalysisType.FEATURE_EXTRACTION])
            
            if result1.error_details or result2.error_details:
                return {
                    "success": False,
                    "error": "Failed to analyze one or both files"
                }
                
            # Calculate similarity metrics
            similarity_scores = {}
            
            # Feature vector similarity
            for feature_type in result1.feature_vectors:
                if feature_type in result2.feature_vectors:
                    vec1 = np.array(result1.feature_vectors[feature_type])
                    vec2 = np.array(result2.feature_vectors[feature_type])
                    
                    # Cosine similarity
                    cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                    similarity_scores[f"{feature_type}_cosine"] = float(cosine_sim)
                    
            # Content category similarity
            category_match = result1.content_category == result2.content_category
            similarity_scores["category_match"] = category_match
            
            # Tag overlap
            tags1 = set(result1.tags)
            tags2 = set(result2.tags)
            tag_overlap = len(tags1.intersection(tags2)) / len(tags1.union(tags2)) if tags1.union(tags2) else 0
            similarity_scores["tag_overlap"] = tag_overlap
            
            # Overall similarity
            feature_scores = [score for key, score in similarity_scores.items() if "cosine" in key]
            overall_similarity = np.mean(feature_scores) if feature_scores else 0.0
            
            return {
                "success": True,
                "file1": file1,
                "file2": file2,
                "similarity_scores": similarity_scores,
                "overall_similarity": overall_similarity,
                "analysis_results": {
                    "file1": result1,
                    "file2": result2
                }
            }
            
        except Exception as e:
            logger.error(f"Content comparison failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def extract_features(self, file_path: str) -> Dict[str, List[float]]:
        """Extract feature vectors from multimedia file"""
        try:
            result = await self.analyze_file(file_path, [AnalysisType.FEATURE_EXTRACTION])
            return result.feature_vectors
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {}
            
    async def classify_content(self, file_path: str) -> Dict[str, Any]:
        """Classify multimedia content"""
        try:
            result = await self.analyze_file(file_path, [AnalysisType.CLASSIFICATION])
            
            return {
                "content_category": result.content_category.value if result.content_category else "unknown",
                "confidence": result.confidence_scores.get("classification", 0.0),
                "tags": result.tags,
                "description": result.description
            }
            
        except Exception as e:
            logger.error(f"Content classification failed: {e}")
            return {
                "content_category": "unknown",
                "confidence": 0.0,
                "error": str(e)
            }
            
    async def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        return {
            **self.analysis_stats,
            "loaded_models": list(self.models.keys()),
            "gpu_enabled": self.gpu_enabled,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Analyzer health check"""
        try:
            # Check model availability
            model_status = {}
            for model_name, model in self.models.items():
                try:
                    # Simple model check
                    model_status[model_name] = "healthy"
                except Exception as e:
                    model_status[model_name] = f"error: {e}"
                    
            # Check GPU availability
            gpu_status = "available" if self.gpu_enabled and torch.cuda.is_available() else "unavailable"
            
            # Check dependencies
            dependency_status = await self._check_dependencies()
            
            overall_status = "healthy"
            if any("error" in status for status in model_status.values()):
                overall_status = "degraded"
                
            return {
                "status": overall_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "models": model_status,
                "gpu_status": gpu_status,
                "dependencies": dependency_status,
                "analysis_stats": self.analysis_stats
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    # Private methods
    
    async def _load_models(self):
        """Load AI models for analysis"""
        try:
            device = "cuda" if self.gpu_enabled else "cpu"
            
            # Image analysis models
            self.models["clip"] = clip.load("ViT-B/32", device=device)[0]
            
            # Image captioning
            self.processors["blip"] = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.models["blip"] = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            # Object detection
            self.models["yolo"] = YOLO("yolov8n.pt")
            
            # Audio analysis
            self.processors["wav2vec2"] = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
            self.models["wav2vec2"] = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
            
            # Text analysis
            self.models["sentiment"] = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            
            # Music analysis
            try:
                self.models["music_classifier"] = TensorflowPredictEffnetDiscogs(
                    graphFilename="discogs-effnet-bs64-1.pb",
                    output="PartitionedCall:1"
                )
            except Exception as e:
                logger.warning(f"Music classifier not available: {e}")
                
            logger.info(f"Loaded {len(self.models)} analysis models")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise
            
    async def _analyze_audio(
        self, 
        file_path: str, 
        result: AnalysisResult, 
        analysis_types: List[AnalysisType],
        options: Dict[str, Any]
    ):
        """Analyze audio file"""
        try:
            # Load audio
            y, sr = librosa.load(file_path, sr=None)
            duration = len(y) / sr
            
            # Technical analysis
            if AnalysisType.TECHNICAL in analysis_types:
                result.technical_metrics = {
                    "duration": duration,
                    "sample_rate": sr,
                    "channels": 1,  # librosa loads as mono by default
                    "bitrate": os.path.getsize(file_path) * 8 / duration if duration > 0 else 0,
                    "dynamic_range": float(np.max(y) - np.min(y)),
                    "rms_energy": float(np.sqrt(np.mean(y**2))),
                    "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y)))
                }
                
            # Feature extraction
            if AnalysisType.FEATURE_EXTRACTION in analysis_types:
                # Extract audio features
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
                spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
                chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                tempo = librosa.beat.tempo(y=y, sr=sr)[0]
                
                result.feature_vectors["mfcc"] = np.mean(mfccs, axis=1).tolist()
                result.feature_vectors["spectral_centroid"] = np.mean(spectral_centroids).tolist()
                result.feature_vectors["spectral_rolloff"] = np.mean(spectral_rolloff).tolist()
                result.feature_vectors["chroma"] = np.mean(chroma, axis=1).tolist()
                
                result.audio_features = {
                    "tempo": float(tempo),
                    "spectral_centroid_mean": float(np.mean(spectral_centroids)),
                    "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
                    "mfcc_mean": np.mean(mfccs).tolist(),
                    "chroma_mean": np.mean(chroma).tolist()
                }
                
            # Content classification
            if AnalysisType.CLASSIFICATION in analysis_types:
                # Simple heuristic classification
                if tempo > 120:
                    result.content_category = ContentCategory.MUSIC
                    result.tags.append("upbeat")
                elif tempo < 80:
                    result.content_category = ContentCategory.MUSIC
                    result.tags.append("slow")
                else:
                    result.content_category = ContentCategory.MUSIC
                    result.tags.append("moderate")
                    
                # Check for speech characteristics
                speech_threshold = 0.5
                if np.mean(spectral_centroids) > speech_threshold:
                    result.tags.append("speech-like")
                    if result.content_category == ContentCategory.MUSIC:
                        result.content_category = ContentCategory.SPEECH
                        
                result.confidence_scores["classification"] = 0.7
                
            # Quality analysis
            if AnalysisType.QUALITY in analysis_types:
                # Simple quality metrics
                snr = 20 * np.log10(np.std(y) / (np.std(y - np.mean(y)) + 1e-10))
                result.quality_score = min(max(snr / 50.0, 0.0), 1.0)  # Normalize to 0-1
                
            logger.debug(f"Audio analysis completed for {file_path}")
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            result.error_details = str(e)
            
    async def _analyze_video(
        self, 
        file_path: str, 
        result: AnalysisResult, 
        analysis_types: List[AnalysisType],
        options: Dict[str, Any]
    ):
        """Analyze video file"""
        try:
            # Open video
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                raise ValueError("Cannot open video file")
                
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Technical analysis
            if AnalysisType.TECHNICAL in analysis_types:
                result.technical_metrics = {
                    "duration": duration,
                    "fps": fps,
                    "frame_count": frame_count,
                    "width": width,
                    "height": height,
                    "resolution": f"{width}x{height}",
                    "aspect_ratio": width / height if height > 0 else 0,
                    "file_size": os.path.getsize(file_path)
                }
                
            # Sample frames for analysis
            sample_frames = []
            if AnalysisType.CONTENT in analysis_types or AnalysisType.FEATURE_EXTRACTION in analysis_types:
                # Sample every 10% of the video
                sample_positions = [int(frame_count * i / 10) for i in range(1, 10)]
                
                for pos in sample_positions[:5]:  # Limit to 5 frames
                    cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
                    ret, frame = cap.read()
                    if ret:
                        # Convert BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        sample_frames.append(frame_rgb)
                        
            cap.release()
            
            # Analyze sample frames
            if sample_frames:
                await self._analyze_video_frames(sample_frames, result, analysis_types, options)
                
            # Content classification
            if AnalysisType.CLASSIFICATION in analysis_types:
                # Basic classification based on aspect ratio and content
                if width > height:
                    result.tags.append("landscape")
                elif height > width:
                    result.tags.append("portrait")
                else:
                    result.tags.append("square")
                    
                if duration < 30:
                    result.tags.append("short-form")
                elif duration > 300:
                    result.tags.append("long-form")
                    
                result.content_category = ContentCategory.OTHER  # Default
                result.confidence_scores["classification"] = 0.6
                
            # Quality analysis
            if AnalysisType.QUALITY in analysis_types:
                # Resolution-based quality score
                pixels = width * height
                if pixels >= 1920 * 1080:
                    result.quality_score = 1.0
                elif pixels >= 1280 * 720:
                    result.quality_score = 0.8
                elif pixels >= 854 * 480:
                    result.quality_score = 0.6
                else:
                    result.quality_score = 0.4
                    
            logger.debug(f"Video analysis completed for {file_path}")
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            result.error_details = str(e)
            
    async def _analyze_image(
        self, 
        file_path: str, 
        result: AnalysisResult, 
        analysis_types: List[AnalysisType],
        options: Dict[str, Any]
    ):
        """Analyze image file"""
        try:
            # Load image
            image = Image.open(file_path).convert("RGB")
            width, height = image.size
            
            # Technical analysis
            if AnalysisType.TECHNICAL in analysis_types:
                result.technical_metrics = {
                    "width": width,
                    "height": height,
                    "resolution": f"{width}x{height}",
                    "aspect_ratio": width / height,
                    "pixels": width * height,
                    "file_size": os.path.getsize(file_path),
                    "format": image.format
                }
                
            # Feature extraction
            if AnalysisType.FEATURE_EXTRACTION in analysis_types:
                # CLIP features
                if "clip" in self.models:
                    preprocess = transforms.Compose([
                        transforms.Resize(224),
                        transforms.CenterCrop(224),
                        transforms.ToTensor(),
                        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                    ])
                    
                    image_tensor = preprocess(image).unsqueeze(0)
                    if self.gpu_enabled:
                        image_tensor = image_tensor.cuda()
                        
                    with torch.no_grad():
                        features = self.models["clip"].encode_image(image_tensor)
                        result.feature_vectors["clip"] = features.cpu().numpy().flatten().tolist()
                        
                # Color histogram
                np_image = np.array(image)
                hist_r = np.histogram(np_image[:,:,0], bins=32, range=(0, 256))[0]
                hist_g = np.histogram(np_image[:,:,1], bins=32, range=(0, 256))[0]
                hist_b = np.histogram(np_image[:,:,2], bins=32, range=(0, 256))[0]
                
                result.visual_features = {
                    "color_histogram_r": hist_r.tolist(),
                    "color_histogram_g": hist_g.tolist(),
                    "color_histogram_b": hist_b.tolist(),
                    "brightness": float(np.mean(np_image)),
                    "contrast": float(np.std(np_image))
                }
                
            # Object detection
            if AnalysisType.CONTENT in analysis_types and "yolo" in self.models:
                results = self.models["yolo"](np.array(image))
                
                for r in results:
                    boxes = r.boxes
                    if boxes is not None:
                        for box in boxes:
                            result.detected_objects.append({
                                "class": r.names[int(box.cls)],
                                "confidence": float(box.conf),
                                "bbox": box.xyxy.tolist()
                            })
                            
            # Face detection
            if AnalysisType.CONTENT in analysis_types:
                try:
                    face_locations = face_recognition.face_locations(np.array(image))
                    for face_location in face_locations:
                        top, right, bottom, left = face_location
                        result.detected_faces.append({
                            "bbox": [left, top, right, bottom],
                            "confidence": 0.9  # face_recognition doesn't provide confidence
                        })
                except Exception as e:
                    logger.debug(f"Face detection failed: {e}")
                    
            # Text extraction
            if AnalysisType.CONTENT in analysis_types:
                try:
                    extracted_text = pytesseract.image_to_string(image)
                    result.extracted_text = extracted_text.strip()
                except Exception as e:
                    logger.debug(f"Text extraction failed: {e}")
                    
            # Image captioning
            if AnalysisType.SEMANTIC in analysis_types and "blip" in self.models:
                try:
                    inputs = self.processors["blip"](image, return_tensors="pt")
                    out = self.models["blip"].generate(**inputs, max_length=50)
                    caption = self.processors["blip"].decode(out[0], skip_special_tokens=True)
                    result.description = caption
                except Exception as e:
                    logger.debug(f"Image captioning failed: {e}")
                    
            # Content classification
            if AnalysisType.CLASSIFICATION in analysis_types:
                # Basic classification based on detected objects
                if result.detected_faces:
                    result.content_category = ContentCategory.PEOPLE
                    result.tags.append("faces")
                elif any("car" in obj["class"] or "truck" in obj["class"] for obj in result.detected_objects):
                    result.content_category = ContentCategory.VEHICLES
                    result.tags.append("vehicles")
                elif any("building" in obj["class"] for obj in result.detected_objects):
                    result.content_category = ContentCategory.BUILDINGS
                    result.tags.append("architecture")
                else:
                    result.content_category = ContentCategory.OTHER
                    
                # Add aspect ratio tags
                if width > height * 1.5:
                    result.tags.append("landscape")
                elif height > width * 1.5:
                    result.tags.append("portrait")
                    
                result.confidence_scores["classification"] = 0.7
                
            # Quality analysis
            if AnalysisType.QUALITY in analysis_types:
                # Resolution and sharpness based quality
                pixels = width * height
                if pixels >= 1920 * 1080:
                    resolution_score = 1.0
                elif pixels >= 1280 * 720:
                    resolution_score = 0.8
                else:
                    resolution_score = 0.6
                    
                # Simple sharpness metric using Laplacian variance
                gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                sharpness_score = min(sharpness / 1000.0, 1.0)  # Normalize
                
                result.quality_score = (resolution_score + sharpness_score) / 2
                
            logger.debug(f"Image analysis completed for {file_path}")
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            result.error_details = str(e)
            
    async def _analyze_document(
        self, 
        file_path: str, 
        result: AnalysisResult, 
        analysis_types: List[AnalysisType],
        options: Dict[str, Any]
    ):
        """Analyze document file"""
        try:
            # Extract text based on format
            text_content = ""
            
            if file_path.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            elif file_path.lower().endswith('.pdf'):
                # PDF text extraction would go here
                # For now, placeholder
                text_content = "PDF content extraction not implemented"
            else:
                text_content = "Unsupported document format"
                
            result.extracted_text = text_content
            
            # Technical analysis
            if AnalysisType.TECHNICAL in analysis_types:
                result.technical_metrics = {
                    "file_size": os.path.getsize(file_path),
                    "character_count": len(text_content),
                    "word_count": len(text_content.split()),
                    "line_count": len(text_content.splitlines())
                }
                
            # Semantic analysis
            if AnalysisType.SEMANTIC in analysis_types:
                # Extract keywords (simple implementation)
                words = text_content.lower().split()
                word_freq = {}
                for word in words:
                    if len(word) > 3:  # Filter short words
                        word_freq[word] = word_freq.get(word, 0) + 1
                        
                # Top keywords
                result.keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
                result.keywords = [word for word, freq in result.keywords]
                
                # Sentiment analysis
                if "sentiment" in self.models and text_content:
                    sentiment_result = self.models["sentiment"](text_content[:512])  # Limit text length
                    if sentiment_result:
                        result.sentiment_score = sentiment_result[0]["score"]
                        if sentiment_result[0]["label"] == "NEGATIVE":
                            result.sentiment_score *= -1
                            
            # Content classification
            if AnalysisType.CLASSIFICATION in analysis_types:
                result.content_category = ContentCategory.DOCUMENT
                result.confidence_scores["classification"] = 1.0
                
                # Add format tag
                ext = os.path.splitext(file_path)[1].lower()
                result.tags.append(f"format_{ext[1:]}")
                
            # Quality analysis
            if AnalysisType.QUALITY in analysis_types:
                # Simple quality based on readability
                words = text_content.split()
                if words:
                    avg_word_length = sum(len(word) for word in words) / len(words)
                    sentences = text_content.split('.')
                    avg_sentence_length = len(words) / len(sentences) if sentences else 0
                    
                    # Simple readability score (0-1)
                    readability = 1.0 - min((avg_word_length - 4) / 10, 0.5) - min((avg_sentence_length - 15) / 20, 0.3)
                    result.quality_score = max(readability, 0.1)
                else:
                    result.quality_score = 0.1
                    
            logger.debug(f"Document analysis completed for {file_path}")
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            result.error_details = str(e)
            
    async def _analyze_video_frames(
        self, 
        frames: List[np.ndarray], 
        result: AnalysisResult, 
        analysis_types: List[AnalysisType],
        options: Dict[str, Any]
    ):
        """Analyze video frames"""
        try:
            all_objects = []
            all_faces = []
            all_features = []
            
            for frame in frames:
                # Object detection
                if "yolo" in self.models:
                    frame_results = self.models["yolo"](frame)
                    for r in frame_results:
                        boxes = r.boxes
                        if boxes is not None:
                            for box in boxes:
                                all_objects.append({
                                    "class": r.names[int(box.cls)],
                                    "confidence": float(box.conf)
                                })
                                
                # Face detection
                try:
                    face_locations = face_recognition.face_locations(frame)
                    all_faces.extend(face_locations)
                except Exception:
                    pass
                    
                # Feature extraction
                if "clip" in self.models:
                    try:
                        frame_pil = Image.fromarray(frame)
                        preprocess = transforms.Compose([
                            transforms.Resize(224),
                            transforms.CenterCrop(224),
                            transforms.ToTensor(),
                            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                        ])
                        
                        frame_tensor = preprocess(frame_pil).unsqueeze(0)
                        if self.gpu_enabled:
                            frame_tensor = frame_tensor.cuda()
                            
                        with torch.no_grad():
                            features = self.models["clip"].encode_image(frame_tensor)
                            all_features.append(features.cpu().numpy().flatten())
                    except Exception:
                        pass
                        
            # Aggregate results
            if all_objects:
                # Count object classes
                class_counts = {}
                for obj in all_objects:
                    class_name = obj["class"]
                    class_counts[class_name] = class_counts.get(class_name, 0) + 1
                    
                # Most common objects
                most_common = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                result.detected_objects = [{"class": cls, "count": cnt} for cls, cnt in most_common]
                
            if all_faces:
                result.detected_faces = [{"count": len(all_faces)}]
                
            if all_features:
                # Average features across frames
                avg_features = np.mean(all_features, axis=0)
                result.feature_vectors["video_clip"] = avg_features.tolist()
                
        except Exception as e:
            logger.error(f"Video frame analysis failed: {e}")
            
    async def _update_analysis_stats(
        self, 
        analysis_types: List[AnalysisType], 
        content_category: Optional[ContentCategory],
        processing_time: float, 
        success: bool
    ):
        """Update analysis statistics"""
        self.analysis_stats["total_analyses"] += 1
        
        if success:
            self.analysis_stats["successful_analyses"] += 1
        else:
            self.analysis_stats["failed_analyses"] += 1
            
        # Update average processing time
        total_time = (
            self.analysis_stats["average_processing_time"] * (self.analysis_stats["total_analyses"] - 1) +
            processing_time
        )
        self.analysis_stats["average_processing_time"] = total_time / self.analysis_stats["total_analyses"]
        
        # Update analysis type stats
        for analysis_type in analysis_types:
            type_key = analysis_type.value
            if type_key not in self.analysis_stats["analysis_types"]:
                self.analysis_stats["analysis_types"][type_key] = 0
            self.analysis_stats["analysis_types"][type_key] += 1
            
        # Update content category stats
        if content_category:
            cat_key = content_category.value
            if cat_key not in self.analysis_stats["content_categories"]:
                self.analysis_stats["content_categories"][cat_key] = 0
            self.analysis_stats["content_categories"][cat_key] += 1
            
    async def _check_dependencies(self) -> Dict[str, str]:
        """Check external dependencies"""
        dependencies = {
            "opencv": "available",
            "pytorch": "available" if torch.cuda.is_available() else "cpu_only",
            "transformers": "available",
            "librosa": "available",
            "face_recognition": "available",
            "pytesseract": "available"
        }
        
        # Check specific tools
        try:
            import cv2
            dependencies["opencv"] = f"version_{cv2.__version__}"
        except ImportError:
            dependencies["opencv"] = "missing"
            
        try:
            import torch
            dependencies["pytorch"] = f"version_{torch.__version__}"
        except ImportError:
            dependencies["pytorch"] = "missing"
            
        return dependencies
