"""
Real-Time Spectral Analysis Engine for Music Agent
==================================================

Ultra-advanced spectral analysis system providing real-time audio analysis,
feature extraction, and intelligent music understanding capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import io

try:
    import librosa
    import soundfile as sf
    HAS_AUDIO_LIBS = True
except ImportError:
    HAS_AUDIO_LIBS = False

logger = logging.getLogger(__name__)

@dataclass
class SpectralFeatures:
    """Container for extracted spectral features"""
    mfcc: List[float]
    spectral_centroid: List[float]
    spectral_bandwidth: List[float]
    spectral_rolloff: List[float]
    chroma: List[float]
    tempo: float
    key: str
    energy: float
    timestamp: datetime

@dataclass
class RealTimeAnalysisResult:
    """Result of real-time spectral analysis"""
    analysis_id: str
    features: SpectralFeatures
    genre_prediction: Optional[str] = None
    mood_analysis: Optional[Dict[str, float]] = None
    quality_score: float = 0.0
    processing_time_ms: float = 0.0

class SpectralAnalyzer:
    """
    Real-Time Spectral Analysis Engine
    
    Provides advanced audio analysis capabilities including:
    - Real-time spectral feature extraction
    - Music information retrieval (MIR)
    - Genre and mood classification
    - Audio quality assessment
    - Tempo and key detection
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 22050)
        self.n_mfcc = self.config.get('n_mfcc', 13)
        self.hop_length = self.config.get('hop_length', 512)
        self.n_fft = self.config.get('n_fft', 2048)
        
        # Initialize audio processing components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize audio processing components"""
        if not HAS_AUDIO_LIBS:
            logger.warning("Audio processing libraries not available. Using basic analysis.")
            self._use_basic_analysis = True
        else:
            self._use_basic_analysis = False
            
    async def analyze_real_time(
        self, 
        audio_data: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RealTimeAnalysisResult:
        """
        Perform real-time spectral analysis on audio data
        
        Args:
            audio_data: Raw audio bytes
            metadata: Optional metadata about the audio
            
        Returns:
            RealTimeAnalysisResult with extracted features and analysis
        """
        start_time = asyncio.get_event_loop().time()
        analysis_id = f"spectral_{int(start_time * 1000)}"
        
        try:
            if self._use_basic_analysis:
                features = await self._basic_analysis(audio_data)
            else:
                features = await self._advanced_analysis(audio_data)
                
            # Predict genre and mood
            genre_prediction = await self._predict_genre(features)
            mood_analysis = await self._analyze_mood(features)
            quality_score = await self._assess_quality(features, audio_data)
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return RealTimeAnalysisResult(
                analysis_id=analysis_id,
                features=features,
                genre_prediction=genre_prediction,
                mood_analysis=mood_analysis,
                quality_score=quality_score,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Spectral analysis failed: {e}")
            raise
    
    async def _advanced_analysis(self, audio_data: bytes) -> SpectralFeatures:
        """Perform advanced spectral analysis using librosa"""
        try:
            # Load audio from bytes
            audio_array, sr = sf.read(io.BytesIO(audio_data))
            
            # Resample if necessary
            if sr != self.sample_rate:
                audio_array = librosa.resample(audio_array, orig_sr=sr, target_sr=self.sample_rate)
            
            # Extract spectral features
            mfcc = librosa.feature.mfcc(
                y=audio_array, 
                sr=self.sample_rate, 
                n_mfcc=self.n_mfcc,
                hop_length=self.hop_length,
                n_fft=self.n_fft
            )
            
            spectral_centroid = librosa.feature.spectral_centroid(
                y=audio_array, 
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(
                y=audio_array, 
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            spectral_rolloff = librosa.feature.spectral_rolloff(
                y=audio_array, 
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            chroma = librosa.feature.chroma_stft(
                y=audio_array, 
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            # Tempo and key detection
            tempo, _ = librosa.beat.beat_track(
                y=audio_array, 
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            # Key detection using chroma
            key = self._detect_key(chroma)
            
            # Energy calculation
            energy = float(np.sum(audio_array ** 2) / len(audio_array))
            
            return SpectralFeatures(
                mfcc=np.mean(mfcc, axis=1).tolist(),
                spectral_centroid=np.mean(spectral_centroid, axis=1).tolist(),
                spectral_bandwidth=np.mean(spectral_bandwidth, axis=1).tolist(),
                spectral_rolloff=np.mean(spectral_rolloff, axis=1).tolist(),
                chroma=np.mean(chroma, axis=1).tolist(),
                tempo=float(tempo),
                key=key,
                energy=energy,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Advanced spectral analysis failed: {e}")
            raise
    
    async def _basic_analysis(self, audio_data: bytes) -> SpectralFeatures:
        """Perform basic analysis without advanced libraries"""
        # Basic analysis using simple calculations
        data_length = len(audio_data)
        
        # Simple energy calculation
        if data_length > 0:
            # Convert bytes to approximate audio values
            audio_values = list(audio_data)
            energy = sum(x**2 for x in audio_values) / len(audio_values) / 65536.0
        else:
            energy = 0.0
        
        # Mock features for basic implementation
        return SpectralFeatures(
            mfcc=[0.0] * self.n_mfcc,
            spectral_centroid=[1000.0],
            spectral_bandwidth=[500.0],
            spectral_rolloff=[2000.0],
            chroma=[0.1] * 12,
            tempo=120.0,
            key="C",
            energy=energy,
            timestamp=datetime.utcnow()
        )
    
    def _detect_key(self, chroma: np.ndarray) -> str:
        """Detect musical key from chroma features"""
        try:
            # Calculate average chroma profile
            chroma_mean = np.mean(chroma, axis=1)
            
            # Key profiles (simplified Krumhansl-Schmuckler key profiles)
            major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
            minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
            
            key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            
            best_correlation = -1
            best_key = "C"
            
            # Test all 24 keys (12 major + 12 minor)
            for i in range(12):
                # Major key
                major_shifted = np.roll(major_profile, i)
                major_corr = np.corrcoef(chroma_mean, major_shifted)[0, 1]
                if major_corr > best_correlation:
                    best_correlation = major_corr
                    best_key = key_names[i]
                
                # Minor key
                minor_shifted = np.roll(minor_profile, i)
                minor_corr = np.corrcoef(chroma_mean, minor_shifted)[0, 1]
                if minor_corr > best_correlation:
                    best_correlation = minor_corr
                    best_key = key_names[i] + "m"
            
            return best_key
            
        except Exception:
            return "C"  # Default to C major
    
    async def _predict_genre(self, features: SpectralFeatures) -> Optional[str]:
        """Predict musical genre based on spectral features"""
        try:
            # Simple genre classification based on features
            tempo = features.tempo
            energy = features.energy
            
            # Basic genre classification rules
            if tempo > 140 and energy > 0.5:
                return "Electronic/Dance"
            elif tempo < 80 and energy < 0.3:
                return "Ambient/Chillout"
            elif 80 <= tempo <= 120 and 0.3 <= energy <= 0.7:
                return "Pop/Rock"
            elif tempo > 120 and energy > 0.4:
                return "Rock/Metal"
            else:
                return "Alternative"
                
        except Exception:
            return None
    
    async def _analyze_mood(self, features: SpectralFeatures) -> Optional[Dict[str, float]]:
        """Analyze musical mood based on spectral features"""
        try:
            # Simple mood analysis based on features
            energy = features.energy
            tempo = features.tempo
            
            # Calculate mood scores (0.0 to 1.0)
            happiness = min(1.0, max(0.0, (tempo - 60) / 120 + energy))
            sadness = 1.0 - happiness
            energy_level = min(1.0, max(0.0, energy * 2))
            calmness = 1.0 - energy_level
            
            return {
                "happiness": happiness,
                "sadness": sadness,
                "energy": energy_level,
                "calmness": calmness
            }
            
        except Exception:
            return None
    
    async def _assess_quality(self, features: SpectralFeatures, audio_data: bytes) -> float:
        """Assess audio quality based on features and data"""
        try:
            # Simple quality assessment
            quality_score = 0.0
            
            # Check energy level (good music should have reasonable energy)
            if 0.1 <= features.energy <= 0.9:
                quality_score += 0.3
            
            # Check tempo consistency
            if 60 <= features.tempo <= 200:
                quality_score += 0.2
            
            # Check data size (larger files might indicate better quality)
            if len(audio_data) > 100000:  # ~100KB
                quality_score += 0.3
            
            # Check spectral richness
            if len(features.mfcc) >= self.n_mfcc:
                quality_score += 0.2
            
            return min(1.0, quality_score)
            
        except Exception:
            return 0.5  # Default quality score
    
    async def batch_analyze(
        self, 
        audio_files: List[Dict[str, Any]]
    ) -> List[RealTimeAnalysisResult]:
        """Perform batch analysis on multiple audio files"""
        results = []
        
        for audio_file in audio_files:
            try:
                audio_data = audio_file.get('data', b'')
                metadata = audio_file.get('metadata', {})
                
                result = await self.analyze_real_time(audio_data, metadata)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Batch analysis failed for file: {e}")
                # Continue with other files
                continue
        
        return results
    
    def get_analyzer_info(self) -> Dict[str, Any]:
        """Get information about the analyzer configuration"""
        return {
            "sample_rate": self.sample_rate,
            "n_mfcc": self.n_mfcc,
            "hop_length": self.hop_length,
            "n_fft": self.n_fft,
            "has_advanced_libs": not self._use_basic_analysis,
            "supported_features": [
                "MFCC", "Spectral Centroid", "Spectral Bandwidth",
                "Spectral Rolloff", "Chroma", "Tempo", "Key Detection",
                "Genre Prediction", "Mood Analysis", "Quality Assessment"
            ]
        }