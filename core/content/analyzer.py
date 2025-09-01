"""Content Analyzer - AI-Powered Content Analysis Engine
=====================================================

The ContentAnalyzer provides intelligent analysis of content using AI/ML
techniques for classification, sentiment analysis, quality assessment,
and feature extraction according to business requirements.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from dataclasses import dataclass
import uuid

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import librosa
import cv2
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..database.models import Content, ContentAnalysis
from ..ml.models.audio_classifier import AudioClassifier
from ..ml.models.video_classifier import VideoClassifier
from ..ml.models.image_classifier import ImageClassifier
from ..ml.models.text_classifier import TextClassifier
from ..ml.sentiment_analyzer import SentimentAnalyzer
from ..ml.feature_extractor import FeatureExtractor


@dataclass
class AnalysisResult:
    """
Content analysis result container"""
    content_id: str
    content_type: str
    classification: Dict[str, Any]
    features: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    sentiment_analysis: Optional[Dict[str, Any]] = None
    recommendations: List[str] = None
    confidence_score: float = 0.0
    analysis_time: float = 0.0


@dataclass
class AnalysisConfig:
    """
Content analysis configuration"""
    enable_classification: bool = True
    enable_feature_extraction: bool = True
    enable_quality_assessment: bool = True
    enable_sentiment_analysis: bool = True
    enable_recommendations: bool = True
    classification_threshold: float = 0.7
    feature_extraction_depth: str = "standard"  # basic, standard, advanced
    quality_threshold: float = 0.6


class ContentAnalyzer:
    """
    AI-Powered Content Analysis Engine
    
    Provides comprehensive content analysis including:
    - Automated classification and tagging
    - Feature extraction and similarity analysis
    - Quality assessment and scoring
    - Sentiment analysis for text content
    - Content recommendations and optimization suggestions
    - Trend analysis and market insights
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        config: AnalysisConfig = None
    ):
        self.db = db_session
        self.config = config or AnalysisConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI/ML models
        self.audio_classifier = AudioClassifier()
        self.video_classifier = VideoClassifier()
        self.image_classifier = ImageClassifier()
        self.text_classifier = TextClassifier()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.feature_extractor = FeatureExtractor()
        
        # Analysis cache
        self.analysis_cache = {}

    async def analyze_content(
        self,
        content_id: str,
        custom_config: AnalysisConfig = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive content analysis
        
        Args:
            content_id: Content identifier
            custom_config: Custom analysis configuration
            
        Returns:
            Analysis result with AI insights and recommendations
        """
        analysis_start = datetime.utcnow()
        config = custom_config or self.config
        
        try:
            self.logger.info(f"Starting content analysis for {content_id}")
            
            # Get content from database
            content = await self._get_content(content_id)
            if not content:
                return {
                    "success": False,
                    "error": "Content not found",
                    "content_id": content_id
                }
            
            # Route to appropriate analyzer
            if content.content_type == "audio":
                analysis_result = await self._analyze_audio(content, config)
            elif content.content_type == "video":
                analysis_result = await self._analyze_video(content, config)
            elif content.content_type == "image":
                analysis_result = await self._analyze_image(content, config)
            elif content.content_type == "text":
                analysis_result = await self._analyze_text(content, config)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported content type: {content.content_type}",
                    "content_id": content_id
                }
            
            # Calculate analysis time
            analysis_time = (datetime.utcnow() - analysis_start).total_seconds()
            analysis_result.analysis_time = analysis_time
            
            # Save analysis to database
            await self._save_analysis_result(content_id, analysis_result)
            
            # Cache analysis result
            self.analysis_cache[content_id] = analysis_result
            
            self.logger.info(f"Content analysis completed for {content_id} in {analysis_time:.2f}s")
            
            return {
                "success": True,
                "content_id": content_id,
                "analysis": self._serialize_analysis_result(analysis_result),
                "analysis_time": analysis_time
            }
            
        except Exception as e:
            analysis_time = (datetime.utcnow() - analysis_start).total_seconds()
            error_msg = f"Content analysis failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "content_id": content_id,
                "analysis_time": analysis_time
            }

    async def _analyze_audio(
        self,
        content: Content,
        config: AnalysisConfig
    ) -> AnalysisResult:
        """
        Analyze audio content with AI models
        
        Args:
            content: Content database object
            config: Analysis configuration
            
        Returns:
            Audio analysis result
        """
        try:
            # Load audio data
            audio_data, sample_rate = librosa.load(content.file_path, sr=None)
            
            classification = {}
            features = {}
            quality_metrics = {}
            recommendations = []
            
            # Audio Classification
            if config.enable_classification:
                classification_result = await self.audio_classifier.classify(
                    content.file_path
                )
                classification = {
                    "genre": classification_result.get("genre", "unknown"),
                    "mood": classification_result.get("mood", "neutral"),
                    "tempo": classification_result.get("tempo", "medium"),
                    "key": classification_result.get("key", "unknown"),
                    "instruments": classification_result.get("instruments", []),
                    "confidence": classification_result.get("confidence", 0.0)
                }
            
            # Feature Extraction
            if config.enable_feature_extraction:
                # Extract audio features
                mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
                spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
                spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
                zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
                
                # Tempo and beat analysis
                tempo, beat_frames = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
                
                features = {
                    "mfcc_mean": np.mean(mfcc, axis=1).tolist(),
                    "spectral_centroid_mean": float(np.mean(spectral_centroid)),
                    "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
                    "zero_crossing_rate_mean": float(np.mean(zero_crossing_rate)),
                    "tempo": float(tempo),
                    "duration": len(audio_data) / sample_rate,
                    "sample_rate": sample_rate,
                    "rms_energy": float(np.sqrt(np.mean(audio_data**2)))
                }
            
            # Quality Assessment
            if config.enable_quality_assessment:
                # Audio quality metrics
                dynamic_range = np.max(audio_data) - np.min(audio_data)
                signal_to_noise_ratio = self._calculate_snr(audio_data)
                
                quality_metrics = {
                    "dynamic_range": float(dynamic_range),
                    "snr": float(signal_to_noise_ratio),
                    "clipping_detected": bool(np.any(np.abs(audio_data) >= 0.99)),
                    "silence_ratio": self._calculate_silence_ratio(audio_data),
                    "overall_quality": self._calculate_audio_quality_score(
                        dynamic_range, signal_to_noise_ratio, audio_data
                    )
                }
            
            # Generate Recommendations
            if config.enable_recommendations:
                recommendations = self._generate_audio_recommendations(
                    classification, quality_metrics, features
                )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                classification, quality_metrics, features
            )
            
            return AnalysisResult(
                content_id=content.id,
                content_type="audio",
                classification=classification,
                features=features,
                quality_metrics=quality_metrics,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            raise Exception(f"Audio analysis failed: {str(e)}")

    async def _analyze_video(
        self,
        content: Content,
        config: AnalysisConfig
    ) -> AnalysisResult:
        """
        Analyze video content with AI models
        
        Args:
            content: Content database object
            config: Analysis configuration
            
        Returns:
            Video analysis result
        """
        try:
            classification = {}
            features = {}
            quality_metrics = {}
            recommendations = []
            
            # Open video file
            cap = cv2.VideoCapture(content.file_path)
            
            if not cap.isOpened():
                raise Exception("Cannot open video file")
            
            # Get video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Video Classification
            if config.enable_classification:
                classification_result = await self.video_classifier.classify(
                    content.file_path
                )
                classification = {
                    "category": classification_result.get("category", "unknown"),
                    "content_type": classification_result.get("content_type", "general"),
                    "style": classification_result.get("style", "unknown"),
                    "quality_level": classification_result.get("quality_level", "standard"),
                    "objects_detected": classification_result.get("objects", []),
                    "scenes": classification_result.get("scenes", []),
                    "confidence": classification_result.get("confidence", 0.0)
                }
            
            # Feature Extraction
            if config.enable_feature_extraction:
                # Sample frames for analysis
                sample_frames = []
                frame_indices = np.linspace(0, frame_count - 1, min(10, frame_count), dtype=int)
                
                for frame_idx in frame_indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, frame = cap.read()
                    if ret:
                        sample_frames.append(frame)
                
                # Extract visual features
                color_histogram = self._extract_color_histogram(sample_frames)
                motion_features = self._extract_motion_features(sample_frames)
                
                features = {
                    "resolution": f"{width}x{height}",
                    "aspect_ratio": width / height if height > 0 else 1.0,
                    "frame_rate": fps,
                    "duration": duration,
                    "frame_count": frame_count,
                    "color_histogram": color_histogram,
                    "motion_intensity": motion_features.get("intensity", 0.0),
                    "scene_changes": motion_features.get("scene_changes", 0),
                    "average_brightness": self._calculate_average_brightness(sample_frames)
                }
            
            # Quality Assessment
            if config.enable_quality_assessment:
                quality_metrics = {
                    "resolution_score": self._calculate_resolution_score(width, height),
                    "frame_rate_score": self._calculate_framerate_score(fps),
                    "compression_quality": self._estimate_compression_quality(sample_frames),
                    "stability_score": self._calculate_stability_score(sample_frames),
                    "overall_quality": self._calculate_video_quality_score(
                        width, height, fps, sample_frames
                    )
                }
            
            cap.release()
            
            # Generate Recommendations
            if config.enable_recommendations:
                recommendations = self._generate_video_recommendations(
                    classification, quality_metrics, features
                )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                classification, quality_metrics, features
            )
            
            return AnalysisResult(
                content_id=content.id,
                content_type="video",
                classification=classification,
                features=features,
                quality_metrics=quality_metrics,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            raise Exception(f"Video analysis failed: {str(e)}")

    async def _analyze_image(
        self,
        content: Content,
        config: AnalysisConfig
    ) -> AnalysisResult:
        """
        Analyze image content with AI models
        
        Args:
            content: Content database object
            config: Analysis configuration
            
        Returns:
            Image analysis result
        """
        try:
            classification = {}
            features = {}
            quality_metrics = {}
            recommendations = []
            
            # Load image
            with Image.open(content.file_path) as img:
                # Image Classification
                if config.enable_classification:
                    classification_result = await self.image_classifier.classify(
                        content.file_path
                    )
                    classification = {
                        "category": classification_result.get("category", "unknown"),
                        "style": classification_result.get("style", "unknown"),
                        "dominant_colors": classification_result.get("colors", []),
                        "objects_detected": classification_result.get("objects", []),
                        "faces_detected": classification_result.get("faces", 0),
                        "text_detected": classification_result.get("text", False),
                        "confidence": classification_result.get("confidence", 0.0)
                    }
                
                # Feature Extraction
                if config.enable_feature_extraction:
                    # Convert to numpy array for processing
                    img_array = np.array(img)
                    
                    # Color analysis
                    color_histogram = self._extract_image_color_histogram(img_array)
                    dominant_colors = self._extract_dominant_colors(img_array)
                    
                    # Texture analysis
                    texture_features = self._extract_texture_features(img_array)
                    
                    features = {
                        "dimensions": {"width": img.width, "height": img.height},
                        "aspect_ratio": img.width / img.height if img.height > 0 else 1.0,
                        "color_mode": img.mode,
                        "file_format": img.format,
                        "color_histogram": color_histogram,
                        "dominant_colors": dominant_colors,
                        "texture_complexity": texture_features.get("complexity", 0.0),
                        "edge_density": texture_features.get("edge_density", 0.0),
                        "brightness_mean": float(np.mean(img_array)),
                        "contrast_level": float(np.std(img_array))
                    }
                
                # Quality Assessment
                if config.enable_quality_assessment:
                    # Image quality metrics
                    sharpness_score = self._calculate_sharpness(img_array)
                    noise_level = self._estimate_noise_level(img_array)
                    exposure_quality = self._assess_exposure_quality(img_array)
                    
                    quality_metrics = {
                        "sharpness_score": float(sharpness_score),
                        "noise_level": float(noise_level),
                        "exposure_quality": float(exposure_quality),
                        "resolution_score": self._calculate_image_resolution_score(
                            img.width, img.height
                        ),
                        "overall_quality": self._calculate_image_quality_score(
                            sharpness_score, noise_level, exposure_quality, img_array
                        )
                    }
            
            # Generate Recommendations
            if config.enable_recommendations:
                recommendations = self._generate_image_recommendations(
                    classification, quality_metrics, features
                )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                classification, quality_metrics, features
            )
            
            return AnalysisResult(
                content_id=content.id,
                content_type="image",
                classification=classification,
                features=features,
                quality_metrics=quality_metrics,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            raise Exception(f"Image analysis failed: {str(e)}")

    async def _analyze_text(
        self,
        content: Content,
        config: AnalysisConfig
    ) -> AnalysisResult:
        """
        Analyze text content with NLP models
        
        Args:
            content: Content database object
            config: Analysis configuration
            
        Returns:
            Text analysis result
        """
        try:
            classification = {}
            features = {}
            quality_metrics = {}
            sentiment_analysis = {}
            recommendations = []
            
            # Read text content
            with open(content.file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Text Classification
            if config.enable_classification:
                classification_result = await self.text_classifier.classify(text_content)
                classification = {
                    "category": classification_result.get("category", "unknown"),
                    "genre": classification_result.get("genre", "unknown"),
                    "topic": classification_result.get("topic", "general"),
                    "language": classification_result.get("language", "unknown"),
                    "reading_level": classification_result.get("reading_level", "intermediate"),
                    "keywords": classification_result.get("keywords", []),
                    "entities": classification_result.get("entities", []),
                    "confidence": classification_result.get("confidence", 0.0)
                }
            
            # Sentiment Analysis
            if config.enable_sentiment_analysis:
                sentiment_result = await self.sentiment_analyzer.analyze(text_content)
                sentiment_analysis = {
                    "overall_sentiment": sentiment_result.get("sentiment", "neutral"),
                    "polarity": sentiment_result.get("polarity", 0.0),
                    "subjectivity": sentiment_result.get("subjectivity", 0.0),
                    "emotion_scores": sentiment_result.get("emotions", {}),
                    "confidence": sentiment_result.get("confidence", 0.0)
                }
            
            # Feature Extraction
            if config.enable_feature_extraction:
                # Text statistics
                words = text_content.split()
                sentences = text_content.split('.')
                paragraphs = text_content.split('\n\n')
                
                # Readability metrics
                readability_scores = self._calculate_readability_scores(text_content)
                
                # Linguistic features
                linguistic_features = self._extract_linguistic_features(text_content)
                
                features = {
                    "word_count": len(words),
                    "sentence_count": len(sentences),
                    "paragraph_count": len(paragraphs),
                    "character_count": len(text_content),
                    "average_word_length": np.mean([len(word) for word in words]) if words else 0,
                    "average_sentence_length": len(words) / len(sentences) if sentences else 0,
                    "readability_scores": readability_scores,
                    "linguistic_complexity": linguistic_features.get("complexity", 0.0),
                    "vocabulary_richness": linguistic_features.get("vocabulary_richness", 0.0),
                    "formality_score": linguistic_features.get("formality", 0.0)
                }
            
            # Quality Assessment
            if config.enable_quality_assessment:
                # Text quality metrics
                grammar_score = self._assess_grammar_quality(text_content)
                coherence_score = self._assess_coherence(text_content)
                
                quality_metrics = {
                    "grammar_score": float(grammar_score),
                    "coherence_score": float(coherence_score),
                    "spelling_errors": self._count_spelling_errors(text_content),
                    "readability_grade": readability_scores.get("grade_level", 0),
                    "overall_quality": self._calculate_text_quality_score(
                        grammar_score, coherence_score, text_content
                    )
                }
            
            # Generate Recommendations
            if config.enable_recommendations:
                recommendations = self._generate_text_recommendations(
                    classification, quality_metrics, features, sentiment_analysis
                )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                classification, quality_metrics, features
            )
            
            return AnalysisResult(
                content_id=content.id,
                content_type="text",
                classification=classification,
                features=features,
                quality_metrics=quality_metrics,
                sentiment_analysis=sentiment_analysis,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            raise Exception(f"Text analysis failed: {str(e)}")

    # Helper methods for analysis operations

    async def _get_content(self, content_id: str) -> Optional[Content]:
        """Get content from database"""
        query = select(Content).where(Content.id == content_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _save_analysis_result(self, content_id: str, analysis: AnalysisResult) -> None:
        """
Save analysis result to database"""
        try:
            analysis_record = ContentAnalysis(
                id=str(uuid.uuid4()),
                content_id=content_id,
                analysis_type="comprehensive",
                classification=analysis.classification,
                features=analysis.features,
                quality_metrics=analysis.quality_metrics,
                sentiment_analysis=analysis.sentiment_analysis,
                recommendations=analysis.recommendations,
                confidence_score=analysis.confidence_score,
                analysis_time=analysis.analysis_time,
                created_at=datetime.utcnow()
            )
            
            self.db.add(analysis_record)
            await self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to save analysis result: {str(e)}")

    def _serialize_analysis_result(self, analysis: AnalysisResult) -> Dict[str, Any]:
        """Convert analysis result to serializable format"""
        return {
            "content_id": analysis.content_id,
            "content_type": analysis.content_type,
            "classification": analysis.classification,
            "features": analysis.features,
            "quality_metrics": analysis.quality_metrics,
            "sentiment_analysis": analysis.sentiment_analysis,
            "recommendations": analysis.recommendations,
            "confidence_score": analysis.confidence_score,
            "analysis_time": analysis.analysis_time
        }

    # Quality assessment helper methods
    def _calculate_snr(self, audio_data: np.ndarray) -> float:
        """Calculate signal-to-noise ratio for audio"""
        signal_power = np.mean(audio_data**2)
        noise_estimate = np.var(audio_data) * 0.1  # Simplified noise estimation
        return 10 * np.log10(signal_power / max(noise_estimate, 1e-10))

    def _calculate_silence_ratio(self, audio_data: np.ndarray) -> float:
        """
Calculate ratio of silence in audio"""
        threshold = 0.01 * np.max(np.abs(audio_data))
        silent_samples = np.sum(np.abs(audio_data) < threshold)
        return silent_samples / len(audio_data)

    def _calculate_audio_quality_score(
        self,
        dynamic_range: float,
        snr: float,
        audio_data: np.ndarray
    ) -> float:
        """
Calculate overall audio quality score"""
        # Normalize metrics and combine
        dr_score = min(1.0, dynamic_range / 2.0)
        snr_score = min(1.0, max(0.0, (snr + 10) / 50))
        clipping_penalty = 0.3 if np.any(np.abs(audio_data) >= 0.99) else 0.0
        
        return max(0.0, (dr_score + snr_score) / 2 - clipping_penalty)

    def _calculate_sharpness(self, img_array: np.ndarray) -> float:
        """
Calculate image sharpness using Laplacian variance"""
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def _estimate_noise_level(self, img_array: np.ndarray) -> float:
        """
Estimate noise level in image"""
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Use standard deviation of Laplacian as noise estimate
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return np.std(laplacian)

    def _generate_audio_recommendations(
        self,
        classification: Dict,
        quality_metrics: Dict,
        features: Dict
    ) -> List[str]:
        """
Generate audio improvement recommendations"""
        recommendations = []
        
        if quality_metrics.get("overall_quality", 0) < 0.6:
            recommendations.append("Consider audio enhancement to improve quality")
        
        if quality_metrics.get("clipping_detected", False):
            recommendations.append("Audio clipping detected - reduce input levels")
        
        if quality_metrics.get("snr", 0) < 20:
            recommendations.append("High noise level detected - apply noise reduction")
        
        if features.get("rms_energy", 0) < 0.01:
            recommendations.append("Audio level is very low - consider normalization")
        
        return recommendations

    def _calculate_confidence_score(
        self,
        classification: Dict,
        quality_metrics: Dict,
        features: Dict
    ) -> float:
        """Calculate overall confidence score for analysis"""
        scores = []
        
        if classification.get("confidence"):
            scores.append(classification["confidence"])
        
        if quality_metrics.get("overall_quality"):
            scores.append(quality_metrics["overall_quality"])
        
        # Add feature-based confidence if available
        if features:
            scores.append(0.8)  # Base confidence for feature extraction
        
        return np.mean(scores) if scores else 0.0

    # Additional helper methods would be implemented for:
    # - _extract_color_histogram
    # - _extract_motion_features  
    # - _calculate_average_brightness
    # - _calculate_resolution_score
    # - _extract_texture_features
    # - _calculate_readability_scores
    # - _assess_grammar_quality
    # And many more specialized analysis functions...
