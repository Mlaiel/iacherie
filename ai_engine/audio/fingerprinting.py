"""Audio Fingerprinting - Advanced Audio Fingerprinting and Recognition
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive audio fingerprinting capabilities for audio identification and matching.
"""
import logging
import numpy as np
import time
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class FingerprintType(Enum):
    """Types of audio fingerprints"""    SPECTRAL_HASH = "spectral_hash"
    CHROMA_VECTOR = "chroma_vector"
    MFCC_FEATURES = "mfcc_features"
    PEAK_LANDMARKS = "peak_landmarks"
    TEMPO_RHYTHM = "tempo_rhythm"
    HARMONIC_CONTENT = "harmonic_content"

class MatchQuality(Enum):
    """Quality levels for fingerprint matching"""    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NO_MATCH = "no_match"

@dataclass
class AudioFingerprint:
    """Audio fingerprint representation"""    fingerprint_id: str
    fingerprint_type: FingerprintType
    fingerprint_data: Union[str, np.ndarray, Dict[str, Any]]
    duration_seconds: float
    sample_rate: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash_value: Optional[str] = None

@dataclass
class FingerprintMatch:
    """Fingerprint match result"""    query_fingerprint: AudioFingerprint
    matched_fingerprint: AudioFingerprint
    similarity_score: float  # 0.0 to 1.0
    match_quality: MatchQuality
    time_offset: float = 0.0  # seconds
    confidence: float = 0.0
    match_details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FingerprintDatabase:
    """Simple fingerprint database"""    fingerprints: Dict[str, AudioFingerprint] = field(default_factory=dict)
    index_by_type: Dict[FingerprintType, List[str]] = field(default_factory=dict)
    total_fingerprints: int = 0

class AudioFingerprinter:
    """Advanced audio fingerprinting engine"""    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Fingerprinting parameters
        self.frame_size = 2048
        self.hop_length = 512
        self.n_chroma = 12
        self.n_mfcc = 13
        
        # Database
        self.database = FingerprintDatabase()
        
        # Matching thresholds
        self.match_thresholds = {
            MatchQuality.EXACT: 0.95,
            MatchQuality.HIGH: 0.85,
            MatchQuality.MEDIUM: 0.70,
            MatchQuality.LOW: 0.55
        }
        
        self.logger.info("AudioFingerprinter initialized successfully")
    
    def generate_fingerprint(self, audio_data: np.ndarray, 
                           fingerprint_type: FingerprintType,
                           metadata: Optional[Dict[str, Any]] = None) -> AudioFingerprint:
        """Generate audio fingerprint"""        try:
            duration = len(audio_data) / self.sample_rate
            fingerprint_id = self._generate_fingerprint_id(audio_data, fingerprint_type)
            
            # Route to specific fingerprint generation method
            if fingerprint_type == FingerprintType.SPECTRAL_HASH:
                fingerprint_data = self._generate_spectral_hash(audio_data)
            elif fingerprint_type == FingerprintType.CHROMA_VECTOR:
                fingerprint_data = self._generate_chroma_vector(audio_data)
            elif fingerprint_type == FingerprintType.MFCC_FEATURES:
                fingerprint_data = self._generate_mfcc_features(audio_data)
            elif fingerprint_type == FingerprintType.PEAK_LANDMARKS:
                fingerprint_data = self._generate_peak_landmarks(audio_data)
            elif fingerprint_type == FingerprintType.TEMPO_RHYTHM:
                fingerprint_data = self._generate_tempo_rhythm(audio_data)
            elif fingerprint_type == FingerprintType.HARMONIC_CONTENT:
                fingerprint_data = self._generate_harmonic_content(audio_data)
            else:
                fingerprint_data = self._generate_spectral_hash(audio_data)
            
            # Generate hash
            hash_value = self._generate_hash(fingerprint_data)
            
            fingerprint = AudioFingerprint(
                fingerprint_id=fingerprint_id,
                fingerprint_type=fingerprint_type,
                fingerprint_data=fingerprint_data,
                duration_seconds=duration,
                sample_rate=self.sample_rate,
                metadata=metadata or {},
                hash_value=hash_value
            )
            
            self.logger.info(f"Generated {fingerprint_type.value} fingerprint: {fingerprint_id}")
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Fingerprint generation failed: {e}")
            raise
    
    def _generate_fingerprint_id(self, audio_data: np.ndarray, fingerprint_type: FingerprintType) -> str:
        """Generate unique fingerprint ID"""        # Create ID from audio hash and type
        audio_hash = hashlib.md5(audio_data.tobytes()).hexdigest()[:8]
        timestamp = int(time.time())
        return f"{fingerprint_type.value}_{audio_hash}_{timestamp}"
    
    def _generate_spectral_hash(self, audio_data: np.ndarray) -> str:
        """Generate spectral hash fingerprint"""        try:
            # Compute FFT
            fft_data = np.fft.fft(audio_data[:self.frame_size * 8])  # Use multiple frames
            magnitude = np.abs(fft_data[:len(fft_data)//2])  # Positive frequencies only
            
            # Create spectral peaks
            peak_threshold = np.percentile(magnitude, 90)
            peaks = magnitude > peak_threshold
            
            # Convert to binary string
            binary_fingerprint = ''.join(['1' if peak else '0' for peak in peaks])
            
            # Convert to hex hash
            hex_hash = hashlib.md5(binary_fingerprint.encode()).hexdigest()
            
            return hex_hash
            
        except Exception as e:
            self.logger.error(f"Spectral hash generation failed: {e}")
            return "error_hash"
    
    def _generate_chroma_vector(self, audio_data: np.ndarray) -> np.ndarray:
        """Generate chroma vector fingerprint"""        try:
            # Simple chroma feature extraction
            # In real implementation, would use librosa or similar
            
            # FFT-based approach
            frame_length = self.frame_size
            num_frames = len(audio_data) // self.hop_length
            
            chroma_features = []
            
            for i in range(min(num_frames, 100)):  # Limit frames for performance
                start = i * self.hop_length
                end = start + frame_length
                
                if end > len(audio_data):
                    break
                
                frame = audio_data[start:end]
                
                # Compute FFT
                fft_frame = np.fft.fft(frame)
                magnitude = np.abs(fft_frame[:len(fft_frame)//2])
                
                # Simple chroma mapping (12 bins for 12 semitones)
                chroma_frame = np.zeros(self.n_chroma)
                
                # Map frequency bins to chroma bins
                freq_per_bin = self.sample_rate / (2 * len(magnitude))
                
                for freq_bin, mag in enumerate(magnitude):
                    if mag > 0:
                        freq = freq_bin * freq_per_bin
                        if freq > 80:  # Ignore very low frequencies
                            # Convert frequency to chroma (simplified)
                            chroma_bin = int(np.log2(freq / 440.0) * 12) % 12
                            chroma_frame[chroma_bin] += mag
                
                # Normalize
                if np.sum(chroma_frame) > 0:
                    chroma_frame /= np.sum(chroma_frame)
                
                chroma_features.append(chroma_frame)
            
            if chroma_features:
                # Average chroma features across frames
                chroma_vector = np.mean(chroma_features, axis=0)
                return chroma_vector
            else:
                return np.zeros(self.n_chroma)
            
        except Exception as e:
            self.logger.error(f"Chroma vector generation failed: {e}")
            return np.zeros(self.n_chroma)
    
    def _generate_mfcc_features(self, audio_data: np.ndarray) -> np.ndarray:
        """Generate MFCC features fingerprint"""        try:
            # Simplified MFCC computation
            # In real implementation, would use librosa or similar
            
            # Pre-emphasis
            emphasized = np.append(audio_data[0], audio_data[1:] - 0.97 * audio_data[:-1])
            
            # Windowing and FFT
            frame_length = self.frame_size
            num_frames = min(len(emphasized) // self.hop_length, 50)  # Limit for performance
            
            mfcc_features = []
            
            for i in range(num_frames):
                start = i * self.hop_length
                end = start + frame_length
                
                if end > len(emphasized):
                    break
                
                frame = emphasized[start:end]
                
                # Apply window
                windowed = frame * np.hanning(len(frame))
                
                # FFT
                fft_frame = np.fft.fft(windowed)
                magnitude = np.abs(fft_frame[:len(fft_frame)//2])
                
                # Power spectrum
                power_spectrum = magnitude ** 2
                
                # Mel filter bank (simplified)
                mel_filters = self._create_mel_filters(len(power_spectrum))
                mel_spectrum = np.dot(mel_filters, power_spectrum)
                
                # Log
                log_mel = np.log(mel_spectrum + 1e-10)
                
                # DCT (simplified - just take first n_mfcc coefficients)
                mfcc_frame = np.fft.fft(log_mel).real[:self.n_mfcc]
                
                mfcc_features.append(mfcc_frame)
            
            if mfcc_features:
                # Average MFCC features across frames
                mfcc_vector = np.mean(mfcc_features, axis=0)
                return mfcc_vector
            else:
                return np.zeros(self.n_mfcc)
            
        except Exception as e:
            self.logger.error(f"MFCC generation failed: {e}")
            return np.zeros(self.n_mfcc)
    
    def _create_mel_filters(self, nfft: int, n_filters: int = 26) -> np.ndarray:
        """Create mel filter bank"""        # Simplified mel filter bank
        low_freq = 0
        high_freq = self.sample_rate / 2
        
        # Convert Hz to mel
        mel_low = 2595 * np.log10(1 + low_freq / 700)
        mel_high = 2595 * np.log10(1 + high_freq / 700)
        
        # Equally spaced mel points
        mel_points = np.linspace(mel_low, mel_high, n_filters + 2)
        
        # Convert mel back to Hz
        hz_points = 700 * (10**(mel_points / 2595) - 1)
        
        # Convert to FFT bin numbers
        bin_points = np.floor((nfft + 1) * hz_points / self.sample_rate)
        
        # Create filter bank
        filters = np.zeros((n_filters, nfft // 2))
        
        for i in range(1, n_filters + 1):
            left = int(bin_points[i - 1])
            center = int(bin_points[i])
            right = int(bin_points[i + 1])
            
            # Left slope
            for j in range(left, center):
                if center > left:
                    filters[i - 1, j] = (j - left) / (center - left)
            
            # Right slope
            for j in range(center, right):
                if right > center:
                    filters[i - 1, j] = (right - j) / (right - center)
        
        return filters
    
    def _generate_peak_landmarks(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Generate peak landmark fingerprint"""        try:
            # Spectral peak detection
            fft_data = np.fft.fft(audio_data[:self.frame_size * 4])
            magnitude = np.abs(fft_data[:len(fft_data)//2])
            
            # Find peaks
            peak_threshold = np.percentile(magnitude, 85)
            peaks = []
            
            for i in range(1, len(magnitude) - 1):
                if (magnitude[i] > magnitude[i-1] and 
                    magnitude[i] > magnitude[i+1] and 
                    magnitude[i] > peak_threshold):
                    
                    freq = i * self.sample_rate / (2 * len(magnitude))
                    peaks.append({
                        'frequency': freq,
                        'magnitude': magnitude[i],
                        'bin': i
                    })
            
            # Sort by magnitude and take top peaks
            peaks.sort(key=lambda x: x['magnitude'], reverse=True)
            top_peaks = peaks[:50]  # Top 50 peaks
            
            # Create landmark pairs
            landmarks = []
            for i, peak1 in enumerate(top_peaks):
                for j, peak2 in enumerate(top_peaks[i+1:], i+1):
                    if j - i > 20:  # Don't pair too many
                        break
                    
                    landmarks.append({
                        'freq1': peak1['frequency'],
                        'freq2': peak2['frequency'],
                        'time_diff': abs(peak1['bin'] - peak2['bin']),
                        'mag1': peak1['magnitude'],
                        'mag2': peak2['magnitude']
                    })
            
            return {
                'peaks': top_peaks,
                'landmarks': landmarks[:100],  # Top 100 landmarks
                'peak_count': len(top_peaks)
            }
            
        except Exception as e:
            self.logger.error(f"Peak landmarks generation failed: {e}")
            return {'peaks': [], 'landmarks': [], 'peak_count': 0}
    
    def _generate_tempo_rhythm(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Generate tempo and rhythm fingerprint"""        try:
            # Simple tempo detection using energy
            frame_length = int(self.sample_rate * 0.1)  # 100ms frames
            num_frames = len(audio_data) // frame_length
            
            energy_frames = []
            for i in range(num_frames):
                start = i * frame_length
                end = start + frame_length
                frame_energy = np.sum(audio_data[start:end] ** 2)
                energy_frames.append(frame_energy)
            
            if len(energy_frames) < 2:
                return {'tempo': 120.0, 'rhythm_regularity': 0.5}
            
            energy_frames = np.array(energy_frames)
            
            # Find energy peaks (beats)
            threshold = np.mean(energy_frames) + np.std(energy_frames)
            beats = []
            
            for i in range(1, len(energy_frames) - 1):
                if (energy_frames[i] > energy_frames[i-1] and
                    energy_frames[i] > energy_frames[i+1] and
                    energy_frames[i] > threshold):
                    beats.append(i * 0.1)  # Convert to time
            
            # Calculate tempo
            if len(beats) > 1:
                beat_intervals = np.diff(beats)
                avg_interval = np.mean(beat_intervals)
                if avg_interval > 0:
                    tempo = 60.0 / avg_interval
                    tempo = np.clip(tempo, 60, 200)  # Reasonable range
                else:
                    tempo = 120.0
                
                # Calculate rhythm regularity
                if len(beat_intervals) > 1:
                    rhythm_regularity = 1.0 / (1.0 + np.std(beat_intervals))
                else:
                    rhythm_regularity = 0.5
            else:
                tempo = 120.0
                rhythm_regularity = 0.5
            
            return {
                'tempo': float(tempo),
                'rhythm_regularity': float(rhythm_regularity),
                'beat_count': len(beats),
                'avg_beat_interval': np.mean(np.diff(beats)) if len(beats) > 1 else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Tempo rhythm generation failed: {e}")
            return {'tempo': 120.0, 'rhythm_regularity': 0.5}
    
    def _generate_harmonic_content(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Generate harmonic content fingerprint"""        try:
            # FFT analysis
            fft_data = np.fft.fft(audio_data[:self.frame_size * 4])
            magnitude = np.abs(fft_data[:len(fft_data)//2])
            freqs = np.fft.fftfreq(len(fft_data), 1/self.sample_rate)[:len(magnitude)]
            
            # Find fundamental frequency
            peak_bin = np.argmax(magnitude)
            fundamental_freq = freqs[peak_bin]
            
            if fundamental_freq < 80:  # Too low to be musical
                fundamental_freq = 440.0  # Default A4
            
            # Calculate harmonic content
            harmonics = []
            harmonic_strengths = []
            
            for harmonic in range(1, 8):  # First 7 harmonics
                target_freq = fundamental_freq * harmonic
                
                # Find closest frequency bin
                freq_bin = int(target_freq * len(magnitude) * 2 / self.sample_rate)
                
                if freq_bin < len(magnitude):
                    harmonic_strength = magnitude[freq_bin]
                    harmonics.append(target_freq)
                    harmonic_strengths.append(harmonic_strength)
            
            # Calculate harmonic ratios
            if len(harmonic_strengths) > 0:
                total_harmonic_energy = sum(harmonic_strengths)
                harmonic_ratios = [h / total_harmonic_energy if total_harmonic_energy > 0 else 0 
                                 for h in harmonic_strengths]
            else:
                harmonic_ratios = []
            
            return {
                'fundamental_frequency': float(fundamental_freq),
                'harmonic_count': len(harmonics),
                'harmonic_strengths': [float(h) for h in harmonic_strengths],
                'harmonic_ratios': [float(r) for r in harmonic_ratios],
                'total_harmonic_energy': float(sum(harmonic_strengths) if harmonic_strengths else 0),
                'harmonicity': float(np.mean(harmonic_ratios) if harmonic_ratios else 0)
            }
            
        except Exception as e:
            self.logger.error(f"Harmonic content generation failed: {e}")
            return {
                'fundamental_frequency': 440.0,
                'harmonic_count': 0,
                'harmonic_strengths': [],
                'harmonic_ratios': [],
                'total_harmonic_energy': 0.0,
                'harmonicity': 0.0
            }
    
    def _generate_hash(self, fingerprint_data: Any) -> str:
        """Generate hash from fingerprint data"""        try:
            if isinstance(fingerprint_data, str):
                return hashlib.md5(fingerprint_data.encode()).hexdigest()
            elif isinstance(fingerprint_data, np.ndarray):
                return hashlib.md5(fingerprint_data.tobytes()).hexdigest()
            elif isinstance(fingerprint_data, dict):
                json_str = json.dumps(fingerprint_data, sort_keys=True)
                return hashlib.md5(json_str.encode()).hexdigest()
            else:
                return hashlib.md5(str(fingerprint_data).encode()).hexdigest()
        except Exception:
            return hashlib.md5(b"error").hexdigest()
    
    def add_to_database(self, fingerprint: AudioFingerprint) -> bool:
        """Add fingerprint to database"""        try:
            # Store fingerprint
            self.database.fingerprints[fingerprint.fingerprint_id] = fingerprint
            
            # Update type index
            if fingerprint.fingerprint_type not in self.database.index_by_type:
                self.database.index_by_type[fingerprint.fingerprint_type] = []
            
            self.database.index_by_type[fingerprint.fingerprint_type].append(fingerprint.fingerprint_id)
            self.database.total_fingerprints += 1
            
            self.logger.info(f"Added fingerprint {fingerprint.fingerprint_id} to database")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add fingerprint to database: {e}")
            return False
    
    def match_fingerprint(self, query_fingerprint: AudioFingerprint, 
                         max_results: int = 10) -> List[FingerprintMatch]:
        """Match fingerprint against database"""        try:
            matches = []
            
            # Get candidates of same type
            candidates = self.database.index_by_type.get(query_fingerprint.fingerprint_type, [])
            
            for candidate_id in candidates:
                candidate = self.database.fingerprints.get(candidate_id)
                if not candidate:
                    continue
                
                # Calculate similarity
                similarity = self._calculate_similarity(query_fingerprint, candidate)
                
                if similarity > self.match_thresholds[MatchQuality.LOW]:
                    # Determine match quality
                    quality = self._determine_match_quality(similarity)
                    
                    match = FingerprintMatch(
                        query_fingerprint=query_fingerprint,
                        matched_fingerprint=candidate,
                        similarity_score=similarity,
                        match_quality=quality,
                        confidence=similarity,
                        match_details={
                            'hash_match': query_fingerprint.hash_value == candidate.hash_value,
                            'duration_diff': abs(query_fingerprint.duration_seconds - candidate.duration_seconds)
                        }
                    )
                    
                    matches.append(match)
            
            # Sort by similarity
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            
            return matches[:max_results]
            
        except Exception as e:
            self.logger.error(f"Fingerprint matching failed: {e}")
            return []
    
    def _calculate_similarity(self, fp1: AudioFingerprint, fp2: AudioFingerprint) -> float:
        """Calculate similarity between two fingerprints"""        try:
            if fp1.fingerprint_type != fp2.fingerprint_type:
                return 0.0
            
            # Hash-based quick check
            if fp1.hash_value and fp2.hash_value:
                if fp1.hash_value == fp2.hash_value:
                    return 1.0
            
            # Type-specific similarity calculation
            if fp1.fingerprint_type == FingerprintType.SPECTRAL_HASH:
                return self._calculate_hash_similarity(fp1.fingerprint_data, fp2.fingerprint_data)
            
            elif fp1.fingerprint_type == FingerprintType.CHROMA_VECTOR:
                return self._calculate_vector_similarity(fp1.fingerprint_data, fp2.fingerprint_data)
            
            elif fp1.fingerprint_type == FingerprintType.MFCC_FEATURES:
                return self._calculate_vector_similarity(fp1.fingerprint_data, fp2.fingerprint_data)
            
            elif fp1.fingerprint_type == FingerprintType.PEAK_LANDMARKS:
                return self._calculate_landmark_similarity(fp1.fingerprint_data, fp2.fingerprint_data)
            
            elif fp1.fingerprint_type == FingerprintType.TEMPO_RHYTHM:
                return self._calculate_tempo_similarity(fp1.fingerprint_data, fp2.fingerprint_data)
            
            elif fp1.fingerprint_type == FingerprintType.HARMONIC_CONTENT:
                return self._calculate_harmonic_similarity(fp1.fingerprint_data, fp2.fingerprint_data)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between hash fingerprints"""        if hash1 == hash2:
            return 1.0
        
        # Calculate Hamming distance for similar hashes
        if len(hash1) == len(hash2):
            matches = sum(1 for a, b in zip(hash1, hash2) if a == b)
            return matches / len(hash1)
        
        return 0.0
    
    def _calculate_vector_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate similarity between vector fingerprints"""        try:
            if len(vec1) != len(vec2):
                return 0.0
            
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return max(0.0, similarity)  # Ensure non-negative
            
        except Exception:
            return 0.0
    
    def _calculate_landmark_similarity(self, landmarks1: Dict, landmarks2: Dict) -> float:
        """Calculate similarity between landmark fingerprints"""        try:
            peaks1 = landmarks1.get('landmarks', [])
            peaks2 = landmarks2.get('landmarks', [])
            
            if not peaks1 or not peaks2:
                return 0.0
            
            # Simple overlap calculation
            matches = 0
            total_comparisons = min(len(peaks1), len(peaks2), 50)  # Limit comparisons
            
            for i in range(total_comparisons):
                for j in range(total_comparisons):
                    freq_diff1 = abs(peaks1[i].get('freq1', 0) - peaks2[j].get('freq1', 0))
                    freq_diff2 = abs(peaks1[i].get('freq2', 0) - peaks2[j].get('freq2', 0))
                    
                    # Allow some frequency tolerance
                    if freq_diff1 < 50 and freq_diff2 < 50:  # 50 Hz tolerance
                        matches += 1
                        break
            
            return matches / total_comparisons if total_comparisons > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_tempo_similarity(self, tempo1: Dict, tempo2: Dict) -> float:
        """Calculate similarity between tempo fingerprints"""        try:
            t1 = tempo1.get('tempo', 120)
            t2 = tempo2.get('tempo', 120)
            
            # Tempo similarity (within reasonable range)
            tempo_diff = abs(t1 - t2)
            tempo_sim = max(0, 1 - tempo_diff / 50.0)  # 50 BPM tolerance
            
            # Rhythm regularity similarity
            r1 = tempo1.get('rhythm_regularity', 0.5)
            r2 = tempo2.get('rhythm_regularity', 0.5)
            rhythm_sim = 1 - abs(r1 - r2)
            
            # Weighted combination
            similarity = tempo_sim * 0.7 + rhythm_sim * 0.3
            return max(0.0, similarity)
            
        except Exception:
            return 0.0
    
    def _calculate_harmonic_similarity(self, harmonic1: Dict, harmonic2: Dict) -> float:
        """Calculate similarity between harmonic fingerprints"""        try:
            # Fundamental frequency similarity
            f1 = harmonic1.get('fundamental_frequency', 440)
            f2 = harmonic2.get('fundamental_frequency', 440)
            
            freq_ratio = min(f1, f2) / max(f1, f2) if max(f1, f2) > 0 else 0
            freq_sim = freq_ratio if freq_ratio > 0.5 else 0  # Allow octave differences
            
            # Harmonic ratio similarity
            ratios1 = harmonic1.get('harmonic_ratios', [])
            ratios2 = harmonic2.get('harmonic_ratios', [])
            
            if ratios1 and ratios2:
                min_len = min(len(ratios1), len(ratios2))
                if min_len > 0:
                    ratio_diffs = [abs(ratios1[i] - ratios2[i]) for i in range(min_len)]
                    ratio_sim = 1 - np.mean(ratio_diffs)
                else:
                    ratio_sim = 0
            else:
                ratio_sim = 0.5
            
            # Weighted combination
            similarity = freq_sim * 0.6 + ratio_sim * 0.4
            return max(0.0, similarity)
            
        except Exception:
            return 0.0
    
    def _determine_match_quality(self, similarity_score: float) -> MatchQuality:
        """Determine match quality from similarity score"""        if similarity_score >= self.match_thresholds[MatchQuality.EXACT]:
            return MatchQuality.EXACT
        elif similarity_score >= self.match_thresholds[MatchQuality.HIGH]:
            return MatchQuality.HIGH
        elif similarity_score >= self.match_thresholds[MatchQuality.MEDIUM]:
            return MatchQuality.MEDIUM
        elif similarity_score >= self.match_thresholds[MatchQuality.LOW]:
            return MatchQuality.LOW
        else:
            return MatchQuality.NO_MATCH
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""        return {
            'total_fingerprints': self.database.total_fingerprints,
            'fingerprints_by_type': {
                fp_type.value: len(ids) 
                for fp_type, ids in self.database.index_by_type.items()
            },
            'database_size_mb': len(str(self.database)) / (1024 * 1024)
        }
    
    def clear_database(self) -> bool:
        """Clear fingerprint database"""        try:
            self.database = FingerprintDatabase()
            self.logger.info("Fingerprint database cleared")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear database: {e}")
            return False

# Export main classes
__all__ = [
    'AudioFingerprinter',
    'AudioFingerprint',
    'FingerprintMatch',
    'FingerprintDatabase',
    'FingerprintType',
    'MatchQuality'
]

logger.info("Audio fingerprinting module loaded successfully")
