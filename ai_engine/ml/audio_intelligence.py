"""
Audio Intelligence Module - Advanced Music & Audio Processing

Specialized audio processing and music intelligence for the IA Influencer platform.
Provides comprehensive audio analysis, fingerprinting, similarity detection, and music understanding.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  STRICT LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime
import json
import hashlib

# Audio processing dependencies
try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    from scipy import signal
    from scipy.spatial.distance import cosine
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# ML dependencies
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    M4A = "m4a"
    AAC = "aac"


class MusicGenre(Enum):
    """Music genre classifications"""
    ROCK = "rock"
    POP = "pop"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    HIP_HOP = "hip_hop"
    COUNTRY = "country"
    BLUES = "blues"
    REGGAE = "reggae"
    FOLK = "folk"
    R_AND_B = "r_and_b"
    INDIE = "indie"
    ALTERNATIVE = "alternative"
    METAL = "metal"
    PUNK = "punk"
    AMBIENT = "ambient"
    WORLD = "world"
    UNKNOWN = "unknown"


class AudioQuality(Enum):
    """Audio quality levels"""
    LOW = "low"           # < 128 kbps
    STANDARD = "standard" # 128-192 kbps
    HIGH = "high"         # 192-320 kbps
    LOSSLESS = "lossless" # FLAC, WAV


@dataclass
class AudioFeatures:
    """Comprehensive audio feature representation"""
    # Basic properties
    duration: float = 0.0
    sample_rate: int = 0
    channels: int = 0
    bit_depth: int = 0
    
    # Spectral features
    spectral_centroid: np.ndarray = field(default_factory=lambda: np.array([]))
    spectral_rolloff: np.ndarray = field(default_factory=lambda: np.array([]))
    spectral_contrast: np.ndarray = field(default_factory=lambda: np.array([]))
    spectral_bandwidth: np.ndarray = field(default_factory=lambda: np.array([]))
    zero_crossing_rate: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Rhythmic features
    tempo: float = 0.0
    beat_track: np.ndarray = field(default_factory=lambda: np.array([]))
    onset_frames: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Harmonic features
    chroma: np.ndarray = field(default_factory=lambda: np.array([]))
    tonnetz: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Timbral features
    mfcc: np.ndarray = field(default_factory=lambda: np.array([]))
    mel_spectrogram: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Statistical features (aggregated)
    rms_energy: float = 0.0
    loudness: float = 0.0
    dynamic_range: float = 0.0
    
    # Advanced features
    pitch_class_profile: np.ndarray = field(default_factory=lambda: np.array([]))
    rhythm_pattern: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Quality metrics
    snr: float = 0.0  # Signal-to-noise ratio
    thd: float = 0.0  # Total harmonic distortion


@dataclass
class AudioFingerprint:
    """Audio fingerprint for content identification"""
    fingerprint_id: str
    fingerprint_data: np.ndarray
    confidence: float
    algorithm: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Metadata
    duration: float = 0.0
    sample_rate: int = 0
    file_hash: str = ""
    
    # Business logic fields
    content_id: str = ""
    creator_id: str = ""
    platform_ids: List[str] = field(default_factory=list)
    rights_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MusicAnalysisResult:
    """Comprehensive music analysis result"""
    # Basic identification
    title: str = "Unknown"
    artist: str = "Unknown"
    genre: MusicGenre = MusicGenre.UNKNOWN
    genre_confidence: float = 0.0
    
    # Musical characteristics
    key: str = "Unknown"
    mode: str = "Unknown"  # Major/Minor
    time_signature: str = "4/4"
    tempo: float = 0.0
    energy: float = 0.0
    valence: float = 0.0  # Musical positivity
    danceability: float = 0.0
    acousticness: float = 0.0
    instrumentalness: float = 0.0
    liveness: float = 0.0
    speechiness: float = 0.0
    
    # Technical quality
    audio_quality: AudioQuality = AudioQuality.STANDARD
    quality_score: float = 0.0
    loudness_lufs: float = 0.0
    dynamic_range: float = 0.0
    
    # Content protection
    fingerprint: Optional[AudioFingerprint] = None
    similar_tracks: List[Dict[str, Any]] = field(default_factory=list)
    copyright_matches: List[Dict[str, Any]] = field(default_factory=list)
    
    # Business metrics
    commercial_viability: float = 0.0
    viral_potential: float = 0.0
    target_demographics: List[str] = field(default_factory=list)
    recommended_platforms: List[str] = field(default_factory=list)
    
    # SEO and metadata
    suggested_tags: List[str] = field(default_factory=list)
    mood_tags: List[str] = field(default_factory=list)
    instrument_tags: List[str] = field(default_factory=list)


class MusicAnalyzer:
    """
    Advanced music analysis system for the IA Influencer platform
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 22050)
        self.hop_length = self.config.get('hop_length', 512)
        self.n_fft = self.config.get('n_fft', 2048)
        
        # Genre classification model (would be loaded from file in production)
        self.genre_model = self._initialize_genre_model()
        
        # Feature extractors
        self.feature_extractors = {
            'spectral': self._extract_spectral_features,
            'rhythmic': self._extract_rhythmic_features,
            'harmonic': self._extract_harmonic_features,
            'timbral': self._extract_timbral_features
        }
        
    def _initialize_genre_model(self) -> Optional[nn.Module]:
        """Initialize genre classification model"""
        # In production, this would load a trained model
        # For now, return a simple model structure
        class GenreClassifier(nn.Module):
            def __init__(self, input_dim=128, num_genres=len(MusicGenre)):
                super().__init__()
                self.fc1 = nn.Linear(input_dim, 256)
                self.fc2 = nn.Linear(256, 128)
                self.fc3 = nn.Linear(128, num_genres)
                self.dropout = nn.Dropout(0.3)
                
            def forward(self, x):
                x = F.relu(self.fc1(x))
                x = self.dropout(x)
                x = F.relu(self.fc2(x))
                x = self.dropout(x)
                x = self.fc3(x)
                return F.softmax(x, dim=1)
        
        return GenreClassifier()
    
    async def analyze_music(self, audio_path: str, metadata: Optional[Dict[str, Any]] = None) -> MusicAnalysisResult:
        """
        Comprehensive music analysis
        """
        if not LIBROSA_AVAILABLE:
            logger.error("Librosa not available for audio analysis")
            return MusicAnalysisResult()
        
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Initialize result
            result = MusicAnalysisResult()
            
            # Extract comprehensive features
            features = await self._extract_all_features(y, sr)
            
            # Basic audio properties
            result.tempo = features.tempo
            duration = len(y) / sr
            
            # Genre classification
            genre, confidence = await self._classify_genre(features)
            result.genre = genre
            result.genre_confidence = confidence
            
            # Musical characteristics
            result.key, result.mode = await self._analyze_key_mode(y, sr)
            result.time_signature = await self._detect_time_signature(y, sr)
            
            # Audio quality assessment
            result.audio_quality, result.quality_score = await self._assess_audio_quality(y, sr, audio_path)
            result.loudness_lufs = await self._calculate_loudness(y, sr)
            result.dynamic_range = features.dynamic_range
            
            # Musical attributes (Spotify-like features)
            result.energy = await self._calculate_energy(features)
            result.valence = await self._calculate_valence(features)
            result.danceability = await self._calculate_danceability(features)
            result.acousticness = await self._calculate_acousticness(features)
            result.instrumentalness = await self._calculate_instrumentalness(features)
            result.speechiness = await self._calculate_speechiness(features)
            
            # Generate fingerprint
            result.fingerprint = await self._generate_fingerprint(y, sr, audio_path)
            
            # Business analysis
            result.commercial_viability = await self._assess_commercial_viability(result)
            result.viral_potential = await self._predict_viral_potential(result)
            result.target_demographics = await self._identify_target_demographics(result)
            result.recommended_platforms = await self._recommend_platforms(result)
            
            # SEO and tagging
            result.suggested_tags = await self._generate_seo_tags(result)
            result.mood_tags = await self._extract_mood_tags(features)
            result.instrument_tags = await self._detect_instruments(features)
            
            # Find similar tracks (placeholder - would use database lookup)
            result.similar_tracks = await self._find_similar_tracks(features)
            
            logger.info(f"Music analysis completed for {audio_path}")
            return result
            
        except Exception as e:
            logger.error(f"Music analysis failed: {e}")
            return MusicAnalysisResult()
    
    async def _extract_all_features(self, y: np.ndarray, sr: int) -> AudioFeatures:
        """Extract comprehensive audio features"""
        features = AudioFeatures()
        features.duration = len(y) / sr
        features.sample_rate = sr
        features.channels = 1 if y.ndim == 1 else y.shape[1]
        
        # Extract different feature types
        spectral_features = await self._extract_spectral_features(y, sr)
        rhythmic_features = await self._extract_rhythmic_features(y, sr)
        harmonic_features = await self._extract_harmonic_features(y, sr)
        timbral_features = await self._extract_timbral_features(y, sr)
        
        # Combine features
        features.__dict__.update(spectral_features)
        features.__dict__.update(rhythmic_features)
        features.__dict__.update(harmonic_features)
        features.__dict__.update(timbral_features)
        
        return features
    
    async def _extract_spectral_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract spectral features"""
        if not LIBROSA_AVAILABLE:
            return {}
        
        features = {}
        
        try:
            # Spectral centroid
            features['spectral_centroid'] = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            
            # Spectral rolloff
            features['spectral_rolloff'] = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Spectral contrast
            features['spectral_contrast'] = librosa.feature.spectral_contrast(y=y, sr=sr)
            
            # Spectral bandwidth
            features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            
            # Zero crossing rate
            features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(y)[0]
            
            # RMS energy
            features['rms_energy'] = float(np.mean(librosa.feature.rms(y=y)[0]))
            
            # Dynamic range
            features['dynamic_range'] = float(np.max(y) - np.min(y))
            
        except Exception as e:
            logger.warning(f"Spectral feature extraction failed: {e}")
        
        return features
    
    async def _extract_rhythmic_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract rhythmic features"""
        if not LIBROSA_AVAILABLE:
            return {}
        
        features = {}
        
        try:
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = float(tempo)
            features['beat_track'] = beats
            
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            features['onset_frames'] = onset_frames
            
            # Rhythm pattern (simplified)
            if len(beats) > 1:
                beat_intervals = np.diff(beats)
                features['rhythm_pattern'] = beat_intervals[:min(16, len(beat_intervals))]
            else:
                features['rhythm_pattern'] = np.array([])
            
        except Exception as e:
            logger.warning(f"Rhythmic feature extraction failed: {e}")
            features['tempo'] = 120.0  # Default tempo
        
        return features
    
    async def _extract_harmonic_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract harmonic features"""
        if not LIBROSA_AVAILABLE:
            return {}
        
        features = {}
        
        try:
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            features['chroma'] = chroma
            
            # Pitch class profile (aggregate chroma)
            features['pitch_class_profile'] = np.mean(chroma, axis=1)
            
            # Tonnetz (harmonic network)
            features['tonnetz'] = librosa.feature.tonnetz(y=y, sr=sr)
            
        except Exception as e:
            logger.warning(f"Harmonic feature extraction failed: {e}")
        
        return features
    
    async def _extract_timbral_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract timbral features"""
        if not LIBROSA_AVAILABLE:
            return {}
        
        features = {}
        
        try:
            # MFCC (Mel-frequency cepstral coefficients)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features['mfcc'] = mfcc
            
            # Mel spectrogram
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
            features['mel_spectrogram'] = mel_spec
            
        except Exception as e:
            logger.warning(f"Timbral feature extraction failed: {e}")
        
        return features
    
    async def _classify_genre(self, features: AudioFeatures) -> Tuple[MusicGenre, float]:
        """Classify music genre using ML model"""



        try:
            # Extract features for classification
            if hasattr(features, 'mfcc') and features.mfcc.size > 0:
                # Use MFCC means as features
                mfcc_features = np.mean(features.mfcc, axis=1)
                
                # Pad or truncate to expected size
                feature_vector = np.zeros(128)
                copy_size = min(len(mfcc_features), 128)
                feature_vector[:copy_size] = mfcc_features[:copy_size]
                
                # Add spectral features if available
                if hasattr(features, 'spectral_centroid') and len(features.spectral_centroid) > 0:
                    feature_vector[13] = np.mean(features.spectral_centroid)
                
                if hasattr(features, 'tempo'):
                    feature_vector[14] = features.tempo / 200.0  # Normalize
                
                # Use model for prediction (simplified)
                if self.genre_model:
                    with torch.no_grad():
                        input_tensor = torch.FloatTensor(feature_vector).unsqueeze(0)
                        predictions = self.genre_model(input_tensor)
                        genre_idx = torch.argmax(predictions, dim=1).item()
                        confidence = torch.max(predictions).item()
                        
                        # Map to genre enum
                        genres = list(MusicGenre)
                        if genre_idx < len(genres):
                            return genres[genre_idx], confidence
            
            # Fallback: rule-based classification
            return await self._rule_based_genre_classification(features)
            
        except Exception as e:
            logger.warning(f"Genre classification failed: {e}")
            return MusicGenre.UNKNOWN, 0.0
    
    async def _rule_based_genre_classification(self, features: AudioFeatures) -> Tuple[MusicGenre, float]:
        """Rule-based genre classification fallback"""
        genre = MusicGenre.UNKNOWN
        confidence = 0.3
        
        try:
            tempo = getattr(features, 'tempo', 120)
            energy = getattr(features, 'rms_energy', 0.1)
            
            # Simple rules based on tempo and energy
            if tempo > 140 and energy > 0.15:
                genre = MusicGenre.ELECTRONIC
                confidence = 0.6
            elif tempo < 80 and energy < 0.1:
                genre = MusicGenre.CLASSICAL
                confidence = 0.5
            elif 100 <= tempo <= 130 and 0.1 <= energy <= 0.2:
                genre = MusicGenre.POP
                confidence = 0.4
            elif tempo > 120 and energy > 0.12:
                genre = MusicGenre.ROCK
                confidence = 0.5
            
        except Exception as e:
            logger.warning(f"Rule-based classification failed: {e}")
        
        return genre, confidence
    
    async def _analyze_key_mode(self, y: np.ndarray, sr: int) -> Tuple[str, str]:
        """Analyze musical key and mode"""



        try:
            if not LIBROSA_AVAILABLE:
                return "C", "Major"
            
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)
            
            # Key detection (simplified)
            key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            key_idx = np.argmax(chroma_mean)
            key = key_names[key_idx]
            
            # Mode detection (major/minor) - simplified
            # Major keys typically have higher energy in the 3rd and 7th
            major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
            minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
            
            major_score = np.dot(chroma_mean, major_profile)
            minor_score = np.dot(chroma_mean, minor_profile)
            
            mode = "Major" if major_score > minor_score else "Minor"
            
            return key, mode
            
        except Exception as e:
            logger.warning(f"Key/mode analysis failed: {e}")
            return "C", "Major"
    
    async def _detect_time_signature(self, y: np.ndarray, sr: int) -> str:
        """Detect time signature"""



        try:
            if not LIBROSA_AVAILABLE:
                return "4/4"
            
            # Beat tracking
            _, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            if len(beats) < 8:
                return "4/4"  # Default
            
            # Analyze beat intervals
            beat_intervals = np.diff(beats)
            
            # Simple heuristic based on beat regularity
            beat_std = np.std(beat_intervals)
            
            if beat_std < 2:
                return "4/4"  # Regular beats
            elif beat_std < 4:
                return "3/4"  # Moderately irregular (waltz)
            else:
                return "4/4"  # Default for complex rhythms
            
        except Exception as e:
            logger.warning(f"Time signature detection failed: {e}")
            return "4/4"
    
    async def _assess_audio_quality(self, y: np.ndarray, sr: int, file_path: str) -> Tuple[AudioQuality, float]:
        """Assess audio quality"""



        try:
            # File-based quality assessment
            file_path_obj = Path(file_path)
            file_size = file_path_obj.stat().st_size
            duration = len(y) / sr
            
            # Estimate bitrate
            bitrate_kbps = (file_size * 8) / (duration * 1000)
            
            # Quality classification
            if file_path.lower().endswith(('.flac', '.wav')):
                quality = AudioQuality.LOSSLESS
                score = 1.0
            elif bitrate_kbps > 320:
                quality = AudioQuality.HIGH
                score = 0.9
            elif bitrate_kbps > 192:
                quality = AudioQuality.HIGH
                score = 0.8
            elif bitrate_kbps > 128:
                quality = AudioQuality.STANDARD
                score = 0.6
            else:
                quality = AudioQuality.LOW
                score = 0.4
            
            # Audio signal quality analysis
            # Signal-to-noise ratio estimate
            signal_power = np.mean(y**2)
            noise_floor = np.percentile(np.abs(y), 10)**2
            snr = 10 * np.log10(signal_power / max(noise_floor, 1e-10))
            
            # Adjust score based on SNR
            if snr > 40:
                score = min(score + 0.1, 1.0)
            elif snr < 20:
                score = max(score - 0.2, 0.0)
            
            return quality, score
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {e}")
            return AudioQuality.STANDARD, 0.5
    
    async def _calculate_loudness(self, y: np.ndarray, sr: int) -> float:
        """Calculate loudness in LUFS (simplified)"""



        try:
            # Simplified loudness calculation (not true LUFS)
            rms = np.sqrt(np.mean(y**2))
            lufs = 20 * np.log10(max(rms, 1e-10)) - 23  # Rough approximation
            return float(lufs)
        except Exception as e:
            logger.warning(f"Loudness calculation failed: {e}")
            return -23.0  # Default reference
    
    async def _calculate_energy(self, features: AudioFeatures) -> float:
        """Calculate energy level (0-1)"""



        try:
            energy = getattr(features, 'rms_energy', 0.1)
            # Normalize and clamp
            return min(max(energy * 5, 0.0), 1.0)
        except:
            return 0.5
    
    async def _calculate_valence(self, features: AudioFeatures) -> float:
        """Calculate valence (musical positivity) 0-1"""



        try:
            # Simple heuristic based on spectral features
            tempo = getattr(features, 'tempo', 120)
            energy = getattr(features, 'rms_energy', 0.1)
            
            # Higher tempo and energy generally indicate higher valence
            tempo_factor = min(tempo / 140, 1.0)
            energy_factor = min(energy * 10, 1.0)
            
            valence = (tempo_factor * 0.6 + energy_factor * 0.4)
            return min(max(valence, 0.0), 1.0)
        except:
            return 0.5
    
    async def _calculate_danceability(self, features: AudioFeatures) -> float:
        """Calculate danceability (0-1)"""



        try:
            tempo = getattr(features, 'tempo', 120)
            
            # Danceability peaks around 120-130 BPM
            if 100 <= tempo <= 140:
                danceability = 1.0 - abs(tempo - 120) / 40
            else:
                danceability = max(0.2, 1.0 - abs(tempo - 120) / 80)
            
            return min(max(danceability, 0.0), 1.0)
        except:
            return 0.5
    
    async def _calculate_acousticness(self, features: AudioFeatures) -> float:
        """Calculate acousticness (0-1)"""



        try:
            # Simple heuristic - lower spectral centroid suggests more acoustic
            if hasattr(features, 'spectral_centroid') and len(features.spectral_centroid) > 0:
                avg_centroid = np.mean(features.spectral_centroid)
                # Normalize (typical range 0-8000 Hz)
                acousticness = 1.0 - min(avg_centroid / 8000, 1.0)
                return min(max(acousticness, 0.0), 1.0)
        except:
            pass
        return 0.5
    
    async def _calculate_instrumentalness(self, features: AudioFeatures) -> float:
        """Calculate instrumentalness (0-1)"""



        try:
            # Simple heuristic based on spectral characteristics
            if hasattr(features, 'spectral_contrast') and features.spectral_contrast.size > 0:
                contrast = np.mean(features.spectral_contrast)
                # Higher contrast often indicates presence of vocals
                instrumentalness = 1.0 - min(contrast / 50, 1.0)
                return min(max(instrumentalness, 0.0), 1.0)
        except:
            pass
        return 0.7  # Default to mostly instrumental
    
    async def _calculate_speechiness(self, features: AudioFeatures) -> float:
        """Calculate speechiness (0-1)"""



        try:
            # Higher zero-crossing rate often indicates speech-like content
            if hasattr(features, 'zero_crossing_rate') and len(features.zero_crossing_rate) > 0:
                zcr = np.mean(features.zero_crossing_rate)
                speechiness = min(zcr * 20, 1.0)  # Scale and clamp
                return speechiness
        except:
            pass
        return 0.1  # Default low speechiness for music
    
    async def _generate_fingerprint(self, y: np.ndarray, sr: int, file_path: str) -> AudioFingerprint:
        """Generate audio fingerprint for content protection"""



        try:
            # Simple fingerprint based on spectral features
            if LIBROSA_AVAILABLE:
                # Extract mel spectrogram
                mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
                mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
                
                # Create fingerprint from spectrogram peaks
                fingerprint_data = mel_spec_db.flatten()[:1024]  # Limit size
                
                # Generate fingerprint ID
                fingerprint_str = ','.join([f"{x:.2f}" for x in fingerprint_data])
                fingerprint_id = hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]
                
                # File hash for integrity
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    file_hash = hashlib.md5(file_content).hexdigest()
                
                return AudioFingerprint(
                    fingerprint_id=fingerprint_id,
                    fingerprint_data=fingerprint_data,
                    confidence=0.85,
                    algorithm="mel_spectrogram_peaks",
                    duration=len(y) / sr,
                    sample_rate=sr,
                    file_hash=file_hash
                )
            
        except Exception as e:
            logger.warning(f"Fingerprint generation failed: {e}")
        
        # Fallback fingerprint
        return AudioFingerprint(
            fingerprint_id=f"fallback_{int(datetime.now().timestamp())}",
            fingerprint_data=np.array([0.0]),
            confidence=0.1,
            algorithm="fallback"
        )
    
    async def _assess_commercial_viability(self, result: MusicAnalysisResult) -> float:
        """Assess commercial viability (0-1)"""



        try:
            score = 0.5  # Base score
            
            # Genre popularity weights (simplified)
            genre_weights = {
                MusicGenre.POP: 0.9,
                MusicGenre.ROCK: 0.8,
                MusicGenre.HIP_HOP: 0.85,
                MusicGenre.ELECTRONIC: 0.75,
                MusicGenre.R_AND_B: 0.7,
                MusicGenre.INDIE: 0.6,
                MusicGenre.JAZZ: 0.5,
                MusicGenre.CLASSICAL: 0.4
            }
            
            genre_weight = genre_weights.get(result.genre, 0.5)
            score = score * 0.3 + genre_weight * 0.7
            
            # Quality impact
            if result.quality_score > 0.8:
                score += 0.1
            elif result.quality_score < 0.5:
                score -= 0.1
            
            # Tempo and energy impact
            if 100 <= result.tempo <= 140 and result.energy > 0.5:
                score += 0.05
            
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"Commercial viability assessment failed: {e}")
            return 0.5
    
    async def _predict_viral_potential(self, result: MusicAnalysisResult) -> float:
        """Predict viral potential (0-1)"""



        try:
            viral_score = 0.3  # Base score
            
            # Factors that contribute to virality
            if result.danceability > 0.7:
                viral_score += 0.2
            
            if result.energy > 0.6:
                viral_score += 0.15
            
            if result.valence > 0.6:
                viral_score += 0.1
            
            if 110 <= result.tempo <= 135:  # Sweet spot for viral music
                viral_score += 0.15
            
            # Genre impact on virality
            viral_genres = [MusicGenre.POP, MusicGenre.HIP_HOP, MusicGenre.ELECTRONIC]
            if result.genre in viral_genres:
                viral_score += 0.1
            
            return min(max(viral_score, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"Viral potential prediction failed: {e}")
            return 0.3
    
    async def _identify_target_demographics(self, result: MusicAnalysisResult) -> List[str]:
        """Identify target demographics"""
        demographics = []
        
        try:
            # Age groups based on genre and characteristics
            if result.genre in [MusicGenre.HIP_HOP, MusicGenre.ELECTRONIC, MusicGenre.POP]:
                demographics.extend(["16-24", "25-34"])
            elif result.genre in [MusicGenre.ROCK, MusicGenre.ALTERNATIVE]:
                demographics.extend(["25-34", "35-44"])
            elif result.genre in [MusicGenre.JAZZ, MusicGenre.CLASSICAL]:
                demographics.extend(["35-44", "45-54", "55+"])
            elif result.genre in [MusicGenre.COUNTRY, MusicGenre.FOLK]:
                demographics.extend(["25-34", "35-44", "45-54"])
            
            # Energy-based demographics
            if result.energy > 0.7:
                demographics.append("fitness_enthusiasts")
            
            if result.danceability > 0.7:
                demographics.append("party_goers")
            
            if result.valence < 0.4:
                demographics.append("indie_music_lovers")
            
        except Exception as e:
            logger.warning(f"Demographics identification failed: {e}")
        
        return list(set(demographics))  # Remove duplicates
    
    async def _recommend_platforms(self, result: MusicAnalysisResult) -> List[str]:
        """Recommend distribution platforms"""
        platforms = []
        
        try:
            # Always recommend major platforms
            platforms.extend(["spotify", "apple_music", "youtube_music"])
            
            # Genre-specific platforms
            if result.genre in [MusicGenre.ELECTRONIC, MusicGenre.HIP_HOP]:
                platforms.extend(["soundcloud", "bandcamp"])
            
            if result.danceability > 0.7:
                platforms.append("tiktok")
            
            if result.genre in [MusicGenre.INDIE, MusicGenre.ALTERNATIVE]:
                platforms.extend(["bandcamp", "soundcloud"])
            
            if result.energy > 0.6:
                platforms.append("instagram")
            
            # Quality-based recommendations
            if result.audio_quality == AudioQuality.LOSSLESS:
                platforms.extend(["tidal", "amazon_music_hd"])
            
        except Exception as e:
            logger.warning(f"Platform recommendation failed: {e}")
        
        return list(set(platforms))  # Remove duplicates
    
    async def _generate_seo_tags(self, result: MusicAnalysisResult) -> List[str]:
        """Generate SEO-optimized tags"""
        tags = []
        
        try:
            # Genre-based tags
            tags.append(result.genre.value)
            
            # Tempo-based tags
            if result.tempo > 140:
                tags.extend(["fast", "energetic", "upbeat"])
            elif result.tempo < 80:
                tags.extend(["slow", "relaxed", "chill"])
            else:
                tags.extend(["moderate", "steady"])
            
            # Energy-based tags
            if result.energy > 0.7:
                tags.extend(["high-energy", "intense", "powerful"])
            elif result.energy < 0.3:
                tags.extend(["mellow", "gentle", "soft"])
            
            # Mood-based tags
            if result.valence > 0.7:
                tags.extend(["happy", "positive", "uplifting"])
            elif result.valence < 0.3:
                tags.extend(["melancholy", "emotional", "introspective"])
            
            # Danceability tags
            if result.danceability > 0.7:
                tags.extend(["danceable", "groovy", "rhythmic"])
            
            # Key and mode
            tags.extend([result.key, result.mode.lower()])
            
        except Exception as e:
            logger.warning(f"SEO tag generation failed: {e}")
        
        return list(set(tags))  # Remove duplicates
    
    async def _extract_mood_tags(self, features: AudioFeatures) -> List[str]:
        """Extract mood tags from audio features"""
        mood_tags = []
        
        try:
            tempo = getattr(features, 'tempo', 120)
            energy = getattr(features, 'rms_energy', 0.1)
            
            # Mood classification based on tempo and energy
            if tempo > 130 and energy > 0.15:
                mood_tags.extend(["energetic", "excited", "powerful"])
            elif tempo < 80 and energy < 0.1:
                mood_tags.extend(["calm", "peaceful", "relaxed"])
            elif tempo > 110 and energy > 0.1:
                mood_tags.extend(["upbeat", "positive", "lively"])
            else:
                mood_tags.extend(["moderate", "balanced"])
            
        except Exception as e:
            logger.warning(f"Mood tag extraction failed: {e}")
        
        return mood_tags
    
    async def _detect_instruments(self, features: AudioFeatures) -> List[str]:
        """Detect prominent instruments (simplified)"""
        instruments = []
        
        try:
            # Simple heuristics based on spectral features
            if hasattr(features, 'spectral_centroid') and len(features.spectral_centroid) > 0:
                avg_centroid = np.mean(features.spectral_centroid)
                
                # Instrument detection heuristics
                if avg_centroid > 5000:
                    instruments.extend(["cymbals", "hi-hat", "strings"])
                elif 2000 <= avg_centroid <= 5000:
                    instruments.extend(["guitar", "piano", "vocals"])
                elif 500 <= avg_centroid < 2000:
                    instruments.extend(["bass", "drums", "saxophone"])
                else:
                    instruments.extend(["bass", "kick_drum"])
            
            # Default instruments for most music
            instruments.extend(["drums", "bass"])
            
        except Exception as e:
            logger.warning(f"Instrument detection failed: {e}")
        
        return list(set(instruments))  # Remove duplicates
    
    async def _find_similar_tracks(self, features: AudioFeatures) -> List[Dict[str, Any]]:
        """Find similar tracks (placeholder for database lookup)"""
        # In production, this would search a database of analyzed tracks
        similar_tracks = []
        
        try:
            # Placeholder similar tracks
            similar_tracks = [
                {
                    "track_id": "similar_001",
                    "title": "Similar Track 1",
                    "artist": "Artist A",
                    "similarity_score": 0.85,
                    "matching_features": ["tempo", "energy", "genre"]
                },
                {
                    "track_id": "similar_002", 
                    "title": "Similar Track 2",
                    "artist": "Artist B", 
                    "similarity_score": 0.78,
                    "matching_features": ["mood", "key", "danceability"]
                }
            ]
            
        except Exception as e:
            logger.warning(f"Similar track search failed: {e}")
        
        return similar_tracks


class AudioFingerprintEngine:
    """
    Advanced audio fingerprinting for content protection
    """
    
    def __init__(self):
        self.fingerprint_database = {}  # In production, this would be a database
        self.similarity_threshold = 0.85
    
    async def generate_fingerprint(self, audio_path: str) -> Optional[AudioFingerprint]:
        """Generate comprehensive audio fingerprint"""



        try:
            if not LIBROSA_AVAILABLE:
                logger.error("Librosa required for fingerprinting")
                return None
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=22050)
            
            # Generate multiple fingerprint types
            spectral_fp = await self._generate_spectral_fingerprint(y, sr)
            chromatic_fp = await self._generate_chromatic_fingerprint(y, sr)
            rhythmic_fp = await self._generate_rhythmic_fingerprint(y, sr)
            
            # Combine fingerprints
            combined_fingerprint = np.concatenate([
                spectral_fp, chromatic_fp, rhythmic_fp
            ])
            
            # Generate unique ID
            fingerprint_str = ','.join([f"{x:.6f}" for x in combined_fingerprint])
            fingerprint_id = hashlib.sha256(fingerprint_str.encode()).hexdigest()[:24]
            
            # File hash
            with open(audio_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            fingerprint = AudioFingerprint(
                fingerprint_id=fingerprint_id,
                fingerprint_data=combined_fingerprint,
                confidence=0.9,
                algorithm="multi_modal_combined",
                duration=len(y) / sr,
                sample_rate=sr,
                file_hash=file_hash
            )
            
            # Store in database
            self.fingerprint_database[fingerprint_id] = fingerprint
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {e}")
            return None
    
    async def _generate_spectral_fingerprint(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Generate spectral fingerprint"""
        # Mel spectrogram peaks
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=32)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Extract peaks and create fingerprint
        fingerprint = np.mean(mel_spec_db, axis=1)
        return fingerprint
    
    async def _generate_chromatic_fingerprint(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Generate chromatic fingerprint"""
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        fingerprint = np.mean(chroma, axis=1)
        return fingerprint
    
    async def _generate_rhythmic_fingerprint(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Generate rhythmic fingerprint"""
        # Tempo and beat-related features
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        # Create rhythmic pattern fingerprint
        if len(beats) > 4:
            beat_intervals = np.diff(beats)
            # Normalize and limit
            fingerprint = beat_intervals[:8] / np.max(beat_intervals)
            if len(fingerprint) < 8:
                fingerprint = np.pad(fingerprint, (0, 8 - len(fingerprint)))
        else:
            fingerprint = np.array([tempo / 200.0] * 8)
        
        return fingerprint
    
    async def find_matches(self, fingerprint: AudioFingerprint, 
                          threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Find matching fingerprints in database"""
        if threshold is None:
            threshold = self.similarity_threshold
        
        matches = []
        
        try:
            query_data = fingerprint.fingerprint_data
            
            for fp_id, stored_fp in self.fingerprint_database.items():
                if fp_id == fingerprint.fingerprint_id:
                    continue  # Skip self
                
                # Calculate similarity
                similarity = await self._calculate_similarity(query_data, stored_fp.fingerprint_data)
                
                if similarity >= threshold:
                    matches.append({
                        "fingerprint_id": fp_id,
                        "similarity_score": similarity,
                        "confidence": stored_fp.confidence,
                        "algorithm": stored_fp.algorithm,
                        "duration": stored_fp.duration,
                        "match_type": "potential_duplicate" if similarity > 0.95 else "similar"
                    })
            
            # Sort by similarity
            matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            
        except Exception as e:
            logger.error(f"Fingerprint matching failed: {e}")
        
        return matches
    
    async def _calculate_similarity(self, fp1: np.ndarray, fp2: np.ndarray) -> float:
        """Calculate similarity between two fingerprints"""



        try:
            # Ensure same length
            min_len = min(len(fp1), len(fp2))
            fp1_trim = fp1[:min_len]
            fp2_trim = fp2[:min_len]
            
            # Cosine similarity
            similarity = 1 - cosine(fp1_trim, fp2_trim)
            return max(similarity, 0.0)
            
        except Exception as e:
            logger.warning(f"Similarity calculation failed: {e}")
            return 0.0


class MusicSimilarityEngine:
    """
    Music similarity detection for recommendation and matching
    """
    
    def __init__(self):
        self.feature_weights = {
            'tempo': 0.15,
            'key': 0.10,
            'genre': 0.20,
            'energy': 0.15,
            'valence': 0.15,
            'danceability': 0.10,
            'acousticness': 0.05,
            'instrumentalness': 0.05,
            'spectral': 0.05
        }
    
    async def calculate_similarity(self, track1: MusicAnalysisResult, 
                                 track2: MusicAnalysisResult) -> float:
        """Calculate overall similarity between two tracks"""



        try:
            similarity_score = 0.0
            
            # Tempo similarity
            tempo_sim = self._tempo_similarity(track1.tempo, track2.tempo)
            similarity_score += tempo_sim * self.feature_weights['tempo']
            
            # Key similarity
            key_sim = self._key_similarity(track1.key, track2.key)
            similarity_score += key_sim * self.feature_weights['key']
            
            # Genre similarity
            genre_sim = self._genre_similarity(track1.genre, track2.genre)
            similarity_score += genre_sim * self.feature_weights['genre']
            
            # Feature similarities
            energy_sim = 1 - abs(track1.energy - track2.energy)
            similarity_score += energy_sim * self.feature_weights['energy']
            
            valence_sim = 1 - abs(track1.valence - track2.valence)
            similarity_score += valence_sim * self.feature_weights['valence']
            
            dance_sim = 1 - abs(track1.danceability - track2.danceability)
            similarity_score += dance_sim * self.feature_weights['danceability']
            
            acoustic_sim = 1 - abs(track1.acousticness - track2.acousticness)
            similarity_score += acoustic_sim * self.feature_weights['acousticness']
            
            instr_sim = 1 - abs(track1.instrumentalness - track2.instrumentalness)
            similarity_score += instr_sim * self.feature_weights['instrumentalness']
            
            return min(max(similarity_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def _tempo_similarity(self, tempo1: float, tempo2: float) -> float:
        """Calculate tempo similarity"""
        tempo_diff = abs(tempo1 - tempo2)
        # Maximum similarity at 0 BPM difference, decreases with difference
        return max(0, 1 - tempo_diff / 50)
    
    def _key_similarity(self, key1: str, key2: str) -> float:
        """Calculate key similarity"""
        if key1 == key2:
            return 1.0
        
        # Circle of fifths similarity
        key_circle = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']
        
        try:
            idx1 = key_circle.index(key1)
            idx2 = key_circle.index(key2)
            distance = min(abs(idx1 - idx2), 12 - abs(idx1 - idx2))
            return max(0, 1 - distance / 6)
        except ValueError:
            return 0.5  # Unknown keys get neutral similarity
    
    def _genre_similarity(self, genre1: MusicGenre, genre2: MusicGenre) -> float:
        """Calculate genre similarity"""
        if genre1 == genre2:
            return 1.0
        
        # Genre similarity matrix (simplified)
        genre_similarities = {
            (MusicGenre.ROCK, MusicGenre.ALTERNATIVE): 0.8,
            (MusicGenre.POP, MusicGenre.R_AND_B): 0.7,
            (MusicGenre.JAZZ, MusicGenre.BLUES): 0.8,
            (MusicGenre.ELECTRONIC, MusicGenre.AMBIENT): 0.6,
            (MusicGenre.COUNTRY, MusicGenre.FOLK): 0.7,
            (MusicGenre.ROCK, MusicGenre.PUNK): 0.7,
            (MusicGenre.HIP_HOP, MusicGenre.R_AND_B): 0.6
        }
        
        # Check both directions
        similarity = genre_similarities.get((genre1, genre2)) or \
                    genre_similarities.get((genre2, genre1))
        
        return similarity if similarity else 0.2  # Default low similarity
