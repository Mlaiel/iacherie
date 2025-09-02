"""🚀 Content Quality Assessor - IA Influencer Agent Platform Enterprise
==================================================================
Module: backend/data_management/validation/quality_assessor.py
Author: Fahed Mlaiel (mlaiel@live.de)
==================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME D'ÉVALUATION QUALITÉ CONTENU IA
Évaluation intelligente de la qualité de contenu multi-format
- Analyse qualité technique automatisée
- Scoring multi-critères avec IA
- Recommandations d'amélioration personnalisées
- Standards de qualité par type de créateur
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import os
import numpy as np

# Audio analysis
import librosa
import soundfile as sf
from scipy import signal
from scipy.stats import entropy

# Video analysis
import cv2
from moviepy.editor import VideoFileClip
from skimage import measure, filters, feature

# Image analysis
from PIL import Image, ImageStat, ImageFilter
from skimage import color, exposure, metrics
import imagehash

# Text analysis
from textstat import flesch_reading_ease, flesch_kincaid_grade, automated_readability_index
from textstat import lexicon_count, sentence_count, syllable_count
import language_tool_python
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

# ML models for quality assessment
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """
Dimensions de qualité évaluées"""

    TECHNICAL_QUALITY = "technical_quality"
    AESTHETIC_QUALITY = "aesthetic_quality"
    CONTENT_RELEVANCE = "content_relevance"
    ENGAGEMENT_POTENTIAL = "engagement_potential"
    PROFESSIONAL_STANDARD = "professional_standard"
    PLATFORM_COMPLIANCE = "platform_compliance"
    ACCESSIBILITY = "accessibility"

class QualityLevel(Enum):
    """Niveaux de qualité"""

    POOR = "poor"           # 0.0 - 0.3
    FAIR = "fair"           # 0.3 - 0.5
    GOOD = "good"           # 0.5 - 0.7
    EXCELLENT = "excellent" # 0.7 - 0.9
    OUTSTANDING = "outstanding" # 0.9 - 1.0

@dataclass
class QualityScore:
    """Score de qualité pour une dimension"""
    dimension: QualityDimension
    score: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    details: Dict[str, Any]
    recommendations: List[str]

@dataclass
class QualityAssessmentResult:
    """
Résultat complet d'évaluation qualité"""
    overall_score: float  # 0.0 - 1.0
    overall_level: QualityLevel
    dimension_scores: Dict[QualityDimension, QualityScore]
    technical_metrics: Dict[str, Any]
    improvement_suggestions: List[str]
    compliance_issues: List[str]
    accessibility_score: float
    creator_specific_feedback: Dict[str, Any]
    metadata: Dict[str, Any]

class AudioQualityAnalyzer:
    """
Analyseur de qualité audio avancé"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.AudioQualityAnalyzer")
        
        # Seuils de qualité pour différents types
        self.quality_thresholds = {
            'musician': {
                'min_sample_rate': 44100,
                'min_bitrate': 192,
                'max_thd': 0.01,  # Total Harmonic Distortion
                'min_dynamic_range': 30,  # dB
                'max_noise_floor': -60  # dB
            },
            'podcaster': {
                'min_sample_rate': 22050,
                'min_bitrate': 128,
                'max_thd': 0.05,
                'min_dynamic_range': 20,
                'max_noise_floor': -50
            }
        }
    
    def assess_audio_quality(self, file_path: str, creator_type: str = "musician") -> QualityAssessmentResult:
        """Évalue la qualité audio complète"""
        try:
            # Chargement audio
            y, sr = librosa.load(file_path, sr=None)
            duration = len(y) / sr
            
            # Métriques techniques
            technical_metrics = self._extract_technical_metrics(y, sr)
            
            # Évaluation par dimensions
            dimension_scores = {}
            
            # Qualité technique
            technical_score = self._assess_technical_quality(technical_metrics, creator_type)
            dimension_scores[QualityDimension.TECHNICAL_QUALITY] = technical_score
            
            # Qualité esthétique
            aesthetic_score = self._assess_aesthetic_quality(y, sr, technical_metrics)
            dimension_scores[QualityDimension.AESTHETIC_QUALITY] = aesthetic_score
            
            # Potentiel d'engagement
            engagement_score = self._assess_engagement_potential(y, sr, duration)
            dimension_scores[QualityDimension.ENGAGEMENT_POTENTIAL] = engagement_score
            
            # Standards professionnels
            professional_score = self._assess_professional_standards(technical_metrics, creator_type)
            dimension_scores[QualityDimension.PROFESSIONAL_STANDARD] = professional_score
            
            # Accessibilité
            accessibility_score = self._assess_accessibility(y, sr, technical_metrics)
            dimension_scores[QualityDimension.ACCESSIBILITY] = accessibility_score
            
            # Score global
            overall_score = np.mean([score.score for score in dimension_scores.values()])
            overall_level = self._determine_quality_level(overall_score)
            
            # Suggestions d'amélioration
            improvement_suggestions = self._generate_improvement_suggestions(dimension_scores, technical_metrics)
            
            # Feedback spécifique au créateur
            creator_feedback = self._generate_creator_feedback(creator_type, dimension_scores, technical_metrics)
            
            return QualityAssessmentResult(
                overall_score=overall_score,
                overall_level=overall_level,
                dimension_scores=dimension_scores,
                technical_metrics=technical_metrics,
                improvement_suggestions=improvement_suggestions,
                compliance_issues=[],
                accessibility_score=accessibility_score.score,
                creator_specific_feedback=creator_feedback,
                metadata={
                    "file_path": file_path,
                    "creator_type": creator_type,
                    "duration": duration,
                    "sample_rate": sr,
                    "assessment_timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erreur évaluation qualité audio {file_path}: {e}")
            return self._create_error_result(str(e))
    
    def _extract_technical_metrics(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extrait les métriques techniques audio"""
        metrics = {}
        
        try:
            # Métriques de base
            metrics['duration'] = len(y) / sr
            metrics['sample_rate'] = sr
            metrics['channels'] = 1 if len(y.shape) == 1 else y.shape[0]
            
            # Niveau RMS et peak
            rms = librosa.feature.rms(y=y)[0]
            metrics['rms_mean'] = float(np.mean(rms))
            metrics['rms_std'] = float(np.std(rms))
            metrics['peak_level'] = float(np.max(np.abs(y)))
            
            # Dynamic range
            metrics['dynamic_range_db'] = float(20 * np.log10(metrics['peak_level'] / (metrics['rms_mean'] + 1e-8)))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            metrics['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            metrics['spectral_centroid_std'] = float(np.std(spectral_centroids))
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            metrics['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            metrics['spectral_bandwidth_mean'] = float(np.mean(spectral_bandwidth))
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            metrics['zero_crossing_rate'] = float(np.mean(zcr))
            
            # Tempo et beat
            try:
                tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
                metrics['tempo'] = float(tempo)
                metrics['beat_count'] = len(beats)
                metrics['rhythm_regularity'] = float(np.std(np.diff(beats)))
            except:
                metrics['tempo'] = 0.0
                metrics['beat_count'] = 0
                metrics['rhythm_regularity'] = 0.0
            
            # Noise floor estimation
            noise_segments = self._estimate_noise_floor(y, sr)
            metrics['noise_floor_db'] = float(20 * np.log10(noise_segments + 1e-8))
            
            # Clipping detection
            clipping_ratio = np.sum(np.abs(y) >= 0.99) / len(y)
            metrics['clipping_ratio'] = float(clipping_ratio)
            
            # Frequency response
            freqs, psd = signal.welch(y, sr, nperseg=2048)
            metrics['frequency_response'] = {
                'bass_energy': float(np.sum(psd[(freqs >= 20) & (freqs <= 250)])),
                'mid_energy': float(np.sum(psd[(freqs >= 250) & (freqs <= 4000)])),
                'treble_energy': float(np.sum(psd[(freqs >= 4000) & (freqs <= 20000)]))
            }
            
        except Exception as e:
            self.logger.error(f"Erreur extraction métriques: {e}")
        
        return metrics
    
    def _assess_technical_quality(self, metrics: Dict[str, Any], creator_type: str) -> QualityScore:
        """Évalue la qualité technique"""
        thresholds = self.quality_thresholds.get(creator_type, self.quality_thresholds['musician'])
        
        technical_scores = []
        details = {}
        recommendations = []
        
        # Sample rate
        sr_score = min(1.0, metrics['sample_rate'] / thresholds['min_sample_rate'])
        technical_scores.append(sr_score)
        details['sample_rate_score'] = sr_score
        
        if sr_score < 1.0:
            recommendations.append(f"Améliorer le taux d'échantillonnage (actuel: {metrics['sample_rate']} Hz)")
        
        # Dynamic range
        dr_score = min(1.0, metrics['dynamic_range_db'] / thresholds['min_dynamic_range'])
        technical_scores.append(dr_score)
        details['dynamic_range_score'] = dr_score
        
        if dr_score < 0.8:
            recommendations.append("Améliorer la plage dynamique - éviter la surcompression")
        
        # Noise floor
        noise_score = 1.0 if metrics['noise_floor_db'] <= thresholds['max_noise_floor'] else 0.5
        technical_scores.append(noise_score)
        details['noise_score'] = noise_score
        
        if noise_score < 1.0:
            recommendations.append("Réduire le bruit de fond lors de l'enregistrement")
        
        # Clipping
        clipping_score = 1.0 - min(1.0, metrics['clipping_ratio'] * 10)
        technical_scores.append(clipping_score)
        details['clipping_score'] = clipping_score
        
        if clipping_score < 0.9:
            recommendations.append("Réduire l'écrêtage - diminuer le niveau d'enregistrement")
        
        overall_technical_score = np.mean(technical_scores)
        confidence = len(technical_scores) / 4.0  # Confiance basée sur completude
        
        return QualityScore(
            dimension=QualityDimension.TECHNICAL_QUALITY,
            score=overall_technical_score,
            confidence=confidence,
            details=details,
            recommendations=recommendations
        )
    
    def _assess_aesthetic_quality(self, y: np.ndarray, sr: int, metrics: Dict[str, Any]) -> QualityScore:
        """Évalue la qualité esthétique"""
        aesthetic_scores = []
        details = {}
        recommendations = []
        
        # Balance spectrale
        freq_response = metrics['frequency_response']
        total_energy = freq_response['bass_energy'] + freq_response['mid_energy'] + freq_response['treble_energy']
        
        if total_energy > 0:
            bass_ratio = freq_response['bass_energy'] / total_energy
            mid_ratio = freq_response['mid_energy'] / total_energy
            treble_ratio = freq_response['treble_energy'] / total_energy
            
            # Score basé sur l'équilibre (idéal: 30% bass, 50% mid, 20% treble)
            ideal_ratios = [0.3, 0.5, 0.2]
            actual_ratios = [bass_ratio, mid_ratio, treble_ratio]
            
            balance_score = 1.0 - np.mean([abs(ideal - actual) for ideal, actual in zip(ideal_ratios, actual_ratios)])
            aesthetic_scores.append(max(0.0, balance_score))
            
            details['spectral_balance'] = {
                'bass_ratio': bass_ratio,
                'mid_ratio': mid_ratio,
                'treble_ratio': treble_ratio,
                'balance_score': balance_score
            }
            
            if balance_score < 0.7:
                recommendations.append("Améliorer l'équilibre spectral avec un égaliseur")
        
        # Régularité du tempo
        if metrics['tempo'] > 0:
            rhythm_score = max(0.0, 1.0 - (metrics['rhythm_regularity'] / 1000.0))
            aesthetic_scores.append(rhythm_score)
            details['rhythm_score'] = rhythm_score
            
            if rhythm_score < 0.6:
                recommendations.append("Améliorer la régularité du rythme")
        
        # Variation dynamique
        dynamic_variation = metrics['rms_std'] / (metrics['rms_mean'] + 1e-8)
        dynamic_score = min(1.0, dynamic_variation * 2.0)  # Score optimal à 0.5 de variation
        aesthetic_scores.append(dynamic_score)
        details['dynamic_variation_score'] = dynamic_score
        
        if dynamic_score < 0.5:
            recommendations.append("Ajouter plus de variation dynamique")
        
        overall_aesthetic_score = np.mean(aesthetic_scores) if aesthetic_scores else 0.5
        confidence = len(aesthetic_scores) / 3.0
        
        return QualityScore(
            dimension=QualityDimension.AESTHETIC_QUALITY,
            score=overall_aesthetic_score,
            confidence=confidence,
            details=details,
            recommendations=recommendations
        )
    
    def _assess_engagement_potential(self, y: np.ndarray, sr: int, duration: float) -> QualityScore:
        """Évalue le potentiel d'engagement"""
        engagement_scores = []
        details = {}
        recommendations = []
        
        # Durée optimale (dépend du contexte)
        optimal_duration = 180  # 3 minutes pour musique
        duration_score = 1.0 - abs(duration - optimal_duration) / optimal_duration
        duration_score = max(0.0, min(1.0, duration_score))
        engagement_scores.append(duration_score)
        details['duration_score'] = duration_score
        
        if duration < 60:
            recommendations.append("Considérer augmenter la durée pour plus d'engagement")
        elif duration > 300:
            recommendations.append("Considérer raccourcir pour maintenir l'attention")
        
        # Variation d'intensité (éviter la monotonie)
        intensity_variation = np.std(librosa.feature.rms(y=y)[0])
        variation_score = min(1.0, intensity_variation * 10)
        engagement_scores.append(variation_score)
        details['intensity_variation_score'] = variation_score
        
        if variation_score < 0.5:
            recommendations.append("Ajouter plus de variation d'intensité")
        
        # Complexité spectrale
        spectral_complexity = metrics.get('spectral_bandwidth_mean', 0) / (sr / 2)
        complexity_score = min(1.0, spectral_complexity * 2)
        engagement_scores.append(complexity_score)
        details['spectral_complexity_score'] = complexity_score
        
        overall_engagement_score = np.mean(engagement_scores)
        confidence = 0.8  # Confiance modérée car subjectif
        
        return QualityScore(
            dimension=QualityDimension.ENGAGEMENT_POTENTIAL,
            score=overall_engagement_score,
            confidence=confidence,
            details=details,
            recommendations=recommendations
        )
    
    def _assess_professional_standards(self, metrics: Dict[str, Any], creator_type: str) -> QualityScore:
        """Évalue le respect des standards professionnels"""
        standards_scores = []
        details = {}
        recommendations = []
        
        thresholds = self.quality_thresholds.get(creator_type, self.quality_thresholds['musician'])
        
        # Niveau RMS approprié
        target_rms = 0.3  # -10 dB RMS environ
        rms_score = 1.0 - abs(metrics['rms_mean'] - target_rms) / target_rms
        rms_score = max(0.0, min(1.0, rms_score))
        standards_scores.append(rms_score)
        details['rms_level_score'] = rms_score
        
        if rms_score < 0.8:
            recommendations.append("Ajuster le niveau RMS pour les standards professionnels")
        
        # Peak level approprié
        peak_score = 1.0 if metrics['peak_level'] < 0.95 else 0.5
        standards_scores.append(peak_score)
        details['peak_level_score'] = peak_score
        
        if peak_score < 1.0:
            recommendations.append("Éviter l'écrêtage - garder des peaks sous -0.5 dB")
        
        # Fréquences équilibrées
        freq_response = metrics['frequency_response']
        total_energy = sum(freq_response.values())
        
        if total_energy > 0:
            mid_dominance = freq_response['mid_energy'] / total_energy
            frequency_score = min(1.0, mid_dominance * 2)  # Privilégier les médiums
            standards_scores.append(frequency_score)
            details['frequency_balance_score'] = frequency_score
        
        overall_standards_score = np.mean(standards_scores)
        confidence = 0.9  # Confiance élevée car objectif
        
        return QualityScore(
            dimension=QualityDimension.PROFESSIONAL_STANDARD,
            score=overall_standards_score,
            confidence=confidence,
            details=details,
            recommendations=recommendations
        )
    
    def _assess_accessibility(self, y: np.ndarray, sr: int, metrics: Dict[str, Any]) -> QualityScore:
        """Évalue l'accessibilité du contenu"""
        accessibility_scores = []
        details = {}
        recommendations = []
        
        # Clarté audio (faible bruit de fond)
        clarity_score = 1.0 if metrics['noise_floor_db'] <= -50 else 0.6
        accessibility_scores.append(clarity_score)
        details['clarity_score'] = clarity_score
        
        if clarity_score < 1.0:
            recommendations.append("Améliorer la clarté pour l'accessibilité")
        
        # Pas de distorsion
        distortion_score = 1.0 if metrics['clipping_ratio'] < 0.001 else 0.7
        accessibility_scores.append(distortion_score)
        details['distortion_score'] = distortion_score
        
        # Consistance volume
        volume_consistency = 1.0 - (metrics['rms_std'] / metrics['rms_mean'])
        consistency_score = max(0.0, min(1.0, volume_consistency))
        accessibility_scores.append(consistency_score)
        details['volume_consistency_score'] = consistency_score
        
        if consistency_score < 0.7:
            recommendations.append("Normaliser les volumes pour l'accessibilité")
        
        overall_accessibility_score = np.mean(accessibility_scores)
        confidence = 0.8
        
        return QualityScore(
            dimension=QualityDimension.ACCESSIBILITY,
            score=overall_accessibility_score,
            confidence=confidence,
            details=details,
            recommendations=recommendations
        )
    
    def _estimate_noise_floor(self, y: np.ndarray, sr: int) -> float:
        """Estime le niveau de bruit de fond"""
        # Segmentation en petits blocs
        block_size = sr // 10  # 100ms blocks
        blocks = [y[i:i+block_size] for i in range(0, len(y) - block_size, block_size)]
        
        # RMS de chaque bloc
        rms_values = [np.sqrt(np.mean(block**2)) for block in blocks if len(block) == block_size]
        
        # Le bruit de fond est approximé par le 10e percentile
        if rms_values:
            return np.percentile(rms_values, 10)
        return 0.0
    
    def _generate_improvement_suggestions(self, dimension_scores: Dict, metrics: Dict) -> List[str]:
        """
Génère des suggestions d'amélioration globales"""
        suggestions = []
        
        # Collecte toutes les recommandations
        for dimension_score in dimension_scores.values():
            suggestions.extend(dimension_score.recommendations)
        
        # Suggestions globales basées sur l'analyse
        if metrics.get('dynamic_range_db', 0) < 20:
            suggestions.append("Considérer utiliser moins de compression dynamique")
        
        if metrics.get('clipping_ratio', 0) > 0.01:
            suggestions.append("Remaster avec plus de headroom pour éviter l'écrêtage")
        
        return list(set(suggestions))  # Dédoublonnage
    
    def _generate_creator_feedback(self, creator_type: str, dimension_scores: Dict, metrics: Dict) -> Dict[str, Any]:
        """Génère un feedback spécifique au type de créateur"""
        feedback = {
            "creator_type": creator_type,
            "priority_improvements": [],
            "strengths": [],
            "next_steps": []
        }
        
        # Analyse des forces et faiblesses
        sorted_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1].score)
        
        # Points faibles (scores < 0.6)
        weak_dimensions = [dim for dim, score in sorted_dimensions if score.score < 0.6]
        if weak_dimensions:
            feedback["priority_improvements"] = [dim.value for dim, _ in weak_dimensions]
        
        # Points forts (scores > 0.8)
        strong_dimensions = [dim for dim, score in sorted_dimensions if score.score > 0.8]
        if strong_dimensions:
            feedback["strengths"] = [dim.value for dim, _ in strong_dimensions]
        
        # Conseils spécifiques par type de créateur
        if creator_type == "musician":
            if metrics.get('tempo', 0) == 0:
                feedback["next_steps"].append("Définir un tempo plus clair")
            if metrics.get('dynamic_range_db', 0) > 40:
                feedback["next_steps"].append("Excellente dynamique - maintenir ce niveau")
        
        return feedback
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Détermine le niveau de qualité global"""
        if score >= 0.9:
            return QualityLevel.OUTSTANDING
        elif score >= 0.7:
            return QualityLevel.EXCELLENT
        elif score >= 0.5:
            return QualityLevel.GOOD
        elif score >= 0.3:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR
    
    def _create_error_result(self, error_msg: str) -> QualityAssessmentResult:
        """
Crée un résultat d'erreur"""
        return QualityAssessmentResult(
            overall_score=0.0,
            overall_level=QualityLevel.POOR,
            dimension_scores={},
            technical_metrics={},
            improvement_suggestions=[],
            compliance_issues=[f"Erreur d'analyse: {error_msg}"],
            accessibility_score=0.0,
            creator_specific_feedback={},
            metadata={"error": error_msg}
        )

class VideoQualityAnalyzer:
    """Analyseur de qualité vidéo avancé"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.VideoQualityAnalyzer")
        
        # Standards de qualité par type de créateur
        self.quality_standards = {
            'influencer': {
                'min_resolution': (720, 1280),  # 720p
                'min_fps': 24,
                'max_fps': 60,
                'optimal_duration': (15, 300),  # 15s - 5min
                'min_bitrate': 2000  # kbps
            },
            'filmmaker': {
                'min_resolution': (1080, 1920),  # 1080p
                'min_fps': 24,
                'max_fps': 120,
                'optimal_duration': (60, 7200),  # 1min - 2h
                'min_bitrate': 5000
            }
        }
    
    def assess_video_quality(self, file_path: str, creator_type: str = "influencer") -> QualityAssessmentResult:
        """Évalue la qualité vidéo complète"""
        try:
            # Ouverture vidéo
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                return self._create_error_result("Impossible d'ouvrir le fichier vidéo")
            
            # Métriques de base
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Extraction métriques techniques
            technical_metrics = self._extract_video_metrics(cap, fps, frame_count, width, height, duration)
            
            cap.release()
            
            # Évaluation par dimensions
            dimension_scores = {}
            
            # Qualité technique
            technical_score = self._assess_video_technical_quality(technical_metrics, creator_type)
            dimension_scores[QualityDimension.TECHNICAL_QUALITY] = technical_score
            
            # Qualité esthétique
            aesthetic_score = self._assess_video_aesthetic_quality(technical_metrics)
            dimension_scores[QualityDimension.AESTHETIC_QUALITY] = aesthetic_score
            
            # Potentiel d'engagement
            engagement_score = self._assess_video_engagement_potential(technical_metrics, creator_type)
            dimension_scores[QualityDimension.ENGAGEMENT_POTENTIAL] = engagement_score
            
            # Standards professionnels
            professional_score = self._assess_video_professional_standards(technical_metrics, creator_type)
            dimension_scores[QualityDimension.PROFESSIONAL_STANDARD] = professional_score
            
            # Score global
            overall_score = np.mean([score.score for score in dimension_scores.values()])
            overall_level = self._determine_quality_level(overall_score)
            
            # Suggestions d'amélioration
            improvement_suggestions = self._generate_video_improvements(dimension_scores, technical_metrics)
            
            return QualityAssessmentResult(
                overall_score=overall_score,
                overall_level=overall_level,
                dimension_scores=dimension_scores,
                technical_metrics=technical_metrics,
                improvement_suggestions=improvement_suggestions,
                compliance_issues=[],
                accessibility_score=self._calculate_accessibility_score(technical_metrics),
                creator_specific_feedback={},
                metadata={
                    "file_path": file_path,
                    "creator_type": creator_type,
                    "resolution": f"{width}x{height}",
                    "fps": fps,
                    "duration": duration
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erreur évaluation qualité vidéo {file_path}: {e}")
            return self._create_error_result(str(e))
    
    def _extract_video_metrics(self, cap: cv2.VideoCapture, fps: float, frame_count: int, 
                              width: int, height: int, duration: float) -> Dict[str, Any]:
        """Extrait les métriques techniques vidéo"""
        metrics = {
            'fps': fps,
            'frame_count': frame_count,
            'width': width,
            'height': height,
            'duration': duration,
            'resolution': width * height
        }
        
        # Échantillonnage de frames pour analyse
        sample_frames = min(30, frame_count)
        frame_step = max(1, frame_count // sample_frames)
        
        brightness_values = []
        contrast_values = []
        sharpness_values = []
        motion_values = []
        
        prev_frame = None
        
        for i in range(0, frame_count, frame_step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Luminosité
            brightness = np.mean(gray)
            brightness_values.append(brightness)
            
            # Contraste (écart-type)
            contrast = np.std(gray)
            contrast_values.append(contrast)
            
            # Netteté (variance du Laplacien)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_values.append(sharpness)
            
            # Mouvement (différence avec frame précédente)
            if prev_frame is not None:
                motion = np.mean(np.abs(gray.astype(float) - prev_frame.astype(float)))
                motion_values.append(motion)
            
            prev_frame = gray
        
        # Agrégation des métriques
        if brightness_values:
            metrics['avg_brightness'] = np.mean(brightness_values)
            metrics['brightness_std'] = np.std(brightness_values)
        
        if contrast_values:
            metrics['avg_contrast'] = np.mean(contrast_values)
            metrics['contrast_consistency'] = 1.0 - (np.std(contrast_values) / np.mean(contrast_values))
        
        if sharpness_values:
            metrics['avg_sharpness'] = np.mean(sharpness_values)
            metrics['sharpness_consistency'] = 1.0 - (np.std(sharpness_values) / np.mean(sharpness_values))
        
        if motion_values:
            metrics['avg_motion'] = np.mean(motion_values)
            metrics['motion_consistency'] = 1.0 - (np.std(motion_values) / (np.mean(motion_values) + 1e-8))
        
        metrics['analyzed_frames'] = len(brightness_values)
        
        return metrics
    
    def _assess_video_technical_quality(self, metrics: Dict[str, Any], creator_type: str) -> QualityScore:
        """Évalue la qualité technique vidéo"""
        standards = self.quality_standards.get(creator_type, self.quality_standards['influencer'])
        
        technical_scores = []
        details = {}
        recommendations = []
        
        # Résolution
        min_pixels = standards['min_resolution'][0] * standards['min_resolution'][1]
        resolution_score = min(1.0, metrics['resolution'] / min_pixels)
        technical_scores.append(resolution_score)
        details['resolution_score'] = resolution_score
        
        if resolution_score < 1.0:
            recommendations.append(f"Augmenter la résolution (minimum {standards['min_resolution']})")
        
        # FPS
        fps_score = 1.0 if standards['min_fps'] <= metrics['fps'] <= standards['max_fps'] else 0.7
        technical_scores.append(fps_score)
        details['fps_score'] = fps_score
        
        if fps_score < 1.0:
            recommendations.append(f"Ajuster le FPS ({standards['min_fps']}-{standards['max_fps']})")
        
        # Netteté
        if 'avg_sharpness' in metrics:
            sharpness_score = min(1.0, metrics['avg_sharpness'] / 500.0)  # Normalisation empirique
            technical_scores.append(sharpness_score)
            details['sharpness_score'] = sharpness_score
            
            if sharpness_score < 0.6:
                recommendations.append("Améliorer la netteté - vérifier la mise au point")
        
        # Stabilité (consistance de netteté)
        if 'sharpness_consistency' in metrics:
            stability_score = metrics['sharpness_consistency']
            technical_scores.append(stability_score)
            details['stability_score'] = stability_score
            
            if stability_score < 0.7:
                recommendations.append("Améliorer la stabilité - utiliser un trépied")
        
        overall_technical_score = np.mean(technical_scores)
        confidence = len(technical_scores) / 4.0
        
        return QualityScore(
            dimension=QualityDimension.TECHNICAL_QUALITY,
            score=overall_technical_score,
            confidence=confidence,
            details=details,
            recommendations=recommendations
        )
    
    def _assess_video_aesthetic_quality(self, metrics: Dict[str, Any]) -> QualityScore:
        """Évalue la qualité esthétique vidéo"""
        aesthetic_scores = []
        details = {}
        recommendations = []
        
        # Exposition (luminosité appropriée)
        if 'avg_brightness' in metrics:
            optimal_brightness = 128  # Milieu de la plage 0-255
            brightness_score = 1.0 - abs(metrics['avg_brightness'] - optimal_brightness) / optimal_brightness
            brightness_score = max(0.0, brightness_score)
            aesthetic_scores.append(brightness_score)
            details['brightness_score'] = brightness_score
            
            if brightness_score < 0.7:
                if metrics['avg_brightness'] < 100:
                    recommendations.append("Améliorer l'éclairage - vidéo trop sombre")
                else:
                    recommendations.append("Réduire l'exposition - vidéo trop claire")
        
        # Contraste approprié
        if 'avg_contrast' in metrics:
            contrast_score = min(1.0, metrics['avg_contrast'] / 50.0)  # Normalisation empirique
            aesthetic_scores.append(contrast_score)
            details['contrast_score'] = contrast_score
            
            if contrast_score < 0.6:
                recommendations.append("Améliorer le contraste")
        
        # Cohérence visuelle
        if 'contrast_consistency' in metrics:
            consistency_score = metrics['contrast_consistency']
            aesthetic_scores.append(consistency_score)
            details['visual_consistency_score'] = consistency_score
            
            if consistency_score < 0.7:
                recommendations.append("Améliorer la cohérence d'éclairage entre les plans")
        
        overall_aesthetic_score = np.mean(aesthetic_scores) if aesthetic_scores else 0.5
        confidence = len(aesthetic_scores) / 3.0
        
        return QualityScore(
            dimension=QualityDimension.AESTHETIC_QUALITY,
            score=overall_aesthetic_score,
            confidence=confidence,
            details=details,
            recommendations=recommendations
        )
    
    def _assess_video_engagement_potential(self, metrics: Dict[str, Any], creator_type: str) -> QualityScore:
        """Évalue le potentiel d'engagement vidéo"""
        standards = self.quality_standards.get(creator_type, self.quality_standards['influencer'])
        
        engagement_scores = []
        details = {}
        recommendations = []
        
        # Durée optimale
        min_duration, max_duration = standards['optimal_duration']
        duration = metrics['duration']
        
        if min_duration <= duration <= max_duration:
            duration_score = 1.0
        else:
            duration_score = 0.6  # Acceptable mais pas optimal
        
        engagement_scores.append(duration_score)
        details['duration_score'] = duration_score
        
        if duration < min_duration:
            recommendations.append("Considérer augmenter la durée pour plus de contenu")
        elif duration > max_duration:
            recommendations.append("Considérer raccourcir pour maintenir l'attention")
        
        # Dynamisme (variation de mouvement)
        if 'motion_consistency' in metrics:
            # Un peu de variation est bon pour l'engagement
            motion_variation = 1.0 - metrics['motion_consistency']
            motion_score = min(1.0, motion_variation * 2.0)
            engagement_scores.append(motion_score)
            details['motion_dynamism_score'] = motion_score
            
            if motion_score < 0.5:
                recommendations.append("Ajouter plus de mouvement dynamique")
        
        overall_engagement_score = np.mean(engagement_scores)
        confidence = 0.7  # Modérée car subjectif
        
        return QualityScore(
            dimension=QualityDimension.ENGAGEMENT_POTENTIAL,
            score=overall_engagement_score,
            confidence=confidence,
            details=details,
            recommendations=recommendations
        )
    
    def _assess_video_professional_standards(self, metrics: Dict[str, Any], creator_type: str) -> QualityScore:
        """Évalue le respect des standards professionnels vidéo"""
        standards = self.quality_standards.get(creator_type, self.quality_standards['influencer'])
        
        professional_scores = []
        details = {}
        recommendations = []
        
        # Résolution minimum
        resolution_meets_standard = metrics['resolution'] >= (standards['min_resolution'][0] * standards['min_resolution'][1])
        resolution_score = 1.0 if resolution_meets_standard else 0.5
        professional_scores.append(resolution_score)
        details['resolution_standard_score'] = resolution_score
        
        # FPS standard
        fps_standard = standards['min_fps'] <= metrics['fps'] <= standards['max_fps']
        fps_score = 1.0 if fps_standard else 0.6
        professional_scores.append(fps_score)
        details['fps_standard_score'] = fps_score
        
        # Stabilité technique
        if 'sharpness_consistency' in metrics and 'contrast_consistency' in metrics:
            technical_stability = (metrics['sharpness_consistency'] + metrics['contrast_consistency']) / 2
            professional_scores.append(technical_stability)
            details['technical_stability_score'] = technical_stability
            
            if technical_stability < 0.8:
                recommendations.append("Améliorer la stabilité technique globale")
        
        overall_professional_score = np.mean(professional_scores)
        confidence = 0.9  # Confiance élevée car objectif
        
        return QualityScore(
            dimension=QualityDimension.PROFESSIONAL_STANDARD,
            score=overall_professional_score,
            confidence=confidence,
            details=details,
            recommendations=recommendations
        )
    
    def _generate_video_improvements(self, dimension_scores: Dict, metrics: Dict) -> List[str]:
        """Génère des suggestions d'amélioration vidéo"""
        suggestions = []
        
        # Collecte des recommandations par dimension
        for dimension_score in dimension_scores.values():
            suggestions.extend(dimension_score.recommendations)
        
        # Suggestions globales
        if metrics.get('avg_sharpness', 0) < 300:
            suggestions.append("Améliorer la mise au point générale")
        
        if metrics.get('brightness_std', 0) > 50:
            suggestions.append("Stabiliser l'exposition entre les plans")
        
        return list(set(suggestions))
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Détermine le niveau de qualité global"""
        if score >= 0.9:
            return QualityLevel.OUTSTANDING
        elif score >= 0.7:
            return QualityLevel.EXCELLENT
        elif score >= 0.5:
            return QualityLevel.GOOD
        elif score >= 0.3:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR
    
    def _create_error_result(self, error_msg: str) -> QualityAssessmentResult:
        """
Crée un résultat d'erreur"""
        return QualityAssessmentResult(
            overall_score=0.0,
            overall_level=QualityLevel.POOR,
            dimension_scores={},
            technical_metrics={},
            improvement_suggestions=[],
            compliance_issues=[f"Erreur d'analyse: {error_msg}"],
            accessibility_score=0.0,
            creator_specific_feedback={},
            metadata={"error": error_msg}
        )

class QualityAssessor:
    """Évaluateur de qualité principal multi-format"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.QualityAssessor")
        
        # Analyseurs spécialisés
        self.audio_analyzer = AudioQualityAnalyzer()
        self.video_analyzer = VideoQualityAnalyzer()
        self.image_analyzer = ImageQualityAnalyzer()
        self.text_analyzer = TextQualityAnalyzer()
        
        # Cache des résultats
        self._assessment_cache: Dict[str, QualityAssessmentResult] = {}
    
    def assess_content_quality(self, file_path: str, content_type: str, creator_type: str = "musician") -> QualityAssessmentResult:
        """Évalue la qualité de contenu selon le type"""
        
        # Vérification du cache
        cache_key = f"{file_path}:{content_type}:{creator_type}"
        if cache_key in self._assessment_cache:
            return self._assessment_cache[cache_key]
        
        try:
            if content_type == 'audio':
                result = self.audio_analyzer.assess_audio_quality(file_path, creator_type)
            elif content_type == 'video':
                result = self.video_analyzer.assess_video_quality(file_path, creator_type)
            elif content_type == 'image':
                result = self.image_analyzer.assess_image_quality(file_path, creator_type)
            elif content_type == 'text':
                result = self.text_analyzer.assess_text_quality(file_path, creator_type)
            else:
                result = self._create_error_result(f"Type de contenu non supporté: {content_type}")
            
            # Mise en cache
            self._assessment_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur évaluation qualité {file_path}: {e}")
            return self._create_error_result(str(e))
    
    def _create_placeholder_result(self, message: str) -> QualityAssessmentResult:
        """Crée un résultat placeholder"""
        return QualityAssessmentResult(
            overall_score=0.5,
            overall_level=QualityLevel.FAIR,
            dimension_scores={},
            technical_metrics={},
            improvement_suggestions=[message],
            compliance_issues=[],
            accessibility_score=0.5,
            creator_specific_feedback={},
            metadata={"status": "placeholder"}
        )
    
    def _create_error_result(self, error_msg: str) -> QualityAssessmentResult:
        """Crée un résultat d'erreur"""
        return QualityAssessmentResult(
            overall_score=0.0,
            overall_level=QualityLevel.POOR,
            dimension_scores={},
            technical_metrics={},
            improvement_suggestions=[],
            compliance_issues=[f"Erreur: {error_msg}"],
            accessibility_score=0.0,
            creator_specific_feedback={},
            metadata={"error": error_msg}
        )
    
    def _calculate_accessibility_score(self, technical_metrics: Dict[str, Any]) -> float:
        """Calculate accessibility score based on technical metrics"""
        try:
            score = 0.8  # Base score
            
            # Adjust based on resolution for video content
            if 'resolution' in technical_metrics:
                resolution = technical_metrics['resolution']
                if isinstance(resolution, str) and 'x' in resolution:
                    width, height = map(int, resolution.split('x'))
                    if width >= 1920:  # HD or higher
                        score += 0.1
                    elif width >= 1280:  # HD ready
                        score += 0.05
            
            # Adjust based on audio quality
            if 'audio_bitrate' in technical_metrics:
                bitrate = technical_metrics.get('audio_bitrate', 0)
                if bitrate >= 320:  # High quality
                    score += 0.1
                elif bitrate >= 128:  # Good quality
                    score += 0.05
            
            return min(1.0, score)
        except Exception as e:
            logger.warning(f"Error calculating accessibility score: {e}")
            return 0.8


class ImageQualityAnalyzer:
    """Analyzer for image quality assessment"""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def assess_image_quality(self, file_path: str, creator_type: str = "photographer") -> QualityAssessmentResult:
        """Assess image quality"""
        try:
            # Basic image quality assessment
            img_path = Path(file_path)
            if not img_path.exists():
                return self._create_error_result(f"Image file not found: {file_path}")
            
            # Load image
            with Image.open(img_path) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode
            
            # Calculate basic metrics
            megapixels = (width * height) / 1_000_000
            aspect_ratio = width / height if height > 0 else 1.0
            
            # Scoring logic
            resolution_score = min(1.0, megapixels / 10)  # Normalize to 10MP max
            format_score = 1.0 if format_name in ['JPEG', 'PNG', 'TIFF'] else 0.7
            
            overall_score = (resolution_score + format_score) / 2
            
            return QualityAssessmentResult(
                overall_score=overall_score,
                overall_level=self._score_to_level(overall_score),
                dimension_scores={
                    'resolution': resolution_score,
                    'format': format_score
                },
                technical_metrics={
                    'width': width,
                    'height': height,
                    'megapixels': megapixels,
                    'format': format_name,
                    'mode': mode,
                    'aspect_ratio': aspect_ratio
                },
                improvement_suggestions=self._get_image_suggestions(overall_score, megapixels, format_name),
                compliance_issues=[],
                accessibility_score=0.9,
                creator_specific_feedback={},
                metadata={'file_path': file_path, 'creator_type': creator_type}
            )
            
        except Exception as e:
            self.logger.error(f"Image quality assessment failed: {e}")
            return self._create_error_result(f"Image analysis error: {str(e)}")
    
    def _score_to_level(self, score: float) -> QualityLevel:
        """Convert score to quality level"""
        if score >= 0.8:
            return QualityLevel.EXCELLENT
        elif score >= 0.6:
            return QualityLevel.GOOD
        elif score >= 0.4:
            return QualityLevel.AVERAGE
        else:
            return QualityLevel.POOR
    
    def _get_image_suggestions(self, score: float, megapixels: float, format_name: str) -> List[str]:
        """
Get improvement suggestions for images"""
        suggestions = []
        
        if megapixels < 2:
            suggestions.append("Consider using higher resolution images (2MP minimum)")
        
        if format_name not in ['JPEG', 'PNG']:
            suggestions.append("Use standard image formats (JPEG, PNG) for better compatibility")
        
        if score < 0.7:
            suggestions.append("Overall image quality could be improved")
        
        return suggestions
    
    def _create_error_result(self, error_msg: str) -> QualityAssessmentResult:
        """Create error result for images"""
        return QualityAssessmentResult(
            overall_score=0.0,
            overall_level=QualityLevel.POOR,
            dimension_scores={},
            technical_metrics={},
            improvement_suggestions=[],
            compliance_issues=[f"Error: {error_msg}"],
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            compliance_issues=[f"Error: {error_msg}"],
            accessibility_score=0.0,
            creator_specific_feedback={},
            metadata={"error": error_msg}
        )


class TextQualityAnalyzer:
    """Analyzer for text quality assessment"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.TextQualityAnalyzer")
    
    def assess_text_quality(self, file_path: str, creator_type: str = "writer") -> QualityAssessmentResult:
        """Assess text quality"""
        try:
            # Read text content
            text_path = Path(file_path)
            if not text_path.exists():
                return self._create_error_result(f"Text file not found: {file_path}")
            
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic text metrics
            word_count = len(content.split())
            char_count = len(content)
            sentence_count = content.count('.') + content.count('!') + content.count('?')
            paragraph_count = content.count('\n\n') + 1
            
            # Calculate readability (basic version)
            avg_words_per_sentence = word_count / max(1, sentence_count)
            avg_chars_per_word = char_count / max(1, word_count)
            
            # Scoring logic
            length_score = min(1.0, word_count / 500)  # Normalize to 500 words
            readability_score = max(0.3, 1.0 - (avg_words_per_sentence - 15) / 50)  # Penalize very long sentences
            structure_score = min(1.0, paragraph_count / max(1, word_count / 100))  # Good paragraph structure
            
            overall_score = (length_score + readability_score + structure_score) / 3
            
            return QualityAssessmentResult(
                overall_score=overall_score,
                overall_level=self._score_to_level(overall_score),
                dimension_scores={
                    'length': length_score,
                    'readability': readability_score,
                    'structure': structure_score
                },
                technical_metrics={
                    'word_count': word_count,
                    'char_count': char_count,
                    'sentence_count': sentence_count,
                    'paragraph_count': paragraph_count,
                    'avg_words_per_sentence': avg_words_per_sentence,
                    'avg_chars_per_word': avg_chars_per_word
                },
                improvement_suggestions=self._get_text_suggestions(overall_score, word_count, avg_words_per_sentence),
                compliance_issues=[],
                accessibility_score=0.8,
                creator_specific_feedback={},
                metadata={'file_path': file_path, 'creator_type': creator_type}
            )
            
        except Exception as e:
            self.logger.error(f"Text quality assessment failed: {e}")
            return self._create_error_result(f"Text analysis error: {str(e)}")
    
    def _score_to_level(self, score: float) -> QualityLevel:
        """Convert score to quality level"""
        if score >= 0.8:
            return QualityLevel.EXCELLENT
        elif score >= 0.6:
            return QualityLevel.GOOD
        elif score >= 0.4:
            return QualityLevel.AVERAGE
        else:
            return QualityLevel.POOR
    
    def _get_text_suggestions(self, score: float, word_count: int, avg_words_per_sentence: float) -> List[str]:
        """
Get improvement suggestions for text"""
        suggestions = []
        
        if word_count < 100:
            suggestions.append("Consider adding more content (minimum 100 words recommended)")
        
        if avg_words_per_sentence > 25:
            suggestions.append("Try shorter sentences for better readability")
        
        if score < 0.6:
            suggestions.append("Overall text quality could be improved")
        
        return suggestions
    
    def _create_error_result(self, error_msg: str) -> QualityAssessmentResult:
        """Create error result for text"""
        return QualityAssessmentResult(
            overall_score=0.0,
            overall_level=QualityLevel.POOR,
            dimension_scores={},
            technical_metrics={},
            improvement_suggestions=[],
            compliance_issues=[f"Error: {error_msg}"],
            accessibility_score=0.0,
            creator_specific_feedback={},
            metadata={"error": error_msg}
        )

    """Version asynchrone de l'évaluateur de qualité"""
    
    def __init__(self):
        self.sync_assessor = QualityAssessor()
        self.logger = logging.getLogger(f"{__name__}.AsyncQualityAssessor")
    
    async def assess_content_quality(self, file_path: str, content_type: str, creator_type: str = "musician") -> QualityAssessmentResult:
        """Évalue la qualité de manière asynchrone"""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            self.sync_assessor.assess_content_quality,
            file_path,
            content_type,
            creator_type
        )
        
        return result
    
    async def assess_batch_quality(self, files: List[Tuple[str, str, str]]) -> Dict[str, QualityAssessmentResult]:
        """Évalue la qualité d'un lot de fichiers"""
        tasks = []
        
        for file_path, content_type, creator_type in files:
            task = self.assess_content_quality(file_path, content_type, creator_type)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Formatage des résultats
        assessment_results = {}
        for i, result in enumerate(results):
            file_path = files[i][0]
            
            if isinstance(result, Exception):
                assessment_results[file_path] = QualityAssessmentResult(
                    overall_score=0.0,
                    overall_level=QualityLevel.POOR,
                    dimension_scores={},
                    technical_metrics={},
                    improvement_suggestions=[],
                    compliance_issues=[f"Erreur: {str(result)}"],
                    accessibility_score=0.0,
                    creator_specific_feedback={},
                    metadata={}
                )
            else:
                assessment_results[file_path] = result
        
        return assessment_results

# Export des classes principales
__all__ = [
    'QualityAssessor',
    'AsyncQualityAssessor',
    'QualityAssessmentResult',
    'QualityScore',
    'QualityDimension',
    'QualityLevel',
    'AudioQualityAnalyzer',
    'VideoQualityAnalyzer'
]
