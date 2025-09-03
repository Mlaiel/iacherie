#!/usr/bin/env python3
"""Voice Clone Detection Module for IA-Influencer-Agent
=====================================================

Advanced AI-powered voice clone detection system to identify artificially
generated or cloned voices for content protection and security.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides:
- Voice authenticity verification
- Clone detection using multiple analysis methods
- Real-time processing capabilities
- Integration with content protection systems
"""

import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time
from abc import ABC, abstractmethod
import asyncio

# Conditional imports
try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("librosa not available, voice clone detection will be limited")
    LIBROSA_AVAILABLE = False

try:
    import scipy.signal
    import scipy.io.wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    scipy = None

logger = logging.getLogger(__name__)


class VoiceAuthenticityLevel(Enum):
    """Voice authenticity levels"""
    AUTHENTIC = "authentic"
    SUSPICIOUS = "suspicious" 
    LIKELY_CLONED = "likely_cloned"
    DEFINITIVELY_CLONED = "definitively_cloned"
    INDETERMINATE = "indeterminate"


class DetectionMethod(Enum):
    """Detection analysis methods"""
    SPECTRAL_ANALYSIS = "spectral_analysis"
    NEURAL_NETWORK = "neural_network"
    ARTIFACT_DETECTION = "artifact_detection"
    TEMPORAL_CONSISTENCY = "temporal_consistency"
    PROSODIC_ANALYSIS = "prosodic_analysis"
    BIOMETRIC_VERIFICATION = "biometric_verification"


@dataclass
class VoiceCloneAnalysis:
    """Comprehensive voice clone analysis result"""
    authenticity_level: VoiceAuthenticityLevel
    confidence_score: float
    clone_probability: float
    analysis_methods: List[DetectionMethod]
    detection_indicators: List[str]
    technical_analysis: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any]


@dataclass
class SpectralFeatures:
    """Spectral features for voice analysis"""
    mfcc: np.ndarray
    spectral_centroid: np.ndarray
    spectral_rolloff: np.ndarray
    spectral_contrast: np.ndarray
    zero_crossing_rate: np.ndarray
    chroma: np.ndarray
    mel_spectrogram: np.ndarray


class VoiceCloneDetector:
    """
    Advanced Voice Clone Detection System
    
    Uses multiple analysis methods to detect artificially generated voices:
    - Spectral analysis for unnatural artifacts
    - Neural network-based detection
    - Temporal consistency analysis
    - Prosodic pattern analysis
    - Biometric verification
    """
    
    def __init__(self, device: str = "cpu"):
        self.device = device
        self.sample_rate = 16000
        self.is_initialized = False
        
        # Detection thresholds
        self.thresholds = {
            'clone_probability': 0.7,
            'confidence_minimum': 0.6,
            'spectral_deviation': 0.3,
            'temporal_inconsistency': 0.4
        }
        
        # Analysis weights for different methods
        self.method_weights = {
            DetectionMethod.NEURAL_NETWORK: 0.35,
            DetectionMethod.SPECTRAL_ANALYSIS: 0.25,
            DetectionMethod.ARTIFACT_DETECTION: 0.20,
            DetectionMethod.TEMPORAL_CONSISTENCY: 0.15,
            DetectionMethod.PROSODIC_ANALYSIS: 0.05
        }
        
        logger.info(f"VoiceCloneDetector initialized on device: {device}")
    
    async def initialize(self) -> bool:
        """Initialize the voice clone detection models"""
        try:
            # Initialize detection models
            self.spectral_detector = self._create_spectral_detector()
            self.neural_detector = self._create_neural_detector()
            self.artifact_detector = self._create_artifact_detector()
            
            # Move models to device
            if torch.cuda.is_available() and self.device == "cuda":
                self.neural_detector = self.neural_detector.cuda()
            
            self.is_initialized = True
            logger.info("Voice clone detector initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize voice clone detector: {e}")
            return False
    
    async def detect_voice_clone(self, 
                               audio_data: np.ndarray,
                               sample_rate: int = None,
                               reference_audio: Optional[np.ndarray] = None) -> VoiceCloneAnalysis:
        """
        Detect if audio contains cloned voice
        
        Args:
            audio_data: Audio signal to analyze
            sample_rate: Sample rate of audio
            reference_audio: Optional reference audio for comparison
            
        Returns:
            VoiceCloneAnalysis with detection results
        """
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Preprocess audio
            if sample_rate != self.sample_rate:
                audio_data = self._resample_audio(audio_data, sample_rate, self.sample_rate)
            
            audio_data = self._normalize_audio(audio_data)
            
            # Extract features
            features = await self._extract_features(audio_data)
            
            # Run different detection methods
            detection_results = {}
            
            # 1. Neural network detection
            detection_results[DetectionMethod.NEURAL_NETWORK] = await self._neural_detection(
                audio_data, features
            )
            
            # 2. Spectral analysis
            detection_results[DetectionMethod.SPECTRAL_ANALYSIS] = await self._spectral_analysis(
                audio_data, features
            )
            
            # 3. Artifact detection
            detection_results[DetectionMethod.ARTIFACT_DETECTION] = await self._artifact_detection(
                audio_data, features
            )
            
            # 4. Temporal consistency analysis
            detection_results[DetectionMethod.TEMPORAL_CONSISTENCY] = await self._temporal_analysis(
                audio_data, features
            )
            
            # 5. Prosodic analysis
            detection_results[DetectionMethod.PROSODIC_ANALYSIS] = await self._prosodic_analysis(
                audio_data, features
            )
            
            # 6. Reference comparison (if available)
            if reference_audio is not None:
                detection_results[DetectionMethod.BIOMETRIC_VERIFICATION] = await self._biometric_verification(
                    audio_data, reference_audio
                )
            
            # Combine results
            analysis = self._combine_detection_results(detection_results)
            analysis.processing_time = time.time() - start_time
            
            return analysis
            
        except Exception as e:
            logger.error(f"Voice clone detection failed: {e}")
            return VoiceCloneAnalysis(
                authenticity_level=VoiceAuthenticityLevel.INDETERMINATE,
                confidence_score=0.0,
                clone_probability=0.5,
                analysis_methods=[],
                detection_indicators=[f"Detection failed: {str(e)}"],
                technical_analysis={},
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    async def _extract_features(self, audio_data: np.ndarray) -> SpectralFeatures:
        """Extract comprehensive features from audio"""
        if not LIBROSA_AVAILABLE:
            # Fallback feature extraction
            return SpectralFeatures(
                mfcc=np.zeros((13, 100)),
                spectral_centroid=np.zeros(100),
                spectral_rolloff=np.zeros(100),
                spectral_contrast=np.zeros((7, 100)),
                zero_crossing_rate=np.zeros(100),
                chroma=np.zeros((12, 100)),
                mel_spectrogram=np.zeros((128, 100))
            )
        
        # Extract MFCC features
        mfcc = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
        
        # Extract spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate)[0]
        spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=self.sample_rate)
        
        # Extract temporal features
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)[0]
        
        # Extract harmonic features
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.sample_rate)
        
        # Extract mel spectrogram
        mel_spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=self.sample_rate)
        
        return SpectralFeatures(
            mfcc=mfcc,
            spectral_centroid=spectral_centroid,
            spectral_rolloff=spectral_rolloff,
            spectral_contrast=spectral_contrast,
            zero_crossing_rate=zero_crossing_rate,
            chroma=chroma,
            mel_spectrogram=mel_spectrogram
        )
    
    async def _neural_detection(self, audio_data: np.ndarray, features: SpectralFeatures) -> Dict[str, Any]:
        """Neural network-based clone detection"""
        try:
            # Prepare input for neural network
            input_features = self._prepare_neural_input(features)
            
            # Run inference
            with torch.no_grad():
                input_tensor = torch.FloatTensor(input_features).unsqueeze(0)
                if torch.cuda.is_available() and self.device == "cuda":
                    input_tensor = input_tensor.cuda()
                
                output = self.neural_detector(input_tensor)
                clone_probability = torch.sigmoid(output).cpu().numpy()[0][0]
            
            return {
                'clone_probability': float(clone_probability),
                'confidence': 0.85,
                'indicators': self._get_neural_indicators(clone_probability)
            }
            
        except Exception as e:
            logger.warning(f"Neural detection failed: {e}")
            return {
                'clone_probability': 0.5,
                'confidence': 0.1,
                'indicators': ["Neural detection unavailable"]
            }
    
    async def _spectral_analysis(self, audio_data: np.ndarray, features: SpectralFeatures) -> Dict[str, Any]:
        """Spectral analysis for clone detection"""
        indicators = []
        clone_score = 0.0
        
        # Analyze spectral centroid variations
        spectral_centroid_std = np.std(features.spectral_centroid)
        if spectral_centroid_std < 200:  # Too stable for natural speech
            indicators.append("Unnaturally stable spectral centroid")
            clone_score += 0.3
        
        # Analyze MFCC patterns
        mfcc_mean = np.mean(features.mfcc, axis=1)
        mfcc_std = np.std(features.mfcc, axis=1)
        
        # Check for synthetic patterns in MFCC
        if np.mean(mfcc_std) < 0.5:  # Too consistent
            indicators.append("MFCC patterns too consistent for natural speech")
            clone_score += 0.2
        
        # Analyze harmonic structure
        chroma_entropy = self._calculate_entropy(features.chroma)
        if chroma_entropy < 2.5:  # Low harmonic complexity
            indicators.append("Low harmonic complexity")
            clone_score += 0.2
        
        # Check for frequency gaps (common in synthesis)
        mel_gaps = self._detect_frequency_gaps(features.mel_spectrogram)
        if mel_gaps > 3:
            indicators.append(f"Detected {mel_gaps} suspicious frequency gaps")
            clone_score += 0.3
        
        return {
            'clone_probability': min(clone_score, 1.0),
            'confidence': 0.75,
            'indicators': indicators,
            'technical_details': {
                'spectral_centroid_std': float(spectral_centroid_std),
                'mfcc_consistency': float(np.mean(mfcc_std)),
                'chroma_entropy': float(chroma_entropy),
                'frequency_gaps': mel_gaps
            }
        }
    
    async def _artifact_detection(self, audio_data: np.ndarray, features: SpectralFeatures) -> Dict[str, Any]:
        """Detect synthesis artifacts"""
        indicators = []
        artifact_score = 0.0
        
        # Check for digital artifacts
        high_freq_energy = np.mean(features.mel_spectrogram[-10:, :])
        if high_freq_energy > 0.1:  # Unusual high frequency content
            indicators.append("Unusual high frequency content")
            artifact_score += 0.2
        
        # Check for periodic patterns (vocoder artifacts)
        if self._detect_periodic_artifacts(audio_data):
            indicators.append("Detected periodic synthesis artifacts")
            artifact_score += 0.3
        
        # Check for phase inconsistencies
        phase_inconsistencies = self._detect_phase_inconsistencies(audio_data)
        if phase_inconsistencies > 0.2:
            indicators.append("Phase inconsistencies detected")
            artifact_score += 0.25
        
        # Check for quantization artifacts
        if self._detect_quantization_artifacts(audio_data):
            indicators.append("Quantization artifacts detected")
            artifact_score += 0.15
        
        return {
            'clone_probability': min(artifact_score, 1.0),
            'confidence': 0.70,
            'indicators': indicators
        }
    
    async def _temporal_analysis(self, audio_data: np.ndarray, features: SpectralFeatures) -> Dict[str, Any]:
        """Analyze temporal consistency"""
        indicators = []
        temporal_score = 0.0
        
        # Analyze energy envelope consistency
        energy_envelope = self._compute_energy_envelope(audio_data)
        energy_consistency = self._analyze_energy_consistency(energy_envelope)
        
        if energy_consistency < 0.3:  # Too consistent for natural speech
            indicators.append("Unnaturally consistent energy patterns")
            temporal_score += 0.3
        
        # Analyze pitch contour smoothness
        if LIBROSA_AVAILABLE:
            pitch = librosa.yin(audio_data, fmin=50, fmax=400, sr=self.sample_rate)
            pitch_smoothness = self._analyze_pitch_smoothness(pitch)
            
            if pitch_smoothness > 0.8:  # Too smooth
                indicators.append("Unnaturally smooth pitch contour")
                temporal_score += 0.25
        
        # Check for unnatural transitions
        transition_score = self._analyze_phoneme_transitions(features)
        if transition_score > 0.7:
            indicators.append("Unnatural phoneme transitions")
            temporal_score += 0.2
        
        return {
            'clone_probability': min(temporal_score, 1.0),
            'confidence': 0.65,
            'indicators': indicators
        }
    
    async def _prosodic_analysis(self, audio_data: np.ndarray, features: SpectralFeatures) -> Dict[str, Any]:
        """Analyze prosodic patterns"""
        indicators = []
        prosodic_score = 0.0
        
        # Analyze rhythm patterns
        rhythm_regularity = self._analyze_rhythm_patterns(audio_data)
        if rhythm_regularity > 0.8:  # Too regular
            indicators.append("Unnaturally regular rhythm patterns")
            prosodic_score += 0.3
        
        # Analyze stress patterns
        stress_patterns = self._analyze_stress_patterns(features)
        if not stress_patterns['natural']:
            indicators.append("Unnatural stress patterns detected")
            prosodic_score += 0.2
        
        return {
            'clone_probability': min(prosodic_score, 1.0),
            'confidence': 0.60,
            'indicators': indicators
        }
    
    async def _biometric_verification(self, audio_data: np.ndarray, reference_audio: np.ndarray) -> Dict[str, Any]:
        """Compare with reference audio for biometric verification"""
        # Extract speaker embeddings
        target_embedding = self._extract_speaker_embedding(audio_data)
        reference_embedding = self._extract_speaker_embedding(reference_audio)
        
        # Calculate similarity
        similarity = self._calculate_embedding_similarity(target_embedding, reference_embedding)
        
        # If similarity is too high with different content, it might be cloned
        clone_probability = 0.0
        indicators = []
        
        if similarity > 0.95:  # Suspiciously high similarity
            indicators.append("Suspiciously high speaker similarity")
            clone_probability = 0.4
        elif similarity < 0.3:  # Very different speakers
            indicators.append("Different speaker detected")
            clone_probability = 0.1
        
        return {
            'clone_probability': clone_probability,
            'confidence': 0.80,
            'indicators': indicators,
            'speaker_similarity': float(similarity)
        }
    
    def _combine_detection_results(self, detection_results: Dict[DetectionMethod, Dict[str, Any]]) -> VoiceCloneAnalysis:
        """Combine results from all detection methods"""
        # Calculate weighted average
        total_weight = 0
        weighted_clone_probability = 0
        weighted_confidence = 0
        all_indicators = []
        
        methods_used = []
        technical_analysis = {}
        
        for method, result in detection_results.items():
            weight = self.method_weights.get(method, 0.1)
            total_weight += weight
            weighted_clone_probability += result['clone_probability'] * weight
            weighted_confidence += result['confidence'] * weight
            all_indicators.extend(result['indicators'])
            methods_used.append(method)
            technical_analysis[method.value] = result
        
        if total_weight > 0:
            final_clone_probability = weighted_clone_probability / total_weight
            final_confidence = weighted_confidence / total_weight
        else:
            final_clone_probability = 0.5
            final_confidence = 0.0
        
        # Determine authenticity level
        if final_clone_probability >= 0.8:
            authenticity_level = VoiceAuthenticityLevel.DEFINITIVELY_CLONED
        elif final_clone_probability >= 0.6:
            authenticity_level = VoiceAuthenticityLevel.LIKELY_CLONED
        elif final_clone_probability >= 0.4:
            authenticity_level = VoiceAuthenticityLevel.SUSPICIOUS
        elif final_clone_probability >= 0.2:
            authenticity_level = VoiceAuthenticityLevel.AUTHENTIC
        else:
            authenticity_level = VoiceAuthenticityLevel.INDETERMINATE
        
        return VoiceCloneAnalysis(
            authenticity_level=authenticity_level,
            confidence_score=final_confidence,
            clone_probability=final_clone_probability,
            analysis_methods=methods_used,
            detection_indicators=all_indicators,
            technical_analysis=technical_analysis,
            processing_time=0.0,  # Will be set by caller
            metadata={
                'total_methods': len(methods_used),
                'weighted_analysis': True
            }
        )
    
    # Helper methods
    def _create_spectral_detector(self):
        """Create spectral analysis detector"""
        return {"initialized": True, "type": "spectral"}
    
    def _create_neural_detector(self) -> nn.Module:
        """Create neural network detector"""
        class CloneDetectionNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv1d(13, 64, kernel_size=3, padding=1)
                self.conv2 = nn.Conv1d(64, 128, kernel_size=3, padding=1)
                self.conv3 = nn.Conv1d(128, 256, kernel_size=3, padding=1)
                self.pool = nn.AdaptiveAvgPool1d(1)
                self.fc1 = nn.Linear(256, 128)
                self.fc2 = nn.Linear(128, 64)
                self.fc3 = nn.Linear(64, 1)
                self.dropout = nn.Dropout(0.3)
            
            def forward(self, x):
                x = F.relu(self.conv1(x))
                x = F.relu(self.conv2(x))
                x = F.relu(self.conv3(x))
                x = self.pool(x).squeeze(-1)
                x = F.relu(self.fc1(x))
                x = self.dropout(x)
                x = F.relu(self.fc2(x))
                x = self.dropout(x)
                x = self.fc3(x)
                return x
        
        return CloneDetectionNet()
    
    def _create_artifact_detector(self):
        """Create artifact detection system"""
        return {"initialized": True, "type": "artifact"}
    
    def _resample_audio(self, audio_data: np.ndarray, source_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate"""
        if LIBROSA_AVAILABLE:
            return librosa.resample(audio_data, orig_sr=source_sr, target_sr=target_sr)
        else:
            # Simple decimation/interpolation fallback
            if source_sr > target_sr:
                factor = source_sr // target_sr
                return audio_data[::factor]
            else:
                return audio_data
    
    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio data"""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val
        return audio_data
    
    def _prepare_neural_input(self, features: SpectralFeatures) -> np.ndarray:
        """Prepare features for neural network input"""
        # Use MFCC features for neural network
        return features.mfcc
    
    def _get_neural_indicators(self, clone_probability: float) -> List[str]:
        """Get indicators based on neural network output"""
        if clone_probability > 0.8:
            return ["Neural network detected high clone probability"]
        elif clone_probability > 0.6:
            return ["Neural network detected moderate clone probability"]
        elif clone_probability > 0.4:
            return ["Neural network detected low clone probability"]
        else:
            return ["Neural network indicates likely authentic voice"]
    
    def _calculate_entropy(self, data: np.ndarray) -> float:
        """Calculate entropy of data"""
        hist, _ = np.histogram(data.flatten(), bins=50, density=True)
        hist = hist[hist > 0]  # Remove zeros
        return -np.sum(hist * np.log2(hist))
    
    def _detect_frequency_gaps(self, mel_spectrogram: np.ndarray) -> int:
        """Detect suspicious frequency gaps"""
        # Count frequency bands with consistently low energy
        mean_energy = np.mean(mel_spectrogram, axis=1)
        low_energy_bands = np.sum(mean_energy < 0.01)
        return int(low_energy_bands)
    
    def _detect_periodic_artifacts(self, audio_data: np.ndarray) -> bool:
        """Detect periodic synthesis artifacts"""
        # Simple autocorrelation-based detection
        autocorr = np.correlate(audio_data, audio_data, mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        
        # Look for strong periodic patterns
        peak_indices = []
        for i in range(1, len(autocorr) - 1):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                if autocorr[i] > 0.3 * autocorr[0]:  # Strong correlation
                    peak_indices.append(i)
        
        # Check if peaks are too regular
        if len(peak_indices) > 3:
            intervals = np.diff(peak_indices)
            interval_consistency = np.std(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else 1
            return interval_consistency < 0.1  # Too consistent
        
        return False
    
    def _detect_phase_inconsistencies(self, audio_data: np.ndarray) -> float:
        """Detect phase inconsistencies"""
        if not SCIPY_AVAILABLE:
            return 0.0
        
        # Compute short-time Fourier transform
        f, t, Zxx = scipy.signal.stft(audio_data, fs=self.sample_rate, nperseg=1024)
        
        # Analyze phase coherence
        phase = np.angle(Zxx)
        phase_diff = np.diff(phase, axis=1)
        
        # Detect abrupt phase changes
        phase_inconsistency = np.mean(np.abs(phase_diff) > np.pi/2)
        return float(phase_inconsistency)
    
    def _detect_quantization_artifacts(self, audio_data: np.ndarray) -> bool:
        """Detect quantization artifacts"""
        # Check for unusual amplitude distributions
        hist, bins = np.histogram(audio_data, bins=256)
        
        # Look for peaks at specific levels (quantization artifacts)
        peak_ratio = np.max(hist) / np.mean(hist)
        return peak_ratio > 10  # Strong quantization artifacts
    
    def _compute_energy_envelope(self, audio_data: np.ndarray) -> np.ndarray:
        """Compute energy envelope of audio"""
        frame_length = 1024
        hop_length = 512
        
        frames = []
        for i in range(0, len(audio_data) - frame_length, hop_length):
            frame = audio_data[i:i + frame_length]
            energy = np.sum(frame ** 2)
            frames.append(energy)
        
        return np.array(frames)
    
    def _analyze_energy_consistency(self, energy_envelope: np.ndarray) -> float:
        """Analyze energy consistency"""
        if len(energy_envelope) == 0:
            return 0.5
        
        # Calculate coefficient of variation
        mean_energy = np.mean(energy_envelope)
        std_energy = np.std(energy_envelope)
        
        if mean_energy > 0:
            cv = std_energy / mean_energy
            return min(cv, 1.0)  # Normalize to [0, 1]
        else:
            return 0.0
    
    def _analyze_pitch_smoothness(self, pitch: np.ndarray) -> float:
        """Analyze pitch contour smoothness"""
        # Remove unvoiced frames (NaN values)
        voiced_pitch = pitch[~np.isnan(pitch)]
        
        if len(voiced_pitch) < 2:
            return 0.5
        
        # Calculate pitch variation
        pitch_diff = np.diff(voiced_pitch)
        smoothness = 1.0 - (np.std(pitch_diff) / (np.mean(voiced_pitch) + 1e-6))
        return max(0.0, min(1.0, smoothness))
    
    def _analyze_phoneme_transitions(self, features: SpectralFeatures) -> float:
        """Analyze phoneme transitions"""
        # Analyze MFCC transitions
        mfcc_diff = np.diff(features.mfcc, axis=1)
        transition_strength = np.mean(np.abs(mfcc_diff))
        
        # Normalize transition strength
        normalized_strength = min(transition_strength / 10.0, 1.0)
        
        # Higher values indicate more abrupt transitions (more synthetic)
        return normalized_strength
    
    def _analyze_rhythm_patterns(self, audio_data: np.ndarray) -> float:
        """Analyze rhythm regularity"""
        # Compute onset strength
        if LIBROSA_AVAILABLE:
            onset_frames = librosa.onset.onset_detect(y=audio_data, sr=self.sample_rate)
            if len(onset_frames) > 2:
                onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate)
                intervals = np.diff(onset_times)
                
                if len(intervals) > 1:
                    # Calculate rhythm regularity
                    mean_interval = np.mean(intervals)
                    std_interval = np.std(intervals)
                    regularity = 1.0 - (std_interval / (mean_interval + 1e-6))
                    return max(0.0, min(1.0, regularity))
        
        return 0.5  # Default if cannot analyze
    
    def _analyze_stress_patterns(self, features: SpectralFeatures) -> Dict[str, Any]:
        """Analyze stress patterns in speech"""
        # Analyze energy and pitch variations for stress detection
        energy_variation = np.std(features.spectral_centroid) / (np.mean(features.spectral_centroid) + 1e-6)
        
        # Natural speech should have varied stress patterns
        natural_stress = energy_variation > 0.1 and energy_variation < 2.0
        
        return {
            'natural': natural_stress,
            'energy_variation': float(energy_variation)
        }
    
    def _extract_speaker_embedding(self, audio_data: np.ndarray) -> np.ndarray:
        """Extract speaker embedding for comparison"""
        # Simple MFCC-based embedding
        if LIBROSA_AVAILABLE:
            mfcc = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
            embedding = np.mean(mfcc, axis=1)
        else:
            # Fallback: simple spectral features
            fft = np.fft.fft(audio_data)
            magnitude = np.abs(fft[:13])  # First 13 components
            embedding = magnitude / (np.linalg.norm(magnitude) + 1e-6)
        
        return embedding
    
    def _calculate_embedding_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate similarity between speaker embeddings"""
        # Cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return max(0.0, min(1.0, similarity))


# Factory function for easy instantiation
def create_voice_clone_detector(device: str = "cpu") -> VoiceCloneDetector:
    """Create and return a VoiceCloneDetector instance"""
    return VoiceCloneDetector(device=device)


# Example usage and testing
async def main():
    """Example usage of VoiceCloneDetector"""
    detector = create_voice_clone_detector()
    await detector.initialize()
    
    # Generate dummy audio for testing
    duration = 3.0  # seconds
    sample_rate = 16000
    t = np.linspace(0, duration, int(duration * sample_rate))
    
    # Create a synthetic voice (sum of sinusoids)
    synthetic_audio = (
        0.3 * np.sin(2 * np.pi * 220 * t) +  # A3
        0.2 * np.sin(2 * np.pi * 440 * t) +  # A4
        0.1 * np.sin(2 * np.pi * 880 * t)    # A5
    )
    
    # Add some noise to make it more realistic
    noise = 0.05 * np.random.randn(len(synthetic_audio))
    synthetic_audio += noise
    
    # Analyze the audio
    result = await detector.detect_voice_clone(synthetic_audio, sample_rate)
    
    print(f"Authenticity Level: {result.authenticity_level.value}")
    print(f"Clone Probability: {result.clone_probability:.2f}")
    print(f"Confidence Score: {result.confidence_score:.2f}")
    print(f"Processing Time: {result.processing_time:.2f}s")
    print("Detection Indicators:")
    for indicator in result.detection_indicators:
        print(f"  - {indicator}")


if __name__ == "__main__":
    asyncio.run(main())