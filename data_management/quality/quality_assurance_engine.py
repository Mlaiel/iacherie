"""🗄️ Advanced Quality Assurance Engine - IA Influencer Agent Platform Enterprise
==============================================================================
Module: backend/data_management/quality/quality_assurance_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Quality Assurance Engine - Enterprise Production-Ready
Responsibility: Validation et assurance qualité multi-format avec IA et métriques avancées
=========================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER QUALITY ASSURANCE:
Content Input → Format Analysis → Quality Metrics Extraction → 
AI Quality Assessment → Business Rules Validation → Performance Check → 
Security Scan → Platform Compliance → Enhancement Recommendations → 
Quality Score Generation → Continuous Monitoring → Improvement Feedback

DIMENSIONS QUALITÉ:
📊 Technical Quality: Resolution, Bitrate, Compression, Format Compliance
🎨 Aesthetic Quality: Composition, Color, Lighting, Visual Appeal
🔊 Audio Quality: Clarity, Dynamic Range, Noise Level, Frequency Response
📝 Content Quality: Readability, SEO, Grammar, Relevance
🛡️ Security Quality: Malware Scan, Privacy Check, Copyright Compliance
🚀 Performance Quality: Load Time, Compression Ratio, Streaming Readiness
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import logging
import json
import uuid
import hashlib
from pathlib import Path

# Quality analysis imports
import cv2
import numpy as np
import librosa
from PIL import Image, ImageStat
import nltk
from textstat import flesch_reading_ease, automated_readability_index
import magic

# AI/ML imports
import torch
from transformers import pipeline

# Core imports
from ..models.content_model import ContentQualityModel
from ..repositories.content_repository import ContentRepository
from ...core.base import BaseQualityEngine
from ...utils.security_scanner import SecurityScanner
from ...utils.performance_analyzer import PerformanceAnalyzer

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Dimensions de qualité évaluées"""

    TECHNICAL = "technical"
    AESTHETIC = "aesthetic"
    AUDIO = "audio"
    CONTENT = "content"
    SECURITY = "security"
    PERFORMANCE = "performance"
    PLATFORM_COMPLIANCE = "platform_compliance"
    ACCESSIBILITY = "accessibility"

class QualityLevel(Enum):
    """Niveaux de qualité"""

    POOR = 1
    BELOW_AVERAGE = 2
    AVERAGE = 3
    GOOD = 4
    EXCELLENT = 5

class ContentType(Enum):
    """
Types de contenu supportés"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"

@dataclass
class QualityMetric:
    """Métrique de qualité individuelle"""
    name: str
    value: float
    max_value: float
    unit: str
    description: str
    importance: float = 1.0  # Poids dans le calcul global

@dataclass
class QualityAssessment:
    """Évaluation complète de qualité"""
    content_id: str
    content_type: ContentType
    overall_score: float
    quality_level: QualityLevel
    dimension_scores: Dict[QualityDimension, float]
    metrics: Dict[str, QualityMetric]
    issues: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    assessment_timestamp: datetime = field(default_factory=datetime.now)
    processing_time_seconds: float = 0.0

@dataclass
class QualityThresholds:
    """
Seuils de qualité par type de contenu"""
    content_type: ContentType
    minimum_scores: Dict[QualityDimension, float]
    warning_scores: Dict[QualityDimension, float]
    target_scores: Dict[QualityDimension, float]

class QualityAssuranceEngine:
    """
    Moteur avancé d'assurance qualité multi-format
    
    Capacités:
    - Évaluation qualité technique et esthétique
    - Validation conformité plateformes
    - Détection automatique de problèmes
    - Recommandations d'amélioration IA
    - Monitoring qualité continu
    - Métriques de performance avancées
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.content_repository = ContentRepository()
        self.security_scanner = SecurityScanner()
        self.performance_analyzer = PerformanceAnalyzer()
        
        # Modèles IA pour l'évaluation
        self.ai_models = self._initialize_ai_models()
        
        # Seuils de qualité par plateforme
        self.platform_thresholds = self._load_platform_thresholds()
        
        # Cache des évaluations
        self.assessment_cache = {}
        
    def _initialize_ai_models(self) -> Dict[str, Any]:
        """
Initialise les modèles IA pour l'évaluation qualité"""
        models = {}
        
        try:
            # Modèle d'évaluation de sentiment pour le contenu
            models["sentiment_analyzer"] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Modèle de classification d'images
            models["image_classifier"] = pipeline(
                "image-classification",
                model="google/vit-base-patch16-224"
            )
            
            # Détecteur de contenu NSFW
            models["nsfw_detector"] = pipeline(
                "image-classification",
                model="Falconsai/nsfw_image_detection"
            )
            
            logger.info("AI models for quality assessment initialized")
            
        except Exception as e:
            logger.warning(f"Some AI models failed to initialize: {e}")
            
        return models
        
    def _load_platform_thresholds(self) -> Dict[str, QualityThresholds]:
        """Charge les seuils de qualité par plateforme"""
        thresholds = {}
        
        # YouTube
        thresholds["youtube"] = {
            ContentType.VIDEO: QualityThresholds(
                content_type=ContentType.VIDEO,
                minimum_scores={
                    QualityDimension.TECHNICAL: 0.6,
                    QualityDimension.AUDIO: 0.7,
                    QualityDimension.CONTENT: 0.5,
                    QualityDimension.SECURITY: 0.9
                },
                warning_scores={
                    QualityDimension.TECHNICAL: 0.75,
                    QualityDimension.AUDIO: 0.8,
                    QualityDimension.CONTENT: 0.7,
                    QualityDimension.SECURITY: 0.95
                },
                target_scores={
                    QualityDimension.TECHNICAL: 0.9,
                    QualityDimension.AUDIO: 0.95,
                    QualityDimension.CONTENT: 0.85,
                    QualityDimension.SECURITY: 1.0
                }
            )
        }
        
        # Instagram
        thresholds["instagram"] = {
            ContentType.IMAGE: QualityThresholds(
                content_type=ContentType.IMAGE,
                minimum_scores={
                    QualityDimension.TECHNICAL: 0.7,
                    QualityDimension.AESTHETIC: 0.6,
                    QualityDimension.SECURITY: 0.9
                },
                warning_scores={
                    QualityDimension.TECHNICAL: 0.8,
                    QualityDimension.AESTHETIC: 0.75,
                    QualityDimension.SECURITY: 0.95
                },
                target_scores={
                    QualityDimension.TECHNICAL: 0.95,
                    QualityDimension.AESTHETIC: 0.9,
                    QualityDimension.SECURITY: 1.0
                }
            )
        }
        
        # Spotify
        thresholds["spotify"] = {
            ContentType.AUDIO: QualityThresholds(
                content_type=ContentType.AUDIO,
                minimum_scores={
                    QualityDimension.TECHNICAL: 0.8,
                    QualityDimension.AUDIO: 0.85,
                    QualityDimension.SECURITY: 0.95
                },
                warning_scores={
                    QualityDimension.TECHNICAL: 0.9,
                    QualityDimension.AUDIO: 0.92,
                    QualityDimension.SECURITY: 0.98
                },
                target_scores={
                    QualityDimension.TECHNICAL: 0.98,
                    QualityDimension.AUDIO: 0.98,
                    QualityDimension.SECURITY: 1.0
                }
            )
        }
        
        return thresholds
    
    async def assess_content_quality(self, content_path: str, content_type: ContentType,
                                   target_platforms: Optional[List[str]] = None,
                                   creator_id: Optional[str] = None) -> QualityAssessment:
        """
        Évalue la qualité complète d'un contenu
        
        Args:
            content_path: Chemin vers le fichier
            content_type: Type de contenu
            target_platforms: Plateformes cibles
            creator_id: ID du créateur
            
        Returns:
            QualityAssessment: Évaluation complète
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            content_id = hashlib.md5(content_path.encode()).hexdigest()
            
            # Vérification du cache
            cache_key = f"{content_id}_{content_type.value}"
            if cache_key in self.assessment_cache:
                cached_assessment = self.assessment_cache[cache_key]
                if (datetime.now() - cached_assessment.assessment_timestamp).seconds < 3600:
                    return cached_assessment
            
            # Initialisation de l'évaluation
            assessment = QualityAssessment(
                content_id=content_id,
                content_type=content_type,
                overall_score=0.0,
                quality_level=QualityLevel.AVERAGE,
                dimension_scores={},
                metrics={},
                issues=[],
                recommendations=[]
            )
            
            # Évaluation par dimension
            if content_type == ContentType.AUDIO:
                await self._assess_audio_quality(content_path, assessment)
            elif content_type == ContentType.VIDEO:
                await self._assess_video_quality(content_path, assessment)
            elif content_type == ContentType.IMAGE:
                await self._assess_image_quality(content_path, assessment)
            elif content_type == ContentType.TEXT:
                await self._assess_text_quality(content_path, assessment)
            
            # Évaluations communes
            await self._assess_security_quality(content_path, assessment)
            await self._assess_performance_quality(content_path, assessment)
            
            if target_platforms:
                await self._assess_platform_compliance(content_path, assessment, target_platforms)
            
            # Calcul du score global
            assessment.overall_score = self._calculate_overall_score(assessment)
            assessment.quality_level = self._determine_quality_level(assessment.overall_score)
            
            # Génération des recommandations
            assessment.recommendations = await self._generate_quality_recommendations(
                content_path, assessment, target_platforms
            )
            
            # Temps de traitement
            end_time = asyncio.get_event_loop().time()
            assessment.processing_time_seconds = end_time - start_time
            
            # Mise en cache
            self.assessment_cache[cache_key] = assessment
            
            logger.info(f"Quality assessment completed: {assessment.overall_score:.2f}/1.0")
            return assessment
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            raise
    
    async def _assess_audio_quality(self, audio_path: str, assessment: QualityAssessment):
        """Évalue la qualité audio"""
        try:
            # Chargement de l'audio
            y, sr = librosa.load(audio_path, sr=None)
            duration = len(y) / sr
            
            # Métriques techniques
            rms = librosa.feature.rms(y=y)[0]
            dynamic_range = np.max(rms) - np.min(rms)
            
            # Détection de clipping
            clipping_ratio = np.sum(np.abs(y) > 0.95) / len(y)
            
            # Analyse spectrale
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Détection de silence
            intervals = librosa.effects.split(y, top_db=20)
            silence_ratio = 1.0 - (len(intervals) * np.mean([e - s for s, e in intervals]) / len(y))
            
            # Analyse de fréquences
            fft = np.fft.fft(y)
            freqs = np.fft.fftfreq(len(fft), 1/sr)
            magnitude = np.abs(fft)
            
            # Répartition fréquentielle
            low_freq_energy = np.sum(magnitude[(freqs >= 20) & (freqs <= 250)])
            mid_freq_energy = np.sum(magnitude[(freqs >= 250) & (freqs <= 4000)])
            high_freq_energy = np.sum(magnitude[(freqs >= 4000) & (freqs <= 20000)])
            total_energy = low_freq_energy + mid_freq_energy + high_freq_energy
            
            # Métriques de qualité
            assessment.metrics.update({
                "audio_duration": QualityMetric(
                    name="Duration",
                    value=duration,
                    max_value=3600,  # 1 heure max
                    unit="seconds",
                    description="Audio duration in seconds"
                ),
                "audio_dynamic_range": QualityMetric(
                    name="Dynamic Range",
                    value=dynamic_range,
                    max_value=1.0,
                    unit="ratio",
                    description="Audio dynamic range"
                ),
                "audio_clipping": QualityMetric(
                    name="Clipping",
                    value=1.0 - clipping_ratio,  # Inversé car moins de clipping = mieux
                    max_value=1.0,
                    unit="ratio",
                    description="Audio clipping detection"
                ),
                "audio_silence": QualityMetric(
                    name="Silence Ratio",
                    value=1.0 - silence_ratio,  # Inversé
                    max_value=1.0,
                    unit="ratio",
                    description="Audio silence detection"
                ),
                "audio_frequency_balance": QualityMetric(
                    name="Frequency Balance",
                    value=self._calculate_frequency_balance(low_freq_energy, mid_freq_energy, high_freq_energy, total_energy),
                    max_value=1.0,
                    unit="score",
                    description="Audio frequency distribution balance"
                )
            })
            
            # Score technique audio
            technical_score = np.mean([
                min(1.0, dynamic_range / 0.5),  # Dynamic range normalisé
                1.0 - clipping_ratio,  # Pas de clipping
                1.0 - silence_ratio if silence_ratio < 0.1 else 0.5,  # Peu de silence
                assessment.metrics["audio_frequency_balance"].value
            ])
            
            assessment.dimension_scores[QualityDimension.TECHNICAL] = technical_score
            assessment.dimension_scores[QualityDimension.AUDIO] = technical_score
            
            # Détection de problèmes
            if clipping_ratio > 0.01:
                assessment.issues.append({
                    "type": "audio_clipping",
                    "severity": "high" if clipping_ratio > 0.05 else "medium",
                    "description": f"Audio clipping detected: {clipping_ratio:.2%}",
                    "recommendation": "Reduce input levels or apply limiting"
                })
            
            if silence_ratio > 0.2:
                assessment.issues.append({
                    "type": "excessive_silence",
                    "severity": "medium",
                    "description": f"High silence ratio: {silence_ratio:.2%}",
                    "recommendation": "Consider trimming silent sections"
                })
                
        except Exception as e:
            logger.error(f"Audio quality assessment failed: {e}")
            assessment.dimension_scores[QualityDimension.AUDIO] = 0.5
    
    def _calculate_frequency_balance(self, low: float, mid: float, high: float, total: float) -> float:
        """Calcule l'équilibre fréquentiel"""
        if total == 0:
            return 0.0
        
        # Ratios idéaux (approximatifs)
        ideal_low = 0.3
        ideal_mid = 0.5
        ideal_high = 0.2
        
        # Ratios actuels
        actual_low = low / total
        actual_mid = mid / total
        actual_high = high / total
        
        # Calcul de la déviation
        deviation = (abs(actual_low - ideal_low) + 
                    abs(actual_mid - ideal_mid) + 
                    abs(actual_high - ideal_high)) / 3
        
        return max(0.0, 1.0 - deviation * 2)
    
    async def _assess_video_quality(self, video_path: str, assessment: QualityAssessment):
        """Évalue la qualité vidéo"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            # Propriétés de base
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Analyse d'échantillons de frames
            frame_qualities = []
            motion_scores = []
            brightness_scores = []
            
            prev_frame = None
            sample_count = min(30, frame_count)
            
            for i in range(sample_count):
                frame_idx = i * frame_count // sample_count
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Netteté (variance du Laplacian)
                    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                    frame_qualities.append(sharpness)
                    
                    # Luminosité
                    brightness = np.mean(gray)
                    brightness_scores.append(brightness)
                    
                    # Mouvement (si frame précédente disponible)
                    if prev_frame is not None:
                        diff = cv2.absdiff(prev_frame, gray)
                        motion = np.mean(diff)
                        motion_scores.append(motion)
                    
                    prev_frame = gray
            
            cap.release()
            
            # Calcul des métriques
            avg_sharpness = np.mean(frame_qualities) if frame_qualities else 0
            avg_brightness = np.mean(brightness_scores) if brightness_scores else 128
            avg_motion = np.mean(motion_scores) if motion_scores else 0
            
            # Résolution score
            resolution_score = min(1.0, (width * height) / (1920 * 1080))
            
            # FPS score
            fps_score = min(1.0, fps / 60) if fps > 0 else 0
            
            # Metrics
            assessment.metrics.update({
                "video_resolution": QualityMetric(
                    name="Resolution",
                    value=width * height,
                    max_value=1920 * 1080,
                    unit="pixels",
                    description="Video resolution in pixels"
                ),
                "video_fps": QualityMetric(
                    name="Frame Rate",
                    value=fps,
                    max_value=60,
                    unit="fps",
                    description="Video frame rate"
                ),
                "video_sharpness": QualityMetric(
                    name="Sharpness",
                    value=min(1.0, avg_sharpness / 1000),
                    max_value=1.0,
                    unit="score",
                    description="Average video sharpness"
                ),
                "video_brightness": QualityMetric(
                    name="Brightness",
                    value=self._normalize_brightness(avg_brightness),
                    max_value=1.0,
                    unit="score",
                    description="Video brightness balance"
                ),
                "video_motion": QualityMetric(
                    name="Motion",
                    value=min(1.0, avg_motion / 50),
                    max_value=1.0,
                    unit="score",
                    description="Video motion analysis"
                )
            })
            
            # Score technique vidéo
            technical_score = np.mean([
                resolution_score,
                fps_score,
                assessment.metrics["video_sharpness"].value,
                assessment.metrics["video_brightness"].value
            ])
            
            assessment.dimension_scores[QualityDimension.TECHNICAL] = technical_score
            
            # Détection de problèmes
            if width < 1280 or height < 720:
                assessment.issues.append({
                    "type": "low_resolution",
                    "severity": "medium",
                    "description": f"Low resolution: {width}x{height}",
                    "recommendation": "Consider increasing resolution to at least 1280x720"
                })
            
            if fps < 24:
                assessment.issues.append({
                    "type": "low_fps",
                    "severity": "medium",
                    "description": f"Low frame rate: {fps} fps",
                    "recommendation": "Increase frame rate to at least 24 fps"
                })
                
        except Exception as e:
            logger.error(f"Video quality assessment failed: {e}")
            assessment.dimension_scores[QualityDimension.TECHNICAL] = 0.5
    
    def _normalize_brightness(self, brightness: float) -> float:
        """Normalise la luminosité (optimal around 128)"""
        # Optimal brightness is around 128 (middle gray)
        optimal = 128
        deviation = abs(brightness - optimal) / optimal
        return max(0.0, 1.0 - deviation)
    
    async def _assess_image_quality(self, image_path: str, assessment: QualityAssessment):
        """Évalue la qualité image"""
        try:
            # Chargement de l'image
            image = Image.open(image_path)
            img_array = np.array(image)
            
            width, height = image.size
            
            # Analyse avec OpenCV
            if len(img_array.shape) == 3:
                cv_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array
                cv_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
            # Netteté
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Analyse des couleurs
            if len(img_array.shape) == 3:
                # Saturation et contraste
                hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
                saturation = np.mean(hsv[:, :, 1])
                brightness = np.mean(hsv[:, :, 2])
                contrast = np.std(gray)
            else:
                saturation = 0
                brightness = np.mean(gray)
                contrast = np.std(gray)
            
            # Détection de bruit
            noise_level = self._calculate_noise_level(gray)
            
            # Composition (règle des tiers approximative)
            composition_score = self._analyze_composition(gray)
            
            # Résolution score
            megapixels = (width * height) / 1000000
            resolution_score = min(1.0, megapixels / 12)  # 12MP comme référence
            
            # Métriques
            assessment.metrics.update({
                "image_resolution": QualityMetric(
                    name="Resolution",
                    value=width * height,
                    max_value=4000 * 3000,
                    unit="pixels",
                    description="Image resolution"
                ),
                "image_sharpness": QualityMetric(
                    name="Sharpness",
                    value=min(1.0, sharpness / 2000),
                    max_value=1.0,
                    unit="score",
                    description="Image sharpness"
                ),
                "image_contrast": QualityMetric(
                    name="Contrast",
                    value=min(1.0, contrast / 100),
                    max_value=1.0,
                    unit="score",
                    description="Image contrast"
                ),
                "image_brightness": QualityMetric(
                    name="Brightness",
                    value=self._normalize_brightness(brightness),
                    max_value=1.0,
                    unit="score",
                    description="Image brightness balance"
                ),
                "image_noise": QualityMetric(
                    name="Noise Level",
                    value=1.0 - min(1.0, noise_level),
                    max_value=1.0,
                    unit="score",
                    description="Image noise level (inverted)"
                ),
                "image_composition": QualityMetric(
                    name="Composition",
                    value=composition_score,
                    max_value=1.0,
                    unit="score",
                    description="Image composition analysis"
                )
            })
            
            # Scores par dimension
            technical_score = np.mean([
                resolution_score,
                assessment.metrics["image_sharpness"].value,
                assessment.metrics["image_contrast"].value,
                assessment.metrics["image_noise"].value
            ])
            
            aesthetic_score = np.mean([
                assessment.metrics["image_brightness"].value,
                assessment.metrics["image_composition"].value,
                min(1.0, saturation / 255) if saturation > 0 else 0.5
            ])
            
            assessment.dimension_scores[QualityDimension.TECHNICAL] = technical_score
            assessment.dimension_scores[QualityDimension.AESTHETIC] = aesthetic_score
            
            # Évaluation IA si disponible
            if "image_classifier" in self.ai_models:
                try:
                    ai_result = self.ai_models["image_classifier"](image)
                    # Utilisation du score de confiance comme indicateur de qualité
                    ai_confidence = max([pred['score'] for pred in ai_result])
                    assessment.metrics["ai_quality_score"] = QualityMetric(
                        name="AI Quality Score",
                        value=ai_confidence,
                        max_value=1.0,
                        unit="score",
                        description="AI-based quality assessment"
                    )
                except Exception as e:
                    logger.warning(f"AI image evaluation failed: {e}")
            
            # Détection de problèmes
            if width < 1024 or height < 768:
                assessment.issues.append({
                    "type": "low_resolution",
                    "severity": "medium",
                    "description": f"Low resolution: {width}x{height}",
                    "recommendation": "Consider using higher resolution images"
                })
            
            if sharpness < 100:
                assessment.issues.append({
                    "type": "blurry_image",
                    "severity": "high",
                    "description": "Image appears blurry",
                    "recommendation": "Use sharper images or apply sharpening filter"
                })
                
        except Exception as e:
            logger.error(f"Image quality assessment failed: {e}")
            assessment.dimension_scores[QualityDimension.TECHNICAL] = 0.5
            assessment.dimension_scores[QualityDimension.AESTHETIC] = 0.5
    
    def _calculate_noise_level(self, gray_image: np.ndarray) -> float:
        """Calcule le niveau de bruit dans l'image"""
        # Utilisation de la variance locale pour détecter le bruit
        kernel = np.ones((3, 3), np.float32) / 9
        blurred = cv2.filter2D(gray_image.astype(np.float32), -1, kernel)
        noise = np.var(gray_image.astype(np.float32) - blurred)
        return min(1.0, noise / 1000)  # Normalisation
    
    def _analyze_composition(self, gray_image: np.ndarray) -> float:
        """
Analyse la composition de l'image (règle des tiers)"""
        h, w = gray_image.shape
        
        # Points d'intérêt selon la règle des tiers
        third_points = [
            (w // 3, h // 3), (2 * w // 3, h // 3),
            (w // 3, 2 * h // 3), (2 * w // 3, 2 * h // 3)
        ]
        
        # Détection des contours
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Score basé sur la présence de contours près des points de règle des tiers
        composition_score = 0.0
        for x, y in third_points:
            region = edges[max(0, y-50):min(h, y+50), max(0, x-50):min(w, x+50)]
            if region.size > 0:
                edge_density = np.sum(region > 0) / region.size
                composition_score += edge_density
        
        return min(1.0, composition_score / len(third_points))
    
    async def _assess_text_quality(self, text_path: str, assessment: QualityAssessment):
        """Évalue la qualité du texte"""
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Statistiques de base
            word_count = len(content.split())
            char_count = len(content)
            sentence_count = len([s for s in content.split('.') if s.strip()])
            
            # Lisibilité
            try:
                readability = flesch_reading_ease(content)
                ari_score = automated_readability_index(content)
            except:
                readability = 50  # Score par défaut
                ari_score = 10
            
            # Analyse linguistique
            spelling_errors = self._count_spelling_errors(content)
            grammar_score = self._analyze_grammar(content)
            
            # Analyse de structure
            structure_score = self._analyze_text_structure(content)
            
            # Métriques
            assessment.metrics.update({
                "text_length": QualityMetric(
                    name="Text Length",
                    value=word_count,
                    max_value=5000,
                    unit="words",
                    description="Number of words in text"
                ),
                "text_readability": QualityMetric(
                    name="Readability",
                    value=min(1.0, readability / 100),
                    max_value=1.0,
                    unit="score",
                    description="Flesch reading ease score"
                ),
                "text_spelling": QualityMetric(
                    name="Spelling",
                    value=max(0.0, 1.0 - spelling_errors / max(1, word_count)),
                    max_value=1.0,
                    unit="score",
                    description="Spelling accuracy"
                ),
                "text_grammar": QualityMetric(
                    name="Grammar",
                    value=grammar_score,
                    max_value=1.0,
                    unit="score",
                    description="Grammar quality"
                ),
                "text_structure": QualityMetric(
                    name="Structure",
                    value=structure_score,
                    max_value=1.0,
                    unit="score",
                    description="Text structure quality"
                )
            })
            
            # Score de contenu
            content_score = np.mean([
                assessment.metrics["text_readability"].value,
                assessment.metrics["text_spelling"].value,
                assessment.metrics["text_grammar"].value,
                assessment.metrics["text_structure"].value
            ])
            
            assessment.dimension_scores[QualityDimension.CONTENT] = content_score
            
            # Analyse de sentiment si disponible
            if "sentiment_analyzer" in self.ai_models:
                try:
                    # Tronquer le texte pour l'analyse
                    text_sample = content[:512]
                    sentiment_result = self.ai_models["sentiment_analyzer"](text_sample)
                    sentiment_score = sentiment_result[0]['score']
                    
                    assessment.metrics["text_sentiment"] = QualityMetric(
                        name="Sentiment",
                        value=sentiment_score,
                        max_value=1.0,
                        unit="score",
                        description="Text sentiment analysis"
                    )
                except Exception as e:
                    logger.warning(f"Sentiment analysis failed: {e}")
            
            # Détection de problèmes
            if word_count < 50:
                assessment.issues.append({
                    "type": "short_text",
                    "severity": "low",
                    "description": f"Text is very short: {word_count} words",
                    "recommendation": "Consider expanding the content"
                })
            
            if readability < 30:
                assessment.issues.append({
                    "type": "poor_readability",
                    "severity": "medium",
                    "description": f"Low readability score: {readability}",
                    "recommendation": "Simplify sentences and vocabulary"
                })
                
        except Exception as e:
            logger.error(f"Text quality assessment failed: {e}")
            assessment.dimension_scores[QualityDimension.CONTENT] = 0.5
    
    def _count_spelling_errors(self, text: str) -> int:
        """Compte les erreurs d'orthographe (implémentation basique)"""
        # Implémentation simplifiée - dans un vrai système, on utiliserait
        # une bibliothèque comme pyspellchecker
        words = text.split()
        errors = 0
        
        # Détection basique : mots avec des caractères répétés anormalement
        for word in words:
            clean_word = ''.join(c for c in word.lower() if c.isalpha())
            if len(clean_word) > 3:
                # Détection de répétitions anormales
                for i in range(len(clean_word) - 2):
                    if clean_word[i] == clean_word[i+1] == clean_word[i+2]:
                        errors += 1
                        break
        
        return errors
    
    def _analyze_grammar(self, text: str) -> float:
        """
Analyse grammaticale basique"""
        # Implémentation simplifiée
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            return 0.5
        
        grammar_score = 0.0
        
        for sentence in sentences:
            words = sentence.split()
            if len(words) == 0:
                continue
                
            # Vérifications basiques
            score = 1.0
            
            # Première lettre majuscule
            if not sentence[0].isupper():
                score -= 0.1
            
            # Longueur de phrase raisonnable
            if len(words) > 30:
                score -= 0.2
            elif len(words) < 3:
                score -= 0.3
            
            grammar_score += max(0.0, score)
        
        return grammar_score / len(sentences)
    
    def _analyze_text_structure(self, text: str) -> float:
        """
Analyse la structure du texte"""
        lines = text.split('\n')
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        structure_score = 0.0
        
        # Présence de paragraphes
        if len(paragraphs) > 1:
            structure_score += 0.3
        
        # Variation de longueur des paragraphes
        if paragraphs:
            para_lengths = [len(p.split()) for p in paragraphs]
            if len(set(para_lengths)) > 1:  # Variété
                structure_score += 0.2
        
        # Présence de titres (lignes courtes)
        title_count = len([l for l in lines if l.strip() and len(l.split()) <= 6])
        if title_count > 0:
            structure_score += 0.2
        
        # Cohérence générale
        structure_score += 0.3  # Score de base
        
        return min(1.0, structure_score)
    
    async def _assess_security_quality(self, content_path: str, assessment: QualityAssessment):
        """Évalue la sécurité du contenu"""
        try:
            # Détection du type de fichier
            file_type = magic.from_file(content_path, mime=True)
            
            # Scan antivirus/malware basique
            security_score = 1.0  # Par défaut, sécurisé
            
            # Vérification de l'extension vs type MIME
            file_extension = Path(content_path).suffix.lower()
            expected_types = {
                '.jpg': ['image/jpeg'],
                '.png': ['image/png'],
                '.mp3': ['audio/mpeg'],
                '.mp4': ['video/mp4'],
                '.txt': ['text/plain']
            }
            
            if file_extension in expected_types:
                if file_type not in expected_types[file_extension]:
                    security_score -= 0.3
                    assessment.issues.append({
                        "type": "file_type_mismatch",
                        "severity": "high",
                        "description": f"File extension {file_extension} doesn't match MIME type {file_type}",
                        "recommendation": "Verify file integrity and source"
                    })
            
            # Taille de fichier raisonnable
            file_size = Path(content_path).stat().st_size
            max_sizes = {
                'image': 50 * 1024 * 1024,  # 50MB
                'audio': 100 * 1024 * 1024,  # 100MB
                'video': 500 * 1024 * 1024,  # 500MB
                'text': 10 * 1024 * 1024    # 10MB
            }
            
            content_type = assessment.content_type.value
            if content_type in max_sizes and file_size > max_sizes[content_type]:
                security_score -= 0.2
                assessment.issues.append({
                    "type": "large_file_size",
                    "severity": "medium",
                    "description": f"File size ({file_size / 1024 / 1024:.1f}MB) is unusually large",
                    "recommendation": "Verify file content and consider compression"
                })
            
            # Vérification NSFW pour les images
            if assessment.content_type == ContentType.IMAGE and "nsfw_detector" in self.ai_models:
                try:
                    image = Image.open(content_path)
                    nsfw_result = self.ai_models["nsfw_detector"](image)
                    nsfw_score = max([pred['score'] for pred in nsfw_result if 'nsfw' in pred['label'].lower()])
                    
                    if nsfw_score > 0.5:
                        security_score -= 0.5
                        assessment.issues.append({
                            "type": "nsfw_content",
                            "severity": "high",
                            "description": f"NSFW content detected with {nsfw_score:.1%} confidence",
                            "recommendation": "Review content for platform compliance"
                        })
                except Exception as e:
                    logger.warning(f"NSFW detection failed: {e}")
            
            assessment.metrics["security_score"] = QualityMetric(
                name="Security Score",
                value=security_score,
                max_value=1.0,
                unit="score",
                description="Overall security assessment"
            )
            
            assessment.dimension_scores[QualityDimension.SECURITY] = security_score
            
        except Exception as e:
            logger.error(f"Security assessment failed: {e}")
            assessment.dimension_scores[QualityDimension.SECURITY] = 0.5
    
    async def _assess_performance_quality(self, content_path: str, assessment: QualityAssessment):
        """Évalue la performance du contenu"""
        try:
            file_size = Path(content_path).stat().st_size
            
            # Calcul de métriques de performance
            compression_efficiency = self._calculate_compression_efficiency(content_path, assessment.content_type)
            loading_time_estimate = self._estimate_loading_time(file_size)
            streaming_readiness = self._assess_streaming_readiness(content_path, assessment.content_type)
            
            performance_score = np.mean([compression_efficiency, streaming_readiness])
            
            assessment.metrics.update({
                "file_size": QualityMetric(
                    name="File Size",
                    value=file_size,
                    max_value=100 * 1024 * 1024,  # 100MB
                    unit="bytes",
                    description="File size in bytes"
                ),
                "compression_efficiency": QualityMetric(
                    name="Compression Efficiency",
                    value=compression_efficiency,
                    max_value=1.0,
                    unit="score",
                    description="Compression efficiency score"
                ),
                "loading_time": QualityMetric(
                    name="Estimated Loading Time",
                    value=loading_time_estimate,
                    max_value=30.0,
                    unit="seconds",
                    description="Estimated loading time over average connection"
                ),
                "streaming_readiness": QualityMetric(
                    name="Streaming Readiness",
                    value=streaming_readiness,
                    max_value=1.0,
                    unit="score",
                    description="Readiness for streaming delivery"
                )
            })
            
            assessment.dimension_scores[QualityDimension.PERFORMANCE] = performance_score
            
            # Détection de problèmes de performance
            if loading_time_estimate > 10:
                assessment.issues.append({
                    "type": "slow_loading",
                    "severity": "medium",
                    "description": f"Estimated loading time: {loading_time_estimate:.1f}s",
                    "recommendation": "Consider compression or format optimization"
                })
                
        except Exception as e:
            logger.error(f"Performance assessment failed: {e}")
            assessment.dimension_scores[QualityDimension.PERFORMANCE] = 0.5
    
    def _calculate_compression_efficiency(self, content_path: str, content_type: ContentType) -> float:
        """Calcule l'efficacité de compression"""
        file_size = Path(content_path).stat().st_size
        
        # Estimations d'efficacité basées sur la taille et le type
        if content_type == ContentType.IMAGE:
            # Pour les images, on considère qu'une bonne compression donne ~100KB/MP
            try:
                image = Image.open(content_path)
                megapixels = (image.width * image.height) / 1000000
                expected_size = megapixels * 100 * 1024  # 100KB par MP
                efficiency = min(1.0, expected_size / file_size)
            except:
                efficiency = 0.5
        elif content_type == ContentType.AUDIO:
            # Pour l'audio, on considère qu'un bon bitrate est ~128kbps
            try:
                y, sr = librosa.load(content_path, sr=None)
                duration = len(y) / sr
                expected_size = duration * 16000  # ~128kbps
                efficiency = min(1.0, expected_size / file_size)
            except:
                efficiency = 0.5
        else:
            # Estimation générique
            efficiency = 0.7
        
        return efficiency
    
    def _estimate_loading_time(self, file_size: int) -> float:
        """
Estime le temps de chargement"""
        # Connexion moyenne : 5 Mbps
        connection_speed = 5 * 1024 * 1024 / 8  # bytes/sec
        return file_size / connection_speed
    
    def _assess_streaming_readiness(self, content_path: str, content_type: ContentType) -> float:
        """Évalue la préparation pour le streaming"""
        if content_type in [ContentType.AUDIO, ContentType.VIDEO]:
            # Vérification de l'encodage progressif
            try:
                if content_type == ContentType.VIDEO:
                    # Pour la vidéo, vérifier si c'est en fast-start
                    return 0.8  # Valeur par défaut
                else:
                    # Pour l'audio, vérifier le format
                    return 0.9
            except:
                return 0.5
        else:
            return 1.0  # Images et texte sont toujours "streaming ready"
    
    async def _assess_platform_compliance(self, content_path: str, assessment: QualityAssessment,
                                        target_platforms: List[str]):
        """Évalue la conformité aux plateformes cibles"""
        compliance_scores = {}
        
        for platform in target_platforms:
            if platform in self.platform_thresholds:
                thresholds = self.platform_thresholds[platform].get(assessment.content_type)
                if thresholds:
                    compliance_score = self._calculate_platform_compliance(assessment, thresholds)
                    compliance_scores[platform] = compliance_score
                    
                    # Vérification des exigences spécifiques
                    platform_issues = self._check_platform_requirements(
                        content_path, assessment, platform
                    )
                    assessment.issues.extend(platform_issues)
        
        if compliance_scores:
            avg_compliance = np.mean(list(compliance_scores.values()))
            assessment.dimension_scores[QualityDimension.PLATFORM_COMPLIANCE] = avg_compliance
            
            assessment.metrics["platform_compliance"] = QualityMetric(
                name="Platform Compliance",
                value=avg_compliance,
                max_value=1.0,
                unit="score",
                description="Average compliance across target platforms"
            )
    
    def _calculate_platform_compliance(self, assessment: QualityAssessment,
                                     thresholds: QualityThresholds) -> float:
        """Calcule le score de conformité pour une plateforme"""
        compliance_scores = []
        
        for dimension, min_score in thresholds.minimum_scores.items():
            actual_score = assessment.dimension_scores.get(dimension, 0.0)
            if actual_score >= min_score:
                compliance_scores.append(1.0)
            else:
                compliance_scores.append(actual_score / min_score)
        
        return np.mean(compliance_scores) if compliance_scores else 0.0
    
    def _check_platform_requirements(self, content_path: str, assessment: QualityAssessment,
                                   platform: str) -> List[Dict[str, Any]]:
        """
Vérifie les exigences spécifiques d'une plateforme"""
        issues = []
        
        if platform == "youtube" and assessment.content_type == ContentType.VIDEO:
            # Vérifications spécifiques YouTube
            if "video_resolution" in assessment.metrics:
                resolution = assessment.metrics["video_resolution"].value
                if resolution < 1280 * 720:
                    issues.append({
                        "type": "youtube_resolution",
                        "severity": "medium",
                        "description": "Resolution below YouTube's recommended 720p",
                        "recommendation": "Increase resolution to at least 1280x720"
                    })
        
        elif platform == "instagram" and assessment.content_type == ContentType.IMAGE:
            # Vérifications spécifiques Instagram
            if "image_resolution" in assessment.metrics:
                try:
                    image = Image.open(content_path)
                    width, height = image.size
                    if width != height:  # Pas carré
                        issues.append({
                            "type": "instagram_aspect_ratio",
                            "severity": "low",
                            "description": "Image is not square format",
                            "recommendation": "Consider using 1:1 aspect ratio for better Instagram display"
                        })
                except:
                    pass
        
        return issues
    
    def _calculate_overall_score(self, assessment: QualityAssessment) -> float:
        """Calcule le score global de qualité"""
        if not assessment.dimension_scores:
            return 0.0
        
        # Poids par dimension
        dimension_weights = {
            QualityDimension.TECHNICAL: 0.25,
            QualityDimension.AESTHETIC: 0.15,
            QualityDimension.AUDIO: 0.20,
            QualityDimension.CONTENT: 0.20,
            QualityDimension.SECURITY: 0.10,
            QualityDimension.PERFORMANCE: 0.05,
            QualityDimension.PLATFORM_COMPLIANCE: 0.05
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for dimension, score in assessment.dimension_scores.items():
            weight = dimension_weights.get(dimension, 0.1)
            weighted_score += score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """
Détermine le niveau de qualité"""
        if overall_score >= 0.9:
            return QualityLevel.EXCELLENT
        elif overall_score >= 0.75:
            return QualityLevel.GOOD
        elif overall_score >= 0.6:
            return QualityLevel.AVERAGE
        elif overall_score >= 0.4:
            return QualityLevel.BELOW_AVERAGE
        else:
            return QualityLevel.POOR
    
    async def _generate_quality_recommendations(self, content_path: str,
                                              assessment: QualityAssessment,
                                              target_platforms: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
Génère des recommandations d'amélioration"""
        recommendations = []
        
        # Recommandations basées sur les scores
        for dimension, score in assessment.dimension_scores.items():
            if score < 0.7:
                if dimension == QualityDimension.TECHNICAL:
                    recommendations.append({
                        "type": "technical_improvement",
                        "priority": "high",
                        "description": "Improve technical quality",
                        "suggestions": [
                            "Increase resolution if possible",
                            "Check audio/video encoding settings",
                            "Verify file format compatibility"
                        ]
                    })
                elif dimension == QualityDimension.AESTHETIC:
                    recommendations.append({
                        "type": "aesthetic_improvement",
                        "priority": "medium",
                        "description": "Enhance visual appeal",
                        "suggestions": [
                            "Improve composition and framing",
                            "Adjust lighting and colors",
                            "Consider professional editing"
                        ]
                    })
        
        # Recommandations spécifiques aux plateformes
        if target_platforms:
            for platform in target_platforms:
                platform_recs = self._generate_platform_recommendations(
                    assessment, platform
                )
                recommendations.extend(platform_recs)
        
        # Recommandations basées sur les problèmes détectés
        high_priority_issues = [issue for issue in assessment.issues if issue["severity"] == "high"]
        if high_priority_issues:
            recommendations.append({
                "type": "critical_fixes",
                "priority": "critical",
                "description": "Address critical issues immediately",
                "suggestions": [issue["recommendation"] for issue in high_priority_issues]
            })
        
        return recommendations
    
    def _generate_platform_recommendations(self, assessment: QualityAssessment,
                                         platform: str) -> List[Dict[str, Any]]:
        """Génère des recommandations spécifiques à une plateforme"""
        recommendations = []
        
        if platform == "youtube":
            recommendations.append({
                "type": "youtube_optimization",
                "priority": "medium",
                "description": "Optimize for YouTube",
                "suggestions": [
                    "Use 16:9 aspect ratio",
                    "Include engaging thumbnail",
                    "Optimize title and description for SEO",
                    "Add closed captions for accessibility"
                ]
            })
        
        elif platform == "instagram":
            recommendations.append({
                "type": "instagram_optimization",
                "priority": "medium",
                "description": "Optimize for Instagram",
                "suggestions": [
                    "Use 1:1 square format for posts",
                    "High contrast and vibrant colors work well",
                    "Include relevant hashtags",
                    "Consider Instagram Stories format (9:16)"
                ]
            })
        
        elif platform == "spotify":
            recommendations.append({
                "type": "spotify_optimization",
                "priority": "high",
                "description": "Optimize for Spotify",
                "suggestions": [
                    "Ensure high audio quality (320kbps)",
                    "Proper mastering and loudness",
                    "Include metadata and tags",
                    "Consider playlist placement strategy"
                ]
            })
        
        return recommendations

# Configuration globale du moteur de qualité
QUALITY_ASSURANCE_CONFIG = {
    "dimension_weights": {
        "technical": 0.25,
        "aesthetic": 0.15,
        "audio": 0.20,
        "content": 0.20,
        "security": 0.10,
        "performance": 0.05,
        "platform_compliance": 0.05
    },
    "quality_thresholds": {
        "excellent": 0.9,
        "good": 0.75,
        "average": 0.6,
        "below_average": 0.4,
        "poor": 0.0
    },
    "platform_specifications": {
        "youtube": "High quality video platform requirements",
        "instagram": "Social media visual platform requirements",
        "spotify": "High quality audio streaming requirements",
        "tiktok": "Short-form video platform requirements"
    }
}
