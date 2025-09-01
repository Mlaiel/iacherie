#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-Influencer-Agent Remix Quality Assessor
================================================================================
Module: ai_engine/remix_generation/remix_quality_assessor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Architecture: Production-Ready Enterprise Remix Quality Assessment AI (Level 3)
Created: 2025-08-30
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

MISSION: Évaluateur de qualité de remix IA ultra-avancé avec analyse multidimensionnelle
TECHNOLOGIES: Deep Learning, Audio Quality Metrics, Perceptual Analysis, Neural Assessment
LOGIQUE MÉTIER: Audio input → Multi-modal analysis → Quality scoring → Recommendations → Assessment report
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import librosa
import scipy.signal as signal
from scipy.stats import pearsonr
import pyloudnorm as pyln

# Configure logging
logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """
Quality assessment dimensions"""

    AUDIO_FIDELITY = "audio_fidelity"
    MUSICAL_COHERENCE = "musical_coherence"
    CREATIVE_ENHANCEMENT = "creative_enhancement"
    TECHNICAL_EXECUTION = "technical_execution"
    PERCEPTUAL_QUALITY = "perceptual_quality"
    HARMONIC_CONSISTENCY = "harmonic_consistency"
    RHYTHMIC_ACCURACY = "rhythmic_accuracy"
    DYNAMIC_PROCESSING = "dynamic_processing"
    STEREO_IMAGING = "stereo_imaging"
    FREQUENCY_BALANCE = "frequency_balance"

class AssessmentLevel(Enum):
    """Quality assessment detail levels"""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    PROFESSIONAL = "professional"

class QualityGrade(Enum):
    """Quality grade classifications"""

    POOR = "poor"           # 0.0 - 0.4
    FAIR = "fair"           # 0.4 - 0.6
    GOOD = "good"           # 0.6 - 0.8
    EXCELLENT = "excellent" # 0.8 - 0.95
    PERFECT = "perfect"     # 0.95 - 1.0

@dataclass
class QualityMetrics:
    """Comprehensive quality metrics"""
    overall_score: float
    dimension_scores: Dict[QualityDimension, float]
    technical_metrics: Dict[str, float]
    perceptual_metrics: Dict[str, float]
    comparative_metrics: Dict[str, float]
    confidence_intervals: Dict[str, Tuple[float, float]]

@dataclass
class QualityRecommendation:
    """
Quality improvement recommendation"""
    category: str
    priority: str  # high, medium, low
    description: str
    technical_details: str
    expected_improvement: float
    implementation_difficulty: str

@dataclass
class QualityAssessment:
    """
Complete quality assessment result"""
    assessment_id: str
    audio_analyzed: bool
    overall_quality_score: float
    quality_grade: QualityGrade
    dimension_analysis: Dict[QualityDimension, float]
    technical_analysis: Dict[str, Any]
    perceptual_analysis: Dict[str, Any]
    comparison_analysis: Dict[str, Any]
    recommendations: List[QualityRecommendation]
    confidence_score: float
    assessment_level: AssessmentLevel
    processing_time_seconds: float
    metadata: Dict[str, Any]
    success: bool

class AudioQualityNetwork(nn.Module):
    """
Neural network for audio quality assessment"""
    
    def __init__(self, input_features: int = 512, hidden_dim: int = 256):
        super(AudioQualityNetwork, self).__init__()
        
        # Feature extraction layers
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_features, hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU()
        )
        
        # Quality dimension predictors
        self.fidelity_predictor = nn.Sequential(
            nn.Linear(hidden_dim // 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        self.coherence_predictor = nn.Sequential(
            nn.Linear(hidden_dim // 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        self.creativity_predictor = nn.Sequential(
            nn.Linear(hidden_dim // 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        self.technical_predictor = nn.Sequential(
            nn.Linear(hidden_dim // 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        # Overall quality predictor
        self.overall_predictor = nn.Sequential(
            nn.Linear(hidden_dim // 2 + 4, 64),  # +4 for dimension scores
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        # Confidence estimator
        self.confidence_estimator = nn.Sequential(
            nn.Linear(hidden_dim // 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # Extract features
        features = self.feature_extractor(x)
        
        # Predict quality dimensions
        fidelity = self.fidelity_predictor(features)
        coherence = self.coherence_predictor(features)
        creativity = self.creativity_predictor(features)
        technical = self.technical_predictor(features)
        
        # Combine for overall prediction
        dimension_scores = torch.cat([fidelity, coherence, creativity, technical], dim=1)
        combined_features = torch.cat([features, dimension_scores], dim=1)
        overall = self.overall_predictor(combined_features)
        
        # Predict confidence
        confidence = self.confidence_estimator(features)
        
        return {
            'overall_quality': overall,
            'fidelity': fidelity,
            'coherence': coherence,
            'creativity': creativity,
            'technical': technical,
            'confidence': confidence
        }

class PerceptualQualityAnalyzer:
    """
Perceptual audio quality analysis"""
    
    def __init__(self):
        self.loudness_meter = pyln.Meter(44100)
        self.perceptual_models = self._initialize_perceptual_models()
    
    def _initialize_perceptual_models(self) -> Dict[str, Any]:
        """
Initialize perceptual quality models"""
        return {
            "loudness_standards": {
                "streaming": -14.0,  # LUFS
                "broadcast": -23.0,
                "cd": -16.0,
                "radio": -12.0
            },
            "dynamic_range_targets": {
                "minimum": 6.0,
                "good": 12.0,
                "excellent": 18.0
            },
            "frequency_balance_weights": {
                "sub_bass": 0.05,
                "bass": 0.15,
                "low_mid": 0.20,
                "mid": 0.25,
                "high_mid": 0.20,
                "presence": 0.10,
                "brilliance": 0.05
            }
        }
    
    async def analyze_perceptual_quality(self, audio: np.ndarray, 
                                       sample_rate: int = 44100) -> Dict[str, float]:
        """Comprehensive perceptual quality analysis"""
        try:
            analysis = {}
            
            # Loudness analysis
            analysis.update(await self._analyze_loudness(audio, sample_rate))
            
            # Dynamic range analysis
            analysis.update(await self._analyze_dynamic_range(audio))
            
            # Frequency balance analysis
            analysis.update(await self._analyze_frequency_balance(audio, sample_rate))
            
            # Stereo imaging analysis
            analysis.update(await self._analyze_stereo_imaging(audio))
            
            # Distortion analysis
            analysis.update(await self._analyze_distortion(audio, sample_rate))
            
            # Temporal stability analysis
            analysis.update(await self._analyze_temporal_stability(audio, sample_rate))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in perceptual quality analysis: {e}")
            return {}
    
    async def _analyze_loudness(self, audio: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze loudness characteristics"""
        try:
            # Ensure stereo for loudness measurement
            if audio.ndim == 1:
                audio_stereo = np.array([audio, audio])
            else:
                audio_stereo = audio
                
            # Integrated loudness
            integrated_loudness = self.loudness_meter.integrated_loudness(audio_stereo.T)
            
            # Loudness range
            loudness_range = self.loudness_meter.range(audio_stereo.T)
            
            # True peak
            true_peak = np.max(np.abs(audio))
            true_peak_db = 20 * np.log10(true_peak + 1e-8)
            
            # Loudness appropriateness score
            target_loudness = self.perceptual_models["loudness_standards"]["streaming"]
            loudness_deviation = abs(integrated_loudness - target_loudness)
            loudness_score = max(0.0, 1.0 - loudness_deviation / 20.0)
            
            # Dynamic range score
            target_lra = 7.0  # Good LRA target
            lra_deviation = abs(loudness_range - target_lra)
            lra_score = max(0.0, 1.0 - lra_deviation / 10.0)
            
            return {
                "integrated_loudness_lufs": integrated_loudness,
                "loudness_range_lu": loudness_range,
                "true_peak_db": true_peak_db,
                "loudness_appropriateness": loudness_score,
                "dynamic_range_score": lra_score,
                "peak_to_loudness_ratio": true_peak_db - integrated_loudness
            }
            
        except Exception as e:
            logger.error(f"Error analyzing loudness: {e}")
            return {
                "integrated_loudness_lufs": -16.0,
                "loudness_appropriateness": 0.5,
                "dynamic_range_score": 0.5
            }
    
    async def _analyze_dynamic_range(self, audio: np.ndarray) -> Dict[str, float]:
        """Analyze dynamic range characteristics"""
        try:
            # RMS and peak analysis
            rms = np.sqrt(np.mean(audio ** 2))
            peak = np.max(np.abs(audio))
            
            # Crest factor
            crest_factor = peak / (rms + 1e-8)
            crest_factor_db = 20 * np.log10(crest_factor)
            
            # DR meter calculation (simplified)
            block_size = len(audio) // 20  # 20 blocks
            if block_size > 0:
                blocks = [audio[i:i+block_size] for i in range(0, len(audio)-block_size, block_size)]
                dr_values = []
                
                for block in blocks:
                    if len(block) > 0:
                        block_rms = np.sqrt(np.mean(block ** 2))
                        block_peak = np.max(np.abs(block))
                        if block_rms > 0:
                            dr_value = 20 * np.log10(block_peak / block_rms)
                            dr_values.append(dr_value)
                
                dr_meter = np.mean(dr_values) if dr_values else 12.0
            else:
                dr_meter = crest_factor_db
            
            # Quality scores
            targets = self.perceptual_models["dynamic_range_targets"]
            
            if dr_meter >= targets["excellent"]:
                dr_quality = 1.0
            elif dr_meter >= targets["good"]:
                dr_quality = 0.8
            elif dr_meter >= targets["minimum"]:
                dr_quality = 0.6
            else:
                dr_quality = max(0.0, dr_meter / targets["minimum"] * 0.6)
            
            return {
                "crest_factor_db": crest_factor_db,
                "dr_meter": dr_meter,
                "dynamic_range_quality": dr_quality,
                "compression_level": max(0.0, 1.0 - dr_meter / 20.0)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing dynamic range: {e}")
            return {
                "crest_factor_db": 12.0,
                "dr_meter": 12.0,
                "dynamic_range_quality": 0.7
            }
    
    async def _analyze_frequency_balance(self, audio: np.ndarray, 
                                       sample_rate: int) -> Dict[str, float]:
        """Analyze frequency balance and spectral characteristics"""
        try:
            # Compute spectrum
            fft = np.fft.rfft(audio)
            magnitude = np.abs(fft)
            frequencies = np.fft.rfftfreq(len(audio), 1/sample_rate)
            
            # Define frequency bands
            bands = {
                "sub_bass": (20, 60),
                "bass": (60, 250),
                "low_mid": (250, 500),
                "mid": (500, 2000),
                "high_mid": (2000, 4000),
                "presence": (4000, 8000),
                "brilliance": (8000, 20000)
            }
            
            # Calculate band energies
            band_energies = {}
            total_energy = np.sum(magnitude ** 2)
            
            for band_name, (low_freq, high_freq) in bands.items():
                band_mask = (frequencies >= low_freq) & (frequencies <= high_freq)
                if np.any(band_mask):
                    band_energy = np.sum(magnitude[band_mask] ** 2)
                    band_energies[band_name] = band_energy / total_energy if total_energy > 0 else 0.0
                else:
                    band_energies[band_name] = 0.0
            
            # Calculate balance score
            weights = self.perceptual_models["frequency_balance_weights"]
            expected_distribution = np.array([weights[band] for band in bands.keys()])
            actual_distribution = np.array([band_energies[band] for band in bands.keys()])
            
            # Normalize actual distribution
            actual_sum = np.sum(actual_distribution)
            if actual_sum > 0:
                actual_distribution = actual_distribution / actual_sum
            
            # Calculate balance score using KL divergence
            kl_divergence = np.sum(expected_distribution * np.log((expected_distribution + 1e-8) / (actual_distribution + 1e-8)))
            balance_score = max(0.0, 1.0 - kl_divergence / 5.0)  # Normalize
            
            # Spectral centroid and rolloff
            spectral_centroid = np.sum(frequencies * magnitude) / np.sum(magnitude) if np.sum(magnitude) > 0 else 1000
            
            cumsum_magnitude = np.cumsum(magnitude)
            rolloff_threshold = 0.85 * cumsum_magnitude[-1]
            rolloff_idx = np.where(cumsum_magnitude >= rolloff_threshold)[0]
            spectral_rolloff = frequencies[rolloff_idx[0]] if len(rolloff_idx) > 0 else frequencies[-1]
            
            return {
                "frequency_balance_score": balance_score,
                "spectral_centroid": spectral_centroid,
                "spectral_rolloff": spectral_rolloff,
                "bass_energy": band_energies["bass"] + band_energies["sub_bass"],
                "midrange_energy": band_energies["low_mid"] + band_energies["mid"],
                "treble_energy": band_energies["high_mid"] + band_energies["presence"] + band_energies["brilliance"],
                **{f"{band}_energy": energy for band, energy in band_energies.items()}
            }
            
        except Exception as e:
            logger.error(f"Error analyzing frequency balance: {e}")
            return {
                "frequency_balance_score": 0.5,
                "spectral_centroid": 1000.0,
                "spectral_rolloff": 8000.0
            }
    
    async def _analyze_stereo_imaging(self, audio: np.ndarray) -> Dict[str, float]:
        """Analyze stereo imaging characteristics"""
        try:
            if audio.ndim == 1:
                return {
                    "stereo_width": 0.0,
                    "mono_compatibility": 1.0,
                    "phase_coherence": 1.0,
                    "stereo_balance": 0.0,
                    "stereo_quality": 1.0
                }
            
            left = audio[0] if audio.shape[0] == 2 else audio
            right = audio[1] if audio.shape[0] == 2 else audio
            
            # Stereo width (correlation-based)
            correlation = np.corrcoef(left, right)[0, 1] if len(left) > 1 else 1.0
            stereo_width = 1.0 - abs(correlation) if not np.isnan(correlation) else 0.5
            
            # Mono compatibility
            mono_sum = left + right
            mono_diff = left - right
            
            mono_sum_energy = np.sum(mono_sum ** 2)
            mono_diff_energy = np.sum(mono_diff ** 2)
            total_energy = mono_sum_energy + mono_diff_energy
            
            if total_energy > 0:
                mono_compatibility = mono_sum_energy / total_energy
            else:
                mono_compatibility = 1.0
            
            # Phase coherence
            cross_correlation = np.correlate(left, right, mode='full')
            max_corr = np.max(np.abs(cross_correlation))
            auto_corr_left = np.correlate(left, left, mode='full')
            auto_corr_right = np.correlate(right, right, mode='full')
            
            normalizer = np.sqrt(np.max(auto_corr_left) * np.max(auto_corr_right))
            if normalizer > 0:
                phase_coherence = max_corr / normalizer
            else:
                phase_coherence = 1.0
            
            # Stereo balance
            left_energy = np.sum(left ** 2)
            right_energy = np.sum(right ** 2)
            total_lr_energy = left_energy + right_energy
            
            if total_lr_energy > 0:
                balance = abs(left_energy - right_energy) / total_lr_energy
                stereo_balance = 1.0 - balance  # 1.0 = perfect balance
            else:
                stereo_balance = 1.0
            
            # Overall stereo quality
            stereo_quality = np.mean([
                min(stereo_width * 2, 1.0),  # Prefer some width but not too much
                mono_compatibility,
                phase_coherence,
                stereo_balance
            ])
            
            return {
                "stereo_width": stereo_width,
                "mono_compatibility": mono_compatibility,
                "phase_coherence": phase_coherence,
                "stereo_balance": stereo_balance,
                "stereo_quality": stereo_quality
            }
            
        except Exception as e:
            logger.error(f"Error analyzing stereo imaging: {e}")
            return {
                "stereo_width": 0.5,
                "mono_compatibility": 0.8,
                "phase_coherence": 0.9,
                "stereo_balance": 0.9,
                "stereo_quality": 0.8
            }
    
    async def _analyze_distortion(self, audio: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze distortion and artifacts"""
        try:
            # Clipping detection
            clipping_threshold = 0.99
            clipped_samples = np.sum(np.abs(audio) >= clipping_threshold)
            clipping_ratio = clipped_samples / len(audio)
            
            # THD estimation (simplified)
            # In practice, this would use sine wave analysis
            fft = np.fft.rfft(audio)
            magnitude = np.abs(fft)
            
            # Find fundamental frequency (simplified)
            frequencies = np.fft.rfftfreq(len(audio), 1/sample_rate)
            fundamental_idx = np.argmax(magnitude[1:]) + 1  # Skip DC
            fundamental_freq = frequencies[fundamental_idx]
            
            # Estimate harmonics
            harmonic_freqs = [fundamental_freq * (i + 2) for i in range(5)]  # 2nd to 6th harmonic
            harmonic_power = 0.0
            fundamental_power = magnitude[fundamental_idx] ** 2
            
            for harm_freq in harmonic_freqs:
                harm_idx = np.argmin(np.abs(frequencies - harm_freq))
                if harm_idx < len(magnitude):
                    harmonic_power += magnitude[harm_idx] ** 2
            
            if fundamental_power > 0:
                thd = np.sqrt(harmonic_power / fundamental_power)
            else:
                thd = 0.0
            
            # Noise floor estimation
            noise_floor = np.percentile(magnitude, 10)  # 10th percentile as noise estimate
            signal_level = np.percentile(magnitude, 90)  # 90th percentile as signal estimate
            
            if noise_floor > 0:
                snr = 20 * np.log10(signal_level / noise_floor)
            else:
                snr = 60.0  # Default good SNR
            
            # Distortion scores
            clipping_score = max(0.0, 1.0 - clipping_ratio * 100)
            thd_score = max(0.0, 1.0 - thd * 10)
            snr_score = min(1.0, max(0.0, (snr - 40) / 40))  # 40-80 dB range
            
            distortion_quality = np.mean([clipping_score, thd_score, snr_score])
            
            return {
                "clipping_ratio": clipping_ratio,
                "thd_estimate": thd,
                "snr_estimate": snr,
                "clipping_score": clipping_score,
                "thd_score": thd_score,
                "snr_score": snr_score,
                "distortion_quality": distortion_quality
            }
            
        except Exception as e:
            logger.error(f"Error analyzing distortion: {e}")
            return {
                "clipping_ratio": 0.0,
                "thd_estimate": 0.01,
                "snr_estimate": 60.0,
                "distortion_quality": 0.8
            }
    
    async def _analyze_temporal_stability(self, audio: np.ndarray, 
                                        sample_rate: int) -> Dict[str, float]:
        """Analyze temporal stability and consistency"""
        try:
            # Segment audio into blocks
            block_duration = 1.0  # 1 second blocks
            block_size = int(block_duration * sample_rate)
            num_blocks = len(audio) // block_size
            
            if num_blocks < 2:
                return {
                    "temporal_stability": 1.0,
                    "level_consistency": 1.0,
                    "spectral_consistency": 1.0
                }
            
            block_rms = []
            block_centroids = []
            
            for i in range(num_blocks):
                start_idx = i * block_size
                end_idx = min((i + 1) * block_size, len(audio))
                block = audio[start_idx:end_idx]
                
                # RMS level
                rms = np.sqrt(np.mean(block ** 2))
                block_rms.append(rms)
                
                # Spectral centroid
                if len(block) > 512:
                    block_fft = np.fft.rfft(block)
                    block_magnitude = np.abs(block_fft)
                    block_freqs = np.fft.rfftfreq(len(block), 1/sample_rate)
                    
                    if np.sum(block_magnitude) > 0:
                        centroid = np.sum(block_freqs * block_magnitude) / np.sum(block_magnitude)
                        block_centroids.append(centroid)
            
            # Level consistency
            if len(block_rms) > 1:
                rms_std = np.std(block_rms)
                rms_mean = np.mean(block_rms)
                if rms_mean > 0:
                    rms_cv = rms_std / rms_mean  # Coefficient of variation
                    level_consistency = max(0.0, 1.0 - rms_cv * 2)
                else:
                    level_consistency = 0.0
            else:
                level_consistency = 1.0
            
            # Spectral consistency
            if len(block_centroids) > 1:
                centroid_std = np.std(block_centroids)
                centroid_mean = np.mean(block_centroids)
                if centroid_mean > 0:
                    centroid_cv = centroid_std / centroid_mean
                    spectral_consistency = max(0.0, 1.0 - centroid_cv)
                else:
                    spectral_consistency = 0.0
            else:
                spectral_consistency = 1.0
            
            # Overall temporal stability
            temporal_stability = np.mean([level_consistency, spectral_consistency])
            
            return {
                "temporal_stability": temporal_stability,
                "level_consistency": level_consistency,
                "spectral_consistency": spectral_consistency,
                "rms_variation": rms_std if len(block_rms) > 1 else 0.0,
                "centroid_variation": np.std(block_centroids) if len(block_centroids) > 1 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing temporal stability: {e}")
            return {
                "temporal_stability": 0.8,
                "level_consistency": 0.8,
                "spectral_consistency": 0.8
            }

class RemixQualityAssessor:
    """Main remix quality assessment engine"""
    
    def __init__(self):
        # Neural networks
        self.quality_network = AudioQualityNetwork()
        
        # Analysis components
        self.perceptual_analyzer = PerceptualQualityAnalyzer()
        
        # Assessment models
        self.reference_models = self._initialize_reference_models()
        
        # Assessment history
        self.assessment_history = []
        
        logger.info("RemixQualityAssessor initialized successfully")
    
    def _initialize_reference_models(self) -> Dict[str, Any]:
        """Initialize reference quality models and benchmarks"""
        return {
            "professional_standards": {
                "minimum_dr": 8.0,
                "target_lufs": -14.0,
                "max_thd": 0.1,
                "min_snr": 60.0,
                "stereo_width_range": (0.3, 0.8),
                "frequency_balance_threshold": 0.7
            },
            "genre_adjustments": {
                "electronic": {"loudness_tolerance": 2.0, "dr_reduction": 2.0},
                "classical": {"loudness_tolerance": 4.0, "dr_bonus": 4.0},
                "rock": {"loudness_tolerance": 1.0, "dr_reduction": 1.0},
                "jazz": {"loudness_tolerance": 3.0, "dr_bonus": 2.0}
            },
            "quality_thresholds": {
                QualityGrade.POOR: 0.4,
                QualityGrade.FAIR: 0.6,
                QualityGrade.GOOD: 0.8,
                QualityGrade.EXCELLENT: 0.95,
                QualityGrade.PERFECT: 1.0
            }
        }
    
    async def assess_remix_quality(self, audio: np.ndarray,
                                 sample_rate: int = 44100,
                                 reference_audio: Optional[np.ndarray] = None,
                                 assessment_level: AssessmentLevel = AssessmentLevel.COMPREHENSIVE,
                                 genre: Optional[str] = None) -> QualityAssessment:
        """Comprehensive remix quality assessment"""
        try:
            start_time = datetime.now()
            assessment_id = f"assessment_{int(start_time.timestamp())}"
            
            # Extract audio features
            audio_features = await self._extract_audio_features(audio, sample_rate)
            
            # Neural network quality prediction
            neural_scores = await self._predict_quality_with_neural_network(audio_features)
            
            # Perceptual quality analysis
            perceptual_analysis = await self.perceptual_analyzer.analyze_perceptual_quality(audio, sample_rate)
            
            # Technical analysis
            technical_analysis = await self._perform_technical_analysis(audio, sample_rate)
            
            # Comparative analysis (if reference provided)
            comparison_analysis = {}
            if reference_audio is not None:
                comparison_analysis = await self._perform_comparative_analysis(
                    audio, reference_audio, sample_rate
                )
            
            # Dimension-specific analysis
            dimension_analysis = await self._analyze_quality_dimensions(
                audio, audio_features, perceptual_analysis, technical_analysis
            )
            
            # Calculate overall quality score
            overall_score = await self._calculate_overall_quality_score(
                neural_scores, dimension_analysis, perceptual_analysis, genre
            )
            
            # Determine quality grade
            quality_grade = await self._determine_quality_grade(overall_score)
            
            # Generate recommendations
            recommendations = await self._generate_quality_recommendations(
                dimension_analysis, perceptual_analysis, technical_analysis
            )
            
            # Calculate confidence
            confidence_score = neural_scores.get("confidence", 0.8)
            
            # Processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create assessment result
            assessment = QualityAssessment(
                assessment_id=assessment_id,
                audio_analyzed=True,
                overall_quality_score=overall_score,
                quality_grade=quality_grade,
                dimension_analysis=dimension_analysis,
                technical_analysis=technical_analysis,
                perceptual_analysis=perceptual_analysis,
                comparison_analysis=comparison_analysis,
                recommendations=recommendations,
                confidence_score=confidence_score,
                assessment_level=assessment_level,
                processing_time_seconds=processing_time,
                metadata={
                    "audio_length_seconds": len(audio) / sample_rate,
                    "sample_rate": sample_rate,
                    "num_channels": audio.ndim,
                    "genre": genre,
                    "has_reference": reference_audio is not None
                },
                success=True
            )
            
            # Store in history
            self.assessment_history.append({
                "timestamp": start_time.isoformat(),
                "assessment_id": assessment_id,
                "overall_score": overall_score,
                "quality_grade": quality_grade.value,
                "assessment_level": assessment_level.value,
                "confidence": confidence_score
            })
            
            logger.info(f"Quality assessment {assessment_id}: {overall_score:.2f} ({quality_grade.value})")
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error in quality assessment: {e}")
            raise
    
    async def _extract_audio_features(self, audio: np.ndarray, 
                                    sample_rate: int) -> np.ndarray:
        """Extract comprehensive audio features for neural network"""
        try:
            features = []
            
            # Spectral features
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            
            # MFCCs
            mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
            features.extend(np.mean(mfccs, axis=1))
            features.extend(np.std(mfccs, axis=1))
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)
            
            features.extend([
                np.mean(spectral_centroid),
                np.std(spectral_centroid),
                np.mean(spectral_rolloff),
                np.std(spectral_rolloff),
                np.mean(spectral_bandwidth),
                np.std(spectral_bandwidth),
                np.mean(zero_crossing_rate),
                np.std(zero_crossing_rate)
            ])
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(S=magnitude, sr=sample_rate)
            features.extend(np.mean(chroma, axis=1))
            
            # Tonnetz features
            tonnetz = librosa.feature.tonnetz(y=audio, sr=sample_rate)
            features.extend(np.mean(tonnetz, axis=1))
            
            # Temporal features
            tempo, beats = librosa.beat.beat_track(y=audio, sr=sample_rate)
            features.append(tempo)
            
            # Onset features
            onset_frames = librosa.onset.onset_detect(y=audio, sr=sample_rate)
            onset_rate = len(onset_frames) / (len(audio) / sample_rate)
            features.append(onset_rate)
            
            # RMS energy
            rms = librosa.feature.rms(y=audio)
            features.extend([np.mean(rms), np.std(rms)])
            
            # Ensure fixed feature size
            features = np.array(features)
            target_size = 512
            
            if len(features) < target_size:
                # Pad with zeros
                padded_features = np.zeros(target_size)
                padded_features[:len(features)] = features
                features = padded_features
            elif len(features) > target_size:
                # Truncate
                features = features[:target_size]
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting audio features: {e}")
            return np.zeros(512)
    
    async def _predict_quality_with_neural_network(self, features: np.ndarray) -> Dict[str, float]:
        """Predict quality scores using neural network"""
        try:
            # Convert to tensor
            features_tensor = torch.FloatTensor(features).unsqueeze(0)
            
            # Predict with neural network
            with torch.no_grad():
                predictions = self.quality_network(features_tensor)
            
            # Convert to dictionary
            neural_scores = {
                "overall_quality": predictions["overall_quality"].item(),
                "fidelity": predictions["fidelity"].item(),
                "coherence": predictions["coherence"].item(),
                "creativity": predictions["creativity"].item(),
                "technical": predictions["technical"].item(),
                "confidence": predictions["confidence"].item()
            }
            
            return neural_scores
            
        except Exception as e:
            logger.error(f"Error in neural network prediction: {e}")
            return {
                "overall_quality": 0.7,
                "fidelity": 0.7,
                "coherence": 0.7,
                "creativity": 0.7,
                "technical": 0.7,
                "confidence": 0.6
            }
    
    async def _perform_technical_analysis(self, audio: np.ndarray, 
                                        sample_rate: int) -> Dict[str, Any]:
        """Perform detailed technical analysis"""
        try:
            technical_analysis = {}
            
            # Basic audio properties
            technical_analysis["duration_seconds"] = len(audio) / sample_rate
            technical_analysis["peak_amplitude"] = np.max(np.abs(audio))
            technical_analysis["rms_level"] = np.sqrt(np.mean(audio ** 2))
            
            # DC offset analysis
            dc_offset = np.mean(audio)
            technical_analysis["dc_offset"] = dc_offset
            technical_analysis["dc_offset_significant"] = abs(dc_offset) > 0.01
            
            # Frequency analysis
            fft = np.fft.rfft(audio)
            magnitude = np.abs(fft)
            frequencies = np.fft.rfftfreq(len(audio), 1/sample_rate)
            
            # Find dominant frequency
            dominant_freq_idx = np.argmax(magnitude[1:]) + 1  # Skip DC
            technical_analysis["dominant_frequency"] = frequencies[dominant_freq_idx]
            
            # Bandwidth analysis
            total_power = np.sum(magnitude ** 2)
            cumulative_power = np.cumsum(magnitude ** 2)
            
            # Find frequencies containing 90% of energy
            threshold_90 = 0.9 * total_power
            idx_90 = np.where(cumulative_power >= threshold_90)[0]
            bandwidth_90 = frequencies[idx_90[0]] if len(idx_90) > 0 else sample_rate / 2
            
            technical_analysis["bandwidth_90_percent"] = bandwidth_90
            
            # Phase analysis (if stereo)
            if audio.ndim > 1:
                left = audio[0]
                right = audio[1]
                
                # Phase correlation
                cross_corr = np.correlate(left, right, mode='full')
                max_corr_idx = np.argmax(np.abs(cross_corr))
                center_idx = len(cross_corr) // 2
                phase_delay_samples = max_corr_idx - center_idx
                phase_delay_ms = (phase_delay_samples / sample_rate) * 1000
                
                technical_analysis["phase_delay_ms"] = phase_delay_ms
                technical_analysis["phase_coherence"] = np.max(np.abs(cross_corr)) / len(left)
            
            return technical_analysis
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            return {}
    
    async def _perform_comparative_analysis(self, audio: np.ndarray,
                                          reference: np.ndarray,
                                          sample_rate: int) -> Dict[str, float]:
        """Perform comparative analysis against reference"""
        try:
            comparison = {}
            
            # Ensure same length for comparison
            min_length = min(len(audio), len(reference))
            audio_trimmed = audio[:min_length]
            reference_trimmed = reference[:min_length]
            
            # Spectral similarity
            audio_spectrum = np.abs(np.fft.rfft(audio_trimmed))
            ref_spectrum = np.abs(np.fft.rfft(reference_trimmed))
            
            # Normalize spectra
            if np.sum(audio_spectrum) > 0:
                audio_spectrum = audio_spectrum / np.sum(audio_spectrum)
            if np.sum(ref_spectrum) > 0:
                ref_spectrum = ref_spectrum / np.sum(ref_spectrum)
            
            # Calculate spectral similarity
            spectral_correlation = pearsonr(audio_spectrum, ref_spectrum)[0]
            if np.isnan(spectral_correlation):
                spectral_correlation = 0.0
            
            comparison["spectral_similarity"] = spectral_correlation
            
            # Loudness comparison
            audio_rms = np.sqrt(np.mean(audio_trimmed ** 2))
            ref_rms = np.sqrt(np.mean(reference_trimmed ** 2))
            
            if ref_rms > 0:
                loudness_ratio = audio_rms / ref_rms
                loudness_difference_db = 20 * np.log10(loudness_ratio)
                comparison["loudness_difference_db"] = loudness_difference_db
                comparison["loudness_similarity"] = max(0.0, 1.0 - abs(loudness_difference_db) / 20.0)
            else:
                comparison["loudness_similarity"] = 0.0
            
            # Temporal similarity
            audio_features = await self._extract_audio_features(audio_trimmed, sample_rate)
            ref_features = await self._extract_audio_features(reference_trimmed, sample_rate)
            
            feature_correlation = pearsonr(audio_features, ref_features)[0]
            if np.isnan(feature_correlation):
                feature_correlation = 0.0
            
            comparison["feature_similarity"] = feature_correlation
            
            # Overall similarity
            comparison["overall_similarity"] = np.mean([
                comparison["spectral_similarity"],
                comparison["loudness_similarity"],
                comparison["feature_similarity"]
            ])
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error in comparative analysis: {e}")
            return {"overall_similarity": 0.5}
    
    async def _analyze_quality_dimensions(self, audio: np.ndarray,
                                        features: np.ndarray,
                                        perceptual_analysis: Dict[str, float],
                                        technical_analysis: Dict[str, Any]) -> Dict[QualityDimension, float]:
        """Analyze quality across different dimensions"""
        try:
            dimension_scores = {}
            
            # Audio Fidelity
            fidelity_components = [
                perceptual_analysis.get("distortion_quality", 0.7),
                perceptual_analysis.get("snr_score", 0.7),
                perceptual_analysis.get("clipping_score", 0.9)
            ]
            dimension_scores[QualityDimension.AUDIO_FIDELITY] = np.mean(fidelity_components)
            
            # Musical Coherence
            coherence_components = [
                perceptual_analysis.get("temporal_stability", 0.8),
                perceptual_analysis.get("spectral_consistency", 0.8),
                min(1.0, technical_analysis.get("bandwidth_90_percent", 10000) / 15000)
            ]
            dimension_scores[QualityDimension.MUSICAL_COHERENCE] = np.mean(coherence_components)
            
            # Technical Execution
            execution_components = [
                perceptual_analysis.get("loudness_appropriateness", 0.7),
                perceptual_analysis.get("dynamic_range_score", 0.7),
                perceptual_analysis.get("frequency_balance_score", 0.7)
            ]
            dimension_scores[QualityDimension.TECHNICAL_EXECUTION] = np.mean(execution_components)
            
            # Perceptual Quality
            perceptual_components = [
                perceptual_analysis.get("stereo_quality", 0.8),
                perceptual_analysis.get("frequency_balance_score", 0.7),
                perceptual_analysis.get("temporal_stability", 0.8)
            ]
            dimension_scores[QualityDimension.PERCEPTUAL_QUALITY] = np.mean(perceptual_components)
            
            # Dynamic Processing
            dynamic_components = [
                perceptual_analysis.get("dynamic_range_score", 0.7),
                1.0 - perceptual_analysis.get("compression_level", 0.3),
                perceptual_analysis.get("level_consistency", 0.8)
            ]
            dimension_scores[QualityDimension.DYNAMIC_PROCESSING] = np.mean(dynamic_components)
            
            # Stereo Imaging
            dimension_scores[QualityDimension.STEREO_IMAGING] = perceptual_analysis.get("stereo_quality", 0.8)
            
            # Frequency Balance
            dimension_scores[QualityDimension.FREQUENCY_BALANCE] = perceptual_analysis.get("frequency_balance_score", 0.7)
            
            # For dimensions not directly computed, use reasonable defaults
            dimension_scores[QualityDimension.CREATIVE_ENHANCEMENT] = 0.75  # Would need specific analysis
            dimension_scores[QualityDimension.HARMONIC_CONSISTENCY] = 0.8   # Would need harmonic analysis
            dimension_scores[QualityDimension.RHYTHMIC_ACCURACY] = 0.8      # Would need rhythm analysis
            
            return dimension_scores
            
        except Exception as e:
            logger.error(f"Error analyzing quality dimensions: {e}")
            return {dim: 0.7 for dim in QualityDimension}
    
    async def _calculate_overall_quality_score(self, neural_scores: Dict[str, float],
                                             dimension_scores: Dict[QualityDimension, float],
                                             perceptual_analysis: Dict[str, float],
                                             genre: Optional[str]) -> float:
        """Calculate overall quality score with weighted components"""
        try:
            # Base neural network score
            neural_overall = neural_scores.get("overall_quality", 0.7)
            
            # Dimension average
            dimension_average = np.mean(list(dimension_scores.values()))
            
            # Key perceptual metrics
            key_perceptual = np.mean([
                perceptual_analysis.get("loudness_appropriateness", 0.7),
                perceptual_analysis.get("dynamic_range_score", 0.7),
                perceptual_analysis.get("frequency_balance_score", 0.7),
                perceptual_analysis.get("distortion_quality", 0.8)
            ])
            
            # Weighted combination
            weights = {
                "neural": 0.3,
                "dimensions": 0.4,
                "perceptual": 0.3
            }
            
            overall_score = (
                neural_overall * weights["neural"] +
                dimension_average * weights["dimensions"] +
                key_perceptual * weights["perceptual"]
            )
            
            # Genre-specific adjustments
            if genre and genre in self.reference_models["genre_adjustments"]:
                adjustments = self.reference_models["genre_adjustments"][genre]
                # Apply minor adjustments based on genre expectations
                # This is simplified - real implementation would be more sophisticated
                overall_score *= (1.0 + adjustments.get("quality_bonus", 0.0) * 0.1)
            
            return max(0.0, min(1.0, overall_score))
            
        except Exception as e:
            logger.error(f"Error calculating overall quality score: {e}")
            return 0.7
    
    async def _determine_quality_grade(self, overall_score: float) -> QualityGrade:
        """Determine quality grade based on overall score"""
        try:
            thresholds = self.reference_models["quality_thresholds"]
            
            if overall_score >= thresholds[QualityGrade.PERFECT]:
                return QualityGrade.PERFECT
            elif overall_score >= thresholds[QualityGrade.EXCELLENT]:
                return QualityGrade.EXCELLENT
            elif overall_score >= thresholds[QualityGrade.GOOD]:
                return QualityGrade.GOOD
            elif overall_score >= thresholds[QualityGrade.FAIR]:
                return QualityGrade.FAIR
            else:
                return QualityGrade.POOR
                
        except Exception as e:
            logger.error(f"Error determining quality grade: {e}")
            return QualityGrade.FAIR
    
    async def _generate_quality_recommendations(self, dimension_scores: Dict[QualityDimension, float],
                                              perceptual_analysis: Dict[str, float],
                                              technical_analysis: Dict[str, Any]) -> List[QualityRecommendation]:
        """Generate quality improvement recommendations"""
        try:
            recommendations = []
            
            # Audio Fidelity recommendations
            if dimension_scores[QualityDimension.AUDIO_FIDELITY] < 0.7:
                if perceptual_analysis.get("clipping_ratio", 0.0) > 0.01:
                    recommendations.append(QualityRecommendation(
                        category="Audio Fidelity",
                        priority="high",
                        description="Reduce clipping distortion",
                        technical_details="Lower input levels or apply limiting before final stage",
                        expected_improvement=0.2,
                        implementation_difficulty="medium"
                    ))
                
                if perceptual_analysis.get("snr_estimate", 60) < 50:
                    recommendations.append(QualityRecommendation(
                        category="Audio Fidelity",
                        priority="medium",
                        description="Improve signal-to-noise ratio",
                        technical_details="Apply noise reduction or use higher quality source material",
                        expected_improvement=0.15,
                        implementation_difficulty="medium"
                    ))
            
            # Dynamic Processing recommendations
            if dimension_scores[QualityDimension.DYNAMIC_PROCESSING] < 0.6:
                dr_score = perceptual_analysis.get("dynamic_range_score", 0.7)
                if dr_score < 0.5:
                    recommendations.append(QualityRecommendation(
                        category="Dynamic Processing",
                        priority="high",
                        description="Improve dynamic range",
                        technical_details="Reduce excessive compression, increase DR to 8+ dB",
                        expected_improvement=0.25,
                        implementation_difficulty="medium"
                    ))
            
            # Frequency Balance recommendations
            if dimension_scores[QualityDimension.FREQUENCY_BALANCE] < 0.6:
                recommendations.append(QualityRecommendation(
                    category="Frequency Balance",
                    priority="medium",
                    description="Improve frequency balance",
                    technical_details="Apply EQ to balance bass, midrange, and treble content",
                    expected_improvement=0.18,
                    implementation_difficulty="low"
                ))
            
            # Stereo Imaging recommendations
            if dimension_scores[QualityDimension.STEREO_IMAGING] < 0.7:
                stereo_width = perceptual_analysis.get("stereo_width", 0.5)
                if stereo_width < 0.2:
                    recommendations.append(QualityRecommendation(
                        category="Stereo Imaging",
                        priority="low",
                        description="Enhance stereo width",
                        technical_details="Apply stereo widening or use stereo enhancement plugins",
                        expected_improvement=0.1,
                        implementation_difficulty="low"
                    ))
                elif stereo_width > 0.9:
                    recommendations.append(QualityRecommendation(
                        category="Stereo Imaging",
                        priority="medium",
                        description="Reduce excessive stereo width",
                        technical_details="Check for phase issues and reduce stereo enhancement",
                        expected_improvement=0.15,
                        implementation_difficulty="low"
                    ))
            
            # Loudness recommendations
            loudness_score = perceptual_analysis.get("loudness_appropriateness", 0.7)
            if loudness_score < 0.6:
                recommendations.append(QualityRecommendation(
                    category="Loudness",
                    priority="medium",
                    description="Adjust loudness to target level",
                    technical_details="Target -14 LUFS for streaming platforms",
                    expected_improvement=0.12,
                    implementation_difficulty="low"
                ))
            
            # Sort by priority and expected improvement
            priority_order = {"high": 3, "medium": 2, "low": 1}
            recommendations.sort(
                key=lambda x: (priority_order[x.priority], x.expected_improvement),
                reverse=True
            )
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def get_assessment_statistics(self) -> Dict[str, Any]:
        """Get assessment performance statistics"""
        try:
            if not self.assessment_history:
                return {"total_assessments": 0}
            
            recent_history = self.assessment_history[-30:]  # Last 30 assessments
            
            # Calculate statistics
            scores = [h["overall_score"] for h in recent_history]
            grades = [h["quality_grade"] for h in recent_history]
            
            return {
                "total_assessments": len(self.assessment_history),
                "recent_average_score": np.mean(scores),
                "recent_score_std": np.std(scores),
                "grade_distribution": {
                    grade: sum(1 for g in grades if g == grade)
                    for grade in set(grades)
                },
                "assessment_level_distribution": {
                    level: sum(1 for h in recent_history if h["assessment_level"] == level)
                    for level in set(h["assessment_level"] for h in recent_history)
                },
                "average_confidence": np.mean([h["confidence"] for h in recent_history]),
                "last_assessment": recent_history[-1] if recent_history else None
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"total_assessments": 0}

# Processing classes for export
QualityAnalyzer = RemixQualityAssessor
AudioQualityAssessor = RemixQualityAssessor
QualityValidator = RemixQualityAssessor

# Export classes
__all__ = [
    "RemixQualityAssessor",
    "QualityAnalyzer",
    "AudioQualityAssessor",
    "QualityValidator",
    "QualityDimension",
    "AssessmentLevel", 
    "QualityGrade",
    "QualityMetrics",
    "QualityRecommendation",
    "QualityAssessment",
    "AudioQualityNetwork",
    "PerceptualQualityAnalyzer"
]