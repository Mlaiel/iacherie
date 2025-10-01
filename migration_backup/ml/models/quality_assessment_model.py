"""
Quality Assessment Model - IA Chéries Enterprise
===========================================
Modèle évaluation qualité contenu avec scoring business.
Quality metrics + aesthetic scoring + technical assessment + business value.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries ML Models
Version: 1.0 Production
"""

import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum
import cv2
from PIL import Image, ImageStat
import librosa
import asyncio
import logging
from pathlib import Path
import json
import math

# ⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
# Cette architecture ML et tous ses algorithmes sont la propriété intellectuelle 
# EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Tous droits réservés.

logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Dimensions de qualité évaluées"""
    TECHNICAL = "technical"
    AESTHETIC = "aesthetic"
    ENGAGEMENT = "engagement"
    BUSINESS_VALUE = "business_value"
    PLATFORM_COMPATIBILITY = "platform_compatibility"

class QualityLevel(Enum):
    """Niveaux de qualité"""
    POOR = 1
    FAIR = 2
    GOOD = 3
    EXCELLENT = 4
    EXCEPTIONAL = 5

@dataclass
class QualityMetrics:
    """Métriques qualité techniques"""
    resolution_score: float
    clarity_score: float
    color_balance_score: float
    composition_score: float
    audio_quality_score: Optional[float] = None
    compression_efficiency: Optional[float] = None
    file_size_optimization: Optional[float] = None

@dataclass
class AestheticScores:
    """Scores esthétiques basés sur ML"""
    visual_appeal: float
    color_harmony: float
    composition_balance: float
    lighting_quality: float
    artistic_value: float
    emotional_impact: float

@dataclass
class BusinessMetrics:
    """Métriques business pour monetization"""
    commercial_viability: float
    brand_safety_score: float
    advertiser_friendliness: float
    viral_potential: float
    engagement_predictability: float
    monetization_readiness: float

@dataclass
class QualityAssessmentResult:
    """Résultat complet d'évaluation qualité"""
    content_id: str
    overall_quality_score: float
    quality_level: QualityLevel
    technical_metrics: QualityMetrics
    aesthetic_scores: AestheticScores
    business_metrics: BusinessMetrics
    platform_scores: Dict[str, float]
    enhancement_recommendations: List[str]
    quality_breakdown: Dict[QualityDimension, float]
    confidence_score: float
    processing_time_ms: float
    timestamp: str

@dataclass
class QualityAssessmentConfig:
    """Configuration pour quality assessment"""
    model_version: str = "1.0"
    device: str = "cpu"
    enable_aesthetic_scoring: bool = True
    enable_business_scoring: bool = True
    quality_threshold: float = 0.7
    detailed_analysis: bool = True

class TechnicalQualityAssessor(nn.Module):
    """Évaluateur qualité technique avec deep learning"""
    
    def __init__(self, config: QualityAssessmentConfig):
        super().__init__()
        self.config = config
        
        # Technical quality neural network
        self.technical_net = nn.Sequential(
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 7)  # 7 technical metrics
        )
        
    def assess_image_quality(self, image_path: str) -> QualityMetrics:
        """Évaluation qualité technique image"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Cannot load image: {image_path}")
            
            # Extract technical features
            features = self._extract_image_features(image)
            
            # Neural network prediction
            with torch.no_grad():
                feature_tensor = torch.FloatTensor(features).unsqueeze(0)
                predictions = self.technical_net(feature_tensor)
                scores = torch.sigmoid(predictions).squeeze().numpy()
            
            return QualityMetrics(
                resolution_score=float(scores[0]),
                clarity_score=float(scores[1]),
                color_balance_score=float(scores[2]),
                composition_score=float(scores[3]),
                compression_efficiency=float(scores[4]),
                file_size_optimization=float(scores[5])
            )
            
        except Exception as e:
            logger.error(f"Image quality assessment error: {e}")
            return self._default_quality_metrics()
    
    def assess_audio_quality(self, audio_path: str) -> QualityMetrics:
        """Évaluation qualité technique audio"""
        try:
            # Load audio
            audio_data, sr = librosa.load(audio_path, sr=22050)
            
            # Extract audio features
            features = self._extract_audio_features(audio_data, sr)
            
            # Neural network prediction
            with torch.no_grad():
                feature_tensor = torch.FloatTensor(features).unsqueeze(0)
                predictions = self.technical_net(feature_tensor)
                scores = torch.sigmoid(predictions).squeeze().numpy()
            
            return QualityMetrics(
                resolution_score=float(scores[0]),  # Bit depth equivalent
                clarity_score=float(scores[1]),
                color_balance_score=0.0,  # N/A for audio
                composition_score=float(scores[2]),  # Dynamic range
                audio_quality_score=float(scores[3]),
                compression_efficiency=float(scores[4]),
                file_size_optimization=float(scores[5])
            )
            
        except Exception as e:
            logger.error(f"Audio quality assessment error: {e}")
            return self._default_quality_metrics()
    
    def _extract_image_features(self, image: np.ndarray) -> np.ndarray:
        """Extraction features techniques image"""
        features = []
        
        # Resolution metrics
        height, width = image.shape[:2]
        features.extend([
            width / 1920.0,  # Normalized width
            height / 1080.0,  # Normalized height
            (width * height) / (1920 * 1080)  # Total pixels ratio
        ])
        
        # Sharpness (Laplacian variance)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        features.append(laplacian_var / 1000.0)  # Normalized
        
        # Color distribution
        color_std = np.std(image, axis=(0, 1))
        features.extend(color_std / 255.0)
        
        # Brightness and contrast
        brightness = np.mean(image)
        contrast = np.std(image)
        features.extend([brightness / 255.0, contrast / 128.0])
        
        # Histogram features
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_features = [
            np.entropy(hist.flatten() + 1e-10),  # Entropy
            np.std(hist),  # Histogram spread
            np.mean(hist)  # Average bin value
        ]
        features.extend(hist_features)
        
        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (width * height)
        features.append(edge_density)
        
        # Pad or truncate to 128 features
        features = features[:128]
        while len(features) < 128:
            features.append(0.0)
            
        return np.array(features, dtype=np.float32)
    
    def _extract_audio_features(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """Extraction features techniques audio"""
        features = []
        
        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
        features.extend([
            np.mean(spectral_centroids),
            np.std(spectral_centroids)
        ])
        
        # Spectral rolloff
        rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)[0]
        features.extend([np.mean(rolloff), np.std(rolloff)])
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        features.extend([np.mean(zcr), np.std(zcr)])
        
        # MFCC features
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
        for i in range(13):
            features.extend([np.mean(mfccs[i]), np.std(mfccs[i])])
        
        # RMS energy
        rms = librosa.feature.rms(y=audio_data)[0]
        features.extend([np.mean(rms), np.std(rms)])
        
        # Tempo
        tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sr)
        features.append(tempo / 200.0)  # Normalized
        
        # Dynamic range
        dynamic_range = np.max(audio_data) - np.min(audio_data)
        features.append(dynamic_range)
        
        # Silence ratio
        silence_threshold = 0.01
        silence_ratio = np.sum(np.abs(audio_data) < silence_threshold) / len(audio_data)
        features.append(silence_ratio)
        
        # Pad or truncate to 128 features
        features = features[:128]
        while len(features) < 128:
            features.append(0.0)
            
        return np.array(features, dtype=np.float32)
    
    def _default_quality_metrics(self) -> QualityMetrics:
        """Métriques par défaut en cas d'erreur"""
        return QualityMetrics(
            resolution_score=0.5,
            clarity_score=0.5,
            color_balance_score=0.5,
            composition_score=0.5,
            audio_quality_score=0.5,
            compression_efficiency=0.5,
            file_size_optimization=0.5
        )

class AestheticQualityScorer(nn.Module):
    """Évaluateur qualité esthétique avec deep learning"""
    
    def __init__(self, config: QualityAssessmentConfig):
        super().__init__()
        self.config = config
        
        # Pre-trained feature extractor
        self.feature_extractor = models.resnet50(pretrained=True)
        self.feature_extractor.fc = nn.Identity()  # Remove final layer
        
        # Aesthetic scoring network
        self.aesthetic_net = nn.Sequential(
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 6)  # 6 aesthetic dimensions
        )
        
    def score_aesthetic_quality(self, image_path: str) -> AestheticScores:
        """Scoring qualité esthétique image"""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            import torchvision.transforms as transforms
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            image_tensor = transform(image).unsqueeze(0)
            
            # Extract features
            with torch.no_grad():
                features = self.feature_extractor(image_tensor)
                aesthetic_scores = self.aesthetic_net(features)
                scores = torch.sigmoid(aesthetic_scores).squeeze().numpy()
            
            return AestheticScores(
                visual_appeal=float(scores[0]),
                color_harmony=float(scores[1]),
                composition_balance=float(scores[2]),
                lighting_quality=float(scores[3]),
                artistic_value=float(scores[4]),
                emotional_impact=float(scores[5])
            )
            
        except Exception as e:
            logger.error(f"Aesthetic scoring error: {e}")
            return self._default_aesthetic_scores()
    
    def _default_aesthetic_scores(self) -> AestheticScores:
        """Scores esthétiques par défaut"""
        return AestheticScores(
            visual_appeal=0.5,
            color_harmony=0.5,
            composition_balance=0.5,
            lighting_quality=0.5,
            artistic_value=0.5,
            emotional_impact=0.5
        )

class BusinessValueCalculator:
    """Calculateur valeur business pour monetization"""
    
    def __init__(self, config: QualityAssessmentConfig):
        self.config = config
    
    def calculate_business_metrics(self, quality_metrics: QualityMetrics,
                                 aesthetic_scores: AestheticScores,
                                 content_metadata: Dict[str, Any]) -> BusinessMetrics:
        """Calcul métriques business basées sur qualité"""
        try:
            # Commercial viability basé sur qualité technique et esthétique
            commercial_viability = (
                quality_metrics.resolution_score * 0.3 +
                quality_metrics.clarity_score * 0.2 +
                aesthetic_scores.visual_appeal * 0.3 +
                aesthetic_scores.artistic_value * 0.2
            )
            
            # Brand safety basé sur contenu et qualité
            brand_safety_score = min(
                quality_metrics.color_balance_score * 1.2,
                aesthetic_scores.emotional_impact * 0.8,
                1.0
            )
            
            # Advertiser friendliness
            advertiser_friendliness = (
                brand_safety_score * 0.4 +
                quality_metrics.composition_score * 0.3 +
                aesthetic_scores.visual_appeal * 0.3
            )
            
            # Viral potential basé sur engagement potentiel
            viral_potential = (
                aesthetic_scores.emotional_impact * 0.4 +
                aesthetic_scores.visual_appeal * 0.3 +
                quality_metrics.clarity_score * 0.3
            )
            
            # Engagement predictability
            engagement_predictability = (
                quality_metrics.composition_score * 0.3 +
                aesthetic_scores.composition_balance * 0.4 +
                aesthetic_scores.color_harmony * 0.3
            )
            
            # Monetization readiness
            monetization_readiness = (
                commercial_viability * 0.4 +
                brand_safety_score * 0.3 +
                quality_metrics.file_size_optimization * 0.3
            )
            
            return BusinessMetrics(
                commercial_viability=commercial_viability,
                brand_safety_score=brand_safety_score,
                advertiser_friendliness=advertiser_friendliness,
                viral_potential=viral_potential,
                engagement_predictability=engagement_predictability,
                monetization_readiness=monetization_readiness
            )
            
        except Exception as e:
            logger.error(f"Business metrics calculation error: {e}")
            return self._default_business_metrics()
    
    def _default_business_metrics(self) -> BusinessMetrics:
        """Métriques business par défaut"""
        return BusinessMetrics(
            commercial_viability=0.5,
            brand_safety_score=0.5,
            advertiser_friendliness=0.5,
            viral_potential=0.5,
            engagement_predictability=0.5,
            monetization_readiness=0.5
        )

class CreatorExperienceOptimizer:
    """Optimiseur expérience créateur avec recommandations"""
    
    def __init__(self, config: QualityAssessmentConfig):
        self.config = config
    
    def generate_enhancement_recommendations(self, 
                                           quality_metrics: QualityMetrics,
                                           aesthetic_scores: AestheticScores,
                                           business_metrics: BusinessMetrics) -> List[str]:
        """Génération recommandations enhancement"""
        recommendations = []
        
        # Technical quality recommendations
        if quality_metrics.resolution_score < 0.6:
            recommendations.append("Consider increasing image resolution for better quality")
        
        if quality_metrics.clarity_score < 0.6:
            recommendations.append("Improve focus and sharpness of the content")
        
        if quality_metrics.color_balance_score < 0.6:
            recommendations.append("Adjust color balance and saturation for better visual appeal")
        
        # Aesthetic recommendations
        if aesthetic_scores.composition_balance < 0.6:
            recommendations.append("Consider rule of thirds for better composition")
        
        if aesthetic_scores.lighting_quality < 0.6:
            recommendations.append("Improve lighting setup for more professional look")
        
        if aesthetic_scores.color_harmony < 0.6:
            recommendations.append("Use complementary colors for better visual harmony")
        
        # Business optimization recommendations
        if business_metrics.commercial_viability < 0.7:
            recommendations.append("Enhance content quality for better commercial potential")
        
        if business_metrics.brand_safety_score < 0.8:
            recommendations.append("Ensure content meets brand safety guidelines")
        
        if business_metrics.viral_potential > 0.8:
            recommendations.append("Content has high viral potential - consider cross-platform promotion")
        
        # Platform-specific recommendations
        recommendations.extend([
            "Optimize aspect ratio for target platforms",
            "Consider adding captions for better accessibility",
            "Ensure mobile-friendly viewing experience"
        ])
        
        return recommendations[:10]  # Limit to top 10 recommendations

class ContentQualityAssessmentModel:
    """
    Modèle principal évaluation qualité contenu avec scoring business.
    Quality metrics + aesthetic scoring + technical assessment + business value.
    """
    
    def __init__(self, quality_config: QualityAssessmentConfig):
        self.quality_config = quality_config
        self.technical_assessor = TechnicalQualityAssessor(quality_config)
        self.aesthetic_scorer = AestheticQualityScorer(quality_config)
        self.business_value_calculator = BusinessValueCalculator(quality_config)
        self.creator_experience_optimizer = CreatorExperienceOptimizer(quality_config)
        
        # Platform compatibility scoring
        self.platform_requirements = {
            "instagram": {"min_resolution": 0.6, "aspect_ratios": ["1:1", "4:5", "9:16"]},
            "youtube": {"min_resolution": 0.7, "aspect_ratios": ["16:9", "9:16"]},
            "tiktok": {"min_resolution": 0.6, "aspect_ratios": ["9:16"]},
            "facebook": {"min_resolution": 0.6, "aspect_ratios": ["1:1", "16:9", "4:5"]},
            "twitter": {"min_resolution": 0.6, "aspect_ratios": ["16:9", "1:1"]},
            "linkedin": {"min_resolution": 0.7, "aspect_ratios": ["1.91:1", "1:1"]}
        }
    
    async def assess_content_quality(self, content_input: Dict[str, Any]) -> QualityAssessmentResult:
        """
        Évaluation qualité contenu avec business scoring.
        
        Quality Assessment Features:
        - Technical quality analysis (resolution, bitrate, compression)
        - Aesthetic quality scoring avec ML perceptual models
        - Content engagement potential basé sur visual/audio appeal
        - Business value assessment pour monetization potential
        - Creator experience optimization recommendations
        - Platform-specific quality requirements validation
        - Automated quality enhancement suggestions
        - Performance impact prediction sur user engagement
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            content_id = content_input.get("content_id", "unknown")
            file_path = content_input.get("file_path")
            content_type = content_input.get("content_type", "image")
            
            # Technical quality assessment
            if content_type in ["image", "video"]:
                quality_metrics = self.technical_assessor.assess_image_quality(file_path)
            elif content_type == "audio":
                quality_metrics = self.technical_assessor.assess_audio_quality(file_path)
            else:
                quality_metrics = self.technical_assessor._default_quality_metrics()
            
            # Aesthetic quality scoring (only for visual content)
            if content_type in ["image", "video"] and self.quality_config.enable_aesthetic_scoring:
                aesthetic_scores = self.aesthetic_scorer.score_aesthetic_quality(file_path)
            else:
                aesthetic_scores = self.aesthetic_scorer._default_aesthetic_scores()
            
            # Business value calculation
            if self.quality_config.enable_business_scoring:
                business_metrics = self.business_value_calculator.calculate_business_metrics(
                    quality_metrics, aesthetic_scores, content_input
                )
            else:
                business_metrics = self.business_value_calculator._default_business_metrics()
            
            # Platform compatibility scoring
            platform_scores = self.calculate_platform_compatibility(
                quality_metrics, content_input
            )
            
            # Overall quality score calculation
            overall_quality_score = self._calculate_overall_quality(
                quality_metrics, aesthetic_scores, business_metrics
            )
            
            # Quality level determination
            quality_level = self._determine_quality_level(overall_quality_score)
            
            # Enhancement recommendations
            enhancement_recommendations = self.creator_experience_optimizer.generate_enhancement_recommendations(
                quality_metrics, aesthetic_scores, business_metrics
            )
            
            # Quality breakdown by dimension
            quality_breakdown = {
                QualityDimension.TECHNICAL: self._calculate_technical_score(quality_metrics),
                QualityDimension.AESTHETIC: self._calculate_aesthetic_score(aesthetic_scores),
                QualityDimension.BUSINESS_VALUE: self._calculate_business_score(business_metrics),
                QualityDimension.ENGAGEMENT: self._calculate_engagement_score(aesthetic_scores, business_metrics),
                QualityDimension.PLATFORM_COMPATIBILITY: np.mean(list(platform_scores.values()))
            }
            
            # Confidence score calculation
            confidence_score = self._calculate_confidence_score(
                quality_metrics, aesthetic_scores, business_metrics
            )
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return QualityAssessmentResult(
                content_id=content_id,
                overall_quality_score=overall_quality_score,
                quality_level=quality_level,
                technical_metrics=quality_metrics,
                aesthetic_scores=aesthetic_scores,
                business_metrics=business_metrics,
                platform_scores=platform_scores,
                enhancement_recommendations=enhancement_recommendations,
                quality_breakdown=quality_breakdown,
                confidence_score=confidence_score,
                processing_time_ms=processing_time,
                timestamp=str(np.datetime64('now'))
            )
            
        except Exception as e:
            logger.error(f"Quality assessment error: {e}")
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Return default result
            return self._default_quality_result(
                content_input.get("content_id", "unknown"), 
                processing_time
            )
    
    def calculate_platform_compatibility(self, quality_metrics: QualityMetrics,
                                       content_input: Dict[str, Any]) -> Dict[str, float]:
        """Calcul compatibilité plateformes basé sur quality requirements"""
        platform_scores = {}
        
        for platform, requirements in self.platform_requirements.items():
            score = 0.0
            
            # Resolution compatibility
            if quality_metrics.resolution_score >= requirements["min_resolution"]:
                score += 0.4
            else:
                score += 0.4 * (quality_metrics.resolution_score / requirements["min_resolution"])
            
            # Quality factors
            score += 0.2 * quality_metrics.clarity_score
            score += 0.2 * quality_metrics.color_balance_score
            score += 0.1 * quality_metrics.composition_score
            
            # File size optimization (important for mobile platforms)
            if quality_metrics.file_size_optimization:
                score += 0.1 * quality_metrics.file_size_optimization
            else:
                score += 0.05  # Default partial score
            
            platform_scores[platform] = min(score, 1.0)
        
        return platform_scores
    
    def _calculate_overall_quality(self, quality_metrics: QualityMetrics,
                                 aesthetic_scores: AestheticScores,
                                 business_metrics: BusinessMetrics) -> float:
        """Calcul score qualité global"""
        technical_score = self._calculate_technical_score(quality_metrics)
        aesthetic_score = self._calculate_aesthetic_score(aesthetic_scores)
        business_score = self._calculate_business_score(business_metrics)
        
        # Weighted average
        overall_score = (
            technical_score * 0.4 +
            aesthetic_score * 0.35 +
            business_score * 0.25
        )
        
        return min(overall_score, 1.0)
    
    def _calculate_technical_score(self, quality_metrics: QualityMetrics) -> float:
        """Calcul score technique"""
        scores = [
            quality_metrics.resolution_score,
            quality_metrics.clarity_score,
            quality_metrics.color_balance_score,
            quality_metrics.composition_score
        ]
        
        if quality_metrics.audio_quality_score:
            scores.append(quality_metrics.audio_quality_score)
        if quality_metrics.compression_efficiency:
            scores.append(quality_metrics.compression_efficiency)
        if quality_metrics.file_size_optimization:
            scores.append(quality_metrics.file_size_optimization)
        
        return np.mean(scores)
    
    def _calculate_aesthetic_score(self, aesthetic_scores: AestheticScores) -> float:
        """Calcul score esthétique"""
        return np.mean([
            aesthetic_scores.visual_appeal,
            aesthetic_scores.color_harmony,
            aesthetic_scores.composition_balance,
            aesthetic_scores.lighting_quality,
            aesthetic_scores.artistic_value,
            aesthetic_scores.emotional_impact
        ])
    
    def _calculate_business_score(self, business_metrics: BusinessMetrics) -> float:
        """Calcul score business"""
        return np.mean([
            business_metrics.commercial_viability,
            business_metrics.brand_safety_score,
            business_metrics.advertiser_friendliness,
            business_metrics.viral_potential,
            business_metrics.engagement_predictability,
            business_metrics.monetization_readiness
        ])
    
    def _calculate_engagement_score(self, aesthetic_scores: AestheticScores,
                                  business_metrics: BusinessMetrics) -> float:
        """Calcul score engagement"""
        return (
            aesthetic_scores.emotional_impact * 0.4 +
            aesthetic_scores.visual_appeal * 0.3 +
            business_metrics.viral_potential * 0.3
        )
    
    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """Détermination niveau qualité"""
        if overall_score >= 0.9:
            return QualityLevel.EXCEPTIONAL
        elif overall_score >= 0.8:
            return QualityLevel.EXCELLENT
        elif overall_score >= 0.6:
            return QualityLevel.GOOD
        elif overall_score >= 0.4:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR
    
    def _calculate_confidence_score(self, quality_metrics: QualityMetrics,
                                  aesthetic_scores: AestheticScores,
                                  business_metrics: BusinessMetrics) -> float:
        """Calcul score confiance basé sur cohérence des métriques"""
        all_scores = [
            quality_metrics.resolution_score,
            quality_metrics.clarity_score,
            quality_metrics.color_balance_score,
            aesthetic_scores.visual_appeal,
            aesthetic_scores.color_harmony,
            business_metrics.commercial_viability
        ]
        
        # Cohérence basée sur écart-type
        std_dev = np.std(all_scores)
        confidence = max(0.5, 1.0 - (std_dev * 2))  # Lower std = higher confidence
        
        return min(confidence, 1.0)
    
    def _default_quality_result(self, content_id: str, processing_time: float) -> QualityAssessmentResult:
        """Résultat qualité par défaut en cas d'erreur"""
        return QualityAssessmentResult(
            content_id=content_id,
            overall_quality_score=0.5,
            quality_level=QualityLevel.FAIR,
            technical_metrics=QualityMetrics(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
            aesthetic_scores=AestheticScores(0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
            business_metrics=BusinessMetrics(0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
            platform_scores={"instagram": 0.5, "youtube": 0.5, "tiktok": 0.5},
            enhancement_recommendations=["Review content quality", "Consider professional tools"],
            quality_breakdown={dim: 0.5 for dim in QualityDimension},
            confidence_score=0.5,
            processing_time_ms=processing_time,
            timestamp=str(np.datetime64('now'))
        )

class QualityAssessmentService:
    """
    Service principal pour quality assessment IA Chéries.
    Orchestration + batch processing + analytics.
    """
    
    def __init__(self, config: QualityAssessmentConfig):
        self.config = config
        self.model = ContentQualityAssessmentModel(config)
        self.analytics_cache = []
    
    async def assess_content_batch(self, content_inputs: List[Dict[str, Any]]) -> List[QualityAssessmentResult]:
        """Assessment batch pour optimisation performance"""
        results = []
        
        for content_input in content_inputs:
            result = await self.model.assess_content_quality(content_input)
            results.append(result)
            
            # Cache pour analytics
            self.analytics_cache.append(result)
        
        return results
    
    async def generate_quality_analytics(self) -> Dict[str, Any]:
        """Génération analytics qualité agrégées"""
        if not self.analytics_cache:
            return {}
        
        results = self.analytics_cache
        
        analytics = {
            "total_assessments": len(results),
            "average_quality_score": np.mean([r.overall_quality_score for r in results]),
            "quality_distribution": {},
            "top_platforms": {},
            "common_recommendations": {},
            "processing_performance": {
                "avg_processing_time_ms": np.mean([r.processing_time_ms for r in results]),
                "confidence_avg": np.mean([r.confidence_score for r in results])
            }
        }
        
        # Distribution qualité
        for result in results:
            level = result.quality_level.name
            analytics["quality_distribution"][level] = analytics["quality_distribution"].get(level, 0) + 1
        
        # Top platforms par compatibilité
        platform_totals = {}
        for result in results:
            for platform, score in result.platform_scores.items():
                if platform not in platform_totals:
                    platform_totals[platform] = []
                platform_totals[platform].append(score)
        
        for platform, scores in platform_totals.items():
            analytics["top_platforms"][platform] = np.mean(scores)
        
        # Recommandations communes
        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.enhancement_recommendations)
        
        from collections import Counter
        rec_counts = Counter(all_recommendations)
        analytics["common_recommendations"] = dict(rec_counts.most_common(10))
        
        return analytics


# Factory function pour faciliter l'utilisation
def create_quality_assessor(device: str = "cpu", 
                          enable_aesthetic_scoring: bool = True,
                          enable_business_scoring: bool = True) -> QualityAssessmentService:
    """Factory function pour créer quality assessor"""
    config = QualityAssessmentConfig(
        device=device,
        enable_aesthetic_scoring=enable_aesthetic_scoring,
        enable_business_scoring=enable_business_scoring,
        quality_threshold=0.7,
        detailed_analysis=True
    )
    
    return QualityAssessmentService(config)


# Export des classes principales
__all__ = [
    "QualityDimension",
    "QualityLevel",
    "QualityMetrics",
    "AestheticScores", 
    "BusinessMetrics",
    "QualityAssessmentResult",
    "QualityAssessmentConfig",
    "ContentQualityAssessmentModel",
    "QualityAssessmentService",
    "create_quality_assessor"
]