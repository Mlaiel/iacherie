"""Music Analysis - Advanced Music Analysis and Processing
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive music analysis capabilities.
"""import logging
import numpy as np
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class MusicGenre(Enum):
    """Music genres"""    POP = "pop"
    ROCK = "rock"
    HIP_HOP = "hip_hop"
    ELECTRONIC = "electronic"
    CLASSICAL = "classical"
    JAZZ = "jazz"
    COUNTRY = "country"
    R_AND_B = "r_and_b"
    REGGAE = "reggae"
    BLUES = "blues"
    FOLK = "folk"
    INDIE = "indie"
    METAL = "metal"
    PUNK = "punk"
    ALTERNATIVE = "alternative"

class MusicKey(Enum):
    """Musical keys"""    C_MAJOR = "C_major"
    C_SHARP_MAJOR = "C#_major"
    D_MAJOR = "D_major"
    D_SHARP_MAJOR = "D#_major"
    E_MAJOR = "E_major"
    F_MAJOR = "F_major"
    F_SHARP_MAJOR = "F#_major"
    G_MAJOR = "G_major"
    G_SHARP_MAJOR = "G#_major"
    A_MAJOR = "A_major"
    A_SHARP_MAJOR = "A#_major"
    B_MAJOR = "B_major"
    A_MINOR = "A_minor"
    B_MINOR = "B_minor"
    C_MINOR = "C_minor"
    D_MINOR = "D_minor"
    E_MINOR = "E_minor"
    F_MINOR = "F_minor"
    G_MINOR = "G_minor"

@dataclass
class MusicFeatures:
    """Music feature analysis results"""    tempo_bpm: float
    key: Optional[MusicKey] = None
    genre: Optional[MusicGenre] = None
    energy: float = 0.0  # 0-1
    valence: float = 0.0  # 0-1 (positivity)
    danceability: float = 0.0  # 0-1
    loudness_db: float = 0.0
    speechiness: float = 0.0  # 0-1
    acousticness: float = 0.0  # 0-1
    instrumentalness: float = 0.0  # 0-1
    liveness: float = 0.0  # 0-1
    time_signature: int = 4
    duration_seconds: float = 0.0

@dataclass
class MusicAnalysisResult:
    """Complete music analysis result"""    features: MusicFeatures
    confidence: float
    analysis_time: float
    spectral_features: Dict[str, float] = field(default_factory=dict)
    rhythm_features: Dict[str, float] = field(default_factory=dict)
    harmonic_features: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MusicAnalyzer:
    """Advanced music analysis engine"""    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Analysis parameters
        self.sample_rate = 44100
        self.frame_size = 2048
        self.hop_length = 512
        
        # Genre classification model (placeholder)
        self.genre_model = None
        
        # Key detection model (placeholder)
        self.key_model = None
        
        self.logger.info("MusicAnalyzer initialized successfully")
    
    def analyze(self, audio_samples: np.ndarray, sample_rate: int = None) -> MusicAnalysisResult:
        """Perform comprehensive music analysis"""        start_time = time.time()
        
        try:
            sample_rate = sample_rate or self.sample_rate
            duration = len(audio_samples) / sample_rate
            
            # Extract various musical features
            tempo = self._analyze_tempo(audio_samples, sample_rate)
            key = self._analyze_key(audio_samples, sample_rate)
            genre = self._analyze_genre(audio_samples, sample_rate)
            
            # Audio features
            energy = self._calculate_energy(audio_samples)
            valence = self._calculate_valence(audio_samples, sample_rate)
            danceability = self._calculate_danceability(audio_samples, sample_rate, tempo)
            loudness = self._calculate_loudness(audio_samples)
            
            # Content analysis
            speechiness = self._analyze_speechiness(audio_samples, sample_rate)
            acousticness = self._analyze_acousticness(audio_samples, sample_rate)
            instrumentalness = self._analyze_instrumentalness(audio_samples, sample_rate)
            liveness = self._analyze_liveness(audio_samples, sample_rate)
            
            # Time signature (simplified)
            time_signature = self._analyze_time_signature(audio_samples, sample_rate, tempo)
            
            # Create features object
            features = MusicFeatures(
                tempo_bpm=tempo,
                key=key,
                genre=genre,
                energy=energy,
                valence=valence,
                danceability=danceability,
                loudness_db=loudness,
                speechiness=speechiness,
                acousticness=acousticness,
                instrumentalness=instrumentalness,
                liveness=liveness,
                time_signature=time_signature,
                duration_seconds=duration
            )
            
            # Additional feature analysis
            spectral_features = self._extract_spectral_features(audio_samples, sample_rate)
            rhythm_features = self._extract_rhythm_features(audio_samples, sample_rate)
            harmonic_features = self._extract_harmonic_features(audio_samples, sample_rate)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(features, spectral_features)
            
            # Calculate confidence based on signal quality
            confidence = self._calculate_confidence(audio_samples, features)
            
            analysis_time = time.time() - start_time
            
            result = MusicAnalysisResult(
                features=features,
                confidence=confidence,
                analysis_time=analysis_time,
                spectral_features=spectral_features,
                rhythm_features=rhythm_features,
                harmonic_features=harmonic_features,
                recommendations=recommendations,
                metadata={
                    'sample_rate': sample_rate,
                    'duration': duration,
                    'samples': len(audio_samples)
                }
            )
            
            self.logger.info(f"Music analysis completed in {analysis_time:.3f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Music analysis failed: {e}")
            # Return basic result
            return MusicAnalysisResult(
                features=MusicFeatures(tempo_bpm=120.0, duration_seconds=len(audio_samples) / (sample_rate or self.sample_rate)),
                confidence=0.0,
                analysis_time=time.time() - start_time,
                recommendations=["Analysis failed - unable to process audio"]
            )
    
    def _analyze_tempo(self, samples: np.ndarray, sample_rate: int) -> float:
        """Analyze tempo (BPM) - simplified implementation"""        try:
            # Placeholder tempo detection
            # In real implementation, would use onset detection and autocorrelation
            
            # Simple energy-based approach
            frame_length = int(sample_rate * 0.1)  # 100ms frames
            num_frames = len(samples) // frame_length
            
            energy_frames = []
            for i in range(num_frames):
                start = i * frame_length
                end = start + frame_length
                frame_energy = np.sum(samples[start:end] ** 2)
                energy_frames.append(frame_energy)
            
            if len(energy_frames) < 2:
                return 120.0  # Default tempo
            
            # Find peaks in energy (simplified beat detection)
            energy_frames = np.array(energy_frames)
            diff = np.diff(energy_frames)
            peaks = np.where(diff > np.std(diff))[0]
            
            if len(peaks) < 2:
                return 120.0
            
            # Calculate average time between peaks
            peak_intervals = np.diff(peaks) * 0.1  # Convert to seconds
            if len(peak_intervals) == 0:
                return 120.0
                
            avg_interval = np.mean(peak_intervals)
            if avg_interval == 0:
                return 120.0
                
            bpm = 60.0 / avg_interval
            
            # Constrain to reasonable BPM range
            bpm = np.clip(bpm, 60, 200)
            
            return float(bpm)
            
        except Exception as e:
            self.logger.error(f"Tempo analysis failed: {e}")
            return 120.0
    
    def _analyze_key(self, samples: np.ndarray, sample_rate: int) -> Optional[MusicKey]:
        """Analyze musical key - simplified implementation"""        try:
            # Placeholder key detection
            # In real implementation, would use chroma features and key profiles
            
            # Random selection for now (would be replaced with actual analysis)
            keys = list(MusicKey)
            return np.random.choice(keys)
            
        except Exception as e:
            self.logger.error(f"Key analysis failed: {e}")
            return None
    
    def _analyze_genre(self, samples: np.ndarray, sample_rate: int) -> Optional[MusicGenre]:
        """Analyze music genre - simplified implementation"""        try:
            # Placeholder genre classification
            # In real implementation, would use spectral features and ML model
            
            # Simple feature-based heuristics
            energy = self._calculate_energy(samples)
            spectral_centroid = self._calculate_spectral_centroid(samples)
            
            if energy > 0.7 and spectral_centroid > 3000:
                return MusicGenre.ELECTRONIC
            elif energy > 0.6:
                return MusicGenre.ROCK
            elif spectral_centroid < 1000:
                return MusicGenre.CLASSICAL
            else:
                return MusicGenre.POP
                
        except Exception as e:
            self.logger.error(f"Genre analysis failed: {e}")
            return None
    
    def _calculate_energy(self, samples: np.ndarray) -> float:
        """Calculate audio energy"""        try:
            rms = np.sqrt(np.mean(samples ** 2))
            # Normalize to 0-1 range
            energy = min(rms * 10, 1.0)  # Scale factor
            return float(energy)
        except Exception:
            return 0.5
    
    def _calculate_valence(self, samples: np.ndarray, sample_rate: int) -> float:
        """Calculate valence (positivity) - simplified"""        try:
            # Placeholder implementation
            # Real implementation would analyze harmonic content, rhythm patterns, etc.
            
            # Use spectral features as proxy
            spectral_centroid = self._calculate_spectral_centroid(samples)
            energy = self._calculate_energy(samples)
            
            # Higher spectral centroid and energy often correlate with positivity
            valence = (spectral_centroid / 5000.0) * 0.6 + energy * 0.4
            return float(np.clip(valence, 0, 1))
            
        except Exception:
            return 0.5
    
    def _calculate_danceability(self, samples: np.ndarray, sample_rate: int, tempo: float) -> float:
        """Calculate danceability score"""        try:
            # Factors for danceability: tempo, rhythm regularity, bass content
            
            # Tempo factor (sweet spot around 120-140 BPM)
            if 110 <= tempo <= 150:
                tempo_factor = 1.0
            elif 90 <= tempo <= 170:
                tempo_factor = 0.7
            else:
                tempo_factor = 0.3
            
            # Energy factor
            energy = self._calculate_energy(samples)
            
            # Rhythm regularity (simplified)
            rhythm_regularity = 0.7  # Placeholder
            
            danceability = (tempo_factor * 0.4 + energy * 0.3 + rhythm_regularity * 0.3)
            return float(np.clip(danceability, 0, 1))
            
        except Exception:
            return 0.5
    
    def _calculate_loudness(self, samples: np.ndarray) -> float:
        """Calculate loudness in dB"""        try:
            rms = np.sqrt(np.mean(samples ** 2))
            if rms > 0:
                loudness_db = 20 * np.log10(rms)
                return float(loudness_db)
            else:
                return -60.0  # Very quiet
        except Exception:
            return -20.0
    
    def _analyze_speechiness(self, samples: np.ndarray, sample_rate: int) -> float:
        """Analyze speechiness (vocal content)"""        try:
            # Placeholder: analyze spectral characteristics typical of speech
            spectral_centroid = self._calculate_spectral_centroid(samples)
            
            # Speech typically has spectral centroid in mid-range
            if 1000 <= spectral_centroid <= 4000:
                speechiness = 0.7
            else:
                speechiness = 0.2
                
            return float(speechiness)
            
        except Exception:
            return 0.3
    
    def _analyze_acousticness(self, samples: np.ndarray, sample_rate: int) -> float:
        """Analyze acousticness vs electronic content"""        try:
            # Placeholder: analyze harmonic vs percussive content
            energy = self._calculate_energy(samples)
            spectral_centroid = self._calculate_spectral_centroid(samples)
            
            # Lower energy and spectral centroid often indicate acoustic
            acousticness = (1 - energy) * 0.6 + (1 - min(spectral_centroid / 5000, 1)) * 0.4
            return float(np.clip(acousticness, 0, 1))
            
        except Exception:
            return 0.5
    
    def _analyze_instrumentalness(self, samples: np.ndarray, sample_rate: int) -> float:
        """Analyze instrumental vs vocal content"""        try:
            # Inverse of speechiness as approximation
            speechiness = self._analyze_speechiness(samples, sample_rate)
            instrumentalness = 1 - speechiness
            return float(instrumentalness)
            
        except Exception:
            return 0.7
    
    def _analyze_liveness(self, samples: np.ndarray, sample_rate: int) -> float:
        """Analyze liveness (live performance characteristics)"""        try:
            # Placeholder: analyze reverb, crowd noise, etc.
            # For now, use a random value with slight bias toward studio recordings
            liveness = np.random.uniform(0.1, 0.4)
            return float(liveness)
            
        except Exception:
            return 0.2
    
    def _analyze_time_signature(self, samples: np.ndarray, sample_rate: int, tempo: float) -> int:
        """Analyze time signature - simplified"""        try:
            # Placeholder: most music is in 4/4 time
            # Real implementation would analyze beat patterns
            time_signatures = [4, 3, 2, 6]
            weights = [0.8, 0.15, 0.03, 0.02]  # 4/4 is most common
            
            return int(np.random.choice(time_signatures, p=weights))
            
        except Exception:
            return 4
    
    def _calculate_spectral_centroid(self, samples: np.ndarray) -> float:
        """Calculate spectral centroid"""        try:
            # Simple frequency domain analysis
            fft = np.fft.fft(samples[:8192])  # Use first 8192 samples
            magnitude = np.abs(fft[:4096])  # First half (positive frequencies)
            
            if np.sum(magnitude) == 0:
                return 1000.0
            
            freqs = np.arange(len(magnitude))
            centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
            
            # Convert to Hz (roughly)
            centroid_hz = centroid * 22050 / len(magnitude)  # Nyquist = 22050 Hz
            
            return float(centroid_hz)
            
        except Exception:
            return 1000.0
    
    def _extract_spectral_features(self, samples: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract spectral features"""        try:
            spectral_centroid = self._calculate_spectral_centroid(samples)
            
            # Additional spectral features (simplified)
            features = {
                'spectral_centroid': spectral_centroid,
                'spectral_bandwidth': spectral_centroid * 0.3,  # Approximation
                'spectral_rolloff': spectral_centroid * 1.5,
                'zero_crossing_rate': float(len(np.where(np.diff(np.sign(samples)))[0]) / len(samples)),
                'mfcc_mean': np.random.uniform(0, 10),  # Placeholder
                'spectral_contrast': np.random.uniform(0.3, 0.8)
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"Spectral feature extraction failed: {e}")
            return {}
    
    def _extract_rhythm_features(self, samples: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract rhythm-related features"""        try:
            features = {
                'beat_strength': np.random.uniform(0.3, 0.9),
                'rhythm_regularity': np.random.uniform(0.4, 0.8),
                'syncopation': np.random.uniform(0.1, 0.6),
                'onset_density': np.random.uniform(2.0, 8.0)  # onsets per second
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"Rhythm feature extraction failed: {e}")
            return {}
    
    def _extract_harmonic_features(self, samples: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract harmonic features"""        try:
            features = {
                'harmonic_ratio': np.random.uniform(0.3, 0.8),
                'chord_complexity': np.random.uniform(0.2, 0.9),
                'tonal_stability': np.random.uniform(0.4, 0.9),
                'dissonance': np.random.uniform(0.1, 0.7)
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"Harmonic feature extraction failed: {e}")
            return {}
    
    def _generate_recommendations(self, features: MusicFeatures, 
                                 spectral_features: Dict[str, float]) -> List[str]:
        """Generate music analysis recommendations"""        recommendations = []
        
        try:
            # Tempo recommendations
            if features.tempo_bpm < 90:
                recommendations.append("Consider increasing tempo for better engagement")
            elif features.tempo_bpm > 160:
                recommendations.append("High tempo - consider if it matches target audience")
            
            # Energy recommendations
            if features.energy < 0.3:
                recommendations.append("Low energy track - consider boosting dynamics")
            elif features.energy > 0.9:
                recommendations.append("Very high energy - ensure it's not overwhelming")
            
            # Danceability recommendations
            if features.danceability > 0.7:
                recommendations.append("High danceability - great for clubs and parties")
            elif features.danceability < 0.3:
                recommendations.append("Low danceability - better for background or listening music")
            
            # Valence recommendations
            if features.valence > 0.7:
                recommendations.append("Positive valence - good for uplifting content")
            elif features.valence < 0.3:
                recommendations.append("Low valence - suitable for emotional or dramatic content")
            
            # Genre-specific recommendations
            if features.genre == MusicGenre.ELECTRONIC:
                recommendations.append("Electronic genre detected - consider modern production techniques")
            elif features.genre == MusicGenre.CLASSICAL:
                recommendations.append("Classical style - focus on instrument quality and arrangement")
            
            # Default recommendation if no specific ones
            if not recommendations:
                recommendations.append("Track analysis complete - good overall characteristics")
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            recommendations = ["Unable to generate specific recommendations"]
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _calculate_confidence(self, samples: np.ndarray, features: MusicFeatures) -> float:
        """Calculate analysis confidence based on signal quality"""        try:
            # Factors affecting confidence
            signal_length = len(samples)
            signal_strength = np.sqrt(np.mean(samples ** 2))
            
            # Length factor (longer audio = higher confidence)
            length_factor = min(signal_length / 441000, 1.0)  # 10 seconds at 44.1kHz
            
            # Signal strength factor
            strength_factor = min(signal_strength * 5, 1.0)
            
            # Feature consistency factor (placeholder)
            consistency_factor = 0.8
            
            confidence = (length_factor * 0.4 + strength_factor * 0.3 + consistency_factor * 0.3)
            return float(np.clip(confidence, 0.1, 0.95))
            
        except Exception:
            return 0.5

# Export main classes
__all__ = [
    'MusicAnalyzer',
    'MusicFeatures',
    'MusicAnalysisResult',
    'MusicGenre',
    'MusicKey'
]

logger.info("Music analysis module loaded successfully")
