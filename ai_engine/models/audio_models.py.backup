"""Advanced Audio AI Models for IA Influencer Agent Platform
Enterprise-grade audio processing and analysis models

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Development Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security
- Microservices + Audio + DevOps + IA Prompt Engineer
Email: mlaiel@live.de
"""
import torch
import torch.nn as nn
import torchaudio
import librosa
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import logging

from ..core.base_models import BaseAIModel, ModelConfig
from ..core.exceptions import ModelError, ValidationError


class AudioQuality(Enum):
    """Audio quality levels for content analysis"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROFESSIONAL = "professional"
    STUDIO = "studio"


class AudioGenre(Enum):
    """Audio genre classification"""
    MUSIC = "music"
    PODCAST = "podcast"
    VOICE_OVER = "voice_over"
    AMBIENT = "ambient"
    SOUND_EFFECT = "sound_effect"
    INTERVIEW = "interview"
    LECTURE = "lecture"
    AUDIOBOOK = "audiobook"


@dataclass
class AudioFeatures:
    """Comprehensive audio feature extraction results"""
    duration: float
    sample_rate: int
    channels: int
    bitrate: Optional[int]
    format: str
    quality: AudioQuality
    genre: AudioGenre
    bpm: Optional[float]
    key: Optional[str]
    loudness: float
    dynamics: float
    spectral_centroid: np.ndarray
    mfcc: np.ndarray
    chroma: np.ndarray
    spectral_rolloff: np.ndarray
    zero_crossing_rate: np.ndarray
    mel_spectrogram: np.ndarray
    audio_fingerprint: str
    voice_activity: List[Tuple[float, float]]
    emotion_scores: Dict[str, float]
    transcription: Optional[str]
    language: Optional[str]
    copyright_markers: List[Dict]
    similarity_hash: str


@dataclass
class AudioProtectionResult:
    """Audio content protection analysis results"""
    is_original: bool
    confidence_score: float
    copyright_matches: List[Dict]
    watermark_detected: bool
    fingerprint_matches: List[Dict]
    protection_level: str
    recommendations: List[str]
    legal_status: str


class AudioFeatureExtractor(BaseAIModel):
    """Advanced audio feature extraction using multiple ML techniques"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.sr = 22050  # Standard sample rate
        self.hop_length = 512
        self.n_mfcc = 13
        self.n_chroma = 12
        self.n_mels = 128
        
        # Initialize models
        self._init_models()
        
    def _init_models(self):
        """Initialize audio processing models"""
        # Emotion recognition model
        self.emotion_model = self._load_emotion_model()
        
        # Voice activity detection
        self.vad_model = self._load_vad_model()
        
        # Genre classification
        self.genre_classifier = self._load_genre_classifier()
        
        # BPM detection
        self.tempo_tracker = self._init_tempo_tracker()
        
    def _load_emotion_model(self):
        """Load emotion recognition model"""
        # In production, load pre-trained emotion model
        return None  # Placeholder for actual model
        
    def _load_vad_model(self):
        """Load voice activity detection model"""
        # In production, load VAD model
        return None  # Placeholder for actual model
        
    def _load_genre_classifier(self):
        """Load genre classification model"""
        # In production, load genre classifier
        return None  # Placeholder for actual model
        
    def _init_tempo_tracker(self):
        """Initialize tempo tracking algorithm"""
        return None  # Placeholder for actual tempo tracker
    
    def extract_features(self, audio_path: Union[str, Path]) -> AudioFeatures:
        """
        Extract comprehensive audio features
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            AudioFeatures object with all extracted features
        """
        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=self.sr)
            
            # Basic audio properties
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            
            # MFCC features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_chroma=self.n_chroma)
            
            # Mel spectrogram
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=self.n_mels)
            
            # Tempo detection
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            # Key detection (simplified)
            key = self._detect_key(chroma)
            
            # Loudness analysis
            loudness = self._calculate_loudness(y)
            
            # Dynamic range
            dynamics = self._calculate_dynamics(y)
            
            # Audio fingerprint
            fingerprint = self._generate_fingerprint(y, sr)
            
            # Voice activity detection
            voice_activity = self._detect_voice_activity(y, sr)
            
            # Emotion analysis
            emotion_scores = self._analyze_emotions(y, sr)
            
            # Quality assessment
            quality = self._assess_quality(y, sr)
            
            # Genre classification
            genre = self._classify_genre(y, sr)
            
            # Generate similarity hash
            similarity_hash = self._generate_similarity_hash(mfcc, chroma)
            
            return AudioFeatures(
                duration=duration,
                sample_rate=sr,
                channels=1,  # Mono after librosa.load
                bitrate=None,  # Would need original file analysis
                format=Path(audio_path).suffix.lower(),
                quality=quality,
                genre=genre,
                bpm=float(tempo),
                key=key,
                loudness=loudness,
                dynamics=dynamics,
                spectral_centroid=spectral_centroid,
                mfcc=mfcc,
                chroma=chroma,
                spectral_rolloff=spectral_rolloff,
                zero_crossing_rate=zero_crossing_rate,
                mel_spectrogram=mel_spec,
                audio_fingerprint=fingerprint,
                voice_activity=voice_activity,
                emotion_scores=emotion_scores,
                transcription=None,  # Would use ASR model
                language=None,  # Would use language detection
                copyright_markers=[],  # Would use copyright detection
                similarity_hash=similarity_hash
            )
            
        except Exception as e:
            raise ModelError(f"Feature extraction failed: {str(e)}")
    
    def _detect_key(self, chroma: np.ndarray) -> str:
        """Detect musical key from chroma features"""
        # Simplified key detection
        key_profiles = {
            'C': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
            'G': [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
            # Add more key profiles...
        }
        
        chroma_mean = np.mean(chroma, axis=1)
        best_key = 'C'  # Default
        best_correlation = 0
        
        for key, profile in key_profiles.items():
            correlation = np.corrcoef(chroma_mean, profile)[0, 1]
            if correlation > best_correlation:
                best_correlation = correlation
                best_key = key
                
        return best_key
    
    def _calculate_loudness(self, y: np.ndarray) -> float:
        """Calculate perceptual loudness"""
        rms = librosa.feature.rms(y=y)[0]
        return float(np.mean(rms))
    
    def _calculate_dynamics(self, y: np.ndarray) -> float:
        """Calculate dynamic range"""
        rms = librosa.feature.rms(y=y)[0]
        return float(np.max(rms) - np.min(rms))
    
    def _generate_fingerprint(self, y: np.ndarray, sr: int) -> str:
        """Generate audio fingerprint for copyright detection"""
        # Simplified fingerprinting
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=12)
        fingerprint = np.mean(mfcc, axis=1)
        return str(hash(tuple(fingerprint.round(3))))
    
    def _detect_voice_activity(self, y: np.ndarray, sr: int) -> List[Tuple[float, float]]:
        """Detect voice activity segments"""
        # Simplified VAD using energy thresholding
        frame_length = int(0.025 * sr)  # 25ms frames
        hop_length = int(0.01 * sr)     # 10ms hop
        
        frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
        energy = np.sum(frames ** 2, axis=0)
        
        # Simple energy-based thresholding
        threshold = np.mean(energy) * 0.1
        voice_frames = energy > threshold
        
        # Convert to time segments
        segments = []
        in_speech = False
        start_time = 0
        
        for i, is_voice in enumerate(voice_frames):
            time = i * hop_length / sr
            
            if is_voice and not in_speech:
                start_time = time
                in_speech = True
            elif not is_voice and in_speech:
                segments.append((start_time, time))
                in_speech = False
        
        if in_speech:
            segments.append((start_time, len(y) / sr))
            
        return segments
    
    def _analyze_emotions(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Analyze emotional content of audio"""
        # Simplified emotion analysis based on acoustic features
        # In production, use trained emotion recognition model
        
        # Extract features for emotion analysis
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        energy = np.mean(librosa.feature.rms(y=y))
        
        # Simple rule-based emotion mapping
        emotions = {
            'happy': min(1.0, (tempo / 120.0) * (energy * 2.0)),
            'sad': min(1.0, max(0.0, 1.0 - (tempo / 120.0)) * (1.0 - energy)),
            'energetic': min(1.0, (energy * 3.0) * (tempo / 100.0)),
            'calm': min(1.0, max(0.0, 1.0 - energy) * max(0.0, 1.0 - tempo / 100.0)),
            'angry': min(1.0, energy * max(0.0, (spectral_centroid - 2000) / 1000.0))
        }
        
        # Normalize to sum to 1.0
        total = sum(emotions.values())
        if total > 0:
            emotions = {k: v / total for k, v in emotions.items()}
        
        return emotions
    
    def _assess_quality(self, y: np.ndarray, sr: int) -> AudioQuality:
        """Assess audio quality"""
        # Simplified quality assessment
        snr = self._estimate_snr(y)
        dynamic_range = self._calculate_dynamics(y)
        
        if snr > 30 and dynamic_range > 0.3:
            return AudioQuality.STUDIO
        elif snr > 20 and dynamic_range > 0.2:
            return AudioQuality.PROFESSIONAL
        elif snr > 15 and dynamic_range > 0.1:
            return AudioQuality.HIGH
        elif snr > 10:
            return AudioQuality.MEDIUM
        else:
            return AudioQuality.LOW
    
    def _estimate_snr(self, y: np.ndarray) -> float:
        """Estimate signal-to-noise ratio"""
        # Simplified SNR estimation
        signal_power = np.mean(y ** 2)
        noise_power = np.mean((y - np.mean(y)) ** 2) * 0.1  # Assume 10% noise
        return 10 * np.log10(signal_power / max(noise_power, 1e-10))
    
    def _classify_genre(self, y: np.ndarray, sr: int) -> AudioGenre:
        """Classify audio genre"""
        # Simplified genre classification
        # In production, use trained genre classifier
        
        # Extract features for genre classification
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        voice_activity = len(self._detect_voice_activity(y, sr))
        
        # Simple rule-based classification
        if voice_activity > 10 and tempo < 100:
            return AudioGenre.PODCAST
        elif voice_activity > 5 and tempo < 80:
            return AudioGenre.VOICE_OVER
        elif tempo > 120 and spectral_centroid > 2000:
            return AudioGenre.MUSIC
        elif voice_activity < 2:
            return AudioGenre.AMBIENT
        else:
            return AudioGenre.MUSIC  # Default
    
    def _generate_similarity_hash(self, mfcc: np.ndarray, chroma: np.ndarray) -> str:
        """Generate hash for similarity comparison"""
        combined_features = np.concatenate([
            np.mean(mfcc, axis=1),
            np.mean(chroma, axis=1)
        ])
        return str(hash(tuple(combined_features.round(2))))


class AudioCopyrightDetector(BaseAIModel):
    """Advanced audio copyright detection and protection"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.fingerprint_db = {}  # In production, use proper database
        self.watermark_detector = self._init_watermark_detector()
        
    def _init_watermark_detector(self):
        """Initialize watermark detection system"""
        # In production, load watermark detection model
        return None
    
    def analyze_protection(self, audio_features: AudioFeatures) -> AudioProtectionResult:
        """
        Analyze audio for copyright protection
        
        Args:
            audio_features: Extracted audio features
            
        Returns:
            AudioProtectionResult with protection analysis
        """
        try:
            # Check fingerprint database
            fingerprint_matches = self._check_fingerprint_matches(audio_features.audio_fingerprint)
            
            # Detect watermarks
            watermark_detected = self._detect_watermarks(audio_features)
            
            # Check similarity hash
            similarity_matches = self._check_similarity_matches(audio_features.similarity_hash)
            
            # Analyze copyright markers
            copyright_matches = self._analyze_copyright_markers(audio_features)
            
            # Calculate originality confidence
            confidence_score = self._calculate_originality_confidence(
                fingerprint_matches, watermark_detected, similarity_matches
            )
            
            # Determine if content is original
            is_original = confidence_score > 0.8 and not watermark_detected
            
            # Generate protection recommendations
            recommendations = self._generate_protection_recommendations(
                is_original, confidence_score, watermark_detected
            )
            
            # Determine legal status
            legal_status = self._assess_legal_status(is_original, confidence_score, copyright_matches)
            
            # Determine protection level
            protection_level = self._determine_protection_level(confidence_score, watermark_detected)
            
            return AudioProtectionResult(
                is_original=is_original,
                confidence_score=confidence_score,
                copyright_matches=copyright_matches,
                watermark_detected=watermark_detected,
                fingerprint_matches=fingerprint_matches,
                protection_level=protection_level,
                recommendations=recommendations,
                legal_status=legal_status
            )
            
        except Exception as e:
            raise ModelError(f"Copyright analysis failed: {str(e)}")
    
    def _check_fingerprint_matches(self, fingerprint: str) -> List[Dict]:
        """Check fingerprint against database"""
        # In production, query fingerprint database
        matches = []
        
        # Simulate database check
        if fingerprint in self.fingerprint_db:
            matches.append({
                'match_id': self.fingerprint_db[fingerprint]['id'],
                'similarity': 0.95,
                'source': self.fingerprint_db[fingerprint]['source'],
                'confidence': 0.9
            })
        
        return matches
    
    def _detect_watermarks(self, audio_features: AudioFeatures) -> bool:
        """Detect digital watermarks in audio"""
        # In production, use sophisticated watermark detection
        # Check for common watermark patterns in spectral domain
        
        # Simplified watermark detection
        # Look for specific patterns in mel spectrogram
        mel_spec = audio_features.mel_spectrogram
        
        # Check for repetitive patterns that might indicate watermarks
        if mel_spec.size > 0:
            autocorr = np.correlate(mel_spec.flatten(), mel_spec.flatten(), mode='full')
            peaks = np.where(autocorr > np.max(autocorr) * 0.8)[0]
            
            # If multiple peaks suggest watermark pattern
            return len(peaks) > 3
        
        return False
    
    def _check_similarity_matches(self, similarity_hash: str) -> List[Dict]:
        """Check for similar content using hash comparison"""
        # In production, use proper similarity search
        matches = []
        
        # Simulate similarity checking
        # In real implementation, use locality-sensitive hashing
        
        return matches
    
    def _analyze_copyright_markers(self, audio_features: AudioFeatures) -> List[Dict]:
        """Analyze embedded copyright markers"""
        # In production, check for embedded metadata, ID3 tags, etc.
        markers = []
        
        # Check for copyright information in audio metadata
        # This would involve parsing ID3 tags, BWF metadata, etc.
        
        return markers
    
    def _calculate_originality_confidence(self, fingerprint_matches: List[Dict], 
                                        watermark_detected: bool, 
                                        similarity_matches: List[Dict]) -> float:
        """Calculate confidence score for content originality"""
        base_confidence = 1.0
        
        # Reduce confidence based on matches
        if fingerprint_matches:
            base_confidence *= 0.2
        
        if watermark_detected:
            base_confidence *= 0.1
        
        if similarity_matches:
            base_confidence *= 0.5
        
        return max(0.0, min(1.0, base_confidence))
    
    def _generate_protection_recommendations(self, is_original: bool, 
                                           confidence_score: float, 
                                           watermark_detected: bool) -> List[str]:
        """Generate protection recommendations"""
        recommendations = []
        
        if is_original and confidence_score > 0.9:
            recommendations.extend([
                "Content appears original - safe to publish",
                "Consider adding digital watermark for protection",
                "Register copyright if valuable content"
            ])
        elif confidence_score > 0.7:
            recommendations.extend([
                "Content likely original with minor concerns",
                "Review potential matches before publishing",
                "Consider legal consultation if commercial use"
            ])
        else:
            recommendations.extend([
                "High risk of copyright infringement",
                "Do not publish without legal clearance",
                "Consider creating original content instead"
            ])
        
        if watermark_detected:
            recommendations.append("Digital watermark detected - verify ownership")
        
        return recommendations
    
    def _assess_legal_status(self, is_original: bool, confidence_score: float, 
                           copyright_matches: List[Dict]) -> str:
        """Assess legal status for publishing"""
        if is_original and confidence_score > 0.9:
            return "SAFE_TO_PUBLISH"
        elif confidence_score > 0.7:
            return "REVIEW_REQUIRED"
        elif confidence_matches:
            return "COPYRIGHT_RISK"
        else:
            return "HIGH_RISK"
    
    def _determine_protection_level(self, confidence_score: float, 
                                  watermark_detected: bool) -> str:
        """Determine content protection level"""
        if confidence_score > 0.9:
            return "HIGH_PROTECTION"
        elif confidence_score > 0.7:
            return "MEDIUM_PROTECTION"
        elif watermark_detected:
            return "WATERMARKED"
        else:
            return "LOW_PROTECTION"


class AudioEnhancer(BaseAIModel):
    """Advanced audio enhancement and processing"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.enhancement_models = self._load_enhancement_models()
    
    def _load_enhancement_models(self):
        """Load audio enhancement models"""
        return {
            'noise_reduction': None,  # Load noise reduction model
            'upsampling': None,       # Load upsampling model
            'mastering': None,        # Load mastering model
            'voice_enhancement': None # Load voice enhancement model
        }
    
    def enhance_audio(self, audio_path: Union[str, Path], 
                     enhancement_type: str = "auto") -> Dict:
        """
        Enhance audio quality using AI models
        
        Args:
            audio_path: Path to input audio
            enhancement_type: Type of enhancement to apply
            
        Returns:
            Dictionary with enhancement results
        """
        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)
            
            enhanced_audio = y.copy()
            applied_enhancements = []
            
            if enhancement_type in ["auto", "noise_reduction"]:
                enhanced_audio = self._reduce_noise(enhanced_audio, sr)
                applied_enhancements.append("noise_reduction")
            
            if enhancement_type in ["auto", "normalize"]:
                enhanced_audio = self._normalize_audio(enhanced_audio)
                applied_enhancements.append("normalization")
            
            if enhancement_type in ["auto", "eq"]:
                enhanced_audio = self._apply_eq(enhanced_audio, sr)
                applied_enhancements.append("equalization")
            
            if enhancement_type in ["auto", "compress"]:
                enhanced_audio = self._apply_compression(enhanced_audio)
                applied_enhancements.append("compression")
            
            # Calculate enhancement metrics
            original_quality = self._assess_audio_quality(y, sr)
            enhanced_quality = self._assess_audio_quality(enhanced_audio, sr)
            
            return {
                'enhanced_audio': enhanced_audio,
                'sample_rate': sr,
                'original_quality': original_quality,
                'enhanced_quality': enhanced_quality,
                'improvement_score': enhanced_quality - original_quality,
                'applied_enhancements': applied_enhancements,
                'processing_time': 0.0  # Would measure actual processing time
            }
            
        except Exception as e:
            raise ModelError(f"Audio enhancement failed: {str(e)}")
    
    def _reduce_noise(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Apply noise reduction"""
        # Simplified spectral subtraction noise reduction
        stft = librosa.stft(y)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Estimate noise from first 0.5 seconds
        noise_frames = int(0.5 * sr / 512)  # Assuming hop_length=512
        noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
        
        # Spectral subtraction
        alpha = 2.0  # Over-subtraction factor
        enhanced_magnitude = magnitude - alpha * noise_spectrum
        enhanced_magnitude = np.maximum(enhanced_magnitude, 0.1 * magnitude)
        
        # Reconstruct audio
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_y = librosa.istft(enhanced_stft)
        
        return enhanced_y
    
    def _normalize_audio(self, y: np.ndarray) -> np.ndarray:
        """Normalize audio levels"""
        # RMS normalization
        rms = np.sqrt(np.mean(y**2))
        target_rms = 0.1  # Target RMS level
        
        if rms > 0:
            normalized_y = y * (target_rms / rms)
            # Prevent clipping
            normalized_y = np.clip(normalized_y, -1.0, 1.0)
            return normalized_y
        
        return y
    
    def _apply_eq(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Apply equalization"""
        # Simple high-pass filter to remove low-frequency noise
        from scipy import signal
        
        # High-pass filter at 80 Hz
        nyquist = sr / 2
        high_freq = 80 / nyquist
        b, a = signal.butter(4, high_freq, btype='high')
        
        filtered_y = signal.filtfilt(b, a, y)
        return filtered_y
    
    def _apply_compression(self, y: np.ndarray) -> np.ndarray:
        """Apply dynamic range compression"""
        # Simple compression using soft knee
        threshold = 0.7
        ratio = 4.0
        
        # Calculate envelope
        envelope = np.abs(y)
        
        # Apply compression
        compressed_y = y.copy()
        mask = envelope > threshold
        
        # Compress signals above threshold
        excess = envelope[mask] - threshold
        compressed_excess = excess / ratio
        compressed_envelope = threshold + compressed_excess
        
        # Apply compression while preserving sign
        compressed_y[mask] = np.sign(y[mask]) * compressed_envelope
        
        return compressed_y
    
    def _assess_audio_quality(self, y: np.ndarray, sr: int) -> float:
        """Assess audio quality score (0-1)"""
        # Multiple quality metrics
        
        # 1. Signal-to-noise ratio estimation
        snr = self._estimate_snr(y)
        snr_score = min(1.0, snr / 30.0)  # Normalize to 30dB max
        
        # 2. Dynamic range
        dynamic_range = np.max(np.abs(y)) - np.mean(np.abs(y))
        dr_score = min(1.0, dynamic_range / 0.5)
        
        # 3. Frequency content analysis
        freqs = np.fft.fftfreq(len(y), 1/sr)
        spectrum = np.abs(np.fft.fft(y))
        
        # Check for good frequency distribution
        low_freq = np.sum(spectrum[(freqs >= 80) & (freqs <= 250)])
        mid_freq = np.sum(spectrum[(freqs >= 250) & (freqs <= 4000)])
        high_freq = np.sum(spectrum[(freqs >= 4000) & (freqs <= sr/2)])
        
        total_energy = low_freq + mid_freq + high_freq
        if total_energy > 0:
            freq_balance = 1.0 - np.std([low_freq, mid_freq, high_freq]) / (total_energy / 3)
        else:
            freq_balance = 0.0
        
        # Combine scores
        quality_score = (snr_score * 0.4 + dr_score * 0.3 + freq_balance * 0.3)
        return max(0.0, min(1.0, quality_score))
    
    def _estimate_snr(self, y: np.ndarray) -> float:
        """Estimate signal-to-noise ratio"""
        # Simple SNR estimation
        signal_power = np.mean(y ** 2)
        
        # Estimate noise from quietest 10% of signal
        sorted_power = np.sort(y ** 2)
        noise_samples = int(len(sorted_power) * 0.1)
        noise_power = np.mean(sorted_power[:noise_samples])
        
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
        else:
            snr = 60.0  # Very high SNR if no noise detected
        
        return snr


# Model registry for audio models
AUDIO_MODEL_REGISTRY = {
    'feature_extractor': AudioFeatureExtractor,
    'copyright_detector': AudioCopyrightDetector,
    'audio_enhancer': AudioEnhancer
}


def create_audio_model(model_type: str, config: ModelConfig) -> BaseAIModel:
    """
    Factory function to create audio models
    
    Args:
        model_type: Type of audio model to create
        config: Model configuration
        
    Returns:
        Initialized audio model instance
    """
    if model_type not in AUDIO_MODEL_REGISTRY:
        raise ValueError(f"Unknown audio model type: {model_type}")
    
    model_class = AUDIO_MODEL_REGISTRY[model_type]
    return model_class(config)


# Export main classes
__all__ = [
    'AudioFeatures',
    'AudioProtectionResult',
    'AudioFeatureExtractor',
    'AudioCopyrightDetector',
    'AudioProtector',
    'AudioEnhancer',
    'AudioQuality',
    'AudioGenre',
    'create_audio_model',
    'AUDIO_MODEL_REGISTRY'
]

# Alias for compatibility
AudioProtector = AudioCopyrightDetector
