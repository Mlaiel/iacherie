"""Quality Assessment and Scoring System
Comprehensive quality evaluation for multimedia content.

This module provides quality assessment algorithms for audio, video, and image content,
including perceptual quality metrics, technical quality validation, and scoring systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ COPYRIGHT PROTECTION ⚠️
This code is proprietary and confidential. Unauthorized use is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import numpy as np
import cv2
import librosa
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from enum import Enum
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import torch
import torch.nn as nn
from pathlib import Path

logger = logging.getLogger(__name__)

class QualityLevel(Enum):
    """Quality level classifications"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

@dataclass
class QualityScore:
    """Quality score with detailed breakdown"""
    overall_score: float
    quality_level: QualityLevel
    
    # Component scores
    technical_quality: float = 0.0
    perceptual_quality: float = 0.0
    content_quality: float = 0.0
    aesthetic_quality: float = 0.0
    
    # Detailed metrics
    detailed_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Issues and recommendations
    quality_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    assessment_timestamp: datetime = field(default_factory=datetime.now)
    assessment_duration: float = 0.0
    
    def __post_init__(self):
        """Determine quality level based on overall score"""
        if self.overall_score >= 0.9:
            self.quality_level = QualityLevel.EXCELLENT
        elif self.overall_score >= 0.75:
            self.quality_level = QualityLevel.GOOD
        elif self.overall_score >= 0.6:
            self.quality_level = QualityLevel.FAIR
        elif self.overall_score >= 0.4:
            self.quality_level = QualityLevel.POOR
        else:
            self.quality_level = QualityLevel.UNACCEPTABLE


class AudioQualityAssessment:
    """Audio quality assessment algorithms"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Quality thresholds
        self.thresholds = self.config.get('audio_thresholds', {
            'snr_excellent': 40.0,
            'snr_good': 25.0,
            'snr_fair': 15.0,
            'dynamic_range_excellent': 30.0,
            'dynamic_range_good': 20.0,
            'dynamic_range_fair': 10.0,
            'clipping_threshold': 0.01,
            'silence_threshold': 0.1
        })
    
    async def assess_audio_quality(self, file_path: str) -> QualityScore:
        """Comprehensive audio quality assessment"""
        start_time = datetime.now()
        
        try:
            # Load audio
            audio, sr = librosa.load(file_path, sr=None, mono=True)
            
            # Technical quality assessment
            technical_score, technical_metrics = await self._assess_technical_quality(audio, sr)
            
            # Perceptual quality assessment
            perceptual_score, perceptual_metrics = await self._assess_perceptual_quality(audio, sr)
            
            # Content quality assessment
            content_score, content_metrics = await self._assess_content_quality(audio, sr)
            
            # Combine all metrics
            all_metrics = {**technical_metrics, **perceptual_metrics, **content_metrics}
            
            # Calculate overall score
            overall_score = np.mean([technical_score, perceptual_score, content_score])
            
            # Generate quality issues and recommendations
            issues, recommendations = self._analyze_quality_issues(all_metrics)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return QualityScore(
                overall_score=float(overall_score),
                technical_quality=float(technical_score),
                perceptual_quality=float(perceptual_score),
                content_quality=float(content_score),
                detailed_metrics=all_metrics,
                quality_issues=issues,
                recommendations=recommendations,
                assessment_duration=duration
            )
            
        except Exception as e:
            self.logger.error(f"Audio quality assessment failed: {e}")
            return QualityScore(overall_score=0.0)
    
    async def _assess_technical_quality(self, audio: np.ndarray, sr: int) -> Tuple[float, Dict[str, float]]:
        """Assess technical audio quality"""
        try:
            metrics = {}
            
            # Signal-to-noise ratio estimation
            signal_power = np.mean(audio**2)
            noise_segments = audio[np.abs(audio) < np.percentile(np.abs(audio), 10)]
            noise_power = np.mean(noise_segments**2) if len(noise_segments) > 0 else 1e-10
            snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
            metrics['snr_db'] = float(snr)
            
            # Dynamic range
            rms = np.sqrt(np.mean(audio**2))
            peak = np.max(np.abs(audio))
            dynamic_range = 20 * np.log10(peak / (rms + 1e-10))
            metrics['dynamic_range_db'] = float(dynamic_range)
            
            # Clipping detection
            clipping_threshold = 0.99
            clipped_samples = np.sum(np.abs(audio) > clipping_threshold)
            clipping_percentage = clipped_samples / len(audio) * 100
            metrics['clipping_percentage'] = float(clipping_percentage)
            
            # Frequency response analysis
            fft = np.fft.fft(audio)
            freqs = np.fft.fftfreq(len(fft), 1/sr)
            magnitude = np.abs(fft)
            
            # Frequency bands analysis
            low_band = magnitude[(freqs >= 20) & (freqs < 250)]
            mid_band = magnitude[(freqs >= 250) & (freqs < 4000)]
            high_band = magnitude[(freqs >= 4000) & (freqs < sr//2)]
            
            total_energy = np.sum(magnitude)
            if total_energy > 0:
                metrics['low_freq_energy'] = float(np.sum(low_band) / total_energy)
                metrics['mid_freq_energy'] = float(np.sum(mid_band) / total_energy)
                metrics['high_freq_energy'] = float(np.sum(high_band) / total_energy)
            
            # Calculate technical score
            snr_score = min(snr / self.thresholds['snr_excellent'], 1.0)
            dr_score = min(dynamic_range / self.thresholds['dynamic_range_excellent'], 1.0)
            clipping_score = max(0.0, 1.0 - clipping_percentage / 5.0)  # Penalize clipping
            
            technical_score = np.mean([snr_score, dr_score, clipping_score])
            
            return technical_score, metrics
            
        except Exception as e:
            self.logger.error(f"Technical quality assessment failed: {e}")
            return 0.0, {}
    
    async def _assess_perceptual_quality(self, audio: np.ndarray, sr: int) -> Tuple[float, Dict[str, float]]:
        """Assess perceptual audio quality"""
        try:
            metrics = {}
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
            
            metrics['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            metrics['spectral_centroid_std'] = float(np.std(spectral_centroids))
            metrics['spectral_bandwidth_mean'] = float(np.mean(spectral_bandwidth))
            metrics['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
            
            # Harmonic-percussive separation
            harmonic, percussive = librosa.effects.hpss(audio)
            harmonic_ratio = np.sum(harmonic**2) / (np.sum(audio**2) + 1e-10)
            metrics['harmonic_ratio'] = float(harmonic_ratio)
            
            # Tonal vs noise content
            tonnetz = librosa.feature.tonnetz(y=harmonic, sr=sr)
            tonal_strength = np.mean(np.abs(tonnetz))
            metrics['tonal_strength'] = float(tonal_strength)
            
            # Chroma features for musical content
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
            chroma_strength = np.mean(np.max(chroma, axis=0))
            metrics['chroma_strength'] = float(chroma_strength)
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            metrics['mfcc_variance'] = float(np.mean(np.var(mfccs, axis=1)))
            
            # Perceptual score calculation
            # Higher spectral centroid variation indicates more interesting content
            centroid_score = min(metrics['spectral_centroid_std'] / 1000.0, 1.0)
            
            # Harmonic content score
            harmonic_score = harmonic_ratio
            
            # Tonal strength score
            tonal_score = min(tonal_strength * 2.0, 1.0)
            
            perceptual_score = np.mean([centroid_score, harmonic_score, tonal_score])
            
            return perceptual_score, metrics
            
        except Exception as e:
            self.logger.error(f"Perceptual quality assessment failed: {e}")
            return 0.0, {}
    
    async def _assess_content_quality(self, audio: np.ndarray, sr: int) -> Tuple[float, Dict[str, float]]:
        """Assess audio content quality"""
        try:
            metrics = {}
            
            # Silence analysis
            silence_threshold = 0.001
            silent_samples = np.sum(np.abs(audio) < silence_threshold)
            silence_percentage = silent_samples / len(audio) * 100
            metrics['silence_percentage'] = float(silence_percentage)
            
            # Energy distribution over time
            frame_length = sr // 10  # 100ms frames
            energy_frames = []
            for i in range(0, len(audio) - frame_length, frame_length):
                frame_energy = np.sum(audio[i:i+frame_length]**2)
                energy_frames.append(frame_energy)
            
            if energy_frames:
                energy_variation = np.std(energy_frames) / (np.mean(energy_frames) + 1e-10)
                metrics['energy_variation'] = float(energy_variation)
            
            # Tempo estimation (for musical content)
            try:
                tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
                metrics['estimated_tempo'] = float(tempo)
            except:
                metrics['estimated_tempo'] = 0.0
            
            # Zero crossing rate variation
            zcr = librosa.feature.zero_crossing_rate(audio)[0]
            zcr_variation = np.std(zcr)
            metrics['zcr_variation'] = float(zcr_variation)
            
            # Content score calculation
            silence_score = max(0.0, 1.0 - silence_percentage / 20.0)  # Penalize excessive silence
            energy_score = min(energy_variation / 0.5, 1.0) if 'energy_variation' in metrics else 0.5
            tempo_score = 1.0 if 60 <= metrics['estimated_tempo'] <= 200 else 0.7
            
            content_score = np.mean([silence_score, energy_score, tempo_score])
            
            return content_score, metrics
            
        except Exception as e:
            self.logger.error(f"Content quality assessment failed: {e}")
            return 0.0, {}
    
    def _analyze_quality_issues(self, metrics: Dict[str, float]) -> Tuple[List[str], List[str]]:
        """Analyze quality metrics and generate issues/recommendations"""
        issues = []
        recommendations = []
        
        # SNR issues
        if metrics.get('snr_db', 0) < self.thresholds['snr_fair']:
            issues.append("Low signal-to-noise ratio")
            recommendations.append("Apply noise reduction or re-record in quieter environment")
        
        # Dynamic range issues
        if metrics.get('dynamic_range_db', 0) < self.thresholds['dynamic_range_fair']:
            issues.append("Limited dynamic range")
            recommendations.append("Avoid over-compression or normalize audio levels")
        
        # Clipping issues
        if metrics.get('clipping_percentage', 0) > self.thresholds['clipping_threshold']:
            issues.append("Audio clipping detected")
            recommendations.append("Reduce input levels to prevent clipping")
        
        # Silence issues
        if metrics.get('silence_percentage', 0) > self.thresholds['silence_threshold'] * 100:
            issues.append("Excessive silence in audio")
            recommendations.append("Trim silence or add content to improve engagement")
        
        # Frequency balance issues
        low_energy = metrics.get('low_freq_energy', 0)
        high_energy = metrics.get('high_freq_energy', 0)
        
        if low_energy > 0.7:
            issues.append("Bass-heavy frequency distribution")
            recommendations.append("Apply high-pass filter to balance frequencies")
        
        if high_energy < 0.1:
            issues.append("Lack of high-frequency content")
            recommendations.append("Check microphone quality or apply brightness enhancement")
        
        return issues, recommendations


class VideoQualityAssessment:
    """Video quality assessment algorithms"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Quality thresholds
        self.thresholds = self.config.get('video_thresholds', {
            'psnr_excellent': 35.0,
            'psnr_good': 30.0,
            'psnr_fair': 25.0,
            'ssim_excellent': 0.95,
            'ssim_good': 0.90,
            'ssim_fair': 0.80,
            'sharpness_excellent': 1000.0,
            'sharpness_good': 500.0,
            'sharpness_fair': 200.0
        })
    
    async def assess_video_quality(self, file_path: str) -> QualityScore:
        """Comprehensive video quality assessment"""
        start_time = datetime.now()
        
        try:
            # Open video file
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {file_path}")
            
            # Sample frames for analysis
            frames = await self._sample_frames(cap)
            cap.release()
            
            if len(frames) < 2:
                raise ValueError("Insufficient frames for analysis")
            
            # Technical quality assessment
            technical_score, technical_metrics = await self._assess_video_technical_quality(frames)
            
            # Perceptual quality assessment
            perceptual_score, perceptual_metrics = await self._assess_video_perceptual_quality(frames)
            
            # Content quality assessment
            content_score, content_metrics = await self._assess_video_content_quality(frames)
            
            # Combine all metrics
            all_metrics = {**technical_metrics, **perceptual_metrics, **content_metrics}
            
            # Calculate overall score
            overall_score = np.mean([technical_score, perceptual_score, content_score])
            
            # Generate quality issues and recommendations
            issues, recommendations = self._analyze_video_quality_issues(all_metrics)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return QualityScore(
                overall_score=float(overall_score),
                technical_quality=float(technical_score),
                perceptual_quality=float(perceptual_score),
                content_quality=float(content_score),
                detailed_metrics=all_metrics,
                quality_issues=issues,
                recommendations=recommendations,
                assessment_duration=duration
            )
            
        except Exception as e:
            self.logger.error(f"Video quality assessment failed: {e}")
            return QualityScore(overall_score=0.0)
    
    async def _sample_frames(self, cap: cv2.VideoCapture) -> List[np.ndarray]:
        """Sample frames from video for analysis"""
        try:
            frames = []
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, frame_count // 50)  # Sample 50 frames max
            
            for i in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
                
                if len(frames) >= 50:
                    break
            
            return frames
            
        except Exception as e:
            self.logger.error(f"Frame sampling failed: {e}")
            return []
    
    async def _assess_video_technical_quality(self, frames: List[np.ndarray]) -> Tuple[float, Dict[str, float]]:
        """Assess technical video quality"""
        try:
            metrics = {}
            
            # PSNR between consecutive frames
            psnr_values = []
            for i in range(len(frames) - 1):
                frame1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                frame2 = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY)
                
                psnr_val = psnr(frame1, frame2, data_range=255)
                if not np.isinf(psnr_val):
                    psnr_values.append(psnr_val)
            
            metrics['average_psnr'] = float(np.mean(psnr_values)) if psnr_values else 0.0
            
            # SSIM between consecutive frames
            ssim_values = []
            for i in range(len(frames) - 1):
                frame1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                frame2 = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY)
                
                ssim_val = ssim(frame1, frame2, data_range=255)
                ssim_values.append(ssim_val)
            
            metrics['average_ssim'] = float(np.mean(ssim_values)) if ssim_values else 0.0
            
            # Sharpness analysis
            sharpness_values = []
            for frame in frames[::5]:  # Sample every 5th frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                sharpness = laplacian.var()
                sharpness_values.append(sharpness)
            
            metrics['average_sharpness'] = float(np.mean(sharpness_values)) if sharpness_values else 0.0
            
            # Noise estimation
            noise_values = []
            for frame in frames[::10]:  # Sample every 10th frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Simple noise estimation using Laplacian
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                noise_estimate = np.std(laplacian)
                noise_values.append(noise_estimate)
            
            metrics['average_noise'] = float(np.mean(noise_values)) if noise_values else 0.0
            
            # Technical score calculation
            psnr_score = min(metrics['average_psnr'] / self.thresholds['psnr_excellent'], 1.0)
            ssim_score = metrics['average_ssim']
            sharpness_score = min(metrics['average_sharpness'] / self.thresholds['sharpness_excellent'], 1.0)
            
            technical_score = np.mean([psnr_score, ssim_score, sharpness_score])
            
            return technical_score, metrics
            
        except Exception as e:
            self.logger.error(f"Video technical quality assessment failed: {e}")
            return 0.0, {}
    
    async def _assess_video_perceptual_quality(self, frames: List[np.ndarray]) -> Tuple[float, Dict[str, float]]:
        """Assess perceptual video quality"""
        try:
            metrics = {}
            
            # Color analysis
            color_stats = {'red': [], 'green': [], 'blue': []}
            brightness_values = []
            contrast_values = []
            
            for frame in frames[::5]:  # Sample every 5th frame
                # Color analysis
                color_stats['blue'].append(np.mean(frame[:, :, 0]))
                color_stats['green'].append(np.mean(frame[:, :, 1]))
                color_stats['red'].append(np.mean(frame[:, :, 2]))
                
                # Brightness analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness_values.append(np.mean(gray))
                
                # Contrast analysis
                contrast = np.std(gray)
                contrast_values.append(contrast)
            
            # Color consistency
            color_consistency = 1.0 - np.mean([
                np.std(color_stats['red']) / 255.0,
                np.std(color_stats['green']) / 255.0,
                np.std(color_stats['blue']) / 255.0
            ])
            metrics['color_consistency'] = float(color_consistency)
            
            # Brightness stability
            brightness_stability = 1.0 - (np.std(brightness_values) / 255.0)
            metrics['brightness_stability'] = float(brightness_stability)
            
            # Contrast quality
            average_contrast = np.mean(contrast_values)
            metrics['average_contrast'] = float(average_contrast)
            
            # Edge density (detail level)
            edge_densities = []
            for frame in frames[::10]:  # Sample every 10th frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size
                edge_densities.append(edge_density)
            
            metrics['average_edge_density'] = float(np.mean(edge_densities)) if edge_densities else 0.0
            
            # Perceptual score calculation
            consistency_score = color_consistency
            stability_score = brightness_stability
            contrast_score = min(average_contrast / 50.0, 1.0)  # Normalize contrast
            detail_score = min(metrics['average_edge_density'] * 10.0, 1.0)
            
            perceptual_score = np.mean([consistency_score, stability_score, contrast_score, detail_score])
            
            return perceptual_score, metrics
            
        except Exception as e:
            self.logger.error(f"Video perceptual quality assessment failed: {e}")
            return 0.0, {}
    
    async def _assess_video_content_quality(self, frames: List[np.ndarray]) -> Tuple[float, Dict[str, float]]:
        """Assess video content quality"""
        try:
            metrics = {}
            
            # Motion analysis
            motion_magnitudes = []
            for i in range(len(frames) - 1):
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY)
                
                # Calculate frame difference
                diff = cv2.absdiff(gray1, gray2)
                motion_magnitude = np.mean(diff)
                motion_magnitudes.append(motion_magnitude)
            
            metrics['average_motion'] = float(np.mean(motion_magnitudes)) if motion_magnitudes else 0.0
            metrics['motion_variation'] = float(np.std(motion_magnitudes)) if motion_magnitudes else 0.0
            
            # Scene variety (using histogram differences)
            scene_changes = 0
            for i in range(1, len(frames), 5):  # Check every 5th frame
                hist1 = cv2.calcHist([frames[i-1]], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist2 = cv2.calcHist([frames[i]], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                
                correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                if correlation < 0.8:  # Significant scene change
                    scene_changes += 1
            
            metrics['scene_variety'] = float(scene_changes / max(1, len(frames) // 5))
            
            # Exposure analysis
            overexposed_frames = 0
            underexposed_frames = 0
            
            for frame in frames[::5]:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Check overexposure
                if np.sum(gray > 240) / gray.size > 0.1:
                    overexposed_frames += 1
                
                # Check underexposure
                if np.sum(gray < 15) / gray.size > 0.1:
                    underexposed_frames += 1
            
            total_sampled = len(frames) // 5
            metrics['overexposure_ratio'] = float(overexposed_frames / max(1, total_sampled))
            metrics['underexposure_ratio'] = float(underexposed_frames / max(1, total_sampled))
            
            # Content score calculation
            motion_score = min(metrics['average_motion'] / 20.0, 1.0)  # Prefer some motion
            variety_score = min(metrics['scene_variety'] * 2.0, 1.0)
            exposure_score = 1.0 - (metrics['overexposure_ratio'] + metrics['underexposure_ratio'])
            
            content_score = np.mean([motion_score, variety_score, exposure_score])
            
            return content_score, metrics
            
        except Exception as e:
            self.logger.error(f"Video content quality assessment failed: {e}")
            return 0.0, {}
    
    def _analyze_video_quality_issues(self, metrics: Dict[str, float]) -> Tuple[List[str], List[str]]:
        """Analyze video quality metrics and generate issues/recommendations"""
        issues = []
        recommendations = []
        
        # PSNR issues
        if metrics.get('average_psnr', 0) < self.thresholds['psnr_fair']:
            issues.append("Low PSNR between frames")
            recommendations.append("Check compression settings or improve source quality")
        
        # Sharpness issues
        if metrics.get('average_sharpness', 0) < self.thresholds['sharpness_fair']:
            issues.append("Low sharpness detected")
            recommendations.append("Focus camera properly or apply sharpening filter")
        
        # Noise issues
        if metrics.get('average_noise', 0) > 30.0:
            issues.append("High noise levels")
            recommendations.append("Use noise reduction or improve lighting conditions")
        
        # Color consistency issues
        if metrics.get('color_consistency', 1.0) < 0.7:
            issues.append("Inconsistent color grading")
            recommendations.append("Apply color correction for consistency")
        
        # Exposure issues
        if metrics.get('overexposure_ratio', 0) > 0.1:
            issues.append("Overexposure detected")
            recommendations.append("Reduce exposure or adjust lighting")
        
        if metrics.get('underexposure_ratio', 0) > 0.1:
            issues.append("Underexposure detected")
            recommendations.append("Increase exposure or improve lighting")
        
        # Motion issues
        if metrics.get('average_motion', 0) < 2.0:
            issues.append("Very low motion content")
            recommendations.append("Add movement or transitions for engagement")
        
        return issues, recommendations


class MultimediaQuality:
    """Unified multimedia quality assessment system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Initialize specialized assessors
        self.audio_assessor = AudioQualityAssessment(config)
        self.video_assessor = VideoQualityAssessment(config)
        
    async def assess_file_quality(self, file_path: str, media_type: Optional[str] = None) -> QualityScore:
        """Assess quality of multimedia file"""
        try:
            file_path = Path(file_path)
            
            # Determine media type if not specified
            if media_type is None:
                media_type = self._detect_media_type(file_path)
            
            # Route to appropriate assessor
            if media_type == 'audio':
                return await self.audio_assessor.assess_audio_quality(str(file_path))
            elif media_type == 'video':
                return await self.video_assessor.assess_video_quality(str(file_path))
            else:
                raise ValueError(f"Unsupported media type: {media_type}")
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed for {file_path}: {e}")
            return QualityScore(overall_score=0.0)
    
    def _detect_media_type(self, file_path: Path) -> str:
        """Detect media type from file extension"""
        extension = file_path.suffix.lower()
        
        audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        
        if extension in audio_extensions:
            return 'audio'
        elif extension in video_extensions:
            return 'video'
        else:
            raise ValueError(f"Unknown media type for extension: {extension}")
    
    async def batch_assess_quality(self, file_paths: List[str]) -> List[QualityScore]:
        """Assess quality of multiple files"""
        try:
            tasks = [self.assess_file_quality(path) for path in file_paths]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to assess {file_paths[i]}: {result}")
                    valid_results.append(QualityScore(overall_score=0.0))
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            self.logger.error(f"Batch quality assessment failed: {e}")
            return []


# Alias for backwards compatibility
QualityScorer = MultimediaQuality